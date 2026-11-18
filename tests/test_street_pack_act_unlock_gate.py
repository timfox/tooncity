#!/usr/bin/env python3
"""Headless / AST tests for soft-gating STREET_PACKS reclaim behind act unlock.

Punchline / Silly street-pack R must not skip story acts. Loopy (act 0)
stays open so discoverable play entry works. Soft nudge only — not a hard
brick on tips / breadcrumbs / explore.

Run from repo root:
  python3 tests/test_street_pack_act_unlock_gate.py
  python3 -m unittest tests.test_street_pack_act_unlock_gate -v
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
HUB = 2000


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_and_func_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                n.name for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
    return set()


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_reclaim_and_campaign():
    """Stub ToontownGlobals, load CorruptionGlobals + ReclaimGlobals + CampaignGlobals."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim', 'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = HUB
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

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp
    return rg, cg, camp


class StreetPackActUnlockGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.cg, cls.camp = _load_panda_free_reclaim_and_campaign()

    def test_required_act_index_matches_acts_order(self):
        rg = self.rg
        self.assertEqual(rg.streetPackRequiredActIndex(LOOPY), 0)
        self.assertEqual(rg.streetPackRequiredActIndex(PUNCHLINE), 1)
        self.assertEqual(rg.streetPackRequiredActIndex(SILLY), 2)
        # Non-pack / unknown zone → fail-open (None).
        self.assertIsNone(rg.streetPackRequiredActIndex(HUB))
        self.assertIsNone(rg.streetPackRequiredActIndex(9999))

    def test_loopy_always_unlocked_for_discoverable_entry(self):
        rg = self.rg
        self.assertTrue(rg.streetPackUnlocked(LOOPY, 0))
        self.assertTrue(rg.streetPackUnlocked(LOOPY, -1))
        self.assertTrue(rg.streetPackUnlocked(LOOPY, 2))

    def test_punchline_and_silly_soft_gated_until_unlock(self):
        rg = self.rg
        # Fresh session — Punchline / Silly skip story if R fields packs.
        self.assertFalse(rg.streetPackUnlocked(PUNCHLINE, 0))
        self.assertFalse(rg.streetPackUnlocked(SILLY, 0))
        # After Loopy clear unlocks act 1.
        self.assertTrue(rg.streetPackUnlocked(PUNCHLINE, 1))
        self.assertFalse(rg.streetPackUnlocked(SILLY, 1))
        # After Punchline clear unlocks finale.
        self.assertTrue(rg.streetPackUnlocked(SILLY, 2))
        # Unknown zones stay open (soft, not a hard brick).
        self.assertTrue(rg.streetPackUnlocked(HUB, 0))
        self.assertTrue(rg.streetPackUnlocked(9999, 0))

    def test_gate_message_points_at_frontier_street(self):
        rg = self.rg
        punch_msg = rg.streetPackGateMessage(PUNCHLINE, 0, face='Oswald')
        self.assertIn('Punchline Place', punch_msg)
        self.assertIn('Loopy Lane', punch_msg)
        self.assertIn('Oswald', punch_msg)
        # No zone ids / magic-word memorization in the soft nudge.
        self.assertNotIn('2300', punch_msg)
        self.assertNotIn('~startreclaim', punch_msg)
        self.assertNotIn('keyblade', punch_msg.lower())

        silly_msg = rg.streetPackGateMessage(SILLY, 1, face='Oswald')
        self.assertIn('Silly Street', silly_msg)
        self.assertIn('Punchline Place', silly_msg)

    def test_ast_helpers_and_wiring(self):
        rg_names = _class_and_func_names(
            _module_ast('toontown/reclaim/ReclaimGlobals.py'))
        for sym in (
                'streetPackRequiredActIndex',
                'streetPackUnlocked',
                'streetPackGateMessage',
                'streetPackParams'):
            self.assertIn(sym, rg_names)

        director_methods = _class_method_names(
            _module_ast('toontown/reclaim/DistributedReclaimDirectorAI.py'),
            'DistributedReclaimDirectorAI')
        self.assertIn('startStreetPackForToon', director_methods)

        director_src = _read(
            'toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('streetPackUnlocked', director_src)
        self.assertIn('unlockedThrough', director_src)
        self.assertIn('force', director_src)
        # Soft-gate must not hard-brick Loopy discoverability wording.
        self.assertIn('Loopy', director_src)
        # R must hydrate CampaignProgressSave before reading unlocks
        # (C already does this in startCampaign; R was the soft-gate leak).
        start_idx = director_src.find('def startStreetPackForToon')
        self.assertGreater(start_idx, 0)
        start_snip = director_src[start_idx:start_idx + 2200]
        self.assertIn('_hydrateFromToon', start_snip)
        hydrate_pos = start_snip.find('_hydrateFromToon')
        unlock_pos = start_snip.find('unlockedThrough', hydrate_pos)
        self.assertGreater(hydrate_pos, 0)
        self.assertGreater(unlock_pos, hydrate_pos)

        pollution_src = _read(
            'toontown/corruption/PollutionManagerAI.py')
        self.assertIn('startStreetPackForToon', pollution_src)
        # Prefer reclaim helper over inlined street-pack spawn on R.
        reclaim_event = pollution_src.find('requestStreetEvent')
        self.assertGreater(reclaim_event, 0)
        snip = pollution_src[reclaim_event:reclaim_event + 1800]
        self.assertIn('startStreetPackForToon', snip)

        magic_src = _read('toontown/reclaim/MagicWords.py')
        self.assertIn('startStreetPackForToon', magic_src)
        self.assertIn('force', magic_src)
        # PlayEntry auto still prefers campaign (C), not street-pack R.
        play_src = _read('toontown/campaign/PlayEntry.py')
        auto_idx = play_src.find('def _autoStartReclaim')
        self.assertGreater(auto_idx, 0)
        auto_snip = play_src[auto_idx:auto_idx + 800]
        self.assertIn('_requestCampaign()', auto_snip)
        self.assertNotIn('_requestReclaim()', auto_snip)


if __name__ == '__main__':
    unittest.main()
