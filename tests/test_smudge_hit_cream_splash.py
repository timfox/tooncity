#!/usr/bin/env python3
"""Behavioral headless tests for Smudge hit cream splash aftershock.

Imports CorruptionGlobals with a ToontownGlobals stub (no Panda3D). Asserts
SMUDGE_HIT_CREAM_SPLASH_* / SMUDGE_HIT_CREAM_AFTERSHOCK_* tunables and AST
wiring on SmudgeHitCreamSplashFx + DistributedCorruptToon (Smudge-only play
from hit path / clear paths).

Run from repo root:
  python3 tests/test_smudge_hit_cream_splash.py
  python3 -m unittest tests.test_smudge_hit_cream_splash -v
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


class SmudgeHitCreamSplashTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_hit_cream_splash_tunables(self):
        self.assertTrue(self.cg.SMUDGE_HIT_CREAM_SPLASH_ENABLED)
        self.assertTrue(self.cg.SMUDGE_HIT_CREAM_AFTERSHOCK_ENABLED)
        self.assertTrue(self.cg.SMUDGE_HIT_CREAM_SPLASH_SMEAR_ENABLED)
        self.assertGreaterEqual(
            self.cg.SMUDGE_HIT_CREAM_SPLASH_DELAY_SEC, 0.0)
        look = self.cg.SMUDGE_HIT_CREAM_SPLASH_LOOK
        self.assertEqual(look.get('id'), 'smudge-hit-cream-splash')
        # Deepened mid-body splash vs #231 baseline (4 flecks / 4 aftershock).
        self.assertGreaterEqual(int(look.get('fleckCount', 0)), 6)
        self.assertGreaterEqual(float(look.get('splatPeak', 0)), 1.65)
        self.assertGreaterEqual(float(look.get('fleckLift', 0)), 0.45)
        self.assertTrue(look.get('smearEnabled'))
        self.assertGreaterEqual(int(look.get('smearCount', 0)), 3)
        self.assertGreater(float(look.get('smearSpread', 0)), 0.0)
        look_id = str(look.get('id', '')).lower()
        self.assertNotIn('keyblade', look_id)
        self.assertNotIn('kingdom hearts', look_id)
        # Cream / pastel — not purple ink splash colors.
        color = self.cg.SMUDGE_HIT_CREAM_SPLASH_COLOR
        self.assertGreaterEqual(float(color[0]), 0.9)
        self.assertGreaterEqual(float(color[1]), 0.9)
        self.assertGreaterEqual(float(color[2]), 0.55)
        smear = self.cg.SMUDGE_HIT_CREAM_SPLASH_SMEAR_COLOR
        self.assertGreaterEqual(float(smear[0]), 0.9)
        self.assertGreaterEqual(float(smear[1]), 0.9)
        self.assertGreaterEqual(float(smear[2]), 0.55)
        self.assertGreater(
            self.cg.SMUDGE_HIT_CREAM_AFTERSHOCK_DELAY_SEC, 0.0)
        # Deepened pack residual — juicier than #231; distinct from Snare whip.
        self.assertGreaterEqual(
            self.cg.SMUDGE_HIT_CREAM_AFTERSHOCK_COUNT, 5)
        self.assertGreaterEqual(
            self.cg.SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_COUNT, 2)
        self.assertGreaterEqual(
            self.cg.SMUDGE_HIT_CREAM_AFTERSHOCK_DRIFT, 0.7)
        self.assertGreaterEqual(
            self.cg.SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_HALF, 0.5)
        self.assertGreaterEqual(float(look.get('delayScale', 0)), 0.2)
        # Compose from purple hit splash timing.
        purple = self.cg.SMUDGE_INK_SPLASH_LOOK['hit']
        self.assertGreater(float(purple.get('splatSec', 0)), 0.0)
        # Distinct from Snare / Brute / Gunk cream splash ids.
        self.assertNotEqual(
            look.get('id'),
            getattr(self.cg, 'SNARE_STRING_COUNTER_CREAM_SPLASH_LOOK',
                    {}).get('id'))
        self.assertNotEqual(
            look.get('id'),
            getattr(self.cg, 'BRUTE_SPIT_CREAM_SPLASH_LOOK', {}).get('id'))
        self.assertNotEqual(
            look.get('id'),
            getattr(self.cg, 'GAGSTER_PUDDLE_CREAM_SPLASH_LOOK', {}).get('id'))

    def test_cream_splash_fx_module_and_wiring(self):
        rel = 'toontown/corruption/SmudgeHitCreamSplashFx.py'
        self.assertTrue((REPO_ROOT / rel).is_file())
        names = _class_and_func_names(_module_ast(rel))
        self.assertIn('SmudgeHitCreamSplash', names)
        self.assertIn('smudgeHitCreamSplashLook', names)
        methods = _class_method_names(
            _module_ast(rel), 'SmudgeHitCreamSplash')
        for name in (
                'play', 'clear', '_spawnSplat', '_spawnHoseSmear',
                '_spawnFleck', '_buildAftershock'):
            self.assertIn(
                name, methods,
                msg='SmudgeHitCreamSplash missing %s' % name)
        src = _read(rel)
        self.assertIn('SMUDGE_HIT_CREAM_SPLASH_LOOK', src)
        self.assertIn('_buildAftershock', src)
        self.assertIn('_spawnHoseSmear', src)
        self.assertIn('smudgeInkSplashLook', src)
        self.assertIn('Snare', src)  # docstring distinctness vs #245
        self.assertIn('Brute', src)  # docstring distinctness vs #249
        self.assertIn('Gunk', src)  # docstring distinctness vs #238
        # CardMaker / interval names stay Toontown cream — no KH brand ids.
        self.assertNotIn("'keyblade", src.lower())
        self.assertNotIn('"keyblade', src.lower())
        self.assertNotIn('kingdom_hearts', src.lower())
        wire = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('SmudgeHitCreamSplash', wire)
        self.assertIn('__playSmudgeHitCreamSplash', wire)
        self.assertIn('__clearSmudgeHitCreamSplash', wire)
        # Fire from Smudge hit path beside purple splash.
        hit_idx = wire.find("ARCHETYPE_INK:")
        self.assertGreater(hit_idx, 0)
        # Prefer the hit-reaction block that plays purple splash.
        play_snip_start = wire.find("self.__playSmudgeInkSplash(kind='hit')")
        self.assertGreater(play_snip_start, 0)
        play_snip = wire[play_snip_start:play_snip_start + 400]
        self.assertIn('__playSmudgeHitCreamSplash()', play_snip)
        self.assertGreater(wire.count('__clearSmudgeHitCreamSplash'), 2)
        # Smudge-only gate on the play helper (skip Overlord).
        play_idx = wire.find('def __playSmudgeHitCreamSplash')
        self.assertGreater(play_idx, 0)
        helper_snip = wire[play_idx:play_idx + 700]
        self.assertIn('ARCHETYPE_INK', helper_snip)
        self.assertIn('__isInkOverlord', helper_snip)
        init_src = _read('toontown/corruption/__init__.py')
        self.assertIn('SmudgeHitCreamSplashFx', init_src)
        self.assertIn('cream hose smears', init_src)
        reclaim = _read('toontown/corruption/RECLAIM.md')
        self.assertIn('SmudgeHitCreamSplashFx', reclaim)
        self.assertIn('radial cream hose', reclaim)
        # No KH / keyblade branding in look id (ban disclaimer may mention them).
        splash_id = str(
            self.cg.SMUDGE_HIT_CREAM_SPLASH_LOOK.get('id', '')).lower()
        self.assertNotIn('keyblade', splash_id)
        self.assertNotIn('kingdom hearts', splash_id)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SmudgeHitCreamSplashTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
