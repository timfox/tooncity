#!/usr/bin/env python3
"""Headless tests: server melee hit cadence, earned counters, planar range.

Locks HackSlashConfig integrity helpers and CorruptToonAI requestHackSlashHit
wiring so clients cannot spoof finisher hitIndex every RPC, set
MELEE_COUNTER_FLAG_PERFECT_DODGE without a server-armed latch, or hit from
any planar distance in-zone. No Panda3D required.

Run from repo root:
  python3 tests/test_server_melee_hit_cadence.py
  python3 -m unittest tests.test_server_melee_hit_cadence -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_config():
    """Load HackSlashConfig without importing MeleeCombat / Panda3D."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.hackslash'):
        _ensure_pkg(pkg)

    cfg_path = REPO_ROOT / 'toontown' / 'hackslash' / 'HackSlashConfig.py'
    cfg_spec = importlib.util.spec_from_file_location(
        'toontown.hackslash.HackSlashConfig', cfg_path)
    cfg = importlib.util.module_from_spec(cfg_spec)
    assert cfg_spec.loader is not None
    sys.modules['toontown.hackslash.HackSlashConfig'] = cfg
    cfg_spec.loader.exec_module(cfg)
    sys.modules['toontown.hackslash'].HackSlashConfig = cfg
    return cfg


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel))


def _class_method(tree: ast.AST, class_name: str, method_name: str):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if (isinstance(child, ast.FunctionDef)
                        and child.name == method_name):
                    return child
    return None


def _class_method_names(tree: ast.AST, class_name: str) -> set:
    names = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    names.add(child.name)
    return names


