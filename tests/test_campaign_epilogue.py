#!/usr/bin/env python3
"""Headless/AST tests: campaign epilogue after chase clear + hub victory tip.

Loads CampaignGlobals / CampaignProgressSave with a ToontownGlobals stub —
no Panda3D. Asserts epilogue copy, chaseCleared persist, hub victory tip,
and client accept wiring (OswaldBetrayalChase / CampaignHandoff / PlayEntry).
Does not regress betrayal kit (#322) or presence stub (#321).

Run from repo root:
  python3 tests/test_campaign_epilogue.py
  python3 -m unittest tests.test_campaign_epilogue -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

LOOPY = 2200
PUNCHLINE = 2300
SILLY = 2100
TTC = 2000


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_modules():
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
    tg.ToontownCentral = TTC
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

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp

    save_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignProgressSave.py'
    save_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignProgressSave', save_path)
    save = importlib.util.module_from_spec(save_spec)
    assert save_spec.loader is not None
    sys.modules['toontown.campaign.CampaignProgressSave'] = save
    save_spec.loader.exec_module(save)
    return camp, save, cg


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


class CampaignEpilogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save, cls.cfg = _load_panda_free_modules()

    def test_epilogue_globals_authored(self):
        camp = self.camp
        self.assertTrue(camp.CAMPAIGN_EPILOGUE_ENABLED)
        self.assertTrue(camp.CAMPAIGN_EPILOGUE_TITLE)
        self.assertIn('Oswald', camp.CAMPAIGN_EPILOGUE_SUB)
        self.assertIn('Replay', camp.CAMPAIGN_EPILOGUE_CUE)
        self.assertIn('Loopy', camp.CAMPAIGN_EPILOGUE_CUE)
        self.assertGreater(float(camp.CAMPAIGN_EPILOGUE_HOLD_SEC), 0.0)
        self.assertIn('stain is washed', camp.HUB_VICTORY_TIP.lower())
        self.assertIn('C campaign', camp.HUB_VICTORY_TIP)
        # Generic hub tip still invites Loopy for fresh runs.
        self.assertIn('Loopy', camp.HUB_TIP)
        blob = ' '.join([
            camp.CAMPAIGN_EPILOGUE_TITLE,
            camp.CAMPAIGN_EPILOGUE_SUB,
            camp.CAMPAIGN_EPILOGUE_CUE,
            camp.HUB_VICTORY_TIP,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, blob)

    def test_hub_play_entry_tip_victory_branch(self):
        camp = self.camp
        fresh = camp.hubPlayEntryTip()
        self.assertIn('Loopy', fresh)
        self.assertNotIn('Campaign complete', fresh)
        victory = camp.hubPlayEntryTip(victory=True)
        self.assertEqual(victory, camp.hubVictoryReplayTip())
        self.assertIn('Campaign complete', victory)
        self.assertIn('Loopy', victory)
        # Explicit nextStreet still works when not victory.
        punch = camp.hubPlayEntryTip(nextStreet='Punchline Place')
        self.assertIn('Punchline Place', punch)

    def test_chase_cleared_persists_across_relog(self):
        save = self.save
        with tempfile.TemporaryDirectory() as tmp:
            path = save.progressPath(tmp, shard=9)
            av_id = 4242
            progress = save.sanitizeProgress({
                'unlockedThrough': 2,
                'actIndex': 2,
                'reclaimCount': 3,
                'state': self.camp.STATE_VICTORY,
                'finalePhase': 0,
                'chaseCleared': 1,
            })
            self.assertEqual(progress['chaseCleared'], 1)
            self.assertTrue(save.writeAvatar(path, av_id, progress))
            loaded = save.readAvatar(path, av_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded['state'], self.camp.STATE_VICTORY)
            self.assertEqual(loaded['chaseCleared'], 1)
            # Defaults omit chase clear.
            fresh = save.defaultProgress()
            self.assertEqual(fresh['chaseCleared'], 0)

    def test_snapshot_apply_round_trips_chase_cleared(self):
        save = self.save
        director = types.SimpleNamespace(
            unlockedThrough=2,
            actIndex=2,
            reclaimCount=4,
            state=self.camp.STATE_VICTORY,
            _finalePhase=0,
            chaseCleared=1,
        )
        blob = save.snapshotFromDirector(director)
        self.assertEqual(blob['chaseCleared'], 1)
        target = types.SimpleNamespace()
        save.applyProgressToDirector(target, blob)
        self.assertEqual(target.chaseCleared, 1)
        self.assertEqual(target.state, self.camp.STATE_VICTORY)

    def test_chase_module_epilogue_surface(self):
        rel = 'toontown/campaign/OswaldBetrayalChase.py'
        names = _module_names(rel)
        for required in (
                'epilogueEnabled',
                'epilogueTitle',
                'epilogueSub',
                'epilogueCue',
                'chaseAttackMove',  # #322 kit must stay
                'spawnCorruptOswald',
                'OswaldBetrayalChaseClient'):
            self.assertIn(required, names)
        src = _read(rel)
        self.assertIn('oswaldBetrayalChaseCleared', src)
        self.assertIn('campaignEpilogue', src)
        self.assertIn('_startChaseWatch', src)
        self.assertIn('_fireEpilogue', src)
        # Betrayal kit pin at spawn must remain.
        self.assertIn("corrupt._stats['attackMove']", src)
        self.assertNotIn('kingdom hearts', src.lower())
        self.assertNotIn('sora', src.lower())

    def test_handoff_and_playentry_accept_chase_clear(self):
        handoff = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn("accept('oswaldBetrayalChaseCleared'", handoff)
        self.assertIn("accept('campaignEpilogue'", handoff)
        self.assertIn('_showEpilogueHandoff', handoff)
        self.assertIn('CAMPAIGN_EPILOGUE', handoff)

        play = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('_victoryEpilogue', play)
        self.assertIn('_onCampaignEpilogue', play)
        self.assertIn("victory=True", play)
        self.assertIn('hubVictoryReplayTip', play)
        # Presence stub wiring must remain.
        self.assertIn('ensureOswaldPresenceClient', play)

    def test_director_chase_clear_persists_and_epilogue(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('chaseCleared', src)
        watch_idx = src.find('def __watchOswaldBetrayalChase')
        self.assertGreater(watch_idx, 0)
        window = src[watch_idx:watch_idx + 1600]
        self.assertIn('self.chaseCleared = 1', window)
        self.assertIn('_persistForToon', window)
        self.assertIn('oswaldBetrayalChaseCleared', window)
        self.assertIn('campaignEpilogue', window)
        # Replay wipe clears chaseCleared only after chase is already done.
        start_idx = src.find('def startCampaign')
        start_win = src[start_idx:start_idx + 1400]
        self.assertIn('_resumePendingOswaldBetrayalChase', start_win)
        self.assertIn('self.chaseCleared = 0', start_win)
        # Hydrate must re-schedule pending chase after relog.
        hydrate_idx = src.find('def _hydrateFromToon')
        hydrate_win = src[hydrate_idx:hydrate_idx + 1600]
        self.assertIn('_resumePendingOswaldBetrayalChase', hydrate_win)

    def test_presence_stub_and_betrayal_kit_untouched_markers(self):
        # Presence (#321) still present.
        self.assertTrue(self.camp.OSWALD_PRESENCE_ENABLED)
        presence = REPO_ROOT / 'toontown' / 'campaign' / 'OswaldPresence.py'
        self.assertTrue(presence.exists())
        # Betrayal kit (#322) still on Corrupted Oswald stats.
        stats = self.cfg.archetypeStats(self.cfg.ARCHETYPE_CORRUPT_OSWALD)
        self.assertEqual(stats.get('attackMove'), 'betrayal_lunge')
        self.assertTrue(self.cfg.OSWALD_BETRAYAL_KIT_ENABLED)


if __name__ == '__main__':
    unittest.main()
