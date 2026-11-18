#!/usr/bin/env python3
"""Headless tests: hub stain beat after Oswald betrayal.

After finale victory (chase pending), TTC HUB_ZONE receives authored
pollution fog and/or a confront placemarker — not a pristine sunny hub.
Chase clear / replay wipe washes the hub. Loads CampaignGlobals with a
ToontownGlobals stub — no Panda3D. HubStain pure helpers run live;
director / PollutionManagerAI / confront wiring are AST-pinned.

Run from repo root:
  python3 tests/test_hub_stain_after_betrayal.py
  python3 -m unittest tests.test_hub_stain_after_betrayal -v
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

    stain_path = REPO_ROOT / 'toontown' / 'campaign' / 'HubStain.py'
    stain_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.HubStain', stain_path)
    stain = importlib.util.module_from_spec(stain_spec)
    assert stain_spec.loader is not None
    sys.modules['toontown.campaign.HubStain'] = stain
    stain_spec.loader.exec_module(stain)
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


class _FakePollutionMgr:
    """Minimal PollutionManagerAI stand-in for HubStain apply/clear."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.zonePollution = {}
        self.streetStatus = {}
        self._purityLocked = set()
        self._recreepAnnounced = set()
        self.applied = []
        self.cleared = []

    def getPollution(self, zoneId):
        return self.zonePollution.get(
            int(zoneId), self.cfg.POLLUTION_DEFAULT)

    def setPollution(self, zoneId, level):
        zoneId = int(zoneId)
        clamped = self.cfg.clampPollution(level)
        previous = self.getPollution(zoneId)
        if self.cfg.streetPurityLockBlocksRise(
                zoneId in self._purityLocked, clamped, previous):
            return previous
        self.zonePollution[zoneId] = clamped
        if clamped <= self.cfg.POLLUTION_PURE and previous > self.cfg.POLLUTION_PURE:
            self.markStreetSecured(zoneId)
        return clamped

    def markStreetSecured(self, zoneId):
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = self.cfg.STREET_SECURED
        self._purityLocked.add(zoneId)
        self.zonePollution[zoneId] = self.cfg.POLLUTION_PURE

    def applyBetrayalHubStain(self, zoneId, level):
        zoneId = int(zoneId)
        self._purityLocked.discard(zoneId)
        self.streetStatus[zoneId] = self.cfg.STREET_SECURED
        applied = self.setPollution(zoneId, level)
        self.applied.append((zoneId, applied))
        return applied

    def clearBetrayalHubStain(self, zoneId):
        zoneId = int(zoneId)
        applied = self.setPollution(zoneId, self.cfg.POLLUTION_PURE)
        if zoneId not in self._purityLocked:
            self.markStreetSecured(zoneId)
        self.cleared.append(zoneId)
        return applied


class _FakeAir:
    def __init__(self, pollutionMgr):
        self.pollutionManager = pollutionMgr
        self.doId2do = {}


class HubStainAfterBetrayalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.stain, cls.cfg = _load_panda_free_modules()

    def test_hub_stain_globals_authored(self):
        camp = self.camp
        self.assertTrue(camp.HUB_STAIN_ENABLED)
        self.assertEqual(int(camp.HUB_ZONE), TTC)
        self.assertGreater(float(camp.HUB_STAIN_POLLUTION), 0.0)
        self.assertLess(float(camp.HUB_STAIN_POLLUTION), 0.75)
        self.assertIn('Toon Central', camp.HUB_STAIN_MSG)
        self.assertIn('stain', camp.HUB_STAIN_MSG.lower())
        self.assertTrue(camp.HUB_STAIN_CONFRONT_ENABLED)
        self.assertIn('Oswald', camp.HUB_STAIN_CONFRONT_LABEL)
        self.assertIn('plaza', camp.HUB_STAIN_CONFRONT_TIP.lower())
        blob = ' '.join([
            camp.HUB_STAIN_MSG,
            camp.HUB_STAIN_CLEAR_MSG,
            camp.HUB_STAIN_CONFRONT_LABEL,
            camp.HUB_STAIN_CONFRONT_TIP,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'kh '):
            self.assertNotIn(banned, blob)

    def test_hub_stain_wanted_gates(self):
        stain = self.stain
        camp = self.camp
        self.assertTrue(stain.hubStainWanted(camp.STATE_VICTORY, chaseCleared=0))
        self.assertFalse(stain.hubStainWanted(camp.STATE_VICTORY, chaseCleared=1))
        self.assertFalse(stain.hubStainWanted(camp.STATE_ACTIVE, chaseCleared=0))
        self.assertFalse(stain.hubStainWanted(camp.STATE_IDLE, chaseCleared=0))
        self.assertEqual(stain.hubStainZone(), TTC)
        self.assertAlmostEqual(
            stain.hubStainLevel(), float(camp.HUB_STAIN_POLLUTION), places=5)

    def test_apply_and_clear_hub_stain_via_pollution_mgr(self):
        stain = self.stain
        mgr = _FakePollutionMgr(self.cfg)
        air = _FakeAir(mgr)
        # Sunny hub can take the betrayal stain.
        applied = stain.applyHubStain(air)
        self.assertIsNotNone(applied)
        self.assertGreater(float(applied), 0.0)
        self.assertAlmostEqual(
            float(mgr.getPollution(TTC)), float(applied), places=5)
        self.assertEqual(mgr.applied[-1][0], TTC)
        # Purity lock must not block the authored hub stain.
        mgr._purityLocked.add(TTC)
        mgr.zonePollution[TTC] = 0.0
        applied2 = stain.applyHubStain(air, level=0.5)
        self.assertGreater(float(applied2), 0.0)
        # Chase clear / wash.
        cleared = stain.clearHubStain(air)
        self.assertEqual(float(cleared), 0.0)
        self.assertEqual(float(mgr.getPollution(TTC)), 0.0)
        self.assertIn(TTC, mgr.cleared)

    def test_sync_hub_stain_from_victory_state(self):
        stain = self.stain
        camp = self.camp
        mgr = _FakePollutionMgr(self.cfg)
        air = _FakeAir(mgr)
        told = []
        wanted = stain.syncHubStain(
            air, camp.STATE_VICTORY, chaseCleared=0,
            tellToon=told.append)
        self.assertTrue(wanted)
        self.assertGreater(float(mgr.getPollution(TTC)), 0.0)
        self.assertTrue(told)
        self.assertIn('stain', told[0].lower())
        # Chase washed — hub goes pure (no wash whisper in sync itself).
        wanted2 = stain.syncHubStain(
            air, camp.STATE_VICTORY, chaseCleared=1, tellToon=None)
        self.assertFalse(wanted2)
        self.assertEqual(float(mgr.getPollution(TTC)), 0.0)

    def test_hub_stain_module_exports(self):
        names = _module_names('toontown/campaign/HubStain.py')
        for need in (
                'hubStainEnabled', 'hubStainZone', 'hubStainLevel',
                'hubStainWanted', 'hubEpilogueBeatWanted', 'applyHubStain',
                'clearHubStain', 'syncHubStain'):
            self.assertIn(need, names)

    def test_director_wires_hub_stain_on_victory_and_clear(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('from toontown.campaign.HubStain import', src)
        self.assertIn('_syncHubStain', src)
        self.assertIn('clearHubStain', src)
        # Victory finale path stains hub before chase schedule.
        reclaim = src[src.find('def __onNeighborhoodReclaimed'):]
        self.assertIn('_syncHubStain', reclaim)
        self.assertIn('_scheduleOswaldBetrayalChase', reclaim)
        # Finale victory stains hub in the same branch as chase schedule.
        finale_at = reclaim.find("if act.get('finale'):")
        self.assertGreater(finale_at, 0)
        finale_snip = reclaim[finale_at:]
        schedule_at = finale_snip.find('_scheduleOswaldBetrayalChase')
        sync_at = finale_snip.find('_syncHubStain')
        victory_at = finale_snip.find("messenger.send('campaignVictory'")
        self.assertGreaterEqual(sync_at, 0)
        self.assertGreaterEqual(victory_at, 0)
        self.assertGreater(schedule_at, victory_at)
        self.assertGreater(sync_at, victory_at)
        # Chase clear washes hub.
        watch = src[src.find('def __watchOswaldBetrayalChase'):]
        watch = watch[:watch.find('def __onNeighborhoodReclaimed')]
        self.assertIn('self.chaseCleared = 1', watch)
        self.assertIn('_syncHubStain', watch)
        # Hydrate re-applies quietly after relog.
        hydrate = src[src.find('def _hydrateFromToon'):]
        hydrate = hydrate[:hydrate.find('def _persistForToon')]
        self.assertIn('_syncHubStain', hydrate)
        self.assertIn('tell=False', hydrate)
        # Replay wipe force-clears (state still VICTORY mid-wipe).
        start = src[src.find('def startCampaign'):]
        start = start[:start.find('def advanceCampaign')]
        self.assertIn('clearHubStain(self.air)', start)

    def test_pollution_mgr_betrayal_hub_helpers(self):
        src = _read('toontown/corruption/PollutionManagerAI.py')
        names = _module_names('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('applyBetrayalHubStain', names)
        self.assertIn('clearBetrayalHubStain', names)
        self.assertIn('applyBetrayalHubStain', src)
        self.assertIn('_purityLocked.discard', src)
        # Authored hub stain must not mark contested (no recreep on HQ).
        apply_snip = src[src.find('def applyBetrayalHubStain'):]
        apply_snip = apply_snip[:apply_snip.find('def clearBetrayalHubStain')]
        self.assertIn('STREET_SECURED', apply_snip)
        self.assertNotIn('STREET_CONTESTED', apply_snip)

    def test_confront_client_and_ttplayground_wiring(self):
        names = _module_names('toontown/campaign/HubStainConfront.py')
        for need in (
                'HubStainConfrontClient', 'confrontEnabled', 'confrontLabel',
                'refreshHubStainConfront', 'stopHubStainConfront',
                'ensureHubStainConfrontClient'):
            self.assertIn(need, names)
        confront_src = _read('toontown/campaign/HubStainConfront.py')
        self.assertIn('hubStainConfrontLabel', confront_src)
        self.assertIn('pollutionChanged', confront_src)
        self.assertIn('hubStainApplied', confront_src)
        # No KH / cream deepen hooks.
        low = confront_src.lower()
        for banned in ('keyblade', 'kingdom hearts', 'cream wash', 'cream hose'):
            self.assertNotIn(banned, low)
        tt = _read('toontown/safezone/TTPlayground.py')
        self.assertIn('refreshHubStainConfront', tt)
        self.assertIn('stopHubStainConfront', tt)
        # OswaldPresence wiring remains (do not regress trusted stub).
        self.assertIn('refreshOswaldPresenceHub', tt)

    def test_hub_stain_helpers_skip_when_disabled(self):
        stain = self.stain
        camp = self.camp
        mgr = _FakePollutionMgr(self.cfg)
        air = _FakeAir(mgr)
        prev = camp.HUB_STAIN_ENABLED
        try:
            camp.HUB_STAIN_ENABLED = False
            self.assertFalse(stain.hubStainWanted(camp.STATE_VICTORY, 0))
            self.assertIsNone(stain.applyHubStain(air))
            self.assertEqual(mgr.applied, [])
        finally:
            camp.HUB_STAIN_ENABLED = prev


if __name__ == '__main__':
    unittest.main()
