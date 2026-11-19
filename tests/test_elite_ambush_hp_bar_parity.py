#!/usr/bin/env python3
"""Headless tests: Elite / Ambush pack HP bar parity with soft-lock prefer.

Soft-lock permanently prefers Elite / Ambush rename prefixes (#375). The
boss/chase life bar must treat the same prefixes as subjects so mid-wave
scrums that steal Tab focus also show a readable HP bar.

Loads CorruptionGlobals with a ToontownGlobals stub — no Panda3D.
BossHpBarHud wiring stays AST-checked (imports pull panda).

Run from repo root:
  python3 tests/test_elite_ambush_hp_bar_parity.py
  python3 -m unittest tests.test_elite_ambush_hp_bar_parity -v
"""

from __future__ import annotations

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


class EliteAmbushHpBarParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cg = _load_panda_free_corruption()

    def test_prefer_name_helper_matches_soft_lock_prefixes(self):
        cg = self.cg
        prefer = cg.isEliteOrAmbushPreferName
        self.assertTrue(prefer('Elite Ink Smudge'))
        self.assertTrue(prefer('Ambush Sludge Brute'))
        self.assertTrue(prefer('elite balloon snare'))
        self.assertTrue(prefer('AMBUSH Gunk Gagster'))
        self.assertFalse(prefer('Ink Smudge'))
        self.assertFalse(prefer('Elite'))
        self.assertFalse(prefer('Ambush'))
        self.assertFalse(prefer('eliteink'))
        self.assertFalse(prefer(''))
        self.assertFalse(prefer(None))

    def test_hp_bar_subject_parity_with_soft_lock(self):
        cg = self.cg
        bar = cg.isBossOrChaseHpBarSubject
        soft = cg.isSoftLockPrioritySubject
        cases = (
            (cg.ARCHETYPE_INK, 'Elite Ink Smudge'),
            (cg.ARCHETYPE_BRUTE, 'Elite Sludge Brute'),
            (cg.ARCHETYPE_SNARE, 'Elite Balloon Snare'),
            (cg.ARCHETYPE_GAGSTER, 'Elite Gunk Gagster'),
            (cg.ARCHETYPE_INK, 'Ambush Ink Smudge'),
            (cg.ARCHETYPE_BRUTE, 'Ambush Sludge Brute'),
            (cg.ARCHETYPE_SNARE, 'Ambush Balloon Snare'),
            (cg.ARCHETYPE_GAGSTER, 'Ambush Gunk Gagster'),
            (cg.ARCHETYPE_INK, 'elite ink smudge'),
            (cg.ARCHETYPE_INK, 'AMBUSH Ink Smudge'),
        )
        for archetype, name in cases:
            self.assertTrue(
                soft(archetype, name=name),
                msg='soft-lock must prefer %r' % name)
            self.assertTrue(
                bar(archetype, name=name),
                msg='HP bar must show for soft-lock preferred %r' % name)

        # Plain fodder remains off for both gates.
        for archetype, name in (
                (cg.ARCHETYPE_INK, 'Ink Smudge'),
                (cg.ARCHETYPE_BRUTE, 'Sludge Brute'),
                (cg.ARCHETYPE_SNARE, 'Balloon Snare'),
                (cg.ARCHETYPE_GAGSTER, 'Gunk Gagster'),
                (cg.ARCHETYPE_INK, 'Elite'),
                (cg.ARCHETYPE_INK, 'Ambush'),
        ):
            self.assertFalse(soft(archetype, name=name))
            self.assertFalse(bar(archetype, name=name))

        # Prior Overlord / Oswald subjects still hold.
        self.assertTrue(bar(cg.ARCHETYPE_CORRUPT_OSWALD))
        self.assertTrue(bar(cg.ARCHETYPE_INK, finalePhase=1))
        self.assertTrue(soft(cg.ARCHETYPE_CORRUPT_OSWALD))
        self.assertTrue(soft(cg.ARCHETYPE_INK, name='Ink Overlord'))

    def test_elite_ambush_fill_and_rim_distinct(self):
        cg = self.cg
        elite_fill = cg.bossHpBarFillColor(
            cg.ARCHETYPE_INK, name='Elite Ink Smudge')
        ambush_fill = cg.bossHpBarFillColor(
            cg.ARCHETYPE_INK, name='Ambush Ink Smudge')
        overlord_fill = cg.bossHpBarFillColor(0, finalePhase=1)
        oswald_fill = cg.bossHpBarFillColor(cg.ARCHETYPE_CORRUPT_OSWALD)
        self.assertEqual(elite_fill, cg.BOSS_HP_BAR_FILL_ELITE)
        self.assertEqual(ambush_fill, cg.BOSS_HP_BAR_FILL_AMBUSH)
        self.assertNotEqual(elite_fill, ambush_fill)
        self.assertNotEqual(elite_fill, overlord_fill)
        self.assertNotEqual(ambush_fill, oswald_fill)
        self.assertEqual(
            cg.bossHpBarRimColor(
                cg.ARCHETYPE_BRUTE, name='Elite Sludge Brute'),
            cg.BOSS_HP_BAR_RIM_ELITE)
        self.assertEqual(
            cg.bossHpBarRimColor(
                cg.ARCHETYPE_SNARE, name='Ambush Balloon Snare'),
            cg.BOSS_HP_BAR_RIM_AMBUSH)
        self.assertEqual(
            cg.bossHpBarLabel(name='Elite Ink Smudge'),
            'Elite Ink Smudge')

    def test_disabled_gate_hides_elite_ambush(self):
        cg = self.cg
        prev = cg.BOSS_HP_BAR_ENABLED
        try:
            cg.BOSS_HP_BAR_ENABLED = False
            self.assertFalse(cg.isBossOrChaseHpBarSubject(
                cg.ARCHETYPE_INK, name='Elite Ink Smudge'))
            self.assertFalse(cg.isBossOrChaseHpBarSubject(
                cg.ARCHETYPE_INK, name='Ambush Ink Smudge'))
        finally:
            cg.BOSS_HP_BAR_ENABLED = prev

    def test_hud_docs_and_no_cream_kh(self):
        hud_src = _read('toontown/reclaim/BossHpBarHud.py')
        self.assertIn('Elite', hud_src)
        self.assertIn('Ambush', hud_src)
        self.assertIn('isBossOrChaseHpBarSubject', hud_src)
        self.assertNotIn('CreamWash', hud_src)
        self.assertNotIn('CreamSplash', hud_src)
        self.assertNotIn('keyblade', hud_src.lower())
        self.assertNotIn('kingdom hearts', hud_src.lower())
        cg_src = _read('toontown/corruption/CorruptionGlobals.py')
        self.assertIn('def isEliteOrAmbushPreferName', cg_src)
        self.assertIn("startswith('elite ')", cg_src)
        self.assertIn("startswith('ambush ')", cg_src)
        gate_idx = cg_src.index('def isBossOrChaseHpBarSubject')
        gate_snip = cg_src[gate_idx:gate_idx + 1100].lower()
        self.assertIn('iseliteorambushprefername', gate_snip)
        self.assertNotIn('cream', gate_snip)
        self.assertNotIn('keyblade', gate_snip)
        self.assertNotIn('kingdom hearts', gate_snip)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        EliteAmbushHpBarParityTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
