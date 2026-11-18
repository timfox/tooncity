#!/usr/bin/env python3
"""Behavioral headless tests for Balloon Snare string-snap counter helpers.

Loads CorruptionGlobals counter helpers without Panda3D. Covers rewarded
opener damage/rate math, arm/until timing, and window-open checks used by
DistributedCorruptToon + MeleeCombatController.

Run from repo root:
  python3 tests/test_snare_string_snap_counter.py
  python3 -m unittest tests.test_snare_string_snap_counter -v
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


def _load_snare_counter_helpers():
    """Load CorruptionGlobals counter helpers without importing Distributed*."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.corruption'):
        _ensure_pkg(pkg)

    cfg_path = REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
    cfg_spec = importlib.util.spec_from_file_location(
        'toontown.corruption.CorruptionGlobals', cfg_path)
    cfg = importlib.util.module_from_spec(cfg_spec)
    assert cfg_spec.loader is not None
    sys.modules['toontown.corruption.CorruptionGlobals'] = cfg
    cfg_spec.loader.exec_module(cfg)
    sys.modules['toontown.corruption'].CorruptionGlobals = cfg
    return cfg


class SnareStringSnapCounterTest(unittest.TestCase):
    """Config + pure helper checks for Balloon Snare string-snap counter."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_snare_counter_helpers()

    def test_config_counter_tunables(self):
        self.assertTrue(self.cfg.SNARE_STRING_COUNTER_ENABLED)
        self.assertTrue(self.cfg.SNARE_STRING_COUNTER_INTERRUPT)
        self.assertGreater(self.cfg.SNARE_STRING_COUNTER_ARM_DELAY_SEC, 0.0)
        self.assertGreater(self.cfg.SNARE_STRING_COUNTER_WINDOW_SEC, 0.0)
        self.assertGreater(self.cfg.SNARE_STRING_COUNTER_RANGE, 0.0)
        self.assertGreater(self.cfg.SNARE_STRING_COUNTER_DAMAGE_MULT, 1.0)
        self.assertGreater(self.cfg.SNARE_STRING_COUNTER_RATE_MULT, 1.0)
        # Arm delay + window should fit inside a generous Snare telegraph+cool beat.
        snare = self.cfg.ARCHETYPE_STATS[self.cfg.ARCHETYPE_SNARE]
        telegraph = float(snare.get('telegraphDelay', self.cfg.ATTACK_TELEGRAPH_DELAY))
        self.assertLessEqual(
            self.cfg.SNARE_STRING_COUNTER_ARM_DELAY_SEC, telegraph + 0.05)
        self.assertEqual(
            self.cfg.SNARE_STRING_COUNTER_EVENT,
            'corruptSnareStringSnapCounter')
        # No KH branding in the event / look ids nearby.
        event_l = self.cfg.SNARE_STRING_COUNTER_EVENT.lower()
        self.assertNotIn('keyblade', event_l)
        self.assertNotIn('kingdom hearts', event_l)
        look_id = str(self.cfg.SNARE_TELEGRAPH_STRING_LOOK.get('id', '')).lower()
        self.assertNotIn('keyblade', look_id)

    def test_opener_damage_bump(self):
        dmg = self.cfg.snareStringCounterOpenerDamage
        base = 8
        bumped = dmg(base)
        self.assertGreater(bumped, base)
        self.assertEqual(
            bumped,
            max(1, int(round(base * self.cfg.SNARE_STRING_COUNTER_DAMAGE_MULT))))
        self.assertEqual(dmg(8, 1.5), 12)
        self.assertEqual(dmg(0, 2.0), 1)  # floor at 1

    def test_opener_rate_bump(self):
        rate_fn = self.cfg.snareStringCounterOpenerRate
        base = 1.0
        bumped = rate_fn(base)
        self.assertGreater(bumped, base)
        self.assertAlmostEqual(
            bumped, base * self.cfg.SNARE_STRING_COUNTER_RATE_MULT)
        self.assertAlmostEqual(rate_fn(2.0, 1.25), 2.5)

    def test_counter_window_open_helper(self):
        open_fn = self.cfg.isSnareStringCounterWindowOpen
        self.assertFalse(open_fn(False, 1.0, 0.5))
        self.assertTrue(open_fn(True, 1.0, 0.5))
        self.assertFalse(open_fn(True, 1.0, 1.0))
        self.assertFalse(open_fn(True, 1.0, 1.1))

    def test_arm_at_and_until_helpers(self):
        arm_at = self.cfg.snareStringCounterArmAt
        until = self.cfg.snareStringCounterUntil
        now = 10.0
        armed = arm_at(now)
        self.assertAlmostEqual(
            armed, now + self.cfg.SNARE_STRING_COUNTER_ARM_DELAY_SEC)
        expiry = until(armed)
        self.assertAlmostEqual(
            expiry, armed + self.cfg.SNARE_STRING_COUNTER_WINDOW_SEC)
        self.assertAlmostEqual(arm_at(now, 0.0), now)
        self.assertAlmostEqual(until(armed, 0.25), armed + 0.25)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SnareStringSnapCounterTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
