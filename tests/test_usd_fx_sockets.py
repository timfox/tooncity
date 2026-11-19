#!/usr/bin/env python3
"""Headless USD combat FX socket → CorruptionGlobals map gates (PR 6).

Socket names map to existing FX hook identifiers used by corrupt
telegraph / death (string table only). Every socket has a known
consumer key on CorruptionGlobals. No mesh-heavy FX, no Hydra.

Run from repo root:
  python3 -m unittest tests.test_usd_fx_sockets -v
  python3 tests/test_usd_fx_sockets.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from toontown.usd.fx_sockets import (  # noqa: E402
    FX_SOCKET_NOTES,
    REQUIRED_KIT_SOCKETS,
    SOCKET_CONSUMER_KEYS,
    consumer_key_for_socket,
    corruption_globals_consumer_names,
    fx_dir,
    list_fx_fixtures,
    load_fx_sockets,
    resolve_fx_fixture,
    telegraph_sockets,
    validate_fx_fixture,
    validate_fx_usda_text,
    FxSocketError,
)
from toontown.usd.character_kit import REQUIRED_FX_SOCKETS  # noqa: E402
from toontown.usd.validate import UsdValidationError  # noqa: E402

FX = REPO_ROOT / 'toontown' / 'usd' / 'fixtures' / 'fx'
FIXTURE_STEM = 'telegraph_sockets'
CORRUPTION_GLOBALS = (
    REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
)

_BANNED = (
    'keyblade',
    'kingdom hearts',
    'kingdomhearts',
    'sora',
    'heartless',
)


class TestTelegraphSocketsFixture(unittest.TestCase):
    def test_fixture_exists_ascii_clean(self):
        path = FX / f'{FIXTURE_STEM}.usda'
        self.assertTrue(path.is_file(), f'missing fixture: {path}')
        text = path.read_text(encoding='utf-8')
        self.assertTrue(text.startswith('#usda'), path.name)
        self.assertNotIn('\x00', text)
        low = text.lower()
        for token in _BANNED:
            self.assertNotIn(token, low, f'banned token in {path.name}')
        # No mesh-heavy FX markers (doc may say "no Hydra").
        self.assertNotIn('def Mesh', text)
        self.assertNotIn('.usdc', low)
        self.assertIn('no hydra', low)

    def test_resolve_and_list(self):
        self.assertEqual(fx_dir(), FX)
        self.assertIn(FIXTURE_STEM, list_fx_fixtures())
        self.assertEqual(
            resolve_fx_fixture(FIXTURE_STEM),
            FX / f'{FIXTURE_STEM}.usda',
        )
        self.assertEqual(
            resolve_fx_fixture(f'{FIXTURE_STEM}.usda'),
            FX / f'{FIXTURE_STEM}.usda',
        )


class TestSocketConsumerMap(unittest.TestCase):
    def test_kit_sockets_match_character_kit(self):
        self.assertEqual(REQUIRED_KIT_SOCKETS, REQUIRED_FX_SOCKETS)
        for socket in REQUIRED_KIT_SOCKETS:
            self.assertIn(socket, SOCKET_CONSUMER_KEYS)

    def test_every_canonical_consumer_exists_in_corruption_globals(self):
        names = corruption_globals_consumer_names(CORRUPTION_GLOBALS)
        for socket, consumer in SOCKET_CONSUMER_KEYS.items():
            self.assertIn(
                consumer,
                names,
                f'socket {socket!r} → {consumer!r} missing from '
                f'CorruptionGlobals',
            )

    def test_validate_and_load_ok(self):
        result = validate_fx_fixture(FIXTURE_STEM)
        self.assertTrue(result['ok'])
        self.assertTrue(result.get('fxOk'))
        self.assertIn('TcFxSocket', result['kinds'])

        loaded = load_fx_sockets(FIXTURE_STEM)
        self.assertEqual(loaded['name'], FIXTURE_STEM)
        self.assertFalse(loaded['meshHeavy'])
        self.assertEqual(loaded['fxSocketNotes'], FX_SOCKET_NOTES)
        self.assertEqual(
            set(loaded['requiredKitSockets']),
            set(REQUIRED_KIT_SOCKETS),
        )

        sockets = {e['socket'] for e in loaded['sockets']}
        self.assertTrue(REQUIRED_KIT_SOCKETS.issubset(sockets))
        for entry in loaded['sockets']:
            self.assertTrue(entry['consumerKey'], entry)
            self.assertEqual(
                entry['consumerKey'],
                SOCKET_CONSUMER_KEYS[entry['socket']],
                entry,
            )
            self.assertEqual(
                loaded['socketToConsumer'][entry['socket']],
                entry['consumerKey'],
            )

    def test_telegraph_sockets_convenience(self):
        a = telegraph_sockets()
        b = load_fx_sockets('telegraph_sockets')
        self.assertEqual(a['socketToConsumer'], b['socketToConsumer'])
        self.assertEqual(
            a['socketToConsumer']['telegraph'],
            'TELEGRAPH_INK_DRIP_LOOK',
        )
        self.assertEqual(
            a['socketToConsumer']['death'],
            'DEATH_POP_LOOK',
        )
        self.assertEqual(
            a['socketToConsumer']['cream'],
            'TELEGRAPH_CREAM_WARN_LOOK',
        )
        self.assertEqual(
            a['socketToConsumer']['hit'],
            'SMUDGE_INK_SPLASH_LOOK',
        )

    def test_consumer_key_for_socket(self):
        self.assertEqual(
            consumer_key_for_socket('telegraph'),
            'TELEGRAPH_INK_DRIP_LOOK',
        )
        self.assertEqual(
            consumer_key_for_socket('DEATH'),
            'DEATH_POP_LOOK',
        )
        with self.assertRaises(FxSocketError):
            consumer_key_for_socket('keyblade')


class TestFxSocketNegatives(unittest.TestCase):
    def test_missing_consumer_key_fails(self):
        text = '''#usda 1.0
def Xform "Bad" (
    customData = {
        string tc:kind = "TcFxSocket"
        string tc:socket = "telegraph"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_fx_usda_text(text)
        self.assertIn('consumerKey', str(ctx.exception))

    def test_unknown_socket_fails(self):
        text = '''#usda 1.0
def Xform "Bad" (
    customData = {
        string tc:kind = "TcFxSocket"
        string tc:socket = "laser_blast"
        string tc:consumerKey = "TELEGRAPH_INK_DRIP_LOOK"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_fx_usda_text(text)
        self.assertIn('unknown socket', str(ctx.exception).lower())

    def test_mismatched_consumer_fails(self):
        text = '''#usda 1.0
def Xform "Bad" (
    customData = {
        string tc:kind = "TcFxSocket"
        string tc:socket = "telegraph"
        string tc:consumerKey = "DEATH_POP_LOOK"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_fx_usda_text(text)
        self.assertIn('canonical', str(ctx.exception))

    def test_unknown_corruption_globals_key_fails(self):
        # Fake known set so a lookalike key is rejected.
        known = set(SOCKET_CONSUMER_KEYS.values()) - {'TELEGRAPH_INK_DRIP_LOOK'}
        # Minimal fixture with kit sockets but telegraph consumer stripped
        # from known set — should fail "not found in CorruptionGlobals".
        text = '''#usda 1.0
def Xform "FxTelegraph" (
    customData = {
        string tc:kind = "TcFxSocket"
        string tc:socket = "telegraph"
        string tc:consumerKey = "TELEGRAPH_INK_DRIP_LOOK"
    }
)
{
}
def Xform "FxHit" (
    customData = {
        string tc:kind = "TcFxSocket"
        string tc:socket = "hit"
        string tc:consumerKey = "SMUDGE_INK_SPLASH_LOOK"
    }
)
{
}
def Xform "FxDeath" (
    customData = {
        string tc:kind = "TcFxSocket"
        string tc:socket = "death"
        string tc:consumerKey = "DEATH_POP_LOOK"
    }
)
{
}
def Xform "FxCream" (
    customData = {
        string tc:kind = "TcFxSocket"
        string tc:socket = "cream"
        string tc:consumerKey = "TELEGRAPH_CREAM_WARN_LOOK"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_fx_usda_text(text, known_consumers=known)
        self.assertIn('CorruptionGlobals', str(ctx.exception))

    def test_banned_token_in_fixture_text_fails_generic_validate(self):
        text = '''#usda 1.0
(
    "keyblade socket test"
)
def Xform "FxTelegraph" (
    customData = {
        string tc:kind = "TcFxSocket"
        string tc:socket = "telegraph"
        string tc:consumerKey = "TELEGRAPH_INK_DRIP_LOOK"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError):
            validate_fx_usda_text(text)


class TestNoGameplaySideEffects(unittest.TestCase):
    def test_notes_declare_no_mesh_no_hydra(self):
        low = FX_SOCKET_NOTES.lower()
        self.assertIn('no mesh', low)
        self.assertIn('no hydra', low)
        self.assertIn('corruptionglobals', low)

    def test_module_is_import_safe(self):
        # Re-import path used by package consumers.
        from toontown.usd import fx_sockets as mod
        self.assertTrue(callable(mod.load_fx_sockets))
        self.assertTrue(callable(mod.telegraph_sockets))


if __name__ == '__main__':
    unittest.main()
