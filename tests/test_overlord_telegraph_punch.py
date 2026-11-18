#!/usr/bin/env python3
"""Behavioral headless tests for Ink Overlord telegraph punch polish.

Imports CorruptionGlobals with a ToontownGlobals stub (no Panda3D). Asserts
OVERLORD_TELEGRAPH_PUNCH_LOOK / ANIM defaults, phase timing vs combat delay,
and AST wiring on OverlordTelegraphPunchFx + DistributedCorruptToon.

Run from repo root:
  python3 tests/test_overlord_telegraph_punch.py
  python3 -m unittest tests.test_overlord_telegraph_punch -v
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


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_and_func_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in getattr(tree, 'body', []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    return set()


class OverlordTelegraphPunchTest(unittest.TestCase):
    """Danger-ring warn + phase timing + impact punch wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_punch_look_and_anim_defaults(self):
        look = self.cg.OVERLORD_TELEGRAPH_PUNCH_LOOK
        self.assertEqual(look.get('id'), 'overlord-telegraph-punch')
        self.assertTrue(self.cg.OVERLORD_TELEGRAPH_PUNCH_ENABLED)
        self.assertGreater(float(look.get('warnHalf', 0)), 1.0)
        self.assertGreater(float(look.get('warnHitRangeScale', 0)), 0.1)
        # P1 magenta (B high) vs P2 crimson (R high) warn colors.
        p1 = look.get('warnColorP1')
        p2 = look.get('warnColorP2')
        self.assertIsInstance(p1, tuple)
        self.assertIsInstance(p2, tuple)
        self.assertGreater(float(p1[2]), float(p1[1]))
        self.assertGreater(float(p2[0]), float(p2[2]))
        anim = self.cg.OVERLORD_TELEGRAPH_ANIM_DEFAULTS
        self.assertIn('p1', anim)
        self.assertIn('p2', anim)
        # P1 hold longer than P2 — fair rising-rain punish window.
        self.assertGreater(
            float(anim['p1']['telegraphHoldSec']),
            float(anim['p2']['telegraphHoldSec']))

    def test_phase_look_timing_tracks_combat_delay(self):
        """Stretch+hold should cover most of AI telegraphDelay before recover."""
        for phase in (1, 2):
            look = self.cg.FINALE_PHASE_LOOK[phase]
            combat = self.cg.overlordPhaseCombat(phase)
            delay = float(combat['telegraphDelay'])
            windup = (
                float(look['telegraphSquashSec'])
                + float(look['telegraphMidSec'])
                + float(look['telegraphStretchSec'])
                + float(look['telegraphHoldSec']))
            # Wind-up (through hold) lands at or just under AI delay so impact
            # usually cuts in while still stretched.
            self.assertLessEqual(windup, delay + 0.02)
            self.assertGreaterEqual(windup, delay * 0.85)
            self.assertIn('impactReboundScale', look)
            self.assertIn('impactSlamSec', look)

    def test_punch_fx_module_api(self):
        tree = _module_ast(
            'toontown/corruption/OverlordTelegraphPunchFx.py')
        names = _class_and_func_names(tree)
        for expected in (
                'overlordTelegraphPunchLook',
                'overlordTelegraphAnimSecs',
                'OverlordTelegraphPunch'):
            self.assertIn(expected, names, msg='missing %s' % expected)
        methods = _class_method_names(tree, 'OverlordTelegraphPunch')
        for expected in ('playWarn', 'playImpact', 'clear'):
            self.assertIn(expected, methods, msg='missing method %s' % expected)
        src = _read('toontown/corruption/OverlordTelegraphPunchFx.py')
        # Ban copy only — no KH identity / keyblade promotion in juice code.
        lower = src.lower()
        self.assertIn('no keyblades', lower)
        self.assertNotIn('kingdom hearts', lower)
        self.assertNotIn('sora', lower)
        self.assertNotIn('keyblade.com', lower)

    def test_distributed_wiring(self):
        src = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('OverlordTelegraphPunch', src)
        self.assertIn('overlordTelegraphAnimSecs', src)
        self.assertIn('__playOverlordTelegraphPunchWarn', src)
        self.assertIn('__playOverlordTelegraphPunchImpact', src)
        self.assertIn('__clearOverlordTelegraphPunch', src)
        tree = _module_ast('toontown/corruption/DistributedCorruptToon.py')
        methods = _class_method_names(tree, 'DistributedCorruptToon')
        for expected in (
                '__playOverlordTelegraphPunchWarn',
                '__playOverlordTelegraphPunchImpact',
                '__clearOverlordTelegraphPunch'):
            self.assertIn(expected, methods)

    def test_warn_half_tracks_hit_range_via_look_helper(self):
        """Import punch look helper (needs CorruptionGlobals already loaded)."""
        fx_path = (
            REPO_ROOT / 'toontown' / 'corruption' / 'OverlordTelegraphPunchFx.py')
        # Stub panda / interval imports so the module loads headless.
        panda = types.ModuleType('panda3d')
        core = types.ModuleType('panda3d.core')
        for name in (
                'CardMaker', 'Point3', 'TransparencyAttrib', 'Vec4', 'Vec3'):
            setattr(core, name, type(name, (), {'__init__': lambda *a, **k: None}))
        sys.modules['panda3d'] = panda
        sys.modules['panda3d.core'] = core
        interval = types.ModuleType('direct.interval.IntervalGlobal')
        for name in (
                'Func', 'LerpColorScaleInterval', 'LerpScaleInterval',
                'Parallel', 'Sequence', 'Wait'):
            setattr(interval, name, lambda *a, **k: None)
        sys.modules.setdefault('direct', types.ModuleType('direct'))
        sys.modules['direct.interval'] = types.ModuleType('direct.interval')
        sys.modules['direct.interval.IntervalGlobal'] = interval

        spec = importlib.util.spec_from_file_location(
            'toontown.corruption.OverlordTelegraphPunchFx', fx_path)
        fx = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(fx)

        p1 = fx.overlordTelegraphPunchLook(phase=1)
        p2 = fx.overlordTelegraphPunchLook(phase=2)
        self.assertGreater(float(p2['warnHalf']), float(p1['warnHalf']))
        combat1 = self.cg.overlordPhaseCombat(1)
        expected = float(combat1['attackHitRange']) * float(
            self.cg.OVERLORD_TELEGRAPH_PUNCH_LOOK['warnHitRangeScale'])
        self.assertGreaterEqual(float(p1['warnHalf']), expected * 0.99)

        anim1 = fx.overlordTelegraphAnimSecs(
            finaleLook=self.cg.FINALE_PHASE_LOOK[1], phase=1)
        anim2 = fx.overlordTelegraphAnimSecs(
            finaleLook=self.cg.FINALE_PHASE_LOOK[2], phase=2)
        self.assertGreater(float(anim1['holdSec']), float(anim2['holdSec']))


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    unittest.main()
