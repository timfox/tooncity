#!/usr/bin/env python3
"""Headless/AST tests: Overlord P2 ink_surge third pressure pattern.

Gap scan #8 — Unleashed kit was rain + close slam only. Mid-range
``ink_surge`` (planar rush then landing AoE) is the third enrage note.
Loads CorruptionGlobals without Panda3D. Must not regress Silly HP P2,
Ink Smudge kit, reclaim KO helper, role AI, or prior archetype kits.

Run from repo root:
  python3 tests/test_overlord_p2_ink_surge.py
  python3 -m unittest tests.test_overlord_p2_ink_surge -v
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


class OverlordP2InkSurgeTest(unittest.TestCase):
    """Ink surge tunables / helpers / AI wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_surge_globals_armed(self):
        self.assertTrue(self.cg.OVERLORD_INK_SURGE_ENABLED)
        self.assertGreater(self.cg.OVERLORD_INK_SURGE_DASH, 0.0)
        self.assertGreater(self.cg.OVERLORD_INK_SURGE_MAX_RANGE, 0.0)
        self.assertGreater(self.cg.OVERLORD_INK_SURGE_STOP, 0.0)
        # Boss surge is longer than Smudge swarm dash.
        self.assertGreater(
            self.cg.OVERLORD_INK_SURGE_DASH, self.cg.INK_DASH_DIST)
        blob = ' '.join([
            'OVERLORD_INK_SURGE_ENABLED',
            'overlordPickEnrageMove',
            'overlordSurgePos',
            'ink_surge',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)
        self.assertNotIn('sora', blob)

    def test_p2_combat_table_has_surge_kit(self):
        p1 = self.cg.overlordPhaseCombat(1)
        p2 = self.cg.overlordPhaseCombat(2)
        self.assertEqual(p1['moveMode'], 'rain')
        self.assertEqual(p2['moveMode'], 'enrage')
        for key in (
                'surgeMaxRange', 'surgeDash', 'surgeStop', 'surgeHitRange',
                'surgeNearMissRange', 'surgeDamage', 'surgeTelegraphDelay',
                'surgeCooldown'):
            self.assertIn(key, p2, msg='P2 missing %s' % key)
            self.assertNotIn(key, p1, msg='P1 should not carry %s' % key)
        # Three-note distance bands: slam < surge < rain engage.
        self.assertLess(p2['slamMeleeRange'], p2['surgeMaxRange'])
        self.assertLess(p2['surgeMaxRange'], p2['meleeRange'])
        self.assertLess(p2['slamHitRange'], p2['surgeHitRange'])
        self.assertLess(p2['surgeHitRange'], p2['attackHitRange'])

    def test_enrage_picker_three_notes(self):
        p2 = self.cg.overlordPhaseCombat(2)
        slam = self.cg.overlordSlamMeleeRange(p2)
        surge = self.cg.overlordSurgeMaxRange(p2)
        self.assertEqual(self.cg.overlordPickEnrageMove(0.0, p2), 'slam')
        self.assertEqual(self.cg.overlordPickEnrageMove(slam, p2), 'slam')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(slam + 0.05, p2), 'ink_surge')
        self.assertEqual(self.cg.overlordPickEnrageMove(surge, p2), 'ink_surge')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(surge + 0.05, p2), 'rain')
        # Disable flag restores two-note rain/slam.
        was = self.cg.OVERLORD_INK_SURGE_ENABLED
        try:
            self.cg.OVERLORD_INK_SURGE_ENABLED = False
            self.assertEqual(
                self.cg.overlordPickEnrageMove(slam + 0.05, p2), 'rain')
            self.assertEqual(self.cg.overlordPickEnrageMove(slam, p2), 'slam')
        finally:
            self.cg.OVERLORD_INK_SURGE_ENABLED = was

    def test_surge_math(self):
        nx, ny = self.cg.overlordSurgePos(
            0.0, 0.0, 10.0, 0.0, dash=4.6, stop=1.1)
        self.assertAlmostEqual(ny, 0.0, places=5)
        self.assertAlmostEqual(nx, 4.6, places=5)
        # Already inside stop → no move.
        nx2, ny2 = self.cg.overlordSurgePos(
            0.0, 0.0, 0.8, 0.0, dash=4.6, stop=1.1)
        self.assertAlmostEqual(nx2, 0.0, places=5)
        self.assertAlmostEqual(ny2, 0.0, places=5)
        # Short gap clamps dash to gap - stop.
        nx3, ny3 = self.cg.overlordSurgePos(
            0.0, 0.0, 3.0, 0.0, dash=4.6, stop=1.1)
        self.assertAlmostEqual(nx3, 3.0 - 1.1, places=5)

    def test_prior_gameplay_not_regressed(self):
        # Silly HP P2 threshold helpers still present.
        self.assertEqual(self.cg.normalizeFinalePhase(2), 2)
        self.assertEqual(self.cg.overlordP2AddCount(1), 0)
        self.assertGreater(self.cg.overlordP2AddCount(2), 0)
        # Ink Smudge kit intact.
        self.assertTrue(self.cg.INK_SMUDGE_KIT_ENABLED)
        self.assertEqual(
            self.cg.inkPickAttackMove(8.0), 'ink_dash')
        self.assertEqual(
            self.cg.inkPickAttackMove(2.0), 'ink_splat')
        # Role AI + other archetype kits intact.
        self.assertTrue(self.cg.ROLE_AI_ENABLED)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_BRUTE),
            self.cg.ROLE_HOLD)
        self.assertTrue(self.cg.BRUTE_SPIT_PROJECTILE_ENABLED)
        self.assertTrue(self.cg.SNARE_LASH_YANK_ENABLED)
        self.assertTrue(self.cg.OSWALD_BETRAYAL_KIT_ENABLED)

    def test_ai_surge_wiring_and_ko_helper(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for required in (
                '__pickOverlordMove',
                '__resolveOverlordRain',
                '__resolveOverlordInkSurge',
                '__surgeOverlordTowardTarget',
                '__damageToonAndCheckReclaimKo'):
            self.assertIn(required, methods)
        src = _read(rel)
        # Stats merge carries surge keys.
        apply = src[src.find('def _applyOverlordCombatStats'):]
        apply_end = apply.find('\n    def ', 1)
        apply_body = apply if apply_end < 0 else apply[:apply_end]
        self.assertIn('surgeMaxRange', apply_body)
        self.assertIn('surgeDash', apply_body)
        self.assertIn('surgeHitRange', apply_body)
        pick = src[src.find('def __pickOverlordMove'):]
        pick_end = pick.find('\n    def ', 1)
        pick_body = pick if pick_end < 0 else pick[:pick_end]
        self.assertIn('overlordPickEnrageMove', pick_body)
        resolve = src[src.find('def __resolveAttack'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn("move == 'ink_surge'", resolve_body)
        self.assertIn('__resolveOverlordInkSurge', resolve_body)
        surge = src[src.find('def __resolveOverlordInkSurge'):]
        surge_end = surge.find('\n    def ', 1)
        surge_body = surge if surge_end < 0 else surge[:surge_end]
        self.assertIn('__surgeOverlordTowardTarget', surge_body)
        self.assertIn('__damageToonAndCheckReclaimKo', surge_body)
        self.assertIn("context='ink_surge'", surge_body)
        self.assertNotIn('.takeDamage(', surge_body)
        # Whole-module: takeDamage only inside the KO helper.
        helper_idx = src.find('def __damageToonAndCheckReclaimKo')
        self.assertGreater(helper_idx, 0)
        after_helper = src[helper_idx:]
        next_def = after_helper.find('\n    def ', 1)
        helper_body = after_helper[:next_def]
        rest = after_helper[next_def:]
        self.assertIn('target.takeDamage(', helper_body)
        self.assertNotIn('target.takeDamage(', rest)

    def test_docs_mention_ink_surge(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('ink_surge', reclaim)
        # P2 section must mention the three-note kit.
        p2 = reclaim.split('phase 2', 1)[-1].split('clear again', 1)[0]
        self.assertIn('ink_surge', p2)
        self.assertIn('slam', p2)
        self.assertIn('rain', p2)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, p2)
        magic = _read('toontown/corruption/MagicWords.py').lower()
        self.assertIn('rain+surge+slam', magic)


if __name__ == '__main__':
    unittest.main()
