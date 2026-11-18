#!/usr/bin/env python3
"""Headless/AST tests for Balloon Snare string-lash yank.

Loads CorruptionGlobals yank helpers without Panda3D. Asserts planar reel
math, AI __resolveSingleTargetHit / __yankTargetTowardSnare wiring, and the
thin MeleeCombat hurt-react lerp. Gameplay identity — not cream FX deepen.

Run from repo root:
  python3 tests/test_snare_lash_yank.py
  python3 -m unittest tests.test_snare_lash_yank -v
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


class SnareLashYankTest(unittest.TestCase):
    """Yank tunables + pure helpers + AI/hackslash wiring (no Panda)."""

    @classmethod
    def setUpClass(cls):
        cls.cg = _load_corruption_globals()

    def test_yank_globals_armed(self):
        self.assertTrue(self.cg.SNARE_LASH_YANK_ENABLED)
        self.assertGreater(self.cg.SNARE_LASH_YANK_DIST, 0.5)
        self.assertGreater(self.cg.SNARE_LASH_YANK_STOP, 0.0)
        self.assertLess(
            self.cg.SNARE_LASH_YANK_STOP, self.cg.SNARE_LASH_YANK_DIST + 2.0)
        self.assertGreater(self.cg.SNARE_LASH_YANK_SEC, 0.0)
        self.assertLess(self.cg.SNARE_LASH_YANK_SEC, 0.5)
        # Short reel — well under Snare string-lash hit reach.
        snare = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_SNARE]
        self.assertLess(
            self.cg.SNARE_LASH_YANK_DIST,
            float(snare.get('attackHitRange', 7.2)))
        blob = ' '.join([
            'SNARE_LASH_YANK_ENABLED',
            'snareLashYankDelta',
            'snareLashYankPos',
        ]).lower()
        self.assertNotIn('keyblade', blob)
        self.assertNotIn('kingdom hearts', blob)

    def test_yank_delta_pulls_toward_snare(self):
        # Toon at (10, 0), Snare at (0, 0) → pull negative X toward origin.
        dx, dy = self.cg.snareLashYankDelta(0.0, 0.0, 10.0, 0.0, dist=2.0, stop=1.5)
        self.assertAlmostEqual(dy, 0.0, places=5)
        self.assertLess(dx, 0.0)
        self.assertAlmostEqual(dx, -2.0, places=5)
        nx, ny = self.cg.snareLashYankPos(0.0, 0.0, 10.0, 0.0, dist=2.0, stop=1.5)
        self.assertAlmostEqual(nx, 8.0, places=5)
        self.assertAlmostEqual(ny, 0.0, places=5)

    def test_yank_respects_stop_radius(self):
        # Already inside stop — no pull.
        dx, dy = self.cg.snareLashYankDelta(0.0, 0.0, 1.0, 0.0, dist=2.0, stop=1.5)
        self.assertEqual((dx, dy), (0.0, 0.0))
        # Partial pull: 3.0 away, stop 1.5, dist 2.0 → only 1.5 (3.0-1.5).
        dx, dy = self.cg.snareLashYankDelta(0.0, 0.0, 3.0, 0.0, dist=2.0, stop=1.5)
        self.assertAlmostEqual(dx, -1.5, places=5)
        self.assertAlmostEqual(dy, 0.0, places=5)
        # Coincident — no pull.
        self.assertEqual(
            self.cg.snareLashYankDelta(5.0, 5.0, 5.0, 5.0), (0.0, 0.0))

    def test_yank_diagonal_unit(self):
        # Equal XY offset — unit vector along diagonal.
        dx, dy = self.cg.snareLashYankDelta(
            0.0, 0.0, 4.0, 4.0, dist=1.0, stop=0.5)
        self.assertAlmostEqual(abs(dx), abs(dy), places=5)
        self.assertLess(dx, 0.0)
        self.assertLess(dy, 0.0)
        length = (dx * dx + dy * dy) ** 0.5
        self.assertAlmostEqual(length, 1.0, places=5)

    def test_oswald_and_gagster_untouched_by_yank_gate(self):
        # Yank is Snare-gated; Oswald betrayal kit + Gagster linger stay intact.
        self.assertIn(
            self.cg.ARCHETYPE_CORRUPT_OSWALD, self.cg.ARCHETYPE_STATS)
        oswald = self.cg.ARCHETYPE_STATS[self.cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertEqual(oswald.get('name'), 'Corrupted Oswald')
        self.assertEqual(oswald.get('attackMove'), 'betrayal_lunge')
        self.assertTrue(self.cg.OSWALD_BETRAYAL_KIT_ENABLED)
        self.assertTrue(self.cg.GAGSTER_PUDDLE_LINGER_ENABLED)
        self.assertGreater(self.cg.GAGSTER_PUDDLE_LINGER_SEC, 1.0)

    def test_ai_resolve_yank_wiring(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        self.assertIn('__resolveSingleTargetHit', methods)
        self.assertIn('__yankTargetTowardSnare', methods)
        # Keep prior gameplay intact on the same AI module.
        self.assertIn('__armGagsterPuddleLinger', methods)
        self.assertIn('_juggleHangStunUntil', _read(rel))
        src = _read(rel)
        resolve = src[src.find('def __resolveSingleTargetHit'):]
        resolve_end = resolve.find('\n    def ', 1)
        resolve_body = resolve if resolve_end < 0 else resolve[:resolve_end]
        self.assertIn('__yankTargetTowardSnare(target)', resolve_body)
        self.assertIn("sendUpdate('announceAttackHit'", resolve_body)
        yank = src[src.find('def __yankTargetTowardSnare'):]
        yank_end = yank.find('\n    def ', 1)
        yank_body = yank if yank_end < 0 else yank[:yank_end]
        self.assertIn('SNARE_LASH_YANK_ENABLED', yank_body)
        self.assertIn('ARCHETYPE_SNARE', yank_body)
        self.assertIn('snareLashYankPos', yank_body)
        self.assertIn('setPos', yank_body)
        # Non-Snare gate — Oswald / Smudge / Brute must not yank.
        self.assertIn('normalizeArchetype', yank_body)

    def test_melee_hurt_react_yank_wiring(self):
        rel = 'toontown/hackslash/MeleeCombat.py'
        methods = _class_method_names(
            _module_ast(rel), 'MeleeCombatController')
        self.assertIn('_yankAvatarTowardSnare', methods)
        self.assertIn('_clearSnareLashYank', methods)
        self.assertIn('_onCorruptHitPlayer', methods)
        src = _read(rel)
        hit = src[src.find('def _onCorruptHitPlayer'):]
        hit_end = hit.find('\n    def ', 1)
        hit_body = hit if hit_end < 0 else hit[:hit_end]
        self.assertIn('_yankAvatarTowardSnare(corrupt)', hit_body)
        yank = src[src.find('def _yankAvatarTowardSnare'):]
        yank_end = yank.find('\n    def ', 1)
        yank_body = yank if yank_end < 0 else yank[:yank_end]
        self.assertIn('SNARE_LASH_YANK_ENABLED', yank_body)
        self.assertIn('ARCHETYPE_SNARE', yank_body)
        self.assertIn('snareLashYankPos', yank_body)
        self.assertIn('LerpPosInterval', yank_body)
        self.assertIn('SNARE_LASH_YANK_SEC', yank_body)
        # Disable cleans the interval so orphaned lerps do not leak.
        disable = src[src.find('def disable(self):'):]
        self.assertIn('_clearSnareLashYank', disable)
        config = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('Snare lash yank', config)
        reclaim = _read('toontown/corruption/RECLAIM.md')
        self.assertIn('yank', reclaim.lower())


if __name__ == '__main__':
    unittest.main()
