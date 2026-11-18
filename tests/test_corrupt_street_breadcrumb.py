#!/usr/bin/env python3
"""Behavioral headless tests for TTC polluted-tunnel placemarker helpers.

Loads pure helpers from CorruptStreetBreadcrumb via AST extraction (no
Panda3D). Covers streetNeedsBreadcrumb pollution/seed rules used by hub
discoverability (#192), placemarker notice-pulse timing (#211), cream
deepen mid-settle + local halo on that pulse (#230), placemarker cream
rim deepen (#252; ≠ #250 / #230), placemarker cream deepen past #252 /
#268 / #277 (brighter/wider halo / longer hold / punchier rebound), the
distinct tunnel-mouth crumb-trail pulse (#216), crumb pulse cream deepen
(mid-settle + pip #241), crumb pip cream deepen (#258; ≠ #252 / #250 /
#241), crumb pip cream deepen past #258 / #270 / #282 (brighter/wider
pip / longer hold / punchier rebound; ≠ fog #295 / tunnel #290 / birds
#285), playground pollution fog edge breath (#221), fog-edge cream
deepen (cream mid-settle + rim #236), and fog cream rim deepen (juicier
rim + mid hold + rebound; ≠ #246 / #236 / birds #285), and fog cream
rim deepen past #250 (brighter/wider rim / longer hold / punchier
rebound; ≠ tunnel #290 / birds #285 / crumb #282+).

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
        '_PULSE_HIGHLIGHT', '_PULSE_CREAM_MID', '_PULSE_CREAM_MID_SEC',
        '_PULSE_HALO_PEAK', '_PULSE_HALO_MID', '_PULSE_HALO_SCALE_PEAK',
        '_PULSE_HALO_HALF_W', '_PULSE_HALO_HALF_H',
        '_PULSE_HALO_HOLD_SEC', '_PULSE_HALO_REBOUND_SCALE',
        '_PULSE_HALO_REBOUND_SEC', '_PULSE_HALO_REBOUND_PEAK',
        '_MARKER_SCALE',
        '_CRUMB_PULSE_PEAK', '_CRUMB_PULSE_HALF_SEC', '_CRUMB_PULSE_GAP_SEC',
        '_CRUMB_STAGGER_SEC', '_CRUMB_COUNT', '_CRUMB_SCALE',
        '_CRUMB_HIGHLIGHT', '_CRUMB_CREAM_MID', '_CRUMB_CREAM_MID_SEC',
        '_CRUMB_PIP_PEAK', '_CRUMB_PIP_MID', '_CRUMB_PIP_SCALE_PEAK',
        '_CRUMB_PIP_HALF_W', '_CRUMB_PIP_HALF_H',
        '_CRUMB_PIP_HOLD_SEC', '_CRUMB_PIP_REBOUND_SCALE',
        '_CRUMB_PIP_REBOUND_SEC', '_CRUMB_PIP_REBOUND_PEAK',
        '_FOG_PULSE_HALF_SEC', '_FOG_PULSE_GAP_SEC', '_FOG_REST', '_FOG_PEAK',
        '_FOG_BILLOW', '_FOG_SCALE',
        '_FOG_CREAM_MID', '_FOG_CREAM_MID_SEC',
        '_FOG_CREAM_RIM_PEAK', '_FOG_CREAM_RIM_MID',
        '_FOG_CREAM_RIM_SCALE_PEAK', '_FOG_CREAM_RIM_HALF_W', '_FOG_CREAM_RIM_HALF_H',
        '_FOG_CREAM_RIM_HOLD_SEC', '_FOG_CREAM_RIM_REBOUND_SCALE',
        '_FOG_CREAM_RIM_REBOUND_SEC', '_FOG_CREAM_RIM_REBOUND_PEAK',
    }
    keep = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in const_names:
                    keep.append(node)
                    break
        elif isinstance(node, ast.FunctionDef) and node.name in (
                '_streetLooksPolluted',
                '_streetActUnlocked',
                'streetNeedsBreadcrumb',
                'streetBreadcrumbDimmed',
                'placemarkerPulseParams',
                'placemarkerPulseCreamParams',
                'streetBreadcrumbPulseParams',
                'streetBreadcrumbPulseCreamParams',
                'playgroundFogEdgePulseParams',
                'playgroundFogEdgeCreamParams'):
            keep.append(node)
    if not any(
            isinstance(n, ast.FunctionDef) and n.name == '_streetLooksPolluted'
            for n in keep):
        raise AssertionError('_streetLooksPolluted not found in %s' % BREADCRUMB_REL)
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
            and n.name == 'placemarkerPulseCreamParams'
            for n in keep):
        raise AssertionError(
            'placemarkerPulseCreamParams not found in %s' % BREADCRUMB_REL)
    if not any(
            isinstance(n, ast.FunctionDef)
            and n.name == 'streetBreadcrumbPulseParams'
            for n in keep):
        raise AssertionError(
            'streetBreadcrumbPulseParams not found in %s' % BREADCRUMB_REL)
    if not any(
            isinstance(n, ast.FunctionDef)
            and n.name == 'streetBreadcrumbPulseCreamParams'
            for n in keep):
        raise AssertionError(
            'streetBreadcrumbPulseCreamParams not found in %s' % BREADCRUMB_REL)
    if not any(
            isinstance(n, ast.FunctionDef)
            and n.name == 'playgroundFogEdgePulseParams'
            for n in keep):
        raise AssertionError(
            'playgroundFogEdgePulseParams not found in %s' % BREADCRUMB_REL)
    if not any(
            isinstance(n, ast.FunctionDef)
            and n.name == 'playgroundFogEdgeCreamParams'
            for n in keep):
        raise AssertionError(
            'playgroundFogEdgeCreamParams not found in %s' % BREADCRUMB_REL)
    mod = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(mod)
    ns = {
        # Vec4-like stand-in so cream/fog Vec4 assignments work headless.
        'Vec4': lambda *args: tuple(args),
    }
    exec(compile(mod, BREADCRUMB_REL, 'exec'), ns)  # noqa: S102 — test harness
    return (
        ns['streetNeedsBreadcrumb'],
        ns['placemarkerPulseParams'],
        ns['placemarkerPulseCreamParams'],
        ns['streetBreadcrumbPulseParams'],
        ns['streetBreadcrumbPulseCreamParams'],
        ns['playgroundFogEdgePulseParams'],
        ns['playgroundFogEdgeCreamParams'],
    )


class CorruptStreetBreadcrumbTest(unittest.TestCase):
    """Pure helper + AST wiring for hub polluted-tunnel placemarkers."""

    @classmethod
    def setUpClass(cls):
        # Store on the class dict under a private name so Python does not
        # bind the helper as an instance method (which would shift args).
        (needs, pulse, cream, crumb_pulse, crumb_cream,
         fog_pulse, fog_cream) = _extract_pure_helpers()
        cls._needs = staticmethod(needs)
        cls._pulse = staticmethod(pulse)
        cls._cream = staticmethod(cream)
        cls._crumb_pulse = staticmethod(crumb_pulse)
        cls._crumb_cream = staticmethod(crumb_cream)
        cls._fog_pulse = staticmethod(fog_pulse)
        cls._fog_cream = staticmethod(fog_cream)
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
                'streetBreadcrumbDimmed',
                'noteCampaignActUnlocked',
                'placemarkerPulseParams',
                'placemarkerPulseCreamParams',
                'streetBreadcrumbPulseParams',
                'streetBreadcrumbPulseCreamParams',
                'playgroundFogEdgePulseParams',
                'playgroundFogEdgeCreamParams',
                'CorruptStreetBreadcrumb',
                'ensureCorruptStreetBreadcrumbs',
                'stopCorruptStreetBreadcrumbs'):
            self.assertIn(expected, names, msg='missing %s' % expected)
        # Act-unlock soft-gate consumer (dim locked crumbs).
        self.assertIn("self.accept('campaignActUnlocked'", self.src)
        self.assertIn('unlockedThrough', self.src)
        # Login progress sync rehydrates unlock latch after relog.
        self.assertIn('_onCampaignProgressSync', self.src)
        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', self.src)

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
        # Cream deepen on placemarker pulse (juicier mid-settle + local halo).
        for needle in (
                'placemarkerPulseCreamParams',
                '_attachPulseCreamHalo',
                '_buildPulseCreamHaloIval',
                '_PULSE_CREAM_MID',
                '_PULSE_CREAM_MID_SEC',
                '_PULSE_HALO_PEAK',
                'corruptStreetPlacemarkerCreamHalo',
                'fullscreenWash'):
            self.assertIn(
                needle, self.src, msg='missing pulse cream deepen %s' % needle)
        # Placemarker cream rim deepen (mid hold + rebound; ≠ fog #250 / #230).
        for needle in (
                '_PULSE_HALO_HOLD_SEC',
                '_PULSE_HALO_REBOUND_SCALE',
                '_PULSE_HALO_REBOUND_SEC',
                '_PULSE_HALO_REBOUND_PEAK',
                'haloHoldSec',
                'haloRimRebound',
                'haloReboundScale'):
            self.assertIn(
                needle, self.src,
                msg='missing pulse cream rim deepen %s' % needle)
        # Distinct tunnel-mouth crumb trail pulse (not placemarker #211).
        for needle in (
                '_attachCrumbTrail',
                '_startCrumbPulseLoop',
                '_buildCrumbPulseIval',
                'streetBreadcrumbPulseParams',
                '_CRUMB_PULSE_GAP_SEC',
                'corruptStreetCrumbTrail'):
            self.assertIn(needle, self.src, msg='missing crumb pulse %s' % needle)
        # Crumb pulse cream deepen (mid-settle + pip; not #230 / #236 / #226).
        for needle in (
                'streetBreadcrumbPulseCreamParams',
                '_makeCrumbCreamPip',
                '_buildCrumbCreamPipIval',
                '_CRUMB_CREAM_MID',
                '_CRUMB_CREAM_MID_SEC',
                '_CRUMB_PIP_PEAK',
                'corruptStreetCrumbCreamPip',
                'localPip'):
            self.assertIn(
                needle, self.src, msg='missing crumb cream deepen %s' % needle)
        # Crumb pip cream deepen (mid hold + rebound; ≠ halo #252 / fog #250).
        for needle in (
                '_CRUMB_PIP_HOLD_SEC',
                '_CRUMB_PIP_REBOUND_SCALE',
                '_CRUMB_PIP_REBOUND_SEC',
                '_CRUMB_PIP_REBOUND_PEAK',
                'pipHoldSec',
                'pipRimRebound',
                'pipReboundScale'):
            self.assertIn(
                needle, self.src,
                msg='missing crumb pip cream deepen %s' % needle)
        # Past-#282 pip deepen floors (brighter/wider pip / longer hold).
        self.assertRegex(
            self.src,
            r'_CRUMB_PIP_SCALE_PEAK\s*=\s*1\.(7[2-9]|[89])')
        self.assertRegex(
            self.src,
            r'_CRUMB_PIP_HOLD_SEC\s*=\s*0\.0(8|9)')
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
        # Fog edge cream deepen (cream mid-settle + rim; not #230 / #226).
        for needle in (
                'playgroundFogEdgeCreamParams',
                '_attachFogCreamRim',
                '_buildFogCreamRimIval',
                '_FOG_CREAM_MID',
                '_FOG_CREAM_MID_SEC',
                '_FOG_CREAM_RIM_PEAK',
                'playgroundPollutionFogCreamRim',
                'localRim'):
            self.assertIn(
                needle, self.src, msg='missing fog cream deepen %s' % needle)
        # Fog cream rim deepen (mid hold + rebound; not birds #246 / #236 alone).
        for needle in (
                '_FOG_CREAM_RIM_HOLD_SEC',
                '_FOG_CREAM_RIM_REBOUND_SCALE',
                '_FOG_CREAM_RIM_REBOUND_SEC',
                '_FOG_CREAM_RIM_REBOUND_PEAK',
                'rimHoldSec',
                'rimRebound',
                'birdsChirpFlecks'):
            self.assertIn(
                needle, self.src, msg='missing fog cream rim deepen %s' % needle)
        # Birds-return cream wash when hub pollution clears (#231).
        for needle in (
                '_cueBirdsReturnCreamWash',
                '_clearBirdsReturnCreamWash',
                'BirdsReturnCreamWashFx',
                'playBirdsReturnCreamWash'):
            self.assertIn(
                needle, self.src, msg='missing birds-return wash %s' % needle)
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

    def test_placemarker_pulse_cream_deepen_params(self):
        cream = self._cream()
        # Juicier cream mid-settle + local halo — not a fullscreen wash.
        self.assertFalse(cream['fullscreenWash'])
        self.assertFalse(cream['fogRim'])
        self.assertGreater(cream['creamMidSec'], 0.04)
        self.assertLessEqual(cream['creamMidSec'], 0.20)
        hi = cream['highlight']
        mid = cream['creamMid']
        self.assertEqual(len(hi), 4)
        self.assertEqual(len(mid), 4)
        # Sunny cream peak is warm (high R/G, softer B) and opaque.
        self.assertGreaterEqual(hi[0], 0.95)
        self.assertGreaterEqual(hi[1], 0.88)
        self.assertLess(hi[2], hi[1])
        self.assertAlmostEqual(hi[3], 1.0, places=2)
        # Mid settle is softer / creamier than the punchy peak.
        self.assertGreater(mid[1], hi[1] - 0.02)
        self.assertGreater(mid[2], hi[2])
        self.assertGreater(cream['haloPeakAlpha'], cream['haloMidAlpha'])
        self.assertGreater(cream['haloPeakAlpha'], 0.20)
        self.assertLess(cream['haloPeakAlpha'], 0.55)
        self.assertGreater(cream['haloMidAlpha'], 0.05)
        self.assertLess(cream['haloMidAlpha'], cream['haloPeakAlpha'])
        self.assertGreater(cream['haloScalePeak'], 1.1)
        self.assertLess(cream['haloScalePeak'], 1.6)
        self.assertGreater(cream['haloHalfW'], 1.5)
        self.assertGreater(cream['haloHalfH'], 0.3)
        # Distinct from placemarker scale-pulse dict (#211 base).
        pulse = self._pulse()
        self.assertNotIn('highlight', pulse)
        self.assertNotIn('haloPeakAlpha', pulse)
        self.assertNotIn('fullscreenWash', pulse)

    def test_placemarker_pulse_cream_rim_deepen_params(self):
        """Halo rim deepen past #230 — juicier + hold + rebound (≠ #250)."""
        cream = self._cream()
        fog_cream = self._fog_cream()
        crumb_cream = self._crumb_cream()
        # Local halo rim rebound — not fog tunnel-lip rim / birds chirp.
        self.assertTrue(cream['haloRimRebound'])
        self.assertFalse(cream['fogRim'])
        self.assertFalse(cream['birdsChirpFlecks'])
        self.assertFalse(cream['fullscreenWash'])
        # Juicier than original #230 halo peak (0.38) / scale (1.32).
        self.assertGreater(cream['haloPeakAlpha'], 0.38)
        self.assertLess(cream['haloPeakAlpha'], 0.55)
        self.assertGreater(cream['haloMidAlpha'], 0.16)
        self.assertLess(cream['haloMidAlpha'], cream['haloPeakAlpha'])
        self.assertGreater(cream['haloScalePeak'], 1.32)
        self.assertLess(cream['haloScalePeak'], crumb_cream['pipScalePeak'])
        # Punchier / snappier than fog rim deepen #250.
        self.assertGreater(cream['haloScalePeak'], fog_cream['rimScalePeak'])
        self.assertLess(cream['haloHoldSec'], fog_cream['rimHoldSec'])
        self.assertGreater(cream['haloReboundScale'], fog_cream['rimReboundScale'])
        self.assertLess(cream['haloReboundSec'], fog_cream['rimReboundSec'])
        # Soft mid hold + micro rebound settle (rim deepen signature).
        self.assertGreater(cream['haloHoldSec'], 0.04)
        self.assertLessEqual(cream['haloHoldSec'], 0.12)
        self.assertGreater(cream['haloReboundScale'], 1.0)
        self.assertLess(cream['haloReboundScale'], cream['haloScalePeak'])
        self.assertGreater(cream['haloReboundSec'], 0.04)
        self.assertLessEqual(cream['haloReboundSec'], 0.12)
        self.assertGreater(cream['haloReboundAlpha'], 0.08)
        self.assertLess(cream['haloReboundAlpha'], cream['haloMidAlpha'])
        # Distinct deepen keys — not fog rim / crumb pip vocabulary.
        self.assertNotIn('haloHoldSec', fog_cream)
        self.assertNotIn('haloRimRebound', fog_cream)
        self.assertNotIn('haloReboundScale', crumb_cream)
        self.assertNotIn('rimHoldSec', cream)
        self.assertNotIn('rimRebound', cream)
        self.assertNotIn('birdsChirpFlecks', crumb_cream)

    def test_placemarker_pulse_cream_deepen_past_252(self):
        """Past-#252 deepen — brighter halo / longer hold / punchier rebound."""
        cream = self._cream()
        fog_cream = self._fog_cream()
        crumb_cream = self._crumb_cream()
        # Still local halo rim rebound — not fog / crumb / fullscreen / birds.
        self.assertTrue(cream['haloRimRebound'])
        self.assertFalse(cream['fogRim'])
        self.assertFalse(cream['birdsChirpFlecks'])
        self.assertFalse(cream['fullscreenWash'])
        # Floors past merged #252 rim deepen knobs.
        self.assertGreater(cream['creamMidSec'], 0.10)
        self.assertLessEqual(cream['creamMidSec'], 0.16)
        self.assertGreater(cream['haloPeakAlpha'], 0.44)
        self.assertLess(cream['haloPeakAlpha'], 0.55)
        self.assertGreater(cream['haloMidAlpha'], 0.22)
        self.assertLess(cream['haloMidAlpha'], cream['haloPeakAlpha'])
        self.assertGreater(cream['haloScalePeak'], 1.38)
        self.assertLess(cream['haloScalePeak'], crumb_cream['pipScalePeak'])
        self.assertGreater(cream['haloHalfW'], 2.70)
        self.assertGreater(cream['haloHalfH'], 0.68)
        self.assertGreater(cream['haloHoldSec'], 0.07)
        self.assertLess(cream['haloHoldSec'], fog_cream['rimHoldSec'])
        self.assertGreater(
            cream['haloReboundScale'], 1.10)
        self.assertLess(
            cream['haloReboundScale'], crumb_cream['pipReboundScale'])
        self.assertGreater(cream['haloReboundSec'], 0.06)
        self.assertLess(cream['haloReboundSec'], fog_cream['rimReboundSec'])
        self.assertGreater(cream['haloReboundAlpha'], 0.14)
        self.assertLess(cream['haloReboundAlpha'], cream['haloMidAlpha'])
        # Warmer text cream peak than #252 (B softer / G creamier).
        hi = cream['highlight']
        mid = cream['creamMid']
        self.assertLess(hi[2], 0.50)
        self.assertGreaterEqual(hi[1], 0.95)
        self.assertGreater(mid[2], 0.74)
        # Distinctness vs crumb pip / fog rim vocabulary stays package-local.
        self.assertNotIn('pipHoldSec', cream)
        self.assertNotIn('rimHoldSec', cream)
        self.assertNotIn('haloHoldSec', crumb_cream)
        self.assertNotIn('haloHoldSec', fog_cream)

    def test_placemarker_pulse_cream_deepen_past_268(self):
        """Past-#268 deepen — brighter/wider halo / longer hold / punchier rebound."""
        cream = self._cream()
        fog_cream = self._fog_cream()
        crumb_cream = self._crumb_cream()
        # Still local halo rim rebound — not fog / crumb / fullscreen / birds.
        self.assertTrue(cream['haloRimRebound'])
        self.assertFalse(cream['fogRim'])
        self.assertFalse(cream['birdsChirpFlecks'])
        self.assertFalse(cream['fullscreenWash'])
        # Floors past merged #268 placemarker cream deepen knobs.
        self.assertGreater(cream['creamMidSec'], 0.11)
        self.assertLessEqual(cream['creamMidSec'], 0.16)
        self.assertGreater(cream['haloPeakAlpha'], 0.48)
        self.assertLess(cream['haloPeakAlpha'], 0.55)
        self.assertGreater(cream['haloMidAlpha'], 0.26)
        self.assertLess(cream['haloMidAlpha'], cream['haloPeakAlpha'])
        self.assertGreater(cream['haloScalePeak'], 1.44)
        self.assertLess(cream['haloScalePeak'], crumb_cream['pipScalePeak'])
        self.assertGreater(cream['haloHalfW'], 2.85)
        self.assertGreater(cream['haloHalfH'], 0.72)
        self.assertGreater(cream['haloHoldSec'], 0.085)
        self.assertLess(cream['haloHoldSec'], fog_cream['rimHoldSec'])
        self.assertGreater(cream['haloReboundScale'], 1.12)
        self.assertLess(
            cream['haloReboundScale'], crumb_cream['pipReboundScale'])
        self.assertGreater(cream['haloReboundSec'], 0.065)
        self.assertLess(cream['haloReboundSec'], fog_cream['rimReboundSec'])
        self.assertGreater(cream['haloReboundAlpha'], 0.17)
        self.assertLess(cream['haloReboundAlpha'], cream['haloMidAlpha'])
        # Warmer text cream peak than #268 (B softer / G creamier).
        hi = cream['highlight']
        mid = cream['creamMid']
        self.assertLess(hi[2], 0.46)
        self.assertGreaterEqual(hi[1], 0.96)
        self.assertGreater(mid[2], 0.78)
        # Distinctness vs crumb pip / fog rim vocabulary stays package-local.
        self.assertNotIn('pipHoldSec', cream)
        self.assertNotIn('rimHoldSec', cream)
        self.assertNotIn('haloHoldSec', crumb_cream)
        self.assertNotIn('haloHoldSec', fog_cream)

    def test_placemarker_pulse_cream_deepen_past_277(self):
        """Past-#277 deepen — brighter/wider halo / longer hold / punchier rebound."""
        cream = self._cream()
        fog_cream = self._fog_cream()
        crumb_cream = self._crumb_cream()
        # Still local halo rim rebound — not fog / crumb / fullscreen / birds.
        self.assertTrue(cream['haloRimRebound'])
        self.assertFalse(cream['fogRim'])
        self.assertFalse(cream['birdsChirpFlecks'])
        self.assertFalse(cream['fullscreenWash'])
        # Floors past merged #277 placemarker cream rim deepen knobs.
        self.assertGreater(cream['creamMidSec'], 0.12)
        self.assertLessEqual(cream['creamMidSec'], 0.16)
        self.assertGreater(cream['haloPeakAlpha'], 0.52)
        self.assertLess(cream['haloPeakAlpha'], 0.55)
        self.assertGreater(cream['haloMidAlpha'], 0.30)
        self.assertLess(cream['haloMidAlpha'], cream['haloPeakAlpha'])
        self.assertGreater(cream['haloScalePeak'], 1.50)
        self.assertLess(cream['haloScalePeak'], crumb_cream['pipScalePeak'])
        self.assertGreater(cream['haloHalfW'], 3.00)
        self.assertGreater(cream['haloHalfH'], 0.76)
        self.assertGreater(cream['haloHoldSec'], 0.092)
        self.assertLess(cream['haloHoldSec'], fog_cream['rimHoldSec'])
        self.assertGreater(cream['haloReboundScale'], 1.14)
        self.assertLess(
            cream['haloReboundScale'], crumb_cream['pipReboundScale'])
        self.assertGreater(cream['haloReboundSec'], 0.072)
        self.assertLess(cream['haloReboundSec'], fog_cream['rimReboundSec'])
        self.assertGreater(cream['haloReboundAlpha'], 0.20)
        self.assertLess(cream['haloReboundAlpha'], cream['haloMidAlpha'])
        # Warmer text cream peak than #277 (B softer / G creamier).
        hi = cream['highlight']
        mid = cream['creamMid']
        self.assertLess(hi[2], 0.42)
        self.assertGreaterEqual(hi[1], 0.97)
        self.assertGreater(mid[2], 0.82)
        # Distinctness vs crumb pip / fog rim / birds wash vocabulary.
        self.assertNotIn('pipHoldSec', cream)
        self.assertNotIn('rimHoldSec', cream)
        self.assertNotIn('haloHoldSec', crumb_cream)
        self.assertNotIn('haloHoldSec', fog_cream)

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

    def test_street_breadcrumb_pulse_cream_deepen_params(self):
        cream = self._crumb_cream()
        placemarker_cream = self._cream()
        fog_cream = self._fog_cream()
        # Trail-local cream pip + mid-settle — not fullscreen / halo / fog rim.
        self.assertTrue(cream['localPip'])
        self.assertFalse(cream['fullscreenWash'])
        self.assertFalse(cream['placemarkerHalo'])
        self.assertFalse(cream['fogRim'])
        self.assertGreater(cream['creamMidSec'], 0.04)
        self.assertLessEqual(cream['creamMidSec'], 0.12)
        # Snappier mid than placemarker (#230) and fog (#236).
        self.assertLess(cream['creamMidSec'], placemarker_cream['creamMidSec'])
        self.assertLess(cream['creamMidSec'], fog_cream['creamMidSec'])
        hi = cream['highlight']
        mid = cream['creamMid']
        self.assertEqual(len(hi), 4)
        self.assertEqual(len(mid), 4)
        # Warm crumb cream peak (high R/G, softer B) and opaque.
        self.assertGreaterEqual(hi[0], 0.95)
        self.assertGreaterEqual(hi[1], 0.82)
        self.assertLess(hi[2], hi[1])
        self.assertAlmostEqual(hi[3], 1.0, places=2)
        # Mid settle is softer / creamier than the punchy peak.
        self.assertGreater(mid[1], hi[1] - 0.02)
        self.assertGreater(mid[2], hi[2])
        self.assertGreater(cream['pipPeakAlpha'], cream['pipMidAlpha'])
        self.assertGreater(cream['pipPeakAlpha'], 0.25)
        self.assertLess(cream['pipPeakAlpha'], 0.65)
        self.assertGreater(cream['pipMidAlpha'], 0.05)
        self.assertLess(cream['pipMidAlpha'], cream['pipPeakAlpha'])
        self.assertGreater(cream['pipScalePeak'], 1.2)
        self.assertLess(cream['pipScalePeak'], 1.80)
        # Punchier pip bloom than fog rim; distinct from placemarker halo.
        self.assertGreater(cream['pipScalePeak'], fog_cream['rimScalePeak'])
        self.assertNotEqual(
            cream['pipScalePeak'], placemarker_cream['haloScalePeak'])
        self.assertGreater(cream['pipHalfW'], 0.2)
        self.assertLess(cream['pipHalfW'], 1.0)
        self.assertGreater(cream['pipHalfH'], 0.1)
        self.assertLess(cream['pipHalfH'], 0.6)
        # Tiny trail blot — much smaller than placemarker halo / fog rim.
        self.assertLess(cream['pipHalfW'], placemarker_cream['haloHalfW'])
        self.assertLess(cream['pipHalfW'], fog_cream['rimHalfW'])
        # Distinct cream-deepen dict keys across the three safezone cues.
        self.assertNotIn('haloPeakAlpha', cream)
        self.assertNotIn('rimPeakAlpha', cream)
        self.assertNotIn('pipPeakAlpha', placemarker_cream)
        self.assertNotIn('pipPeakAlpha', fog_cream)
        self.assertNotIn('localPip', placemarker_cream)
        self.assertNotIn('localPip', fog_cream)

    def test_street_breadcrumb_pulse_cream_pip_deepen_params(self):
        """Pip deepen past #241 — juicier pip + hold + rebound (≠ #252/#250)."""
        cream = self._crumb_cream()
        placemarker_cream = self._cream()
        fog_cream = self._fog_cream()
        # Local pip rim rebound — not placemarker halo rim / fog rim / wash.
        self.assertTrue(cream['localPip'])
        self.assertTrue(cream['pipRimRebound'])
        self.assertFalse(cream['fullscreenWash'])
        self.assertFalse(cream['placemarkerHalo'])
        self.assertFalse(cream['fogRim'])
        # Juicier than original #241 pip peak (0.42) / scale (1.48).
        self.assertGreater(cream['pipPeakAlpha'], 0.42)
        self.assertLess(cream['pipPeakAlpha'], 0.65)
        self.assertGreater(cream['pipMidAlpha'], 0.18)
        self.assertLess(cream['pipMidAlpha'], cream['pipPeakAlpha'])
        self.assertGreater(cream['pipScalePeak'], 1.48)
        self.assertLess(cream['pipScalePeak'], 1.80)
        # Punchier / snappier than placemarker halo #252 and fog rim #250.
        self.assertGreater(cream['pipScalePeak'], placemarker_cream['haloScalePeak'])
        self.assertGreater(cream['pipScalePeak'], fog_cream['rimScalePeak'])
        self.assertLess(cream['pipHoldSec'], placemarker_cream['haloHoldSec'])
        self.assertLess(cream['pipHoldSec'], fog_cream['rimHoldSec'])
        self.assertGreater(
            cream['pipReboundScale'], placemarker_cream['haloReboundScale'])
        self.assertGreater(
            cream['pipReboundScale'], fog_cream['rimReboundScale'])
        self.assertLess(cream['pipReboundSec'], placemarker_cream['haloReboundSec'])
        self.assertLess(cream['pipReboundSec'], fog_cream['rimReboundSec'])
        # Soft mid hold + micro rebound settle (pip deepen signature).
        self.assertGreater(cream['pipHoldSec'], 0.03)
        self.assertLessEqual(cream['pipHoldSec'], 0.10)
        self.assertGreater(cream['pipReboundScale'], 1.0)
        self.assertLess(cream['pipReboundScale'], cream['pipScalePeak'])
        self.assertGreater(cream['pipReboundSec'], 0.03)
        self.assertLessEqual(cream['pipReboundSec'], 0.10)
        self.assertGreater(cream['pipReboundAlpha'], 0.06)
        self.assertLess(cream['pipReboundAlpha'], cream['pipMidAlpha'])
        # Distinct deepen keys — not placemarker halo / fog rim vocabulary.
        self.assertNotIn('pipHoldSec', placemarker_cream)
        self.assertNotIn('pipRimRebound', placemarker_cream)
        self.assertNotIn('pipReboundScale', fog_cream)
        self.assertNotIn('haloHoldSec', cream)
        self.assertNotIn('rimHoldSec', cream)
        self.assertNotIn('haloRimRebound', cream)
        self.assertNotIn('rimRebound', cream)

    def test_street_breadcrumb_pulse_cream_pip_deepen_past_258(self):
        """Past-#258 deepen — brighter/wider pip / longer hold / punchier rebound."""
        cream = self._crumb_cream()
        placemarker_cream = self._cream()
        fog_cream = self._fog_cream()
        # Still trail-local pip rim rebound — not halo / fog / fullscreen.
        self.assertTrue(cream['localPip'])
        self.assertTrue(cream['pipRimRebound'])
        self.assertFalse(cream['fullscreenWash'])
        self.assertFalse(cream['placemarkerHalo'])
        self.assertFalse(cream['fogRim'])
        # Floors past merged #258 pip deepen knobs.
        self.assertGreater(cream['creamMidSec'], 0.08)
        self.assertLess(cream['creamMidSec'], placemarker_cream['creamMidSec'])
        self.assertLess(cream['creamMidSec'], fog_cream['creamMidSec'])
        self.assertGreater(cream['pipPeakAlpha'], 0.48)
        self.assertLess(cream['pipPeakAlpha'], 0.65)
        self.assertGreater(cream['pipMidAlpha'], 0.22)
        self.assertLess(cream['pipMidAlpha'], cream['pipPeakAlpha'])
        self.assertGreater(cream['pipScalePeak'], 1.56)
        self.assertLess(cream['pipScalePeak'], 1.80)
        self.assertGreater(cream['pipHalfW'], 0.42)
        self.assertLess(cream['pipHalfW'], placemarker_cream['haloHalfW'])
        self.assertGreater(cream['pipHalfH'], 0.28)
        self.assertLess(cream['pipHalfH'], 0.6)
        self.assertGreater(cream['pipHoldSec'], 0.05)
        self.assertLess(cream['pipHoldSec'], placemarker_cream['haloHoldSec'])
        self.assertLess(cream['pipHoldSec'], fog_cream['rimHoldSec'])
        self.assertGreater(cream['pipReboundScale'], 1.14)
        self.assertGreater(
            cream['pipReboundScale'], placemarker_cream['haloReboundScale'])
        self.assertGreater(
            cream['pipReboundScale'], fog_cream['rimReboundScale'])
        self.assertLess(cream['pipReboundScale'], cream['pipScalePeak'])
        self.assertGreater(cream['pipReboundSec'], 0.05)
        self.assertLess(cream['pipReboundSec'], placemarker_cream['haloReboundSec'])
        self.assertLess(cream['pipReboundSec'], fog_cream['rimReboundSec'])
        self.assertGreater(cream['pipReboundAlpha'], 0.12)
        self.assertLess(cream['pipReboundAlpha'], cream['pipMidAlpha'])
        # Warmer crumb cream peak than #258 (B softer / G creamier).
        hi = cream['highlight']
        mid = cream['creamMid']
        self.assertLess(hi[2], 0.38)
        self.assertGreaterEqual(hi[1], 0.91)
        self.assertGreater(mid[2], 0.64)
        # Punchier crumb scale snap past #258.
        crumb = self._crumb_pulse()
        self.assertGreater(crumb['peak'], 1.46)
        self.assertLess(crumb['peak'], 1.6)
        # Distinctness vs placemarker halo / fog rim vocabulary.
        self.assertNotIn('haloHoldSec', cream)
        self.assertNotIn('rimHoldSec', cream)
        self.assertNotIn('pipHoldSec', placemarker_cream)
        self.assertNotIn('pipHoldSec', fog_cream)

    def test_street_breadcrumb_pulse_cream_pip_deepen_past_270(self):
        """Past-#270 deepen — brighter/wider pip / longer hold / punchier rebound."""
        cream = self._crumb_cream()
        placemarker_cream = self._cream()
        fog_cream = self._fog_cream()
        # Still trail-local pip rim rebound — not halo / fog / fullscreen.
        self.assertTrue(cream['localPip'])
        self.assertTrue(cream['pipRimRebound'])
        self.assertFalse(cream['fullscreenWash'])
        self.assertFalse(cream['placemarkerHalo'])
        self.assertFalse(cream['fogRim'])
        # Floors past merged #270 pip deepen knobs.
        self.assertGreater(cream['creamMidSec'], 0.09)
        self.assertLess(cream['creamMidSec'], placemarker_cream['creamMidSec'])
        self.assertLess(cream['creamMidSec'], fog_cream['creamMidSec'])
        self.assertGreater(cream['pipPeakAlpha'], 0.52)
        self.assertLess(cream['pipPeakAlpha'], 0.65)
        self.assertGreater(cream['pipMidAlpha'], 0.26)
        self.assertLess(cream['pipMidAlpha'], cream['pipPeakAlpha'])
        self.assertGreater(cream['pipScalePeak'], 1.62)
        self.assertLess(cream['pipScalePeak'], 1.80)
        self.assertGreater(cream['pipHalfW'], 0.46)
        self.assertLess(cream['pipHalfW'], placemarker_cream['haloHalfW'])
        self.assertGreater(cream['pipHalfH'], 0.30)
        self.assertLess(cream['pipHalfH'], 0.6)
        self.assertGreater(cream['pipHoldSec'], 0.06)
        self.assertLess(cream['pipHoldSec'], placemarker_cream['haloHoldSec'])
        self.assertLess(cream['pipHoldSec'], fog_cream['rimHoldSec'])
        self.assertGreater(cream['pipReboundScale'], 1.16)
        self.assertGreater(
            cream['pipReboundScale'], placemarker_cream['haloReboundScale'])
        self.assertGreater(
            cream['pipReboundScale'], fog_cream['rimReboundScale'])
        self.assertLess(cream['pipReboundScale'], cream['pipScalePeak'])
        self.assertGreater(cream['pipReboundSec'], 0.055)
        self.assertLess(cream['pipReboundSec'], placemarker_cream['haloReboundSec'])
        self.assertLess(cream['pipReboundSec'], fog_cream['rimReboundSec'])
        self.assertGreater(cream['pipReboundAlpha'], 0.15)
        self.assertLess(cream['pipReboundAlpha'], cream['pipMidAlpha'])
        # Warmer crumb cream peak than #270 (B softer / G creamier).
        hi = cream['highlight']
        mid = cream['creamMid']
        self.assertLess(hi[2], 0.34)
        self.assertGreaterEqual(hi[1], 0.92)
        self.assertGreater(mid[2], 0.68)
        # Punchier crumb scale snap past #270.
        crumb = self._crumb_pulse()
        self.assertGreater(crumb['peak'], 1.50)
        self.assertLess(crumb['peak'], 1.6)
        # Distinctness vs placemarker halo / fog rim vocabulary.
        self.assertNotIn('haloHoldSec', cream)
        self.assertNotIn('rimHoldSec', cream)
        self.assertNotIn('pipHoldSec', placemarker_cream)
        self.assertNotIn('pipHoldSec', fog_cream)

    def test_street_breadcrumb_pulse_cream_pip_deepen_past_282(self):
        """Past-#282 deepen — brighter/wider pip / longer hold / punchier rebound."""
        cream = self._crumb_cream()
        placemarker_cream = self._cream()
        fog_cream = self._fog_cream()
        # Still trail-local pip rim rebound — not halo / fog / tunnel / wash.
        self.assertTrue(cream['localPip'])
        self.assertTrue(cream['pipRimRebound'])
        self.assertFalse(cream['fullscreenWash'])
        self.assertFalse(cream['placemarkerHalo'])
        self.assertFalse(cream['fogRim'])
        # Floors past merged #282 pip deepen knobs.
        self.assertGreater(cream['creamMidSec'], 0.10)
        self.assertLess(cream['creamMidSec'], placemarker_cream['creamMidSec'])
        self.assertLess(cream['creamMidSec'], fog_cream['creamMidSec'])
        self.assertGreater(cream['pipPeakAlpha'], 0.54)
        self.assertLess(cream['pipPeakAlpha'], 0.65)
        self.assertGreater(cream['pipMidAlpha'], 0.30)
        self.assertLess(cream['pipMidAlpha'], cream['pipPeakAlpha'])
        self.assertGreater(cream['pipScalePeak'], 1.68)
        self.assertLess(cream['pipScalePeak'], 1.80)
        self.assertGreater(cream['pipHalfW'], 0.50)
        self.assertLess(cream['pipHalfW'], placemarker_cream['haloHalfW'])
        self.assertGreater(cream['pipHalfH'], 0.32)
        self.assertLess(cream['pipHalfH'], 0.6)
        self.assertGreater(cream['pipHoldSec'], 0.07)
        self.assertLess(cream['pipHoldSec'], placemarker_cream['haloHoldSec'])
        self.assertLess(cream['pipHoldSec'], fog_cream['rimHoldSec'])
        self.assertGreater(cream['pipReboundScale'], 1.18)
        self.assertGreater(
            cream['pipReboundScale'], placemarker_cream['haloReboundScale'])
        self.assertGreater(
            cream['pipReboundScale'], fog_cream['rimReboundScale'])
        self.assertLess(cream['pipReboundScale'], cream['pipScalePeak'])
        self.assertGreater(cream['pipReboundSec'], 0.062)
        self.assertLess(cream['pipReboundSec'], placemarker_cream['haloReboundSec'])
        self.assertLess(cream['pipReboundSec'], fog_cream['rimReboundSec'])
        self.assertGreater(cream['pipReboundAlpha'], 0.18)
        self.assertLess(cream['pipReboundAlpha'], cream['pipMidAlpha'])
        # Warmer crumb cream peak than #282 (B softer / G creamier).
        hi = cream['highlight']
        mid = cream['creamMid']
        self.assertLess(hi[2], 0.30)
        self.assertGreaterEqual(hi[1], 0.93)
        self.assertGreater(mid[2], 0.72)
        # Punchier crumb scale snap past #282.
        crumb = self._crumb_pulse()
        self.assertGreater(crumb['peak'], 1.54)
        self.assertLess(crumb['peak'], 1.6)
        # Distinctness vs placemarker halo / fog rim / birds vocabulary.
        self.assertNotIn('haloHoldSec', cream)
        self.assertNotIn('rimHoldSec', cream)
        self.assertNotIn('birdsChirpFlecks', cream)
        self.assertNotIn('pipHoldSec', placemarker_cream)
        self.assertNotIn('pipHoldSec', fog_cream)

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

    def test_playground_fog_edge_cream_deepen_params(self):
        cream = self._fog_cream()
        placemarker_cream = self._cream()
        fog = self._fog_pulse()
        # Tunnel-lip cream rim + mid-settle — not fullscreen / placemarker halo.
        self.assertTrue(cream['localRim'])
        self.assertFalse(cream['fullscreenWash'])
        self.assertFalse(cream['placemarkerHalo'])
        self.assertGreater(cream['creamMidSec'], 0.08)
        self.assertLessEqual(cream['creamMidSec'], 0.25)
        # Fog cream mid is slower than placemarker cream mid (#230).
        self.assertGreater(cream['creamMidSec'], placemarker_cream['creamMidSec'])
        mid = cream['creamMid']
        self.assertEqual(len(mid), 4)
        # Cream-ink mid sits between rest and peak alphas on the fog veil.
        self.assertGreater(cream['creamMidAlpha'], fog['restAlpha'])
        self.assertLess(cream['creamMidAlpha'], fog['peakAlpha'])
        self.assertGreater(cream['rimPeakAlpha'], cream['rimMidAlpha'])
        self.assertGreater(cream['rimPeakAlpha'], 0.18)
        self.assertLess(cream['rimPeakAlpha'], 0.50)
        self.assertGreater(cream['rimMidAlpha'], 0.05)
        self.assertLess(cream['rimMidAlpha'], cream['rimPeakAlpha'])
        self.assertGreater(cream['rimScalePeak'], 1.05)
        self.assertLess(cream['rimScalePeak'], 1.35)
        # Gentler bloom than placemarker halo scale peak (#230).
        self.assertLess(cream['rimScalePeak'], placemarker_cream['haloScalePeak'])
        self.assertGreater(cream['rimHalfW'], fog.get('baseScale', 0.5) + 2.0)
        self.assertGreater(cream['rimHalfH'], 0.5)
        # Distinct from placemarker cream deepen dict keys.
        self.assertNotIn('haloPeakAlpha', cream)
        self.assertNotIn('highlight', cream)
        self.assertNotIn('rimPeakAlpha', placemarker_cream)
        self.assertNotIn('localRim', placemarker_cream)

    def test_playground_fog_cream_rim_deepen_params(self):
        """Rim deepen past #236 — juicier rim + hold + rebound (≠ #246)."""
        cream = self._fog_cream()
        placemarker_cream = self._cream()
        crumb_cream = self._crumb_cream()
        # Local rim rebound residual — not birds chirp flecks / fullscreen.
        self.assertTrue(cream['localRim'])
        self.assertTrue(cream['rimRebound'])
        self.assertFalse(cream['birdsChirpFlecks'])
        self.assertFalse(cream['fullscreenWash'])
        # Juicier than original #236 rim peak (0.30) / scale (1.16).
        self.assertGreater(cream['rimPeakAlpha'], 0.30)
        self.assertLess(cream['rimPeakAlpha'], 0.50)
        self.assertGreater(cream['rimMidAlpha'], 0.14)
        self.assertLess(cream['rimMidAlpha'], cream['rimPeakAlpha'])
        self.assertGreater(cream['rimScalePeak'], 1.16)
        self.assertLess(cream['rimScalePeak'], placemarker_cream['haloScalePeak'])
        # Still gentler than crumb pip bloom; wider than crumb pip blot.
        self.assertLess(cream['rimScalePeak'], crumb_cream['pipScalePeak'])
        self.assertGreater(cream['rimHalfW'], crumb_cream['pipHalfW'])
        # Soft mid hold + micro rebound settle (rim deepen signature).
        self.assertGreater(cream['rimHoldSec'], 0.05)
        self.assertLessEqual(cream['rimHoldSec'], 0.20)
        self.assertGreater(cream['rimReboundScale'], 1.0)
        self.assertLess(cream['rimReboundScale'], cream['rimScalePeak'])
        self.assertGreater(cream['rimReboundSec'], 0.04)
        self.assertLessEqual(cream['rimReboundSec'], 0.16)
        self.assertGreater(cream['rimReboundAlpha'], 0.04)
        self.assertLess(cream['rimReboundAlpha'], cream['rimMidAlpha'])
        # Distinct deepen keys — not placemarker halo rim / crumb pip vocabulary.
        self.assertNotIn('rimHoldSec', placemarker_cream)
        self.assertNotIn('rimRebound', placemarker_cream)
        self.assertNotIn('rimReboundScale', crumb_cream)
        self.assertNotIn('birdsChirpFlecks', crumb_cream)
        # Placemarker cream rim deepen also denies birds chirp / fog rim.
        self.assertFalse(placemarker_cream['birdsChirpFlecks'])
        self.assertFalse(placemarker_cream['fogRim'])
        # Fog rim hold is slower than snappier placemarker halo rim deepen.
        self.assertGreater(cream['rimHoldSec'], placemarker_cream['haloHoldSec'])
        self.assertLess(
            cream['rimReboundScale'], placemarker_cream['haloReboundScale'])

    def test_playground_fog_cream_rim_deepen_past_250(self):
        """Past-#250 deepen — brighter/wider rim / longer hold / punchier rebound."""
        cream = self._fog_cream()
        placemarker_cream = self._cream()
        crumb_cream = self._crumb_cream()
        fog = self._fog_pulse()
        # Still local tunnel-lip rim rebound — not tunnel #290 / birds / crumb.
        self.assertTrue(cream['localRim'])
        self.assertTrue(cream['rimRebound'])
        self.assertFalse(cream['birdsChirpFlecks'])
        self.assertFalse(cream['fullscreenWash'])
        self.assertFalse(cream['placemarkerHalo'])
        # Floors past merged #250 fog cream rim deepen knobs.
        self.assertGreater(cream['creamMidSec'], 0.14)
        self.assertLessEqual(cream['creamMidSec'], 0.22)
        self.assertGreater(cream['creamMidAlpha'], fog['restAlpha'])
        self.assertLess(cream['creamMidAlpha'], fog['peakAlpha'])
        self.assertGreater(cream['rimPeakAlpha'], 0.38)
        self.assertLess(cream['rimPeakAlpha'], 0.50)
        self.assertGreater(cream['rimMidAlpha'], 0.20)
        self.assertLess(cream['rimMidAlpha'], cream['rimPeakAlpha'])
        self.assertGreater(cream['rimScalePeak'], 1.22)
        self.assertLess(cream['rimScalePeak'], placemarker_cream['haloScalePeak'])
        self.assertLess(cream['rimScalePeak'], crumb_cream['pipScalePeak'])
        self.assertGreater(cream['rimHalfW'], 3.55)
        self.assertGreater(cream['rimHalfH'], 1.14)
        self.assertGreater(cream['rimHoldSec'], 0.10)
        self.assertLessEqual(cream['rimHoldSec'], 0.20)
        self.assertGreater(cream['rimHoldSec'], placemarker_cream['haloHoldSec'])
        self.assertGreater(cream['rimHoldSec'], crumb_cream['pipHoldSec'])
        self.assertGreater(cream['rimReboundScale'], 1.06)
        self.assertLess(cream['rimReboundScale'], placemarker_cream['haloReboundScale'])
        self.assertLess(cream['rimReboundScale'], crumb_cream['pipReboundScale'])
        self.assertGreater(cream['rimReboundSec'], 0.08)
        self.assertLessEqual(cream['rimReboundSec'], 0.16)
        self.assertGreater(cream['rimReboundSec'], placemarker_cream['haloReboundSec'])
        self.assertGreater(cream['rimReboundSec'], crumb_cream['pipReboundSec'])
        self.assertGreater(cream['rimReboundAlpha'], 0.10)
        self.assertLess(cream['rimReboundAlpha'], cream['rimMidAlpha'])
        # Slightly juicier fog billow past #250; still soft opacity breath.
        self.assertGreater(fog['billow'], 1.12)
        self.assertLess(fog['billow'], 1.25)
        # Distinctness vs placemarker / crumb / birds vocabulary.
        self.assertNotIn('haloHoldSec', cream)
        self.assertNotIn('pipHoldSec', cream)
        self.assertNotIn('rimHoldSec', placemarker_cream)
        self.assertNotIn('rimReboundScale', crumb_cream)

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
