#!/usr/bin/env python3
"""Headless tests: dim hub breadcrumbs for locked campaign acts.

streetNeedsBreadcrumb respects act unlock (soft-gate parity with
street-pack R). Locked polluted tunnels get streetBreadcrumbDimmed.
Client accepts campaignActUnlocked (PlayEntry + CorruptStreetBreadcrumb)
to latch unlock and refresh crumbs. Login campaignProgressSync also
raises the unlock latch so hub crumbs undim after relog. No
CampaignDirectorAI rewrite — messenger already sends. No cream deepen
/ no KH.

Run from repo root:
  python3 tests/test_hub_breadcrumb_act_unlock.py
  python3 -m unittest tests.test_hub_breadcrumb_act_unlock -v
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
DIRECTOR_REL = 'toontown/campaign/CampaignDirectorAI.py'


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
    return rg, camp


def _extract_breadcrumb_unlock_helpers():
    """Compile pollution + unlock helpers without importing panda-heavy module."""
    path = REPO_ROOT / BREADCRUMB_REL
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src, filename=BREADCRUMB_REL)

    # Bind unlock latch + helpers; streetPackUnlocked via injected ReclaimGlobals.
    keep_assign = {
        '_clientUnlockedThrough',
    }
    keep_funcs = {
        'getClientUnlockedThrough',
        'setClientUnlockedThrough',
        'resetClientUnlockedThrough',
        '_streetActUnlocked',
        '_streetLooksPolluted',
        'streetNeedsBreadcrumb',
        'streetBreadcrumbDimmed',
        'noteCampaignActUnlocked',
    }
    keep = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in keep_assign:
                    keep.append(node)
                    break
        elif isinstance(node, ast.FunctionDef) and node.name in keep_funcs:
            # Skip noteCampaignActUnlocked — needs _activeBreadcrumb / notify.
            if node.name == 'noteCampaignActUnlocked':
                continue
            keep.append(node)
    needed = keep_funcs - {'noteCampaignActUnlocked'}
    found = {
        n.name for n in keep if isinstance(n, ast.FunctionDef)}
    missing = needed - found
    if missing:
        raise AssertionError(
            'missing breadcrumb helpers %s in %s' % (sorted(missing), BREADCRUMB_REL))

    mod = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(mod)
    rg, _camp = _load_reclaim_and_campaign()
    reclaim_pkg = types.ModuleType('toontown.reclaim')
    reclaim_pkg.ReclaimGlobals = rg
    ns = {
        'ReclaimGlobals': rg,
    }
    # _streetActUnlocked does `from toontown.reclaim import ReclaimGlobals`.
    sys.modules['toontown.reclaim'] = reclaim_pkg
    exec(compile(mod, BREADCRUMB_REL, 'exec'), ns)  # noqa: S102 — test harness
    return ns


class HubBreadcrumbActUnlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.camp = _load_reclaim_and_campaign()
        cls.helpers = _extract_breadcrumb_unlock_helpers()
        cls.src = _read(BREADCRUMB_REL)
        cls.play_src = _read(PLAY_ENTRY_REL)
        cls.director_src = _read(DIRECTOR_REL)

    def setUp(self):
        self.helpers['resetClientUnlockedThrough']()

    def test_street_needs_breadcrumb_respects_act_unlock(self):
        needs = self.helpers['streetNeedsBreadcrumb']
        # Pollution-only (unlockedThrough omitted) stays backward compatible.
        self.assertTrue(needs(PUNCHLINE, {}, seedPollution=0.70, pure=0.0))
        self.assertTrue(needs(SILLY, {}, seedPollution=0.80, pure=0.0))
        # Fresh latch — only Loopy gets a full reclaim crumb.
        self.assertTrue(needs(
            LOOPY, {}, seedPollution=0.55, pure=0.0, unlockedThrough=0))
        self.assertFalse(needs(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=0))
        self.assertFalse(needs(
            SILLY, {}, seedPollution=0.80, pure=0.0, unlockedThrough=0))
        # After Loopy clear unlocks Punchline.
        self.assertTrue(needs(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=1))
        self.assertFalse(needs(
            SILLY, {}, seedPollution=0.80, pure=0.0, unlockedThrough=1))
        # After Punchline clear unlocks Silly.
        self.assertTrue(needs(
            SILLY, {}, seedPollution=0.80, pure=0.0, unlockedThrough=2))
        # Clean streets never need a full crumb even when unlocked.
        self.assertFalse(needs(
            PUNCHLINE, {PUNCHLINE: 0.0}, seedPollution=0.70, pure=0.0,
            unlockedThrough=1))

    def test_street_breadcrumb_dimmed_for_locked_polluted(self):
        dimmed = self.helpers['streetBreadcrumbDimmed']
        # Locked + seed-polluted → dim cue (explore visible, reclaim muted).
        self.assertTrue(dimmed(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=0))
        self.assertTrue(dimmed(
            SILLY, {}, seedPollution=0.80, pure=0.0, unlockedThrough=0))
        self.assertTrue(dimmed(
            SILLY, {}, seedPollution=0.80, pure=0.0, unlockedThrough=1))
        # Loopy (act 0) is never dim-locked.
        self.assertFalse(dimmed(
            LOOPY, {}, seedPollution=0.55, pure=0.0, unlockedThrough=0))
        # Unlocked + polluted → full crumb path, not dim.
        self.assertFalse(dimmed(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=1))
        # Clean → neither full nor dim.
        self.assertFalse(dimmed(
            PUNCHLINE, {PUNCHLINE: 0.0}, seedPollution=0.70, pure=0.0,
            unlockedThrough=0))

    def test_client_unlock_latch_raises_only(self):
        get_u = self.helpers['getClientUnlockedThrough']
        set_u = self.helpers['setClientUnlockedThrough']
        self.assertEqual(get_u(), 0)
        self.assertEqual(set_u(1), 1)
        self.assertEqual(get_u(), 1)
        # Never lower (reclaim another street / stale event).
        self.assertEqual(set_u(0), 1)
        self.assertEqual(set_u(2), 2)
        self.assertEqual(get_u(), 2)

    def test_ast_wiring_accept_and_dim_path(self):
        crumb_tree = ast.parse(self.src, filename=BREADCRUMB_REL)
        names = {
            n.name for n in crumb_tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        for expected in (
                'streetNeedsBreadcrumb',
                'streetBreadcrumbDimmed',
                'getClientUnlockedThrough',
                'setClientUnlockedThrough',
                'noteCampaignActUnlocked',
                'resetClientUnlockedThrough'):
            self.assertIn(expected, names, msg='missing %s' % expected)

        # Breadcrumb client accepts campaignActUnlocked.
        self.assertIn("self.accept('campaignActUnlocked'", self.src)
        self.assertIn('_onCampaignActUnlocked', self.src)
        self.assertIn("mode == 'dim'", self.src)
        self.assertIn('_MARKER_SCALE_DIM', self.src)
        self.assertIn('_TEXT_FG_DIM', self.src)
        # refresh passes unlockedThrough into streetNeedsBreadcrumb.
        self.assertIn('unlockedThrough=unlocked', self.src)
        self.assertIn('streetBreadcrumbDimmed', self.src)
        # Login sync rehydrates unlock latch (dim → full after relog).
        self.assertIn('_onCampaignProgressSync', self.src)
        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', self.src)
        crumb_sync_idx = self.src.find('def _onCampaignProgressSync')
        self.assertGreater(crumb_sync_idx, 0)
        crumb_sync = self.src[crumb_sync_idx:crumb_sync_idx + 700]
        self.assertIn('setClientUnlockedThrough', crumb_sync)
        self.assertIn('noteCampaignActUnlocked', crumb_sync)
        self.assertIn('unlockedThrough', crumb_sync)

        # PlayEntry thin accept + purity mirror (AI messenger is process-local).
        self.assertIn("self.accept('campaignActUnlocked'", self.play_src)
        self.assertIn('_onCampaignActUnlocked', self.play_src)
        self.assertIn('_mirrorCampaignActUnlocked', self.play_src)
        self.assertIn('noteCampaignActUnlocked', self.play_src)
        # Progress sync raises crumb unlock latch (not tip-only).
        play_sync_idx = self.play_src.find('def _onCampaignProgressSync')
        self.assertGreater(play_sync_idx, 0)
        play_sync_next = self.play_src.find('\n    def ', play_sync_idx + 1)
        play_sync = self.play_src[
            play_sync_idx:(
                play_sync_next if play_sync_next > 0
                else play_sync_idx + 2400)]
        self.assertIn('noteCampaignActUnlocked', play_sync)
        self.assertIn('CorruptStreetBreadcrumb', play_sync)
        self.assertIn("mirror.get('unlockedThrough'", play_sync)
        # Purity mirror rebroadcasts so breadcrumb.accept fires on client.
        mirror_idx = self.play_src.find('def _mirrorCampaignActUnlocked')
        self.assertGreater(mirror_idx, 0)
        mirror_snip = self.play_src[mirror_idx:mirror_idx + 900]
        self.assertIn('messenger.send', mirror_snip)
        self.assertIn('campaignActUnlocked', mirror_snip)
        # Soft assert: purity path mirrors unlock before next-street tip latch.
        purity_idx = self.play_src.find('def _onPurity')
        self.assertGreater(purity_idx, 0)
        purity_snip = self.play_src[purity_idx:purity_idx + 1800]
        mirror_pos = purity_snip.find('_mirrorCampaignActUnlocked')
        self.assertGreater(mirror_pos, 0)
        # Finale returns before mirror (no post-finale act unlock).
        finale_return = purity_snip.find('return', 0, mirror_pos)
        self.assertGreater(finale_return, 0)

        # AI still sends (no rewrite required for this PR).
        self.assertIn("'campaignActUnlocked'", self.director_src)
        self.assertIn('messenger.send', self.director_src)

        # No KH branding in the new unlock/dim helpers (PlayEntry already
        # mentions "no keyblade" in pre-existing stretch-punch comments).
        src_l = self.src.lower()
        for banned in ('keyblade', 'kingdom hearts'):
            self.assertNotIn(banned, src_l)
        unlock_snip = self.play_src[
            self.play_src.find('def _onCampaignActUnlocked'):
            self.play_src.find('def _onReclaimStart')]
        self.assertNotIn('keyblade', unlock_snip.lower())
        self.assertNotIn('kingdom hearts', unlock_snip.lower())


if __name__ == '__main__':
    unittest.main()
