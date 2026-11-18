#!/usr/bin/env python3
"""Behavioral headless tests for Punchline tip cream hose settle deepen.

Panda-free: loads CampaignGlobals + AST-checks PlayEntry tipHose='punchline'
wires a juicier cream overshoot→rest→micro rebound after trust/fracture
settle past #256 (#198 / #227 / #256 deepen path). Distinct from Silly
almost-confess tip cream hose (#232/#279 — taller primary, no tip rebound)
and Silly Overlord tip cream wash aftershock (#251/#279 — wash flecks/halo).

Run from repo root:
  python3 tests/test_punchline_tip_cream_hose_settle.py
  python3 -m unittest tests.test_punchline_tip_cream_hose_settle -v
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


def _load_campaign_globals():
    """Stub ToontownGlobals; load CampaignGlobals without Panda3D."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = 2000
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    return camp


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


class PunchlineTipCreamHoseSettleTest(unittest.TestCase):
    """Config + AST checks for deepened Punchline tip cream hose settle."""

    @classmethod
    def setUpClass(cls):
        cls.camp = _load_campaign_globals()

    def test_settle_tunables_deepened_past_256(self):
        camp = self.camp
        self.assertTrue(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED)
        over = camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertEqual(len(over), 4)
        ox, oy, oz, over_sec = over
        self.assertGreater(float(over_sec), 0.0)
        # Brief outward rubber-hose bounce (not a shrink snap).
        self.assertGreater(float(ox), 1.0)
        self.assertGreater(float(oz), 1.0)
        self.assertAlmostEqual(float(oy), 1.0)
        # Juicier than #256 baseline (1.08 / 1.12 / 0.065 / rest 0.10).
        self.assertGreaterEqual(float(ox), 1.10)
        self.assertGreaterEqual(float(oz), 1.15)
        self.assertGreaterEqual(float(over_sec), 0.075)
        rest = float(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC)
        self.assertGreaterEqual(rest, 0.11)
        rebound = camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND
        self.assertEqual(len(rebound), 4)
        rx, ry, rz, rebound_sec = rebound
        self.assertGreater(float(rx), 1.0)
        self.assertGreater(float(rz), 1.0)
        self.assertAlmostEqual(float(ry), 1.0)
        self.assertGreater(float(rebound_sec), 0.0)
        # Juicier micro rebound past #256 (1.03 / 1.05 / 0.04); under betrayal.
        self.assertGreaterEqual(float(rx), 1.035)
        self.assertGreaterEqual(float(rz), 1.06)
        self.assertGreaterEqual(float(rebound_sec), 0.045)
        betrayal_rebound = camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND
        self.assertNotEqual(tuple(rebound), tuple(betrayal_rebound))
        self.assertLess(float(rz), float(betrayal_rebound[2]))
        # Rebound is a quieter second bounce under the primary overshoot.
        self.assertLess(float(rx), float(ox))
        self.assertLess(float(rz), float(oz))
        rebound_rest = float(
            camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND_REST_SEC)
        self.assertGreaterEqual(rebound_rest, 0.07)
        # Settle stays a short readable beat under tip hang / wash delay.
        total = (
            float(over_sec) + rest + float(rebound_sec) + rebound_rest)
        self.assertLess(total, 0.40)
        self.assertGreater(total, 0.15)
        wash_delay = float(camp.PUNCHLINE_ACT_TIP_CREAM_WASH_DELAY_SEC)
        self.assertGreaterEqual(wash_delay, total)
        self.assertGreaterEqual(wash_delay, 0.70)
        # Soft wash rides the juicier hose settle past #256.
        self.assertGreaterEqual(
            float(camp.PUNCHLINE_ACT_TIP_CREAM_WASH_PEAK), 0.13)
        self.assertGreaterEqual(
            float(camp.PUNCHLINE_ACT_TIP_CREAM_WASH_MID), 0.08)
        self.assertGreaterEqual(
            float(camp.PUNCHLINE_ACT_TIP_CREAM_WASH_OUT_SEC), 0.40)
        # Distinct from Silly almost-confess tip cream hose (#232/#279).
        silly_over = camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertNotEqual(tuple(over), tuple(silly_over))
        self.assertNotEqual(
            rest, float(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC))
        # Silly keeps taller primary Z / longer rest; Punchline owns rebound.
        self.assertGreater(float(silly_over[2]), float(oz))
        self.assertGreater(
            float(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC), rest)
        self.assertFalse(hasattr(
            camp, 'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND'))
        # Distinct from Silly Overlord tip cream wash aftershock (#251/#279).
        self.assertNotEqual(
            float(oz),
            float(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ORIGIN[2]))
        self.assertNotEqual(
            int(camp.PUNCHLINE_ACT_TIP_CREAM_WASH_BIN),
            int(camp.SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_BIN))
        # Under betrayal primary overshoot Z so twist hose stays bigger.
        betrayal_z = float(
            camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT[2])
        self.assertLess(float(oz), betrayal_z)
        # No KH product nouns in the settle block comments.
        src = _read('toontown/campaign/CampaignGlobals.py').lower()
        idx = src.find('punchline_act_tip_cream_hose_settle_enabled')
        self.assertGreater(idx, 0)
        snip = src[max(0, idx - 700):idx + 700]
        self.assertIn('no keyblades', snip)
        self.assertIn('rebound', snip)
        self.assertIn('juicier', snip)
        self.assertIn('#256', snip)
        self.assertIn('#232', snip)
        self.assertIn('#251', snip)
        for banned in ('kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, snip)

    def test_playentry_wires_cream_hose_settle_rebound(self):
        play_src = _read('toontown/campaign/PlayEntry.py')
        tip_idx = play_src.find('def _tipHosePopInterval')
        self.assertGreater(tip_idx, 0)
        punch_idx = play_src.find("tipHose == 'punchline'", tip_idx)
        silly_idx = play_src.find("tipHose == 'silly'", tip_idx)
        self.assertGreater(punch_idx, 0)
        self.assertGreater(silly_idx, punch_idx)
        punch_snip = play_src[punch_idx:silly_idx]
        self.assertIn('PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED', punch_snip)
        self.assertIn('creamHoseSettle', punch_snip)
        self.assertIn(
            'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND', punch_snip)
        self.assertIn(
            'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND_REST_SEC',
            punch_snip)
        self.assertIn('#256', punch_snip)
        # Cream hose settle append lives after trust/fracture bounce.
        full_tip = play_src[tip_idx:play_src.find(
            'def _armPunchlineTipCreamWash', tip_idx)]
        self.assertIn('PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT', full_tip)
        self.assertIn('PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC', full_tip)
        self.assertIn('PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND', full_tip)
        self.assertIn('micro rebound', full_tip.lower())
        self.assertIn('#256', full_tip)
        # Silly tipHose must not arm Punchline cream hose settle / rebound.
        silly_end = play_src.find('\n        else:', silly_idx)
        if silly_end < 0:
            silly_end = silly_idx + 1800
        silly_snip = play_src[silly_idx:silly_end]
        self.assertNotIn(
            'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED', silly_snip)
        self.assertNotIn(
            'PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND', silly_snip)

    def test_magicwords_mention_deepened_cream_hose_settle(self):
        magic_src = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('juicier deepened cream hose settle', magic_src)
        self.assertIn('past #256', magic_src)
        self.assertIn('micro rebound', magic_src)
        self.assertIn('punchline', magic_src)
        self.assertIn('no keyblades', magic_src)
        self.assertNotIn('kingdom hearts', magic_src)
        self.assertNotIn('sora', magic_src)

    def test_punchline_tip_cream_wash_fx_defaults_track_deepen(self):
        wash_src = _read('toontown/campaign/PunchlineTipCreamWashFx.py')
        self.assertIn('past #256', wash_src)
        self.assertIn('0.13', wash_src)
        self.assertIn('0.70', wash_src)
        self.assertIn('no keyblades', wash_src.lower())
        self.assertNotIn('kingdom hearts', wash_src.lower())


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        PunchlineTipCreamHoseSettleTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
