#!/usr/bin/env python3
"""Headless/AST tests: Ink Smudge ink-dash + splat secondary (not smack fodder).

Loads CorruptionGlobals without Panda3D. Asserts ink_dash / ink_splat
tunables + pure helpers (pick move, dash math) and AI wiring on
DistributedCorruptToonAI. Gameplay identity — not cream FX deepen. Must not
regress role AI, Brute spit, Snare yank, Oswald kit, juggle hang stun, or
reclaim KO helper as the only hit-path takeDamage entry.

Run from repo root:
  python3 tests/test_ink_smudge_ink_dash.py
  python3 -m unittest tests.test_ink_smudge_ink_dash -v
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


class InkSmudgeInkDashTest(unittest.TestCase):
    """Ink-dash / splat tunables / helpers / AI wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_ink_kit_globals_armed(self):
        self.assertTrue(self.cg.INK_SMUDGE_KIT_ENABLED)
        self.assertTrue(self.cg.INK_DASH_ENABLED)
        self.assertTrue(self.cg.INK_SPLAT_SECONDARY_ENABLED)
        self.assertGreater(self.cg.INK_DASH_DIST, 1.5)
        self.assertGreater(self.cg.INK_SPLAT_MELEE_RANGE, 2.0)
        self.assertGreater(self.cg.INK_DASH_STOP, 0.0)
        # Shorter rush than Oswald betrayal lunge — swarm fodder, not chase boss.
        self.assertLess(self.cg.INK_DASH_DIST, self.cg.OSWALD_BETRAYAL_LUNGE_DASH)
        ink = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_INK]
        self.assertLess(
            self.cg.INK_SPLAT_MELEE_RANGE,
            float(ink.get('meleeRange', 5.8)))
        blob = ' '.join([
            'INK_SMUDGE_KIT_ENABLED',
            'inkPickAttackMove',
            'inkDashPos',
            'ink_dash',
            'ink_splat',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)
        self.assertNotIn('sora', blob)

    def test_ink_archetype_dash_splat_stats(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_INK]
        self.assertEqual(stats.get('attackMove'), 'ink_dash')
        self.assertGreater(float(stats.get('meleeRange', 0)), 5.0)
        self.assertGreater(float(stats.get('dashDist', 0)), 1.5)
        self.assertGreater(float(stats.get('splatMeleeRange', 0)), 2.0)
        self.assertGreater(
            int(stats.get('splatDamage', 0)),
            int(stats.get('dashDamage', 0)) - 1)
        # Orbit / weave role — kit is attack identity; role AI circles.
        self.assertEqual(
            self.cg.archetypeCombatRole(self.cg.ARCHETYPE_INK),
            self.cg.ROLE_ORBIT)
        # Distinct from Oswald betrayal moves.
        self.assertNotEqual(stats.get('attackMove'), 'betrayal_lunge')
        self.assertNotEqual(stats.get('attackMove'), 'stain_burst')

    def test_ink_pick_attack_move(self):
        stats = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_INK]
        # Far → ink_dash; close → ink_splat.
        self.assertEqual(
            self.cg.inkPickAttackMove(8.0, stats), 'ink_dash')
        self.assertEqual(
            self.cg.inkPickAttackMove(2.0, stats), 'ink_splat')
        edge = self.cg.inkSplatMeleeRange(stats)
        self.assertEqual(
            self.cg.inkPickAttackMove(edge, stats), 'ink_splat')
        self.assertEqual(
            self.cg.inkPickAttackMove(edge + 0.1, stats), 'ink_dash')

    def test_ink_dash_math(self):
        nx, ny = self.cg.inkDashPos(
            0.0, 0.0, 10.0, 0.0, dash=3.2, stop=0.75)
        self.assertAlmostEqual(ny, 0.0, places=5)
        self.assertAlmostEqual(nx, 3.2, places=5)
        # Already inside stop → no move.
        nx2, ny2 = self.cg.inkDashPos(
            0.0, 0.0, 0.5, 0.0, dash=3.2, stop=0.75)
        self.assertAlmostEqual(nx2, 0.0, places=5)
        self.assertAlmostEqual(ny2, 0.0, places=5)
        # Short gap clamps dash to gap - stop.
        nx3, ny3 = self.cg.inkDashPos(
            0.0, 0.0, 2.5, 0.0, dash=3.2, stop=0.75)
        self.assertAlmostEqual(nx3, 2.5 - 0.75, places=5)

    def test_prior_gameplay_not_regressed(self):
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
        self.assertTrue(self.cg.GAGSTER_PUDDLE_LINGER_ENABLED)
        oswald = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertEqual(oswald.get('attackMove'), 'betrayal_lunge')
        self.assertTrue(self.cg.OSWALD_BETRAYAL_KIT_ENABLED)
        self.assertTrue(self.cg.OSWALD_BETRAYAL_SHOVE_ENABLED)

    def test_ai_ink_kit_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for required in (
                '__resolveInkDash',
                '__resolveInkSplat',
                '__dashInkTowardTarget',
                '__damageToonAndCheckReclaimKo'):
            self.assertIn(required, methods)
        # Keep prior gameplay intact on the same AI module.
        self.assertIn('__resolveBruteSpit', methods)
        self.assertIn('__yankTargetTowardSnare', methods)
        self.assertIn('__resolveOswaldBetrayalLunge', methods)
        self.assertIn('__roleMoveToward', methods)
        self.assertIn('isJuggleHangStunned', methods)
        src = _read(rel)
        self.assertIn('_juggleHangStunUntil', src)
        begin = src[src.find('def __beginAttack'):]
        begin_end = begin.find('\n    def ', 1)
        begin_body = begin if begin_end < 0 else begin[:begin_end]
        self.assertIn('inkPickAttackMove', begin_body)
        self.assertIn('ARCHETYPE_INK', begin_body)
        resolve = src[src.find('def __resolveAttack'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn("move == 'ink_dash'", resolve_body)
        self.assertIn("move == 'ink_splat'", resolve_body)
        self.assertIn('__resolveInkDash', resolve_body)
        self.assertIn('__resolveInkSplat', resolve_body)
        # Ink splat damage must use KO helper — no raw takeDamage on hit paths.
        splat = src[src.find('def __resolveInkSplat'):]
        splat_end = splat.find('\n    def ', 1)
        splat_body = splat if splat_end < 0 else splat[:splat_end]
        self.assertIn('__damageToonAndCheckReclaimKo', splat_body)
        self.assertIn("context='ink_splat'", splat_body)
        self.assertNotIn('target.takeDamage(', splat_body)
        dash = src[src.find('def __resolveInkDash'):]
        dash_end = dash.find('\n    def ', 1)
        dash_body = dash if dash_end < 0 else dash[:dash_end]
        self.assertIn('__dashInkTowardTarget', dash_body)
        self.assertIn("__resolveSingleTargetHit('ink_dash')", dash_body)
        # Whole-module: takeDamage only inside the KO helper.
        helper_idx = src.find('def __damageToonAndCheckReclaimKo')
        self.assertGreater(helper_idx, 0)
        after_helper = src[helper_idx:]
        next_def = after_helper.find('\n    def ', 1)
        helper_body = after_helper[:next_def]
        rest = after_helper[next_def:]
        self.assertIn('target.takeDamage(', helper_body)
        self.assertNotIn('target.takeDamage(', rest)

    def test_docs_mention_ink_dash(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('ink_dash', reclaim)
        self.assertIn('ink_splat', reclaim)
        # New kit copy only — doc may say "no keyblades" elsewhere.
        kit_snip = reclaim.split('ink smudge ai uses', 1)[-1].split('\n## ', 1)[0]
        self.assertIn('ink_dash', kit_snip)
        self.assertIn('ink_splat', kit_snip)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, kit_snip)
        init = _read('toontown/corruption/__init__.py').lower()
        self.assertIn('ink_dash', init)
        self.assertIn('ink_splat', init)


if __name__ == '__main__':
    unittest.main()
