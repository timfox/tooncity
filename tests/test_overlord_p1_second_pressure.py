#!/usr/bin/env python3
"""Headless/AST tests: Overlord P1 second pressure pattern beyond rain.

TC-342 / gap scan #8 — Rising was rain-only. Close slam is the second
Rising note so Silly climax is not one-note before HP-threshold Unleash.
Does not redo P2 ink_surge; surge keys stay Unleashed-only.
Loads CorruptionGlobals without Panda3D.

Run from repo root:
  python3 tests/test_overlord_p1_second_pressure.py
  python3 -m unittest tests.test_overlord_p1_second_pressure -v
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


class OverlordP1SecondPressureTest(unittest.TestCase):
    """Rising slam tunables / picker / AI wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_p1_slam_globals_armed(self):
        self.assertTrue(self.cg.OVERLORD_P1_SLAM_ENABLED)
        blob = ' '.join([
            'OVERLORD_P1_SLAM_ENABLED',
            'overlordPickRisingMove',
            'rising',
            'slam',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)
        self.assertNotIn('sora', blob)

    def test_p1_combat_table_has_slam_not_surge(self):
        p1 = self.cg.overlordPhaseCombat(1)
        p2 = self.cg.overlordPhaseCombat(2)
        self.assertEqual(p1['id'], 'rising-rain')
        self.assertEqual(p1['moveMode'], 'rising')
        self.assertEqual(p2['moveMode'], 'enrage')
        for key in (
                'slamHitRange', 'slamNearMissRange', 'slamDamage',
                'slamTelegraphDelay', 'slamCooldown', 'slamMeleeRange'):
            self.assertIn(key, p1, msg='P1 missing %s' % key)
            self.assertIn(key, p2, msg='P2 missing %s' % key)
        for key in (
                'surgeMaxRange', 'surgeDash', 'surgeStop', 'surgeHitRange',
                'surgeNearMissRange', 'surgeDamage', 'surgeTelegraphDelay',
                'surgeCooldown'):
            self.assertNotIn(key, p1, msg='P1 must not carry %s' % key)
            self.assertIn(key, p2, msg='P2 missing %s' % key)
        # Close slam band sits inside rain engage.
        self.assertLess(p1['slamMeleeRange'], p1['meleeRange'])
        self.assertLess(p1['slamHitRange'], p1['attackHitRange'])
        self.assertLess(p1['slamTelegraphDelay'], p1['telegraphDelay'])
        self.assertLess(p1['slamCooldown'], p1['attackCooldown'])
        # Softer / slower than Unleashed slam.
        self.assertLess(p1['slamDamage'], p2['slamDamage'])
        self.assertGreater(p1['slamTelegraphDelay'], p2['slamTelegraphDelay'])
        self.assertLess(p1['slamHitRange'], p2['slamHitRange'])
        self.assertLess(p1['slamMeleeRange'], p2['slamMeleeRange'])

    def test_rising_picker_two_notes(self):
        p1 = self.cg.overlordPhaseCombat(1)
        slam = self.cg.overlordSlamMeleeRange(p1)
        self.assertEqual(self.cg.overlordPickRisingMove(0.0, p1), 'slam')
        self.assertEqual(self.cg.overlordPickRisingMove(slam, p1), 'slam')
        self.assertEqual(
            self.cg.overlordPickRisingMove(slam + 0.05, p1), 'rain')
        self.assertEqual(
            self.cg.overlordPickRisingMove(p1['meleeRange'], p1), 'rain')
        # Rising never picks ink_surge even at mid-range.
        mid = (slam + float(p1['meleeRange'])) * 0.5
        self.assertEqual(self.cg.overlordPickRisingMove(mid, p1), 'rain')
        # Disable flag restores rain-only.
        was = self.cg.OVERLORD_P1_SLAM_ENABLED
        try:
            self.cg.OVERLORD_P1_SLAM_ENABLED = False
            self.assertEqual(self.cg.overlordPickRisingMove(0.0, p1), 'rain')
            self.assertEqual(self.cg.overlordPickRisingMove(slam, p1), 'rain')
        finally:
            self.cg.OVERLORD_P1_SLAM_ENABLED = was

    def test_p2_enrage_picker_untouched(self):
        """P2 three-note kit still rains / surges / slams — not reworked here."""
        p2 = self.cg.overlordPhaseCombat(2)
        slam = self.cg.overlordSlamMeleeRange(p2)
        surge = self.cg.overlordSurgeMaxRange(p2)
        self.assertEqual(self.cg.overlordPickEnrageMove(0.0, p2), 'slam')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(slam + 0.05, p2), 'ink_surge')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(surge + 0.05, p2), 'rain')

    def test_prior_gameplay_not_regressed(self):
        self.assertEqual(self.cg.normalizeFinalePhase(1), 1)
        self.assertEqual(self.cg.normalizeFinalePhase(2), 2)
        self.assertEqual(self.cg.overlordP2AddCount(1), 0)
        self.assertGreater(self.cg.overlordP2AddCount(2), 0)
        self.assertTrue(self.cg.OVERLORD_INK_SURGE_ENABLED)
        self.assertTrue(self.cg.INK_SMUDGE_KIT_ENABLED)
        self.assertTrue(self.cg.ROLE_AI_ENABLED)
        self.assertTrue(self.cg.BRUTE_SPIT_PROJECTILE_ENABLED)
        self.assertTrue(self.cg.SNARE_LASH_YANK_ENABLED)
        self.assertTrue(self.cg.OSWALD_BETRAYAL_KIT_ENABLED)

    def test_ai_rising_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for required in (
                '__pickOverlordMove',
                '__resolveOverlordRain',
                '__resolveSingleTargetHit',
                '__resolveOverlordInkSurge'):
            self.assertIn(required, methods)
        src = _read(rel)
        pick = src[src.find('def __pickOverlordMove'):]
        pick_end = pick.find('\n    def ', 1)
        pick_body = pick if pick_end < 0 else pick[:pick_end]
        self.assertIn('overlordPickRisingMove', pick_body)
        self.assertIn('overlordPickEnrageMove', pick_body)
        self.assertIn("'rising'", pick_body)
        # P1 path must not call the enrage/surge picker as its only branch.
        self.assertIn("mode == 'rising'", pick_body)
        self.assertIn("mode == 'enrage'", pick_body)
        # Slam resolve still routes through single-target (existing path).
        resolve = src[src.find('def __resolveAttack'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn("move == 'ink_surge'", resolve_body)
        self.assertIn('__resolveSingleTargetHit', resolve_body)
        blob = (pick_body + resolve_body).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, blob)

    def test_docs_and_magic_mention_p1_slam(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        p1 = reclaim.split('phase 1', 1)[-1].split('phase 2', 1)[0]
        self.assertIn('slam', p1)
        self.assertIn('rain', p1)
        self.assertNotIn('ink_surge', p1)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, p1)
        magic = _read('toontown/corruption/MagicWords.py').lower()
        self.assertIn('rain+slam', magic)
        self.assertIn('rain+surge+slam', magic)


if __name__ == '__main__':
    unittest.main()
