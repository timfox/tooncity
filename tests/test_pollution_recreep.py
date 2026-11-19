#!/usr/bin/env python3
"""Behavioral headless tests for incomplete-reclaim pollution re-creep.

Imports CorruptionGlobals with a ToontownGlobals stub (no Panda3D). Asserts
street status helpers, pollutionRecreepStep pure-stays-pure / cap behavior,
and AST hooks on PollutionManagerAI + DistributedReclaimDirectorAI.

Run from repo root:
  python3 tests/test_pollution_recreep.py
  python3 -m unittest tests.test_pollution_recreep -v
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


def _load_corruption_globals():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.toonbase', 'toontown.corruption'):
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
    return cg


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


class PollutionRecreepTest(unittest.TestCase):
    """Pure-Python re-creep math + reclaim/pollution hook wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_street_status_constants_registered(self):
        cg = self.cg
        self.assertEqual(cg.STREET_SECURED, 0)
        self.assertEqual(cg.STREET_RECLAIMING, 1)
        self.assertEqual(cg.STREET_CONTESTED, 2)
        self.assertEqual(cg.streetStatusName(cg.STREET_SECURED), 'secured')
        self.assertEqual(
            cg.streetStatusName(cg.STREET_RECLAIMING), 'reclaiming')
        self.assertEqual(
            cg.streetStatusName(cg.STREET_CONTESTED), 'contested')
        self.assertFalse(cg.streetAllowsRecreep(cg.STREET_SECURED))
        self.assertFalse(cg.streetAllowsRecreep(cg.STREET_RECLAIMING))
        self.assertTrue(cg.streetAllowsRecreep(cg.STREET_CONTESTED))
        # Non-status junk never opens re-creep.
        self.assertFalse(cg.streetAllowsRecreep(None))
        self.assertFalse(cg.streetAllowsRecreep('contested'))

    def test_recreep_tunable_lock(self):
        """#194 value lock — slow rubber-hose seep, not full blackout."""
        cg = self.cg
        self.assertIs(cg.POLLUTION_RECREEP_ENABLED, True)
        self.assertAlmostEqual(cg.POLLUTION_RECREEP_TICK_SEC, 2.5, places=2)
        self.assertAlmostEqual(cg.POLLUTION_RECREEP_PER_TICK, 0.04, places=3)
        self.assertAlmostEqual(cg.POLLUTION_RECREEP_CAP, 0.85, places=2)
        # Cap leaves reclaim headroom (below full pollution).
        self.assertLess(cg.POLLUTION_RECREEP_CAP, 1.0)
        self.assertGreater(cg.POLLUTION_RECREEP_TICK_SEC, 1.0)

    def test_pure_streets_stay_pure(self):
        cg = self.cg
        self.assertEqual(cg.pollutionRecreepStep(0.0), cg.POLLUTION_PURE)
        self.assertEqual(cg.pollutionRecreepStep(-0.5), cg.POLLUTION_PURE)
        # Contested bookkeeping must not invent ink on a clean street.
        self.assertEqual(
            cg.pollutionRecreepStep(cg.POLLUTION_PURE, perTick=0.5),
            cg.POLLUTION_PURE)

    def test_contested_residual_ink_creeps_toward_cap(self):
        cg = self.cg
        start = 0.40
        nxt = cg.pollutionRecreepStep(start)
        self.assertGreater(nxt, start)
        self.assertAlmostEqual(
            nxt, start + cg.POLLUTION_RECREEP_PER_TICK, places=5)
        # Exact one-tick residual (#194) — 0.40 → 0.44 at shipped per-tick.
        self.assertAlmostEqual(cg.pollutionRecreepStep(0.40), 0.44, places=5)

        # Cap holds — no overshoot past POLLUTION_RECREEP_CAP.
        near = cg.POLLUTION_RECREEP_CAP - 0.01
        capped = cg.pollutionRecreepStep(near, perTick=0.5)
        self.assertLessEqual(capped, cg.POLLUTION_RECREEP_CAP)
        self.assertEqual(
            cg.pollutionRecreepStep(cg.POLLUTION_RECREEP_CAP, perTick=1.0),
            cg.clampPollution(cg.POLLUTION_RECREEP_CAP))

        # Custom per-tick / cap for tuning smoke.
        self.assertAlmostEqual(
            cg.pollutionRecreepStep(0.2, perTick=0.1, cap=0.25),
            0.25, places=5)

        # Multi-tick seep stays monotonic and capped.
        level = 0.50
        for _ in range(20):
            nxt = cg.pollutionRecreepStep(level)
            self.assertGreaterEqual(nxt, level)
            self.assertLessEqual(nxt, cg.POLLUTION_RECREEP_CAP)
            level = nxt
        self.assertAlmostEqual(level, cg.POLLUTION_RECREEP_CAP, places=5)

    def test_zero_step_is_noop(self):
        cg = self.cg
        self.assertEqual(cg.pollutionRecreepStep(0.55, perTick=0.0), 0.55)

    def test_recreep_copy_is_rubber_hose_not_kh(self):
        msg = self.cg.POLLUTION_RECREEP_MSG.lower()
        self.assertIn('ink', msg)
        self.assertIn('reclaim', msg)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, msg)

    def test_pollution_manager_ai_recreep_hooks(self):
        tree = _module_ast('toontown/corruption/PollutionManagerAI.py')
        methods = _class_method_names(tree, 'PollutionManagerAI')
        for name in (
                'markStreetSecured',
                'markStreetReclaiming',
                'markStreetContested',
                'isPurityLocked',
                '_ensureRecreepTask',
                '__recreepTick',
                '_emitPollutionRecreeping',
                '_announceRecreep'):
            self.assertIn(name, methods, msg='PollutionManagerAI missing %s' % name)
        src = _read('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('STREET_CONTESTED', src)
        self.assertIn('pollutionRecreepStep', src)
        self.assertIn('POLLUTION_RECREEP_MSG', src)
        self.assertIn('pollutionRecreeping', src)
        self.assertIn('_emitPollutionRecreeping', src)
        self.assertIn('announcePollutionRecreeping', src)
        self.assertIn('_purityLocked', src)
        self.assertIn('streetPurityLockBlocksRise', src)
        # Tip-latch helpers (orphan → accept) live on CorruptionGlobals.
        self.assertEqual(self.cg.POLLUTION_RECREEPING_MSG, 'pollutionRecreeping')
        self.assertTrue(self.cg.POLLUTION_RECREEP_TIP_LATCH_ENABLED)
        self.assertEqual(
            self.cg.pollutionRecreepingMsgName(), 'pollutionRecreeping')

    def test_reclaim_director_marks_incomplete_vs_secured(self):
        src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('markStreetReclaiming', src)
        self.assertIn('markStreetContested', src)
        self.assertIn('markStreetSecured', src)
        self.assertIn('wasActive', src)
        # Contested only on ACTIVE bail-out, not after COMPLETE.
        stop_idx = src.find('def stop(self):')
        complete_idx = src.find('def __complete(self):')
        self.assertGreater(stop_idx, 0)
        self.assertGreater(complete_idx, 0)
        stop_snip = src[stop_idx:complete_idx]
        self.assertIn('markStreetContested', stop_snip)
        self.assertIn('wasActive', stop_snip)
        complete_snip = src[complete_idx:complete_idx + 900]
        self.assertIn('markStreetSecured', complete_snip)
        self.assertNotIn('markStreetContested', complete_snip)
        # Unlock purity lock before seeding so finished streets can restart.
        start_idx = src.find('def start(')
        self.assertGreater(start_idx, 0)
        start_snip = src[start_idx:stop_idx]
        self.assertLess(
            start_snip.find('markStreetReclaiming'),
            start_snip.find('setPollution'))


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PollutionRecreepTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
