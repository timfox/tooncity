#!/usr/bin/env python3
"""Headless tests for Ink Smudge ink_dash / ink_splat melee interrupt.

Loads CorruptionGlobals without Panda3D. Asserts Smudge interrupt tunables
+ isMeleeInterruptibleTelegraph for swarm move ids, and AI wiring on
DistributedCorruptToonAI (__maybeInterruptMeleeTelegraph from
takeHackSlashDamage). Extends Snare/Brute/Gagster/Overlord/Oswald
mid-telegraph cancel to the Act 1 / P2-add kit. No cream FX, no KH.

Run from repo root:
  python3 tests/test_melee_interrupt_ink_smudge.py
  python3 -m unittest tests.test_melee_interrupt_ink_smudge -v
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


class MeleeInterruptInkSmudgeTest(unittest.TestCase):
    """Ink Smudge ink_dash / ink_splat melee interrupt tunables + AI wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_interrupt_globals_armed(self):
        self.assertTrue(self.cg.INK_DASH_MELEE_INTERRUPT)
        self.assertTrue(self.cg.INK_SPLAT_MELEE_INTERRUPT)
        # Street / Overlord / Oswald flags stay armed — shared AI path.
        self.assertTrue(self.cg.BRUTE_SPIT_MELEE_INTERRUPT)
        self.assertTrue(self.cg.GAGSTER_LOB_MELEE_INTERRUPT)
        self.assertTrue(self.cg.OVERLORD_RAIN_MELEE_INTERRUPT)
        self.assertTrue(self.cg.OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT)
        blob = ' '.join([
            'INK_DASH_MELEE_INTERRUPT',
            'INK_SPLAT_MELEE_INTERRUPT',
            'isMeleeInterruptibleTelegraph',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_helper_allows_ink_dash_and_splat(self):
        fn = self.cg.isMeleeInterruptibleTelegraph
        ink = self.cg.ARCHETYPE_INK
        self.assertTrue(fn(ink, 'ink_dash'))
        self.assertTrue(fn(ink, 'ink_splat'))
        # Overlord climax move ids still interruptible on same archetype.
        self.assertTrue(fn(ink, 'rain'))
        self.assertTrue(fn(ink, 'slam'))
        self.assertTrue(fn(ink, 'ink_surge'))
        # smack stays non-Smudge (kit always resolves to ink_dash/ink_splat).
        self.assertFalse(fn(ink, 'smack'))
        # Street / Oswald still interruptible.
        self.assertTrue(fn(self.cg.ARCHETYPE_BRUTE, 'spit'))
        self.assertTrue(fn(self.cg.ARCHETYPE_GAGSTER, 'gag_lob'))
        self.assertTrue(fn(self.cg.ARCHETYPE_SNARE, 'string_lash'))
        self.assertTrue(fn(
            self.cg.ARCHETYPE_CORRUPT_OSWALD, 'betrayal_lunge'))

    def test_helper_respects_disable_flags(self):
        fn = self.cg.isMeleeInterruptibleTelegraph
        ink = self.cg.ARCHETYPE_INK
        prev_d = self.cg.INK_DASH_MELEE_INTERRUPT
        prev_s = self.cg.INK_SPLAT_MELEE_INTERRUPT
        try:
            self.cg.INK_DASH_MELEE_INTERRUPT = False
            self.assertFalse(fn(ink, 'ink_dash'))
            self.assertTrue(fn(ink, 'ink_splat'))
            self.cg.INK_SPLAT_MELEE_INTERRUPT = False
            self.assertFalse(fn(ink, 'ink_splat'))
            # Overlord rain unaffected by Smudge flags.
            self.assertTrue(fn(ink, 'rain'))
        finally:
            self.cg.INK_DASH_MELEE_INTERRUPT = prev_d
            self.cg.INK_SPLAT_MELEE_INTERRUPT = prev_s
        self.assertTrue(fn(ink, 'ink_dash'))
        self.assertTrue(fn(ink, 'ink_splat'))

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
        self.assertIn('ink_dash', take_l)
        self.assertIn('ink_splat', take_l)
        interrupt = _method_source(
            rel, 'DistributedCorruptToonAI', '__maybeInterruptMeleeTelegraph')
        self.assertIn('isMeleeInterruptibleTelegraph', interrupt)
        self.assertIn('corrupt-attack', interrupt)
        interrupt_l = interrupt.lower()
        self.assertNotIn('cream', interrupt_l)
        self.assertNotIn('keyblade', interrupt_l)
        self.assertNotIn('kingdom hearts', interrupt_l)

    def test_reclaim_docs_mention_smudge_interrupt(self):
        reclaim = _read('toontown/corruption/RECLAIM.md')
        reclaim_l = reclaim.lower()
        self.assertIn('ink_dash_melee_interrupt', reclaim_l)
        self.assertIn('ink_splat_melee_interrupt', reclaim_l)
        self.assertIn('mid-ink_dash', reclaim_l)
        self.assertIn('mid-ink_splat', reclaim_l)
        for line in reclaim.splitlines():
            low = line.lower()
            if ('ink_dash_melee_interrupt' in low
                    or 'ink_splat_melee_interrupt' in low
                    or 'mid-ink_dash' in low
                    or 'mid-ink_splat' in low):
                self.assertNotIn('keyblade', low)
                self.assertNotIn('kingdom hearts', low)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        MeleeInterruptInkSmudgeTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
