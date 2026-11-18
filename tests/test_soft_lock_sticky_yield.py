#!/usr/bin/env python3
"""Headless / AST tests: soft-lock sticky yield to Overlord / Oswald.

After #339 fresh-acquire priority, sticky hold must yield when a higher-
priority Overlord or Corrupted Oswald is in the acquire cone instead of
gluing onto pack Smudge adds for TARGET_LOCK_HOLD_SEC.

Loads SoftTarget + HackSlashConfig without Panda3D. Covers the pure
shouldStickyYieldToPriority helper and AST wiring in SoftTargetFinder.acquire.

Run from repo root:
  python3 tests/test_soft_lock_sticky_yield.py
  python3 -m unittest tests.test_soft_lock_sticky_yield -v
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


def _load_soft_target_helpers():
    """Load SoftTarget helpers without importing MeleeCombat / Panda."""
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

    soft_path = REPO_ROOT / 'toontown' / 'hackslash' / 'SoftTarget.py'
    soft_spec = importlib.util.spec_from_file_location(
        'toontown.hackslash.SoftTarget', soft_path)
    soft = importlib.util.module_from_spec(soft_spec)
    assert soft_spec.loader is not None
    sys.modules['toontown.hackslash.SoftTarget'] = soft
    soft_spec.loader.exec_module(soft)
    sys.modules['toontown.hackslash'].SoftTarget = soft
    return soft, cfg


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _method_body_names(rel: str, class_name: str, method_name: str) -> set[str]:
    tree = ast.parse(_read(rel))
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.name != method_name:
                continue
            for child in ast.walk(item):
                if isinstance(child, ast.Name):
                    out.add(child.id)
                elif isinstance(child, ast.Attribute):
                    out.add(child.attr)
    return out


class SoftLockStickyYieldTest(unittest.TestCase):
    """Sticky hold yields pack-add glue when Overlord/Oswald is available."""

    @classmethod
    def setUpClass(cls):
        cls.soft, cls.cfg = _load_soft_target_helpers()

    def test_config_priority_toggle_still_on(self):
        self.assertTrue(self.cfg.TARGET_PRIORITY_ENABLED)
        self.assertGreater(self.cfg.TARGET_LOCK_HOLD_SEC, 0.0)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_should_sticky_yield_to_priority_helper(self):
        yield_fn = self.soft.shouldStickyYieldToPriority
        # Glued add + Overlord/Oswald in cone → yield.
        self.assertTrue(yield_fn(False, True))
        self.assertTrue(yield_fn(False, True, enabled=True))
        # Already on priority → keep sticky (no yield).
        self.assertFalse(yield_fn(True, True))
        self.assertFalse(yield_fn(True, False))
        # No priority candidate → keep sticky on add.
        self.assertFalse(yield_fn(False, False))
        # Priority disabled → never yield (nearest-only restore).
        self.assertFalse(yield_fn(False, True, enabled=False))
        # Default enabled reads HackSlashConfig.TARGET_PRIORITY_ENABLED.
        prev = self.cfg.TARGET_PRIORITY_ENABLED
        try:
            self.cfg.TARGET_PRIORITY_ENABLED = False
            self.assertFalse(yield_fn(False, True))
            self.cfg.TARGET_PRIORITY_ENABLED = True
            self.assertTrue(yield_fn(False, True))
        finally:
            self.cfg.TARGET_PRIORITY_ENABLED = prev

    def test_sticky_yield_then_pick_prefers_boss(self):
        """Yield decision + #339 pick: glued add → Overlord / Oswald."""
        yield_fn = self.soft.shouldStickyYieldToPriority
        pick = self.soft.pickSoftLockAcquire
        smudge = ('doId', 1)
        overlord = ('doId', 2)
        oswald = ('doId', 3)

        self.assertTrue(yield_fn(False, True))
        self.assertEqual(
            pick([
                (False, 2.5, smudge),
                (True, 11.0, overlord),
            ]),
            overlord)
        self.assertEqual(
            pick([
                (False, 1.0, smudge),
                (True, 10.5, oswald),
            ]),
            oswald)
        # No yield → sticky would keep the add; pick still unused.
        self.assertFalse(yield_fn(False, False))

    def test_acquire_ast_wires_sticky_yield(self):
        names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            'acquire')
        self.assertIn('shouldStickyYieldToPriority', names)
        self.assertIn('_isPriorityTarget', names)
        self.assertIn('pickSoftLockAcquire', names)
        self.assertIn('_inStickyCone', names)
        # Sticky path still refreshes hold when not yielding.
        self.assertIn('TARGET_LOCK_HOLD_SEC', names)

    def test_soft_target_module_documents_sticky_yield(self):
        src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('shouldStickyYieldToPriority', src)
        self.assertIn('Yield sticky', src)
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('sticky hold yield', cfg_src.lower())

    def test_package_exports_sticky_yield_helper(self):
        init_src = _read('toontown/hackslash/__init__.py')
        self.assertIn('shouldStickyYieldToPriority', init_src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockStickyYieldTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
