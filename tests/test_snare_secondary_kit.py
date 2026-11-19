#!/usr/bin/env python3
"""Headless/AST tests: Balloon Snare string-lash + cord-coil secondary kit.

Loads CorruptionGlobals without Panda3D. Asserts string_lash / cord_coil
tunables + pure helpers (pick move) and AI / thin client telegraph wiring.
Gameplay identity — not cream FX deepen. Must not regress role AI, Brute
spit, Snare yank, Oswald kit, Ink dash, or reclaim KO helper as the only
hit-path takeDamage entry.

Run from repo root:
  python3 tests/test_snare_secondary_kit.py
  python3 -m unittest tests.test_snare_secondary_kit -v
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


class SnareSecondaryKitTest(unittest.TestCase):
    """String-lash / cord-coil tunables / helpers / AI wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_snare_kit_globals_armed(self):
        self.assertTrue(self.cg.SNARE_STRING_KIT_ENABLED)
        self.assertTrue(self.cg.SNARE_CORD_COIL_SECONDARY_ENABLED)
        self.assertGreater(self.cg.SNARE_CORD_COIL_MELEE_RANGE, 1.5)
        snare = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_SNARE]
        self.assertLess(
            self.cg.SNARE_CORD_COIL_MELEE_RANGE,
            float(snare.get('meleeRange', 3.8)))
        # Coil wrap telegraph is vertical; lash stretch is horizontal.
        coil_sx, coil_sy, coil_sz = self.cg.SNARE_COIL_TELEGRAPH_STRETCH
        lash_sx, lash_sy, lash_sz = self.cg.SNARE_TELEGRAPH_STRETCH
        self.assertGreater(coil_sz, coil_sx)
        self.assertGreater(lash_sx, lash_sz)
        blob = ' '.join([
            'SNARE_STRING_KIT_ENABLED',
            'snarePickAttackMove',
            'string_lash',
            'cord_coil',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)
        self.assertNotIn('sora', blob)

    def test_snare_archetype_lash_coil_stats(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_SNARE]
        self.assertEqual(stats.get('attackMove'), 'string_lash')
        self.assertGreater(float(stats.get('meleeRange', 0)), 3.0)
        self.assertGreater(float(stats.get('attackHitRange', 0)), 6.0)
        self.assertGreater(float(stats.get('coilMeleeRange', 0)), 1.5)
        self.assertGreater(
            int(stats.get('coilDamage', 0)),
            int(stats.get('attackDamage', 0)) - 1)
        self.assertLess(
            float(stats.get('coilHitRange', 0)),
            float(stats.get('attackHitRange', 7.2)))
        self.assertLess(
            float(stats.get('coilTelegraphDelay', 1.0)),
            float(stats.get('telegraphDelay', 0.38)) + 0.01)
        # Flank role — kit is attack identity; role AI flanks.
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_SNARE),
            self.cg.ROLE_FLANK)
        # Distinct from Smudge / Oswald / Brute moves.
        self.assertNotEqual(stats.get('attackMove'), 'ink_dash')
        self.assertNotEqual(stats.get('attackMove'), 'betrayal_lunge')
        self.assertNotEqual(stats.get('attackMove'), 'spit')

    def test_snare_pick_attack_move(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_SNARE]
        # Far → string_lash; close → cord_coil.
        self.assertEqual(
            self.cg.snarePickAttackMove(8.0, stats), 'string_lash')
        self.assertEqual(
            self.cg.snarePickAttackMove(1.0, stats), 'cord_coil')
        edge = self.cg.snareCoilMeleeRange(stats)
        self.assertEqual(
            self.cg.snarePickAttackMove(edge, stats), 'cord_coil')
        self.assertEqual(
            self.cg.snarePickAttackMove(edge + 0.1, stats), 'string_lash')

    def test_snare_pick_respects_disable_flags(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_SNARE]
        prev_kit = self.cg.SNARE_STRING_KIT_ENABLED
        prev_coil = self.cg.SNARE_CORD_COIL_SECONDARY_ENABLED
        try:
            self.cg.SNARE_CORD_COIL_SECONDARY_ENABLED = False
            self.assertEqual(
                self.cg.snarePickAttackMove(1.0, stats), 'string_lash')
            self.cg.SNARE_STRING_KIT_ENABLED = False
            self.assertEqual(
                self.cg.snarePickAttackMove(1.0, stats), 'smack')
        finally:
            self.cg.SNARE_STRING_KIT_ENABLED = prev_kit
            self.cg.SNARE_CORD_COIL_SECONDARY_ENABLED = prev_coil
        self.assertEqual(
            self.cg.snarePickAttackMove(1.0, stats), 'cord_coil')

    def test_prior_gameplay_not_regressed(self):
        self.assertTrue(self.cg.ROLE_AI_ENABLED)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_GAGSTER),
            self.cg.ROLE_KITE)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_BRUTE),
            self.cg.ROLE_HOLD)
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_INK),
            self.cg.ROLE_ORBIT)
        brute = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_BRUTE]
        self.assertEqual(brute.get('attackMove'), 'spit')
        self.assertTrue(self.cg.BRUTE_SPIT_PROJECTILE_ENABLED)
        self.assertTrue(self.cg.BRUTE_SLAM_SECONDARY_ENABLED)
        self.assertTrue(self.cg.SNARE_LASH_YANK_ENABLED)
        self.assertTrue(self.cg.GAGSTER_PUDDLE_LINGER_ENABLED)
        ink = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_INK]
        self.assertEqual(ink.get('attackMove'), 'ink_dash')
        self.assertTrue(self.cg.INK_SMUDGE_KIT_ENABLED)
        oswald = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertEqual(oswald.get('attackMove'), 'betrayal_lunge')
        self.assertTrue(self.cg.OSWALD_BETRAYAL_KIT_ENABLED)
        self.assertTrue(self.cg.OSWALD_BETRAYAL_SHOVE_ENABLED)
        # Snare string notes still interrupt + counter like legacy smack.
        self.assertTrue(
            self.cg.isMeleeInterruptibleTelegraph(
                self.cg.ARCHETYPE_SNARE, 'string_lash'))
        self.assertTrue(
            self.cg.isMeleeInterruptibleTelegraph(
                self.cg.ARCHETYPE_SNARE, 'cord_coil'))
        self.assertTrue(
            self.cg.isDedicatedTelegraphCounterMove(
                self.cg.ARCHETYPE_SNARE, 'string_lash'))
        self.assertTrue(
            self.cg.isDedicatedTelegraphCounterMove(
                self.cg.ARCHETYPE_SNARE, 'cord_coil'))

    def test_ai_snare_kit_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for required in (
                '__resolveSnareStringLash',
                '__resolveSnareCordCoil',
                '__yankTargetTowardSnare',
                '__damageToonAndCheckReclaimKo'):
            self.assertIn(required, methods)
        # Keep prior gameplay intact on the same AI module.
        self.assertIn('__resolveBruteSpit', methods)
        self.assertIn('__resolveInkDash', methods)
        self.assertIn('__resolveOswaldBetrayalLunge', methods)
        self.assertIn('__roleMoveToward', methods)
        self.assertIn('isJuggleHangStunned', methods)
        src = _read(rel)
        self.assertIn('_juggleHangStunUntil', src)
        begin = src[src.find('def __beginAttack'):]
        begin_end = begin.find('\n    def ', 1)
        begin_body = begin if begin_end < 0 else begin[:begin_end]
        self.assertIn('snarePickAttackMove', begin_body)
        self.assertIn('ARCHETYPE_SNARE', begin_body)
        resolve = src[src.find('def __resolveAttack'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn("move == 'string_lash'", resolve_body)
        self.assertIn("move == 'cord_coil'", resolve_body)
        self.assertIn('__resolveSnareStringLash', resolve_body)
        self.assertIn('__resolveSnareCordCoil', resolve_body)
        # Cord coil damage must use KO helper — no raw takeDamage on hit paths.
        coil = src[src.find('def __resolveSnareCordCoil'):]
        coil_end = coil.find('\n    def ', 1)
        coil_body = coil if coil_end < 0 else coil[:coil_end]
        self.assertIn('__damageToonAndCheckReclaimKo', coil_body)
        self.assertIn("context='cord_coil'", coil_body)
        self.assertIn('__yankTargetTowardSnare(target)', coil_body)
        self.assertNotIn('target.takeDamage(', coil_body)
        lash = src[src.find('def __resolveSnareStringLash'):]
        lash_end = lash.find('\n    def ', 1)
        lash_body = lash if lash_end < 0 else lash[:lash_end]
        self.assertIn("__resolveSingleTargetHit('string_lash')", lash_body)
        # Whole-module: takeDamage only inside the KO helper.
        helper_idx = src.find('def __damageToonAndCheckReclaimKo')
        self.assertGreater(helper_idx, 0)
        after_helper = src[helper_idx:]
        next_def = after_helper.find('\n    def ', 1)
        helper_body = after_helper[:next_def]
        rest = after_helper[next_def:]
        self.assertIn('target.takeDamage(', helper_body)
        self.assertNotIn('target.takeDamage(', rest)

    def test_client_telegraph_counter_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        src = _read(rel)
        tele = src[src.find('def announceAttackTelegraph'):]
        tele_end = tele.find('\n    def ', 1)
        tele_body = tele if tele_end < 0 else tele[:tele_end]
        self.assertIn('SNARE_COIL_TELEGRAPH_STRETCH', tele_body)
        self.assertIn("== 'cord_coil'", tele_body)
        self.assertIn("'string_lash'", tele_body)
        self.assertIn('__scheduleSnareStringSnapCounter', tele_body)
        self.assertNotIn('keyblade', tele_body.lower())
        self.assertNotIn('kingdom hearts', tele_body.lower())

    def test_elite_scales_coil_damage(self):
        rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
        src = rg_path.read_text(encoding='utf-8')
        keys = src[src.find('ELITE_DAMAGE_STAT_KEYS'):]
        keys_end = keys.find(')')
        keys_snip = keys[:keys_end]
        self.assertIn("'coilDamage'", keys_snip)
        self.assertIn("'burstDamage'", keys_snip)

    def test_docs_mention_snare_kit(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('string_lash', reclaim)
        self.assertIn('cord_coil', reclaim)
        kit_snip = reclaim.split('balloon snare string-lash', 1)[-1].split(
            '\n## ', 1)[0]
        self.assertIn('string_lash', kit_snip)
        self.assertIn('cord_coil', kit_snip)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, kit_snip)
        init = _read('toontown/corruption/__init__.py').lower()
        self.assertIn('string_lash', init)
        self.assertIn('cord_coil', init)


if __name__ == '__main__':
    unittest.main()
