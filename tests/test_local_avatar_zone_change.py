#!/usr/bin/env python3
"""AST/wiring tests: localAvatarZoneChange / localToonLeftZone send sites.

Gap: PlayEntry, PollutionManager, and reclaim entry FX accept these messengers,
but nothing historically sent them — tunnel hub→street hops never re-armed tips,
auto-campaign, or pollution presentation.

Asserts Place helpers + Street/Playground enter/exit send sites, and that key
accepts still match. Panda-free.

Run from repo root:
  python3 tests/test_local_avatar_zone_change.py
  python3 -m unittest tests.test_local_avatar_zone_change -v
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PLACE_REL = 'toontown/hood/Place.py'
STREET_REL = 'toontown/town/Street.py'
PLAYGROUND_REL = 'toontown/safezone/Playground.py'
PLAY_ENTRY_REL = 'toontown/campaign/PlayEntry.py'
POLLUTION_REL = 'toontown/corruption/PollutionManager.py'
ENTRY_SHIMMER_REL = 'toontown/reclaim/EntryCreamShimmerFx.py'
ENTRY_WASH_REL = 'toontown/reclaim/EntryCreamWashPulseFx.py'

ZONE_CHANGE = 'localAvatarZoneChange'
LEFT_ZONE = 'localToonLeftZone'


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in getattr(tree, 'body', []):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
    raise AssertionError('class %r not found' % class_name)


def _calls_named(tree: ast.AST, class_name: str, method_name: str, call_name: str) -> bool:
    """True if class.method contains a Call to call_name (attr or bare)."""
    for node in getattr(tree, 'body', []):
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for item in node.body:
            if not (
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == method_name):
                continue
            for sub in ast.walk(item):
                if not isinstance(sub, ast.Call):
                    continue
                func = sub.func
                if isinstance(func, ast.Name) and func.id == call_name:
                    return True
                if isinstance(func, ast.Attribute) and func.attr == call_name:
                    return True
            return False
    raise AssertionError('%s.%s not found' % (class_name, method_name))


def _messenger_send_events(tree: ast.AST, class_name: str, method_name: str) -> set[str]:
    """Collect string event names passed to messenger.send in a method."""
    events: set[str] = set()
    for node in getattr(tree, 'body', []):
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for item in node.body:
            if not (
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == method_name):
                continue
            for sub in ast.walk(item):
                if not isinstance(sub, ast.Call):
                    continue
                func = sub.func
                is_send = (
                    (isinstance(func, ast.Attribute) and func.attr == 'send')
                    or (isinstance(func, ast.Name) and func.id == 'send'))
                if not is_send:
                    continue
                if not sub.args:
                    continue
                arg0 = sub.args[0]
                if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                    events.add(arg0.value)
            return events
    raise AssertionError('%s.%s not found' % (class_name, method_name))


def _accept_events(tree: ast.AST, class_name: str) -> set[str]:
    """Collect string event names in self.accept(...) anywhere in the class."""
    events: set[str] = set()
    for node in getattr(tree, 'body', []):
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            func = sub.func
            is_accept = (
                (isinstance(func, ast.Attribute) and func.attr == 'accept')
                or (isinstance(func, ast.Name) and func.id == 'accept'))
            if not is_accept:
                continue
            if not sub.args:
                continue
            arg0 = sub.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                events.add(arg0.value)
        return events
    raise AssertionError('class %r not found' % class_name)


class LocalAvatarZoneChangeTest(unittest.TestCase):
    """Send sites exist; key accepts still match."""

    def test_place_helpers_send_zone_events(self):
        tree = _module_ast(PLACE_REL)
        methods = _class_method_names(tree, 'Place')
        self.assertIn('announceLocalAvatarZoneChange', methods)
        self.assertIn('announceLocalToonLeftZone', methods)

        change_events = _messenger_send_events(
            tree, 'Place', 'announceLocalAvatarZoneChange')
        self.assertIn(ZONE_CHANGE, change_events)
        self.assertNotIn(LEFT_ZONE, change_events)

        left_events = _messenger_send_events(
            tree, 'Place', 'announceLocalToonLeftZone')
        self.assertIn(LEFT_ZONE, left_events)
        self.assertNotIn(ZONE_CHANGE, left_events)

        # Branch normalize so ACTS / STREET_PACKS keys match floor ids.
        place_src = _read(PLACE_REL)
        announce_idx = place_src.find('def announceLocalAvatarZoneChange')
        self.assertGreater(announce_idx, 0)
        snip = place_src[announce_idx:announce_idx + 900]
        self.assertIn('getBranchZone', snip)

    def test_street_enter_exit_announce(self):
        tree = _module_ast(STREET_REL)
        self.assertTrue(
            _calls_named(tree, 'Street', 'enter', 'announceLocalAvatarZoneChange'),
            msg='Street.enter must announceLocalAvatarZoneChange')
        self.assertTrue(
            _calls_named(tree, 'Street', 'exit', 'announceLocalToonLeftZone'),
            msg='Street.exit must announceLocalToonLeftZone')

    def test_playground_enter_exit_announce(self):
        tree = _module_ast(PLAYGROUND_REL)
        self.assertTrue(
            _calls_named(
                tree, 'Playground', 'enter', 'announceLocalAvatarZoneChange'),
            msg='Playground.enter must announceLocalAvatarZoneChange')
        self.assertTrue(
            _calls_named(
                tree, 'Playground', 'exit', 'announceLocalToonLeftZone'),
            msg='Playground.exit must announceLocalToonLeftZone')

    def test_key_accepts_still_match(self):
        play_accepts = _accept_events(_module_ast(PLAY_ENTRY_REL), 'PlayEntryClient')
        self.assertIn(ZONE_CHANGE, play_accepts)

        pollution_accepts = _accept_events(
            _module_ast(POLLUTION_REL), 'PollutionManager')
        self.assertIn(ZONE_CHANGE, pollution_accepts)
        self.assertIn(LEFT_ZONE, pollution_accepts)

        shimmer_accepts = _accept_events(
            _module_ast(ENTRY_SHIMMER_REL), 'EntryCreamShimmerFxClient')
        self.assertIn(ZONE_CHANGE, shimmer_accepts)
        self.assertIn(LEFT_ZONE, shimmer_accepts)

        wash_accepts = _accept_events(
            _module_ast(ENTRY_WASH_REL), 'EntryCreamWashPulseFxClient')
        self.assertIn(ZONE_CHANGE, wash_accepts)
        self.assertIn(LEFT_ZONE, wash_accepts)

    def test_consumers_branch_normalize_zone(self):
        """Thin consumer fix: boot/floor ids still match ACTS / STREET_PACKS."""
        play_src = _read(PLAY_ENTRY_REL)
        on_zone_idx = play_src.find('def _onZoneChange')
        self.assertGreater(on_zone_idx, 0)
        play_snip = play_src[on_zone_idx:on_zone_idx + 500]
        self.assertIn('getBranchZone', play_snip)

        pollution_src = _read(POLLUTION_REL)
        handle_idx = pollution_src.find('def __handleZoneChange')
        self.assertGreater(handle_idx, 0)
        pol_snip = pollution_src[handle_idx:handle_idx + 500]
        self.assertIn('getBranchZone', pol_snip)

    def test_no_orphan_accept_without_send(self):
        """Repo must send both events at least once (Place helpers)."""
        place_src = _read(PLACE_REL)
        self.assertIn("messenger.send('%s'" % ZONE_CHANGE, place_src)
        self.assertIn("messenger.send('%s'" % LEFT_ZONE, place_src)
        # Street + hub call sites — not cream-constant-only.
        street_src = _read(STREET_REL)
        playground_src = _read(PLAYGROUND_REL)
        self.assertIn('announceLocalAvatarZoneChange', street_src)
        self.assertIn('announceLocalToonLeftZone', street_src)
        self.assertIn('announceLocalAvatarZoneChange', playground_src)
        self.assertIn('announceLocalToonLeftZone', playground_src)


if __name__ == '__main__':
    unittest.main()
