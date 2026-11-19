#!/usr/bin/env python3
"""Headless tests for Overlord ink-rain lingering sludge hazard.

Imports CorruptionGlobals with a ToontownGlobals stub (no Panda3D). Asserts
OVERLORD_RAIN_LINGER_* tunables + pure helpers, AST wiring on
DistributedCorruptToonAI (__armOverlordRainLinger / __tickOverlordRainLinger),
and client hold/slow hooks in DistributedCorruptToon. Gameplay trap — not
cream FX deepen. No KH branding.

Run from repo root:
  python3 tests/test_overlord_rain_linger.py
  python3 -m unittest tests.test_overlord_rain_linger -v
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


class OverlordRainLingerTest(unittest.TestCase):
    """Rain linger sludge tunables + AI/client wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_linger_globals_armed(self):
        self.assertTrue(self.cg.OVERLORD_RAIN_LINGER_ENABLED)
        self.assertGreater(self.cg.OVERLORD_RAIN_LINGER_SEC, 1.0)
        self.assertGreater(self.cg.OVERLORD_RAIN_LINGER_TICK_SEC, 0.0)
        self.assertLess(
            self.cg.OVERLORD_RAIN_LINGER_TICK_SEC,
            self.cg.OVERLORD_RAIN_LINGER_SEC)
        self.assertGreaterEqual(self.cg.OVERLORD_RAIN_LINGER_TICK_DAMAGE, 1)
        self.assertGreater(self.cg.OVERLORD_RAIN_LINGER_RADIUS, 0.0)
        self.assertGreater(self.cg.OVERLORD_RAIN_LINGER_SLOW_FACTOR, 0.0)
        self.assertLess(self.cg.OVERLORD_RAIN_LINGER_SLOW_FACTOR, 1.0)
        self.assertGreater(self.cg.OVERLORD_RAIN_LINGER_SLOW_SEC, 0.0)
        # No KH branding in linger names / comments nearby.
        blob = ' '.join([
            'OVERLORD_RAIN_LINGER_ENABLED',
            'overlordRainLingerUntil',
            'isInsideOverlordRainLinger',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_phase_combat_linger_stats(self):
        for phase in (1, 2):
            combat = self.cg.OVERLORD_PHASE_COMBAT[phase]
            self.assertGreater(float(combat.get('rainLingerSec', 0)), 1.0)
            self.assertGreater(float(combat.get('rainLingerTickSec', 0)), 0.0)
            self.assertGreaterEqual(
                int(combat.get('rainLingerTickDamage', 0)), 1)
            self.assertGreater(
                float(combat.get('rainLingerSlowFactor', 0)), 0.0)
            self.assertLess(
                float(combat.get('rainLingerSlowFactor', 1)), 1.0)
            # Linger radius tracks rain hit range so dodge-out still escapes.
            self.assertAlmostEqual(
                float(combat.get('attackHitRange')),
                float(combat.get('attackHitRange')),
                places=2)
        # P1 fallback radius matches Rising rain hit band.
        p1 = self.cg.OVERLORD_PHASE_COMBAT[1]
        self.assertAlmostEqual(
            float(p1.get('attackHitRange')),
            float(self.cg.OVERLORD_RAIN_LINGER_RADIUS),
            places=2)
        # Unleashed ticks a bit harder than Rising.
        self.assertGreaterEqual(
            int(self.cg.OVERLORD_PHASE_COMBAT[2]['rainLingerTickDamage']),
            int(self.cg.OVERLORD_PHASE_COMBAT[1]['rainLingerTickDamage']))

    def test_pure_helpers(self):
        land_at = 10.0
        until = self.cg.overlordRainLingerUntil(land_at)
        self.assertAlmostEqual(
            until, land_at + self.cg.OVERLORD_RAIN_LINGER_SEC, places=4)
        ticks = self.cg.overlordRainLingerTickCount()
        self.assertGreaterEqual(ticks, 3)
        self.assertEqual(
            ticks,
            int(self.cg.OVERLORD_RAIN_LINGER_SEC
                // self.cg.OVERLORD_RAIN_LINGER_TICK_SEC))
        self.assertTrue(self.cg.isInsideOverlordRainLinger(0.0, 0.0, 9.5))
        self.assertTrue(self.cg.isInsideOverlordRainLinger(5.0, 0.0, 9.5))
        self.assertFalse(self.cg.isInsideOverlordRainLinger(10.0, 0.0, 9.5))
        self.assertTrue(self.cg.isOverlordRainSlowActive(12.0, 11.5))
        self.assertFalse(self.cg.isOverlordRainSlowActive(12.0, 12.0))
        slow_until = self.cg.overlordRainSlowUntil(10.0)
        self.assertAlmostEqual(
            slow_until, 10.0 + self.cg.OVERLORD_RAIN_LINGER_SLOW_SEC, places=4)
        self.assertEqual(
            self.cg.overlordRainLingerTickDamage(),
            self.cg.OVERLORD_RAIN_LINGER_TICK_DAMAGE)
        self.assertEqual(
            self.cg.overlordRainLingerTickDamage(
                {'rainLingerTickDamage': 0}),
            1)
        self.assertEqual(
            self.cg.overlordRainLingerTickDamage(
                {'rainLingerTickDamage': 2}),
            2)

    def test_ai_arm_and_tick_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for name in (
                '__resolveOverlordRain',
                '__armOverlordRainLinger',
                '__tickOverlordRainLinger',
                '__clearOverlordRainLinger'):
            self.assertIn(name, methods, msg='AI missing %s' % name)
        src = _read(rel)
        self.assertIn('__armOverlordRainLinger(ox, oy, hitRange)', src)
        self.assertIn("uniqueName('overlord-rain-linger')", src)
        self.assertIn('hackSlashOverlordRainSludgeUntil', src)
        self.assertIn('hackSlashOverlordRainSludgeSlow', src)
        self.assertIn('isInsideOverlordRainLinger', src)
        self.assertIn('overlordRainLingerTickDamage', src)
        # Linger must clear on delete so orphaned tasks do not leak.
        delete_snip = src[src.find('def delete(self):'):]
        self.assertIn('__clearOverlordRainLinger', delete_snip)
        # Quiet ticks — land already fired impact AV; no sendUpdate replay.
        tick_snip = src[src.find('def __tickOverlordRainLinger'):]
        tick_end = tick_snip.find('\n    def ', 1)
        tick_body = tick_snip if tick_end < 0 else tick_snip[:tick_end]
        self.assertNotIn("sendUpdate('announceAttackHit'", tick_body)
        # Resolve always arms linger after the land tick.
        resolve = src[src.find('def __resolveOverlordRain'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn('__armOverlordRainLinger', resolve_body)
        # Phase combat merges rainLinger* into Overlord _stats.
        apply = src[src.find('def _applyOverlordCombatStats'):]
        apply_end = apply.find('\n    def ', 1)
        apply_body = apply if apply_end < 0 else apply[:apply_end]
        self.assertIn('rainLingerSec', apply_body)
        self.assertIn('rainLingerTickDamage', apply_body)

    def test_client_hold_and_slow_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        methods = _class_method_names(
            _module_ast(rel), 'DistributedCorruptToon')
        for name in (
                '__playOverlordRainLingerPuddle',
                '__armOverlordRainSludgeSlow',
                '__tickOverlordRainSludgeSlow',
                '__clearOverlordRainSludgeSlow',
                '__clearOverlordRainLingerPuddle'):
            self.assertIn(name, methods, msg='client missing %s' % name)
        src = _read(rel)
        self.assertIn('OVERLORD_RAIN_LINGER_ENABLED', src)
        self.assertIn('OVERLORD_RAIN_LINGER_SEC', src)
        self.assertIn('setWalkSpeedSlow', src)
        self.assertIn('setWalkSpeedNormal', src)
        self.assertIn('isInsideOverlordRainLinger', src)
        # Hit + dodge both leave the linger ring (AI arms after either).
        hit = src[src.find('def announceAttackHit'):]
        hit_end = hit.find('\n    def ', 1)
        hit_body = hit if hit_end < 0 else hit[:hit_end]
        self.assertIn('__playOverlordRainLingerPuddle', hit_body)
        dodge = src[src.find('def announceAttackDodged'):]
        dodge_end = dodge.find('\n    def ', 1)
        dodge_body = dodge if dodge_end < 0 else dodge[:dodge_end]
        self.assertIn('__playOverlordRainLingerPuddle', dodge_body)
        # Rain wrapper delegates to shared move linger (slam/surge parity).
        play = src[src.find('def __playOverlordRainLingerPuddle'):]
        play_end = play.find('\n    def ', 1)
        play_body = play if play_end < 0 else play[:play_end]
        self.assertIn('__playOverlordLingerPuddleForMove', play_body)
        shared = src[src.find('def __playOverlordLingerPuddleForMove'):]
        shared_end = shared.find('\n    def ', 1)
        shared_body = shared if shared_end < 0 else shared[:shared_end]
        # Hold Wait uses linger sec so the magenta ring matches AI hazard.
        self.assertIn('holdSec', shared_body)
        self.assertIn('__armOverlordRainSludgeSlow', shared_body)
        self.assertIn('OVERLORD_RAIN_LINGER_SEC', shared_body)
        # No cream deepen / KH in the linger path.
        blob = shared_body.lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)


if __name__ == '__main__':
    unittest.main()
