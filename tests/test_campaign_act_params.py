#!/usr/bin/env python3
"""Behavioral headless tests for campaign ACTS P1/P2 param merge.

Loads CampaignGlobals (+ ReclaimGlobals STREET_PACKS) with a ToontownGlobals
stub — no Panda3D. Mirrors CampaignDirectorAI._actParams merge rules and
checks ACTS ↔ STREET_PACKS consistency for the three-hood loop.

Run from repo root:
  python3 tests/test_campaign_act_params.py
  python3 -m unittest tests.test_campaign_act_params -v
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

# Keys CampaignDirectorAI._actParams pulls from an act (+ phase2 override).
_ACT_PARAM_KEYS = (
    'seedPollution', 'packSize', 'maxPacks', 'corruptHp', 'corruptName',
    'bruteFraction', 'bruteWaveStart', 'bruteName',
    'snareFraction', 'snareWaveStart', 'snareName',
    'gagsterFraction', 'gagsterWaveStart', 'gagsterName',
    'waveScripts',
    'waveModifiers',
    'ambushBeats',
    'banner',
)


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_campaign_and_reclaim():
    """Stub ToontownGlobals; load CampaignGlobals + ReclaimGlobals."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim', 'toontown.campaign'):
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

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    return camp, rg, cg


def resolve_act_params(act, finale_phase=0):
    """Pure mirror of CampaignDirectorAI._actParams (panda-free).

    finale_phase mirrors director._finalePhase: 0 = first Silly reclaim (P1),
    ≥1 = after first Silly clear → apply phase2 overrides (P2).
    """
    params = {
        'seedPollution': act.get('seedPollution'),
        'packSize': act.get('packSize'),
        'maxPacks': act.get('maxPacks'),
        'corruptHp': act.get('corruptHp'),
        'corruptName': act.get('corruptName'),
        'bruteFraction': act.get('bruteFraction'),
        'bruteWaveStart': act.get('bruteWaveStart'),
        'bruteName': act.get('bruteName'),
        'snareFraction': act.get('snareFraction'),
        'snareWaveStart': act.get('snareWaveStart'),
        'snareName': act.get('snareName'),
        'gagsterFraction': act.get('gagsterFraction'),
        'gagsterWaveStart': act.get('gagsterWaveStart'),
        'gagsterName': act.get('gagsterName'),
        'waveScripts': act.get('waveScripts'),
        'waveModifiers': act.get('waveModifiers'),
        'ambushBeats': act.get('ambushBeats'),
        'banner': act.get('banner'),
        'finalePhase': 0,
        'transitionSting': False,
    }
    if act.get('finale'):
        if int(finale_phase or 0) >= 1:
            phase2 = act.get('phase2') or {}
            params.update(phase2)
            params['finalePhase'] = int(phase2.get('finalePhase', 2))
            params['transitionSting'] = bool(
                phase2.get('transitionSting', True))
        else:
            params['finalePhase'] = int(act.get('finalePhase', 1))
    return params


