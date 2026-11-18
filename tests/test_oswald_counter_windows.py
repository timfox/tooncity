#!/usr/bin/env python3
"""Headless tests for Oswald betrayal_lunge / stain_burst dedicated counters.

Loads CorruptionGlobals without Panda3D. Asserts Snare-like counter tunables
+ pure helpers, client schedule hooks on DistributedCorruptToon, and
MeleeCombat listener wiring. Beyond interrupt cancel — these are dedicated
telegraph punish→melee windows (no cream deepen, no KH).

Run from repo root:
  python3 tests/test_oswald_counter_windows.py
  python3 -m unittest tests.test_oswald_counter_windows -v
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


class OswaldCounterWindowsTest(unittest.TestCase):
    """Oswald betrayal_lunge / stain_burst dedicated counter tunables + wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_counter_globals_armed(self):
        self.assertTrue(self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED)
        self.assertTrue(self.cg.OSWALD_STAIN_BURST_COUNTER_ENABLED)
        self.assertGreater(
            self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_ARM_DELAY_SEC, 0.0)
        self.assertGreater(
            self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_WINDOW_SEC, 0.0)
        self.assertGreater(self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_RANGE, 0.0)
        self.assertGreater(
            self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_DAMAGE_MULT, 1.0)
        self.assertGreater(
            self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_RATE_MULT, 1.0)
        self.assertGreater(
            self.cg.OSWALD_STAIN_BURST_COUNTER_ARM_DELAY_SEC, 0.0)
        self.assertGreater(self.cg.OSWALD_STAIN_BURST_COUNTER_WINDOW_SEC, 0.0)
        self.assertGreater(self.cg.OSWALD_STAIN_BURST_COUNTER_RANGE, 0.0)
        self.assertGreater(
            self.cg.OSWALD_STAIN_BURST_COUNTER_DAMAGE_MULT, 1.0)
        self.assertGreater(self.cg.OSWALD_STAIN_BURST_COUNTER_RATE_MULT, 1.0)
        # Arm delay fits inside each Oswald telegraph beat.
        oswald = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        lunge_tele = float(oswald.get(
            'telegraphDelay', self.cg.ATTACK_TELEGRAPH_DELAY))
        burst_tele = float(oswald.get(
            'burstTelegraphDelay', oswald.get('telegraphDelay', 0.32)))
        self.assertLessEqual(
            self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_ARM_DELAY_SEC,
            lunge_tele + 0.05)
        self.assertLessEqual(
            self.cg.OSWALD_STAIN_BURST_COUNTER_ARM_DELAY_SEC,
            burst_tele + 0.05)
        self.assertEqual(
            self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_EVENT,
            'corruptOswaldBetrayalLungeCounter')
        self.assertEqual(
            self.cg.OSWALD_STAIN_BURST_COUNTER_EVENT,
            'corruptOswaldStainBurstCounter')
        # Distinct from Snare / Brute / Gagster events; no KH / cream branding.
        for event in (
                self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_EVENT,
                self.cg.OSWALD_STAIN_BURST_COUNTER_EVENT):
            self.assertNotEqual(event, self.cg.SNARE_STRING_COUNTER_EVENT)
            self.assertNotEqual(event, self.cg.BRUTE_SPIT_COUNTER_EVENT)
            self.assertNotEqual(event, self.cg.GAGSTER_LOB_COUNTER_EVENT)
            low = event.lower()
            self.assertNotIn('keyblade', low)
            self.assertNotIn('kingdom hearts', low)
            self.assertNotIn('cream', low)

    def test_dedicated_counter_move_helper(self):
        fn = self.cg.isDedicatedTelegraphCounterMove
        oswald = self.cg.ARCHETYPE_CORRUPT_OSWALD
        self.assertTrue(fn(oswald, 'betrayal_lunge'))
        self.assertTrue(fn(oswald, 'stain_burst'))
        self.assertTrue(fn(oswald, 'smack'))
        # Street kits still covered.
        self.assertTrue(fn(self.cg.ARCHETYPE_BRUTE, 'spit'))
        self.assertTrue(fn(self.cg.ARCHETYPE_GAGSTER, 'gag_lob'))
        self.assertTrue(fn(self.cg.ARCHETYPE_SNARE, 'smack'))
        # Overlord climax counters are covered by test_overlord_counter_windows.py.
        # Smudge kit stays without dedicated counters.
        self.assertTrue(fn(self.cg.ARCHETYPE_INK, 'rain'))
        self.assertFalse(fn(self.cg.ARCHETYPE_INK, 'ink_dash'))
        self.assertFalse(fn(self.cg.ARCHETYPE_BRUTE, 'slam'))
        # Disable flags respected.
        prev_l = self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED
        prev_b = self.cg.OSWALD_STAIN_BURST_COUNTER_ENABLED
        try:
            self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED = False
            self.assertFalse(fn(oswald, 'betrayal_lunge'))
            self.cg.OSWALD_STAIN_BURST_COUNTER_ENABLED = False
            self.assertFalse(fn(oswald, 'stain_burst'))
        finally:
            self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED = prev_l
            self.cg.OSWALD_STAIN_BURST_COUNTER_ENABLED = prev_b
        self.assertTrue(fn(oswald, 'betrayal_lunge'))
        self.assertTrue(fn(oswald, 'stain_burst'))

    def test_lunge_opener_helpers(self):
        dmg = self.cg.oswaldBetrayalLungeCounterOpenerDamage
        rate_fn = self.cg.oswaldBetrayalLungeCounterOpenerRate
        self.assertEqual(
            dmg(8),
            max(1, int(round(
                8 * self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_DAMAGE_MULT))))
        self.assertEqual(dmg(8, 1.5), 12)
        self.assertEqual(dmg(0, 2.0), 1)
        self.assertAlmostEqual(
            rate_fn(1.0),
            1.0 * self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_RATE_MULT)
        self.assertAlmostEqual(rate_fn(2.0, 1.25), 2.5)
        open_fn = self.cg.isOswaldBetrayalLungeCounterWindowOpen
        self.assertFalse(open_fn(False, 1.0, 0.5))
        self.assertTrue(open_fn(True, 1.0, 0.5))
        self.assertFalse(open_fn(True, 1.0, 1.0))
        arm_at = self.cg.oswaldBetrayalLungeCounterArmAt
        until = self.cg.oswaldBetrayalLungeCounterUntil
        now = 10.0
        armed = arm_at(now)
        self.assertAlmostEqual(
            armed,
            now + self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_ARM_DELAY_SEC)
        self.assertAlmostEqual(
            until(armed),
            armed + self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_WINDOW_SEC)

    def test_burst_opener_helpers(self):
        dmg = self.cg.oswaldStainBurstCounterOpenerDamage
        rate_fn = self.cg.oswaldStainBurstCounterOpenerRate
        self.assertEqual(
            dmg(8),
            max(1, int(round(
                8 * self.cg.OSWALD_STAIN_BURST_COUNTER_DAMAGE_MULT))))
        self.assertEqual(dmg(8, 1.5), 12)
        self.assertAlmostEqual(
            rate_fn(1.0),
            1.0 * self.cg.OSWALD_STAIN_BURST_COUNTER_RATE_MULT)
        open_fn = self.cg.isOswaldStainBurstCounterWindowOpen
        self.assertTrue(open_fn(True, 1.0, 0.5))
        self.assertFalse(open_fn(True, 1.0, 1.1))
        arm_at = self.cg.oswaldStainBurstCounterArmAt
        until = self.cg.oswaldStainBurstCounterUntil
        now = 5.0
        armed = arm_at(now)
        self.assertAlmostEqual(
            armed, now + self.cg.OSWALD_STAIN_BURST_COUNTER_ARM_DELAY_SEC)
        self.assertAlmostEqual(
            until(armed),
            armed + self.cg.OSWALD_STAIN_BURST_COUNTER_WINDOW_SEC)

    def test_client_schedule_hooks(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        methods = _class_method_names(
            _module_ast(rel), 'DistributedCorruptToon')
        for name in (
                '__scheduleOswaldBetrayalLungeCounter',
                '__clearOswaldBetrayalLungeCounter',
                '__scheduleOswaldStainBurstCounter',
                '__clearOswaldStainBurstCounter',
                '__scheduleBruteSpitCounter',
                '__scheduleGagsterLobCounter',
                '__scheduleSnareStringSnapCounter'):
            self.assertIn(name, methods)
        telegraph = _method_source(
            rel, 'DistributedCorruptToon', 'announceAttackTelegraph')
        self.assertIn('__scheduleOswaldBetrayalLungeCounter', telegraph)
        self.assertIn('__scheduleOswaldStainBurstCounter', telegraph)
        self.assertIn('betrayal_lunge', telegraph)
        self.assertIn('stain_burst', telegraph)
        lunge_sched = _method_source(
            rel, 'DistributedCorruptToon',
            '__scheduleOswaldBetrayalLungeCounter')
        self.assertIn('OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED', lunge_sched)
        self.assertIn('corruptOswaldBetrayalLungeCounter', lunge_sched)
        self.assertNotIn('cream', lunge_sched.lower())
        self.assertNotIn('keyblade', lunge_sched.lower())
        burst_sched = _method_source(
            rel, 'DistributedCorruptToon',
            '__scheduleOswaldStainBurstCounter')
        self.assertIn('OSWALD_STAIN_BURST_COUNTER_ENABLED', burst_sched)
        self.assertIn('corruptOswaldStainBurstCounter', burst_sched)
        self.assertNotIn('cream', burst_sched.lower())
        self.assertNotIn('keyblade', burst_sched.lower())

    def test_melee_listener_wiring(self):
        rel = 'toontown/hackslash/MeleeCombat.py'
        methods = _class_method_names(
            _module_ast(rel), 'MeleeCombatController')
        self.assertIn('_onOswaldBetrayalLungeCounter', methods)
        self.assertIn('_onOswaldStainBurstCounter', methods)
        self.assertIn('_onBruteSpitCounter', methods)
        self.assertIn('_onGagsterLobCounter', methods)
        self.assertIn('_armTelegraphCounterWindow', methods)
        src = _read(rel)
        self.assertIn('corruptOswaldBetrayalLungeCounter', src)
        self.assertIn('corruptOswaldStainBurstCounter', src)
        self.assertIn('OSWALD_BETRAYAL_LUNGE_COUNTER_RANGE', src)
        self.assertIn('OSWALD_STAIN_BURST_COUNTER_RANGE', src)
        arm = _method_source(
            rel, 'MeleeCombatController', '_armTelegraphCounterWindow')
        self.assertIn('_armPerfectDodgeCounterWindow', arm)
        arm_l = arm.lower()
        self.assertNotIn('cream', arm_l)
        self.assertNotIn('keyblade', arm_l)
        self.assertNotIn('kingdom hearts', arm_l)
        hint = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('Oswald lunge→F counter', hint)
        self.assertIn('Oswald burst→F counter', hint)

    def test_docs_mention_counters(self):
        reclaim = _read('toontown/corruption/RECLAIM.md')
        reclaim_l = reclaim.lower()
        self.assertIn('oswald_betrayal_lunge_counter_', reclaim_l)
        self.assertIn('oswald_stain_burst_counter_', reclaim_l)
        self.assertIn('dedicated counter window', reclaim_l)
        init_src = _read('toontown/corruption/__init__.py')
        self.assertIn('OSWALD_BETRAYAL_LUNGE_COUNTER_', init_src)
        self.assertIn('OSWALD_STAIN_BURST_COUNTER_', init_src)
        self.assertIn('interrupt ≠ counter', init_src)
        for line in reclaim.splitlines():
            low = line.lower()
            if ('oswald_betrayal_lunge_counter_' in low
                    or 'oswald_stain_burst_counter_' in low):
                self.assertNotIn('keyblade', low)
                self.assertNotIn('kingdom hearts', low)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        OswaldCounterWindowsTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
