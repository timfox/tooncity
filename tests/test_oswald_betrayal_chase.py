#!/usr/bin/env python3
"""Headless/AST tests: short corrupted-Oswald chase after finale betrayal.

Loads CampaignGlobals / CorruptionGlobals / ReclaimGlobals with a
ToontownGlobals stub — no Panda3D. Chase module + director wiring are
AST-checked (client/AI imports pull panda / DistributedObject).

Run from repo root:
  python3 tests/test_oswald_betrayal_chase.py
  python3 -m unittest tests.test_oswald_betrayal_chase -v
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


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_globals():
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


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_names(rel: str) -> set[str]:
    tree = ast.parse(_read(rel))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


class OswaldBetrayalChaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.rg, cls.cfg = _load_panda_free_globals()

    def test_corrupt_oswald_archetype_registered(self):
        cfg = self.cfg
        aid = cfg.ARCHETYPE_CORRUPT_OSWALD
        self.assertEqual(aid, 4)
        self.assertEqual(cfg.ARCHETYPE_NAMES[aid], 'Corrupted Oswald')
        self.assertEqual(cfg.archetypeDefaultName(aid), 'Corrupted Oswald')
        stats = cfg.ARCHETYPE_STATS[aid]
        self.assertGreater(float(stats['chaseSpeed']), 10.0)
        self.assertGreater(float(stats['hpScale']), 1.0)
        self.assertGreater(int(stats.get('defaultHp', 0)), 0)
        tint = stats['actorTint']
        # Crimson-shadow: R dominant over B (vs street purple ink).
        self.assertGreater(float(tint[0]), float(tint[2]))
        self.assertEqual(cfg.normalizeArchetype(aid), aid)
        self.assertEqual(cfg.normalizeArchetype(99), cfg.ARCHETYPE_INK)

    def test_corrupt_oswald_looks_present(self):
        cfg = self.cfg
        aid = cfg.ARCHETYPE_CORRUPT_OSWALD
        self.assertIn(aid, cfg.TELEGRAPH_INK_DRIP_LOOK)
        self.assertIn(aid, cfg.IDLE_INK_DRIP_LOOK)
        self.assertIn(aid, cfg.DEATH_POP_LOOK)
        self.assertIn('betrayal', cfg.TELEGRAPH_INK_DRIP_LOOK[aid]['id'])
        self.assertIn('betrayal', cfg.DEATH_POP_LOOK[aid]['id'])

    def test_wave_script_token_oswald(self):
        self.assertEqual(self.rg.WAVE_SCRIPT_TOKENS.get('oswald'), 4)
        self.assertEqual(
            self.rg.WAVE_SCRIPT_TOKENS.get('corrupted_oswald'), 4)
        resolved = self.rg.resolveWaveScript((('oswald',),), 1)
        self.assertEqual(resolved, [self.cfg.ARCHETYPE_CORRUPT_OSWALD])

    def test_campaign_chase_tunables(self):
        camp = self.camp
        self.assertTrue(camp.OSWALD_BETRAYAL_CHASE_ENABLED)
        self.assertGreater(float(camp.OSWALD_BETRAYAL_CHASE_DELAY_SEC), 0.0)
        self.assertGreaterEqual(
            float(camp.OSWALD_BETRAYAL_CHASE_DELAY_SEC),
            float(camp.FINALE_REVEAL_DELAY_SEC))
        self.assertIn('Oswald', camp.OSWALD_BETRAYAL_CHASE_TIP)
        self.assertIn('fight', camp.OSWALD_BETRAYAL_CHASE_TIP.lower())
        self.assertIn('Corrupted Oswald', camp.OSWALD_BETRAYAL_CHASE_NAME)
        self.assertIn('chase', camp.OSWALD_BETRAYAL_CHASE_BANNER.lower())
        blob = ' '.join([
            camp.OSWALD_BETRAYAL_CHASE_TIP,
            camp.OSWALD_BETRAYAL_CHASE_BANNER,
            camp.OSWALD_BETRAYAL_CHASE_MSG,
            camp.OSWALD_BETRAYAL_CHASE_CLEAR_MSG,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, blob)

    def test_chase_helper_defaults_match_globals(self):
        camp = self.camp
        cfg = self.cfg
        # Mirror OswaldBetrayalChase.chaseHp / chaseDelay without importing
        # the panda-bound module.
        delay = float(camp.OSWALD_BETRAYAL_CHASE_DELAY_SEC)
        self.assertGreater(delay, 0.0)
        hp = int(camp.OSWALD_BETRAYAL_CHASE_HP or 0)
        if hp <= 0:
            hp = cfg.archetypeDefaultHp(cfg.ARCHETYPE_CORRUPT_OSWALD)
        self.assertGreater(hp, 0)
        self.assertEqual(
            camp.OSWALD_BETRAYAL_CHASE_NAME,
            cfg.ARCHETYPE_NAMES[cfg.ARCHETYPE_CORRUPT_OSWALD])

    def test_director_schedules_chase_after_finale(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('_scheduleOswaldBetrayalChase', src)
        self.assertIn('spawnCorruptOswald', src)
        self.assertIn('oswaldBetrayalChase', src)
        self.assertIn('_cancelOswaldBetrayalChase', src)
        # Pin the finale victory branch (not statusText's finale phase note).
        marker = "messenger.send('campaignVictory'"
        victory_idx = src.find(marker)
        self.assertGreater(victory_idx, 0)
        # Schedule call should sit near the first campaignVictory send.
        window = src[max(0, victory_idx - 200):victory_idx + 220]
        self.assertIn('STATE_VICTORY', window)
        self.assertIn('_scheduleOswaldBetrayalChase', window)

    def test_chase_module_ast_surface(self):
        rel = 'toontown/campaign/OswaldBetrayalChase.py'
        names = _module_names(rel)
        for required in (
                'spawnCorruptOswald',
                'OswaldBetrayalChaseClient',
                'ensureOswaldBetrayalChaseClient',
                'chaseEnabled',
                'chaseDelaySec',
                'chaseHp'):
            self.assertIn(required, names)
        src = _read(rel)
        self.assertIn('ARCHETYPE_CORRUPT_OSWALD', src)
        self.assertIn('oswaldRevealBanner', src)
        self.assertIn('campaignVictory', src)
        self.assertIn('enableHackSlashMelee', src)
        # Doc may say "no keyblades"; ban affirmative KH product copy only.
        self.assertNotIn('kingdom hearts', src.lower())
        self.assertNotIn('sora', src.lower())

    def test_client_wiring(self):
        finale_src = _read('toontown/campaign/FinalePhaseFx.py')
        self.assertIn('ensureOswaldBetrayalChaseClient', finale_src)
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('ensureOswaldBetrayalChaseClient', play_src)

    def test_magic_words_and_docs(self):
        magic = _read('toontown/corruption/MagicWords.py')
        self.assertIn('SpawnCorruptOswald', magic)
        self.assertIn('ARCHETYPE_CORRUPT_OSWALD', magic)
        self.assertIn('spawncorruptedoswald', magic.lower())
        camp_magic = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('corrupted oswald chase', camp_magic)
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('corrupted oswald', reclaim)
        self.assertIn('oswald_betrayal_chase', reclaim)

    def test_finale_act_still_has_betrayal_handoff(self):
        finale = None
        for act in self.camp.ACTS:
            if act.get('finale'):
                finale = act
                break
        self.assertIsNotNone(finale)
        self.assertTrue(finale.get('betrayalHandoff'))


if __name__ == '__main__':
    unittest.main()
