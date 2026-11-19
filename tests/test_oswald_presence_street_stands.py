#!/usr/bin/env python3
"""Headless tests: authored Oswald street presence stands on ACTS zones.

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D.
Locks OSWALD_PRESENCE_STREET_POS coverage for every ACTS zone and
AST-checks OswaldPresence placement prefers authored street stands
(not SPAWN_FORWARD beside the local toon). Hub plaza stays intact.

Run from repo root:
  python3 tests/test_oswald_presence_street_stands.py
  python3 -m unittest tests.test_oswald_presence_street_stands -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

LOOPY = 2200
PUNCHLINE = 2300
SILLY = 2100
TTC = 2000


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_globals():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, REPO_ROOT.as_posix())

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim', 'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = TTC
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

    rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
    rg_spec = importlib.util.spec_from_file_location(
        'toontown.reclaim.ReclaimGlobals', rg_path)
    rg = importlib.util.module_from_spec(rg_spec)
    assert rg_spec.loader is not None
    sys.modules['toontown.reclaim.ReclaimGlobals'] = rg
    rg_spec.loader.exec_module(rg)

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    return camp


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_names(rel: str) -> set[str]:
    tree = ast.parse(_read(rel))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _class_methods(rel: str, class_name: str) -> set[str]:
    tree = ast.parse(_read(rel))
    methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(child.name)
    return methods


def _mirror_street_stand(camp, zoneId):
    """Mirror OswaldPresence.streetStandPos without importing panda."""
    raw_map = getattr(camp, 'OSWALD_PRESENCE_STREET_POS', None) or {}
    raw = raw_map.get(int(zoneId))
    if raw is None:
        return None
    return (float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]))


class OswaldPresenceStreetStandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp = _load_panda_free_globals()

    def test_street_pos_covers_every_acts_zone(self):
        camp = self.camp
        street_pos = camp.OSWALD_PRESENCE_STREET_POS
        self.assertIsInstance(street_pos, dict)
        self.assertGreaterEqual(len(street_pos), 3)
        act_zones = [int(act['zoneId']) for act in camp.ACTS]
        self.assertEqual(set(act_zones), {LOOPY, PUNCHLINE, SILLY})
        seen = set()
        for zid in act_zones:
            self.assertIn(zid, street_pos)
            stand = street_pos[zid]
            self.assertEqual(len(stand), 4)
            self.assertTrue(all(isinstance(v, (int, float)) for v in stand))
            # Distinct landmarks — not the same stand cloned per street.
            key = tuple(float(v) for v in stand)
            self.assertNotIn(key, seen)
            seen.add(key)
        # Hub plaza remains authored and is not a street-map entry.
        hub = camp.OSWALD_PRESENCE_HUB_POS
        self.assertEqual(len(hub), 4)
        self.assertNotIn(int(camp.HUB_ZONE), street_pos)
        self.assertNotEqual(tuple(hub), next(iter(seen)))

    def test_street_stands_are_not_avatar_relative_offsets(self):
        camp = self.camp
        # SPAWN_* remain as unmapped-zone fallback only — stands are absolute.
        self.assertGreater(float(camp.OSWALD_PRESENCE_SPAWN_FORWARD), 0.0)
        self.assertGreater(float(camp.OSWALD_PRESENCE_SPAWN_RIGHT), 0.0)
        for zid in (LOOPY, PUNCHLINE, SILLY):
            stand = _mirror_street_stand(camp, zid)
            self.assertIsNotNone(stand)
            x, y, z, h = stand
            # Absolute world landmark, not a tiny offset-style (0, forward, 0).
            self.assertNotEqual((x, y), (0.0, 0.0))
            self.assertNotEqual(
                (x, y),
                (0.0, float(camp.OSWALD_PRESENCE_SPAWN_FORWARD)))

    def test_presence_module_prefers_street_stands(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        names = _module_names(rel)
        for required in (
                'hubPlazaPos',
                'streetStandPos',
                '_parseStandPos',
                'OswaldPresenceClient'):
            self.assertIn(required, names)
        methods = _class_methods(rel, 'OswaldPresenceClient')
        for required in (
                '_placeBody',
                '_placeBodyAtPlaza',
                '_placeBodyAtStreetStand',
                '_placeBodyAtAuthoredStand',
                '_placeBodyNearAvatar'):
            self.assertIn(required, methods)
        src = _read(rel)
        self.assertIn('OSWALD_PRESENCE_STREET_POS', src)
        self.assertIn('streetStandPos', src)
        self.assertIn('_placeBodyAtStreetStand', src)
        self.assertIn('_placeBodyAtAuthoredStand', src)
        # Placement order: plaza → street stand → near-avatar fallback.
        place_idx = src.index('def _placeBody(')
        plaza_idx = src.index('_placeBodyAtPlaza', place_idx)
        street_idx = src.index('_placeBodyAtStreetStand', place_idx)
        near_idx = src.index('_placeBodyNearAvatar', place_idx)
        self.assertLess(plaza_idx, street_idx)
        self.assertLess(street_idx, near_idx)
        # Hub plaza path preserved.
        self.assertIn('OSWALD_PRESENCE_HUB_POS', src)
        self.assertIn('_placeBodyAtPlaza', src)
        # Stub shippable — not full DNA NPC.
        src_l = src.lower()
        self.assertIn('stub', src_l)
        self.assertIn('full distributednpc', src_l)
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('sora', src_l)
        self.assertNotIn('from toontown.toon', src)
        self.assertNotIn('cream_wash', src_l)

    def test_globals_comment_documents_street_landmarks(self):
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        self.assertIn('OSWALD_PRESENCE_STREET_POS', camp_src)
        self.assertIn('LoopyLane', camp_src[
            camp_src.index('OSWALD_PRESENCE_STREET_POS'):
            camp_src.index('OSWALD_PRESENCE_SPAWN_FORWARD')])
        blob = camp_src[
            camp_src.index('OSWALD_PRESENCE_STREET_POS') - 400:
            camp_src.index('OSWALD_PRESENCE_SPAWN_FORWARD')].lower()
        self.assertIn('landmark', blob)
        self.assertIn('not spawn_forward', blob.replace('-', '_'))
        # Fallback spawn offsets still present for unmapped zones.
        self.assertIn('OSWALD_PRESENCE_SPAWN_FORWARD', camp_src)
        self.assertIn('OSWALD_PRESENCE_SPAWN_RIGHT', camp_src)

    def test_docs_mention_street_stands(self):
        magic = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('acts street', magic)
        self.assertIn('plaza/street stands', magic)
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('authored acts street stands', reclaim)
        self.assertIn('not spawn-forward', reclaim)


if __name__ == '__main__':
    unittest.main()
