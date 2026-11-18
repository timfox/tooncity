#!/usr/bin/env python3
"""Headless smoke: explore → fight → reclaim wiring (no Panda3D / resources).

Asserts STREET_PACKS, campaign ACTS / PlayEntry entry points, and corrupt
archetype registration via AST / direct import of panda-free modules.

Run from repo root:
  python3 tests/test_headless_loop_smoke.py
  python3 -m unittest tests.test_headless_loop_smoke -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Hood street zones (ToontownGlobals) — explore → fight → reclaim path.
EXPECTED_ZONES = {
    'LoopyLane': 2200,
    'PunchlinePlace': 2300,
    'SillyStreet': 2100,
}

EXPECTED_PACK_IDS = {
    2200: 'loopy-smudge',
    2300: 'punchline-sludge',
    2100: 'silly-overlord',
}

EXPECTED_ACT_IDS = ('loopy', 'punchline', 'finale')

# Street archetypes + Ink Overlord finale registration (not a street archetype id).
EXPECTED_ARCHETYPE_NAMES = {
    'Ink Smudge',
    'Sludge Brute',
    'Balloon Snare',
}


def _read(rel: str) -> str:
    path = REPO_ROOT / rel
    return path.read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _const(node: ast.AST):
    if isinstance(node, ast.Constant):
        return node.value
    return None


def _assign_map(tree: ast.AST) -> dict:
    """Top-level Name = Constant assignments."""
    out = {}
    for node in getattr(tree, 'body', []):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name):
            value = _const(node.value)
            if value is not None:
                out[target.id] = value
    return out


def _attr_name(node: ast.AST):
    """ToontownGlobals.LoopyLane → LoopyLane; bare Name → id."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def _dict_literal(node: ast.AST) -> dict:
    """Evaluate a dict of Constant / Name-key → nested Constant/dict/list values."""
    if not isinstance(node, ast.Dict):
        raise AssertionError('expected dict literal, got %s' % type(node).__name__)
    out = {}
    for key_node, val_node in zip(node.keys, node.values):
        key = _const(key_node)
        if key is None:
            key = _attr_name(key_node)
        if key is None:
            continue
        out[key] = _literal(val_node)
    return out


def _literal(node: ast.AST):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Dict):
        return _dict_literal(node)
    if isinstance(node, ast.List) or isinstance(node, ast.Tuple):
        return [_literal(elt) for elt in node.elts]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _const(node.operand)
        if isinstance(inner, (int, float)):
            return -inner
    if isinstance(node, ast.Name):
        # Keep unresolved names as markers (e.g. ToontownGlobals refs elsewhere).
        return {'__name__': node.id}
    if isinstance(node, ast.Attribute):
        return {'__attr__': _attr_name(node) or ast.dump(node)}
    return None


def _toplevel_value(tree: ast.AST, name: str):
    for node in getattr(tree, 'body', []):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == name and node.value is not None:
                return node.value
    raise AssertionError('top-level %r not found' % name)


