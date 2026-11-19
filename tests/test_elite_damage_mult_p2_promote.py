#!/usr/bin/env python3
"""Headless tests: elite damage mult survives Overlord P2 promote.

Silly wave-2 elite twins spawn Rising with elite land-hit buff. HP-threshold
promote rebuilds ``_stats`` from archetype + phase combat — without a
re-apply, Unleash silently drops the elite damage mult. This suite locks
CorruptToonAI stash/re-apply + thin director stash wiring (no Panda3D, no
cream, no KH).

Run from repo root:
  python3 tests/test_elite_damage_mult_p2_promote.py
  python3 -m unittest tests.test_elite_damage_mult_p2_promote -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

LOOPY = 2200
PUNCHLINE = 2300
SILLY = 2100


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


def _method_body(src: str, def_name: str) -> str:
    marker = 'def %s' % def_name
    start = src.find(marker)
    if start < 0:
        return ''
    snip = src[start:]
    end = snip.find('\n    def ', 1)
    return snip if end < 0 else snip[:end]


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_reclaim():
    """Stub ToontownGlobals, then load CorruptionGlobals + ReclaimGlobals."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
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

    rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
    rg_spec = importlib.util.spec_from_file_location(
        'toontown.reclaim.ReclaimGlobals', rg_path)
    rg = importlib.util.module_from_spec(rg_spec)
    assert rg_spec.loader is not None
    sys.modules['toontown.reclaim.ReclaimGlobals'] = rg
    rg_spec.loader.exec_module(rg)
    sys.modules['toontown.reclaim'].ReclaimGlobals = rg
    return rg, cg


class EliteDamageMultP2PromoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.cg = _load_panda_free_reclaim()

    def test_silly_wave2_is_elite_overlord_rising(self):
        """Twin swell spawns elite while still Rising — the wipe target."""
        rg = self.rg
        silly = rg.STREET_PACKS[SILLY]
        self.assertEqual(silly['finalePhase'], 1)
        mods = rg.resolveWaveModifiers(silly['waveModifiers'], 2)
        self.assertTrue(rg.waveIsElite(mods))
        self.assertEqual(rg.waveDamageMult(mods), rg.ELITE_DAMAGE_MULT)
        # Wave 1 solo Overlord is not elite — buff only on twin swell.
        self.assertIsNone(rg.resolveWaveModifiers(silly['waveModifiers'], 1))

    def test_promote_rebuild_then_reapply_keeps_elite_land_hits(self):
        """Simulate spawn buff → P2 rebuild → re-apply (the bug path)."""
        rg, cg = self.rg, self.cg
        mods = {'elite': True}
        mult = rg.ELITE_DAMAGE_MULT

        # Spawn Rising: phase combat + elite damage (director at spawn).
        p1 = dict(cg.archetypeStats(cg.ARCHETYPE_INK))
        combat1 = cg.overlordPhaseCombat(1)
        self.assertTrue(combat1)
        for key in ('attackDamage', 'slamDamage', 'surgeDamage'):
            if key in combat1:
                p1[key] = combat1[key]
        elite_p1 = rg.applyWaveDamageMultToStats(p1, mods)
        self.assertEqual(
            elite_p1['attackDamage'],
            max(1, int(round(float(p1['attackDamage']) * mult))))

        # Promote Unleash: rebuild from base + P2 only (wipes elite).
        # Note: P1 elite attackDamage (4*1.4→6) equals raw P2 attackDamage —
        # prove the wipe via slamDamage (P1 elite 3*1.4→4 vs raw P2 slam 5).
        rebuilt = dict(cg.archetypeStats(cg.ARCHETYPE_INK))
        combat2 = cg.overlordPhaseCombat(2)
        self.assertEqual(combat2['moveMode'], 'enrage')
        for key in ('attackDamage', 'slamDamage', 'surgeDamage'):
            if key in combat2:
                rebuilt[key] = combat2[key]
        self.assertEqual(rebuilt['attackDamage'], combat2['attackDamage'])
        self.assertEqual(rebuilt['slamDamage'], combat2['slamDamage'])
        self.assertNotEqual(
            rebuilt['slamDamage'], elite_p1['slamDamage'],
            msg='P2 rebuild must drop spawn elite slam buff (the bug)')
        self.assertLess(
            rebuilt['slamDamage'],
            max(1, int(round(float(combat2['slamDamage']) * mult))),
            msg='raw P2 slam must be below elite-scaled P2 slam')

        # Re-apply remembered mods — Unleash keeps elite land-hit buff.
        elite_p2 = rg.applyWaveDamageMultToStats(rebuilt, mods)
        self.assertEqual(
            elite_p2['attackDamage'],
            max(1, int(round(float(combat2['attackDamage']) * mult))))
        self.assertEqual(
            elite_p2['slamDamage'],
            max(1, int(round(float(combat2['slamDamage']) * mult))))
        self.assertEqual(
            elite_p2['surgeDamage'],
            max(1, int(round(float(combat2['surgeDamage']) * mult))))
        self.assertGreater(elite_p2['slamDamage'], rebuilt['slamDamage'])

    def test_corrupt_ai_stash_and_reapply_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for expected in (
                'setEliteDamageMods',
                'getEliteDamageMods',
                '_reapplyEliteDamageMods',
                '_applyOverlordCombatStats',
                'promoteFinalePhase'):
            self.assertIn(expected, methods, msg='missing %s' % expected)

        src = _read(rel)
        self.assertIn('_eliteDamageMods', src)

        apply_body = _method_body(src, '_applyOverlordCombatStats')
        self.assertIn('_reapplyEliteDamageMods', apply_body)
        # Both street (no combat) and Overlord merge paths re-apply.
        self.assertGreaterEqual(apply_body.count('_reapplyEliteDamageMods()'), 2)

        reapply_body = _method_body(src, '_reapplyEliteDamageMods')
        self.assertIn('applyWaveDamageMultToStats', reapply_body)
        self.assertIn('waveIsElite', reapply_body)

        promote_body = _method_body(src, 'promoteFinalePhase')
        self.assertIn('setFinalePhase', promote_body)
        # Promote relies on setFinalePhase → _applyOverlordCombatStats re-apply.
        self.assertIn('elite', promote_body.lower())

        # No KH / cream branding on the new helpers.
        blob = (
            _method_body(src, 'setEliteDamageMods')
            + reapply_body
            + promote_body).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless', 'cream'):
            self.assertNotIn(banned, blob)

    def test_director_stashes_mods_on_elite_apply(self):
        rel = 'toontown/reclaim/DistributedReclaimDirectorAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedReclaimDirectorAI')
        self.assertIn('_applyEliteModifiers', methods)
        self.assertIn('_promoteStreetOverlordP2', methods)

        apply_body = _method_body(_read(rel), '_applyEliteModifiers')
        self.assertIn('setEliteDamageMods', apply_body)
        self.assertIn('_eliteDamageMods', apply_body)
        self.assertIn('applyWaveDamageMultToStats', apply_body)

        promote_body = _method_body(_read(rel), '_promoteStreetOverlordP2')
        self.assertIn('promoteFinalePhase', promote_body)
        # Re-apply lives on corrupt AI after promote rebuild — director only
        # stashes at spawn (thin hook).
        self.assertNotIn('_reapplyEliteDamageMods', promote_body)

        blob = (apply_body + promote_body).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, blob)


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    unittest.main()
