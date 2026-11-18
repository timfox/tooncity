#!/usr/bin/env python3
"""Thin AST/unit tests for victory confetti Oswald twist sting.

Loads CampaignGlobals with a ToontownGlobals stub (no Panda3D). Asserts
VICTORY_TWIST_CONFETTI_* tunables, rubber-hose (non-KH) wiring on the
betrayal handoff plate, and VictoryTwistConfettiSting module presence.

Run from repo root:
  python3 tests/test_victory_twist_confetti_sting.py
  python3 -m unittest tests.test_victory_twist_confetti_sting -v
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
            'toontown.reclaim', 'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = 2000
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    # CampaignGlobals imports CorruptionGlobals / ReclaimGlobals transitively
    # via some paths; stub the minimal packages CampaignGlobals needs.
    cg_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    # CampaignGlobals only needs ToontownGlobals for zone ids.
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', cg_path)
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


class VictoryTwistConfettiStingTest(unittest.TestCase):
    """Pure-Python twist confetti sting wiring."""

    @classmethod
    def setUpClass(cls):
        cls.camp = _load_campaign_globals()
        cls.finale = None
        for act in cls.camp.ACTS:
            if act.get('finale'):
                cls.finale = act
                break

    def test_finale_betrayal_handoff_armed(self):
        self.assertIsNotNone(self.finale)
        self.assertTrue(self.finale.get('betrayalHandoff'))

    def test_twist_confetti_tunables_enabled(self):
        camp = self.camp
        self.assertIs(camp.VICTORY_TWIST_CONFETTI_ENABLED, True)
        self.assertGreater(camp.VICTORY_TWIST_CONFETTI_COUNT, 0)
        self.assertGreater(camp.VICTORY_TWIST_CONFETTI_SEC, 0.0)
        self.assertGreater(camp.VICTORY_TWIST_CONFETTI_FALL, 0.0)
        self.assertGreaterEqual(camp.VICTORY_TWIST_CONFETTI_DELAY_SEC, 0.0)
        self.assertGreater(len(camp.VICTORY_TWIST_CONFETTI_COLORS), 0)
        self.assertGreater(camp.VICTORY_TWIST_CONFETTI_STREAK_COUNT, 0)
        # Quieter / shorter than sunny victory cream swell.
        self.assertLess(
            camp.VICTORY_TWIST_CONFETTI_COUNT,
            camp.VICTORY_CREAM_CONFETTI_COUNT)
        self.assertLess(
            camp.VICTORY_TWIST_CONFETTI_SEC,
            camp.VICTORY_CREAM_CONFETTI_SEC)
        self.assertLess(
            camp.VICTORY_TWIST_CONFETTI_FLASH_PEAK,
            camp.VICTORY_CREAM_FLASH_PEAK)

    def test_no_kh_branding_in_module_docs(self):
        sting_src = _read(
            'toontown/campaign/VictoryTwistConfettiSting.py').lower()
        magic_src = _read(
            'toontown/campaign/MagicWords.py').lower()
        for banned in ('kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, sting_src)
            self.assertNotIn(banned, magic_src)
        # Hard ban allows the "no keyblades" disclaimer only.
        self.assertIn('no keyblades', sting_src)
        self.assertIn('no keyblades', magic_src)
        self.assertNotIn('keyblade ', sting_src.replace('no keyblades', ''))
        self.assertIn('oswald', sting_src)
        self.assertIn('corruption', sting_src)

    def test_sting_module_api(self):
        sting_rel = 'toontown/campaign/VictoryTwistConfettiSting.py'
        tree = _module_ast(sting_rel)
        funcs = _top_level_func_names(tree)
        self.assertIn('playVictoryTwistConfettiSting', funcs)
        self.assertIn('clearVictoryTwistConfettiSting', funcs)
        self.assertIn('ensureVictoryTwistConfettiSting', funcs)
        methods = _class_method_names(tree, 'VictoryTwistConfettiSting')
        self.assertIn('play', methods)
        self.assertIn('clear', methods)
        self.assertIn('_spawnConfetti', methods)
        self.assertIn('_spawnFlash', methods)
        sting_src = _read(sting_rel)
        self.assertIn('VICTORY_TWIST_CONFETTI_ENABLED', sting_src)
        self.assertIn('campaignVictoryTwistConfettiSting', sting_src)

    def test_handoff_wires_sting_on_betrayal(self):
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playVictoryTwistConfettiSting', handoff_src)
        self.assertIn('clearVictoryTwistConfettiSting', handoff_src)
        self.assertIn('VictoryTwistConfettiSting', handoff_src)
        self.assertIn('VICTORY_TWIST_CONFETTI_ORIGIN', handoff_src)
        # Sting lives on betrayalHandoff branch, not sunny creamSwell.
        betrayal_idx = handoff_src.find('if betrayalHandoff:')
        self.assertGreater(betrayal_idx, 0)
        cream_idx = handoff_src.find('elif creamSwell:', betrayal_idx)
        self.assertGreater(cream_idx, betrayal_idx)
        betrayal_snip = handoff_src[betrayal_idx:cream_idx]
        self.assertIn('playVictoryTwistConfettiSting', betrayal_snip)
        self.assertNotIn('playVictoryCreamSwell', betrayal_snip)

    def test_magic_words_mention_twist_confetti(self):
        magic_l = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('confetti twist sting', magic_l)
        self.assertIn('betrayal handoff', magic_l)


if __name__ == '__main__':
    unittest.main()
