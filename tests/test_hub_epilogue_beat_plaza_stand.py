#!/usr/bin/env python3
"""Headless tests: authored HubEpilogueBeat plaza stand.

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D.
Locks HUB_EPILOGUE_BEAT_POS as a stable washed-plaza landmark (not
FORWARD beside the local toon) and AST-checks HubEpilogueBeat
placement prefers the authored stand. Distinct from
OSWALD_PRESENCE_HUB_POS (trusted face) and HUB_STAIN_CONFRONT_POS
(pending-stain confront). No cream / no KH.

Run from repo root:
  python3 tests/test_hub_epilogue_beat_plaza_stand.py
  python3 -m unittest tests.test_hub_epilogue_beat_plaza_stand -v
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

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    return camp


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


def _mirror_epilogue_plaza(camp):
    """Mirror HubEpilogueBeat.epilogueBeatPlazaPos without importing panda."""
    raw = getattr(camp, 'HUB_EPILOGUE_BEAT_POS', None)
    if raw is None:
        return None
    return (float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]))


class HubEpilogueBeatPlazaStandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp = _load_panda_free_globals()

    def test_epilogue_pos_is_authored_plaza_landmark(self):
        camp = self.camp
        stand = camp.HUB_EPILOGUE_BEAT_POS
        self.assertEqual(len(stand), 4)
        self.assertTrue(all(isinstance(v, (int, float)) for v in stand))
        x, y, z, h = (float(v) for v in stand)
        # Absolute world landmark — not a tiny offset-style (0, forward, 0).
        self.assertNotEqual((x, y), (0.0, 0.0))
        self.assertNotEqual(
            (x, y), (0.0, float(camp.HUB_EPILOGUE_BEAT_FORWARD)))
        # Distinct from Oswald's trusted-face hub stand.
        hub = camp.OSWALD_PRESENCE_HUB_POS
        self.assertEqual(len(hub), 4)
        self.assertNotEqual(tuple(stand), tuple(hub))
        # Distinct from pending-stain confront plaza stand.
        confront = camp.HUB_STAIN_CONFRONT_POS
        self.assertEqual(len(confront), 4)
        self.assertNotEqual(tuple(stand), tuple(confront))
        self.assertEqual(int(camp.HUB_ZONE), TTC)
        # FORWARD remains as unset-POS fallback only.
        self.assertGreater(float(camp.HUB_EPILOGUE_BEAT_FORWARD), 0.0)

    def test_epilogue_plaza_mirror_parses(self):
        stand = _mirror_epilogue_plaza(self.camp)
        self.assertIsNotNone(stand)
        self.assertEqual(len(stand), 4)

    def test_epilogue_module_prefers_plaza_stand(self):
        rel = 'toontown/campaign/HubEpilogueBeat.py'
        names = _module_names(rel)
        for required in (
                'epilogueBeatPlazaPos',
                'epilogueBeatForward',
                'HubEpilogueBeatClient',
                'ensureHubEpilogueBeatClient'):
            self.assertIn(required, names)
        methods = _class_methods(rel, 'HubEpilogueBeatClient')
        for required in (
                '_placeMarker',
                '_placeMarkerAtPlaza',
                '_placeMarkerNearAvatar',
                '_attachMarkerLabels'):
            self.assertIn(required, methods)
        src = _read(rel)
        self.assertIn('HUB_EPILOGUE_BEAT_POS', src)
        self.assertIn('epilogueBeatPlazaPos', src)
        self.assertIn('_placeMarkerAtPlaza', src)
        # Placement order: plaza → near-avatar fallback.
        place_idx = src.index('def _placeMarker(')
        plaza_idx = src.index('_placeMarkerAtPlaza', place_idx)
        near_idx = src.index('_placeMarkerNearAvatar', place_idx)
        self.assertLess(plaza_idx, near_idx)
        # Zone-change path calls _placeMarker (not near-avatar directly).
        zone = src[src.index('def _onZoneChange'):]
        zone = zone[:zone.index('def _progressWantsBeat')]
        self.assertIn('self._placeMarker()', zone)
        self.assertNotIn('self._placeMarkerNearAvatar()', zone)
        # No cream / KH.
        src_l = src.lower()
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('keyblade', src_l)
        self.assertNotIn('sora', src_l)
        self.assertNotIn('cream_wash', src_l)
        self.assertNotIn('cream wash', src_l)

    def test_globals_comment_documents_plaza_landmark(self):
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        self.assertIn('HUB_EPILOGUE_BEAT_POS', camp_src)
        blob = camp_src[
            camp_src.index('HUB_EPILOGUE_BEAT_POS') - 400:
            camp_src.index('HUB_EPILOGUE_BEAT_FORWARD')].lower()
        self.assertIn('landmark', blob)
        self.assertIn('not forward', blob)
        self.assertIn('oswald_presence_hub_pos', blob)
        self.assertIn('hub_stain_confront_pos', blob)
        # Fallback forward offset still present.
        self.assertIn('HUB_EPILOGUE_BEAT_FORWARD', camp_src)

    def test_no_kh_cream_in_epilogue_copy(self):
        camp = self.camp
        blob = ' '.join([
            camp.HUB_EPILOGUE_BEAT_LABEL,
            camp.HUB_EPILOGUE_BEAT_ABSENCE,
            camp.HUB_EPILOGUE_BEAT_TIP,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'kh '):
            self.assertNotIn(banned, blob)


if __name__ == '__main__':
    unittest.main()
