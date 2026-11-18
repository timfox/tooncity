#!/usr/bin/env python3
"""Headless tests: wire reclaimAmbushSpawn into mid-fight pressure / soft-lock cue.

Loads ReclaimGlobals + SoftTarget / HackSlashConfig with ToontownGlobals
stubs — no Panda3D. Covers ambush pressure tip helpers, soft-lock prefer
pulse helpers, and AST locks that DistributedReclaimDirector + MeleeCombat
accept the formerly orphan messenger.

Run from repo root:
  python3 tests/test_reclaim_ambush_spawn_cue.py
  python3 -m unittest tests.test_reclaim_ambush_spawn_cue -v
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
TTC = 2000


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_reclaim():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = TTC
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

    rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
    rg_spec = importlib.util.spec_from_file_location(
        'toontown.reclaim.ReclaimGlobals', rg_path)
    rg = importlib.util.module_from_spec(rg_spec)
    assert rg_spec.loader is not None
    sys.modules['toontown.reclaim.ReclaimGlobals'] = rg
    rg_spec.loader.exec_module(rg)
    sys.modules['toontown.reclaim'].ReclaimGlobals = rg
    return rg


def _load_soft_target_helpers():
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


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    return set()


def _accept_events(tree: ast.AST, class_name: str) -> set[str]:
    """Collect string literals / Name attr patterns passed to self.accept."""
    events = set()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in ast.walk(node):
            if not isinstance(item, ast.Call):
                continue
            func = item.func
            if not (isinstance(func, ast.Attribute) and func.attr == 'accept'):
                continue
            if not item.args:
                continue
            arg0 = item.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                events.add(arg0.value)
            elif isinstance(arg0, ast.Str):  # py<3.8 compat
                events.add(arg0.s)
            elif isinstance(arg0, ast.Call):
                # ReclaimGlobals.ambushMsgName() / getattr(...) — capture
                # nested string constants when present.
                for sub in ast.walk(arg0):
                    if isinstance(sub, ast.Constant) and isinstance(
                            sub.value, str):
                        events.add(sub.value)
                    elif isinstance(sub, ast.Str):
                        events.add(sub.s)
            elif isinstance(arg0, ast.Name):
                events.add(arg0.id)
    return events


class ReclaimAmbushSpawnCueTests(unittest.TestCase):
    """Orphan reclaimAmbushSpawn → pressure tip + soft-lock prefer pulse."""

    @classmethod
    def setUpClass(cls):
        cls.rg = _load_panda_free_reclaim()
        cls.soft, cls.cfg = _load_soft_target_helpers()

    def test_ambush_pressure_tip_helpers(self):
        rg = self.rg
        self.assertTrue(rg.AMBUSH_PRESSURE_TIP_ENABLED)
        self.assertEqual(rg.ambushMsgName(), 'reclaimAmbushSpawn')
        tip = rg.ambushPressureTipText(afterWave=3, count=2, zoneId=LOOPY)
        self.assertIn('ambush', tip.lower())
        self.assertIn('soft-lock', tip.lower())
        self.assertIn('pack of 2', tip)
        plain = rg.ambushPressureTipText(afterWave=1, count=0)
        self.assertNotIn('pack of', plain)
        # Distinct from banner Oswald tip.
        banner = rg.ambushOswaldTip(3, zoneId=LOOPY)
        self.assertNotEqual(tip, banner)
        blob = tip.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, blob)

    def test_ambush_soft_lock_prefer_helpers(self):
        rg = self.rg
        soft = self.soft
        self.assertTrue(rg.AMBUSH_SOFT_LOCK_PREFER_ENABLED)
        self.assertGreater(rg.AMBUSH_SOFT_LOCK_PREFER_SEC, 0.0)
        self.assertTrue(rg.isAmbushSoftLockPreferName('Ambush Balloon Snare'))
        self.assertFalse(rg.isAmbushSoftLockPreferName('Balloon Snare'))
        self.assertFalse(rg.isAmbushSoftLockPreferName('Elite Ink Smudge'))
        self.assertTrue(rg.ambushSoftLockPreferActive(10.0, 5.0))
        self.assertFalse(rg.ambushSoftLockPreferActive(10.0, 10.0))
        self.assertFalse(
            rg.ambushSoftLockPreferActive(10.0, 5.0, enabled=False))
        # SoftTarget mirrors.
        self.assertTrue(soft.isAmbushPreferName('Ambush Ink Smudge'))
        self.assertFalse(soft.isAmbushPreferName('Ink Smudge'))
        self.assertTrue(soft.ambushPreferWindowActive(8.0, 3.0))
        self.assertFalse(soft.ambushPreferWindowActive(8.0, 9.0))
        self.assertFalse(
            soft.ambushPreferWindowActive(8.0, 3.0, enabled=False))

    def test_soft_target_pulse_expires_sticky(self):
        soft = self.soft
        finder = soft.SoftTargetFinder(avatar=object())
        finder._lockedKey = ('doId', 1)
        finder._lockedUntil = 99.0
        armed = finder.pulseAmbushPrefer(duration=3.5, now=10.0)
        self.assertTrue(armed)
        self.assertEqual(finder._lockedUntil, 0.0)
        self.assertAlmostEqual(finder._ambushPreferUntil, 13.5)
        self.assertTrue(finder.isAmbushPreferActive(now=12.0))
        self.assertFalse(finder.isAmbushPreferActive(now=14.0))
        finder.clear()
        self.assertEqual(finder._ambushPreferUntil, 0.0)

    def test_prefer_pulse_disabled_is_noop(self):
        soft = self.soft
        cfg = self.cfg
        prev = cfg.AMBUSH_SOFT_LOCK_PREFER_ENABLED
        cfg.AMBUSH_SOFT_LOCK_PREFER_ENABLED = False
        try:
            finder = soft.SoftTargetFinder(avatar=object())
            finder._lockedUntil = 42.0
            self.assertFalse(finder.pulseAmbushPrefer(duration=2.0, now=1.0))
            self.assertEqual(finder._lockedUntil, 42.0)
            self.assertEqual(finder._ambushPreferUntil, 0.0)
        finally:
            cfg.AMBUSH_SOFT_LOCK_PREFER_ENABLED = prev

    def test_pick_acquire_prefers_ambush_during_pulse(self):
        soft = self.soft
        # Ambush nearer-or-farther: priority tier wins over plain pack.
        rows = [
            (False, 2.0, 'smudge'),
            (True, 9.0, 'ambush'),
        ]
        self.assertEqual(soft.pickSoftLockAcquire(rows), 'ambush')

    def test_director_accepts_ambush_spawn_cue(self):
        rel = 'toontown/reclaim/DistributedReclaimDirector.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedReclaimDirector')
        self.assertIn('announceAmbushSpawn', methods)
        self.assertIn('__onAmbushSpawnCue', methods)
        self.assertIn('__showPressureTip', methods)
        src = _read(rel)
        self.assertIn('ambushMsgName()', src)
        self.assertIn('__onAmbushSpawnCue', src)
        self.assertIn('ambushPressureTipText', src)
        self.assertIn('warnPressure', src)
        self.assertIn('AMBUSH_PRESSURE_TIP_ENABLED', src)
        # Orphan send is now accepted (not send-only).
        self.assertIn("accept(\n            ReclaimGlobals.ambushMsgName()", src)
        src_l = src.lower()
        self.assertNotIn('keyblade', src_l)
        self.assertNotIn('kingdom hearts', src_l)

    def test_melee_accepts_ambush_soft_lock_prefer(self):
        rel = 'toontown/hackslash/MeleeCombat.py'
        methods = _class_method_names(
            _module_ast(rel), 'MeleeCombatController')
        self.assertIn('_onAmbushSpawnPrefer', methods)
        src = _read(rel)
        self.assertIn('_onAmbushSpawnPrefer', src)
        self.assertIn('pulseAmbushPrefer', src)
        self.assertIn('AMBUSH_SOFT_LOCK_PREFER_MSG', src)
        self.assertIn('reclaimAmbushSpawn', src)
        soft_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('def pulseAmbushPrefer', soft_src)
        self.assertIn('def isAmbushPreferName', soft_src)
        self.assertIn('def ambushPreferWindowActive', soft_src)
        self.assertIn('_ambushPreferUntil', soft_src)
        self.assertIn('isAmbushPreferActive', soft_src)
        cfg = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('AMBUSH_SOFT_LOCK_PREFER_ENABLED', cfg)
        self.assertIn('AMBUSH_SOFT_LOCK_PREFER_SEC', cfg)
        self.assertIn("AMBUSH_SOFT_LOCK_PREFER_MSG = 'reclaimAmbushSpawn'", cfg)

    def test_no_cream_or_kh_in_ambush_cue_block(self):
        rg_src = _read('toontown/reclaim/ReclaimGlobals.py')
        start = rg_src.index('AMBUSH_PRESSURE_TIP_ENABLED')
        end = rg_src.index('AMBUSH_MSG') + 40
        block = rg_src[start:end].lower()
        # Comment may mention "no cream deepen" — assert no cream *tunables*.
        self.assertNotIn('cream_wash', block)
        self.assertNotIn('sparkle', block)
        self.assertNotIn('keyblade', block)
        self.assertNotIn('kingdom hearts', block)


if __name__ == '__main__':
    unittest.main()
