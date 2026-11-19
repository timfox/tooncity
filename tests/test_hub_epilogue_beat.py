#!/usr/bin/env python3
"""Headless tests: epilogue hub-return beat after stain wash.

After chase clear, TTC washed-plaza gets an authored world placemarker
beyond HUD epilogue plate + HUB_VICTORY_TIP. Loads CampaignGlobals with a
ToontownGlobals stub — no Panda3D. HubEpilogueBeat pure helpers run live;
confront / handoff / PlayEntry / TTPlayground wiring are AST-pinned.

Run from repo root:
  python3 tests/test_hub_epilogue_beat.py
  python3 -m unittest tests.test_hub_epilogue_beat -v
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

    # HubStain is a dependency of HubEpilogueBeat (hubStainZone) — load pure.
    stain_path = REPO_ROOT / 'toontown' / 'campaign' / 'HubStain.py'
    stain_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.HubStain', stain_path)
    stain = importlib.util.module_from_spec(stain_spec)
    assert stain_spec.loader is not None
    sys.modules['toontown.campaign.HubStain'] = stain
    stain_spec.loader.exec_module(stain)

    # HubEpilogueBeat imports panda3d / DirectObject — load helpers only via
    # AST for client class; execute a thin stub of the wanted gate by
    # re-implementing from source constants (camp) + AST pin of the module.
    return camp, stain, cg


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


class HubEpilogueBeatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.stain, cls.cfg = _load_panda_free_modules()

    def test_epilogue_beat_globals_authored(self):
        camp = self.camp
        self.assertTrue(camp.HUB_EPILOGUE_BEAT_ENABLED)
        self.assertTrue(camp.CAMPAIGN_EPILOGUE_ENABLED)
        self.assertIn('washed', camp.HUB_EPILOGUE_BEAT_LABEL.lower())
        self.assertIn('Oswald', camp.HUB_EPILOGUE_BEAT_ABSENCE)
        self.assertIn('plaza', camp.HUB_EPILOGUE_BEAT_TIP.lower())
        self.assertIn('absence', camp.HUB_EPILOGUE_BEAT_TIP.lower())
        self.assertIn('Loopy', camp.HUB_EPILOGUE_BEAT_TIP)
        self.assertGreater(float(camp.HUB_EPILOGUE_BEAT_FORWARD), 0.0)
        # Distinct from pending-stain confront copy.
        self.assertNotEqual(
            camp.HUB_EPILOGUE_BEAT_LABEL, camp.HUB_STAIN_CONFRONT_LABEL)
        self.assertNotIn(
            'wash the betrayal chase', camp.HUB_EPILOGUE_BEAT_TIP.lower())
        blob = ' '.join([
            camp.HUB_EPILOGUE_BEAT_LABEL,
            camp.HUB_EPILOGUE_BEAT_ABSENCE,
            camp.HUB_EPILOGUE_BEAT_TIP,
        ]).lower()
        for banned in (
                'keyblade', 'kingdom hearts', 'sora', 'kh ',
                'cream wash', 'cream hose'):
            self.assertNotIn(banned, blob)

    def test_hub_epilogue_beat_wanted_gates(self):
        camp = self.camp
        stain = self.stain
        # Complementary to hubStainWanted: pending stains; cleared beats.
        self.assertTrue(stain.hubStainWanted(camp.STATE_VICTORY, chaseCleared=0))
        self.assertFalse(
            stain.hubEpilogueBeatWanted(camp.STATE_VICTORY, chaseCleared=0))
        self.assertFalse(stain.hubStainWanted(camp.STATE_VICTORY, chaseCleared=1))
        self.assertTrue(
            stain.hubEpilogueBeatWanted(camp.STATE_VICTORY, chaseCleared=1))
        self.assertFalse(
            stain.hubEpilogueBeatWanted(camp.STATE_ACTIVE, chaseCleared=1))
        self.assertFalse(
            stain.hubEpilogueBeatWanted(camp.STATE_IDLE, chaseCleared=0))
        prev = camp.HUB_EPILOGUE_BEAT_ENABLED
        try:
            camp.HUB_EPILOGUE_BEAT_ENABLED = False
            self.assertFalse(
                stain.hubEpilogueBeatWanted(camp.STATE_VICTORY, chaseCleared=1))
        finally:
            camp.HUB_EPILOGUE_BEAT_ENABLED = prev

    def test_epilogue_beat_module_exports(self):
        names = _module_names('toontown/campaign/HubEpilogueBeat.py')
        for need in (
                'HubEpilogueBeatClient', 'epilogueBeatEnabled',
                'epilogueBeatLabel', 'epilogueBeatAbsence', 'epilogueBeatTip',
                'epilogueBeatPlazaPos', 'epilogueBeatForward',
                'ensureHubEpilogueBeatClient', 'refreshHubEpilogueBeat',
                'clearHubEpilogueBeat', 'stopHubEpilogueBeat'):
            self.assertIn(need, names)
        # Pure gate lives on HubStain (panda-free) and is re-exported.
        stain_names = _module_names('toontown/campaign/HubStain.py')
        self.assertIn('hubEpilogueBeatWanted', stain_names)
        src = _read('toontown/campaign/HubEpilogueBeat.py')
        self.assertIn('hubEpilogueBeatWanted', src)
        self.assertIn('hubEpilogueBeatLabel', src)
        self.assertIn('hubEpilogueBeatAbsence', src)
        self.assertIn('hubEpilogueBeatShown', src)
        self.assertIn('HUB_EPILOGUE_BEAT_SHOWN_MSG', src)
        self.assertIn('ensurePlayEntryClient', src)
        self.assertIn('ensureOswaldPresenceClient', src)
        self.assertIn('hubStainCleared', src)
        self.assertIn('oswaldBetrayalChaseCleared', src)
        self.assertIn('campaignEpilogue', src)
        self.assertIn('campaignProgressSync', src)
        # No cream / KH deepen.
        low = src.lower()
        for banned in ('keyblade', 'kingdom hearts', 'cream wash', 'cream hose'):
            self.assertNotIn(banned, low)
        # Orphan → accept surface.
        self.assertEqual(
            self.camp.HUB_EPILOGUE_BEAT_SHOWN_MSG, 'hubEpilogueBeatShown')
        self.assertTrue(self.camp.HUB_EPILOGUE_BEAT_TIP_LATCH_ENABLED)

    def test_ttplayground_and_client_wiring(self):
        tt = _read('toontown/safezone/TTPlayground.py')
        self.assertIn('refreshHubEpilogueBeat', tt)
        self.assertIn('stopHubEpilogueBeat', tt)
        # Do not regress confront / presence mounts.
        self.assertIn('refreshHubStainConfront', tt)
        self.assertIn('stopHubStainConfront', tt)
        self.assertIn('refreshOswaldPresenceHub', tt)

        handoff = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('_refreshHubEpilogueBeat', handoff)
        self.assertIn('refreshHubEpilogueBeat', handoff)
        # Epilogue plate path still present.
        self.assertIn('_showEpilogueHandoff', handoff)

        play = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('ensureHubEpilogueBeatClient', play)
        self.assertIn('refreshHubEpilogueBeat', play)
        self.assertIn('clearHubEpilogueBeat', play)
        self.assertIn('_onCampaignEpilogue', play)
        self.assertIn('_onHubEpilogueBeatShown', play)
        self.assertIn('hubEpilogueBeatShown', play)
        presence = _read('toontown/campaign/OswaldPresence.py')
        self.assertIn('_onHubEpilogueBeatShown', presence)
        self.assertIn('hubEpilogueBeatShown', presence)

    def test_hub_stain_clear_still_only_clears_confront(self):
        """Confront clears on wash; epilogue beat is a separate module."""
        confront = _read('toontown/campaign/HubStainConfront.py')
        self.assertIn('_onHubStainCleared', confront)
        self.assertIn('_clearMarker', confront)
        self.assertNotIn('HubEpilogueBeat', confront)
        self.assertNotIn('hubEpilogueBeat', confront)


if __name__ == '__main__':
    unittest.main()
