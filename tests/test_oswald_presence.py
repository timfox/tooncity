#!/usr/bin/env python3
"""Headless/AST tests: Oswald hub/street presence stub (trust lead).

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D.
OswaldPresence helpers are mirrored from CampaignGlobals (module imports
panda); client wiring is AST-checked.

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


def _mirror_greet(camp, zoneId):
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
        self.assertGreater(float(camp.OSWALD_PRESENCE_INTERACT_RADIUS), 2.0)
        self.assertGreater(float(camp.OSWALD_PRESENCE_SPAWN_FORWARD), 0.0)
        self.assertTrue(camp.OSWALD_PRESENCE_HIDE_ON_BETRAYAL)
        blob = ' '.join([
            camp.OSWALD_PRESENCE_HUB_GREET,
            camp.OSWALD_PRESENCE_STREET_GREET,
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

    def test_presence_module_ast_surface(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        names = _module_names(rel)
        for required in (
                'presenceEnabled',
                'presenceLabel',
                'hubGreetTip',
                'streetGreetTip',
                'greetTipForZone',
                'shouldShowPresence',
                'presenceZoneIds',
                'OswaldPresenceClient',
                'ensureOswaldPresenceClient',
                'refreshOswaldPresenceHub',
                'stopOswaldPresenceClient'):
            self.assertIn(required, names)
        src = _read(rel).lower()
        self.assertIn('oswaldpresencemet', src)
        self.assertIn('localavatarzonechange', src)
        self.assertIn('oswaldrevealbanner', src)
        self.assertIn('oswaldbetrayalchase', src)
        self.assertIn('campaignvictory', src)
        # Doc may say "no keyblades"; ban affirmative KH product copy only.
        self.assertNotIn('kingdom hearts', src)
        self.assertNotIn('sora', src)
        # Stub — no DistributedNPC import / subclass (meetable placemarker only).
        self.assertNotIn('from toontown.toon', src)
        self.assertNotIn('distributednpctoon', src)
        self.assertIn('stub', src)
        self.assertIn('not a distributednpc', src)

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
        self.assertIn('presence stub', magic)
        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('oswaldpresence', reclaim)
        self.assertIn('trusted reclaim lead', reclaim)

    def test_not_cream_only_module(self):
        src = _read('toontown/campaign/OswaldPresence.py').lower()
        # Presence stub owns placemarker/greet — not a cream wash deepen PR.
        self.assertNotIn('cream_wash', src)
        self.assertNotIn('creamaftershock', src.replace('_', ''))
        self.assertIn('proximity', src)
        self.assertIn('placemarker', src)


if __name__ == '__main__':
    unittest.main()
