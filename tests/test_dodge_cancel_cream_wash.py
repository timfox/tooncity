#!/usr/bin/env python3
"""Behavioral headless tests for dodge-cancel cream wash flash deepen helpers.

Loads HackSlashConfig dodge-cancel cream wash helpers without Panda3D. Covers
deepened-past-#257 flash tunables + richer cream flash aftershock so
late-dodge cancel into melee reads juicier still (#219 / #242 / #257 deepen)
— distinct from dodge i-frame cream wash deepen (#228 / #272), combo
counter cream edge deepen (#237), and hurt-stagger cream wash deepen
(#247 / #263).

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
    """Config + AST checks for deepened dodge-cancel cream wash flash."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_dodge_cancel_wash_helpers()

    def test_config_dodge_cancel_cream_wash_tunables(self):
        self.assertTrue(self.cfg.DODGE_CANCEL_CREAM_WASH_ENABLED)
        self.assertTrue(self.cfg.DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_ENABLED)
        self.assertGreaterEqual(self.cfg.DODGE_CANCEL_CREAM_WASH_DELAY_SEC, 0.0)
        self.assertGreater(self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK, 0.0)
        self.assertGreater(self.cfg.DODGE_CANCEL_CREAM_WASH_MID, 0.0)
        self.assertLess(
            self.cfg.DODGE_CANCEL_CREAM_WASH_MID,
            self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK)
        # Deepened past #257: juicier than second deepen cancel flash.
        self.assertGreaterEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK, 0.16)
        self.assertGreaterEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_HOLD_SEC, 0.07)
        self.assertGreaterEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_MID, 0.095)
        self.assertGreaterEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_PULSE_SEC, 0.09)
        self.assertGreaterEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_OUT_SEC, 0.32)
        # Snappier flash than dodge-trail settle wash; still a brief cancel beat.
        self.assertLessEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_DELAY_SEC,
            self.cfg.DODGE_TRAIL_CREAM_WASH_DELAY_SEC)
        self.assertLess(
            self.cfg.DODGE_CANCEL_CREAM_WASH_IN_SEC,
            self.cfg.DODGE_TRAIL_CREAM_WASH_IN_SEC)
        self.assertLess(
            self.cfg.DODGE_CANCEL_CREAM_WASH_OUT_SEC,
            self.cfg.DODGE_TRAIL_CREAM_WASH_OUT_SEC)
        # Cancel flash can pop a touch louder than hit wash; still soft.
        self.assertLessEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK,
            self.cfg.HIT_SPARK_CREAM_WASH_PEAK + 0.06)
        # Richer residual flash aftershock after the deepened veil.
        self.assertGreaterEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_COUNT, 6)
        self.assertGreaterEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_PEAK, 1.28)
        self.assertGreaterEqual(
            self.cfg.DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA, 0.13)
        self.assertTrue(
            self.cfg.DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_ENABLED)
        self.assertGreater(
            self.cfg.DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_BIN,
            self.cfg.DODGE_CANCEL_CREAM_WASH_BIN)
        # Louder / snappier than hurt-stagger deepen (#247).
        self.assertGreater(
            self.cfg.DODGE_CANCEL_CREAM_WASH_PEAK,
            self.cfg.HURT_STAGGER_CREAM_WASH_PEAK)
        self.assertLess(
            self.cfg.DODGE_CANCEL_CREAM_WASH_DELAY_SEC,
            self.cfg.HURT_STAGGER_CREAM_WASH_DELAY_SEC)
        flash_body = (
            self.cfg.DODGE_CANCEL_CREAM_WASH_IN_SEC
            + self.cfg.DODGE_CANCEL_CREAM_WASH_PULSE_SEC
            + self.cfg.DODGE_CANCEL_CREAM_WASH_HOLD_SEC
            + self.cfg.DODGE_CANCEL_CREAM_WASH_OUT_SEC)
        self.assertLess(
            self.cfg.DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_DELAY_SEC, flash_body)
        # Peak lands immediately so cancel→melee reads as one beat.
        peak_at = self.cfg.dodgeCancelCreamWashPeakAtSec()
        self.assertLess(peak_at, self.cfg.DODGE_CANCEL_WINDOW_SEC)
        cream = self.cfg.DODGE_CANCEL_CREAM_WASH_COLOR
        self.assertEqual(len(cream), 3)
        # Cream / pastel — no ink purple wash.
        self.assertGreaterEqual(cream[0], cream[2])
        self.assertGreaterEqual(cream[1], cream[2])
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertIn('cream flash deepen++', hint_l)
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

    def test_dodge_cancel_cream_wash_aftershock_helper(self):
        after_fn = self.cfg.dodgeCancelCreamWashAftershockAtSec
        self.assertAlmostEqual(
            after_fn(),
            self.cfg.DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_DELAY_SEC)
        self.assertAlmostEqual(after_fn(0.10), 0.10)
        self.assertAlmostEqual(after_fn(-1.0), 0.0)

    def test_ast_dodge_cancel_cream_wash_fx(self):
        rel = 'toontown/hackslash/DodgeCancelCreamWashFx.py'
        tree = _module_ast(rel)
        names = _class_names(tree)
        self.assertIn('DodgeCancelCreamWashPulse', names)
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        self.assertIn('DODGE_CANCEL_CREAM_WASH_ENABLED', src)
        self.assertIn('DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_ENABLED', src)
        self.assertIn('_cancelDodgeIntoMelee', src)
        self.assertIn('_buildAftershock', src)
        self.assertIn('_spawnAftershockHalo', src)
        self.assertIn('_spawnAftershockFleck', src)
        # Ban phrasing only — no KH product names as branding.
        self.assertIn('no keyblades', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())
        # Distinct from combo-edge / i-frame deepen cues.
        self.assertIn('distinct from', src.lower())

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
        self.assertIn('dodgeCancelCreamWashAftershockAtSec', init_src)

        cfg_names = _top_level_names(
            _module_ast('toontown/hackslash/HackSlashConfig.py'))
        for name in (
                'DODGE_CANCEL_CREAM_WASH_ENABLED',
                'DODGE_CANCEL_CREAM_WASH_DELAY_SEC',
                'DODGE_CANCEL_CREAM_WASH_PEAK',
                'DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_ENABLED',
                'DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_COUNT',
                'DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_ENABLED',
                'dodgeCancelCreamWashPeakAtSec',
                'dodgeCancelCreamWashAftershockAtSec'):
            self.assertIn(name, cfg_names)

        mw_src = (REPO_ROOT / 'toontown/hackslash/MagicWords.py').read_text(
            encoding='utf-8')
        self.assertIn('cream wash flash', mw_src.lower())
        self.assertIn('deepened-past-#257 cream wash', mw_src.lower())
        self.assertIn('richer cream flash', mw_src.lower())
        self.assertIn('aftershock', mw_src.lower())
        self.assertNotIn('keyblade', mw_src.lower())


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        DodgeCancelCreamWashTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
