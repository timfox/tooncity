#!/usr/bin/env python3
"""Headless tests: relay campaignVictory to client on finale reclaim.

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D. Asserts
thin PollutionManager DC announceCampaignVictory, AI push wiring, director
_pushVictoryToClient on both victory branches, and client acceptors so
PlayEntry / OswaldPresence / chase / FinalePhaseFx / Handoff hear the live
event (not AI-local messenger only).

Run from repo root:
  python3 tests/test_campaign_victory_client_relay.py
  python3 -m unittest tests.test_campaign_victory_client_relay -v
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
    return camp, cg


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
    """Collect string event names passed to self.accept in a class."""
    events = set()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for child in ast.walk(item):
                if not isinstance(child, ast.Call):
                    continue
                func = child.func
                if isinstance(func, ast.Attribute) and func.attr == 'accept':
                    if child.args and isinstance(child.args[0], ast.Constant):
                        if isinstance(child.args[0].value, str):
                            events.add(child.args[0].value)
                elif isinstance(func, ast.Attribute) and func.attr == 'accept':
                    if child.args and isinstance(child.args[0], ast.Str):
                        events.add(child.args[0].s)
    return events


class CampaignVictoryClientRelayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.cg = _load_panda_free_modules()

    def test_globals_victory_msg(self):
        self.assertEqual(self.camp.CAMPAIGN_VICTORY_MSG, 'campaignVictory')

    def test_dc_declares_announce_campaign_victory(self):
        dc = _read('etc/toon.dc')
        self.assertIn('announceCampaignVictory', dc)
        pollution_block = dc.split('dclass PollutionManager')[1].split(
            'dclass ')[0]
        self.assertIn('announceCampaignVictory(uint8)', pollution_block)
        # Still thin PollutionManager — no DistributedToon campaign field.
        self.assertIn('dclass PollutionManager', dc)

    def test_pollution_manager_client_announce(self):
        rel = 'toontown/corruption/PollutionManager.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'PollutionManager')
        self.assertIn('announceCampaignVictory', methods)
        src = _read(rel)
        self.assertIn('CAMPAIGN_VICTORY_MSG', src)
        self.assertIn('campaignVictory', src)
        self.assertIn('messenger.send', src)

    def test_pollution_manager_ai_push(self):
        rel = 'toontown/corruption/PollutionManagerAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'PollutionManagerAI')
        self.assertIn('pushCampaignVictoryToAvatar', methods)
        src = _read(rel)
        self.assertIn('announceCampaignVictory', src)
        self.assertIn('sendUpdateToAvatarId', src)
        # Distinct from login progress mirror.
        self.assertIn('pushCampaignProgressToAvatar', methods)

    def test_director_pushes_victory_on_finale_reclaim(self):
        rel = 'toontown/campaign/CampaignDirectorAI.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'CampaignDirectorAI')
        self.assertIn('_pushVictoryToClient', methods)
        src = _read(rel)
        marker = "messenger.send('campaignVictory'"
        first = src.find(marker)
        self.assertGreater(first, 0)
        # Both victory branches (finale act + exhausted ACTS) push to client.
        second = src.find(marker, first + len(marker))
        self.assertGreater(second, first)
        for idx in (first, second):
            window = src[idx:idx + 280]
            self.assertIn('_pushVictoryToClient', window)

    def test_client_acceptors_keep_campaign_victory(self):
        acceptors = (
            ('toontown/campaign/PlayEntry.py', 'PlayEntryClient'),
            ('toontown/campaign/OswaldPresence.py', 'OswaldPresenceClient'),
            ('toontown/campaign/OswaldBetrayalChase.py',
             'OswaldBetrayalChaseClient'),
            ('toontown/campaign/FinalePhaseFx.py', 'FinalePhaseFxClient'),
            ('toontown/campaign/CampaignHandoff.py', 'CampaignHandoffClient'),
        )
        for rel, class_name in acceptors:
            tree = _module_ast(rel)
            events = _accept_events(tree, class_name)
            self.assertIn(
                'campaignVictory', events,
                msg='%s.%s must accept campaignVictory' % (rel, class_name))

    def test_chase_comment_notes_relay(self):
        src = _read('toontown/campaign/OswaldBetrayalChase.py')
        self.assertIn('announceCampaignVictory', src)
        # Still accepts reveal as backup when victory path is delayed.
        self.assertIn('oswaldRevealBanner', src)

    def test_no_kh_copy_in_touched_modules(self):
        for rel in (
                'toontown/campaign/CampaignDirectorAI.py',
                'toontown/campaign/CampaignGlobals.py',
                'toontown/campaign/OswaldBetrayalChase.py',
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
