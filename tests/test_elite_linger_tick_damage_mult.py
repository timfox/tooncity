#!/usr/bin/env python3
"""Headless tests: elite damage mult scales linger tick DoTs.

Wave-4 / Silly twin elite packing already buffs land hits (+ spit trail).
Puddle / rain / slam / surge linger tick damages must scale too so elite
DoT pressure matches the land-hit fantasy (no cream, no KH).

Run from repo root:
  python3 tests/test_elite_linger_tick_damage_mult.py
  python3 -m unittest tests.test_elite_linger_tick_damage_mult -v
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

LINGER_TICK_DAMAGE_KEYS = (
    'puddleLingerTickDamage',
    'rainLingerTickDamage',
    'slamLingerTickDamage',
    'surgeLingerTickDamage',
)


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_reclaim():
    """Stub ToontownGlobals, then load CorruptionGlobals + ReclaimGlobals."""
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

    rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
    rg_spec = importlib.util.spec_from_file_location(
        'toontown.reclaim.ReclaimGlobals', rg_path)
    rg = importlib.util.module_from_spec(rg_spec)
    assert rg_spec.loader is not None
    sys.modules['toontown.reclaim.ReclaimGlobals'] = rg
    rg_spec.loader.exec_module(rg)
    sys.modules['toontown.reclaim'].ReclaimGlobals = rg
    return rg, cg


class EliteLingerTickDamageMultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.cg = _load_panda_free_reclaim()

    def test_elite_damage_keys_include_linger_ticks(self):
        rg = self.rg
        for key in LINGER_TICK_DAMAGE_KEYS:
            self.assertIn(key, rg.ELITE_DAMAGE_STAT_KEYS)

    def test_apply_wave_damage_mult_scales_linger_ticks(self):
        rg = self.rg
        mult = rg.ELITE_DAMAGE_MULT
        stats = {
            'attackDamage': 2,
            'puddleLingerTickDamage': 1,
            'rainLingerTickDamage': 1,
            'slamLingerTickDamage': 1,
            'surgeLingerTickDamage': 2,
            # Non-damage linger timing / slow — must stay untouched.
            'puddleLingerSec': 2.5,
            'puddleLingerTickSec': 0.5,
            'puddleLingerSlowFactor': 0.55,
            'rainLingerSec': 3.0,
            'chaseSpeed': 9.0,
        }
        out = rg.applyWaveDamageMultToStats(stats, {'elite': True})
        for key, base in (
                ('puddleLingerTickDamage', 1),
                ('rainLingerTickDamage', 1),
                ('slamLingerTickDamage', 1),
                ('surgeLingerTickDamage', 2),
                ('attackDamage', 2)):
            self.assertEqual(
                out[key], max(1, int(round(base * mult))),
                msg='%s should scale by elite mult' % key)
        self.assertEqual(out['puddleLingerSec'], 2.5)
        self.assertEqual(out['puddleLingerTickSec'], 0.5)
        self.assertEqual(out['puddleLingerSlowFactor'], 0.55)
        self.assertEqual(out['rainLingerSec'], 3.0)
        self.assertEqual(out['chaseSpeed'], 9.0)

    def test_helpers_read_scaled_linger_ticks_from_stats(self):
        """CorruptionGlobals helpers prefer stats over module defaults."""
        rg, cg = self.rg, self.cg
        mods = {'elite': True}
        mult = rg.ELITE_DAMAGE_MULT

        puddle_base = {
            'puddleLingerTickDamage': int(
                cg.ARCHETYPE_STATS[cg.ARCHETYPE_GAGSTER].get(
                    'puddleLingerTickDamage', 1)),
        }
        puddle_elite = rg.applyWaveDamageMultToStats(puddle_base, mods)
        self.assertEqual(
            cg.gagsterPuddleLingerTickDamage(puddle_elite),
            max(1, int(round(puddle_base['puddleLingerTickDamage'] * mult))))

        rain_base = {'rainLingerTickDamage': 1}
        rain_elite = rg.applyWaveDamageMultToStats(rain_base, mods)
        self.assertEqual(
            cg.overlordRainLingerTickDamage(rain_elite),
            max(1, int(round(1 * mult))))

        slam_base = {'slamLingerTickDamage': 1}
        slam_elite = rg.applyWaveDamageMultToStats(slam_base, mods)
        self.assertEqual(
            cg.overlordSlamLingerTickDamage(slam_elite),
            max(1, int(round(1 * mult))))

        surge_base = {'surgeLingerTickDamage': 2}
        surge_elite = rg.applyWaveDamageMultToStats(surge_base, mods)
        self.assertEqual(
            cg.overlordInkSurgeLingerTickDamage(surge_elite),
            max(1, int(round(2 * mult))))

    def test_no_op_without_elite_mods(self):
        rg = self.rg
        stats = {
            'puddleLingerTickDamage': 1,
            'rainLingerTickDamage': 2,
            'slamLingerTickDamage': 1,
            'surgeLingerTickDamage': 2,
        }
        out = rg.applyWaveDamageMultToStats(stats, None)
        self.assertEqual(out['puddleLingerTickDamage'], 1)
        self.assertEqual(out['rainLingerTickDamage'], 2)
        self.assertEqual(out['slamLingerTickDamage'], 1)
        self.assertEqual(out['surgeLingerTickDamage'], 2)


if __name__ == '__main__':
    unittest.main()
