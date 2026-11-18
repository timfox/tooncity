#!/usr/bin/env python3
"""Behavioral headless tests for purity-complete meter hose settle cream.

Imports ReclaimGlobals with a ToontownGlobals stub (no Panda3D). Asserts
further-deepened PURITY_COMPLETE_METER_SETTLE / CREAM tunables past #266,
rubber-hose (non-KH) copy, and AST hooks on PurityMeterHud + reclaim director
restore settle path. Distinct from wave-hose cream deepen (#239 / #280), lock
celebration deepen (#243 / #261 / #286), mid-wave rim / wave-clear sparkle,
and original complete hose settle (#225).

Run from repo root:
  python3 tests/test_purity_complete_meter_hose_settle.py
  python3 -m unittest tests.test_purity_complete_meter_hose_settle -v
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


class PurityCompleteMeterHoseSettleTest(unittest.TestCase):
    """Pure-Python purity-complete meter hose-settle cream deepen past #266."""

    @classmethod
    def setUpClass(cls):
        cls.rg = _load_reclaim_globals()

    def test_complete_meter_settle_tunables_enabled(self):
        rg = self.rg
        self.assertIs(rg.PURITY_COMPLETE_METER_SETTLE_ENABLED, True)
        self.assertIs(rg.PURITY_COMPLETE_METER_SETTLE_CREAM_ENABLED, True)
        # Floors past #266 deepen (0.24 / 0.42 / stretch Z 1.36 / count 8).
        self.assertGreater(float(rg.PURITY_COMPLETE_METER_SETTLE_SEC), 0.24)
        self.assertGreaterEqual(float(rg.PURITY_COMPLETE_METER_SETTLE_RIM_SEC), 0.46)
        stretch = rg.PURITY_COMPLETE_METER_SETTLE_STRETCH
        self.assertEqual(len(stretch), 4)
        # Tall stretch overshoot — settle finish, not flat squash first.
        self.assertGreater(float(stretch[2]), 1.36)  # past #266 tall finish
        self.assertLess(float(stretch[2]), float(rg.WAVE_START_METER_POP_STRETCH[2]))
        # Settle dwell longer than stretch beat so the finish lands.
        self.assertGreater(
            float(rg.PURITY_COMPLETE_METER_SETTLE_SEC),
            float(stretch[3]))
        # Richer settling cream flecks / halo past #266 (downward finish juice).
        self.assertGreaterEqual(int(rg.PURITY_COMPLETE_METER_SETTLE_CREAM_COUNT), 10)
        self.assertGreater(float(rg.PURITY_COMPLETE_METER_SETTLE_CREAM_FALL), 0.14)
        self.assertGreater(
            float(rg.PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_PEAK), 1.38)
        self.assertGreaterEqual(
            float(rg.PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_PEAK_ALPHA), 0.18)
        self.assertTrue(rg.PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_ENABLED)

    def test_rim_accent_distinct_from_wave_start_and_secured(self):
        rg = self.rg
        finish = rg.PURITY_COMPLETE_METER_SETTLE_RIM_COLOR
        start = rg.WAVE_START_METER_RIM_COLOR
        lock = rg.SECURED_LOCK_RIM_COLOR
        warn = rg.PURITY_PRESSURE_RIM_WARN_COLOR
        cream = rg.PURITY_COMPLETE_METER_SETTLE_CREAM_COLOR
        self.assertNotEqual(tuple(finish), tuple(start))
        self.assertNotEqual(tuple(finish), tuple(lock))
        self.assertNotEqual(tuple(finish), tuple(warn))
        # Sunny pure cream: R and G high, B lower — not green lock (G>>R).
        self.assertGreater(float(finish[0]), 0.9)
        self.assertGreater(float(finish[1]), 0.9)
        self.assertLess(float(finish[2]), float(finish[1]))
        self.assertGreaterEqual(float(finish[3]), 0.96)  # creamier rim alpha past #266
        self.assertGreater(float(lock[1]), float(lock[0]))  # green lock
        # Settling finish flecks stay pure cream (high G), not green lock glitter.
        self.assertGreater(float(cream[1]), 0.95)
        self.assertGreaterEqual(float(cream[3]), 0.96)
        self.assertNotEqual(
            tuple(cream), tuple(rg.WAVE_START_METER_CREAM_COLOR))
        self.assertNotEqual(
            tuple(cream[:3]), tuple(rg.SECURED_LOCK_SPARKLE_COLOR[:3]))

    def test_no_kh_branding_in_complete_settle_tunables(self):
        banned = ('keyblade', 'kingdom hearts', 'sora', 'heartless', 'kh ')
        blob = ' '.join([
            str(self.rg.PURITY_COMPLETE_METER_SETTLE_ENABLED),
            str(self.rg.PURITY_COMPLETE_METER_SETTLE_RIM_COLOR),
            str(self.rg.PURITY_COMPLETE_METER_SETTLE_CREAM_COLOR),
            'purity complete meter hose settle sunny cream deepen past 266',
        ]).lower()
        for term in banned:
            self.assertNotIn(term, blob)

    def test_purity_meter_hud_has_settle_complete(self):
        tree = _module_ast('toontown/reclaim/PurityMeterHud.py')
        methods = _class_method_names(tree, 'PurityMeterHud')
        self.assertIn('settleComplete', methods)
        self.assertIn('_buildCompleteSettleCreamJuice', methods)
        self.assertIn('_spawnCompleteSettleCreamFlecks', methods)
        self.assertIn('_spawnCompleteSettleCreamHalo', methods)
        self.assertIn('popWaveStart', methods)
        self.assertIn('confirmSecured', methods)
        src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('PURITY_COMPLETE_METER_SETTLE', src)
        self.assertIn('PURITY_COMPLETE_METER_SETTLE_CREAM', src)
        self.assertIn('reclaimPurityMeterCompleteSettle', src)
        self.assertIn('reclaimPurityMeterCompleteSettleCream', src)
        # Complete settle stays distinct from wave-start squash and lock green.
        settle_snip = src.split('def settleComplete')[1].split(
            'def confirmSecured')[0]
        self.assertNotIn('WAVE_START_METER_POP_SQUASH', settle_snip)
        self.assertNotIn('WAVE_START_METER_CREAM', settle_snip)
        self.assertNotIn('SECURED_LOCK_RIM_COLOR', settle_snip)
        self.assertNotIn('SECURED_LOCK_METER_POP', settle_snip)
        self.assertNotIn('SECURED_LOCK_SPARKLE', settle_snip)
        self.assertIn('PURITY_COMPLETE_METER_SETTLE_STRETCH', settle_snip)
        self.assertIn('PURITY_COMPLETE_METER_SETTLE_SEC', settle_snip)
        self.assertIn('_buildCompleteSettleCreamJuice', settle_snip)
        # Settling flecks fall downward — finish residual, not rising begin.
        self.assertIn('PURITY_COMPLETE_METER_SETTLE_CREAM_FALL', settle_snip)
        self.assertNotIn('WAVE_START_METER_CREAM_RISE', settle_snip)

    def test_director_restore_calls_hose_settle_before_settled(self):
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirector.py')
        methods = _class_method_names(tree, 'DistributedReclaimDirector')
        self.assertIn('__playRestoreFx', methods)
        self.assertIn('__hoseSettlePurityMeterComplete', methods)
        src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        play_idx = src.find('def __playRestoreFx')
        next_def = src.find('\n    def ', play_idx + 1)
        snip = src[play_idx:next_def]
        self.assertIn('__hoseSettlePurityMeterComplete', snip)
        self.assertIn('purityRestoreSettled', snip)
        # Hose settle arms before the settled messenger so the finish reads.
        self.assertLess(
            snip.find('__hoseSettlePurityMeterComplete'),
            snip.find('purityRestoreSettled'))
        # Must not restage wave-start / secured sparkle messengers here.
        self.assertNotIn('popWaveStart', snip)
        self.assertNotIn('reclaimStreetSecured', snip)

        settle_idx = src.find('def __hoseSettlePurityMeterComplete')
        settle_next = src.find('\n    def ', settle_idx + 1)
        settle_snip = src[settle_idx:settle_next]
        self.assertIn('settleComplete', settle_snip)
        self.assertIn('PURITY_COMPLETE_METER_SETTLE', settle_snip)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        PurityCompleteMeterHoseSettleTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
