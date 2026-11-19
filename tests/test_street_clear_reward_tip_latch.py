#!/usr/bin/env python3
"""Headless tests: wire streetClearReward into post-clear tip latch.

Loads CampaignGlobals / CampaignPower with a ToontownGlobals stub — no
Panda3D. Covers tip / emit helpers and AST locks that PlayEntry + Handoff
accept the formerly orphan CampaignPower messenger.

Run from repo root:
  python3 tests/test_street_clear_reward_tip_latch.py
  python3 -m unittest tests.test_street_clear_reward_tip_latch -v
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


def _load_panda_free_modules():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, REPO_ROOT.as_posix())

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.campaign',
            'toontown.hackslash'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = TTC
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    hs = types.ModuleType('toontown.hackslash.HackSlashConfig')
    hs.COMBO_DAMAGE = (8, 12, 28)
    sys.modules['toontown.hackslash.HackSlashConfig'] = hs
    sys.modules['toontown.hackslash'].HackSlashConfig = hs

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp

    power_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignPower.py'
    power_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignPower', power_path)
    power = importlib.util.module_from_spec(power_spec)
    assert power_spec.loader is not None
    sys.modules['toontown.campaign.CampaignPower'] = power
    power_spec.loader.exec_module(power)

    return camp, power


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


class StreetClearRewardTipLatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.power = _load_panda_free_modules()

    def test_globals_msg_and_helpers(self):
        camp = self.camp
        self.assertEqual(camp.STREET_CLEAR_REWARD_MSG, 'streetClearReward')
        self.assertEqual(
            camp.streetClearRewardMsgName(), 'streetClearReward')
        self.assertEqual(
            self.power.streetClearRewardMsgName(), 'streetClearReward')
        self.assertTrue(camp.STREET_CLEAR_REWARD_TIP_LATCH_ENABLED)
        self.assertTrue(camp.STREET_CLEAR_REWARD_ENABLED)
        tip = camp.streetClearRewardLatchTipText(
            face='Oswald', beans=20, laff=5, trophy='Street Trophy: Loopy Lane reclaimed!')
        self.assertIn('Oswald', tip)
        self.assertIn('Street Trophy', tip)
        self.assertIn('20', tip)
        self.assertIn('5', tip)
        self.assertIn('Loopy Lane', tip)
        # Named tip stays distinct from plate handoff line.
        self.assertNotEqual(tip, camp.STREET_CLEAR_REWARD_HANDOFF_FMT % (20, 5))
        bare = camp.streetClearRewardLatchTipText(
            face='Oswald', beans=20, laff=5)
        self.assertIn('Oswald', bare)
        self.assertIn('20', bare)
        self.assertNotIn('—', bare)

    def test_no_cream_or_kh_in_latch_globals(self):
        camp = self.camp
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        start = camp_src.index('STREET_CLEAR_REWARD_MSG =')
        end = camp_src.index('def streetClearRewardLatchTipText')
        block = camp_src[start:end].lower()
        self.assertNotIn('cream_wash', block)
        self.assertNotIn('sparkle', block)
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        tip_block = camp.streetClearRewardLatchTipText(
            face='Oswald', beans=20, laff=5,
            trophy='Street Trophy: Loopy Lane reclaimed!').lower()
        self.assertNotIn('keyblade', tip_block)
        self.assertNotIn('kingdom hearts', tip_block)
        blob = ' '.join([
            camp.STREET_CLEAR_REWARD_LATCH_TIP,
            camp.STREET_CLEAR_REWARD_LATCH_TIP_NAMED,
            camp.STREET_CLEAR_REWARD_HANDOFF_FMT,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'cream wash'):
            self.assertNotIn(banned, blob)

    def test_campaign_power_emits_street_clear_reward(self):
        rel = 'toontown/campaign/CampaignPower.py'
        src = _read(rel)
        self.assertIn('streetClearReward', src)
        self.assertIn('emitStreetClearReward', src)
        self.assertIn('streetClearRewardMsgName', src)
        self.assertIn('ensurePlayEntryClient', src)
        self.assertIn('ensureCampaignHandoffClient', src)
        self.assertIn('ensureClients=False', src)
        methods = set()
        tree = _module_ast(rel)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.add(node.name)
        self.assertIn('emitStreetClearReward', methods)
        self.assertIn('awardStreetClearReward', methods)
        # Scope KH check to the emit / award arm.
        start = src.index('def emitStreetClearReward')
        end = src.index('def streetClearLaff')
        block = src[start:end].lower()
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        award_idx = src.index('def awardStreetClearReward')
        award_block = src[award_idx:award_idx + 1600].lower()
        self.assertIn('emitstreetclearreward', award_block)
        self.assertIn('ensureclients=false', award_block)

    def test_play_entry_tip_latch_accept(self):
        rel = 'toontown/campaign/PlayEntry.py'
        methods = _class_method_names(
            _module_ast(rel), 'PlayEntryClient')
        self.assertIn('_onStreetClearReward', methods)
        src = _read(rel)
        self.assertIn('_onStreetClearReward', src)
        self.assertIn('STREET_CLEAR_REWARD_MSG', src)
        self.assertIn('STREET_CLEAR_REWARD_TIP_LATCH_ENABLED', src)
        self.assertIn('streetClearRewardLatchTipText', src)
        self.assertIn('streetClearReward', src)
        self.assertIn('_postClearRewardLatchedZone', src)
        tip_idx = src.index('def _onStreetClearReward')
        next_def = src.find('\n    def ', tip_idx + 10)
        block = src[tip_idx:next_def if next_def > 0 else tip_idx + 900]
        self.assertIn('_latchSoftNextCue', block)
        self.assertIn('_postClearRewardLatchedZone', block)
        block_l = block.lower()
        self.assertNotIn('keyblade', block_l)
        self.assertNotIn('kingdom hearts', block_l)
        self.assertNotIn('cream_wash', block_l)
        # Reclaim start clears the per-zone latch for the next clear.
        start_idx = src.index('def _onReclaimStart')
        start_next = src.find('\n    def ', start_idx + 10)
        start_block = src[start_idx:start_next if start_next > 0 else start_idx + 400]
        self.assertIn('_postClearRewardLatchedZone = None', start_block)

    def test_handoff_thin_accept_and_purity_mirror(self):
        rel = 'toontown/campaign/CampaignHandoff.py'
        methods = _class_method_names(
            _module_ast(rel), 'CampaignHandoffClient')
        self.assertIn('_onStreetClearReward', methods)
        self.assertIn('_emitStreetClearRewardMirror', methods)
        self.assertIn('_streetClearRewardLine', methods)
        src = _read(rel)
        self.assertIn('STREET_CLEAR_REWARD_MSG', src)
        self.assertIn('_onStreetClearReward', src)
        self.assertIn('_emitStreetClearRewardMirror', src)
        self.assertIn('emitStreetClearReward', src)
        self.assertIn('_streetClearRewardLatch', src)
        self.assertIn('streetClearReward', src)
        purity_idx = src.index('def _onPurityRestore')
        purity_next = src.find('\n    def ', purity_idx + 10)
        purity_win = src[purity_idx:purity_next if purity_next > 0 else purity_idx + 1200]
        self.assertIn('_emitStreetClearRewardMirror', purity_win)
        self.assertIn('_streetClearRewardLine', purity_win)
        accept_idx = src.index('def _onStreetClearReward')
        accept_next = src.find('\n    def ', accept_idx + 10)
        accept_block = src[
            accept_idx:accept_next if accept_next > 0 else accept_idx + 700].lower()
        self.assertNotIn('cream_wash', accept_block)
        self.assertNotIn('keyblade', accept_block)
        self.assertNotIn('kingdom hearts', accept_block)

    def test_globals_assign_names_locked(self):
        names = _toplevel_assign_names(
            _module_ast('toontown/campaign/CampaignGlobals.py'))
        for name in (
                'STREET_CLEAR_REWARD_MSG',
                'STREET_CLEAR_REWARD_TIP_LATCH_ENABLED',
                'STREET_CLEAR_REWARD_LATCH_TIP',
                'STREET_CLEAR_REWARD_LATCH_TIP_NAMED'):
            self.assertIn(name, names)


if __name__ == '__main__':
    unittest.main()
