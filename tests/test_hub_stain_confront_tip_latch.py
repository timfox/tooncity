#!/usr/bin/env python3
"""Headless tests: wire hubStainConfrontShown into PlayEntry tip latch.

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D. Covers tip
helpers and AST locks that PlayEntry accepts the formerly orphan
HubStainConfront messenger (orphan → accept; no cream / no KH).

Run from repo root:
  python3 tests/test_hub_stain_confront_tip_latch.py
  python3 -m unittest tests.test_hub_stain_confront_tip_latch -v
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


class HubStainConfrontTipLatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp = _load_panda_free_campaign()

    def test_globals_msg_and_helpers(self):
        camp = self.camp
        self.assertEqual(
            camp.HUB_STAIN_CONFRONT_SHOWN_MSG, 'hubStainConfrontShown')
        self.assertEqual(
            camp.hubStainConfrontShownMsgName(), 'hubStainConfrontShown')
        self.assertTrue(camp.HUB_STAIN_CONFRONT_TIP_LATCH_ENABLED)
        self.assertTrue(camp.HUB_STAIN_CONFRONT_ENABLED)
        tip = camp.hubStainConfrontLatchTipText(face='Oswald')
        self.assertIn('Oswald', tip)
        self.assertIn('plaza', tip.lower())
        self.assertIn('betrayal chase', tip.lower())
        self.assertIn('stain', tip.lower())
        # Must not claim wash early (chase still pending).
        self.assertNotIn('washed', tip.lower())
        self.assertNotIn('absence', tip.lower())
        # World tip stays distinct from tip-bar latch copy.
        self.assertNotEqual(tip, camp.HUB_STAIN_CONFRONT_TIP)
        self.assertIn('Oswald', camp.HUB_STAIN_CONFRONT_LABEL)

    def test_no_cream_or_kh_in_latch_globals(self):
        camp = self.camp
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        start = camp_src.index('HUB_STAIN_CONFRONT_SHOWN_MSG')
        end = camp_src.index('HUB_EPILOGUE_BEAT_ENABLED')
        block = camp_src[start:end].lower()
        self.assertNotIn('cream_wash', block)
        self.assertNotIn('sparkle', block)
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        tip_block = camp.hubStainConfrontLatchTipText(face='Oswald').lower()
        self.assertNotIn('keyblade', tip_block)
        self.assertNotIn('kingdom hearts', tip_block)
        blob = ' '.join([
            camp.HUB_STAIN_CONFRONT_LATCH_TIP,
            camp.HUB_STAIN_CONFRONT_TIP,
            camp.HUB_STAIN_CONFRONT_LABEL,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'cream wash'):
            self.assertNotIn(banned, blob)

    def test_hub_stain_confront_sends_shown(self):
        rel = 'toontown/campaign/HubStainConfront.py'
        src = _read(rel)
        self.assertIn('hubStainConfrontShown', src)
        self.assertIn('HUB_STAIN_CONFRONT_SHOWN_MSG', src)
        self.assertIn('ensurePlayEntryClient', src)
        methods = _class_method_names(
            _module_ast(rel), 'HubStainConfrontClient')
        self.assertIn('_refreshForHubPollution', methods)
        self.assertIn('_flashTip', methods)
        # Scope KH check to the shown-send arm (placemarker → shown msg).
        start = src.index('self._placeMarker()')
        end = src.index('def _progressWantsConfront', start)
        block = src[start:end].lower()
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        self.assertIn('ensureplayentryclient', block)
        self.assertIn('hubstainconfrontshown', block)
        self.assertIn('messenger.send', block)

    def test_play_entry_tip_latch_accept(self):
        rel = 'toontown/campaign/PlayEntry.py'
        methods = _class_method_names(
            _module_ast(rel), 'PlayEntryClient')
        self.assertIn('_onHubStainConfrontShown', methods)
        src = _read(rel)
        self.assertIn('_onHubStainConfrontShown', src)
        self.assertIn('HUB_STAIN_CONFRONT_SHOWN_MSG', src)
        self.assertIn('HUB_STAIN_CONFRONT_TIP_LATCH_ENABLED', src)
        self.assertIn('hubStainConfrontLatchTipText', src)
        self.assertIn('hubStainConfrontShown', src)
        self.assertIn('_postConfrontTipLatched', src)
        tip_idx = src.index('def _onHubStainConfrontShown')
        next_def = src.find('\n    def ', tip_idx + 10)
        block = src[tip_idx:next_def if next_def > 0 else tip_idx + 900]
        self.assertIn('_latchSoftNextCue', block)
        self.assertIn('_postConfrontTipLatched', block)
        self.assertIn('_chasePending = True', block)
        # Soft-next must not point at Loopy (would invite Act 1 mid-chase).
        self.assertNotIn("ACTS[0]", block)
        block_l = block.lower()
        self.assertNotIn('keyblade', block_l)
        self.assertNotIn('kingdom hearts', block_l)
        self.assertNotIn('cream_wash', block_l)
        # Wash / epilogue clears confront latch.
        wash_idx = src.index('def _onHubEpilogueBeatShown')
        wash_next = src.find('\n    def ', wash_idx + 10)
        wash_block = src[wash_idx:wash_next if wash_next > 0 else wash_idx + 700]
        self.assertIn('_postConfrontTipLatched = False', wash_block)

    def test_globals_assign_names_locked(self):
        names = _toplevel_assign_names(
            _module_ast('toontown/campaign/CampaignGlobals.py'))
        for name in (
                'HUB_STAIN_CONFRONT_SHOWN_MSG',
                'HUB_STAIN_CONFRONT_TIP_LATCH_ENABLED',
                'HUB_STAIN_CONFRONT_LATCH_TIP'):
            self.assertIn(name, names)


if __name__ == '__main__':
    unittest.main()
