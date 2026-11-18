#!/usr/bin/env python3
"""Behavioral headless tests for hurt-stagger cream wash aftershock helpers.

Loads HackSlashConfig hurt-stagger cream wash helpers without Panda3D. Covers
deepened-past tunables + peak timing so the wash reads during committed
stagger (#199 / #215 / #247 / #263 deepen) before the F/Shift recovery cancel
window, plus residual wash aftershock. Distinct from dodge-cancel cream flash
deepen (#242 / #257 / #281) and i-frame cream wash deepen (#228 / #272).

Run from repo root:
  python3 tests/test_hurt_stagger_cream_wash.py
  python3 -m unittest tests.test_hurt_stagger_cream_wash -v
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


def _load_hurt_wash_helpers():
    """Load HackSlashConfig hurt cream wash helpers without MeleeCombat."""
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


class HurtStaggerCreamWashTest(unittest.TestCase):
    """Config + AST checks for deepened-past hurt-stagger cream wash."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_hurt_wash_helpers()

    def test_config_hurt_cream_wash_tunables(self):
        self.assertTrue(self.cfg.HURT_STAGGER_CREAM_WASH_ENABLED)
        self.assertTrue(self.cfg.HURT_STAGGER_CREAM_WASH_AFTERSHOCK_ENABLED)
        self.assertGreater(self.cfg.HURT_STAGGER_CREAM_WASH_DELAY_SEC, 0.0)
        self.assertGreater(self.cfg.HURT_STAGGER_CREAM_WASH_PEAK, 0.0)
        self.assertGreater(self.cfg.HURT_STAGGER_CREAM_WASH_MID, 0.0)
        self.assertLess(
            self.cfg.HURT_STAGGER_CREAM_WASH_MID,
            self.cfg.HURT_STAGGER_CREAM_WASH_PEAK)
        # Deepened-past readability: juicier than merged #263 hurt wash.
        self.assertGreaterEqual(
            self.cfg.HURT_STAGGER_CREAM_WASH_PEAK, 0.099)
        self.assertGreaterEqual(
            self.cfg.HURT_STAGGER_CREAM_WASH_HOLD_SEC, 0.10)
        self.assertGreaterEqual(
            self.cfg.HURT_STAGGER_CREAM_WASH_MID, 0.075)
        # Quieter / earlier than hit-connect wash — smacks fire often.
        self.assertLess(
            self.cfg.HURT_STAGGER_CREAM_WASH_PEAK,
            self.cfg.HIT_SPARK_CREAM_WASH_PEAK)
        self.assertLess(
            self.cfg.HURT_STAGGER_CREAM_WASH_DELAY_SEC,
            self.cfg.HIT_SPARK_CREAM_WASH_DELAY_SEC)
        self.assertLess(
            self.cfg.HURT_STAGGER_CREAM_WASH_BIN,
            self.cfg.HIT_SPARK_CREAM_WASH_BIN)
        # Distinct from dodge-cancel cream flash deepen (#242 / #257) —
        # quieter, delayed stagger settle (not instant cancel flash).
        self.assertLess(
            self.cfg.HURT_STAGGER_CREAM_WASH_PEAK,
            self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK)
        self.assertGreater(
            self.cfg.HURT_STAGGER_CREAM_WASH_DELAY_SEC,
            self.cfg.DODGE_CANCEL_CREAM_WASH_DELAY_SEC)
        # Distinct from i-frame cream wash deepen (#228) — earlier smack beat.
        self.assertLess(
            self.cfg.HURT_STAGGER_CREAM_WASH_DELAY_SEC,
            self.cfg.DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC)
        # Peak during committed stagger, before cancel window opens.
        peak_at = self.cfg.hurtStaggerCreamWashPeakAtSec()
        self.assertLess(peak_at, self.cfg.HURT_STAGGER_SEC)
        # Richer residual wash aftershock after the deepened-past-#263 veil.
        self.assertGreaterEqual(
            self.cfg.HURT_STAGGER_CREAM_WASH_AFTERSHOCK_COUNT, 6)
        self.assertGreaterEqual(
            self.cfg.HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_PEAK, 1.35)
        self.assertGreaterEqual(
            self.cfg.HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA, 0.14)
        self.assertTrue(
            self.cfg.HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_ENABLED)
        self.assertGreater(
            self.cfg.HURT_STAGGER_CREAM_WASH_AFTERSHOCK_BIN,
            self.cfg.HURT_STAGGER_CREAM_WASH_BIN)
        wash_body = (
            self.cfg.HURT_STAGGER_CREAM_WASH_IN_SEC
            + self.cfg.HURT_STAGGER_CREAM_WASH_PULSE_SEC
            + self.cfg.HURT_STAGGER_CREAM_WASH_HOLD_SEC
            + self.cfg.HURT_STAGGER_CREAM_WASH_OUT_SEC)
        self.assertLess(
            self.cfg.HURT_STAGGER_CREAM_WASH_AFTERSHOCK_DELAY_SEC, wash_body)
        cream = self.cfg.HURT_STAGGER_CREAM_WASH_COLOR
        self.assertEqual(len(cream), 3)
        # Cream / pastel — no ink purple wash.
        self.assertGreaterEqual(cream[0], cream[2])
        self.assertGreaterEqual(cream[1], cream[2])
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertIn('hurt cream wash', hint_l)
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_hurt_stagger_cream_wash_peak_helper(self):
        peak_fn = self.cfg.hurtStaggerCreamWashPeakAtSec
        self.assertAlmostEqual(
            peak_fn(),
            self.cfg.HURT_STAGGER_CREAM_WASH_DELAY_SEC
            + self.cfg.HURT_STAGGER_CREAM_WASH_IN_SEC)
        self.assertAlmostEqual(peak_fn(0.02, 0.05), 0.07)
        self.assertAlmostEqual(peak_fn(-1.0, 0.05), 0.05)

    def test_hurt_stagger_cream_wash_aftershock_helper(self):
        after_fn = self.cfg.hurtStaggerCreamWashAftershockAtSec
        self.assertAlmostEqual(
            after_fn(),
            self.cfg.HURT_STAGGER_CREAM_WASH_AFTERSHOCK_DELAY_SEC)
        self.assertAlmostEqual(after_fn(0.10), 0.10)
        self.assertAlmostEqual(after_fn(-1.0), 0.0)

    def test_ast_hurt_stagger_cream_wash_fx(self):
        rel = 'toontown/hackslash/HurtStaggerCreamWashFx.py'
        tree = _module_ast(rel)
        names = _class_names(tree)
        self.assertIn('HurtStaggerCreamWashPulse', names)
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        self.assertIn('HURT_STAGGER_CREAM_WASH_ENABLED', src)
        self.assertIn('HURT_STAGGER_CREAM_WASH_AFTERSHOCK_ENABLED', src)
        self.assertIn('_buildAftershock', src)
        self.assertIn('_spawnAftershockHalo', src)
        self.assertIn('_spawnAftershockFleck', src)
        # Ban phrasing only — no KH product names as branding.
        self.assertIn('no keyblades', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())
        # Distinct from dodge-cancel / i-frame deepen cues; past #263.
        self.assertIn('distinct from', src.lower())
        self.assertIn('deepened past #263', src.lower())

    def test_ast_melee_wires_hurt_cream_wash(self):
        melee_rel = 'toontown/hackslash/MeleeCombat.py'
        melee_src = (REPO_ROOT / melee_rel).read_text(encoding='utf-8')
        self.assertIn('HurtStaggerCreamWashPulse', melee_src)
        self.assertIn('_playHurtCreamWash', melee_src)
        self.assertIn('_clearHurtCreamWash', melee_src)
        self.assertIn('self._playHurtCreamWash()', melee_src)

        init_rel = 'toontown/hackslash/__init__.py'
        init_src = (REPO_ROOT / init_rel).read_text(encoding='utf-8')
        self.assertIn('HurtStaggerCreamWashPulse', init_src)
        self.assertIn('hurtStaggerCreamWashPeakAtSec', init_src)
        self.assertIn('hurtStaggerCreamWashAftershockAtSec', init_src)

        cfg_names = _top_level_names(
            _module_ast('toontown/hackslash/HackSlashConfig.py'))
        for name in (
                'HURT_STAGGER_CREAM_WASH_ENABLED',
                'HURT_STAGGER_CREAM_WASH_DELAY_SEC',
                'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_ENABLED',
                'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_COUNT',
                'hurtStaggerCreamWashPeakAtSec',
                'hurtStaggerCreamWashAftershockAtSec'):
            self.assertIn(name, cfg_names)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        HurtStaggerCreamWashTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
