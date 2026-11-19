#!/usr/bin/env python3
"""Headless tests: soft-lock cycle remaps melee cadence combo (TC-409).

After #386, server hit cadence is per-hostile. Tab/` mid-string must remap
client comboIndex to opener 0 so the new AI accepts the next punch. Locks
HackSlashConfig.remapMeleeComboIndexOnSoftLockChange and MeleeCombat
_cycleSoftLockTarget / tick wiring. No Panda3D required.

Run from repo root:
  python3 tests/test_soft_lock_cycle_melee_cadence.py
  python3 -m unittest tests.test_soft_lock_cycle_melee_cadence -v
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


def _load_config():
    """Load HackSlashConfig without importing MeleeCombat / Panda3D."""
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


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel))


def _class_method(tree: ast.AST, class_name: str, method_name: str):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if (isinstance(child, ast.FunctionDef)
                        and child.name == method_name):
                    return child
    return None


def _class_method_names(tree: ast.AST, class_name: str) -> set:
    names = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    names.add(child.name)
    return names


def _method_body_names(rel: str, class_name: str, method_name: str) -> set:
    tree = _module_ast(rel)
    method = _class_method(tree, class_name, method_name)
    if method is None:
        return set()
    names = set()
    for node in ast.walk(method):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


class SoftLockCycleMeleeCadenceTest(unittest.TestCase):
    """Combo remap on soft-lock cycle / sticky target change."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_config()

    def test_config_remap_toggle_armed(self):
        self.assertTrue(self.cfg.MELEE_COMBO_REMAP_ON_SOFT_LOCK_CHANGE)
        self.assertTrue(self.cfg.MELEE_HIT_CADENCE_ENABLED)
        self.assertTrue(self.cfg.TARGET_CYCLE_ENABLED)

    def test_remap_helper_resets_on_snap(self):
        remap = self.cfg.remapMeleeComboIndexOnSoftLockChange
        # Fresh lock key → opener regardless of mid/finisher string.
        self.assertEqual(remap(0, True), 0)
        self.assertEqual(remap(1, True), 0)
        self.assertEqual(remap(2, True), 0)
        # Same-key refresh keeps live beat.
        self.assertEqual(remap(0, False), 0)
        self.assertEqual(remap(1, False), 1)
        self.assertEqual(remap(2, False), 2)
        # Toggle off leaves index alone even when snapped.
        self.assertEqual(remap(2, True, enabled=False), 2)
        self.assertEqual(remap(1, False, enabled=False), 1)
        # Bad / out-of-range inputs clamp safely.
        self.assertEqual(remap(-3, False), 0)
        self.assertEqual(remap(99, False), self.cfg.COMBO_LENGTH - 1)
        self.assertEqual(remap('x', True), 0)

    def test_remapped_opener_accepted_by_per_hostile_cadence(self):
        """New hostile expects 0; remapped client index must pass accept."""
        accept = self.cfg.acceptMeleeHitIndex
        expected = self.cfg.expectedMeleeComboHitIndex
        remap = self.cfg.remapMeleeComboIndexOnSoftLockChange
        # Mid-string on old hostile, then Tab onto fresh AI state.
        mid = 1
        remapped = remap(mid, snapped=True)
        self.assertEqual(remapped, 0)
        fresh_expected = expected(-1, 0.0, 10.0)
        self.assertEqual(fresh_expected, 0)
        self.assertTrue(accept(remapped, fresh_expected))
        # Without remap, mid would be rejected against opener expect.
        self.assertFalse(accept(mid, fresh_expected))
        # Finisher spam against fresh hostile still blocked.
        self.assertFalse(accept(2, 0))

    def test_melee_combat_wires_remap_on_cycle_and_tick(self):
        rel = 'toontown/hackslash/MeleeCombat.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'MeleeCombatController')
        self.assertIn('_remapMeleeCadenceComboForSoftLockChange', methods)
        self.assertIn('_cycleSoftLockTarget', methods)

        cycle_names = _method_body_names(
            rel, 'MeleeCombatController', '_cycleSoftLockTarget')
        self.assertIn(
            '_remapMeleeCadenceComboForSoftLockChange', cycle_names,
            msg='Tab/` cycle must remap combo on lock-key change')

        tick_names = _method_body_names(
            rel, 'MeleeCombatController', '_tick')
        self.assertIn(
            '_remapMeleeCadenceComboForSoftLockChange', tick_names,
            msg='sticky yield / acquire snap must remap combo')

        remap_src = ast.get_source_segment(
            _read(rel),
            _class_method(
                tree, 'MeleeCombatController',
                '_remapMeleeCadenceComboForSoftLockChange')) or ''
        self.assertIn('remapMeleeComboIndexOnSoftLockChange', remap_src)
        self.assertIn('MELEE_COMBO_REMAP_ON_SOFT_LOCK_CHANGE', remap_src)
        self.assertIn('_finishSwing', remap_src)
        self.assertIn('_clearJuggleCancelWindow', remap_src)
        self.assertIn('comboIndex', remap_src)

    def test_exports_remap_helper(self):
        init_src = _read('toontown/hackslash/__init__.py')
        self.assertIn('remapMeleeComboIndexOnSoftLockChange', init_src)
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('MELEE_COMBO_REMAP_ON_SOFT_LOCK_CHANGE', cfg_src)
        self.assertIn('def remapMeleeComboIndexOnSoftLockChange', cfg_src)
        # Contract note: per-hostile cadence + soft-lock cycle.
        block = cfg_src.split(
            'def remapMeleeComboIndexOnSoftLockChange', 1)[1][:700].lower()
        self.assertIn('opener', block)
        self.assertIn('soft-lock', block)

    def test_no_kh_branding_in_remap(self):
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        block = cfg_src.split(
            'MELEE_COMBO_REMAP_ON_SOFT_LOCK_CHANGE', 1)[1][:900].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, block)
        melee_src = _read('toontown/hackslash/MeleeCombat.py')
        remap_block = melee_src.split(
            '_remapMeleeCadenceComboForSoftLockChange', 1)[1][:900].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, remap_block)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockCycleMeleeCadenceTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
