#!/usr/bin/env python3
"""Headless USD corrupt character kit gates (PR 5 / TC-423).

Ink Smudge kit lists lod1000/500/250, pure/ink material variants, FX
sockets; bans KH tokens; documents Actor bake paths without replacing
DistributedCorruptToon CardMaker fallback.

Run from repo root:
  python3 -m unittest tests.test_usd_corrupt_kit -v
  python3 tests/test_usd_corrupt_kit.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from toontown.usd.character_kit import (  # noqa: E402
    ACTOR_BAKE_NOTES,
    ALLOWED_KIT_LOOKS,
    REQUIRED_FX_SOCKETS,
    ink_smudge_kit,
    kits_dir,
    list_kits,
    load_kit,
    resolve_kit,
    validate_kit,
    validate_kit_usda_text,
)
from toontown.usd.validate import (  # noqa: E402
    ALLOWED_LOD_NAMES,
    UsdValidationError,
)

KITS = REPO_ROOT / 'toontown' / 'usd' / 'fixtures' / 'kits'
KIT_STEM = 'ink_smudge_kit'
SCHEMAS_MD = REPO_ROOT / 'toontown' / 'usd' / 'schemas.md'
CORRUPT_TOON = (
    REPO_ROOT / 'toontown' / 'corruption' / 'DistributedCorruptToon.py'
)

_BANNED = (
    'keyblade',
    'kingdom hearts',
    'kingdomhearts',
    'sora',
    'heartless',
)


class TestInkSmudgeFixture(unittest.TestCase):
    def test_fixture_exists_ascii_clean(self):
        path = KITS / f'{KIT_STEM}.usda'
        self.assertTrue(path.is_file(), f'missing fixture: {path}')
        text = path.read_text(encoding='utf-8')
        self.assertTrue(text.startswith('#usda'), path.name)
        self.assertNotIn('\x00', text)
        low = text.lower()
        for token in _BANNED:
            self.assertNotIn(token, low, f'banned token in {path.name}')

    def test_resolve_and_list(self):
        self.assertEqual(kits_dir(), KITS)
        self.assertIn(KIT_STEM, list_kits())
        self.assertEqual(resolve_kit(KIT_STEM), KITS / f'{KIT_STEM}.usda')
        self.assertEqual(
            resolve_kit(f'{KIT_STEM}.usda'),
            KITS / f'{KIT_STEM}.usda',
        )


class TestKitAssembly(unittest.TestCase):
    def test_validate_kit_ok(self):
        result = validate_kit(KIT_STEM)
        self.assertTrue(result['ok'])
        self.assertTrue(result.get('kitOk'))
        self.assertIn('TcCharacterKit', result['kinds'])
        self.assertIn('TcLodGroup', result['kinds'])
        self.assertIn('TcMaterialLook', result['kinds'])
        self.assertIn('TcFxSocket', result['kinds'])

    def test_load_kit_lods_looks_sockets(self):
        kit = load_kit(KIT_STEM)
        lod_names = {entry['name'] for entry in kit['lods']}
        self.assertEqual(lod_names, set(ALLOWED_LOD_NAMES))
        for entry in kit['lods']:
            self.assertTrue(
                str(entry.get('bamPath') or '').endswith('.bam'),
                entry,
            )
            self.assertIn('phase_3/models/char/', entry['bamPath'])
        self.assertEqual(set(kit['materialLooks']), set(ALLOWED_KIT_LOOKS))
        self.assertEqual(set(kit['fxSockets']), set(REQUIRED_FX_SOCKETS))
        self.assertEqual(kit['variant'], 'ink')
        self.assertEqual(kit['archetype'], 'ink')
        self.assertEqual(kit['kitId'], 'ink-smudge')
        self.assertFalse(kit['replacesCardFallback'])

    def test_ink_smudge_convenience(self):
        kit = ink_smudge_kit()
        self.assertEqual(kit['name'], KIT_STEM)
        self.assertEqual(
            set(kit['actorPaths']),
            set(ALLOWED_LOD_NAMES),
        )


class TestActorBakeDocs(unittest.TestCase):
    def test_bake_notes_mention_actor_and_fallback(self):
        notes = ACTOR_BAKE_NOTES.lower()
        self.assertIn('actor', notes)
        self.assertIn('lod', notes)
        self.assertIn('cardmaker', notes.replace(' ', ''))
        # Prefer readable form too.
        self.assertIn('DistributedCorruptToon', ACTOR_BAKE_NOTES)
        self.assertIn('CardMaker', ACTOR_BAKE_NOTES)

    def test_load_kit_exposes_bake_notes(self):
        kit = load_kit(KIT_STEM)
        self.assertEqual(kit['actorBakeNotes'], ACTOR_BAKE_NOTES)
        self.assertFalse(kit['replacesCardFallback'])

    def test_schemas_md_documents_kit_bake(self):
        text = SCHEMAS_MD.read_text(encoding='utf-8')
        self.assertIn('ink_smudge_kit', text)
        self.assertIn('DistributedCorruptToon', text)
        self.assertIn('CardMaker', text)
        low = text.lower()
        for token in _BANNED:
            self.assertNotIn(token, low)

    def test_corrupt_toon_card_fallback_still_present(self):
        """Guard: kit PR must not strip CardMaker fallback from client."""
        self.assertTrue(CORRUPT_TOON.is_file())
        src = CORRUPT_TOON.read_text(encoding='utf-8')
        self.assertIn('CardMaker', src)
        self.assertIn('__buildCardSilhouette', src)
        self.assertIn('__tryBuildActorSilhouette', src)
        # No USD kit import wired into gameplay yet.
        self.assertNotIn('character_kit', src)
        self.assertNotIn('ink_smudge_kit', src)


class TestKitNegativeCases(unittest.TestCase):
    def test_missing_lod_fails(self):
        bad = '''#usda 1.0
def Xform "Kit" (
    customData = {
        string tc:kind = "TcCharacterKit"
        string tc:variant = "ink"
        string tc:kitId = "broken"
    }
)
{
    def Xform "LodGroup" (
        customData = { string tc:kind = "TcLodGroup" }
    )
    {
        def Xform "lod1000" { }
        def Xform "lod500" { }
    }
    def Xform "LookPure" (
        customData = {
            string tc:kind = "TcMaterialLook"
            string tc:look = "pure"
        }
    ) { }
    def Xform "LookInk" (
        customData = {
            string tc:kind = "TcMaterialLook"
            string tc:look = "ink"
        }
    ) { }
    def Xform "FxTelegraph" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "telegraph"
        }
    ) { }
    def Xform "FxHit" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "hit"
        }
    ) { }
    def Xform "FxDeath" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "death"
        }
    ) { }
    def Xform "FxCream" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "cream"
        }
    ) { }
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_kit_usda_text(bad, fixture_name='no_lod250')
        self.assertIn('lod250', str(ctx.exception))

    def test_missing_ink_look_fails(self):
        bad = '''#usda 1.0
def Xform "Kit" (
    customData = {
        string tc:kind = "TcCharacterKit"
        string tc:variant = "ink"
        string tc:kitId = "broken"
    }
)
{
    def Xform "LodGroup" (
        customData = { string tc:kind = "TcLodGroup" }
    )
    {
        def Xform "lod1000" { }
        def Xform "lod500" { }
        def Xform "lod250" { }
    }
    def Xform "LookPure" (
        customData = {
            string tc:kind = "TcMaterialLook"
            string tc:look = "pure"
        }
    ) { }
    def Xform "FxTelegraph" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "telegraph"
        }
    ) { }
    def Xform "FxHit" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "hit"
        }
    ) { }
    def Xform "FxDeath" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "death"
        }
    ) { }
    def Xform "FxCream" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "cream"
        }
    ) { }
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_kit_usda_text(bad, fixture_name='no_ink_look')
        msg = str(ctx.exception)
        self.assertIn('material looks', msg)
        self.assertIn('ink', msg)

    def test_missing_fx_socket_fails(self):
        bad = '''#usda 1.0
def Xform "Kit" (
    customData = {
        string tc:kind = "TcCharacterKit"
        string tc:variant = "ink"
        string tc:kitId = "broken"
    }
)
{
    def Xform "LodGroup" (
        customData = { string tc:kind = "TcLodGroup" }
    )
    {
        def Xform "lod1000" { }
        def Xform "lod500" { }
        def Xform "lod250" { }
    }
    def Xform "LookPure" (
        customData = {
            string tc:kind = "TcMaterialLook"
            string tc:look = "pure"
        }
    ) { }
    def Xform "LookInk" (
        customData = {
            string tc:kind = "TcMaterialLook"
            string tc:look = "ink"
        }
    ) { }
    def Xform "FxTelegraph" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "telegraph"
        }
    ) { }
    def Xform "FxHit" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "hit"
        }
    ) { }
    def Xform "FxDeath" (
        customData = {
            string tc:kind = "TcFxSocket"
            string tc:socket = "death"
        }
    ) { }
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_kit_usda_text(bad, fixture_name='no_cream_socket')
        self.assertIn('cream', str(ctx.exception))

    def test_banned_kh_token_fails(self):
        bad = '''#usda 1.0
def Xform "KeybladeKit" (
    customData = {
        string tc:kind = "TcCharacterKit"
        string tc:variant = "ink"
        string tc:kitId = "nope"
    }
)
{
}
'''
        with self.assertRaises(UsdValidationError) as ctx:
            validate_kit_usda_text(bad, fixture_name='kh_kit')
        self.assertIn('banned', str(ctx.exception).lower())


class TestNoGameplayImports(unittest.TestCase):
    def test_character_kit_stdlib_only(self):
        """character_kit must stay importable without panda3d / Hydra."""
        import toontown.usd.character_kit as ck
        src = Path(ck.__file__).read_text(encoding='utf-8')
        low = src.lower()
        self.assertNotIn('panda3d', low)
        self.assertNotIn('from pxr', src)
        # Docstring may mention DistributedCorruptToon; code must not import it.
        self.assertNotIn('from toontown.corruption', src)
        self.assertNotIn('import DistributedCorruptToon', src)


if __name__ == '__main__':
    unittest.main()
