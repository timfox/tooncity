#!/usr/bin/env python3
"""Behavioral headless tests for finisher slam FOV punch + settle helpers.

Loads HackSlashConfig.finisherFovPunchKeys without Panda3D. Covers punch /
undershoot / rest keyframes used by MeleeCombatController._playFinisherFovPunch
on slam connect (including air-juggle cancel→slam).

Run from repo root:
  python3 tests/test_finisher_slam_fov_settle.py
  python3 -m unittest tests.test_finisher_slam_fov_settle -v
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


def _load_finisher_fov_helpers():
    """Load HackSlashConfig FOV punch+settle helpers without MeleeCombat."""
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


class FinisherSlamFovSettleTest(unittest.TestCase):
    """Config + pure helper checks for finisher slam FOV punch + settle."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_finisher_fov_helpers()

    def test_config_finisher_fov_settle_tunables(self):
        self.assertGreater(self.cfg.FINISHER_FOV_PUNCH, 0.0)
        self.assertGreater(self.cfg.FINISHER_FOV_IN_SEC, 0.0)
        self.assertGreater(self.cfg.FINISHER_FOV_OUT_SEC, 0.0)
        self.assertGreater(self.cfg.FINISHER_FOV_SETTLE, 0.0)
        self.assertGreater(self.cfg.FINISHER_FOV_SETTLE_SEC, 0.0)
        # Settle is a brief undershoot — milder than the punch widen.
        self.assertLess(
            self.cfg.FINISHER_FOV_SETTLE, self.cfg.FINISHER_FOV_PUNCH)
        # Total punch+settle stays a short connect beat (under half a second).
        total = (
            self.cfg.FINISHER_FOV_IN_SEC
            + self.cfg.FINISHER_FOV_OUT_SEC
            + self.cfg.FINISHER_FOV_SETTLE_SEC)
        self.assertLess(total, 0.5)
        self.assertGreater(total, 0.2)

    def test_finisher_fov_punch_keys(self):
        keys = self.cfg.finisherFovPunchKeys
        base, peak, trough, rest = keys(52.0)
        self.assertAlmostEqual(base, 52.0)
        self.assertAlmostEqual(rest, 52.0)
        self.assertAlmostEqual(peak, 52.0 + self.cfg.FINISHER_FOV_PUNCH)
        self.assertAlmostEqual(trough, 52.0 - self.cfg.FINISHER_FOV_SETTLE)
        self.assertGreater(peak, base)
        self.assertLess(trough, rest)
        # Explicit overrides (settle=0 → no undershoot).
        b2, p2, t2, r2 = keys(40.0, punch=10.0, settle=0.0)
        self.assertAlmostEqual(b2, 40.0)
        self.assertAlmostEqual(p2, 50.0)
        self.assertAlmostEqual(t2, 40.0)
        self.assertAlmostEqual(r2, 40.0)
        # Negative inputs clamp.
        b3, p3, t3, r3 = keys(30.0, punch=-4.0, settle=-2.0)
        self.assertAlmostEqual(b3, 30.0)
        self.assertAlmostEqual(p3, 30.0)
        self.assertAlmostEqual(t3, 30.0)
        self.assertAlmostEqual(r3, 30.0)

    def test_no_kh_branding_in_fov_comments(self):
        cfg_path = REPO_ROOT / 'toontown' / 'hackslash' / 'HackSlashConfig.py'
        src = cfg_path.read_text(encoding='utf-8').lower()
        # FOV settle block must stay rubber-hose (no KH product nouns).
        fov_idx = src.find('finisher_fov_punch')
        self.assertGreater(fov_idx, 0)
        fov_snip = src[max(0, fov_idx - 400):fov_idx + 600]
        self.assertNotIn('keyblade', fov_snip)
        self.assertNotIn('kingdom hearts', fov_snip)
        self.assertNotIn('sora', fov_snip)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        FinisherSlamFovSettleTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
