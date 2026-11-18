#!/usr/bin/env python3
"""Headless smoke: explore → fight → reclaim wiring (no Panda3D / resources).

Asserts STREET_PACKS, campaign ACTS / PlayEntry entry points, corrupt
archetype registration, and recent rubber-hose juice module / symbol
presence via AST / direct import of panda-free modules.

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
    'Gunk Gagster',
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


def _class_method_names(tree: ast.AST, class_name: str) -> set:
    """Method / nested func names defined directly on a top-level class."""
    for node in getattr(tree, 'body', []):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    raise AssertionError('class %r not found' % class_name)


def _toplevel_assign_names(tree: ast.AST) -> set:
    """Names bound by top-level Assign / AnnAssign (any RHS shape)."""
    names = set()
    for node in getattr(tree, 'body', []):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def _assert_module_file(rel: str) -> Path:
    path = REPO_ROOT / rel
    if not path.is_file():
        raise AssertionError('missing module file %s' % rel)
    return path


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
                'streetPlayEntryTip', 'resolveWaveScript',
                'normalizeWaveScriptToken', 'pickPackArchetype'):
            self.assertIn(helper, helper_names)

        # Scripted reclaim waves — each hood pack declares waveScripts.
        for zone, pack in resolved.items():
            scripts = pack.get('waveScripts')
            self.assertTrue(
                scripts,
                msg='zone %s STREET_PACKS missing waveScripts' % zone)
            self.assertGreaterEqual(
                len(scripts), 1,
                msg='zone %s waveScripts empty' % zone)

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
        # Campaign acts carry per-wave scripts (Loopy ramp / Punchline sludge /
        # Silly Overlord swell + P2 unleashed scripts).
        for act in acts:
            self.assertTrue(
                act.get('waveScripts'),
                msg='ACTS %s missing waveScripts' % act.get('id'))
        self.assertTrue(acts[2]['phase2'].get('waveScripts'))

        play_names = _class_and_func_names(self.play_entry_tree)
        self.assertIn('PlayEntryClient', play_names)
        self.assertIn('ensurePlayEntryClient', play_names)
        # Hub tip + soft next-street cue (discoverability without ~startcampaign).
        play_methods = _class_method_names(
            self.play_entry_tree, 'PlayEntryClient')
        self.assertIn('_showHubTip', play_methods)
        self.assertIn('_latchSoftNextCue', play_methods)

        campaign_names = _class_and_func_names(self.campaign_tree)
        self.assertIn('hubPlayEntryTip', campaign_names)
        self.assertIn('handoffTravelHint', campaign_names)
        hub_tip = _toplevel_value(self.campaign_tree, 'HUB_TIP')
        self.assertIsNotNone(hub_tip)
        hub_zone = _toplevel_value(self.campaign_tree, 'HUB_ZONE')
        self.assertIsNotNone(hub_zone)

        # Static read: PlayEntry wires STREET_PACK delays for the three packs.
        play_src = _read('toontown/campaign/PlayEntry.py')
        for pack_id in EXPECTED_PACK_IDS.values():
            self.assertIn(pack_id, play_src)
        self.assertIn('CampaignGlobals.ACTS', play_src)
        self.assertIn('requestStreetEvent', play_src)
        self.assertIn('HUB_ZONE', play_src)
        self.assertIn('_requestCampaign()', play_src)
        self.assertIn('_showHubTip', play_src)
        # Auto path prefers campaign (C) — not street-pack reclaim (R).
        auto_idx = play_src.find('def _autoStartReclaim')
        self.assertGreater(auto_idx, 0)
        auto_snip = play_src[auto_idx:auto_idx + 700]
        self.assertIn('_requestCampaign()', auto_snip)
        self.assertNotIn('_requestReclaim()', auto_snip)

        director_src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('handoffTravelHint', director_src)
        self.assertNotIn('~startcampaign', director_src)

        pollution_src = _read('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('STATE_ACTIVE', pollution_src)
        self.assertIn('startCampaign', pollution_src)
        # Incomplete-reclaim re-creep — contested streets slowly re-ink.
        self.assertIn('markStreetContested', pollution_src)
        self.assertIn('markStreetSecured', pollution_src)
        self.assertIn('markStreetReclaiming', pollution_src)
        self.assertIn('pollutionRecreepStep', pollution_src)

    def test_corrupt_archetypes_registered(self):
        cg = self.corruption
        names = set(cg.ARCHETYPE_NAMES.values())
        self.assertTrue(
            EXPECTED_ARCHETYPE_NAMES.issubset(names),
            msg='ARCHETYPE_NAMES missing %s' % (EXPECTED_ARCHETYPE_NAMES - names))

        for archetype_id, expected in (
                (cg.ARCHETYPE_INK, 'Ink Smudge'),
                (cg.ARCHETYPE_BRUTE, 'Sludge Brute'),
                (cg.ARCHETYPE_SNARE, 'Balloon Snare'),
                (cg.ARCHETYPE_GAGSTER, 'Gunk Gagster')):
            self.assertEqual(cg.archetypeDefaultName(archetype_id), expected)
            self.assertIn(archetype_id, cg.ARCHETYPE_STATS)

        # Gunk Gagster (#191) — distinct gag-lob puddle kit (not Smudge rename).
        gagster = cg.ARCHETYPE_STATS[cg.ARCHETYPE_GAGSTER]
        self.assertEqual(gagster.get('attackMove'), 'gag_lob')
        self.assertEqual(gagster.get('name'), 'Gunk Gagster')
        self.assertGreater(float(gagster.get('meleeRange', 0)), 6.0)
        self.assertGreater(float(gagster.get('attackHitRange', 0)), 0.0)
        # Teal actor tint (R low, G/B higher) — readable vs brown Brute / ink Smudge.
        tint = gagster.get('actorTint')
        self.assertIsInstance(tint, tuple)
        self.assertGreaterEqual(len(tint), 3)
        self.assertLess(float(tint[0]), float(tint[2]))
        self.assertTrue(hasattr(cg, 'GAGSTER_TELEGRAPH_CHARGE_COLOR'))
        self.assertTrue(hasattr(cg, 'GAGSTER_PUDDLE_COLOR'))
        self.assertTrue(hasattr(cg, 'GAGSTER_LOB_ARC_Z'))
        # Gunk Gagster telegraph / puddle warn juice (#197) — teal bounce-pie
        # + cream/ink landing warn so Punchline lob wind-up is readable.
        self.assertTrue(hasattr(cg, 'GAGSTER_TELEGRAPH_PUDDLE_LOOK'))
        puddle_look = cg.GAGSTER_TELEGRAPH_PUDDLE_LOOK
        self.assertEqual(puddle_look.get('id'), 'teal-gag-puddle-warn')
        self.assertIn('puddleInkColor', puddle_look)
        self.assertIn('puddleCreamColor', puddle_look)
        self.assertIn('pieColor', puddle_look)
        self.assertIn('creamFleckCount', puddle_look)
        self.assertIn('puddleHalf', puddle_look)
        self.assertGreater(float(puddle_look.get('puddleHalf', 0)), 0.5)
        self.assertGreater(int(puddle_look.get('creamFleckCount', 0)), 0)
        pie = puddle_look.get('pieColor')
        self.assertIsInstance(pie, tuple)
        self.assertGreaterEqual(len(pie), 3)
        # Teal charge (R low, B high) — distinct from brown Brute spit.
        self.assertLess(float(pie[0]), float(pie[2]))
        self.assertLessEqual(float(puddle_look.get('holdSec', 99)), 0.35)
        gagster_fx_rel = 'toontown/corruption/GagsterPuddleTelegraphFx.py'
        _assert_module_file(gagster_fx_rel)
        gagster_fx_names = _class_and_func_names(_module_ast(gagster_fx_rel))
        self.assertIn('GagsterPuddleTelegraphWarn', gagster_fx_names)
        self.assertIn('gagsterTelegraphPuddleLook', gagster_fx_names)
        gagster_fx_methods = _class_method_names(
            _module_ast(gagster_fx_rel), 'GagsterPuddleTelegraphWarn')
        self.assertIn('play', gagster_fx_methods)
        self.assertIn('clear', gagster_fx_methods)
        self.assertIn('_buildPuddleWarn', gagster_fx_methods)
        self.assertIn('_buildBouncePie', gagster_fx_methods)
        self.assertIn('_buildCreamWarnFlecks', gagster_fx_methods)
        corrupt_src = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('GagsterPuddleTelegraphWarn', corrupt_src)
        self.assertIn('__isGunkGagster', corrupt_src)
        self.assertIn('__playGagsterTelegraphPuddle', corrupt_src)
        self.assertIn('__clearGagsterTelegraphPuddle', corrupt_src)
        # Gunk-only gate on telegraph announce (not Smudge/Brute/Snare).
        self.assertIn('isGagster and not look', corrupt_src)
        self.assertGreater(corrupt_src.count('__clearGagsterTelegraphPuddle'), 2)
        # Gunk Gagster puddle land cream splash aftershock — juicy trap impact.
        self.assertTrue(hasattr(cg, 'GAGSTER_PUDDLE_CREAM_SPLASH_ENABLED'))
        self.assertTrue(hasattr(cg, 'GAGSTER_PUDDLE_CREAM_SPLASH_LOOK'))
        self.assertTrue(hasattr(cg, 'GAGSTER_PUDDLE_CREAM_AFTERSHOCK_ENABLED'))
        self.assertIs(cg.GAGSTER_PUDDLE_CREAM_SPLASH_ENABLED, True)
        self.assertIs(cg.GAGSTER_PUDDLE_CREAM_AFTERSHOCK_ENABLED, True)
        cream_look = cg.GAGSTER_PUDDLE_CREAM_SPLASH_LOOK
        self.assertEqual(cream_look.get('id'), 'gagster-puddle-cream-splash')
        self.assertGreater(int(cream_look.get('fleckCount', 0)), 0)
        cream_look_id = str(cream_look.get('id', '')).lower()
        self.assertNotIn('keyblade', cream_look_id)
        self.assertNotIn('kingdom hearts', cream_look_id)
        cream_fx_rel = 'toontown/corruption/GagsterPuddleCreamSplashFx.py'
        _assert_module_file(cream_fx_rel)
        cream_fx_names = _class_and_func_names(_module_ast(cream_fx_rel))
        self.assertIn('GagsterPuddleCreamSplash', cream_fx_names)
        self.assertIn('gagsterPuddleCreamSplashLook', cream_fx_names)
        cream_fx_methods = _class_method_names(
            _module_ast(cream_fx_rel), 'GagsterPuddleCreamSplash')
        self.assertIn('play', cream_fx_methods)
        self.assertIn('clear', cream_fx_methods)
        self.assertIn('_buildAftershock', cream_fx_methods)
        self.assertIn('GagsterPuddleCreamSplash', corrupt_src)
        self.assertIn('__playGagsterPuddleCreamSplash', corrupt_src)
        self.assertIn('__clearGagsterPuddleCreamSplash', corrupt_src)
        self.assertIn('__playGagsterPuddleCreamSplash(landPos)', corrupt_src)
        self.assertGreater(corrupt_src.count('__clearGagsterPuddleCreamSplash'), 2)
        reclaim_md = _read('toontown/corruption/RECLAIM.md')
        self.assertIn('GagsterPuddleCreamSplashFx', reclaim_md)
        corr_init = _read('toontown/corruption/__init__.py')
        self.assertIn('GagsterPuddleCreamSplashFx', corr_init)
        # Sludge Brute spit land cream splash aftershock — juicy green spit impact.
        self.assertTrue(hasattr(cg, 'BRUTE_SPIT_CREAM_SPLASH_ENABLED'))
        self.assertTrue(hasattr(cg, 'BRUTE_SPIT_CREAM_SPLASH_LOOK'))
        self.assertTrue(hasattr(cg, 'BRUTE_SPIT_CREAM_AFTERSHOCK_ENABLED'))
        self.assertIs(cg.BRUTE_SPIT_CREAM_SPLASH_ENABLED, True)
        self.assertIs(cg.BRUTE_SPIT_CREAM_AFTERSHOCK_ENABLED, True)
        brute_cream_look = cg.BRUTE_SPIT_CREAM_SPLASH_LOOK
        self.assertEqual(brute_cream_look.get('id'), 'brute-spit-cream-splash')
        self.assertGreater(int(brute_cream_look.get('fleckCount', 0)), 0)
        brute_cream_id = str(brute_cream_look.get('id', '')).lower()
        self.assertNotIn('keyblade', brute_cream_id)
        self.assertNotIn('kingdom hearts', brute_cream_id)
        brute_cream_fx_rel = 'toontown/corruption/BruteSpitCreamSplashFx.py'
        _assert_module_file(brute_cream_fx_rel)
        brute_cream_fx_names = _class_and_func_names(_module_ast(brute_cream_fx_rel))
        self.assertIn('BruteSpitCreamSplash', brute_cream_fx_names)
        self.assertIn('bruteSpitCreamSplashLook', brute_cream_fx_names)
        brute_cream_fx_methods = _class_method_names(
            _module_ast(brute_cream_fx_rel), 'BruteSpitCreamSplash')
        self.assertIn('play', brute_cream_fx_methods)
        self.assertIn('clear', brute_cream_fx_methods)
        self.assertIn('_buildAftershock', brute_cream_fx_methods)
        self.assertIn('BruteSpitCreamSplash', corrupt_src)
        self.assertIn('__playBruteSpitCreamSplash', corrupt_src)
        self.assertIn('__clearBruteSpitCreamSplash', corrupt_src)
        self.assertIn('__playBruteSpitCreamSplash(end)', corrupt_src)
        self.assertGreater(corrupt_src.count('__clearBruteSpitCreamSplash'), 2)
        self.assertIn('BruteSpitCreamSplashFx', reclaim_md)
        self.assertIn('BruteSpitCreamSplashFx', corr_init)
        ai_src = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn('gag_lob', ai_src)
        self.assertIn('__resolveGagsterPuddle', ai_src)
        self.assertIn('_puddleXY', ai_src)
        magic_src = _read('toontown/corruption/MagicWords.py')
        self.assertIn('spawngagster', magic_src)
        self.assertIn('ARCHETYPE_GAGSTER', magic_src)

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
        # Phase combat AI (beyond Smudge chase) must stay registered beside looks.
        self.assertIn(1, cg.OVERLORD_PHASE_COMBAT)
        self.assertIn(2, cg.OVERLORD_PHASE_COMBAT)
        self.assertEqual(cg.OVERLORD_PHASE_COMBAT[1].get('moveMode'), 'rain')
        self.assertEqual(cg.OVERLORD_PHASE_COMBAT[2].get('moveMode'), 'enrage')
        self.assertIsNotNone(cg.overlordPhaseCombat(1))
        self.assertIsNotNone(cg.overlordPhaseCombat(2))
        self.assertEqual(cg.overlordP2AddCount(1), 0)
        self.assertGreater(cg.overlordP2AddCount(2), 0)

    def test_rubber_hose_juice_modules_present(self):
        """AST-assert recent juice modules / symbols without importing Panda."""
        # --- hackslash: hit-stop / soft-lock reticle / dodge trail + FOV ---
        hack_modules = {
            'toontown/hackslash/HitStopFx.py': {'HitStopFx'},
            'toontown/hackslash/SoftLockReticleFx.py': {'SoftLockReticleFx'},
            'toontown/hackslash/DodgeTrailFx.py': {'DodgeTrailFx'},
            'toontown/hackslash/DodgePerfectFx.py': {'DodgePerfectFx'},
        }
        for rel, expected in hack_modules.items():
            _assert_module_file(rel)
            names = _class_and_func_names(_module_ast(rel))
            missing = expected - names
            self.assertFalse(
                missing, msg='%s missing symbols %s' % (rel, missing))

        config_tree = _module_ast('toontown/hackslash/HackSlashConfig.py')
        config_names = _toplevel_assign_names(config_tree)
        for tunable in (
                'SOFT_LOCK_FOV_ENABLED',
                'SOFT_LOCK_FOV_PUNCH',
                'SOFT_LOCK_FOV_IN_SEC',
                'SOFT_LOCK_FOV_OUT_SEC'):
            self.assertIn(
                tunable, config_names,
                msg='HackSlashConfig missing soft-lock FOV tunable %s' % tunable)

        # Soft-lock cream pulse ring on acquire (#92).
        for tunable in (
                'SOFT_LOCK_PULSE_RING_ENABLED',
                'SOFT_LOCK_PULSE_RING_HALF',
                'SOFT_LOCK_PULSE_RING_START',
                'SOFT_LOCK_PULSE_RING_PEAK',
                'SOFT_LOCK_PULSE_RING_SEC',
                'SOFT_LOCK_PULSE_RING_COLOR',
                'SOFT_LOCK_PULSE_RING_END',
                'SOFT_LOCK_PULSE_RING_BIN'):
            self.assertIn(
                tunable, config_names,
                msg='HackSlashConfig missing soft-lock pulse ring %s' % tunable)

        reticle_tree = _module_ast('toontown/hackslash/SoftLockReticleFx.py')
        reticle_methods = _class_method_names(reticle_tree, 'SoftLockReticleFx')
        self.assertIn('_playPulseRing', reticle_methods)

        # Perfect-dodge cream star aftershock (#89).
        for tunable in (
                'PERFECT_DODGE_CREAM_AFTERSHOCK_ENABLED',
                'PERFECT_DODGE_CREAM_AFTERSHOCK_DELAY_SEC',
                'PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_COUNT',
                'PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_COLOR',
                'PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_ENABLED',
                'PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                tunable, config_names,
                msg='HackSlashConfig missing perfect-dodge aftershock %s' % tunable)

        dodge_perfect_tree = _module_ast('toontown/hackslash/DodgePerfectFx.py')
        dodge_perfect_methods = _class_method_names(
            dodge_perfect_tree, 'DodgePerfectFx')
        self.assertIn('_buildAftershock', dodge_perfect_methods)
        self.assertIn('play', dodge_perfect_methods)

        melee_src = _read('toontown/hackslash/MeleeCombat.py')
        self.assertIn('DodgePerfectFx', melee_src)
        self.assertIn('self._dodgePerfect', melee_src)

        # Melee hit cream spark aftershock (#96) — delayed residual on HitSparkFx.
        _assert_module_file('toontown/hackslash/HitSparkFx.py')
        hit_spark_tree = _module_ast('toontown/hackslash/HitSparkFx.py')
        hit_spark_names = _class_and_func_names(hit_spark_tree)
        self.assertIn('HitSparkFx', hit_spark_names)
        hit_spark_methods = _class_method_names(hit_spark_tree, 'HitSparkFx')
        self.assertIn('play', hit_spark_methods)
        self.assertIn('_buildAftershock', hit_spark_methods)
        self.assertIn('_spawnAftershockHalo', hit_spark_methods)
        self.assertIn('_spawnAftershockSpark', hit_spark_methods)
        for tunable in (
                'HIT_SPARK_CREAM_AFTERSHOCK_ENABLED',
                'HIT_SPARK_CREAM_AFTERSHOCK_DELAY_SEC',
                'HIT_SPARK_CREAM_AFTERSHOCK_COUNT',
                'HIT_SPARK_CREAM_AFTERSHOCK_COLOR',
                'HIT_SPARK_CREAM_AFTERSHOCK_HALO_ENABLED',
                'HIT_SPARK_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                tunable, config_names,
                msg='HackSlashConfig missing hit-spark aftershock %s' % tunable)
        self.assertIn('HitSparkFx', melee_src)
        self.assertIn('self._hitSpark', melee_src)

        # Re-exports keep client import paths stable.
        hack_init = _read('toontown/hackslash/__init__.py')
        for symbol in (
                'HitStopFx', 'SoftLockReticleFx', 'DodgeTrailFx',
                'DodgePerfectFx', 'HitSparkFx'):
            self.assertIn(symbol, hack_init)

        # --- reclaim: street wash + wave-clear cream burst + purity shimmer ---
        _assert_module_file('toontown/reclaim/StreetColorWash.py')
        wash_names = _class_and_func_names(
            _module_ast('toontown/reclaim/StreetColorWash.py'))
        self.assertIn('StreetColorWash', wash_names)

        _assert_module_file('toontown/reclaim/WaveCreamBurstFx.py')
        cream_names = _class_and_func_names(
            _module_ast('toontown/reclaim/WaveCreamBurstFx.py'))
        self.assertIn('WaveCreamBurstFxClient', cream_names)
        self.assertIn('ensureWaveCreamBurstFxClient', cream_names)

        reclaim_names = _toplevel_assign_names(self.reclaim_tree)
        for cream_key in (
                'WAVE_CLEAR_CREAM_ENABLED',
                'WAVE_CLEAR_CREAM_FLASH_PEAK',
                'WAVE_CLEAR_CREAM_COLOR',
                'WAVE_CLEAR_CREAM_FLECK_COUNT',
                'WAVE_CLEAR_CREAM_BIN'):
            self.assertIn(
                cream_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % cream_key)

        # Purity meter fill cream shimmer (#90).
        _assert_module_file('toontown/reclaim/PurityMeterHud.py')
        purity_tree = _module_ast('toontown/reclaim/PurityMeterHud.py')
        purity_names = _class_and_func_names(purity_tree)
        self.assertIn('PurityMeterHud', purity_names)
        purity_methods = _class_method_names(purity_tree, 'PurityMeterHud')
        self.assertIn('_spawnFillShimmerFlecks', purity_methods)
        for shimmer_key in (
                'PURITY_METER_FILL_SHIMMER_ENABLED',
                'PURITY_METER_FILL_SHIMMER_COUNT',
                'PURITY_METER_FILL_SHIMMER_SIZE',
                'PURITY_METER_FILL_SHIMMER_COLOR',
                'PURITY_METER_FILL_SHIMMER_END_COLOR',
                'PURITY_METER_FILL_SHIMMER_BIN'):
            self.assertIn(
                shimmer_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % shimmer_key)

        # Wave-clear cream shimmer hang (#93) — delayed residual after burst.
        shimmer_rel = 'toontown/reclaim/WaveClearCreamShimmerFx.py'
        _assert_module_file(shimmer_rel)
        wave_shimmer_names = _class_and_func_names(_module_ast(shimmer_rel))
        self.assertIn('WaveClearCreamShimmerFxClient', wave_shimmer_names)
        self.assertIn('ensureWaveClearCreamShimmerFxClient', wave_shimmer_names)
        wave_shimmer_methods = _class_method_names(
            _module_ast(shimmer_rel), 'WaveClearCreamShimmerFxClient')
        self.assertIn('_spawnShimmer', wave_shimmer_methods)
        self.assertIn('_spawnFlecks', wave_shimmer_methods)
        for shimmer_hang_key in (
                'WAVE_CLEAR_CREAM_SHIMMER_ENABLED',
                'WAVE_CLEAR_CREAM_SHIMMER_DELAY_SEC',
                'WAVE_CLEAR_CREAM_SHIMMER_COLOR',
                'WAVE_CLEAR_CREAM_SHIMMER_BIN',
                'WAVE_CLEAR_CREAM_SHIMMER_FLECK_COUNT',
                'WAVE_CLEAR_CREAM_SHIMMER_FLECK_COLOR'):
            self.assertIn(
                shimmer_hang_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % shimmer_hang_key)
        director_src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('ensureWaveClearCreamShimmerFxClient', director_src)

        # --- corruption: idle ink drip + overlord phase ink rain + magenta splash ---
        _assert_module_file('toontown/corruption/IdleInkDripFx.py')
        idle_names = _class_and_func_names(
            _module_ast('toontown/corruption/IdleInkDripFx.py'))
        self.assertIn('IdleInkDrip', idle_names)
        self.assertIn('idleInkLook', idle_names)

        _assert_module_file('toontown/corruption/OverlordPhaseInkRainFx.py')
        rain_names = _class_and_func_names(
            _module_ast('toontown/corruption/OverlordPhaseInkRainFx.py'))
        self.assertIn('OverlordPhaseInkRain', rain_names)
        self.assertIn('overlordInkRainLook', rain_names)

        # Overlord magenta ink splash on hit/death (#88).
        splash_rel = 'toontown/corruption/OverlordMagentaInkSplashFx.py'
        _assert_module_file(splash_rel)
        splash_names = _class_and_func_names(_module_ast(splash_rel))
        self.assertIn('OverlordMagentaInkSplash', splash_names)
        self.assertIn('overlordMagentaInkSplashLook', splash_names)

        cg = self.corruption
        self.assertTrue(
            hasattr(cg, 'OVERLORD_PHASE_INK_RAIN_LOOK'),
            msg='CorruptionGlobals missing OVERLORD_PHASE_INK_RAIN_LOOK')
        self.assertEqual(
            cg.OVERLORD_PHASE_INK_RAIN_LOOK.get('id'), 'ink-rain')
        self.assertTrue(
            hasattr(cg, 'IDLE_INK_DRIP_LOOK'),
            msg='CorruptionGlobals missing IDLE_INK_DRIP_LOOK')
        self.assertTrue(
            hasattr(cg, 'OVERLORD_MAGENTA_INK_SPLASH_LOOK'),
            msg='CorruptionGlobals missing OVERLORD_MAGENTA_INK_SPLASH_LOOK')
        splash_look = cg.OVERLORD_MAGENTA_INK_SPLASH_LOOK
        self.assertIn('hit', splash_look)
        self.assertIn('death', splash_look)
        self.assertEqual(splash_look['hit'].get('id'), 'overlord-hit-splash')
        self.assertEqual(splash_look['death'].get('id'), 'overlord-death-splash')

        corrupt_src = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('OverlordMagentaInkSplash', corrupt_src)
        self.assertIn('__playOverlordMagentaInkSplash', corrupt_src)

        # Corrupt death cream flecks (#94) — cream/pastel layer on death pop.
        fleck_rel = 'toontown/corruption/CorruptDeathCreamFleckFx.py'
        _assert_module_file(fleck_rel)
        fleck_names = _class_and_func_names(_module_ast(fleck_rel))
        self.assertIn('DeathCreamFleckBurst', fleck_names)
        self.assertIn('deathCreamFleckLook', fleck_names)
        fleck_methods = _class_method_names(
            _module_ast(fleck_rel), 'DeathCreamFleckBurst')
        self.assertIn('play', fleck_methods)
        self.assertIn('_spawnFleck', fleck_methods)
        self.assertTrue(
            hasattr(cg, 'DEATH_CREAM_FLECK_LOOK'),
            msg='CorruptionGlobals missing DEATH_CREAM_FLECK_LOOK')
        self.assertEqual(
            cg.DEATH_CREAM_FLECK_LOOK.get('id'), 'death-cream-fleck')
        self.assertTrue(
            hasattr(cg, 'DEATH_CREAM_FLECK_ENABLED'),
            msg='CorruptionGlobals missing DEATH_CREAM_FLECK_ENABLED')
        death_pop_src = _read('toontown/corruption/CorruptDeathPopFx.py')
        self.assertIn('DeathCreamFleckBurst', death_pop_src)
        self.assertIn('CorruptDeathCreamFleckFx', death_pop_src)

        # --- campaign: Punchline Act 2 tip hose pop (#91) ---
        campaign_names = _toplevel_assign_names(self.campaign_tree)
        for tip_key in (
                'PUNCHLINE_ACT_TIP_POP_SQUASH',
                'PUNCHLINE_ACT_TIP_POP_STRETCH',
                'PUNCHLINE_ACT_TIP_POP_SETTLE_SEC',
                'PUNCHLINE_ACT_TIP_TRUST_SETTLE_OVERSHOOT',
                'PUNCHLINE_ACT_TIP_TRUST_SETTLE_REST_SEC'):
            self.assertIn(
                tip_key, campaign_names,
                msg='CampaignGlobals missing %s' % tip_key)

        acts_node = _toplevel_value(self.campaign_tree, 'ACTS')
        acts = [_literal(elt) for elt in acts_node.elts]
        punchline = next(a for a in acts if a.get('id') == 'punchline')
        entry_tip = punchline.get('entryTip') or ''
        self.assertIn('Gunk Gagsters', entry_tip)
        self.assertIn('Sludge Brutes', entry_tip)
        self.assertIn('Balloon Snares', entry_tip)
        self.assertIn('Oswald', entry_tip)

        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('PUNCHLINE_ACT_TIP_POP_SQUASH', play_src)
        self.assertIn('_tipHosePopInterval', play_src)
        self.assertIn('playEntryTipHosePop', play_src)

        # Silly Act 3 tip hose pop (#95) — Oswald trusted lead + Ink Overlord.
        for silly_tip_key in (
                'SILLY_ACT_TIP_POP_SQUASH',
                'SILLY_ACT_TIP_POP_STRETCH',
                'SILLY_ACT_TIP_POP_SETTLE_SEC',
                'SILLY_ACT_TIP_TRUST_SETTLE_OVERSHOOT',
                'SILLY_ACT_TIP_TRUST_SETTLE_REST_SEC'):
            self.assertIn(
                silly_tip_key, campaign_names,
                msg='CampaignGlobals missing %s' % silly_tip_key)
        finale = next(a for a in acts if a.get('id') == 'finale')
        finale_tip = finale.get('entryTip') or ''
        self.assertIn('Oswald', finale_tip)
        self.assertIn('Ink Overlord', finale_tip)
        self.assertIn('Silly Street', finale_tip)
        self.assertIn('SILLY_ACT_TIP_POP_SQUASH', play_src)
        self.assertIn('SILLY_ACT_TIP_TRUST_SETTLE_OVERSHOOT', play_src)
        # Silly mid-act almost-confess approach tip (before finale reveal).
        approach_tip = finale.get('approachTip') or ''
        if isinstance(approach_tip, list):
            approach_tip = ''.join(str(part) for part in approach_tip)
        approach_l = str(approach_tip).lower()
        self.assertIn('almost confess', approach_l)
        self.assertIn('gag went wrong', approach_l)
        self.assertTrue(finale.get('entryTipUnease'))
        self.assertFalse(bool(finale.get('trustFracture')))
        self.assertIn('SILLY_APPROACH_TIP_DELAY_SEC', campaign_names)
        self.assertIn('_armSillyApproachTip', play_src)
        self.assertIn('_showSillyApproachTip', play_src)
        for banned in (
                'keyblade', 'kingdom hearts', 'caused the corruption', 'sora'):
            self.assertNotIn(banned, approach_l)
            self.assertNotIn(banned, str(finale_tip).lower())

        # Reclaim cheer cream sparkle flecks (#98) — mid-screen flecks with pitch swell.
        cheer_sparkle_rel = 'toontown/reclaim/CheerCreamSparkleFx.py'
        _assert_module_file(cheer_sparkle_rel)
        cheer_sparkle_names = _class_and_func_names(_module_ast(cheer_sparkle_rel))
        self.assertIn('CheerCreamSparkleFxClient', cheer_sparkle_names)
        self.assertIn('ensureCheerCreamSparkleFxClient', cheer_sparkle_names)
        cheer_sparkle_methods = _class_method_names(
            _module_ast(cheer_sparkle_rel), 'CheerCreamSparkleFxClient')
        self.assertIn('playSparkle', cheer_sparkle_methods)
        self.assertIn('_spawnFlecks', cheer_sparkle_methods)
        for cheer_key in (
                'CHEER_CREAM_SPARKLE_ENABLED',
                'CHEER_CREAM_SPARKLE_COUNT',
                'CHEER_CREAM_SPARKLE_COUNT_WAVE',
                'CHEER_CREAM_SPARKLE_COLOR',
                'CHEER_CREAM_SPARKLE_END_COLOR',
                'CHEER_CREAM_SPARKLE_BIN'):
            self.assertIn(
                cheer_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % cheer_key)
        cheer_src = _read('toontown/reclaim/ReclaimCheer.py')
        self.assertIn('ensureCheerCreamSparkleFxClient', cheer_src)
        self.assertIn('CheerCreamSparkleFx', cheer_src)
        self.assertIn('CheerCreamSparkleFx', director_src)

        # Campaign handoff cream sparkle flecks (#99) — glitter on carnival confetti.
        for handoff_key in (
                'HANDOFF_CREAM_SPARKLE_ENABLED',
                'HANDOFF_CREAM_SPARKLE_COUNT',
                'HANDOFF_CREAM_SPARKLE_STREAK_COUNT',
                'HANDOFF_CREAM_SPARKLE_COLORS',
                'HANDOFF_CREAM_SPARKLE_BIN'):
            self.assertIn(
                handoff_key, campaign_names,
                msg='CampaignGlobals missing %s' % handoff_key)
        confetti_rel = 'toontown/campaign/CampaignHandoffConfetti.py'
        _assert_module_file(confetti_rel)
        confetti_names = _class_and_func_names(_module_ast(confetti_rel))
        self.assertIn('HandoffConfettiPop', confetti_names)
        confetti_methods = _class_method_names(
            _module_ast(confetti_rel), 'HandoffConfettiPop')
        self.assertIn('_spawnCreamSparkle', confetti_methods)
        confetti_src = _read(confetti_rel)
        self.assertIn('HANDOFF_CREAM_SPARKLE_ENABLED', confetti_src)

        # Pollution fog cream dissolve (#100) — cream veil + flecks on purity clear.
        fog_rel = 'toontown/corruption/PollutionFogCreamDissolveFx.py'
        _assert_module_file(fog_rel)
        fog_names = _class_and_func_names(_module_ast(fog_rel))
        self.assertIn('PollutionFogCreamDissolveFx', fog_names)
        fog_methods = _class_method_names(
            _module_ast(fog_rel), 'PollutionFogCreamDissolveFx')
        self.assertIn('playDissolve', fog_methods)
        self.assertIn('_spawnShimmer', fog_methods)
        self.assertIn('_spawnFlecks', fog_methods)
        for fog_key in (
                'FOG_CREAM_DISSOLVE_ENABLED',
                'FOG_CREAM_DISSOLVE_SEC',
                'FOG_CREAM_DISSOLVE_COLOR',
                'FOG_CREAM_DISSOLVE_FLECK_COUNT',
                'FOG_CREAM_DISSOLVE_FLECK_COLOR',
                'FOG_CREAM_DISSOLVE_BIN'):
            self.assertTrue(
                hasattr(cg, fog_key),
                msg='CorruptionGlobals missing %s' % fog_key)
        self.assertTrue(
            hasattr(cg, 'hoodFogCreamDissolveColor'),
            msg='CorruptionGlobals missing hoodFogCreamDissolveColor')
        pollution_src = _read('toontown/corruption/PollutionManager.py')
        self.assertIn('PollutionFogCreamDissolveFx', pollution_src)
        self.assertIn('beginCreamDissolve', pollution_src)
        self.assertIn('setCreamDissolveBlend', pollution_src)

        # Incomplete-reclaim re-creep (#194) — pure stays pure; contested
        # residual ink slowly re-inks toward cap (not full blackout).
        for recreep_key in (
                'STREET_SECURED',
                'STREET_RECLAIMING',
                'STREET_CONTESTED',
                'POLLUTION_RECREEP_ENABLED',
                'POLLUTION_RECREEP_TICK_SEC',
                'POLLUTION_RECREEP_PER_TICK',
                'POLLUTION_RECREEP_CAP',
                'POLLUTION_RECREEP_MSG'):
            self.assertTrue(
                hasattr(cg, recreep_key),
                msg='CorruptionGlobals missing %s' % recreep_key)
        self.assertTrue(
            hasattr(cg, 'pollutionRecreepStep'),
            msg='CorruptionGlobals missing pollutionRecreepStep')
        self.assertTrue(
            hasattr(cg, 'streetAllowsRecreep'),
            msg='CorruptionGlobals missing streetAllowsRecreep')
        # Value lock (#194): enabled seep, 2.5s tick, +0.04/tick, cap 0.85.
        self.assertIs(cg.POLLUTION_RECREEP_ENABLED, True)
        self.assertAlmostEqual(cg.POLLUTION_RECREEP_TICK_SEC, 2.5, places=2)
        self.assertAlmostEqual(cg.POLLUTION_RECREEP_PER_TICK, 0.04, places=3)
        self.assertAlmostEqual(cg.POLLUTION_RECREEP_CAP, 0.85, places=2)
        self.assertLess(cg.POLLUTION_RECREEP_CAP, 1.0)
        self.assertFalse(cg.streetAllowsRecreep(cg.STREET_SECURED))
        self.assertFalse(cg.streetAllowsRecreep(cg.STREET_RECLAIMING))
        self.assertTrue(cg.streetAllowsRecreep(cg.STREET_CONTESTED))
        self.assertEqual(cg.pollutionRecreepStep(0.0), cg.POLLUTION_PURE)
        self.assertGreater(cg.pollutionRecreepStep(0.3), 0.3)
        self.assertAlmostEqual(cg.pollutionRecreepStep(0.40), 0.44, places=5)
        recreep_msg = str(cg.POLLUTION_RECREEP_MSG).lower()
        self.assertIn('ink', recreep_msg)
        self.assertIn('reclaim', recreep_msg)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, recreep_msg)
        pollution_ai_methods = _class_method_names(
            _module_ast('toontown/corruption/PollutionManagerAI.py'),
            'PollutionManagerAI')
        for recreep_method in (
                'markStreetSecured',
                'markStreetReclaiming',
                'markStreetContested',
                'isPurityLocked',
                '_ensureRecreepTask',
                '__recreepTick',
                '_announceRecreep'):
            self.assertIn(
                recreep_method, pollution_ai_methods,
                msg='PollutionManagerAI missing %s' % recreep_method)
        pollution_ai_src = _read(
            'toontown/corruption/PollutionManagerAI.py')
        self.assertIn('pollutionRecreeping', pollution_ai_src)
        self.assertIn('POLLUTION_RECREEP_MSG', pollution_ai_src)
        self.assertIn('_purityLocked', pollution_ai_src)
        self.assertIn('streetPurityLockBlocksRise', pollution_ai_src)
        self.assertTrue(
            hasattr(cg, 'STREET_PURITY_LOCK_ENABLED'),
            msg='CorruptionGlobals missing STREET_PURITY_LOCK_ENABLED')
        self.assertTrue(
            hasattr(cg, 'streetPurityLockBlocksRise'),
            msg='CorruptionGlobals missing streetPurityLockBlocksRise')
        self.assertIs(cg.STREET_PURITY_LOCK_ENABLED, True)
        self.assertTrue(cg.streetPurityLockBlocksRise(True, 0.5, 0.0))
        self.assertFalse(cg.streetPurityLockBlocksRise(False, 0.5, 0.0))
        director_ai_src = _read(
            'toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('markStreetContested', director_ai_src)
        self.assertIn('markStreetSecured', director_ai_src)
        self.assertIn('markStreetReclaiming', director_ai_src)
        # Contested only on ACTIVE bail-out; complete secures (no re-creep).
        stop_idx = director_ai_src.find('def stop(self):')
        complete_idx = director_ai_src.find('def __complete(self):')
        self.assertGreater(stop_idx, 0)
        self.assertGreater(complete_idx, 0)
        stop_snip = director_ai_src[stop_idx:complete_idx]
        self.assertIn('markStreetContested', stop_snip)
        self.assertIn('wasActive', stop_snip)
        complete_snip = director_ai_src[complete_idx:complete_idx + 900]
        self.assertIn('markStreetSecured', complete_snip)
        self.assertNotIn('markStreetContested', complete_snip)
        # Unlock purity lock before seeding so finished streets can restart.
        start_idx = director_ai_src.find('def start(')
        self.assertGreater(start_idx, 0)
        start_snip = director_ai_src[start_idx:stop_idx]
        self.assertLess(
            start_snip.find('markStreetReclaiming'),
            start_snip.find('setPollution'))
        # Client secured-lock tip + meter rim confirm on full reclaim.
        director_client_src = _read(
            'toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('__confirmSecuredLock', director_client_src)
        self.assertIn('securedLockTipText', director_client_src)
        self.assertIn('confirmSecured', director_client_src)
        for secured_key in (
                'SECURED_LOCK_TIP_ENABLED',
                'SECURED_LOCK_TIP',
                'SECURED_LOCK_RIM_COLOR',
                'SECURED_LOCK_HUD_HOLD_SEC',
                'SECURED_LOCK_SPARKLE_ENABLED',
                'SECURED_LOCK_SPARKLE_COLOR',
                'SECURED_LOCK_STING_ENABLED',
                'SECURED_LOCK_STING_SFX',
                'SECURED_LOCK_METER_POP_SCALE'):
            self.assertIn(
                secured_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % secured_key)
        self.assertIn(
            '__playSecuredLockSparkleSting', director_client_src)
        self.assertIn('reclaimStreetSecured', director_client_src)
        self.assertIn(
            'ensureSecuredLockSparkleFxClient', director_client_src)
        sparkle_fx_src = _read(
            'toontown/reclaim/SecuredLockSparkleFx.py')
        self.assertIn('playLockSting', sparkle_fx_src)
        self.assertIn('SECURED_LOCK_SPARKLE', sparkle_fx_src)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, sparkle_fx_src.lower())
        secured_helpers = _class_and_func_names(self.reclaim_tree)
        self.assertIn(
            'securedLockTipText', secured_helpers,
            msg='ReclaimGlobals missing securedLockTipText')
        secured_assigns = _assign_map(self.reclaim_tree)
        self.assertIs(secured_assigns.get('SECURED_LOCK_TIP_ENABLED'), True)
        secured_tip = str(secured_assigns.get('SECURED_LOCK_TIP', '')).lower()
        self.assertIn('secured', secured_tip)
        self.assertIn('ink', secured_tip)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, secured_tip)
        meter_methods = _class_method_names(
            _module_ast('toontown/reclaim/PurityMeterHud.py'),
            'PurityMeterHud')
        self.assertIn('confirmSecured', meter_methods)
        # Client presentation follows setZonePollution (no extra AI thrash).
        client_pollution_src = _read(
            'toontown/corruption/PollutionManager.py')
        self.assertIn('Incomplete reclaim re-creep', client_pollution_src)

        # Dodge roll cream sparkle flecks (#101) — glitter along smear trail.
        for dodge_sparkle_key in (
                'DODGE_TRAIL_CREAM_SPARKLE_ENABLED',
                'DODGE_TRAIL_CREAM_SPARKLE_COUNT',
                'DODGE_TRAIL_CREAM_SPARKLE_STREAK_COUNT',
                'DODGE_TRAIL_CREAM_SPARKLE_COLOR',
                'DODGE_TRAIL_CREAM_SPARKLE_END',
                'DODGE_TRAIL_CREAM_SPARKLE_SPAWN_SEC'):
            self.assertIn(
                dodge_sparkle_key, config_names,
                msg='HackSlashConfig missing dodge cream sparkle %s'
                % dodge_sparkle_key)
        dodge_trail_tree = _module_ast('toontown/hackslash/DodgeTrailFx.py')
        dodge_trail_methods = _class_method_names(dodge_trail_tree, 'DodgeTrailFx')
        self.assertIn('_spawnCreamSparkles', dodge_trail_methods)
        self.assertIn('_makeCreamSparkleFleck', dodge_trail_methods)
        dodge_trail_src = _read('toontown/hackslash/DodgeTrailFx.py')
        self.assertIn('DODGE_TRAIL_CREAM_SPARKLE_ENABLED', dodge_trail_src)

        # Corrupt telegraph cream warn flecks (#102) — cream contrast at wind-up.
        warn_rel = 'toontown/corruption/CorruptTelegraphCreamWarnFx.py'
        _assert_module_file(warn_rel)
        warn_names = _class_and_func_names(_module_ast(warn_rel))
        self.assertIn('TelegraphCreamWarnFlecks', warn_names)
        self.assertIn('telegraphCreamWarnLook', warn_names)
        warn_methods = _class_method_names(
            _module_ast(warn_rel), 'TelegraphCreamWarnFlecks')
        self.assertIn('play', warn_methods)
        self.assertIn('_spawnFleck', warn_methods)
        self.assertTrue(
            hasattr(cg, 'TELEGRAPH_CREAM_WARN_LOOK'),
            msg='CorruptionGlobals missing TELEGRAPH_CREAM_WARN_LOOK')
        self.assertEqual(
            cg.TELEGRAPH_CREAM_WARN_LOOK.get('id'), 'telegraph-cream-warn')
        self.assertTrue(
            hasattr(cg, 'TELEGRAPH_CREAM_WARN_ENABLED'),
            msg='CorruptionGlobals missing TELEGRAPH_CREAM_WARN_ENABLED')
        self.assertIn('TelegraphCreamWarnFlecks', corrupt_src)
        self.assertIn('CorruptTelegraphCreamWarnFx', corrupt_src)

        # Purity-complete cream wash pulse (#104) — veil under StreetSparkleFx.
        purity_wash_rel = 'toontown/reclaim/PurityCompleteCreamWashFx.py'
        _assert_module_file(purity_wash_rel)
        purity_wash_names = _class_and_func_names(_module_ast(purity_wash_rel))
        self.assertIn('PurityCompleteCreamWashFxClient', purity_wash_names)
        self.assertIn('ensurePurityCompleteCreamWashFxClient', purity_wash_names)
        purity_wash_methods = _class_method_names(
            _module_ast(purity_wash_rel), 'PurityCompleteCreamWashFxClient')
        self.assertIn('playPulse', purity_wash_methods)
        self.assertIn('_onPurityRestore', purity_wash_methods)
        for purity_wash_key in (
                'PURITY_COMPLETE_CREAM_WASH_ENABLED',
                'PURITY_COMPLETE_CREAM_WASH_COLOR',
                'PURITY_COMPLETE_CREAM_WASH_BIN',
                'PURITY_COMPLETE_CREAM_WASH_PEAK',
                'PURITY_COMPLETE_CREAM_WASH_MID',
                'PURITY_COMPLETE_CREAM_WASH_OUT_SEC'):
            self.assertIn(
                purity_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % purity_wash_key)
        self.assertIn('ensurePurityCompleteCreamWashFxClient', director_src)

        # Victory cream sparkle flecks (#105) — glitter on victory confetti swell.
        for victory_key in (
                'VICTORY_CREAM_SPARKLE_ENABLED',
                'VICTORY_CREAM_SPARKLE_COUNT',
                'VICTORY_CREAM_SPARKLE_STREAK_COUNT',
                'VICTORY_CREAM_SPARKLE_COLORS',
                'VICTORY_CREAM_SPARKLE_BIN'):
            self.assertIn(
                victory_key, campaign_names,
                msg='CampaignGlobals missing %s' % victory_key)
        victory_methods = _class_method_names(
            _module_ast(confetti_rel), 'VictoryCreamConfettiSwell')
        self.assertIn('_spawnCreamSparkle', victory_methods)
        self.assertIn('play', victory_methods)
        self.assertIn('VictoryCreamConfettiSwell', confetti_names)
        self.assertIn('ensureVictoryCreamConfettiSwell', confetti_names)
        self.assertIn('VICTORY_CREAM_SPARKLE_ENABLED', confetti_src)

        # Finisher cream sparkle hang (#107) — delayed residual after slam flash.
        slam_rel = 'toontown/hackslash/CreamSlamFlashFx.py'
        _assert_module_file(slam_rel)
        slam_names = _class_and_func_names(_module_ast(slam_rel))
        self.assertIn('CreamSlamFlashFx', slam_names)
        slam_methods = _class_method_names(_module_ast(slam_rel), 'CreamSlamFlashFx')
        self.assertIn('play', slam_methods)
        self.assertIn('_buildSparkleHang', slam_methods)
        self.assertIn('_spawnHangVeil', slam_methods)
        self.assertIn('_spawnHangSpark', slam_methods)
        for hang_key in (
                'FINISHER_CREAM_SPARKLE_HANG_ENABLED',
                'FINISHER_CREAM_SPARKLE_HANG_DELAY_SEC',
                'FINISHER_CREAM_SPARKLE_HANG_COUNT',
                'FINISHER_CREAM_SPARKLE_HANG_COLOR',
                'FINISHER_CREAM_SPARKLE_HANG_VEIL_ENABLED',
                'FINISHER_CREAM_SPARKLE_HANG_VEIL_COLOR'):
            self.assertIn(
                hang_key, config_names,
                msg='HackSlashConfig missing finisher sparkle hang %s' % hang_key)
        slam_src = _read(slam_rel)
        self.assertIn('FINISHER_CREAM_SPARKLE_HANG_ENABLED', slam_src)
        self.assertIn('CreamSlamFlashFx', melee_src)

        # Idle cream drip contrast (#108) — soft cream drips vs idle ink.
        cream_drip_rel = 'toontown/corruption/IdleCreamDripContrastFx.py'
        _assert_module_file(cream_drip_rel)
        cream_drip_names = _class_and_func_names(_module_ast(cream_drip_rel))
        self.assertIn('IdleCreamDripContrast', cream_drip_names)
        self.assertIn('idleCreamDripLook', cream_drip_names)
        cream_drip_methods = _class_method_names(
            _module_ast(cream_drip_rel), 'IdleCreamDripContrast')
        self.assertIn('start', cream_drip_methods)
        self.assertIn('_spawnDrip', cream_drip_methods)
        self.assertIn('_emitBurst', cream_drip_methods)
        self.assertTrue(
            hasattr(cg, 'IDLE_CREAM_DRIP_LOOK'),
            msg='CorruptionGlobals missing IDLE_CREAM_DRIP_LOOK')
        self.assertEqual(
            cg.IDLE_CREAM_DRIP_LOOK.get('id'), 'idle-cream-drip')
        self.assertTrue(
            hasattr(cg, 'IDLE_CREAM_DRIP_ENABLED'),
            msg='CorruptionGlobals missing IDLE_CREAM_DRIP_ENABLED')
        self.assertIn('IdleCreamDripContrast', corrupt_src)
        self.assertIn('__startIdleCreamDrip', corrupt_src)

        # Entry cream wash pulse (#109) — soft veil under EntryCreamShimmerFx.
        entry_wash_rel = 'toontown/reclaim/EntryCreamWashPulseFx.py'
        _assert_module_file(entry_wash_rel)
        entry_wash_names = _class_and_func_names(_module_ast(entry_wash_rel))
        self.assertIn('EntryCreamWashPulseFxClient', entry_wash_names)
        self.assertIn('ensureEntryCreamWashPulseFxClient', entry_wash_names)
        entry_wash_methods = _class_method_names(
            _module_ast(entry_wash_rel), 'EntryCreamWashPulseFxClient')
        self.assertIn('playPulse', entry_wash_methods)
        self.assertIn('_streetIsPolluted', entry_wash_methods)
        for entry_wash_key in (
                'ENTRY_CREAM_WASH_PULSE_ENABLED',
                'ENTRY_CREAM_WASH_PULSE_MIN_POLLUTION',
                'ENTRY_CREAM_WASH_PULSE_COLOR',
                'ENTRY_CREAM_WASH_PULSE_BIN',
                'ENTRY_CREAM_WASH_PULSE_PEAK',
                'ENTRY_CREAM_WASH_PULSE_OUT_SEC'):
            self.assertIn(
                entry_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % entry_wash_key)
        self.assertIn('ensureEntryCreamWashPulseFxClient', director_src)
        self.assertIn('ensureEntryCreamWashPulseFxClient', cheer_src)

        # Act banner cream edge pulse (#110) — cream frame on act-enter banners.
        act_edge_rel = 'toontown/campaign/ActBannerCreamEdgeFx.py'
        _assert_module_file(act_edge_rel)
        act_edge_names = _class_and_func_names(_module_ast(act_edge_rel))
        self.assertIn('ActBannerCreamEdgeFx', act_edge_names)
        self.assertIn('playActBannerCreamEdge', act_edge_names)
        self.assertIn('clearActBannerCreamEdge', act_edge_names)
        act_edge_methods = _class_method_names(
            _module_ast(act_edge_rel), 'ActBannerCreamEdgeFx')
        self.assertIn('play', act_edge_methods)
        self.assertIn('_spawnEdgeFlecks', act_edge_methods)
        self.assertIn('_buildEdgeRoot', act_edge_methods)
        for act_edge_key in (
                'PLAY_ENTRY_BANNER_CREAM_EDGE_ENABLED',
                'PLAY_ENTRY_BANNER_CREAM_EDGE_COLOR',
                'PLAY_ENTRY_BANNER_CREAM_EDGE_PEAK',
                'PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_COUNT',
                'PLAY_ENTRY_BANNER_CREAM_EDGE_BIN'):
            self.assertIn(
                act_edge_key, campaign_names,
                msg='CampaignGlobals missing %s' % act_edge_key)
        self.assertIn('playActBannerCreamEdge', play_src)
        self.assertIn('creamEdge=True', play_src)

        # Air-juggle cream aftershock (#111) — delayed residual on CreamHangSparkleFx.
        hang_rel = 'toontown/hackslash/CreamHangSparkleFx.py'
        _assert_module_file(hang_rel)
        hang_names = _class_and_func_names(_module_ast(hang_rel))
        self.assertIn('CreamHangSparkleFx', hang_names)
        hang_methods = _class_method_names(
            _module_ast(hang_rel), 'CreamHangSparkleFx')
        self.assertIn('play', hang_methods)
        self.assertIn('_buildAftershock', hang_methods)
        self.assertIn('_spawnAftershockHalo', hang_methods)
        self.assertIn('_spawnAftershockSpark', hang_methods)
        for juggle_key in (
                'LAUNCH_HANG_CREAM_AFTERSHOCK_ENABLED',
                'LAUNCH_HANG_CREAM_AFTERSHOCK_DELAY_SEC',
                'LAUNCH_HANG_CREAM_AFTERSHOCK_COUNT',
                'LAUNCH_HANG_CREAM_AFTERSHOCK_COLOR',
                'LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_ENABLED',
                'LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                juggle_key, config_names,
                msg='HackSlashConfig missing juggle aftershock %s' % juggle_key)
        self.assertIn('CreamHangSparkleFx', melee_src)
        self.assertIn('CreamHangSparkleFx', hack_init)

        # Hood tint cream fade (#112) — cream lift of PollutionPropTint on purity.
        hood_fade_rel = 'toontown/corruption/PollutionHoodTintCreamFadeFx.py'
        _assert_module_file(hood_fade_rel)
        hood_fade_names = _class_and_func_names(_module_ast(hood_fade_rel))
        self.assertIn('PollutionHoodTintCreamFadeFx', hood_fade_names)
        hood_fade_methods = _class_method_names(
            _module_ast(hood_fade_rel), 'PollutionHoodTintCreamFadeFx')
        self.assertIn('playFade', hood_fade_methods)
        self.assertIn('_spawnShimmer', hood_fade_methods)
        self.assertIn('_spawnFlecks', hood_fade_methods)
        for hood_fade_key in (
                'HOOD_TINT_CREAM_FADE_ENABLED',
                'HOOD_TINT_CREAM_FADE_SEC',
                'HOOD_TINT_CREAM_FADE_COLOR',
                'HOOD_TINT_CREAM_FADE_FLECK_COUNT',
                'HOOD_TINT_CREAM_FADE_BIN'):
            self.assertTrue(
                hasattr(cg, hood_fade_key),
                msg='CorruptionGlobals missing %s' % hood_fade_key)
        self.assertTrue(
            hasattr(cg, 'hoodPropTintCreamFadeColor'),
            msg='CorruptionGlobals missing hoodPropTintCreamFadeColor')
        prop_tint_src = _read('toontown/corruption/PollutionPropTint.py')
        self.assertIn('beginCreamFade', prop_tint_src)
        self.assertIn('PollutionHoodTintCreamFadeFx', pollution_src)

        # Wave-edge cream sparkle (#113) — StreetSparkle flecks on announce edge.
        wave_edge_methods = _class_method_names(
            _module_ast('toontown/reclaim/WaveCreamBurstFx.py'),
            'WaveCreamBurstFxClient')
        self.assertIn('playEdgePulse', wave_edge_methods)
        self.assertIn('_spawnEdgeSparkles', wave_edge_methods)
        self.assertIn('_spawnEdgeFlecks', wave_edge_methods)
        for wave_sparkle_key in (
                'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_ENABLED',
                'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_COUNT',
                'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_COLOR',
                'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_END_COLOR',
                'WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_SEC'):
            self.assertIn(
                wave_sparkle_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % wave_sparkle_key)
        wave_burst_src = _read('toontown/reclaim/WaveCreamBurstFx.py')
        self.assertIn('WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_ENABLED', wave_burst_src)

        # Wave-start purity meter hose pop — sunny squash/stretch on pack spawn.
        for wave_start_key in (
                'WAVE_START_METER_POP_ENABLED',
                'WAVE_START_METER_POP_SQUASH',
                'WAVE_START_METER_POP_STRETCH',
                'WAVE_START_METER_POP_SETTLE_SEC',
                'WAVE_START_METER_RIM_COLOR',
                'WAVE_START_METER_RIM_SEC'):
            self.assertIn(
                wave_start_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % wave_start_key)
        wave_start_assigns = _assign_map(self.reclaim_tree)
        self.assertIs(
            wave_start_assigns.get('WAVE_START_METER_POP_ENABLED'), True)
        wave_start_hud_methods = _class_method_names(
            _module_ast('toontown/reclaim/PurityMeterHud.py'), 'PurityMeterHud')
        self.assertIn('popWaveStart', wave_start_hud_methods)
        self.assertIn('_resetRootScale', wave_start_hud_methods)
        wave_start_director_src = _read(
            'toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('popWaveStart', wave_start_director_src)
        wave_start_hud_src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('WAVE_START_METER_POP', wave_start_hud_src)
        self.assertIn('reclaimPurityMeterWaveStartHose', wave_start_hud_src)

        # Purity-complete meter hose settle — stretch→settle after celebration.
        for complete_settle_key in (
                'PURITY_COMPLETE_METER_SETTLE_ENABLED',
                'PURITY_COMPLETE_METER_SETTLE_STRETCH',
                'PURITY_COMPLETE_METER_SETTLE_SEC',
                'PURITY_COMPLETE_METER_SETTLE_RIM_COLOR',
                'PURITY_COMPLETE_METER_SETTLE_RIM_SEC',
                'PURITY_COMPLETE_METER_SETTLE_HUD_HOLD_SEC'):
            self.assertIn(
                complete_settle_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % complete_settle_key)
        complete_settle_assigns = _assign_map(self.reclaim_tree)
        self.assertIs(
            complete_settle_assigns.get(
                'PURITY_COMPLETE_METER_SETTLE_ENABLED'), True)
        self.assertIn('settleComplete', wave_start_hud_methods)
        self.assertIn(
            '__hoseSettlePurityMeterComplete', wave_start_director_src)
        self.assertIn('settleComplete', wave_start_director_src)
        self.assertIn(
            'reclaimPurityMeterCompleteSettle', wave_start_hud_src)
        self.assertIn('PURITY_COMPLETE_METER_SETTLE', wave_start_hud_src)

        # Silhouette cream rim flecks (#114) — cream rim sparkle on corrupt ink.
        rim_rel = 'toontown/corruption/CorruptSilhouetteCreamRimFx.py'
        _assert_module_file(rim_rel)
        rim_names = _class_and_func_names(_module_ast(rim_rel))
        self.assertIn('SilhouetteCreamRimFlecks', rim_names)
        self.assertIn('silhouetteCreamRimLook', rim_names)
        rim_methods = _class_method_names(
            _module_ast(rim_rel), 'SilhouetteCreamRimFlecks')
        self.assertIn('start', rim_methods)
        self.assertIn('_spawnFleck', rim_methods)
        self.assertIn('_emitBurst', rim_methods)
        self.assertTrue(
            hasattr(cg, 'SILHOUETTE_CREAM_RIM_LOOK'),
            msg='CorruptionGlobals missing SILHOUETTE_CREAM_RIM_LOOK')
        self.assertEqual(
            cg.SILHOUETTE_CREAM_RIM_LOOK.get('id'), 'silhouette-cream-rim')
        self.assertTrue(
            hasattr(cg, 'SILHOUETTE_CREAM_RIM_ENABLED'),
            msg='CorruptionGlobals missing SILHOUETTE_CREAM_RIM_ENABLED')
        self.assertIn('SilhouetteCreamRimFlecks', corrupt_src)
        self.assertIn('__startSilhouetteCreamRim', corrupt_src)

        # Combo counter cream aftershock (#116) — delayed residual after cream tick.
        hit_juice_rel = 'toontown/hackslash/HitJuice.py'
        _assert_module_file(hit_juice_rel)
        hit_juice_names = _class_and_func_names(_module_ast(hit_juice_rel))
        self.assertIn('spawnComboCreamSparkles', hit_juice_names)
        self.assertIn('_buildComboCreamAftershock', hit_juice_names)
        self.assertIn('_spawnComboCreamAftershockHalo', hit_juice_names)
        self.assertIn('_spawnComboCreamAftershockSpark', hit_juice_names)
        for combo_as_key in (
                'COMBO_COUNTER_CREAM_AFTERSHOCK_ENABLED',
                'COMBO_COUNTER_CREAM_AFTERSHOCK_DELAY_SEC',
                'COMBO_COUNTER_CREAM_AFTERSHOCK_COUNT',
                'COMBO_COUNTER_CREAM_AFTERSHOCK_COLOR',
                'COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_ENABLED',
                'COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                combo_as_key, config_names,
                msg='HackSlashConfig missing combo aftershock %s' % combo_as_key)
        hit_juice_src = _read(hit_juice_rel)
        self.assertIn('COMBO_COUNTER_CREAM_AFTERSHOCK_ENABLED', hit_juice_src)
        self.assertIn('spawnComboCreamSparkles', melee_src)

        # Oswald trust banner cream edge (#117) — cream frame on handoff settle.
        act_edge_names = _class_and_func_names(_module_ast(act_edge_rel))
        self.assertIn('playOswaldTrustBannerCreamEdge', act_edge_names)
        self.assertIn('clearOswaldTrustBannerCreamEdge', act_edge_names)
        for trust_edge_key in (
                'OSWALD_TRUST_BANNER_CREAM_EDGE_ENABLED',
                'OSWALD_TRUST_BANNER_CREAM_EDGE_COLOR',
                'OSWALD_TRUST_BANNER_CREAM_EDGE_PEAK',
                'OSWALD_TRUST_BANNER_CREAM_EDGE_FLECK_COUNT',
                'OSWALD_TRUST_BANNER_CREAM_EDGE_BIN'):
            self.assertIn(
                trust_edge_key, campaign_names,
                msg='CampaignGlobals missing %s' % trust_edge_key)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playOswaldTrustBannerCreamEdge', handoff_src)
        self.assertIn('trustSettle=True', handoff_src)

        # Cheer cream aftershock (#118) — delayed residual after cheer sparkle.
        cheer_sparkle_methods = _class_method_names(
            _module_ast(cheer_sparkle_rel), 'CheerCreamSparkleFxClient')
        self.assertIn('_buildAftershock', cheer_sparkle_methods)
        self.assertIn('_spawnAftershockHalo', cheer_sparkle_methods)
        self.assertIn('_spawnAftershockFleck', cheer_sparkle_methods)
        for cheer_as_key in (
                'CHEER_CREAM_AFTERSHOCK_ENABLED',
                'CHEER_CREAM_AFTERSHOCK_DELAY_SEC',
                'CHEER_CREAM_AFTERSHOCK_COUNT',
                'CHEER_CREAM_AFTERSHOCK_COLOR',
                'CHEER_CREAM_AFTERSHOCK_HALO_ENABLED',
                'CHEER_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                cheer_as_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % cheer_as_key)
        cheer_sparkle_src = _read(cheer_sparkle_rel)
        self.assertIn('CHEER_CREAM_AFTERSHOCK_ENABLED', cheer_sparkle_src)

        # Corrupt death cream wash (#119) — soft wash after death fleck burst.
        death_wash_rel = 'toontown/corruption/CorruptDeathCreamWashFx.py'
        _assert_module_file(death_wash_rel)
        death_wash_names = _class_and_func_names(_module_ast(death_wash_rel))
        self.assertIn('DeathCreamWashPulse', death_wash_names)
        death_wash_methods = _class_method_names(
            _module_ast(death_wash_rel), 'DeathCreamWashPulse')
        self.assertIn('play', death_wash_methods)
        self.assertIn('clear', death_wash_methods)
        for death_wash_key in (
                'DEATH_CREAM_WASH_ENABLED',
                'DEATH_CREAM_WASH_DELAY_SEC',
                'DEATH_CREAM_WASH_COLOR',
                'DEATH_CREAM_WASH_PEAK',
                'DEATH_CREAM_WASH_MID',
                'DEATH_CREAM_WASH_BIN'):
            self.assertTrue(
                hasattr(cg, death_wash_key),
                msg='CorruptionGlobals missing %s' % death_wash_key)
        death_pop_src = _read('toontown/corruption/CorruptDeathPopFx.py')
        self.assertIn('DeathCreamWashPulse', death_pop_src)
        self.assertIn('CorruptDeathCreamWashFx', death_pop_src)

        # (#120 was prior headless smoke through #114 — no new juice symbols.)

        # Telegraph cream aftershock (#121) — delayed residual after warn flecks.
        warn_methods = _class_method_names(
            _module_ast(warn_rel), 'TelegraphCreamWarnFlecks')
        self.assertIn('_buildAftershock', warn_methods)
        self.assertIn('_spawnAftershockHalo', warn_methods)
        self.assertIn('_spawnAftershockSpark', warn_methods)
        for telegraph_as_key in (
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_ENABLED',
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_DELAY_SEC',
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_COUNT',
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_COLOR',
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_ENABLED',
                'TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_COLOR'):
            self.assertTrue(
                hasattr(cg, telegraph_as_key),
                msg='CorruptionGlobals missing %s' % telegraph_as_key)
        warn_src = _read(warn_rel)
        self.assertIn('TELEGRAPH_CREAM_WARN_AFTERSHOCK_ENABLED', warn_src)

        # Finisher cream aftershock (#122) — delayed residual after sparkle hang.
        slam_methods = _class_method_names(
            _module_ast(slam_rel), 'CreamSlamFlashFx')
        self.assertIn('_buildAftershock', slam_methods)
        self.assertIn('_spawnAftershockHalo', slam_methods)
        self.assertIn('_spawnAftershockSpark', slam_methods)
        for finisher_as_key in (
                'FINISHER_CREAM_AFTERSHOCK_ENABLED',
                'FINISHER_CREAM_AFTERSHOCK_DELAY_SEC',
                'FINISHER_CREAM_AFTERSHOCK_COUNT',
                'FINISHER_CREAM_AFTERSHOCK_COLOR',
                'FINISHER_CREAM_AFTERSHOCK_HALO_ENABLED',
                'FINISHER_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                finisher_as_key, config_names,
                msg='HackSlashConfig missing finisher aftershock %s'
                % finisher_as_key)
        slam_src = _read(slam_rel)
        self.assertIn('FINISHER_CREAM_AFTERSHOCK_ENABLED', slam_src)

        # Purity-fill cream aftershock (#123) — delayed residual after fill shimmer.
        purity_methods = _class_method_names(
            _module_ast('toontown/reclaim/PurityMeterHud.py'), 'PurityMeterHud')
        self.assertIn('_buildFillAftershock', purity_methods)
        self.assertIn('_spawnFillAftershockHalo', purity_methods)
        self.assertIn('_spawnFillAftershockFleck', purity_methods)
        for purity_as_key in (
                'PURITY_METER_FILL_AFTERSHOCK_ENABLED',
                'PURITY_METER_FILL_AFTERSHOCK_DELAY_SEC',
                'PURITY_METER_FILL_AFTERSHOCK_COUNT',
                'PURITY_METER_FILL_AFTERSHOCK_COLOR',
                'PURITY_METER_FILL_AFTERSHOCK_HALO_ENABLED',
                'PURITY_METER_FILL_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                purity_as_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % purity_as_key)
        purity_src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('PURITY_METER_FILL_AFTERSHOCK_ENABLED', purity_src)

        # Handoff cream edge (#124) — cream frame on carnival confetti handoff.
        act_edge_names = _class_and_func_names(_module_ast(act_edge_rel))
        self.assertIn('playHandoffCreamEdge', act_edge_names)
        self.assertIn('clearHandoffCreamEdge', act_edge_names)
        for handoff_edge_key in (
                'HANDOFF_CREAM_EDGE_ENABLED',
                'HANDOFF_CREAM_EDGE_COLOR',
                'HANDOFF_CREAM_EDGE_PEAK',
                'HANDOFF_CREAM_EDGE_FLECK_COUNT',
                'HANDOFF_CREAM_EDGE_BIN',
                'HANDOFF_CREAM_EDGE_SPARKLE_ENABLED',
                'HANDOFF_CREAM_EDGE_SETTLE_ENABLED',
                'HANDOFF_CREAM_EDGE_SETTLE_OVERSHOOT',
                'HANDOFF_CREAM_EDGE_SETTLE_REST_SEC'):
            self.assertIn(
                handoff_edge_key, campaign_names,
                msg='CampaignGlobals missing %s' % handoff_edge_key)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playHandoffCreamEdge', handoff_src)
        self.assertIn('confetti=True', handoff_src)
        # Act handoff cream edge settle — overshoot→rest after edge peak.
        act_edge_methods = _class_method_names(
            _module_ast(act_edge_rel), 'ActBannerCreamEdgeFx')
        self.assertIn('_settleScalePart', act_edge_methods)
        act_edge_src = _read(act_edge_rel)
        self.assertIn('SETTLE_OVERSHOOT', act_edge_src)
        self.assertIn('CreamEdgeSettle', act_edge_src)
        magic_src_l = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('edge settle', magic_src_l)

        # Idle cream drip sparkle (#125) — twinkle flecks on idle cream drip.
        idle_sparkle_rel = 'toontown/corruption/IdleCreamDripSparkleFx.py'
        _assert_module_file(idle_sparkle_rel)
        idle_sparkle_names = _class_and_func_names(_module_ast(idle_sparkle_rel))
        self.assertIn('IdleCreamDripSparkles', idle_sparkle_names)
        self.assertIn('idleCreamDripSparkleLook', idle_sparkle_names)
        idle_sparkle_methods = _class_method_names(
            _module_ast(idle_sparkle_rel), 'IdleCreamDripSparkles')
        self.assertIn('start', idle_sparkle_methods)
        self.assertIn('_spawnFleck', idle_sparkle_methods)
        self.assertIn('_emitBurst', idle_sparkle_methods)
        self.assertTrue(
            hasattr(cg, 'IDLE_CREAM_DRIP_SPARKLE_LOOK'),
            msg='CorruptionGlobals missing IDLE_CREAM_DRIP_SPARKLE_LOOK')
        self.assertEqual(
            cg.IDLE_CREAM_DRIP_SPARKLE_LOOK.get('id'), 'idle-cream-drip-sparkle')
        self.assertTrue(
            hasattr(cg, 'IDLE_CREAM_DRIP_SPARKLE_ENABLED'),
            msg='CorruptionGlobals missing IDLE_CREAM_DRIP_SPARKLE_ENABLED')
        self.assertIn('IdleCreamDripSparkles', corrupt_src)
        self.assertIn('__startIdleCreamDripSparkle', corrupt_src)

        # Dodge trail cream aftershock (#126) — delayed residual after sparkle drip.
        dodge_trail_methods = _class_method_names(
            _module_ast('toontown/hackslash/DodgeTrailFx.py'), 'DodgeTrailFx')
        self.assertIn('_buildCreamAftershock', dodge_trail_methods)
        self.assertIn('_spawnCreamAftershockHalo', dodge_trail_methods)
        self.assertIn('_spawnCreamAftershockFleck', dodge_trail_methods)
        for dodge_as_key in (
                'DODGE_TRAIL_CREAM_AFTERSHOCK_ENABLED',
                'DODGE_TRAIL_CREAM_AFTERSHOCK_DELAY_SEC',
                'DODGE_TRAIL_CREAM_AFTERSHOCK_COUNT',
                'DODGE_TRAIL_CREAM_AFTERSHOCK_COLOR',
                'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_ENABLED',
                'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                dodge_as_key, config_names,
                msg='HackSlashConfig missing dodge aftershock %s' % dodge_as_key)
        dodge_trail_src = _read('toontown/hackslash/DodgeTrailFx.py')
        self.assertIn('DODGE_TRAIL_CREAM_AFTERSHOCK_ENABLED', dodge_trail_src)

        # Wave-clear cream aftershock (#127) — delayed residual after shimmer hang.
        wave_shimmer_methods = _class_method_names(
            _module_ast(shimmer_rel), 'WaveClearCreamShimmerFxClient')
        self.assertIn('_buildAftershock', wave_shimmer_methods)
        self.assertIn('_spawnAftershockHalo', wave_shimmer_methods)
        self.assertIn('_spawnAftershockFleck', wave_shimmer_methods)
        for wave_as_key in (
                'WAVE_CLEAR_CREAM_AFTERSHOCK_ENABLED',
                'WAVE_CLEAR_CREAM_AFTERSHOCK_DELAY_SEC',
                'WAVE_CLEAR_CREAM_AFTERSHOCK_COUNT',
                'WAVE_CLEAR_CREAM_AFTERSHOCK_COLOR',
                'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_ENABLED',
                'WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                wave_as_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % wave_as_key)
        wave_shimmer_src = _read(shimmer_rel)
        self.assertIn('WAVE_CLEAR_CREAM_AFTERSHOCK_ENABLED', wave_shimmer_src)

        # (#128 was prior headless smoke through #123 — no new juice symbols.)

        # Victory cream edge (#129) — cream frame on victory confetti/sparkle swell.
        act_edge_names = _class_and_func_names(_module_ast(act_edge_rel))
        self.assertIn('playVictoryCreamEdge', act_edge_names)
        self.assertIn('clearVictoryCreamEdge', act_edge_names)
        for victory_edge_key in (
                'VICTORY_CREAM_EDGE_ENABLED',
                'VICTORY_CREAM_EDGE_COLOR',
                'VICTORY_CREAM_EDGE_PEAK',
                'VICTORY_CREAM_EDGE_FLECK_COUNT',
                'VICTORY_CREAM_EDGE_BIN',
                'VICTORY_CREAM_EDGE_SPARKLE_ENABLED'):
            self.assertIn(
                victory_edge_key, campaign_names,
                msg='CampaignGlobals missing %s' % victory_edge_key)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playVictoryCreamEdge', handoff_src)
        self.assertIn('creamSwell=True', handoff_src)

        # Perfect-dodge cream wash (#130) — soft wash after perfect-dodge aftershock.
        pd_wash_rel = 'toontown/hackslash/PerfectDodgeCreamWashFx.py'
        _assert_module_file(pd_wash_rel)
        pd_wash_names = _class_and_func_names(_module_ast(pd_wash_rel))
        self.assertIn('PerfectDodgeCreamWashPulse', pd_wash_names)
        pd_wash_methods = _class_method_names(
            _module_ast(pd_wash_rel), 'PerfectDodgeCreamWashPulse')
        self.assertIn('play', pd_wash_methods)
        self.assertIn('clear', pd_wash_methods)
        for pd_wash_key in (
                'PERFECT_DODGE_CREAM_WASH_ENABLED',
                'PERFECT_DODGE_CREAM_WASH_DELAY_SEC',
                'PERFECT_DODGE_CREAM_WASH_COLOR',
                'PERFECT_DODGE_CREAM_WASH_PEAK',
                'PERFECT_DODGE_CREAM_WASH_MID',
                'PERFECT_DODGE_CREAM_WASH_BIN'):
            self.assertIn(
                pd_wash_key, config_names,
                msg='HackSlashConfig missing %s' % pd_wash_key)
        dodge_perfect_src = _read('toontown/hackslash/DodgePerfectFx.py')
        self.assertIn('PerfectDodgeCreamWashPulse', dodge_perfect_src)
        self.assertIn('PerfectDodgeCreamWashPulse', hack_init)

        # Silhouette cream sparkle (#131) — rising flecks on silhouette cream rim.
        silh_sparkle_rel = 'toontown/corruption/CorruptSilhouetteCreamSparkleFx.py'
        _assert_module_file(silh_sparkle_rel)
        silh_sparkle_names = _class_and_func_names(_module_ast(silh_sparkle_rel))
        self.assertIn('SilhouetteCreamSparkles', silh_sparkle_names)
        self.assertIn('silhouetteCreamSparkleLook', silh_sparkle_names)
        silh_sparkle_methods = _class_method_names(
            _module_ast(silh_sparkle_rel), 'SilhouetteCreamSparkles')
        self.assertIn('start', silh_sparkle_methods)
        self.assertIn('_spawnFleck', silh_sparkle_methods)
        self.assertIn('_emitBurst', silh_sparkle_methods)
        self.assertTrue(
            hasattr(cg, 'SILHOUETTE_CREAM_SPARKLE_LOOK'),
            msg='CorruptionGlobals missing SILHOUETTE_CREAM_SPARKLE_LOOK')
        self.assertEqual(
            cg.SILHOUETTE_CREAM_SPARKLE_LOOK.get('id'), 'silhouette-cream-sparkle')
        self.assertTrue(
            hasattr(cg, 'SILHOUETTE_CREAM_SPARKLE_ENABLED'),
            msg='CorruptionGlobals missing SILHOUETTE_CREAM_SPARKLE_ENABLED')
        self.assertIn('SilhouetteCreamSparkles', corrupt_src)
        self.assertIn('__startSilhouetteCreamSparkle', corrupt_src)

        # Entry cream wash aftershock (#132) — delayed residual after entry wash.
        entry_wash_methods = _class_method_names(
            _module_ast(entry_wash_rel), 'EntryCreamWashPulseFxClient')
        self.assertIn('_buildAftershock', entry_wash_methods)
        self.assertIn('_spawnAftershockHalo', entry_wash_methods)
        self.assertIn('_spawnAftershockFleck', entry_wash_methods)
        for entry_as_key in (
                'ENTRY_CREAM_WASH_AFTERSHOCK_ENABLED',
                'ENTRY_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
                'ENTRY_CREAM_WASH_AFTERSHOCK_COUNT',
                'ENTRY_CREAM_WASH_AFTERSHOCK_COLOR',
                'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_ENABLED',
                'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                entry_as_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % entry_as_key)
        entry_wash_src = _read(entry_wash_rel)
        self.assertIn('ENTRY_CREAM_WASH_AFTERSHOCK_ENABLED', entry_wash_src)

        # Finale reveal cream edge (#133) — cream frame on Oswald reveal aftershock.
        act_edge_names = _class_and_func_names(_module_ast(act_edge_rel))
        self.assertIn('playFinaleRevealCreamEdge', act_edge_names)
        self.assertIn('clearFinaleRevealCreamEdge', act_edge_names)
        for finale_edge_key in (
                'FINALE_REVEAL_CREAM_EDGE_ENABLED',
                'FINALE_REVEAL_CREAM_EDGE_COLOR',
                'FINALE_REVEAL_CREAM_EDGE_PEAK',
                'FINALE_REVEAL_CREAM_EDGE_FLECK_COUNT',
                'FINALE_REVEAL_CREAM_EDGE_BIN',
                'FINALE_REVEAL_CREAM_EDGE_SPARKLE_ENABLED'):
            self.assertIn(
                finale_edge_key, campaign_names,
                msg='CampaignGlobals missing %s' % finale_edge_key)
        finale_phase_src = _read('toontown/campaign/FinalePhaseFx.py')
        self.assertIn('playFinaleRevealCreamEdge', finale_phase_src)
        self.assertIn('clearFinaleRevealCreamEdge', finale_phase_src)

        # Melee hit cream wash (#134) — soft wash after hit-spark cream aftershock.
        hit_wash_rel = 'toontown/hackslash/HitSparkCreamWashFx.py'
        _assert_module_file(hit_wash_rel)
        hit_wash_names = _class_and_func_names(_module_ast(hit_wash_rel))
        self.assertIn('HitSparkCreamWashPulse', hit_wash_names)
        hit_wash_methods = _class_method_names(
            _module_ast(hit_wash_rel), 'HitSparkCreamWashPulse')
        self.assertIn('play', hit_wash_methods)
        self.assertIn('clear', hit_wash_methods)
        for hit_wash_key in (
                'HIT_SPARK_CREAM_WASH_ENABLED',
                'HIT_SPARK_CREAM_WASH_DELAY_SEC',
                'HIT_SPARK_CREAM_WASH_COLOR',
                'HIT_SPARK_CREAM_WASH_PEAK',
                'HIT_SPARK_CREAM_WASH_MID',
                'HIT_SPARK_CREAM_WASH_BIN'):
            self.assertIn(
                hit_wash_key, config_names,
                msg='HackSlashConfig missing %s' % hit_wash_key)
        hit_spark_src = _read('toontown/hackslash/HitSparkFx.py')
        self.assertIn('HitSparkCreamWashPulse', hit_spark_src)
        self.assertIn('HitSparkCreamWashPulse', hack_init)

        # Telegraph cream sparkle (#135) — rising flecks on telegraph cream warn.
        tel_sparkle_rel = 'toontown/corruption/CorruptTelegraphCreamSparkleFx.py'
        _assert_module_file(tel_sparkle_rel)
        tel_sparkle_names = _class_and_func_names(_module_ast(tel_sparkle_rel))
        self.assertIn('TelegraphCreamSparkles', tel_sparkle_names)
        self.assertIn('telegraphCreamSparkleLook', tel_sparkle_names)
        tel_sparkle_methods = _class_method_names(
            _module_ast(tel_sparkle_rel), 'TelegraphCreamSparkles')
        self.assertIn('play', tel_sparkle_methods)
        self.assertIn('_spawnFleck', tel_sparkle_methods)
        self.assertTrue(
            hasattr(cg, 'TELEGRAPH_CREAM_SPARKLE_LOOK'),
            msg='CorruptionGlobals missing TELEGRAPH_CREAM_SPARKLE_LOOK')
        self.assertEqual(
            cg.TELEGRAPH_CREAM_SPARKLE_LOOK.get('id'), 'telegraph-cream-sparkle')
        self.assertTrue(
            hasattr(cg, 'TELEGRAPH_CREAM_SPARKLE_ENABLED'),
            msg='CorruptionGlobals missing TELEGRAPH_CREAM_SPARKLE_ENABLED')
        self.assertIn('TelegraphCreamSparkles', corrupt_src)
        self.assertIn('__playTelegraphCreamSparkle', corrupt_src)

        # Purity-complete cream aftershock (#136) — delayed residual after wash pulse.
        purity_wash_methods = _class_method_names(
            _module_ast(purity_wash_rel), 'PurityCompleteCreamWashFxClient')
        self.assertIn('_buildAftershock', purity_wash_methods)
        self.assertIn('_spawnAftershockHalo', purity_wash_methods)
        self.assertIn('_spawnAftershockFleck', purity_wash_methods)
        for purity_complete_as_key in (
                'PURITY_COMPLETE_CREAM_AFTERSHOCK_ENABLED',
                'PURITY_COMPLETE_CREAM_AFTERSHOCK_DELAY_SEC',
                'PURITY_COMPLETE_CREAM_AFTERSHOCK_COUNT',
                'PURITY_COMPLETE_CREAM_AFTERSHOCK_COLOR',
                'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_ENABLED',
                'PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                purity_complete_as_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % purity_complete_as_key)
        purity_wash_src = _read(purity_wash_rel)
        self.assertIn('PURITY_COMPLETE_CREAM_AFTERSHOCK_ENABLED', purity_wash_src)

        # (#137 was prior headless smoke through #132 — no new juice symbols.)

        # Victory cream wash (#138) — soft wash after victory cream edge.
        victory_wash_rel = 'toontown/campaign/VictoryCreamWashFx.py'
        _assert_module_file(victory_wash_rel)
        victory_wash_names = _class_and_func_names(_module_ast(victory_wash_rel))
        self.assertIn('VictoryCreamWashPulse', victory_wash_names)
        self.assertIn('playVictoryCreamWash', victory_wash_names)
        self.assertIn('clearVictoryCreamWash', victory_wash_names)
        victory_wash_methods = _class_method_names(
            _module_ast(victory_wash_rel), 'VictoryCreamWashPulse')
        self.assertIn('play', victory_wash_methods)
        self.assertIn('clear', victory_wash_methods)
        for victory_wash_key in (
                'VICTORY_CREAM_WASH_ENABLED',
                'VICTORY_CREAM_WASH_DELAY_SEC',
                'VICTORY_CREAM_WASH_COLOR',
                'VICTORY_CREAM_WASH_PEAK',
                'VICTORY_CREAM_WASH_MID',
                'VICTORY_CREAM_WASH_BIN'):
            self.assertIn(
                victory_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % victory_wash_key)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playVictoryCreamWash', handoff_src)
        self.assertIn('creamSwell=True', handoff_src)

        # Dodge cream wash (#139) — soft wash after dodge cream aftershock.
        dodge_wash_rel = 'toontown/hackslash/DodgeTrailCreamWashFx.py'
        _assert_module_file(dodge_wash_rel)
        dodge_wash_names = _class_and_func_names(_module_ast(dodge_wash_rel))
        self.assertIn('DodgeTrailCreamWashPulse', dodge_wash_names)
        dodge_wash_methods = _class_method_names(
            _module_ast(dodge_wash_rel), 'DodgeTrailCreamWashPulse')
        self.assertIn('play', dodge_wash_methods)
        self.assertIn('clear', dodge_wash_methods)
        for dodge_wash_key in (
                'DODGE_TRAIL_CREAM_WASH_ENABLED',
                'DODGE_TRAIL_CREAM_WASH_DELAY_SEC',
                'DODGE_TRAIL_CREAM_WASH_COLOR',
                'DODGE_TRAIL_CREAM_WASH_PEAK',
                'DODGE_TRAIL_CREAM_WASH_MID',
                'DODGE_TRAIL_CREAM_WASH_BIN'):
            self.assertIn(
                dodge_wash_key, config_names,
                msg='HackSlashConfig missing %s' % dodge_wash_key)
        dodge_trail_src = _read('toontown/hackslash/DodgeTrailFx.py')
        self.assertIn('DodgeTrailCreamWashPulse', dodge_trail_src)
        self.assertIn('DodgeTrailCreamWashPulse', hack_init)

        # Death cream sparkle (#140) — rising flecks on death cream fleck burst.
        death_sparkle_rel = 'toontown/corruption/CorruptDeathCreamSparkleFx.py'
        _assert_module_file(death_sparkle_rel)
        death_sparkle_names = _class_and_func_names(_module_ast(death_sparkle_rel))
        self.assertIn('DeathCreamSparkles', death_sparkle_names)
        self.assertIn('deathCreamSparkleLook', death_sparkle_names)
        death_sparkle_methods = _class_method_names(
            _module_ast(death_sparkle_rel), 'DeathCreamSparkles')
        self.assertIn('play', death_sparkle_methods)
        self.assertIn('_spawnFleck', death_sparkle_methods)
        self.assertTrue(
            hasattr(cg, 'DEATH_CREAM_SPARKLE_LOOK'),
            msg='CorruptionGlobals missing DEATH_CREAM_SPARKLE_LOOK')
        self.assertEqual(
            cg.DEATH_CREAM_SPARKLE_LOOK.get('id'), 'death-cream-sparkle')
        self.assertTrue(
            hasattr(cg, 'DEATH_CREAM_SPARKLE_ENABLED'),
            msg='CorruptionGlobals missing DEATH_CREAM_SPARKLE_ENABLED')
        death_pop_src = _read('toontown/corruption/CorruptDeathPopFx.py')
        self.assertIn('DeathCreamSparkles', death_pop_src)
        self.assertIn('CorruptDeathCreamSparkleFx', death_pop_src)

        # Handoff cream wash (#141) — soft wash after handoff cream edge.
        handoff_wash_rel = 'toontown/campaign/HandoffCreamWashFx.py'
        _assert_module_file(handoff_wash_rel)
        handoff_wash_names = _class_and_func_names(_module_ast(handoff_wash_rel))
        self.assertIn('HandoffCreamWashPulse', handoff_wash_names)
        self.assertIn('playHandoffCreamWash', handoff_wash_names)
        self.assertIn('clearHandoffCreamWash', handoff_wash_names)
        handoff_wash_methods = _class_method_names(
            _module_ast(handoff_wash_rel), 'HandoffCreamWashPulse')
        self.assertIn('play', handoff_wash_methods)
        self.assertIn('clear', handoff_wash_methods)
        for handoff_wash_key in (
                'HANDOFF_CREAM_WASH_ENABLED',
                'HANDOFF_CREAM_WASH_DELAY_SEC',
                'HANDOFF_CREAM_WASH_COLOR',
                'HANDOFF_CREAM_WASH_PEAK',
                'HANDOFF_CREAM_WASH_MID',
                'HANDOFF_CREAM_WASH_BIN'):
            self.assertIn(
                handoff_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % handoff_wash_key)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playHandoffCreamWash', handoff_src)
        self.assertIn('confetti=True', handoff_src)

        # Cheer cream wash (#142) — soft wash after cheer cream aftershock.
        cheer_wash_rel = 'toontown/reclaim/CheerCreamWashFx.py'
        _assert_module_file(cheer_wash_rel)
        cheer_wash_names = _class_and_func_names(_module_ast(cheer_wash_rel))
        self.assertIn('CheerCreamWashPulse', cheer_wash_names)
        cheer_wash_methods = _class_method_names(
            _module_ast(cheer_wash_rel), 'CheerCreamWashPulse')
        self.assertIn('play', cheer_wash_methods)
        self.assertIn('clear', cheer_wash_methods)
        for cheer_wash_key in (
                'CHEER_CREAM_WASH_ENABLED',
                'CHEER_CREAM_WASH_DELAY_SEC',
                'CHEER_CREAM_WASH_COLOR',
                'CHEER_CREAM_WASH_PEAK',
                'CHEER_CREAM_WASH_MID',
                'CHEER_CREAM_WASH_BIN'):
            self.assertIn(
                cheer_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % cheer_wash_key)
        cheer_sparkle_src = _read(cheer_sparkle_rel)
        self.assertIn('CheerCreamWashPulse', cheer_sparkle_src)

        # Finisher cream wash (#143) — soft wash after finisher cream aftershock.
        finisher_wash_rel = 'toontown/hackslash/FinisherCreamWashFx.py'
        _assert_module_file(finisher_wash_rel)
        finisher_wash_names = _class_and_func_names(_module_ast(finisher_wash_rel))
        self.assertIn('FinisherCreamWashPulse', finisher_wash_names)
        finisher_wash_methods = _class_method_names(
            _module_ast(finisher_wash_rel), 'FinisherCreamWashPulse')
        self.assertIn('play', finisher_wash_methods)
        self.assertIn('clear', finisher_wash_methods)
        for finisher_wash_key in (
                'FINISHER_CREAM_WASH_ENABLED',
                'FINISHER_CREAM_WASH_DELAY_SEC',
                'FINISHER_CREAM_WASH_COLOR',
                'FINISHER_CREAM_WASH_PEAK',
                'FINISHER_CREAM_WASH_MID',
                'FINISHER_CREAM_WASH_BIN'):
            self.assertIn(
                finisher_wash_key, config_names,
                msg='HackSlashConfig missing %s' % finisher_wash_key)
        slam_src = _read(slam_rel)
        self.assertIn('FinisherCreamWashPulse', slam_src)
        self.assertIn('FinisherCreamWashPulse', hack_init)

        # Wave-clear cream wash (#144) — soft wash after wave-clear aftershock.
        wave_wash_rel = 'toontown/reclaim/WaveClearCreamWashFx.py'
        _assert_module_file(wave_wash_rel)
        wave_wash_names = _class_and_func_names(_module_ast(wave_wash_rel))
        self.assertIn('WaveClearCreamWashPulse', wave_wash_names)
        wave_wash_methods = _class_method_names(
            _module_ast(wave_wash_rel), 'WaveClearCreamWashPulse')
        self.assertIn('play', wave_wash_methods)
        self.assertIn('clear', wave_wash_methods)
        self.assertIn('_buildSparkle', wave_wash_methods)
        self.assertIn('_buildSparkleAftershock', wave_wash_methods)
        for wave_wash_key in (
                'WAVE_CLEAR_CREAM_WASH_ENABLED',
                'WAVE_CLEAR_CREAM_WASH_DELAY_SEC',
                'WAVE_CLEAR_CREAM_WASH_COLOR',
                'WAVE_CLEAR_CREAM_WASH_PEAK',
                'WAVE_CLEAR_CREAM_WASH_MID',
                'WAVE_CLEAR_CREAM_WASH_BIN',
                'WAVE_CLEAR_CREAM_SPARKLE_ENABLED',
                'WAVE_CLEAR_CREAM_SPARKLE_POP',
                'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_ENABLED',
                'WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_COUNT'):
            self.assertIn(
                wave_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % wave_wash_key)
        wave_shimmer_src = _read(shimmer_rel)
        self.assertIn('WaveClearCreamWashPulse', wave_shimmer_src)
        self.assertIn('WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK', wave_shimmer_src)
        # Deepened pack-clear glitter stays below StreetSparkle horizon payoff.
        wave_sparkle_assigns = _assign_map(self.reclaim_tree)
        self.assertGreaterEqual(
            int(wave_sparkle_assigns.get('WAVE_CLEAR_CREAM_SPARKLE_COUNT', 0)),
            8)
        self.assertLess(
            int(wave_sparkle_assigns.get('WAVE_CLEAR_CREAM_SPARKLE_COUNT', 0)),
            int(wave_sparkle_assigns.get('STREET_SPARKLE_COUNT', 0)))

        # Oswald trust cream wash (#145) — soft wash after trust cream edge.
        trust_wash_rel = 'toontown/campaign/OswaldTrustCreamWashFx.py'
        _assert_module_file(trust_wash_rel)
        trust_wash_names = _class_and_func_names(_module_ast(trust_wash_rel))
        self.assertIn('OswaldTrustCreamWashPulse', trust_wash_names)
        self.assertIn('playOswaldTrustCreamWash', trust_wash_names)
        self.assertIn('clearOswaldTrustCreamWash', trust_wash_names)
        trust_wash_methods = _class_method_names(
            _module_ast(trust_wash_rel), 'OswaldTrustCreamWashPulse')
        self.assertIn('play', trust_wash_methods)
        self.assertIn('clear', trust_wash_methods)
        for trust_wash_key in (
                'OSWALD_TRUST_BANNER_CREAM_WASH_ENABLED',
                'OSWALD_TRUST_BANNER_CREAM_WASH_DELAY_SEC',
                'OSWALD_TRUST_BANNER_CREAM_WASH_COLOR',
                'OSWALD_TRUST_BANNER_CREAM_WASH_PEAK',
                'OSWALD_TRUST_BANNER_CREAM_WASH_MID',
                'OSWALD_TRUST_BANNER_CREAM_WASH_BIN'):
            self.assertIn(
                trust_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % trust_wash_key)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playOswaldTrustCreamWash', handoff_src)
        self.assertIn('trustSettle=True', handoff_src)

        # Idle cream wash (#146) — soft wash against corrupt idle ink drips.
        idle_wash_rel = 'toontown/corruption/IdleCreamWashPulseFx.py'
        _assert_module_file(idle_wash_rel)
        idle_wash_names = _class_and_func_names(_module_ast(idle_wash_rel))
        self.assertIn('IdleCreamWashPulse', idle_wash_names)
        self.assertIn('idleCreamWashLook', idle_wash_names)
        idle_wash_methods = _class_method_names(
            _module_ast(idle_wash_rel), 'IdleCreamWashPulse')
        self.assertIn('start', idle_wash_methods)
        self.assertIn('pause', idle_wash_methods)
        self.assertIn('resume', idle_wash_methods)
        self.assertIn('clear', idle_wash_methods)
        self.assertTrue(
            hasattr(cg, 'IDLE_CREAM_WASH_LOOK'),
            msg='CorruptionGlobals missing IDLE_CREAM_WASH_LOOK')
        self.assertEqual(
            cg.IDLE_CREAM_WASH_LOOK.get('id'), 'idle-cream-wash')
        self.assertTrue(
            hasattr(cg, 'IDLE_CREAM_WASH_ENABLED'),
            msg='CorruptionGlobals missing IDLE_CREAM_WASH_ENABLED')
        for idle_wash_key in (
                'IDLE_CREAM_WASH_ENABLED',
                'IDLE_CREAM_WASH_DELAY_SEC',
                'IDLE_CREAM_WASH_COLOR',
                'IDLE_CREAM_WASH_PEAK',
                'IDLE_CREAM_WASH_MID',
                'IDLE_CREAM_WASH_BIN'):
            self.assertTrue(
                hasattr(cg, idle_wash_key),
                msg='CorruptionGlobals missing %s' % idle_wash_key)
        self.assertIn('IdleCreamWashPulse', corrupt_src)
        self.assertIn('__startIdleCreamWash', corrupt_src)

        # Combo cream wash (#147) — soft wash after combo cream aftershock.
        combo_wash_rel = 'toontown/hackslash/ComboCounterCreamWashFx.py'
        _assert_module_file(combo_wash_rel)
        combo_wash_names = _class_and_func_names(_module_ast(combo_wash_rel))
        self.assertIn('ComboCounterCreamWashPulse', combo_wash_names)
        combo_wash_methods = _class_method_names(
            _module_ast(combo_wash_rel), 'ComboCounterCreamWashPulse')
        self.assertIn('play', combo_wash_methods)
        self.assertIn('clear', combo_wash_methods)
        for combo_wash_key in (
                'COMBO_COUNTER_CREAM_WASH_ENABLED',
                'COMBO_COUNTER_CREAM_WASH_DELAY_SEC',
                'COMBO_COUNTER_CREAM_WASH_COLOR',
                'COMBO_COUNTER_CREAM_WASH_PEAK',
                'COMBO_COUNTER_CREAM_WASH_MID',
                'COMBO_COUNTER_CREAM_WASH_BIN'):
            self.assertIn(
                combo_wash_key, config_names,
                msg='HackSlashConfig missing %s' % combo_wash_key)
        hit_juice_src = _read(hit_juice_rel)
        self.assertIn('ComboCounterCreamWashPulse', hit_juice_src)
        self.assertIn('ComboCounterCreamWashPulse', hack_init)

        # (#148 / #152 were prior headless smoke through #143 / #147 — no new juice.)

        # Finale reveal cream wash (#149) — soft wash after finale cream edge.
        finale_wash_rel = 'toontown/campaign/FinaleRevealCreamWashFx.py'
        _assert_module_file(finale_wash_rel)
        finale_wash_names = _class_and_func_names(_module_ast(finale_wash_rel))
        self.assertIn('FinaleRevealCreamWashPulse', finale_wash_names)
        self.assertIn('playFinaleRevealCreamWash', finale_wash_names)
        self.assertIn('clearFinaleRevealCreamWash', finale_wash_names)
        finale_wash_methods = _class_method_names(
            _module_ast(finale_wash_rel), 'FinaleRevealCreamWashPulse')
        self.assertIn('play', finale_wash_methods)
        self.assertIn('clear', finale_wash_methods)
        for finale_wash_key in (
                'FINALE_REVEAL_CREAM_WASH_ENABLED',
                'FINALE_REVEAL_CREAM_WASH_DELAY_SEC',
                'FINALE_REVEAL_CREAM_WASH_COLOR',
                'FINALE_REVEAL_CREAM_WASH_PEAK',
                'FINALE_REVEAL_CREAM_WASH_MID',
                'FINALE_REVEAL_CREAM_WASH_BIN'):
            self.assertIn(
                finale_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % finale_wash_key)
        finale_phase_src = _read('toontown/campaign/FinalePhaseFx.py')
        self.assertIn('playFinaleRevealCreamWash', finale_phase_src)

        # Air-juggle cream wash (#150) — soft wash after hang cream aftershock.
        juggle_wash_rel = 'toontown/hackslash/CreamHangCreamWashFx.py'
        _assert_module_file(juggle_wash_rel)
        juggle_wash_names = _class_and_func_names(_module_ast(juggle_wash_rel))
        self.assertIn('CreamHangCreamWashPulse', juggle_wash_names)
        juggle_wash_methods = _class_method_names(
            _module_ast(juggle_wash_rel), 'CreamHangCreamWashPulse')
        self.assertIn('play', juggle_wash_methods)
        self.assertIn('clear', juggle_wash_methods)
        for juggle_wash_key in (
                'LAUNCH_HANG_CREAM_WASH_ENABLED',
                'LAUNCH_HANG_CREAM_WASH_DELAY_SEC',
                'LAUNCH_HANG_CREAM_WASH_COLOR',
                'LAUNCH_HANG_CREAM_WASH_PEAK',
                'LAUNCH_HANG_CREAM_WASH_MID',
                'LAUNCH_HANG_CREAM_WASH_BIN'):
            self.assertIn(
                juggle_wash_key, config_names,
                msg='HackSlashConfig missing %s' % juggle_wash_key)
        hang_sparkle_src = _read('toontown/hackslash/CreamHangSparkleFx.py')
        self.assertIn('CreamHangCreamWashPulse', hang_sparkle_src)
        self.assertIn('CreamHangCreamWashPulse', hack_init)

        # Purity-fill cream wash (#151) — soft wash after fill cream aftershock.
        purity_fill_wash_rel = 'toontown/reclaim/PurityFillCreamWashFx.py'
        _assert_module_file(purity_fill_wash_rel)
        purity_fill_wash_names = _class_and_func_names(
            _module_ast(purity_fill_wash_rel))
        self.assertIn('PurityFillCreamWashPulse', purity_fill_wash_names)
        purity_fill_wash_methods = _class_method_names(
            _module_ast(purity_fill_wash_rel), 'PurityFillCreamWashPulse')
        self.assertIn('play', purity_fill_wash_methods)
        self.assertIn('clear', purity_fill_wash_methods)
        for purity_fill_wash_key in (
                'PURITY_METER_FILL_CREAM_WASH_ENABLED',
                'PURITY_METER_FILL_CREAM_WASH_DELAY_SEC',
                'PURITY_METER_FILL_CREAM_WASH_COLOR',
                'PURITY_METER_FILL_CREAM_WASH_PEAK',
                'PURITY_METER_FILL_CREAM_WASH_MID',
                'PURITY_METER_FILL_CREAM_WASH_BIN'):
            self.assertIn(
                purity_fill_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % purity_fill_wash_key)
        purity_hud_src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('PurityFillCreamWashPulse', purity_hud_src)

        # Silhouette cream wash (#153) — soft wash against corrupt ink silhouette.
        silh_wash_rel = 'toontown/corruption/CorruptSilhouetteCreamWashFx.py'
        _assert_module_file(silh_wash_rel)
        silh_wash_names = _class_and_func_names(_module_ast(silh_wash_rel))
        self.assertIn('SilhouetteCreamWashPulse', silh_wash_names)
        self.assertIn('silhouetteCreamWashLook', silh_wash_names)
        silh_wash_methods = _class_method_names(
            _module_ast(silh_wash_rel), 'SilhouetteCreamWashPulse')
        self.assertIn('start', silh_wash_methods)
        self.assertIn('pause', silh_wash_methods)
        self.assertIn('resume', silh_wash_methods)
        self.assertIn('clear', silh_wash_methods)
        self.assertTrue(
            hasattr(cg, 'SILHOUETTE_CREAM_WASH_LOOK'),
            msg='CorruptionGlobals missing SILHOUETTE_CREAM_WASH_LOOK')
        self.assertEqual(
            cg.SILHOUETTE_CREAM_WASH_LOOK.get('id'), 'silhouette-cream-wash')
        self.assertTrue(
            hasattr(cg, 'SILHOUETTE_CREAM_WASH_ENABLED'),
            msg='CorruptionGlobals missing SILHOUETTE_CREAM_WASH_ENABLED')
        for silh_wash_key in (
                'SILHOUETTE_CREAM_WASH_ENABLED',
                'SILHOUETTE_CREAM_WASH_DELAY_SEC',
                'SILHOUETTE_CREAM_WASH_COLOR',
                'SILHOUETTE_CREAM_WASH_PEAK',
                'SILHOUETTE_CREAM_WASH_MID',
                'SILHOUETTE_CREAM_WASH_BIN'):
            self.assertTrue(
                hasattr(cg, silh_wash_key),
                msg='CorruptionGlobals missing %s' % silh_wash_key)
        self.assertIn('SilhouetteCreamWashPulse', corrupt_src)
        self.assertIn('__startSilhouetteCreamWash', corrupt_src)

        # Act-banner cream wash (#154) — soft wash after act-enter cream edge.
        act_wash_rel = 'toontown/campaign/ActBannerCreamWashFx.py'
        _assert_module_file(act_wash_rel)
        act_wash_names = _class_and_func_names(_module_ast(act_wash_rel))
        self.assertIn('ActBannerCreamWashPulse', act_wash_names)
        self.assertIn('playActBannerCreamWash', act_wash_names)
        self.assertIn('clearActBannerCreamWash', act_wash_names)
        act_wash_methods = _class_method_names(
            _module_ast(act_wash_rel), 'ActBannerCreamWashPulse')
        self.assertIn('play', act_wash_methods)
        self.assertIn('clear', act_wash_methods)
        for act_wash_key in (
                'PLAY_ENTRY_BANNER_CREAM_WASH_ENABLED',
                'PLAY_ENTRY_BANNER_CREAM_WASH_DELAY_SEC',
                'PLAY_ENTRY_BANNER_CREAM_WASH_COLOR',
                'PLAY_ENTRY_BANNER_CREAM_WASH_PEAK',
                'PLAY_ENTRY_BANNER_CREAM_WASH_MID',
                'PLAY_ENTRY_BANNER_CREAM_WASH_BIN'):
            self.assertIn(
                act_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % act_wash_key)
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('playActBannerCreamWash', play_src)

        # Soft-lock reticle cream wash (#155) — soft wash after cream pulse ring.
        reticle_wash_rel = 'toontown/hackslash/SoftLockCreamWashFx.py'
        _assert_module_file(reticle_wash_rel)
        reticle_wash_names = _class_and_func_names(_module_ast(reticle_wash_rel))
        self.assertIn('SoftLockCreamWashPulse', reticle_wash_names)
        reticle_wash_methods = _class_method_names(
            _module_ast(reticle_wash_rel), 'SoftLockCreamWashPulse')
        self.assertIn('play', reticle_wash_methods)
        self.assertIn('clear', reticle_wash_methods)
        for reticle_wash_key in (
                'SOFT_LOCK_CREAM_WASH_ENABLED',
                'SOFT_LOCK_CREAM_WASH_DELAY_SEC',
                'SOFT_LOCK_CREAM_WASH_COLOR',
                'SOFT_LOCK_CREAM_WASH_PEAK',
                'SOFT_LOCK_CREAM_WASH_MID',
                'SOFT_LOCK_CREAM_WASH_BIN'):
            self.assertIn(
                reticle_wash_key, config_names,
                msg='HackSlashConfig missing %s' % reticle_wash_key)
        reticle_src = _read('toontown/hackslash/SoftLockReticleFx.py')
        self.assertIn('SoftLockCreamWashPulse', reticle_src)
        self.assertIn('SoftLockCreamWashPulse', hack_init)

        # Wave-edge cream wash (#156) — soft wash after wave-edge cream sparkle.
        wave_edge_wash_rel = 'toontown/reclaim/WaveEdgeCreamWashFx.py'
        _assert_module_file(wave_edge_wash_rel)
        wave_edge_wash_names = _class_and_func_names(
            _module_ast(wave_edge_wash_rel))
        self.assertIn('WaveEdgeCreamWashPulse', wave_edge_wash_names)
        wave_edge_wash_methods = _class_method_names(
            _module_ast(wave_edge_wash_rel), 'WaveEdgeCreamWashPulse')
        self.assertIn('play', wave_edge_wash_methods)
        self.assertIn('clear', wave_edge_wash_methods)
        for wave_edge_wash_key in (
                'WAVE_ANNOUNCE_CREAM_EDGE_WASH_ENABLED',
                'WAVE_ANNOUNCE_CREAM_EDGE_WASH_DELAY_SEC',
                'WAVE_ANNOUNCE_CREAM_EDGE_WASH_COLOR',
                'WAVE_ANNOUNCE_CREAM_EDGE_WASH_PEAK',
                'WAVE_ANNOUNCE_CREAM_EDGE_WASH_MID',
                'WAVE_ANNOUNCE_CREAM_EDGE_WASH_BIN'):
            self.assertIn(
                wave_edge_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % wave_edge_wash_key)
        wave_burst_src = _read('toontown/reclaim/WaveCreamBurstFx.py')
        self.assertIn('WaveEdgeCreamWashPulse', wave_burst_src)

        # Telegraph cream wash (#157) — soft wash after telegraph cream sparkle.
        tel_wash_rel = 'toontown/corruption/CorruptTelegraphCreamWashFx.py'
        _assert_module_file(tel_wash_rel)
        tel_wash_names = _class_and_func_names(_module_ast(tel_wash_rel))
        self.assertIn('TelegraphCreamWashPulse', tel_wash_names)
        self.assertIn('telegraphCreamWashLook', tel_wash_names)
        tel_wash_methods = _class_method_names(
            _module_ast(tel_wash_rel), 'TelegraphCreamWashPulse')
        self.assertIn('play', tel_wash_methods)
        self.assertIn('clear', tel_wash_methods)
        self.assertTrue(
            hasattr(cg, 'TELEGRAPH_CREAM_WASH_LOOK'),
            msg='CorruptionGlobals missing TELEGRAPH_CREAM_WASH_LOOK')
        self.assertEqual(
            cg.TELEGRAPH_CREAM_WASH_LOOK.get('id'), 'telegraph-cream-wash')
        self.assertTrue(
            hasattr(cg, 'TELEGRAPH_CREAM_WASH_ENABLED'),
            msg='CorruptionGlobals missing TELEGRAPH_CREAM_WASH_ENABLED')
        for tel_wash_key in (
                'TELEGRAPH_CREAM_WASH_ENABLED',
                'TELEGRAPH_CREAM_WASH_DELAY_SEC',
                'TELEGRAPH_CREAM_WASH_COLOR',
                'TELEGRAPH_CREAM_WASH_PEAK',
                'TELEGRAPH_CREAM_WASH_MID',
                'TELEGRAPH_CREAM_WASH_BIN'):
            self.assertTrue(
                hasattr(cg, tel_wash_key),
                msg='CorruptionGlobals missing %s' % tel_wash_key)
        self.assertIn('TelegraphCreamWashPulse', corrupt_src)
        self.assertIn('__playTelegraphCreamWash', corrupt_src)

        # Punchline tip cream wash (#158) — soft wash after Punchline tip hose pop.
        tip_wash_rel = 'toontown/campaign/PunchlineTipCreamWashFx.py'
        _assert_module_file(tip_wash_rel)
        tip_wash_names = _class_and_func_names(_module_ast(tip_wash_rel))
        self.assertIn('PunchlineTipCreamWashPulse', tip_wash_names)
        self.assertIn('playPunchlineTipCreamWash', tip_wash_names)
        self.assertIn('clearPunchlineTipCreamWash', tip_wash_names)
        tip_wash_methods = _class_method_names(
            _module_ast(tip_wash_rel), 'PunchlineTipCreamWashPulse')
        self.assertIn('play', tip_wash_methods)
        self.assertIn('clear', tip_wash_methods)
        for tip_wash_key in (
                'PUNCHLINE_ACT_TIP_CREAM_WASH_ENABLED',
                'PUNCHLINE_ACT_TIP_CREAM_WASH_DELAY_SEC',
                'PUNCHLINE_ACT_TIP_CREAM_WASH_COLOR',
                'PUNCHLINE_ACT_TIP_CREAM_WASH_PEAK',
                'PUNCHLINE_ACT_TIP_CREAM_WASH_MID',
                'PUNCHLINE_ACT_TIP_CREAM_WASH_BIN',
                'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED',
                'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT',
                'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC'):
            self.assertIn(
                tip_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % tip_wash_key)
        self.assertIn('playPunchlineTipCreamWash', play_src)
        self.assertIn('PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT', play_src)
        self.assertIn('creamHoseSettle', play_src)
        magic_src_l = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('cream hose settle', magic_src_l)

        # Street cream wash aftershock (#159) — delayed residual after street wash.
        street_wash_rel = 'toontown/reclaim/StreetColorWash.py'
        street_wash_methods = _class_method_names(
            _module_ast(street_wash_rel), 'StreetColorWash')
        self.assertIn('__buildAftershock', street_wash_methods)
        self.assertIn('__spawnAftershockHalo', street_wash_methods)
        self.assertIn('__spawnAftershockFleck', street_wash_methods)
        for street_as_key in (
                'STREET_WASH_AFTERSHOCK_ENABLED',
                'STREET_WASH_AFTERSHOCK_DELAY_SEC',
                'STREET_WASH_AFTERSHOCK_COUNT',
                'STREET_WASH_AFTERSHOCK_COLOR',
                'STREET_WASH_AFTERSHOCK_HALO_ENABLED',
                'STREET_WASH_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                street_as_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % street_as_key)
        street_wash_src = _read(street_wash_rel)
        self.assertIn('STREET_WASH_AFTERSHOCK_ENABLED', street_wash_src)

        # Soft-lock FOV cream wash (#160) — soft wash after soft-lock FOV punch.
        fov_wash_rel = 'toontown/hackslash/SoftLockFovCreamWashFx.py'
        _assert_module_file(fov_wash_rel)
        fov_wash_names = _class_and_func_names(_module_ast(fov_wash_rel))
        self.assertIn('SoftLockFovCreamWashPulse', fov_wash_names)
        fov_wash_methods = _class_method_names(
            _module_ast(fov_wash_rel), 'SoftLockFovCreamWashPulse')
        self.assertIn('play', fov_wash_methods)
        self.assertIn('clear', fov_wash_methods)
        for fov_wash_key in (
                'SOFT_LOCK_FOV_CREAM_WASH_ENABLED',
                'SOFT_LOCK_FOV_CREAM_WASH_DELAY_SEC',
                'SOFT_LOCK_FOV_CREAM_WASH_COLOR',
                'SOFT_LOCK_FOV_CREAM_WASH_PEAK',
                'SOFT_LOCK_FOV_CREAM_WASH_MID',
                'SOFT_LOCK_FOV_CREAM_WASH_BIN'):
            self.assertIn(
                fov_wash_key, config_names,
                msg='HackSlashConfig missing %s' % fov_wash_key)
        reticle_src = _read('toontown/hackslash/SoftLockReticleFx.py')
        self.assertIn('SoftLockFovCreamWashPulse', reticle_src)
        self.assertIn('_armFovCreamWash', reticle_src)
        self.assertIn('SoftLockFovCreamWashPulse', hack_init)

        # Overlord hit cream wash (#161) — soft wash after Overlord hit splash.
        ol_wash_rel = 'toontown/corruption/OverlordHitCreamWashFx.py'
        _assert_module_file(ol_wash_rel)
        ol_wash_names = _class_and_func_names(_module_ast(ol_wash_rel))
        self.assertIn('OverlordHitCreamWashPulse', ol_wash_names)
        self.assertIn('overlordHitCreamWashLook', ol_wash_names)
        ol_wash_methods = _class_method_names(
            _module_ast(ol_wash_rel), 'OverlordHitCreamWashPulse')
        self.assertIn('play', ol_wash_methods)
        self.assertIn('clear', ol_wash_methods)
        self.assertTrue(
            hasattr(cg, 'OVERLORD_HIT_CREAM_WASH_LOOK'),
            msg='CorruptionGlobals missing OVERLORD_HIT_CREAM_WASH_LOOK')
        self.assertEqual(
            cg.OVERLORD_HIT_CREAM_WASH_LOOK.get('id'),
            'overlord-hit-cream-wash')
        self.assertTrue(
            hasattr(cg, 'OVERLORD_HIT_CREAM_WASH_ENABLED'),
            msg='CorruptionGlobals missing OVERLORD_HIT_CREAM_WASH_ENABLED')
        for ol_wash_key in (
                'OVERLORD_HIT_CREAM_WASH_ENABLED',
                'OVERLORD_HIT_CREAM_WASH_DELAY_SEC',
                'OVERLORD_HIT_CREAM_WASH_COLOR',
                'OVERLORD_HIT_CREAM_WASH_PEAK',
                'OVERLORD_HIT_CREAM_WASH_MID',
                'OVERLORD_HIT_CREAM_WASH_BIN'):
            self.assertTrue(
                hasattr(cg, ol_wash_key),
                msg='CorruptionGlobals missing %s' % ol_wash_key)
        self.assertIn('OverlordHitCreamWashPulse', corrupt_src)
        self.assertIn('__playOverlordHitCreamWash', corrupt_src)

        # Silly tip cream wash (#162) — soft wash after Silly tip hose pop.
        silly_tip_wash_rel = 'toontown/campaign/SillyTipCreamWashFx.py'
        _assert_module_file(silly_tip_wash_rel)
        silly_tip_wash_names = _class_and_func_names(
            _module_ast(silly_tip_wash_rel))
        self.assertIn('SillyTipCreamWashPulse', silly_tip_wash_names)
        self.assertIn('playSillyTipCreamWash', silly_tip_wash_names)
        self.assertIn('clearSillyTipCreamWash', silly_tip_wash_names)
        silly_tip_wash_methods = _class_method_names(
            _module_ast(silly_tip_wash_rel), 'SillyTipCreamWashPulse')
        self.assertIn('play', silly_tip_wash_methods)
        self.assertIn('clear', silly_tip_wash_methods)
        for silly_tip_wash_key in (
                'SILLY_ACT_TIP_CREAM_WASH_ENABLED',
                'SILLY_ACT_TIP_CREAM_WASH_DELAY_SEC',
                'SILLY_ACT_TIP_CREAM_WASH_COLOR',
                'SILLY_ACT_TIP_CREAM_WASH_PEAK',
                'SILLY_ACT_TIP_CREAM_WASH_MID',
                'SILLY_ACT_TIP_CREAM_WASH_BIN',
                'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED',
                'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT',
                'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC'):
            self.assertIn(
                silly_tip_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % silly_tip_wash_key)
        self.assertIn('playSillyTipCreamWash', play_src)
        self.assertIn('SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT', play_src)
        self.assertIn('creamHoseSettle', play_src)

        # FOV purity burst cream wash (#164) — soft wash after purity FOV punch.
        purity_fov_wash_rel = 'toontown/reclaim/PurityFovCreamWashFx.py'
        _assert_module_file(purity_fov_wash_rel)
        purity_fov_wash_names = _class_and_func_names(
            _module_ast(purity_fov_wash_rel))
        self.assertIn('PurityFovCreamWashPulse', purity_fov_wash_names)
        purity_fov_wash_methods = _class_method_names(
            _module_ast(purity_fov_wash_rel), 'PurityFovCreamWashPulse')
        self.assertIn('play', purity_fov_wash_methods)
        self.assertIn('clear', purity_fov_wash_methods)
        for purity_fov_wash_key in (
                'PURITY_FOV_CREAM_WASH_ENABLED',
                'PURITY_FOV_CREAM_WASH_DELAY_SEC',
                'PURITY_FOV_CREAM_WASH_COLOR',
                'PURITY_FOV_CREAM_WASH_PEAK',
                'PURITY_FOV_CREAM_WASH_MID',
                'PURITY_FOV_CREAM_WASH_BIN'):
            self.assertIn(
                purity_fov_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % purity_fov_wash_key)
        purity_burst_src = _read('toontown/reclaim/PurityBurstFx.py')
        self.assertIn('PurityFovCreamWashPulse', purity_burst_src)
        self.assertIn('_armFovCreamWash', purity_burst_src)

        # Smudge hit cream wash (#165) — soft wash after Smudge purple splash.
        smudge_wash_rel = 'toontown/corruption/SmudgeHitCreamWashFx.py'
        _assert_module_file(smudge_wash_rel)
        smudge_wash_names = _class_and_func_names(_module_ast(smudge_wash_rel))
        self.assertIn('SmudgeHitCreamWashPulse', smudge_wash_names)
        self.assertIn('smudgeHitCreamWashLook', smudge_wash_names)
        smudge_wash_methods = _class_method_names(
            _module_ast(smudge_wash_rel), 'SmudgeHitCreamWashPulse')
        self.assertIn('play', smudge_wash_methods)
        self.assertIn('clear', smudge_wash_methods)
        self.assertTrue(
            hasattr(cg, 'SMUDGE_HIT_CREAM_WASH_LOOK'),
            msg='CorruptionGlobals missing SMUDGE_HIT_CREAM_WASH_LOOK')
        self.assertEqual(
            cg.SMUDGE_HIT_CREAM_WASH_LOOK.get('id'),
            'smudge-hit-cream-wash')
        self.assertTrue(
            hasattr(cg, 'SMUDGE_HIT_CREAM_WASH_ENABLED'),
            msg='CorruptionGlobals missing SMUDGE_HIT_CREAM_WASH_ENABLED')
        for smudge_wash_key in (
                'SMUDGE_HIT_CREAM_WASH_ENABLED',
                'SMUDGE_HIT_CREAM_WASH_DELAY_SEC',
                'SMUDGE_HIT_CREAM_WASH_COLOR',
                'SMUDGE_HIT_CREAM_WASH_PEAK',
                'SMUDGE_HIT_CREAM_WASH_MID',
                'SMUDGE_HIT_CREAM_WASH_BIN'):
            self.assertTrue(
                hasattr(cg, smudge_wash_key),
                msg='CorruptionGlobals missing %s' % smudge_wash_key)
        self.assertIn('SmudgeHitCreamWashPulse', corrupt_src)
        self.assertIn('__playSmudgeHitCreamWash', corrupt_src)

        # Dodge i-frame cream wash (#166 deepen) — stronger wash + aftershock
        # after first i-frame pulse so invuln windows read clearly.
        iframe_wash_rel = 'toontown/hackslash/DodgeIFrameCreamWashFx.py'
        _assert_module_file(iframe_wash_rel)
        iframe_wash_names = _class_and_func_names(_module_ast(iframe_wash_rel))
        self.assertIn('DodgeIFrameCreamWashPulse', iframe_wash_names)
        iframe_wash_methods = _class_method_names(
            _module_ast(iframe_wash_rel), 'DodgeIFrameCreamWashPulse')
        self.assertIn('play', iframe_wash_methods)
        self.assertIn('clear', iframe_wash_methods)
        self.assertIn('_buildAftershock', iframe_wash_methods)
        self.assertIn('_spawnAftershockHalo', iframe_wash_methods)
        self.assertIn('_spawnAftershockFleck', iframe_wash_methods)
        for iframe_wash_key in (
                'DODGE_TRAIL_PULSE_CREAM_WASH_ENABLED',
                'DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC',
                'DODGE_TRAIL_PULSE_CREAM_WASH_COLOR',
                'DODGE_TRAIL_PULSE_CREAM_WASH_PEAK',
                'DODGE_TRAIL_PULSE_CREAM_WASH_MID',
                'DODGE_TRAIL_PULSE_CREAM_WASH_BIN',
                'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ENABLED',
                'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_COUNT',
                'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED'):
            self.assertIn(
                iframe_wash_key, config_names,
                msg='HackSlashConfig missing %s' % iframe_wash_key)
        config_funcs = _class_and_func_names(config_tree)
        self.assertIn('dodgeIFrameCreamWashPeakAtSec', config_funcs)
        dodge_trail_src = _read('toontown/hackslash/DodgeTrailFx.py')
        self.assertIn('DodgeIFrameCreamWashPulse', dodge_trail_src)
        self.assertIn('_armIFrameCreamWash', dodge_trail_src)
        self.assertIn('DodgeIFrameCreamWashPulse', hack_init)
        self.assertIn('dodgeIFrameCreamWashPeakAtSec', hack_init)

        # (#167 was prior headless smoke through #162 — no new juice symbols.)
        # (#169 was prior headless smoke through #166 — no new juice symbols.)

        # Victory cream aftershock (#168) — residual flecks + halo after victory wash.
        victory_wash_methods = _class_method_names(
            _module_ast(victory_wash_rel), 'VictoryCreamWashPulse')
        self.assertIn('_buildAftershock', victory_wash_methods)
        self.assertIn('_spawnAftershockHalo', victory_wash_methods)
        self.assertIn('_spawnAftershockFleck', victory_wash_methods)
        for victory_as_key in (
                'VICTORY_CREAM_AFTERSHOCK_ENABLED',
                'VICTORY_CREAM_AFTERSHOCK_DELAY_SEC',
                'VICTORY_CREAM_AFTERSHOCK_COUNT',
                'VICTORY_CREAM_AFTERSHOCK_COLOR',
                'VICTORY_CREAM_AFTERSHOCK_HALO_ENABLED',
                'VICTORY_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                victory_as_key, campaign_names,
                msg='CampaignGlobals missing %s' % victory_as_key)
        victory_wash_src = _read(victory_wash_rel)
        self.assertIn('VICTORY_CREAM_AFTERSHOCK_ENABLED', victory_wash_src)

        # Entry aftershock cream wash (#170) — settle wash after entry aftershock.
        entry_as_wash_rel = 'toontown/reclaim/EntryAftershockCreamWashFx.py'
        _assert_module_file(entry_as_wash_rel)
        entry_as_wash_names = _class_and_func_names(
            _module_ast(entry_as_wash_rel))
        self.assertIn('EntryAftershockCreamWashPulse', entry_as_wash_names)
        entry_as_wash_methods = _class_method_names(
            _module_ast(entry_as_wash_rel), 'EntryAftershockCreamWashPulse')
        self.assertIn('play', entry_as_wash_methods)
        self.assertIn('clear', entry_as_wash_methods)
        for entry_as_wash_key in (
                'ENTRY_AFTERSHOCK_CREAM_WASH_ENABLED',
                'ENTRY_AFTERSHOCK_CREAM_WASH_DELAY_SEC',
                'ENTRY_AFTERSHOCK_CREAM_WASH_COLOR',
                'ENTRY_AFTERSHOCK_CREAM_WASH_PEAK',
                'ENTRY_AFTERSHOCK_CREAM_WASH_MID',
                'ENTRY_AFTERSHOCK_CREAM_WASH_BIN'):
            self.assertIn(
                entry_as_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % entry_as_wash_key)
        entry_wash_src = _read(entry_wash_rel)
        self.assertIn('EntryAftershockCreamWashPulse', entry_wash_src)
        self.assertIn('ENTRY_AFTERSHOCK_CREAM_WASH_DELAY_SEC', entry_wash_src)

        # Perfect-dodge cream wash aftershock (#171) — residual after wash pulse.
        pd_wash_methods = _class_method_names(
            _module_ast(pd_wash_rel), 'PerfectDodgeCreamWashPulse')
        self.assertIn('_buildAftershock', pd_wash_methods)
        self.assertIn('_spawnAftershockHalo', pd_wash_methods)
        self.assertIn('_spawnAftershockFleck', pd_wash_methods)
        for pd_as_key in (
                'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_ENABLED',
                'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
                'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_COUNT',
                'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_COLOR',
                'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED',
                'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                pd_as_key, config_names,
                msg='HackSlashConfig missing %s' % pd_as_key)
        pd_wash_src = _read(pd_wash_rel)
        self.assertIn(
            'PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_ENABLED', pd_wash_src)

        # Corrupt death cream wash aftershock (#172) — residual after death wash.
        death_wash_methods = _class_method_names(
            _module_ast(death_wash_rel), 'DeathCreamWashPulse')
        self.assertIn('_buildAftershock', death_wash_methods)
        self.assertIn('_spawnAftershockHalo', death_wash_methods)
        self.assertIn('_spawnAftershockFleck', death_wash_methods)
        for death_as_key in (
                'DEATH_CREAM_WASH_AFTERSHOCK_ENABLED',
                'DEATH_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
                'DEATH_CREAM_WASH_AFTERSHOCK_COUNT',
                'DEATH_CREAM_WASH_AFTERSHOCK_COLOR',
                'DEATH_CREAM_WASH_AFTERSHOCK_HALO_ENABLED',
                'DEATH_CREAM_WASH_AFTERSHOCK_HALO_COLOR'):
            self.assertTrue(
                hasattr(cg, death_as_key),
                msg='CorruptionGlobals missing %s' % death_as_key)
        death_wash_src = _read(death_wash_rel)
        self.assertIn('DEATH_CREAM_WASH_AFTERSHOCK_ENABLED', death_wash_src)
        death_pop_src = _read('toontown/corruption/CorruptDeathPopFx.py')
        self.assertIn('DeathCreamWashPulse', death_pop_src)

        # (#173 was prior headless smoke through #172 — no new juice symbols.)

        # Melee hit cream wash aftershock (#174) — residual after hit wash pulse.
        hit_wash_methods = _class_method_names(
            _module_ast(hit_wash_rel), 'HitSparkCreamWashPulse')
        self.assertIn('_buildAftershock', hit_wash_methods)
        self.assertIn('_spawnAftershockHalo', hit_wash_methods)
        self.assertIn('_spawnAftershockFleck', hit_wash_methods)
        for hit_as_key in (
                'HIT_SPARK_CREAM_WASH_AFTERSHOCK_ENABLED',
                'HIT_SPARK_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
                'HIT_SPARK_CREAM_WASH_AFTERSHOCK_COUNT',
                'HIT_SPARK_CREAM_WASH_AFTERSHOCK_COLOR',
                'HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_ENABLED',
                'HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                hit_as_key, config_names,
                msg='HackSlashConfig missing %s' % hit_as_key)
        hit_wash_src = _read(hit_wash_rel)
        self.assertIn('HIT_SPARK_CREAM_WASH_AFTERSHOCK_ENABLED', hit_wash_src)
        hit_spark_src = _read('toontown/hackslash/HitSparkFx.py')
        self.assertIn('HitSparkCreamWashPulse', hit_spark_src)

        # Purity-complete aftershock cream wash (#175) — settle wash after aftershock.
        purity_as_wash_rel = (
            'toontown/reclaim/PurityCompleteAftershockCreamWashFx.py')
        _assert_module_file(purity_as_wash_rel)
        purity_as_wash_names = _class_and_func_names(
            _module_ast(purity_as_wash_rel))
        self.assertIn(
            'PurityCompleteAftershockCreamWashPulse', purity_as_wash_names)
        purity_as_wash_methods = _class_method_names(
            _module_ast(purity_as_wash_rel),
            'PurityCompleteAftershockCreamWashPulse')
        self.assertIn('play', purity_as_wash_methods)
        self.assertIn('clear', purity_as_wash_methods)
        for purity_as_wash_key in (
                'PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_ENABLED',
                'PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_DELAY_SEC',
                'PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_COLOR',
                'PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_PEAK',
                'PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_MID',
                'PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_BIN'):
            self.assertIn(
                purity_as_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % purity_as_wash_key)
        purity_wash_src = _read(purity_wash_rel)
        self.assertIn(
            'PurityCompleteAftershockCreamWashPulse', purity_wash_src)
        self.assertIn(
            'PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_DELAY_SEC', purity_wash_src)

        # Finale reveal cream wash aftershock (#176) — residual after reveal wash.
        finale_wash_methods = _class_method_names(
            _module_ast(finale_wash_rel), 'FinaleRevealCreamWashPulse')
        self.assertIn('_buildAftershock', finale_wash_methods)
        self.assertIn('_spawnAftershockHalo', finale_wash_methods)
        self.assertIn('_spawnAftershockFleck', finale_wash_methods)
        for finale_as_key in (
                'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_ENABLED',
                'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
                'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_COUNT',
                'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_COLOR',
                'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_ENABLED',
                'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                finale_as_key, campaign_names,
                msg='CampaignGlobals missing %s' % finale_as_key)
        finale_wash_src = _read(finale_wash_rel)
        self.assertIn(
            'FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_ENABLED', finale_wash_src)

        # Corrupt idle cream wash aftershock (#177) — residual after idle wash.
        idle_wash_methods = _class_method_names(
            _module_ast(idle_wash_rel), 'IdleCreamWashPulse')
        self.assertIn('_buildAftershock', idle_wash_methods)
        self.assertIn('_spawnAftershockHalo', idle_wash_methods)
        self.assertIn('_spawnAftershockFleck', idle_wash_methods)
        for idle_as_key in (
                'IDLE_CREAM_WASH_AFTERSHOCK_ENABLED',
                'IDLE_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
                'IDLE_CREAM_WASH_AFTERSHOCK_COUNT',
                'IDLE_CREAM_WASH_AFTERSHOCK_COLOR',
                'IDLE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED',
                'IDLE_CREAM_WASH_AFTERSHOCK_HALO_COLOR'):
            self.assertTrue(
                hasattr(cg, idle_as_key),
                msg='CorruptionGlobals missing %s' % idle_as_key)
        idle_wash_src = _read(idle_wash_rel)
        self.assertIn('IDLE_CREAM_WASH_AFTERSHOCK_ENABLED', idle_wash_src)
        corrupt_src = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('IdleCreamWashPulse', corrupt_src)

        # Dodge → melee cancel window — late-dodge cancel into stretch-punch.
        # Combat-feel timing (not cream FX): early roll lockout + buffer +
        # cancel-into-melee helpers on MeleeCombatController.
        for dodge_cancel_key in (
                'DODGE_CANCEL_ENABLED',
                'DODGE_CANCEL_START_SEC',
                'DODGE_CANCEL_WINDOW_SEC',
                'DODGE_CANCEL_BUFFER'):
            self.assertIn(
                dodge_cancel_key, config_names,
                msg='HackSlashConfig missing dodge cancel %s' % dodge_cancel_key)
        # Timing values (#186): commitment lockout then open cancel window.
        config_assigns = _assign_map(config_tree)
        self.assertIs(config_assigns.get('DODGE_CANCEL_ENABLED'), True)
        self.assertIs(config_assigns.get('DODGE_CANCEL_BUFFER'), True)
        start_sec = config_assigns.get('DODGE_CANCEL_START_SEC')
        window_sec = config_assigns.get('DODGE_CANCEL_WINDOW_SEC')
        dodge_dur = config_assigns.get('DODGE_DURATION_SEC')
        self.assertIsInstance(start_sec, float)
        self.assertIsInstance(window_sec, float)
        self.assertGreater(start_sec, 0.0)
        self.assertGreater(window_sec, 0.0)
        # Commitment lockout ends mid-roll; cancel stays open into recovery.
        if isinstance(dodge_dur, float):
            self.assertLess(start_sec, dodge_dur)
        dodge_cd = config_assigns.get('DODGE_COOLDOWN_SEC')
        if isinstance(dodge_cd, float):
            self.assertLessEqual(start_sec + window_sec, dodge_cd + 0.05)
        melee_tree = _module_ast('toontown/hackslash/MeleeCombat.py')
        melee_methods = _class_method_names(melee_tree, 'MeleeCombatController')
        for dodge_cancel_method in (
                '_armDodgeCancelWindow',
                '_clearDodgeCancelWindow',
                '_isInDodgeCancelLockout',
                'isDodgeCancelOpen',
                '_cancelDodgeIntoMelee',
                '_flushDodgeCancelBuffer'):
            self.assertIn(
                dodge_cancel_method, melee_methods,
                msg='MeleeCombatController missing %s' % dodge_cancel_method)
        melee_src = _read('toontown/hackslash/MeleeCombat.py')
        self.assertIn('DODGE_CANCEL_ENABLED', melee_src)
        self.assertIn('hackslash-dodge-cancel', melee_src)
        self.assertIn('dodge→F', _read('toontown/hackslash/HackSlashConfig.py'))
        # Mid-roll attack during lockout buffers; window flush starts fresh hit 0.
        self.assertIn('_flushDodgeCancelBuffer', melee_src)
        self.assertIn('_cancelDodgeIntoMelee', melee_src)

        # Perfect-dodge counter → melee — rewarded cancel window after perfect
        # dodge into a bumped/snappy stretch-punch opener (builds on #186).
        for pd_counter_key in (
                'PERFECT_DODGE_COUNTER_ENABLED',
                'PERFECT_DODGE_COUNTER_WINDOW_SEC',
                'PERFECT_DODGE_COUNTER_DAMAGE_MULT',
                'PERFECT_DODGE_COUNTER_RATE_MULT',
                'PERFECT_DODGE_COUNTER_BUFFER'):
            self.assertIn(
                pd_counter_key, config_names,
                msg='HackSlashConfig missing perfect-dodge counter %s' % (
                    pd_counter_key,))
        self.assertIs(config_assigns.get('PERFECT_DODGE_COUNTER_ENABLED'), True)
        self.assertIs(config_assigns.get('PERFECT_DODGE_COUNTER_BUFFER'), True)
        pd_window = config_assigns.get('PERFECT_DODGE_COUNTER_WINDOW_SEC')
        pd_dmg = config_assigns.get('PERFECT_DODGE_COUNTER_DAMAGE_MULT')
        pd_rate = config_assigns.get('PERFECT_DODGE_COUNTER_RATE_MULT')
        self.assertIsInstance(pd_window, float)
        self.assertIsInstance(pd_dmg, float)
        self.assertIsInstance(pd_rate, float)
        self.assertGreater(pd_window, 0.0)
        self.assertGreater(pd_dmg, 1.0)
        self.assertGreater(pd_rate, 1.0)
        config_funcs = {
            node.name for node in getattr(config_tree, 'body', [])
            if isinstance(node, ast.FunctionDef)}
        for pd_helper in (
                'perfectDodgeCounterOpenerDamage',
                'perfectDodgeCounterOpenerRate',
                'isPerfectDodgeCounterWindowOpen'):
            self.assertIn(
                pd_helper, config_funcs,
                msg='HackSlashConfig missing helper %s' % pd_helper)
        for pd_counter_method in (
                '_armPerfectDodgeCounterWindow',
                '_clearPerfectDodgeCounterWindow',
                '_consumePerfectDodgeCounter',
                'isPerfectDodgeCounterOpen',
                '_flushPerfectDodgeCounterBuffer'):
            self.assertIn(
                pd_counter_method, melee_methods,
                msg='MeleeCombatController missing %s' % pd_counter_method)
        self.assertIn('PERFECT_DODGE_COUNTER_ENABLED', melee_src)
        self.assertIn('hackslash-perfect-dodge-counter', melee_src)
        self.assertIn('_armPerfectDodgeCounterWindow', melee_src)
        self.assertIn('perfectDodgeCounterOpenerDamage', melee_src)
        config_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('perfect dodge→F counter', config_src)
        hack_init_src = _read('toontown/hackslash/__init__.py')
        self.assertIn('perfectDodgeCounterOpenerDamage', hack_init_src)
        self.assertIn('isPerfectDodgeCounterWindowOpen', hack_init_src)
        magic_src = _read('toontown/hackslash/MagicWords.py')
        self.assertIn('perfect-dodge counter', magic_src)

        # Balloon Snare string-snap counter window — after amber string
        # telegraph, short punish→melee (synergy with perfect-dodge counter).
        cg_names = set(dir(self.corruption))
        for snare_counter_key in (
                'SNARE_STRING_COUNTER_ENABLED',
                'SNARE_STRING_COUNTER_ARM_DELAY_SEC',
                'SNARE_STRING_COUNTER_WINDOW_SEC',
                'SNARE_STRING_COUNTER_RANGE',
                'SNARE_STRING_COUNTER_DAMAGE_MULT',
                'SNARE_STRING_COUNTER_RATE_MULT',
                'SNARE_STRING_COUNTER_INTERRUPT',
                'SNARE_STRING_COUNTER_EVENT',
                'SNARE_STRING_COUNTER_CREAM_SPLASH_ENABLED',
                'SNARE_STRING_COUNTER_CREAM_HIT_GRACE_SEC',
                'SNARE_STRING_COUNTER_CREAM_SPLASH_LOOK',
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_ENABLED',
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_DELAY_SEC',
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_COLOR',
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_ENABLED',
                'SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_COLOR'):
            self.assertIn(
                snare_counter_key, cg_names,
                msg='CorruptionGlobals missing snare string counter %s' % (
                    snare_counter_key,))
        self.assertIs(self.corruption.SNARE_STRING_COUNTER_ENABLED, True)
        self.assertIs(self.corruption.SNARE_STRING_COUNTER_INTERRUPT, True)
        self.assertIs(
            self.corruption.SNARE_STRING_COUNTER_CREAM_SPLASH_ENABLED, True)
        self.assertIs(
            self.corruption.SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_ENABLED,
            True)
        self.assertGreater(
            float(self.corruption.SNARE_STRING_COUNTER_ARM_DELAY_SEC), 0.0)
        self.assertGreater(
            float(self.corruption.SNARE_STRING_COUNTER_WINDOW_SEC), 0.0)
        self.assertGreater(
            float(self.corruption.SNARE_STRING_COUNTER_DAMAGE_MULT), 1.0)
        self.assertGreater(
            float(self.corruption.SNARE_STRING_COUNTER_RATE_MULT), 1.0)
        self.assertGreater(
            float(self.corruption.SNARE_STRING_COUNTER_CREAM_HIT_GRACE_SEC),
            0.0)
        self.assertEqual(
            self.corruption.SNARE_STRING_COUNTER_EVENT,
            'corruptSnareStringSnapCounter')
        for snare_helper in (
                'snareStringCounterOpenerDamage',
                'snareStringCounterOpenerRate',
                'isSnareStringCounterWindowOpen',
                'snareStringCounterArmAt',
                'snareStringCounterUntil',
                'isSnareStringCounterCreamSplashEligible'):
            self.assertTrue(
                callable(getattr(self.corruption, snare_helper, None)),
                msg='CorruptionGlobals missing helper %s' % snare_helper)
        corrupt_src = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('__scheduleSnareStringSnapCounter', corrupt_src)
        self.assertIn('__clearSnareStringSnapCounter', corrupt_src)
        self.assertIn('corruptSnareStringSnapCounter', corrupt_src)
        self.assertIn('__consumeSnareStringCounterCreamSplash', corrupt_src)
        self.assertIn('__playSnareStringCounterCreamSplash', corrupt_src)
        self.assertIn('SnareStringCounterCreamSplash', corrupt_src)
        cream_fx_src = _read(
            'toontown/corruption/SnareStringCounterCreamSplashFx.py')
        self.assertIn('class SnareStringCounterCreamSplash', cream_fx_src)
        self.assertIn('snareStringCounterCreamSplashLook', cream_fx_src)
        self.assertIn('_buildAftershock', cream_fx_src)
        cream_look_id = str(
            self.corruption.SNARE_STRING_COUNTER_CREAM_SPLASH_LOOK.get(
                'id', '')).lower()
        self.assertNotIn('keyblade', cream_look_id)
        self.assertNotIn('kingdom hearts', cream_look_id)
        corrupt_ai_src = _read(
            'toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn('__maybeInterruptSnareTelegraph', corrupt_ai_src)
        self.assertIn('SNARE_STRING_COUNTER_INTERRUPT', corrupt_ai_src)
        self.assertIn('_onSnareStringSnapCounter', melee_src)
        self.assertIn('corruptSnareStringSnapCounter', melee_src)
        self.assertIn('windowSec', melee_src)
        self.assertIn('Snare string→F counter', config_src)
        self.assertIn('Balloon Snare', magic_src)
        reclaim_md = _read('toontown/corruption/RECLAIM.md')
        self.assertIn('string-snap counter', reclaim_md)
        self.assertIn('SnareStringCounterCreamSplashFx', reclaim_md)
        corr_init = _read('toontown/corruption/__init__.py')
        self.assertIn('SnareStringCounterCreamSplashFx', corr_init)

        # Air-juggle → slam cancel window — mid-juggle hang cancel into
        # finisher slam (aerial control; builds on dodge-cancel grammar).
        for juggle_cancel_key in (
                'JUGGLE_CANCEL_ENABLED',
                'JUGGLE_CANCEL_START_SEC',
                'JUGGLE_CANCEL_WINDOW_SEC',
                'JUGGLE_CANCEL_BUFFER'):
            self.assertIn(
                juggle_cancel_key, config_names,
                msg='HackSlashConfig missing juggle cancel %s' % (
                    juggle_cancel_key,))
        self.assertIs(config_assigns.get('JUGGLE_CANCEL_ENABLED'), True)
        self.assertIs(config_assigns.get('JUGGLE_CANCEL_BUFFER'), True)
        jc_start = config_assigns.get('JUGGLE_CANCEL_START_SEC')
        jc_window = config_assigns.get('JUGGLE_CANCEL_WINDOW_SEC')
        self.assertIsInstance(jc_start, float)
        self.assertIsInstance(jc_window, float)
        self.assertGreater(jc_start, 0.0)
        self.assertGreater(jc_window, 0.0)
        # Timing lock (#196) — 0.12 rise lockout / 0.45 hang window.
        self.assertAlmostEqual(jc_start, 0.12, places=2)
        self.assertAlmostEqual(jc_window, 0.45, places=2)
        for jc_helper in (
                'juggleCancelSlamHitIndex',
                'isJuggleCancelWindowOpen'):
            self.assertIn(
                jc_helper, config_funcs,
                msg='HackSlashConfig missing helper %s' % jc_helper)
        for jc_method in (
                '_armJuggleCancelWindow',
                '_clearJuggleCancelWindow',
                '_expireJuggleCancelIfNeeded',
                '_isInJuggleCancelLockout',
                'isJuggleCancelOpen',
                '_cancelJuggleIntoSlam',
                '_flushJuggleCancelBuffer'):
            self.assertIn(
                jc_method, melee_methods,
                msg='MeleeCombatController missing %s' % jc_method)
        self.assertIn('JUGGLE_CANCEL_ENABLED', melee_src)
        self.assertIn('hackslash-juggle-cancel', melee_src)
        self.assertIn('_cancelJuggleIntoSlam', melee_src)
        self.assertIn('juggleCancelSlamHitIndex', melee_src)
        self.assertIn('_armJuggleCancelWindow', melee_src)
        self.assertIn('juggle→F slam', config_src)
        self.assertIn('juggleCancelSlamHitIndex', hack_init_src)
        self.assertIn('isJuggleCancelWindowOpen', hack_init_src)
        self.assertIn('juggle cancel', magic_src)
        # Demo hint stays rubber-hose (no KH product nouns in player-facing copy).
        demo_hint_node = _toplevel_value(config_tree, 'DEMO_HINT')
        demo_hint = _literal(demo_hint_node)
        if isinstance(demo_hint, list):
            demo_hint = ''.join(str(part) for part in demo_hint)
        self.assertIsInstance(demo_hint, str)
        hint_l = demo_hint.lower()
        self.assertIn('juggle→f slam', hint_l)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, hint_l)

        # Finisher slam FOV punch + settle — deepen slam connect impact after
        # air-juggle→slam (#196); rubber-hose undershoot then rest (no KH).
        for fov_settle_key in (
                'FINISHER_FOV_PUNCH',
                'FINISHER_FOV_IN_SEC',
                'FINISHER_FOV_OUT_SEC',
                'FINISHER_FOV_SETTLE',
                'FINISHER_FOV_SETTLE_SEC'):
            self.assertIn(
                fov_settle_key, config_names,
                msg='HackSlashConfig missing finisher FOV settle %s' % (
                    fov_settle_key,))
        fov_punch = config_assigns.get('FINISHER_FOV_PUNCH')
        fov_settle = config_assigns.get('FINISHER_FOV_SETTLE')
        fov_settle_sec = config_assigns.get('FINISHER_FOV_SETTLE_SEC')
        self.assertIsInstance(fov_punch, float)
        self.assertIsInstance(fov_settle, float)
        self.assertIsInstance(fov_settle_sec, float)
        self.assertGreater(fov_punch, 0.0)
        self.assertGreater(fov_settle, 0.0)
        self.assertLess(fov_settle, fov_punch)
        self.assertGreater(fov_settle_sec, 0.0)
        self.assertIn(
            'finisherFovPunchKeys', config_funcs,
            msg='HackSlashConfig missing finisherFovPunchKeys')
        self.assertIn(
            '_playFinisherFovPunch', melee_methods,
            msg='MeleeCombatController missing _playFinisherFovPunch')
        self.assertIn('finisherFovPunchKeys', melee_src)
        self.assertIn('FINISHER_FOV_SETTLE', melee_src)
        self.assertIn('finisherFovPunchKeys', hack_init_src)
        self.assertIn('FOV punch + settle', magic_src)

        # Hub tip discoverability (#184) — Oswald + Loopy + C, no magic words.
        hub_tip_node = _toplevel_value(self.campaign_tree, 'HUB_TIP')
        hub_tip = _literal(hub_tip_node)
        if isinstance(hub_tip, list):
            hub_tip = ''.join(str(part) for part in hub_tip)
        self.assertIsInstance(hub_tip, str)
        self.assertIn('Oswald', hub_tip)
        self.assertIn('Loopy Lane', hub_tip)
        self.assertIn('C campaign', hub_tip)
        self.assertNotIn('~startcampaign', hub_tip)

        # Soft-lock target cycle (#189) — Tab/` manual next/prev among sticky
        # hostiles. Combat-feel targeting (not cream FX): SoftTargetFinder.cycle
        # + MeleeCombatController cycle handlers.
        for target_cycle_key in (
                'TARGET_CYCLE_ENABLED',
                'TARGET_CYCLE_NEXT_KEY',
                'TARGET_CYCLE_PREV_KEY',
                'TARGET_CYCLE_COOLDOWN_SEC',
                'TARGET_CYCLE_RANGE',
                'TARGET_CYCLE_HALF_ANGLE_DEG'):
            self.assertIn(
                target_cycle_key, config_names,
                msg='HackSlashConfig missing target cycle %s' % target_cycle_key)
        # Timing / key values (#189): enabled, Tab/`, snappy cooldown, wide FOV.
        self.assertIs(config_assigns.get('TARGET_CYCLE_ENABLED'), True)
        self.assertEqual(config_assigns.get('TARGET_CYCLE_NEXT_KEY'), 'tab')
        self.assertEqual(config_assigns.get('TARGET_CYCLE_PREV_KEY'), '`')
        cycle_cd = config_assigns.get('TARGET_CYCLE_COOLDOWN_SEC')
        cycle_range = config_assigns.get('TARGET_CYCLE_RANGE')
        soft_range = config_assigns.get('TARGET_RANGE')
        self.assertIsInstance(cycle_cd, float)
        self.assertGreater(cycle_cd, 0.0)
        self.assertLessEqual(cycle_cd, 0.35)
        self.assertIsInstance(cycle_range, float)
        if isinstance(soft_range, float):
            self.assertGreaterEqual(cycle_range, soft_range)
        soft_target_tree = _module_ast('toontown/hackslash/SoftTarget.py')
        soft_target_names = _class_and_func_names(soft_target_tree)
        for cycle_helper in ('nextCycleIndex', 'pickCycleChoice'):
            self.assertIn(
                cycle_helper, soft_target_names,
                msg='SoftTarget missing cycle helper %s' % cycle_helper)
        soft_target_methods = _class_method_names(soft_target_tree, 'SoftTargetFinder')
        self.assertIn(
            'cycle', soft_target_methods,
            msg='SoftTargetFinder missing cycle()')
        for cycle_method in (
                '_onCycleNextPressed',
                '_onCyclePrevPressed',
                '_cycleSoftLockTarget'):
            self.assertIn(
                cycle_method, melee_methods,
                msg='MeleeCombatController missing %s' % cycle_method)
        self.assertIn('TARGET_CYCLE_ENABLED', melee_src)
        self.assertIn('hackslash-target-cycle', melee_src)
        self.assertIn('TARGET_CYCLE_NEXT_KEY', melee_src)
        config_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('Tab/` soft-lock cycle', config_src)
        soft_target_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('pickCycleChoice', soft_target_src)
        self.assertIn('pickCycleChoice', hack_init)
        self.assertIn('nextCycleIndex', hack_init)

        # Soft-lock cycle reticle pulse — brief hose pulse + short cream ring
        # when Tab/` switches lock (lighter than acquire snap FOV/wash).
        for cycle_pulse_key in (
                'SOFT_LOCK_CYCLE_PULSE_ENABLED',
                'SOFT_LOCK_CYCLE_PULSE_SQUASH',
                'SOFT_LOCK_CYCLE_PULSE_STRETCH',
                'SOFT_LOCK_CYCLE_PULSE_SETTLE_SEC',
                'SOFT_LOCK_CYCLE_PULSE_RING_ENABLED',
                'SOFT_LOCK_CYCLE_PULSE_RING_PEAK',
                'SOFT_LOCK_CYCLE_PULSE_RING_SEC',
                'SOFT_LOCK_CYCLE_PULSE_RING_PEAK_ALPHA'):
            self.assertIn(
                cycle_pulse_key, config_names,
                msg='HackSlashConfig missing cycle pulse %s' % cycle_pulse_key)
        self.assertIs(config_assigns.get('SOFT_LOCK_CYCLE_PULSE_ENABLED'), True)
        self.assertIs(
            config_assigns.get('SOFT_LOCK_CYCLE_PULSE_RING_ENABLED'), True)
        self.assertIn(
            'softLockCyclePulseScaleKeys', config_funcs,
            msg='HackSlashConfig missing softLockCyclePulseScaleKeys')
        self.assertIn('softLockCyclePulseScaleKeys', hack_init)
        reticle_tree = _module_ast('toontown/hackslash/SoftLockReticleFx.py')
        reticle_methods = _class_method_names(reticle_tree, 'SoftLockReticleFx')
        self.assertIn(
            'playCyclePulse', reticle_methods,
            msg='SoftLockReticleFx missing playCyclePulse')
        self.assertIn('_playCyclePulseRing', reticle_methods)
        hit_juice_src = _read('toontown/hackslash/HitJuice.py')
        self.assertIn('playSoftLockCyclePulse', hit_juice_src)
        self.assertIn('cycled=', melee_src)
        self.assertIn('SOFT_LOCK_CYCLE_PULSE_ENABLED', config_src)
        self.assertIn('Tab/` soft-lock cycle pulse', config_src)

        # Soft-lock hit assist — one-shot yaw/aim nudge on melee connect
        # against the sticky soft-lock (combat feel, not cream FX).
        for hit_assist_key in (
                'LOCK_HIT_ASSIST_ENABLED',
                'LOCK_HIT_ASSIST_YAW_FRAC',
                'LOCK_HIT_ASSIST_YAW_MAX_DEG',
                'LOCK_HIT_ASSIST_CAM_FRAC',
                'LOCK_HIT_ASSIST_DEADZONE_DEG'):
            self.assertIn(
                hit_assist_key, config_names,
                msg='HackSlashConfig missing hit assist %s' % hit_assist_key)
        self.assertIs(config_assigns.get('LOCK_HIT_ASSIST_ENABLED'), True)
        yaw_frac = config_assigns.get('LOCK_HIT_ASSIST_YAW_FRAC')
        yaw_max = config_assigns.get('LOCK_HIT_ASSIST_YAW_MAX_DEG')
        self.assertIsInstance(yaw_frac, float)
        self.assertGreater(yaw_frac, 0.0)
        self.assertLessEqual(yaw_frac, 1.0)
        self.assertIsInstance(yaw_max, float)
        self.assertGreater(yaw_max, 0.0)
        self.assertLess(yaw_max, 90.0)
        for assist_helper in (
                'signedYawDeltaDeg',
                'assistAimYawNudge',
                'shouldAssistAimOnHit'):
            self.assertIn(
                assist_helper, soft_target_names,
                msg='SoftTarget missing hit assist helper %s' % assist_helper)
            self.assertIn(assist_helper, hack_init)
        self.assertIn(
            '_assistAimOnHit', melee_methods,
            msg='MeleeCombatController missing _assistAimOnHit')
        self.assertIn('LOCK_HIT_ASSIST_ENABLED', melee_src)
        self.assertIn('_assistAimOnHit', melee_src)
        self.assertIn('hit soft-lock aim', config_src)

        # Mid-act Oswald trust fracture (#190) + Punchline deepen unease tip
        # (#198). Finale stays sunny (no fracture) — foreshadow only.
        acts_node = _toplevel_value(self.campaign_tree, 'ACTS')
        acts = [_literal(elt) for elt in acts_node.elts]
        loopy_act = next(
            (a for a in acts if isinstance(a, dict) and a.get('id') == 'loopy'),
            None)
        punch_act = next(
            (a for a in acts if isinstance(a, dict) and a.get('id') == 'punchline'),
            None)
        finale_act = next(
            (a for a in acts if isinstance(a, dict) and a.get('id') == 'finale'),
            None)
        self.assertIsNotNone(loopy_act)
        self.assertIsNotNone(punch_act)
        self.assertIsNotNone(finale_act)
        self.assertIs(loopy_act.get('trustFracture'), True)
        self.assertIs(punch_act.get('trustFracture'), True)
        self.assertFalse(bool(finale_act.get('trustFracture')))
        handoff = loopy_act.get('handoff') or ''
        if isinstance(handoff, list):
            handoff = ''.join(str(part) for part in handoff)
        self.assertIn('rubbery beat', str(handoff).lower())
        punch_handoff = punch_act.get('handoff') or ''
        if isinstance(punch_handoff, list):
            punch_handoff = ''.join(str(part) for part in punch_handoff)
        punch_tip = punch_act.get('entryTip') or ''
        if isinstance(punch_tip, list):
            punch_tip = ''.join(str(part) for part in punch_tip)
        punch_cue = punch_act.get('nextCue') or ''
        if isinstance(punch_cue, list):
            punch_cue = ''.join(str(part) for part in punch_cue)
        self.assertIn('rubbery again', str(punch_handoff).lower())
        self.assertIn('half-beat off', str(punch_tip).lower())
        self.assertIn('half-beat late', str(punch_cue).lower())
        # Combat cues stay on Punchline tip while cheer feels off.
        tip_l = str(punch_tip).lower()
        self.assertIn('gunk gagster', tip_l)
        self.assertIn('reclaim', tip_l)
        for banned in (
                'keyblade', 'kingdom hearts', 'caused the corruption', 'sora'):
            self.assertNotIn(banned, str(punch_handoff).lower())
            self.assertNotIn(banned, tip_l)
            self.assertNotIn(banned, str(punch_cue).lower())
        for fracture_key in (
                'OSWALD_TRUST_FRACTURE_CREAM_EDGE_ENABLED',
                'OSWALD_TRUST_FRACTURE_CREAM_EDGE_HOLD_SEC',
                'OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_COUNT',
                'OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC',
                'OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT'):
            self.assertIn(
                fracture_key, _toplevel_assign_names(self.campaign_tree),
                msg='CampaignGlobals missing %s' % fracture_key)
        campaign_assigns = _assign_map(self.campaign_tree)
        self.assertIs(
            campaign_assigns.get('OSWALD_TRUST_FRACTURE_CREAM_EDGE_ENABLED'),
            True)
        fracture_rest = campaign_assigns.get(
            'OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC')
        if isinstance(fracture_rest, float):
            self.assertGreaterEqual(fracture_rest, 0.10)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('trustFracture', handoff_src)
        self.assertIn('playOswaldTrustFractureCreamEdge', handoff_src)
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT', play_src)
        # Punchline tipHose uses fracture settle when trustFracture is armed.
        tip_idx = play_src.find('def _tipHosePopInterval')
        self.assertGreater(tip_idx, 0)
        punch_idx = play_src.find("tipHose == 'punchline'", tip_idx)
        silly_idx = play_src.find("tipHose == 'silly'", tip_idx)
        self.assertGreater(punch_idx, 0)
        self.assertGreater(silly_idx, punch_idx)
        punch_snip = play_src[punch_idx:silly_idx]
        self.assertIn("punchAct.get('trustFracture')", punch_snip)
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC', punch_snip)
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT', punch_snip)
        edge_fx_names = _class_and_func_names(
            _module_ast('toontown/campaign/ActBannerCreamEdgeFx.py'))
        self.assertIn('playOswaldTrustFractureCreamEdge', edge_fx_names)
        self.assertIn('clearOswaldTrustFractureCreamEdge', edge_fx_names)
        camp_magic_src = _read('toontown/campaign/MagicWords.py')
        camp_magic_l = camp_magic_src.lower()
        self.assertIn('tip unease', camp_magic_l)
        self.assertIn('punchline', camp_magic_l)
        self.assertIn('almost confess', camp_magic_l)
        self.assertIn('no keyblades', camp_magic_l)
        self.assertNotIn('kingdom hearts', camp_magic_l)
        # Silly tipHose fracture settle when entryTipUnease (#200).
        silly_else = play_src.find('\n        else:', silly_idx)
        silly_end = silly_else if silly_else > silly_idx else silly_idx + 1600
        silly_snip = play_src[silly_idx:silly_end]
        self.assertIn("sillyAct.get('entryTipUnease')", silly_snip)
        self.assertIn('OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT', silly_snip)
        self.assertIn('SILLY_ACT_TIP_TRUST_SETTLE_OVERSHOOT', silly_snip)
        # Mid-act almost-confess approach tip before finale reveal.
        finale_approach = finale_act.get('approachTip') or ''
        if isinstance(finale_approach, list):
            finale_approach = ''.join(str(part) for part in finale_approach)
        self.assertIn('almost confess', str(finale_approach).lower())
        self.assertTrue(finale_act.get('entryTipUnease'))
        self.assertIn('_armSillyApproachTip', play_src)
        self.assertIn('SILLY_APPROACH_TIP_DELAY_SEC', campaign_names)

        # Finale betrayal handoff banner — hose-pop plate when reveal fires.
        self.assertTrue(finale_act.get('betrayalHandoff'))
        for betrayal_key in (
                'FINALE_BETRAYAL_HANDOFF_CUE',
                'FINALE_BETRAYAL_HANDOFF_HOLD_SEC',
                'FINALE_BETRAYAL_SETTLE_OVERSHOOT',
                'FINALE_BETRAYAL_SETTLE_REST_SEC',
                'FINALE_BETRAYAL_SUB_COLOR',
                'FINALE_BETRAYAL_CUE_COLOR',
                'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_ENABLED',
                'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT',
                'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REST_SEC'):
            self.assertIn(
                betrayal_key, campaign_names,
                msg='CampaignGlobals missing %s' % betrayal_key)
        self.assertIn('oswaldRevealBanner', handoff_src)
        self.assertIn('_onOswaldBetrayalBanner', handoff_src)
        self.assertIn('_showBetrayalHandoff', handoff_src)
        self.assertIn('betrayalHandoff', handoff_src)
        self.assertIn('FINALE_BETRAYAL_SETTLE_OVERSHOOT', handoff_src)
        self.assertIn('FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT', handoff_src)
        # Victory/confetti Oswald twist sting — bittersweet chips on betrayal.
        for twist_key in (
                'VICTORY_TWIST_CONFETTI_ENABLED',
                'VICTORY_TWIST_CONFETTI_COUNT',
                'VICTORY_TWIST_CONFETTI_ORIGIN',
                'VICTORY_TWIST_CONFETTI_COLORS',
                'VICTORY_TWIST_CONFETTI_DELAY_SEC'):
            self.assertIn(
                twist_key, campaign_names,
                msg='CampaignGlobals missing %s' % twist_key)
        twist_rel = 'toontown/campaign/VictoryTwistConfettiSting.py'
        _assert_module_file(twist_rel)
        twist_names = _class_and_func_names(_module_ast(twist_rel))
        self.assertIn('VictoryTwistConfettiSting', twist_names)
        self.assertIn('playVictoryTwistConfettiSting', twist_names)
        self.assertIn('clearVictoryTwistConfettiSting', twist_names)
        self.assertIn('playVictoryTwistConfettiSting', handoff_src)
        self.assertIn('clearVictoryTwistConfettiSting', handoff_src)
        finale_fx_src = _read('toontown/campaign/FinalePhaseFx.py')
        self.assertIn('ensureCampaignHandoffClient', finale_fx_src)
        self.assertIn('betrayal handoff', camp_magic_l)
        self.assertIn('cream hose settle', camp_magic_l)
        self.assertIn('confetti twist sting', camp_magic_l)
        betrayal_cue = campaign_assigns.get('FINALE_BETRAYAL_HANDOFF_CUE') or ''
        if isinstance(betrayal_cue, list):
            betrayal_cue = ''.join(str(part) for part in betrayal_cue)
        betrayal_cue_l = str(betrayal_cue).lower()
        self.assertIn('smile', betrayal_cue_l)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, betrayal_cue_l)

        # TTC polluted tunnel placemarkers (#192) — hub discoverability.
        crumb_rel = 'toontown/safezone/CorruptStreetBreadcrumb.py'
        _assert_module_file(crumb_rel)
        crumb_names = _class_and_func_names(_module_ast(crumb_rel))
        for crumb_sym in (
                'reclaimStreetEntries',
                'streetNeedsBreadcrumb',
                'placemarkerPulseParams',
                'placemarkerPulseCreamParams',
                'streetBreadcrumbPulseParams',
                'playgroundFogEdgePulseParams',
                'CorruptStreetBreadcrumb',
                'ensureCorruptStreetBreadcrumbs',
                'stopCorruptStreetBreadcrumbs'):
            self.assertIn(
                crumb_sym, crumb_names,
                msg='CorruptStreetBreadcrumb missing %s' % crumb_sym)
        crumb_src = _read(crumb_rel)
        self.assertIn('Ink stains Loopy', crumb_src)
        self.assertIn('streetNeedsBreadcrumb', crumb_src)
        # Brief pulse / cream highlight so reclaim tunnels catch the eye.
        self.assertIn('_startPulseLoop', crumb_src)
        self.assertIn('_PULSE_HIGHLIGHT', crumb_src)
        # Cream deepen on placemarker pulse (local halo, not birds wash).
        self.assertIn('_PULSE_CREAM_MID', crumb_src)
        self.assertIn('_attachPulseCreamHalo', crumb_src)
        self.assertIn('corruptStreetPlacemarkerCreamHalo', crumb_src)
        # Distinct tunnel-mouth crumb trail pulse (playground-side cue).
        self.assertIn('_startCrumbPulseLoop', crumb_src)
        self.assertIn('_CRUMB_PULSE_GAP_SEC', crumb_src)
        # Playground pollution fog edge breath (distinct from #211 / #216).
        self.assertIn('_startFogPulseLoop', crumb_src)
        self.assertIn('_FOG_PULSE_GAP_SEC', crumb_src)
        self.assertIn('playgroundPollutionFogEdge', crumb_src)
        # Birds-return cream wash on hub pollution clear (pairs with #55).
        birds_wash_rel = 'toontown/safezone/BirdsReturnCreamWashFx.py'
        _assert_module_file(birds_wash_rel)
        birds_wash_names = _class_and_func_names(_module_ast(birds_wash_rel))
        for birds_sym in (
                'birdsReturnCreamWashParams',
                'shouldPlayBirdsReturnCreamWash',
                'BirdsReturnCreamWashPulse',
                'playBirdsReturnCreamWash',
                'clearBirdsReturnCreamWash'):
            self.assertIn(
                birds_sym, birds_wash_names,
                msg='BirdsReturnCreamWashFx missing %s' % birds_sym)
        self.assertIn('_cueBirdsReturnCreamWash', crumb_src)
        self.assertIn('playBirdsReturnCreamWash', crumb_src)
        playground_src = _read('toontown/safezone/TTPlayground.py')
        self.assertIn('ensureCorruptStreetBreadcrumbs', playground_src)
        self.assertIn('stopCorruptStreetBreadcrumbs', playground_src)

        # Perfect-dodge counter (#193) timing lock — window fits dodge beat.
        self.assertAlmostEqual(pd_window, 0.50, places=2)
        self.assertAlmostEqual(pd_dmg, 1.5, places=2)
        self.assertAlmostEqual(pd_rate, 1.2, places=2)
        if isinstance(dodge_cd, float):
            self.assertLessEqual(pd_window, dodge_cd + 0.05)

        # Mid-wave purity pressure tip — contested whisper after re-creep #194.
        for pressure_key in (
                'PURITY_PRESSURE_TIP_ENABLED',
                'PURITY_PRESSURE_STALL_SEC',
                'PURITY_PRESSURE_RISE_THRESHOLD',
                'PURITY_PRESSURE_COOLDOWN_SEC',
                'PURITY_PRESSURE_TIP_STALL',
                'PURITY_PRESSURE_TIP_RISE',
                'PURITY_PRESSURE_RIM_WARN_COLOR',
                'PURITY_PRESSURE_RIM_FLASH_ENABLED',
                'PURITY_PRESSURE_RIM_FLASH_PULSES',
                'PURITY_PRESSURE_RIM_FLASH_HOLD_SEC',
                'PURITY_PRESSURE_RIM_FLASH_SCALE'):
            self.assertIn(
                pressure_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % pressure_key)
        pressure_helpers = _class_and_func_names(self.reclaim_tree)
        for pressure_helper in (
                'isMidWavePressureContext',
                'purityPressureReason',
                'purityPressureTipText'):
            self.assertIn(
                pressure_helper, pressure_helpers,
                msg='ReclaimGlobals missing %s' % pressure_helper)
        pressure_assigns = _assign_map(self.reclaim_tree)
        self.assertIs(
            pressure_assigns.get('PURITY_PRESSURE_TIP_ENABLED'), True)
        stall_tip = str(
            pressure_assigns.get('PURITY_PRESSURE_TIP_STALL', '')).lower()
        rise_tip = str(
            pressure_assigns.get('PURITY_PRESSURE_TIP_RISE', '')).lower()
        self.assertIn('purity', stall_tip)
        self.assertIn('ink', rise_tip)
        self.assertIn('contested', rise_tip)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, stall_tip)
            self.assertNotIn(banned, rise_tip)
        pressure_director_src = _read(
            'toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('__evaluatePurityPressure', pressure_director_src)
        self.assertIn('__showPressureTip', pressure_director_src)
        self.assertIn('warnPressure', pressure_director_src)
        pressure_hud_methods = _class_method_names(
            _module_ast('toontown/reclaim/PurityMeterHud.py'), 'PurityMeterHud')
        self.assertIn('warnPressure', pressure_hud_methods)
        self.assertIn('_buildRimWarnPulse', pressure_hud_methods)
        self.assertIs(
            pressure_assigns.get('PURITY_PRESSURE_RIM_FLASH_ENABLED'), True)
        self.assertGreaterEqual(
            int(pressure_assigns.get('PURITY_PRESSURE_RIM_FLASH_PULSES', 0)), 2)
        pressure_hud_src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('PURITY_PRESSURE_RIM_FLASH', pressure_hud_src)
        self.assertIn('_buildRimWarnPulse', pressure_hud_src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HeadlessLoopSmokeTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Allow `python3 tests/test_headless_loop_smoke.py` without package install.
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
