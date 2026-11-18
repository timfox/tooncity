#!/usr/bin/env python3
"""Headless/AST tests for archetype role AI (kite / hold / flank).

Loads CorruptionGlobals without Panda3D. Asserts role tunables + pure
helpers (Gagster kite ring, Brute hold plant, Snare flank goal) and AI
wiring on DistributedCorruptToonAI (__roleMoveToward / __moveTowardXY).
Gameplay identity — not cream FX deepen. Must not regress Snare yank,
Gagster linger, Oswald chase, or juggle hang stun.

Run from repo root:
  python3 tests/test_archetype_role_ai.py
  python3 -m unittest tests.test_archetype_role_ai -v
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


class ArchetypeRoleAiTest(unittest.TestCase):
    """Role AI tunables + pure helpers + AI wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_role_globals_armed(self):
        self.assertTrue(self.cg.ROLE_AI_ENABLED)
        self.assertEqual(self.cg.ROLE_KITE, 'kite')
        self.assertEqual(self.cg.ROLE_HOLD, 'hold')
        self.assertEqual(self.cg.ROLE_FLANK, 'flank')
        self.assertGreater(self.cg.GAGSTER_KITE_PREFERRED, 5.0)
        self.assertGreater(self.cg.GAGSTER_KITE_BAND, 0.0)
        self.assertGreater(self.cg.BRUTE_HOLD_RANGE, 4.0)
        self.assertGreater(self.cg.SNARE_FLANK_OFFSET, 1.0)
        self.assertGreater(
            self.cg.SNARE_FLANK_CLOSE_DIST, self.cg.SNARE_FLANK_OFFSET)
        # No KH branding in role names.
        blob = ' '.join([
            'ROLE_AI_ENABLED',
            'archetypeCombatRole',
            'roleMoveGoal',
            'Gagster kite',
            'Brute hold',
            'Snare flank',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_archetype_combat_roles(self):
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_GAGSTER),
            self.cg.ROLE_KITE)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_BRUTE),
            self.cg.ROLE_HOLD)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_SNARE),
            self.cg.ROLE_FLANK)
        # Smudge / Oswald stay plain chase — do not regress nearest-chase.
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_INK),
            self.cg.ROLE_CHASE)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_CORRUPT_OSWALD),
            self.cg.ROLE_CHASE)

    def test_gagster_kite_ring(self):
        # Far: approach toward preferred ring (not onto the toon).
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_KITE, 20.0, 0.0, 0.0, 0.0, preferred=10.0, band=1.0)
        self.assertEqual(action, 'approach')
        self.assertAlmostEqual(gx, 10.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)
        # Too close: retreat out to the ring.
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_KITE, 3.0, 0.0, 0.0, 0.0, preferred=10.0, band=1.0)
        self.assertEqual(action, 'retreat')
        self.assertAlmostEqual(gx, 10.0, places=5)
        # In band: hold / plant for lob.
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_KITE, 10.0, 0.0, 0.0, 0.0, preferred=10.0, band=1.5)
        self.assertEqual(action, 'hold')
        self.assertAlmostEqual(gx, 10.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)

    def test_brute_hold_plant(self):
        # Outside hold range → approach the toon.
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_HOLD, 15.0, 0.0, 0.0, 0.0, holdRange=8.0)
        self.assertEqual(action, 'approach')
        self.assertAlmostEqual(gx, 0.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)
        # Inside → plant (stay put).
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_HOLD, 5.0, 0.0, 0.0, 0.0, holdRange=8.0)
        self.assertEqual(action, 'hold')
        self.assertAlmostEqual(gx, 5.0, places=5)
        self.assertAlmostEqual(gy, 0.0, places=5)
        # Hold chase is sluggish vs default.
        self.assertLess(
            self.cg.roleMoveSpeedScale(self.cg.ROLE_HOLD, 'approach'), 1.0)

    def test_snare_flank_offset(self):
        # Far out: close first.
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_FLANK, 20.0, 0.0, 0.0, 0.0,
            flankOffset=5.0, flankCloseDist=12.0, flankSide=1)
        self.assertEqual(action, 'approach')
        self.assertAlmostEqual(gx, 0.0, places=5)
        # Mid range: perpendicular flank goal (toon at origin, snare on +X).
        # toon→self = (8, 0); perp (-uy, ux) with side +1 → (0, 5).
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_FLANK, 8.0, 0.0, 0.0, 0.0,
            flankOffset=5.0, flankCloseDist=12.0, flankSide=1)
        self.assertEqual(action, 'flank')
        self.assertAlmostEqual(gx, 0.0, places=5)
        self.assertAlmostEqual(gy, 5.0, places=5)
        # Opposite side flips the flank.
        gx2, gy2, action2 = self.cg.roleMoveGoal(
            self.cg.ROLE_FLANK, 8.0, 0.0, 0.0, 0.0,
            flankOffset=5.0, flankCloseDist=12.0, flankSide=-1)
        self.assertEqual(action2, 'flank')
        self.assertAlmostEqual(gy2, -5.0, places=5)
        self.assertEqual(self.cg.snareFlankSide(10), 1)
        self.assertEqual(self.cg.snareFlankSide(11), -1)

    def test_default_chase_goal(self):
        gx, gy, action = self.cg.roleMoveGoal(
            self.cg.ROLE_CHASE, 4.0, 2.0, 1.0, 3.0)
        self.assertEqual(action, 'chase')
        self.assertAlmostEqual(gx, 1.0, places=5)
        self.assertAlmostEqual(gy, 3.0, places=5)

    def test_prior_gameplay_not_regressed(self):
        # Snare yank (#314), Gagster linger (#311), Oswald chase (#313).
        self.assertTrue(self.cg.SNARE_LASH_YANK_ENABLED)
        self.assertGreater(self.cg.SNARE_LASH_YANK_DIST, 0.5)
        self.assertTrue(self.cg.GAGSTER_PUDDLE_LINGER_ENABLED)
        self.assertGreater(self.cg.GAGSTER_PUDDLE_LINGER_SEC, 1.0)
        self.assertIn(
            self.cg.ARCHETYPE_CORRUPT_OSWALD, self.cg.ARCHETYPE_STATS)
        oswald = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertEqual(oswald.get('name'), 'Corrupted Oswald')
        self.assertGreater(float(oswald.get('chaseSpeed', 0)), 8.0)
        # Betrayal kit stays attack identity; role AI still plain chase.
        self.assertEqual(oswald.get('attackMove'), 'betrayal_lunge')
        self.assertTrue(self.cg.OSWALD_BETRAYAL_KIT_ENABLED)
        # Brute hold still plants; spit projectile kit stays armed beside role AI.
        brute = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_BRUTE]
        self.assertEqual(brute.get('attackMove'), 'spit')
        self.assertTrue(self.cg.BRUTE_SPIT_PROJECTILE_ENABLED)

    def test_ai_role_move_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        self.assertIn('__roleMoveToward', methods)
        self.assertIn('__moveTowardXY', methods)
        self.assertIn('__faceTowardXY', methods)
        self.assertIn('__chaseToward', methods)
        # Keep prior gameplay intact on the same AI module.
        self.assertIn('__yankTargetTowardSnare', methods)
        self.assertIn('__armGagsterPuddleLinger', methods)
        self.assertIn('isJuggleHangStunned', methods)
        src = _read(rel)
        self.assertIn('_juggleHangStunUntil', src)
        tick = src[src.find('def __aiTick'):]
        tick_end = tick.find('\n    def ', 1)
        tick_body = tick if tick_end < 0 else tick[:tick_end]
        self.assertIn('__roleMoveToward(target)', tick_body)
        self.assertIn('isJuggleHangStunned', tick_body)
        role = src[src.find('def __roleMoveToward'):]
        role_end = role.find('\n    def ', 1)
        role_body = role if role_end < 0 else role[:role_end]
        self.assertIn('ROLE_AI_ENABLED', role_body)
        self.assertIn('archetypeCombatRole', role_body)
        self.assertIn('roleMoveGoal', role_body)
        self.assertIn('snareFlankSide', role_body)
        self.assertIn('_isOverlord', role_body)
        # Overlord / Smudge path still has nearest chase.
        self.assertIn('__chaseToward(target)', role_body)

    def test_reclaim_docs_mention_role_ai(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('role ai', reclaim)
        self.assertIn('kite', reclaim)
        self.assertIn('flank', reclaim)
        # Doc bans KH branding explicitly (same line as Overlord framing).
        self.assertIn('no keyblades', reclaim)


if __name__ == '__main__':
    unittest.main()
