#!/usr/bin/env python3
"""Headless tests: hub tip while victory + chase still pending.

STATE_VICTORY with chaseCleared=0 must NOT show HUB_VICTORY_TIP claiming
Oswald's stain is washed — show HUB_CHASE_PENDING_TIP instead. After chase
clear, victory replay tip is allowed. Loads CampaignGlobals /
CampaignProgressSave with a ToontownGlobals stub — no Panda3D.

Run from repo root:
  python3 tests/test_hub_tip_chase_pending.py
  python3 -m unittest tests.test_hub_tip_chase_pending -v
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
TTC = 2000


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_modules():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, REPO_ROOT.as_posix())

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


class HubTipChasePendingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save, cls.cfg = _load_panda_free_modules()

    def test_chase_pending_tip_authored(self):
        camp = self.camp
        tip = camp.HUB_CHASE_PENDING_TIP
        self.assertTrue(tip)
        self.assertIn('Oswald', tip)
        self.assertIn('betrayal chase', tip.lower())
        self.assertIn('C campaign', tip)
        # Must not claim stain washed early.
        self.assertNotIn('stain is washed', tip.lower())
        self.assertNotIn('Campaign complete', tip)
        blob = ' '.join([
            tip,
            camp.HUB_VICTORY_TIP,
            camp.HUB_TIP,
            camp.HUB_STAIN_CONFRONT_TIP,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, blob)

    def test_hub_play_entry_tip_chase_pending_branch(self):
        camp = self.camp
        pending = camp.hubPlayEntryTip(victory=True, chasePending=True)
        self.assertEqual(pending, camp.hubChasePendingTip())
        self.assertEqual(pending, camp.HUB_CHASE_PENDING_TIP)
        self.assertIn('betrayal chase', pending.lower())
        self.assertNotIn('stain is washed', pending.lower())
        self.assertNotIn('Campaign complete', pending)

        cleared = camp.hubPlayEntryTip(victory=True, chasePending=False)
        self.assertEqual(cleared, camp.hubVictoryReplayTip())
        self.assertIn('stain is washed', cleared.lower())
        self.assertIn('Campaign complete', cleared)

        # Victory alone (legacy callers) still means washed / cleared tip.
        legacy = camp.hubPlayEntryTip(victory=True)
        self.assertEqual(legacy, camp.hubVictoryReplayTip())

        fresh = camp.hubPlayEntryTip()
        self.assertIn('Loopy', fresh)
        self.assertNotIn('betrayal chase', fresh.lower())

    def test_client_mirror_drives_tip_honesty(self):
        save, camp = self.save, self.camp
        pending_mirror = save.clientMirrorFromProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
            'chaseCleared': 0,
        })
        self.assertTrue(pending_mirror['victoryEpilogue'])
        self.assertTrue(pending_mirror['chasePending'])
        tip = camp.hubPlayEntryTip(
            victory=pending_mirror['victoryEpilogue'],
            chasePending=pending_mirror['chasePending'])
        self.assertEqual(tip, camp.HUB_CHASE_PENDING_TIP)
        self.assertNotIn('stain is washed', tip.lower())

        cleared_mirror = save.clientMirrorFromProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
            'chaseCleared': 1,
        })
        self.assertTrue(cleared_mirror['victoryEpilogue'])
        self.assertFalse(cleared_mirror['chasePending'])
        washed = camp.hubPlayEntryTip(
            victory=cleared_mirror['victoryEpilogue'],
            chasePending=cleared_mirror['chasePending'])
        self.assertEqual(washed, camp.HUB_VICTORY_TIP)
        self.assertIn('stain is washed', washed.lower())

    def test_playentry_latches_chase_pending(self):
        src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('self._chasePending', src)
        self.assertIn("mirror.get('chasePending')", src)
        self.assertIn('chasePending=bool(self._chasePending)', src)
        # Live victory before chase clear marks pending; epilogue clears it.
        victory_idx = src.find('def _onCampaignVictory')
        self.assertGreater(victory_idx, 0)
        victory_win = src[victory_idx:victory_idx + 400]
        self.assertIn('self._chasePending = True', victory_win)
        epi_idx = src.find('def _onCampaignEpilogue')
        self.assertGreater(epi_idx, 0)
        epi_win = src[epi_idx:epi_idx + 500]
        self.assertIn('self._chasePending = False', epi_win)
        # Hub banner must not claim campaign complete while chase pending.
        show_idx = src.find('def _showHubTip')
        self.assertGreater(show_idx, 0)
        show_win = src[show_idx:show_idx + 1200]
        self.assertIn('self._chasePending', show_win)
        self.assertIn('wash the betrayal chase', show_win.lower())

    def test_globals_expose_chase_pending_helpers(self):
        camp = self.camp
        self.assertTrue(hasattr(camp, 'HUB_CHASE_PENDING_TIP'))
        self.assertTrue(callable(camp.hubChasePendingTip))
        self.assertTrue(callable(camp.hubPlayEntryTip))
        # Signature accepts chasePending kwarg.
        tip = camp.hubPlayEntryTip(chasePending=True, victory=True)
        self.assertEqual(tip, camp.hubChasePendingTip())


if __name__ == '__main__':
    unittest.main()
