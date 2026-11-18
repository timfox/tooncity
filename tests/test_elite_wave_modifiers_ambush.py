#!/usr/bin/env python3
"""Headless tests for elite wave modifiers + between-wave ambush beats.

Locks real HP/damage modifiers, earlier-wave ambush tables (beyond
post-wave-3 only), Silly between-swell ambush/elite pressure, STREET_PACKS
wiring, and AST hooks on DistributedReclaimDirectorAI / client
announceAmbushSpawn / toon.dc.

Run from repo root:
  python3 tests/test_elite_wave_modifiers_ambush.py
  python3 -m unittest tests.test_elite_wave_modifiers_ambush -v
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
    sys.modules['toontown.reclaim'].ReclaimGlobals = rg

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp
    return rg, cg, camp


class EliteWaveModifiersAmbushTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.cg, cls.camp = _load_panda_free_reclaim()

    def test_elite_constants_are_real_buffs(self):
        rg = self.rg
        self.assertGreater(rg.ELITE_HP_MULT, 1.0)
        self.assertGreater(rg.ELITE_DAMAGE_MULT, 1.0)
        self.assertGreater(rg.AMBUSH_DELAY, 0.0)
        self.assertLess(rg.AMBUSH_DELAY, rg.WAVE_SPAWN_DELAY)
        self.assertTrue(rg.ELITE_NAME_PREFIX)
        self.assertTrue(rg.AMBUSH_NAME_PREFIX)
        self.assertIn('attackDamage', rg.ELITE_DAMAGE_STAT_KEYS)

    def test_resolve_wave_modifiers_elite_defaults(self):
        rg = self.rg
        mods = {4: {'elite': True}, '2': {'hpMult': 1.5, 'damageMult': 2.0}}
        w4 = rg.resolveWaveModifiers(mods, 4)
        self.assertTrue(rg.waveIsElite(w4))
        self.assertEqual(rg.waveHpMult(w4), rg.ELITE_HP_MULT)
        self.assertEqual(rg.waveDamageMult(w4), rg.ELITE_DAMAGE_MULT)

        w2 = rg.resolveWaveModifiers(mods, 2)
        self.assertTrue(rg.waveIsElite(w2))
        self.assertEqual(rg.waveHpMult(w2), 1.5)
        self.assertEqual(rg.waveDamageMult(w2), 2.0)

        self.assertIsNone(rg.resolveWaveModifiers(mods, 1))
        self.assertIsNone(rg.resolveWaveModifiers(None, 4))
        self.assertFalse(rg.waveIsElite(None))
        self.assertFalse(rg.waveIsElite({}))

    def test_apply_elite_hp_and_name(self):
        rg = self.rg
        mods = {'elite': True}
        base = 46  # Loopy wave-4 scaled base before elite
        elite_hp = rg.applyElitePackHp(base, mods)
        self.assertEqual(
            elite_hp, max(1, int(round(base * rg.ELITE_HP_MULT))))
        self.assertGreater(elite_hp, base)
        self.assertEqual(
            rg.applyElitePackHp(base, None), base)
        self.assertEqual(
            rg.applyElitePackName('Ink Smudge', mods),
            rg.ELITE_NAME_PREFIX + 'Ink Smudge')
        # Idempotent prefix.
        tagged = rg.ELITE_NAME_PREFIX + 'Ink Smudge'
        self.assertEqual(rg.applyElitePackName(tagged, mods), tagged)
        self.assertEqual(rg.applyElitePackName('Ink Smudge', None), 'Ink Smudge')

    def test_apply_wave_damage_mult_scales_kit_keys(self):
        rg = self.rg
        stats = {
            'attackDamage': 2,
            'dashDamage': 2,
            'splatDamage': 3,
            'chaseSpeed': 9.0,
            'name': 'Ink Smudge',
        }
        out = rg.applyWaveDamageMultToStats(stats, {'elite': True})
        mult = rg.ELITE_DAMAGE_MULT
        self.assertEqual(
            out['attackDamage'], max(1, int(round(2 * mult))))
        self.assertEqual(
            out['dashDamage'], max(1, int(round(2 * mult))))
        self.assertEqual(
            out['splatDamage'], max(1, int(round(3 * mult))))
        # Non-damage keys untouched.
        self.assertEqual(out['chaseSpeed'], 9.0)
        self.assertEqual(out['name'], 'Ink Smudge')
        # No-op without mods.
        self.assertEqual(
            rg.applyWaveDamageMultToStats(stats, None)['attackDamage'], 2)

    def test_resolve_ambush_beat_tokens(self):
        rg, cg = self.rg, self.cg
        beats = {3: ('snare',), '2': ('gagster', 'ink')}
        self.assertEqual(
            rg.resolveAmbushBeat(beats, 3), [cg.ARCHETYPE_SNARE])
        self.assertEqual(
            rg.resolveAmbushBeat(beats, 2),
            [cg.ARCHETYPE_GAGSTER, cg.ARCHETYPE_INK])
        self.assertIsNone(rg.resolveAmbushBeat(beats, 1))
        self.assertIsNone(rg.resolveAmbushBeat(None, 3))

    def test_street_packs_elite_and_ambush_not_composition_only(self):
        rg, cg = self.rg, self.cg
        loopy = rg.STREET_PACKS[LOOPY]
        punch = rg.STREET_PACKS[PUNCHLINE]
        silly = rg.STREET_PACKS[SILLY]

        loopy_mods = rg.resolveWaveModifiers(loopy['waveModifiers'], 4)
        self.assertTrue(rg.waveIsElite(loopy_mods))
        self.assertIsNone(
            rg.resolveWaveModifiers(loopy['waveModifiers'], 3))
        # Earlier-wave ambushes beyond post-wave-3 only.
        self.assertEqual(
            rg.resolveAmbushBeat(loopy['ambushBeats'], 1),
            [cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveAmbushBeat(loopy['ambushBeats'], 2),
            [cg.ARCHETYPE_SNARE])
        self.assertEqual(
            rg.resolveAmbushBeat(loopy['ambushBeats'], 3),
            [cg.ARCHETYPE_SNARE])

        punch_mods = rg.resolveWaveModifiers(punch['waveModifiers'], 4)
        self.assertTrue(rg.waveIsElite(punch_mods))
        self.assertEqual(
            rg.resolveAmbushBeat(punch['ambushBeats'], 1),
            [cg.ARCHETYPE_GAGSTER])
        self.assertEqual(
            rg.resolveAmbushBeat(punch['ambushBeats'], 2),
            [cg.ARCHETYPE_SNARE])
        self.assertEqual(
            rg.resolveAmbushBeat(punch['ambushBeats'], 3),
            [cg.ARCHETYPE_GAGSTER, cg.ARCHETYPE_SNARE])

        # Silly between-swell: Smudge ambush after solo + elite twin swell.
        self.assertIn('waveModifiers', silly)
        self.assertIn('ambushBeats', silly)
        silly_mods = rg.resolveWaveModifiers(silly['waveModifiers'], 2)
        self.assertTrue(rg.waveIsElite(silly_mods))
        self.assertIsNone(
            rg.resolveWaveModifiers(silly['waveModifiers'], 1))
        self.assertEqual(
            rg.resolveAmbushBeat(silly['ambushBeats'], 1),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertIsNone(rg.resolveAmbushBeat(silly['ambushBeats'], 2))

        # streetPackParams forwards both keys for director.start().
        for zone in (LOOPY, PUNCHLINE, SILLY):
            params = rg.streetPackParams(zone)
            self.assertIn('waveModifiers', params)
            self.assertIn('ambushBeats', params)
            self.assertEqual(
                params['waveModifiers'],
                rg.STREET_PACKS[zone]['waveModifiers'])
            self.assertEqual(
                params['ambushBeats'],
                rg.STREET_PACKS[zone]['ambushBeats'])

    def test_wave_clear_tip_foreshadows_ambush(self):
        rg = self.rg
        # Earlier waves + post-3 all foreshadow ambush on Loopy / Punchline.
        for wave in (1, 2, 3):
            loopy_tip = rg.waveClearedOswaldTip(wave, zoneId=LOOPY)
            self.assertIn(
                'ambush', loopy_tip.lower(),
                msg='Loopy wave %s clear tip missing ambush' % wave)
            punch_tip = rg.waveClearedOswaldTip(wave, zoneId=PUNCHLINE)
            self.assertIn(
                'ambush', punch_tip.lower(),
                msg='Punchline wave %s clear tip missing ambush' % wave)
        # Silly between-swell after solo Overlord.
        silly_tip = rg.waveClearedOswaldTip(1, zoneId=SILLY)
        self.assertIn('ambush', silly_tip.lower())
        self.assertIn('swell', silly_tip.lower())
        # Final Silly wave has no trailing ambush — plain pause tip.
        self.assertNotIn(
            'ambush', rg.waveClearedOswaldTip(2, zoneId=SILLY).lower())
        # Wave-aware tips stay Toontown-tone (no KH).
        for wave, zone in (
                (1, LOOPY), (2, LOOPY), (3, LOOPY),
                (1, PUNCHLINE), (3, PUNCHLINE),
                (1, SILLY)):
            tip = rg.ambushOswaldTip(wave, zoneId=zone)
            self.assertIn('ambush', tip.lower())
            self.assertNotIn('keyblade', tip.lower())
            self.assertNotIn('kh', tip.lower())

    def test_elite_wave_announce_copy(self):
        rg = self.rg
        title = rg.waveAnnounceTitle(4, 4, zoneId=LOOPY)
        self.assertIn('Elite', title)
        tip = rg.waveOswaldTip(4, 4, zoneId=LOOPY, packCount=5)
        self.assertIn('elite', tip.lower())
        # Non-elite wave keeps inbound default tone.
        mid = rg.waveAnnounceTitle(2, 4, zoneId=LOOPY)
        self.assertNotIn('Elite', mid)
        # Silly twin swell elite tip (discoverable street pack tables).
        silly_tip = rg.waveOswaldTip(2, 2, zoneId=SILLY, packCount=2)
        self.assertIn('elite', silly_tip.lower())
        self.assertNotIn('keyblade', silly_tip.lower())

    def test_campaign_acts_mirror_street_packs_elite_and_ambush(self):
        """Story C path owns the same elite/ambush tables as discoverable R."""
        rg, cg, camp = self.rg, self.cg, self.camp
        acts = {a['id']: a for a in camp.ACTS}
        loopy = acts['loopy']
        punch = acts['punchline']
        finale = acts['finale']

        self.assertEqual(loopy['maxPacks'], 4)
        self.assertEqual(len(loopy['waveScripts']), 4)
        self.assertEqual(
            loopy['waveScripts'], rg.STREET_PACKS[LOOPY]['waveScripts'])
        self.assertEqual(
            loopy['waveModifiers'], rg.STREET_PACKS[LOOPY]['waveModifiers'])
        self.assertEqual(
            loopy['ambushBeats'], rg.STREET_PACKS[LOOPY]['ambushBeats'])
        self.assertTrue(
            rg.waveIsElite(
                rg.resolveWaveModifiers(loopy['waveModifiers'], 4)))
        self.assertEqual(
            rg.resolveAmbushBeat(loopy['ambushBeats'], 1),
            [cg.ARCHETYPE_INK])

        self.assertEqual(
            punch['waveModifiers'],
            rg.STREET_PACKS[PUNCHLINE]['waveModifiers'])
        self.assertEqual(
            punch['ambushBeats'],
            rg.STREET_PACKS[PUNCHLINE]['ambushBeats'])

        self.assertEqual(
            finale['waveModifiers'],
            rg.STREET_PACKS[SILLY]['waveModifiers'])
        self.assertEqual(
            finale['ambushBeats'],
            rg.STREET_PACKS[SILLY]['ambushBeats'])
        self.assertNotIn('overlordP2HpFrac', finale)

    def test_finale_phase2_elite_and_ambush_beside_adds(self):
        """Story P2 Unleashed swells carry elite/ambush beside Smudge adds."""
        rg, cg, camp = self.rg, self.cg, self.camp
        finale = {a['id']: a for a in camp.ACTS}['finale']
        phase2 = finale['phase2']

        self.assertEqual(phase2['maxPacks'], 3)
        self.assertEqual(phase2.get('addWaveStart'), 2)
        self.assertEqual(phase2.get('addName'), 'Ink Smudge')
        self.assertIn('waveModifiers', phase2)
        self.assertIn('ambushBeats', phase2)
        # Elite on add waves (2+) — pressure beside Unleashed Smudge adds.
        self.assertTrue(
            rg.waveIsElite(
                rg.resolveWaveModifiers(phase2['waveModifiers'], 2)))
        self.assertTrue(
            rg.waveIsElite(
                rg.resolveWaveModifiers(phase2['waveModifiers'], 3)))
        self.assertIsNone(
            rg.resolveWaveModifiers(phase2['waveModifiers'], 1))
        # Between-swell Smudge ambush before wave 2 and wave 3.
        self.assertEqual(
            rg.resolveAmbushBeat(phase2['ambushBeats'], 1),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveAmbushBeat(phase2['ambushBeats'], 2),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertIsNone(
            rg.resolveAmbushBeat(phase2['ambushBeats'], 3))
        # Distinct from P1 / Silly STREET_PACKS tables.
        self.assertNotEqual(
            phase2['waveModifiers'], finale['waveModifiers'])
        self.assertNotEqual(
            phase2['ambushBeats'], finale['ambushBeats'])
        self.assertNotIn('overlordP2HpFrac', phase2)
        self.assertNotIn('overlordP2HpFrac', finale)
        # No cream / KH on the authored phase2 pressure block.
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        p2_idx = camp_src.index("'corruptName': 'Ink Overlord Unleashed'")
        p2_end = camp_src.index("'addName': 'Ink Smudge'", p2_idx) + 40
        p2_snip = camp_src[p2_idx:p2_end]
        self.assertIn("'waveModifiers'", p2_snip)
        self.assertIn("'ambushBeats'", p2_snip)
        self.assertIn("'addWaveStart'", p2_snip)
        # Key must stay omitted (comment may name the asymmetry).
        self.assertNotIn("'overlordP2HpFrac'", p2_snip)
        self.assertNotIn('overlordP2HpFrac:', p2_snip)
        p2_l = p2_snip.lower()
        self.assertNotIn('keyblade', p2_l)
        self.assertNotIn('kingdom hearts', p2_l)

    def test_director_ai_wires_elite_and_ambush(self):
        src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirectorAI.py')
        methods = _class_method_names(tree, 'DistributedReclaimDirectorAI')
        self.assertIn('_spawnAmbush', methods)
        self.assertIn('_scheduleAmbushIfNeeded', methods)
        self.assertIn('_applyEliteModifiers', methods)
        self.assertIn('announceAmbushSpawn', src)
        self.assertIn('waveModifiers=None', src)
        self.assertIn('ambushBeats=None', src)
        self.assertIn('applyElitePackHp', src)
        self.assertIn('applyWaveDamageMultToStats', src)
        self.assertIn('resolveAmbushBeat', src)
        # Campaign C start also forwards elite/ambush kwargs.
        camp_src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('waveModifiers=params.get(', camp_src)
        self.assertIn('ambushBeats=params.get(', camp_src)
        self.assertNotIn('overlordP2HpFrac=params.get', camp_src)
        # No KH / keyblade branding in director.
        self.assertNotIn('keyblade', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())
        self.assertNotIn('keyblade', camp_src.lower())
        self.assertNotIn('kingdom hearts', camp_src.lower())

    def test_client_and_dc_announce_ambush(self):
        client = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('def announceAmbushSpawn', client)
        self.assertIn('ambushOswaldTip', client)
        self.assertIn('reclaimAmbushSpawn', client)
        # Orphan messenger is accepted for mid-fight pressure tip.
        self.assertIn('__onAmbushSpawnCue', client)
        self.assertIn('ambushMsgName()', client)
        self.assertIn('ambushPressureTipText', client)
        dc = _read('etc/toon.dc')
        self.assertIn('announceAmbushSpawn(uint8, uint8) broadcast;', dc)

    def test_no_cream_deepen_in_feature_surfaces(self):
        """Elite/ambush feature must not ship cream FX deepen."""
        rg_src = _read('toontown/reclaim/ReclaimGlobals.py')
        # New constants block should not introduce cream wash tunables.
        elite_block = rg_src[rg_src.index('ELITE_HP_MULT'):rg_src.index(
            'AMBUSH_SUB_BANNER_COLOR') + 80]
        self.assertNotIn('cream', elite_block.lower())
        self.assertNotIn('sparkle', elite_block.lower())


if __name__ == '__main__':
    unittest.main()
