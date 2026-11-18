#!/usr/bin/env python3
"""Behavioral headless tests for TTC polluted-tunnel placemarker helpers.

Loads pure helpers from CorruptStreetBreadcrumb via AST extraction (no
Panda3D). Covers streetNeedsBreadcrumb pollution/seed rules used by hub
discoverability (#192), placemarker notice-pulse timing (#211), the
distinct tunnel-mouth crumb-trail pulse (#216), and playground pollution
fog edge breath.

Run from repo root:
  python3 tests/test_corrupt_street_breadcrumb.py
  python3 -m unittest tests.test_corrupt_street_breadcrumb -v
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BREADCRUMB_REL = 'toontown/safezone/CorruptStreetBreadcrumb.py'


def _extract_pure_helpers():
    """Compile pure helpers without importing panda-heavy module."""
    path = REPO_ROOT / BREADCRUMB_REL
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src, filename=BREADCRUMB_REL)
    # Pulse helpers close over module constants — bind them.
    const_names = {
        '_PULSE_PEAK', '_PULSE_HALF_SEC', '_PULSE_BEATS', '_PULSE_GAP_SEC',
        '_MARKER_SCALE',
        '_CRUMB_PULSE_PEAK', '_CRUMB_PULSE_HALF_SEC', '_CRUMB_PULSE_GAP_SEC',
        '_CRUMB_STAGGER_SEC', '_CRUMB_COUNT', '_CRUMB_SCALE',
        '_FOG_PULSE_HALF_SEC', '_FOG_PULSE_GAP_SEC', '_FOG_REST', '_FOG_PEAK',
        '_FOG_BILLOW', '_FOG_SCALE',
    }
    keep = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in const_names:
                    keep.append(node)
                    break
        elif isinstance(node, ast.FunctionDef) and node.name in (
                'streetNeedsBreadcrumb',
                'placemarkerPulseParams',
                'streetBreadcrumbPulseParams',
                'playgroundFogEdgePulseParams'):
            keep.append(node)
    if not any(
            isinstance(n, ast.FunctionDef) and n.name == 'streetNeedsBreadcrumb'
            for n in keep):
        raise AssertionError('streetNeedsBreadcrumb not found in %s' % BREADCRUMB_REL)
    if not any(
            isinstance(n, ast.FunctionDef) and n.name == 'placemarkerPulseParams'
            for n in keep):
        raise AssertionError('placemarkerPulseParams not found in %s' % BREADCRUMB_REL)
    if not any(
            isinstance(n, ast.FunctionDef)
            and n.name == 'streetBreadcrumbPulseParams'
            for n in keep):
        raise AssertionError(
            'streetBreadcrumbPulseParams not found in %s' % BREADCRUMB_REL)
    if not any(
            isinstance(n, ast.FunctionDef)
            and n.name == 'playgroundFogEdgePulseParams'
            for n in keep):
        raise AssertionError(
            'playgroundFogEdgePulseParams not found in %s' % BREADCRUMB_REL)
    mod = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(mod)
    ns = {
        # Vec4-like stand-in so _FOG_REST/_FOG_PEAK assignments work headless.
        'Vec4': lambda *args: tuple(args),
    }
    exec(compile(mod, BREADCRUMB_REL, 'exec'), ns)  # noqa: S102 — test harness
    return (
        ns['streetNeedsBreadcrumb'],
        ns['placemarkerPulseParams'],
        ns['streetBreadcrumbPulseParams'],
        ns['playgroundFogEdgePulseParams'],
    )


class CorruptStreetBreadcrumbTest(unittest.TestCase):
    """Pure helper + AST wiring for hub polluted-tunnel placemarkers."""

    @classmethod
    def setUpClass(cls):
        # Store on the class dict under a private name so Python does not
        # bind the helper as an instance method (which would shift args).
        needs, pulse, crumb_pulse, fog_pulse = _extract_pure_helpers()
        cls._needs = staticmethod(needs)
        cls._pulse = staticmethod(pulse)
        cls._crumb_pulse = staticmethod(crumb_pulse)
        cls._fog_pulse = staticmethod(fog_pulse)
        cls.src = (REPO_ROOT / BREADCRUMB_REL).read_text(encoding='utf-8')
        cls.tree = ast.parse(cls.src, filename=BREADCRUMB_REL)

    def test_street_needs_breadcrumb_known_pollution(self):
        needs = self._needs
        # Known polluted → show; known pure → hide.
        self.assertTrue(needs(2200, {2200: 0.55}, seedPollution=0.4, pure=0.0))
        self.assertFalse(needs(2200, {2200: 0.0}, seedPollution=0.4, pure=0.0))
        self.assertFalse(needs(2200, {2200: 0.05}, seedPollution=0.9, pure=0.1))
        self.assertTrue(needs(2200, {2200: 0.2}, seedPollution=0.0, pure=0.1))

    def test_street_needs_breadcrumb_seed_fallback(self):
        needs = self._needs
        # Unknown zone falls back to seed so reclaim streets stay discoverable.
        self.assertTrue(needs(2300, {}, seedPollution=0.70, pure=0.0))
        self.assertFalse(needs(2300, {}, seedPollution=0.0, pure=0.0))
        self.assertFalse(needs(2100, {}, seedPollution=0.05, pure=0.1))
        # Bad seed / pollution values do not crash — treat as no marker.
        self.assertFalse(needs(2200, {2200: 'nope'}, seedPollution=0.5))
        self.assertFalse(needs(2200, {}, seedPollution='nope'))

    def test_module_exports_and_hub_copy(self):
        names = {
            node.name for node in self.tree.body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
        for expected in (
                'reclaimStreetEntries',
                'streetNeedsBreadcrumb',
                'placemarkerPulseParams',
                'streetBreadcrumbPulseParams',
                'playgroundFogEdgePulseParams',
                'CorruptStreetBreadcrumb',
                'ensureCorruptStreetBreadcrumbs',
                'stopCorruptStreetBreadcrumbs'):
            self.assertIn(expected, names, msg='missing %s' % expected)

        # Rubber-hose placemarker copy for all three reclaim tunnels.
        for needle in (
                'Ink stains Loopy',
                'Sludge jokes on Punchline',
                'Silly Street ink-deep',
                'reclaim'):
            self.assertIn(needle, self.src)
        # Notice pulse wiring (scale + cream highlight) on polluted markers.
        for needle in (
                '_startPulseLoop',
                '_buildNoticePulseIval',
                'LerpColorScaleInterval',
                '_PULSE_HIGHLIGHT',
                '_PULSE_GAP_SEC'):
            self.assertIn(needle, self.src, msg='missing pulse cue %s' % needle)
        # Distinct tunnel-mouth crumb trail pulse (not placemarker #211).
        for needle in (
                '_attachCrumbTrail',
                '_startCrumbPulseLoop',
                '_buildCrumbPulseIval',
                'streetBreadcrumbPulseParams',
                '_CRUMB_PULSE_GAP_SEC',
                'corruptStreetCrumbTrail'):
            self.assertIn(needle, self.src, msg='missing crumb pulse %s' % needle)
        # Playground pollution fog edge breath (not #211 / #216).
        for needle in (
                '_attachFogEdge',
                '_startFogPulseLoop',
                '_buildFogPulseIval',
                'playgroundFogEdgePulseParams',
                '_FOG_PULSE_GAP_SEC',
                'playgroundPollutionFogEdge',
                'CardMaker'):
            self.assertIn(needle, self.src, msg='missing fog edge %s' % needle)
        # No KH branding / magic-word discoverability.
        src_l = self.src.lower()
        self.assertNotIn('keyblade', src_l)
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('~startcampaign', self.src)
        self.assertNotIn('~reclaim', self.src)

    def test_placemarker_pulse_params(self):
        params = self._pulse()
        self.assertGreater(params['peak'], 1.0)
        self.assertLess(params['peak'], 1.5)
        self.assertGreater(params['halfSec'], 0.05)
        self.assertLessEqual(params['halfSec'], 0.35)
        self.assertGreaterEqual(params['beats'], 2)
        self.assertLessEqual(params['beats'], 4)
        self.assertGreaterEqual(params['gapSec'], 2.0)
        self.assertLessEqual(params['gapSec'], 8.0)
        self.assertGreater(params['baseScale'], 0.5)

    def test_street_breadcrumb_pulse_params_distinct(self):
        placemarker = self._pulse()
        crumb = self._crumb_pulse()
        self.assertGreater(crumb['peak'], 1.0)
        self.assertLess(crumb['peak'], 1.6)
        self.assertGreater(crumb['halfSec'], 0.04)
        self.assertLessEqual(crumb['halfSec'], 0.30)
        self.assertGreaterEqual(crumb['count'], 2)
        self.assertLessEqual(crumb['count'], 5)
        self.assertGreaterEqual(crumb['staggerSec'], 0.05)
        self.assertLess(crumb['staggerSec'], 0.4)
        self.assertGreater(crumb['baseScale'], 0.2)
        # Crumb trail is snappier / denser than overhead placemarker pulse.
        self.assertLess(crumb['gapSec'], placemarker['gapSec'])
        self.assertLess(crumb['halfSec'], placemarker['halfSec'])
        self.assertNotEqual(crumb['peak'], placemarker['peak'])

    def test_playground_fog_edge_pulse_params_distinct(self):
        placemarker = self._pulse()
        crumb = self._crumb_pulse()
        fog = self._fog_pulse()
        # Opacity breath — not a cream scale snap like #211 / #216.
        self.assertIn('restAlpha', fog)
        self.assertIn('peakAlpha', fog)
        self.assertIn('billow', fog)
        self.assertGreater(fog['peakAlpha'], fog['restAlpha'])
        self.assertGreater(fog['restAlpha'], 0.05)
        self.assertLess(fog['peakAlpha'], 0.55)
        self.assertGreater(fog['billow'], 1.0)
        self.assertLess(fog['billow'], 1.25)
        self.assertGreater(fog['halfSec'], 0.25)
        self.assertLessEqual(fog['halfSec'], 0.70)
        self.assertGreaterEqual(fog['gapSec'], 5.0)
        self.assertLessEqual(fog['gapSec'], 9.0)
        # Slower / softer than placemarker + crumb scale pulses.
        self.assertGreater(fog['gapSec'], placemarker['gapSec'])
        self.assertGreater(fog['gapSec'], crumb['gapSec'])
        self.assertGreater(fog['halfSec'], placemarker['halfSec'])
        self.assertGreater(fog['halfSec'], crumb['halfSec'])
        # Fog helper must not look like the scale-peak crumb/placemarker dicts.
        self.assertNotIn('peak', fog)
        self.assertNotIn('staggerSec', fog)
        self.assertNotIn('beats', fog)

    def test_tt_playground_wires_breadcrumbs(self):
        playground = (
            REPO_ROOT / 'toontown' / 'safezone' / 'TTPlayground.py'
        ).read_text(encoding='utf-8')
        self.assertIn('CorruptStreetBreadcrumb', playground)
        self.assertIn('ensureCorruptStreetBreadcrumbs', playground)
        self.assertIn('stopCorruptStreetBreadcrumbs', playground)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        CorruptStreetBreadcrumbTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
