#!/usr/bin/env python3
"""Behavioral headless tests for reclaim wave pick / HP / size math.

Imports ReclaimGlobals with a ToontownGlobals stub (no Panda3D). Asserts
wavePackSize, waveCorruptHp, pickPackArchetype slot rules, and STREET_PACKS
mix params used by DistributedReclaimDirectorAI._spawnPack.

Run from repo root:
  python3 tests/test_reclaim_wave_logic.py
  python3 -m unittest tests.test_reclaim_wave_logic -v
"""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

LOOPY = 2200
PUNCHLINE = 2300
SILLY = 2100


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


class ReclaimWaveLogicTest(unittest.TestCase):
    """Table-driven wave size / HP / archetype pick coverage."""

    @classmethod
    def setUpClass(cls):
        cls.rg, cls.cg = _load_panda_free_reclaim()

    def test_wave_pack_size_escalates_then_caps(self):
        rg = self.rg
        # WAVE_SIZE_BONUS=1, WAVE_MAX_EXTRA=3 → +0/+1/+2/+3 then hold.
        cases = (
            (3, 1, 3),
            (3, 2, 4),
            (3, 3, 5),
            (3, 4, 6),
            (3, 5, 6),
            (4, 1, 4),
            (4, 2, 5),
            (1, 4, 4),
        )
        for base, wave, expected in cases:
            self.assertEqual(
                rg.wavePackSize(base, wave), expected,
                msg='wavePackSize(%s, %s)' % (base, wave))

    def test_wave_corrupt_hp_scales_by_wave_index(self):
        rg = self.rg
        # scale = 1 + (wave-1)*0.18; round then clamp ≥1.
        cases = (
            (30, 1, 30),
            (30, 2, 35),   # 30 * 1.18 = 35.4 → 35
            (30, 3, 41),   # 30 * 1.36 = 40.8 → 41
            (30, 4, 46),   # 30 * 1.54 = 46.2 → 46
            (40, 1, 40),
            (40, 2, 47),   # 40 * 1.18 = 47.2 → 47
            (90, 2, 106),  # 90 * 1.18 = 106.2 → 106
            (160, 1, 160),
        )
        for base, wave, expected in cases:
            self.assertEqual(
                rg.waveCorruptHp(base, wave), expected,
                msg='waveCorruptHp(%s, %s)' % (base, wave))

    def test_pack_slot_hp_matches_wave_corrupt_hp(self):
        rg = self.rg
        cg = self.cg
        # Brute tankiness is applied later via hpScale — packSlotHp must not
        # pre-multiply archetype scale.
        for arch in (cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE, cg.ARCHETYPE_SNARE):
            self.assertEqual(
                rg.packSlotHp(arch, 30, 2), rg.waveCorruptHp(30, 2))

    def test_pick_default_wave1_is_pure_smudge(self):
        rg = self.rg
        cg = self.cg
        for pack in (1, 3, 4):
            picks = [
                rg.pickPackArchetype(1, slot, pack) for slot in range(pack)]
            self.assertEqual(
                picks, [cg.ARCHETYPE_INK] * pack,
                msg='default wave-1 pack %s' % pack)

    def test_pick_default_wave2_snare_front_brute_rear(self):
        rg = self.rg
        cg = self.cg
        # pack=3, bruteFrac=0.34 → 1 brute; snareFrac=0.22 → 1 snare.
        picks = [rg.pickPackArchetype(2, slot, 3) for slot in range(3)]
        self.assertEqual(
            picks,
            [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE])

    def test_pick_zero_fractions_stay_smudge(self):
        rg = self.rg
        cg = self.cg
        picks = [
            rg.pickPackArchetype(
                3, slot, 4,
                bruteFraction=0.0, snareFraction=0.0)
            for slot in range(4)]
        self.assertEqual(picks, [cg.ARCHETYPE_INK] * 4)

    def test_pick_punchline_wave1_mix(self):
        rg = self.rg
        cg = self.cg
        pack = rg.STREET_PACKS[PUNCHLINE]
        picks = [
            rg.pickPackArchetype(
                1, slot, pack['packSize'],
                bruteFraction=pack['bruteFraction'],
                bruteWaveStart=pack['bruteWaveStart'],
                snareFraction=pack['snareFraction'],
                snareWaveStart=pack['snareWaveStart'])
            for slot in range(pack['packSize'])]
        # packSize=4, brute 0.4 → 2 rear brutes; snare 0.25 → 1 front snare.
        self.assertEqual(
            picks,
            [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_INK,
             cg.ARCHETYPE_BRUTE, cg.ARCHETYPE_BRUTE])

    def test_pick_loopy_street_pack_wave_rules(self):
        rg = self.rg
        cg = self.cg
        pack = rg.STREET_PACKS[LOOPY]
        # Wave 1 still pure Smudge (brute/snare start at 2).
        w1 = [
            rg.pickPackArchetype(
                1, slot, pack['packSize'],
                bruteFraction=pack['bruteFraction'],
                bruteWaveStart=pack['bruteWaveStart'],
                snareFraction=pack['snareFraction'],
                snareWaveStart=pack['snareWaveStart'])
            for slot in range(pack['packSize'])]
        self.assertEqual(w1, [cg.ARCHETYPE_INK] * pack['packSize'])

        w2 = [
            rg.pickPackArchetype(
                2, slot, pack['packSize'],
                bruteFraction=pack['bruteFraction'],
                bruteWaveStart=pack['bruteWaveStart'],
                snareFraction=pack['snareFraction'],
                snareWaveStart=pack['snareWaveStart'])
            for slot in range(pack['packSize'])]
        self.assertIn(cg.ARCHETYPE_BRUTE, w2)
        self.assertIn(cg.ARCHETYPE_SNARE, w2)
        self.assertIn(cg.ARCHETYPE_INK, w2)

    def test_pick_silly_overlord_pack_no_mix(self):
        rg = self.rg
        cg = self.cg
        pack = rg.STREET_PACKS[SILLY]
        for wave in (1, 2):
            picks = [
                rg.pickPackArchetype(
                    wave, slot, pack['packSize'],
                    bruteFraction=pack['bruteFraction'],
                    snareFraction=pack['snareFraction'])
                for slot in range(pack['packSize'])]
            self.assertEqual(
                picks, [cg.ARCHETYPE_INK] * pack['packSize'],
                msg='silly wave %s' % wave)

    def test_pick_leaves_one_smudge_when_fractions_overflow(self):
        rg = self.rg
        cg = self.cg
        # Both fractions would consume the whole pack — keep ≥1 Smudge.
        picks = [
            rg.pickPackArchetype(
                2, slot, 3,
                bruteFraction=0.9, bruteWaveStart=1,
                snareFraction=0.9, snareWaveStart=1)
            for slot in range(3)]
        self.assertEqual(picks.count(cg.ARCHETYPE_INK), 1)
        self.assertEqual(
            picks.count(cg.ARCHETYPE_BRUTE) + picks.count(cg.ARCHETYPE_SNARE),
            2)

    def test_street_pack_params_keys_for_director_start(self):
        rg = self.rg
        loopy = rg.streetPackParams(LOOPY)
        self.assertEqual(loopy['packSize'], 3)
        self.assertEqual(loopy['corruptHp'], 30)
        self.assertEqual(loopy['bruteWaveStart'], 2)
        self.assertEqual(loopy['snareWaveStart'], 2)

        punch = rg.streetPackParams(PUNCHLINE)
        self.assertEqual(punch['packSize'], 4)
        self.assertEqual(punch['corruptHp'], 40)
        self.assertEqual(punch['bruteWaveStart'], 1)
        self.assertEqual(punch['snareWaveStart'], 1)

        silly = rg.streetPackParams(SILLY)
        self.assertEqual(silly['packSize'], 1)
        self.assertEqual(silly['corruptHp'], 90)
        self.assertEqual(silly['bruteFraction'], 0.0)
        self.assertEqual(silly['snareFraction'], 0.0)


if __name__ == '__main__':
    unittest.main()
