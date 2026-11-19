#!/usr/bin/env python3
"""Headless / AST tests: boss + chase + Elite/Ambush pack HP bar.

Loads CorruptionGlobals with a ToontownGlobals stub — no Panda3D. BossHpBarHud
and DistributedCorruptToon wiring are AST-checked (imports pull panda).

Run from repo root:
  python3 tests/test_boss_chase_hp_bar.py
  python3 -m unittest tests.test_boss_chase_hp_bar -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

LOOPY = 2200
PUNCHLINE = 2300
SILLY = 2100


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_corruption():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
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


def _module_names(rel: str) -> set[str]:
    tree = ast.parse(_read(rel))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _method_calls_named(rel: str, class_name: str, method_name: str) -> set[str]:
    """Names of Call funcs inside ClassDef.method (bare Name or Attribute)."""
    tree = ast.parse(_read(rel))
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.name != method_name:
                continue
            for child in ast.walk(item):
                if not isinstance(child, ast.Call):
                    continue
                func = child.func
                if isinstance(func, ast.Name):
                    out.add(func.id)
                elif isinstance(func, ast.Attribute):
                    out.add(func.attr)
    return out


class BossChaseHpBarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cg = _load_panda_free_corruption()

    def test_boss_hp_bar_enabled_and_layout(self):
        cg = self.cg
        self.assertTrue(cg.BOSS_HP_BAR_ENABLED)
        self.assertGreater(float(cg.BOSS_HP_BAR_WIDTH), 0.5)
        self.assertGreater(float(cg.BOSS_HP_BAR_HEIGHT), 0.0)
        self.assertGreater(float(cg.BOSS_HP_BAR_POS[2]), 0.5)
        self.assertGreater(int(cg.BOSS_HP_BAR_BIN), 45)
        self.assertIn('Overlord', cg.BOSS_HP_BAR_DEFAULT_OVERLORD_LABEL)
        self.assertIn('Oswald', cg.BOSS_HP_BAR_DEFAULT_OSWALD_LABEL)

    def test_subject_gate_overlord_oswald_and_elite_ambush(self):
        cg = self.cg
        subject = cg.isBossOrChaseHpBarSubject
        # Plain street archetypes — never.
        self.assertFalse(subject(cg.ARCHETYPE_INK))
        self.assertFalse(subject(cg.ARCHETYPE_BRUTE))
        self.assertFalse(subject(cg.ARCHETYPE_SNARE, name='Balloon Snare'))
        self.assertFalse(subject(cg.ARCHETYPE_GAGSTER))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ink Smudge'))
        # P2 Smudge adds keep per-toon finalePhase=0 — not bar subjects even
        # during Silly Unleashed (director street phase must not be applied).
        self.assertFalse(subject(
            cg.ARCHETYPE_INK, name='Ink Smudge', finalePhase=0))
        self.assertFalse(subject(
            cg.ARCHETYPE_INK, name='Ink Smudge 2', finalePhase=0))
        # Bare tokens without the rename space prefix — not Elite/Ambush.
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Elite'))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ambush'))
        # Corrupted Oswald chase — always.
        self.assertTrue(subject(cg.ARCHETYPE_CORRUPT_OSWALD))
        self.assertTrue(subject(
            cg.ARCHETYPE_CORRUPT_OSWALD, name='Corrupted Oswald'))
        # Overlord via per-toon finale phase or name (not director street phase).
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=1))
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=2))
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord', finalePhase=0))
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord Rising'))
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord Unleashed'))
        # Elite / Ambush pack renames — soft-lock prefer parity (#375).
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='Elite Ink Smudge'))
        self.assertTrue(subject(
            cg.ARCHETYPE_BRUTE, name='Elite Sludge Brute'))
        self.assertTrue(subject(
            cg.ARCHETYPE_SNARE, name='Ambush Balloon Snare'))
        self.assertTrue(subject(
            cg.ARCHETYPE_GAGSTER, name='Ambush Gunk Gagster'))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='elite ink smudge'))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='AMBUSH Ink Smudge'))
        self.assertTrue(cg.isEliteOrAmbushPreferName('Elite Ink Smudge'))
        self.assertTrue(cg.isEliteOrAmbushPreferName('Ambush Sludge Brute'))
        self.assertFalse(cg.isEliteOrAmbushPreferName('Ink Smudge'))

    def test_resolve_finale_phase_from_name(self):
        cg = self.cg
        resolve = cg.resolveBossHpBarFinalePhase
        self.assertEqual(resolve(0, 'Ink Overlord Rising'), 1)
        self.assertEqual(resolve(0, 'Ink Overlord Unleashed'), 2)
        self.assertEqual(resolve(1, 'anything'), 1)
        self.assertEqual(resolve(2, 'smudge'), 2)
        self.assertEqual(resolve(0, 'Ink Smudge'), 0)
        self.assertEqual(resolve('x', None), 0)

    def test_hp_ratio_clamp(self):
        cg = self.cg
        ratio = cg.bossHpBarRatio
        self.assertEqual(ratio(50, 100), 0.5)
        self.assertEqual(ratio(0, 100), 0.0)
        self.assertEqual(ratio(100, 100), 1.0)
        self.assertEqual(ratio(150, 100), 1.0)
        self.assertEqual(ratio(-5, 100), 0.0)
        self.assertEqual(ratio(10, 0), 0.0)
        self.assertEqual(ratio('x', 100), 0.0)

    def test_label_and_colors(self):
        cg = self.cg
        self.assertEqual(
            cg.bossHpBarLabel(name='Ink Overlord Rising'),
            'Ink Overlord Rising')
        self.assertEqual(
            cg.bossHpBarLabel(name='Elite Ink Smudge'),
            'Elite Ink Smudge')
        self.assertEqual(
            cg.bossHpBarLabel(name='Ambush Balloon Snare'),
            'Ambush Balloon Snare')
        self.assertEqual(
            cg.bossHpBarLabel(archetype=cg.ARCHETYPE_CORRUPT_OSWALD),
            cg.BOSS_HP_BAR_DEFAULT_OSWALD_LABEL)
        self.assertEqual(
            cg.bossHpBarLabel(finalePhase=1),
            cg.BOSS_HP_BAR_DEFAULT_OVERLORD_LABEL)
        self.assertEqual(
            cg.bossHpBarFillColor(cg.ARCHETYPE_CORRUPT_OSWALD),
            cg.BOSS_HP_BAR_FILL_OSWALD)
        self.assertEqual(
            cg.bossHpBarFillColor(0, finalePhase=1),
            cg.BOSS_HP_BAR_FILL_OVERLORD_P1)
        self.assertEqual(
            cg.bossHpBarFillColor(0, finalePhase=2),
            cg.BOSS_HP_BAR_FILL_OVERLORD_P2)
        self.assertEqual(
            cg.bossHpBarFillColor(
                cg.ARCHETYPE_INK, name='Elite Ink Smudge'),
            cg.BOSS_HP_BAR_FILL_ELITE)
        self.assertEqual(
            cg.bossHpBarFillColor(
                cg.ARCHETYPE_SNARE, name='Ambush Balloon Snare'),
            cg.BOSS_HP_BAR_FILL_AMBUSH)
        self.assertEqual(
            cg.bossHpBarRimColor(0, name='Ink Overlord Unleashed'),
            cg.BOSS_HP_BAR_RIM_OVERLORD_P2)
        self.assertEqual(
            cg.bossHpBarRimColor(
                cg.ARCHETYPE_BRUTE, name='Elite Sludge Brute'),
            cg.BOSS_HP_BAR_RIM_ELITE)
        self.assertEqual(
            cg.bossHpBarRimColor(
                cg.ARCHETYPE_INK, name='Ambush Ink Smudge'),
            cg.BOSS_HP_BAR_RIM_AMBUSH)

    def test_disabled_gate(self):
        cg = self.cg
        prev = cg.BOSS_HP_BAR_ENABLED
        try:
            cg.BOSS_HP_BAR_ENABLED = False
            self.assertFalse(cg.isBossOrChaseHpBarSubject(
                cg.ARCHETYPE_CORRUPT_OSWALD))
            self.assertFalse(cg.isBossOrChaseHpBarSubject(
                0, finalePhase=2))
        finally:
            cg.BOSS_HP_BAR_ENABLED = prev

    def test_hud_module_symbols(self):
        names = _module_names('toontown/reclaim/BossHpBarHud.py')
        for expected in (
                'BossHpBarHud', 'syncFromCorruptToon', 'releaseCorruptToon',
                'hideBossHpBar', 'destroyBossHpBar'):
            self.assertIn(expected, names)
        src = _read('toontown/reclaim/BossHpBarHud.py')
        self.assertIn('aspect2d', src)
        self.assertIn('boss-chase-hp-bar', src)
        # Per-hostile phase only — never reclaim-director street phase on adds.
        self.assertIn("getattr(toon, 'finalePhase'", src)
        self.assertNotIn('reclaimDirector', src)
        # Thin readable life bar only — no cream wash FX modules.
        self.assertNotIn('CreamWash', src)
        self.assertNotIn('CreamSplash', src)
        self.assertNotIn('keyblade', src.lower())
        self.assertNotIn('kingdom hearts', src.lower())

    def test_client_hooks_sync_and_release(self):
        rel = 'toontown/corruption/DistributedCorruptToon.py'
        src = _read(rel)
        self.assertIn('BossHpBarHud', src)
        self.assertIn('syncBossHpBar', src)
        self.assertIn('releaseBossHpBar', src)
        for method in ('setHp', 'setMaxHp', 'setName', 'setArchetype'):
            calls = _method_calls_named(
                rel, 'DistributedCorruptToon', method)
            self.assertIn(
                'syncBossHpBar', calls,
                msg='%s must sync boss/chase HP bar' % method)
        for method in ('announceDefeat', 'disable', 'delete'):
            calls = _method_calls_named(
                rel, 'DistributedCorruptToon', method)
            self.assertIn(
                'releaseBossHpBar', calls,
                msg='%s must release boss/chase HP bar' % method)

    def test_no_ai_interrupt_edits(self):
        # Prefer client-only — AI interrupt work is a sibling task.
        ai_src = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertNotIn('BossHpBar', ai_src)
        self.assertNotIn('bossHpBar', ai_src)
        self.assertNotIn('BOSS_HP_BAR', ai_src)


if __name__ == '__main__':
    unittest.main()
