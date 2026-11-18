#!/usr/bin/env python3
"""Behavioral headless tests for soft-lock hit-assist aim nudge helpers.

Imports SoftTarget assist helpers with a stub package path (no Panda3D).
Covers signed yaw delta, capped assist nudge, and shouldAssistAimOnHit gate
used by MeleeCombatController._assistAimOnHit on melee connect.

Run from repo root:
  python3 tests/test_soft_lock_hit_assist.py
  python3 -m unittest tests.test_soft_lock_hit_assist -v
"""

from __future__ import annotations

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


class SoftLockHitAssistTest(unittest.TestCase):
    """Table-driven yaw assist math / gate for soft-lock hit nudge."""

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
        self.assertIn('hit soft-lock aim', self.cfg.DEMO_HINT)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

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


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockHitAssistTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
