"""Headless validators for Toon City USD fixtures (text mode).

Enforces prim conventions from ``schemas.md``:

- Street roots (``TcStreetRoot``) require ``tc:zoneId`` and ``tc:packId``
- Spawn stand ``tc:archetype`` must be in the reclaim allow-list
- LOD prim names must be ``lod1000`` / ``lod500`` / ``lod250``
- Banned KH tokens in prim paths / metadata

Optional ``pxr`` checks are skip-if-missing and never fail default CI when
OpenUSD is absent.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from toontown.usd.bridge import (
    parse_usda_text,
    resolve_fixture,
)

# Tokens banned from fixtures / metadata (KH branding preference).
_BANNED_TOKENS = (
    'keyblade',
    'key blade',
    'kingdom hearts',
    'kingdomhearts',
    'sora',
    'heartless',
)

_STREET_KINDS = frozenset({'TcStreetRoot'})
_SPAWN_KINDS = frozenset({'TcSpawnStand'})
_LOD_GROUP_KIND = 'TcLodGroup'

# Reclaim short tokens (WAVE_SCRIPT_TOKENS short forms) — USD allow-list.
ALLOWED_ARCHETYPES = frozenset({
    'ink',
    'brute',
    'snare',
    'gag',
    'oswald',
})

# Toon Actor LOD bands mirrored as prim names under TcLodGroup.
ALLOWED_LOD_NAMES = frozenset({
    'lod1000',
    'lod500',
    'lod250',
})

_LOD_NAME_RE = re.compile(r'^lod\d+$', re.IGNORECASE)


class UsdValidationError(ValueError):
    """Raised when a fixture fails Toon City USD validation."""


def _banned_hits(text: str) -> List[str]:
    low = text.lower()
    return [token for token in _BANNED_TOKENS if token in low]


def _check_street_roots(
    prim_records: Sequence[Dict[str, Any]],
    *,
    require_street_pack_id: bool,
    require_street_zone_id: bool,
) -> List[str]:
    errors: List[str] = []
    for rec in prim_records:
        if rec.get('kind') not in _STREET_KINDS:
            continue
        custom = rec.get('customData') or {}
        if require_street_zone_id and custom.get('zoneId') in (None, ''):
            errors.append(
                f'street root "{rec["name"]}" (TcStreetRoot) missing '
                f'required tc:zoneId'
            )
        if require_street_pack_id and not custom.get('packId'):
            errors.append(
                f'street root "{rec["name"]}" (TcStreetRoot) missing '
                f'required tc:packId'
            )
    return errors


def _check_archetypes(prim_records: Sequence[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    for rec in prim_records:
        if rec.get('kind') not in _SPAWN_KINDS:
            continue
        custom = rec.get('customData') or {}
        archetype = custom.get('archetype')
        if archetype is None or archetype == '':
            errors.append(
                f'spawn stand "{rec["name"]}" (TcSpawnStand) missing '
                f'tc:archetype'
            )
            continue
        token = str(archetype).strip().lower()
        if token not in ALLOWED_ARCHETYPES:
            allowed = ', '.join(sorted(ALLOWED_ARCHETYPES))
            errors.append(
                f'spawn stand "{rec["name"]}" archetype "{archetype}" '
                f'not in allow-list ({allowed})'
            )
    return errors


def _check_lod_names(
    prim_records: Sequence[Dict[str, Any]],
    prim_names: Sequence[str],
) -> List[str]:
    errors: List[str] = []
    lod_prims = [
        name for name in prim_names if _LOD_NAME_RE.match(name)
    ]
    for name in lod_prims:
        if name not in ALLOWED_LOD_NAMES:
            allowed = ', '.join(sorted(ALLOWED_LOD_NAMES))
            errors.append(
                f'LOD prim "{name}" not allowed; use exactly {allowed}'
            )

    has_lod_group = any(
        rec.get('kind') == _LOD_GROUP_KIND for rec in prim_records
    )
    if has_lod_group:
        present = set(lod_prims)
        missing = sorted(ALLOWED_LOD_NAMES - present)
        if missing:
            errors.append(
                'TcLodGroup requires LOD children '
                + ', '.join(sorted(ALLOWED_LOD_NAMES))
                + f'; missing: {", ".join(missing)}'
            )
    return errors


def validate_fixture(
    name: str,
    *,
    require_street_pack_id: bool = True,
    require_street_zone_id: bool = True,
) -> Dict[str, Any]:
    """Validate a fixture by stem or filename.

    For street roots (``TcStreetRoot``), ``tc:zoneId`` and ``tc:packId``
    must be set when the corresponding require_* flags are True.

    Returns a result dict on success; raises ``UsdValidationError`` on
    failure.
    """
    path = resolve_fixture(name)
    text = path.read_text(encoding='utf-8')
    return validate_usda_text(
        text,
        fixture_name=path.stem,
        require_street_pack_id=require_street_pack_id,
        require_street_zone_id=require_street_zone_id,
        path=path,
    )


def validate_usda_text(
    text: str,
    *,
    fixture_name: str = '<memory>',
    require_street_pack_id: bool = True,
    require_street_zone_id: bool = True,
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Validate ASCII USDA text (used by tests for negative cases)."""
    errors: List[str] = []

    if '\x00' in text:
        errors.append('fixture must be ASCII USDA (nul byte found)')

    banned = _banned_hits(text)
    if banned:
        errors.append(f'banned KH tokens present: {", ".join(banned)}')

    parsed = parse_usda_text(text)
    prim_records = parsed.get('primRecords') or []
    prim_names = parsed.get('prims') or []

    # Fallback when kind appears only as text marker (legacy flatten path).
    kinds = set(parsed['kinds'])
    if require_street_pack_id and kinds & _STREET_KINDS:
        # Prefer per-prim checks; if no primRecords tagged street, use flat.
        street_recs = [
            r for r in prim_records if r.get('kind') in _STREET_KINDS
        ]
        if not street_recs:
            custom = parsed['customData']
            if require_street_zone_id and custom.get('zoneId') in (None, ''):
                errors.append(
                    'street overlay (TcStreetRoot) missing required tc:zoneId'
                )
            if not custom.get('packId'):
                errors.append(
                    'street overlay (TcStreetRoot) missing required tc:packId'
                )

    errors.extend(
        _check_street_roots(
            prim_records,
            require_street_pack_id=require_street_pack_id,
            require_street_zone_id=require_street_zone_id,
        )
    )
    errors.extend(_check_archetypes(prim_records))
    errors.extend(_check_lod_names(prim_records, prim_names))

    if errors:
        where = path.name if path is not None else fixture_name
        raise UsdValidationError(
            f'{where}: ' + '; '.join(errors)
        )

    return {
        'ok': True,
        'name': fixture_name,
        'kinds': list(parsed['kinds']),
        'customData': dict(parsed['customData']),
        'primRecords': list(prim_records),
        'path': str(path) if path is not None else None,
    }


def validate_fixtures(
    names: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    """Validate one or more fixtures; default = all under fixtures/."""
    from toontown.usd.bridge import list_fixtures

    targets = list(names) if names is not None else list_fixtures()
    return [validate_fixture(n) for n in targets]
