#!/usr/bin/env python3
"""Behavioral headless tests for further-deepened wave-clear cream sparkle.

Imports ReclaimGlobals with a ToontownGlobals stub (no Panda3D). Asserts
WAVE_CLEAR_CREAM_SPARKLE / AFTERSHOCK tunables past #229, rubber-hose
(non-KH) copy, and AST hooks on WaveClearCreamWashFx + shimmer hold wiring.
Distinct from secured-lock green sting (#243) and purity-complete meter hose
settle cream (#248).

Run from repo root:
  python3 tests/test_wave_clear_cream_sparkle.py
  python3 -m unittest tests.test_wave_clear_cream_sparkle -v
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


def _load_reclaim_globals():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.toonbase', 'toontown.reclaim'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = 2200
    tg.PunchlinePlace = 2300
    tg.SillyStreet = 2100
    tg.ToontownCentral = 2000
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
    rg_spec = importlib.util.spec_from_file_location(
        'toontown.reclaim.ReclaimGlobals', rg_path)
    rg = importlib.util.module_from_spec(rg_spec)
    assert rg_spec.loader is not None
    sys.modules['toontown.reclaim.ReclaimGlobals'] = rg
    rg_spec.loader.exec_module(rg)
    sys.modules['toontown.reclaim'].ReclaimGlobals = rg
    return rg


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


class WaveClearCreamSparkleTest(unittest.TestCase):
    """Pure-Python further-deepened wave-clear cream sparkle wiring."""

    @classmethod
    def setUpClass(cls):
        cls.rg = _load_reclaim_globals()

    def test_sparkle_tunables_deepened_past_229(self):
        rg = self.rg
        self.assertIs(rg.WAVE_CLEAR_CREAM_SPARKLE_ENABLED, True)
        self.assertIs(rg.WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_ENABLED, True)
        # Juicier than #229 deepen (9 / 0.36 / 1.22 / aftershock 4).
        self.assertGreaterEqual(rg.WAVE_CLEAR_CREAM_SPARKLE_COUNT, 10)
        self.assertGreaterEqual(float(rg.WAVE_CLEAR_CREAM_SPARKLE_RISE), 0.38)
        self.assertGreaterEqual(float(rg.WAVE_CLEAR_CREAM_SPARKLE_SEC), 0.38)
        self.assertGreater(float(rg.WAVE_CLEAR_CREAM_SPARKLE_POP), 1.22)
        self.assertGreaterEqual(rg.WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_COUNT, 5)
        self.assertGreaterEqual(
            float(rg.WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_SEC), 0.32)
        self.assertTrue(rg.WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_ENABLED)
        self.assertGreaterEqual(
            float(rg.WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_PEAK), 1.15)
        # Still quieter than full-purity StreetSparkle horizon payoff.
        self.assertLess(
            rg.WAVE_CLEAR_CREAM_SPARKLE_COUNT, rg.STREET_SPARKLE_COUNT)
        self.assertLess(
            float(rg.WAVE_CLEAR_CREAM_SPARKLE_RISE),
            float(rg.STREET_SPARKLE_RISE))

    def test_sunny_cream_not_secured_green_or_hose_settle(self):
        rg = self.rg
        color = rg.WAVE_CLEAR_CREAM_SPARKLE_COLOR
        secured = rg.SECURED_LOCK_SPARKLE_COLOR
        # Sunny cream: R >= G > B; secured lock is greener (G > R).
        self.assertGreaterEqual(color[0], color[1])
        self.assertGreater(color[1], color[2])
        self.assertGreater(secured[1], secured[0])
        # Mid-screen origin — not secured tip / street horizon.
        ox, oy, oz = rg.WAVE_CLEAR_CREAM_SPARKLE_ORIGIN
        self.assertAlmostEqual(oz, 0.08, places=2)
        self.assertNotEqual(
            tuple(rg.WAVE_CLEAR_CREAM_SPARKLE_ORIGIN),
            tuple(rg.SECURED_LOCK_SPARKLE_ORIGIN))
        self.assertNotEqual(
            tuple(rg.WAVE_CLEAR_CREAM_SPARKLE_ORIGIN),
            tuple(rg.STREET_SPARKLE_ORIGIN))
        # Halo stays sunny cream — not tip-near green lock halo.
        wave_halo = rg.WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_COLOR
        lock_halo = rg.SECURED_LOCK_SPARKLE_AFTERSHOCK_HALO_COLOR
        self.assertGreaterEqual(wave_halo[0], wave_halo[1])
        self.assertGreater(lock_halo[1], lock_halo[0])
        self.assertNotEqual(tuple(wave_halo), tuple(lock_halo))
        # Does not own purity-complete meter hose settle tunables.
        self.assertTrue(hasattr(rg, 'PURITY_COMPLETE_METER_SETTLE_ENABLED'))
        self.assertTrue(
            hasattr(rg, 'PURITY_COMPLETE_METER_SETTLE_CREAM_ENABLED'))
        wash_src = _read('toontown/reclaim/WaveClearCreamWashFx.py')
        self.assertNotIn('PURITY_COMPLETE_METER_SETTLE', wash_src)
        self.assertNotIn('SECURED_LOCK_SPARKLE', wash_src)
        self.assertNotIn('settleComplete', wash_src)
        self.assertNotIn('confirmSecured', wash_src)

    def test_wash_fx_owns_deepened_sparkle_and_aftershock(self):
        tree = _module_ast('toontown/reclaim/WaveClearCreamWashFx.py')
        methods = _class_method_names(tree, 'WaveClearCreamWashPulse')
        for name in (
                'play',
                '_buildSparkle',
                '_spawnSparkleFlecks',
                '_buildSparkleAftershock',
                '_spawnSparkleAftershockFleck',
                '_spawnSparkleAftershockHalo',
                'clear'):
            self.assertIn(
                name, methods,
                msg='WaveClearCreamWashPulse missing %s' % name)
        src = _read('toontown/reclaim/WaveClearCreamWashFx.py')
        self.assertIn('WAVE_CLEAR_CREAM_SPARKLE_POP', src)
        self.assertIn('WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK', src)
        self.assertIn('reclaim-wave-clear-cream-sparkle', src)
        self.assertIn('#229', src)
        lower = src.lower()
        self.assertTrue(
            'no keyblade' in lower or 'no kh' in lower,
            msg='WaveClearCreamWashFx must keep KH/keyblade ban copy')
        for banned in ('kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, lower)

    def test_shimmer_hold_covers_sparkle_aftershock(self):
        src = _read('toontown/reclaim/WaveClearCreamShimmerFx.py')
        self.assertIn('WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK', src)
        self.assertIn('WaveClearCreamWashPulse', src)
        self.assertIn('#229', src)
        lower = src.lower()
        self.assertTrue(
            'no keyblade' in lower or 'no kh' in lower,
            msg='WaveClearCreamShimmerFx must keep KH/keyblade ban copy')
        for banned in ('kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, lower)

    def test_globals_comment_kh_free_and_distinct(self):
        rg_src = _read('toontown/reclaim/ReclaimGlobals.py')
        # Comment near sparkle block should ban KH framing + cite distinct cues.
        idx = rg_src.find('WAVE_CLEAR_CREAM_SPARKLE_ENABLED')
        self.assertGreater(idx, 0)
        snip = rg_src[max(0, idx - 700):idx + 200].lower()
        self.assertIn('no kh', snip)
        self.assertIn('#229', snip)
        self.assertTrue(
            '#243' in snip or 'lock' in snip,
            msg='sparkle comment should stay distinct from lock celebration')
        self.assertTrue(
            '#248' in snip or 'hose' in snip,
            msg='sparkle comment should stay distinct from purity hose deepen')
        for banned in ('kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, snip)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        WaveClearCreamSparkleTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
