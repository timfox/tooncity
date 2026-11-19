#!/usr/bin/env python3
"""Headless USD SafeZone/Town loader feature-flag hook gates (PR 7).

Default-off. When enabled with a fixture path / street, the hook returns
an overlay dict consumed by ``apply_overlay_metadata`` (pollution seed /
stand list). No Hydra, no hard ``pxr`` dependency, no display.

Run from repo root:
  python3 -m unittest tests.test_usd_runtime_hook_headless -v
  python3 tests/test_usd_runtime_hook_headless.py
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from toontown.usd.runtime_hook import (  # noqa: E402
    RUNTIME_HOOK_NOTES,
    WANT_USD_STREET_OVERLAY,
    ZONE_TO_STREET,
    UsdRuntimeHookError,
    apply_overlay_metadata,
    is_usd_street_overlay_wanted,
    load_street_overlay,
    street_for_zone,
    try_apply_street_overlay,
)

_BANNED = (
    'keyblade',
    'kingdom hearts',
    'kingdomhearts',
    'sora',
    'heartless',
)

TOWN_LOADER = REPO_ROOT / 'toontown' / 'town' / 'TownLoader.py'
SAFEZONE_LOADER = REPO_ROOT / 'toontown' / 'safezone' / 'SafeZoneLoader.py'
RECLAIM_AI = (
    REPO_ROOT / 'toontown' / 'reclaim' / 'DistributedReclaimDirectorAI.py'
)
RUNTIME_HOOK = REPO_ROOT / 'toontown' / 'usd' / 'runtime_hook.py'


def _source_mentions_hook(path: Path) -> str:
    return path.read_text(encoding='utf-8')


class TestFeatureFlagDefaultOff(unittest.TestCase):
    def test_flag_name_and_default(self):
        self.assertEqual(WANT_USD_STREET_OVERLAY, 'want-usd-street-overlay')
        self.assertFalse(is_usd_street_overlay_wanted())
        self.assertFalse(is_usd_street_overlay_wanted(enabled=False))
        self.assertTrue(is_usd_street_overlay_wanted(enabled=True))

    def test_load_returns_none_when_off(self):
        self.assertIsNone(load_street_overlay())
        self.assertIsNone(load_street_overlay(enabled=False, street='loopy_lane'))
        self.assertIsNone(try_apply_street_overlay())
        self.assertIsNone(try_apply_street_overlay(
            enabled=False, street='loopy_lane'))

    def test_apply_none_passthrough(self):
        self.assertIsNone(apply_overlay_metadata(None))
        self.assertIsNone(apply_overlay_metadata({}))


class TestOverlayWhenEnabled(unittest.TestCase):
    def test_loopy_street_overlay_metadata(self):
        overlay = load_street_overlay(enabled=True, street='loopy_lane')
        self.assertIsNotNone(overlay)
        self.assertTrue(overlay['enabled'])
        self.assertEqual(overlay['featureFlag'], WANT_USD_STREET_OVERLAY)
        self.assertFalse(overlay['hydra'])
        self.assertEqual(overlay['mode'], 'text')
        self.assertEqual(overlay['packId'], 'loopy-smudge')
        self.assertEqual(overlay['zoneId'], 2200)
        self.assertAlmostEqual(float(overlay['seedPollution']), 0.55)
        self.assertGreaterEqual(len(overlay['spawnStands']), 1)

        meta = apply_overlay_metadata(overlay)
        self.assertIsNotNone(meta)
        self.assertEqual(meta['zoneId'], 2200)
        self.assertEqual(meta['packId'], 'loopy-smudge')
        self.assertAlmostEqual(meta['seedPollution'], 0.55)
        self.assertFalse(meta['hydra'])
        archetypes = {s['archetype'] for s in meta['spawnStands']}
        self.assertIn('ink', archetypes)
        self.assertEqual(meta['standCount'], len(meta['spawnStands']))

    def test_try_apply_via_zone_id(self):
        self.assertEqual(street_for_zone(2200), 'loopy_lane')
        self.assertEqual(ZONE_TO_STREET[2200], 'loopy_lane')
        meta = try_apply_street_overlay(enabled=True, zone_id=2200)
        self.assertIsNotNone(meta)
        self.assertEqual(meta['packId'], 'loopy-smudge')
        self.assertAlmostEqual(meta['seedPollution'], 0.55)

    def test_try_apply_via_fixture_path(self):
        street_dir = (
            REPO_ROOT / 'toontown' / 'usd' / 'fixtures' / 'streets' / 'loopy_lane'
        )
        meta = try_apply_street_overlay(enabled=True, path=street_dir)
        self.assertIsNotNone(meta)
        self.assertEqual(meta['zoneId'], 2200)
        self.assertGreaterEqual(meta['standCount'], 1)

    def test_enabled_without_source_raises(self):
        with self.assertRaises(UsdRuntimeHookError):
            load_street_overlay(enabled=True)

    def test_notes_declare_no_hydra(self):
        low = RUNTIME_HOOK_NOTES.lower()
        self.assertIn('no hydra', low)
        self.assertIn('metadata', low)
        self.assertIn(WANT_USD_STREET_OVERLAY, RUNTIME_HOOK_NOTES)


class TestNoPxrHardDependency(unittest.TestCase):
    def test_module_source_has_no_hard_pxr_import(self):
        text = RUNTIME_HOOK.read_text(encoding='utf-8')
        tree = ast.parse(text, filename=str(RUNTIME_HOOK))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertFalse(
                        alias.name == 'pxr' or alias.name.startswith('pxr.'),
                        'hard pxr import in runtime_hook',
                    )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ''
                self.assertFalse(
                    mod == 'pxr' or mod.startswith('pxr.'),
                    'hard pxr import in runtime_hook',
                )
        # Optional pxr must never be a top-level requirement.
        self.assertNotIn('from pxr', text)
        self.assertNotIn('import pxr', text)

    def test_banned_tokens_absent(self):
        text = RUNTIME_HOOK.read_text(encoding='utf-8').lower()
        for token in _BANNED:
            self.assertNotIn(token, text)


class TestCallsitesWired(unittest.TestCase):
    """AST / text gates — do not import Panda-heavy loader modules."""

    def test_town_loader_calls_hook(self):
        text = _source_mentions_hook(TOWN_LOADER)
        self.assertIn('want-usd-street-overlay', text)
        self.assertIn('try_apply_street_overlay', text)
        self.assertIn('usdStreetOverlayMeta', text)
        self.assertIn('toontown.usd.runtime_hook', text)

    def test_safezone_loader_calls_hook(self):
        text = _source_mentions_hook(SAFEZONE_LOADER)
        self.assertIn('want-usd-street-overlay', text)
        self.assertIn('try_apply_street_overlay', text)
        self.assertIn('usdStreetOverlayMeta', text)

    def test_reclaim_enter_calls_hook(self):
        text = _source_mentions_hook(RECLAIM_AI)
        self.assertIn('want-usd-street-overlay', text)
        self.assertIn('try_apply_street_overlay', text)
        self.assertIn('usdStreetOverlayMeta', text)
        # Hook lives inside start() reclaim enter path.
        self.assertIn('def start(', text)
        start_idx = text.index('def start(')
        hook_idx = text.index('try_apply_street_overlay', start_idx)
        self.assertGreater(hook_idx, start_idx)


class TestPackageExport(unittest.TestCase):
    def test_package_reexports(self):
        from toontown import usd as usd_pkg
        self.assertTrue(callable(usd_pkg.load_street_overlay))
        self.assertTrue(callable(usd_pkg.apply_overlay_metadata))
        self.assertTrue(callable(usd_pkg.try_apply_street_overlay))
        self.assertIn('load_street_overlay', usd_pkg.__all__)
        self.assertIn('apply_overlay_metadata', usd_pkg.__all__)
        self.assertIn('try_apply_street_overlay', usd_pkg.__all__)


if __name__ == '__main__':
    unittest.main()
