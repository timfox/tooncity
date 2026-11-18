#!/usr/bin/env python3
"""Headless tests: mid-chase Oswald HP survives resume / relog.

STATE_VICTORY + chaseCleared=0 + chaseHp>0 must re-field Corrupted Oswald
at the saved remaining HP — not a free full heal. Loads CampaignGlobals /
CampaignProgressSave / panda-free chase helpers with a ToontownGlobals stub.

Run from repo root:
  python3 tests/test_oswald_chase_hp_persist.py
  python3 -m unittest tests.test_oswald_chase_hp_persist -v
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


def _load_chase_helpers(camp, cg):
    """Panda-free subset of OswaldBetrayalChase (chaseHp / resolve / defeat)."""
    mod = types.ModuleType('oswald_chase_hp_helpers')

    def chaseHp():
        hp = int(getattr(camp, 'OSWALD_BETRAYAL_CHASE_HP', 0) or 0)
        if hp > 0:
            return hp
        return cg.archetypeDefaultHp(cg.ARCHETYPE_CORRUPT_OSWALD)

    def resolveChaseSpawnHp(remaining=None, maxHp=None):
        if maxHp is None:
            maxHp = chaseHp()
        try:
            maxHp = int(maxHp)
        except (TypeError, ValueError):
            maxHp = 0
        maxHp = max(1, maxHp)
        if remaining is None:
            return maxHp, maxHp
        try:
            rem = int(remaining)
        except (TypeError, ValueError):
            rem = 0
        if rem <= 0:
            return maxHp, maxHp
        return maxHp, max(1, min(rem, maxHp))

    def chaseCombatDefeated(corrupt):
        if corrupt is None:
            return False
        if bool(getattr(corrupt, '_defeated', False)):
            return True
        try:
            hp = int(getattr(corrupt, 'hp', 0) or 0)
        except Exception:
            hp = 0
        return hp <= 0

    mod.chaseHp = chaseHp
    mod.resolveChaseSpawnHp = resolveChaseSpawnHp
    mod.chaseCombatDefeated = chaseCombatDefeated
    return mod


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _module_names(rel: str) -> set[str]:
    tree = _module_ast(rel)
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


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
    """Panda-free mirror of chase-HP persist + resume spawn override."""

    def __init__(self, air, save_mod, camp_mod, chase_mod):
        self.air = air
        self._save = save_mod
        self._camp = camp_mod
        self._chase = chase_mod
        self.state = camp_mod.STATE_IDLE
        self.actIndex = 0
        self.reclaimCount = 0
        self.unlockedThrough = 0
        self._finalePhase = 0
        self.chaseCleared = 0
        self.chaseHp = 0
        self._lastToonId = None
        self._hydratedToonId = None
        self._oswaldChaseDoId = None
        self._oswaldChaseTask = None
        self.scheduleCalls = []
        self.spawnHpArgs = []
        self.persistCalls = 0

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

    def _persistForToon(self, toon=None):
        avId = getattr(toon, 'doId', None) if toon is not None else None
        if avId is None:
            avId = self._lastToonId
        if avId is None:
            return False
        self.persistCalls += 1
        return self._save.writeAvatar(
            self._progressPath(), avId,
            self._save.snapshotFromDirector(self))

    def _snapshotOswaldChaseHp(self, corrupt, toon=None, persist=False):
        if corrupt is None or self._chase.chaseCombatDefeated(corrupt):
            return False
        try:
            liveHp = int(getattr(corrupt, 'hp', 0) or 0)
        except (TypeError, ValueError):
            liveHp = 0
        if liveHp <= 0:
            return False
        _max, clamped = self._chase.resolveChaseSpawnHp(
            remaining=liveHp, maxHp=self._chase.chaseHp())
        prior = int(getattr(self, 'chaseHp', 0) or 0)
        if clamped == prior:
            return False
        self.chaseHp = int(clamped)
        if persist:
            self._persistForToon(toon)
        return True

    def _scheduleOswaldBetrayalChase(self, toon, zoneId):
        remaining = int(getattr(self, 'chaseHp', 0) or 0)
        hp_arg = remaining if remaining > 0 else None
        self.scheduleCalls.append((
            getattr(toon, 'doId', None), int(zoneId), hp_arg))
        self.spawnHpArgs.append(hp_arg)
        self._oswaldChaseTask = 'campaign-oswald-betrayal-chase'
        # Mirror spawn: resolve what HP the chase would field.
        _max, current = self._chase.resolveChaseSpawnHp(
            remaining=hp_arg, maxHp=self._chase.chaseHp())
        self.chaseHp = int(current)

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


class OswaldChaseHpPersistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save, cls.cfg = _load_panda_free_modules()
        cls.chase = _load_chase_helpers(cls.camp, cls.cfg)

    def test_resolve_chase_spawn_hp_clamps_remaining(self):
        chase = self.chase
        max_hp = chase.chaseHp()
        self.assertGreater(max_hp, 10)
        self.assertEqual(chase.resolveChaseSpawnHp(None), (max_hp, max_hp))
        self.assertEqual(chase.resolveChaseSpawnHp(0), (max_hp, max_hp))
        self.assertEqual(chase.resolveChaseSpawnHp(-5), (max_hp, max_hp))
        mid = max(1, max_hp // 2)
        self.assertEqual(chase.resolveChaseSpawnHp(mid), (max_hp, mid))
        self.assertEqual(
            chase.resolveChaseSpawnHp(max_hp + 50), (max_hp, max_hp))
        self.assertEqual(chase.resolveChaseSpawnHp(1), (max_hp, 1))
        # Never spawn already-KO'd from a stale zero remaining with override.
        self.assertEqual(
            chase.resolveChaseSpawnHp(remaining=0, maxHp=40), (40, 40))

    def test_sanitize_persists_mid_chase_hp(self):
        save = self.save
        camp = self.camp
        blob = save.sanitizeProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'reclaimCount': 3,
            'state': camp.STATE_VICTORY,
            'finalePhase': 0,
            'chaseCleared': 0,
            'chaseHp': 37,
        })
        self.assertEqual(blob['chaseHp'], 37)
        self.assertEqual(blob['chaseCleared'], 0)
        # Cleared chase drops remaining HP.
        cleared = save.sanitizeProgress({
            'state': camp.STATE_VICTORY,
            'chaseCleared': 1,
            'chaseHp': 37,
        })
        self.assertEqual(cleared['chaseHp'], 0)
        # Non-victory drops remaining HP.
        active = save.sanitizeProgress({
            'state': camp.STATE_ACTIVE,
            'chaseCleared': 0,
            'chaseHp': 37,
        })
        self.assertEqual(active['chaseHp'], 0)
        fresh = save.defaultProgress()
        self.assertEqual(fresh['chaseHp'], 0)
        self.assertIn('chaseHp', fresh)

    def test_snapshot_apply_round_trip_chase_hp(self):
        save = self.save
        camp = self.camp
        director = types.SimpleNamespace(
            unlockedThrough=2,
            actIndex=2,
            reclaimCount=4,
            state=camp.STATE_VICTORY,
            _finalePhase=0,
            chaseCleared=0,
            chaseHp=22,
        )
        blob = save.snapshotFromDirector(director)
        self.assertEqual(blob['chaseHp'], 22)
        target = types.SimpleNamespace()
        save.applyProgressToDirector(target, blob)
        self.assertEqual(target.chaseHp, 22)
        self.assertEqual(target.chaseCleared, 0)
        self.assertEqual(target.state, camp.STATE_VICTORY)

    def test_json_relog_keeps_damaged_chase_hp(self):
        save = self.save
        camp = self.camp
        chase = self.chase
        max_hp = chase.chaseHp()
        damaged = max(1, max_hp // 3)
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp, district_id=9)
            toon = types.SimpleNamespace(doId=4401, zoneId=TTC)
            prior = _FakeDirector(air, save, camp, chase)
            prior.state = camp.STATE_VICTORY
            prior.unlockedThrough = 2
            prior.actIndex = 2
            prior.reclaimCount = 3
            prior.chaseCleared = 0
            prior.chaseHp = damaged
            path = prior._progressPath()
            self.assertTrue(save.writeAvatar(
                path, toon.doId, save.snapshotFromDirector(prior)))

            loaded = save.readAvatar(path, toon.doId)
            self.assertEqual(loaded['chaseHp'], damaged)
            self.assertEqual(loaded['chaseCleared'], 0)
            self.assertEqual(loaded['state'], camp.STATE_VICTORY)

            # Fresh director hydrate must resume with remaining HP override.
            after = _FakeDirector(air, save, camp, chase)
            self.assertTrue(after._hydrateFromToon(toon))
            self.assertEqual(after.state, camp.STATE_VICTORY)
            self.assertEqual(after.chaseCleared, 0)
            self.assertEqual(len(after.scheduleCalls), 1)
            self.assertEqual(after.spawnHpArgs[0], damaged)
            # Director chaseHp stays at resolved remaining (not full heal).
            self.assertEqual(after.chaseHp, damaged)
            _max, current = chase.resolveChaseSpawnHp(remaining=damaged)
            self.assertEqual(current, damaged)
            self.assertLess(current, _max)

    def test_snapshot_during_watch_persists_damage(self):
        save = self.save
        camp = self.camp
        chase = self.chase
        max_hp = chase.chaseHp()
        damaged = max(1, max_hp - 15)
        with tempfile.TemporaryDirectory() as tmp:
            air = _FakeAir(tmp)
            toon = types.SimpleNamespace(doId=77, zoneId=SILLY)
            director = _FakeDirector(air, save, camp, chase)
            director.state = camp.STATE_VICTORY
            director.chaseCleared = 0
            director.chaseHp = 0
            director._lastToonId = toon.doId
            oswald = types.SimpleNamespace(
                doId=55, hp=damaged, maxHp=max_hp, _defeated=False)
            self.assertTrue(director._snapshotOswaldChaseHp(
                oswald, toon=toon, persist=True))
            self.assertEqual(director.chaseHp, damaged)
            self.assertEqual(director.persistCalls, 1)
            loaded = save.readAvatar(director._progressPath(), toon.doId)
            self.assertEqual(loaded['chaseHp'], damaged)
            # Unchanged HP does not re-flush.
            self.assertFalse(director._snapshotOswaldChaseHp(
                oswald, toon=toon, persist=True))
            self.assertEqual(director.persistCalls, 1)

    def test_clear_and_replay_wipe_zero_chase_hp(self):
        save = self.save
        camp = self.camp
        blob = save.sanitizeProgress({
            'state': camp.STATE_VICTORY,
            'chaseCleared': 1,
            'chaseHp': 12,
            'unlockedThrough': 2,
            'actIndex': 2,
        })
        self.assertEqual(blob['chaseHp'], 0)
        # Replay wipe path: director fields reset including chaseHp.
        director = types.SimpleNamespace(
            unlockedThrough=0,
            actIndex=0,
            reclaimCount=0,
            state=camp.STATE_ACTIVE,
            _finalePhase=0,
            chaseCleared=0,
            chaseHp=0,
        )
        wiped = save.snapshotFromDirector(director)
        self.assertEqual(wiped['chaseHp'], 0)

    def test_chase_module_exports_resolve_helper(self):
        names = _module_names('toontown/campaign/OswaldBetrayalChase.py')
        self.assertIn('resolveChaseSpawnHp', names)
        self.assertIn('spawnCorruptOswald', names)
        self.assertIn('chaseHp', names)
        src = _read('toontown/campaign/OswaldBetrayalChase.py')
        self.assertIn('resolveChaseSpawnHp', src)
        self.assertIn('remaining=hp', src)
        # Signature accepts mid-chase hp override.
        self.assertIn('hp=None', src)
        # Doc may say "no keyblades"; ban affirmative KH product copy only.
        lowered = src.lower()
        for banned in ('kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, lowered)

    def test_director_ai_wires_chase_hp_persist(self):
        tree = _module_ast('toontown/campaign/CampaignDirectorAI.py')
        methods = _class_method_names(tree, 'CampaignDirectorAI')
        self.assertIn('_snapshotOswaldChaseHp', methods)
        self.assertIn('__spawnOswaldBetrayalChase', methods)
        self.assertIn('__watchOswaldBetrayalChase', methods)
        self.assertIn('__finishOswaldBetrayalChaseClear', methods)

        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('self.chaseHp = 0', src)
        self.assertIn('_snapshotOswaldChaseHp', src)
        self.assertIn('resolveChaseSpawnHp', src)
        self.assertIn('spawnCorruptOswald', src)

        spawn = src[src.find('def __spawnOswaldBetrayalChase'):]
        spawn = spawn[:spawn.find('def __watchOswaldBetrayalChase')]
        self.assertIn('hp=remaining if remaining > 0 else None', spawn)
        self.assertIn('chaseHp', spawn)

        watch = src[src.find('def __watchOswaldBetrayalChase'):]
        watch = watch[:watch.find('def __finishOswaldBetrayalChaseClear')]
        self.assertIn('_snapshotOswaldChaseHp', watch)
        self.assertIn('persist=True', watch)
        self.assertNotIn('self.chaseCleared = 1', watch)

        finish = src[src.find('def __finishOswaldBetrayalChaseClear'):]
        finish = finish[:finish.find('def __onNeighborhoodReclaimed')]
        self.assertIn('self.chaseCleared = 1', finish)
        self.assertIn('self.chaseHp = 0', finish)

        start = src[src.find('def startCampaign'):]
        start = start[:start.find('def advanceCampaign')]
        # Replay wipe zeros chaseHp after resume gate.
        wipe_hp = start.find('self.chaseHp = 0')
        resume_at = start.find('_resumePendingOswaldBetrayalChase')
        self.assertGreater(wipe_hp, resume_at)

        cancel = src[src.find('def _cancelOswaldBetrayalChase'):]
        cancel = cancel[:cancel.find('def _scheduleOswaldBetrayalChase')]
        self.assertIn('_snapshotOswaldChaseHp', cancel)

        save_src = _read('toontown/campaign/CampaignProgressSave.py')
        self.assertIn("'chaseHp'", save_src)
        self.assertIn('director.chaseHp', save_src)
        lowered = src.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, lowered)

    def test_no_cream_or_kh_in_progress_save(self):
        src = _read('toontown/campaign/CampaignProgressSave.py').lower()
        for banned in ('kingdom hearts', 'sora', 'key blade', 'cream', 'sparkle'):
            self.assertNotIn(banned, src)


if __name__ == '__main__':
    unittest.main()
