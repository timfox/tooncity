#!/usr/bin/env python3
"""Headless tests: sync campaign progress to client on login.

Loads CampaignGlobals / CampaignProgressSave with a ToontownGlobals stub —
no Panda3D. Asserts clientMirror flags (victory / unlock / chase), thin
PollutionManager DC + AI push wiring, and PlayEntry / OswaldPresence accept
of campaignProgressSync so hub tip + trusted presence match after relog.

Run from repo root:
  python3 tests/test_campaign_progress_client_sync.py
  python3 -m unittest tests.test_campaign_progress_client_sync -v
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
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim', 'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = TTC
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

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
    return camp, save, cg


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _module_names(rel: str) -> set[str]:
    tree = _module_ast(rel)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


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
    """Collect string event names passed to self.accept in a class."""
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
    return events


class CampaignProgressClientSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save, cls.cfg = _load_panda_free_modules()

    def test_client_mirror_fresh_campaign(self):
        save = self.save
        camp = self.camp
        mirror = save.clientMirrorFromProgress(save.defaultProgress())
        self.assertFalse(mirror['victoryEpilogue'])
        self.assertFalse(mirror['betrayed'])
        self.assertFalse(mirror['chasePending'])
        self.assertEqual(mirror['unlockedThrough'], 0)
        self.assertEqual(mirror['state'], camp.STATE_IDLE)
        self.assertIsNone(mirror['softNextStreet'])

    def test_client_mirror_mid_act_unlock(self):
        save = self.save
        camp = self.camp
        mirror = save.clientMirrorFromProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'state': camp.STATE_ACTIVE,
            'chaseCleared': 0,
        })
        self.assertFalse(mirror['victoryEpilogue'])
        self.assertFalse(mirror['betrayed'])
        self.assertEqual(mirror['softNextStreet'], camp.ACTS[1]['name'])
        self.assertIn('Punchline', mirror['softNextStreet'])

    def test_client_mirror_victory_chase_pending(self):
        save = self.save
        camp = self.camp
        mirror = save.clientMirrorFromProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
            'chaseCleared': 0,
        })
        self.assertTrue(mirror['victoryEpilogue'])
        self.assertTrue(mirror['betrayed'])
        self.assertTrue(mirror['chasePending'])
        self.assertIsNone(mirror['softNextStreet'])
        # Hub tip branch for victory.
        tip = camp.hubPlayEntryTip(victory=mirror['victoryEpilogue'])
        self.assertIn('Campaign complete', tip)

    def test_client_mirror_victory_chase_cleared(self):
        save = self.save
        camp = self.camp
        mirror = save.clientMirrorFromProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
            'chaseCleared': 1,
        })
        self.assertTrue(mirror['victoryEpilogue'])
        self.assertTrue(mirror['betrayed'])
        self.assertFalse(mirror['chasePending'])
        self.assertEqual(mirror['chaseCleared'], 1)

    def test_soft_next_street_helper(self):
        save = self.save
        camp = self.camp
        self.assertIsNone(save.softNextStreetFromProgress({
            'unlockedThrough': 0, 'state': camp.STATE_IDLE}))
        self.assertEqual(
            save.softNextStreetFromProgress({
                'unlockedThrough': 2, 'actIndex': 2,
                'state': camp.STATE_ACTIVE}),
            camp.ACTS[2]['name'])
        self.assertIsNone(save.softNextStreetFromProgress({
            'unlockedThrough': 2, 'state': camp.STATE_VICTORY}))

    def test_globals_sync_msg(self):
        self.assertEqual(
            self.camp.CAMPAIGN_PROGRESS_SYNC_MSG, 'campaignProgressSync')

    def test_dc_declares_campaign_progress(self):
        dc = _read('etc/toon.dc')
        self.assertIn('requestCampaignProgress', dc)
        self.assertIn('setCampaignProgress', dc)
        # Still no DistributedToon campaign field — thin PollutionManager only.
        self.assertIn('dclass PollutionManager', dc)
        pollution_block = dc.split('dclass PollutionManager')[1].split(
            'dclass ')[0]
        self.assertIn('setCampaignProgress(uint8, uint8, uint8)', pollution_block)

    def test_pollution_manager_client_surface(self):
        rel = 'toontown/corruption/PollutionManager.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'PollutionManager')
        self.assertIn('d_requestCampaignProgress', methods)
        self.assertIn('setCampaignProgress', methods)
        src = _read(rel)
        self.assertIn('campaignProgressSync', src)
        self.assertIn('campaignUnlockedThrough', src)
        self.assertIn('campaignChaseCleared', src)

    def test_pollution_manager_ai_push(self):
        rel = 'toontown/corruption/PollutionManagerAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'PollutionManagerAI')
        self.assertIn('requestCampaignProgress', methods)
        self.assertIn('pushCampaignProgressToAvatar', methods)
        src = _read(rel)
        self.assertIn('setCampaignProgress', src)
        self.assertIn('_hydrateFromToon', src)
        self.assertIn('sendUpdateToAvatarId', src)

    def test_director_pushes_on_hydrate_and_persist(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('_pushProgressToClient', src)
        hydrate_idx = src.find('def _hydrateFromToon')
        hydrate_win = src[hydrate_idx:hydrate_idx + 1800]
        self.assertIn('_pushProgressToClient', hydrate_win)
        persist_idx = src.find('def _persistForAvatarId')
        persist_win = src[persist_idx:persist_idx + 1200]
        self.assertIn('_pushProgressToClient', persist_win)

    def test_playentry_accepts_and_requests_sync(self):
        rel = 'toontown/campaign/PlayEntry.py'
        src = _read(rel)
        self.assertIn('_onCampaignProgressSync', src)
        self.assertIn('_bootCampaignProgress', src)
        self.assertIn('d_requestCampaignProgress', src)
        self.assertIn('clientMirrorFromProgress', src)
        self.assertIn('_victoryEpilogue', src)
        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', src)
        # Preserve #332 hub breadcrumb unlock accept alongside login sync.
        self.assertIn("accept('campaignActUnlocked'", src)
        self.assertIn('_onCampaignActUnlocked', src)
        self.assertIn('CorruptStreetBreadcrumb', src)

    def test_oswald_presence_accepts_sync(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        src = _read(rel)
        self.assertIn('_onCampaignProgressSync', src)
        self.assertIn('clientMirrorFromProgress', src)
        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', src)
        self.assertIn('_betrayed', src)
        # Presence still hides on live betrayal messengers.
        self.assertIn("accept('campaignVictory'", src)
        self.assertIn("accept('oswaldBetrayalChase'", src)

    def test_no_kh_copy_in_touched_modules(self):
        # Affirmative KH product copy only — docs may say "no keyblades".
        for rel in (
                'toontown/campaign/CampaignProgressSave.py',
                'toontown/campaign/PlayEntry.py',
                'toontown/campaign/OswaldPresence.py',
                'toontown/corruption/PollutionManager.py',
                'toontown/corruption/PollutionManagerAI.py'):
            blob = _read(rel).lower()
            for banned in ('kingdom hearts', 'sora'):
                self.assertNotIn(
                    banned, blob, msg='%s contains %r' % (rel, banned))
            # Ban standalone product use of "keyblade" outside negation.
            for token in ('keyblade', 'key blade'):
                if token not in blob:
                    continue
                # Allow "no keyblade(s)" / "without keyblade" guardrails.
                if ('no %s' % token) in blob or ('no %ss' % token) in blob:
                    continue
                if ('without %s' % token) in blob:
                    continue
                self.fail('%s contains affirmative %r' % (rel, token))


if __name__ == '__main__':
    unittest.main()
