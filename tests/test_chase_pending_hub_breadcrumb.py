#!/usr/bin/env python3
"""Headless tests: chase-pending hub breadcrumb honesty (no reclaim-Oswald lie).

STATE_VICTORY + chaseCleared=0 must not keep Silly (or peer) placemarkers
saying reclaim-with-Oswald. Prefer wash-the-chase copy and gate reclaim
invites. Loads CampaignGlobals / breadcrumb pure helpers with a
ToontownGlobals stub — no Panda3D. No cream deepen / no KH.

Run from repo root:
  python3 tests/test_chase_pending_hub_breadcrumb.py
  python3 -m unittest tests.test_chase_pending_hub_breadcrumb -v
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
HUB = 2000

BREADCRUMB_REL = 'toontown/safezone/CorruptStreetBreadcrumb.py'
PLAY_ENTRY_REL = 'toontown/campaign/PlayEntry.py'
CAMP_GLOBALS_REL = 'toontown/campaign/CampaignGlobals.py'


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_reclaim_and_campaign():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim', 'toontown.campaign', 'toontown.safezone'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = HUB

    def _missing(*_a, **_k):
        raise RuntimeError('getSignFont unavailable headless')

    tg.getSignFont = _missing
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
    sys.modules['toontown.reclaim'].ReclaimGlobals = rg

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp
    return rg, camp, tg


def _extract_breadcrumb_chase_helpers(tg):
    path = REPO_ROOT / BREADCRUMB_REL
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src, filename=BREADCRUMB_REL)

    keep_assign = {
        '_clientUnlockedThrough',
        '_clientChasePending',
        '_STREET_COPY',
        '_STREET_COPY_CHASE_PENDING',
    }
    keep_funcs = {
        'getClientUnlockedThrough',
        'setClientUnlockedThrough',
        'resetClientUnlockedThrough',
        'getClientChasePending',
        'setClientChasePending',
        'resetClientChasePending',
        'noteChasePending',
        'noteCampaignProgressFields',
        'streetBreadcrumbText',
        'streetNeedsBreadcrumb',
        'streetBreadcrumbChasePending',
        'streetBreadcrumbDimmed',
        '_streetActUnlocked',
        '_streetLooksPolluted',
        'reclaimStreetEntries',
    }
    keep = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in keep_assign:
                    keep.append(node)
                    break
        elif isinstance(node, ast.FunctionDef) and node.name in keep_funcs:
            keep.append(node)
    found = {n.name for n in keep if isinstance(n, ast.FunctionDef)}
    missing = keep_funcs - found
    if missing:
        raise AssertionError(
            'missing breadcrumb helpers %s' % sorted(missing))

    mod = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(mod)
    rg = sys.modules['toontown.reclaim.ReclaimGlobals']
    camp = sys.modules['toontown.campaign.CampaignGlobals']
    reclaim_pkg = types.ModuleType('toontown.reclaim')
    reclaim_pkg.ReclaimGlobals = rg
    sys.modules['toontown.reclaim'] = reclaim_pkg
    campaign_pkg = sys.modules.get('toontown.campaign')
    if campaign_pkg is None:
        campaign_pkg = types.ModuleType('toontown.campaign')
        sys.modules['toontown.campaign'] = campaign_pkg
    campaign_pkg.CampaignGlobals = camp
    ns = {
        'ToontownGlobals': tg,
        'ReclaimGlobals': rg,
        'notify': types.SimpleNamespace(debug=lambda *_a, **_k: None),
        '_activeBreadcrumb': None,
    }
    exec(compile(mod, BREADCRUMB_REL, 'exec'), ns)  # noqa: S102
    return ns


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                item.name for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return set()


def _accept_events(tree: ast.AST, class_name: str) -> set[str]:
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
            elif isinstance(arg0, ast.Name):
                events.add(arg0.id)
    return events


class ChasePendingHubBreadcrumbTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.camp, cls.tg = _load_reclaim_and_campaign()
        cls.helpers = _extract_breadcrumb_chase_helpers(cls.tg)
        cls.crumb_src = _read(BREADCRUMB_REL)
        cls.play_src = _read(PLAY_ENTRY_REL)
        cls.camp_src = _read(CAMP_GLOBALS_REL)

    def setUp(self):
        self.helpers['resetClientUnlockedThrough']()
        self.helpers['resetClientChasePending']()

    def test_campaign_chase_pending_helper(self):
        camp = self.camp
        self.assertTrue(callable(camp.campaignChasePending))
        self.assertTrue(camp.campaignChasePending(camp.STATE_VICTORY, 0))
        self.assertFalse(camp.campaignChasePending(camp.STATE_VICTORY, 1))
        self.assertFalse(camp.campaignChasePending(camp.STATE_ACTIVE, 0))
        self.assertFalse(camp.campaignChasePending(camp.STATE_IDLE, 0))

    def test_silly_chase_pending_copy_not_reclaim_with_oswald(self):
        text_fn = self.helpers['streetBreadcrumbText']
        reclaim = text_fn(SILLY, streetName='Silly Street', chasePending=False)
        self.assertIn('reclaim with Oswald', reclaim)
        pending = text_fn(SILLY, streetName='Silly Street', chasePending=True)
        self.assertNotIn('reclaim with Oswald', pending.lower())
        self.assertIn('betrayal chase', pending.lower())
        self.assertIn('wash', pending.lower())
        self.assertIn('Silly', pending)
        # Peer streets also honest while chase pending.
        for zone, name in (
                (LOOPY, 'Loopy Lane'),
                (PUNCHLINE, 'Punchline Place')):
            peer = text_fn(zone, streetName=name, chasePending=True)
            self.assertNotIn('reclaim with Oswald', peer.lower())
            self.assertIn('betrayal chase', peer.lower())

    def test_reclaim_invite_gated_while_chase_pending(self):
        needs = self.helpers['streetNeedsBreadcrumb']
        chase = self.helpers['streetBreadcrumbChasePending']
        # Unlocked Silly would normally reclaim-invite.
        self.assertTrue(needs(
            SILLY, {}, seedPollution=0.80, pure=0.0,
            unlockedThrough=2, chasePending=False))
        self.assertFalse(chase(
            SILLY, {}, seedPollution=0.80, pure=0.0,
            unlockedThrough=2, chasePending=False))
        # Chase pending gates reclaim invite; chase placemarker wins.
        self.assertFalse(needs(
            SILLY, {}, seedPollution=0.80, pure=0.0,
            unlockedThrough=2, chasePending=True))
        self.assertTrue(chase(
            SILLY, {}, seedPollution=0.80, pure=0.0,
            unlockedThrough=2, chasePending=True))
        # Locked act stays dim, not chase (unlock soft-gate still wins).
        self.assertFalse(chase(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0,
            unlockedThrough=0, chasePending=True))

    def test_progress_fields_latch_chase_pending(self):
        camp = self.camp
        note = self.helpers['noteCampaignProgressFields']
        get_p = self.helpers['getClientChasePending']
        get_u = self.helpers['getClientUnlockedThrough']

        unlocked, pending = note(
            unlockedThrough=2,
            state=camp.STATE_VICTORY,
            chaseCleared=0,
            reclaimCount=3)
        self.assertEqual(unlocked, 2)
        self.assertEqual(get_u(), 2)
        self.assertTrue(pending)
        self.assertTrue(get_p())

        unlocked, pending = note(
            unlockedThrough=2,
            state=camp.STATE_VICTORY,
            chaseCleared=1,
            reclaimCount=3)
        self.assertFalse(pending)
        self.assertFalse(get_p())

        # Active campaign must clear chase-pending latch.
        note(unlockedThrough=1, state=camp.STATE_ACTIVE, chaseCleared=0)
        self.assertFalse(get_p())

    def test_note_chase_pending_and_entries(self):
        note = self.helpers['noteChasePending']
        get_p = self.helpers['getClientChasePending']
        entries = self.helpers['reclaimStreetEntries']

        self.assertFalse(get_p())
        self.assertTrue(note(True))
        self.assertTrue(get_p())
        pending_entries = entries(chasePending=True)
        self.assertTrue(pending_entries)
        blob = ' '.join(text for _z, _n, text, _s in pending_entries)
        self.assertNotIn('reclaim with Oswald', blob)
        self.assertIn('betrayal chase', blob.lower())
        silly = [t for z, _n, t, _s in pending_entries if int(z) == SILLY]
        self.assertTrue(silly)
        self.assertIn('wash', silly[0].lower())

        reclaim_entries = entries(chasePending=False)
        reclaim_blob = ' '.join(t for _z, _n, t, _s in reclaim_entries)
        self.assertIn('reclaim with Oswald', reclaim_blob)

    def test_breadcrumb_wires_chase_pending(self):
        tree = ast.parse(self.crumb_src, filename=BREADCRUMB_REL)
        methods = _class_method_names(tree, 'CorruptStreetBreadcrumb')
        for name in (
                '_onCampaignProgressSync',
                '_onCampaignVictory',
                '_onCampaignEpilogue'):
            self.assertIn(name, methods)

        accepts = _accept_events(tree, 'CorruptStreetBreadcrumb')
        self.assertTrue(
            'syncMsg' in accepts or 'campaignProgressSync' in accepts)
        self.assertTrue(
            'victoryMsg' in accepts or 'campaignVictory' in accepts)
        self.assertIn('campaignEpilogue', accepts)

        sync_idx = self.crumb_src.find('def _onCampaignProgressSync')
        self.assertGreater(sync_idx, 0)
        next_idx = self.crumb_src.find('\n    def ', sync_idx + 1)
        sync_win = self.crumb_src[
            sync_idx:next_idx if next_idx > 0 else sync_idx + 900]
        self.assertIn('noteCampaignProgressFields', sync_win)
        self.assertIn('chaseCleared', sync_win)
        self.assertIn('state', sync_win)
        # Must not claim crumbs ignore chase fields anymore.
        self.assertNotIn('crumbs only need unlock cursor', sync_win)

        self.assertIn("mode == 'chase'", self.crumb_src)
        self.assertIn('streetBreadcrumbChasePending', self.crumb_src)
        self.assertIn('_STREET_COPY_CHASE_PENDING', self.crumb_src)
        self.assertIn('wash Oswald', self.crumb_src)

    def test_playentry_notes_chase_pending(self):
        src = self.play_src
        sync_idx = src.find('def _onCampaignProgressSync')
        self.assertGreater(sync_idx, 0)
        next_idx = src.find('\n    def ', sync_idx + 1)
        sync_win = src[sync_idx:next_idx if next_idx > 0 else sync_idx + 2200]
        self.assertIn('noteChasePending', sync_win)
        self.assertIn("bool(self._chasePending)", sync_win)

        victory_idx = src.find('def _onCampaignVictory')
        victory_next = src.find('\n    def ', victory_idx + 1)
        victory_win = src[
            victory_idx:victory_next if victory_next > 0 else victory_idx + 500]
        self.assertIn('noteChasePending(True)', victory_win)

        epi_idx = src.find('def _onCampaignEpilogue')
        epi_next = src.find('\n    def ', epi_idx + 1)
        epi_win = src[epi_idx:epi_next if epi_next > 0 else epi_idx + 800]
        self.assertIn('noteChasePending(False)', epi_win)

    def test_no_kh_and_no_cream_deepen_in_this_pr_scope(self):
        for rel in (BREADCRUMB_REL, PLAY_ENTRY_REL, CAMP_GLOBALS_REL):
            blob = _read(rel).lower()
            for banned in ('kingdom hearts', 'sora', 'keyblade', 'key blade'):
                # Allow explicit "no KH" / "no keyblade" product bans.
                if banned in ('keyblade', 'key blade'):
                    if ('no %s' % banned) in blob or ('without %s' % banned) in blob:
                        continue
                    if ('no kh' in blob) and banned.startswith('key'):
                        # Still fail affirmative keyblade product copy.
                        pass
                if banned in blob and (
                        'no %s' % banned) not in blob and (
                        'without %s' % banned) not in blob:
                    # CampaignGlobals already bans KH in many comments —
                    # only fail affirmative product copy in new chase strings.
                    if rel == CAMP_GLOBALS_REL and banned in (
                            'kingdom hearts', 'sora'):
                        continue
                    if 'no kh' in blob and banned in (
                            'kingdom hearts', 'sora', 'keyblade', 'key blade'):
                        continue
                    # Narrow: chase-pending copy block must stay clean.
                    pass
        chase_blob = ' '.join([
            self.helpers['streetBreadcrumbText'](
                z, chasePending=True)
            for z in (LOOPY, PUNCHLINE, SILLY)
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'key blade'):
            self.assertNotIn(banned, chase_blob)


if __name__ == '__main__':
    unittest.main()
