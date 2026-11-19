#!/usr/bin/env python3
"""Headless / AST tests: soft-lock priority tiers (boss > elite > ambush).

Binary prefer (#339/#375) let nearest Ambush outrank Overlord during
Unleashed adds + ambush beats. softLockPriorityTier ranks Overlord /
Oswald above Elite above Ambush above fodder; SoftTarget acquire /
sticky yield / cycle-with-lock use those tiers.

Loads SoftTarget + HackSlashConfig without Panda3D, and CorruptionGlobals
with a ToontownGlobals stub.

Run from repo root:
  python3 tests/test_soft_lock_priority_tiers.py
  python3 -m unittest tests.test_soft_lock_priority_tiers -v
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


class SoftLockPriorityTiersTest(unittest.TestCase):
    """Overlord/Oswald > Elite > Ambush > fodder soft-lock prefer."""

    @classmethod
    def setUpClass(cls):
        cls.soft, cls.cfg = _load_soft_target_helpers()
        cls.cg = _load_panda_free_corruption()

    def test_config_and_no_kh_cream(self):
        self.assertTrue(self.cfg.TARGET_PRIORITY_ENABLED)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('priority tiers', cfg_src.lower())
        soft_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('softLockPriorityTier', soft_src)
        self.assertNotIn('kingdom hearts', soft_src.lower())
        # Disclaimer may mention KH; strip it before branding scan.
        cleaned = soft_src.lower().replace(
            'without kh branding / keyblades', '')
        self.assertNotIn('keyblade', cleaned)
        cg_src = _read('toontown/corruption/CorruptionGlobals.py')
        tier_idx = cg_src.index('def softLockPriorityTier')
        next_def = cg_src.find('\ndef ', tier_idx + 1)
        tier_body = cg_src[tier_idx:next_def if next_def > 0 else tier_idx + 2000]
        snip = tier_body.lower()
        self.assertNotIn('cream', snip)
        self.assertNotIn('keyblade', snip)
        self.assertNotIn('kingdom hearts', snip)

    def test_soft_lock_priority_tier_constants_and_gate(self):
        cg = self.cg
        boss = cg.SOFT_LOCK_PRIORITY_TIER_BOSS
        elite = cg.SOFT_LOCK_PRIORITY_TIER_ELITE
        ambush = cg.SOFT_LOCK_PRIORITY_TIER_AMBUSH
        fodder = cg.SOFT_LOCK_PRIORITY_TIER_FODDER
        self.assertEqual(boss, 0)
        self.assertEqual(elite, 1)
        self.assertEqual(ambush, 2)
        self.assertEqual(fodder, 3)
        self.assertLess(boss, elite)
        self.assertLess(elite, ambush)
        self.assertLess(ambush, fodder)

        tier = cg.softLockPriorityTier
        # Boss / Oswald / Overlord phase.
        self.assertEqual(tier(cg.ARCHETYPE_CORRUPT_OSWALD), boss)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='Ink Overlord'), boss)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='Ink Overlord Unleashed'), boss)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, finalePhase=1), boss)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, finalePhase=2), boss)
        # Elite / Ambush rename prefixes.
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='Elite Ink Smudge'), elite)
        self.assertEqual(
            tier(cg.ARCHETYPE_BRUTE, name='Elite Sludge Brute'), elite)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='Ambush Ink Smudge'), ambush)
        self.assertEqual(
            tier(cg.ARCHETYPE_BRUTE, name='Ambush Sludge Brute'), ambush)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='elite ink smudge'), elite)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='AMBUSH Ink Smudge'), ambush)
        # Pack fodder.
        self.assertEqual(tier(cg.ARCHETYPE_INK), fodder)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='Ink Smudge'), fodder)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='Elite'), fodder)
        self.assertEqual(
            tier(cg.ARCHETYPE_INK, name='Ambush'), fodder)
        # Subject gate stays True for any non-fodder tier.
        subject = cg.isSoftLockPrioritySubject
        self.assertTrue(subject(cg.ARCHETYPE_CORRUPT_OSWALD))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='Ink Overlord'))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='Elite Ink Smudge'))
        self.assertTrue(subject(
            cg.ARCHETYPE_BRUTE, name='Ambush Sludge Brute'))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ink Smudge'))
        # Split helpers feed the shared Elite/Ambush gate.
        self.assertTrue(cg.isElitePreferName('Elite Ink Smudge'))
        self.assertFalse(cg.isElitePreferName('Ambush Ink Smudge'))
        self.assertTrue(cg.isAmbushPreferName('Ambush Ink Smudge'))
        self.assertFalse(cg.isAmbushPreferName('Elite Ink Smudge'))
        self.assertTrue(cg.isEliteOrAmbushPreferName('Elite Ink Smudge'))
        self.assertTrue(cg.isEliteOrAmbushPreferName('Ambush Ink Smudge'))

    def test_acquire_rank_and_pick_respect_tiers(self):
        cg = self.cg
        soft = self.soft
        boss = cg.SOFT_LOCK_PRIORITY_TIER_BOSS
        elite = cg.SOFT_LOCK_PRIORITY_TIER_ELITE
        ambush = cg.SOFT_LOCK_PRIORITY_TIER_AMBUSH
        fodder = cg.SOFT_LOCK_PRIORITY_TIER_FODDER
        rank = soft.softLockAcquireRank
        pick = soft.pickSoftLockAcquire

        # Farther Overlord beats nearer Elite / Ambush / fodder.
        self.assertLess(rank(14.0, boss), rank(3.0, elite))
        self.assertLess(rank(14.0, boss), rank(2.0, ambush))
        self.assertLess(rank(14.0, boss), rank(1.0, fodder))
        # Farther Elite beats nearer Ambush / fodder.
        self.assertLess(rank(12.0, elite), rank(2.5, ambush))
        self.assertLess(rank(12.0, elite), rank(1.5, fodder))
        # Farther Ambush still beats nearer fodder.
        self.assertLess(rank(11.0, ambush), rank(1.0, fodder))
        # Within tier, nearer wins.
        self.assertLess(rank(4.0, boss), rank(9.0, boss))
        self.assertLess(rank(3.0, elite), rank(8.0, elite))
        # Legacy bool still maps True→boss, False→fodder.
        self.assertEqual(rank(5.0, True), rank(5.0, boss))
        self.assertEqual(rank(5.0, False), rank(5.0, fodder))

        overlord = ('doId', 1)
        oswald = ('doId', 2)
        elite_t = ('doId', 3)
        ambush_t = ('doId', 4)
        smudge = ('doId', 5)

        # Near Ambush must not outrank far Overlord.
        self.assertEqual(
            pick([
                (ambush, 2.0, ambush_t),
                (boss, 13.0, overlord),
            ]),
            overlord)
        # Near Elite must not outrank far Oswald.
        self.assertEqual(
            pick([
                (elite, 2.5, elite_t),
                (boss, 12.0, oswald),
            ]),
            oswald)
        # Near Ambush loses to far Elite.
        self.assertEqual(
            pick([
                (ambush, 1.5, ambush_t),
                (elite, 10.0, elite_t),
            ]),
            elite_t)
        # Mixed scrum → Overlord.
        self.assertEqual(
            pick([
                (fodder, 1.0, smudge),
                (ambush, 2.0, ambush_t),
                (elite, 3.0, elite_t),
                (boss, 11.0, overlord),
            ]),
            overlord)
        # No boss → Elite over nearer Ambush / fodder.
        self.assertEqual(
            pick([
                (fodder, 1.0, smudge),
                (ambush, 2.0, ambush_t),
                (elite, 9.0, elite_t),
            ]),
            elite_t)

    def test_sticky_and_cycle_yield_to_higher_tier(self):
        cg = self.cg
        soft = self.soft
        boss = cg.SOFT_LOCK_PRIORITY_TIER_BOSS
        elite = cg.SOFT_LOCK_PRIORITY_TIER_ELITE
        ambush = cg.SOFT_LOCK_PRIORITY_TIER_AMBUSH
        fodder = cg.SOFT_LOCK_PRIORITY_TIER_FODDER
        yield_fn = soft.shouldStickyYieldToPriority
        prefer = soft.shouldCyclePreferPriority

        # Ambush sticky / lock yields to Elite and Overlord.
        self.assertTrue(yield_fn(
            True, True, lockedTier=ambush, candidateTier=elite))
        self.assertTrue(yield_fn(
            True, True, lockedTier=ambush, candidateTier=boss))
        self.assertTrue(prefer(
            True, True, lockedTier=ambush, candidateTier=elite))
        self.assertTrue(prefer(
            True, True, lockedTier=ambush, candidateTier=boss))
        # Elite yields to boss, not to Ambush.
        self.assertTrue(yield_fn(
            True, True, lockedTier=elite, candidateTier=boss))
        self.assertFalse(yield_fn(
            True, True, lockedTier=elite, candidateTier=ambush))
        self.assertTrue(prefer(
            True, True, lockedTier=elite, candidateTier=boss))
        self.assertFalse(prefer(
            True, True, lockedTier=elite, candidateTier=ambush))
        # Boss keeps sticky / yaw-orbits.
        self.assertFalse(yield_fn(
            True, True, lockedTier=boss, candidateTier=elite))
        self.assertFalse(yield_fn(
            True, True, lockedTier=boss, candidateTier=ambush))
        self.assertFalse(prefer(
            True, True, lockedTier=boss, candidateTier=elite))
        # Fodder yields to any prefer tier.
        self.assertTrue(yield_fn(
            False, True, lockedTier=fodder, candidateTier=ambush))
        self.assertTrue(prefer(
            False, True, lockedTier=fodder, candidateTier=boss))
        # Same tier → no yield / no forced jump.
        self.assertFalse(yield_fn(
            True, True, lockedTier=ambush, candidateTier=ambush))
        self.assertFalse(prefer(
            True, True, lockedTier=elite, candidateTier=elite))
        # Disabled → never.
        self.assertFalse(yield_fn(
            False, True, enabled=False,
            lockedTier=fodder, candidateTier=boss))
        self.assertFalse(prefer(
            False, True, enabled=False,
            lockedTier=ambush, candidateTier=boss))
        # Legacy binary path still works for older callers / tests.
        self.assertTrue(yield_fn(False, True))
        self.assertFalse(yield_fn(True, True))
        self.assertTrue(prefer(False, True))
        self.assertFalse(prefer(True, True))

    def test_soft_target_ast_wires_tiers(self):
        for method in ('acquire', 'cycle'):
            names = _method_body_names(
                'toontown/hackslash/SoftTarget.py',
                'SoftTargetFinder',
                method)
            self.assertIn(
                '_priorityTier', names,
                msg='%s missing _priorityTier' % method)
            self.assertIn('pickSoftLockAcquire', names)
        acquire = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            'acquire')
        self.assertIn('shouldStickyYieldToPriority', acquire)
        self.assertIn('lockedTier', acquire)
        self.assertIn('candidateTier', acquire)
        cycle = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            'cycle')
        self.assertIn('shouldCyclePreferPriority', cycle)
        self.assertIn('lockedTier', cycle)
        self.assertIn('candidateTier', cycle)
        tier_names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            '_priorityTier')
        self.assertIn('softLockPriorityTier', tier_names)
        soft_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('lockedTier', soft_src)
        self.assertIn('candidateTier', soft_src)
        self.assertIn('Overlord/Oswald > Elite > Ambush', soft_src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockPriorityTiersTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
