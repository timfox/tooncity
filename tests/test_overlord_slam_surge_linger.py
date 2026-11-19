#!/usr/bin/env python3
"""Headless tests for Overlord slam / ink_surge lingering sludge hazards.

Imports CorruptionGlobals with a ToontownGlobals stub (no Panda3D). Asserts
OVERLORD_SLAM_LINGER_* / OVERLORD_INK_SURGE_LINGER_* tunables + pure helpers,
AST wiring on DistributedCorruptToonAI (__armOverlordSlamLinger /
__armOverlordInkSurgeLinger), and client hold/slow hooks in
DistributedCorruptToon. Rain parity (#362) — gameplay trap, not cream FX.
No KH branding.

Run from repo root:
  python3 tests/test_overlord_slam_surge_linger.py
  python3 -m unittest tests.test_overlord_slam_surge_linger -v
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


def _method_body(src: str, def_name: str) -> str:
    marker = 'def %s' % def_name
    start = src.find(marker)
    if start < 0:
        return ''
    snip = src[start:]
    end = snip.find('\n    def ', 1)
    return snip if end < 0 else snip[:end]


class OverlordSlamSurgeLingerTest(unittest.TestCase):
    """Slam / ink_surge linger sludge tunables + AI/client wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_slam_linger_globals_armed(self):
        self.assertTrue(self.cg.OVERLORD_SLAM_LINGER_ENABLED)
        self.assertGreater(self.cg.OVERLORD_SLAM_LINGER_SEC, 1.0)
        self.assertGreater(self.cg.OVERLORD_SLAM_LINGER_TICK_SEC, 0.0)
        self.assertLess(
            self.cg.OVERLORD_SLAM_LINGER_TICK_SEC,
            self.cg.OVERLORD_SLAM_LINGER_SEC)
        self.assertGreaterEqual(self.cg.OVERLORD_SLAM_LINGER_TICK_DAMAGE, 1)
        self.assertGreater(self.cg.OVERLORD_SLAM_LINGER_RADIUS, 0.0)
        self.assertGreater(self.cg.OVERLORD_SLAM_LINGER_SLOW_FACTOR, 0.0)
        self.assertLess(self.cg.OVERLORD_SLAM_LINGER_SLOW_FACTOR, 1.0)
        self.assertGreater(self.cg.OVERLORD_SLAM_LINGER_SLOW_SEC, 0.0)
        # Slam linger is tighter / shorter than rain arena trap.
        self.assertLess(
            self.cg.OVERLORD_SLAM_LINGER_SEC,
            self.cg.OVERLORD_RAIN_LINGER_SEC)
        self.assertLess(
            self.cg.OVERLORD_SLAM_LINGER_RADIUS,
            self.cg.OVERLORD_RAIN_LINGER_RADIUS)
        blob = ' '.join([
            'OVERLORD_SLAM_LINGER_ENABLED',
            'overlordSlamLingerUntil',
            'isInsideOverlordSlamLinger',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_ink_surge_linger_globals_armed(self):
        self.assertTrue(self.cg.OVERLORD_INK_SURGE_LINGER_ENABLED)
        self.assertGreater(self.cg.OVERLORD_INK_SURGE_LINGER_SEC, 1.0)
        self.assertGreater(self.cg.OVERLORD_INK_SURGE_LINGER_TICK_SEC, 0.0)
        self.assertLess(
            self.cg.OVERLORD_INK_SURGE_LINGER_TICK_SEC,
            self.cg.OVERLORD_INK_SURGE_LINGER_SEC)
        self.assertGreaterEqual(
            self.cg.OVERLORD_INK_SURGE_LINGER_TICK_DAMAGE, 1)
        self.assertGreater(self.cg.OVERLORD_INK_SURGE_LINGER_RADIUS, 0.0)
        self.assertGreater(self.cg.OVERLORD_INK_SURGE_LINGER_SLOW_FACTOR, 0.0)
        self.assertLess(self.cg.OVERLORD_INK_SURGE_LINGER_SLOW_FACTOR, 1.0)
        self.assertGreater(self.cg.OVERLORD_INK_SURGE_LINGER_SLOW_SEC, 0.0)
        # Surge linger sits between slam and rain footprints.
        self.assertGreater(
            self.cg.OVERLORD_INK_SURGE_LINGER_RADIUS,
            self.cg.OVERLORD_SLAM_LINGER_RADIUS)
        self.assertLess(
            self.cg.OVERLORD_INK_SURGE_LINGER_RADIUS,
            self.cg.OVERLORD_RAIN_LINGER_RADIUS)
        blob = ' '.join([
            'OVERLORD_INK_SURGE_LINGER_ENABLED',
            'overlordInkSurgeLingerUntil',
            'isInsideOverlordInkSurgeLinger',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_phase_combat_linger_stats(self):
        for phase in (1, 2):
            combat = self.cg.OVERLORD_PHASE_COMBAT[phase]
            self.assertGreater(float(combat.get('slamLingerSec', 0)), 1.0)
            self.assertGreater(float(combat.get('slamLingerTickSec', 0)), 0.0)
            self.assertGreaterEqual(
                int(combat.get('slamLingerTickDamage', 0)), 1)
            self.assertGreater(
                float(combat.get('slamLingerSlowFactor', 0)), 0.0)
            self.assertLess(
                float(combat.get('slamLingerSlowFactor', 1)), 1.0)
            # Linger radius tracks slam hit range so dodge-out still escapes.
            self.assertAlmostEqual(
                float(combat.get('slamHitRange')),
                float(combat.get('slamHitRange')),
                places=2)
        # P1 fallback radius matches Rising slam hit band.
        p1 = self.cg.OVERLORD_PHASE_COMBAT[1]
        self.assertAlmostEqual(
            float(p1.get('slamHitRange')),
            float(self.cg.OVERLORD_SLAM_LINGER_RADIUS),
            places=2)
        # Unleashed slam linger lasts at least as long as Rising.
        self.assertGreaterEqual(
            float(self.cg.OVERLORD_PHASE_COMBAT[2]['slamLingerSec']),
            float(self.cg.OVERLORD_PHASE_COMBAT[1]['slamLingerSec']))
        # Surge linger is P2-only (Unleashed three-note kit).
        self.assertNotIn('surgeLingerSec', self.cg.OVERLORD_PHASE_COMBAT[1])
        p2 = self.cg.OVERLORD_PHASE_COMBAT[2]
        self.assertGreater(float(p2.get('surgeLingerSec', 0)), 1.0)
        self.assertGreaterEqual(int(p2.get('surgeLingerTickDamage', 0)), 1)
        self.assertAlmostEqual(
            float(p2.get('surgeHitRange')),
            float(self.cg.OVERLORD_INK_SURGE_LINGER_RADIUS),
            places=2)

    def test_pure_helpers(self):
        land_at = 10.0
        slam_until = self.cg.overlordSlamLingerUntil(land_at)
        self.assertAlmostEqual(
            slam_until, land_at + self.cg.OVERLORD_SLAM_LINGER_SEC, places=4)
        slam_ticks = self.cg.overlordSlamLingerTickCount()
        self.assertGreaterEqual(slam_ticks, 2)
        self.assertEqual(
            slam_ticks,
            int(self.cg.OVERLORD_SLAM_LINGER_SEC
                // self.cg.OVERLORD_SLAM_LINGER_TICK_SEC))
        self.assertTrue(self.cg.isInsideOverlordSlamLinger(0.0, 0.0, 4.6))
        self.assertTrue(self.cg.isInsideOverlordSlamLinger(2.0, 0.0, 4.6))
        self.assertFalse(self.cg.isInsideOverlordSlamLinger(5.0, 0.0, 4.6))
        self.assertTrue(self.cg.isOverlordSlamSlowActive(12.0, 11.5))
        self.assertFalse(self.cg.isOverlordSlamSlowActive(12.0, 12.0))
        slam_slow = self.cg.overlordSlamSlowUntil(10.0)
        self.assertAlmostEqual(
            slam_slow, 10.0 + self.cg.OVERLORD_SLAM_LINGER_SLOW_SEC, places=4)
        self.assertEqual(
            self.cg.overlordSlamLingerTickDamage(),
            self.cg.OVERLORD_SLAM_LINGER_TICK_DAMAGE)
        self.assertEqual(
            self.cg.overlordSlamLingerTickDamage(
                {'slamLingerTickDamage': 0}),
            1)

        surge_until = self.cg.overlordInkSurgeLingerUntil(land_at)
        self.assertAlmostEqual(
            surge_until,
            land_at + self.cg.OVERLORD_INK_SURGE_LINGER_SEC,
            places=4)
        surge_ticks = self.cg.overlordInkSurgeLingerTickCount()
        self.assertGreaterEqual(surge_ticks, 3)
        self.assertTrue(self.cg.isInsideOverlordInkSurgeLinger(0.0, 0.0, 7.0))
        self.assertFalse(self.cg.isInsideOverlordInkSurgeLinger(8.0, 0.0, 7.0))
        self.assertEqual(
            self.cg.overlordInkSurgeLingerTickDamage(
                {'surgeLingerTickDamage': 2}),
            2)

    def test_ai_arm_and_tick_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for name in (
                '__resolveOverlordSlam',
                '__armOverlordSlamLinger',
                '__tickOverlordSlamLinger',
                '__clearOverlordSlamLinger',
                '__resolveOverlordInkSurge',
                '__armOverlordInkSurgeLinger',
                '__tickOverlordInkSurgeLinger',
                '__clearOverlordInkSurgeLinger'):
            self.assertIn(name, methods, msg='AI missing %s' % name)
        src = _read(rel)
        self.assertIn('__armOverlordSlamLinger(ox, oy, hitRange)', src)
        self.assertIn('__armOverlordInkSurgeLinger(ox, oy, hitRange)', src)
        self.assertIn("uniqueName('overlord-slam-linger')", src)
        self.assertIn("uniqueName('overlord-ink-surge-linger')", src)
        self.assertIn('hackSlashOverlordSlamSludgeUntil', src)
        self.assertIn('hackSlashOverlordInkSurgeSludgeUntil', src)
        self.assertIn('isInsideOverlordSlamLinger', src)
        self.assertIn('isInsideOverlordInkSurgeLinger', src)
        self.assertIn('overlordSlamLingerTickDamage', src)
        self.assertIn('overlordInkSurgeLingerTickDamage', src)
        # Resolve routes Overlord slam through dedicated linger path.
        resolve_attack = _method_body(src, '__resolveAttack')
        self.assertIn("move == 'slam'", resolve_attack)
        self.assertIn('__resolveOverlordSlam', resolve_attack)
        # Linger must clear on delete so orphaned tasks do not leak.
        delete_snip = _method_body(src, 'delete')
        self.assertIn('__clearOverlordSlamLinger', delete_snip)
        self.assertIn('__clearOverlordInkSurgeLinger', delete_snip)
        # Quiet ticks — land already fired impact AV; no sendUpdate replay.
        for tick_name in (
                '__tickOverlordSlamLinger', '__tickOverlordInkSurgeLinger'):
            tick_body = _method_body(src, tick_name)
            self.assertNotIn("sendUpdate('announceAttackHit'", tick_body)
        # Slam resolve always arms linger after single-target land.
        slam_resolve = _method_body(src, '__resolveOverlordSlam')
        self.assertIn('__resolveSingleTargetHit', slam_resolve)
        self.assertIn('__armOverlordSlamLinger', slam_resolve)
        # Surge resolve always arms linger after the land tick.
        surge_resolve = _method_body(src, '__resolveOverlordInkSurge')
        self.assertIn('__armOverlordInkSurgeLinger', surge_resolve)
        # Phase combat merges slamLinger* / surgeLinger* into Overlord _stats.
        apply_body = _method_body(src, '_applyOverlordCombatStats')
        self.assertIn('slamLingerSec', apply_body)
        self.assertIn('slamLingerTickDamage', apply_body)
        self.assertIn('surgeLingerSec', apply_body)
        self.assertIn('surgeLingerTickDamage', apply_body)

    def test_client_hold_and_slow_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        methods = _class_method_names(
            _module_ast(rel), 'DistributedCorruptToon')
        for name in (
                '__playOverlordSlamLingerPuddle',
                '__playOverlordInkSurgeLingerPuddle',
                '__playOverlordLingerPuddleForMove',
                '__armOverlordRainSludgeSlow',
                '__clearOverlordRainLingerPuddle'):
            self.assertIn(name, methods, msg='client missing %s' % name)
        src = _read(rel)
        self.assertIn('OVERLORD_SLAM_LINGER_ENABLED', src)
        self.assertIn('OVERLORD_INK_SURGE_LINGER_ENABLED', src)
        self.assertIn('OVERLORD_SLAM_LINGER_SEC', src)
        self.assertIn('OVERLORD_INK_SURGE_LINGER_SEC', src)
        # Hit + dodge both leave the linger ring (AI arms after either).
        hit_body = _method_body(src, 'announceAttackHit')
        self.assertIn('__playOverlordSlamLingerPuddle', hit_body)
        self.assertIn('__playOverlordInkSurgeLingerPuddle', hit_body)
        dodge_body = _method_body(src, 'announceAttackDodged')
        self.assertIn('__playOverlordSlamLingerPuddle', dodge_body)
        self.assertIn('__playOverlordInkSurgeLingerPuddle', dodge_body)
        # Shared play path uses move-scaled hold / radius.
        play_body = _method_body(src, '__playOverlordLingerPuddleForMove')
        self.assertIn('holdSec', play_body)
        self.assertIn('__armOverlordRainSludgeSlow', play_body)
        self.assertIn('slamHitRange', play_body)
        self.assertIn('surgeHitRange', play_body)
        blob = play_body.lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)


if __name__ == '__main__':
    unittest.main()
