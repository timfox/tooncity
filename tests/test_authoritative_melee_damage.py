#!/usr/bin/env python3
"""Headless tests: authoritative server melee damage from hitIndex.

Locks HackSlashConfig.meleeDamageFromHitIndex (COMBO_DAMAGE + optional
counterFlags) and CorruptToonAI requestHackSlashHit wiring so client-sent
amounts are not trusted. No Panda3D required.

Run from repo root:
  python3 tests/test_authoritative_melee_damage.py
  python3 -m unittest tests.test_authoritative_melee_damage -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_config():
    """Load HackSlashConfig without importing MeleeCombat / Panda3D."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in ('toontown', 'toontown.hackslash'):
        _ensure_pkg(pkg)

    cfg_path = REPO_ROOT / 'toontown' / 'hackslash' / 'HackSlashConfig.py'
    cfg_spec = importlib.util.spec_from_file_location(
        'toontown.hackslash.HackSlashConfig', cfg_path)
    cfg = importlib.util.module_from_spec(cfg_spec)
    assert cfg_spec.loader is not None
    sys.modules['toontown.hackslash.HackSlashConfig'] = cfg
    cfg_spec.loader.exec_module(cfg)
    sys.modules['toontown.hackslash'].HackSlashConfig = cfg
    return cfg


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


class AuthoritativeMeleeDamageTest(unittest.TestCase):
    """COMBO_DAMAGE table helper + AI/client/DC wiring."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_config()

    def test_table_lookup_matches_combo_damage(self):
        fn = self.cfg.meleeDamageFromHitIndex
        table = self.cfg.COMBO_DAMAGE
        self.assertEqual(len(table), self.cfg.COMBO_LENGTH)
        for idx, expected in enumerate(table):
            self.assertEqual(fn(idx), int(expected))
        # Out-of-range hitIndex clamps to last entry (same as client swing).
        self.assertEqual(fn(99), int(table[-1]))
        self.assertEqual(fn(-1), int(table[0]))

    def test_counter_flag_applies_known_opener_mult(self):
        fn = self.cfg.meleeDamageFromHitIndex
        base = int(self.cfg.COMBO_DAMAGE[0])
        flag = int(self.cfg.MELEE_COUNTER_FLAG_PERFECT_DODGE)
        bumped = fn(0, flag)
        self.assertGreater(bumped, base)
        self.assertEqual(
            bumped,
            self.cfg.perfectDodgeCounterOpenerDamage(base))
        # Unknown / empty flags stay on the baseline table entry.
        self.assertEqual(fn(0, 0), base)
        self.assertEqual(fn(0, self.cfg.MELEE_COUNTER_FLAG_NONE), base)
        # Mid / finisher with counter flag still scale that hit's table entry.
        mid = int(self.cfg.COMBO_DAMAGE[1])
        self.assertEqual(
            fn(1, flag),
            self.cfg.perfectDodgeCounterOpenerDamage(mid))

    def test_spoofed_client_amount_cannot_inflate_helper(self):
        """Helper has no damage= arg — only hitIndex / flags / table."""
        fn = self.cfg.meleeDamageFromHitIndex
        # Explicit alternate table still clamps through MELEE_DAMAGE_MAX.
        huge = (999, 999, 999)
        capped = fn(0, 0, damageTable=huge)
        self.assertEqual(capped, int(self.cfg.MELEE_DAMAGE_MAX))
        self.assertLessEqual(capped, 80)

    def test_no_kh_branding_in_damage_helper_copy(self):
        src = _read('toontown/hackslash/HackSlashConfig.py')
        block = src.split('def meleeDamageFromHitIndex', 1)[1][:700].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, block)
        self.assertIn('rubber-hose', block)

    def test_ai_derives_damage_ignores_client_amount(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        src = _read(rel)
        tree = _module_ast(rel)
        req = _class_method(tree, 'DistributedCorruptToonAI', 'requestHackSlashHit')
        self.assertIsNotNone(req)
        arg_names = [a.arg for a in req.args.args]
        self.assertIn('hitIndex', arg_names)
        self.assertIn('counterFlags', arg_names)
        # Legacy client-trusted damage param is gone.
        self.assertNotIn('damage', arg_names)
        req_src = ast.get_source_segment(src, req) or ''
        self.assertIn('meleeDamageFromHitIndex', req_src)
        self.assertNotIn('min(80', req_src)
        self.assertIn('HackSlashConfig.meleeDamageFromHitIndex', src)
        # takeHackSlashDamage still receives the derived amount.
        self.assertIn('takeHackSlashDamage(amount', req_src)

    def test_client_and_dc_pass_hit_index_and_flags(self):
        client = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn("sendUpdate('requestHackSlashHit', [idx, flags])", client)
        self.assertIn('counterFlags=0', client)
        self.assertIn('local juice', client.lower())
        dc = _read('etc/toon.dc')
        self.assertIn('requestHackSlashHit(uint8, uint8)', dc)
        self.assertIn('counterFlags', dc)
        self.assertNotIn('requestHackSlashHit(uint16, uint8)', dc)
        melee = _read('toontown/hackslash/MeleeCombat.py')
        self.assertIn('_pendingCounterFlags', melee)
        self.assertIn('MELEE_COUNTER_FLAG_PERFECT_DODGE', melee)
        init_src = _read('toontown/hackslash/__init__.py')
        self.assertIn('meleeDamageFromHitIndex', init_src)
        target = _read('toontown/corruption/HackSlashTarget.py')
        self.assertIn('meleeDamageFromHitIndex', target)
        self.assertIn('counterFlags', target)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        AuthoritativeMeleeDamageTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
