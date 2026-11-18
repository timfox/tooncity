#!/usr/bin/env python3
"""Headless / AST tests: soft-lock prefers Elite and Ambush pack hostiles.

After #339/#347/#356 Overlord/Oswald prefer and #372 brief Ambush pulse,
Elite / Ambush rename prefixes must permanently score as soft-lock
priority subjects so mid-wave scrums do not glue onto nearer fodder.

Loads SoftTarget + HackSlashConfig without Panda3D, and CorruptionGlobals
with a ToontownGlobals stub. Covers isSoftLockPrioritySubject Elite/Ambush
gates, acquire pick preference, and SoftTarget priority wiring.

Run from repo root:
  python3 tests/test_soft_lock_elite_ambush_prefer.py
  python3 -m unittest tests.test_soft_lock_elite_ambush_prefer -v
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


class SoftLockEliteAmbushPreferTest(unittest.TestCase):
    """Elite / Ambush name prefixes permanently prefer over pack fodder."""

    @classmethod
    def setUpClass(cls):
        cls.soft, cls.cfg = _load_soft_target_helpers()
        cls.cg = _load_panda_free_corruption()

    def test_config_priority_toggle_and_no_kh(self):
        self.assertTrue(self.cfg.TARGET_PRIORITY_ENABLED)
        hint_l = self.cfg.DEMO_HINT.lower()
        self.assertNotIn('keyblade', hint_l)
        self.assertNotIn('kingdom hearts', hint_l)
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('Elite/Ambush', cfg_src)
        # Priority docs mention Elite/Ambush; no KH product branding beyond
        # the existing "without KH branding / keyblades" disclaimer.
        soft_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('Elite / Ambush', soft_src)
        self.assertNotIn('kingdom hearts', soft_src.lower())
        self.assertNotIn('keyblade', soft_src.lower().replace(
            'without kh branding / keyblades', ''))

    def test_soft_lock_priority_subject_elite_ambush_prefixes(self):
        cg = self.cg
        subject = cg.isSoftLockPrioritySubject
        # Plain pack fodder — never.
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ink Smudge'))
        self.assertFalse(subject(cg.ARCHETYPE_BRUTE, name='Sludge Brute'))
        self.assertFalse(subject(cg.ARCHETYPE_SNARE, name='Balloon Snare'))
        self.assertFalse(subject(cg.ARCHETYPE_GAGSTER, name='Gunk Gagster'))
        # Bare tokens without the rename space prefix — not Elite/Ambush.
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Elite'))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ambush'))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='eliteink'))
        # Elite rename prefix (ReclaimGlobals.ELITE_NAME_PREFIX).
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='Elite Ink Smudge'))
        self.assertTrue(subject(cg.ARCHETYPE_BRUTE, name='Elite Sludge Brute'))
        self.assertTrue(subject(cg.ARCHETYPE_SNARE, name='Elite Balloon Snare'))
        self.assertTrue(subject(
            cg.ARCHETYPE_GAGSTER, name='Elite Gunk Gagster'))
        # Ambush rename prefix (ReclaimGlobals.AMBUSH_NAME_PREFIX).
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='Ambush Ink Smudge'))
        self.assertTrue(subject(cg.ARCHETYPE_BRUTE, name='Ambush Sludge Brute'))
        # Case-insensitive prefix match (client/AI name casing).
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='elite ink smudge'))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='AMBUSH Ink Smudge'))
        # Prior Overlord / Oswald gates still hold.
        self.assertTrue(subject(cg.ARCHETYPE_CORRUPT_OSWALD))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='Ink Overlord'))
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=1))

    def test_pick_soft_lock_acquire_prefers_elite_and_ambush(self):
        pick = self.soft.pickSoftLockAcquire
        fodder = ('doId', 1)
        elite = ('doId', 2)
        ambush = ('doId', 3)
        overlord = ('doId', 4)

        # Nearer fodder vs farther Elite → Elite.
        self.assertEqual(
            pick([
                (False, 2.0, fodder),
                (True, 11.0, elite),
            ]),
            elite)
        # Nearer fodder vs farther Ambush → Ambush.
        self.assertEqual(
            pick([
                (False, 1.5, fodder),
                (True, 10.0, ambush),
            ]),
            ambush)
        # Two priority subjects → nearer wins (Elite vs Overlord).
        self.assertEqual(
            pick([
                (True, 9.0, overlord),
                (True, 4.0, elite),
            ]),
            elite)
        # Rank helper: Elite priority beats nearer fodder.
        rank = self.soft.softLockAcquireRank
        self.assertLess(rank(12.0, True), rank(3.0, False))

    def test_sticky_and_cycle_helpers_still_yield_to_priority(self):
        yield_fn = self.soft.shouldStickyYieldToPriority
        prefer = self.soft.shouldCyclePreferPriority
        # Glued fodder + Elite/Ambush in cone → yield / jump.
        self.assertTrue(yield_fn(False, True))
        self.assertTrue(prefer(False, True))
        # Already on Elite/Ambush → keep sticky / yaw-orbit.
        self.assertFalse(yield_fn(True, True))
        self.assertFalse(prefer(True, True))

    def test_soft_target_priority_helper_ast_still_wired(self):
        names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            '_isPriorityTarget')
        self.assertIn('isSoftLockPrioritySubject', names)
        self.assertIn('isAmbushPreferName', names)
        soft_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('Elite / Ambush', soft_src)
        self.assertIn('isSoftLockPrioritySubject', soft_src)
        cg_src = _read('toontown/corruption/CorruptionGlobals.py')
        self.assertIn("startswith('elite ')", cg_src)
        self.assertIn("startswith('ambush ')", cg_src)
        # No cream deepen / no KH branding in the gate.
        gate_idx = cg_src.index('def isSoftLockPrioritySubject')
        gate_snip = cg_src[gate_idx:gate_idx + 900].lower()
        self.assertNotIn('cream', gate_snip)
        self.assertNotIn('keyblade', gate_snip)
        self.assertNotIn('kingdom hearts', gate_snip)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SoftLockEliteAmbushPreferTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
