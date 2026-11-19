#!/usr/bin/env python3
"""Headless tests: server earned-counter latch uses move-specific windows.

Locks CorruptionGlobals.dedicatedTelegraphCounterWindowSec (Snare / Brute /
Gagster / Oswald / Overlord / Smudge client-parity lengths) and the AI /
HackSlashConfig telegraph latch helpers so __armEarnedCounterForTelegraph
no longer uses a flat PERFECT_DODGE_COUNTER_WINDOW_SEC. No Panda3D, no cream,
no KH.

Run from repo root:
  python3 tests/test_server_earned_counter_move_windows.py
  python3 -m unittest tests.test_server_earned_counter_move_windows -v
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


def _load_corruption_globals():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.toonbase', 'toontown.corruption'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = 2200
    tg.PunchlinePlace = 2300
    tg.SillyStreet = 2100
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


def _load_config():
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
    return ast.parse(_read(rel), filename=rel)


def _class_method(tree: ast.AST, class_name: str, method_name: str):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if (isinstance(child, ast.FunctionDef)
                        and child.name == method_name):
                    return child
    return None


class ServerEarnedCounterMoveWindowsTest(unittest.TestCase):
    """Move-specific telegraph window helpers + AI latch wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()
        cls.cfg = _load_config()

    def test_dedicated_window_helper_matches_client_constants(self):
        win = self.cg.dedicatedTelegraphCounterWindowSec
        cases = (
            (self.cg.ARCHETYPE_SNARE, 'smack',
             self.cg.SNARE_STRING_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_BRUTE, 'spit',
             self.cg.BRUTE_SPIT_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_GAGSTER, 'gag_lob',
             self.cg.GAGSTER_LOB_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_CORRUPT_OSWALD, 'betrayal_lunge',
             self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_CORRUPT_OSWALD, 'smack',
             self.cg.OSWALD_BETRAYAL_LUNGE_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_CORRUPT_OSWALD, 'stain_burst',
             self.cg.OSWALD_STAIN_BURST_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_INK, 'rain',
             self.cg.OVERLORD_RAIN_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_INK, 'slam',
             self.cg.OVERLORD_SLAM_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_INK, 'ink_surge',
             self.cg.OVERLORD_INK_SURGE_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_INK, 'ink_dash',
             self.cg.INK_DASH_COUNTER_WINDOW_SEC),
            (self.cg.ARCHETYPE_INK, 'ink_splat',
             self.cg.INK_SPLAT_COUNTER_WINDOW_SEC),
        )
        seen = set()
        for archetype, move, expected in cases:
            got = win(archetype, move)
            self.assertAlmostEqual(
                got, expected, places=4,
                msg='%s/%s window' % (archetype, move))
            seen.add(round(float(expected), 4))
        # Kit windows span the documented 0.42–0.55 band (not a flat 0.50).
        self.assertIn(0.42, seen)
        self.assertIn(0.55, seen)
        self.assertGreaterEqual(max(seen), 0.55)
        self.assertLessEqual(min(seen), 0.42)

    def test_non_dedicated_moves_return_default(self):
        win = self.cg.dedicatedTelegraphCounterWindowSec
        # Brute slam stays commit-through — no dedicated counter window.
        self.assertIsNone(win(self.cg.ARCHETYPE_BRUTE, 'slam'))
        self.assertAlmostEqual(
            win(self.cg.ARCHETYPE_BRUTE, 'slam', default=0.5), 0.5, places=4)
        # Gagster non-lob / Smudge-less ink without move id → default.
        self.assertIsNone(win(self.cg.ARCHETYPE_GAGSTER, 'smack'))
        self.assertIsNone(win(self.cg.ARCHETYPE_INK, 'smack'))

    def test_windows_differ_from_flat_perfect_dodge(self):
        pd = float(self.cfg.PERFECT_DODGE_COUNTER_WINDOW_SEC)
        self.assertAlmostEqual(pd, 0.50, places=4)
        # At least one kit window must differ from the flat dodge default.
        diffs = []
        for archetype, move in (
                (self.cg.ARCHETYPE_SNARE, 'smack'),
                (self.cg.ARCHETYPE_BRUTE, 'spit'),
                (self.cg.ARCHETYPE_INK, 'slam'),
                (self.cg.ARCHETYPE_CORRUPT_OSWALD, 'stain_burst')):
            w = float(self.cg.dedicatedTelegraphCounterWindowSec(
                archetype, move))
            if abs(w - pd) > 1e-6:
                diffs.append((move, w))
        self.assertGreaterEqual(len(diffs), 3)
        # Slam is shorter; Brute spit is longer.
        self.assertAlmostEqual(
            self.cg.dedicatedTelegraphCounterWindowSec(
                self.cg.ARCHETYPE_INK, 'slam'),
            0.42, places=4)
        self.assertAlmostEqual(
            self.cg.dedicatedTelegraphCounterWindowSec(
                self.cg.ARCHETYPE_BRUTE, 'spit'),
            0.55, places=4)

    def test_hackslash_telegraph_until_helper(self):
        window_fn = self.cfg.earnedCounterWindowSec
        until_fn = self.cfg.earnedTelegraphCounterUntil
        self.assertAlmostEqual(window_fn(), 0.50, places=4)
        self.assertAlmostEqual(window_fn(0.42), 0.42, places=4)
        now = 10.0
        delay = 0.8
        # Flat default path.
        self.assertAlmostEqual(
            until_fn(now, delay), now + delay + 0.50, places=4)
        # Move-specific slam window is shorter than dodge default.
        self.assertAlmostEqual(
            until_fn(now, delay, windowSec=0.42),
            now + delay + 0.42, places=4)
        # earnedCounterUntil still accepts explicit windowSec.
        self.assertAlmostEqual(
            self.cfg.earnedCounterUntil(now + delay, windowSec=0.55),
            now + delay + 0.55, places=4)

    def test_ai_arm_uses_move_specific_helpers(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        src = _read(rel)
        tree = _module_ast(rel)
        method = _class_method(
            tree, 'DistributedCorruptToonAI', '__armEarnedCounterForTelegraph')
        self.assertIsNotNone(method)
        body = ast.get_source_segment(src, method) or ''
        self.assertIn('dedicatedTelegraphCounterWindowSec', body)
        self.assertIn('earnedTelegraphCounterUntil', body)
        self.assertIn('default=', body)
        self.assertIn('windowSec=', body)
        # Latch expiry must go through the helper — not now+delay+flat 0.50.
        self.assertNotIn('until=now + delay + window', body)
        self.assertIn('earnedTelegraphCounterUntil', body)
        # Flat perfect-dodge constant is only the default fallback.
        self.assertIn('PERFECT_DODGE_COUNTER_WINDOW_SEC', body)
        self.assertIn('defaultWindow', body)
        # No KH branding in the arm path.
        body_l = body.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, body_l)

    def test_exports_and_no_kh_in_helpers(self):
        init_src = _read('toontown/hackslash/__init__.py')
        self.assertIn('earnedCounterWindowSec', init_src)
        self.assertIn('earnedTelegraphCounterUntil', init_src)
        helper = _read('toontown/corruption/CorruptionGlobals.py')
        block = helper.split(
            'def dedicatedTelegraphCounterWindowSec', 1)[1][:900].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, block)
        self.assertIn('no cream', block)
        cfg_block = _read('toontown/hackslash/HackSlashConfig.py').split(
            'def earnedTelegraphCounterUntil', 1)[1][:500].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, cfg_block)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ServerEarnedCounterMoveWindowsTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
