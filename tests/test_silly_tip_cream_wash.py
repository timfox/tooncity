#!/usr/bin/env python3
"""Thin AST/unit tests for deepened Silly Overlord tip cream wash.

Loads CampaignGlobals with a ToontownGlobals stub (no Panda3D). Asserts
SILLY_ACT_TIP_CREAM_WASH_* deepen tunables, soft cream aftershock under the
tip bar, rubber-hose (non-KH) wiring on tipHose='silly', and
SillyTipCreamWashFx module presence. Distinct from victory twist sting
cream deepen (#244) and betrayal banner cream hose settle (#235); hose
settle deepen (#232) stays on the tip scale path.

Run from repo root:
  python3 tests/test_silly_tip_cream_wash.py
  python3 -m unittest tests.test_silly_tip_cream_wash -v
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


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_campaign_globals():
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


def _top_level_func_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


class SillyTipCreamWashDeepenTest(unittest.TestCase):
    """Pure-Python deepened Silly Overlord tip cream wash wiring."""

    @classmethod
    def setUpClass(cls):
        cls.camp = _load_campaign_globals()

    def test_wash_tunables_deepened(self):
        camp = self.camp
        self.assertIs(camp.SILLY_ACT_TIP_CREAM_WASH_ENABLED, True)
        self.assertIs(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ENABLED, True)
        # Juicier than #162 baseline (0.12 / 0.07 / 0.10 / 0.36 / no aftershock).
        self.assertGreaterEqual(float(camp.SILLY_ACT_TIP_CREAM_WASH_PEAK), 0.14)
        self.assertGreaterEqual(float(camp.SILLY_ACT_TIP_CREAM_WASH_MID), 0.08)
        self.assertGreaterEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_HOLD_SEC), 0.12)
        self.assertGreaterEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_OUT_SEC), 0.40)
        self.assertGreater(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COUNT, 0)
        self.assertGreater(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_SEC), 0.0)
        self.assertTrue(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_ENABLED)
        origin = camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ORIGIN
        self.assertEqual(len(origin), 3)
        # Tip-bar residual (bottom), not betrayal / victory plate.
        self.assertLess(float(origin[2]), 0.0)
        # Soft aftershock stays above wash bin.
        self.assertGreater(
            int(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_BIN),
            int(camp.SILLY_ACT_TIP_CREAM_WASH_BIN))
        # Distinct from victory twist aftershock (#244).
        twist_origin = camp.VICTORY_TWIST_CONFETTI_ORIGIN
        self.assertNotEqual(tuple(origin), tuple(twist_origin))
        self.assertNotEqual(
            int(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COUNT),
            int(camp.VICTORY_TWIST_CONFETTI_AFTERSHOCK_COUNT))
        self.assertNotEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_PEAK),
            float(camp.VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_PEAK))
        self.assertNotEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_FALL),
            float(camp.VICTORY_TWIST_CONFETTI_AFTERSHOCK_FALL))
        # Distinct from betrayal cream hose settle (#235) — different mechanism.
        self.assertNotEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_PEAK),
            float(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT[0]))
        self.assertNotEqual(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_SEC),
            float(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REST_SEC))
        # Quieter tip residual than sunny victory cream wash aftershock.
        self.assertLess(
            camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COUNT,
            camp.VICTORY_CREAM_AFTERSHOCK_COUNT)
        self.assertLess(
            float(camp.SILLY_ACT_TIP_CREAM_WASH_PEAK),
            float(camp.VICTORY_CREAM_WASH_PEAK))

    def test_no_kh_branding_in_module_docs(self):
        wash_src = _read(
            'toontown/campaign/SillyTipCreamWashFx.py').lower()
        magic_src = _read(
            'toontown/campaign/MagicWords.py').lower()
        for banned in ('kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, wash_src)
            self.assertNotIn(banned, magic_src)
        self.assertIn('no keyblades', wash_src)
        self.assertIn('no keyblades', magic_src)
        self.assertNotIn('keyblade ', wash_src.replace('no keyblades', ''))
        self.assertIn('overlord', wash_src)
        self.assertIn('foreshadow', wash_src)
        self.assertIn('aftershock', wash_src)
        self.assertIn('juicier', wash_src)

    def test_wash_module_api(self):
        wash_rel = 'toontown/campaign/SillyTipCreamWashFx.py'
        tree = _module_ast(wash_rel)
        funcs = _top_level_func_names(tree)
        self.assertIn('playSillyTipCreamWash', funcs)
        self.assertIn('clearSillyTipCreamWash', funcs)
        methods = _class_method_names(tree, 'SillyTipCreamWashPulse')
        for name in (
                'play',
                'clear',
                '_buildAftershock',
                '_spawnAftershockHalo',
                '_spawnAftershockFleck'):
            self.assertIn(name, methods, msg='missing %s' % name)
        wash_src = _read(wash_rel)
        self.assertIn('SILLY_ACT_TIP_CREAM_WASH_ENABLED', wash_src)
        self.assertIn('SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK', wash_src)
        self.assertIn('campaignSillyTipCreamWash', wash_src)
        self.assertIn('_buildAftershock', wash_src)
        # Does not own betrayal hose / victory twist sting keys.
        self.assertNotIn('FINALE_BETRAYAL_CREAM_HOSE_SETTLE', wash_src)
        self.assertNotIn('VICTORY_TWIST_CONFETTI', wash_src)

    def test_playentry_wires_wash_on_silly_tip(self):
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('playSillyTipCreamWash', play_src)
        self.assertIn('clearSillyTipCreamWash', play_src)
        self.assertIn('_armSillyTipCreamWash', play_src)
        tip_idx = play_src.find('def _tipHosePopInterval')
        self.assertGreater(tip_idx, 0)
        silly_idx = play_src.find("tipHose == 'silly'", tip_idx)
        self.assertGreater(silly_idx, tip_idx)
        # Wash arm lives beside tipHose='silly' land path.
        self.assertIn('_armSillyTipCreamWash', play_src[silly_idx:])

    def test_magic_words_mention_deepened_silly_tip_wash(self):
        magic_l = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('deepened soft cream wash pulse + cream aftershock', magic_l)
        self.assertIn('silly act 3 tip', magic_l)
        self.assertIn('overlord foreshadow', magic_l)

    def test_globals_comment_kh_free_and_distinct(self):
        src = _read('toontown/campaign/CampaignGlobals.py').lower()
        idx = src.find('silly_act_tip_cream_wash_enabled')
        self.assertGreater(idx, 0)
        snip = src[max(0, idx - 650):idx + 900]
        self.assertIn('no keyblades', snip)
        self.assertIn('juicier', snip)
        self.assertIn('aftershock', snip)
        self.assertIn('foreshadow', snip)
        self.assertIn('#244', snip)
        self.assertIn('#235', snip)
        for banned in ('kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, snip)


if __name__ == '__main__':
    unittest.main()
