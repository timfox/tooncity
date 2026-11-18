#!/usr/bin/env python3
"""Behavioral headless tests for dodge-cancel cream wash flash helpers.

Loads HackSlashConfig dodge-cancel cream wash helpers without Panda3D. Covers
tunables + peak timing so the flash reads the instant late-dodge cancel into
melee fires (#186).

Run from repo root:
  python3 tests/test_dodge_cancel_cream_wash.py
  python3 -m unittest tests.test_dodge_cancel_cream_wash -v
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


def _load_dodge_cancel_wash_helpers():
    """Load HackSlashConfig dodge-cancel cream wash helpers without MeleeCombat."""
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


class DodgeCancelCreamWashTest(unittest.TestCase):
    """Config + AST checks for dodge-cancel cream wash flash."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_dodge_cancel_wash_helpers()

    def test_config_dodge_cancel_cream_wash_tunables(self):
        self.assertTrue(self.cfg.DODGE_CANCEL_CREAM_WASH_ENABLED)
        self.assertGreaterEqual(self.cfg.DODGE_CANCEL_CREAM_WASH_DELAY_SEC, 0.0)
        self.assertGreater(self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK, 0.0)
        self.assertGreater(self.cfg.DODGE_CANCEL_CREAM_WASH_MID, 0.0)
        self.assertLess(
            self.cfg.DODGE_CANCEL_CREAM_WASH_MID,
            self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK)
        # Snappier flash than dodge-trail settle wash; quieter than hit wash.
        self.assertLessEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_DELAY_SEC,
            self.cfg.DODGE_TRAIL_CREAM_WASH_DELAY_SEC)
        self.assertLess(
            self.cfg.DODGE_CANCEL_CREAM_WASH_IN_SEC,
            self.cfg.DODGE_TRAIL_CREAM_WASH_IN_SEC)
        self.assertLess(
            self.cfg.DODGE_CANCEL_CREAM_WASH_OUT_SEC,
            self.cfg.DODGE_TRAIL_CREAM_WASH_OUT_SEC)
        self.assertLessEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK,
            self.cfg.HIT_SPARK_CREAM_WASH_PEAK + 0.02)
        # Peak lands immediately so cancel→melee reads as one beat.
        peak_at = self.cfg.dodgeCancelCreamWashPeakAtSec()
        self.assertLess(peak_at, self.cfg.DODGE_CANCEL_WINDOW_SEC)
        cream = self.cfg.DODGE_CANCEL_CREAM_WASH_COLOR
        self.assertEqual(len(cream), 3)
        # Cream / pastel — no ink purple wash.
        self.assertGreaterEqual(cream[0], cream[2])
        self.assertGreaterEqual(cream[1], cream[2])
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertIn('cream flash', hint_l)
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_dodge_cancel_cream_wash_peak_helper(self):
        peak_fn = self.cfg.dodgeCancelCreamWashPeakAtSec
        self.assertAlmostEqual(
            peak_fn(),
            self.cfg.DODGE_CANCEL_CREAM_WASH_DELAY_SEC
            + self.cfg.DODGE_CANCEL_CREAM_WASH_IN_SEC)
        self.assertAlmostEqual(peak_fn(0.0, 0.03), 0.03)
        self.assertAlmostEqual(peak_fn(-1.0, 0.05), 0.05)

    def test_ast_dodge_cancel_cream_wash_fx(self):
        rel = 'toontown/hackslash/DodgeCancelCreamWashFx.py'
        tree = _module_ast(rel)
        names = _class_names(tree)
        self.assertIn('DodgeCancelCreamWashPulse', names)
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        self.assertIn('DODGE_CANCEL_CREAM_WASH_ENABLED', src)
        self.assertIn('_cancelDodgeIntoMelee', src)
        # Ban phrasing only — no KH product names as branding.
        self.assertIn('no keyblades', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())

    def test_ast_melee_wires_dodge_cancel_cream_wash(self):
        melee_rel = 'toontown/hackslash/MeleeCombat.py'
        melee_src = (REPO_ROOT / melee_rel).read_text(encoding='utf-8')
        self.assertIn('DodgeCancelCreamWashPulse', melee_src)
        self.assertIn('_playDodgeCancelCreamWash', melee_src)
        self.assertIn('_clearDodgeCancelCreamWash', melee_src)
        self.assertIn('self._playDodgeCancelCreamWash()', melee_src)

        init_rel = 'toontown/hackslash/__init__.py'
        init_src = (REPO_ROOT / init_rel).read_text(encoding='utf-8')
        self.assertIn('DodgeCancelCreamWashPulse', init_src)
        self.assertIn('dodgeCancelCreamWashPeakAtSec', init_src)

        cfg_names = _top_level_names(
            _module_ast('toontown/hackslash/HackSlashConfig.py'))
        for name in (
                'DODGE_CANCEL_CREAM_WASH_ENABLED',
                'DODGE_CANCEL_CREAM_WASH_DELAY_SEC',
                'DODGE_CANCEL_CREAM_WASH_PEAK',
                'dodgeCancelCreamWashPeakAtSec'):
            self.assertIn(name, cfg_names)

        mw_src = (REPO_ROOT / 'toontown/hackslash/MagicWords.py').read_text(
            encoding='utf-8')
        self.assertIn('cream wash flash', mw_src.lower())
        self.assertNotIn('keyblade', mw_src.lower())


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        DodgeCancelCreamWashTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
