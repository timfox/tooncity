#!/usr/bin/env python3
"""Headless tests: rehydrate CampaignPower from reclaimCount on login.

Loads CampaignGlobals / CampaignProgressSave / CampaignPower with a
ToontownGlobals stub — no Panda3D. Asserts POWER_BUMP math, clientMirror
reclaimCount, thin PollutionManager DC + AI push of reclaimCount, and
CampaignHandoff silent re-apply on campaignProgressSync so melee scale
survives relog.

Run from repo root:
  python3 tests/test_campaign_power_rehydrate.py
  python3 -m unittest tests.test_campaign_power_rehydrate -v
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

    # Stub HackSlashConfig so CampaignPower can mutate COMBO_DAMAGE.
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

    save_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignProgressSave.py'
    save_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignProgressSave', save_path)
    save = importlib.util.module_from_spec(save_spec)
    assert save_spec.loader is not None
    sys.modules['toontown.campaign.CampaignProgressSave'] = save
    save_spec.loader.exec_module(save)

    power_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignPower.py'
    power_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignPower', power_path)
    power = importlib.util.module_from_spec(power_spec)
    assert power_spec.loader is not None
    sys.modules['toontown.campaign.CampaignPower'] = power
    power_spec.loader.exec_module(power)

    return camp, save, power, hs


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


def _accept_events(tree: ast.AST, class_name: str) -> set[str]:
    """Collect string / name event targets passed to self.accept in a class."""
    events = set()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in ast.walk(node):
            if not isinstance(item, ast.Call):
                continue
            func = item.func
            if not (isinstance(func, ast.Attribute) and func.attr == 'accept'):
                continue
            if not item.args:
                continue
            arg0 = item.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                events.add(arg0.value)
            elif isinstance(arg0, ast.Str):  # py<3.8
                events.add(arg0.s)
            elif isinstance(arg0, ast.Name):
                events.add(arg0.id)
    return events


class CampaignPowerRehydrateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save, cls.power, cls.hs = _load_panda_free_modules()

    def setUp(self):
        # Reset baseline damage between tests (CampaignPower caches baseline).
        self.hs.COMBO_DAMAGE = (8, 12, 28)
        # Force re-baseline from current stub tuple.
        self.power._BASE_DAMAGE = None

    def test_power_bump_scales_with_reclaim_count(self):
        camp = self.camp
        power = self.power
        hs = self.hs
        base = (8, 12, 28)
        hs.COMBO_DAMAGE = base
        power._BASE_DAMAGE = None

        mult0 = power.applyPowerBump(0)
        self.assertAlmostEqual(mult0, 1.0)
        self.assertEqual(hs.COMBO_DAMAGE, base)

        mult1 = power.applyPowerBump(1)
        expected1 = 1.0 + camp.POWER_BUMP_PER_RECLAIM
        self.assertAlmostEqual(mult1, expected1)
        self.assertEqual(
            hs.COMBO_DAMAGE,
            tuple(max(1, int(round(d * expected1))) for d in base))

        # Cap at POWER_BUMP_MAX (5 reclaims * 0.08 = 0.40).
        mult_max = power.applyPowerBump(99)
        self.assertAlmostEqual(mult_max, 1.0 + camp.POWER_BUMP_MAX)
        self.assertEqual(
            hs.COMBO_DAMAGE,
            tuple(max(1, int(round(d * (1.0 + camp.POWER_BUMP_MAX))))
                  for d in base))

    def test_reset_power_bump_restores_baseline(self):
        power = self.power
        hs = self.hs
        power.applyPowerBump(3)
        self.assertNotEqual(hs.COMBO_DAMAGE, (8, 12, 28))
        power.resetPowerBump()
        self.assertEqual(hs.COMBO_DAMAGE, (8, 12, 28))

    def test_client_mirror_includes_reclaim_count(self):
        save = self.save
        camp = self.camp
        fresh = save.clientMirrorFromProgress(save.defaultProgress())
        self.assertEqual(fresh['reclaimCount'], 0)

        mid = save.clientMirrorFromProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'state': camp.STATE_ACTIVE,
            'reclaimCount': 3,
            'chaseCleared': 0,
        })
        self.assertEqual(mid['reclaimCount'], 3)

    def test_rehydrate_applies_same_bump_as_live_session(self):
        """Login reclaimCount=N must match N street-clear bumps in-session."""
        power = self.power
        hs = self.hs
        camp = self.camp

        # Simulate live session: three purity restores.
        live_mult = 1.0
        for n in (1, 2, 3):
            live_mult = power.applyPowerBump(n)
        live_damage = tuple(hs.COMBO_DAMAGE)
        expected = 1.0 + min(
            camp.POWER_BUMP_MAX, 3 * camp.POWER_BUMP_PER_RECLAIM)
        self.assertAlmostEqual(live_mult, expected)

        # Simulate relog: reset config, rehydrate from persisted reclaimCount.
        hs.COMBO_DAMAGE = (8, 12, 28)
        power._BASE_DAMAGE = None
        re_mult = power.applyPowerBump(3)
        self.assertAlmostEqual(re_mult, live_mult)
        self.assertEqual(hs.COMBO_DAMAGE, live_damage)

    def test_dc_declares_reclaim_count_on_progress(self):
        dc = _read('etc/toon.dc')
        pollution_block = dc.split('dclass PollutionManager')[1].split(
            'dclass ')[0]
        self.assertIn(
            'setCampaignProgress(uint8, uint8, uint8, uint8)', pollution_block)
        self.assertIn('reclaimCount', pollution_block)

    def test_pollution_manager_pushes_reclaim_count(self):
        ai_src = _read('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('reclaimCount', ai_src)
        push_idx = ai_src.find('def pushCampaignProgressToAvatar')
        self.assertGreater(push_idx, 0)
        push_win = ai_src[push_idx:push_idx + 2200]
        self.assertIn("blob.get('reclaimCount'", push_win)
        self.assertIn('setCampaignProgress', push_win)
        # Four-arg send: unlocked, state, chaseCleared, reclaimCount.
        self.assertIn(
            '[unlocked, state, chaseCleared, reclaimCount]', push_win)

        client_src = _read('toontown/corruption/PollutionManager.py')
        self.assertIn('campaignReclaimCount', client_src)
        tree = _module_ast('toontown/corruption/PollutionManager.py')
        methods = _class_method_names(tree, 'PollutionManager')
        self.assertIn('setCampaignProgress', methods)
        set_idx = client_src.find('def setCampaignProgress')
        set_win = client_src[set_idx:set_idx + 900]
        self.assertIn('reclaimCount', set_win)
        self.assertIn('campaignReclaimCount', set_win)

    def test_handoff_accepts_sync_and_applies_power(self):
        rel = 'toontown/campaign/CampaignHandoff.py'
        src = _read(rel)
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'CampaignHandoffClient')
        self.assertIn('_onCampaignProgressSync', methods)
        self.assertIn('_onPurityRestore', methods)

        accepts = _accept_events(tree, 'CampaignHandoffClient')
        # syncMsg variable OR literal — either means the accept is wired.
        self.assertTrue(
            'syncMsg' in accepts or 'campaignProgressSync' in accepts,
            msg='CampaignHandoffClient must accept campaign progress sync')

        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', src)
        self.assertIn('applyPowerBump', src)
        sync_idx = src.find('def _onCampaignProgressSync')
        self.assertGreater(sync_idx, 0)
        sync_win = src[sync_idx:sync_idx + 500]
        self.assertIn('reclaimCount', sync_win)
        self.assertIn('_localReclaimCount', sync_win)
        self.assertIn('applyPowerBump', sync_win)
        # Silent rehydrate — no celebration plate on login sync.
        self.assertNotIn('_celebrate', sync_win)

        # Live reclaim path still bumps from _localReclaimCount.
        purity_idx = src.find('def _onPurityRestore')
        purity_win = src[purity_idx:purity_idx + 400]
        self.assertIn('_localReclaimCount += 1', purity_win)
        self.assertIn('applyPowerBump(self._localReclaimCount)', purity_win)

    def test_globals_document_reclaim_on_sync(self):
        src = _read('toontown/campaign/CampaignGlobals.py')
        # Comment near CAMPAIGN_PROGRESS_SYNC_MSG mentions reclaimCount.
        idx = src.find('CAMPAIGN_PROGRESS_SYNC_MSG')
        self.assertGreater(idx, 0)
        window = src[max(0, idx - 400):idx + 80]
        self.assertIn('reclaimCount', window)
        self.assertIn('POWER_BUMP', window)

    def test_no_kh_copy_in_touched_modules(self):
        # Affirmative KH product copy only — docs may say "no keyblades".
        for rel in (
                'toontown/campaign/CampaignPower.py',
                'toontown/campaign/CampaignProgressSave.py',
                'toontown/corruption/PollutionManager.py',
                'toontown/corruption/PollutionManagerAI.py'):
            blob = _read(rel).lower()
            for banned in ('kingdom hearts', 'sora'):
                self.assertNotIn(
                    banned, blob, msg='%s contains %r' % (rel, banned))
            for token in ('keyblade', 'key blade'):
                if token not in blob:
                    continue
                if ('no %s' % token) in blob or ('no %ss' % token) in blob:
                    continue
                if ('without %s' % token) in blob:
                    continue
                self.fail('%s contains affirmative %r' % (rel, token))


if __name__ == '__main__':
    unittest.main()
