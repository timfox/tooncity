#!/usr/bin/env python3
"""Headless tests: BossHpBarHud ownership follows soft-lock target (TC-425).

After #390/#394/#399, Elite/Ambush/Overlord/Oswald all qualify as bar
subjects and soft-lock ranks them — but the singleton still flipped to
whichever living subject's setHp landed last. Soft-lock bind owns the
bar; other subjects cannot steal via sync.

Loads CorruptionGlobals with a ToontownGlobals stub — no Panda3D.
BossHpBarHud / MeleeCombat wiring is AST-checked (imports pull panda).

Run from repo root:
  python3 tests/test_boss_hp_bar_soft_lock_owner.py
  python3 -m unittest tests.test_boss_hp_bar_soft_lock_owner -v
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


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_corruption():
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
    return cg


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel))


def _class_method(tree: ast.AST, class_name: str, method_name: str):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if (isinstance(child, ast.FunctionDef)
                        and child.name == method_name):
                    return child
    return None


def _class_method_names(tree: ast.AST, class_name: str) -> set:
    names = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    names.add(child.name)
    return names


def _method_body_names(rel: str, class_name: str, method_name: str) -> set:
    tree = _module_ast(rel)
    method = _class_method(tree, class_name, method_name)
    if method is None:
        return set()
    names = set()
    for node in ast.walk(method):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def _function_body_names(rel: str, func_name: str) -> set[str]:
    tree = _module_ast(rel)
    out = set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != func_name:
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                out.add(child.id)
            elif isinstance(child, ast.Attribute):
                out.add(child.attr)
    return out


def _module_func_names(rel: str) -> set[str]:
    tree = _module_ast(rel)
    return {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


class BossHpBarSoftLockOwnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cg = _load_panda_free_corruption()

    def test_should_claim_ownership_gate(self):
        """Soft-lock bind blocks other subjects; None keeps last-writer."""
        claim = self.cg.shouldClaimBossHpBarOwnership
        # No soft-lock prefer → any living subject may claim (legacy).
        self.assertTrue(claim(101, None))
        self.assertTrue(claim(202, None))
        # Soft-lock on Elite A → only A may refresh/claim.
        self.assertTrue(claim(101, 101))
        self.assertFalse(claim(202, 101))
        self.assertFalse(claim(303, 101))
        # Soft-lock on Overlord → Elite cannot steal.
        self.assertTrue(claim(9001, 9001))
        self.assertFalse(claim(101, 9001))
        # Bad sync id never claims while soft-lock is bound.
        self.assertFalse(claim(None, 101))
        # String/int doId parity (client doIds are ints; tolerate either).
        self.assertTrue(claim('55', 55))
        self.assertFalse(claim('56', 55))

    def test_hud_bind_and_sync_gate_wiring(self):
        rel = 'toontown/reclaim/BossHpBarHud.py'
        names = _module_func_names(rel)
        for expected in (
                'bindSoftLockTarget',
                'syncFromCorruptToon',
                'getSoftLockBossHpBarDoId',
                'getBossHpBarOwnerDoId',
                'releaseCorruptToon',
                'hideBossHpBar',
                'destroyBossHpBar',
        ):
            self.assertIn(expected, names)

        bind_names = _function_body_names(rel, 'bindSoftLockTarget')
        self.assertIn('isBossOrChaseHpBarSubject', bind_names)
        self.assertIn('syncFromCorruptToon', bind_names)
        self.assertIn('_softLockDoId', bind_names)

        sync_names = _function_body_names(rel, 'syncFromCorruptToon')
        self.assertIn('shouldClaimBossHpBarOwnership', sync_names)
        self.assertIn('_softLockDoId', sync_names)
        self.assertIn('isBossOrChaseHpBarSubject', sync_names)
        # Still never glue reclaim-director street phase onto pack adds.
        self.assertNotIn('reclaimDirector', sync_names)

        src = _read(rel)
        self.assertIn('soft-lock', src.lower())
        self.assertIn('_softLockDoId', src)
        # Bind clears prefer only on None — fodder leaves prior prefer sticky.
        bind_idx = src.index('def bindSoftLockTarget')
        bind_snip = src[bind_idx:bind_idx + 1400]
        self.assertIn('fodder', bind_snip.lower())
        self.assertIn('_softLockDoId = None', bind_snip)
        self.assertIn('syncFromCorruptToon(toon)', bind_snip)

    def test_melee_combat_binds_on_tick_and_cycle(self):
        rel = 'toontown/hackslash/MeleeCombat.py'
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'MeleeCombatController')
        self.assertIn('_bindBossHpBarToSoftLock', methods)

        tick_names = _method_body_names(
            rel, 'MeleeCombatController', '_tick')
        self.assertIn(
            '_bindBossHpBarToSoftLock', tick_names,
            msg='sticky acquire must bind HP bar to soft-lock target')

        cycle_names = _method_body_names(
            rel, 'MeleeCombatController', '_cycleSoftLockTarget')
        self.assertIn(
            '_bindBossHpBarToSoftLock', cycle_names,
            msg='Tab/` cycle must bind HP bar to soft-lock target')

        bind_src = ast.get_source_segment(
            _read(rel),
            _class_method(
                tree, 'MeleeCombatController',
                '_bindBossHpBarToSoftLock')) or ''
        self.assertIn('bindSoftLockTarget', bind_src)
        self.assertIn('BossHpBarHud', bind_src)

    def test_globals_docs_and_exports(self):
        cg_src = _read('toontown/corruption/CorruptionGlobals.py')
        self.assertIn('def shouldClaimBossHpBarOwnership', cg_src)
        claim_idx = cg_src.index('def shouldClaimBossHpBarOwnership')
        claim_snip = cg_src[claim_idx:claim_idx + 700].lower()
        self.assertIn('soft-lock', claim_snip)
        self.assertIn('sethp', claim_snip)
        self.assertNotIn('keyblade', claim_snip)
        self.assertNotIn('kingdom hearts', claim_snip)

        reclaim = _read('toontown/corruption/RECLAIM.md').lower()
        self.assertIn('soft-lock bind', reclaim)
        self.assertIn('last `sethp`', reclaim)

    def test_no_cream_kh(self):
        for rel in (
                'toontown/reclaim/BossHpBarHud.py',
                'toontown/hackslash/MeleeCombat.py',
        ):
            src = _read(rel)
            if rel.endswith('BossHpBarHud.py'):
                low = src.lower()
                self.assertNotIn('creamwash', low)
                self.assertNotIn('creamsplash', low)
                self.assertNotIn('keyblade', low)
                self.assertNotIn('kingdom hearts', low)
            else:
                block = src.split('_bindBossHpBarToSoftLock', 1)[1][:900].lower()
                for banned in ('keyblade', 'kingdom hearts', 'sora'):
                    self.assertNotIn(banned, block)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        BossHpBarSoftLockOwnerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
