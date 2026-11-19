"""Headless validators for Toon City USD fixtures (text mode).

Street overlays must declare ``tc:packId``. Optional ``pxr`` checks are
skip-if-missing and never fail default CI when OpenUSD is absent.
"""

from __future__ import annotations

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


class UsdValidationError(ValueError):
    """Raised when a fixture fails Toon City USD spike validation."""


def _banned_hits(text: str) -> List[str]:
    low = text.lower()
    return [token for token in _BANNED_TOKENS if token in low]


def validate_fixture(
    name: str,
    *,
    require_street_pack_id: bool = True,
) -> Dict[str, Any]:
    """Validate a fixture by stem or filename.

    For street overlays (``TcStreetRoot`` present), ``tc:packId`` /
    ``packId`` must be set when ``require_street_pack_id`` is True.

    Returns a result dict on success; raises ``UsdValidationError`` on
    failure.
    """
    path = resolve_fixture(name)
    text = path.read_text(encoding='utf-8')
    return validate_usda_text(
        text,
        fixture_name=path.stem,
        require_street_pack_id=require_street_pack_id,
        path=path,
    )


def validate_usda_text(
    text: str,
    *,
    fixture_name: str = '<memory>',
    require_street_pack_id: bool = True,
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
    kinds = set(parsed['kinds'])
    custom = parsed['customData']

    if require_street_pack_id and kinds & _STREET_KINDS:
        pack_id = custom.get('packId')
        if not pack_id:
            errors.append(
                'street overlay (TcStreetRoot) missing required tc:packId'
            )

    if errors:
        where = path.name if path is not None else fixture_name
        raise UsdValidationError(
            f'{where}: ' + '; '.join(errors)
        )

    return {
        'ok': True,
        'name': fixture_name,
        'kinds': list(parsed['kinds']),
        'customData': dict(custom),
        'path': str(path) if path is not None else None,
    }


def validate_fixtures(
    names: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    """Validate one or more fixtures; default = all under fixtures/."""
    from toontown.usd.bridge import list_fixtures

    targets = list(names) if names is not None else list_fixtures()
    return [validate_fixture(n) for n in targets]
