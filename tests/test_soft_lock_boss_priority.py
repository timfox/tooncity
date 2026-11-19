#!/usr/bin/env python3
"""Headless / AST tests: soft-lock prefers Overlord / Corrupted Oswald.

Loads SoftTarget + HackSlashConfig without Panda3D, and CorruptionGlobals
with a ToontownGlobals stub. Covers acquire rank / pick helpers, archetype
priority gates (Overlord name + Oswald vs pack Smudge adds), and AST wiring
in SoftTargetFinder.acquire / cycle.

Run from repo root:
  python3 tests/test_soft_lock_boss_priority.py
  python3 -m unittest tests.test_soft_lock_boss_priority -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

LOOPY = 2200
PUNCHLINE = 2300
SILLY = 2100


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


def _load_panda_free_corruption():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = 2000
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    cg_path = REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
    cg_spec = importlib.util.spec_from_file_location(
        'toontown.corruption.CorruptionGlobals', cg_path)
    cg = importlib.util.module_from_spec(cg_spec)
    assert cg_spec.loader is not None
    sys.modules['toontown.corruption.CorruptionGlobals'] = cg
    cg_spec.loader.exec_module(cg)
    sys.modules['toontown.corruption'].CorruptionGlobals = cg
    return cg


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


class SoftLockBossPriorityTest(unittest.TestCase):
    """Acquire rank + corruption gates so climax/twist beat pack adds."""

    @classmethod
    def setUpClass(cls):
        cls.soft, cls.cfg = _load_soft_target_helpers()
        cls.cg = _load_panda_free_corruption()

    def test_config_priority_toggle(self):
        self.assertTrue(self.cfg.TARGET_PRIORITY_ENABLED)
        self.assertGreater(self.cfg.TARGET_RANGE, 0.0)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)

    def test_soft_lock_acquire_rank_priority_beats_nearer_add(self):
        rank = self.soft.softLockAcquireRank
        # Far Overlord (priority) beats near Smudge add.
        self.assertLess(rank(12.0, True), rank(3.0, False))
        # Within tier, nearer wins.
        self.assertLess(rank(4.0, True), rank(9.0, True))
        self.assertLess(rank(2.0, False), rank(8.0, False))
        # Equal distance: priority still wins.
        self.assertLess(rank(5.0, True), rank(5.0, False))

    def test_pick_soft_lock_acquire_prefers_overlord_and_oswald(self):
        pick = self.soft.pickSoftLockAcquire
        smudge = ('doId', 1)
        overlord = ('doId', 2)
        oswald = ('doId', 3)

        self.assertIsNone(pick([]))

        # Nearer Smudge vs farther Overlord → Overlord.
        self.assertEqual(
            pick([
                (False, 2.5, smudge),
                (True, 11.0, overlord),
            ]),
            overlord)

        # Nearer Smudge vs farther Oswald → Oswald.
        self.assertEqual(
            pick([
                (False, 1.0, smudge),
                (True, 10.5, oswald),
            ]),
            oswald)

        # Two priority subjects → nearer wins.
        self.assertEqual(
            pick([
                (True, 9.0, overlord),
                (True, 4.0, oswald),
            ]),
            oswald)

        # Pack-only → nearest Smudge.
        other = ('doId', 4)
        self.assertEqual(
            pick([
                (False, 6.0, other),
                (False, 3.0, smudge),
            ]),
            smudge)

    def test_soft_lock_priority_subject_gate(self):
        cg = self.cg
        subject = cg.isSoftLockPrioritySubject
        # Street pack archetypes / Smudge adds — never.
        self.assertFalse(subject(cg.ARCHETYPE_INK))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ink Smudge'))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ink Smudge 2'))
        self.assertFalse(subject(cg.ARCHETYPE_BRUTE, name='Sludge Brute'))
        self.assertFalse(subject(cg.ARCHETYPE_SNARE))
        self.assertFalse(subject(cg.ARCHETYPE_GAGSTER))
        # Corrupted Oswald chase — always.
        self.assertTrue(subject(cg.ARCHETYPE_CORRUPT_OSWALD))
        self.assertTrue(subject(
            cg.ARCHETYPE_CORRUPT_OSWALD, name='Corrupted Oswald'))
        # Overlord via name tokens (client path — no per-DO finalePhase DC).
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord'))
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord Rising'))
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord Unleashed'))
        # Per-toon finalePhase (AI Overlord DOs) — not director street phase
        # on Smudge adds (those keep finalePhase=0 on the DO).
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=1))
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=2))
        self.assertFalse(subject(
            cg.ARCHETYPE_INK, name='Ink Smudge', finalePhase=0))
        # Elite / Ambush pack rename prefixes — permanent soft-lock prefer.
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Elite Ink Smudge'))
        self.assertTrue(subject(
            cg.ARCHETYPE_BRUTE, name='Ambush Sludge Brute'))
        # Gate is independent of boss HP bar HUD toggle.
        prev = cg.BOSS_HP_BAR_ENABLED
        try:
            cg.BOSS_HP_BAR_ENABLED = False
            self.assertTrue(subject(cg.ARCHETYPE_CORRUPT_OSWALD))
            self.assertTrue(subject(
                cg.ARCHETYPE_INK, name='Ink Overlord'))
            self.assertTrue(subject(
                cg.ARCHETYPE_INK, name='Elite Ink Smudge'))
        finally:
            cg.BOSS_HP_BAR_ENABLED = prev

    def test_soft_target_acquire_ast_uses_priority_pick(self):
        names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            'acquire')
        self.assertIn('pickSoftLockAcquire', names)
        self.assertIn('_isPriorityTarget', names)

    def test_soft_target_cycle_fresh_lock_uses_priority_pick(self):
        names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            'cycle')
        self.assertIn('pickSoftLockAcquire', names)
        self.assertIn('_isPriorityTarget', names)

    def test_soft_target_priority_helper_ast(self):
        names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            '_isPriorityTarget')
        self.assertIn('_priorityTier', names)
        tier_names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            '_priorityTier')
        self.assertIn('softLockPriorityTier', tier_names)
        self.assertIn('getattr', tier_names)
        self.assertIn('HackSlashConfig', tier_names)
        # Tunable is read via getattr(..., 'TARGET_PRIORITY_ENABLED', ...).
        helper_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('TARGET_PRIORITY_ENABLED', helper_src)
        # Must not glue onto director street phase for every pack add.
        self.assertNotIn('reclaimDirector', tier_names)
        self.assertNotIn('reclaimDirector', names)

    def test_package_exports_priority_helpers(self):
        init_src = _read('toontown/hackslash/__init__.py')
        self.assertIn('softLockAcquireRank', init_src)
        self.assertIn('pickSoftLockAcquire', init_src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockBossPriorityTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
