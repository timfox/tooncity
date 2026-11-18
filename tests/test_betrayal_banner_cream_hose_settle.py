#!/usr/bin/env python3
"""Behavioral headless tests for betrayal banner cream hose settle deepen.

Panda-free: loads CampaignGlobals + AST-checks CampaignHandoff betrayal
title hose-pop appends juicier cream overshoot→rest→micro rebound after
betrayal settle (#212 / #235 deepen). Distinct from Punchline tip cream
hose rebound (#256 — tip bar) and Silly almost-confess tip cream hose
(#232 — taller tip primary, no tip rebound).

Run from repo root:
  python3 tests/test_betrayal_banner_cream_hose_settle.py
  python3 -m unittest tests.test_betrayal_banner_cream_hose_settle -v
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


class BetrayalBannerCreamHoseSettleTest(unittest.TestCase):
    """Config + AST checks for deepened betrayal banner cream hose settle."""

    @classmethod
    def setUpClass(cls):
        cls.camp = _load_campaign_globals()

    def test_settle_tunables_deepened(self):
        camp = self.camp
        self.assertTrue(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_ENABLED)
        over = camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertEqual(len(over), 4)
        ox, oy, oz, over_sec = over
        self.assertGreater(float(over_sec), 0.0)
        # Brief outward rubber-hose bounce (not a shrink snap).
        self.assertGreater(float(ox), 1.0)
        self.assertGreater(float(oz), 1.0)
        self.assertAlmostEqual(float(oy), 1.0)
        # Juicier than #235 baseline (1.12 / 1.18 / 0.08 / rest 0.13).
        self.assertGreaterEqual(float(ox), 1.14)
        self.assertGreaterEqual(float(oz), 1.22)
        self.assertGreaterEqual(float(over_sec), 0.09)
        rest = float(camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REST_SEC)
        self.assertGreaterEqual(rest, 0.14)
        rebound = camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND
        self.assertEqual(len(rebound), 4)
        rx, ry, rz, rebound_sec = rebound
        self.assertGreater(float(rx), 1.0)
        self.assertGreater(float(rz), 1.0)
        self.assertAlmostEqual(float(ry), 1.0)
        self.assertGreater(float(rebound_sec), 0.0)
        # Rebound is a quieter second bounce under the primary overshoot.
        self.assertLess(float(rx), float(ox))
        self.assertLess(float(rz), float(oz))
        rebound_rest = float(
            camp.FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND_REST_SEC)
        self.assertGreater(rebound_rest, 0.0)
        # Settle stays a short readable climax beat.
        total = (
            float(over_sec) + rest + float(rebound_sec) + rebound_rest)
        self.assertLess(total, 0.45)
        self.assertGreater(total, 0.20)
        # Distinct from Punchline tip cream hose rebound (#256) and Silly #232.
        punch_over = camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT
        silly_over = camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT
        self.assertNotEqual(tuple(over), tuple(punch_over))
        self.assertNotEqual(tuple(over), tuple(silly_over))
        self.assertNotEqual(
            rest, float(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC))
        self.assertNotEqual(
            rest, float(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC))
        self.assertNotEqual(
            tuple(rebound),
            tuple(camp.PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND))
        self.assertNotEqual(
            tuple(rebound),
            tuple(camp.HANDOFF_CREAM_EDGE_SETTLE_REBOUND))
        # Juicier climax than tip settles: taller Z and longer rest.
        self.assertGreater(float(oz), float(silly_over[2]))
        self.assertGreater(
            rest, float(camp.SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC))
        # Silly tip keeps no tip rebound; betrayal title owns climax rebound.
        self.assertFalse(hasattr(
            camp, 'SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND'))
        # No KH product nouns in the settle block comments.
        src = _read('toontown/campaign/CampaignGlobals.py').lower()
        idx = src.find('finale_betrayal_cream_hose_settle_enabled')
        self.assertGreater(idx, 0)
        snip = src[max(0, idx - 650):idx + 650]
        self.assertIn('no keyblades', snip)
        self.assertIn('betrayal', snip)
        self.assertIn('rebound', snip)
        self.assertIn('juicier', snip)
        self.assertIn('#235', snip)
        self.assertIn('#256', snip)
        for banned in ('kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, snip)

    def test_handoff_wires_cream_hose_settle_rebound(self):
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        title_idx = handoff_src.find('def _titleHosePopInterval')
        self.assertGreater(title_idx, 0)
        title_end = handoff_src.find(
            '\n    def _trustSubHosePopInterval', title_idx)
        if title_end < 0:
            title_end = title_idx + 3600
        title_snip = handoff_src[title_idx:title_end]
        self.assertIn('FINALE_BETRAYAL_CREAM_HOSE_SETTLE_ENABLED', title_snip)
        self.assertIn('FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT', title_snip)
        self.assertIn(
            'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REST_SEC', title_snip)
        self.assertIn(
            'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND', title_snip)
        self.assertIn(
            'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND_REST_SEC', title_snip)
        self.assertIn('betrayalHandoff', title_snip)
        self.assertIn('micro rebound', title_snip.lower())
        # Betrayal settle still lands before cream hose settle / rebound.
        betr_settle = title_snip.find('FINALE_BETRAYAL_SETTLE_OVERSHOOT')
        cream_settle = title_snip.find(
            'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT')
        cream_rebound = title_snip.find(
            'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND')
        self.assertGreater(betr_settle, 0)
        self.assertGreater(cream_settle, betr_settle)
        self.assertGreater(cream_rebound, cream_settle)
        # Module doc mentions deepened cream hose settle on betrayal plate.
        self.assertIn('deepened cream hose settle', handoff_src.lower())
        self.assertIn('micro rebound', handoff_src.lower())

    def test_magicwords_mention_deepened_betrayal_cream_hose_settle(self):
        magic_src = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('deepened cream hose', magic_src)
        self.assertIn('micro rebound', magic_src)
        self.assertIn('betrayal handoff banner', magic_src)
        self.assertIn('no keyblades', magic_src)
        self.assertNotIn('kingdom hearts', magic_src)
        self.assertNotIn('sora', magic_src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        BetrayalBannerCreamHoseSettleTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
