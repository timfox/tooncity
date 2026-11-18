#!/usr/bin/env python3
"""Headless tests: hub-stain lock drop mirrors campaign securedZones.

#368 persist honesty edge: applyBetrayalHubStain discarded the district
purity lock + pollution_secured.json, but left CampaignProgressSave
securedZones listing TTC. Contested already mirrors secured=False; hub
stain must too so hydrate cannot reseal then rely on _syncHubStain.

No Panda3D / no cream / no KH.

Run from repo root:
  python3 tests/test_hub_stain_secured_zones_mirror.py
  python3 -m unittest tests.test_hub_stain_secured_zones_mirror -v
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
            'toontown.campaign'):
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

    secured_path = (
        REPO_ROOT / 'toontown' / 'corruption' / 'PollutionSecuredSave.py')
    secured_spec = importlib.util.spec_from_file_location(
        'toontown.corruption.PollutionSecuredSave', secured_path)
    secured = importlib.util.module_from_spec(secured_spec)
    assert secured_spec.loader is not None
    sys.modules['toontown.corruption.PollutionSecuredSave'] = secured
    secured_spec.loader.exec_module(secured)
    sys.modules['toontown.corruption'].PollutionSecuredSave = secured

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
    return cg, secured, camp, save


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


class _FakeNotify:
    def debug(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None


class _FakeCampaign:
    """Minimal CampaignDirectorAI stand-in for securedZones mirror."""

    def __init__(self, secured_zones=None):
        self.securedZones = list(secured_zones or [])
        self.persisted = 0

    def _persistForToon(self, toon=None):
        self.persisted += 1
        return True


class _FakeAir:
    def __init__(self, data_folder, district_id=7, campaign=None):
        self.dataFolder = data_folder if data_folder.endswith('/') else (
            data_folder + '/')
        self.districtId = district_id
        self.doId2do = {}
        self.pollutionManager = None
        self.campaignDirector = campaign


class _FakePollutionManager:
    """Panda-free stand-in with real mirror + hub-stain lock-drop semantics."""

    def __init__(self, air, secured_mod, cg):
        self.air = air
        self._secured = secured_mod
        self._cg = cg
        self.notify = _FakeNotify()
        self.zonePollution = {}
        self.streetStatus = {}
        self._purityLocked = set()
        self._recreepAnnounced = set()
        self._securedHydrated = False
        air.pollutionManager = self

    def _securedPersistEnabled(self):
        return True

    def _securedPath(self):
        return self._secured.securedPath(
            self.air.dataFolder, getattr(self.air, 'districtId', None))

    def isPurityLocked(self, zoneId):
        return int(zoneId) in self._purityLocked

    def getPollution(self, zoneId):
        return self.zonePollution.get(
            int(zoneId), self._cg.POLLUTION_DEFAULT)

    def setPollution(self, zoneId, level):
        zoneId = int(zoneId)
        clamped = self._cg.clampPollution(level)
        previous = self.getPollution(zoneId)
        if self._cg.streetPurityLockBlocksRise(
                self.isPurityLocked(zoneId), clamped, previous):
            return previous
        self.zonePollution[zoneId] = clamped
        if clamped <= self._cg.POLLUTION_PURE and previous > self._cg.POLLUTION_PURE:
            self.markStreetSecured(zoneId)
        return clamped

    def _persistSecuredLocks(self):
        blob = self._secured.snapshotFromManager(self)
        ok = self._secured.saveSecured(self._securedPath(), blob)
        if ok:
            self._securedHydrated = True
        return ok

    def _mirrorSecuredZoneToCampaign(self, zoneId, secured=True):
        """Mirrors PollutionManagerAI._mirrorSecuredZoneToCampaign."""
        campaign = getattr(self.air, 'campaignDirector', None)
        if campaign is None:
            return False
        zones = list(getattr(campaign, 'securedZones', None) or [])
        zoneId = int(zoneId)
        changed = False
        if secured:
            if zoneId not in zones:
                zones.append(zoneId)
                changed = True
        else:
            if zoneId in zones:
                zones = [z for z in zones if int(z) != zoneId]
                changed = True
        if not changed:
            campaign.securedZones = sorted(
                {int(z) for z in zones if int(z) > 0})
            return False
        campaign.securedZones = sorted(
            {int(z) for z in zones if int(z) > 0})
        persist = getattr(campaign, '_persistForToon', None)
        if callable(persist):
            try:
                persist()
            except Exception:
                return False
        return True

    def markStreetSecured(self, zoneId, persist=True):
        zoneId = int(zoneId)
        already = self.isPurityLocked(zoneId)
        self.streetStatus[zoneId] = self._cg.STREET_SECURED
        self._purityLocked.add(zoneId)
        self._recreepAnnounced.discard(zoneId)
        self.zonePollution[zoneId] = self._cg.POLLUTION_PURE
        if persist:
            self._persistSecuredLocks()
            if not already:
                self._mirrorSecuredZoneToCampaign(zoneId, secured=True)

    def markStreetContested(self, zoneId, persist=True):
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = self._cg.STREET_CONTESTED
        self._purityLocked.discard(zoneId)
        self._recreepAnnounced.discard(zoneId)
        if persist:
            self._persistSecuredLocks()
            self._mirrorSecuredZoneToCampaign(zoneId, secured=False)

    def applyBetrayalHubStain(self, zoneId, level):
        """Mirrors PollutionManagerAI.applyBetrayalHubStain lock-drop + mirror."""
        zoneId = int(zoneId)
        self._purityLocked.discard(zoneId)
        self.streetStatus[zoneId] = self._cg.STREET_SECURED
        self._recreepAnnounced.discard(zoneId)
        self._persistSecuredLocks()
        self._mirrorSecuredZoneToCampaign(zoneId, secured=False)
        return self.setPollution(zoneId, level)

    def applySecuredZones(self, zones, persist=True):
        applied = False
        for item in zones or []:
            zoneId = int(item)
            if self.isPurityLocked(zoneId):
                continue
            self.markStreetSecured(zoneId, persist=False)
            applied = True
        if applied and persist:
            self._persistSecuredLocks()
        return applied


class HubStainSecuredZonesMirrorTest(unittest.TestCase):
    """Hub stain drops campaign securedZones like contested does."""

    @classmethod
    def setUpClass(cls):
        cls.cg, cls.secured, cls.camp, cls.save = _load_panda_free_modules()

    def test_apply_betrayal_hub_stain_mirrors_false(self):
        src = _read('toontown/corruption/PollutionManagerAI.py')
        tree = _module_ast('toontown/corruption/PollutionManagerAI.py')
        methods = _class_method_names(tree, 'PollutionManagerAI')
        self.assertIn('applyBetrayalHubStain', methods)
        self.assertIn('_mirrorSecuredZoneToCampaign', methods)
        apply_snip = src[src.find('def applyBetrayalHubStain'):]
        apply_snip = apply_snip[:apply_snip.find('def clearBetrayalHubStain')]
        self.assertIn('_persistSecuredLocks', apply_snip)
        self.assertIn('_mirrorSecuredZoneToCampaign', apply_snip)
        self.assertIn('secured=False', apply_snip)
        # District file then campaign blob — same honesty order as contested.
        persist_at = apply_snip.find('_persistSecuredLocks')
        mirror_at = apply_snip.find('_mirrorSecuredZoneToCampaign')
        self.assertGreater(persist_at, 0)
        self.assertGreater(mirror_at, persist_at)
        # Still not contested (no recreep on HQ).
        self.assertIn('STREET_SECURED', apply_snip)
        self.assertNotIn('STREET_CONTESTED', apply_snip)
        # Contested parity — both lock-drop paths mirror secured=False.
        contested_snip = src[src.find('def markStreetContested'):]
        contested_snip = contested_snip[
            :contested_snip.find('def _anyContestedStreet')]
        self.assertIn('_mirrorSecuredZoneToCampaign', contested_snip)
        self.assertIn('secured=False', contested_snip)

    def test_hub_stain_drops_ttc_from_campaign_and_district(self):
        secured = self.secured
        cg = self.cg
        with tempfile.TemporaryDirectory() as tmp:
            campaign = _FakeCampaign(secured_zones=[TTC, LOOPY])
            air = _FakeAir(tmp, campaign=campaign)
            mgr = _FakePollutionManager(air, secured, cg)
            # Sunny wash / prior clear left TTC purity-locked + mirrored.
            mgr.markStreetSecured(TTC)
            mgr.markStreetSecured(LOOPY)
            self.assertTrue(mgr.isPurityLocked(TTC))
            self.assertEqual(sorted(campaign.securedZones), [TTC, LOOPY])
            disk = secured.loadSecured(mgr._securedPath())
            self.assertIn(TTC, disk['securedZones'])
            self.assertIn(LOOPY, disk['securedZones'])

            # Betrayal hub stain: district + campaign both drop TTC.
            level = float(self.camp.HUB_STAIN_POLLUTION)
            applied = mgr.applyBetrayalHubStain(TTC, level)
            self.assertAlmostEqual(float(applied), level, places=5)
            self.assertFalse(mgr.isPurityLocked(TTC))
            self.assertEqual(
                mgr.streetStatus[TTC], cg.STREET_SECURED)
            self.assertNotIn(TTC, campaign.securedZones)
            self.assertIn(LOOPY, campaign.securedZones)
            self.assertGreaterEqual(campaign.persisted, 1)
            disk2 = secured.loadSecured(mgr._securedPath())
            self.assertNotIn(TTC, disk2['securedZones'])
            self.assertIn(LOOPY, disk2['securedZones'])
            # Fog landed (lock no longer blocks the rise).
            self.assertAlmostEqual(
                float(mgr.getPollution(TTC)), level, places=5)

    def test_hydrate_after_hub_stain_does_not_reseal_ttc(self):
        """Blob honesty: after mirror-drop, campaign hydrate won't reseal TTC."""
        save = self.save
        secured = self.secured
        cg = self.cg
        with tempfile.TemporaryDirectory() as tmp:
            campaign = _FakeCampaign(secured_zones=[TTC, LOOPY])
            air = _FakeAir(tmp, campaign=campaign)
            mgr = _FakePollutionManager(air, secured, cg)
            mgr.markStreetSecured(TTC)
            mgr.markStreetSecured(LOOPY)
            mgr.applyBetrayalHubStain(TTC, float(self.camp.HUB_STAIN_POLLUTION))
            # Persist campaign blob as applyBetrayalHubStain's mirror would.
            progress = save.sanitizeProgress({
                'unlockedThrough': 2,
                'actIndex': 2,
                'state': self.camp.STATE_VICTORY,
                'chaseCleared': 0,
                'securedZones': list(campaign.securedZones),
            })
            self.assertNotIn(TTC, progress['securedZones'])
            self.assertIn(LOOPY, progress['securedZones'])
            path = save.progressPath(tmp, shard=air.districtId)
            self.assertTrue(save.writeAvatar(path, 7, progress))
            loaded = save.readAvatar(path, 7)
            # Fresh manager after AI restart / hydrate — TTC stays unlocked.
            air2 = _FakeAir(tmp, campaign=_FakeCampaign(
                secured_zones=list(loaded['securedZones'])))
            mgr2 = _FakePollutionManager(air2, secured, cg)
            mgr2.applySecuredZones(loaded['securedZones'])
            self.assertFalse(mgr2.isPurityLocked(TTC))
            self.assertTrue(mgr2.isPurityLocked(LOOPY))

    def test_director_hydrate_notes_hub_stain_mirror(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        hydrate = src[src.find('def _hydrateFromToon'):]
        hydrate = hydrate[:hydrate.find('def _applySecuredZonesToPollution')]
        self.assertIn('_applySecuredZonesToPollution', hydrate)
        self.assertIn('_syncHubStain', hydrate)
        self.assertIn('secured=False', hydrate)
        self.assertIn('securedZones', hydrate)

    def test_no_kh_branding(self):
        for rel in (
                'toontown/corruption/PollutionManagerAI.py',
                'toontown/campaign/CampaignDirectorAI.py'):
            lowered = _read(rel).lower()
            for banned in ('keyblade', 'kingdom hearts', 'key blade', 'sora'):
                self.assertNotIn(banned, lowered, msg=rel)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        HubStainSecuredZonesMirrorTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
