#!/usr/bin/env python3
"""Headless tests for Gunk Gagster lingering sludge hazard.

Imports CorruptionGlobals with a ToontownGlobals stub (no Panda3D). Asserts
linger tunables + pure helpers, AST wiring on DistributedCorruptToonAI
(__armGagsterPuddleLinger / __tickGagsterPuddleLinger), and client hold/slow
hooks in DistributedCorruptToon. Gameplay trap — not cream FX deepen.

Run from repo root:
  python3 tests/test_gagster_puddle_linger.py
  python3 -m unittest tests.test_gagster_puddle_linger -v
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


def _class_and_func_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    return set()


class GagsterPuddleLingerTest(unittest.TestCase):
    """Linger sludge tunables + AI/client wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_linger_globals_armed(self):
        self.assertTrue(self.cg.GAGSTER_PUDDLE_LINGER_ENABLED)
        self.assertGreater(self.cg.GAGSTER_PUDDLE_LINGER_SEC, 1.0)
        self.assertGreater(self.cg.GAGSTER_PUDDLE_LINGER_TICK_SEC, 0.0)
        self.assertLess(
            self.cg.GAGSTER_PUDDLE_LINGER_TICK_SEC,
            self.cg.GAGSTER_PUDDLE_LINGER_SEC)
        self.assertGreaterEqual(self.cg.GAGSTER_PUDDLE_LINGER_TICK_DAMAGE, 1)
        self.assertGreater(self.cg.GAGSTER_PUDDLE_LINGER_RADIUS, 0.0)
        self.assertGreater(self.cg.GAGSTER_PUDDLE_LINGER_SLOW_FACTOR, 0.0)
        self.assertLess(self.cg.GAGSTER_PUDDLE_LINGER_SLOW_FACTOR, 1.0)
        self.assertGreater(self.cg.GAGSTER_PUDDLE_LINGER_SLOW_SEC, 0.0)
        # No KH branding in linger names / comments nearby.
        blob = ' '.join([
            'GAGSTER_PUDDLE_LINGER_ENABLED',
            'gagsterPuddleLingerUntil',
            'isInsideGagsterPuddle',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_gagster_archetype_linger_stats(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_GAGSTER]
        self.assertEqual(stats.get('attackMove'), 'gag_lob')
        self.assertGreater(float(stats.get('puddleLingerSec', 0)), 1.0)
        self.assertGreater(float(stats.get('puddleLingerTickSec', 0)), 0.0)
        self.assertGreaterEqual(int(stats.get('puddleLingerTickDamage', 0)), 1)
        self.assertGreater(float(stats.get('puddleLingerSlowFactor', 0)), 0.0)
        self.assertLess(float(stats.get('puddleLingerSlowFactor', 1)), 1.0)
        # Linger radius tracks land hit range so dodge-out still escapes.
        self.assertAlmostEqual(
            float(stats.get('attackHitRange')),
            float(self.cg.GAGSTER_PUDDLE_LINGER_RADIUS),
            places=2)

    def test_pure_helpers(self):
        land_at = 10.0
        until = self.cg.gagsterPuddleLingerUntil(land_at)
        self.assertAlmostEqual(
            until, land_at + self.cg.GAGSTER_PUDDLE_LINGER_SEC, places=4)
        ticks = self.cg.gagsterPuddleLingerTickCount()
        self.assertGreaterEqual(ticks, 3)
        self.assertEqual(
            ticks,
            int(self.cg.GAGSTER_PUDDLE_LINGER_SEC
                // self.cg.GAGSTER_PUDDLE_LINGER_TICK_SEC))
        self.assertTrue(self.cg.isInsideGagsterPuddle(0.0, 0.0, 5.0))
        self.assertTrue(self.cg.isInsideGagsterPuddle(3.0, 4.0, 5.0))
        self.assertFalse(self.cg.isInsideGagsterPuddle(3.0, 4.1, 5.0))
        self.assertTrue(self.cg.isGagsterPuddleSlowActive(12.0, 11.5))
        self.assertFalse(self.cg.isGagsterPuddleSlowActive(12.0, 12.0))
        slow_until = self.cg.gagsterPuddleSlowUntil(10.0)
        self.assertAlmostEqual(
            slow_until, 10.0 + self.cg.GAGSTER_PUDDLE_LINGER_SLOW_SEC, places=4)
        self.assertEqual(
            self.cg.gagsterPuddleLingerTickDamage(),
            self.cg.GAGSTER_PUDDLE_LINGER_TICK_DAMAGE)
        self.assertEqual(
            self.cg.gagsterPuddleLingerTickDamage(
                {'puddleLingerTickDamage': 0}),
            1)

    def test_ai_arm_and_tick_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for name in (
                '__resolveGagsterPuddle',
                '__armGagsterPuddleLinger',
                '__tickGagsterPuddleLinger',
                '__clearGagsterPuddleLinger'):
            self.assertIn(name, methods, msg='AI missing %s' % name)
        src = _read(rel)
        self.assertIn('__armGagsterPuddleLinger(px, py, hitRange)', src)
        self.assertIn("uniqueName('gagster-puddle-linger')", src)
        self.assertIn('hackSlashGagsterSludgeUntil', src)
        self.assertIn('hackSlashGagsterSludgeSlow', src)
        self.assertIn('isInsideGagsterPuddle', src)
        self.assertIn('gagsterPuddleLingerTickDamage', src)
        # Linger must clear on delete so orphaned tasks do not leak.
        delete_snip = src[src.find('def delete(self):'):]
        self.assertIn('__clearGagsterPuddleLinger', delete_snip)
        # Quiet ticks — land already fired impact AV; no sendUpdate replay.
        tick_snip = src[src.find('def __tickGagsterPuddleLinger'):]
        tick_end = tick_snip.find('\n    def ', 1)
        tick_body = tick_snip if tick_end < 0 else tick_snip[:tick_end]
        self.assertNotIn("sendUpdate('announceAttackHit'", tick_body)

    def test_client_hold_and_slow_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        methods = _class_method_names(
            _module_ast(rel), 'DistributedCorruptToon')
        for name in (
                '__playGagPuddle',
                '__armGagsterSludgeSlow',
                '__tickGagsterSludgeSlow',
                '__clearGagsterSludgeSlow'):
            self.assertIn(name, methods, msg='client missing %s' % name)
        src = _read(rel)
        self.assertIn('GAGSTER_PUDDLE_LINGER_ENABLED', src)
        self.assertIn('GAGSTER_PUDDLE_LINGER_SEC', src)
        self.assertIn('setWalkSpeedSlow', src)
        self.assertIn('setWalkSpeedNormal', src)
        self.assertIn('isInsideGagsterPuddle', src)
        # Hold Wait uses linger sec so the teal ring matches AI hazard window.
        play = src[src.find('def __playGagPuddle'):]
        play_end = play.find('\n    def ', 1)
        play_body = play if play_end < 0 else play[:play_end]
        self.assertIn('holdSec', play_body)
        self.assertIn('__armGagsterSludgeSlow', play_body)


if __name__ == '__main__':
    unittest.main()
