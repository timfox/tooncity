#!/usr/bin/env python3
"""Behavioral headless tests for hurt-stagger recovery cancel helpers.

Loads HackSlashConfig hurt-stagger helpers without Panda3D. Covers stagger +
cancel-window open checks and total timing used by MeleeCombatController.

Run from repo root:
  python3 tests/test_hurt_stagger_recovery_cancel.py
  python3 -m unittest tests.test_hurt_stagger_recovery_cancel -v
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


def _load_hurt_stagger_helpers():
    """Load HackSlashConfig hurt-stagger helpers without importing MeleeCombat."""
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


class HurtStaggerRecoveryCancelTest(unittest.TestCase):
    """Config + pure helper checks for hurt-stagger recovery cancel."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_hurt_stagger_helpers()

    def test_config_hurt_stagger_tunables(self):
        self.assertTrue(self.cfg.HURT_STAGGER_ENABLED)
        self.assertTrue(self.cfg.HURT_RECOVERY_CANCEL_BUFFER)
        self.assertGreater(self.cfg.HURT_STAGGER_SEC, 0.0)
        self.assertGreater(self.cfg.HURT_RECOVERY_CANCEL_WINDOW_SEC, 0.0)
        # Stagger covers squash + early stretch of the player hit-react.
        squash_sec = self.cfg.PLAYER_HIT_REACT_SQUASH[3]
        stretch_sec = self.cfg.PLAYER_HIT_REACT_STRETCH[3]
        self.assertGreaterEqual(
            self.cfg.HURT_STAGGER_SEC, squash_sec)
        self.assertLessEqual(
            self.cfg.HURT_STAGGER_SEC, squash_sec + stretch_sec + 0.05)
        # Cancel window should fit inside the post-hit i-frame beat.
        total = self.cfg.hurtStaggerTotalSec()
        self.assertLessEqual(total, self.cfg.IFRAME_SEC + 0.05)
        self.assertIn('hurt→F/Shift cancel', self.cfg.DEMO_HINT)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_hurt_stagger_total_sec(self):
        total_fn = self.cfg.hurtStaggerTotalSec
        self.assertAlmostEqual(
            total_fn(),
            self.cfg.HURT_STAGGER_SEC + self.cfg.HURT_RECOVERY_CANCEL_WINDOW_SEC)
        self.assertAlmostEqual(total_fn(0.1, 0.2), 0.3)
        self.assertAlmostEqual(total_fn(-1.0, 0.5), 0.5)

    def test_hurt_recovery_cancel_window_open_helper(self):
        open_fn = self.cfg.isHurtRecoveryCancelWindowOpen
        # Not armed.
        self.assertFalse(open_fn(False, 0.14, 0.52, 0.20))
        # Lockout (before openAt).
        self.assertFalse(open_fn(True, 0.14, 0.52, 0.05))
        # Live window.
        self.assertTrue(open_fn(True, 0.14, 0.52, 0.14))
        self.assertTrue(open_fn(True, 0.14, 0.52, 0.40))
        # Closed at/after until.
        self.assertFalse(open_fn(True, 0.14, 0.52, 0.52))
        self.assertFalse(open_fn(True, 0.14, 0.52, 0.60))


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        HurtStaggerRecoveryCancelTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
