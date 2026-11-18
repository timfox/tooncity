#!/usr/bin/env python3
"""Headless unit tests for Ink Overlord P1/P2 combat AI tunables.

Panda-free: imports CorruptionGlobals + CampaignGlobals ACTS phase2 wiring
via file-path loaders (same pattern as test_headless_loop_smoke).

Run from repo root:
  python3 tests/test_overlord_phase_combat.py
  python3 -m unittest tests.test_overlord_phase_combat -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_module(rel: str, name: str):
    path = REPO_ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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


class OverlordPhaseCombatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cg = _load_module(
            'toontown/corruption/CorruptionGlobals.py',
            'overlord_phase_combat_CorruptionGlobals')

    def test_phase_combat_tables_differ(self):
        p1 = self.cg.overlordPhaseCombat(1)
        p2 = self.cg.overlordPhaseCombat(2)
        self.assertIsNotNone(p1)
        self.assertIsNotNone(p2)
        self.assertEqual(p1['id'], 'rising-rain')
        self.assertEqual(p2['id'], 'unleashed-enrage')
        self.assertEqual(p1['moveMode'], 'rising')
        self.assertEqual(p2['moveMode'], 'enrage')
        self.assertTrue(p1['aoe'])
        self.assertTrue(p2['aoe'])
        # P2 is the enrage beat: faster chase, harder hit, snappier cadence.
        self.assertGreater(p2['chaseSpeed'], p1['chaseSpeed'])
        self.assertGreater(p2['attackDamage'], p1['attackDamage'])
        self.assertGreater(p2['attackHitRange'], p1['attackHitRange'])
        self.assertLess(p2['attackCooldown'], p1['attackCooldown'])
        self.assertLess(p2['telegraphDelay'], p1['telegraphDelay'])
        # Both phases carry slam; surge stays Unleashed-only.
        self.assertIn('slamHitRange', p1)
        self.assertIn('slamDamage', p1)
        self.assertIn('slamHitRange', p2)
        self.assertIn('slamDamage', p2)
        self.assertNotIn('surgeMaxRange', p1)
        self.assertIn('surgeMaxRange', p2)

    def test_finale_phase_look_has_telegraph_punch_timing(self):
        """P1/P2 looks carry AV telegraph + impact punch timing keys."""
        for phase in (1, 2):
            look = self.cg.FINALE_PHASE_LOOK[phase]
            for key in (
                    'telegraphSquashSec', 'telegraphMidSec',
                    'telegraphStretchSec', 'telegraphHoldSec',
                    'telegraphRecoverSec', 'impactSlamSec',
                    'impactReboundSec', 'impactSettleSec',
                    'impactReboundScale'):
                self.assertIn(key, look, msg='P%s missing %s' % (phase, key))
        punch = self.cg.OVERLORD_TELEGRAPH_PUNCH_LOOK
        self.assertEqual(punch.get('id'), 'overlord-telegraph-punch')
        self.assertTrue(self.cg.OVERLORD_TELEGRAPH_PUNCH_ENABLED)
        self.assertTrue(self.cg.OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_ENABLED)
        self.assertGreaterEqual(int(punch.get('creamFleckCount', 0)), 7)
        self.assertGreaterEqual(float(punch.get('warnRimScale', 0)), 1.16)
        self.assertGreaterEqual(
            self.cg.OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_COUNT, 6)
        self.assertTrue(
            self.cg.OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_ENABLED)

    def test_normalize_and_lookup_edges(self):
        self.assertEqual(self.cg.normalizeFinalePhase(1), 1)
        self.assertEqual(self.cg.normalizeFinalePhase(2), 2)
        self.assertEqual(self.cg.normalizeFinalePhase(0), 0)
        self.assertEqual(self.cg.normalizeFinalePhase(99), 0)
        self.assertEqual(self.cg.normalizeFinalePhase('nope'), 0)
        self.assertIsNone(self.cg.overlordPhaseCombat(0))
        self.assertIsNone(self.cg.overlordPhaseCombat(None))

    def test_p2_add_wave_gate(self):
        self.assertEqual(self.cg.overlordP2AddCount(1), 0)
        self.assertEqual(
            self.cg.overlordP2AddCount(2), self.cg.OVERLORD_P2_ADD_COUNT)
        self.assertEqual(self.cg.overlordP2AddCount(3), self.cg.OVERLORD_P2_ADD_COUNT)
        self.assertEqual(
            self.cg.overlordP2AddCount(2, addCount=3, addWaveStart=2), 3)
        self.assertEqual(
            self.cg.overlordP2AddCount(1, addCount=3, addWaveStart=2), 0)
        self.assertEqual(
            self.cg.overlordP2AddCount(5, addCount=0, addWaveStart=2), 0)

    def test_rain_hit_radius_tracks_ink_rain_look(self):
        """Rain AoE should be at least as wide as the visual rain spread."""
        rain = self.cg.OVERLORD_PHASE_INK_RAIN_LOOK
        spread = float(rain.get('spread', 1.55))
        puddle = float(rain.get('puddleHalf', 0.55))
        visual = max(spread, puddle) * 2.0
        for phase in (1, 2):
            combat = self.cg.overlordPhaseCombat(phase)
            self.assertGreaterEqual(
                float(combat['attackHitRange']), visual,
                msg='P%s rain hit range narrower than ink-rain look' % phase)

    def test_campaign_phase2_add_wiring(self):
        """ACTS finale phase2 carries add tunables into director start kwargs."""
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        self.assertIn("'addWaveStart'", camp_src)
        self.assertIn("'addCount'", camp_src)
        self.assertIn("'addHp'", camp_src)
        self.assertIn("'addName'", camp_src)
        director_src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('addCount=params.get', director_src)
        self.assertIn('addWaveStart=params.get', director_src)
        reclaim_src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('_spawnOverlordAdds', reclaim_src)
        self.assertIn('finalePhase=self.finalePhase', reclaim_src)

    def test_ai_module_has_overlord_branch(self):
        tree = _module_ast('toontown/corruption/DistributedCorruptToonAI.py')
        names = _class_and_func_names(tree)
        for expected in (
                'setFinalePhase',
                'promoteFinalePhase',
                '_applyOverlordCombatStats',
                '_isOverlord',
                '__pickOverlordMove',
                '__resolveOverlordRain',
                '__resolveOverlordInkSurge',
                '__surgeOverlordTowardTarget',
                '__resolveSingleTargetHit'):
            self.assertIn(expected, names, msg='missing %s' % expected)
        src = _read('toontown/corruption/DistributedCorruptToonAI.py')
        pick = src[src.find('def __pickOverlordMove'):]
        pick_end = pick.find('\n    def ', 1)
        pick_body = pick if pick_end < 0 else pick[:pick_end]
        self.assertIn('overlordPickEnrageMove', pick_body)
        self.assertIn('overlordPickRisingMove', pick_body)
        resolve = src[src.find('def __resolveAttack'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn("move == 'ink_surge'", resolve_body)
        self.assertIn('__resolveOverlordInkSurge', resolve_body)
        surge = src[src.find('def __resolveOverlordInkSurge'):]
        surge_end = surge.find('\n    def ', 1)
        surge_body = surge if surge_end < 0 else surge[:surge_end]
        self.assertIn('__damageToonAndCheckReclaimKo', surge_body)
        self.assertIn("context='ink_surge'", surge_body)
        self.assertNotIn('target.takeDamage(', surge_body)
        self.assertIn('__surgeOverlordTowardTarget', surge_body)
        # No KH branding in the new surge path.
        blob = (pick_body + resolve_body + surge_body).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, blob)

    def test_silly_street_pack_finale_phase(self):
        """Street reclaim on Silly still arms P1 Overlord AI (AST — no Panda)."""
        src = _read('toontown/reclaim/ReclaimGlobals.py')
        self.assertIn("'finalePhase'", src)
        self.assertIn("'packId': 'silly-overlord'", src)
        # finalePhase key must be forwarded through streetPackParams.
        keys = src.split('_STREET_PACK_START_KEYS')[1][:700]
        self.assertIn("'finalePhase'", keys)
        self.assertIn("'overlordP2HpFrac'", keys)
        # silly-overlord starts Rising; HP-threshold arms Unleash mid-fight.
        silly = src.split("'packId': 'silly-overlord'", 1)[1][:1200]
        self.assertIn("'finalePhase': 1", silly)
        self.assertIn("'corruptName': 'Ink Overlord'", silly)
        self.assertIn("'overlordP2HpFrac'", silly)
        self.assertIn("'addWaveStart': 1", silly)

    def test_p2_rain_and_slam_widen_pressure(self):
        """Unleashed rain is wider/faster than Rising; slam is close-range only."""
        p1 = self.cg.overlordPhaseCombat(1)
        p2 = self.cg.overlordPhaseCombat(2)
        self.assertGreater(p2['attackHitRange'], p1['attackHitRange'])
        self.assertGreater(p2['attackNearMissRange'], p1['attackNearMissRange'])
        self.assertGreater(p2['meleeRange'], p1['meleeRange'])
        # Slam kit is close pressure between rain volleys — shorter than rain.
        self.assertLess(p1['slamHitRange'], p1['attackHitRange'])
        self.assertLess(p1['slamMeleeRange'], p1['meleeRange'])
        self.assertLess(p1['slamTelegraphDelay'], p1['telegraphDelay'])
        self.assertLess(p2['slamHitRange'], p2['attackHitRange'])
        self.assertLess(p2['slamMeleeRange'], p2['meleeRange'])
        self.assertLess(p2['slamTelegraphDelay'], p2['telegraphDelay'])
        self.assertLess(p2['slamCooldown'], p2['attackCooldown'])
        self.assertGreater(p2['slamDamage'], 0)
        # Rising slam is softer / slower than Unleashed slam.
        self.assertLess(p1['slamDamage'], p2['slamDamage'])
        self.assertGreater(p1['slamTelegraphDelay'], p2['slamTelegraphDelay'])
        self.assertLess(p1['slamHitRange'], p2['slamHitRange'])

    def test_p2_ink_surge_third_pressure_note(self):
        """Unleashed mid-range ink_surge sits between slam and rain."""
        self.assertTrue(self.cg.OVERLORD_INK_SURGE_ENABLED)
        p1 = self.cg.overlordPhaseCombat(1)
        p2 = self.cg.overlordPhaseCombat(2)
        self.assertNotIn('surgeMaxRange', p1)
        self.assertIn('surgeMaxRange', p2)
        self.assertIn('surgeDash', p2)
        self.assertIn('surgeHitRange', p2)
        self.assertIn('surgeDamage', p2)
        # Banding: slam < surgeMax < rain engage / hit.
        self.assertLess(p2['slamMeleeRange'], p2['surgeMaxRange'])
        self.assertLess(p2['surgeMaxRange'], p2['meleeRange'])
        self.assertLess(p2['slamHitRange'], p2['surgeHitRange'])
        self.assertLess(p2['surgeHitRange'], p2['attackHitRange'])
        self.assertLess(p2['surgeTelegraphDelay'], p2['telegraphDelay'])
        self.assertGreater(p2['surgeTelegraphDelay'], p2['slamTelegraphDelay'])
        self.assertLess(p2['surgeCooldown'], p2['attackCooldown'])
        self.assertGreater(p2['surgeDash'], self.cg.INK_DASH_DIST)
        # Pure helper picker — three-note Unleashed kit.
        slam_edge = self.cg.overlordSlamMeleeRange(p2)
        surge_edge = self.cg.overlordSurgeMaxRange(p2)
        self.assertEqual(
            self.cg.overlordPickEnrageMove(slam_edge, p2), 'slam')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(slam_edge + 0.1, p2), 'ink_surge')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(surge_edge, p2), 'ink_surge')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(surge_edge + 0.1, p2), 'rain')
        # Surge math — advances but never overshoots past stop.
        nx, ny = self.cg.overlordSurgePos(
            0.0, 0.0, 10.0, 0.0, dash=4.6, stop=1.1)
        self.assertAlmostEqual(ny, 0.0, places=5)
        self.assertAlmostEqual(nx, 4.6, places=5)
        nx2, ny2 = self.cg.overlordSurgePos(
            0.0, 0.0, 0.5, 0.0, dash=4.6, stop=1.1)
        self.assertAlmostEqual(nx2, 0.0, places=5)
        self.assertAlmostEqual(ny2, 0.0, places=5)

    def test_p2_add_constants_are_smudge_pressure(self):
        """P2 adds are Ink Smudge trash mobs — not a fourth archetype."""
        self.assertEqual(self.cg.OVERLORD_P2_ADD_WAVE_START, 2)
        self.assertEqual(self.cg.OVERLORD_P2_ADD_COUNT, 2)
        self.assertEqual(self.cg.OVERLORD_P2_ADD_HP, 25)
        self.assertEqual(self.cg.OVERLORD_P2_ADD_NAME, 'Ink Smudge')
        self.assertGreater(self.cg.OVERLORD_P2_ADD_SPACING, 0)
        self.assertGreater(self.cg.OVERLORD_P2_ADD_FORWARD, 0)

    def test_spawnoverlord_magic_word_defaults_p1(self):
        """~spawnoverlord shortcut arms Rising rain unless finalePhase passed."""
        src = _read('toontown/corruption/MagicWords.py')
        self.assertIn('spawnoverlord', src)
        self.assertIn('finalePhase', src)
        # Default arg for the shortcut is P1 rising rain.
        self.assertIn("('finalePhase', int, False, 1)", src)
        self.assertIn('overlordPhaseCombat(finalePhase)', src)

    def test_reclaim_director_gates_adds_on_p2(self):
        """Adds only fire while Unleashed (finalePhase >= 2) on wave 2+."""
        src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('def _spawnOverlordAdds', src)
        # Hard gate — street Silly / campaign P1 must not drip Smudge adds.
        adds_idx = src.find('def _spawnOverlordAdds')
        self.assertGreater(adds_idx, 0)
        snip = src[adds_idx:adds_idx + 900]
        self.assertIn('finalePhase) < 2', snip)
        self.assertIn('overlordP2AddCount', snip)


if __name__ == '__main__':
    # Keep CorruptionGlobals import path stable when run as a script.
    sys.path.insert(0, str(REPO_ROOT))
    unittest.main()
