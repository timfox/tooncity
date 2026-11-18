#!/usr/bin/env python3
"""Behavioral headless tests for Sludge Brute spit cream splash aftershock.

Imports CorruptionGlobals with a ToontownGlobals stub (no Panda3D). Asserts
BRUTE_SPIT_CREAM_SPLASH_* tunables and AST wiring on BruteSpitCreamSplashFx
+ DistributedCorruptToon (Brute-only play from spit land / clear paths).

Run from repo root:
  python3 tests/test_brute_spit_cream_splash.py
  python3 -m unittest tests.test_brute_spit_cream_splash -v
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


class BruteSpitCreamSplashTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_spit_cream_splash_tunables(self):
        self.assertTrue(self.cg.BRUTE_SPIT_CREAM_SPLASH_ENABLED)
        self.assertTrue(self.cg.BRUTE_SPIT_CREAM_AFTERSHOCK_ENABLED)
        self.assertTrue(self.cg.BRUTE_SPIT_CREAM_SPLASH_DRIP_ENABLED)
        self.assertGreaterEqual(
            self.cg.BRUTE_SPIT_CREAM_SPLASH_DELAY_SEC, 0.0)
        self.assertGreater(self.cg.BRUTE_SPIT_CREAM_SPLASH_LIFT, 0.0)
        look = self.cg.BRUTE_SPIT_CREAM_SPLASH_LOOK
        self.assertEqual(look.get('id'), 'brute-spit-cream-splash')
        # Beyond #264 spit-land deepen (was 7 flecks / 4 drips / 6 aftershock).
        self.assertGreaterEqual(int(look.get('fleckCount', 0)), 8)
        self.assertGreaterEqual(float(look.get('splatPeak', 0)), 2.0)
        self.assertGreaterEqual(float(look.get('splatHalf', 0)), 0.36)
        self.assertGreaterEqual(float(look.get('fleckLift', 0)), 0.6)
        self.assertTrue(look.get('dripEnabled'))
        self.assertGreaterEqual(int(look.get('dripCount', 0)), 5)
        self.assertGreaterEqual(float(look.get('dripFall', 0)), 1.2)
        look_id = str(look.get('id', '')).lower()
        self.assertNotIn('keyblade', look_id)
        self.assertNotIn('kingdom hearts', look_id)
        # Cream / pastel — not green spit blob colors.
        color = self.cg.BRUTE_SPIT_CREAM_SPLASH_COLOR
        self.assertGreaterEqual(float(color[0]), 0.9)
        self.assertGreaterEqual(float(color[1]), 0.9)
        self.assertGreaterEqual(float(color[2]), 0.55)
        drip = self.cg.BRUTE_SPIT_CREAM_SPLASH_DRIP_COLOR
        self.assertGreaterEqual(float(drip[0]), 0.9)
        self.assertGreaterEqual(float(drip[1]), 0.9)
        self.assertGreaterEqual(float(drip[2]), 0.55)
        self.assertGreater(
            self.cg.BRUTE_SPIT_CREAM_AFTERSHOCK_DELAY_SEC, 0.0)
        # Heavier spit residual beyond #264; distinct from Snare whip / Smudge.
        self.assertGreaterEqual(
            self.cg.BRUTE_SPIT_CREAM_AFTERSHOCK_COUNT, 7)
        self.assertGreaterEqual(
            self.cg.BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_COUNT, 4)
        self.assertGreaterEqual(
            self.cg.BRUTE_SPIT_CREAM_AFTERSHOCK_FALL, 0.75)
        self.assertGreaterEqual(
            self.cg.BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_HALF, 0.7)
        # Delay composes toward spit travel (impact timing).
        self.assertGreater(float(self.cg.BRUTE_SPIT_BLOB_TRAVEL), 0.0)
        self.assertGreaterEqual(float(look.get('delayScale', 0)), 0.5)
        # Distinct from Snare / Gunk cream splash ids.
        self.assertNotEqual(
            look.get('id'),
            getattr(self.cg, 'SNARE_STRING_COUNTER_CREAM_SPLASH_LOOK',
                    {}).get('id'))
        self.assertNotEqual(
            look.get('id'),
            getattr(self.cg, 'GAGSTER_PUDDLE_CREAM_SPLASH_LOOK', {}).get('id'))

    def test_cream_splash_fx_module_and_wiring(self):
        rel = 'toontown/corruption/BruteSpitCreamSplashFx.py'
        self.assertTrue((REPO_ROOT / rel).is_file())
        names = _class_and_func_names(_module_ast(rel))
        self.assertIn('BruteSpitCreamSplash', names)
        self.assertIn('bruteSpitCreamSplashLook', names)
        methods = _class_method_names(
            _module_ast(rel), 'BruteSpitCreamSplash')
        for name in (
                'play', 'clear', '_spawnSplat', '_spawnDripFilament',
                '_spawnFleck', '_buildAftershock'):
            self.assertIn(
                name, methods,
                msg='BruteSpitCreamSplash missing %s' % name)
        src = _read(rel)
        self.assertIn('BRUTE_SPIT_CREAM_SPLASH_LOOK', src)
        self.assertIn('_buildAftershock', src)
        self.assertIn('_spawnDripFilament', src)
        self.assertIn('BRUTE_SPIT_BLOB_TRAVEL', src)
        self.assertIn('Snare', src)  # docstring distinctness vs #269 / #245
        self.assertIn('Gunk', src)  # docstring distinctness vs #276 / #238
        self.assertIn('Smudge', src)  # docstring distinctness vs #283 / #259
        self.assertIn('#264', src)  # deepen floor past merged spit cream
        # CardMaker / interval names stay Toontown cream — no KH brand ids.
        self.assertNotIn("'keyblade", src.lower())
        self.assertNotIn('"keyblade', src.lower())
        self.assertNotIn('kingdom_hearts', src.lower())
        wire = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('BruteSpitCreamSplash', wire)
        self.assertIn('__playBruteSpitCreamSplash', wire)
        self.assertIn('__clearBruteSpitCreamSplash', wire)
        # Fire from spit land (after telegraph), not wind-up alone.
        spit_idx = wire.find('def __playSpitBlob')
        self.assertGreater(spit_idx, 0)
        spit_snip = wire[spit_idx:spit_idx + 2200]
        self.assertIn('__playBruteSpitCreamSplash(end)', spit_snip)
        self.assertGreater(wire.count('__clearBruteSpitCreamSplash'), 2)
        # Brute-only gate on the play helper.
        play_idx = wire.find('def __playBruteSpitCreamSplash')
        self.assertGreater(play_idx, 0)
        play_snip = wire[play_idx:play_idx + 700]
        self.assertIn('__isBruteSpit', play_snip)
        init_src = _read('toontown/corruption/__init__.py')
        self.assertIn('BruteSpitCreamSplashFx', init_src)
        reclaim = _read('toontown/corruption/RECLAIM.md')
        self.assertIn('BruteSpitCreamSplashFx', reclaim)
        self.assertIn('drip filament', reclaim.lower())


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        BruteSpitCreamSplashTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
