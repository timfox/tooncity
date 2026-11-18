#!/usr/bin/env python3
"""Headless tests: SECURED purity-lock survives AI restart.

Loads CorruptionGlobals / PollutionSecuredSave / CampaignProgressSave with a
ToontownGlobals stub (no Panda3D). Exercises district JSON round-trip,
manager hydrate→persist→rehydrate, and campaign securedZones mirror.

Run from repo root:
  python3 tests/test_secured_purity_lock_persist.py
  python3 -m unittest tests.test_secured_purity_lock_persist -v
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


class _FakeAir:
    def __init__(self, data_folder, district_id=7):
        self.dataFolder = data_folder if data_folder.endswith('/') else (
            data_folder + '/')
        self.districtId = district_id
        self.doId2do = {}
        self.pollutionManager = None
        self.campaignDirector = None


class _FakePollutionManager:
    """Panda-free stand-in mirroring PollutionManagerAI lock bookkeeping."""

    def __init__(self, air, secured_mod, cg):
        self.air = air
        self._secured = secured_mod
        self._cg = cg
        self.zonePollution = {}
        self.streetStatus = {}
        self._purityLocked = set()
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
        return self.zonePollution.get(int(zoneId), 0.0)

    def markStreetSecured(self, zoneId, persist=True):
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = self._cg.STREET_SECURED
        self._purityLocked.add(zoneId)
        self.zonePollution[zoneId] = 0.0
        if persist:
            self._persistSecuredLocks()

    def markStreetReclaiming(self, zoneId, persist=True):
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = self._cg.STREET_RECLAIMING
        self._purityLocked.discard(zoneId)
        if persist:
            self._persistSecuredLocks()

    def markStreetContested(self, zoneId, persist=True):
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = self._cg.STREET_CONTESTED
        self._purityLocked.discard(zoneId)
        if persist:
            self._persistSecuredLocks()

    def _hydrateSecuredLocks(self):
        if self._securedHydrated:
            return False
        blob = self._secured.loadSecured(self._securedPath())
        self._securedHydrated = True
        self._secured.applySecuredToManager(self, blob, mark=True)
        return bool(blob.get('securedZones'))

    def _persistSecuredLocks(self):
        blob = self._secured.snapshotFromManager(self)
        ok = self._secured.saveSecured(self._securedPath(), blob)
        if ok:
            self._securedHydrated = True
        return ok

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


class SecuredPurityLockPersistTest(unittest.TestCase):
    """Finished-reclaim purity locks survive AI process restart."""

    @classmethod
    def setUpClass(cls):
        cls.cg, cls.secured, cls.camp, cls.save = _load_panda_free_modules()

    def test_globals_enable_secured_persist_filename(self):
        cg = self.cg
        self.assertIs(cg.POLLUTION_SECURED_PERSIST_ENABLED, True)
        self.assertEqual(
            cg.POLLUTION_SECURED_FILENAME, 'pollution_secured.json')
        self.assertEqual(
            self.secured.SECURED_FILENAME, 'pollution_secured.json')

    def test_sanitize_and_json_round_trip(self):
        secured = self.secured
        blob = secured.sanitizeSecured({
            'securedZones': [PUNCHLINE, 'nope', LOOPY, LOOPY, -3, 0],
        })
        self.assertEqual(blob['securedZones'], [LOOPY, PUNCHLINE])
        with tempfile.TemporaryDirectory() as tmp:
            path = secured.securedPath(tmp, shard=9)
            self.assertTrue(path.endswith('9_pollution_secured.json'))
            self.assertTrue(secured.saveSecured(path, blob))
            loaded = secured.loadSecured(path)
            self.assertEqual(loaded['securedZones'], [LOOPY, PUNCHLINE])
            # Missing file → empty defaults (not crash).
            missing = secured.loadSecured(path + '.missing')
            self.assertEqual(missing['securedZones'], [])

    def test_manager_persist_survives_ai_restart(self):
        secured = self.secured
        cg = self.cg
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp, district_id=3)
            mgr = _FakePollutionManager(air, secured, cg)
            mgr.markStreetSecured(LOOPY)
            mgr.markStreetSecured(PUNCHLINE)
            self.assertTrue(mgr.isPurityLocked(LOOPY))
            self.assertTrue(mgr.isPurityLocked(PUNCHLINE))
            self.assertEqual(
                mgr.streetStatus[LOOPY], cg.STREET_SECURED)

            # Simulate AI restart: new manager, same dataFolder.
            air2 = _FakeAir(tmp, district_id=3)
            mgr2 = _FakePollutionManager(air2, secured, cg)
            self.assertFalse(mgr2.isPurityLocked(LOOPY))
            mgr2._hydrateSecuredLocks()
            self.assertTrue(mgr2.isPurityLocked(LOOPY))
            self.assertTrue(mgr2.isPurityLocked(PUNCHLINE))
            self.assertEqual(
                mgr2.streetStatus[LOOPY], cg.STREET_SECURED)
            # Locked street refuses re-stain semantics stay intact.
            self.assertTrue(
                cg.streetPurityLockBlocksRise(
                    mgr2.isPurityLocked(LOOPY), 0.55, 0.0))

    def test_reclaiming_drops_live_lock_but_file_tracks(self):
        secured = self.secured
        cg = self.cg
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp)
            mgr = _FakePollutionManager(air, secured, cg)
            mgr.markStreetSecured(LOOPY)
            mgr.markStreetReclaiming(LOOPY)
            self.assertFalse(mgr.isPurityLocked(LOOPY))
            self.assertEqual(
                mgr.streetStatus[LOOPY], cg.STREET_RECLAIMING)
            # District file no longer lists the zone (seed can land).
            disk = secured.loadSecured(mgr._securedPath())
            self.assertNotIn(LOOPY, disk['securedZones'])

    def test_contested_clears_lock_from_disk(self):
        secured = self.secured
        cg = self.cg
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp)
            mgr = _FakePollutionManager(air, secured, cg)
            mgr.markStreetSecured(LOOPY)
            mgr.markStreetContested(LOOPY)
            self.assertFalse(mgr.isPurityLocked(LOOPY))
            disk = secured.loadSecured(mgr._securedPath())
            self.assertNotIn(LOOPY, disk['securedZones'])

    def test_campaign_progress_secured_zones_field(self):
        save = self.save
        camp = self.camp
        # Fresh default includes securedZones.
        fresh = save.defaultProgress()
        self.assertEqual(fresh['securedZones'], [])
        # Explicit empty list is preserved (contested drop stays dropped).
        explicit = save.sanitizeProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'securedZones': [],
        })
        self.assertEqual(explicit['securedZones'], [])
        # Older blobs without the key migrate from unlocks.
        migrated = save.sanitizeProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'state': camp.STATE_ACTIVE,
        })
        self.assertIn(LOOPY, migrated['securedZones'])
        self.assertNotIn(PUNCHLINE, migrated['securedZones'])
        # Victory migrates all ACT streets.
        victory = save.sanitizeProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
        })
        for act in camp.ACTS:
            self.assertIn(int(act['zoneId']), victory['securedZones'])

    def test_campaign_hydrate_applies_secured_zones_to_pollution(self):
        save = self.save
        secured = self.secured
        cg = self.cg
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp)
            mgr = _FakePollutionManager(air, secured, cg)
            path = save.progressPath(tmp, shard=air.districtId)
            progress = save.sanitizeProgress({
                'unlockedThrough': 1,
                'actIndex': 1,
                'reclaimCount': 1,
                'state': self.camp.STATE_ACTIVE,
                'securedZones': [LOOPY],
            })
            self.assertTrue(save.writeAvatar(path, 42, progress))
            loaded = save.readAvatar(path, 42)
            self.assertEqual(loaded['securedZones'], [LOOPY])
            # Campaign hydrate backup: apply blob locks onto fresh manager.
            mgr.applySecuredZones(loaded['securedZones'])
            self.assertTrue(mgr.isPurityLocked(LOOPY))
            # District file also flushed by applySecuredZones.
            disk = secured.loadSecured(mgr._securedPath())
            self.assertIn(LOOPY, disk['securedZones'])

    def test_pollution_manager_ai_persist_hooks(self):
        tree = _module_ast('toontown/corruption/PollutionManagerAI.py')
        methods = _class_method_names(tree, 'PollutionManagerAI')
        for name in (
                'generate',
                '_hydrateSecuredLocks',
                '_persistSecuredLocks',
                'applySecuredZones',
                'markStreetSecured',
                'markStreetReclaiming',
                'markStreetContested'):
            self.assertIn(name, methods, msg='missing %s' % name)
        src = _read('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('PollutionSecuredSave', src)
        self.assertIn('_hydrateSecuredLocks', src)
        self.assertIn('_persistSecuredLocks', src)
        self.assertIn('persist=False', src)
        # delete flushes before clearing memory.
        delete_idx = src.find('def delete(self):')
        self.assertGreater(delete_idx, 0)
        delete_snip = src[delete_idx:delete_idx + 500]
        self.assertIn('_persistSecuredLocks', delete_snip)

    def test_campaign_director_applies_secured_on_hydrate(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('securedZones', src)
        self.assertIn('_applySecuredZonesToPollution', src)
        hydrate_idx = src.find('def _hydrateFromToon')
        self.assertGreater(hydrate_idx, 0)
        hydrate_snip = src[hydrate_idx:hydrate_idx + 2200]
        self.assertIn('_applySecuredZonesToPollution', hydrate_snip)

    def test_no_kh_branding(self):
        for rel in (
                'toontown/corruption/PollutionSecuredSave.py',
                'toontown/corruption/PollutionManagerAI.py',
                'toontown/campaign/CampaignProgressSave.py'):
            lowered = _read(rel).lower()
            for banned in ('keyblade', 'kingdom hearts', 'key blade'):
                self.assertNotIn(banned, lowered, msg=rel)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SecuredPurityLockPersistTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
