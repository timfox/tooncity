#!/usr/bin/env python3
"""Headless USD Loopy Lane street-pack composition gates (PR 4).

Composed stage resolves ``packId=loopy-smudge``, spawn stands, and reclaim
volume. Root metadata matches ``ReclaimGlobals`` zone ``2200`` / pack id
via pure-Python assert (AST / text of ``STREET_PACKS`` — no panda3d).

Run from repo root:
  python3 -m unittest tests.test_usd_loopy_compose -v
  python3 tests/test_usd_loopy_compose.py
"""

from __future__ import annotations

import ast
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from toontown.usd import compose  # noqa: E402
from toontown.usd.compose import (  # noqa: E402
    UsdComposeError,
    compose_loopy_lane,
    compose_street_pack,
    iter_loopy_layer_texts,
    layer_stack_for,
    loopy_lane_dir,
)
from toontown.usd.validate import validate_usda_text  # noqa: E402

LOOPY_DIR = REPO_ROOT / 'toontown' / 'usd' / 'fixtures' / 'streets' / 'loopy_lane'
RECLAIM_GLOBALS = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
TOONTOWN_GLOBALS = REPO_ROOT / 'toontown' / 'toonbase' / 'ToontownGlobals.py'

_BANNED = (
    'keyblade',
    'kingdom hearts',
    'kingdomhearts',
    'sora',
    'heartless',
)


def _loopy_zone_id_from_globals() -> int:
    """Pure-Python: ``LoopyLane = N`` in ToontownGlobals (no panda import)."""
    text = TOONTOWN_GLOBALS.read_text(encoding='utf-8')
    match = re.search(r'^LoopyLane\s*=\s*(\d+)\s*$', text, re.MULTILINE)
    if not match:
        raise AssertionError('LoopyLane assignment not found in ToontownGlobals')
    return int(match.group(1))


def _loopy_street_pack_from_ast() -> dict:
    """AST-skim ``STREET_PACKS[ToontownGlobals.LoopyLane]`` without importing."""
    tree = ast.parse(
        RECLAIM_GLOBALS.read_text(encoding='utf-8'),
        filename=str(RECLAIM_GLOBALS),
    )
    packs_assign = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'STREET_PACKS':
                    packs_assign = node
                    break
    if packs_assign is None or not isinstance(packs_assign.value, ast.Dict):
        raise AssertionError('STREET_PACKS dict not found in ReclaimGlobals')

    loopy_value = None
    for key, value in zip(packs_assign.value.keys, packs_assign.value.values):
        # Keys are Attribute: ToontownGlobals.LoopyLane
        if (
            isinstance(key, ast.Attribute)
            and key.attr == 'LoopyLane'
            and isinstance(key.value, ast.Name)
            and key.value.id == 'ToontownGlobals'
        ):
            loopy_value = value
            break
    if loopy_value is None or not isinstance(loopy_value, ast.Dict):
        raise AssertionError('LoopyLane entry missing from STREET_PACKS')

    out: dict = {}
    for key, value in zip(loopy_value.keys, loopy_value.values):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            continue
        field = key.value
        if isinstance(value, ast.Constant):
            out[field] = value.value
        elif isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub):
            if isinstance(value.operand, ast.Constant):
                out[field] = -value.operand.value
    return out


class TestLoopyFixturesExist(unittest.TestCase):
    def test_expected_layer_files(self):
        expected = (
            'loopy_lane.usda',
            'packs/loopy_smudge.usda',
            'looks/polluted.usda',
            'looks/pure.usda',
        )
        for rel in expected:
            path = LOOPY_DIR / rel
            self.assertTrue(path.is_file(), f'missing layer: {path}')
            text = path.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('#usda'), rel)
            self.assertNotIn('\x00', text)
            low = text.lower()
            for token in _BANNED:
                self.assertNotIn(token, low, f'{rel} has banned token')

    def test_loopy_dir_helper(self):
        self.assertEqual(loopy_lane_dir(), LOOPY_DIR)

    def test_iter_loopy_layer_texts(self):
        names = [name for name, _ in iter_loopy_layer_texts()]
        self.assertIn('loopy_lane.usda', names)
        self.assertIn('packs/loopy_smudge.usda', names)
        self.assertIn('looks/polluted.usda', names)
        self.assertIn('looks/pure.usda', names)


