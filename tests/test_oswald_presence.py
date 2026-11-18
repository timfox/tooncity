#!/usr/bin/env python3
"""Headless/AST tests: Oswald plaza NPC deepen + reclaim cheer (trust lead).

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D.
OswaldPresence helpers are mirrored from CampaignGlobals (module imports
panda); client wiring is AST-checked. Beyond the CardMaker spawn-near-
avatar stub: authored plaza stand, idle bob, reclaim cheer on
npcCheerStub / ReclaimCheer nudge; preserves #333 persisted-victory hide.

Run from repo root:
  python3 tests/test_oswald_presence.py
  python3 -m unittest tests.test_oswald_presence -v
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


def _load_panda_free_globals():
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
    sys.modules['toontown.corruption'].CorruptionGlobals = cg

    rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
    rg_spec = importlib.util.spec_from_file_location(
        'toontown.reclaim.ReclaimGlobals', rg_path)
    rg = importlib.util.module_from_spec(rg_spec)
    assert rg_spec.loader is not None
    sys.modules['toontown.reclaim.ReclaimGlobals'] = rg
    rg_spec.loader.exec_module(rg)

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    return camp, rg, cg


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_names(rel: str) -> set[str]:
    tree = ast.parse(_read(rel))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _class_methods(rel: str, class_name: str) -> set[str]:
    tree = ast.parse(_read(rel))
    methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(child.name)
    return methods


def _mirror_should_show(camp, zoneId, betrayed=False):
    """Mirror OswaldPresence.shouldShowPresence without importing panda."""
    if not bool(getattr(camp, 'OSWALD_PRESENCE_ENABLED', True)):
        return False
    if betrayed and bool(getattr(camp, 'OSWALD_PRESENCE_HIDE_ON_BETRAYAL', True)):
        return False
    zones = {int(camp.HUB_ZONE)}
    for act in camp.ACTS:
        zones.add(int(act['zoneId']))
    return int(zoneId) in zones


def _mirror_greet(camp, zoneId, cheered=False, softNextStreet=None):
    helper = getattr(camp, 'oswaldPresenceGreetTip', None)
    if callable(helper):
        return str(helper(
            zoneId, cheered=cheered, softNextStreet=softNextStreet))
    if int(zoneId) == int(camp.HUB_ZONE):
        return str(camp.OSWALD_PRESENCE_HUB_GREET)
    return str(camp.OSWALD_PRESENCE_STREET_GREET)


class OswaldPresenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.rg, cls.cfg = _load_panda_free_globals()

    def test_presence_tunables(self):
        camp = self.camp
        self.assertTrue(camp.OSWALD_PRESENCE_ENABLED)
        self.assertEqual(camp.OSWALD_PRESENCE_LABEL, camp.PROTAGONIST)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_HUB_GREET)
        self.assertIn('Loopy', camp.OSWALD_PRESENCE_HUB_GREET)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_STREET_GREET)
        self.assertIn('fight', camp.OSWALD_PRESENCE_STREET_GREET.lower())
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_FIRST_MEET_TIP)
        self.assertIn('met', camp.OSWALD_PRESENCE_FIRST_MEET_TIP.lower())
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_CHEER_TIP)
        self.assertIn('clean', camp.OSWALD_PRESENCE_CHEER_TIP.lower())
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_INTERACT_PROMPT)
        self.assertIn('Talk', camp.OSWALD_PRESENCE_INTERACT_PROMPT)
        self.assertGreater(float(camp.OSWALD_PRESENCE_INTERACT_RADIUS), 2.0)
        self.assertGreater(float(camp.OSWALD_PRESENCE_SPAWN_FORWARD), 0.0)
        self.assertGreater(float(camp.OSWALD_PRESENCE_BODY_SCALE), 0.0)
        self.assertTrue(camp.OSWALD_PRESENCE_HIDE_ON_BETRAYAL)
        self.assertTrue(camp.OSWALD_PRESENCE_CHEER_ON_RECLAIM)
        self.assertTrue(camp.OSWALD_PRESENCE_IDLE_BOB)
        hub_pos = camp.OSWALD_PRESENCE_HUB_POS
        self.assertEqual(len(hub_pos), 4)
        self.assertTrue(all(isinstance(v, (int, float)) for v in hub_pos))
        self.assertEqual(camp.OSWALD_PRESENCE_CHEER_MSG, 'oswaldPresenceCheer')
        self.assertEqual(
            camp.OSWALD_PRESENCE_CHEERED_MSG, 'oswaldPresenceCheered')
        self.assertEqual(
            camp.OSWALD_PRESENCE_CHEERED_SYNC_MSG, 'oswaldCheeredSync')
        self.assertEqual(camp.OSWALD_PRESENCE_MET_MSG, 'oswaldPresenceMet')
        self.assertEqual(camp.OSWALD_PRESENCE_MET_SYNC_MSG, 'oswaldMetSync')
        self.assertIn('{street}', camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT)
        self.assertIn('{street}', camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_HUB_GREET_CHEERED)
        self.assertTrue(callable(camp.oswaldPresenceGreetTip))
        blob = ' '.join([
            camp.OSWALD_PRESENCE_HUB_GREET,
            camp.OSWALD_PRESENCE_STREET_GREET,
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_HUB_GREET_CHEERED,
            camp.OSWALD_PRESENCE_STREET_GREET_CHEERED,
            camp.OSWALD_PRESENCE_FIRST_MEET_TIP,
            camp.OSWALD_PRESENCE_CHEER_TIP,
            camp.OSWALD_PRESENCE_INTERACT_PROMPT,
            camp.OSWALD_PRESENCE_LABEL,
            camp.OSWALD_PRESENCE_PLATE,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, blob)

    def test_presence_zones_hub_and_acts(self):
        camp = self.camp
        self.assertTrue(_mirror_should_show(camp, TTC))
        self.assertTrue(_mirror_should_show(camp, LOOPY))
        self.assertTrue(_mirror_should_show(camp, PUNCHLINE))
        self.assertTrue(_mirror_should_show(camp, SILLY))
        self.assertFalse(_mirror_should_show(camp, 9999))
        # After betrayal the trusted face hides.
        self.assertFalse(_mirror_should_show(camp, TTC, betrayed=True))
        self.assertFalse(_mirror_should_show(camp, LOOPY, betrayed=True))

    def test_greet_copy_hub_vs_street(self):
        camp = self.camp
        hub = _mirror_greet(camp, TTC)
        street = _mirror_greet(camp, LOOPY)
        self.assertIn('plaza', hub.lower())
        self.assertIn('packs', street.lower())
        self.assertNotEqual(hub, street)
        # Soft-next after cheer latch + unlocks.
        hub_soft = _mirror_greet(
            camp, TTC, cheered=True, softNextStreet='Punchline Place')
        self.assertIn('Punchline Place', hub_soft)
        self.assertNotEqual(hub_soft, hub)
        cheered_only = _mirror_greet(camp, TTC, cheered=True)
        self.assertEqual(cheered_only, camp.OSWALD_PRESENCE_HUB_GREET_CHEERED)

    def test_presence_module_ast_surface(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        names = _module_names(rel)
        for required in (
                'presenceEnabled',
                'presenceLabel',
                'hubGreetTip',
                'streetGreetTip',
                'hubGreetSoftNextTip',
                'streetGreetSoftNextTip',
                'hubGreetCheeredTip',
                'streetGreetCheeredTip',
                'firstMeetTip',
                'cheerTip',
                'interactPromptTip',
                'greetTipForZone',
                'shouldShowPresence',
                'presenceZoneIds',
                'hubPlazaPos',
                'cheerOnReclaim',
                'metMsgName',
                'metSyncMsgName',
                'OswaldPresenceClient',
                'ensureOswaldPresenceClient',
                'getOswaldPresenceClient',
                'playOswaldPresenceCheer',
                'refreshOswaldPresenceHub',
                'stopOswaldPresenceClient'):
            self.assertIn(required, names)
        methods = _class_methods(rel, 'OswaldPresenceClient')
        for required in (
                '_placeBody',
                '_placeBodyAtPlaza',
                '_placeBodyNearAvatar',
                '_buildNpcSilhouette',
                '_buildNametag',
                '_armInteract',
                '_onInteractKey',
                '_meetOswald',
                '_onOswaldPresenceMet',
                '_onOswaldMetSync',
                '_requestPersistMet',
                '_onOswaldPresenceCheered',
                '_onOswaldCheeredSync',
                '_requestPersistCheered',
                '_onCampaignActUnlocked',
                '_refreshSoftNextStreet',
                '_playGreetWave',
                '_playCheerBounce',
                '_onReclaimCheer',
                'playReclaimCheer',
                '_startIdleBob',
                '_onCampaignProgressSync',
                '_onBetrayal'):
            self.assertIn(required, methods)
        src = _read(rel)
        src_l = src.lower()
        self.assertIn('oswaldpresencemet', src_l)
        self.assertIn('oswaldmetsync', src_l)
        self.assertIn('oswaldpresencecheered', src_l)
        self.assertIn('oswaldcheeredsync', src_l)
        self.assertIn('_oswaldmet', src_l)
        self.assertIn('_oswaldcheered', src_l)
        self.assertIn('firstmeettip', src_l)
        self.assertIn('d_requestoswaldmet', src_l)
        self.assertIn('d_requestoswaldcheered', src_l)
        self.assertIn('localavatarzonechange', src_l)
        self.assertIn('oswaldrevealbanner', src_l)
        self.assertIn('oswaldbetrayalchase', src_l)
        self.assertIn('campaignvictory', src_l)
        self.assertIn('npccheerstub', src_l)
        self.assertIn('purityrestorefx', src_l)
        self.assertIn('oswaldpresencecheer', src_l)
        # Plaza NPC deepen beyond spawn-near-avatar CardMaker stub.
        self.assertIn('CardMaker', src)
        self.assertIn('oswald-npc-torso', src)
        self.assertIn('oswald-npc-head', src)
        self.assertIn('oswald-npc-ear-l', src)
        self.assertIn('_buildNpcSilhouette', src)
        self.assertIn('_placeBodyAtPlaza', src)
        self.assertIn('OSWALD_PRESENCE_HUB_POS', src)
        self.assertIn('_armInteract', src)
        self.assertIn("accept('e'", src)
        self.assertIn('oswaldPresenceInteract', src)
        self.assertIn('playReclaimCheer', src)
        self.assertIn('_playCheerBounce', src)
        self.assertIn('oswaldPresenceArms', src)
        # Preserve #333 login mirror hide on persisted victory.
        self.assertIn('_onCampaignProgressSync', src)
        self.assertIn('clientMirrorFromProgress', src)
        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', src)
        # Doc may say "no keyblades"; ban affirmative KH product copy only.
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('sora', src_l)
        # Stub — not a full DistributedNPC / companion AI.
        self.assertNotIn('from toontown.toon', src)
        self.assertNotIn('distributednpctoon', src_l)
        self.assertIn('not a', src_l)
        self.assertIn('full distributednpc', src_l)
        self.assertIn('stub', src_l)
        # Beyond TextNode-only #321 placemarker.
        self.assertNotIn("TextNode('oswaldPresenceLabel')", src)

    def test_reclaim_cheer_nudges_oswald(self):
        cheer_src = _read('toontown/reclaim/ReclaimCheer.py')
        self.assertIn('_nudgeOswald', cheer_src)
        self.assertIn('ensureOswaldPresenceClient', cheer_src)
        self.assertIn('OSWALD_PRESENCE_CHEER_MSG', cheer_src)
        self.assertIn('oswaldPresenceCheer', cheer_src)
        director_src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('ensureOswaldPresenceClient', director_src)
        self.assertIn('npcCheerStub', director_src)

    def test_client_wiring(self):
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('ensureOswaldPresenceClient', play_src)
        # Chase wiring (#313) must remain.
        self.assertIn('ensureOswaldBetrayalChaseClient', play_src)
        playground = _read('toontown/safezone/TTPlayground.py')
        self.assertIn('refreshOswaldPresenceHub', playground)
        self.assertIn('stopOswaldPresenceClient', playground)
        # Breadcrumbs stay on hub enter.
        self.assertIn('ensureCorruptStreetBreadcrumbs', playground)

    def test_chase_and_loopy_unease_not_regressed(self):
        camp = self.camp
        # #313 chase tunables still present.
        self.assertTrue(camp.OSWALD_BETRAYAL_CHASE_ENABLED)
        self.assertIn('Corrupted Oswald', camp.OSWALD_BETRAYAL_CHASE_NAME)
        # #319 Loopy mid-act unease tip still present.
        loopy = camp.ACTS[0]
        self.assertEqual(loopy['id'], 'loopy')
        tip = loopy.get('approachTip') or ''
        self.assertIn('Oswald', tip)
        self.assertIn('half-beat', tip.lower())
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('_armLoopyApproachTip', play_src)
        self.assertIn('_showLoopyApproachTip', play_src)
        chase_src = _read('toontown/campaign/OswaldBetrayalChase.py')
        self.assertIn('spawnCorruptOswald', chase_src)
        self.assertIn('ARCHETYPE_CORRUPT_OSWALD', chase_src)

    def test_magic_words_and_docs_mention_presence(self):
        magic = _read('toontown/campaign/MagicWords.py').lower()
        self.assertIn('plaza', magic)
        self.assertIn('cheer on reclaim', magic)
        self.assertIn('e-talk', magic)
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('oswaldpresence', reclaim)
        self.assertIn('trusted reclaim lead', reclaim)
        self.assertIn('e-talk', reclaim)
        self.assertIn('npccheerstub', reclaim.replace('`', ''))
        self.assertIn('plaza', reclaim)

    def test_not_cream_only_module(self):
        src = _read('toontown/campaign/OswaldPresence.py').lower()
        # Presence deepen owns plaza NPC / cheer — not a cream wash deepen PR.
        self.assertNotIn('cream_wash', src)
        self.assertNotIn('creamaftershock', src.replace('_', ''))
        self.assertIn('greet', src)
        self.assertIn('silhouette', src)
        self.assertIn('interact', src)
        self.assertIn('cheer', src)
        self.assertIn('plaza', src)


if __name__ == '__main__':
    unittest.main()