def _class_and_func_names(tree: ast.AST) -> set:
    names = set()
    for node in getattr(tree, 'body', []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _load_corruption_globals():
    """CorruptionGlobals has no panda deps — import from file path."""
    path = REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
    spec = importlib.util.spec_from_file_location(
        'toontown_corruption_CorruptionGlobals_smoke', path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class HeadlessLoopSmokeTest(unittest.TestCase):
    """Pure-Python wiring checks for the discoverable reclaim loop."""

    @classmethod
    def setUpClass(cls):
        cls.zone_assigns = _assign_map(
            _module_ast('toontown/toonbase/ToontownGlobals.py'))
        cls.reclaim_tree = _module_ast('toontown/reclaim/ReclaimGlobals.py')
        cls.campaign_tree = _module_ast('toontown/campaign/CampaignGlobals.py')
        cls.play_entry_tree = _module_ast('toontown/campaign/PlayEntry.py')
        cls.corruption = _load_corruption_globals()

    def test_zone_ids_loopy_punchline_silly(self):
        for name, zone in EXPECTED_ZONES.items():
            self.assertEqual(
                self.zone_assigns.get(name), zone,
                msg='%s should be zone %s' % (name, zone))

    def test_street_packs_cover_hood_path(self):
        packs_node = _toplevel_value(self.reclaim_tree, 'STREET_PACKS')
        packs_by_attr = _dict_literal(packs_node)
        # Keys are Attribute names (LoopyLane) or resolved ints if ever literal.
        resolved = {}
        for key, pack in packs_by_attr.items():
            if key in EXPECTED_ZONES:
                zone = EXPECTED_ZONES[key]
            elif isinstance(key, int):
                zone = key
            else:
                continue
            self.assertIsInstance(pack, dict)
            resolved[zone] = pack

        for zone, pack_id in EXPECTED_PACK_IDS.items():
            self.assertIn(zone, resolved, msg='STREET_PACKS missing zone %s' % zone)
            pack = resolved[zone]
            self.assertEqual(
                pack.get('packId'), pack_id,
                msg='zone %s packId' % zone)
            self.assertTrue(pack.get('playEntryTip'), msg='zone %s playEntryTip' % zone)

        # Helpers used by PlayEntry / PollutionManagerAI auto-reclaim path.
        helper_names = _class_and_func_names(self.reclaim_tree)
        for helper in (
                'streetPack', 'streetPackId', 'streetPackParams',
                'streetPlayEntryTip'):
            self.assertIn(helper, helper_names)

    def test_campaign_acts_and_play_entry(self):
        acts_node = _toplevel_value(self.campaign_tree, 'ACTS')
        self.assertIsInstance(acts_node, (ast.Tuple, ast.List))
        acts = [_literal(elt) for elt in acts_node.elts]
        self.assertEqual(len(acts), 3)
        act_ids = [a.get('id') for a in acts]
        self.assertEqual(tuple(act_ids), EXPECTED_ACT_IDS)

        zone_by_act = {}
        for act in acts:
            attr = act.get('zoneId')
            # zoneId is stored as {'__attr__': 'LoopyLane'} from AST Attribute.
            if isinstance(attr, dict) and '__attr__' in attr:
                zone_name = attr['__attr__']
                zone_by_act[act['id']] = EXPECTED_ZONES[zone_name]
            elif isinstance(attr, int):
                zone_by_act[act['id']] = attr

        self.assertEqual(zone_by_act.get('loopy'), 2200)
        self.assertEqual(zone_by_act.get('punchline'), 2300)
        self.assertEqual(zone_by_act.get('finale'), 2100)
        self.assertTrue(acts[2].get('finale'))
        self.assertEqual(acts[2].get('corruptName'), 'Ink Overlord')
        self.assertIn('phase2', acts[2])

        play_names = _class_and_func_names(self.play_entry_tree)
        self.assertIn('PlayEntryClient', play_names)
        self.assertIn('ensurePlayEntryClient', play_names)

        # Static read: PlayEntry wires STREET_PACK delays for the three packs.
        play_src = _read('toontown/campaign/PlayEntry.py')
        for pack_id in EXPECTED_PACK_IDS.values():
            self.assertIn(pack_id, play_src)
        self.assertIn('CampaignGlobals.ACTS', play_src)
        self.assertIn('requestStreetEvent', play_src)

    def test_corrupt_archetypes_registered(self):
        cg = self.corruption
        names = set(cg.ARCHETYPE_NAMES.values())
        self.assertTrue(
            EXPECTED_ARCHETYPE_NAMES.issubset(names),
            msg='ARCHETYPE_NAMES missing %s' % (EXPECTED_ARCHETYPE_NAMES - names))

        for archetype_id, expected in (
                (cg.ARCHETYPE_INK, 'Ink Smudge'),
                (cg.ARCHETYPE_BRUTE, 'Sludge Brute'),
                (cg.ARCHETYPE_SNARE, 'Balloon Snare')):
            self.assertEqual(cg.archetypeDefaultName(archetype_id), expected)
            self.assertIn(archetype_id, cg.ARCHETYPE_STATS)

        # Ink Overlord is the Silly finale boss look (phases + crown telegraph),
        # not a street ARCHETYPE_* id — still must be registered here.
        self.assertIn(1, cg.FINALE_PHASE_LOOK)
        self.assertIn(2, cg.FINALE_PHASE_LOOK)
        self.assertEqual(cg.FINALE_PHASE_LOOK[1].get('id'), 'rising')
        self.assertEqual(cg.FINALE_PHASE_LOOK[2].get('id'), 'unleashed')
        self.assertIsNotNone(cg.finalePhaseLook(1))
        self.assertIsNotNone(cg.finalePhaseLook(2))
        self.assertEqual(
            cg.OVERLORD_TELEGRAPH_CROWN_LOOK.get('id'), 'ink-crown')


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HeadlessLoopSmokeTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Allow `python3 tests/test_headless_loop_smoke.py` without package install.
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
