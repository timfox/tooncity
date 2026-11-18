#!/usr/bin/env python3
"""Behavioral headless tests for soft-lock cycle reticle cream deepen.

Loads HackSlashConfig cycle pulse + cycle cream wash helpers without
Panda3D. Covers deepened cream ring tunables, quiet cycle cream wash, and
scale keyframes used by HitJuice.playSoftLockCyclePulse /
SoftLockReticleFx.playCyclePulse when Tab/` switches soft-lock (#210 deepen).

Run from repo root:
  python3 tests/test_soft_lock_cycle_reticle_pulse.py
  python3 -m unittest tests.test_soft_lock_cycle_reticle_pulse -v
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


class SoftLockCycleReticlePulseTest(unittest.TestCase):
    """Config + AST checks for deepened Tab/` cycle reticle cream cue."""

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
        # Deepened cream ring — juicier than original #210, under acquire.
        self.assertTrue(self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_ENABLED)
        self.assertGreaterEqual(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_PEAK, 1.90)
        self.assertGreaterEqual(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_SEC, 0.18)
        self.assertGreaterEqual(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_PEAK_ALPHA, 0.58)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_PEAK,
            self.cfg.SOFT_LOCK_PULSE_RING_PEAK)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_SEC,
            self.cfg.SOFT_LOCK_PULSE_RING_SEC)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_PEAK_ALPHA,
            self.cfg.SOFT_LOCK_PULSE_RING_PEAK_ALPHA)
        # Quiet cycle cream wash under acquire reticle wash.
        self.assertTrue(self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_ENABLED)
        self.assertGreater(self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_PEAK, 0.0)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_PEAK,
            self.cfg.SOFT_LOCK_CREAM_WASH_PEAK)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_MID,
            self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_PEAK)
        self.assertLess(
            self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_BIN,
            self.cfg.SOFT_LOCK_CREAM_WASH_BIN)
        cream = self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_COLOR
        self.assertEqual(len(cream), 3)
        self.assertGreaterEqual(cream[0], cream[2])
        self.assertGreaterEqual(cream[1], cream[2])
        # Peak lands during / just after deepened cycle cream ring.
        peak_at = self.cfg.softLockCycleCreamWashPeakAtSec()
        self.assertLessEqual(
            peak_at, self.cfg.SOFT_LOCK_CYCLE_PULSE_RING_SEC + 0.05)
        self.assertIn('Tab/` soft-lock cycle cream', self.cfg.DEMO_HINT)
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

    def test_soft_lock_cycle_cream_wash_peak_helper(self):
        peak_fn = self.cfg.softLockCycleCreamWashPeakAtSec
        self.assertAlmostEqual(
            peak_fn(),
            self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_DELAY_SEC
            + self.cfg.SOFT_LOCK_CYCLE_CREAM_WASH_IN_SEC)
        self.assertAlmostEqual(peak_fn(0.10, 0.05), 0.15)
        self.assertAlmostEqual(peak_fn(-1.0, 0.05), 0.05)

    def test_ast_cycle_cream_wash_fx(self):
        rel = 'toontown/hackslash/SoftLockCycleCreamWashFx.py'
        tree = _module_ast(rel)
        names = _class_names(tree)
        self.assertIn('SoftLockCycleCreamWashPulse', names)
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        self.assertIn('SOFT_LOCK_CYCLE_CREAM_WASH_ENABLED', src)
        self.assertIn('no keyblades', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())

        reticle_src = (
            REPO_ROOT / 'toontown/hackslash/SoftLockReticleFx.py'
        ).read_text(encoding='utf-8')
        self.assertIn('SoftLockCycleCreamWashPulse', reticle_src)
        self.assertIn('_armCycleCreamWash', reticle_src)

        init_src = (
            REPO_ROOT / 'toontown/hackslash/__init__.py'
        ).read_text(encoding='utf-8')
        self.assertIn('SoftLockCycleCreamWashPulse', init_src)
        self.assertIn('softLockCycleCreamWashPeakAtSec', init_src)

        cfg_names = _top_level_names(
            _module_ast('toontown/hackslash/HackSlashConfig.py'))
        for name in (
                'SOFT_LOCK_CYCLE_CREAM_WASH_ENABLED',
                'SOFT_LOCK_CYCLE_CREAM_WASH_DELAY_SEC',
                'SOFT_LOCK_CYCLE_CREAM_WASH_PEAK',
                'SOFT_LOCK_CYCLE_CREAM_WASH_MID',
                'SOFT_LOCK_CYCLE_CREAM_WASH_BIN',
                'softLockCycleCreamWashPeakAtSec'):
            self.assertIn(name, cfg_names)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockCycleReticlePulseTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
