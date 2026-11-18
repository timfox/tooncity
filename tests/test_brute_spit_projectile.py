#!/usr/bin/env python3
"""Headless/AST tests for Sludge Brute spit projectile + slam secondary.

Loads CorruptionGlobals without Panda3D. Asserts spit/slam tunables + pure
helpers (aim clamp, flight lerp, splash, pick move) and AI wiring on
DistributedCorruptToonAI (__resolveBruteSpit / trail tick / clear). Thin
client spit blob travel tracks AI travel sec. Gameplay identity — not cream
FX deepen. Must not regress role AI, Snare yank, Gagster linger, or juggle stun.

Run from repo root:
  python3 tests/test_brute_spit_projectile.py
  python3 -m unittest tests.test_brute_spit_projectile -v
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


class BruteSpitProjectileTest(unittest.TestCase):
    """Spit projectile + slam tunables / helpers / AI wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_spit_slam_globals_armed(self):
        self.assertTrue(self.cg.BRUTE_SPIT_PROJECTILE_ENABLED)
        self.assertTrue(self.cg.BRUTE_SLAM_SECONDARY_ENABLED)
        self.assertGreater(self.cg.BRUTE_SPIT_TRAVEL_SEC, 0.1)
        self.assertGreater(self.cg.BRUTE_SPIT_MAX_RANGE, 6.0)
        self.assertGreater(self.cg.BRUTE_SPIT_LAND_RADIUS, 1.0)
        self.assertGreater(self.cg.BRUTE_SPIT_TRAIL_TICK_SEC, 0.0)
        self.assertLess(
            self.cg.BRUTE_SPIT_TRAIL_TICK_SEC, self.cg.BRUTE_SPIT_TRAVEL_SEC)
        self.assertGreater(self.cg.BRUTE_SPIT_TRAIL_RADIUS, 0.5)
        self.assertGreaterEqual(self.cg.BRUTE_SPIT_TRAIL_DAMAGE, 1)
        self.assertGreater(self.cg.BRUTE_SLAM_MELEE_RANGE, 2.0)
        # Land splash is local; mid-range reach is projectile max range.
        self.assertLess(
            self.cg.BRUTE_SPIT_LAND_RADIUS, self.cg.BRUTE_SPIT_MAX_RANGE)
        self.assertLess(
            self.cg.BRUTE_SLAM_MELEE_RANGE, self.cg.BRUTE_SPIT_MAX_RANGE)
        blob = ' '.join([
            'BRUTE_SPIT_PROJECTILE_ENABLED',
            'bruteSpitAimPos',
            'brutePickAttackMove',
            'BRUTE_SLAM_SECONDARY_ENABLED',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_brute_archetype_spit_slam_stats(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_BRUTE]
        self.assertEqual(stats.get('attackMove'), 'spit')
        self.assertGreater(float(stats.get('meleeRange', 0)), 6.0)
        self.assertAlmostEqual(
            float(stats.get('attackHitRange')),
            float(self.cg.BRUTE_SPIT_LAND_RADIUS),
            places=2)
        self.assertGreater(float(stats.get('spitMaxRange', 0)), 8.0)
        self.assertGreater(float(stats.get('spitTravelSec', 0)), 0.1)
        self.assertGreater(float(stats.get('spitTrailRadius', 0)), 0.5)
        self.assertGreaterEqual(int(stats.get('spitTrailDamage', 0)), 1)
        self.assertGreater(float(stats.get('slamMeleeRange', 0)), 2.0)
        self.assertGreater(int(stats.get('slamDamage', 0)), int(
            stats.get('attackDamage', 0)))
        # Slam is the close secondary — shorter engage than spit plant.
        self.assertLess(
            float(stats.get('slamMeleeRange')),
            float(stats.get('meleeRange')))

    def test_aim_clamp_and_flight_lerp(self):
        # Aim inside max — unchanged.
        lx, ly = self.cg.bruteSpitAimPos(0.0, 0.0, 5.0, 0.0, maxRange=11.0)
        self.assertAlmostEqual(lx, 5.0, places=5)
        self.assertAlmostEqual(ly, 0.0, places=5)
        # Aim beyond max — clamped on the ray.
        lx, ly = self.cg.bruteSpitAimPos(0.0, 0.0, 20.0, 0.0, maxRange=11.0)
        self.assertAlmostEqual(lx, 11.0, places=5)
        self.assertAlmostEqual(ly, 0.0, places=5)
        # Mid-flight lerp.
        px, py = self.cg.bruteSpitPosAtFrac(0.0, 0.0, 10.0, 0.0, 0.5)
        self.assertAlmostEqual(px, 5.0, places=5)
        self.assertAlmostEqual(py, 0.0, places=5)
        self.assertTrue(self.cg.isInsideBruteSpitSplash(0.0, 0.0, 3.5))
        self.assertTrue(self.cg.isInsideBruteSpitSplash(2.0, 2.0, 3.5))
        self.assertFalse(self.cg.isInsideBruteSpitSplash(3.0, 3.0, 3.5))

    def test_pick_spit_vs_slam(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_BRUTE]
        slam_range = float(stats['slamMeleeRange'])
        self.assertEqual(
            self.cg.brutePickAttackMove(slam_range - 0.1, stats), 'slam')
        self.assertEqual(
            self.cg.brutePickAttackMove(slam_range + 0.5, stats), 'spit')
        self.assertEqual(
            self.cg.brutePickAttackMove(9.0, stats), 'spit')
        # Helpers respect archetype overrides.
        self.assertAlmostEqual(
            self.cg.bruteSpitTravelSec(stats),
            float(stats['spitTravelSec']),
            places=4)
        self.assertEqual(
            self.cg.bruteSpitTrailDamage({'spitTrailDamage': 0}), 1)

    def test_ai_spit_projectile_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for name in (
                '__resolveBruteSpit',
                '__tickBruteSpitProjectile',
                '__applyBruteSpitSplash',
                '__clearBruteSpitProjectile'):
            self.assertIn(name, methods, msg='AI missing %s' % name)
        src = _read(rel)
        self.assertIn("move == 'spit'", src)
        self.assertIn('brutePickAttackMove', src)
        self.assertIn('_spitAimXY', src)
        self.assertIn('_spitProjectile', src)
        self.assertIn("uniqueName('brute-spit-projectile')", src)
        self.assertIn('bruteSpitAimPos', src)
        self.assertIn('bruteSpitPosAtFrac', src)
        self.assertIn('isInsideBruteSpitSplash', src)
        # Resolve routes spit before generic single-target smack.
        resolve = src[src.find('def __resolveAttack'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn("__resolveBruteSpit()", resolve_body)
        self.assertLess(
            resolve_body.find("move == 'spit'"),
            resolve_body.find('__resolveSingleTargetHit'))
        # Clear on delete / defeat / juggle cancel so tasks do not leak.
        delete_snip = src[src.find('def delete(self):'):]
        self.assertIn('__clearBruteSpitProjectile', delete_snip)
        defeat = src[src.find('def __defeat'):]
        defeat_end = defeat.find('\n    def ', 1)
        defeat_body = defeat if defeat_end < 0 else defeat[:defeat_end]
        self.assertIn('__clearBruteSpitProjectile', defeat_body)
        # Quiet trail ticks — land owns announceAttackHit.
        tick = src[src.find('def __tickBruteSpitProjectile'):]
        # Trail branch uses trailOnly=True before land announce.
        self.assertIn('trailOnly=True', tick)
        self.assertIn("sendUpdate('announceAttackHit'", tick)

    def test_client_blob_tracks_ai_travel(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        src = _read(rel)
        spit = src[src.find('def __playSpitBlob'):]
        spit_end = spit.find('\n    def ', 1)
        spit_body = spit if spit_end < 0 else spit[:spit_end]
        self.assertIn('BRUTE_SPIT_TRAVEL_SEC', spit_body)
        # Blob travel constant stays in sync with AI default travel.
        self.assertAlmostEqual(
            float(self.cg.BRUTE_SPIT_BLOB_TRAVEL),
            float(self.cg.BRUTE_SPIT_TRAVEL_SEC),
            places=4)

    def test_prior_gameplay_not_regressed(self):
        # Role AI (#315), Snare yank (#314), Gagster linger (#311), juggle stun.
        self.assertTrue(self.cg.ROLE_AI_ENABLED)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_BRUTE),
            self.cg.ROLE_HOLD)
        self.assertTrue(self.cg.SNARE_LASH_YANK_ENABLED)
        self.assertTrue(self.cg.GAGSTER_PUDDLE_LINGER_ENABLED)
        ai_src = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn('__roleMoveToward', ai_src)
        self.assertIn('__yankTargetTowardSnare', ai_src)
        self.assertIn('__armGagsterPuddleLinger', ai_src)
        self.assertIn('isJuggleHangStunned', ai_src)
        self.assertIn('_juggleHangStunUntil', ai_src)

    def test_reclaim_docs_mention_projectile(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('traveling projectile', reclaim)
        self.assertIn('slam secondary', reclaim)
        # Doc bans KH branding explicitly (same Overlord framing as role AI).
        self.assertIn('no keyblades', reclaim)


if __name__ == '__main__':
    unittest.main()
