#!/usr/bin/env python3
"""Headless/AST tests: Corrupted Oswald chase role AI (press / circle).

Loads CorruptionGlobals without Panda3D. Asserts ROLE_PRESS tunables +
pure roleMoveGoal press/circle helpers and AI wiring on
DistributedCorruptToonAI.__roleMoveToward. Betrayal climax approach
asymmetry — not cream FX deepen / no KH. Must not regress Smudge orbit,
street kite/hold/flank, or Oswald betrayal kit identity.

Run from repo root:
  python3 tests/test_oswald_chase_role_ai.py
  python3 -m unittest tests.test_oswald_chase_role_ai -v
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


class OswaldChaseRoleAiTest(unittest.TestCase):
    """Oswald ROLE_PRESS press/circle tunables + helpers + AI wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_press_globals_armed(self):
        self.assertTrue(self.cg.ROLE_AI_ENABLED)
        self.assertEqual(self.cg.ROLE_PRESS, 'press')
        self.assertGreater(self.cg.OSWALD_PRESS_PREFERRED, 3.0)
        self.assertGreater(self.cg.OSWALD_PRESS_BAND, 0.0)
        self.assertGreater(
            self.cg.OSWALD_PRESS_CLOSE_DIST, self.cg.OSWALD_PRESS_PREFERRED)
        self.assertGreater(self.cg.OSWALD_PRESS_CIRCLE, 0.0)
        self.assertGreater(self.cg.OSWALD_PRESS_SPEED_SCALE, 1.0)
        self.assertGreater(self.cg.OSWALD_CIRCLE_SPEED_SCALE, 1.0)
        # Preferred sits at/under lunge engage so betrayal_lunge still fires.
        oswald = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertLessEqual(
            self.cg.OSWALD_PRESS_PREFERRED, float(oswald['meleeRange']))
        # No KH / cream deepen tokens in role names.
        blob = ' '.join([
            'ROLE_PRESS',
            'OSWALD_PRESS_PREFERRED',
            'press',
            'circle',
            'betrayal lunge',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)
        self.assertNotIn('cream', blob)

    def test_oswald_is_press_role(self):
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_CORRUPT_OSWALD),
            self.cg.ROLE_PRESS)
        # Street roles stay distinct; Overlord path still skips via AI gate.
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_INK),
            self.cg.ROLE_ORBIT)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_GAGSTER),
            self.cg.ROLE_KITE)

    def test_oswald_press_circle_goal(self):
        # Far: press toward preferred ring (not straight onto the toon).
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_PRESS, 22.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, pressCircle=4.0, pressCloseDist=14.0,
            flankSide=1)
        self.assertEqual(action, 'press')
        self.assertAlmostEqual(gx, 6.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)
        # Mid range: circle on preferred ring, advanced tangentially.
        # toon at origin, Oswald on +X at 8; side +1 → CCW circle toward +Y.
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_PRESS, 8.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, pressCircle=4.0, pressCloseDist=14.0,
            flankSide=1)
        self.assertEqual(action, 'circle')
        self.assertAlmostEqual(math.hypot(gx, gy), 6.0, places=5)
        self.assertGreater(gy, 0.0)
        # Opposite side flips the circle.
        gx2, gy2, action2 = self.cg.roleMoveGoal(
            self.cg.ROLE_PRESS, 8.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, pressCircle=4.0, pressCloseDist=14.0,
            flankSide=-1)
        self.assertEqual(action2, 'circle')
        self.assertAlmostEqual(math.hypot(gx2, gy2), 6.0, places=5)
        self.assertLess(gy2, 0.0)
        # Too close: press onto the toon for stain_burst (not Smudge retreat).
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_PRESS, 2.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, pressCircle=4.0, pressCloseDist=14.0,
            flankSide=1)
        self.assertEqual(action, 'press')
        self.assertAlmostEqual(gx, 0.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)

    def test_press_speed_scales(self):
        self.assertGreater(
            self.cg.roleMoveSpeedScale(self.cg.ROLE_PRESS, 'press'), 1.0)
        self.assertGreater(
            self.cg.roleMoveSpeedScale(self.cg.ROLE_PRESS, 'circle'), 1.0)
        # Press-in is snappier than mid circle.
        self.assertGreater(
            self.cg.roleMoveSpeedScale(self.cg.ROLE_PRESS, 'press'),
            self.cg.roleMoveSpeedScale(self.cg.ROLE_PRESS, 'circle'))

    def test_distinct_from_smudge_orbit(self):
        # Same mid geometry: Smudge orbits (retreat when close); Oswald presses.
        gx_s, gy_s, act_s = self.cg.roleMoveGoal(
            self.cg.ROLE_ORBIT, 2.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, weave=4.0, orbitCloseDist=12.0,
            flankSide=1)
        gx_o, gy_o, act_o = self.cg.roleMoveGoal(
            self.cg.ROLE_PRESS, 2.0, 0.0, 0.0, 0.0,
            preferred=6.0, band=1.0, pressCircle=4.0, pressCloseDist=14.0,
            flankSide=1)
        self.assertEqual(act_s, 'retreat')
        self.assertEqual(act_o, 'press')
        self.assertAlmostEqual(math.hypot(gx_s, gy_s), 6.0, places=5)
        self.assertAlmostEqual(gx_o, 0.0, places=5)
        self.assertAlmostEqual(gy_o, 0.0, places=5)

    def test_betrayal_kit_stays_attack_identity(self):
        oswald = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertEqual(oswald.get('attackMove'), 'betrayal_lunge')
        self.assertTrue(self.cg.OSWALD_BETRAYAL_KIT_ENABLED)
        self.assertTrue(self.cg.OSWALD_BETRAYAL_SHOVE_ENABLED)
        self.assertEqual(self.cg.oswaldPickAttackMove(8.0), 'betrayal_lunge')
        self.assertEqual(self.cg.oswaldPickAttackMove(2.0), 'stain_burst')

    def test_ai_role_move_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        self.assertIn('__roleMoveToward', methods)
        self.assertIn('__chaseToward', methods)
        src = _read(rel)
        role = src[src.find('def __roleMoveToward'):]
        role_end = role.find('\n    def ', 1)
        role_body = role if role_end < 0 else role[:role_end]
        self.assertIn('ROLE_AI_ENABLED', role_body)
        self.assertIn('archetypeCombatRole', role_body)
        self.assertIn('roleMoveGoal', role_body)
        self.assertIn('_isOverlord', role_body)
        # Oswald press/circle called out; Overlord still nearest chase.
        self.assertIn('press', role_body.lower())
        self.assertIn('circle', role_body.lower())
        self.assertIn('__chaseToward(target)', role_body)
        # Class docstring names press/circle for Oswald.
        self.assertIn('press/circle', src.lower().replace(' ', ''))
        # No KH branding in AI module role docs.
        self.assertNotIn('keyblade', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())

    def test_reclaim_docs_mention_oswald_press(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('role_press', reclaim)
        self.assertIn('press/circle', reclaim)
        self.assertIn('no keyblades', reclaim)


if __name__ == '__main__':
    unittest.main()
