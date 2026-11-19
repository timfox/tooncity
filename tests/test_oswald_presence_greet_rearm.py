#!/usr/bin/env python3
"""Headless tests: re-arm Oswald soft-next greet after unlock / zone leave.

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D.
Locks OswaldPresence clearing ``_greetedZone`` on zone leave and
``_rearmSoftNextGreet`` after ``campaignActUnlocked`` so plaza E-talk
shows the refreshed soft-next tip. Soft-next copy helpers stay intact.
No cream / no KH.

Run from repo root:
  python3 tests/test_oswald_presence_greet_rearm.py
  python3 -m unittest tests.test_oswald_presence_greet_rearm -v
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


def _load_panda_free_campaign():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = TTC
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
    return camp


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


def _method_source(rel: str, class_name: str, method_name: str) -> str:
    src = _read(rel)
    tree = ast.parse(src, filename=rel)
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                    item.name == method_name):
                return ast.get_source_segment(src, item) or ''
    return ''


def _accept_events(tree: ast.AST, class_name: str) -> set[str]:
    events = set()
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for item in node.body:
            if not (
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == '__init__'):
                continue
            for call in ast.walk(item):
                if not isinstance(call, ast.Call):
                    continue
                func = call.func
                if isinstance(func, ast.Attribute) and func.attr == 'accept':
                    if call.args:
                        arg0 = call.args[0]
                        if isinstance(arg0, ast.Constant) and isinstance(
                                arg0.value, str):
                            events.add(arg0.value)
                        elif isinstance(arg0, ast.Str):
                            events.add(arg0.s)
    return events


class _GreetLatchMirror:
    """Panda-free mirror of once-per-visit greet latch + re-arm rules."""

    def __init__(self):
        self._greetedZone = None
        self._zoneId = None
        self._inRange = False
        self._softNextStreet = None
        self._interactArmed = False
        self._promptShown = False

    def meet(self, zoneId):
        if self._greetedZone is not None and int(self._greetedZone) == int(
                zoneId):
            return False
        self._greetedZone = int(zoneId)
        self._interactArmed = False
        self._promptShown = False
        return True

    def on_zone_change(self, zoneId):
        self._inRange = False
        self._interactArmed = False
        self._promptShown = False
        self._greetedZone = None
        self._zoneId = int(zoneId)

    def on_enter_range(self, zoneId):
        if self._greetedZone is not None and int(self._greetedZone) == int(
                zoneId):
            return False
        self._inRange = True
        self._interactArmed = True
        self._promptShown = True
        return True

    def refresh_soft_next(self, street):
        self._softNextStreet = street

    def rearm_soft_next_greet(self):
        self._greetedZone = None
        if not self._inRange or self._zoneId is None:
            return
        self._interactArmed = True
        self._promptShown = True

    def on_act_unlocked(self, street):
        self.refresh_soft_next(street)
        self.rearm_soft_next_greet()


class OswaldPresenceGreetRearmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp = _load_panda_free_campaign()

    def test_soft_next_greet_copy_still_progress_aware(self):
        camp = self.camp
        tip = camp.oswaldPresenceGreetTip(
            TTC, cheered=True, softNextStreet='Punchline Place')
        self.assertIn('Punchline Place', tip)
        self.assertIn('Oswald', tip)
        self.assertIn('stretchy', tip.lower())
        self.assertIn('{street}', camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT)
        silly_tip = camp.oswaldPresenceGreetTip(
            TTC, cheered=True, softNextStreet=camp.ACTS[2]['name'])
        self.assertIn('half-beat off', silly_tip.lower())
        blob = ' '.join([
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT_SILLY,
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT_SILLY,
            tip,
            silly_tip,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade',
                       'cream_wash', 'cream wash', 'almost confess'):
            self.assertNotIn(banned, blob)

    def test_globals_doc_mentions_greet_rearm(self):
        src = _read('toontown/campaign/CampaignGlobals.py')
        block_start = src.index('OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT')
        # Comment sits just above the soft-next templates.
        preamble = src[max(0, block_start - 900):block_start]
        self.assertIn('_greetedZone', preamble)
        self.assertIn('campaignActUnlocked', preamble)
        self.assertIn('zone', preamble.lower())

    def test_presence_ast_rearm_wiring(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        methods = _class_method_names(
            _module_ast(rel), 'OswaldPresenceClient')
        for required in (
                '_onZoneChange',
                '_onCampaignActUnlocked',
                '_refreshSoftNextStreet',
                '_rearmSoftNextGreet',
                '_meetOswald',
                '_onEnterRange',
                '_armInteract',
                '_showInteractPrompt'):
            self.assertIn(required, methods)

        accepts = _accept_events(
            _module_ast(rel), 'OswaldPresenceClient')
        self.assertIn('localAvatarZoneChange', accepts)
        self.assertIn('campaignActUnlocked', accepts)

        zone_src = _method_source(
            rel, 'OswaldPresenceClient', '_onZoneChange')
        self.assertIn('self._greetedZone = None', zone_src)
        self.assertIn('self._inRange = False', zone_src)

        unlock_src = _method_source(
            rel, 'OswaldPresenceClient', '_onCampaignActUnlocked')
        self.assertIn('_refreshSoftNextStreet', unlock_src)
        self.assertIn('_rearmSoftNextGreet', unlock_src)

        rearm_src = _method_source(
            rel, 'OswaldPresenceClient', '_rearmSoftNextGreet')
        self.assertIn('self._greetedZone = None', rearm_src)
        self.assertIn('self._inRange', rearm_src)
        self.assertIn('_armInteract', rearm_src)
        self.assertIn('_showInteractPrompt', rearm_src)
        self.assertIn('shouldShowPresence', rearm_src)

        # Meet still latches once per visit until clear/re-arm.
        meet_src = _method_source(
            rel, 'OswaldPresenceClient', '_meetOswald')
        self.assertIn('self._greetedZone = int(zoneId)', meet_src)
        self.assertIn('softNextStreet=self._softNextStreet', meet_src)

        src_l = _read(rel).lower()
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('sora', src_l)
        self.assertNotIn('cream_wash', src_l)

    def test_greet_latch_mirror_zone_leave_and_unlock(self):
        mirror = _GreetLatchMirror()
        mirror.on_zone_change(TTC)
        self.assertTrue(mirror.on_enter_range(TTC))
        self.assertTrue(mirror.meet(TTC))
        self.assertEqual(mirror._greetedZone, TTC)
        # Same-zone re-meet blocked until leave / unlock re-arm.
        self.assertFalse(mirror.meet(TTC))
        self.assertFalse(mirror.on_enter_range(TTC))

        # Zone leave clears latch — re-entry arms E-talk again.
        mirror.on_zone_change(LOOPY)
        self.assertIsNone(mirror._greetedZone)
        mirror.on_zone_change(TTC)
        self.assertTrue(mirror.on_enter_range(TTC))
        self.assertTrue(mirror.meet(TTC))

        # Unlock while still in plaza re-arms soft-next E-talk.
        mirror.on_act_unlocked('Punchline Place')
        self.assertEqual(mirror._softNextStreet, 'Punchline Place')
        self.assertIsNone(mirror._greetedZone)
        self.assertTrue(mirror._interactArmed)
        self.assertTrue(mirror._promptShown)
        self.assertTrue(mirror.meet(TTC))


if __name__ == '__main__':
    unittest.main()
