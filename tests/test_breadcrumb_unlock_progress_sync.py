#!/usr/bin/env python3
"""Headless tests: rehydrate hub breadcrumb unlock from campaignProgressSync.

Soft-gate R + tip/soft-next already hydrate from AI progress after relog,
but hub crumbs stayed dim until a live campaignActUnlocked. PlayEntry
and CorruptStreetBreadcrumb must raise the client unlockedThrough latch
on campaignProgressSync so Punchline/Silly undim without waiting.

No cream deepen / no KH.

Run from repo root:
  python3 tests/test_breadcrumb_unlock_progress_sync.py
  python3 -m unittest tests.test_breadcrumb_unlock_progress_sync -v
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
    path = REPO_ROOT / BREADCRUMB_REL
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src, filename=BREADCRUMB_REL)

    keep_assign = {'_clientUnlockedThrough'}
    keep_funcs = {
        'getClientUnlockedThrough',
        'setClientUnlockedThrough',
        'resetClientUnlockedThrough',
        'streetNeedsBreadcrumb',
        'streetBreadcrumbDimmed',
        '_streetActUnlocked',
        '_streetLooksPolluted',
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
    rg, _camp = _load_reclaim_and_campaign()
    reclaim_pkg = types.ModuleType('toontown.reclaim')
    reclaim_pkg.ReclaimGlobals = rg
    sys.modules['toontown.reclaim'] = reclaim_pkg
    ns = {'ReclaimGlobals': rg}
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


class BreadcrumbUnlockProgressSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.camp = _load_reclaim_and_campaign()
        cls.helpers = _extract_breadcrumb_unlock_helpers()
        cls.crumb_src = _read(BREADCRUMB_REL)
        cls.play_src = _read(PLAY_ENTRY_REL)

    def setUp(self):
        self.helpers['resetClientUnlockedThrough']()

    def test_sync_raise_undims_punchline_and_silly(self):
        """Mid-campaign unlockedThrough makes full crumbs available after sync."""
        get_u = self.helpers['getClientUnlockedThrough']
        set_u = self.helpers['setClientUnlockedThrough']
        needs = self.helpers['streetNeedsBreadcrumb']
        dimmed = self.helpers['streetBreadcrumbDimmed']

        self.assertEqual(get_u(), 0)
        self.assertTrue(dimmed(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=0))
        self.assertFalse(needs(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=0))

        # Simulate campaignProgressSync raising the session latch (PlayEntry
        # / breadcrumb _onCampaignProgressSync → setClientUnlockedThrough).
        self.assertEqual(set_u(1), 1)
        unlocked = get_u()
        self.assertEqual(unlocked, 1)
        self.assertTrue(needs(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0,
            unlockedThrough=unlocked))
        self.assertFalse(dimmed(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0,
            unlockedThrough=unlocked))
        # Silly still locked at unlockedThrough=1.
        self.assertTrue(dimmed(
            SILLY, {}, seedPollution=0.80, pure=0.0,
            unlockedThrough=unlocked))

        self.assertEqual(set_u(2), 2)
        unlocked = get_u()
        self.assertTrue(needs(
            SILLY, {}, seedPollution=0.80, pure=0.0,
            unlockedThrough=unlocked))
        self.assertFalse(dimmed(
            SILLY, {}, seedPollution=0.80, pure=0.0,
            unlockedThrough=unlocked))

    def test_playentry_sync_raises_crumb_latch(self):
        src = self.play_src
        self.assertIn('_onCampaignProgressSync', src)
        sync_idx = src.find('def _onCampaignProgressSync')
        self.assertGreater(sync_idx, 0)
        # Bound by next PlayEntry method so tip-only sync cannot pass.
        next_idx = src.find('\n    def ', sync_idx + 1)
        sync_win = src[sync_idx:next_idx if next_idx > 0 else sync_idx + 1800]
        self.assertIn('noteCampaignActUnlocked', sync_win)
        self.assertIn('CorruptStreetBreadcrumb', sync_win)
        self.assertIn("mirror.get('unlockedThrough'", sync_win)
        # Preserve tip / soft-next / victory latches alongside unlock.
        self.assertIn('_victoryEpilogue', sync_win)
        self.assertIn('_chasePending', sync_win)
        self.assertIn('softNextStreet', sync_win)
        # Still accepts live campaignActUnlocked (#332).
        self.assertIn("accept('campaignActUnlocked'", src)

    def test_breadcrumb_accepts_progress_sync(self):
        tree = ast.parse(self.crumb_src, filename=BREADCRUMB_REL)
        methods = _class_method_names(tree, 'CorruptStreetBreadcrumb')
        self.assertIn('_onCampaignProgressSync', methods)
        self.assertIn('_onCampaignActUnlocked', methods)

        accepts = _accept_events(tree, 'CorruptStreetBreadcrumb')
        self.assertIn('campaignActUnlocked', accepts)
        self.assertTrue(
            'syncMsg' in accepts or 'campaignProgressSync' in accepts,
            msg='CorruptStreetBreadcrumb must accept campaignProgressSync')

        sync_idx = self.crumb_src.find('def _onCampaignProgressSync')
        self.assertGreater(sync_idx, 0)
        next_idx = self.crumb_src.find('\n    def ', sync_idx + 1)
        sync_win = self.crumb_src[
            sync_idx:next_idx if next_idx > 0 else sync_idx + 900]
        # Unlock + chase-pending honesty from progress fields.
        self.assertIn('noteCampaignProgressFields', sync_win)
        self.assertIn('unlockedThrough', sync_win)
        self.assertIn('chaseCleared', sync_win)
        # Arity parity with PollutionManager fan-out.
        self.assertIn('reclaimCount', sync_win)
        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', self.crumb_src)

    def test_no_kh_copy(self):
        for rel in (BREADCRUMB_REL, PLAY_ENTRY_REL):
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
