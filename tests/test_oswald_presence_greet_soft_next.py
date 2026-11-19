#!/usr/bin/env python3
"""Headless tests: Oswald presence greet soft-next from oswaldCheered / unlocks.

Loads CampaignGlobals + CampaignProgressSave with a ToontownGlobals stub —
no Panda3D. Exercises oswaldPresenceGreetTip progress-aware plaza/street
copy and AST-locks OswaldPresence E-talk soft-next wiring after the #369
cheer latch.

Run from repo root:
  python3 tests/test_oswald_presence_greet_soft_next.py
  python3 -m unittest tests.test_oswald_presence_greet_soft_next -v
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


def _module_names(rel: str) -> set[str]:
    tree = _module_ast(rel)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
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
                        elif isinstance(arg0, ast.Call):
                            # accept(metMsgName()) / cheeredMsgName() etc.
                            if isinstance(arg0.func, ast.Name):
                                events.add(arg0.func.id)
    return events


class OswaldPresenceGreetSoftNextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save = _load_panda_free_campaign()

    def test_soft_next_greet_tunables(self):
        camp = self.camp
        self.assertIn('{street}', camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT)
        self.assertIn('{street}', camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_HUB_GREET_CHEERED)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_STREET_GREET_CHEERED)
        self.assertIn('reclaim', camp.OSWALD_PRESENCE_HUB_GREET_CHEERED.lower())
        self.assertIn(
            'packs', camp.OSWALD_PRESENCE_STREET_GREET_CHEERED.lower())
        # Pre-cheer static greets stay distinct from soft-next templates.
        self.assertNotEqual(
            camp.OSWALD_PRESENCE_HUB_GREET,
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT)
        self.assertNotEqual(
            camp.OSWALD_PRESENCE_STREET_GREET,
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT)
        blob = ' '.join([
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_HUB_GREET_CHEERED,
            camp.OSWALD_PRESENCE_STREET_GREET_CHEERED,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade',
                       'cream_wash', 'cream wash'):
            self.assertNotIn(banned, blob)

    def test_oswald_presence_greet_tip_helper(self):
        camp = self.camp
        greet = camp.oswaldPresenceGreetTip
        # Pre-cheer: static hub / street.
        self.assertEqual(greet(TTC), camp.OSWALD_PRESENCE_HUB_GREET)
        self.assertEqual(greet(LOOPY), camp.OSWALD_PRESENCE_STREET_GREET)
        self.assertEqual(
            greet(TTC, cheered=False), camp.OSWALD_PRESENCE_HUB_GREET)
        # Cheered, no soft-next yet (Act 1 cursor).
        self.assertEqual(
            greet(TTC, cheered=True),
            camp.OSWALD_PRESENCE_HUB_GREET_CHEERED)
        self.assertEqual(
            greet(LOOPY, cheered=True),
            camp.OSWALD_PRESENCE_STREET_GREET_CHEERED)
        # Cheered + soft-next street from unlocks (Punchline-tier unease).
        hub_soft = greet(
            TTC, cheered=True, softNextStreet='Punchline Place')
        street_soft = greet(
            LOOPY, cheered=True, softNextStreet='Punchline Place')
        self.assertIn('Punchline Place', hub_soft)
        self.assertIn('Punchline Place', street_soft)
        self.assertIn('Oswald', hub_soft)
        self.assertIn('Oswald', street_soft)
        self.assertIn('stretchy', hub_soft.lower())
        self.assertIn('half-beat', street_soft.lower())
        self.assertNotEqual(hub_soft, camp.OSWALD_PRESENCE_HUB_GREET)
        self.assertNotEqual(street_soft, camp.OSWALD_PRESENCE_STREET_GREET)
        # Finale soft-next deepens Silly-tier unease (no twist spoilers).
        finale = greet(
            TTC, cheered=True,
            softNextStreet=camp.ACTS[2]['name'])
        self.assertIn(camp.ACTS[2]['name'], finale)
        self.assertIn('half-beat off', finale.lower())
        self.assertNotEqual(hub_soft, finale)
        self.assertNotIn('almost confess', finale.lower())

    def test_soft_next_street_from_progress_feeds_greet(self):
        camp = self.camp
        save = self.save
        soft = save.softNextStreetFromProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'state': camp.STATE_ACTIVE,
        })
        self.assertEqual(soft, camp.ACTS[1]['name'])
        tip = camp.oswaldPresenceGreetTip(
            TTC, cheered=True, softNextStreet=soft)
        self.assertIn(soft, tip)
        # Fresh Act 1 — no soft-next; cheered fallback.
        self.assertIsNone(save.softNextStreetFromProgress({
            'unlockedThrough': 0, 'state': camp.STATE_IDLE}))
        tip0 = camp.oswaldPresenceGreetTip(
            TTC, cheered=True, softNextStreet=None)
        self.assertEqual(tip0, camp.OSWALD_PRESENCE_HUB_GREET_CHEERED)

    def test_presence_ast_soft_next_wiring(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        names = _module_names(rel)
        for required in (
                'greetTipForZone',
                'hubGreetSoftNextTip',
                'streetGreetSoftNextTip',
                'hubGreetCheeredTip',
                'streetGreetCheeredTip',
                'firstMeetTip'):
            self.assertIn(required, names)
        methods = _class_method_names(
            _module_ast(rel), 'OswaldPresenceClient')
        for required in (
                '_meetOswald',
                '_onCampaignProgressSync',
                '_onCampaignActUnlocked',
                '_refreshSoftNextStreet',
                '_onOswaldPresenceCheered',
                '_onOswaldCheeredSync'):
            self.assertIn(required, methods)
        src = _read(rel)
        self.assertIn('softNextStreet', src)
        self.assertIn('_softNextStreet', src)
        self.assertIn('_unlockedThrough', src)
        self.assertIn("accept('campaignActUnlocked'", src)
        self.assertIn('greetTipForZone(', src)
        self.assertIn('cheered=bool(self._oswaldCheered)', src)
        self.assertIn('softNextStreet=self._softNextStreet', src)
        self.assertIn('oswaldPresenceGreetTip', src)
        self.assertIn('_refreshSoftNextStreet', src)
        self.assertIn('softNextStreetFromProgress', src)
        # Preserve first-meet + cheer latch paths.
        self.assertIn('firstMeetTip()', src)
        self.assertIn('_oswaldCheered', src)
        self.assertIn('d_requestOswaldCheered', src)
        accepts = _accept_events(
            _module_ast(rel), 'OswaldPresenceClient')
        self.assertIn('campaignActUnlocked', accepts)
        src_l = src.lower()
        # Ban product KH/cream copy — docstring "no keyblades" is intentional.
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('sora', src_l)
        self.assertNotIn('cream_wash', src_l)

    def test_globals_helper_exported(self):
        camp = self.camp
        self.assertTrue(callable(camp.oswaldPresenceGreetTip))
        names = _module_names('toontown/campaign/CampaignGlobals.py')
        self.assertIn('oswaldPresenceGreetTip', names)
        for required in (
                'OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT',
                'OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT',
                'OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT_SILLY',
                'OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT_SILLY',
                'OSWALD_PRESENCE_HUB_GREET_CHEERED',
                'OSWALD_PRESENCE_STREET_GREET_CHEERED',
                'oswaldPresenceSoftNextUneaseTier',
                'oswaldPresenceSoftNextTemplates'):
            self.assertIn(required, names)

    def test_cheer_latch_still_persists(self):
        # Soft-next presentation must not drop #369 cheer sanitize.
        save = self.save
        blob = save.sanitizeProgress({
            'unlockedThrough': 1,
            'oswaldCheered': 1,
            'securedZones': [LOOPY],
        })
        self.assertEqual(blob['oswaldCheered'], 1)
        self.assertIn(LOOPY, blob['securedZones'])
        mirror = save.clientMirrorFromProgress(blob)
        self.assertEqual(mirror['oswaldCheered'], 1)
        self.assertEqual(mirror['softNextStreet'], self.camp.ACTS[1]['name'])


if __name__ == '__main__':
    unittest.main()
