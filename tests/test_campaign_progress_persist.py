#!/usr/bin/env python3
"""Headless tests: campaign unlockedThrough persists across relog.

Loads CampaignGlobals + CampaignProgressSave with a ToontownGlobals stub
(no Panda3D). Exercises sanitize / JSON round-trip and a lightweight
director hydrate→persist→rehydrate loop (no Direct / Astron).

Run from repo root:
  python3 tests/test_campaign_progress_persist.py
  python3 -m unittest tests.test_campaign_progress_persist -v
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


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_campaign_progress():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = 2000
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

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
    return camp, save


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


class _FakeDirector:
    """Minimal stand-in for CampaignDirectorAI progress fields."""

    def __init__(self, air):
        self.air = air
        self.state = 0
        self.actIndex = 0
        self.reclaimCount = 0
        self.unlockedThrough = 0
        self._finalePhase = 0
        self.chaseCleared = 0
        self.chaseHp = 0
        self._lastToonId = None
        self._hydratedToonId = None

    # Mirror the real director helpers (panda-free copy for unit tests).
    def _progressEnabled(self):
        return True

    def _progressPath(self):
        return self._save.progressPath(
            self.air.dataFolder, getattr(self.air, 'districtId', None))

    def _hydrateFromToon(self, toon, save_mod):
        self._save = save_mod
        avId = getattr(toon, 'doId', None)
        if avId is None:
            return False
        if self._hydratedToonId == avId:
            return False
        if self._hydratedToonId is not None and self._hydratedToonId != avId:
            self._persistForAvatarId(self._hydratedToonId, save_mod)
        progress = save_mod.readAvatar(self._progressPath(), avId)
        self._hydratedToonId = avId
        if progress is None:
            progress = save_mod.defaultProgress()
        save_mod.applyProgressToDirector(self, progress)
        return True

    def _persistForAvatarId(self, avId, save_mod):
        self._save = save_mod
        if avId is None:
            return False
        blob = save_mod.snapshotFromDirector(self)
        ok = save_mod.writeAvatar(self._progressPath(), avId, blob)
        if ok:
            self._hydratedToonId = avId
        return ok


class CampaignProgressPersistTest(unittest.TestCase):
    """unlockedThrough survives logout via AI dataFolder JSON."""

    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save = _load_panda_free_campaign_progress()

    def test_globals_enable_progress_filename(self):
        camp = self.camp
        self.assertIs(camp.CAMPAIGN_PROGRESS_ENABLED, True)
        self.assertEqual(
            camp.CAMPAIGN_PROGRESS_FILENAME, 'campaign_progress.json')
        self.assertEqual(self.save.PROGRESS_FILENAME, 'campaign_progress.json')

    def test_sanitize_clamps_and_orders_act_vs_unlock(self):
        save = self.save
        blob = save.sanitizeProgress({
            'unlockedThrough': 99,
            'actIndex': 50,
            'reclaimCount': -3,
            'state': 9,
            'finalePhase': 4,
        })
        max_i = len(self.camp.ACTS) - 1
        self.assertEqual(blob['unlockedThrough'], max_i)
        self.assertEqual(blob['actIndex'], max_i)
        self.assertEqual(blob['reclaimCount'], 0)
        self.assertEqual(blob['state'], self.camp.STATE_VICTORY)
        self.assertEqual(blob['finalePhase'], 1)

        # Act cursor cannot outrun unlocks.
        ordered = save.sanitizeProgress({
            'unlockedThrough': 1,
            'actIndex': 2,
        })
        self.assertEqual(ordered['unlockedThrough'], 1)
        self.assertEqual(ordered['actIndex'], 1)

    def test_json_round_trip_survives_relog(self):
        save = self.save
        with tempfile.TemporaryDirectory() as tmp:
            path = save.progressPath(tmp, shard=42)
            self.assertTrue(path.endswith('42_campaign_progress.json'))
            av_id = 1001
            progress = save.sanitizeProgress({
                'unlockedThrough': 1,
                'actIndex': 1,
                'reclaimCount': 1,
                'state': self.camp.STATE_ACTIVE,
                'finalePhase': 0,
            })
            self.assertTrue(save.writeAvatar(path, av_id, progress))
            # Simulate logout: drop memory, read fresh from disk.
            loaded = save.readAvatar(path, av_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded['unlockedThrough'], 1)
            self.assertEqual(loaded['actIndex'], 1)
            self.assertEqual(loaded['reclaimCount'], 1)
            self.assertEqual(loaded['state'], self.camp.STATE_ACTIVE)
            # Unknown avatar stays missing (not defaulted by readAvatar).
            self.assertIsNone(save.readAvatar(path, 9999))

    def test_director_hydrate_persist_rehydrate_keeps_unlock(self):
        save = self.save
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp, district_id=3)
            director = _FakeDirector(air)
            toon = types.SimpleNamespace(doId=5505)

            # Fresh login — defaults.
            director._hydrateFromToon(toon, save)
            self.assertEqual(director.unlockedThrough, 0)
            self.assertEqual(director.actIndex, 0)

            # Clear Loopy → unlock Punchline (session).
            director.unlockedThrough = 1
            director.actIndex = 1
            director.reclaimCount = 1
            director.state = self.camp.STATE_ACTIVE
            self.assertTrue(
                director._persistForAvatarId(toon.doId, save))

            # Relog: new director process, same avatar id.
            director2 = _FakeDirector(air)
            director2._hydrateFromToon(toon, save)
            self.assertEqual(director2.unlockedThrough, 1)
            self.assertEqual(director2.actIndex, 1)
            self.assertEqual(director2.reclaimCount, 1)
            self.assertEqual(director2.state, self.camp.STATE_ACTIVE)

    def test_switching_avatars_does_not_leak_unlock(self):
        save = self.save
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp)
            director = _FakeDirector(air)
            alice = types.SimpleNamespace(doId=1)
            bob = types.SimpleNamespace(doId=2)

            director._hydrateFromToon(alice, save)
            director.unlockedThrough = 2
            director.actIndex = 2
            director.state = self.camp.STATE_ACTIVE
            director._persistForAvatarId(alice.doId, save)

            director._hydrateFromToon(bob, save)
            self.assertEqual(director.unlockedThrough, 0)
            self.assertEqual(director.actIndex, 0)

            # Alice still has her unlock on disk.
            alice_blob = save.readAvatar(director._progressPath(), alice.doId)
            self.assertEqual(alice_blob['unlockedThrough'], 2)

    def test_director_ai_wires_hydrate_and_persist_hooks(self):
        tree = _module_ast('toontown/campaign/CampaignDirectorAI.py')
        methods = _class_method_names(tree, 'CampaignDirectorAI')
        for name in (
                '_hydrateFromToon',
                '_persistForToon',
                '_persistForAvatarId',
                '_progressPath',
                'startCampaign',
                'advanceCampaign'):
            self.assertIn(name, methods)

        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('CampaignProgressSave', src)
        self.assertIn('_hydrateFromToon(toon)', src)
        self.assertIn('_persistForToon(toon)', src)
        # Unlock-on-reclaim path must flush so Punchline survives logout.
        reclaim_idx = src.find('def __onNeighborhoodReclaimed')
        self.assertGreater(reclaim_idx, 0)
        reclaim_snip = src[reclaim_idx:reclaim_idx + 2200]
        self.assertIn('_persistForToon(toon)', reclaim_snip)
        self.assertIn(
            'self.unlockedThrough = max(self.unlockedThrough, nextIndex)',
            reclaim_snip)

    def test_progress_save_module_has_no_keyblade_branding(self):
        src = _read('toontown/campaign/CampaignProgressSave.py')
        lowered = src.lower()
        for banned in ('keyblade', 'kingdom hearts', 'key blade'):
            self.assertNotIn(banned, lowered)


if __name__ == '__main__':
    unittest.main()
