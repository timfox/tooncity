#!/usr/bin/env python3
"""Behavioral headless tests for Gunk Gagster puddle telegraph warn (#197).

Imports CorruptionGlobals with a ToontownGlobals stub (no Panda3D). Asserts
GAGSTER_TELEGRAPH_PUDDLE_LOOK teal/cream warn fields and AST wiring on
GagsterPuddleTelegraphFx + DistributedCorruptToon (Gunk-only play/clear).

Run from repo root:
  python3 tests/test_gagster_telegraph_warn.py
  python3 -m unittest tests.test_gagster_telegraph_warn -v
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


def _class_and_func_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in getattr(tree, 'body', []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    return set()


class GagsterTelegraphWarnTest(unittest.TestCase):
    """Puddle-warn look + Gunk-only telegraph wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_puddle_look_teal_cream_warn(self):
        look = self.cg.GAGSTER_TELEGRAPH_PUDDLE_LOOK
        self.assertEqual(look.get('id'), 'teal-gag-puddle-warn')
        # Teal bounce-pie (G high / B high, R low) — readable vs Brute spit.
        pie = look.get('pieColor')
        self.assertIsInstance(pie, tuple)
        self.assertGreaterEqual(len(pie), 3)
        self.assertLess(float(pie[0]), float(pie[2]))
        self.assertGreater(float(pie[1]), 0.5)
        # Cream/ink ground puddle warn at predicted lob landing.
        for key in (
                'puddleInkColor', 'puddleCreamColor', 'puddleHalf',
                'puddlePeak', 'puddleHoldSec', 'creamFleckCount'):
            self.assertIn(key, look, msg='puddle look missing %s' % key)
        self.assertGreater(float(look['puddleHalf']), 0.5)
        self.assertGreater(int(look['creamFleckCount']), 0)
        # Short wind-up warn — readable before impact, not a linger trap.
        self.assertLessEqual(float(look.get('holdSec', 99)), 0.35)
        self.assertLessEqual(float(look.get('puddleDelay', 99)), 0.20)
        blob = ' '.join(str(v).lower() for v in look.values())
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, blob)

    def test_fx_module_exports_warn(self):
        rel = 'toontown/corruption/GagsterPuddleTelegraphFx.py'
        self.assertTrue((REPO_ROOT / rel).is_file())
        names = _class_and_func_names(_module_ast(rel))
        self.assertIn('GagsterPuddleTelegraphWarn', names)
        self.assertIn('gagsterTelegraphPuddleLook', names)
        methods = _class_method_names(
            _module_ast(rel), 'GagsterPuddleTelegraphWarn')
        for name in (
                'play', 'clear', '_buildBouncePie', '_buildPuddleWarn',
                '_buildCreamWarnFlecks'):
            self.assertIn(
                name, methods,
                msg='GagsterPuddleTelegraphWarn missing %s' % name)
        src = _read(rel)
        self.assertIn('GAGSTER_TELEGRAPH_PUDDLE_LOOK', src)
        self.assertIn('puddleCreamColor', src)

    def test_corrupt_toon_gunk_only_wiring(self):
        src = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('GagsterPuddleTelegraphWarn', src)
        self.assertIn('__isGunkGagster', src)
        self.assertIn('__playGagsterTelegraphPuddle', src)
        self.assertIn('__clearGagsterTelegraphPuddle', src)
        # Play only on Gunk wind-up; otherwise clear.
        self.assertIn('isGagster and not look', src)
        self.assertIn('__playGagsterTelegraphPuddle()', src)
        self.assertIn('__clearGagsterTelegraphPuddle()', src)
        # Landing warn aims at local avatar feet when available.
        play_idx = src.find('def __playGagsterTelegraphPuddle')
        self.assertGreater(play_idx, 0)
        play_snip = src[play_idx:play_idx + 900]
        self.assertIn('warnPos', play_snip)
        self.assertIn('localAvatar', play_snip)
        # Clear on defeat / disable paths (string presence is enough headless).
        self.assertGreater(src.count('__clearGagsterTelegraphPuddle'), 2)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        GagsterTelegraphWarnTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
