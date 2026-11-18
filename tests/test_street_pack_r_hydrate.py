#!/usr/bin/env python3
"""Headless / AST: street-pack R hydrates campaign progress before soft-gate.

#318 persisted unlockedThrough and hydrated on C (startCampaign /
advanceCampaign). R (startStreetPackForToon) still read the live director
without hydrate — after relog the soft-gate could treat Punchline / Silly
as locked even when the toon's blob had unlocks.

Run from repo root:
  python3 tests/test_street_pack_r_hydrate.py
  python3 -m unittest tests.test_street_pack_r_hydrate -v
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
HUB = 2000


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_stack():
    """Stub ToontownGlobals; load reclaim + campaign progress helpers."""
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
    tg.ToontownCentral = HUB
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    cg_path = REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
    cg_spec = importlib.util.spec_from_file_location(
        'toontown.corruption.CorruptionGlobals', cg_path)
    cg = importlib.util.module_from_spec(cg_spec)
    assert cg_spec.loader is not None
    sys.modules['toontown.corruption.CorruptionGlobals'] = cg
    cg_spec.loader.exec_module(cg)

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
    sys.modules['toontown.campaign'].CampaignGlobals = camp

    save_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignProgressSave.py'
    save_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignProgressSave', save_path)
    save = importlib.util.module_from_spec(save_spec)
    assert save_spec.loader is not None
    sys.modules['toontown.campaign.CampaignProgressSave'] = save
    save_spec.loader.exec_module(save)
    return rg, camp, save


class _FakeAir:
    def __init__(self, data_folder, district_id=7):
        self.dataFolder = data_folder if data_folder.endswith('/') else (
            data_folder + '/')
        self.districtId = district_id


class _FakeDirector:
    """Minimal CampaignDirectorAI progress surface for R-start hydrate."""

    def __init__(self, air, save_mod):
        self.air = air
        self._save = save_mod
        self.state = 0
        self.actIndex = 0
        self.reclaimCount = 0
        self.unlockedThrough = 0
        self._finalePhase = 0
        self._hydratedToonId = None
        self.hydrateCalls = 0

    def _progressPath(self):
        return self._save.progressPath(
            self.air.dataFolder, getattr(self.air, 'districtId', None))

    def _hydrateFromToon(self, toon):
        self.hydrateCalls += 1
        avId = getattr(toon, 'doId', None)
        if avId is None:
            return False
        if self._hydratedToonId == avId:
            return False
        progress = self._save.readAvatar(self._progressPath(), avId)
        self._hydratedToonId = avId
        if progress is None:
            progress = self._save.defaultProgress()
        self._save.applyProgressToDirector(self, progress)
        return True


def _r_gate_unlocked_through(campaign, toon, rg, zone_id):
    """Mirror startStreetPackForToon soft-gate: hydrate then check unlock."""
    if hasattr(campaign, '_hydrateFromToon'):
        campaign._hydrateFromToon(toon)
    unlocked = int(getattr(campaign, 'unlockedThrough', 0) or 0)
    return rg.streetPackUnlocked(zone_id, unlocked), unlocked


class StreetPackRHydrateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.camp, cls.save = _load_panda_free_stack()

    def test_ast_r_start_hydrates_before_unlock_read(self):
        src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirectorAI.py')
        method = None
        for node in ast.walk(tree):
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == 'startStreetPackForToon'):
                method = node
                break
        self.assertIsNotNone(method)
        method_src = ast.get_source_segment(src, method)
        self.assertIsNotNone(method_src)
        self.assertIn('_hydrateFromToon', method_src)
        self.assertIn('unlockedThrough', method_src)
        hydrate_at = method_src.find('_hydrateFromToon')
        unlock_at = method_src.find(
            "getattr(campaign, 'unlockedThrough'", hydrate_at)
        if unlock_at < 0:
            unlock_at = method_src.find('unlockedThrough', hydrate_at + 1)
        self.assertGreater(hydrate_at, 0)
        self.assertGreater(unlock_at, hydrate_at)
        # Prefer gate still present; hydrate is additive, not a rewrite.
        self.assertIn('streetPackUnlocked', method_src)
        lowered = method_src.lower()
        for banned in ('keyblade', 'kingdom hearts', 'key blade'):
            self.assertNotIn(banned, lowered)

    def test_relog_r_soft_gate_sees_persisted_punchline_unlock(self):
        """After Loopy clear + logout, R on Punchline must unlock via hydrate."""
        save = self.save
        rg = self.rg
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp, district_id=11)
            toon = types.SimpleNamespace(doId=4242, zoneId=PUNCHLINE)

            # Session that cleared Loopy — persist Punchline unlock.
            live = _FakeDirector(air, save)
            live.unlockedThrough = 1
            live.actIndex = 1
            live.state = self.camp.STATE_ACTIVE
            path = live._progressPath()
            self.assertTrue(save.writeAvatar(
                path, toon.doId, save.snapshotFromDirector(live)))

            # Relog: fresh air director defaults to unlockedThrough=0.
            after = _FakeDirector(air, save)
            self.assertEqual(after.unlockedThrough, 0)
            # Without hydrate, Punchline R would soft-gate wrongly.
            self.assertFalse(rg.streetPackUnlocked(PUNCHLINE, 0))

            ok, unlocked = _r_gate_unlocked_through(
                after, toon, rg, PUNCHLINE)
            self.assertEqual(after.hydrateCalls, 1)
            self.assertEqual(unlocked, 1)
            self.assertTrue(ok)
            self.assertTrue(rg.streetPackUnlocked(PUNCHLINE, unlocked))
            # Silly still gated until Punchline clear.
            self.assertFalse(rg.streetPackUnlocked(SILLY, unlocked))

    def test_fresh_toon_r_still_gates_punchline(self):
        save = self.save
        rg = self.rg
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp)
            toon = types.SimpleNamespace(doId=7, zoneId=PUNCHLINE)
            director = _FakeDirector(air, save)
            ok, unlocked = _r_gate_unlocked_through(
                director, toon, rg, PUNCHLINE)
            self.assertEqual(director.hydrateCalls, 1)
            self.assertEqual(unlocked, 0)
            self.assertFalse(ok)
            # Loopy discoverable entry stays open.
            self.assertTrue(rg.streetPackUnlocked(LOOPY, unlocked))


if __name__ == '__main__':
    unittest.main()
