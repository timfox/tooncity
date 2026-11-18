#!/usr/bin/env python3
"""Headless tests: wire oswaldPresenceCheered → oswaldCheered persist.

Loads CampaignGlobals + CampaignProgressSave with a ToontownGlobals stub —
no Panda3D. Exercises sanitize / mirror / JSON round-trip for oswaldCheered
(keeping securedZones intact) and AST-locks OswaldPresence accept +
PollutionManager DC / AI push wiring.

Run from repo root:
  python3 tests/test_oswald_presence_cheered.py
  python3 -m unittest tests.test_oswald_presence_cheered -v
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


class OswaldPresenceCheeredTests(unittest.TestCase):
    """Reclaim cheer tip + durable oswaldCheered persist (trust beat)."""

    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save = _load_panda_free_campaign_progress()

    def test_cheer_tip_and_cheered_msg_tunable(self):
        camp = self.camp
        tip = camp.OSWALD_PRESENCE_CHEER_TIP
        self.assertIn('Oswald', tip)
        self.assertIn('clean', tip.lower())
        self.assertEqual(camp.OSWALD_PRESENCE_CHEER_MSG, 'oswaldPresenceCheer')
        self.assertEqual(
            camp.OSWALD_PRESENCE_CHEERED_MSG, 'oswaldPresenceCheered')
        self.assertEqual(
            camp.OSWALD_PRESENCE_CHEERED_SYNC_MSG, 'oswaldCheeredSync')
        blob = tip.lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, blob)

    def test_default_progress_includes_oswald_cheered(self):
        save = self.save
        fresh = save.defaultProgress()
        self.assertIn('oswaldCheered', fresh)
        self.assertEqual(fresh['oswaldCheered'], 0)
        # #368 securedZones must remain on the blob.
        self.assertIn('securedZones', fresh)
        self.assertEqual(fresh['securedZones'], [])
        self.assertIn('oswaldMet', fresh)

    def test_sanitize_clamps_oswald_cheered(self):
        save = self.save
        self.assertEqual(
            save.sanitizeProgress({'oswaldCheered': 9})['oswaldCheered'], 1)
        self.assertEqual(
            save.sanitizeProgress({'oswaldCheered': -1})['oswaldCheered'], 0)
        self.assertEqual(
            save.sanitizeProgress({'oswaldCheered': '1'})['oswaldCheered'], 1)
        self.assertEqual(
            save.sanitizeProgress({})['oswaldCheered'], 0)

    def test_sanitize_keeps_secured_zones_with_cheered(self):
        save = self.save
        blob = save.sanitizeProgress({
            'oswaldCheered': 1,
            'oswaldMet': 1,
            'securedZones': [PUNCHLINE, LOOPY, LOOPY, -1, 0],
        })
        self.assertEqual(blob['oswaldCheered'], 1)
        self.assertEqual(blob['oswaldMet'], 1)
        self.assertEqual(blob['securedZones'], [LOOPY, PUNCHLINE])

    def test_client_mirror_exposes_oswald_cheered(self):
        save = self.save
        camp = self.camp
        mirror = save.clientMirrorFromProgress({
            'unlockedThrough': 0,
            'state': camp.STATE_IDLE,
            'oswaldCheered': 1,
            'securedZones': [LOOPY],
        })
        self.assertEqual(mirror['oswaldCheered'], 1)
        self.assertEqual(mirror['securedZones'], [LOOPY])
        fresh = save.clientMirrorFromProgress({
            'unlockedThrough': 0,
            'state': camp.STATE_IDLE,
        })
        self.assertEqual(fresh['oswaldCheered'], 0)

    def test_json_round_trip_keeps_oswald_cheered_and_secured(self):
        save = self.save
        with tempfile.TemporaryDirectory() as tmp:
            path = save.progressPath(tmp, shard=7)
            av_id = 5151
            progress = save.sanitizeProgress({
                'unlockedThrough': 1,
                'actIndex': 1,
                'state': self.camp.STATE_ACTIVE,
                'oswaldMet': 1,
                'oswaldCheered': 1,
                'securedZones': [LOOPY],
            })
            self.assertTrue(save.writeAvatar(path, av_id, progress))
            loaded = save.readAvatar(path, av_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded['oswaldCheered'], 1)
            self.assertEqual(loaded['oswaldMet'], 1)
            self.assertEqual(loaded['securedZones'], [LOOPY])
            self.assertEqual(loaded['unlockedThrough'], 1)

    def test_snapshot_apply_director_oswald_cheered(self):
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
            oswaldCheered=1,
            securedZones=[LOOPY],
        )
        blob = save.snapshotFromDirector(director)
        self.assertEqual(blob['oswaldCheered'], 1)
        self.assertEqual(blob['securedZones'], [LOOPY])
        target = types.SimpleNamespace()
        save.applyProgressToDirector(target, {
            'unlockedThrough': 0,
            'oswaldCheered': 1,
            'securedZones': [PUNCHLINE],
        })
        self.assertEqual(target.oswaldCheered, 1)
        self.assertEqual(target.securedZones, [PUNCHLINE])

    def test_presence_accepts_cheered_and_persists(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        names = _module_names(rel)
        for required in (
                'cheerTip', 'cheeredMsgName', 'cheeredSyncMsgName'):
            self.assertIn(required, names)
        methods = _class_method_names(
            _module_ast(rel), 'OswaldPresenceClient')
        for required in (
                '_onOswaldPresenceCheered',
                '_onOswaldCheeredSync',
                '_requestPersistCheered',
                'playReclaimCheer'):
            self.assertIn(required, methods)
        src = _read(rel)
        self.assertIn("accept(cheeredMsgName()", src)
        self.assertIn("accept(cheeredSyncMsgName()", src)
        self.assertIn('_oswaldCheered', src)
        self.assertIn('cheerTip()', src)
        self.assertIn('d_requestOswaldCheered', src)
        self.assertIn('cheeredMsgName()', src)
        # Orphan send is now accepted (not send-only).
        self.assertIn('oswaldPresenceCheered', src)
        self.assertIn('oswaldCheeredSync', src)
        # Preserve plaza meet / victory hide / cheer body.
        self.assertIn('playReclaimCheer', src)
        self.assertIn('_onOswaldPresenceMet', src)
        self.assertIn('clientMirrorFromProgress', src)
        src_l = src.lower()
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('sora', src_l)
        self.assertNotIn('cream_wash', src_l)

    def test_dc_declares_oswald_cheered_sibling(self):
        dc = _read('etc/toon.dc')
        pollution_block = dc.split('dclass PollutionManager')[1].split(
            'dclass ')[0]
        # Keep 4-arg progress DC (breadcrumb / power sync untouched).
        self.assertIn(
            'setCampaignProgress(uint8, uint8, uint8, uint8)', pollution_block)
        self.assertIn('requestOswaldMet() airecv clsend', pollution_block)
        self.assertIn('setOswaldMet(uint8)', pollution_block)
        self.assertIn(
            'requestOswaldCheered() airecv clsend', pollution_block)
        self.assertIn('setOswaldCheered(uint8)', pollution_block)

    def test_pollution_manager_client_oswald_cheered(self):
        rel = 'toontown/corruption/PollutionManager.py'
        methods = _class_method_names(
            _module_ast(rel), 'PollutionManager')
        self.assertIn('d_requestOswaldCheered', methods)
        self.assertIn('setOswaldCheered', methods)
        src = _read(rel)
        self.assertIn('campaignOswaldCheered', src)
        self.assertIn('oswaldCheeredSync', src)
        self.assertIn('OSWALD_PRESENCE_CHEERED_SYNC_MSG', src)

    def test_pollution_manager_ai_oswald_cheered(self):
        rel = 'toontown/corruption/PollutionManagerAI.py'
        methods = _class_method_names(
            _module_ast(rel), 'PollutionManagerAI')
        self.assertIn('requestOswaldCheered', methods)
        self.assertIn('pushOswaldCheeredToAvatar', methods)
        src = _read(rel)
        self.assertIn('markOswaldCheered', src)
        self.assertIn("setOswaldCheered", src)
        self.assertIn('oswaldCheered', src)

    def test_director_mark_oswald_cheered(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('def markOswaldCheered', src)
        self.assertIn('def _pushOswaldCheeredToClient', src)
        self.assertIn('self.oswaldCheered = 0', src)
        self.assertIn('self.oswaldCheered = 1', src)
        # Replay wipe must NOT clear oswaldCheered (durable trust beat).
        start_idx = src.find('def startCampaign')
        start_win = src[start_idx:start_idx + 2200]
        wipe_at = start_win.find('self.chaseCleared = 0')
        self.assertGreater(wipe_at, 0)
        wipe_win = start_win[wipe_at:wipe_at + 500]
        self.assertNotIn('self.oswaldCheered = 0', wipe_win)
        # securedZones still wipe on replay (#368) — leave that intact.
        self.assertIn('self.securedZones = []', wipe_win)
        # Progress push also mirrors cheer latch.
        push_idx = src.find('def _pushProgressToClient')
        push_win = src[push_idx:push_idx + 1100]
        self.assertIn('_pushOswaldCheeredToClient', push_win)

    def test_playentry_breadcrumb_sync_preserved(self):
        # #357 breadcrumb unlock from campaignProgressSync must remain.
        src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('_onCampaignProgressSync', src)
        self.assertIn('noteCampaignActUnlocked', src)
        sync_idx = src.find('def _onCampaignProgressSync')
        sync_win = src[sync_idx:sync_idx + 1800]
        self.assertIn('noteCampaignActUnlocked(unlocked)', sync_win)
        # This PR intentionally avoids PlayEntry breadcrumb edits.
        self.assertNotIn('oswaldPresenceCheered', src)
        self.assertNotIn('oswaldCheered', src)

    def test_progress_save_doc_mentions_oswald_cheered(self):
        src = _read('toontown/campaign/CampaignProgressSave.py')
        self.assertIn("'oswaldCheered'", src)
        self.assertIn('oswaldCheered', src)
        # #368 securedZones stay present.
        self.assertIn("'securedZones'", src)
        self.assertIn('securedZones', src)


if __name__ == '__main__':
    unittest.main()
