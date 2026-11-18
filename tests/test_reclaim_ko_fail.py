#!/usr/bin/env python3
"""Headless / AST tests: reclaim fails on player knockout → contested.

Gap scan #5: explore→fight→reclaim lacked an authored fail state; only
manual bail marked contested. Corrupt hit takeDamage must notify the
reclaim director, which announces fail then contested-bail like ~stopreclaim.

Run from repo root:
  python3 tests/test_reclaim_ko_fail.py
  python3 -m unittest tests.test_reclaim_ko_fail -v
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


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            break
    return names


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_reclaim():
    """Stub ToontownGlobals, then load CorruptionGlobals + ReclaimGlobals."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = 2000
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
    return rg, cg


class ReclaimKoFailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rg, cls.cg = _load_panda_free_reclaim()

    def test_fail_banner_copy_no_keyblade(self):
        rg = self.rg
        self.assertTrue(hasattr(rg, 'BANNER_FAILED'))
        self.assertTrue(hasattr(rg, 'BANNER_FAILED_SUB'))
        title = str(rg.BANNER_FAILED).lower()
        sub = str(rg.BANNER_FAILED_SUB).lower()
        self.assertIn('fail', title)
        self.assertIn('knocked out', sub)
        self.assertIn('ink', sub)
        self.assertIn('oswald', sub)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, title)
            self.assertNotIn(banned, sub)
        self.assertGreater(float(rg.BANNER_FAILED_HOLD_SEC), 0.0)

    def test_director_ai_ko_fail_hooks(self):
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirectorAI.py')
        methods = _class_method_names(tree, 'DistributedReclaimDirectorAI')
        self.assertIn('failStreetOnKnockout', methods)
        self.assertIn('__deferredKnockoutFail', methods)
        src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('def failStreetOnKnockout', src)
        self.assertIn('def __deferredKnockoutFail', src)
        self.assertIn('announceReclaimFailed', src)
        self.assertIn('markStreetContested', src)
        self.assertIn('_koFailPending', src)
        # Fail path announces then stops (contested), same as bail.
        fail_idx = src.find('def failStreetOnKnockout')
        stop_idx = src.find('def stop(self):')
        self.assertGreater(fail_idx, 0)
        self.assertGreater(stop_idx, fail_idx)
        fail_snip = src[fail_idx:stop_idx]
        self.assertIn('announceReclaimFailed', fail_snip)
        self.assertIn('STATE_ACTIVE', fail_snip)
        self.assertIn('__deferredKnockoutFail', fail_snip)
        deferred_idx = src.find('def __deferredKnockoutFail')
        deferred_snip = src[deferred_idx:stop_idx]
        self.assertIn('self.stop()', deferred_snip)
        self.assertIn('requestDelete', deferred_snip)
        # Contested still only on ACTIVE stop; complete stays secured.
        complete_idx = src.find('def __complete(self):')
        self.assertGreater(complete_idx, stop_idx)
        stop_snip = src[stop_idx:complete_idx]
        self.assertIn('markStreetContested', stop_snip)
        self.assertIn('wasActive', stop_snip)
        complete_snip = src[complete_idx:complete_idx + 900]
        self.assertIn('markStreetSecured', complete_snip)
        self.assertNotIn('markStreetContested', complete_snip)

    def test_corrupt_ai_thin_ko_hook(self):
        tree = _module_ast('toontown/corruption/DistributedCorruptToonAI.py')
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        self.assertIn('__damageToonAndCheckReclaimKo', methods)
        src = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn('def __damageToonAndCheckReclaimKo', src)
        self.assertIn('failStreetOnKnockout', src)
        self.assertIn('reclaimDirectors', src)
        # All corrupt hit paths route through the KO helper (not raw takeDamage).
        for needle in (
                '__damageToonAndCheckReclaimKo',
                "context='brute spit'",
                "context='gag_lob'",
                "context='gagster linger'",
                "context='rain'",
                "context='smack'",
                "context='stain_burst'",
        ):
            self.assertIn(needle, src, msg='missing KO damage path: %s' % needle)
        # takeDamage only inside the KO helper — hit resolves call the helper.
        helper_idx = src.find('def __damageToonAndCheckReclaimKo')
        self.assertGreater(helper_idx, 0)
        after_helper = src[helper_idx:]
        next_def = after_helper.find('\n    def ', 1)
        self.assertGreater(next_def, 0)
        helper_body = after_helper[:next_def]
        rest = after_helper[next_def:]
        self.assertIn('target.takeDamage(', helper_body)
        self.assertNotIn('target.takeDamage(', rest)
        self.assertIn('__damageToonAndCheckReclaimKo(', rest)

    def test_client_fail_announce_hooks(self):
        tree = _module_ast('toontown/reclaim/DistributedReclaimDirector.py')
        methods = _class_method_names(tree, 'DistributedReclaimDirector')
        self.assertIn('announceReclaimFailed', methods)
        src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('BANNER_FAILED', src)
        self.assertIn('__showFailBanner', src)
        self.assertIn('_failBannerNP', src)
        # Fail plates survive IDLE clearHud (dedicated nodes).
        clear_idx = src.find('def __clearHud')
        self.assertGreater(clear_idx, 0)
        clear_snip = src[clear_idx:clear_idx + 500]
        self.assertNotIn('__hideFailBanner', clear_snip)
        self.assertNotIn('_failBannerNP', clear_snip)

    def test_dc_announces_reclaim_failed(self):
        dc = _read('etc/toon.dc')
        self.assertIn('announceReclaimFailed() broadcast;', dc)
        # Soft-gate / hydrate R surface must remain (no regression of #317/#320).
        ai = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('startStreetPackForToon', ai)
        self.assertIn('streetPackUnlocked', ai)
        self.assertIn('_hydrateFromToon', ai)

    def test_docs_mention_ko_fail(self):
        md = _read('toontown/corruption/RECLAIM.md')
        lower = md.lower()
        self.assertIn('knockout', lower)
        self.assertIn('failstreetonknockout', lower)
        self.assertIn('announcereclaimfailed', lower)
        # Fail step copy must stay rubber-hose (doc may say "no keyblades" elsewhere).
        step7 = lower.split('7. player knockout', 1)[-1].split('\n## ', 1)[0]
        self.assertIn('contested', step7)
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, step7)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReclaimKoFailTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