class ServerMeleeHitCadenceTest(unittest.TestCase):
    """Cadence / combo / earned-counter / planar-range integrity helpers."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_config()

    def test_cadence_ready_respects_min_gap(self):
        ready = self.cfg.isMeleeHitCadenceReady
        gap = float(self.cfg.MELEE_HIT_MIN_GAP_SEC)
        self.assertTrue(ready(0.0, 1.0))
        self.assertTrue(ready(1.0, 1.0 + gap))
        self.assertFalse(ready(1.0, 1.0 + gap * 0.5))
        self.assertTrue(ready(1.0, 1.0 + gap, minGap=0.0))

    def test_combo_sequence_blocks_finisher_spam(self):
        expected = self.cfg.expectedMeleeComboHitIndex
        accept = self.cfg.acceptMeleeHitIndex
        hold = float(self.cfg.MELEE_HIT_COMBO_HOLD_SEC)
        # Fresh string expects opener.
        self.assertEqual(expected(-1, 0.0, 10.0), 0)
        self.assertTrue(accept(0, 0))
        self.assertFalse(accept(2, 0))
        # After opener, mid is next; finisher without mid is rejected.
        self.assertEqual(expected(0, 1.0, 1.2), 1)
        self.assertTrue(accept(1, 1))
        self.assertFalse(accept(2, 1))
        # After mid, finisher is next; then string resets.
        self.assertEqual(expected(1, 1.0, 1.2), 2)
        self.assertTrue(accept(2, 2))
        self.assertEqual(expected(2, 1.0, 1.2), 0)
        # Hold expiry resets to opener.
        self.assertEqual(expected(1, 1.0, 1.0 + hold + 0.01), 0)
        # Explicit opener always allowed (whiff / string reset).
        self.assertTrue(accept(0, 2))

    def test_earned_counter_strips_spoofed_perfect_dodge_bit(self):
        resolve = self.cfg.resolveEarnedCounterFlags
        flag = int(self.cfg.MELEE_COUNTER_FLAG_PERFECT_DODGE)
        # Spoofed bit with no latch → stripped.
        flags, consumed = resolve(flag, 0.0, 1.0)
        self.assertEqual(flags & flag, 0)
        self.assertFalse(consumed)
        # Live latch + client bit → kept and consumed.
        until = self.cfg.earnedCounterUntil(1.0, windowSec=0.5)
        flags, consumed = resolve(flag, until, 1.2)
        self.assertEqual(flags & flag, flag)
        self.assertTrue(consumed)
        # Expired latch → stripped.
        flags, consumed = resolve(flag, until, until + 0.01)
        self.assertEqual(flags & flag, 0)
        self.assertFalse(consumed)
        # No client bit → no consume even with live latch.
        flags, consumed = resolve(0, until, 1.2)
        self.assertEqual(flags & flag, 0)
        self.assertFalse(consumed)

    def test_planar_range_helper_applies_slack(self):
        reach = self.cfg.meleeHitPlanarRange()
        base = float(self.cfg.MELEE_HIT_PLANAR_RANGE)
        slack = float(self.cfg.MELEE_HIT_PLANAR_RANGE_SLACK)
        self.assertAlmostEqual(reach, base * slack, places=4)
        self.assertGreater(reach, base)
        self.assertAlmostEqual(
            self.cfg.meleeHitPlanarRange(baseRange=4.0, slack=1.0),
            4.0,
            places=4)

    def test_counter_flag_still_scales_when_earned(self):
        """Integrity helpers feed meleeDamageFromHitIndex — earned path works."""
        flag = int(self.cfg.MELEE_COUNTER_FLAG_PERFECT_DODGE)
        base = int(self.cfg.COMBO_DAMAGE[0])
        until = self.cfg.earnedCounterUntil(0.0, windowSec=1.0)
        flags, consumed = self.cfg.resolveEarnedCounterFlags(flag, until, 0.1)
        self.assertTrue(consumed)
        bumped = self.cfg.meleeDamageFromHitIndex(0, flags)
        self.assertEqual(
            bumped,
            self.cfg.perfectDodgeCounterOpenerDamage(base))
        # Spoofed path stays on baseline table entry.
        stripped, _ = self.cfg.resolveEarnedCounterFlags(flag, 0.0, 0.1)
        self.assertEqual(
            self.cfg.meleeDamageFromHitIndex(0, stripped),
            base)

    def test_no_kh_branding_in_integrity_helpers(self):
        src = _read('toontown/hackslash/HackSlashConfig.py')
        block = src.split('MELEE_HIT_CADENCE_ENABLED', 1)[1][:1200].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, block)
        self.assertIn('rubber-hose', block)
        helper_block = src.split(
            'def resolveEarnedCounterFlags', 1)[1][:500].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, helper_block)

    def test_ai_request_hit_wires_integrity_gates(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        src = _read(rel)
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for name in (
                'requestHackSlashHit',
                '__acceptMeleeHitIntegrity',
                '__meleeHitInPlanarRange',
                '__armEarnedCounter',
                '__armEarnedCounterForTelegraph',
                '__announceAttackDodged',
                '__meleeHitState'):
            self.assertIn(name, methods, msg='AI missing %s' % name)
        self.assertIn('_meleeHitStateByAv', src)
        req = _class_method(tree, 'DistributedCorruptToonAI', 'requestHackSlashHit')
        self.assertIsNotNone(req)
        req_src = ast.get_source_segment(src, req) or ''
        self.assertIn('__meleeHitInPlanarRange', req_src)
        self.assertIn('__acceptMeleeHitIntegrity', req_src)
        self.assertIn('meleeDamageFromHitIndex', req_src)
        self.assertIn('resolveEarnedCounterFlags', src)
        self.assertIn('expectedMeleeComboHitIndex', src)
        self.assertIn('isMeleeHitCadenceReady', src)
        self.assertIn('meleeHitPlanarRange', src)
        self.assertIn('__armEarnedCounterForTelegraph', src)
        # Dodge path arms earned latch (single-target + AoE sites).
        self.assertIn('__announceAttackDodged', src)
        self.assertGreater(src.count('__armEarnedCounter('), 4)

    def test_exports_and_config_toggles(self):
        self.assertTrue(self.cfg.MELEE_HIT_CADENCE_ENABLED)
        self.assertTrue(self.cfg.MELEE_HIT_RANGE_GATE_ENABLED)
        self.assertTrue(self.cfg.MELEE_EARNED_COUNTER_ENABLED)
        self.assertGreater(self.cfg.MELEE_HIT_MIN_GAP_SEC, 0.0)
        self.assertGreater(self.cfg.MELEE_HIT_COMBO_HOLD_SEC, 0.0)
        self.assertGreater(self.cfg.MELEE_HIT_PLANAR_RANGE, 0.0)
        init_src = _read('toontown/hackslash/__init__.py')
        for name in (
                'acceptMeleeHitIndex',
                'earnedCounterUntil',
                'earnedCounterWindowSec',
                'earnedTelegraphCounterUntil',
                'expectedMeleeComboHitIndex',
                'isMeleeHitCadenceReady',
                'meleeHitPlanarRange',
                'remapMeleeComboIndexOnSoftLockChange',
                'resolveEarnedCounterFlags'):
            self.assertIn(name, init_src)
        target = _read('toontown/corruption/HackSlashTarget.py')
        self.assertIn('earned counterFlags', target)
        self.assertIn('planar range', target.lower())


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ServerMeleeHitCadenceTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
