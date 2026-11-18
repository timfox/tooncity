#!/usr/bin/env python3
"""Headless/AST tests: Overlord telegraph carries move id (rain/slam/ink_surge).

TC-351 / gap scan #5 — AI already picked distinct moves, but
``announceAttackTelegraph`` took no arg and client always played rain AV.
Move id must pass DC → AI sendUpdate → client branch so players can read
which pressure is coming. No cream deepen / no KH branding.

Run from repo root:
  python3 tests/test_overlord_telegraph_move_id.py
  python3 -m unittest tests.test_overlord_telegraph_move_id -v
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


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    return set()


def _method_args(tree: ast.AST, class_name: str, method_name: str) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and item.name == method_name):
                    return [a.arg for a in item.args.args]
    return []


class OverlordTelegraphMoveIdTest(unittest.TestCase):
    """Move-id helpers / DC / AI / client wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_move_helpers_and_hud(self):
        self.assertEqual(
            set(self.cg.OVERLORD_TELEGRAPH_MOVES),
            {'rain', 'slam', 'ink_surge'})
        self.assertEqual(
            self.cg.normalizeOverlordTelegraphMove('RAIN'), 'rain')
        self.assertEqual(
            self.cg.normalizeOverlordTelegraphMove('ink_surge'), 'ink_surge')
        self.assertEqual(
            self.cg.normalizeOverlordTelegraphMove('spit'), '')
        self.assertEqual(
            self.cg.normalizeOverlordTelegraphMove(''), '')
        self.assertTrue(self.cg.overlordTelegraphShowsInkRain('rain'))
        self.assertFalse(self.cg.overlordTelegraphShowsInkRain('slam'))
        self.assertFalse(self.cg.overlordTelegraphShowsInkRain('ink_surge'))
        for move in ('rain', 'slam', 'ink_surge'):
            self.assertTrue(
                self.cg.overlordTelegraphShowsPunchWarn(move),
                msg='%s should show punch warn' % move)
        self.assertFalse(self.cg.overlordTelegraphShowsPunchWarn('spit'))

        p2 = self.cg.overlordPhaseCombat(2)
        rain_r = self.cg.overlordTelegraphMoveHitRange('rain', 2, p2)
        slam_r = self.cg.overlordTelegraphMoveHitRange('slam', 2, p2)
        surge_r = self.cg.overlordTelegraphMoveHitRange('ink_surge', 2, p2)
        self.assertAlmostEqual(rain_r, float(p2['attackHitRange']))
        self.assertAlmostEqual(slam_r, float(p2['slamHitRange']))
        self.assertAlmostEqual(surge_r, float(p2['surgeHitRange']))
        self.assertLess(slam_r, surge_r)
        self.assertLess(surge_r, rain_r)

        look = self.cg.FINALE_PHASE_LOOK[1]
        cue = self.cg.overlordTelegraphMoveHudCue('slam', 1, look)
        self.assertIn('SLAM', cue)
        self.assertIn(str(look.get('hudCue', '')), cue)
        surge_cue = self.cg.overlordTelegraphMoveHudCue('ink_surge', 2, None)
        self.assertIn('SURGE', surge_cue)
        self.assertIn('P2', surge_cue)

        blob = ' '.join([
            'OVERLORD_TELEGRAPH_MOVES',
            'normalizeOverlordTelegraphMove',
            'overlordTelegraphMoveHitRange',
            'rain', 'slam', 'ink_surge',
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, blob)

    def test_dc_and_ai_pass_move_string(self):
        dc = _read('etc/toon.dc')
        self.assertIn('announceAttackTelegraph(string) broadcast;', dc)
        self.assertNotIn('announceAttackTelegraph() broadcast;', dc)
        ai = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn(
            "sendUpdate('announceAttackTelegraph', [str(move or '')])", ai)
        self.assertNotIn(
            "sendUpdate('announceAttackTelegraph', [])", ai)

    def test_client_branches_rain_slam_surge(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        tree = _module_ast(rel)
        args = _method_args(tree, 'DistributedCorruptToon', 'announceAttackTelegraph')
        self.assertIn('moveId', args)
        methods = _class_method_names(tree, 'DistributedCorruptToon')
        for required in (
                '__playOverlordTelegraphCrown',
                '__playOverlordPhaseInkRain',
                '__playOverlordTelegraphPunchWarn',
                '__clearOverlordPhaseInkRain'):
            self.assertIn(required, methods)
        src = _read(rel)
        telegraph = src[src.find('def announceAttackTelegraph'):]
        telegraph_end = telegraph.find('\n    def ', 1)
        body = telegraph if telegraph_end < 0 else telegraph[:telegraph_end]
        self.assertIn('normalizeOverlordTelegraphMove', body)
        self.assertIn('overlordTelegraphShowsInkRain', body)
        self.assertIn('overlordTelegraphShowsPunchWarn', body)
        self.assertIn('overlordTelegraphMoveHudCue', body)
        self.assertIn('moveId=overlordMove', body)
        # Rain shower gated; slam/surge clear rain when not raining.
        self.assertIn('__playOverlordPhaseInkRain', body)
        self.assertIn('__clearOverlordPhaseInkRain', body)
        self.assertIn('_telegraphMove', body)
        lower = body.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, lower)

    def test_punch_look_scales_by_move(self):
        fx_path = (
            REPO_ROOT / 'toontown' / 'corruption' / 'OverlordTelegraphPunchFx.py')
        panda = types.ModuleType('panda3d')
        core = types.ModuleType('panda3d.core')
        for name in (
                'CardMaker', 'Point3', 'TransparencyAttrib', 'Vec4', 'Vec3'):
            setattr(core, name, type(name, (), {'__init__': lambda *a, **k: None}))
        sys.modules['panda3d'] = panda
        sys.modules['panda3d.core'] = core
        interval = types.ModuleType('direct.interval.IntervalGlobal')
        for name in (
                'Func', 'LerpColorScaleInterval', 'LerpPosInterval',
                'LerpScaleInterval', 'Parallel', 'Sequence', 'Wait'):
            setattr(interval, name, lambda *a, **k: None)
        sys.modules.setdefault('direct', types.ModuleType('direct'))
        sys.modules['direct.interval'] = types.ModuleType('direct.interval')
        sys.modules['direct.interval.IntervalGlobal'] = interval

        spec = importlib.util.spec_from_file_location(
            'toontown.corruption.OverlordTelegraphPunchFx', fx_path)
        fx = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(fx)

        rain = fx.overlordTelegraphPunchLook(phase=2, moveId='rain')
        slam = fx.overlordTelegraphPunchLook(phase=2, moveId='slam')
        surge = fx.overlordTelegraphPunchLook(phase=2, moveId='ink_surge')
        self.assertEqual(rain.get('telegraphMove'), 'rain')
        self.assertEqual(slam.get('telegraphMove'), 'slam')
        self.assertEqual(surge.get('telegraphMove'), 'ink_surge')
        self.assertLess(float(slam['warnHalf']), float(surge['warnHalf']))
        self.assertLess(float(surge['warnHalf']), float(rain['warnHalf']))
        # Legacy call (no moveId) keeps rain footprint.
        legacy = fx.overlordTelegraphPunchLook(phase=2)
        self.assertAlmostEqual(
            float(legacy['warnHalf']), float(rain['warnHalf']), places=5)

        fx_src = _read('toontown/corruption/OverlordTelegraphPunchFx.py')
        self.assertIn('moveId', fx_src)
        self.assertIn('overlordTelegraphMoveHitRange', fx_src)

    def test_docs_mention_move_id_telegraph(self):
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('announceattacktelegraph(string)', reclaim)
        self.assertIn('move-id telegraph', reclaim)
        self.assertIn('ink_surge', reclaim)
        init_src = _read('toontown/corruption/__init__.py').lower()
        self.assertIn('rain / slam / ink_surge', init_src)
        # Ban KH identity / promotion — "no keyblades" disclaimer is OK.
        self.assertIn('no keyblades', reclaim)
        for banned in ('kingdom hearts', 'sora', 'heartless', 'keyblade.com'):
            self.assertNotIn(banned, reclaim)
            self.assertNotIn(banned, init_src)

    def test_prior_overlord_kits_not_regressed(self):
        self.assertEqual(self.cg.overlordPickRisingMove(0.0), 'slam')
        p2 = self.cg.overlordPhaseCombat(2)
        slam = self.cg.overlordSlamMeleeRange(p2)
        surge = self.cg.overlordSurgeMaxRange(p2)
        self.assertEqual(self.cg.overlordPickEnrageMove(0.0, p2), 'slam')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(slam + 0.05, p2), 'ink_surge')
        self.assertEqual(
            self.cg.overlordPickEnrageMove(surge + 0.05, p2), 'rain')
        self.assertTrue(self.cg.OVERLORD_P1_SLAM_ENABLED)
        self.assertTrue(self.cg.OVERLORD_INK_SURGE_ENABLED)
        self.assertTrue(self.cg.OVERLORD_TELEGRAPH_PUNCH_ENABLED)


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    unittest.main()
