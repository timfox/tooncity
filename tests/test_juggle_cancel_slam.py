#!/usr/bin/env python3
"""Behavioral headless tests for air-juggle cancel→slam helpers.

Loads HackSlashConfig juggle-cancel helpers without Panda3D. Covers slam hit
index selection and cancel-window open checks used by MeleeCombatController.

Run from repo root:
  python3 tests/test_juggle_cancel_slam.py
  python3 -m unittest tests.test_juggle_cancel_slam -v
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


def _load_juggle_cancel_helpers():
    """Load HackSlashConfig juggle-cancel helpers without importing MeleeCombat."""
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


class JuggleCancelSlamTest(unittest.TestCase):
    """Config + pure helper checks for air-juggle cancel→slam."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_juggle_cancel_helpers()

    def test_config_juggle_cancel_tunables(self):
        self.assertTrue(self.cfg.JUGGLE_CANCEL_ENABLED)
        self.assertTrue(self.cfg.JUGGLE_CANCEL_BUFFER)
        self.assertGreater(self.cfg.JUGGLE_CANCEL_START_SEC, 0.0)
        self.assertGreater(self.cfg.JUGGLE_CANCEL_WINDOW_SEC, 0.0)
        # Timing lock (#196) — 0.12 rise lockout / 0.45 hang window.
        self.assertAlmostEqual(
            self.cfg.JUGGLE_CANCEL_START_SEC, 0.12, places=2)
        self.assertAlmostEqual(
            self.cfg.JUGGLE_CANCEL_WINDOW_SEC, 0.45, places=2)
        # Lockout ends around mid-juggle rise; window covers hang + early fall.
        mid_up = self.cfg.LAUNCH_UP_SEC[1]
        mid_hang = self.cfg.LAUNCH_HANG_SEC[1]
        mid_down = self.cfg.LAUNCH_DOWN_SEC[1]
        self.assertLessEqual(self.cfg.JUGGLE_CANCEL_START_SEC, mid_up + 0.05)
        self.assertGreaterEqual(
            self.cfg.JUGGLE_CANCEL_WINDOW_SEC, mid_hang)
        self.assertLessEqual(
            self.cfg.JUGGLE_CANCEL_START_SEC + self.cfg.JUGGLE_CANCEL_WINDOW_SEC,
            mid_up + mid_hang + mid_down + 0.25)
        self.assertIn('juggle hang stun→F slam', self.cfg.DEMO_HINT)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)
        self.assertNotIn('sora', hint_l)

    def test_slam_hit_index(self):
        slam = self.cfg.juggleCancelSlamHitIndex
        self.assertEqual(slam(), self.cfg.COMBO_LENGTH - 1)
        self.assertEqual(slam(3), 2)
        self.assertEqual(slam(1), 0)
        self.assertEqual(slam(0), 0)
        # Finisher slam is always the last combo beat.
        self.assertEqual(slam(self.cfg.COMBO_LENGTH), self.cfg.COMBO_LENGTH - 1)

    def test_juggle_cancel_window_open_helper(self):
        open_fn = self.cfg.isJuggleCancelWindowOpen
        start = self.cfg.JUGGLE_CANCEL_START_SEC
        until = start + self.cfg.JUGGLE_CANCEL_WINDOW_SEC
        # Not armed.
        self.assertFalse(open_fn(False, start, until, start + 0.08))
        # Lockout (before openAt).
        self.assertFalse(open_fn(True, start, until, start - 0.01))
        # Live window — opens at start, covers hang.
        self.assertTrue(open_fn(True, start, until, start))
        self.assertTrue(open_fn(True, start, until, start + 0.28))
        # Closed at/after until.
        self.assertFalse(open_fn(True, start, until, until))
        self.assertFalse(open_fn(True, start, until, until + 0.03))

    def test_juggle_hang_stun_helpers(self):
        """Server hang stun covers launch beats so cancel→slam sticks."""
        self.assertTrue(self.cfg.JUGGLE_HANG_STUN_ENABLED)
        self.assertGreater(self.cfg.JUGGLE_HANG_STUN_PAD_SEC, 0.0)
        self.assertGreater(self.cfg.JUGGLE_HANG_STUN_MAX_SEC, 0.5)
        stun_hit = self.cfg.isJuggleHangStunHit
        stun_sec = self.cfg.juggleHangStunSec
        stunned = self.cfg.isJuggleHangStunned
        launch = self.cfg.LAUNCH_HIT_INDEX
        # Opener does not stun; mid/finisher launch beats do.
        self.assertFalse(stun_hit(0))
        self.assertTrue(stun_hit(launch))
        self.assertTrue(stun_hit(self.cfg.COMBO_LENGTH - 1))
        self.assertEqual(stun_sec(0), 0.0)
        mid = stun_sec(launch)
        fin = stun_sec(self.cfg.COMBO_LENGTH - 1)
        self.assertGreater(mid, 0.0)
        self.assertGreater(fin, 0.0)
        # Mid stun lasts through cancel window (from launch start) + hitstop.
        cancel_end = (
            self.cfg.JUGGLE_CANCEL_START_SEC
            + self.cfg.JUGGLE_CANCEL_WINDOW_SEC)
        hitstop = self.cfg.HITSTOP_SEC[launch]
        self.assertGreaterEqual(mid, hitstop + cancel_end - 0.001)
        self.assertLessEqual(mid, self.cfg.JUGGLE_HANG_STUN_MAX_SEC)
        self.assertFalse(stunned(10.0, 10.0))
        self.assertTrue(stunned(10.5, 10.0))
        self.assertFalse(stunned(10.0, 10.5))
        # Disabled / capped.
        self.assertEqual(stun_sec(launch, enabled=False), 0.0)
        self.assertLessEqual(stun_sec(launch, maxSec=0.2), 0.2)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        JuggleCancelSlamTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
