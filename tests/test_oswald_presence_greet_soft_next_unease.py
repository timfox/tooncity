#!/usr/bin/env python3
"""Headless tests: Oswald soft-next greets deepen unease from unlock progress.

Loads CampaignGlobals + CampaignProgressSave with a ToontownGlobals stub —
no Panda3D. Locks Punchline→Silly soft-next greet unease ladder after
#373/#395 soft-next plumbing (stub-safe foreshadow; no twist spoilers /
no DNA Oswald / no cream / no KH).

Run from repo root:
  python3 tests/test_oswald_presence_greet_soft_next_unease.py
  python3 -m unittest tests.test_oswald_presence_greet_soft_next_unease -v
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


def _load_panda_free_campaign():
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


class OswaldPresenceGreetSoftNextUneaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.save = _load_panda_free_campaign()

    def test_soft_next_unease_tunables(self):
        camp = self.camp
        # Punchline-tier (default soft-next) carries light unease.
        self.assertIn('{street}', camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT)
        self.assertIn('{street}', camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT)
        punch_blob = ' '.join([
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT,
        ]).lower()
        self.assertIn('stretchy', punch_blob)
        self.assertIn('half-beat', punch_blob)
        # Silly-tier deepens further.
        self.assertIn('{street}', camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT_SILLY)
        self.assertIn(
            '{street}', camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT_SILLY)
        silly_blob = ' '.join([
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT_SILLY,
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT_SILLY,
        ]).lower()
        self.assertIn('half-beat off', silly_blob)
        self.assertIn('rubbery', silly_blob)
        self.assertNotEqual(
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT_SILLY)
        self.assertNotEqual(
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT,
            camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT_SILLY)
        # Stub-safe foreshadow — no twist spoilers / cream / KH.
        all_blob = ' '.join([punch_blob, silly_blob])
        for banned in (
                'almost confess', 'caused', 'keyblade', 'kingdom hearts',
                'sora', 'key blade', 'cream_wash', 'cream wash'):
            self.assertNotIn(banned, all_blob)

    def test_unease_tier_helper(self):
        camp = self.camp
        tier = camp.oswaldPresenceSoftNextUneaseTier
        self.assertEqual(tier('Punchline Place'), 'punchline')
        self.assertEqual(tier(camp.ACTS[1]['name']), 'punchline')
        self.assertEqual(tier(camp.ACTS[2]['name']), 'silly')
        self.assertEqual(tier('Silly Street'), 'silly')
        self.assertEqual(tier(None), 'punchline')
        self.assertEqual(tier(''), 'punchline')

    def test_soft_next_templates_by_tier(self):
        camp = self.camp
        punch_hub, punch_street = camp.oswaldPresenceSoftNextTemplates(
            'Punchline Place')
        silly_hub, silly_street = camp.oswaldPresenceSoftNextTemplates(
            camp.ACTS[2]['name'])
        self.assertEqual(punch_hub, camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT)
        self.assertEqual(
            punch_street, camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT)
        self.assertEqual(
            silly_hub, camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT_SILLY)
        self.assertEqual(
            silly_street, camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT_SILLY)

    def test_greet_tip_punchline_then_silly_ladder(self):
        camp = self.camp
        greet = camp.oswaldPresenceGreetTip
        punch_name = camp.ACTS[1]['name']
        silly_name = camp.ACTS[2]['name']

        hub_punch = greet(TTC, cheered=True, softNextStreet=punch_name)
        street_punch = greet(LOOPY, cheered=True, softNextStreet=punch_name)
        self.assertIn(punch_name, hub_punch)
        self.assertIn(punch_name, street_punch)
        self.assertIn('stretchy', hub_punch.lower())
        self.assertIn('half-beat', street_punch.lower())
        self.assertNotIn('half-beat off', hub_punch.lower())

        hub_silly = greet(TTC, cheered=True, softNextStreet=silly_name)
        street_silly = greet(
            PUNCHLINE, cheered=True, softNextStreet=silly_name)
        self.assertIn(silly_name, hub_silly)
        self.assertIn(silly_name, street_silly)
        self.assertIn('half-beat off', hub_silly.lower())
        self.assertIn('rubbery', street_silly.lower())
        self.assertNotEqual(hub_punch, hub_silly)
        self.assertNotEqual(street_punch, street_silly)
        # Still distinct from pre-cheer / cheered-only greets.
        self.assertNotEqual(hub_punch, camp.OSWALD_PRESENCE_HUB_GREET)
        self.assertNotEqual(hub_silly, camp.OSWALD_PRESENCE_HUB_GREET_CHEERED)
        for tip in (hub_punch, street_punch, hub_silly, street_silly):
            self.assertNotIn('almost confess', tip.lower())
            self.assertNotIn('keyblade', tip.lower())
            self.assertNotIn('cream wash', tip.lower())

    def test_progress_feeds_unease_ladder(self):
        camp = self.camp
        save = self.save
        punch_soft = save.softNextStreetFromProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'state': camp.STATE_ACTIVE,
        })
        self.assertEqual(punch_soft, camp.ACTS[1]['name'])
        punch_tip = camp.oswaldPresenceGreetTip(
            TTC, cheered=True, softNextStreet=punch_soft)
        self.assertIn('stretchy', punch_tip.lower())
        self.assertEqual(
            camp.oswaldPresenceSoftNextUneaseTier(punch_soft), 'punchline')

        silly_soft = save.softNextStreetFromProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_ACTIVE,
        })
        self.assertEqual(silly_soft, camp.ACTS[2]['name'])
        silly_tip = camp.oswaldPresenceGreetTip(
            TTC, cheered=True, softNextStreet=silly_soft)
        self.assertIn('half-beat off', silly_tip.lower())
        self.assertEqual(
            camp.oswaldPresenceSoftNextUneaseTier(silly_soft), 'silly')
        self.assertNotEqual(punch_tip, silly_tip)

    def test_presence_ast_unease_wiring(self):
        rel = 'toontown/campaign/OswaldPresence.py'
        names = _module_names(rel)
        for required in (
                'softNextUneaseTier',
                'softNextTemplates',
                'hubGreetSoftNextTip',
                'streetGreetSoftNextTip',
                'greetTipForZone'):
            self.assertIn(required, names)
        src = _read(rel)
        self.assertIn('oswaldPresenceSoftNextUneaseTier', src)
        self.assertIn('oswaldPresenceSoftNextTemplates', src)
        self.assertIn('SOFT_NEXT_SILLY', src)
        self.assertIn('Punchline', src)
        self.assertIn('unease', src.lower())
        src_l = src.lower()
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('sora', src_l)
        self.assertNotIn('cream_wash', src_l)

    def test_globals_exports_unease_helpers(self):
        camp = self.camp
        names = _module_names('toontown/campaign/CampaignGlobals.py')
        for required in (
                'oswaldPresenceSoftNextUneaseTier',
                'oswaldPresenceSoftNextTemplates',
                'oswaldPresenceGreetTip',
                'OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT',
                'OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT',
                'OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT_SILLY',
                'OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT_SILLY'):
            self.assertIn(required, names)
        self.assertTrue(callable(camp.oswaldPresenceSoftNextUneaseTier))
        self.assertTrue(callable(camp.oswaldPresenceSoftNextTemplates))
        # Comment lock: ladder + stub-safe foreshadow notes.
        src = _read('toontown/campaign/CampaignGlobals.py')
        block_start = src.index('OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT')
        preamble = src[max(0, block_start - 700):block_start]
        block = src[
            block_start:src.index('OSWALD_PRESENCE_HUB_GREET_CHEERED')]
        combined = preamble + block
        self.assertIn('Punchline', combined)
        self.assertIn('Silly', combined)
        self.assertIn('unease', combined.lower())
        self.assertIn('almost confess', combined.lower())
        self.assertIn('no DNA', combined)


if __name__ == '__main__':
    unittest.main()
