#!/usr/bin/env python3
"""Headless tests: authoritative CampaignPower melee table from reclaimCount.

After #366, AI melee used process COMBO_DAMAGE baseline while client
CampaignPower mutated a separate table. Locks shared POWER_BUMP_* math
(HackSlashConfig.comboDamageTableFromReclaimCount) + CorruptToonAI
reclaimCount push so mid-campaign reclaim power changes hostile HP drain.
No Panda3D / no cream / no KH.

Run from repo root:
  python3 tests/test_campaign_power_melee_table.py
  python3 -m unittest tests.test_campaign_power_melee_table -v
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


def _load_modules():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

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

    cfg_path = REPO_ROOT / 'toontown' / 'hackslash' / 'HackSlashConfig.py'
    cfg_spec = importlib.util.spec_from_file_location(
        'toontown.hackslash.HackSlashConfig', cfg_path)
    cfg = importlib.util.module_from_spec(cfg_spec)
    assert cfg_spec.loader is not None
    sys.modules['toontown.hackslash.HackSlashConfig'] = cfg
    cfg_spec.loader.exec_module(cfg)
    sys.modules['toontown.hackslash'].HackSlashConfig = cfg

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp

    # Real CampaignPower against the loaded HackSlashConfig (shared helper).
    power_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignPower.py'
    # Fresh load so _BASE_DAMAGE re-captures current COMBO_DAMAGE.
    for key in list(sys.modules):
        if key.endswith('CampaignPower'):
            del sys.modules[key]
    power_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignPower', power_path)
    power = importlib.util.module_from_spec(power_spec)
    assert power_spec.loader is not None
    sys.modules['toontown.campaign.CampaignPower'] = power
    power_spec.loader.exec_module(power)

    return cfg, camp, power


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel))


def _class_method(tree: ast.AST, class_name: str, method_name: str):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if (isinstance(child, ast.FunctionDef)
                        and child.name == method_name):
                    return child
    return None


class CampaignPowerMeleeTableTest(unittest.TestCase):
    """Shared POWER_BUMP table + AI reclaimCount wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cfg, cls.camp, cls.power = _load_modules()

    def setUp(self):
        # Keep baseline table stable across cases that mutate COMBO_DAMAGE.
        self.cfg.COMBO_DAMAGE = (8, 12, 28)
        self.power._BASE_DAMAGE = None
        self.power.resetPowerBump()

    def test_power_bump_multiplier_matches_campaign_globals(self):
        per = self.camp.POWER_BUMP_PER_RECLAIM
        cap = self.camp.POWER_BUMP_MAX
        self.assertAlmostEqual(
            self.cfg.powerBumpMultiplier(0, perReclaim=per, bumpMax=cap),
            1.0)
        self.assertAlmostEqual(
            self.cfg.powerBumpMultiplier(1, perReclaim=per, bumpMax=cap),
            1.0 + per)
        self.assertAlmostEqual(
            self.cfg.powerBumpMultiplier(3, perReclaim=per, bumpMax=cap),
            1.0 + min(cap, 3 * per))
        self.assertAlmostEqual(
            self.cfg.powerBumpMultiplier(99, perReclaim=per, bumpMax=cap),
            1.0 + cap)
        # Defaults match authored campaign constants.
        self.assertAlmostEqual(
            self.cfg.POWER_BUMP_PER_RECLAIM_DEFAULT, per)
        self.assertAlmostEqual(self.cfg.POWER_BUMP_MAX_DEFAULT, cap)

    def test_combo_table_scales_like_apply_power_bump(self):
        base = (8, 12, 28)
        per = self.camp.POWER_BUMP_PER_RECLAIM
        cap = self.camp.POWER_BUMP_MAX
        for count in (0, 1, 3, 5, 99):
            table = self.cfg.comboDamageTableFromReclaimCount(
                count, baseTable=base, perReclaim=per, bumpMax=cap)
            mult = self.power.applyPowerBump(count)
            self.assertEqual(table, tuple(self.cfg.COMBO_DAMAGE))
            self.assertEqual(
                table,
                tuple(max(1, int(round(d * mult))) for d in base))
            # AI helper path must match client mutation for the same count.
            for idx, amount in enumerate(table):
                self.assertEqual(
                    self.cfg.meleeDamageFromHitIndex(
                        idx, damageTable=table),
                    int(amount))

    def test_melee_helper_with_reclaim_table_exceeds_baseline(self):
        base = self.cfg.COMBO_DAMAGE
        bumped = self.cfg.comboDamageTableFromReclaimCount(
            3,
            baseTable=base,
            perReclaim=self.camp.POWER_BUMP_PER_RECLAIM,
            bumpMax=self.camp.POWER_BUMP_MAX)
        self.assertGreater(bumped[0], base[0])
        self.assertGreater(bumped[-1], base[-1])
        self.assertEqual(
            self.cfg.meleeDamageFromHitIndex(0, damageTable=bumped),
            int(bumped[0]))
        self.assertEqual(
            self.cfg.meleeDamageFromHitIndex(0),
            int(base[0]))
        # Ceiling still clamps spoofed reclaim tables.
        huge = self.cfg.comboDamageTableFromReclaimCount(
            0, baseTable=(999, 999, 999))
        self.assertEqual(
            self.cfg.meleeDamageFromHitIndex(0, damageTable=huge),
            int(self.cfg.MELEE_DAMAGE_MAX))

    def test_ai_pushes_reclaim_count_into_damage_table(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        src = _read(rel)
        tree = _module_ast(rel)
        req = _class_method(
            tree, 'DistributedCorruptToonAI', 'requestHackSlashHit')
        self.assertIsNotNone(req)
        req_src = ast.get_source_segment(src, req) or ''
        self.assertIn('__campaignPowerDamageTable', req_src)
        self.assertIn('damageTable=table', req_src)
        self.assertIn('meleeDamageFromHitIndex', req_src)

        helper = _class_method(
            tree, 'DistributedCorruptToonAI', '__campaignPowerDamageTable')
        self.assertIsNotNone(helper)
        helper_src = ast.get_source_segment(src, helper) or ''
        self.assertIn('getCampaignDirector', helper_src)
        self.assertIn('reclaimCount', helper_src)
        self.assertIn('comboDamageTableFromReclaimCount', helper_src)
        self.assertIn('POWER_BUMP_PER_RECLAIM', helper_src)
        self.assertIn('POWER_BUMP_MAX', helper_src)

    def test_campaign_power_uses_shared_helper(self):
        power_src = _read('toontown/campaign/CampaignPower.py')
        apply_idx = power_src.find('def applyPowerBump')
        self.assertGreater(apply_idx, 0)
        apply_win = power_src[apply_idx:apply_idx + 1200]
        self.assertIn('comboDamageTableFromReclaimCount', apply_win)
        self.assertIn('powerBumpMultiplier', apply_win)
        self.assertIn('POWER_BUMP_PER_RECLAIM', apply_win)

    def test_exports_and_no_kh(self):
        init_src = _read('toontown/hackslash/__init__.py')
        self.assertIn('comboDamageTableFromReclaimCount', init_src)
        self.assertIn('powerBumpMultiplier', init_src)
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        block = cfg_src.split(
            'def comboDamageTableFromReclaimCount', 1)[1][:900].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, block)
        self.assertIn('rubber-hose', block)
        target = _read('toontown/corruption/HackSlashTarget.py')
        self.assertIn('reclaimCount', target)
        self.assertIn('POWER_BUMP', target)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        CampaignPowerMeleeTableTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
