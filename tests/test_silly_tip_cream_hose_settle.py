#!/usr/bin/env python3
"""Behavioral headless tests for Silly tip cream hose settle.

Panda-free: loads CampaignGlobals + AST-checks PlayEntry tipHose='silly'
wires a juicier cream overshoot→rest after trust/fracture settle (#207
almost-confess path). Distinct from Punchline tip cream hose settle (#227).

Run from repo root:
  python3 tests/test_silly_tip_cream_hose_settle.py
  python3 -m unittest tests.test_silly_tip_cream_hose_settle -v
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


class SillyTipCreamHoseSettleTest(unittest.TestCase):
    """Config + AST checks for Silly almost-confess tip cream hose settle."""

    @classmethod
    def setUpClass(cls):
        cls.camp = _load_campaign_globals()

    def test_settle_tunables(self):
        camp = self.camp
        self.assertTrue(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED)
        over = camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertEqual(len(over), 4)
        ox, oy, oz, over_sec = over
        self.assertGreater(float(over_sec), 0.0)
        # Brief outward rubber-hose bounce (not a shrink snap).
        self.assertGreater(float(ox), 1.0)
        self.assertGreater(float(oz), 1.0)
        self.assertAlmostEqual(float(oy), 1.0)
        rest = float(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC)
        self.assertGreater(rest, 0.0)
        # Settle stays a short readable beat under tip hang / wash delay.
        total = float(over_sec) + rest
        self.assertLess(total, 0.35)
        self.assertGreater(total, 0.08)
        wash_delay = float(camp.SILLY_ACT_TIP_CREAM_WASH_DELAY_SEC)
        self.assertGreaterEqual(wash_delay, total)
        # Distinct from Punchline #227 cream hose settle tunables.
        punch_over = camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertNotEqual(tuple(over), tuple(punch_over))
        self.assertNotEqual(
            rest, float(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC))
        # Juicier than Punchline: taller Z and longer rest.
        self.assertGreater(float(oz), float(punch_over[2]))
        self.assertGreater(
            rest, float(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC))
        # No KH product nouns in the settle block comments.
        src = _read('toontown/campaign/CampaignGlobals.py').lower()
        idx = src.find('silly_act_tip_cream_hose_settle_enabled')
        self.assertGreater(idx, 0)
        snip = src[max(0, idx - 500):idx + 500]
        self.assertIn('no keyblades', snip)
        self.assertIn('almost-confess', snip)
        for banned in ('kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, snip)

    def test_playentry_wires_cream_hose_settle(self):
        play_src = _read('toontown/campaign/PlayEntry.py')
        tip_idx = play_src.find('def _tipHosePopInterval')
        self.assertGreater(tip_idx, 0)
        punch_idx = play_src.find("tipHose == 'punchline'", tip_idx)
        silly_idx = play_src.find("tipHose == 'silly'", tip_idx)
        self.assertGreater(punch_idx, 0)
        self.assertGreater(silly_idx, punch_idx)
        silly_end = play_src.find('\n        else:', silly_idx)
        if silly_end < 0:
            silly_end = silly_idx + 1800
        silly_snip = play_src[silly_idx:silly_end]
        self.assertIn('SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED', silly_snip)
        self.assertIn('creamHoseSettle', silly_snip)
        self.assertIn('SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT', silly_snip)
        self.assertIn('SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC', silly_snip)
        # Punchline tipHose must not arm Silly cream hose settle.
        punch_snip = play_src[punch_idx:silly_idx]
        self.assertNotIn(
            'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED', punch_snip)
        # Approach tip still reuses tipHose='silly' (almost-confess path).
        self.assertIn("tipHose='silly'", play_src)
        self.assertIn('_showSillyApproachTip', play_src)

    def test_magicwords_mention_cream_hose_settle(self):
        magic_src = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('cream hose settle', magic_src)
        self.assertIn('silly', magic_src)
        self.assertIn('almost confess', magic_src)
        self.assertIn('no keyblades', magic_src)
        self.assertNotIn('kingdom hearts', magic_src)
        self.assertNotIn('sora', magic_src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SillyTipCreamHoseSettleTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
