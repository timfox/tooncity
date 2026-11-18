#!/usr/bin/env python3
"""Headless/AST tests: Corrupted Oswald betrayal attack kit (not smack reskin).

Loads CorruptionGlobals without Panda3D. Asserts betrayal_lunge / stain_burst
tunables + pure helpers (pick move, lunge dash, shove) and AI / chase / thin
hackslash shove wiring. Gameplay identity — not cream FX deepen. Must not
regress role AI, Brute spit, Snare yank, or juggle hang stun.

Run from repo root:
  python3 tests/test_oswald_betrayal_kit.py
  python3 -m unittest tests.test_oswald_betrayal_kit -v
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


def _module_names(rel: str) -> set[str]:
    tree = ast.parse(_read(rel))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


class OswaldBetrayalKitTest(unittest.TestCase):
    """Betrayal kit tunables / helpers / AI wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_betrayal_kit_globals_armed(self):
        self.assertTrue(self.cg.OSWALD_BETRAYAL_KIT_ENABLED)
        self.assertTrue(self.cg.OSWALD_BETRAYAL_LUNGE_ENABLED)
        self.assertTrue(self.cg.OSWALD_STAIN_BURST_SECONDARY_ENABLED)
        self.assertTrue(self.cg.OSWALD_BETRAYAL_SHOVE_ENABLED)
        self.assertGreater(self.cg.OSWALD_BETRAYAL_LUNGE_DASH, 2.0)
        self.assertGreater(self.cg.OSWALD_STAIN_BURST_MELEE_RANGE, 2.0)
        self.assertGreater(self.cg.OSWALD_BETRAYAL_SHOVE_DIST, 0.5)
        self.assertGreater(self.cg.OSWALD_BETRAYAL_SHOVE_SEC, 0.0)
        self.assertLess(self.cg.OSWALD_BETRAYAL_SHOVE_SEC, 0.5)
        # Burst is the close secondary — inside lunge engage.
        oswald = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertLess(
            self.cg.OSWALD_STAIN_BURST_MELEE_RANGE,
            float(oswald.get('meleeRange', 6.4)))
        blob = ' '.join([
            'OSWALD_BETRAYAL_KIT_ENABLED',
            'oswaldPickAttackMove',
            'oswaldBetrayalShoveDelta',
            'betrayal_lunge',
            'stain_burst',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)
        self.assertNotIn('sora', blob)

    def test_oswald_archetype_betrayal_kit_stats(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertEqual(stats.get('attackMove'), 'betrayal_lunge')
        self.assertGreater(float(stats.get('meleeRange', 0)), 5.0)
        self.assertGreater(float(stats.get('lungeDashDist', 0)), 2.0)
        self.assertGreater(float(stats.get('burstMeleeRange', 0)), 2.0)
        self.assertGreater(int(stats.get('burstDamage', 0)),
                           int(stats.get('lungeDamage', 0)) - 1)
        self.assertGreater(float(stats.get('shoveDist', 0)), 0.5)
        # Still chase role — kit is attack identity, not role AI.
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_CORRUPT_OSWALD),
            self.cg.ROLE_CHASE)

    def test_oswald_pick_attack_move(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        # Far → lunge; close → stain burst.
        self.assertEqual(
            self.cg.oswaldPickAttackMove(8.0, stats), 'betrayal_lunge')
        self.assertEqual(
            self.cg.oswaldPickAttackMove(2.0, stats), 'stain_burst')
        # At exact burst edge → burst.
        edge = self.cg.oswaldBurstMeleeRange(stats)
        self.assertEqual(
            self.cg.oswaldPickAttackMove(edge, stats), 'stain_burst')
        self.assertEqual(
            self.cg.oswaldPickAttackMove(edge + 0.1, stats), 'betrayal_lunge')

    def test_oswald_lunge_dash_math(self):
        # Dash closes toward target but stops short of overshoot.
        nx, ny = self.cg.oswaldLungeDashPos(
            0.0, 0.0, 10.0, 0.0, dash=4.0, stop=0.85)
        self.assertAlmostEqual(ny, 0.0, places=5)
        self.assertAlmostEqual(nx, 4.0, places=5)
        # Already inside stop → no move.
        nx2, ny2 = self.cg.oswaldLungeDashPos(
            0.0, 0.0, 0.5, 0.0, dash=4.0, stop=0.85)
        self.assertAlmostEqual(nx2, 0.0, places=5)
        self.assertAlmostEqual(ny2, 0.0, places=5)
        # Short gap clamps dash to gap - stop.
        nx3, ny3 = self.cg.oswaldLungeDashPos(
            0.0, 0.0, 3.0, 0.0, dash=4.0, stop=0.85)
        self.assertAlmostEqual(nx3, 3.0 - 0.85, places=5)

    def test_oswald_betrayal_shove_math(self):
        # Opposite of Snare yank — push away along the Oswald→toon vector.
        dx, dy = self.cg.oswaldBetrayalShoveDelta(
            0.0, 0.0, 4.0, 0.0, dist=2.0)
        self.assertAlmostEqual(dx, 2.0, places=5)
        self.assertAlmostEqual(dy, 0.0, places=5)
        nx, ny = self.cg.oswaldBetrayalShovePos(
            0.0, 0.0, 4.0, 0.0, dist=2.0)
        self.assertAlmostEqual(nx, 6.0, places=5)
        self.assertAlmostEqual(ny, 0.0, places=5)
        # Coincident → fallback +Y shove.
        dx0, dy0 = self.cg.oswaldBetrayalShoveDelta(
            1.0, 1.0, 1.0, 1.0, dist=2.0)
        self.assertAlmostEqual(dx0, 0.0, places=5)
        self.assertAlmostEqual(dy0, 2.0, places=5)
        # Zero dist → no shove.
        self.assertEqual(
            self.cg.oswaldBetrayalShoveDelta(0.0, 0.0, 3.0, 0.0, dist=0.0),
            (0.0, 0.0))

    def test_prior_gameplay_not_regressed(self):
        # Role AI (#315), Brute spit (#316), Snare yank (#314), Gagster linger.
        self.assertTrue(self.cg.ROLE_AI_ENABLED)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_GAGSTER),
            self.cg.ROLE_KITE)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_BRUTE),
            self.cg.ROLE_HOLD)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_SNARE),
            self.cg.ROLE_FLANK)
        brute = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_BRUTE]
        self.assertEqual(brute.get('attackMove'), 'spit')
        self.assertTrue(self.cg.BRUTE_SPIT_PROJECTILE_ENABLED)
        self.assertTrue(self.cg.BRUTE_SLAM_SECONDARY_ENABLED)
        self.assertTrue(self.cg.SNARE_LASH_YANK_ENABLED)
        self.assertGreater(self.cg.SNARE_LASH_YANK_DIST, 0.5)
        self.assertTrue(self.cg.GAGSTER_PUDDLE_LINGER_ENABLED)
        # Ink Smudge still default smack (separate gap) — Oswald is not Smudge.
        ink = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_INK]
        self.assertNotEqual(ink.get('attackMove', 'smack'), 'betrayal_lunge')

    def test_ai_betrayal_kit_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for required in (
                '__resolveOswaldBetrayalLunge',
                '__resolveOswaldStainBurst',
                '__dashOswaldTowardTarget',
                '__shoveTargetFromOswald'):
            self.assertIn(required, methods)
        # Keep prior gameplay intact on the same AI module.
        self.assertIn('__resolveBruteSpit', methods)
        self.assertIn('__yankTargetTowardSnare', methods)
        self.assertIn('__roleMoveToward', methods)
        self.assertIn('isJuggleHangStunned', methods)
        src = _read(rel)
        self.assertIn('_juggleHangStunUntil', src)
        begin = src[src.find('def __beginAttack'):]
        begin_end = begin.find('\n    def ', 1)
        begin_body = begin if begin_end < 0 else begin[:begin_end]
        self.assertIn('oswaldPickAttackMove', begin_body)
        self.assertIn('ARCHETYPE_CORRUPT_OSWALD', begin_body)
        resolve = src[src.find('def __resolveAttack'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn("move == 'betrayal_lunge'", resolve_body)
        self.assertIn("move == 'stain_burst'", resolve_body)
        self.assertIn('__resolveOswaldBetrayalLunge', resolve_body)
        self.assertIn('__resolveOswaldStainBurst', resolve_body)
        # Single-target path still yanks Snare and shoves Oswald.
        single = src[src.find('def __resolveSingleTargetHit'):]
        single_end = single.find('\n    def ', 1)
        single_body = single if single_end < 0 else single[:single_end]
        self.assertIn('__yankTargetTowardSnare(target)', single_body)
        self.assertIn('__shoveTargetFromOswald(target)', single_body)
        shove = src[src.find('def __shoveTargetFromOswald'):]
        shove_end = shove.find('\n    def ', 1)
        shove_body = shove if shove_end < 0 else shove[:shove_end]
        self.assertIn('OSWALD_BETRAYAL_SHOVE_ENABLED', shove_body)
        self.assertIn('ARCHETYPE_CORRUPT_OSWALD', shove_body)
        self.assertIn('oswaldBetrayalShovePos', shove_body)

    def test_chase_module_kit_hook(self):
        rel = 'toontown/campaign/OswaldBetrayalChase.py'
        names = _module_names(rel)
        self.assertIn('chaseAttackMove', names)
        self.assertIn('spawnCorruptOswald', names)
        src = _read(rel)
        self.assertIn('betrayal_lunge', src)
        self.assertIn('OSWALD_BETRAYAL_KIT_ENABLED', src)
        self.assertIn("attackMove", src)
        self.assertIn('betrayal lunge', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())
        self.assertNotIn('sora', src.lower())

    def test_melee_hurt_react_shove_wiring(self):
        rel = 'toontown/hackslash/MeleeCombat.py'
        methods = _class_method_names(
            _module_ast(rel), 'MeleeCombatController')
        self.assertIn('_shoveAvatarFromOswald', methods)
        self.assertIn('_clearOswaldBetrayalShove', methods)
        self.assertIn('_yankAvatarTowardSnare', methods)
        src = _read(rel)
        hit = src[src.find('def _onCorruptHitPlayer'):]
        hit_end = hit.find('\n    def ', 1)
        hit_body = hit if hit_end < 0 else hit[:hit_end]
        self.assertIn('_yankAvatarTowardSnare(corrupt)', hit_body)
        self.assertIn('_shoveAvatarFromOswald(corrupt)', hit_body)
        shove = src[src.find('def _shoveAvatarFromOswald'):]
        shove_end = shove.find('\n    def ', 1)
        shove_body = shove if shove_end < 0 else shove[:shove_end]
        self.assertIn('OSWALD_BETRAYAL_SHOVE_ENABLED', shove_body)
        self.assertIn('ARCHETYPE_CORRUPT_OSWALD', shove_body)
        self.assertIn('oswaldBetrayalShovePos', shove_body)
        self.assertIn('LerpPosInterval', shove_body)
        disable = src[src.find('def disable(self):'):]
        self.assertIn('_clearOswaldBetrayalShove', disable)
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('betrayal_lunge', reclaim)
        self.assertIn('stain_burst', reclaim)


if __name__ == '__main__':
    unittest.main()
