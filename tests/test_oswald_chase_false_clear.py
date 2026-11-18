#!/usr/bin/env python3
"""Headless tests: don't false-clear Oswald chase on zone leave / DO despawn.

Chase soft-end (chaseCleared / hub wash / epilogue) requires intentional
combat defeat (hp≤0 / _defeated). Missing DO or deleted-without-defeat
must keep chaseCleared=0 so resume can re-field. Loads CampaignGlobals
with a ToontownGlobals stub — no Panda3D. Pure defeat helper is exercised
via a panda-stubbed OswaldBetrayalChase import; director / client gates
are AST-pinned + lightweight fakes.

Run from repo root:
  python3 tests/test_oswald_chase_false_clear.py
  python3 -m unittest tests.test_oswald_chase_false_clear -v
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


def _stub_module(name: str, **attrs) -> types.ModuleType:
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    sys.modules[name] = mod
    return mod


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
    return camp, cg


def _load_chase_helpers(camp, cg):
    """Import OswaldBetrayalChase with panda/direct stubs for pure helpers."""
    class _Vec4:
        def __init__(self, *args):
            self.args = args

        def __getitem__(self, idx):
            return self.args[idx]

    class _TextNode:
        ACenter = 0

        def __init__(self, name=''):
            self.name = name

        def setText(self, *a, **k):
            pass

        def setAlign(self, *a, **k):
            pass

        def setTextColor(self, *a, **k):
            pass

        def setShadow(self, *a, **k):
            pass

        def setShadowColor(self, *a, **k):
            pass

        def setWordwrap(self, *a, **k):
            pass

    _stub_module('panda3d')
    _stub_module('panda3d.core', TextNode=_TextNode, Vec4=_Vec4)
    _stub_module('direct')
    _stub_module('direct.interval')
    _stub_module(
        'direct.interval.IntervalGlobal',
        Func=object, LerpColorScaleInterval=object,
        LerpScaleInterval=object, Parallel=object, Sequence=object,
        Wait=object)
    _stub_module('direct.showbase')
    _stub_module('direct.showbase.DirectObject', DirectObject=object)
    # Avoid pulling real DistributedCorruptToonAI (panda-bound).
    ai_mod = _stub_module(
        'toontown.corruption.DistributedCorruptToonAI',
        DistributedCorruptToonAI=type('DistributedCorruptToonAI', (), {}))
    sys.modules['toontown.corruption'].DistributedCorruptToonAI = ai_mod

    path = REPO_ROOT / 'toontown' / 'campaign' / 'OswaldBetrayalChase.py'
    spec = importlib.util.spec_from_file_location(
        'toontown.campaign.OswaldBetrayalChase', path)
    chase = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules['toontown.campaign.OswaldBetrayalChase'] = chase
    spec.loader.exec_module(chase)
    return chase


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


class _Task:
    done = 'done'
    again = 'again'


class _FakeWatchDirector:
    """Mirrors CampaignDirectorAI chase-watch gate without panda / TaskMgr."""

    def __init__(self, air, chase_mod, camp):
        self.air = air
        self.chase = chase_mod
        self.camp = camp
        self.state = camp.STATE_VICTORY
        self.chaseCleared = 0
        self._oswaldChaseDoId = None
        self._oswaldChaseWatch = 'watch'
        self._oswaldChaseTask = None
        self._lastToonId = None
        self.resumeCalls = []
        self.clearCalls = []
        self.hubWashCalls = 0
        self.persisted = 0
        self.messages = []
        self.messengerEvents = []

    def _pendingOswaldBetrayalChase(self):
        if self.state != self.camp.STATE_VICTORY:
            return False
        if int(getattr(self, 'chaseCleared', 0) or 0):
            return False
        return True

    def _resumePendingOswaldBetrayalChase(self, toon=None):
        self.resumeCalls.append(getattr(toon, 'doId', None))
        return True

    def _toonFromLast(self):
        if self._lastToonId is None:
            return None
        return self.air.doId2do.get(self._lastToonId)

    def _syncHubStain(self, tell=False, toon=None):
        self.hubWashCalls += 1

    def _persistForToon(self, toon=None):
        self.persisted += 1

    def _tellToon(self, toon, message):
        self.messages.append(str(message))

    def watchOswaldBetrayalChase(self, doId, toonId, task):
        # Keep in sync with CampaignDirectorAI.__watchOswaldBetrayalChase.
        if doId <= 0:
            self._oswaldChaseWatch = None
            self._oswaldChaseDoId = None
            return _Task.done
        corrupt = self.air.doId2do.get(int(doId))
        if corrupt is not None and self.chase.chaseCombatDefeated(corrupt):
            return self.finishOswaldBetrayalChaseClear(doId, toonId)
        present = (
            corrupt is not None
            and not getattr(corrupt, 'isDeleted', lambda: True)())
        if present:
            return _Task.again
        self._oswaldChaseWatch = None
        self._oswaldChaseDoId = None
        toon = self.air.doId2do.get(int(toonId)) if toonId else None
        if toon is None:
            toon = self._toonFromLast()
        if self._pendingOswaldBetrayalChase():
            self._resumePendingOswaldBetrayalChase(toon)
        return _Task.done

    def finishOswaldBetrayalChaseClear(self, doId, toonId):
        self._oswaldChaseWatch = None
        self._oswaldChaseDoId = None
        toon = self.air.doId2do.get(int(toonId)) if toonId else None
        if toon is None:
            toon = self._toonFromLast()
        self.chaseCleared = 1
        self._syncHubStain(tell=True, toon=toon)
        self._persistForToon(toon)
        self.clearCalls.append(int(doId))
        self.messengerEvents.append('oswaldBetrayalChaseCleared')
        self.messengerEvents.append('campaignEpilogue')
        return _Task.done


class OswaldChaseFalseClearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.cfg = _load_panda_free_modules()
        cls.chase = _load_chase_helpers(cls.camp, cls.cfg)

    def test_chase_combat_defeated_helper(self):
        chase = self.chase
        self.assertFalse(chase.chaseCombatDefeated(None))
        alive = types.SimpleNamespace(hp=40, _defeated=False)
        self.assertFalse(chase.chaseCombatDefeated(alive))
        # Intentional combat KO.
        ko_hp = types.SimpleNamespace(hp=0, _defeated=False)
        self.assertTrue(chase.chaseCombatDefeated(ko_hp))
        ko_flag = types.SimpleNamespace(hp=12, _defeated=True)
        self.assertTrue(chase.chaseCombatDefeated(ko_flag))
        # Zone-leave / despawn stand-in: missing object is not a defeat.
        self.assertFalse(chase.chaseCombatDefeated(None))

    def test_watch_clears_only_on_combat_defeat(self):
        air = types.SimpleNamespace(doId2do={})
        toon = types.SimpleNamespace(doId=7, zoneId=SILLY)
        air.doId2do[7] = toon
        director = _FakeWatchDirector(air, self.chase, self.camp)
        director._lastToonId = 7
        director._oswaldChaseDoId = 55

        oswald = types.SimpleNamespace(
            doId=55, hp=40, _defeated=False,
            isDeleted=lambda: False)
        air.doId2do[55] = oswald
        self.assertEqual(
            director.watchOswaldBetrayalChase(55, 7, None), _Task.again)
        self.assertEqual(director.chaseCleared, 0)
        self.assertEqual(director.resumeCalls, [])
        self.assertEqual(director.clearCalls, [])

        # Combat defeat → clear + hub wash + epilogue tokens.
        oswald.hp = 0
        oswald._defeated = True
        self.assertEqual(
            director.watchOswaldBetrayalChase(55, 7, None), _Task.done)
        self.assertEqual(director.chaseCleared, 1)
        self.assertEqual(director.clearCalls, [55])
        self.assertEqual(director.hubWashCalls, 1)
        self.assertEqual(director.persisted, 1)
        self.assertIn('oswaldBetrayalChaseCleared', director.messengerEvents)
        self.assertIn('campaignEpilogue', director.messengerEvents)
        self.assertEqual(director.resumeCalls, [])

    def test_watch_zone_leave_or_despawn_does_not_clear(self):
        air = types.SimpleNamespace(doId2do={})
        toon = types.SimpleNamespace(doId=9, zoneId=TTC)
        air.doId2do[9] = toon
        director = _FakeWatchDirector(air, self.chase, self.camp)
        director._lastToonId = 9
        director._oswaldChaseDoId = 88

        # DO missing from map (zone leave / despawn) — not a defeat.
        self.assertEqual(
            director.watchOswaldBetrayalChase(88, 9, None), _Task.done)
        self.assertEqual(director.chaseCleared, 0)
        self.assertEqual(director.clearCalls, [])
        self.assertEqual(director.hubWashCalls, 0)
        self.assertEqual(director.persisted, 0)
        self.assertEqual(director.messengerEvents, [])
        self.assertEqual(director.resumeCalls, [9])
        self.assertIsNone(director._oswaldChaseDoId)

        # Deleted without _defeated / hp<=0 — same: resume, no clear.
        director2 = _FakeWatchDirector(air, self.chase, self.camp)
        director2._lastToonId = 9
        director2._oswaldChaseDoId = 89
        gone = types.SimpleNamespace(
            doId=89, hp=40, _defeated=False,
            isDeleted=lambda: True)
        air.doId2do[89] = gone
        self.assertEqual(
            director2.watchOswaldBetrayalChase(89, 9, None), _Task.done)
        self.assertEqual(director2.chaseCleared, 0)
        self.assertEqual(director2.clearCalls, [])
        self.assertEqual(director2.resumeCalls, [9])

    def test_watch_defeated_mid_delete_still_clears(self):
        air = types.SimpleNamespace(doId2do={})
        toon = types.SimpleNamespace(doId=3, zoneId=SILLY)
        air.doId2do[3] = toon
        director = _FakeWatchDirector(air, self.chase, self.camp)
        director._lastToonId = 3
        # Defeat delete delay: still in map, isDeleted, but combat-defeated.
        oswald = types.SimpleNamespace(
            doId=44, hp=0, _defeated=True,
            isDeleted=lambda: True)
        air.doId2do[44] = oswald
        self.assertEqual(
            director.watchOswaldBetrayalChase(44, 3, None), _Task.done)
        self.assertEqual(director.chaseCleared, 1)
        self.assertEqual(director.clearCalls, [44])
        self.assertEqual(director.resumeCalls, [])

    def test_director_ast_gates_defeat_before_clear(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        methods = _class_method_names(
            _module_ast('toontown/campaign/CampaignDirectorAI.py'),
            'CampaignDirectorAI')
        self.assertIn('__watchOswaldBetrayalChase', methods)
        self.assertIn('__finishOswaldBetrayalChaseClear', methods)
        self.assertIn('chaseCombatDefeated', src)

        watch = src[src.find('def __watchOswaldBetrayalChase'):]
        watch = watch[:watch.find('def __finishOswaldBetrayalChaseClear')]
        self.assertIn('chaseCombatDefeated', watch)
        self.assertIn('_resumePendingOswaldBetrayalChase', watch)
        # Must not set chaseCleared in the non-defeat branch.
        self.assertNotIn('self.chaseCleared = 1', watch)

        finish = src[src.find('def __finishOswaldBetrayalChaseClear'):]
        finish = finish[:finish.find('def __onNeighborhoodReclaimed')]
        self.assertIn('self.chaseCleared = 1', finish)
        self.assertIn('_syncHubStain', finish)
        self.assertIn('oswaldBetrayalChaseCleared', finish)
        self.assertIn('campaignEpilogue', finish)
        lowered = src.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, lowered)

    def test_client_poll_ast_requires_defeat(self):
        rel = 'toontown/campaign/OswaldBetrayalChase.py'
        names = _module_names(rel)
        self.assertIn('chaseCombatDefeated', names)
        self.assertIn('_findCorruptOswald', names)
        self.assertIn('_pollChaseClear', names)

        src = _read(rel)
        poll = src[src.find('def _pollChaseClear'):]
        poll = poll[:poll.find('def _findLiveCorruptOswald')]
        self.assertIn('chaseCombatDefeated', poll)
        self.assertIn('_emitChaseCleared', poll)
        # Old false-clear copy must be gone.
        self.assertNotIn('treat as clear', poll.lower())
        # Absent-without-defeat path keeps watching (task.again), no emit.
        self.assertIn('zone leave', poll.lower())
        self.assertTrue(poll.rstrip().endswith('return task.again'))
        # Only the defeat branch emits clear (one call site in poll).
        self.assertEqual(poll.count('_emitChaseCleared'), 1)
        # Doc may say "no keyblades"; ban affirmative KH product copy only.
        for banned in ('kingdom hearts', 'sora'):
            self.assertNotIn(banned, src.lower())

    def test_hub_stain_watch_pin_still_washes_on_clear(self):
        # Sibling hub-stain suite pins chaseCleared in the clear path —
        # finish helper still owns that assignment.
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        finish = src[src.find('def __finishOswaldBetrayalChaseClear'):]
        finish = finish[:finish.find('def __onNeighborhoodReclaimed')]
        self.assertIn('self.chaseCleared = 1', finish)
        self.assertIn('_syncHubStain', finish)


if __name__ == '__main__':
    unittest.main()
