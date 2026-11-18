#!/usr/bin/env python3
"""Behavioral headless tests for dodge i-frame pulse cream wash helpers.

Loads HackSlashConfig dodge i-frame cream wash helpers without Panda3D.
Covers deepened tunables + peak timing so the wash reads clearly during
dodge invuln (#166 deepen), plus residual wash aftershock.

Run from repo root:
  python3 tests/test_dodge_iframe_cream_wash.py
  python3 -m unittest tests.test_dodge_iframe_cream_wash -v
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


def _load_iframe_wash_helpers():
    """Load HackSlashConfig i-frame cream wash helpers without MeleeCombat."""
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


class DodgeIFrameCreamWashTest(unittest.TestCase):
    """Config + AST checks for deepened dodge i-frame cream wash."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_iframe_wash_helpers()

    def test_config_iframe_cream_wash_tunables(self):
        self.assertTrue(self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_ENABLED)
        self.assertTrue(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ENABLED)
        self.assertGreater(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC, 0.0)
        self.assertGreater(self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_PEAK, 0.0)
        self.assertGreater(self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_MID, 0.0)
        self.assertLess(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_MID,
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_PEAK)
        # Deepened readability: at least as strong as the prior quiet wash.
        self.assertGreaterEqual(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_PEAK, 0.09)
        self.assertGreaterEqual(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_HOLD_SEC, 0.08)
        # Still quieter / under trail settle wash (rolls fire often).
        self.assertLessEqual(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_PEAK,
            self.cfg.DODGE_TRAIL_CREAM_WASH_PEAK)
        self.assertLess(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_BIN,
            self.cfg.DODGE_TRAIL_CREAM_WASH_BIN)
        # Peak lands while dodge i-frames are still live (first pulse @ start).
        peak_at = self.cfg.dodgeIFrameCreamWashPeakAtSec()
        self.assertLess(peak_at, self.cfg.DODGE_IFRAME_SEC)
        self.assertGreaterEqual(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_COUNT, 1)
        self.assertTrue(
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED)
        cream = self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_COLOR
        self.assertEqual(len(cream), 3)
        # Cream / pastel — no ink purple wash.
        self.assertGreaterEqual(cream[0], cream[2])
        self.assertGreaterEqual(cream[1], cream[2])
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertIn('i-frame cream wash', hint_l)
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_iframe_cream_wash_peak_helper(self):
        peak_fn = self.cfg.dodgeIFrameCreamWashPeakAtSec
        self.assertAlmostEqual(
            peak_fn(),
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC
            + self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_IN_SEC)
        self.assertAlmostEqual(peak_fn(0.10, 0.05), 0.15)
        self.assertAlmostEqual(peak_fn(-1.0, 0.05), 0.05)

    def test_ast_iframe_cream_wash_fx(self):
        rel = 'toontown/hackslash/DodgeIFrameCreamWashFx.py'
        tree = _module_ast(rel)
        names = _class_names(tree)
        self.assertIn('DodgeIFrameCreamWashPulse', names)
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        self.assertIn('DODGE_TRAIL_PULSE_CREAM_WASH_ENABLED', src)
        self.assertIn('DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ENABLED', src)
        self.assertIn('_buildAftershock', src)
        # Ban phrasing only — no KH product names as branding.
        self.assertIn('no keyblades', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())

    def test_ast_trail_wires_iframe_cream_wash(self):
        trail_rel = 'toontown/hackslash/DodgeTrailFx.py'
        trail_src = (REPO_ROOT / trail_rel).read_text(encoding='utf-8')
        self.assertIn('DodgeIFrameCreamWashPulse', trail_src)
        self.assertIn('_armIFrameCreamWash', trail_src)

        init_rel = 'toontown/hackslash/__init__.py'
        init_src = (REPO_ROOT / init_rel).read_text(encoding='utf-8')
        self.assertIn('DodgeIFrameCreamWashPulse', init_src)
        self.assertIn('dodgeIFrameCreamWashPeakAtSec', init_src)

        cfg_names = _top_level_names(
            _module_ast('toontown/hackslash/HackSlashConfig.py'))
        for name in (
                'DODGE_TRAIL_PULSE_CREAM_WASH_ENABLED',
                'DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC',
                'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ENABLED',
                'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_COUNT',
                'dodgeIFrameCreamWashPeakAtSec'):
            self.assertIn(name, cfg_names)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        DodgeIFrameCreamWashTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
