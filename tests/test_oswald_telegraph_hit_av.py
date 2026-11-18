#!/usr/bin/env python3
"""Headless/AST tests: Corrupted Oswald telegraph + hit AV ≠ Smudge.

TC-353 / gap scan #7 — server kit is real, but client wind-up fell through
to Ink Smudge purple telegraph and hit/death splash missed Oswald. Must
branch ARCHETYPE_CORRUPT_OSWALD for crimson stain-lunge telegraph +
betrayal splash. No cream deepen / no KH branding / no Overlord move-id
plumbing changes.

Run from repo root:
  python3 tests/test_oswald_telegraph_hit_av.py
  python3 -m unittest tests.test_oswald_telegraph_hit_av -v
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


def _is_crimson_rgb(color) -> bool:
    """True when R dominates G/B enough to read as betrayal crimson, not purple."""
    r, g, b = float(color[0]), float(color[1]), float(color[2])
    return r > g and r > b and b < 0.7 and g < 0.55


class OswaldTelegraphHitAvTest(unittest.TestCase):
    """Oswald crimson AV looks + DistributedCorruptToon wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_telegraph_charge_crimson_not_smudge_purple(self):
        charge = self.cg.OSWALD_TELEGRAPH_CHARGE_COLOR
        hold = self.cg.OSWALD_TELEGRAPH_HOLD_COLOR
        smudge = self.cg.TELEGRAPH_CHARGE_COLOR
        self.assertTrue(_is_crimson_rgb(charge), msg=repr(charge))
        self.assertTrue(_is_crimson_rgb(hold), msg=repr(hold))
        # Distinct from Smudge purple (high B channel).
        self.assertNotEqual(tuple(charge[:3]), tuple(smudge[:3]))
        self.assertGreater(float(smudge[2]), float(smudge[1]))
        self.assertLess(float(charge[2]), float(charge[0]))
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, ' '.join(str(v).lower() for v in charge))

    def test_telegraph_stain_look_betrayal_lunge(self):
        look = self.cg.OSWALD_TELEGRAPH_STAIN_LOOK
        self.assertEqual(look.get('id'), 'betrayal-crimson-lunge')
        self.assertTrue(_is_crimson_rgb(look['fistColor']))
        self.assertTrue(_is_crimson_rgb(look['rimColor']))
        self.assertTrue(_is_crimson_rgb(look['smearColor']))
        self.assertNotEqual(
            look.get('id'),
            self.cg.SMUDGE_TELEGRAPH_INK_LOOK.get('id'))
        # Motion table present for lunge squash/stretch.
        for key in (
                'squash', 'stretch', 'squashSec', 'stretchSec',
                'smearCount', 'lift'):
            self.assertIn(key, look)
        self.assertGreaterEqual(int(look['smearCount']), 4)
        blob = ' '.join(str(v).lower() for v in look.values())
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, blob)

    def test_splash_look_crimson_not_smudge(self):
        looks = self.cg.OSWALD_BETRAYAL_SPLASH_LOOK
        for kind in ('hit', 'death'):
            look = looks[kind]
            self.assertIn('oswald', str(look.get('id', '')).lower())
            self.assertTrue(
                _is_crimson_rgb(look['splatColor']),
                msg='%s splat %r' % (kind, look['splatColor']))
            self.assertTrue(
                _is_crimson_rgb(look['rimColor']),
                msg='%s rim %r' % (kind, look['rimColor']))
            self.assertNotEqual(
                look.get('id'),
                self.cg.SMUDGE_INK_SPLASH_LOOK[kind].get('id'))
        # Death splash larger than hit for pop readability.
        self.assertGreater(
            float(looks['death']['splatPeak']),
            float(looks['hit']['splatPeak']))
        self.assertGreater(
            float(looks['death']['splatHalf']),
            float(looks['hit']['splatHalf']))

    def test_telegraph_fx_module(self):
        rel = 'toontown/corruption/OswaldBetrayalTelegraphFx.py'
        self.assertTrue((REPO_ROOT / rel).is_file())
        names = _class_and_func_names(_module_ast(rel))
        self.assertIn('OswaldBetrayalTelegraphStain', names)
        self.assertIn('oswaldTelegraphStainLook', names)
        methods = _class_method_names(
            _module_ast(rel), 'OswaldBetrayalTelegraphStain')
        for name in (
                'play', 'clear', '_buildStainLunge',
                '_buildMainLungeInterval', '_buildCrimsonSmears'):
            self.assertIn(
                name, methods,
                msg='OswaldBetrayalTelegraphStain missing %s' % name)
        src = _read(rel).lower()
        self.assertIn('oswald_telegraph_stain_look', src)
        self.assertIn('crimson', src)
        self.assertIn('smudge', src)  # docstring distinctness
        # Ban brand ids / props — allow "no keyblades" disclaimer text.
        self.assertNotIn("'keyblade", src)
        self.assertNotIn('"keyblade', src)
        self.assertNotIn('kingdom_hearts', src)
        # No cream deepen in Oswald telegraph FX.
        self.assertNotIn('cream splash', src)
        self.assertNotIn('cream wash', src)

    def test_splash_fx_module(self):
        rel = 'toontown/corruption/OswaldBetrayalSplashFx.py'
        self.assertTrue((REPO_ROOT / rel).is_file())
        names = _class_and_func_names(_module_ast(rel))
        self.assertIn('OswaldBetrayalSplash', names)
        self.assertIn('oswaldBetrayalSplashLook', names)
        methods = _class_method_names(
            _module_ast(rel), 'OswaldBetrayalSplash')
        for name in (
                'play', 'clear', '_spawnSplat', '_spawnSmear',
                '_spawnFleck', '_spawnDrip'):
            self.assertIn(
                name, methods,
                msg='OswaldBetrayalSplash missing %s' % name)
        src = _read(rel).lower()
        self.assertIn('oswald_betrayal_splash_look', src)
        self.assertIn('archetype_corrupt_oswald', src)
        self.assertIn('smudge', src)
        self.assertNotIn("'keyblade", src)
        self.assertNotIn('"keyblade', src)
        self.assertNotIn('kingdom_hearts', src)
        self.assertNotIn('cream splash', src)
        self.assertNotIn('cream wash', src)

    def test_corrupt_toon_oswald_wiring(self):
        src = _read('toontown/corruption/DistributedCorruptToon.py')
        methods = _class_method_names(
            _module_ast('toontown/corruption/DistributedCorruptToon.py'),
            'DistributedCorruptToon')
        for name in (
                '__isCorruptOswald',
                '__playOswaldTelegraphStain',
                '__clearOswaldTelegraphStain',
                '__playOswaldBetrayalSplash',
                '__clearOswaldBetrayalSplash'):
            self.assertIn(name, methods, msg='missing %s' % name)
        self.assertIn('OswaldBetrayalTelegraphStain', src)
        self.assertIn('OswaldBetrayalSplash', src)
        self.assertIn('OSWALD_TELEGRAPH_CHARGE_COLOR', src)
        self.assertIn('ARCHETYPE_CORRUPT_OSWALD', src)
        # Telegraph: Oswald branch before Smudge else; Smudge gated off Oswald.
        tele_idx = src.find('def announceAttackTelegraph')
        self.assertGreater(tele_idx, 0)
        next_def = src.find('\n    def ', tele_idx + 1)
        tele = src[tele_idx:next_def if next_def > 0 else tele_idx + 8000]
        self.assertIn('isOswald = self.__isCorruptOswald()', tele)
        self.assertIn('elif isOswald:', tele)
        self.assertIn('__playOswaldTelegraphStain()', tele)
        self.assertIn('and (not isOswald)', tele)
        # Impact: crimson Oswald branch, not purple Smudge else.
        hit_idx = src.find('def announceAttackHit')
        self.assertGreater(hit_idx, 0)
        next_hit = src.find('\n    def ', hit_idx + 1)
        hit = src[hit_idx:next_hit if next_hit > 0 else hit_idx + 5000]
        self.assertIn('elif isOswald:', hit)
        self.assertIn('__clearOswaldTelegraphStain()', hit)
        # Hit reaction + death splash branches.
        self.assertIn("__playOswaldBetrayalSplash(kind='hit')", src)
        self.assertIn("__playOswaldBetrayalSplash(splatPos, kind='death')", src)
        # Clear paths cover stop + defeat.
        self.assertGreaterEqual(src.count('__clearOswaldTelegraphStain'), 3)
        self.assertGreaterEqual(src.count('__clearOswaldBetrayalSplash'), 2)

    def test_docs_mention_oswald_av(self):
        init_src = _read('toontown/corruption/__init__.py')
        self.assertIn('OswaldBetrayalTelegraphFx', init_src)
        self.assertIn('OswaldBetrayalSplashFx', init_src)
        self.assertIn('not Smudge', init_src)
        reclaim = _read('toontown/corruption/RECLAIM.md')
        self.assertIn('OswaldBetrayalTelegraphFx', reclaim)
        self.assertIn('OswaldBetrayalSplashFx', reclaim)
        self.assertIn('No cream deepen on Oswald AV', reclaim)
        demo_idx = reclaim.find('## Corrupted Oswald telegraph')
        self.assertGreater(demo_idx, 0)
        demo = reclaim[demo_idx:demo_idx + 600].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, demo)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        OswaldTelegraphHitAvTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
