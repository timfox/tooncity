#!/usr/bin/env python3
"""Headless/AST tests: Overlord between-telegraph role AI (hold / circle).

Loads CorruptionGlobals without Panda3D. Asserts ROLE_CIRCLE tunables +
pure roleMoveGoal hold/circle helpers and AI wiring on
DistributedCorruptToonAI.__roleMoveToward. Climax approach asymmetry —
not cream FX deepen / no KH. Must not regress Smudge orbit, Oswald
press/circle, street kite/hold/flank, or Overlord rain/slam/surge kit.

Run from repo root:
  python3 tests/test_overlord_circle_role_ai.py
  python3 -m unittest tests.test_overlord_circle_role_ai -v
"""

from __future__ import annotations

import ast
import importlib.util
import math
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


class OverlordCircleRoleAiTest(unittest.TestCase):
    """Overlord ROLE_CIRCLE hold/circle tunables + helpers + AI wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_circle_globals_armed(self):
        self.assertTrue(self.cg.ROLE_AI_ENABLED)
        self.assertEqual(self.cg.ROLE_CIRCLE, 'circle')
        self.assertGreater(self.cg.OVERLORD_CIRCLE_PREFERRED, 3.0)
        self.assertGreater(self.cg.OVERLORD_CIRCLE_BAND, 0.0)
        self.assertGreater(
            self.cg.OVERLORD_CIRCLE_CLOSE_DIST,
            self.cg.OVERLORD_CIRCLE_PREFERRED)
        self.assertGreater(self.cg.OVERLORD_CIRCLE_LEAD, 0.0)
        self.assertGreater(self.cg.OVERLORD_CIRCLE_SPEED_SCALE, 1.0)
        self.assertLess(self.cg.OVERLORD_APPROACH_SPEED_SCALE, 1.0)
        # Preferred sits under P1 rain engage so rain/slam still fire.
        p1 = self.cg.OVERLORD_PHASE_COMBAT[1]
        self.assertLessEqual(
            self.cg.OVERLORD_CIRCLE_PREFERRED, float(p1['meleeRange']))
        self.assertLessEqual(
            self.cg.OVERLORD_CIRCLE_PREFERRED + self.cg.OVERLORD_CIRCLE_BAND,
            float(p1['meleeRange']))
        # No KH / cream deepen tokens in role names.
        blob = ' '.join([
            'ROLE_CIRCLE',
            'OVERLORD_CIRCLE_PREFERRED',
            'hold',
            'circle',
            'ink rain',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)
        self.assertNotIn('cream', blob)

    def test_overlord_is_circle_role(self):
        self.assertEqual(
            self.cg.overlordCombatRole(), self.cg.ROLE_CIRCLE)
        # Smudge still orbits via archetype; Overlord uses separate helper
        # because Overlord shares ARCHETYPE_INK with Smudge.
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_INK),
            self.cg.ROLE_ORBIT)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_CORRUPT_OSWALD),
            self.cg.ROLE_PRESS)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_BRUTE),
            self.cg.ROLE_HOLD)

    def test_overlord_hold_circle_goal(self):
        # Far: approach toward preferred ring (not straight onto the toon).
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_CIRCLE, 22.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, circleLead=4.0, circleCloseDist=15.0,
            flankSide=1)
        self.assertEqual(action, 'approach')
        self.assertAlmostEqual(gx, 6.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)
        # Mid range: circle on preferred ring, advanced tangentially.
        # toon at origin, Overlord on +X at 10; side +1 → CCW circle toward +Y.
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_CIRCLE, 10.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, circleLead=4.0, circleCloseDist=15.0,
            flankSide=1)
        self.assertEqual(action, 'circle')
        self.assertAlmostEqual(math.hypot(gx, gy), 6.0, places=5)
        self.assertGreater(gy, 0.0)
        # Opposite side flips the circle.
        gx2, gy2, action2 = self.cg.roleMoveGoal(
            self.cg.ROLE_CIRCLE, 10.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, circleLead=4.0, circleCloseDist=15.0,
            flankSide=-1)
        self.assertEqual(action2, 'circle')
        self.assertAlmostEqual(math.hypot(gx2, gy2), 6.0, places=5)
        self.assertLess(gy2, 0.0)
        # In band: hold plant (not Smudge retreat, not Oswald press-onto).
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_CIRCLE, 6.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, circleLead=4.0, circleCloseDist=15.0,
            flankSide=1)
        self.assertEqual(action, 'hold')
        self.assertAlmostEqual(gx, 6.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)
        # Too close: still hold (slam-ready plant).
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_CIRCLE, 2.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, circleLead=4.0, circleCloseDist=15.0,
            flankSide=1)
        self.assertEqual(action, 'hold')
        self.assertAlmostEqual(gx, 2.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)

    def test_circle_speed_scales(self):
        self.assertGreater(
            self.cg.roleMoveSpeedScale(self.cg.ROLE_CIRCLE, 'circle'), 1.0)
        self.assertLess(
            self.cg.roleMoveSpeedScale(self.cg.ROLE_CIRCLE, 'approach'), 1.0)
        self.assertEqual(
            self.cg.roleMoveSpeedScale(self.cg.ROLE_CIRCLE, 'hold'), 1.0)

    def test_distinct_from_smudge_and_oswald(self):
        # Same close geometry: Smudge retreats; Oswald presses; Overlord holds.
        gx_s, gy_s, act_s = self.cg.roleMoveGoal(
            self.cg.ROLE_ORBIT, 2.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, weave=4.0, orbitCloseDist=12.0,
            flankSide=1)
        gx_o, gy_o, act_o = self.cg.roleMoveGoal(
            self.cg.ROLE_PRESS, 2.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, pressCircle=4.0, pressCloseDist=14.0,
            flankSide=1)
        gx_v, gy_v, act_v = self.cg.roleMoveGoal(
            self.cg.ROLE_CIRCLE, 2.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, circleLead=4.0, circleCloseDist=15.0,
            flankSide=1)
        self.assertEqual(act_s, 'retreat')
        self.assertEqual(act_o, 'press')
        self.assertEqual(act_v, 'hold')
        self.assertAlmostEqual(math.hypot(gx_s, gy_s), 6.0, places=5)
        self.assertAlmostEqual(gx_o, 0.0, places=5)
        self.assertAlmostEqual(gy_o, 0.0, places=5)
        self.assertAlmostEqual(gx_v, 2.0, places=5)
        self.assertAlmostEqual(gy_v, 0.0, places=5)

    def test_overlord_kit_stays_attack_identity(self):
        p1 = self.cg.OVERLORD_PHASE_COMBAT[1]
        p2 = self.cg.OVERLORD_PHASE_COMBAT[2]
        self.assertEqual(p1.get('moveMode'), 'rising')
        self.assertEqual(p2.get('moveMode'), 'enrage')
        self.assertEqual(self.cg.overlordPickRisingMove(10.0), 'rain')
        self.assertEqual(self.cg.overlordPickRisingMove(2.0), 'slam')
        self.assertEqual(self.cg.overlordPickEnrageMove(10.0), 'rain')
        self.assertEqual(self.cg.overlordPickEnrageMove(6.0), 'ink_surge')
        self.assertEqual(self.cg.overlordPickEnrageMove(2.0), 'slam')
        self.assertTrue(self.cg.OVERLORD_RAIN_LINGER_ENABLED)
        self.assertTrue(self.cg.OVERLORD_SLAM_LINGER_ENABLED)
        self.assertTrue(self.cg.OVERLORD_INK_SURGE_LINGER_ENABLED)

    def test_ai_role_move_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        self.assertIn('__roleMoveToward', methods)
        self.assertIn('__chaseToward', methods)
        self.assertIn('_isOverlord', methods)
        src = _read(rel)
        role = src[src.find('def __roleMoveToward'):]
        role_end = role.find('\n    def ', 1)
        role_body = role if role_end < 0 else role[:role_end]
        self.assertIn('ROLE_AI_ENABLED', role_body)
        self.assertIn('overlordCombatRole', role_body)
        self.assertIn('archetypeCombatRole', role_body)
        self.assertIn('roleMoveGoal', role_body)
        self.assertIn('_isOverlord', role_body)
        # Overlord hold/circle called out; no forced chase early-out.
        self.assertIn('hold', role_body.lower())
        self.assertIn('circle', role_body.lower())
        self.assertNotIn(
            'if self._isOverlord() or not getattr', role_body)
        # Tick uses hold/circle between telegraphs on cooldown.
        tick = src[src.find('def __aiTick'):]
        tick_end = tick.find('\n    def ', 1)
        tick_body = tick if tick_end < 0 else tick[:tick_end]
        self.assertIn('_isOverlord', tick_body)
        self.assertIn('__roleMoveToward(target)', tick_body)
        # Class docstring names hold/circle for Overlord.
        self.assertIn('hold', src.lower())
        self.assertIn('circle', src.lower())
        # No KH branding in AI module role docs.
        self.assertNotIn('keyblade', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())

    def test_reclaim_docs_mention_overlord_hold_circle(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('role_circle', reclaim)
        self.assertIn('hold/circle', reclaim)
        self.assertIn('no keyblades', reclaim)


if __name__ == '__main__':
    unittest.main()
