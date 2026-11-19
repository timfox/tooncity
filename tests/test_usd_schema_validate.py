#!/usr/bin/env python3
"""Headless USD schema / prim-convention gates (PR 2).

Validates ``schemas.md`` conventions: LOD names, banned KH tokens,
required ``tc:zoneId`` for street roots, and spawn archetype allow-list
(``ink`` / ``brute`` / ``snare`` / ``gag`` / ``oswald``).

Run from repo root:
  python3 -m unittest tests.test_usd_schema_validate -v
  python3 tests/test_usd_schema_validate.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from toontown.usd.bridge import parse_usda_text  # noqa: E402
from toontown.usd.validate import (  # noqa: E402
    ALLOWED_ARCHETYPES,
    ALLOWED_LOD_NAMES,
    UsdValidationError,
    validate_fixture,
    validate_usda_text,
)

FIXTURES = REPO_ROOT / 'toontown' / 'usd' / 'fixtures'
SCHEMAS_MD = REPO_ROOT / 'toontown' / 'usd' / 'schemas.md'
KITCHEN_SINK = 'schema_kitchen_sink'

_BANNED = (
    'keyblade',
    'kingdom hearts',
    'kingdomhearts',
    'sora',
    'heartless',
)

_EXPECTED_KINDS = (
    'TcStreetRoot',
    'TcReclaimVolume',
    'TcSpawnStand',
    'TcProp',
    'TcCharacterKit',
    'TcLodGroup',
    'TcMaterialLook',
    'TcAnimClip',
    'TcFxSocket',
    'TcCameraShot',
    'TcLightLook',
)


class TestSchemasDoc(unittest.TestCase):
    def test_schemas_md_exists_and_clean(self):
        self.assertTrue(SCHEMAS_MD.is_file(), f'missing {SCHEMAS_MD}')
        text = SCHEMAS_MD.read_text(encoding='utf-8').lower()
        for token in _BANNED:
            self.assertNotIn(token, text, f'schemas.md has banned token')
        for kind in _EXPECTED_KINDS:
            self.assertIn(kind, SCHEMAS_MD.read_text(encoding='utf-8'))
        for lod in ALLOWED_LOD_NAMES:
            self.assertIn(lod, text)
        for arch in ALLOWED_ARCHETYPES:
            self.assertIn(f'`{arch}`', SCHEMAS_MD.read_text(encoding='utf-8'))


class TestKitchenSinkFixture(unittest.TestCase):
    def test_kitchen_sink_ascii_and_kinds(self):
        path = FIXTURES / f'{KITCHEN_SINK}.usda'
        self.assertTrue(path.is_file(), f'missing fixture: {path}')
        text = path.read_text(encoding='utf-8')
        self.assertTrue(text.startswith('#usda'), path.name)
        self.assertNotIn('\x00', text)
        low = text.lower()
        for token in _BANNED:
            self.assertNotIn(token, low)

        parsed = parse_usda_text(text)
        for kind in _EXPECTED_KINDS:
            self.assertIn(kind, parsed['kinds'], f'missing kind {kind}')
        for lod in ALLOWED_LOD_NAMES:
            self.assertIn(lod, parsed['prims'])

        archetypes = {
            r['customData'].get('archetype')
            for r in parsed['primRecords']
            if r.get('kind') == 'TcSpawnStand'
        }
        self.assertEqual(archetypes, set(ALLOWED_ARCHETYPES))

    def test_kitchen_sink_validates(self):
        result = validate_fixture(KITCHEN_SINK)
        self.assertTrue(result['ok'])
        self.assertEqual(result['customData'].get('zoneId'), 2200)
        self.assertEqual(result['customData'].get('packId'), 'loopy-smudge')


class TestStreetZoneId(unittest.TestCase):
    def test_street_root_missing_zone_id_fails(self):
        bad = '''#usda 1.0
def Xform "BrokenStreet" (
    customData = {
        string tc:kind = "TcStreetRoot"
        string tc:packId = "loopy-smudge"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='no_zone')
        self.assertIn('zoneId', str(ctx.exception))

    def test_street_root_missing_pack_id_still_fails(self):
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
            validate_usda_text(bad, fixture_name='no_pack')
        self.assertIn('packId', str(ctx.exception))


class TestArchetypeAllowList(unittest.TestCase):
    def test_unknown_archetype_fails(self):
        bad = '''#usda 1.0
def Xform "Stand" (
    customData = {
        string tc:kind = "TcSpawnStand"
        string tc:archetype = "heartless"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='bad_arch')
        msg = str(ctx.exception).lower()
        # heartless is both banned KH and invalid archetype — either path fails.
        self.assertTrue(
            'banned' in msg or 'allow-list' in msg or 'archetype' in msg
        )

    def test_non_allowlist_archetype_fails(self):
        bad = '''#usda 1.0
def Xform "Stand" (
    customData = {
        string tc:kind = "TcSpawnStand"
        string tc:archetype = "elite"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='elite_arch')
        self.assertIn('allow-list', str(ctx.exception))
        self.assertIn('elite', str(ctx.exception))

    def test_missing_archetype_fails(self):
        bad = '''#usda 1.0
def Xform "Stand" (
    customData = {
        string tc:kind = "TcSpawnStand"
        int tc:standIndex = 0
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='no_arch')
        self.assertIn('archetype', str(ctx.exception))

    def test_each_allowlisted_archetype_ok(self):
        for token in sorted(ALLOWED_ARCHETYPES):
            good = f'''#usda 1.0
def Xform "Stand_{token}" (
    customData = {{
        string tc:kind = "TcSpawnStand"
        string tc:archetype = "{token}"
    }}
)
{{
}}
'''
            result = validate_usda_text(good, fixture_name=f'arch_{token}')
            self.assertTrue(result['ok'], token)


class TestLodNames(unittest.TestCase):
    def test_illegal_lod_name_fails(self):
        bad = '''#usda 1.0
def Xform "LodGroup" (
    customData = {
        string tc:kind = "TcLodGroup"
    }
)
{
    def Xform "lod1000" { }
    def Xform "lod500" { }
    def Xform "lod250" { }
    def Xform "lod125" { }
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='bad_lod')
        self.assertIn('lod125', str(ctx.exception))

    def test_lod_group_missing_band_fails(self):
        bad = '''#usda 1.0
def Xform "LodGroup" (
    customData = {
        string tc:kind = "TcLodGroup"
    }
)
{
    def Xform "lod1000" { }
    def Xform "lod500" { }
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='incomplete_lod')
        self.assertIn('lod250', str(ctx.exception))

    def test_complete_lod_group_ok(self):
        good = '''#usda 1.0
def Xform "LodGroup" (
    customData = {
        string tc:kind = "TcLodGroup"
    }
)
{
    def Xform "lod1000" { }
    def Xform "lod500" { }
    def Xform "lod250" { }
}
'''
        result = validate_usda_text(good, fixture_name='ok_lod')
        self.assertTrue(result['ok'])


class TestBannedKhTokens(unittest.TestCase):
    def test_banned_token_in_prim_path_fails(self):
        bad = '''#usda 1.0
def Xform "KeybladeProp" (
    customData = {
        string tc:kind = "TcProp"
        string tc:bamPath = "phase_5/models/props/banner.bam"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='kh_prim')
        self.assertIn('banned', str(ctx.exception).lower())

    def test_banned_token_in_metadata_fails(self):
        bad = '''#usda 1.0
def Xform "Nope" (
    customData = {
        string tc:kind = "TcProp"
        string tc:bamPath = "phase_5/models/props/sora_banner.bam"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_usda_text(bad, fixture_name='kh_meta')
        self.assertIn('banned', str(ctx.exception).lower())


class TestShippedFixturesStillPass(unittest.TestCase):
    def test_spike_and_kitchen_sink(self):
        for stem in ('smoke_prop', 'loopy_pack_overlay', KITCHEN_SINK):
            result = validate_fixture(stem)
            self.assertTrue(result['ok'], stem)


if __name__ == '__main__':
    unittest.main()
