#!/usr/bin/env python3
"""Headless / AST tests for Silly street Overlord HP-threshold P1→P2.

Discoverable Silly reclaim starts Rising (finalePhase 1) and promotes to
Unleashed (slam + Smudge adds) when Overlord HP drops to overlordP2HpFrac —
no campaign restart. Oswald twist stays campaign-start-Unleashed only.

Run from repo root:
  python3 tests/test_silly_street_overlord_hp_p2.py
  python3 -m unittest tests.test_silly_street_overlord_hp_p2 -v
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


def _class_and_func_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


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


class SillyStreetOverlordHpP2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.cg = _load_panda_free_reclaim()

    def test_overlord_hp_threshold_helper(self):
        rg = self.rg
        self.assertTrue(rg.overlordHpAtP2Threshold(45, 90, 0.5))
        self.assertTrue(rg.overlordHpAtP2Threshold(44, 90, 0.5))
        self.assertFalse(rg.overlordHpAtP2Threshold(46, 90, 0.5))
        self.assertFalse(rg.overlordHpAtP2Threshold(90, 90, 0.5))
        self.assertFalse(rg.overlordHpAtP2Threshold(0, 90, None))
        self.assertFalse(rg.overlordHpAtP2Threshold(10, 90, 0))
        self.assertFalse(rg.overlordHpAtP2Threshold(10, 0, 0.5))
        self.assertFalse(rg.overlordHpAtP2Threshold('x', 90, 0.5))
        self.assertEqual(rg.OVERLORD_STREET_P2_HP_FRAC, 0.5)

    def test_silly_street_pack_arms_hp_threshold_p2(self):
        rg = self.rg
        silly = rg.STREET_PACKS[SILLY]
        self.assertEqual(silly['finalePhase'], 1)
        self.assertEqual(
            silly['overlordP2HpFrac'], rg.OVERLORD_STREET_P2_HP_FRAC)
        self.assertTrue(silly['transitionSting'])
        self.assertEqual(silly['addWaveStart'], 1)
        self.assertEqual(silly['addCount'], 2)
        self.assertEqual(silly['addHp'], 25)
        self.assertEqual(silly['addName'], 'Ink Smudge')

        params = rg.streetPackParams(SILLY)
        for key in (
                'finalePhase', 'overlordP2HpFrac', 'transitionSting',
                'addCount', 'addWaveStart', 'addHp', 'addName'):
            self.assertIn(key, params, msg='streetPackParams missing %s' % key)
        self.assertEqual(params['finalePhase'], 1)
        self.assertEqual(params['overlordP2HpFrac'], 0.5)
        self.assertEqual(params['addWaveStart'], 1)

        # Loopy / Punchline stay free of Overlord HP-threshold wiring.
        self.assertNotIn('overlordP2HpFrac', rg.streetPackParams(LOOPY))
        self.assertNotIn('overlordP2HpFrac', rg.streetPackParams(PUNCHLINE))

    def test_director_ai_has_hp_threshold_promote(self):
        tree = _module_ast(
            'toontown/reclaim/DistributedReclaimDirectorAI.py')
        names = _class_and_func_names(tree)
        for expected in (
                '_maybePromoteStreetOverlordP2',
                '_promoteStreetOverlordP2',
                '_spawnOverlordAdds'):
            self.assertIn(expected, names, msg='missing %s' % expected)

        src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('overlordP2HpFrac', src)
        self.assertIn('_maybePromoteStreetOverlordP2()', src)
        self.assertIn('overlordHpAtP2Threshold', src)
        self.assertIn('announceFinalePhaseTransition', src)
        self.assertIn('promoteFinalePhase', src)

    def test_corrupt_ai_promote_finale_phase_hook(self):
        tree = _module_ast(
            'toontown/corruption/DistributedCorruptToonAI.py')
        names = _class_and_func_names(tree)
        self.assertIn('promoteFinalePhase', names)
        self.assertIn('__interruptAttackForPhasePromote', names)

        src = _read('toontown/corruption/DistributedCorruptToonAI.py')
        # Promote must re-apply Overlord combat stats via setFinalePhase.
        promote_idx = src.find('def promoteFinalePhase')
        self.assertGreater(promote_idx, 0)
        snip = src[promote_idx:promote_idx + 700]
        self.assertIn('setFinalePhase', snip)
        self.assertIn('__interruptAttackForPhasePromote', snip)

    def test_client_twist_gated_on_start_phase(self):
        """Street HP-threshold P2 must not fire Oswald twist on clear."""
        src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('_startFinalePhase', src)
        complete_idx = src.find('def announceReclaimComplete')
        self.assertGreater(complete_idx, 0)
        snip = src[complete_idx:complete_idx + 2200]
        self.assertIn('bannerPhase', snip)
        self.assertIn('startedUnleashed', snip)
        self.assertIn("messenger.send('oswaldRevealSting'", snip)
        # Twist requires reclaim started already Unleashed (campaign P2).
        self.assertIn('bannerPhase >= 2', snip)

    def test_p2_combat_still_has_slam_after_promote(self):
        """Sanity: Unleashed kit is what street promote arms."""
        p2 = self.cg.overlordPhaseCombat(2)
        self.assertEqual(p2['moveMode'], 'enrage')
        self.assertIn('slamDamage', p2)
        self.assertIn('slamHitRange', p2)
        # Third Unleashed note (ink_surge) stays armed after HP-threshold promote.
        self.assertIn('surgeMaxRange', p2)
        self.assertIn('surgeDamage', p2)
        self.assertTrue(self.cg.OVERLORD_INK_SURGE_ENABLED)

    def test_no_kh_branding_in_street_p2_copy(self):
        silly = _read('toontown/reclaim/ReclaimGlobals.py')
        block = silly.split("'packId': 'silly-overlord'", 1)[1][:1200].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, block)


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    unittest.main()
