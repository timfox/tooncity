#!/usr/bin/env python3
"""Behavioral headless tests for soft-lock target cycle helpers.

Imports SoftTarget cycle helpers with a stub package path (no Panda3D).
Covers wraparound next/prev index math and pickCycleChoice snap rules used
by SoftTargetFinder.cycle / MeleeCombatController Tab/` wiring.

Run from repo root:
  python3 tests/test_soft_lock_target_cycle.py
  python3 -m unittest tests.test_soft_lock_target_cycle -v
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
    """Load SoftTarget cycle helpers without importing MeleeCombat / Panda."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.hackslash'):
        _ensure_pkg(pkg)

    # SoftTarget imports HackSlashConfig at module load — load config first.
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


class SoftLockTargetCycleTest(unittest.TestCase):
    """Table-driven cycle index / pick rules for soft-lock switch."""

    @classmethod
    def setUpClass(cls):
        cls.soft, cls.cfg = _load_soft_target_helpers()

    def test_config_cycle_tunables(self):
        self.assertTrue(self.cfg.TARGET_CYCLE_ENABLED)
        self.assertEqual(self.cfg.TARGET_CYCLE_NEXT_KEY, 'tab')
        self.assertEqual(self.cfg.TARGET_CYCLE_PREV_KEY, '`')
        self.assertGreater(self.cfg.TARGET_CYCLE_COOLDOWN_SEC, 0.0)
        self.assertGreaterEqual(
            self.cfg.TARGET_CYCLE_RANGE, self.cfg.TARGET_RANGE)
        self.assertIn('Tab/` soft-lock cycle', self.cfg.DEMO_HINT)

    def test_next_cycle_index_wraparound(self):
        nextCycleIndex = self.soft.nextCycleIndex
        self.assertIsNone(nextCycleIndex(0, None, 1))
        self.assertEqual(nextCycleIndex(3, None, 1), 0)
        self.assertEqual(nextCycleIndex(3, None, -1), 2)
        self.assertEqual(nextCycleIndex(3, 0, 1), 1)
        self.assertEqual(nextCycleIndex(3, 2, 1), 0)
        self.assertEqual(nextCycleIndex(3, 0, -1), 2)
        self.assertEqual(nextCycleIndex(1, 0, 1), 0)
        self.assertEqual(nextCycleIndex(1, 0, -1), 0)

    def test_pick_cycle_choice_snap_rules(self):
        pick = self.soft.pickCycleChoice
        keys = [('doId', 1), ('doId', 2), ('doId', 3)]

        # Empty — no lock.
        self.assertEqual(pick([], None, 1), (None, False))

        # No current lock → first (next) / last (prev), snapped.
        self.assertEqual(pick(keys, None, 1), (('doId', 1), True))
        self.assertEqual(pick(keys, None, -1), (('doId', 3), True))

        # Cycle next / prev with wrap + snap.
        self.assertEqual(
            pick(keys, ('doId', 1), 1), (('doId', 2), True))
        self.assertEqual(
            pick(keys, ('doId', 3), 1), (('doId', 1), True))
        self.assertEqual(
            pick(keys, ('doId', 1), -1), (('doId', 3), True))

        # Sole already-locked target — refresh feel, no snap spam.
        sole = [('doId', 9)]
        self.assertEqual(pick(sole, ('doId', 9), 1), (('doId', 9), False))
        self.assertEqual(pick(sole, ('doId', 9), -1), (('doId', 9), False))

        # Current key missing from candidates → treat as fresh acquire.
        self.assertEqual(
            pick(keys, ('doId', 99), 1), (('doId', 1), True))


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockTargetCycleTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
