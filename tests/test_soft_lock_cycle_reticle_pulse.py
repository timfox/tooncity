#!/usr/bin/env python3
"""Behavioral headless tests for soft-lock cycle reticle pulse helpers.

Loads HackSlashConfig.softLockCyclePulseScaleKeys without Panda3D. Covers
cycle pulse tunables and scale keyframes used by HitJuice.playSoftLockCyclePulse
/ SoftLockReticleFx.playCyclePulse when Tab/` switches soft-lock (#189).

Run from repo root:
  python3 tests/test_soft_lock_cycle_reticle_pulse.py
  python3 -m unittest tests.test_soft_lock_cycle_reticle_pulse -v
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


def _load_cycle_pulse_helpers():
    """Load HackSlashConfig cycle pulse helpers without MeleeCombat."""
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


class SoftLockCycleReticlePulseTest(unittest.TestCase):
    """Config + pure helper checks for Tab/` cycle reticle pulse."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_cycle_pulse_helpers()

    def test_config_cycle_pulse_tunables(self):
        self.assertTrue(self.cfg.SOFT_LOCK_CYCLE_PULSE_ENABLED)
        squash = self.cfg.SOFT_LOCK_CYCLE_PULSE_SQUASH
        stretch = self.cfg.SOFT_LOCK_CYCLE_PULSE_STRETCH
        self.assertEqual(len(squash), 4)
        self.assertEqual(len(stretch), 4)
        self.assertGreater(squash[3], 0.0)
        self.assertGreater(stretch[3], 0.0)
        self.assertGreater(self.cfg.SOFT_LOCK_CYCLE_PULSE_SETTLE_SEC, 0.0)
        # Cycle pulse is snappier than full acquire hose pop.
        acquire_total = (
            self.cfg.SOFT_LOCK_RETICLE_SQUASH[3]
            + self.cfg.SOFT_LOCK_RETICLE_STRETCH[3]
            + self.cfg.SOFT_LOCK_RETICLE_SETTLE_SEC)
        cycle_total = (
            squash[3] + stretch[3] + self.cfg.SOFT_LOCK_CYCLE_PULSE_SETTLE_SEC)
        self.assertLess(cycle_total, acquire_total)
        self.assertLess(cycle_total, 0.25)
        # Milder squash / stretch than acquire pop.
        self.assertLess(squash[0], self.cfg.SOFT_LOCK_RETICLE_SQUASH[0])
        self.assertLess(stretch[2], self.cfg.SOFT_LOCK_RETICLE_STRETCH[2])
        # Short cream ring — quieter/faster than acquire ring.
        self.assertTrue(self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_ENABLED)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_PEAK,
            self.cfg.SOFT_LOCK_PULSE_RING_PEAK)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_SEC,
            self.cfg.SOFT_LOCK_PULSE_RING_SEC)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_PEAK_ALPHA,
            self.cfg.SOFT_LOCK_PULSE_RING_PEAK_ALPHA)
        self.assertIn('Tab/` soft-lock cycle pulse', self.cfg.DEMO_HINT)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_soft_lock_cycle_pulse_scale_keys(self):
        keys = self.cfg.softLockCyclePulseScaleKeys
        settle, squash, stretch = keys(1.0)
        self.assertEqual(settle, (1.0, 1.0, 1.0))
        sx, sy, sz, _ = self.cfg.SOFT_LOCK_CYCLE_PULSE_SQUASH
        tx, ty, tz, _ = self.cfg.SOFT_LOCK_CYCLE_PULSE_STRETCH
        self.assertAlmostEqual(squash[0], sx)
        self.assertAlmostEqual(squash[1], sy)
        self.assertAlmostEqual(squash[2], sz)
        self.assertAlmostEqual(stretch[0], tx)
        self.assertAlmostEqual(stretch[1], ty)
        self.assertAlmostEqual(stretch[2], tz)
        # Default settle follows reticle settle scale.
        d_settle, d_squash, _d_stretch = keys()
        base = float(self.cfg.SOFT_LOCK_RETICLE_SETTLE_SCALE)
        self.assertAlmostEqual(d_settle[0], base)
        self.assertAlmostEqual(d_squash[0], base * sx)
        # Zero-ish settle still clamps above zero.
        z_settle, z_squash, z_stretch = keys(0.0)
        self.assertGreater(z_settle[0], 0.0)
        self.assertGreater(z_squash[0], 0.0)
        self.assertGreater(z_stretch[0], 0.0)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockCycleReticlePulseTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
