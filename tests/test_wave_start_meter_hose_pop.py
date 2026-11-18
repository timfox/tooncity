#!/usr/bin/env python3
"""Behavioral headless tests for wave-start purity meter hose pop cream.

Imports ReclaimGlobals with a ToontownGlobals stub (no Panda3D). Asserts
deepened WAVE_START_METER_POP / CREAM tunables, rubber-hose (non-KH) copy,
and AST hooks on PurityMeterHud + reclaim director announcePackSpawn.
Distinct from rim-flash cream deepen (#234), wave-clear sparkle (#229),
and purity-complete hose settle (#225).

Run from repo root:
  python3 tests/test_wave_start_meter_hose_pop.py
  python3 -m unittest tests.test_wave_start_meter_hose_pop -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_reclaim_globals():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.toonbase', 'toontown.reclaim'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = 2200
    tg.PunchlinePlace = 2300
    tg.SillyStreet = 2100
    tg.ToontownCentral = 2000
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
    rg_spec = importlib.util.spec_from_file_location(
        'toontown.reclaim.ReclaimGlobals', rg_path)
    rg = importlib.util.module_from_spec(rg_spec)
    assert rg_spec.loader is not None
    sys.modules['toontown.reclaim.ReclaimGlobals'] = rg
    rg_spec.loader.exec_module(rg)
    sys.modules['toontown.reclaim'].ReclaimGlobals = rg
    return rg


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    return set()


class WaveStartMeterHosePopTest(unittest.TestCase):
    """Pure-Python wave-start meter hose-pop wiring."""

    @classmethod
    def setUpClass(cls):
        cls.rg = _load_reclaim_globals()

    def test_wave_start_meter_pop_tunables_enabled(self):
        rg = self.rg
        self.assertIs(rg.WAVE_START_METER_POP_ENABLED, True)
        self.assertIs(rg.WAVE_START_METER_CREAM_ENABLED, True)
        self.assertGreater(float(rg.WAVE_START_METER_POP_SETTLE_SEC), 0.10)
        self.assertGreaterEqual(float(rg.WAVE_START_METER_RIM_SEC), 0.26)
        squash = rg.WAVE_START_METER_POP_SQUASH
        stretch = rg.WAVE_START_METER_POP_STRETCH
        self.assertEqual(len(squash), 4)
        self.assertEqual(len(stretch), 4)
        # Hose squash flattens Z; stretch overshoots Z — classic rubber-hose.
        self.assertLess(float(squash[2]), 0.60)  # deepened flat squash
        self.assertGreater(float(stretch[2]), 1.30)  # deepened tall stretch
        # Cream flecks / halo deepen (rising begin juice, not warn rim cream).
        self.assertGreaterEqual(int(rg.WAVE_START_METER_CREAM_COUNT), 6)
        self.assertGreater(float(rg.WAVE_START_METER_CREAM_RISE), 0.0)
        self.assertTrue(rg.WAVE_START_METER_CREAM_HALO_ENABLED)

    def test_rim_accent_is_sunny_not_warn_or_secured_green(self):
        rg = self.rg
        start = rg.WAVE_START_METER_RIM_COLOR
        warn = rg.PURITY_PRESSURE_RIM_WARN_COLOR
        lock = rg.SECURED_LOCK_RIM_COLOR
        cream = rg.WAVE_START_METER_CREAM_COLOR
        self.assertNotEqual(tuple(start), tuple(warn))
        self.assertNotEqual(tuple(start), tuple(lock))
        # Sunny cream: R and G high, B lower — not warm-orange warn (R>>G)
        # and not green lock (G>>R).
        self.assertGreater(float(start[0]), 0.9)
        self.assertGreater(float(start[1]), 0.9)
        self.assertLess(float(start[2]), float(start[1]))
        self.assertGreaterEqual(float(start[3]), 0.85)  # creamier rim alpha
        self.assertGreater(float(warn[0]), float(warn[1]))  # warm warn
        self.assertGreater(float(lock[1]), float(lock[0]))  # green lock
        # Rising begin flecks stay sunny (high G), not warm warn cream.
        self.assertGreater(float(cream[1]), 0.95)
        self.assertNotEqual(
            tuple(cream), tuple(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_COLOR))

    def test_no_kh_branding_in_wave_start_tunables(self):
        banned = ('keyblade', 'kingdom hearts', 'sora', 'heartless', 'kh ')
        blob = ' '.join([
            str(self.rg.WAVE_START_METER_POP_ENABLED),
            str(self.rg.WAVE_START_METER_RIM_COLOR),
            str(self.rg.WAVE_START_METER_CREAM_COLOR),
            'wave start meter hose pop sunny cream deepen',
        ]).lower()
        for term in banned:
            self.assertNotIn(term, blob)

    def test_purity_meter_hud_has_pop_wave_start(self):
        tree = _module_ast('toontown/reclaim/PurityMeterHud.py')
        methods = _class_method_names(tree, 'PurityMeterHud')
        self.assertIn('popWaveStart', methods)
        self.assertIn('_buildWaveStartCreamJuice', methods)
        self.assertIn('_spawnWaveStartCreamFlecks', methods)
        self.assertIn('_spawnWaveStartCreamHalo', methods)
        self.assertIn('_resetRootScale', methods)
        self.assertIn('warnPressure', methods)
        self.assertIn('confirmSecured', methods)
        src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('WAVE_START_METER_POP', src)
        self.assertIn('WAVE_START_METER_CREAM', src)
        self.assertIn('reclaimPurityMeterWaveStartHose', src)
        self.assertIn('reclaimPurityMeterWaveStartCream', src)
        # Wave-start hose stays distinct from secured / warn / clear / settle.
        pop_snip = src.split('def popWaveStart')[1].split('def warnPressure')[0]
        self.assertNotIn('SECURED_LOCK_RIM_COLOR', pop_snip)
        self.assertNotIn('PURITY_PRESSURE_RIM_WARN_COLOR', pop_snip)
        self.assertNotIn('WAVE_CLEAR_CREAM_SPARKLE', pop_snip)
        self.assertNotIn('PURITY_COMPLETE_METER_SETTLE', pop_snip)
        self.assertIn('WAVE_START_METER_POP_SQUASH', pop_snip)
        self.assertIn('WAVE_START_METER_POP_STRETCH', pop_snip)
        self.assertIn('_buildWaveStartCreamJuice', pop_snip)

    def test_director_announce_pack_spawn_calls_pop_wave_start(self):
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirector.py')
        methods = _class_method_names(tree, 'DistributedReclaimDirector')
        self.assertIn('announcePackSpawn', methods)
        src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        announce_idx = src.find('def announcePackSpawn')
        next_def = src.find('\n    def ', announce_idx + 1)
        snip = src[announce_idx:next_def]
        self.assertIn('popWaveStart', snip)
        self.assertIn('reclaimWaveAnnounce', snip)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        WaveStartMeterHosePopTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
