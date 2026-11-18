#!/usr/bin/env python3
"""Behavioral headless tests for soft-lock hit-assist aim nudge + cream deepen.

Imports SoftTarget assist helpers with a stub package path (no Panda3D).
Covers signed yaw delta, capped assist nudge, shouldAssistAimOnHit gate,
and deepened hit-assist cream wash tunables / AST wiring used by
MeleeCombatController._assistAimOnHit on melee connect.

Run from repo root:
  python3 tests/test_soft_lock_hit_assist.py
  python3 -m unittest tests.test_soft_lock_hit_assist -v
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


def _load_soft_target_helpers():
    """Load SoftTarget assist helpers without importing MeleeCombat / Panda."""
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

    soft_path = REPO_ROOT / 'toontown' / 'hackslash' / 'SoftTarget.py'
    soft_spec = importlib.util.spec_from_file_location(
        'toontown.hackslash.SoftTarget', soft_path)
    soft = importlib.util.module_from_spec(soft_spec)
    assert soft_spec.loader is not None
    sys.modules['toontown.hackslash.SoftTarget'] = soft
    soft_spec.loader.exec_module(soft)
    sys.modules['toontown.hackslash'].SoftTarget = soft
    return soft, cfg


def _module_ast(rel_path: str) -> ast.Module:
    src = (REPO_ROOT / rel_path).read_text(encoding='utf-8')
    return ast.parse(src, filename=rel_path)


def _class_names(tree: ast.AST) -> set[str]:
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


def _top_level_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in getattr(tree, 'body', []):
        if isinstance(node, ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.FunctionDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


class SoftLockHitAssistTest(unittest.TestCase):
    """Table-driven yaw assist math / gate + cream deepen for soft-lock hit nudge."""

    @classmethod
    def setUpClass(cls):
        cls.soft, cls.cfg = _load_soft_target_helpers()

    def test_config_hit_assist_tunables(self):
        self.assertTrue(self.cfg.LOCK_HIT_ASSIST_ENABLED)
        self.assertGreater(self.cfg.LOCK_HIT_ASSIST_YAW_FRAC, 0.0)
        self.assertLessEqual(self.cfg.LOCK_HIT_ASSIST_YAW_FRAC, 1.0)
        self.assertGreater(self.cfg.LOCK_HIT_ASSIST_YAW_MAX_DEG, 0.0)
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_YAW_MAX_DEG, 90.0)
        self.assertGreaterEqual(self.cfg.LOCK_HIT_ASSIST_CAM_FRAC, 0.0)
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CAM_FRAC,
            self.cfg.LOCK_HIT_ASSIST_YAW_FRAC)
        self.assertGreaterEqual(self.cfg.LOCK_HIT_ASSIST_DEADZONE_DEG, 0.0)
        # Deepened glue vs original #204 assist.
        self.assertGreaterEqual(self.cfg.LOCK_HIT_ASSIST_YAW_FRAC, 0.62)
        self.assertGreaterEqual(self.cfg.LOCK_HIT_ASSIST_YAW_MAX_DEG, 26.0)
        self.assertGreaterEqual(self.cfg.LOCK_HIT_ASSIST_CAM_FRAC, 0.34)
        self.assertIn('hit soft-lock aim cream deepen', self.cfg.DEMO_HINT)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_config_hit_assist_cream_wash_tunables(self):
        self.assertTrue(self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_ENABLED)
        self.assertTrue(self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_ENABLED)
        self.assertGreaterEqual(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC, 0.0)
        self.assertGreater(self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_PEAK, 0.0)
        self.assertGreater(self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_MID, 0.0)
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_MID,
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_PEAK)
        # Deepened readability: juicier assist cream flash.
        self.assertGreaterEqual(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_PEAK, 0.085)
        self.assertGreaterEqual(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_HOLD_SEC, 0.035)
        self.assertGreaterEqual(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_MID, 0.048)
        # Quieter / earlier than hit-connect wash — assists fire mid-combo.
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_PEAK,
            self.cfg.HIT_SPARK_CREAM_WASH_PEAK)
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC,
            self.cfg.HIT_SPARK_CREAM_WASH_DELAY_SEC)
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_BIN,
            self.cfg.HIT_SPARK_CREAM_WASH_BIN)
        # Distinct from soft-lock cycle reticle cream deepen (#233) — connect
        # assist flash (not Tab/` cycle settle).
        self.assertGreater(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_PEAK,
            self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_PEAK)
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC,
            self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_DELAY_SEC)
        # Distinct from hurt wash cream deepen (#247) — quieter/snappier glue
        # flash (not smack→recovery settle).
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_PEAK,
            self.cfg.HURT_STAGGER_CREAM_WASH_PEAK)
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC,
            self.cfg.HURT_STAGGER_CREAM_WASH_DELAY_SEC)
        # Quiet residual wash aftershock after the deepened veil.
        self.assertGreaterEqual(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_COUNT, 3)
        self.assertTrue(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_ENABLED)
        self.assertGreater(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_BIN,
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_BIN)
        wash_body = (
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_IN_SEC
            + self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_PULSE_SEC
            + self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_HOLD_SEC
            + self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_OUT_SEC)
        self.assertLess(
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_DELAY_SEC,
            wash_body)
        cream = self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_COLOR
        self.assertEqual(len(cream), 3)
        # Cream / pastel — no ink purple wash.
        self.assertGreaterEqual(cream[0], cream[2])
        self.assertGreaterEqual(cream[1], cream[2])

    def test_hit_assist_cream_wash_peak_helper(self):
        peak_fn = self.cfg.hitAssistCreamWashPeakAtSec
        self.assertAlmostEqual(
            peak_fn(),
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC
            + self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_IN_SEC)
        self.assertAlmostEqual(peak_fn(0.02, 0.05), 0.07)
        self.assertAlmostEqual(peak_fn(-1.0, 0.05), 0.05)

    def test_hit_assist_cream_wash_aftershock_helper(self):
        after_fn = self.cfg.hitAssistCreamWashAftershockAtSec
        self.assertAlmostEqual(
            after_fn(),
            self.cfg.LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_DELAY_SEC)
        self.assertAlmostEqual(after_fn(0.10), 0.10)
        self.assertAlmostEqual(after_fn(-1.0), 0.0)

    def test_signed_yaw_delta_wraparound(self):
        delta = self.soft.signedYawDeltaDeg
        self.assertAlmostEqual(delta(0.0, 10.0), 10.0)
        self.assertAlmostEqual(delta(10.0, 0.0), -10.0)
        self.assertAlmostEqual(delta(350.0, 10.0), 20.0)
        self.assertAlmostEqual(delta(10.0, 350.0), -20.0)
        # Exactly 180° lands on -180 (same heading); range is [-180, 180).
        self.assertAlmostEqual(delta(0.0, 180.0), -180.0)
        self.assertAlmostEqual(delta(0.0, 181.0), -179.0)

    def test_assist_aim_yaw_nudge_cap_and_deadzone(self):
        nudge = self.soft.assistAimYawNudge
        # Deadzone — already glued.
        self.assertEqual(nudge(1.5, frac=0.55, maxDeg=22.0, deadzoneDeg=2.0), 0.0)
        # Fractional close under cap.
        self.assertAlmostEqual(
            nudge(20.0, frac=0.5, maxDeg=22.0, deadzoneDeg=2.0), 10.0)
        # Hard cap — never snaps the full large error.
        self.assertAlmostEqual(
            nudge(80.0, frac=0.55, maxDeg=22.0, deadzoneDeg=2.0), 22.0)
        self.assertAlmostEqual(
            nudge(-80.0, frac=0.55, maxDeg=22.0, deadzoneDeg=2.0), -22.0)
        # Zero frac / max collapses assist.
        self.assertEqual(nudge(40.0, frac=0.0, maxDeg=22.0, deadzoneDeg=2.0), 0.0)
        self.assertEqual(nudge(40.0, frac=0.55, maxDeg=0.0, deadzoneDeg=2.0), 0.0)
        # Defaults pull from HackSlashConfig.
        expected = min(
            40.0 * self.cfg.LOCK_HIT_ASSIST_YAW_FRAC,
            self.cfg.LOCK_HIT_ASSIST_YAW_MAX_DEG)
        self.assertAlmostEqual(nudge(40.0), expected)

    def test_should_assist_aim_on_hit_gate(self):
        gate = self.soft.shouldAssistAimOnHit
        key_a = ('doId', 1)
        key_b = ('doId', 2)
        self.assertTrue(gate(key_a, key_a, enabled=True))
        self.assertFalse(gate(key_a, key_b, enabled=True))
        self.assertFalse(gate(key_a, None, enabled=True))
        self.assertFalse(gate(None, key_a, enabled=True))
        self.assertFalse(gate(key_a, key_a, enabled=False))
        # Default enabled follows config (True on develop).
        self.assertTrue(gate(key_a, key_a))

    def test_ast_hit_assist_cream_wash_fx(self):
        rel = 'toontown/hackslash/HitAssistCreamWashFx.py'
        tree = _module_ast(rel)
        names = _class_names(tree)
        self.assertIn('HitAssistCreamWashPulse', names)
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        self.assertIn('LOCK_HIT_ASSIST_CREAM_WASH_ENABLED', src)
        self.assertIn('LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_ENABLED', src)
        self.assertIn('_buildAftershock', src)
        self.assertIn('_spawnAftershockHalo', src)
        self.assertIn('_spawnAftershockFleck', src)
        # Ban phrasing only — no KH product names as branding.
        self.assertIn('no keyblades', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())
        # Distinct from cycle reticle / hurt wash deepen cues.
        self.assertIn('distinct from', src.lower())

    def test_ast_melee_wires_hit_assist_cream_wash(self):
        melee_rel = 'toontown/hackslash/MeleeCombat.py'
        melee_src = (REPO_ROOT / melee_rel).read_text(encoding='utf-8')
        self.assertIn('HitAssistCreamWashPulse', melee_src)
        self.assertIn('_playHitAssistCreamWash', melee_src)
        self.assertIn('_clearHitAssistCreamWash', melee_src)
        self.assertIn('self._playHitAssistCreamWash()', melee_src)

        init_rel = 'toontown/hackslash/__init__.py'
        init_src = (REPO_ROOT / init_rel).read_text(encoding='utf-8')
        self.assertIn('HitAssistCreamWashPulse', init_src)
        self.assertIn('hitAssistCreamWashPeakAtSec', init_src)
        self.assertIn('hitAssistCreamWashAftershockAtSec', init_src)

        cfg_names = _top_level_names(
            _module_ast('toontown/hackslash/HackSlashConfig.py'))
        for name in (
                'LOCK_HIT_ASSIST_CREAM_WASH_ENABLED',
                'LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC',
                'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_ENABLED',
                'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_COUNT',
                'hitAssistCreamWashPeakAtSec',
                'hitAssistCreamWashAftershockAtSec'):
            self.assertIn(name, cfg_names)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockHitAssistTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())