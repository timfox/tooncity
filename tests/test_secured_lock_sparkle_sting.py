#!/usr/bin/env python3
"""Behavioral headless tests for secured-street purity sparkle sting.

Imports ReclaimGlobals with a ToontownGlobals stub (no Panda3D). Asserts
SECURED_LOCK_SPARKLE / STING tunables, rubber-hose (non-KH) copy, and AST
hooks on SecuredLockSparkleFx + reclaim director / meter confirm.

Run from repo root:
  python3 tests/test_secured_lock_sparkle_sting.py
  python3 -m unittest tests.test_secured_lock_sparkle_sting -v
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


def _top_level_func_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


class SecuredLockSparkleStingTest(unittest.TestCase):
    """Pure-Python secured-lock sparkle / sting wiring."""

    @classmethod
    def setUpClass(cls):
        cls.rg = _load_reclaim_globals()

    def test_sparkle_sting_tunables_enabled(self):
        rg = self.rg
        self.assertIs(rg.SECURED_LOCK_SPARKLE_ENABLED, True)
        self.assertIs(rg.SECURED_LOCK_STING_ENABLED, True)
        self.assertGreater(rg.SECURED_LOCK_SPARKLE_COUNT, 0)
        self.assertGreater(rg.SECURED_LOCK_SPARKLE_SEC, 0.0)
        self.assertGreater(rg.SECURED_LOCK_STING_VOLUME, 0.0)
        self.assertLess(rg.SECURED_LOCK_STING_VOLUME, rg.PURITY_STING_VOLUME)
        # Green-cream lock glitter — greener than sunny wave-clear cream.
        sparkle = rg.SECURED_LOCK_SPARKLE_COLOR
        wave = rg.WAVE_CLEAR_CREAM_SPARKLE_COLOR
        self.assertGreater(sparkle[1], sparkle[0])  # G > R
        self.assertGreater(sparkle[2], wave[2])  # more green channel vs cream
        # Origin near tip / meter, not wave-clear mid or StreetSparkle horizon.
        ox, oy, oz = rg.SECURED_LOCK_SPARKLE_ORIGIN
        self.assertAlmostEqual(oz, 0.42, places=2)
        self.assertNotEqual(
            tuple(rg.SECURED_LOCK_SPARKLE_ORIGIN),
            tuple(rg.WAVE_CLEAR_CREAM_SPARKLE_ORIGIN))

    def test_sting_sfx_is_cheer_cousin_not_purity_whistle(self):
        rg = self.rg
        self.assertNotEqual(rg.SECURED_LOCK_STING_SFX, rg.PURITY_STING_SFX)
        self.assertEqual(rg.SECURED_LOCK_STING_SFX, rg.PURITY_CHEER_SFX)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, rg.SECURED_LOCK_STING_SFX.lower())

    def test_secured_lock_sparkle_fx_module_hooks(self):
        tree = _module_ast('toontown/reclaim/SecuredLockSparkleFx.py')
        methods = _class_method_names(tree, 'SecuredLockSparkleFxClient')
        for name in (
                'playLockSting',
                '_spawnFlecks',
                '_playStingSfx',
                'clear',
                '_onStreetSecured'):
            self.assertIn(
                name, methods,
                msg='SecuredLockSparkleFxClient missing %s' % name)
        funcs = _top_level_func_names(tree)
        self.assertIn('ensureSecuredLockSparkleFxClient', funcs)
        src = _read('toontown/reclaim/SecuredLockSparkleFx.py')
        self.assertIn('reclaimStreetSecured', src)
        self.assertIn('SECURED_LOCK_SPARKLE', src)
        self.assertIn('reclaimSecuredLockSparkle', src)
        self.assertIn('reclaimSecuredLockSting', src)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, src.lower())

    def test_director_arms_sparkle_from_confirm_secured(self):
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirector.py')
        methods = _class_method_names(tree, 'DistributedReclaimDirector')
        self.assertIn('__confirmSecuredLock', methods)
        self.assertIn('__playSecuredLockSparkleSting', methods)
        src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        confirm_idx = src.find('def __confirmSecuredLock')
        self.assertGreater(confirm_idx, 0)
        # Next def after confirm — snip the method body.
        next_def = src.find('\n    def ', confirm_idx + 10)
        confirm_snip = src[confirm_idx:next_def]
        self.assertIn('__playSecuredLockSparkleSting', confirm_snip)
        self.assertIn('confirmSecured', confirm_snip)
        play_idx = src.find('def __playSecuredLockSparkleSting')
        self.assertGreater(play_idx, 0)
        play_next = src.find('\n    def ', play_idx + 10)
        play_snip = src[play_idx:play_next]
        self.assertIn('ensureSecuredLockSparkleFxClient', play_snip)
        self.assertIn('reclaimStreetSecured', play_snip)
        # Must not restage wave-clear / purityRestore sparkle messengers here.
        self.assertNotIn('reclaimWaveCleared', play_snip)
        self.assertNotIn('purityRestoreFx', play_snip)

    def test_meter_confirm_has_hose_pop(self):
        meter_src = _read('toontown/reclaim/PurityMeterHud.py')
        self.assertIn('SECURED_LOCK_METER_POP', meter_src)
        self.assertIn('reclaimPurityMeterSecuredConfirm', meter_src)
        confirm_idx = meter_src.find('def confirmSecured')
        self.assertGreater(confirm_idx, 0)
        next_def = meter_src.find('\n    def ', confirm_idx + 10)
        snip = meter_src[confirm_idx:next_def]
        self.assertIn('LerpScaleInterval', snip)
        self.assertIn('SECURED_LOCK_RIM_COLOR', snip)

    def test_distinct_from_pressure_and_wave_clear(self):
        """Secured sting must not reuse pressure tip or wave-clear sparkle APIs."""
        fx_src = _read('toontown/reclaim/SecuredLockSparkleFx.py')
        self.assertNotIn('PURITY_PRESSURE', fx_src)
        self.assertNotIn('WAVE_CLEAR_CREAM_SPARKLE', fx_src)
        self.assertNotIn('warnPressure', fx_src)
        self.assertIn('green-cream', fx_src.lower())


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SecuredLockSparkleStingTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
