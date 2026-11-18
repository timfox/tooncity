#!/usr/bin/env python3
"""Headless tests for Brute spit / Gagster lob melee interrupt windows.

Loads CorruptionGlobals without Panda3D. Asserts interrupt tunables + pure
isMeleeInterruptibleTelegraph helper, and AI wiring on
DistributedCorruptToonAI (__maybeInterruptMeleeTelegraph from
takeHackSlashDamage). Extends snare-style mid-telegraph cancel for Punchline
kits — not cream FX. Overlord rain/slam/surge interrupt lives in
test_melee_interrupt_overlord.py. Dedicated counter windows live in
test_brute_gagster_counter_windows.py.

Run from repo root:
  python3 tests/test_melee_interrupt_brute_gagster.py
  python3 -m unittest tests.test_melee_interrupt_brute_gagster -v
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


class MeleeInterruptBruteGagsterTest(unittest.TestCase):
    """Brute spit / Gagster lob melee interrupt tunables + AI wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_interrupt_globals_armed(self):
        self.assertTrue(self.cg.SNARE_STRING_COUNTER_INTERRUPT)
        self.assertTrue(self.cg.BRUTE_SPIT_MELEE_INTERRUPT)
        self.assertTrue(self.cg.GAGSTER_LOB_MELEE_INTERRUPT)
        blob = ' '.join([
            'BRUTE_SPIT_MELEE_INTERRUPT',
            'GAGSTER_LOB_MELEE_INTERRUPT',
            'isMeleeInterruptibleTelegraph',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_helper_allows_snare_brute_spit_gagster_lob(self):
        fn = self.cg.isMeleeInterruptibleTelegraph
        snare = self.cg.ARCHETYPE_SNARE
        brute = self.cg.ARCHETYPE_BRUTE
        gagster = self.cg.ARCHETYPE_GAGSTER
        ink = self.cg.ARCHETYPE_INK
        # Snare — any string telegraph.
        self.assertTrue(fn(snare, 'smack'))
        self.assertTrue(fn(snare, 'string_lash'))
        # Brute spit yes; slam no (commit-through tank secondary).
        self.assertTrue(fn(brute, 'spit'))
        self.assertFalse(fn(brute, 'slam'))
        self.assertFalse(fn(brute, 'smack'))
        # Gagster lob yes.
        self.assertTrue(fn(gagster, 'gag_lob'))
        self.assertFalse(fn(gagster, 'smack'))
        # Smudge dash/splat stay commit-through here.
        # Overlord rain/slam/surge interrupt is covered by
        # test_melee_interrupt_overlord.py; Oswald betrayal interrupt by
        # test_melee_interrupt_oswald.py (shared helper).
        self.assertFalse(fn(ink, 'ink_dash'))
        self.assertFalse(fn(ink, 'ink_splat'))

    def test_helper_respects_disable_flags(self):
        fn = self.cg.isMeleeInterruptibleTelegraph
        brute = self.cg.ARCHETYPE_BRUTE
        gagster = self.cg.ARCHETYPE_GAGSTER
        snare = self.cg.ARCHETYPE_SNARE
        prev_b = self.cg.BRUTE_SPIT_MELEE_INTERRUPT
        prev_g = self.cg.GAGSTER_LOB_MELEE_INTERRUPT
        prev_s = self.cg.SNARE_STRING_COUNTER_INTERRUPT
        try:
            self.cg.BRUTE_SPIT_MELEE_INTERRUPT = False
            self.assertFalse(fn(brute, 'spit'))
            self.cg.GAGSTER_LOB_MELEE_INTERRUPT = False
            self.assertFalse(fn(gagster, 'gag_lob'))
            self.cg.SNARE_STRING_COUNTER_INTERRUPT = False
            self.assertFalse(fn(snare, 'smack'))
        finally:
            self.cg.BRUTE_SPIT_MELEE_INTERRUPT = prev_b
            self.cg.GAGSTER_LOB_MELEE_INTERRUPT = prev_g
            self.cg.SNARE_STRING_COUNTER_INTERRUPT = prev_s
        self.assertTrue(fn(brute, 'spit'))
        self.assertTrue(fn(gagster, 'gag_lob'))
        self.assertTrue(fn(snare, 'smack'))

    def test_ai_melee_interrupt_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        self.assertIn('__maybeInterruptMeleeTelegraph', methods)
        self.assertNotIn('__maybeInterruptSnareTelegraph', methods)
        src = _read(rel)
        self.assertIn('isMeleeInterruptibleTelegraph', src)
        self.assertIn('__maybeInterruptMeleeTelegraph', src)
        take = _method_source(
            rel, 'DistributedCorruptToonAI', 'takeHackSlashDamage')
        self.assertIn('__maybeInterruptMeleeTelegraph', take)
        interrupt = _method_source(
            rel, 'DistributedCorruptToonAI', '__maybeInterruptMeleeTelegraph')
        self.assertIn('_spitAimXY', interrupt)
        self.assertIn('_puddleXY', interrupt)
        self.assertIn('corrupt-attack', interrupt)
        # Must not clear linger sludge from the interrupt path.
        self.assertNotIn('_puddleLinger', interrupt)
        self.assertNotIn('__clearGagsterPuddleLinger', interrupt)
        # No cream / KH branding in the AI interrupt path.
        interrupt_l = interrupt.lower()
        self.assertNotIn('cream', interrupt_l)
        self.assertNotIn('keyblade', interrupt_l)
        self.assertNotIn('kingdom hearts', interrupt_l)

    def test_reclaim_docs_mention_interrupt(self):
        reclaim = _read('toontown/corruption/RECLAIM.md')
        reclaim_l = reclaim.lower()
        self.assertIn('mid-spit-telegraph', reclaim_l)
        self.assertIn('mid-lob', reclaim_l)
        self.assertIn('melee mid-telegraph interrupts', reclaim_l)
        self.assertIn('shared ai path with brute spit / gagster lob', reclaim_l)
        # New interrupt copy stays Toontown — no KH branding in those lines.
        for line in reclaim.splitlines():
            low = line.lower()
            if ('mid-spit-telegraph' in low or 'mid-lob' in low
                    or 'shared ai path with brute spit' in low):
                self.assertNotIn('keyblade', low)
                self.assertNotIn('kingdom hearts', low)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        MeleeInterruptBruteGagsterTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
