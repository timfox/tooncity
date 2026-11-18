#!/usr/bin/env python3
"""Behavioral headless tests for combo-counter cream edge deepen helpers.

Loads HackSlashConfig combo cream edge helpers without Panda3D. Covers
deepened edge tunables + quiet local cream edge aftershock so the punch
counter reads juicier on each tick beside hose pop + cream sparkle —
distinct from soft-lock cycle reticle cream deepen (#233) and dodge
i-frame cream wash deepen (#228).

Run from repo root:
  python3 tests/test_combo_counter_cream_edge.py
  python3 -m unittest tests.test_combo_counter_cream_edge -v
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


def _load_combo_edge_helpers():
    """Load HackSlashConfig combo cream edge helpers without MeleeCombat."""
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


class ComboCounterCreamEdgeTest(unittest.TestCase):
    """Config + AST checks for deepened combo-counter cream edge pop."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_combo_edge_helpers()

    def test_config_combo_cream_edge_tunables(self):
        self.assertTrue(self.cfg.COMBO_COUNTER_CREAM_EDGE_ENABLED)
        self.assertTrue(self.cfg.COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_ENABLED)
        self.assertGreater(self.cfg.COMBO_COUNTER_CREAM_EDGE, 0.0)
        self.assertGreater(self.cfg.COMBO_COUNTER_CREAM_EDGE_HALF_W, 0.0)
        self.assertGreater(self.cfg.COMBO_COUNTER_CREAM_EDGE_HALF_H, 0.0)
        self.assertGreater(self.cfg.COMBO_COUNTER_CREAM_EDGE_PEAK, 0.0)
        self.assertGreater(self.cfg.COMBO_COUNTER_CREAM_EDGE_PULSE, 0.0)
        self.assertLess(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_PULSE,
            self.cfg.COMBO_COUNTER_CREAM_EDGE_PEAK)
        self.assertGreater(self.cfg.COMBO_COUNTER_CREAM_EDGE_SCALE_PEAK, 1.0)
        # Deepened readability: juicier than original #224 edge pop.
        self.assertGreaterEqual(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_PEAK, 0.72)
        self.assertGreaterEqual(
            self.cfg.COMBO_COUNTER_CREAM_EDGE, 0.024)
        self.assertGreaterEqual(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_HOLD_SEC, 0.04)
        self.assertGreaterEqual(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_SCALE_PEAK, 1.28)
        # Snappier than banner / wave cream edge settle (ticks fire often).
        self.assertLess(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_IN_SEC, 0.08)
        self.assertLess(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_OUT_SEC, 0.30)
        # Under counter TextNode bin (55); over fullscreen wash veil (28).
        self.assertLess(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_BIN, 55)
        self.assertGreater(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_BIN,
            self.cfg.COMBO_COUNTER_CREAM_WASH_BIN)
        # Quiet local edge aftershock under the edge strips.
        self.assertGreaterEqual(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_COUNT, 1)
        self.assertTrue(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_ENABLED)
        self.assertLess(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_BIN,
            self.cfg.COMBO_COUNTER_CREAM_EDGE_BIN)
        # Aftershock begins during / just after deepened edge peak hold.
        edge_body = (
            self.cfg.COMBO_COUNTER_CREAM_EDGE_IN_SEC
            + self.cfg.COMBO_COUNTER_CREAM_EDGE_HOLD_SEC
            + self.cfg.COMBO_COUNTER_CREAM_EDGE_PULSE_SEC
            + self.cfg.COMBO_COUNTER_CREAM_EDGE_OUT_SEC)
        self.assertLess(
            self.cfg.COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_DELAY_SEC, edge_body)
        cream = self.cfg.COMBO_COUNTER_CREAM_EDGE_COLOR
        self.assertEqual(len(cream), 4)
        # Cream / pastel — no ink purple edge.
        self.assertGreaterEqual(cream[0], cream[2])
        self.assertGreaterEqual(cream[1], cream[2])
        peak_at = self.cfg.comboCounterCreamEdgePeakAtSec()
        self.assertAlmostEqual(
            peak_at, self.cfg.COMBO_COUNTER_CREAM_EDGE_IN_SEC)
        self.assertIn('combo cream edge', self.cfg.DEMO_HINT.lower())
        banned = ('keyblade', 'kingdom hearts', 'sora', 'heartless')
        blob = ' '.join([
            'combo counter cream edge pop',
            str(cream),
            str(self.cfg.COMBO_COUNTER_LABEL),
            self.cfg.DEMO_HINT,
        ]).lower()
        for term in banned:
            self.assertNotIn(term, blob)

    def test_combo_cream_edge_peak_helper(self):
        peak_fn = self.cfg.comboCounterCreamEdgePeakAtSec
        self.assertAlmostEqual(
            peak_fn(), self.cfg.COMBO_COUNTER_CREAM_EDGE_IN_SEC)
        self.assertAlmostEqual(peak_fn(0.03), 0.03)
        self.assertAlmostEqual(peak_fn(-1.0), 0.0)

    def test_combo_cream_edge_aftershock_helper(self):
        after_fn = self.cfg.comboCounterCreamEdgeAftershockAtSec
        self.assertAlmostEqual(
            after_fn(),
            self.cfg.COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_DELAY_SEC)
        self.assertAlmostEqual(after_fn(0.12), 0.12)
        self.assertAlmostEqual(after_fn(-1.0), 0.0)

    def test_ast_combo_cream_edge_fx(self):
        rel = 'toontown/hackslash/ComboCounterCreamEdgeFx.py'
        tree = _module_ast(rel)
        names = _class_names(tree)
        self.assertIn('ComboCounterCreamEdgePulse', names)
        src = (REPO_ROOT / rel).read_text(encoding='utf-8')
        self.assertIn('COMBO_COUNTER_CREAM_EDGE_ENABLED', src)
        self.assertIn('COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_ENABLED', src)
        self.assertIn('_buildEdgeRoot', src)
        self.assertIn('_buildAftershock', src)
        self.assertIn('_spawnAftershockHalo', src)
        self.assertIn('_spawnAftershockFleck', src)
        self.assertIn('hackslashComboCounterCreamEdge', src)
        # Ban phrasing only — no KH product names as branding.
        self.assertIn('no keyblades', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())
        # Distinct from soft-lock / i-frame deepen cues.
        self.assertIn('distinct from', src.lower())

    def test_ast_melee_wires_combo_cream_edge(self):
        melee_rel = 'toontown/hackslash/MeleeCombat.py'
        melee_src = (REPO_ROOT / melee_rel).read_text(encoding='utf-8')
        self.assertIn('ComboCounterCreamEdgePulse', melee_src)
        self.assertIn('_playComboCreamEdge', melee_src)
        self.assertIn('_clearComboCreamEdge', melee_src)
        self.assertIn('self._playComboCreamEdge(', melee_src)

        init_rel = 'toontown/hackslash/__init__.py'
        init_src = (REPO_ROOT / init_rel).read_text(encoding='utf-8')
        self.assertIn('ComboCounterCreamEdgePulse', init_src)
        self.assertIn('comboCounterCreamEdgePeakAtSec', init_src)
        self.assertIn('comboCounterCreamEdgeAftershockAtSec', init_src)

        cfg_names = _top_level_names(
            _module_ast('toontown/hackslash/HackSlashConfig.py'))
        for name in (
                'COMBO_COUNTER_CREAM_EDGE_ENABLED',
                'COMBO_COUNTER_CREAM_EDGE_PEAK',
                'COMBO_COUNTER_CREAM_EDGE_HALF_W',
                'COMBO_COUNTER_CREAM_EDGE_SCALE_PEAK',
                'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_ENABLED',
                'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_COUNT',
                'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_ENABLED',
                'comboCounterCreamEdgePeakAtSec',
                'comboCounterCreamEdgeAftershockAtSec'):
            self.assertIn(name, cfg_names)

        mw_src = (REPO_ROOT / 'toontown/hackslash/MagicWords.py').read_text(
            encoding='utf-8')
        self.assertIn('cream edge', mw_src.lower())
        self.assertIn('aftershock', mw_src.lower())
        self.assertNotIn('keyblade', mw_src.lower())


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ComboCounterCreamEdgeTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
