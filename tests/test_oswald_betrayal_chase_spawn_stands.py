#!/usr/bin/env python3
"""Headless tests: authored Oswald betrayal chase spawn stands.

Loads CampaignGlobals with a ToontownGlobals stub — no Panda3D.
Locks OSWALD_BETRAYAL_CHASE_POS as stable landmarks (hub shares
HubStainConfront plaza xy; Silly finale wash arena distinct from
OSWALD_PRESENCE_STREET_POS) and AST-checks spawnCorruptOswald prefers
authored stands over SPAWN_FORWARD beside the local toon. Hub
resume-at-confront falls back to HUB_STAIN_CONFRONT_POS when chase POS
unset. No cream / no KH.

Run from repo root:
  python3 tests/test_oswald_betrayal_chase_spawn_stands.py
  python3 -m unittest tests.test_oswald_betrayal_chase_spawn_stands -v
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


def _parse_stand(raw):
    if raw is None:
        return None
    return (float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]))


def _mirror_chase_spawn_stand(camp, zoneId):
    """Mirror OswaldBetrayalChase.chaseSpawnStand without importing panda."""
    raw_map = getattr(camp, 'OSWALD_BETRAYAL_CHASE_POS', None) or {}
    try:
        zid = int(zoneId)
    except Exception:
        return None
    raw = None
    try:
        raw = raw_map.get(zid)
    except Exception:
        raw = None
    if raw is None:
        try:
            raw = raw_map.get(str(zid))
        except Exception:
            raw = None
    stand = _parse_stand(raw)
    if stand is not None:
        return stand
    hub = int(getattr(camp, 'HUB_ZONE', -1))
    if zid != hub:
        return None
    confront = _parse_stand(getattr(camp, 'HUB_STAIN_CONFRONT_POS', None))
    if confront is None:
        return None
    x, y, z, h = confront
    if z > 0.5:
        hub_body = _parse_stand(getattr(camp, 'OSWALD_PRESENCE_HUB_POS', None))
        if hub_body is not None:
            z = hub_body[2]
        else:
            z = float(getattr(camp, 'OSWALD_PRESENCE_BODY_Z', 0.0) or 0.0)
    return (x, y, z, h)


class OswaldBetrayalChaseSpawnStandsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp = _load_panda_free_globals()

    def test_chase_pos_map_covers_hub_and_finale(self):
        camp = self.camp
        pos_map = camp.OSWALD_BETRAYAL_CHASE_POS
        self.assertIn(int(camp.HUB_ZONE), pos_map)
        self.assertIn(TTC, pos_map)
        self.assertIn(SILLY, pos_map)
        # Loopy / Punchline not required — chase fields on finale / hub resume.
        self.assertNotIn(LOOPY, pos_map)
        self.assertNotIn(PUNCHLINE, pos_map)
        stands = []
        for zid in (TTC, SILLY):
            stand = pos_map[zid]
            self.assertEqual(len(stand), 4)
            self.assertTrue(all(isinstance(v, (int, float)) for v in stand))
            x, y = float(stand[0]), float(stand[1])
            self.assertNotEqual((x, y), (0.0, 0.0))
            self.assertNotEqual(
                (x, y), (0.0, float(camp.OSWALD_BETRAYAL_CHASE_SPAWN_FORWARD)),
                msg='zone %s looks like SPAWN_FORWARD offset' % zid)
            stands.append(tuple(float(v) for v in stand))
        self.assertEqual(len(set(stands)), 2)
        self.assertGreater(float(camp.OSWALD_BETRAYAL_CHASE_SPAWN_FORWARD), 0.0)

    def test_hub_chase_stand_shares_confront_landmark_xy(self):
        camp = self.camp
        hub_stand = camp.OSWALD_BETRAYAL_CHASE_POS[TTC]
        confront = camp.HUB_STAIN_CONFRONT_POS
        self.assertEqual(float(hub_stand[0]), float(confront[0]))
        self.assertEqual(float(hub_stand[1]), float(confront[1]))
        self.assertEqual(float(hub_stand[3]), float(confront[3]))
        # Fightable body is grounded — not confront label height.
        self.assertLessEqual(float(hub_stand[2]), 0.5)
        # Distinct from trusted-face presence hub stand.
        presence = camp.OSWALD_PRESENCE_HUB_POS
        self.assertNotEqual(tuple(hub_stand), tuple(presence))
        # Distinct from washed-plaza epilogue beat.
        epi = camp.HUB_EPILOGUE_BEAT_POS
        self.assertNotEqual(
            (float(hub_stand[0]), float(hub_stand[1])),
            (float(epi[0]), float(epi[1])))

    def test_silly_chase_stand_distinct_from_presence_street(self):
        camp = self.camp
        chase = camp.OSWALD_BETRAYAL_CHASE_POS[SILLY]
        presence = camp.OSWALD_PRESENCE_STREET_POS[SILLY]
        self.assertNotEqual(tuple(chase), tuple(presence))
        self.assertNotEqual(
            (float(chase[0]), float(chase[1])),
            (float(presence[0]), float(presence[1])))

    def test_chase_spawn_stand_mirror_hub_and_silly(self):
        hub = _mirror_chase_spawn_stand(self.camp, TTC)
        silly = _mirror_chase_spawn_stand(self.camp, SILLY)
        self.assertIsNotNone(hub)
        self.assertIsNotNone(silly)
        self.assertEqual(len(hub), 4)
        self.assertEqual(len(silly), 4)
        # Unmapped street → None (near-avatar fallback path).
        self.assertIsNone(_mirror_chase_spawn_stand(self.camp, LOOPY))

    def test_hub_confront_fallback_when_chase_pos_cleared(self):
        camp = self.camp
        # Simulate unset chase POS for hub — still resume at confront.
        saved = dict(camp.OSWALD_BETRAYAL_CHASE_POS)
        try:
            camp.OSWALD_BETRAYAL_CHASE_POS = {
                k: v for k, v in saved.items() if int(k) != TTC}
            stand = _mirror_chase_spawn_stand(camp, TTC)
            self.assertIsNotNone(stand)
            confront = camp.HUB_STAIN_CONFRONT_POS
            self.assertEqual(float(stand[0]), float(confront[0]))
            self.assertEqual(float(stand[1]), float(confront[1]))
            self.assertLessEqual(float(stand[2]), 0.5)
        finally:
            camp.OSWALD_BETRAYAL_CHASE_POS = saved

    def test_chase_module_prefers_authored_stand(self):
        rel = 'toontown/campaign/OswaldBetrayalChase.py'
        names = _module_names(rel)
        for required in (
                'chaseSpawnStand',
                '_parseStandPos',
                'spawnCorruptOswald',
                'OswaldBetrayalChaseClient'):
            self.assertIn(required, names)
        src = _read(rel)
        self.assertIn('OSWALD_BETRAYAL_CHASE_POS', src)
        self.assertIn('HUB_STAIN_CONFRONT_POS', src)
        self.assertIn('chaseSpawnStand', src)
        # Placement order inside spawn: authored stand → near-avatar fallback.
        spawn = src[src.index('def spawnCorruptOswald'):]
        spawn = spawn[:spawn.index('\ndef ', 1)]
        stand_idx = spawn.index('chaseSpawnStand')
        near_idx = spawn.index('getX()')
        self.assertLess(stand_idx, near_idx)
        self.assertIn('OSWALD_BETRAYAL_CHASE_SPAWN_FORWARD', spawn)
        # Ban affirmative KH product copy; "no KH branding" negation is OK.
        src_l = src.lower()
        self.assertNotIn('kingdom hearts', src_l)
        self.assertNotIn('sora', src_l)
        self.assertNotIn('key blade', src_l)
        self.assertNotIn('cream_wash', src_l)
        self.assertNotIn('cream wash', src_l)

    def test_director_documents_authored_stand_preference(self):
        src = _read('toontown/campaign/CampaignDirectorAI.py')
        spawn = src[src.find('def __spawnOswaldBetrayalChase'):]
        spawn = spawn[:spawn.find('\n    def ', 1)]
        self.assertIn('OSWALD_BETRAYAL_CHASE_POS', spawn)
        self.assertIn('HubStainConfront', spawn)
        self.assertIn('spawnCorruptOswald', spawn)
        self.assertIn('liveZone', spawn)

    def test_globals_comment_documents_landmarks(self):
        camp_src = _read('toontown/campaign/CampaignGlobals.py')
        self.assertIn('OSWALD_BETRAYAL_CHASE_POS', camp_src)
        # Slice the authored-stands comment block above the POS assignment.
        assign_idx = camp_src.index('OSWALD_BETRAYAL_CHASE_POS = {')
        blob = camp_src[assign_idx - 700:assign_idx].lower()
        self.assertIn('landmark', blob)
        self.assertIn('not spawn_forward', blob)
        self.assertIn('hubstainconfront', blob)
        self.assertIn('OSWALD_BETRAYAL_CHASE_SPAWN_FORWARD', camp_src)

    def test_no_kh_cream_in_chase_copy(self):
        camp = self.camp
        blob = ' '.join([
            camp.OSWALD_BETRAYAL_CHASE_TIP,
            camp.OSWALD_BETRAYAL_CHASE_BANNER,
            camp.OSWALD_BETRAYAL_CHASE_MSG,
            camp.OSWALD_BETRAYAL_CHASE_CLEAR_MSG,
            camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'kh '):
            self.assertNotIn(banned, blob)


if __name__ == '__main__':
    unittest.main()
