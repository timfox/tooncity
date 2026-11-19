#!/usr/bin/env python3
"""Headless tests: wire pollutionRecreeping into post-recreep tip latch.

Loads CorruptionGlobals with a ToontownGlobals stub — no Panda3D. Covers tip
helpers and AST locks that PlayEntry + DistributedReclaimDirector accept the
formerly orphan PollutionManagerAI messenger (plus client DC rebroadcast).

Run from repo root:
  python3 tests/test_pollution_recreeping_tip_latch.py
  python3 -m unittest tests.test_pollution_recreeping_tip_latch -v
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


def _load_corruption_globals():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, REPO_ROOT.as_posix())

    for pkg in ('toontown', 'toontown.toonbase', 'toontown.corruption'):
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
    return cg


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


class PollutionRecreepingTipLatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_globals_msg_and_helpers(self):
        cg = self.cg
        self.assertEqual(cg.POLLUTION_RECREEPING_MSG, 'pollutionRecreeping')
        self.assertEqual(
            cg.pollutionRecreepingMsgName(), 'pollutionRecreeping')
        self.assertTrue(cg.POLLUTION_RECREEP_TIP_LATCH_ENABLED)
        self.assertTrue(cg.POLLUTION_RECREEP_ENABLED)
        tip = cg.pollutionRecreepLatchTipText(face='Oswald')
        self.assertIn('Oswald', tip)
        self.assertIn('creeping', tip.lower())
        self.assertIn('reclaim', tip.lower())
        pressure = cg.pollutionRecreepPressureTipText(zoneId=LOOPY)
        self.assertIn('creeping', pressure.lower())
        self.assertIn('reclaim', pressure.lower())
        # Latch tip stays distinct from system whisper + meter pressure tip.
        self.assertNotEqual(tip, cg.POLLUTION_RECREEP_MSG)
        self.assertNotEqual(pressure, tip)
        self.assertAlmostEqual(
            cg.POLLUTION_RECREEP_PRESSURE_TIP_HOLD_SEC, 2.4, places=2)

    def test_no_cream_or_kh_in_latch_globals(self):
        cg = self.cg
        src = _read('toontown/corruption/CorruptionGlobals.py')
        start = src.index('POLLUTION_RECREEPING_MSG =')
        end = src.index('STREET_PURITY_LOCK_ENABLED')
        block = src[start:end].lower()
        self.assertNotIn('cream_wash', block)
        self.assertNotIn('sparkle', block)
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)
        tip_block = cg.pollutionRecreepLatchTipText(face='Oswald').lower()
        self.assertNotIn('keyblade', tip_block)
        self.assertNotIn('kingdom hearts', tip_block)
        blob = ' '.join([
            cg.POLLUTION_RECREEP_MSG,
            cg.POLLUTION_RECREEP_LATCH_TIP,
            cg.POLLUTION_RECREEP_PRESSURE_TIP,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'cream wash'):
            self.assertNotIn(banned, blob)

    def test_pollution_manager_ai_emits_named_messenger(self):
        rel = 'toontown/corruption/PollutionManagerAI.py'
        methods = _class_method_names(
            _module_ast(rel), 'PollutionManagerAI')
        self.assertIn('_emitPollutionRecreeping', methods)
        self.assertIn('__recreepTick', methods)
        src = _read(rel)
        self.assertIn('pollutionRecreepingMsgName', src)
        self.assertIn('_emitPollutionRecreeping', src)
        self.assertIn('announcePollutionRecreeping', src)
        tick_idx = src.index('def __recreepTick')
        tick_next = src.find('\n    def ', tick_idx + 10)
        tick_block = src[tick_idx:tick_next if tick_next > 0 else tick_idx + 1200]
        self.assertIn('_emitPollutionRecreeping', tick_block)
        emit_idx = src.index('def _emitPollutionRecreeping')
        emit_next = src.find('\n    def ', emit_idx + 10)
        emit_block = src[
            emit_idx:emit_next if emit_next > 0 else emit_idx + 900].lower()
        self.assertIn('announcepollutionrecreeping', emit_block)
        self.assertNotIn('keyblade', emit_block)
        self.assertNotIn('kingdom hearts', emit_block)
        self.assertNotIn('cream_wash', emit_block)

    def test_pollution_manager_client_rebroadcast(self):
        rel = 'toontown/corruption/PollutionManager.py'
        methods = _class_method_names(
            _module_ast(rel), 'PollutionManager')
        self.assertIn('announcePollutionRecreeping', methods)
        src = _read(rel)
        self.assertIn('announcePollutionRecreeping', src)
        self.assertIn('pollutionRecreepingMsgName', src)
        ann_idx = src.index('def announcePollutionRecreeping')
        ann_next = src.find('\n    def ', ann_idx + 10)
        ann_block = src[
            ann_idx:ann_next if ann_next > 0 else ann_idx + 900].lower()
        self.assertIn('messenger.send', ann_block)
        self.assertNotIn('keyblade', ann_block)
        self.assertNotIn('cream_wash', ann_block)

    def test_play_entry_tip_latch_accept(self):
        rel = 'toontown/campaign/PlayEntry.py'
        methods = _class_method_names(
            _module_ast(rel), 'PlayEntryClient')
        self.assertIn('_onPollutionRecreeping', methods)
        src = _read(rel)
        self.assertIn('_onPollutionRecreeping', src)
        self.assertIn('POLLUTION_RECREEPING_MSG', src)
        self.assertIn('POLLUTION_RECREEP_TIP_LATCH_ENABLED', src)
        self.assertIn('pollutionRecreepLatchTipText', src)
        self.assertIn('pollutionRecreeping', src)
        self.assertIn('_postRecreepLatchedZone', src)
        tip_idx = src.index('def _onPollutionRecreeping')
        next_def = src.find('\n    def ', tip_idx + 10)
        block = src[tip_idx:next_def if next_def > 0 else tip_idx + 900]
        self.assertIn('_latchSoftNextCue', block)
        self.assertIn('_postRecreepLatchedZone', block)
        block_l = block.lower()
        self.assertNotIn('keyblade', block_l)
        self.assertNotIn('kingdom hearts', block_l)
        self.assertNotIn('cream_wash', block_l)
        # Reclaim start clears the per-zone latch for the next recreep.
        start_idx = src.index('def _onReclaimStart')
        start_next = src.find('\n    def ', start_idx + 10)
        start_block = src[start_idx:start_next if start_next > 0 else start_idx + 400]
        self.assertIn('_postRecreepLatchedZone = None', start_block)

    def test_reclaim_director_pressure_tip_accept(self):
        rel = 'toontown/reclaim/DistributedReclaimDirector.py'
        methods = _class_method_names(
            _module_ast(rel), 'DistributedReclaimDirector')
        self.assertIn('__onPollutionRecreeping', methods)
        src = _read(rel)
        self.assertIn('pollutionRecreepingMsgName()', src)
        self.assertIn('__onPollutionRecreeping', src)
        self.assertIn('pollutionRecreepPressureTipText', src)
        self.assertIn('POLLUTION_RECREEP_TIP_LATCH_ENABLED', src)
        accept_idx = src.index('def __onPollutionRecreeping')
        accept_next = src.find('\n    def ', accept_idx + 10)
        accept_block = src[
            accept_idx:accept_next if accept_next > 0 else accept_idx + 900]
        self.assertIn('__showPressureTip', accept_block)
        self.assertIn('warnPressure', accept_block)
        accept_l = accept_block.lower()
        self.assertNotIn('cream_wash', accept_l)
        self.assertNotIn('keyblade', accept_l)
        self.assertNotIn('kingdom hearts', accept_l)

    def test_dc_announce_pollution_recreeping(self):
        dc = _read('etc/toon.dc')
        self.assertIn('announcePollutionRecreeping', dc)
        # Stay inside the PollutionManager dclass block.
        start = dc.index('dclass PollutionManager')
        end = dc.index('dclass DistributedCorruptToon')
        block = dc[start:end]
        self.assertIn('announcePollutionRecreeping', block)
        self.assertIn('broadcast', block)

    def test_globals_assign_names_locked(self):
        names = _toplevel_assign_names(
            _module_ast('toontown/corruption/CorruptionGlobals.py'))
        for name in (
                'POLLUTION_RECREEPING_MSG',
                'POLLUTION_RECREEP_TIP_LATCH_ENABLED',
                'POLLUTION_RECREEP_LATCH_TIP',
                'POLLUTION_RECREEP_PRESSURE_TIP',
                'POLLUTION_RECREEP_PRESSURE_TIP_HOLD_SEC'):
            self.assertIn(name, names)


if __name__ == '__main__':
    unittest.main()
