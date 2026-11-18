#!/usr/bin/env python3
"""Headless / AST tests: soft-lock cycle-with-lock prefers Overlord / Oswald.

After #339 fresh-acquire priority and #347 sticky yield, manual Tab/` with
an existing lock on a pack add must jump to Overlord / Corrupted Oswald in
the cycle cone instead of yaw-orbiting through Smudge trash.

Loads SoftTarget + HackSlashConfig without Panda3D. Covers the pure
shouldCyclePreferPriority helper and AST wiring in SoftTargetFinder.cycle.

Run from repo root:
  python3 tests/test_soft_lock_cycle_boss_prefer.py
  python3 -m unittest tests.test_soft_lock_cycle_boss_prefer -v
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


class SoftLockCycleBossPreferTest(unittest.TestCase):
    """Tab/` with lock on trash jumps to Overlord/Oswald in cycle cone."""

    @classmethod
    def setUpClass(cls):
        cls.soft, cls.cfg = _load_soft_target_helpers()

    def test_config_priority_toggle_still_on(self):
        self.assertTrue(self.cfg.TARGET_PRIORITY_ENABLED)
        self.assertTrue(self.cfg.TARGET_CYCLE_ENABLED)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('cycle-with-lock', cfg_src.lower())

    def test_should_cycle_prefer_priority_helper(self):
        prefer = self.soft.shouldCyclePreferPriority
        # Glued add + Overlord/Oswald in cycle cone → prefer jump.
        self.assertTrue(prefer(False, True))
        self.assertTrue(prefer(False, True, enabled=True))
        # Already on priority → yaw-orbit (no forced jump).
        self.assertFalse(prefer(True, True))
        self.assertFalse(prefer(True, False))
        # No priority candidate → yaw-orbit through pack.
        self.assertFalse(prefer(False, False))
        # Priority disabled → never prefer (nearest/orbit restore).
        self.assertFalse(prefer(False, True, enabled=False))
        # Default enabled reads HackSlashConfig.TARGET_PRIORITY_ENABLED.
        prev = self.cfg.TARGET_PRIORITY_ENABLED
        try:
            self.cfg.TARGET_PRIORITY_ENABLED = False
            self.assertFalse(prefer(False, True))
            self.cfg.TARGET_PRIORITY_ENABLED = True
            self.assertTrue(prefer(False, True))
        finally:
            self.cfg.TARGET_PRIORITY_ENABLED = prev

    def test_cycle_prefer_then_pick_jumps_to_boss(self):
        """Prefer decision + #339 pick: locked add → Overlord / Oswald."""
        prefer = self.soft.shouldCyclePreferPriority
        pick = self.soft.pickSoftLockAcquire
        cycle = self.soft.pickCycleChoice
        smudge_a = ('doId', 1)
        smudge_b = ('doId', 2)
        overlord = ('doId', 3)
        oswald = ('doId', 4)

        self.assertTrue(prefer(False, True))
        # Locked on near Smudge — priority pick jumps to far Overlord.
        self.assertEqual(
            pick([
                (True, 11.0, overlord),
            ]),
            overlord)
        self.assertEqual(
            pick([
                (True, 10.5, oswald),
            ]),
            oswald)
        # Two priority subjects → nearer wins (same as acquire).
        self.assertEqual(
            pick([
                (True, 9.0, overlord),
                (True, 4.0, oswald),
            ]),
            oswald)
        # Without prefer → yaw orbit would step to next Smudge, not boss.
        self.assertFalse(prefer(False, False))
        ordered = [smudge_a, smudge_b, overlord]
        self.assertEqual(
            cycle(ordered, smudge_a, 1),
            (smudge_b, True))
        # Already on Overlord → prefer is False; orbit can leave boss.
        self.assertFalse(prefer(True, True))
        self.assertEqual(
            cycle(ordered, overlord, 1),
            (smudge_a, True))

    def test_cycle_ast_wires_prefer_priority(self):
        names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            'cycle')
        self.assertIn('shouldCyclePreferPriority', names)
        self.assertIn('_isPriorityTarget', names)
        self.assertIn('pickSoftLockAcquire', names)
        self.assertIn('pickCycleChoice', names)

    def test_soft_target_module_documents_cycle_prefer(self):
        src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('shouldCyclePreferPriority', src)
        self.assertIn('yaw-orbit', src.lower())
        # Module doc + locked-path comment cover the gap.
        self.assertIn('jumps to Overlord/Oswald', src)
        self.assertIn('pack add jumps to Overlord/Oswald', src)

    def test_package_exports_cycle_prefer_helper(self):
        init_src = _read('toontown/hackslash/__init__.py')
        self.assertIn('shouldCyclePreferPriority', init_src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockCycleBossPreferTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
