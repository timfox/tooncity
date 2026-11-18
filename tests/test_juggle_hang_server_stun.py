#!/usr/bin/env python3
"""Headless/AST tests for server air-juggle hang stun.

Ensures launch beats arm CorruptToonAI chase/attack pause so cancel→slam is
not client-only under multi-enemy pressure. No Panda3D required.

Run from repo root:
  python3 tests/test_juggle_hang_server_stun.py
  python3 -m unittest tests.test_juggle_hang_server_stun -v
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


def _load_juggle_hang_stun_helpers():
    """Load HackSlashConfig stun helpers without importing MeleeCombat."""
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


def _class_method_names(tree: ast.AST, class_name: str) -> set:
    methods = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    methods.add(child.name)
    return methods


class JuggleHangServerStunTest(unittest.TestCase):
    """Config helpers + AI/client/DC wiring for hang stun."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = _load_juggle_hang_stun_helpers()

    def test_stun_duration_covers_cancel_window(self):
        mid_idx = self.cfg.LAUNCH_HIT_INDEX
        mid = self.cfg.juggleHangStunSec(mid_idx)
        hitstop = float(self.cfg.HITSTOP_SEC[mid_idx])
        up = float(self.cfg.LAUNCH_UP_SEC[mid_idx])
        hang = float(self.cfg.LAUNCH_HANG_SEC[mid_idx])
        pad = float(self.cfg.JUGGLE_HANG_STUN_PAD_SEC)
        cancel_end = (
            float(self.cfg.JUGGLE_CANCEL_START_SEC)
            + float(self.cfg.JUGGLE_CANCEL_WINDOW_SEC))
        expected = hitstop + max(up + hang + pad, cancel_end)
        self.assertAlmostEqual(mid, expected, places=4)
        # Finisher: rise+hang+pad (+ hitstop), no cancel-window floor.
        fin_idx = self.cfg.COMBO_LENGTH - 1
        fin = self.cfg.juggleHangStunSec(fin_idx)
        fin_expected = (
            float(self.cfg.HITSTOP_SEC[fin_idx])
            + float(self.cfg.LAUNCH_UP_SEC[fin_idx])
            + float(self.cfg.LAUNCH_HANG_SEC[fin_idx])
            + pad)
        self.assertAlmostEqual(fin, fin_expected, places=4)

    def test_no_kh_branding_in_stun_copy(self):
        src = _read('toontown/hackslash/HackSlashConfig.py')
        # Stun block comments near JUGGLE_HANG_STUN — keep rubber-hose only.
        block = src.split('JUGGLE_HANG_STUN_ENABLED', 1)[1][:900].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, block)
        hint = str(self.cfg.DEMO_HINT).lower()
        self.assertIn('juggle hang stun', hint)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, hint)

    def test_ai_ast_has_stun_gate(self):
        rel = 'toontown/corruption/DistributedCorruptToonAI.py'
        src = _read(rel)
        tree = _module_ast(rel)
        methods = _class_method_names(tree, 'DistributedCorruptToonAI')
        for name in (
                '__applyJuggleHangStun',
                '__cancelAttackForJuggleHang',
                'isJuggleHangStunned',
                'requestHackSlashHit'):
            self.assertIn(name, methods, msg='AI missing %s' % name)
        self.assertIn('_juggleHangStunUntil', src)
        self.assertIn('isJuggleHangStunned', src)
        self.assertIn('juggleHangStunSec', src)
        self.assertIn('JUGGLE_HANG_STUN_ENABLED', src)
        self.assertIn('HackSlashConfig', src)
        # __aiTick must gate on stun before chase/attack.
        ai_tick = None
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and (
                    node.name == 'DistributedCorruptToonAI'):
                for child in node.body:
                    if (isinstance(child, ast.FunctionDef)
                            and child.name == '__aiTick'):
                        ai_tick = child
                        break
        self.assertIsNotNone(ai_tick)
        tick_src = ast.get_source_segment(src, ai_tick) or ''
        self.assertIn('isJuggleHangStunned', tick_src)
        # requestHackSlashHit takes hitIndex.
        req = None
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and (
                    node.name == 'DistributedCorruptToonAI'):
                for child in node.body:
                    if (isinstance(child, ast.FunctionDef)
                            and child.name == 'requestHackSlashHit'):
                        req = child
                        break
        self.assertIsNotNone(req)
        arg_names = [a.arg for a in req.args.args]
        self.assertIn('hitIndex', arg_names)
        self.assertIn('__applyJuggleHangStun', src)

    def test_client_and_dc_pass_hit_index(self):
        client = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn("sendUpdate('requestHackSlashHit', [amount, idx])", client)
        dc = _read('etc/toon.dc')
        self.assertIn(
            'requestHackSlashHit(uint16, uint8)',
            dc)
        self.assertIn('juggle-hang stun', dc.lower().replace('_', '-'))
        init_src = _read('toontown/hackslash/__init__.py')
        for name in (
                'juggleHangStunSec',
                'isJuggleHangStunHit',
                'isJuggleHangStunned'):
            self.assertIn(name, init_src)
        magic = _read('toontown/hackslash/MagicWords.py')
        self.assertIn('server stun', magic.lower())
        for banned in ('keyblade', 'kingdom hearts'):
            self.assertNotIn(banned, magic.lower())


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        JuggleHangServerStunTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
