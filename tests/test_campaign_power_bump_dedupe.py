#!/usr/bin/env python3
"""Headless tests: dedupe CampaignPower bump across purity + progress sync.

After #349 login rehydrate + #361 street trophy, live purityRestore and
AI progress sync both touched reclaimCount → COMBO_DAMAGE. Sync-before-
purity stacked a free extra bump. CampaignHandoff now keeps a synced
watermark, hydrates once, and purity absorbs AI absolute via max() so
both paths are idempotent.

Run from repo root:
  python3 tests/test_campaign_power_bump_dedupe.py
  python3 -m unittest tests.test_campaign_power_bump_dedupe -v
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
TTC = 2000


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_modules():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, REPO_ROOT.as_posix())

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim', 'toontown.campaign', 'toontown.hackslash'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = TTC
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    hs = types.ModuleType('toontown.hackslash.HackSlashConfig')
    hs.COMBO_DAMAGE = (8, 12, 28)
    sys.modules['toontown.hackslash.HackSlashConfig'] = hs
    sys.modules['toontown.hackslash'].HackSlashConfig = hs

    cg_path = REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
    cg_spec = importlib.util.spec_from_file_location(
        'toontown.corruption.CorruptionGlobals', cg_path)
    cg = importlib.util.module_from_spec(cg_spec)
    assert cg_spec.loader is not None
    sys.modules['toontown.corruption.CorruptionGlobals'] = cg
    cg_spec.loader.exec_module(cg)

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp

    power_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignPower.py'
    power_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignPower', power_path)
    power = importlib.util.module_from_spec(power_spec)
    assert power_spec.loader is not None
    sys.modules['toontown.campaign.CampaignPower'] = power
    power_spec.loader.exec_module(power)

    return camp, power, hs


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


class _PowerHandoffHarness:
    """Mirrors CampaignHandoffClient reclaim-power dedupe (no Panda / HUD)."""

    def __init__(self, power, pollution_count=0):
        self.power = power
        self._localReclaimCount = 0
        self._syncedReclaimCount = 0
        self._powerHydrated = False
        self._pollutionCount = int(pollution_count or 0)
        self.lastMult = 1.0

    def _pollutionReclaimCount(self):
        return max(0, int(self._pollutionCount or 0))

    def _applyReclaimPower(self, count):
        count = max(0, int(count or 0))
        self._localReclaimCount = max(self._localReclaimCount, count)
        self.lastMult = self.power.applyPowerBump(self._localReclaimCount)
        return self.lastMult

    def onSync(self, reclaimCount=0):
        count = max(0, int(reclaimCount or 0))
        self._syncedReclaimCount = max(self._syncedReclaimCount, count)
        self._pollutionCount = max(self._pollutionCount, count)
        if not self._powerHydrated:
            self._localReclaimCount = count
            self._powerHydrated = True
        self.lastMult = self.power.applyPowerBump(
            max(self._localReclaimCount, self._syncedReclaimCount))
        return self.lastMult

    def onPurity(self):
        self._powerHydrated = True
        synced = max(self._syncedReclaimCount, self._pollutionReclaimCount())
        if synced > self._localReclaimCount:
            return self._applyReclaimPower(synced)
        return self._applyReclaimPower(self._localReclaimCount + 1)


class CampaignPowerBumpDedupeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.power, cls.hs = _load_panda_free_modules()

    def setUp(self):
        self.hs.COMBO_DAMAGE = (8, 12, 28)
        self.power._BASE_DAMAGE = None

    def _expected_mult(self, count):
        bump = min(
            self.camp.POWER_BUMP_MAX,
            max(0.0, float(count) * self.camp.POWER_BUMP_PER_RECLAIM))
        return 1.0 + bump

    def test_sync_before_purity_does_not_double_bump(self):
        """AI persist push then purityRestore → one COMBO_DAMAGE step."""
        h = _PowerHandoffHarness(self.power)
        # Boot hydrate at 0 (PlayEntry requestCampaignProgress).
        h.onSync(0)
        self.assertEqual(h._localReclaimCount, 0)
        # Mid-act clear: sync lands first with absolute reclaimCount=1.
        h.onSync(1)
        self.assertEqual(h._localReclaimCount, 0)  # live watermark not raised
        self.assertAlmostEqual(h.lastMult, self._expected_mult(1))
        # Purity absorbs absolute — no stacked +=1.
        h.onPurity()
        self.assertEqual(h._localReclaimCount, 1)
        self.assertAlmostEqual(h.lastMult, self._expected_mult(1))
        self.assertEqual(
            self.hs.COMBO_DAMAGE,
            tuple(max(1, int(round(d * self._expected_mult(1))))
                  for d in (8, 12, 28)))

    def test_purity_before_sync_still_advances_once(self):
        h = _PowerHandoffHarness(self.power)
        h.onSync(0)
        h.onPurity()
        self.assertEqual(h._localReclaimCount, 1)
        self.assertAlmostEqual(h.lastMult, self._expected_mult(1))
        # Later persist push matches — idempotent, no extra step.
        h.onSync(1)
        self.assertEqual(h._localReclaimCount, 1)
        self.assertAlmostEqual(h.lastMult, self._expected_mult(1))

    def test_login_hydrate_then_live_clear_advances(self):
        h = _PowerHandoffHarness(self.power)
        h.onSync(3)  # relog mid-campaign
        self.assertEqual(h._localReclaimCount, 3)
        self.assertAlmostEqual(h.lastMult, self._expected_mult(3))
        h.onPurity()  # new street clear
        self.assertEqual(h._localReclaimCount, 4)
        self.assertAlmostEqual(h.lastMult, self._expected_mult(4))

    def test_mid_act_sync_before_purity_from_prior_count(self):
        h = _PowerHandoffHarness(self.power)
        h.onSync(2)
        self.assertEqual(h._localReclaimCount, 2)
        # Next clear: sync absolute 3 before purity FX.
        h.onSync(3)
        self.assertEqual(h._localReclaimCount, 2)
        h.onPurity()
        self.assertEqual(h._localReclaimCount, 3)
        self.assertAlmostEqual(h.lastMult, self._expected_mult(3))

    def test_handoff_source_wires_idempotent_dedupe(self):
        rel = 'toontown/campaign/CampaignHandoff.py'
        src = _read(rel)
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'CampaignHandoffClient')
        for name in (
                '_onCampaignProgressSync',
                '_onPurityRestore',
                '_applyReclaimPower',
                '_pollutionReclaimCount'):
            self.assertIn(name, methods)

        self.assertIn('_syncedReclaimCount', src)
        self.assertIn('_powerHydrated', src)
        self.assertIn('campaignReclaimCount', src)

        sync_idx = src.find('def _onCampaignProgressSync')
        sync_win = src[sync_idx:sync_idx + 1100]
        self.assertIn('_syncedReclaimCount', sync_win)
        self.assertIn('_powerHydrated', sync_win)
        self.assertIn('applyPowerBump', sync_win)
        self.assertNotIn('_celebrate', sync_win)

        purity_idx = src.find('def _onPurityRestore')
        purity_win = src[purity_idx:purity_idx + 900]
        self.assertIn('_applyReclaimPower', purity_win)
        self.assertIn('synced > self._localReclaimCount', purity_win)
        self.assertIn('self._localReclaimCount + 1', purity_win)
        # Blind +=1 was the double-bump race — must stay gone.
        self.assertNotIn('_localReclaimCount += 1', purity_win)

    def test_no_kh_or_cream_scope_creep(self):
        blob = _read('toontown/campaign/CampaignHandoff.py').lower()
        # Affirmative KH product copy only — "no KH" docs stay allowed.
        for banned in ('kingdom hearts', 'sora', 'keyblade'):
            if banned not in blob:
                continue
            if ('no %s' % banned) in blob or ('no kh') in blob:
                continue
            if ('without %s' % banned) in blob:
                continue
            # Existing module docstring mentions no KH framing — allow.
            if 'no kh' in blob or 'not kh' in blob:
                continue
            self.fail('CampaignHandoff contains affirmative %r' % banned)


if __name__ == '__main__':
    unittest.main()
