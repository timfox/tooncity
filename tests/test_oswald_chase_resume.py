#!/usr/bin/env python3
"""Headless tests: resume pending Oswald betrayal chase after relog / hub.

STATE_VICTORY + chaseCleared=0 must re-schedule the chase on hydrate, and
startCampaign must not wipe mid-victory while the chase is still pending.
Loads CampaignGlobals / CampaignProgressSave with a ToontownGlobals stub —
no Panda3D. Director resume helpers are exercised via a lightweight fake
that mirrors CampaignDirectorAI's pending/resume gates (AST pins the real
wiring).

Run from repo root:
  python3 tests/test_oswald_chase_resume.py
  python3 -m unittest tests.test_oswald_chase_resume -v
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
    """Panda-free mirror of CampaignDirectorAI pending-chase resume gates."""

    def __init__(self, air, save_mod, camp_mod):
        self.air = air
        self._save = save_mod
        self._camp = camp_mod
        self.state = camp_mod.STATE_IDLE
        self.actIndex = 0
        self.reclaimCount = 0
        self.unlockedThrough = 0
        self._finalePhase = 0
        self.chaseCleared = 0
        self._lastToonId = None
        self._hydratedToonId = None
        self._oswaldChaseDoId = None
        self._oswaldChaseTask = None
        self.scheduleCalls = []
        self.cancelCalls = 0
        self.wipeCalls = 0

    def _progressPath(self):
        return self._save.progressPath(
            self.air.dataFolder, getattr(self.air, 'districtId', None))

    def _chaseEnabled(self):
        return bool(getattr(
            self._camp, 'OSWALD_BETRAYAL_CHASE_ENABLED', True))

    def _pendingOswaldBetrayalChase(self):
        if self.state != self._camp.STATE_VICTORY:
            return False
        if int(getattr(self, 'chaseCleared', 0) or 0):
            return False
        return self._chaseEnabled()

    def _scheduleOswaldBetrayalChase(self, toon, zoneId):
        self.scheduleCalls.append((
            getattr(toon, 'doId', None), int(zoneId)))
        self._oswaldChaseTask = 'campaign-oswald-betrayal-chase'

    def _cancelOswaldBetrayalChase(self):
        self.cancelCalls += 1
        self._oswaldChaseTask = None
        self._oswaldChaseDoId = None

    def _resumePendingOswaldBetrayalChase(self, toon=None):
        if not self._pendingOswaldBetrayalChase():
            return False
        if toon is None:
            return False
        if (self._oswaldChaseTask is not None
                or self._oswaldChaseDoId is not None):
            return True
        avId = getattr(toon, 'doId', None)
        if avId is not None:
            self._lastToonId = avId
        zoneId = int(getattr(toon, 'zoneId', 0) or 0)
        if zoneId <= 0:
            for act in self._camp.ACTS:
                if act.get('finale'):
                    zoneId = int(act['zoneId'])
                    break
        self._scheduleOswaldBetrayalChase(toon, zoneId)
        return True

    def _hydrateFromToon(self, toon):
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
        self._lastToonId = avId
        self._resumePendingOswaldBetrayalChase(toon)
        return True

    def startCampaign(self, toon):
        """Mirror victory resume vs replay-wipe branch (no reclaim spawn)."""
        self._lastToonId = getattr(toon, 'doId', None)
        self._hydrateFromToon(toon)
        if self.state == self._camp.STATE_VICTORY:
            if self._resumePendingOswaldBetrayalChase(toon):
                return getattr(
                    self._camp, 'OSWALD_BETRAYAL_CHASE_RESUME_MSG',
                    'resume')
            # Replay wipe.
            self.wipeCalls += 1
            self.actIndex = 0
            self.unlockedThrough = 0
            self.reclaimCount = 0
            self._finalePhase = 0
            self.chaseCleared = 0
            self._cancelOswaldBetrayalChase()
            self._save.writeAvatar(
                self._progressPath(), toon.doId,
                self._save.snapshotFromDirector(self))
            self.state = self._camp.STATE_ACTIVE
            return 'replay'
        self.state = self._camp.STATE_ACTIVE
        return 'active'


class OswaldChaseResumeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save, cls.cfg = _load_panda_free_modules()

    def test_resume_msg_and_no_kh_branding(self):
        camp = self.camp
        self.assertTrue(camp.OSWALD_BETRAYAL_CHASE_ENABLED)
        self.assertTrue(camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG)
        self.assertIn('Oswald', camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG)
        self.assertIn('pending', camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG.lower())
        blob = camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, blob)

    def test_director_ai_wires_resume_helpers(self):
        tree = _module_ast('toontown/campaign/CampaignDirectorAI.py')
        methods = _class_method_names(tree, 'CampaignDirectorAI')
        for name in (
                '_pendingOswaldBetrayalChase',
                '_resumePendingOswaldBetrayalChase',
                '_hydrateFromToon',
                'startCampaign',
                '_scheduleOswaldBetrayalChase'):
            self.assertIn(name, methods)

        src = _read('toontown/campaign/CampaignDirectorAI.py')
        hydrate_idx = src.find('def _hydrateFromToon')
        self.assertGreater(hydrate_idx, 0)
        hydrate_win = src[hydrate_idx:hydrate_idx + 1800]
        self.assertIn('_resumePendingOswaldBetrayalChase(toon)', hydrate_win)

        start_idx = src.find('def startCampaign')
        start_win = src[start_idx:start_idx + 1600]
        resume_at = start_win.find('_resumePendingOswaldBetrayalChase')
        wipe_at = start_win.find('self.chaseCleared = 0')
        self.assertGreater(resume_at, 0)
        self.assertGreater(wipe_at, resume_at)
        # Pending path must return before STATE_ACTIVE reclaim start.
        self.assertIn('OSWALD_BETRAYAL_CHASE_RESUME_MSG', start_win)
        self.assertIn('return tip', start_win)

        resume_idx = src.find('def _resumePendingOswaldBetrayalChase')
        resume_win = src[resume_idx:resume_idx + 1600]
        self.assertIn('_pendingOswaldBetrayalChase', resume_win)
        self.assertIn('_scheduleOswaldBetrayalChase', resume_win)
        self.assertIn('_oswaldChaseTask', resume_win)
        self.assertIn('_oswaldChaseDoId', resume_win)
        lowered = src.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, lowered)

    def test_hydrate_victory_uncleared_reschedules_chase(self):
        save = self.save
        camp = self.camp
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp, district_id=5)
            toon = types.SimpleNamespace(doId=9001, zoneId=TTC)
            # Prior session: finale victory, chase not cleared, then logout.
            prior = _FakeDirector(air, save, camp)
            prior.state = camp.STATE_VICTORY
            prior.unlockedThrough = 2
            prior.actIndex = 2
            prior.reclaimCount = 3
            prior.chaseCleared = 0
            path = prior._progressPath()
            self.assertTrue(save.writeAvatar(
                path, toon.doId, save.snapshotFromDirector(prior)))

            # Relog: fresh director hydrates and must re-schedule chase.
            after = _FakeDirector(air, save, camp)
            self.assertEqual(after.state, camp.STATE_IDLE)
            self.assertTrue(after._hydrateFromToon(toon))
            self.assertEqual(after.state, camp.STATE_VICTORY)
            self.assertEqual(after.chaseCleared, 0)
            self.assertEqual(after.unlockedThrough, 2)
            self.assertEqual(len(after.scheduleCalls), 1)
            self.assertEqual(after.scheduleCalls[0], (9001, TTC))
            # Second hydrate same process does not double-schedule.
            self.assertFalse(after._hydrateFromToon(toon))
            self.assertEqual(len(after.scheduleCalls), 1)

    def test_hydrate_victory_cleared_does_not_schedule(self):
        save = self.save
        camp = self.camp
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp)
            toon = types.SimpleNamespace(doId=42, zoneId=LOOPY)
            prior = _FakeDirector(air, save, camp)
            prior.state = camp.STATE_VICTORY
            prior.unlockedThrough = 2
            prior.actIndex = 2
            prior.chaseCleared = 1
            self.assertTrue(save.writeAvatar(
                prior._progressPath(), toon.doId,
                save.snapshotFromDirector(prior)))

            after = _FakeDirector(air, save, camp)
            after._hydrateFromToon(toon)
            self.assertEqual(after.chaseCleared, 1)
            self.assertEqual(after.scheduleCalls, [])

    def test_start_campaign_mid_victory_pending_does_not_wipe(self):
        save = self.save
        camp = self.camp
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp, district_id=2)
            toon = types.SimpleNamespace(doId=77, zoneId=TTC)
            # Persist victory + uncleared chase, then fresh director + C.
            blob = save.sanitizeProgress({
                'unlockedThrough': 2,
                'actIndex': 2,
                'reclaimCount': 4,
                'state': camp.STATE_VICTORY,
                'finalePhase': 0,
                'chaseCleared': 0,
            })
            director = _FakeDirector(air, save, camp)
            self.assertTrue(save.writeAvatar(
                director._progressPath(), toon.doId, blob))

            tip = director.startCampaign(toon)
            self.assertEqual(tip, camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG)
            self.assertEqual(director.wipeCalls, 0)
            self.assertEqual(director.cancelCalls, 0)
            self.assertEqual(director.state, camp.STATE_VICTORY)
            self.assertEqual(director.chaseCleared, 0)
            self.assertEqual(director.unlockedThrough, 2)
            self.assertEqual(director.reclaimCount, 4)
            self.assertGreaterEqual(len(director.scheduleCalls), 1)
            # Disk must still hold victory + uncleared chase.
            loaded = save.readAvatar(director._progressPath(), toon.doId)
            self.assertEqual(loaded['state'], camp.STATE_VICTORY)
            self.assertEqual(loaded['chaseCleared'], 0)
            self.assertEqual(loaded['unlockedThrough'], 2)

    def test_start_campaign_victory_cleared_still_replays(self):
        save = self.save
        camp = self.camp
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp)
            toon = types.SimpleNamespace(doId=88, zoneId=LOOPY)
            blob = save.sanitizeProgress({
                'unlockedThrough': 2,
                'actIndex': 2,
                'reclaimCount': 5,
                'state': camp.STATE_VICTORY,
                'finalePhase': 0,
                'chaseCleared': 1,
            })
            director = _FakeDirector(air, save, camp)
            self.assertTrue(save.writeAvatar(
                director._progressPath(), toon.doId, blob))

            tip = director.startCampaign(toon)
            self.assertEqual(tip, 'replay')
            self.assertEqual(director.wipeCalls, 1)
            self.assertEqual(director.cancelCalls, 1)
            self.assertEqual(director.state, camp.STATE_ACTIVE)
            self.assertEqual(director.chaseCleared, 0)
            self.assertEqual(director.unlockedThrough, 0)
            self.assertEqual(director.actIndex, 0)
            self.assertEqual(director.scheduleCalls, [])

    def test_resume_skips_when_chase_already_live(self):
        camp = self.camp
        air = _FakeAir('/tmp')
        director = _FakeDirector(air, self.save, camp)
        director.state = camp.STATE_VICTORY
        director.chaseCleared = 0
        director._oswaldChaseDoId = 555
        toon = types.SimpleNamespace(doId=1, zoneId=TTC)
        self.assertTrue(director._resumePendingOswaldBetrayalChase(toon))
        self.assertEqual(director.scheduleCalls, [])


if __name__ == '__main__':
    unittest.main()
