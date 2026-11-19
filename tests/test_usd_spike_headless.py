#!/usr/bin/env python3
"""Headless USD spike gates: fixtures + bridge stub (no Panda / no display).

PR 1 of the OpenUSD adoption plan — ASCII USDA fixtures under
``toontown/usd/fixtures/``, pure-Python parse / bake-plan bridge, and
validate that street overlays require ``tc:packId``. Optional ``pxr``
open is probed but never required for green CI.

Run from repo root:
  python3 -m unittest tests.test_usd_spike_headless -v
  python3 tests/test_usd_spike_headless.py
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from toontown.usd import bridge, validate  # noqa: E402
from toontown.usd.bridge import load_fixture, parse_usda_text  # noqa: E402
from toontown.usd.validate import (  # noqa: E402
    UsdValidationError,
    validate_fixture,
    validate_usda_text,
)

FIXTURES = REPO_ROOT / 'toontown' / 'usd' / 'fixtures'
SMOKE_PROP = 'smoke_prop'
LOOPY_OVERLAY = 'loopy_pack_overlay'

# Ban list mirrors project preference: no Kingdom Hearts branding.
_BANNED = (
    'keyblade',
    'kingdom hearts',
    'kingdomhearts',
    'sora',
    'heartless',
)


class TestUsdSpikeFixtures(unittest.TestCase):
    def test_fixture_files_exist_ascii(self):
        for stem in (SMOKE_PROP, LOOPY_OVERLAY):
            path = FIXTURES / f'{stem}.usda'
            self.assertTrue(path.is_file(), f'missing fixture: {path}')
            text = path.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('#usda'), path.name)
            self.assertNotIn('\x00', text)
            low = text.lower()
            for token in _BANNED:
                self.assertNotIn(token, low, f'{path.name} has banned token')

    def test_smoke_prop_declares_tc_prop(self):
        text = (FIXTURES / f'{SMOKE_PROP}.usda').read_text(encoding='utf-8')
        parsed = parse_usda_text(text)
        self.assertIn('TcProp', parsed['kinds'])
        self.assertEqual(
            parsed['customData'].get('bamPath'),
            'phase_5/models/props/loopy_ink_banner.bam',
        )

    def test_loopy_overlay_declares_street_and_spawn(self):
        text = (FIXTURES / f'{LOOPY_OVERLAY}.usda').read_text(encoding='utf-8')
        parsed = parse_usda_text(text)
        self.assertIn('TcStreetRoot', parsed['kinds'])
        self.assertIn('TcSpawnStand', parsed['kinds'])
        self.assertEqual(parsed['customData'].get('zoneId'), 2200)
        self.assertEqual(parsed['customData'].get('packId'), 'loopy-smudge')


class TestUsdBridgeStub(unittest.TestCase):
    def test_load_fixture_smoke_prop_bake_plan(self):
        plan = load_fixture(SMOKE_PROP)
        self.assertEqual(plan['name'], SMOKE_PROP)
        self.assertEqual(
            plan['bamPath'],
            'phase_5/models/props/loopy_ink_banner.bam',
        )
        # Prop fixture has no street pack / zone — keys still present.
        self.assertIn('zoneId', plan)
        self.assertIn('packId', plan)
        self.assertIsNone(plan['zoneId'])
        self.assertIsNone(plan['packId'])
        self.assertIn('TcProp', plan['kinds'])
        self.assertIn(plan['mode'], ('text', 'pxr'))

    def test_load_fixture_loopy_overlay_bake_plan(self):
        plan = load_fixture(LOOPY_OVERLAY)
        self.assertEqual(plan['bamPath'],
                         'phase_5/models/neighborhoods/loopy_lane_overlay.bam')
        self.assertEqual(plan['zoneId'], 2200)
        self.assertEqual(plan['packId'], 'loopy-smudge')
        self.assertIn('TcStreetRoot', plan['kinds'])
        self.assertIn('TcSpawnStand', plan['kinds'])

    def test_load_fixture_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_fixture('does_not_exist_fixture')

    def test_package_exports(self):
        import toontown.usd as usd_pkg
        self.assertTrue(callable(usd_pkg.load_fixture))
        self.assertTrue(callable(usd_pkg.validate_fixture))


class TestUsdValidate(unittest.TestCase):
    def test_validate_shipped_fixtures_ok(self):
        for stem in (SMOKE_PROP, LOOPY_OVERLAY):
            result = validate_fixture(stem)
            self.assertTrue(result['ok'])

    def test_street_overlay_missing_pack_id_fails(self):
        bad = '''#usda 1.0
def Xform "BrokenStreet" (
    customData = {
        string tc:kind = "TcStreetRoot"
        int tc:zoneId = 2200
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='broken_street')
        self.assertIn('packId', str(ctx.exception))

    def test_banned_kh_token_fails(self):
        bad = '''#usda 1.0
def Xform "Nope" (
    customData = {
        string tc:kind = "TcProp"
        string tc:bamPath = "phase_5/models/props/keyblade.bam"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='kh_ban')
        self.assertIn('banned', str(ctx.exception).lower())


class TestOptionalPxr(unittest.TestCase):
    def test_pxr_optional_does_not_break_without_bindings(self):
        """Text mode always works; pxr enrich only when importable."""
        plan = load_fixture(SMOKE_PROP)
        pxr_spec = importlib.util.find_spec('pxr')
        if pxr_spec is None:
            self.assertEqual(plan['mode'], 'text')
            self.assertNotIn('pxr', plan)
        else:
            # Bindings present — either deeper open succeeded or reported.
            self.assertIn(plan['mode'], ('text', 'pxr'))
            if 'pxr' in plan:
                self.assertIn('pxrOpen', plan['pxr'])


if __name__ == '__main__':
    unittest.main()