class CampaignActParamsTest(unittest.TestCase):
    """ACTS table + finale P1/P2 merge + STREET_PACKS alignment."""

    @classmethod
    def setUpClass(cls):
        cls.camp, cls.rg, cls.cg = _load_panda_free_campaign_and_reclaim()
        cls.acts_by_id = {a['id']: a for a in cls.camp.ACTS}

    def test_acts_cover_three_hoods(self):
        acts = self.camp.ACTS
        self.assertEqual(len(acts), 3)
        self.assertEqual(
            tuple(a['id'] for a in acts), ('loopy', 'punchline', 'finale'))
        self.assertEqual(self.acts_by_id['loopy']['zoneId'], LOOPY)
        self.assertEqual(self.acts_by_id['punchline']['zoneId'], PUNCHLINE)
        self.assertEqual(self.acts_by_id['finale']['zoneId'], SILLY)

    def test_loopy_act_params_pure_smudge_tutorial(self):
        params = resolve_act_params(self.acts_by_id['loopy'])
        self.assertEqual(params['packSize'], 3)
        self.assertEqual(params['maxPacks'], 4)
        self.assertEqual(params['corruptHp'], 30)
        self.assertEqual(params['corruptName'], 'Ink Smudge')
        # Fraction fallback stays Smudge-only; waveScripts own the ramp.
        self.assertEqual(params['bruteFraction'], 0.0)
        self.assertEqual(params['snareFraction'], 0.0)
        self.assertTrue(params.get('waveScripts'))
        self.assertEqual(len(params['waveScripts']), 4)
        self.assertEqual(params['finalePhase'], 0)
        self.assertFalse(params['transitionSting'])

    def test_punchline_act_params_gagster_brute_snare_from_wave1(self):
        params = resolve_act_params(self.acts_by_id['punchline'])
        self.assertEqual(params['packSize'], 4)
        self.assertEqual(params['corruptHp'], 40)
        self.assertEqual(params['corruptName'], 'Ink Smudge')
        self.assertEqual(params['bruteFraction'], 0.3)
        self.assertEqual(params['bruteWaveStart'], 1)
        self.assertEqual(params['snareFraction'], 0.2)
        self.assertEqual(params['snareWaveStart'], 1)
        self.assertEqual(params['gagsterFraction'], 0.3)
        self.assertEqual(params['gagsterWaveStart'], 1)
        self.assertEqual(params['gagsterName'], 'Gunk Gagster')
        self.assertTrue(params.get('waveScripts'))
        self.assertEqual(params['finalePhase'], 0)

    def test_finale_p1_params_before_phase_advance(self):
        act = self.acts_by_id['finale']
        params = resolve_act_params(act, finale_phase=0)
        self.assertTrue(act.get('finale'))
        self.assertEqual(params['finalePhase'], 1)
        self.assertEqual(params['packSize'], 1)
        self.assertEqual(params['maxPacks'], 2)
        self.assertEqual(params['corruptHp'], 90)
        self.assertEqual(params['corruptName'], 'Ink Overlord')
        self.assertEqual(params['seedPollution'], 0.75)
        self.assertEqual(params['bruteFraction'], 0.0)
        self.assertEqual(params['snareFraction'], 0.0)
        self.assertEqual(params['gagsterFraction'], 0.0)
        self.assertEqual(params.get('waveScripts'), act.get('waveScripts'))
        self.assertFalse(params['transitionSting'])
        self.assertIn('Phase 1', params['banner'])

    def test_finale_p2_merge_overrides_scalars(self):
        act = self.acts_by_id['finale']
        # After first Silly reclaim, director sets _finalePhase >= 1.
        params = resolve_act_params(act, finale_phase=1)
        phase2 = act['phase2']
        self.assertEqual(params['finalePhase'], 2)
        self.assertEqual(params['packSize'], phase2['packSize'])
        self.assertEqual(params['maxPacks'], phase2['maxPacks'])
        self.assertEqual(params['corruptHp'], phase2['corruptHp'])
        self.assertEqual(params['corruptName'], phase2['corruptName'])
        self.assertEqual(params['seedPollution'], phase2['seedPollution'])
        self.assertEqual(params['banner'], phase2['banner'])
        self.assertTrue(params['transitionSting'])
        # Explicit Overlord-only mix retained on P2.
        self.assertEqual(params['bruteFraction'], 0.0)
        self.assertEqual(params['snareFraction'], 0.0)
        self.assertEqual(params['gagsterFraction'], 0.0)
        self.assertEqual(params.get('waveScripts'), phase2.get('waveScripts'))
        # P2 is strictly harder than P1 on the key combat scalars.
        self.assertGreater(params['corruptHp'], act['corruptHp'])
        self.assertGreater(params['packSize'], act['packSize'])
        self.assertGreater(params['maxPacks'], act['maxPacks'])
        self.assertGreater(params['seedPollution'], act['seedPollution'])

    def test_finale_phase2_table_shape(self):
        phase2 = self.acts_by_id['finale']['phase2']
        self.assertEqual(phase2['finalePhase'], 2)
        self.assertEqual(phase2['corruptHp'], 160)
        self.assertEqual(phase2['packSize'], 2)
        self.assertEqual(phase2['maxPacks'], 3)
        self.assertEqual(phase2['corruptName'], 'Ink Overlord Unleashed')
        self.assertTrue(phase2.get('transitionSting'))
        self.assertTrue(phase2.get('waveScripts'))
        self.assertEqual(len(phase2['waveScripts']), 3)

    def test_acts_align_with_street_packs_on_shared_keys(self):
        """Campaign C and discoverable auto-reclaim share hood fantasy scalars."""
        rg = self.rg
        shared = (
            'seedPollution', 'packSize', 'maxPacks', 'corruptHp',
            'corruptName', 'bruteFraction', 'snareFraction', 'gagsterFraction',
        )
        # Loopy campaign Act 1 is Smudge-only (brute/snare 0); STREET_PACKS
        # Loopy still introduces Brutes from wave 2 for auto-reclaim demos.
        # Align on HP / pollution / pack size / naming / wave depth + elite.
        loopy_act = self.acts_by_id['loopy']
        loopy_pack = rg.STREET_PACKS[LOOPY]
        for key in (
                'seedPollution', 'packSize', 'maxPacks', 'corruptHp',
                'corruptName', 'waveScripts', 'waveModifiers', 'ambushBeats'):
            self.assertEqual(
                loopy_act[key], loopy_pack[key],
                msg='loopy %s act vs STREET_PACKS' % key)

        punch_act = self.acts_by_id['punchline']
        punch_pack = rg.STREET_PACKS[PUNCHLINE]
        for key in shared + (
                'bruteWaveStart', 'snareWaveStart', 'gagsterWaveStart',
                'waveScripts', 'waveModifiers', 'ambushBeats'):
            self.assertEqual(
                punch_act[key], punch_pack[key],
                msg='punchline %s act vs STREET_PACKS' % key)

        # Finale P1 matches Silly STREET_PACKS Overlord-only spawn + elite/ambush.
        # overlordP2HpFrac stays R-only (intentional C asymmetry).
        finale_p1 = resolve_act_params(self.acts_by_id['finale'], 0)
        silly_pack = rg.STREET_PACKS[SILLY]
        for key in (
                'seedPollution', 'packSize', 'maxPacks', 'corruptHp',
                'corruptName', 'bruteFraction', 'snareFraction',
                'gagsterFraction', 'waveScripts', 'waveModifiers',
                'ambushBeats'):
            self.assertEqual(
                finale_p1[key], silly_pack[key],
                msg='finale P1 %s vs silly STREET_PACKS' % key)
        self.assertNotIn('overlordP2HpFrac', self.acts_by_id['finale'])
        self.assertNotIn('overlordP2HpFrac', finale_p1)

    def test_act_wave_scripts_resolve_through_p2(self):
        """Campaign ACTS scripts (#185) resolve to distinct hood beats + P2 swell."""
        rg, cg, camp = self.rg, self.cg, self.camp
        loopy = camp.ACTS[0]
        punch = camp.ACTS[1]
        finale = camp.ACTS[2]

        self.assertEqual(
            rg.resolveWaveScript(loopy['waveScripts'], 1),
            [cg.ARCHETYPE_INK] * 3)
        self.assertEqual(
            rg.resolveWaveScript(loopy['waveScripts'], 2),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE])
        self.assertEqual(
            rg.resolveWaveScript(loopy['waveScripts'], 3),
            [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE,
             cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveWaveScript(loopy['waveScripts'], 4),
            [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_INK, cg.ARCHETYPE_BRUTE,
             cg.ARCHETYPE_SNARE, cg.ARCHETYPE_INK])

        punch_w1 = rg.resolveWaveScript(punch['waveScripts'], 1)
        self.assertEqual(punch_w1[0], cg.ARCHETYPE_SNARE)
        self.assertEqual(punch_w1[1], cg.ARCHETYPE_GAGSTER)
        self.assertEqual(punch_w1[-1], cg.ARCHETYPE_BRUTE)
        self.assertIn(cg.ARCHETYPE_GAGSTER, punch_w1)
        # Full Punchline campaign scripts keep gagster mid through wave 4.
        punch_w2 = rg.resolveWaveScript(punch['waveScripts'], 2)
        self.assertEqual(
            punch_w2,
            [cg.ARCHETYPE_SNARE, cg.ARCHETYPE_GAGSTER, cg.ARCHETYPE_GAGSTER,
             cg.ARCHETYPE_BRUTE, cg.ARCHETYPE_INK])

        p1 = resolve_act_params(finale, finale_phase=0)
        self.assertEqual(
            rg.resolveWaveScript(p1['waveScripts'], 1), [cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveWaveScript(p1['waveScripts'], 2),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])

        p2 = resolve_act_params(finale, finale_phase=1)
        self.assertEqual(p2['finalePhase'], 2)
        self.assertEqual(
            rg.resolveWaveScript(p2['waveScripts'], 1),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveWaveScript(p2['waveScripts'], 3),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        # P2 add kwargs stay on the merge for Unleashed Smudge pressure (#187).
        self.assertEqual(p2.get('addWaveStart'), 2)
        self.assertEqual(p2.get('addCount'), 2)
        self.assertEqual(p2.get('addName'), 'Ink Smudge')

    def test_acts_elite_and_ambush_mirror_street_packs(self):
        """Campaign C path carries elite/ambush tables (gap #1+#6)."""
        rg, cg = self.rg, self.cg
        loopy = resolve_act_params(self.acts_by_id['loopy'])
        punch = resolve_act_params(self.acts_by_id['punchline'])
        finale = resolve_act_params(self.acts_by_id['finale'], 0)

        self.assertEqual(loopy['maxPacks'], 4)
        loopy_mods = rg.resolveWaveModifiers(loopy['waveModifiers'], 4)
        self.assertTrue(rg.waveIsElite(loopy_mods))
        self.assertEqual(
            rg.resolveAmbushBeat(loopy['ambushBeats'], 1),
            [cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveAmbushBeat(loopy['ambushBeats'], 3),
            [cg.ARCHETYPE_SNARE])

        punch_mods = rg.resolveWaveModifiers(punch['waveModifiers'], 4)
        self.assertTrue(rg.waveIsElite(punch_mods))
        self.assertEqual(
            rg.resolveAmbushBeat(punch['ambushBeats'], 3),
            [cg.ARCHETYPE_GAGSTER, cg.ARCHETYPE_SNARE])

        silly_mods = rg.resolveWaveModifiers(finale['waveModifiers'], 2)
        self.assertTrue(rg.waveIsElite(silly_mods))
        self.assertEqual(
            rg.resolveAmbushBeat(finale['ambushBeats'], 1),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        # C Silly P2 asymmetry: no mid-fight HP promote on ACTS.
        self.assertIsNone(finale.get('overlordP2HpFrac'))

    def test_campaign_director_passes_elite_and_ambush(self):
        """CampaignDirectorAI._actParams / start wire elite + ambush kwargs."""
        src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'CampaignDirectorAI.py'
        ).read_text(encoding='utf-8')
        self.assertIn("'waveModifiers': act.get('waveModifiers')", src)
        self.assertIn("'ambushBeats': act.get('ambushBeats')", src)
        self.assertIn('waveModifiers=params.get(\'waveModifiers\')', src)
        self.assertIn('ambushBeats=params.get(\'ambushBeats\')', src)
        # Do not promote R-only overlordP2HpFrac onto C start.
        self.assertNotIn('overlordP2HpFrac=params.get', src)
        self.assertNotIn('keyblade', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())

    def test_hub_tip_discoverability_copy(self):
        """Hub tip (#184) points at Loopy + C campaign without magic words."""
        camp = self.camp
        tip = camp.hubPlayEntryTip()
        self.assertIn('Oswald', tip)
        self.assertIn('Loopy Lane', tip)
        self.assertIn('C campaign', tip)
        self.assertNotIn('~startcampaign', tip)
        self.assertNotIn('2200', tip)
        # Soft next-street cue after handoff.
        next_tip = camp.hubPlayEntryTip(nextStreet='Punchline Place')
        self.assertIn('Punchline Place', next_tip)
        hint = camp.handoffTravelHint({'name': 'Silly Street'})
        self.assertIn('Silly Street', hint)
        self.assertNotIn('~startcampaign', hint)

    def test_loopy_mid_act_trust_fracture(self):
        """Loopy clear (#190) foreshadows twist — Punchline deepens unease."""
        camp = self.camp
        loopy = self.acts_by_id['loopy']
        punch = self.acts_by_id['punchline']
        finale = self.acts_by_id['finale']

        self.assertIs(loopy.get('trustFracture'), True)
        self.assertIs(punch.get('trustFracture'), True)
        self.assertFalse(bool(finale.get('trustFracture')))

        handoff = loopy.get('handoff') or ''
        next_cue = loopy.get('nextCue') or ''
        self.assertIn('rubbery beat', handoff.lower())
        self.assertIn('Punchline Place', handoff)
        self.assertIn('stretchy', next_cue.lower())
        # Punchline handoff/act tip deepen Oswald unease (no Silly spoilers).
        punch_handoff = punch.get('handoff') or ''
        punch_cue = punch.get('nextCue') or ''
        punch_tip = punch.get('entryTip') or ''
        self.assertIn('rubbery again', punch_handoff.lower())
        self.assertIn('half-beat', punch_cue.lower())
        self.assertIn('half-beat late', punch_cue.lower())
        self.assertIn('half-beat off', punch_tip.lower())
        self.assertIn('Silly Street', punch_handoff)
        # Combat cues stay on Punchline tip (Gagster / Brute / Snare / reclaim).
        tip_l = punch_tip.lower()
        self.assertIn('gunk gagster', tip_l)
        self.assertIn('reclaim', tip_l)
        self.assertIn('shift dodge', tip_l)
        # Foreshadow only — no Silly twist spoilers on mid-act beat.
        for banned in (
                'keyblade', 'kingdom hearts', 'betrayed', 'villain',
                'caused the corruption', 'his all along', 'sora'):
            for blob in (
                    handoff, next_cue, punch_handoff, punch_cue, punch_tip):
                self.assertNotIn(banned, blob.lower())

        # Cool cream → shadow fleck edge tunables present + enabled.
        self.assertTrue(camp.OSWALD_TRUST_FRACTURE_CREAM_EDGE_ENABLED)
        self.assertGreater(camp.OSWALD_TRUST_FRACTURE_CREAM_EDGE_HOLD_SEC, 0.0)
        self.assertGreater(camp.OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_COUNT, 0)
        self.assertGreater(camp.OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC, 0.0)
        # Fracture settle rest is a rubbery beat (not a snap).
        self.assertGreaterEqual(
            camp.OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC, 0.10)
        # Fracture edge is cooler/longer-hold than sunny handoff edge.
        sunny_hold = float(getattr(
            camp, 'HANDOFF_CREAM_EDGE_HOLD_SEC', 0.0) or 0.0)
        if sunny_hold > 0.0:
            self.assertGreaterEqual(
                camp.OSWALD_TRUST_FRACTURE_CREAM_EDGE_HOLD_SEC, sunny_hold)

    def test_loopy_approach_unease_tip(self):
        """Loopy mid-act approach tip foreshadows before Punchline handoff."""
        camp = self.camp
        loopy = self.acts_by_id['loopy']
        punch = self.acts_by_id['punchline']
        # Early Act 1 entry stays trusted STREET_PACK tip (no campaign entryTip).
        self.assertFalse(bool(loopy.get('entryTip')))
        approach = loopy.get('approachTip') or ''
        self.assertIn('rubbery half-beat', approach.lower())
        self.assertIn('ink', approach.lower())
        self.assertIn('reclaim', approach.lower())
        self.assertIn('smudge', approach.lower())
        # Lighter than Punchline "half-beat off" / Silly almost-confess.
        self.assertNotIn('half-beat off', approach.lower())
        self.assertNotIn('almost confess', approach.lower())
        # Punchline entryTip still deepens the Act 1 mid-act beat.
        punch_tip = punch.get('entryTip') or ''
        self.assertIn('half-beat off', punch_tip.lower())
        for banned in (
                'keyblade', 'kingdom hearts', 'caused the corruption',
                'his all along', 'betrayed', 'villain', 'sora'):
            self.assertNotIn(banned, approach.lower())
        self.assertGreater(camp.LOOPY_APPROACH_TIP_DELAY_SEC, 0.0)
        self.assertGreaterEqual(
            camp.LOOPY_APPROACH_TIP_DELAY_SEC,
            1.55)  # after Loopy auto-reclaim explore beat
        play_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'PlayEntry.py'
        ).read_text(encoding='utf-8')
        self.assertIn('_armLoopyApproachTip', play_src)
        self.assertIn('_showLoopyApproachTip', play_src)
        self.assertIn('_cancelLoopyApproachTip', play_src)
        self.assertIn('LOOPY_APPROACH_TIP_DELAY_SEC', play_src)
        self.assertIn("tipHose == 'loopy'", play_src)
        self.assertIn("loopyAct.get('trustFracture')", play_src)
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT', play_src)
        # No cream hose/wash deepen on Loopy tipHose path.
        tip_idx = play_src.find('def _tipHosePopInterval')
        loopy_idx = play_src.find("tipHose == 'loopy'", tip_idx)
        punch_idx = play_src.find("tipHose == 'punchline'", tip_idx)
        self.assertGreater(loopy_idx, 0)
        self.assertGreater(punch_idx, loopy_idx)
        loopy_snip = play_src[loopy_idx:punch_idx]
        self.assertNotIn('CREAM_HOSE', loopy_snip)
        self.assertNotIn('CREAM_WASH', loopy_snip)
        magic_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8')
        magic_l = magic_src.lower()
        self.assertIn('loopy mid-act unease tip', magic_l)
        self.assertIn('rubbery half-beat', magic_l)

    def test_punchline_tip_uses_fracture_settle(self):
        """#198 — Punchline tipHose reads trustFracture settle when armed."""
        play_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'PlayEntry.py'
        ).read_text(encoding='utf-8')
        tip_idx = play_src.find('def _tipHosePopInterval')
        self.assertGreater(tip_idx, 0)
        punch_idx = play_src.find("tipHose == 'punchline'", tip_idx)
        silly_idx = play_src.find("tipHose == 'silly'", tip_idx)
        # Outer tipHose else follows the silly branch (skip nested else:).
        else_idx = play_src.find('\n        else:', silly_idx if silly_idx > 0 else tip_idx)
        self.assertGreater(punch_idx, 0)
        self.assertGreater(silly_idx, punch_idx)
        punch_snip = play_src[punch_idx:silly_idx]
        self.assertIn("act.get('id') == 'punchline'", punch_snip)
        self.assertIn("punchAct.get('trustFracture')", punch_snip)
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT', punch_snip)
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC', punch_snip)
        # #200 — Silly tipHose uses fracture settle when entryTipUnease armed.
        silly_end = else_idx if else_idx > silly_idx else silly_idx + 1600
        silly_snip = play_src[silly_idx:silly_end]
        self.assertIn("sillyAct.get('entryTipUnease')", silly_snip)
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT', silly_snip)
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC', silly_snip)
        self.assertIn('SILLY_ACT_TIP_TRUST_SETTLE_OVERSHOOT', silly_snip)
        magic_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8')
        magic_l = magic_src.lower()
        self.assertIn('tip unease', magic_l)
        self.assertIn('punchline', magic_l)
        # Advanced desc explicitly rejects KH props (word appears only as ban).
        self.assertIn('no keyblades', magic_l)
        self.assertNotIn('kingdom hearts', magic_l)

    def test_silly_approach_almost_confess_tip(self):
        """Silly mid-act approach tip almost-confesses before finale reveal."""
        camp = self.camp
        finale = self.acts_by_id['finale']
        entry = finale.get('entryTip') or ''
        approach = finale.get('approachTip') or ''
        self.assertTrue(finale.get('entryTipUnease'))
        self.assertFalse(bool(finale.get('trustFracture')))
        self.assertIn('cheer feels wrong', entry.lower())
        self.assertIn('ink overlord', entry.lower())
        self.assertIn('almost confess', approach.lower())
        self.assertIn('gag went wrong', approach.lower())
        self.assertIn('overlord', approach.lower())
        # Half-truth only — full twist stays on victory reveal.
        for banned in (
                'keyblade', 'kingdom hearts', 'caused the corruption',
                'his all along', 'betrayed', 'villain', 'sora'):
            self.assertNotIn(banned, approach.lower())
            self.assertNotIn(banned, entry.lower())
        self.assertGreater(camp.SILLY_APPROACH_TIP_DELAY_SEC, 0.0)
        self.assertGreaterEqual(
            camp.SILLY_APPROACH_TIP_DELAY_SEC,
            2.15)  # after Silly auto-reclaim explore beat
        play_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'PlayEntry.py'
        ).read_text(encoding='utf-8')
        self.assertIn('_armSillyApproachTip', play_src)
        self.assertIn('_showSillyApproachTip', play_src)
        self.assertIn('_cancelSillyApproachTip', play_src)
        self.assertIn('approachTip', play_src)
        self.assertIn('SILLY_APPROACH_TIP_DELAY_SEC', play_src)
        magic_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8')
        magic_l = magic_src.lower()
        self.assertIn('almost confess', magic_l)
        self.assertIn('half-truth', magic_l)

    def test_handoff_cream_edge_settle_tunables(self):
        """Loopy→Punchline→Silly handoff cream edge settle juicier past #271."""
        camp = self.camp
        self.assertTrue(camp.HANDOFF_CREAM_EDGE_SETTLE_ENABLED)
        over = camp.HANDOFF_CREAM_EDGE_SETTLE_OVERSHOOT
        self.assertEqual(len(over), 4)
        self.assertGreaterEqual(float(over[3]), 0.11)
        self.assertGreaterEqual(float(over[0]), 1.12)
        self.assertGreaterEqual(float(over[2]), 1.18)
        self.assertGreaterEqual(
            float(camp.HANDOFF_CREAM_EDGE_SETTLE_REST_SEC), 0.10)
        rebound = camp.HANDOFF_CREAM_EDGE_SETTLE_REBOUND
        self.assertEqual(len(rebound), 4)
        self.assertGreaterEqual(float(rebound[0]), 1.05)
        self.assertGreaterEqual(float(rebound[2]), 1.08)
        self.assertGreaterEqual(float(rebound[3]), 0.06)
        self.assertGreaterEqual(
            float(camp.HANDOFF_CREAM_EDGE_SETTLE_REBOUND_REST_SEC), 0.10)
        self.assertGreaterEqual(float(camp.HANDOFF_CREAM_WASH_DELAY_SEC), 0.58)
        self.assertGreaterEqual(float(camp.HANDOFF_CREAM_WASH_PEAK), 0.16)
        # Distinct from tip hose / betrayal hose / victory twist.
        self.assertNotEqual(
            tuple(over),
            tuple(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT))
        self.assertNotEqual(
            tuple(over),
            tuple(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT))
        self.assertNotEqual(
            tuple(over),
            tuple(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT))
        edge_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'ActBannerCreamEdgeFx.py'
        ).read_text(encoding='utf-8')
        self.assertIn('_settleScalePart', edge_src)
        self.assertIn('SETTLE_OVERSHOOT', edge_src)
        self.assertIn('SETTLE_REBOUND', edge_src)
        self.assertIn('past #271', edge_src)
        magic_l = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8').lower()
        self.assertIn('juicier deepened edge settle past #271', magic_l)

    def test_punchline_tip_cream_hose_settle_tunables(self):
        """#198 / #227 / #256 deepen — Punchline tip juicier cream hose + rebound."""
        camp = self.camp
        self.assertTrue(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED)
        over = camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertEqual(len(over), 4)
        self.assertGreaterEqual(float(over[0]), 1.10)
        self.assertGreaterEqual(float(over[2]), 1.15)
        self.assertGreaterEqual(float(over[3]), 0.075)
        self.assertGreaterEqual(
            float(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC), 0.11)
        rebound = camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND
        self.assertEqual(len(rebound), 4)
        self.assertGreaterEqual(float(rebound[0]), 1.035)
        self.assertGreaterEqual(float(rebound[2]), 1.06)
        self.assertGreaterEqual(float(rebound[3]), 0.045)
        self.assertLess(float(rebound[0]), float(over[0]))
        self.assertNotEqual(
            tuple(rebound),
            tuple(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND))
        self.assertGreaterEqual(
            float(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND_REST_SEC),
            0.07)
        self.assertGreaterEqual(
            float(camp.PUNCHLINE_ACT_TIP_CREAM_WASH_DELAY_SEC), 0.70)
        self.assertGreaterEqual(
            float(camp.PUNCHLINE_ACT_TIP_CREAM_WASH_PEAK), 0.13)
        # Distinct from Silly almost-confess (#232/#279) and wash (#251/#279).
        self.assertNotEqual(
            tuple(over),
            tuple(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT))
        self.assertFalse(hasattr(
            camp, 'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND'))
        self.assertNotEqual(
            float(over[2]),
            float(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ORIGIN[2]))
        play_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'PlayEntry.py'
        ).read_text(encoding='utf-8')
        self.assertIn('PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED', play_src)
        self.assertIn('PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT', play_src)
        self.assertIn('PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND', play_src)
        self.assertIn('#256', play_src)
        magic_l = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8').lower()
        self.assertIn('juicier deepened cream hose settle', magic_l)
        self.assertIn('past #256', magic_l)
        self.assertIn('micro rebound', magic_l)

    def test_silly_tip_cream_hose_settle_tunables(self):
        """#207 / #232 / #279 Silly almost-confess tip cream hose settle deepen."""
        camp = self.camp
        self.assertTrue(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED)
        over = camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertEqual(len(over), 4)
        # Past #279 floors (1.11 / 1.17 / 0.08 / rest 0.12).
        self.assertGreaterEqual(float(over[0]), 1.13)
        self.assertGreaterEqual(float(over[2]), 1.20)
        self.assertGreaterEqual(float(over[3]), 0.09)
        self.assertGreaterEqual(
            float(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC), 0.13)
        # Distinct from Punchline #227 / #256 / #284; no Silly tip rebound.
        self.assertNotEqual(
            tuple(over),
            tuple(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT))
        self.assertFalse(hasattr(
            camp, 'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND'))
        self.assertLess(
            float(over[2]),
            float(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT[2]))
        play_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'PlayEntry.py'
        ).read_text(encoding='utf-8')
        self.assertIn('SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED', play_src)
        self.assertIn('SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT', play_src)
        self.assertIn('past #279', play_src)
        magic_l = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8').lower()
        self.assertIn('cream hose settle past #279', magic_l)
        self.assertIn('almost confess', magic_l)

    def test_silly_tip_cream_wash_deepen_tunables(self):
        """#200 / #251 / #279 Silly almost-confess tip cream wash deepen."""
        camp = self.camp
        self.assertTrue(camp.SILLY_ACT_TIP_CREAM_WASH_ENABLED)
        self.assertTrue(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ENABLED)
        # Past #279 floors (0.15 / 0.09 / aftershock 5 / halo 1.18).
        self.assertGreaterEqual(float(camp.SILLY_ACT_TIP_CREAM_WASH_PEAK), 0.15)
        self.assertGreaterEqual(float(camp.SILLY_ACT_TIP_CREAM_WASH_MID), 0.10)
        self.assertGreaterEqual(
            int(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COUNT), 5)
        self.assertGreaterEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_PEAK), 1.22)
        self.assertGreaterEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_SEC), 0.40)
        origin = camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ORIGIN
        self.assertEqual(len(origin), 3)
        self.assertLess(float(origin[2]), 0.0)
        # Distinct from victory twist aftershock (#244) and betrayal hose (#288).
        self.assertNotEqual(
            tuple(origin), tuple(camp.VICTORY_TWIST_CONFETTI_ORIGIN))
        self.assertNotEqual(
            int(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COUNT),
            int(camp.VICTORY_TWIST_CONFETTI_AFTERSHOCK_COUNT))
        self.assertNotEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_PEAK),
            float(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT[0]))
        self.assertLess(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_PEAK),
            float(camp.VICTORY_CREAM_WASH_PEAK))
        wash_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'SillyTipCreamWashFx.py'
        ).read_text(encoding='utf-8')
        self.assertIn('SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK', wash_src)
        self.assertIn('_buildAftershock', wash_src)
        self.assertIn('almost-confess', wash_src.lower())
        self.assertIn('past #279', wash_src)
        magic_l = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8').lower()
        self.assertIn('cream aftershock past #279', magic_l)
        self.assertIn('cream aftershock', magic_l)

    def test_betrayal_banner_cream_hose_settle_tunables(self):
        """#212 / #235 / #260 deepen — betrayal banner juicier cream hose past #260."""
        camp = self.camp
        self.assertTrue(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_ENABLED)
        over = camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertEqual(len(over), 4)
        self.assertGreaterEqual(float(over[0]), 1.16)
        self.assertGreaterEqual(float(over[2]), 1.26)
        self.assertGreaterEqual(float(over[3]), 0.10)
        self.assertGreaterEqual(
            float(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REST_SEC), 0.15)
        rebound = camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND
        self.assertEqual(len(rebound), 4)
        self.assertGreaterEqual(float(rebound[0]), 1.05)
        self.assertGreaterEqual(float(rebound[2]), 1.09)
        self.assertGreaterEqual(float(rebound[3]), 0.055)
        self.assertGreaterEqual(
            float(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND_REST_SEC),
            0.08)
        # Distinct from Punchline tip rebound (#256/#284) and Silly tip.
        self.assertNotEqual(
            tuple(over),
            tuple(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT))
        self.assertNotEqual(
            tuple(over),
            tuple(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT))
        self.assertNotEqual(
            tuple(rebound),
            tuple(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND))
        handoff_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'CampaignHandoff.py'
        ).read_text(encoding='utf-8')
        self.assertIn('FINALE_BETRAYAL_CREAM_HOSE_SETTLE_ENABLED', handoff_src)
        self.assertIn(
            'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT', handoff_src)
        self.assertIn(
            'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND', handoff_src)
        self.assertIn('past #260', handoff_src)
        magic_l = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8').lower()
        self.assertIn('cream hose settle past #260', magic_l)
        self.assertIn('micro rebound', magic_l)
        self.assertIn('betrayal handoff banner', magic_l)

    def test_finale_betrayal_handoff_banner(self):
        """Finale betrayal handoff plate lands twist when reveal fires."""
        camp = self.camp
        finale = self.acts_by_id['finale']
        self.assertTrue(finale.get('betrayalHandoff'))
        self.assertFalse(bool(finale.get('trustFracture')))
        self.assertIn('caused the corruption', camp.FINALE_REVEAL_BANNER.lower())
        self.assertIn('trusted', camp.FINALE_REVEAL_SUB.lower())
        self.assertIn('smile', camp.FINALE_BETRAYAL_HANDOFF_CUE.lower())
        self.assertGreater(camp.FINALE_BETRAYAL_HANDOFF_HOLD_SEC, 0.0)
        self.assertGreater(camp.FINALE_BETRAYAL_SETTLE_REST_SEC, 0.0)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, camp.FINALE_REVEAL_BANNER.lower())
            self.assertNotIn(banned, camp.FINALE_REVEAL_SUB.lower())
            self.assertNotIn(banned, camp.FINALE_BETRAYAL_HANDOFF_CUE.lower())
        handoff_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'CampaignHandoff.py'
        ).read_text(encoding='utf-8')
        self.assertIn('oswaldRevealBanner', handoff_src)
        self.assertIn('_onOswaldBetrayalBanner', handoff_src)
        self.assertIn('_showBetrayalHandoff', handoff_src)
        self.assertIn('betrayalHandoff', handoff_src)
        self.assertIn('FINALE_BETRAYAL_SETTLE_OVERSHOOT', handoff_src)
        self.assertIn('FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT', handoff_src)
        self.assertIn('playFinaleRevealCreamEdge', handoff_src)
        self.assertIn('playVictoryTwistConfettiSting', handoff_src)
        self.assertIn('clearVictoryTwistConfettiSting', handoff_src)
        self.assertTrue(getattr(camp, 'VICTORY_TWIST_CONFETTI_ENABLED', False))
        self.assertGreaterEqual(camp.VICTORY_TWIST_CONFETTI_COUNT, 13)
        self.assertTrue(
            getattr(camp, 'VICTORY_TWIST_CONFETTI_AFTERSHOCK_ENABLED', False))
        self.assertGreaterEqual(
            float(getattr(camp, 'VICTORY_TWIST_CONFETTI_POP', 0)), 1.84)
        self.assertGreaterEqual(
            float(getattr(camp, 'VICTORY_TWIST_CONFETTI_POP_REBOUND', 0)),
            1.28)
        self.assertGreaterEqual(
            camp.VICTORY_TWIST_CONFETTI_AFTERSHOCK_COUNT, 8)
        self.assertGreaterEqual(
            camp.VICTORY_TWIST_CONFETTI_STREAK_COUNT, 6)
        sting_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'VictoryTwistConfettiSting.py'
        ).read_text(encoding='utf-8')
        self.assertIn('VictoryTwistConfettiSting', sting_src)
        self.assertIn('caused the corruption', sting_src.lower())
        self.assertIn('_buildAftershock', sting_src)
        self.assertIn('past #265', sting_src)
        self.assertIn('VICTORY_TWIST_CONFETTI_POP', sting_src)
        self.assertIn('VICTORY_TWIST_CONFETTI_POP_REBOUND', sting_src)
        finale_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'FinalePhaseFx.py'
        ).read_text(encoding='utf-8')
        self.assertIn('ensureCampaignHandoffClient', finale_src)
        self.assertIn('oswaldRevealBanner', finale_src)
        magic_src = (
            Path(__file__).resolve().parents[1]
            / 'toontown' / 'campaign' / 'MagicWords.py'
        ).read_text(encoding='utf-8')
        magic_l = magic_src.lower()
        self.assertIn('betrayal handoff', magic_l)
        self.assertIn('deepened victory/confetti twist cream sting', magic_l)
        self.assertIn('past #265', magic_l)
        self.assertIn('taller micro cream pop', magic_l)
        self.assertIn('no keyblades', magic_l)

    def test_act_param_keys_present_for_director(self):
        for act_id, act in self.acts_by_id.items():
            params = resolve_act_params(act)
            for key in _ACT_PARAM_KEYS:
                # Optional mix keys may be absent on Smudge-only acts.
                if key in (
                        'bruteWaveStart', 'bruteName',
                        'snareWaveStart', 'snareName',
                        'gagsterWaveStart', 'gagsterName'):
                    continue
                self.assertIn(
                    key, params,
                    msg='%s missing %s after resolve' % (act_id, key))


if __name__ == '__main__':
    unittest.main()
