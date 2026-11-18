#!/usr/bin/env python3
"""Headless tests for Overlord rain / slam / ink_surge melee interrupt windows.

Loads CorruptionGlobals without Panda3D. Asserts Overlord interrupt tunables
+ isMeleeInterruptibleTelegraph for climax move ids, and AI wiring on
DistributedCorruptToonAI (__maybeInterruptMeleeTelegraph from
takeHackSlashDamage). Extends street-kit mid-telegraph cancel to boss
telegraphs after move-aware announce (#340). No cream FX, no KH.

Run from repo root:
  python3 tests/test_melee_interrupt_overlord.py
  python3 -m unittest tests.test_melee_interrupt_overlord -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_corruption_globals():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.toonbase', 'toontown.corruption'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = 2200
    tg.PunchlinePlace = 2300
    tg.SillyStreet = 2100
    tg.ToontownCentral = 2000
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    cg_path = REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
    cg_spec = importlib.util.spec_from_file_location(
        'toontown.corruption.CorruptionGlobals', cg_path)
    cg = importlib.util.module_from_spec(cg_spec)
    assert cg_spec.loader is not None
    sys.modules['toontown.corruption.CorruptionGlobals'] = cg
    cg_spec.loader.exec_module(cg)
    sys.modules['toontown.corruption'].CorruptionGlobals = cg
    return cg


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    return set()


def _method_source(rel: str, class_name: str, method_name: str) -> str:
    tree = _module_ast(rel)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name == method_name):
                    return ast.get_source_segment(_read(rel), item) or ''
    return ''


class MeleeInterruptOverlordTest(unittest.TestCase):
    """Overlord rain / slam / ink_surge melee interrupt tunables + AI wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_interrupt_globals_armed(self):
        self.assertTrue(self.cg.OVERLORD_RAIN_MELEE_INTERRUPT)
        self.assertTrue(self.cg.OVERLORD_SLAM_MELEE_INTERRUPT)
        self.assertTrue(self.cg.OVERLORD_INK_SURGE_MELEE_INTERRUPT)
        # Street flags stay armed — shared AI path.
        self.assertTrue(self.cg.BRUTE_SPIT_MELEE_INTERRUPT)
        self.assertTrue(self.cg.GAGSTER_LOB_MELEE_INTERRUPT)
        blob = ' '.join([
            'OVERLORD_RAIN_MELEE_INTERRUPT',
            'OVERLORD_SLAM_MELEE_INTERRUPT',
            'OVERLORD_INK_SURGE_MELEE_INTERRUPT',
            'isMeleeInterruptibleTelegraph',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_helper_allows_overlord_rain_slam_surge(self):
        fn = self.cg.isMeleeInterruptibleTelegraph
        ink = self.cg.ARCHETYPE_INK
        # Overlord climax move ids on ARCHETYPE_INK.
        self.assertTrue(fn(ink, 'rain'))
        self.assertTrue(fn(ink, 'slam'))
        self.assertTrue(fn(ink, 'ink_surge'))
        # Smudge kit interrupt covered by test_melee_interrupt_ink_smudge.py
        # (same archetype, distinct move ids).
        self.assertTrue(fn(ink, 'ink_dash'))
        self.assertTrue(fn(ink, 'ink_splat'))
        self.assertFalse(fn(ink, 'smack'))
        # Brute slam stays out of Overlord interrupt scope.
        # Oswald betrayal interrupt/counter is covered by
        # test_melee_interrupt_oswald.py / test_oswald_counter_windows.py.
        self.assertFalse(fn(self.cg.ARCHETYPE_BRUTE, 'slam'))
        # Street kits still interruptible.
        self.assertTrue(fn(self.cg.ARCHETYPE_BRUTE, 'spit'))
        self.assertTrue(fn(self.cg.ARCHETYPE_GAGSTER, 'gag_lob'))
        self.assertTrue(fn(self.cg.ARCHETYPE_SNARE, 'string_lash'))
        # Dedicated Overlord counters stay move-gated; Smudge counters are
        # covered by test_ink_smudge_counter_windows.py (shared helper).
        self.assertTrue(
            self.cg.isDedicatedTelegraphCounterMove(ink, 'rain'))
        self.assertTrue(
            self.cg.isDedicatedTelegraphCounterMove(ink, 'slam'))
        self.assertTrue(
            self.cg.isDedicatedTelegraphCounterMove(ink, 'ink_surge'))
        self.assertTrue(
            self.cg.isDedicatedTelegraphCounterMove(ink, 'ink_dash'))

    def test_helper_respects_disable_flags(self):
        fn = self.cg.isMeleeInterruptibleTelegraph
        ink = self.cg.ARCHETYPE_INK
        prev_r = self.cg.OVERLORD_RAIN_MELEE_INTERRUPT
        prev_s = self.cg.OVERLORD_SLAM_MELEE_INTERRUPT
        prev_g = self.cg.OVERLORD_INK_SURGE_MELEE_INTERRUPT
        try:
            self.cg.OVERLORD_RAIN_MELEE_INTERRUPT = False
            self.assertFalse(fn(ink, 'rain'))
            self.assertTrue(fn(ink, 'slam'))
            self.cg.OVERLORD_SLAM_MELEE_INTERRUPT = False
            self.assertFalse(fn(ink, 'slam'))
            self.cg.OVERLORD_INK_SURGE_MELEE_INTERRUPT = False
            self.assertFalse(fn(ink, 'ink_surge'))
        finally:
            self.cg.OVERLORD_RAIN_MELEE_INTERRUPT = prev_r
            self.cg.OVERLORD_SLAM_MELEE_INTERRUPT = prev_s
            self.cg.OVERLORD_INK_SURGE_MELEE_INTERRUPT = prev_g
        self.assertTrue(fn(ink, 'rain'))
        self.assertTrue(fn(ink, 'slam'))
        self.assertTrue(fn(ink, 'ink_surge'))

    def test_ai_melee_interrupt_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        self.assertIn('__maybeInterruptMeleeTelegraph', methods)
        src = _read(rel)
        self.assertIn('isMeleeInterruptibleTelegraph', src)
        take = _method_source(
            rel, 'DistributedCorruptToonAI', 'takeHackSlashDamage')
        self.assertIn('__maybeInterruptMeleeTelegraph', take)
        # takeHackSlashDamage comment names Overlord climax moves.
        take_l = take.lower()
        self.assertIn('rain', take_l)
        self.assertIn('slam', take_l)
        interrupt = _method_source(
            rel, 'DistributedCorruptToonAI', '__maybeInterruptMeleeTelegraph')
        self.assertIn('isMeleeInterruptibleTelegraph', interrupt)
        self.assertIn('corrupt-attack', interrupt)
        # Shared path still clears street aim snapshots; Overlord uses same.
        self.assertIn('_spitAimXY', interrupt)
        self.assertIn('_puddleXY', interrupt)
        # Must not clear linger sludge from the interrupt path.
        self.assertNotIn('_puddleLinger', interrupt)
        self.assertNotIn('__clearGagsterPuddleLinger', interrupt)
        interrupt_l = interrupt.lower()
        self.assertNotIn('cream', interrupt_l)
        self.assertNotIn('keyblade', interrupt_l)
        self.assertNotIn('kingdom hearts', interrupt_l)

    def test_reclaim_docs_mention_overlord_interrupt(self):
        reclaim = _read('toontown/corruption/RECLAIM.md')
        reclaim_l = reclaim.lower()
        self.assertIn('overlord_rain_melee_interrupt', reclaim_l)
        self.assertIn('overlord_slam_melee_interrupt', reclaim_l)
        self.assertIn('overlord_ink_surge_melee_interrupt', reclaim_l)
        self.assertIn('mid-rain', reclaim_l)
        self.assertIn('mid-slam', reclaim_l)
        for line in reclaim.splitlines():
            low = line.lower()
            if ('overlord_rain_melee_interrupt' in low
                    or 'overlord_slam_melee_interrupt' in low
                    or 'overlord_ink_surge_melee_interrupt' in low
                    or 'mid-rain' in low or 'mid-slam' in low):
                self.assertNotIn('keyblade', low)
                self.assertNotIn('kingdom hearts', low)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        MeleeInterruptOverlordTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
