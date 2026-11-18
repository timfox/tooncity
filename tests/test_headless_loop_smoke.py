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
                'HANDOFF_CREAM_EDGE_SPARKLE_ENABLED'):
            self.assertIn(
                handoff_edge_key, campaign_names,
                msg='CampaignGlobals missing %s' % handoff_edge_key)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playHandoffCreamEdge', handoff_src)
        self.assertIn('confetti=True', handoff_src)

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
        for wave_wash_key in (
                'WAVE_CLEAR_CREAM_WASH_ENABLED',
                'WAVE_CLEAR_CREAM_WASH_DELAY_SEC',
                'WAVE_CLEAR_CREAM_WASH_COLOR',
                'WAVE_CLEAR_CREAM_WASH_PEAK',
                'WAVE_CLEAR_CREAM_WASH_MID',
                'WAVE_CLEAR_CREAM_WASH_BIN'):
            self.assertIn(
                wave_wash_key, reclaim_names,
                msg='ReclaimGlobals missing %s' % wave_wash_key)
        wave_shimmer_src = _read(shimmer_rel)
        self.assertIn('WaveClearCreamWashPulse', wave_shimmer_src)

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
                'PUNCHLINE_ACT_TIP_CREAM_WASH_BIN'):
            self.assertIn(
                tip_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % tip_wash_key)
        self.assertIn('playPunchlineTipCreamWash', play_src)

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
                'SILLY_ACT_TIP_CREAM_WASH_BIN'):
            self.assertIn(
                silly_tip_wash_key, campaign_names,
                msg='CampaignGlobals missing %s' % silly_tip_wash_key)
        self.assertIn('playSillyTipCreamWash', play_src)

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

        # Dodge i-frame cream wash (#166) — soft wash after first i-frame pulse.
        iframe_wash_rel = 'toontown/hackslash/DodgeIFrameCreamWashFx.py'
        _assert_module_file(iframe_wash_rel)
        iframe_wash_names = _class_and_func_names(_module_ast(iframe_wash_rel))
        self.assertIn('DodgeIFrameCreamWashPulse', iframe_wash_names)
        iframe_wash_methods = _class_method_names(
            _module_ast(iframe_wash_rel), 'DodgeIFrameCreamWashPulse')
        self.assertIn('play', iframe_wash_methods)
        self.assertIn('clear', iframe_wash_methods)
        for iframe_wash_key in (
                'DODGE_TRAIL_PULSE_CREAM_WASH_ENABLED',
                'DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC',
                'DODGE_TRAIL_PULSE_CREAM_WASH_COLOR',
                'DODGE_TRAIL_PULSE_CREAM_WASH_PEAK',
                'DODGE_TRAIL_PULSE_CREAM_WASH_MID',
                'DODGE_TRAIL_PULSE_CREAM_WASH_BIN'):
            self.assertIn(
                iframe_wash_key, config_names,
                msg='HackSlashConfig missing %s' % iframe_wash_key)
        dodge_trail_src = _read('toontown/hackslash/DodgeTrailFx.py')
        self.assertIn('DodgeIFrameCreamWashPulse', dodge_trail_src)
        self.assertIn('_armIFrameCreamWash', dodge_trail_src)
        self.assertIn('DodgeIFrameCreamWashPulse', hack_init)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HeadlessLoopSmokeTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Allow `python3 tests/test_headless_loop_smoke.py` without package install.
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
