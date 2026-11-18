#!/usr/bin/env python3
"""Behavioral headless tests for finished-reclaim secured purity lock.

Imports CorruptionGlobals / ReclaimGlobals with a ToontownGlobals stub (no
Panda3D). Asserts streetPurityLockBlocksRise, secured tip copy, and AST hooks
on PollutionManagerAI + reclaim director / HUD confirmation.

Run from repo root:
  python3 tests/test_secured_purity_lock.py
  python3 -m unittest tests.test_secured_purity_lock -v
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


def _load_panda_free_modules():
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
    return cg, rg


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


class SecuredPurityLockTest(unittest.TestCase):
    """Pure-Python secured lock helpers + reclaim/pollution wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cg, cls.rg = _load_panda_free_modules()

    def test_purity_lock_blocks_rise_only_when_locked(self):
        cg = self.cg
        self.assertIs(cg.STREET_PURITY_LOCK_ENABLED, True)
        # Unlocked ambient SECURED default still accepts rises (~pollute).
        self.assertFalse(cg.streetPurityLockBlocksRise(False, 0.5, 0.0))
        # Finished reclaim lock refuses re-stain.
        self.assertTrue(cg.streetPurityLockBlocksRise(True, 0.4, 0.0))
        self.assertTrue(cg.streetPurityLockBlocksRise(True, 0.2, 0.1))
        # Same / lower levels still allowed (purify / noop).
        self.assertFalse(cg.streetPurityLockBlocksRise(True, 0.0, 0.0))
        self.assertFalse(cg.streetPurityLockBlocksRise(True, 0.0, 0.3))
        # Toggle soft-opens rises without clearing bookkeeping.
        self.assertFalse(
            cg.streetPurityLockBlocksRise(True, 0.9, 0.0, enabled=False))

    def test_contested_still_allows_recreep_helpers(self):
        cg = self.cg
        self.assertFalse(cg.streetAllowsRecreep(cg.STREET_SECURED))
        self.assertFalse(cg.streetAllowsRecreep(cg.STREET_RECLAIMING))
        self.assertTrue(cg.streetAllowsRecreep(cg.STREET_CONTESTED))
        self.assertGreater(cg.pollutionRecreepStep(0.30), 0.30)

    def test_secured_tip_copy_is_rubber_hose_not_kh(self):
        rg = self.rg
        self.assertIs(rg.SECURED_LOCK_TIP_ENABLED, True)
        tip = rg.securedLockTipText(2200).lower()
        self.assertIn('secured', tip)
        self.assertIn('ink', tip)
        self.assertIn('lock', tip)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, tip)
        lock_msg = self.cg.STREET_PURITY_LOCK_MSG.lower()
        self.assertIn('secured', lock_msg)
        self.assertIn('ink', lock_msg)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, lock_msg)

    def test_pollution_manager_ai_purity_lock_hooks(self):
        tree = _module_ast('toontown/corruption/PollutionManagerAI.py')
        methods = _class_method_names(tree, 'PollutionManagerAI')
        for name in (
                'isPurityLocked',
                'markStreetSecured',
                'markStreetReclaiming',
                'markStreetContested',
                'setPollution',
                '__recreepTick'):
            self.assertIn(name, methods, msg='PollutionManagerAI missing %s' % name)
        src = _read('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('_purityLocked', src)
        self.assertIn('streetPurityLockBlocksRise', src)
        self.assertIn('streetAllowsRecreep', src)
        self.assertIn('purity-locked', src)

    def test_reclaim_director_unlocks_before_seed(self):
        src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        start_idx = src.find('def start(')
        stop_idx = src.find('def stop(self):')
        self.assertGreater(start_idx, 0)
        self.assertGreater(stop_idx, start_idx)
        start_snip = src[start_idx:stop_idx]
        reclaiming_at = start_snip.find('markStreetReclaiming')
        seed_at = start_snip.find('setPollution')
        self.assertGreater(reclaiming_at, 0)
        self.assertGreater(seed_at, reclaiming_at)
        # Complete still secures; stop contested only while ACTIVE.
        complete_idx = src.find('def __complete(self):')
        self.assertGreater(complete_idx, 0)
        complete_snip = src[complete_idx:complete_idx + 900]
        self.assertIn('markStreetSecured', complete_snip)
        self.assertNotIn('markStreetContested', complete_snip)

    def test_client_secured_lock_hud_hooks(self):
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirector.py')
        methods = _class_method_names(tree, 'DistributedReclaimDirector')
        for name in (
                '__confirmSecuredLock',
                '__showSecuredLockTip',
                '__hideSecuredLockTip',
                '__cancelSecuredHudHold',
                '__playSecuredLockSparkleSting'):
            self.assertIn(
                name, methods,
                msg='DistributedReclaimDirector missing %s' % name)
        src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('securedLockTipText', src)
        self.assertIn('confirmSecured', src)
        self.assertIn('announceReclaimComplete', src)
        self.assertIn('reclaimStreetSecured', src)
        self.assertIn('ensureSecuredLockSparkleFxClient', src)
        meter = _module_ast('toontown/reclaim/PurityMeterHud.py')
        meter_methods = _class_method_names(meter, 'PurityMeterHud')
        self.assertIn('confirmSecured', meter_methods)
        meter_src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('SECURED_LOCK_RIM', meter_src)
        self.assertIn('reclaimPurityMeterSecuredConfirm', meter_src)
        # Sparkle sting module + tunables.
        self.assertIs(self.rg.SECURED_LOCK_SPARKLE_ENABLED, True)
        fx = _module_ast('toontown/reclaim/SecuredLockSparkleFx.py')
        fx_methods = _class_method_names(fx, 'SecuredLockSparkleFxClient')
        self.assertIn('playLockSting', fx_methods)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SecuredPurityLockTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
