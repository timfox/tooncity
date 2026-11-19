"""Corrupt / Oswald character kit assemblies (USD → Actor bake map).

Thin headless helpers for ``fixtures/kits/*.usda``. Parses kit metadata
(LOD bands, material looks, FX sockets) into a dict that offline bake
workers can turn into Actor-compatible BAM trees.

**Bake → Actor (documented, not wired yet)**

1. Each ``lod1000`` / ``lod500`` / ``lod250`` prim carries ``tc:bamPath``
   under ``phase_3/models/char/…`` (or future phase). Bake emits those
   BAMs with LOD part names matching ``Toon.setLODs()`` (1000/500/250).
2. ``tc:actorRoot`` is the Actor model stem; anim clips (``tc:animKey``)
   map 1:1 onto Actor anim-dict keys (``neutral``, ``run``, …).
3. Material looks ``pure`` / ``ink`` bake to tint / material binds that
   mirror ``CorruptionGlobals`` actor tint hooks — ``ink`` for corrupt
   swarm, ``pure`` for reclaim restore previews.
4. FX sockets stay empty Xforms; runtime still attaches telegraph / hit /
   death / cream juice in Python (see PR 6 for consumer map).

**Runtime non-goal for this PR**

``DistributedCorruptToon.__tryBuildActorSilhouette`` continues to prefer
a ToonDNA Actor, then falls back to CardMaker cards. This module does
**not** replace that path — it only validates and maps kit metadata so
a later feature-flagged load can point Actor paths at baked kit BAMs
without dropping the card silhouette fallback.

No Hydra, no Panda display, no ``pxr`` hard dependency.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

from toontown.usd.bridge import FIXTURES_DIR, parse_usda_text
from toontown.usd.validate import (
    ALLOWED_LOD_NAMES,
    UsdValidationError,
    validate_usda_text,
)

KITS_DIR = FIXTURES_DIR / 'kits'

# Character-kit material looks (PR 5 acceptance: pure / ink).
ALLOWED_KIT_LOOKS = frozenset({'pure', 'ink'})

# Required FX socket names on a corrupt kit (attach points only).
REQUIRED_FX_SOCKETS = frozenset({
    'telegraph',
    'hit',
    'death',
    'cream',
})

_KIT_KIND = 'TcCharacterKit'
_LOD_GROUP_KIND = 'TcLodGroup'
_MATERIAL_KIND = 'TcMaterialLook'
_FX_KIND = 'TcFxSocket'
_ANIM_KIND = 'TcAnimClip'

# Human-readable bake contract for docs / tests (stable string).
ACTOR_BAKE_NOTES = (
    'Bake lod1000/500/250 tc:bamPath BAMs into Actor LOD parts matching '
    'Toon.setLODs(); map tc:animKey clips to Actor anim dict keys; bind '
    'pure/ink TcMaterialLook to CorruptionGlobals tint hooks. Do not '
    'replace DistributedCorruptToon CardMaker fallback until a '
    'feature-flagged kit load lands.'
)


class CharacterKitError(ValueError):
    """Raised when a character kit fixture cannot be loaded or validated."""


def kits_dir() -> Path:
    return KITS_DIR


def list_kits() -> List[str]:
    """Return kit fixture stem names under ``fixtures/kits/``."""
    if not KITS_DIR.is_dir():
        return []
    return sorted(p.stem for p in KITS_DIR.glob('*.usda'))


def resolve_kit(name: str) -> Path:
    """Resolve a kit fixture by stem or filename."""
    stem = name[:-5] if name.endswith('.usda') else name
    path = KITS_DIR / f'{stem}.usda'
    if not path.is_file():
        raise FileNotFoundError(f'USD character kit fixture not found: {path}')
    return path


def _records_of_kind(
    prim_records: Sequence[Dict[str, Any]],
    kind: str,
) -> List[Dict[str, Any]]:
    return [r for r in prim_records if r.get('kind') == kind]


def _kit_assembly_errors(
    prim_records: Sequence[Dict[str, Any]],
    prim_names: Sequence[str],
) -> List[str]:
    """Kit-specific gates beyond generic ``validate_usda_text``."""
    errors: List[str] = []

    kits = _records_of_kind(prim_records, _KIT_KIND)
    if not kits:
        errors.append('character kit missing TcCharacterKit prim')
    else:
        custom = kits[0].get('customData') or {}
        if not custom.get('variant'):
            errors.append('TcCharacterKit missing tc:variant')
        if not custom.get('kitId'):
            errors.append('TcCharacterKit missing tc:kitId')

    lod_groups = _records_of_kind(prim_records, _LOD_GROUP_KIND)
    if not lod_groups:
        errors.append('character kit missing TcLodGroup')

    present_lods = {n for n in prim_names if n in ALLOWED_LOD_NAMES}
    missing_lods = sorted(ALLOWED_LOD_NAMES - present_lods)
    if missing_lods:
        errors.append(
            'character kit missing LOD prims: ' + ', '.join(missing_lods)
        )

    looks: Set[str] = set()
    for rec in _records_of_kind(prim_records, _MATERIAL_KIND):
        look = (rec.get('customData') or {}).get('look')
        if look:
            looks.add(str(look).strip().lower())
    missing_looks = sorted(ALLOWED_KIT_LOOKS - looks)
    if missing_looks:
        errors.append(
            'character kit missing material looks: '
            + ', '.join(missing_looks)
            + f' (need {", ".join(sorted(ALLOWED_KIT_LOOKS))})'
        )
    unknown_looks = sorted(looks - ALLOWED_KIT_LOOKS)
    if unknown_looks:
        errors.append(
            'character kit unknown material looks: '
            + ', '.join(unknown_looks)
            + f' (allowed {", ".join(sorted(ALLOWED_KIT_LOOKS))})'
        )

    sockets: Set[str] = set()
    for rec in _records_of_kind(prim_records, _FX_KIND):
        socket = (rec.get('customData') or {}).get('socket')
        if socket:
            sockets.add(str(socket).strip().lower())
    missing_sockets = sorted(REQUIRED_FX_SOCKETS - sockets)
    if missing_sockets:
        errors.append(
            'character kit missing FX sockets: '
            + ', '.join(missing_sockets)
        )

    return errors


def validate_kit(name: str) -> Dict[str, Any]:
    """Validate a kit fixture (generic schema + kit assembly gates)."""
    path = resolve_kit(name)
    text = path.read_text(encoding='utf-8')
    # Street-only flags off — kits are not TcStreetRoot stages.
    base = validate_usda_text(
        text,
        fixture_name=path.stem,
        require_street_pack_id=False,
        require_street_zone_id=False,
        path=path,
    )
    parsed = parse_usda_text(text)
    kit_errors = _kit_assembly_errors(
        parsed.get('primRecords') or [],
        parsed.get('prims') or [],
    )
    if kit_errors:
        raise UsdValidationError(
            f'{path.name}: ' + '; '.join(kit_errors)
        )
    base['kitOk'] = True
    return base


def validate_kit_usda_text(
    text: str,
    *,
    fixture_name: str = '<memory>',
) -> Dict[str, Any]:
    """Validate in-memory kit USDA (negative tests)."""
    base = validate_usda_text(
        text,
        fixture_name=fixture_name,
        require_street_pack_id=False,
        require_street_zone_id=False,
    )
    parsed = parse_usda_text(text)
    kit_errors = _kit_assembly_errors(
        parsed.get('primRecords') or [],
        parsed.get('prims') or [],
    )
    if kit_errors:
        raise UsdValidationError(
            f'{fixture_name}: ' + '; '.join(kit_errors)
        )
    base['kitOk'] = True
    return base


def _lod_entries(
    prim_records: Sequence[Dict[str, Any]],
    prim_names: Sequence[str],
) -> List[Dict[str, Any]]:
    """Build ordered LOD bake entries from prim records / names."""
    by_name = {r['name']: r for r in prim_records}
    entries: List[Dict[str, Any]] = []
    for lod_name in ('lod1000', 'lod500', 'lod250'):
        if lod_name not in prim_names and lod_name not in by_name:
            continue
        rec = by_name.get(lod_name) or {'name': lod_name, 'customData': {}}
        custom = dict(rec.get('customData') or {})
        band = custom.get('lodBand')
        if band is None and lod_name.startswith('lod'):
            try:
                band = int(lod_name[3:])
            except ValueError:
                band = None
        entries.append({
            'name': lod_name,
            'lodBand': band,
            'bamPath': custom.get('bamPath'),
            'purpose': custom.get('purpose'),
        })
    return entries


def load_kit(name: str) -> Dict[str, Any]:
    """Load a kit fixture into an Actor-oriented bake map (headless).

    Returns a dict with kit metadata, LOD bam paths, material looks,
    FX sockets, anim keys, and ``actorBakeNotes``. Does not touch
    ``DistributedCorruptToon`` or require Panda / Hydra / ``pxr``.
    """
    path = resolve_kit(name)
    validate_kit(name)
    text = path.read_text(encoding='utf-8')
    parsed = parse_usda_text(text)
    prim_records = list(parsed.get('primRecords') or [])
    prim_names = list(parsed.get('prims') or [])

    kit_recs = _records_of_kind(prim_records, _KIT_KIND)
    kit_custom = dict(kit_recs[0].get('customData') or {}) if kit_recs else {}

    looks = sorted({
        str((r.get('customData') or {}).get('look')).strip().lower()
        for r in _records_of_kind(prim_records, _MATERIAL_KIND)
        if (r.get('customData') or {}).get('look')
    })
    sockets = sorted({
        str((r.get('customData') or {}).get('socket')).strip().lower()
        for r in _records_of_kind(prim_records, _FX_KIND)
        if (r.get('customData') or {}).get('socket')
    })
    anim_keys = sorted({
        str((r.get('customData') or {}).get('animKey')).strip()
        for r in _records_of_kind(prim_records, _ANIM_KIND)
        if (r.get('customData') or {}).get('animKey')
    })

    lods = _lod_entries(prim_records, prim_names)
    actor_paths = {
        entry['name']: entry['bamPath']
        for entry in lods
        if entry.get('bamPath')
    }

    return {
        'name': path.stem,
        'path': str(path),
        'kitId': kit_custom.get('kitId'),
        'variant': kit_custom.get('variant'),
        'archetype': kit_custom.get('archetype'),
        'actorRoot': kit_custom.get('actorRoot'),
        'lods': lods,
        'actorPaths': actor_paths,
        'materialLooks': looks,
        'fxSockets': sockets,
        'animKeys': anim_keys,
        'kinds': list(parsed.get('kinds') or []),
        'prims': prim_names,
        'customData': dict(parsed.get('customData') or {}),
        'actorBakeNotes': ACTOR_BAKE_NOTES,
        'replacesCardFallback': False,
        'mode': 'text',
    }


def ink_smudge_kit() -> Dict[str, Any]:
    """Convenience: load the shipped Ink Smudge (ink variant) kit."""
    return load_kit('ink_smudge_kit')
