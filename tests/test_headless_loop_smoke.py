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


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HeadlessLoopSmokeTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Allow `python3 tests/test_headless_loop_smoke.py` without package install.
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
