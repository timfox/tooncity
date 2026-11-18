#!/usr/bin/env python3
"""Behavioral headless tests for mid-wave purity pressure tip / rim flash.

Imports ReclaimGlobals with a ToontownGlobals stub (no Panda3D). Asserts
isMidWavePressureContext / purityPressureReason / tip copy, further-deepened
rim flash cream tunables past #275, plus AST hooks on
DistributedReclaimDirector + PurityMeterHud. Distinct from wave-clear
sparkle (#297), lock celebration, wave-start hose, and purity-complete
meter hose settle.

Run from repo root:
  python3 tests/test_purity_pressure_tip.py
  python3 -m unittest tests.test_purity_pressure_tip -v
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


def _load_panda_free_reclaim():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = 2200
    tg.PunchlinePlace = 2300
    tg.SillyStreet = 2100
    tg.ToontownCentral = 2000
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


class PurityPressureTipTest(unittest.TestCase):
    """Pure-Python mid-wave pressure tip helpers + client wiring."""

    @classmethod
    def setUpClass(cls):
        cls.rg = _load_panda_free_reclaim()

    def test_mid_wave_context_requires_active_packs(self):
        rg = self.rg
        self.assertFalse(
            rg.isMidWavePressureContext(rg.STATE_IDLE, 2, 3))
        self.assertFalse(
            rg.isMidWavePressureContext(rg.STATE_ACTIVE, 0, 3))
        self.assertFalse(
            rg.isMidWavePressureContext(rg.STATE_ACTIVE, 2, 0))
        self.assertTrue(
            rg.isMidWavePressureContext(rg.STATE_ACTIVE, 1, 1))
        self.assertTrue(
            rg.isMidWavePressureContext(rg.STATE_ACTIVE, 3, 4))

    def test_rise_beats_stall_and_disabled_is_silent(self):
        rg = self.rg
        self.assertEqual(
            rg.purityPressureReason(0.05, 0.0),
            rg.PURITY_PRESSURE_REASON_RISE)
        self.assertEqual(
            rg.purityPressureReason(0.05, 99.0),
            rg.PURITY_PRESSURE_REASON_RISE)
        self.assertEqual(
            rg.purityPressureReason(0.0, rg.PURITY_PRESSURE_STALL_SEC),
            rg.PURITY_PRESSURE_REASON_STALL)
        self.assertIsNone(
            rg.purityPressureReason(0.01, rg.PURITY_PRESSURE_STALL_SEC - 0.1))
        self.assertIsNone(
            rg.purityPressureReason(0.5, 99.0, enabled=False))

    def test_tip_copy_is_rubber_hose_not_kh(self):
        rg = self.rg
        stall = rg.purityPressureTipText(rg.PURITY_PRESSURE_REASON_STALL).lower()
        rise = rg.purityPressureTipText(rg.PURITY_PRESSURE_REASON_RISE).lower()
        self.assertIn('purity', stall)
        self.assertIn('ink', rise)
        self.assertIn('contested', rise)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, stall)
            self.assertNotIn(banned, rise)

    def test_director_client_pressure_hooks(self):
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirector.py')
        methods = _class_method_names(tree, 'DistributedReclaimDirector')
        for name in (
                '__armPurityPressure',
                '__evaluatePurityPressure',
                '__showPressureTip',
                '__hidePressureTip',
                '__ensurePressureWatch',
                '__stopPressureWatch'):
            self.assertIn(
                name, methods,
                msg='DistributedReclaimDirector missing %s' % name)
        src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('purityPressureReason', src)
        self.assertIn('purityPressureTipText', src)
        self.assertIn('warnPressure', src)
        self.assertIn('isMidWavePressureContext', src)

    def test_purity_meter_warn_pressure_hook(self):
        tree = _module_ast('toontown/reclaim/PurityMeterHud.py')
        methods = _class_method_names(tree, 'PurityMeterHud')
        self.assertIn('warnPressure', methods)
        self.assertIn('_clearPressureWarn', methods)
        self.assertIn('_buildRimWarnPulse', methods)
        self.assertIn('_buildRimWarnCreamJuice', methods)
        self.assertIn('_spawnRimWarnCreamFlecks', methods)
        self.assertIn('_spawnRimWarnCreamHalo', methods)
        self.assertIn('_clearWarnCream', methods)
        self.assertIn('_setRimWarnColor', methods)
        self.assertIn('_resetRimScale', methods)
        src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('PURITY_PRESSURE_RIM_WARN', src)
        self.assertIn('PURITY_PRESSURE_RIM_FLASH', src)
        self.assertIn('PURITY_PRESSURE_RIM_FLASH_CREAM', src)
        self.assertIn('reclaimPurityMeterPressureWarn', src)
        self.assertIn('reclaimPurityMeterPressureCream', src)
        # Danger flash stays distinct from secured-lock celebration /
        # wave-clear sparkle / complete hose settle (warn body only).
        warn_snip = src.split('def warnPressure')[1].split(
            'def _buildRimWarnPulse')[0]
        cream_snip = src.split('def _buildRimWarnCreamJuice')[1].split(
            'def _setRimWarnColor')[0]
        for snip in (warn_snip, cream_snip):
            self.assertNotIn('SECURED_LOCK_RIM_COLOR', snip)
            self.assertNotIn('SECURED_LOCK_SPARKLE', snip)
            self.assertNotIn('WAVE_CLEAR_CREAM_SPARKLE', snip)
            self.assertNotIn('PURITY_COMPLETE_METER_SETTLE', snip)
            self.assertNotIn('settleComplete', snip)

    def test_rim_flash_tunables_are_warm_danger_not_secured_green(self):
        rg = self.rg
        self.assertTrue(rg.PURITY_PRESSURE_RIM_FLASH_ENABLED)
        self.assertTrue(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_ENABLED)
        # Further-deepened juice past #275: triple pulse + juicier rim nudge.
        self.assertGreaterEqual(int(rg.PURITY_PRESSURE_RIM_FLASH_PULSES), 3)
        warn = rg.PURITY_PRESSURE_RIM_WARN_COLOR
        lock = rg.SECURED_LOCK_RIM_COLOR
        # Warm/orange warn vs green secured — channels must not match.
        self.assertGreater(float(warn[0]), float(warn[1]))
        self.assertGreater(float(lock[1]), float(lock[0]))
        self.assertNotEqual(warn, lock)
        self.assertGreaterEqual(float(warn[3]), 0.98)
        self.assertGreaterEqual(float(rg.PURITY_PRESSURE_RIM_FLASH_SCALE), 1.36)
        self.assertGreaterEqual(
            float(rg.PURITY_PRESSURE_RIM_FLASH_HOLD_SEC), 0.22)
        self.assertLess(float(rg.PURITY_PRESSURE_RIM_FLASH_HOLD_SEC), 0.5)
        # Local cream flecks stay warm cream (not secured green glitter).
        cream = rg.PURITY_PRESSURE_RIM_FLASH_CREAM_COLOR
        self.assertGreater(float(cream[0]), 0.9)
        self.assertGreater(float(cream[1]), float(cream[2]))
        self.assertGreaterEqual(float(cream[3]), 0.98)
        self.assertGreaterEqual(int(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_COUNT), 8)
        self.assertGreaterEqual(
            float(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_SIZE), 0.015)
        self.assertGreaterEqual(
            float(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_DRIFT), 0.14)
        self.assertGreaterEqual(
            float(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_SEC), 0.36)
        self.assertTrue(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_ENABLED)
        self.assertGreaterEqual(
            float(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_PEAK), 1.42)
        self.assertGreaterEqual(
            float(rg.PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_PEAK_ALPHA), 0.24)
        # Distinct from wave-clear mid-screen sparkle and complete hose settle.
        self.assertNotEqual(
            rg.PURITY_PRESSURE_RIM_FLASH_CREAM_COLOR,
            rg.WAVE_CLEAR_CREAM_SPARKLE_COLOR)
        self.assertNotEqual(
            rg.PURITY_PRESSURE_RIM_WARN_COLOR,
            rg.PURITY_COMPLETE_METER_SETTLE_RIM_COLOR)
        self.assertNotEqual(
            rg.PURITY_PRESSURE_RIM_FLASH_CREAM_COLOR,
            rg.WAVE_START_METER_CREAM_COLOR)

    def test_magic_word_mentions_rim_flash_cream(self):
        src = _read('toontown/reclaim/MagicWords.py').lower()
        self.assertIn('cream flecks', src)
        self.assertIn('rim', src)
        self.assertIn('past #275', src)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        PurityPressureTipTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
