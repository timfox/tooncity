#!/usr/bin/env python3
"""Headless tests for Ink Smudge ink_dash / ink_splat dedicated counters.

Loads CorruptionGlobals without Panda3D. Asserts Snare-like counter tunables
+ pure helpers, client schedule hooks on DistributedCorruptToon, and
MeleeCombat listener wiring. Beyond interrupt cancel — these are dedicated
telegraph punish→melee windows (no cream deepen, no KH).

Run from repo root:
  python3 tests/test_ink_smudge_counter_windows.py
  python3 -m unittest tests.test_ink_smudge_counter_windows -v
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


class InkSmudgeCounterWindowsTest(unittest.TestCase):
    """Ink Smudge ink_dash / ink_splat dedicated counter tunables + wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_counter_globals_armed(self):
        self.assertTrue(self.cg.INK_DASH_COUNTER_ENABLED)
        self.assertTrue(self.cg.INK_SPLAT_COUNTER_ENABLED)
        self.assertGreater(self.cg.INK_DASH_COUNTER_ARM_DELAY_SEC, 0.0)
        self.assertGreater(self.cg.INK_DASH_COUNTER_WINDOW_SEC, 0.0)
        self.assertGreater(self.cg.INK_DASH_COUNTER_RANGE, 0.0)
        self.assertGreater(self.cg.INK_DASH_COUNTER_DAMAGE_MULT, 1.0)
        self.assertGreater(self.cg.INK_DASH_COUNTER_RATE_MULT, 1.0)
        self.assertGreater(self.cg.INK_SPLAT_COUNTER_ARM_DELAY_SEC, 0.0)
        self.assertGreater(self.cg.INK_SPLAT_COUNTER_WINDOW_SEC, 0.0)
        self.assertGreater(self.cg.INK_SPLAT_COUNTER_RANGE, 0.0)
        self.assertGreater(self.cg.INK_SPLAT_COUNTER_DAMAGE_MULT, 1.0)
        self.assertGreater(self.cg.INK_SPLAT_COUNTER_RATE_MULT, 1.0)
        # Arm delay fits inside each Smudge telegraph beat.
        ink = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_INK]
        dash_tele = float(ink.get(
            'telegraphDelay', self.cg.ATTACK_TELEGRAPH_DELAY))
        splat_tele = float(ink.get(
            'splatTelegraphDelay', ink.get('telegraphDelay', 0.42)))
        self.assertLessEqual(
            self.cg.INK_DASH_COUNTER_ARM_DELAY_SEC, dash_tele + 0.05)
        self.assertLessEqual(
            self.cg.INK_SPLAT_COUNTER_ARM_DELAY_SEC, splat_tele + 0.05)
        self.assertEqual(
            self.cg.INK_DASH_COUNTER_EVENT, 'corruptInkDashCounter')
        self.assertEqual(
            self.cg.INK_SPLAT_COUNTER_EVENT, 'corruptInkSplatCounter')
        # Distinct from street / Oswald / Overlord events; no KH / cream.
        for event in (
                self.cg.INK_DASH_COUNTER_EVENT,
                self.cg.INK_SPLAT_COUNTER_EVENT):
            self.assertNotEqual(event, self.cg.SNARE_STRING_COUNTER_EVENT)
            self.assertNotEqual(event, self.cg.BRUTE_SPIT_COUNTER_EVENT)
            self.assertNotEqual(event, self.cg.GAGSTER_LOB_COUNTER_EVENT)
            self.assertNotEqual(
                event, self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_EVENT)
            self.assertNotEqual(
                event, self.cg.OSWALD_STAIN_BURST_COUNTER_EVENT)
            self.assertNotEqual(event, self.cg.OVERLORD_RAIN_COUNTER_EVENT)
            self.assertNotEqual(event, self.cg.OVERLORD_SLAM_COUNTER_EVENT)
            self.assertNotEqual(
                event, self.cg.OVERLORD_INK_SURGE_COUNTER_EVENT)
            low = event.lower()
            self.assertNotIn('keyblade', low)
            self.assertNotIn('kingdom hearts', low)
            self.assertNotIn('cream', low)

    def test_dedicated_counter_move_helper(self):
        fn = self.cg.isDedicatedTelegraphCounterMove
        ink = self.cg.ARCHETYPE_INK
        self.assertTrue(fn(ink, 'ink_dash'))
        self.assertTrue(fn(ink, 'ink_splat'))
        # Overlord climax counters still covered on same archetype.
        self.assertTrue(fn(ink, 'rain'))
        self.assertTrue(fn(ink, 'slam'))
        self.assertTrue(fn(ink, 'ink_surge'))
        self.assertFalse(fn(ink, 'smack'))
        # Street / Oswald kits still covered.
        self.assertTrue(fn(self.cg.ARCHETYPE_BRUTE, 'spit'))
        self.assertTrue(fn(self.cg.ARCHETYPE_GAGSTER, 'gag_lob'))
        self.assertTrue(fn(self.cg.ARCHETYPE_SNARE, 'smack'))
        self.assertTrue(fn(self.cg.ARCHETYPE_CORRUPT_OSWALD, 'betrayal_lunge'))
        self.assertFalse(fn(self.cg.ARCHETYPE_BRUTE, 'slam'))
        # Disable flags respected.
        prev_d = self.cg.INK_DASH_COUNTER_ENABLED
        prev_s = self.cg.INK_SPLAT_COUNTER_ENABLED
        try:
            self.cg.INK_DASH_COUNTER_ENABLED = False
            self.assertFalse(fn(ink, 'ink_dash'))
            self.assertTrue(fn(ink, 'ink_splat'))
            self.cg.INK_SPLAT_COUNTER_ENABLED = False
            self.assertFalse(fn(ink, 'ink_splat'))
            self.assertTrue(fn(ink, 'rain'))
        finally:
            self.cg.INK_DASH_COUNTER_ENABLED = prev_d
            self.cg.INK_SPLAT_COUNTER_ENABLED = prev_s
        self.assertTrue(fn(ink, 'ink_dash'))
        self.assertTrue(fn(ink, 'ink_splat'))

    def test_dash_opener_helpers(self):
        dmg = self.cg.inkDashCounterOpenerDamage
        rate_fn = self.cg.inkDashCounterOpenerRate
        self.assertEqual(
            dmg(8),
            max(1, int(round(8 * self.cg.INK_DASH_COUNTER_DAMAGE_MULT))))
        self.assertEqual(dmg(8, 1.5), 12)
        self.assertEqual(dmg(0, 2.0), 1)
        self.assertAlmostEqual(
            rate_fn(1.0), 1.0 * self.cg.INK_DASH_COUNTER_RATE_MULT)
        self.assertAlmostEqual(rate_fn(2.0, 1.25), 2.5)
        open_fn = self.cg.isInkDashCounterWindowOpen
        self.assertFalse(open_fn(False, 1.0, 0.5))
        self.assertTrue(open_fn(True, 1.0, 0.5))
        self.assertFalse(open_fn(True, 1.0, 1.0))
        arm_at = self.cg.inkDashCounterArmAt
        until = self.cg.inkDashCounterUntil
        now = 10.0
        armed = arm_at(now)
        self.assertAlmostEqual(
            armed, now + self.cg.INK_DASH_COUNTER_ARM_DELAY_SEC)
        self.assertAlmostEqual(
            until(armed), armed + self.cg.INK_DASH_COUNTER_WINDOW_SEC)

    def test_splat_opener_helpers(self):
        dmg = self.cg.inkSplatCounterOpenerDamage
        rate_fn = self.cg.inkSplatCounterOpenerRate
        self.assertEqual(
            dmg(8),
            max(1, int(round(8 * self.cg.INK_SPLAT_COUNTER_DAMAGE_MULT))))
        self.assertEqual(dmg(8, 1.5), 12)
        self.assertAlmostEqual(
            rate_fn(1.0), 1.0 * self.cg.INK_SPLAT_COUNTER_RATE_MULT)
        open_fn = self.cg.isInkSplatCounterWindowOpen
        self.assertTrue(open_fn(True, 1.0, 0.5))
        self.assertFalse(open_fn(True, 1.0, 1.1))
        arm_at = self.cg.inkSplatCounterArmAt
        until = self.cg.inkSplatCounterUntil
        now = 5.0
        armed = arm_at(now)
        self.assertAlmostEqual(
            armed, now + self.cg.INK_SPLAT_COUNTER_ARM_DELAY_SEC)
        self.assertAlmostEqual(
            until(armed), armed + self.cg.INK_SPLAT_COUNTER_WINDOW_SEC)

    def test_client_schedule_hooks(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        methods = _class_method_names(
            _module_ast(rel), 'DistributedCorruptToon')
        for name in (
                '__scheduleInkDashCounter',
                '__clearInkDashCounter',
                '__scheduleInkSplatCounter',
                '__clearInkSplatCounter',
                '__scheduleOswaldBetrayalLungeCounter',
                '__scheduleBruteSpitCounter',
                '__scheduleOverlordRainCounter',
                '__scheduleSnareStringSnapCounter'):
            self.assertIn(name, methods)
        telegraph = _method_source(
            rel, 'DistributedCorruptToon', 'announceAttackTelegraph')
        self.assertIn('__scheduleInkDashCounter', telegraph)
        self.assertIn('__scheduleInkSplatCounter', telegraph)
        self.assertIn('ink_dash', telegraph)
        self.assertIn('ink_splat', telegraph)
        dash_sched = _method_source(
            rel, 'DistributedCorruptToon', '__scheduleInkDashCounter')
        self.assertIn('INK_DASH_COUNTER_ENABLED', dash_sched)
        self.assertIn('corruptInkDashCounter', dash_sched)
        self.assertNotIn('cream', dash_sched.lower())
        self.assertNotIn('keyblade', dash_sched.lower())
        splat_sched = _method_source(
            rel, 'DistributedCorruptToon', '__scheduleInkSplatCounter')
        self.assertIn('INK_SPLAT_COUNTER_ENABLED', splat_sched)
        self.assertIn('corruptInkSplatCounter', splat_sched)
        self.assertNotIn('cream', splat_sched.lower())
        self.assertNotIn('keyblade', splat_sched.lower())

    def test_melee_listener_wiring(self):
        rel = 'toontown/hackslash/MeleeCombat.py'
        methods = _class_method_names(
            _module_ast(rel), 'MeleeCombatController')
        self.assertIn('_onInkDashCounter', methods)
        self.assertIn('_onInkSplatCounter', methods)
        self.assertIn('_onOverlordRainCounter', methods)
        self.assertIn('_onOswaldBetrayalLungeCounter', methods)
        self.assertIn('_armTelegraphCounterWindow', methods)
        src = _read(rel)
        self.assertIn('corruptInkDashCounter', src)
        self.assertIn('corruptInkSplatCounter', src)
        self.assertIn('INK_DASH_COUNTER_RANGE', src)
        self.assertIn('INK_SPLAT_COUNTER_RANGE', src)
        arm = _method_source(
            rel, 'MeleeCombatController', '_armTelegraphCounterWindow')
        self.assertIn('_armPerfectDodgeCounterWindow', arm)
        arm_l = arm.lower()
        self.assertNotIn('cream', arm_l)
        self.assertNotIn('keyblade', arm_l)
        self.assertNotIn('kingdom hearts', arm_l)
        hint = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('Smudge dash→F counter', hint)
        self.assertIn('Smudge splat→F counter', hint)

    def test_docs_mention_counters(self):
        reclaim = _read('toontown/corruption/RECLAIM.md')
        reclaim_l = reclaim.lower()
        self.assertIn('ink_dash_counter_', reclaim_l)
        self.assertIn('ink_splat_counter_', reclaim_l)
        self.assertIn('dedicated counter window', reclaim_l)
        init_src = _read('toontown/corruption/__init__.py')
        self.assertIn('INK_DASH_COUNTER_', init_src)
        self.assertIn('INK_SPLAT_COUNTER_', init_src)
        self.assertIn('interrupt ≠ counter', init_src)
        for line in reclaim.splitlines():
            low = line.lower()
            if ('ink_dash_counter_' in low
                    or 'ink_splat_counter_' in low):
                self.assertNotIn('keyblade', low)
                self.assertNotIn('kingdom hearts', low)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        InkSmudgeCounterWindowsTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
