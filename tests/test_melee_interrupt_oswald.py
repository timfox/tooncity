#!/usr/bin/env python3
"""Headless tests for Oswald betrayal_lunge / stain_burst melee interrupt.

Loads CorruptionGlobals without Panda3D. Asserts Oswald interrupt tunables
+ isMeleeInterruptibleTelegraph for twist chase move ids, and AI wiring on
DistributedCorruptToonAI (__maybeInterruptMeleeTelegraph from
takeHackSlashDamage). Extends Snare/Brute/Gagster mid-telegraph cancel to
the betrayal kit. No cream FX, no KH.

Run from repo root:
  python3 tests/test_melee_interrupt_oswald.py
  python3 -m unittest tests.test_melee_interrupt_oswald -v
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


class MeleeInterruptOswaldTest(unittest.TestCase):
    """Oswald betrayal_lunge / stain_burst melee interrupt tunables + AI wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_interrupt_globals_armed(self):
        self.assertTrue(self.cg.OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT)
        self.assertTrue(self.cg.OSWALD_STAIN_BURST_MELEE_INTERRUPT)
        # Street / Overlord flags stay armed — shared AI path.
        self.assertTrue(self.cg.BRUTE_SPIT_MELEE_INTERRUPT)
        self.assertTrue(self.cg.GAGSTER_LOB_MELEE_INTERRUPT)
        self.assertTrue(self.cg.OVERLORD_RAIN_MELEE_INTERRUPT)
        blob = ' '.join([
            'OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT',
            'OSWALD_STAIN_BURST_MELEE_INTERRUPT',
            'isMeleeInterruptibleTelegraph',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_helper_allows_oswald_lunge_and_burst(self):
        fn = self.cg.isMeleeInterruptibleTelegraph
        oswald = self.cg.ARCHETYPE_CORRUPT_OSWALD
        self.assertTrue(fn(oswald, 'betrayal_lunge'))
        self.assertTrue(fn(oswald, 'stain_burst'))
        # smack aliases the default lunge wind-up.
        self.assertTrue(fn(oswald, 'smack'))
        # Smudge kit stays commit-through.
        ink = self.cg.ARCHETYPE_INK
        self.assertFalse(fn(ink, 'ink_dash'))
        self.assertFalse(fn(ink, 'ink_splat'))
        # Street / Overlord still interruptible.
        self.assertTrue(fn(self.cg.ARCHETYPE_BRUTE, 'spit'))
        self.assertTrue(fn(self.cg.ARCHETYPE_GAGSTER, 'gag_lob'))
        self.assertTrue(fn(self.cg.ARCHETYPE_SNARE, 'string_lash'))
        self.assertTrue(fn(ink, 'rain'))

    def test_helper_respects_disable_flags(self):
        fn = self.cg.isMeleeInterruptibleTelegraph
        oswald = self.cg.ARCHETYPE_CORRUPT_OSWALD
        prev_l = self.cg.OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT
        prev_b = self.cg.OSWALD_STAIN_BURST_MELEE_INTERRUPT
        try:
            self.cg.OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT = False
            self.assertFalse(fn(oswald, 'betrayal_lunge'))
            self.assertTrue(fn(oswald, 'stain_burst'))
            self.cg.OSWALD_STAIN_BURST_MELEE_INTERRUPT = False
            self.assertFalse(fn(oswald, 'stain_burst'))
        finally:
            self.cg.OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT = prev_l
            self.cg.OSWALD_STAIN_BURST_MELEE_INTERRUPT = prev_b
        self.assertTrue(fn(oswald, 'betrayal_lunge'))
        self.assertTrue(fn(oswald, 'stain_burst'))

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
        take_l = take.lower()
        self.assertIn('betrayal_lunge', take_l)
        self.assertIn('stain_burst', take_l)
        interrupt = _method_source(
            rel, 'DistributedCorruptToonAI', '__maybeInterruptMeleeTelegraph')
        self.assertIn('isMeleeInterruptibleTelegraph', interrupt)
        self.assertIn('corrupt-attack', interrupt)
        self.assertIn('_spitAimXY', interrupt)
        self.assertIn('_puddleXY', interrupt)
        self.assertNotIn('_puddleLinger', interrupt)
        interrupt_l = interrupt.lower()
        self.assertNotIn('cream', interrupt_l)
        self.assertNotIn('keyblade', interrupt_l)
        self.assertNotIn('kingdom hearts', interrupt_l)

    def test_reclaim_docs_mention_oswald_interrupt(self):
        reclaim = _read('toontown/corruption/RECLAIM.md')
        reclaim_l = reclaim.lower()
        self.assertIn('oswald_betrayal_lunge_melee_interrupt', reclaim_l)
        self.assertIn('oswald_stain_burst_melee_interrupt', reclaim_l)
        self.assertIn('mid-betrayal_lunge', reclaim_l)
        self.assertIn('mid-stain_burst', reclaim_l)
        for line in reclaim.splitlines():
            low = line.lower()
            if ('oswald_betrayal_lunge_melee_interrupt' in low
                    or 'oswald_stain_burst_melee_interrupt' in low
                    or 'mid-betrayal_lunge' in low
                    or 'mid-stain_burst' in low):
                self.assertNotIn('keyblade', low)
                self.assertNotIn('kingdom hearts', low)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        MeleeInterruptOswaldTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
