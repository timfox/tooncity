#!/usr/bin/env python3
"""Behavioral headless tests for TTC birds-return cream wash helpers.

Loads pure helpers from BirdsReturnCreamWashFx via AST extraction (no
Panda3D). Covers polluted→pure flip gate + cream deepen past #285
(juicier veil + denser rising chirp aftershock) so clean-neighborhood
birds return (#55) reads juicier on the hub — distinct from crumb pip
(#241/#298) / fog rim (#236/#295) / tunnel pulse (#290) / original
veil-only wash (#226) / #246/#262/#274/#285.

Run from repo root:
  python3 tests/test_birds_return_cream_wash.py
  python3 -m unittest tests.test_birds_return_cream_wash -v
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FX_REL = 'toontown/safezone/BirdsReturnCreamWashFx.py'
BREADCRUMB_REL = 'toontown/safezone/CorruptStreetBreadcrumb.py'


def _extract_pure_helpers():
    """Compile pure helpers without importing panda-heavy module."""
    path = REPO_ROOT / FX_REL
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src, filename=FX_REL)
    const_names = {
        'BIRDS_RETURN_CREAM_WASH_ENABLED',
        'BIRDS_RETURN_CREAM_WASH_DELAY_SEC',
        'BIRDS_RETURN_CREAM_WASH_PEAK',
        'BIRDS_RETURN_CREAM_WASH_MID',
        'BIRDS_RETURN_CREAM_WASH_IN_SEC',
        'BIRDS_RETURN_CREAM_WASH_PULSE_SEC',
        'BIRDS_RETURN_CREAM_WASH_HOLD_SEC',
        'BIRDS_RETURN_CREAM_WASH_OUT_SEC',
        'BIRDS_RETURN_CREAM_WASH_BIN',
        'BIRDS_RETURN_CREAM_WASH_COLOR',
        'BIRDS_RETURN_CREAM_WASH_DEBOUNCE_SEC',
        'BIRDS_RETURN_CREAM_WASH_AUDIO_THRESHOLD',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_ENABLED',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_COUNT',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SEC',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SIZE',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_RISE',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SPREAD',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_ORIGIN',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_COLOR',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_END_COLOR',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_BIN',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_ENABLED',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_HALF',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_START',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_PEAK',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_SEC',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA',
        'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
    }
    keep = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in const_names:
                    keep.append(node)
                    break
        elif isinstance(node, ast.FunctionDef) and node.name in (
                'birdsReturnCreamWashParams',
                'shouldPlayBirdsReturnCreamWash'):
            keep.append(node)
    if not any(
            isinstance(n, ast.FunctionDef)
            and n.name == 'birdsReturnCreamWashParams'
            for n in keep):
        raise AssertionError(
            'birdsReturnCreamWashParams not found in %s' % FX_REL)
    if not any(
            isinstance(n, ast.FunctionDef)
            and n.name == 'shouldPlayBirdsReturnCreamWash'
            for n in keep):
        raise AssertionError(
            'shouldPlayBirdsReturnCreamWash not found in %s' % FX_REL)
    mod = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(mod)
    ns = {}
    exec(compile(mod, FX_REL, 'exec'), ns)  # noqa: S102 — test harness
    return (
        ns['birdsReturnCreamWashParams'],
        ns['shouldPlayBirdsReturnCreamWash'],
    )


class BirdsReturnCreamWashTest(unittest.TestCase):
    """Pure helper + AST wiring for deepened TTC birds-return cream wash."""

    @classmethod
    def setUpClass(cls):
        params, should = _extract_pure_helpers()
        cls._params = staticmethod(params)
        cls._should = staticmethod(should)
        cls.fx_src = (REPO_ROOT / FX_REL).read_text(encoding='utf-8')
        cls.fx_tree = ast.parse(cls.fx_src, filename=FX_REL)
        cls.crumb_src = (
            REPO_ROOT / BREADCRUMB_REL).read_text(encoding='utf-8')

    def test_params_soft_explore_wash(self):
        params = self._params()
        self.assertTrue(params['enabled'])
        self.assertGreater(params['peak'], 0.0)
        self.assertLess(params['peak'], 0.24)
        self.assertGreater(params['mid'], 0.0)
        self.assertLess(params['mid'], params['peak'])
        # Cream deepen past #285: juicier than #226/#246/#262/#274/#285 (0.175/0.108).
        self.assertGreaterEqual(params['peak'], 0.185)
        self.assertGreaterEqual(params['mid'], 0.115)
        self.assertGreaterEqual(params['holdSec'], 0.26)
        self.assertGreaterEqual(params['pulseSec'], 0.19)
        self.assertGreaterEqual(params['outSec'], 0.58)
        self.assertGreaterEqual(params['inSec'], 0.105)
        # Land during birds fade-in (~0.55s), not before chirps start.
        self.assertGreaterEqual(params['delaySec'], 0.25)
        self.assertLessEqual(params['delaySec'], 0.65)
        self.assertGreater(params['inSec'], 0.0)
        self.assertGreater(params['outSec'], params['inSec'])
        self.assertGreaterEqual(params['debounceSec'], 1.5)
        self.assertLessEqual(params['debounceSec'], 3.5)
        self.assertAlmostEqual(
            params['audioThreshold'], 0.05, places=2)
        color = params['color']
        self.assertEqual(len(color), 3)
        # Cream / pastel — high R/G, warm B (not ink purple).
        self.assertGreaterEqual(color[0], 0.9)
        self.assertGreaterEqual(color[1], 0.9)
        self.assertGreaterEqual(color[2], 0.7)
        self.assertGreater(color[2], 0.5)

    def test_aftershock_rising_chirp_deepen(self):
        params = self._params()
        self.assertTrue(params['aftershockEnabled'])
        self.assertGreaterEqual(params['aftershockDelaySec'], 0.06)
        self.assertLessEqual(params['aftershockDelaySec'], 0.28)
        # Denser chirp residual than #285 (count 8 / rise 0.48 / halo 1.32).
        self.assertGreaterEqual(params['aftershockCount'], 9)
        self.assertLessEqual(params['aftershockCount'], 11)
        self.assertGreaterEqual(params['aftershockRise'], 0.50)
        self.assertGreaterEqual(params['aftershockSpread'], 0.72)
        self.assertGreaterEqual(params['aftershockSec'], 0.48)
        # Skyward halo peak past #285; distinct from crumb pip 1.48 / fog rim 1.22.
        self.assertGreaterEqual(params['aftershockHaloPeak'], 1.34)
        self.assertLess(params['aftershockHaloPeak'], 1.45)
        self.assertNotAlmostEqual(
            params['aftershockHaloPeak'], 1.48, places=2)
        self.assertNotAlmostEqual(
            params['aftershockHaloPeak'], 1.22, places=2)
        self.assertNotAlmostEqual(
            params['aftershockHaloPeak'], 1.26, places=2)
        self.assertNotAlmostEqual(
            params['aftershockHaloPeak'], 1.32, places=2)
        self.assertGreaterEqual(params['aftershockHaloPeakAlpha'], 0.175)
        self.assertLess(params['aftershockHaloPeakAlpha'], 0.26)
        self.assertGreaterEqual(params['aftershockHaloSec'], 0.36)
        # Rising chirp residual — not combat settle fall grammar.
        self.assertIn('AFTERSHOCK_RISE', self.fx_src)
        self.assertIn('_spawnChirpFleck', self.fx_src)
        self.assertIn('safezone-birds-return-cream-wash-chirp', self.fx_src)
        self.assertIn('safezone-birds-return-cream-wash-sky-halo', self.fx_src)
        self.assertIn('past #285', self.fx_src)
        self.assertNotIn('AFTERSHOCK_FALL', self.fx_src)

    def test_should_play_on_polluted_to_pure_flip(self):
        should = self._should
        self.assertTrue(should(0.55, 0.0))
        self.assertTrue(should(0.2, 0.05))
        self.assertTrue(should(0.06, 0.0, threshold=0.05))
        # Stay polluted / already pure / bad values → no wash.
        self.assertFalse(should(0.55, 0.40))
        self.assertFalse(should(0.0, 0.0))
        self.assertFalse(should(0.02, 0.0))  # already under threshold
        self.assertFalse(should('nope', 0.0))
        self.assertFalse(should(0.5, 'nope'))

    def test_module_exports_and_no_kh(self):
        names = {
            node.name for node in self.fx_tree.body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
        for expected in (
                'birdsReturnCreamWashParams',
                'shouldPlayBirdsReturnCreamWash',
                'BirdsReturnCreamWashPulse',
                'playBirdsReturnCreamWash',
                'clearBirdsReturnCreamWash'):
            self.assertIn(expected, names, msg='missing %s' % expected)
        for needle in (
                'CardMaker',
                'LerpColorScaleInterval',
                'Parallel',
                'safezone-birds-return-cream-wash',
                'BIRDS_RETURN_CREAM_WASH_PEAK',
                'BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_ENABLED',
                '_buildAftershock',
                '_spawnChirpFleck',
                '_spawnAftershockHalo'):
            self.assertIn(needle, self.fx_src, msg='missing %s' % needle)
        src_l = self.fx_src.lower()
        self.assertNotIn('keyblade', src_l)
        self.assertNotIn('kingdom hearts', src_l)

    def test_breadcrumb_wires_birds_return_wash(self):
        for needle in (
                'BirdsReturnCreamWashFx',
                'playBirdsReturnCreamWash',
                'clearBirdsReturnCreamWash',
                'shouldPlayBirdsReturnCreamWash',
                '_cueBirdsReturnCreamWash',
                '_clearBirdsReturnCreamWash'):
            self.assertIn(
                needle, self.crumb_src,
                msg='breadcrumb missing wash wire %s' % needle)
        crumb_l = self.crumb_src.lower()
        self.assertNotIn('keyblade', crumb_l)
        self.assertNotIn('kingdom hearts', crumb_l)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        BirdsReturnCreamWashTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