class TestComposeLoopyLane(unittest.TestCase):
    def test_composed_pack_id_stands_and_volume(self):
        stage = compose_loopy_lane(look='polluted')
        self.assertEqual(stage['packId'], 'loopy-smudge')
        self.assertEqual(stage['zoneId'], 2200)
        self.assertEqual(stage['hood'], 'TT')
        self.assertEqual(stage['street'], 'loopy_lane')
        self.assertEqual(stage['pack'], 'loopy_smudge')
        self.assertEqual(stage['look'], 'polluted')
        self.assertIn('TcStreetRoot', stage['kinds'])
        self.assertIn('TcSpawnStand', stage['kinds'])
        self.assertIn('TcReclaimVolume', stage['kinds'])

        stands = stage['spawnStands']
        self.assertGreaterEqual(len(stands), 2)
        archetypes = [s['archetype'] for s in stands]
        self.assertIn('ink', archetypes)
        self.assertIn('brute', archetypes)
        self.assertEqual(stands[0]['standIndex'], 0)

        volumes = stage['reclaimVolumes']
        self.assertEqual(len(volumes), 1)
        self.assertEqual(volumes[0]['name'], 'ReclaimVolume')
        self.assertEqual(volumes[0]['seedPollution'], 0.55)
        self.assertEqual(stage['seedPollution'], 0.55)

    def test_polluted_look_attached(self):
        stage = compose_loopy_lane(look='polluted')
        look_names = {look['look'] for look in stage['looks']}
        self.assertIn('polluted', look_names)
        self.assertNotIn('pure', look_names)

    def test_pure_look_swap(self):
        stage = compose_loopy_lane(look='pure')
        self.assertEqual(stage['look'], 'pure')
        self.assertEqual(stage['packId'], 'loopy-smudge')
        look_names = {look['look'] for look in stage['looks']}
        self.assertIn('pure', look_names)
        self.assertNotIn('polluted', look_names)

    def test_layer_stack_order(self):
        paths = layer_stack_for('loopy_lane', pack='loopy_smudge', look='polluted')
        names = [p.name for p in paths]
        self.assertEqual(
            names,
            ['loopy_lane.usda', 'loopy_smudge.usda', 'polluted.usda'],
        )
        # Base → pack → look (opinion order).
        self.assertTrue(paths[0].name == 'loopy_lane.usda')
        self.assertEqual(paths[1].parent.name, 'packs')
        self.assertEqual(paths[2].parent.name, 'looks')

    def test_compose_street_pack_alias(self):
        a = compose_loopy_lane()
        b = compose_street_pack('loopy_lane')
        self.assertEqual(a['packId'], b['packId'])
        self.assertEqual(a['zoneId'], b['zoneId'])
        self.assertEqual(
            [s['name'] for s in a['spawnStands']],
            [s['name'] for s in b['spawnStands']],
        )

    def test_missing_look_raises(self):
        with self.assertRaises(UsdComposeError):
            compose_loopy_lane(look='does_not_exist_look')

    def test_package_exports_compose(self):
        import toontown.usd as usd_pkg
        self.assertTrue(callable(usd_pkg.compose_loopy_lane))
        self.assertTrue(callable(getattr(usd_pkg, 'compose_street_pack', None)))


class TestMatchesReclaimGlobals(unittest.TestCase):
    def test_zone_and_pack_match_street_packs(self):
        zone_id = _loopy_zone_id_from_globals()
        self.assertEqual(zone_id, 2200)

        pack = _loopy_street_pack_from_ast()
        self.assertEqual(pack.get('packId'), 'loopy-smudge')
        self.assertEqual(pack.get('seedPollution'), 0.55)

        stage = compose_loopy_lane()
        self.assertEqual(stage['zoneId'], zone_id)
        self.assertEqual(stage['packId'], pack['packId'])
        self.assertEqual(stage['seedPollution'], pack['seedPollution'])


class TestLoopyLayersValidate(unittest.TestCase):
    def test_each_layer_validates(self):
        for rel, text in iter_loopy_layer_texts():
            # Look-only layers have no street root — skip street-pack require.
            require_pack = 'packs/' in rel or rel == 'loopy_lane.usda'
            # Base layer intentionally omits packId (pack overlay supplies it).
            if rel == 'loopy_lane.usda':
                result = validate_usda_text(
                    text,
                    fixture_name=rel,
                    require_street_pack_id=False,
                    require_street_zone_id=True,
                )
            elif rel.startswith('looks/'):
                result = validate_usda_text(
                    text,
                    fixture_name=rel,
                    require_street_pack_id=False,
                    require_street_zone_id=False,
                )
            else:
                result = validate_usda_text(
                    text,
                    fixture_name=rel,
                    require_street_pack_id=require_pack,
                    require_street_zone_id=True,
                )
            self.assertTrue(result['ok'], rel)


class TestComposeModuleSurface(unittest.TestCase):
    def test_compose_module_helpers(self):
        self.assertTrue(callable(compose.compose_loopy_lane))
        self.assertTrue(callable(compose.compose_layers))
        streets = compose.list_street_packs()
        self.assertIn('loopy_lane', streets)


if __name__ == '__main__':
    unittest.main()
