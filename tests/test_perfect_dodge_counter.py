#!/usr/bin/env python3
"""Behavioral headless tests for perfect-dodge counter→melee helpers.

Loads HackSlashConfig counter helpers without Panda3D. Covers rewarded opener
damage/rate math and counter-window open checks used by MeleeCombatController.

Run from repo root:
  python3 tests/test_perfect_dodge_counter.py
  python3 -m unittest tests.test_perfect_dodge_counter -v
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


def _load_counter_helpers():
    """Load HackSlashConfig counter helpers without importing MeleeCombat."""
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


class PerfectDodgeCounterTest(unittest.TestCase):
    """Config + pure helper checks for perfect-dodge counter→melee."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_counter_helpers()

    def test_config_counter_tunables(self):
        self.assertTrue(self.cfg.PERFECT_DODGE_COUNTER_ENABLED)
        self.assertTrue(self.cfg.PERFECT_DODGE_COUNTER_BUFFER)
        self.assertGreater(self.cfg.PERFECT_DODGE_COUNTER_WINDOW_SEC, 0.0)
        self.assertGreater(self.cfg.PERFECT_DODGE_COUNTER_DAMAGE_MULT, 1.0)
        self.assertGreater(self.cfg.PERFECT_DODGE_COUNTER_RATE_MULT, 1.0)
        # Counter window should fit inside a generous dodge cooldown beat.
        self.assertLessEqual(
            self.cfg.PERFECT_DODGE_COUNTER_WINDOW_SEC,
            self.cfg.DODGE_COOLDOWN_SEC + 0.05)
        self.assertIn('perfect dodge→F counter', self.cfg.DEMO_HINT)
        # No KH branding in the demo hint.
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_opener_damage_bump(self):
        dmg = self.cfg.perfectDodgeCounterOpenerDamage
        base = self.cfg.COMBO_DAMAGE[0]
        bumped = dmg(base)
        self.assertGreater(bumped, base)
        self.assertEqual(
            bumped,
            max(1, int(round(base * self.cfg.PERFECT_DODGE_COUNTER_DAMAGE_MULT))))
        self.assertEqual(dmg(8, 1.5), 12)
        self.assertEqual(dmg(0, 2.0), 1)  # floor at 1

    def test_opener_rate_bump(self):
        rate_fn = self.cfg.perfectDodgeCounterOpenerRate
        base = self.cfg.COMBO_PLAY_RATES[0]
        bumped = rate_fn(base)
        self.assertGreater(bumped, base)
        self.assertAlmostEqual(
            bumped, base * self.cfg.PERFECT_DODGE_COUNTER_RATE_MULT)
        self.assertAlmostEqual(rate_fn(2.0, 1.25), 2.5)

    def test_counter_window_open_helper(self):
        open_fn = self.cfg.isPerfectDodgeCounterWindowOpen
        self.assertFalse(open_fn(False, 1.0, 0.5))
        self.assertTrue(open_fn(True, 1.0, 0.5))
        self.assertFalse(open_fn(True, 1.0, 1.0))
        self.assertFalse(open_fn(True, 1.0, 1.1))


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        PerfectDodgeCounterTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
