#!/usr/bin/env python3
"""Headless tests for Brute spit / Gagster lob dedicated counter windows.

Loads CorruptionGlobals without Panda3D. Asserts Snare-like counter tunables
+ pure helpers, client schedule hooks on DistributedCorruptToon, and
MeleeCombat listener wiring. Beyond #329 interrupt cancel — these are
dedicated telegraph punish→melee windows (no cream deepen, no KH).

Run from repo root:
  python3 tests/test_brute_gagster_counter_windows.py
  python3 -m unittest tests.test_brute_gagster_counter_windows -v
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


class BruteGagsterCounterWindowsTest(unittest.TestCase):
    """Brute spit / Gagster lob dedicated counter tunables + wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_counter_globals_armed(self):
        self.assertTrue(self.cg.BRUTE_SPIT_COUNTER_ENABLED)
        self.assertTrue(self.cg.GAGSTER_LOB_COUNTER_ENABLED)
        self.assertGreater(self.cg.BRUTE_SPIT_COUNTER_ARM_DELAY_SEC, 0.0)
        self.assertGreater(self.cg.BRUTE_SPIT_COUNTER_WINDOW_SEC, 0.0)
        self.assertGreater(self.cg.BRUTE_SPIT_COUNTER_RANGE, 0.0)
        self.assertGreater(self.cg.BRUTE_SPIT_COUNTER_DAMAGE_MULT, 1.0)
        self.assertGreater(self.cg.BRUTE_SPIT_COUNTER_RATE_MULT, 1.0)
        self.assertGreater(self.cg.GAGSTER_LOB_COUNTER_ARM_DELAY_SEC, 0.0)
        self.assertGreater(self.cg.GAGSTER_LOB_COUNTER_WINDOW_SEC, 0.0)
        self.assertGreater(self.cg.GAGSTER_LOB_COUNTER_RANGE, 0.0)
        self.assertGreater(self.cg.GAGSTER_LOB_COUNTER_DAMAGE_MULT, 1.0)
        self.assertGreater(self.cg.GAGSTER_LOB_COUNTER_RATE_MULT, 1.0)
        # Arm delay fits inside each kit's telegraph beat.
        brute = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_BRUTE]
        gagster = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_GAGSTER]
        brute_tele = float(brute.get(
            'telegraphDelay', self.cg.ATTACK_TELEGRAPH_DELAY))
        gag_tele = float(gagster.get(
            'telegraphDelay', self.cg.ATTACK_TELEGRAPH_DELAY))
        self.assertLessEqual(
            self.cg.BRUTE_SPIT_COUNTER_ARM_DELAY_SEC, brute_tele + 0.05)
        self.assertLessEqual(
            self.cg.GAGSTER_LOB_COUNTER_ARM_DELAY_SEC, gag_tele + 0.05)
        self.assertEqual(
            self.cg.BRUTE_SPIT_COUNTER_EVENT, 'corruptBruteSpitCounter')
        self.assertEqual(
            self.cg.GAGSTER_LOB_COUNTER_EVENT, 'corruptGagsterLobCounter')
        # Distinct from Snare event; no KH branding.
        self.assertNotEqual(
            self.cg.BRUTE_SPIT_COUNTER_EVENT,
            self.cg.SNARE_STRING_COUNTER_EVENT)
        self.assertNotEqual(
            self.cg.GAGSTER_LOB_COUNTER_EVENT,
            self.cg.SNARE_STRING_COUNTER_EVENT)
        for event in (
                self.cg.BRUTE_SPIT_COUNTER_EVENT,
                self.cg.GAGSTER_LOB_COUNTER_EVENT):
            low = event.lower()
            self.assertNotIn('keyblade', low)
            self.assertNotIn('kingdom hearts', low)
            self.assertNotIn('cream', low)

    def test_dedicated_counter_move_helper(self):
        fn = self.cg.isDedicatedTelegraphCounterMove
        snare = self.cg.ARCHETYPE_SNARE
        brute = self.cg.ARCHETYPE_BRUTE
        gagster = self.cg.ARCHETYPE_GAGSTER
        ink = self.cg.ARCHETYPE_INK
        self.assertTrue(fn(snare, 'smack'))
        self.assertTrue(fn(snare, 'string_lash'))
        self.assertTrue(fn(brute, 'spit'))
        self.assertFalse(fn(brute, 'slam'))
        self.assertFalse(fn(brute, 'smack'))
        self.assertTrue(fn(gagster, 'gag_lob'))
        self.assertFalse(fn(gagster, 'smack'))
        self.assertFalse(fn(ink, 'ink_dash'))
        self.assertFalse(fn(ink, 'rain'))
        # Oswald betrayal counters are covered by test_oswald_counter_windows.py.
        # Disable flags respected.
        prev_b = self.cg.BRUTE_SPIT_COUNTER_ENABLED
        prev_g = self.cg.GAGSTER_LOB_COUNTER_ENABLED
        prev_s = self.cg.SNARE_STRING_COUNTER_ENABLED
        try:
            self.cg.BRUTE_SPIT_COUNTER_ENABLED = False
            self.assertFalse(fn(brute, 'spit'))
            self.cg.GAGSTER_LOB_COUNTER_ENABLED = False
            self.assertFalse(fn(gagster, 'gag_lob'))
            self.cg.SNARE_STRING_COUNTER_ENABLED = False
            self.assertFalse(fn(snare, 'smack'))
        finally:
            self.cg.BRUTE_SPIT_COUNTER_ENABLED = prev_b
            self.cg.GAGSTER_LOB_COUNTER_ENABLED = prev_g
            self.cg.SNARE_STRING_COUNTER_ENABLED = prev_s
        self.assertTrue(fn(brute, 'spit'))
        self.assertTrue(fn(gagster, 'gag_lob'))
        self.assertTrue(fn(snare, 'smack'))

    def test_brute_opener_helpers(self):
        dmg = self.cg.bruteSpitCounterOpenerDamage
        rate_fn = self.cg.bruteSpitCounterOpenerRate
        self.assertEqual(
            dmg(8),
            max(1, int(round(8 * self.cg.BRUTE_SPIT_COUNTER_DAMAGE_MULT))))
        self.assertEqual(dmg(8, 1.5), 12)
        self.assertEqual(dmg(0, 2.0), 1)
        self.assertAlmostEqual(
            rate_fn(1.0), 1.0 * self.cg.BRUTE_SPIT_COUNTER_RATE_MULT)
        self.assertAlmostEqual(rate_fn(2.0, 1.25), 2.5)
        open_fn = self.cg.isBruteSpitCounterWindowOpen
        self.assertFalse(open_fn(False, 1.0, 0.5))
        self.assertTrue(open_fn(True, 1.0, 0.5))
        self.assertFalse(open_fn(True, 1.0, 1.0))
        arm_at = self.cg.bruteSpitCounterArmAt
        until = self.cg.bruteSpitCounterUntil
        now = 10.0
        armed = arm_at(now)
        self.assertAlmostEqual(
            armed, now + self.cg.BRUTE_SPIT_COUNTER_ARM_DELAY_SEC)
        self.assertAlmostEqual(
            until(armed),
            armed + self.cg.BRUTE_SPIT_COUNTER_WINDOW_SEC)

    def test_gagster_opener_helpers(self):
        dmg = self.cg.gagsterLobCounterOpenerDamage
        rate_fn = self.cg.gagsterLobCounterOpenerRate
        self.assertEqual(
            dmg(8),
            max(1, int(round(8 * self.cg.GAGSTER_LOB_COUNTER_DAMAGE_MULT))))
        self.assertEqual(dmg(8, 1.5), 12)
        self.assertAlmostEqual(
            rate_fn(1.0), 1.0 * self.cg.GAGSTER_LOB_COUNTER_RATE_MULT)
        open_fn = self.cg.isGagsterLobCounterWindowOpen
        self.assertTrue(open_fn(True, 1.0, 0.5))
        self.assertFalse(open_fn(True, 1.0, 1.1))
        arm_at = self.cg.gagsterLobCounterArmAt
        until = self.cg.gagsterLobCounterUntil
        now = 5.0
        armed = arm_at(now)
        self.assertAlmostEqual(
            armed, now + self.cg.GAGSTER_LOB_COUNTER_ARM_DELAY_SEC)
        self.assertAlmostEqual(
            until(armed),
            armed + self.cg.GAGSTER_LOB_COUNTER_WINDOW_SEC)

    def test_client_schedule_hooks(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        methods = _class_method_names(
            _module_ast(rel), 'DistributedCorruptToon')
        for name in (
                '__scheduleBruteSpitCounter',
                '__clearBruteSpitCounter',
                '__scheduleGagsterLobCounter',
                '__clearGagsterLobCounter',
                '__scheduleSnareStringSnapCounter'):
            self.assertIn(name, methods)
        telegraph = _method_source(
            rel, 'DistributedCorruptToon', 'announceAttackTelegraph')
        self.assertIn('__scheduleBruteSpitCounter', telegraph)
        self.assertIn('__scheduleGagsterLobCounter', telegraph)
        self.assertIn("telegraphMove == 'spit'", telegraph)
        self.assertIn('gag_lob', telegraph)
        # Slam must not arm the spit counter.
        brute_sched = _method_source(
            rel, 'DistributedCorruptToon', '__scheduleBruteSpitCounter')
        self.assertIn('BRUTE_SPIT_COUNTER_ENABLED', brute_sched)
        self.assertIn('corruptBruteSpitCounter', brute_sched)
        self.assertNotIn('cream', brute_sched.lower())
        self.assertNotIn('keyblade', brute_sched.lower())
        gag_sched = _method_source(
            rel, 'DistributedCorruptToon', '__scheduleGagsterLobCounter')
        self.assertIn('GAGSTER_LOB_COUNTER_ENABLED', gag_sched)
        self.assertIn('corruptGagsterLobCounter', gag_sched)
        self.assertNotIn('cream', gag_sched.lower())
        self.assertNotIn('keyblade', gag_sched.lower())

    def test_melee_listener_wiring(self):
        rel = 'toontown/hackslash/MeleeCombat.py'
        methods = _class_method_names(
            _module_ast(rel), 'MeleeCombatController')
        self.assertIn('_onBruteSpitCounter', methods)
        self.assertIn('_onGagsterLobCounter', methods)
        self.assertIn('_onSnareStringSnapCounter', methods)
        self.assertIn('_armTelegraphCounterWindow', methods)
        src = _read(rel)
        self.assertIn('corruptBruteSpitCounter', src)
        self.assertIn('corruptGagsterLobCounter', src)
        self.assertIn('BRUTE_SPIT_COUNTER_RANGE', src)
        self.assertIn('GAGSTER_LOB_COUNTER_RANGE', src)
        arm = _method_source(
            rel, 'MeleeCombatController', '_armTelegraphCounterWindow')
        self.assertIn('_armPerfectDodgeCounterWindow', arm)
        # No cream / KH branding in the shared arm path.
        arm_l = arm.lower()
        self.assertNotIn('cream', arm_l)
        self.assertNotIn('keyblade', arm_l)
        self.assertNotIn('kingdom hearts', arm_l)
        hint = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('Brute spit→F counter', hint)
        self.assertIn('Gagster lob→F counter', hint)

    def test_docs_mention_counters(self):
        reclaim = _read('toontown/corruption/RECLAIM.md')
        reclaim_l = reclaim.lower()
        self.assertIn('dedicated spit counter', reclaim_l)
        self.assertIn('dedicated lob counter', reclaim_l)
        self.assertIn('brute_spit_counter', reclaim_l)
        self.assertIn('gagster_lob_counter', reclaim_l)
        init_src = _read('toontown/corruption/__init__.py')
        self.assertIn('BRUTE_SPIT_COUNTER_', init_src)
        self.assertIn('GAGSTER_LOB_COUNTER_', init_src)
        self.assertIn('interrupt ≠ counter', init_src)
        # New counter copy stays Toontown — no KH branding on those lines.
        for line in reclaim.splitlines():
            low = line.lower()
            if 'dedicated spit counter' in low or 'dedicated lob counter' in low:
                self.assertNotIn('keyblade', low)
                self.assertNotIn('kingdom hearts', low)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        BruteGagsterCounterWindowsTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
