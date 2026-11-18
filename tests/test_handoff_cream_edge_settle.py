#!/usr/bin/env python3
"""Behavioral headless tests for act handoff cream edge settle.

Panda-free: loads CampaignGlobals + AST-checks ActBannerCreamEdgeFx /
CampaignHandoff wiring for Loopy→Punchline→Silly cream edge overshoot→rest.

Run from repo root:
  python3 tests/test_handoff_cream_edge_settle.py
  python3 -m unittest tests.test_handoff_cream_edge_settle -v
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


class HandoffCreamEdgeSettleTest(unittest.TestCase):
    """Config + AST checks for act handoff cream edge settle."""

    @classmethod
    def setUpClass(cls):
        cls.camp = _load_campaign_globals()

    def test_settle_tunables(self):
        camp = self.camp
        self.assertTrue(camp.HANDOFF_CREAM_EDGE_SETTLE_ENABLED)
        self.assertTrue(camp.HANDOFF_CREAM_EDGE_ENABLED)
        over = camp.HANDOFF_CREAM_EDGE_SETTLE_OVERSHOOT
        self.assertEqual(len(over), 4)
        ox, oy, oz, over_sec = over
        self.assertGreater(float(over_sec), 0.0)
        # Brief outward rubber-hose bounce (not a shrink snap).
        self.assertGreater(float(ox), 1.0)
        self.assertGreater(float(oz), 1.0)
        self.assertAlmostEqual(float(oy), 1.0)
        rest = float(camp.HANDOFF_CREAM_EDGE_SETTLE_REST_SEC)
        self.assertGreater(rest, 0.0)
        # Settle stays a short readable beat under the edge hang.
        total = (
            float(camp.HANDOFF_CREAM_EDGE_IN_SEC)
            + float(over_sec)
            + rest)
        self.assertLess(total, 0.45)
        self.assertGreater(total, 0.15)
        # No KH product nouns in the settle block comments.
        src = _read('toontown/campaign/CampaignGlobals.py').lower()
        idx = src.find('handoff_cream_edge_settle_enabled')
        self.assertGreater(idx, 0)
        snip = src[max(0, idx - 350):idx + 350]
        self.assertIn('no keyblades', snip)
        for banned in ('kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, snip)

    def test_edge_fx_wires_settle_scale(self):
        edge_src = _read('toontown/campaign/ActBannerCreamEdgeFx.py')
        self.assertIn('_settleScalePart', edge_src)
        self.assertIn('SETTLE_OVERSHOOT', edge_src)
        self.assertIn('SETTLE_REST_SEC', edge_src)
        self.assertIn('CreamEdgeSettle', edge_src)
        tree = ast.parse(edge_src)
        method_names = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == 'ActBannerCreamEdgeFx':
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_names.append(item.name)
        self.assertIn('_settleScalePart', method_names)
        self.assertIn('play', method_names)
        # play() must call settle helper.
        play_src = edge_src[edge_src.find('def play('):edge_src.find('def _settleScalePart')]
        self.assertIn('_settleScalePart', play_src)
        self.assertIn('SETTLE_ENABLED', edge_src)

    def test_handoff_path_arms_cream_edge(self):
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('playHandoffCreamEdge', handoff_src)
        self.assertIn('cream edge pulse with a brief', handoff_src.lower())
        magic_src = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('edge settle', magic_src)
        self.assertIn('no keyblades', magic_src)
        self.assertNotIn('kingdom hearts', magic_src)
        self.assertNotIn('sora', magic_src)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        HandoffCreamEdgeSettleTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
