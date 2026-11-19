#!/usr/bin/env python3
"""Headless tests: wire hubEpilogueBeatShown into post-wash tip latch.

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D. Covers tip /
soft-clear helpers and AST locks that PlayEntry + OswaldPresence accept the
formerly orphan HubEpilogueBeat messenger.

Run from repo root:
  python3 tests/test_hub_epilogue_beat_shown.py
  python3 -m unittest tests.test_hub_epilogue_beat_shown -v
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


def _toplevel_assign_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


class HubEpilogueBeatShownTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp = _load_panda_free_campaign()

    def test_globals_msg_and_helpers(self):
        camp = self.camp
        self.assertEqual(
            camp.HUB_EPILOGUE_BEAT_SHOWN_MSG, 'hubEpilogueBeatShown')
        self.assertEqual(
            camp.hubEpilogueBeatShownMsgName(), 'hubEpilogueBeatShown')
        self.assertTrue(camp.HUB_EPILOGUE_BEAT_TIP_LATCH_ENABLED)
        self.assertTrue(camp.HUB_EPILOGUE_BEAT_PRESENCE_CLEAR_ENABLED)
        tip = camp.hubEpilogueBeatLatchTipText(face='Oswald')
        self.assertIn('Oswald', tip)
        self.assertIn('plaza washed', tip.lower())
        self.assertIn('absence', tip.lower())
        self.assertIn('Loopy', tip)
        # World tip stays distinct from tip-bar latch copy.
        self.assertNotEqual(tip, camp.HUB_EPILOGUE_BEAT_TIP)
        self.assertIn('washed', camp.HUB_EPILOGUE_BEAT_LABEL.lower())

    def test_no_cream_or_kh_in_latch_globals(self):
        camp = self.camp
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        start = camp_src.index('HUB_EPILOGUE_BEAT_SHOWN_MSG')
        end = camp_src.index('def hubEpilogueBeatLatchTipText')
        block = camp_src[start:end].lower()
        self.assertNotIn('cream_wash', block)
        self.assertNotIn('sparkle', block)
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        tip_block = camp.hubEpilogueBeatLatchTipText(face='Oswald').lower()
        self.assertNotIn('keyblade', tip_block)
        self.assertNotIn('kingdom hearts', tip_block)
        blob = ' '.join([
            camp.HUB_EPILOGUE_BEAT_LATCH_TIP,
            camp.HUB_EPILOGUE_BEAT_TIP,
            camp.HUB_EPILOGUE_BEAT_ABSENCE,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'cream wash'):
            self.assertNotIn(banned, blob)

    def test_hub_epilogue_beat_sends_shown(self):
        rel = 'toontown/campaign/HubEpilogueBeat.py'
        src = _read(rel)
        self.assertIn('hubEpilogueBeatShown', src)
        self.assertIn('HUB_EPILOGUE_BEAT_SHOWN_MSG', src)
        self.assertIn('ensurePlayEntryClient', src)
        self.assertIn('ensureOswaldPresenceClient', src)
        methods = _class_method_names(
            _module_ast(rel), 'HubEpilogueBeatClient')
        self.assertIn('_onZoneChange', methods)
        self.assertIn('_flashTip', methods)
        # Scope KH check to the shown-send arm.
        start = src.index('self._placeMarkerNearAvatar()')
        end = src.index('def _progressWantsBeat', start)
        block = src[start:end].lower()
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        self.assertIn('ensureplayentryclient', block)
        self.assertIn('ensureoswaldpresenceclient', block)
        self.assertIn('hubepiloguebeatshown', block)

    def test_play_entry_tip_latch_accept(self):
        rel = 'toontown/campaign/PlayEntry.py'
        methods = _class_method_names(
            _module_ast(rel), 'PlayEntryClient')
        self.assertIn('_onHubEpilogueBeatShown', methods)
        src = _read(rel)
        self.assertIn('_onHubEpilogueBeatShown', src)
        self.assertIn('HUB_EPILOGUE_BEAT_SHOWN_MSG', src)
        self.assertIn('HUB_EPILOGUE_BEAT_TIP_LATCH_ENABLED', src)
        self.assertIn('hubEpilogueBeatLatchTipText', src)
        self.assertIn('hubEpilogueBeatShown', src)
        self.assertIn('_postWashTipLatched', src)
        tip_idx = src.index('def _onHubEpilogueBeatShown')
        next_def = src.find('\n    def ', tip_idx + 10)
        block = src[tip_idx:next_def if next_def > 0 else tip_idx + 700]
        self.assertIn('_latchSoftNextCue', block)
        self.assertIn('_postWashTipLatched', block)
        block_l = block.lower()
        self.assertNotIn('keyblade', block_l)
        self.assertNotIn('kingdom hearts', block_l)
        self.assertNotIn('cream_wash', block_l)

    def test_oswald_presence_soft_clear_accept(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        methods = _class_method_names(
            _module_ast(rel), 'OswaldPresenceClient')
        self.assertIn('_onHubEpilogueBeatShown', methods)
        self.assertIn('_onBetrayal', methods)
        src = _read(rel)
        self.assertIn('_onHubEpilogueBeatShown', src)
        self.assertIn('HUB_EPILOGUE_BEAT_SHOWN_MSG', src)
        self.assertIn('HUB_EPILOGUE_BEAT_PRESENCE_CLEAR_ENABLED', src)
        self.assertIn('hubEpilogueBeatShown', src)
        self.assertIn('_postWashCleared', src)
        tip_idx = src.index('def _onHubEpilogueBeatShown')
        next_def = src.find('\n    def ', tip_idx + 10)
        block = src[tip_idx:next_def if next_def > 0 else tip_idx + 500]
        self.assertIn('_onBetrayal', block)
        self.assertIn('_postWashCleared', block)
        block_l = block.lower()
        self.assertNotIn('keyblade', block_l)
        self.assertNotIn('kingdom hearts', block_l)
        self.assertNotIn('cream_wash', block_l)

    def test_globals_assign_names_locked(self):
        names = _toplevel_assign_names(
            _module_ast('toontown/campaign/CampaignGlobals.py'))
        for name in (
                'HUB_EPILOGUE_BEAT_SHOWN_MSG',
                'HUB_EPILOGUE_BEAT_TIP_LATCH_ENABLED',
                'HUB_EPILOGUE_BEAT_PRESENCE_CLEAR_ENABLED',
                'HUB_EPILOGUE_BEAT_LATCH_TIP'):
            self.assertIn(name, names)


if __name__ == '__main__':
    unittest.main()
