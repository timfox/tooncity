#!/usr/bin/env python3
"""Behavioral headless tests for reclaim wave pick / HP / size / scripts.

Imports ReclaimGlobals with a ToontownGlobals stub (no Panda3D). Asserts
wavePackSize, waveCorruptHp, pickPackArchetype slot rules, waveScripts
resolution, and STREET_PACKS mix params used by
DistributedReclaimDirectorAI._spawnPack.

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
    """Table-driven wave size / HP / archetype pick / script coverage."""

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
        for arch in (
                cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE, cg.ARCHETYPE_SNARE,
                cg.ARCHETYPE_GAGSTER):
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
                snareWaveStart=pack['snareWaveStart'],
                gagsterFraction=pack['gagsterFraction'],
                gagsterWaveStart=pack['gagsterWaveStart'])
            for slot in range(pack['packSize'])]
        # packSize=4: snare front, gagster mid, brute rear (+1 smudge).
        # brute 0.3 → 1; snare 0.2 → 1; gagster 0.3 → 1.
        self.assertEqual(
            picks,
            [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_GAGSTER,
             cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE])
        self.assertIn(cg.ARCHETYPE_GAGSTER, picks)

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
        self.assertIn('waveScripts', loopy)

        punch = rg.streetPackParams(PUNCHLINE)
        self.assertEqual(punch['packSize'], 4)
        self.assertEqual(punch['corruptHp'], 40)
        self.assertEqual(punch['bruteWaveStart'], 1)
        self.assertEqual(punch['snareWaveStart'], 1)
        self.assertEqual(punch['gagsterWaveStart'], 1)
        self.assertEqual(punch['gagsterFraction'], 0.3)
        self.assertIn('waveScripts', punch)

        silly = rg.streetPackParams(SILLY)
        self.assertEqual(silly['packSize'], 1)
        self.assertEqual(silly['corruptHp'], 90)
        self.assertEqual(silly['bruteFraction'], 0.0)
        self.assertEqual(silly['snareFraction'], 0.0)
        self.assertEqual(silly['gagsterFraction'], 0.0)
        self.assertIn('waveScripts', silly)
        # Discoverable Silly: start Rising, HP-threshold Unleash + adds.
        self.assertEqual(silly['finalePhase'], 1)
        self.assertEqual(silly['overlordP2HpFrac'], rg.OVERLORD_STREET_P2_HP_FRAC)
        self.assertEqual(silly['addWaveStart'], 1)
        self.assertEqual(silly['addCount'], 2)

    def test_normalize_wave_script_tokens(self):
        rg, cg = self.rg, self.cg
        self.assertEqual(rg.normalizeWaveScriptToken('ink'), cg.ARCHETYPE_INK)
        self.assertEqual(rg.normalizeWaveScriptToken('smudge'), cg.ARCHETYPE_INK)
        self.assertEqual(rg.normalizeWaveScriptToken('brute'), cg.ARCHETYPE_BRUTE)
        self.assertEqual(rg.normalizeWaveScriptToken('sludge'), cg.ARCHETYPE_BRUTE)
        self.assertEqual(rg.normalizeWaveScriptToken('snare'), cg.ARCHETYPE_SNARE)
        self.assertEqual(rg.normalizeWaveScriptToken('balloon'), cg.ARCHETYPE_SNARE)
        self.assertEqual(rg.normalizeWaveScriptToken('gagster'), cg.ARCHETYPE_GAGSTER)
        self.assertEqual(rg.normalizeWaveScriptToken('gunk'), cg.ARCHETYPE_GAGSTER)
        self.assertEqual(rg.normalizeWaveScriptToken(1), cg.ARCHETYPE_BRUTE)
        self.assertEqual(rg.normalizeWaveScriptToken('2'), cg.ARCHETYPE_SNARE)
        self.assertEqual(rg.normalizeWaveScriptToken('3'), cg.ARCHETYPE_GAGSTER)
        self.assertEqual(rg.normalizeWaveScriptToken('nope'), cg.ARCHETYPE_INK)

    def test_resolve_wave_script_sequence_and_dict(self):
        rg, cg = self.rg, self.cg
        scripts = (
            ('ink', 'ink'),
            ('snare', 'brute'),
        )
        self.assertEqual(
            rg.resolveWaveScript(scripts, 1),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveWaveScript(scripts, 2),
            [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_BRUTE])
        self.assertIsNone(rg.resolveWaveScript(scripts, 3))
        self.assertIsNone(rg.resolveWaveScript(None, 1))

        keyed = {1: ('brute',), '2': ('snare', 'ink')}
        self.assertEqual(
            rg.resolveWaveScript(keyed, 1), [cg.ARCHETYPE_BRUTE])
        self.assertEqual(
            rg.resolveWaveScript(keyed, 2),
            [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_INK])

    def test_wave_pack_size_honors_script(self):
        rg = self.rg
        script = rg.resolveWaveScript((('ink', 'brute', 'snare'),), 1)
        self.assertEqual(rg.wavePackSize(3, 1, waveScript=script), 3)
        # Without script, legacy bonus still grows pack size.
        self.assertEqual(rg.wavePackSize(3, 1), 3)
        self.assertEqual(rg.wavePackSize(3, 2), 4)

    def test_pick_pack_archetype_prefers_script(self):
        rg, cg = self.rg, self.cg
        script = [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE]
        self.assertEqual(
            rg.pickPackArchetype(1, 0, 3, waveScript=script),
            cg.ARCHETYPE_SNARE)
        self.assertEqual(
            rg.pickPackArchetype(1, 1, 3, waveScript=script),
            cg.ARCHETYPE_INK)
        self.assertEqual(
            rg.pickPackArchetype(1, 2, 3, waveScript=script),
            cg.ARCHETYPE_BRUTE)
        # No script → Loopy-style wave-1 pure Smudge.
        self.assertEqual(
            rg.pickPackArchetype(1, 0, 3, bruteFraction=0.34, bruteWaveStart=2),
            cg.ARCHETYPE_INK)

    def test_street_pack_scripts_feel_distinct(self):
        rg, cg = self.rg, self.cg
        loopy = rg.STREET_PACKS[LOOPY]['waveScripts']
        punch = rg.STREET_PACKS[PUNCHLINE]['waveScripts']
        silly = rg.STREET_PACKS[SILLY]['waveScripts']

        loopy_w1 = rg.resolveWaveScript(loopy, 1)
        punch_w1 = rg.resolveWaveScript(punch, 1)
        silly_w1 = rg.resolveWaveScript(silly, 1)

        self.assertEqual(loopy_w1, [cg.ARCHETYPE_INK] * 3)
        self.assertEqual(punch_w1[0], cg.ARCHETYPE_SNARE)
        self.assertEqual(punch_w1[1], cg.ARCHETYPE_GAGSTER)
        self.assertEqual(punch_w1[-1], cg.ARCHETYPE_BRUTE)
        self.assertIn(cg.ARCHETYPE_GAGSTER, punch_w1)
        self.assertEqual(silly_w1, [cg.ARCHETYPE_INK])

        # Loopy introduces Brute on wave 2; Punchline already mixed on wave 1.
        loopy_w2 = rg.resolveWaveScript(loopy, 2)
        self.assertIn(cg.ARCHETYPE_BRUTE, loopy_w2)
        self.assertNotEqual(loopy_w1, punch_w1)
        # Gunk Gagster stays Punchline-forward (not Loopy tutorial).
        self.assertNotIn(cg.ARCHETYPE_GAGSTER, loopy_w1)
        self.assertNotIn(cg.ARCHETYPE_GAGSTER, loopy_w2)

        silly_w2 = rg.resolveWaveScript(silly, 2)
        self.assertEqual(silly_w2, [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertTrue(all(a == cg.ARCHETYPE_INK for a in silly_w2))

    def test_street_pack_scripts_lock_full_compositions(self):
        """Lock every STREET_PACKS wave beat (#185/#191) — not just openers."""
        rg, cg = self.rg, self.cg
        ink, brute, snare, gagster = (
            cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE, cg.ARCHETYPE_SNARE,
            cg.ARCHETYPE_GAGSTER)

        expected = {
            LOOPY: {
                1: [ink, ink, ink],
                2: [ink, ink, brute],
                3: [snare, ink, brute, ink],
                4: [snare, ink, brute, snare, ink],
            },
            # Punchline (#191): Gunk Gagster mid slots from wave 1.
            PUNCHLINE: {
                1: [snare, gagster, ink, brute],
                2: [snare, gagster, gagster, brute, ink],
                3: [snare, gagster, brute, brute, ink],
                4: [snare, gagster, gagster, brute, snare, ink],
            },
            SILLY: {
                1: [ink],
                2: [ink, ink],
            },
        }
        for zone, waves in expected.items():
            scripts = rg.STREET_PACKS[zone]['waveScripts']
            for wave, composition in waves.items():
                self.assertEqual(
                    rg.resolveWaveScript(scripts, wave), composition,
                    msg='zone %s wave %s script' % (zone, wave))
            # Past the last scripted beat → fraction fallback path.
            past = max(waves) + 1
            self.assertIsNone(
                rg.resolveWaveScript(scripts, past),
                msg='zone %s wave %s should fall through' % (zone, past))

    def test_scripted_pack_size_matches_composition(self):
        """wavePackSize must honor script length so spawned slots = script."""
        rg = self.rg
        for zone in (LOOPY, PUNCHLINE, SILLY):
            pack = rg.STREET_PACKS[zone]
            scripts = pack['waveScripts']
            for wave in range(1, len(scripts) + 1):
                script = rg.resolveWaveScript(scripts, wave)
                self.assertIsNotNone(script)
                self.assertEqual(
                    rg.wavePackSize(pack['packSize'], wave, waveScript=script),
                    len(script),
                    msg='zone %s wave %s pack size' % (zone, wave))

    def test_director_prefers_wave_scripts_ast(self):
        """DistributedReclaimDirectorAI must resolve + spawn from waveScripts."""
        src = (REPO_ROOT / 'toontown' / 'reclaim' /
               'DistributedReclaimDirectorAI.py').read_text(encoding='utf-8')
        self.assertIn('waveScripts=', src)
        self.assertIn('resolveWaveScript', src)
        self.assertIn('waveScript=waveScript', src)
        # Start kwargs keep scripts for the whole reclaim session.
        self.assertIn('self._waveScripts = waveScripts', src)

    def test_street_pack_elite_modifiers_and_ambush_beats(self):
        """Street packs carry real elite + earlier-wave / Silly ambush tables."""
        rg, cg = self.rg, self.cg
        for zone in (LOOPY, PUNCHLINE):
            pack = rg.STREET_PACKS[zone]
            self.assertIn('waveModifiers', pack)
            self.assertIn('ambushBeats', pack)
            mods = rg.resolveWaveModifiers(pack['waveModifiers'], 4)
            self.assertTrue(rg.waveIsElite(mods))
            # Earlier waves + post-3 all resolve real ambush compositions.
            for cleared in (1, 2, 3):
                ambush = rg.resolveAmbushBeat(pack['ambushBeats'], cleared)
                self.assertTrue(
                    ambush,
                    msg='%s missing ambush after wave %s' % (zone, cleared))
                self.assertTrue(all(
                    a in (
                        cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE,
                        cg.ARCHETYPE_SNARE, cg.ARCHETYPE_GAGSTER)
                    for a in ambush))
        silly = rg.STREET_PACKS[SILLY]
        self.assertIn('waveModifiers', silly)
        self.assertIn('ambushBeats', silly)
        self.assertTrue(
            rg.waveIsElite(rg.resolveWaveModifiers(silly['waveModifiers'], 2)))
        silly_ambush = rg.resolveAmbushBeat(silly['ambushBeats'], 1)
        self.assertEqual(
            silly_ambush, [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        params = rg.streetPackParams(LOOPY)
        self.assertEqual(
            params['waveModifiers'],
            rg.STREET_PACKS[LOOPY]['waveModifiers'])
        self.assertEqual(
            params['ambushBeats'],
            rg.STREET_PACKS[LOOPY]['ambushBeats'])
        silly_params = rg.streetPackParams(SILLY)
        self.assertEqual(
            silly_params['waveModifiers'],
            rg.STREET_PACKS[SILLY]['waveModifiers'])
        self.assertEqual(
            silly_params['ambushBeats'],
            rg.STREET_PACKS[SILLY]['ambushBeats'])


if __name__ == '__main__':
    unittest.main()
