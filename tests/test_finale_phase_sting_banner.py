#!/usr/bin/env python3
"""Headless tests: wire finalePhaseStingBanner into phase-transition plate.

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D. Covers tip /
cue helpers and AST locks that CampaignHandoff + PlayEntry accept the
formerly orphan FinalePhaseFx messenger.

Run from repo root:
  python3 tests/test_finale_phase_sting_banner.py
  python3 -m unittest tests.test_finale_phase_sting_banner -v
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


class FinalePhaseStingBannerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp = _load_panda_free_campaign()

    def test_globals_msg_and_helpers(self):
        camp = self.camp
        self.assertEqual(
            camp.FINALE_PHASE_STING_BANNER_MSG, 'finalePhaseStingBanner')
        self.assertEqual(
            camp.finalePhaseStingMsgName(), 'finalePhaseStingBanner')
        self.assertTrue(camp.FINALE_PHASE_STING_PLATE_ENABLED)
        self.assertTrue(camp.FINALE_PHASE_STING_TIP_ENABLED)
        self.assertGreater(float(camp.FINALE_PHASE_STING_HOLD_SEC), 0.0)
        tip2 = camp.finalePhaseStingTipText(2, face='Oswald')
        self.assertIn('Oswald', tip2)
        self.assertIn('Unleashed', tip2)
        tip1 = camp.finalePhaseStingTipText(1, face='Oswald')
        self.assertIn('Rising', tip1)
        cue2 = camp.finalePhaseStingCueText(2)
        self.assertIn('Unleashed', cue2)
        # P2 banner / sub still authored for the plate.
        self.assertIn('UNLEASHED', camp.FINALE_PHASE_BANNER[2].upper())
        self.assertIn('hollow', camp.FINALE_PHASE_SUB[2].lower())

    def test_no_cream_or_kh_in_sting_globals(self):
        camp = self.camp
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        start = camp_src.index('FINALE_PHASE_STING_BANNER_MSG')
        end = camp_src.index('def finalePhaseStingCueText')
        block = camp_src[start:end].lower()
        self.assertNotIn('cream_wash', block)
        self.assertNotIn('sparkle', block)
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        tip_block = (
            camp.finalePhaseStingTipText(2) + ' ' +
            camp.finalePhaseStingCueText(2)).lower()
        self.assertNotIn('keyblade', tip_block)
        self.assertNotIn('kingdom hearts', tip_block)

    def test_finale_phase_fx_sends_sting_banner(self):
        rel = 'toontown/campaign/FinalePhaseFx.py'
        src = _read(rel)
        self.assertIn('finalePhaseStingBanner', src)
        self.assertIn('FINALE_PHASE_STING_BANNER_MSG', src)
        self.assertIn('ensureCampaignHandoffClient', src)
        self.assertIn('playTransition', src)
        methods = _class_method_names(
            _module_ast(rel), 'FinalePhaseFxClient')
        self.assertIn('playTransition', methods)
        # Scope KH check to the sting-banner send arm (module docstring
        # may say "no keyblades" as a product rule).
        start = src.index('title = CampaignGlobals.FINALE_PHASE_BANNER')
        end = src.index('self._ival = Sequence', start)
        block = src[start:end].lower()
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        self.assertIn('ensurecampaignhandoffclient', block)
        self.assertIn('finalephasestingbanner', block)

    def test_handoff_accepts_sting_banner_plate(self):
        rel = 'toontown/campaign/CampaignHandoff.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'CampaignHandoffClient')
        self.assertIn('_onFinalePhaseStingBanner', methods)
        self.assertIn('_showFinalePhaseStingPlate', methods)
        self.assertIn('_onPhase', methods)
        src = _read(rel)
        self.assertIn('FINALE_PHASE_STING_BANNER_MSG', src)
        self.assertIn('_onFinalePhaseStingBanner', src)
        self.assertIn('_showFinalePhaseStingPlate', src)
        self.assertIn('FINALE_PHASE_STING_PLATE_ENABLED', src)
        self.assertIn('emitHandoffCue=False', src)
        self.assertIn('finalePhaseStingBanner', src)
        # P2 still skipped on campaignPhase — sting owns that plate.
        on_phase = None
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == 'CampaignHandoffClient':
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == '_onPhase':
                        on_phase = item
                        break
        self.assertIsNotNone(on_phase)
        phase_src = ast.get_source_segment(src, on_phase) or ''
        self.assertIn('phase >= 2', phase_src)
        src_l = src.lower()
        # Accept path itself must stay cream-deepen / KH free.
        accept_idx = src.index('_onFinalePhaseStingBanner')
        plate_idx = src.index('def _celebrate', accept_idx)
        block = src[accept_idx:plate_idx].lower()
        self.assertNotIn('cream_wash', block)
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)

    def test_play_entry_thin_tip_accept(self):
        rel = 'toontown/campaign/PlayEntry.py'
        methods = _class_method_names(
            _module_ast(rel), 'PlayEntryClient')
        self.assertIn('_onFinalePhaseStingBanner', methods)
        src = _read(rel)
        self.assertIn('_onFinalePhaseStingBanner', src)
        self.assertIn('FINALE_PHASE_STING_BANNER_MSG', src)
        self.assertIn('FINALE_PHASE_STING_TIP_ENABLED', src)
        self.assertIn('finalePhaseStingTipText', src)
        self.assertIn('finalePhaseStingBanner', src)
        # Tip only — no soft-next latch on this path.
        tip_idx = src.index('def _onFinalePhaseStingBanner')
        next_def = src.find('\n    def ', tip_idx + 10)
        block = src[tip_idx:next_def if next_def > 0 else tip_idx + 500]
        self.assertIn('_showTip', block)
        self.assertNotIn('_latchSoftNextCue', block)
        block_l = block.lower()
        self.assertNotIn('keyblade', block_l)
        self.assertNotIn('kingdom hearts', block_l)

    def test_globals_assign_names_locked(self):
        names = _toplevel_assign_names(
            _module_ast('toontown/campaign/CampaignGlobals.py'))
        for name in (
                'FINALE_PHASE_STING_BANNER_MSG',
                'FINALE_PHASE_STING_PLATE_ENABLED',
                'FINALE_PHASE_STING_TIP_ENABLED',
                'FINALE_PHASE_STING_HOLD_SEC',
                'FINALE_PHASE_STING_TIP',
                'FINALE_PHASE_STING_CUE'):
            self.assertIn(name, names)


if __name__ == '__main__':
    unittest.main()
