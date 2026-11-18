#!/usr/bin/env python3
"""Headless tests: wire oswaldPresenceMet → first-meet tip + oswaldMet persist.

Loads CampaignGlobals + CampaignProgressSave with a ToontownGlobals stub —
no Panda3D. Exercises sanitize / mirror / JSON round-trip for oswaldMet and
AST-locks OswaldPresence accept + PollutionManager DC / AI push wiring.

Run from repo root:
  python3 tests/test_oswald_presence_met.py
  python3 -m unittest tests.test_oswald_presence_met -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
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


def _load_panda_free_campaign_progress():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = TTC
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

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
    return camp, save


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


class OswaldPresenceMetTests(unittest.TestCase):
    """First-meet tip + durable oswaldMet persist (trust beat)."""

    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save = _load_panda_free_campaign_progress()

    def test_first_meet_tip_tunable(self):
        camp = self.camp
        tip = camp.OSWALD_PRESENCE_FIRST_MEET_TIP
        self.assertIn('Oswald', tip)
        self.assertIn('met', tip.lower())
        self.assertIn('reclaim', tip.lower())
        self.assertEqual(camp.OSWALD_PRESENCE_MET_MSG, 'oswaldPresenceMet')
        self.assertEqual(camp.OSWALD_PRESENCE_MET_SYNC_MSG, 'oswaldMetSync')
        blob = tip.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, blob)

    def test_default_progress_includes_oswald_met(self):
        save = self.save
        fresh = save.defaultProgress()
        self.assertIn('oswaldMet', fresh)
        self.assertEqual(fresh['oswaldMet'], 0)

    def test_sanitize_clamps_oswald_met(self):
        save = self.save
        self.assertEqual(save.sanitizeProgress({'oswaldMet': 9})['oswaldMet'], 1)
        self.assertEqual(save.sanitizeProgress({'oswaldMet': -1})['oswaldMet'], 0)
        self.assertEqual(
            save.sanitizeProgress({'oswaldMet': '1'})['oswaldMet'], 1)
        self.assertEqual(
            save.sanitizeProgress({})['oswaldMet'], 0)

    def test_client_mirror_exposes_oswald_met(self):
        save = self.save
        camp = self.camp
        mirror = save.clientMirrorFromProgress({
            'unlockedThrough': 0,
            'state': camp.STATE_IDLE,
            'oswaldMet': 1,
        })
        self.assertEqual(mirror['oswaldMet'], 1)
        fresh = save.clientMirrorFromProgress({
            'unlockedThrough': 0,
            'state': camp.STATE_IDLE,
        })
        self.assertEqual(fresh['oswaldMet'], 0)

    def test_json_round_trip_keeps_oswald_met(self):
        save = self.save
        with tempfile.TemporaryDirectory() as tmp:
            path = save.progressPath(tmp, shard=7)
            av_id = 4242
            progress = save.sanitizeProgress({
                'unlockedThrough': 1,
                'actIndex': 1,
                'state': self.camp.STATE_ACTIVE,
                'oswaldMet': 1,
            })
            self.assertTrue(save.writeAvatar(path, av_id, progress))
            loaded = save.readAvatar(path, av_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded['oswaldMet'], 1)
            self.assertEqual(loaded['unlockedThrough'], 1)

    def test_snapshot_apply_director_oswald_met(self):
        save = self.save
        director = types.SimpleNamespace(
            unlockedThrough=0,
            actIndex=0,
            reclaimCount=0,
            state=self.camp.STATE_IDLE,
            _finalePhase=0,
            chaseCleared=0,
            chaseHp=0,
            oswaldMet=1,
        )
        blob = save.snapshotFromDirector(director)
        self.assertEqual(blob['oswaldMet'], 1)
        target = types.SimpleNamespace()
        save.applyProgressToDirector(target, {
            'unlockedThrough': 0,
            'oswaldMet': 1,
        })
        self.assertEqual(target.oswaldMet, 1)

    def test_presence_accepts_met_and_shows_first_meet(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        names = _module_names(rel)
        for required in (
                'firstMeetTip', 'metMsgName', 'metSyncMsgName'):
            self.assertIn(required, names)
        methods = _class_method_names(
            _module_ast(rel), 'OswaldPresenceClient')
        for required in (
                '_onOswaldPresenceMet',
                '_onOswaldMetSync',
                '_requestPersistMet',
                '_meetOswald'):
            self.assertIn(required, methods)
        src = _read(rel)
        self.assertIn("accept(metMsgName()", src)
        self.assertIn("accept(metSyncMsgName()", src)
        self.assertIn('_oswaldMet', src)
        self.assertIn('firstMeetTip()', src)
        self.assertIn('d_requestOswaldMet', src)
        self.assertIn('OSWALD_PRESENCE_FIRST_MEET_TIP', src)
        # Orphan send is now accepted (not send-only).
        self.assertIn('oswaldPresenceMet', src)
        self.assertIn('oswaldMetSync', src)
        # Preserve plaza cheer / victory hide.
        self.assertIn('playReclaimCheer', src)
        self.assertIn('clientMirrorFromProgress', src)
        src_l = src.lower()
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('sora', src_l)
        self.assertNotIn('cream_wash', src_l)

    def test_dc_declares_oswald_met_sibling(self):
        dc = _read('etc/toon.dc')
        pollution_block = dc.split('dclass PollutionManager')[1].split(
            'dclass ')[0]
        # Keep 4-arg progress DC (breadcrumb / power sync untouched).
        self.assertIn(
            'setCampaignProgress(uint8, uint8, uint8, uint8)', pollution_block)
        self.assertIn('requestOswaldMet() airecv clsend', pollution_block)
        self.assertIn('setOswaldMet(uint8)', pollution_block)

    def test_pollution_manager_client_oswald_met(self):
        rel = 'toontown/corruption/PollutionManager.py'
        methods = _class_method_names(
            _module_ast(rel), 'PollutionManager')
        self.assertIn('d_requestOswaldMet', methods)
        self.assertIn('setOswaldMet', methods)
        src = _read(rel)
        self.assertIn('campaignOswaldMet', src)
        self.assertIn('oswaldMetSync', src)
        self.assertIn('OSWALD_PRESENCE_MET_SYNC_MSG', src)

    def test_pollution_manager_ai_oswald_met(self):
        rel = 'toontown/corruption/PollutionManagerAI.py'
        methods = _class_method_names(
            _module_ast(rel), 'PollutionManagerAI')
        self.assertIn('requestOswaldMet', methods)
        self.assertIn('pushOswaldMetToAvatar', methods)
        src = _read(rel)
        self.assertIn('markOswaldMet', src)
        self.assertIn("setOswaldMet", src)
        self.assertIn('oswaldMet', src)

    def test_director_mark_oswald_met(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('def markOswaldMet', src)
        self.assertIn('def _pushOswaldMetToClient', src)
        self.assertIn('self.oswaldMet = 0', src)
        self.assertIn('self.oswaldMet = 1', src)
        # Replay wipe must NOT clear oswaldMet (durable trust beat).
        start_idx = src.find('def startCampaign')
        start_win = src[start_idx:start_idx + 2200]
        wipe_at = start_win.find('self.chaseCleared = 0')
        self.assertGreater(wipe_at, 0)
        wipe_win = start_win[wipe_at:wipe_at + 400]
        self.assertNotIn('self.oswaldMet = 0', wipe_win)
        # Progress push also mirrors met latch.
        push_idx = src.find('def _pushProgressToClient')
        push_win = src[push_idx:push_idx + 900]
        self.assertIn('_pushOswaldMetToClient', push_win)

    def test_playentry_breadcrumb_sync_preserved(self):
        # #357 breadcrumb unlock from campaignProgressSync must remain.
        src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('_onCampaignProgressSync', src)
        self.assertIn('noteCampaignActUnlocked', src)
        sync_idx = src.find('def _onCampaignProgressSync')
        sync_win = src[sync_idx:sync_idx + 1800]
        self.assertIn('noteCampaignActUnlocked(unlocked)', sync_win)
        # This PR intentionally avoids PlayEntry breadcrumb edits.
        self.assertNotIn('oswaldPresenceMet', src)
        self.assertNotIn('oswaldMet', src)

    def test_progress_save_doc_mentions_oswald_met(self):
        src = _read('toontown/campaign/CampaignProgressSave.py')
        self.assertIn("'oswaldMet'", src)
        self.assertIn('oswaldMet', src)


if __name__ == '__main__':
    unittest.main()
