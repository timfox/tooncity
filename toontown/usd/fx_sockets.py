"""Combat FX socket placeholders → CorruptionGlobals consumer map.

Headless string table for ``fixtures/fx/telegraph_sockets.usda``. Each
``TcFxSocket`` empty Xform carries ``tc:socket`` + ``tc:consumerKey``;
consumer keys are attribute names on ``CorruptionGlobals`` that drive
corrupt telegraph / hit / death / cream juice (LOOK tables).

No mesh FX, no Hydra, no Panda display, no gameplay loop wiring — bake /
tooling metadata only. Runtime still attaches juice in Python
(``DistributedCorruptToon`` / ``Corrupt*Fx`` modules).
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

from toontown.usd.bridge import FIXTURES_DIR, parse_usda_text
from toontown.usd.validate import UsdValidationError, validate_usda_text

FX_DIR = FIXTURES_DIR / 'fx'
CORRUPTION_GLOBALS_PATH = (
    Path(__file__).resolve().parents[1] / 'corruption' / 'CorruptionGlobals.py'
)

_FX_KIND = 'TcFxSocket'

# Kit-required sockets (PR 5) — always present in the telegraph fixture.
REQUIRED_KIT_SOCKETS = frozenset({
    'telegraph',
    'hit',
    'death',
    'cream',
})

# Canonical socket → CorruptionGlobals consumer attribute (string table).
# Primary four match character-kit REQUIRED_FX_SOCKETS; extras cover layered
# telegraph/death cream hooks that already exist as LOOK tables.
SOCKET_CONSUMER_KEYS: Dict[str, str] = {
    'telegraph': 'TELEGRAPH_INK_DRIP_LOOK',
    'hit': 'SMUDGE_INK_SPLASH_LOOK',
    'death': 'DEATH_POP_LOOK',
    'cream': 'TELEGRAPH_CREAM_WARN_LOOK',
    'death_cream': 'DEATH_CREAM_FLECK_LOOK',
    'telegraph_cream_sparkle': 'TELEGRAPH_CREAM_SPARKLE_LOOK',
    'telegraph_cream_wash': 'TELEGRAPH_CREAM_WASH_LOOK',
    'death_cream_sparkle': 'DEATH_CREAM_SPARKLE_LOOK',
    'hit_cream': 'SMUDGE_HIT_CREAM_SPLASH_LOOK',
}

# Human-readable contract for docs / tests (stable string).
FX_SOCKET_NOTES = (
    'Empty TcFxSocket Xforms map tc:socket → CorruptionGlobals LOOK '
    'attribute names (TELEGRAPH_INK_DRIP_LOOK, DEATH_POP_LOOK, …). '
    'String table only — no mesh FX, no Hydra, no DistributedCorruptToon '
    'wiring. Runtime juice stays procedural in Corrupt*Fx modules.'
)


class FxSocketError(ValueError):
    """Raised when an FX socket fixture cannot be loaded or validated."""


def fx_dir() -> Path:
    return FX_DIR


def list_fx_fixtures() -> List[str]:
    """Return FX fixture stem names under ``fixtures/fx/``."""
    if not FX_DIR.is_dir():
        return []
    return sorted(p.stem for p in FX_DIR.glob('*.usda'))


def resolve_fx_fixture(name: str) -> Path:
    """Resolve an FX fixture by stem or filename."""
    stem = name[:-5] if name.endswith('.usda') else name
    path = FX_DIR / f'{stem}.usda'
    if not path.is_file():
        raise FileNotFoundError(f'USD FX socket fixture not found: {path}')
    return path


def corruption_globals_consumer_names(
    path: Optional[Path] = None,
) -> Set[str]:
    """AST-skim top-level names assigned in ``CorruptionGlobals.py``.

    Headless — no import of Panda / game runtime. Used to prove every
    ``tc:consumerKey`` names a real CorruptionGlobals hook.
    """
    target = path or CORRUPTION_GLOBALS_PATH
    tree = ast.parse(target.read_text(encoding='utf-8'), filename=str(target))
    names: Set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target_node in node.targets:
                if isinstance(target_node, ast.Name):
                    names.add(target_node.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def _records_of_kind(
    prim_records: Sequence[Dict[str, Any]],
    kind: str,
) -> List[Dict[str, Any]]:
    return [r for r in prim_records if r.get('kind') == kind]


def _socket_entries(
    prim_records: Sequence[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """Extract ordered socket → consumerKey rows from TcFxSocket prims."""
    entries: List[Dict[str, str]] = []
    for rec in _records_of_kind(prim_records, _FX_KIND):
        custom = rec.get('customData') or {}
        socket = str(custom.get('socket') or '').strip().lower()
        consumer = str(custom.get('consumerKey') or '').strip()
        event = str(custom.get('event') or '').strip()
        if not socket and not consumer:
            continue
        entries.append({
            'prim': str(rec.get('name') or ''),
            'socket': socket,
            'consumerKey': consumer,
            'event': event,
        })
    return entries


def _fx_assembly_errors(
    prim_records: Sequence[Dict[str, Any]],
    *,
    known_consumers: Set[str],
) -> List[str]:
    """FX-fixture gates beyond generic ``validate_usda_text``."""
    errors: List[str] = []
    entries = _socket_entries(prim_records)
    if not entries:
        errors.append('FX fixture missing TcFxSocket prims')
        return errors

    sockets_seen: Set[str] = set()
    for entry in entries:
        socket = entry['socket']
        consumer = entry['consumerKey']
        prim = entry['prim'] or '(unnamed)'

        if not socket:
            errors.append(f'TcFxSocket "{prim}" missing tc:socket')
            continue
        if not consumer:
            errors.append(
                f'TcFxSocket "{prim}" (socket={socket!r}) missing '
                f'tc:consumerKey'
            )
            continue

        sockets_seen.add(socket)
        expected = SOCKET_CONSUMER_KEYS.get(socket)
        if expected is None:
            errors.append(
                f'TcFxSocket "{prim}" unknown socket name {socket!r} '
                f'(not in SOCKET_CONSUMER_KEYS)'
            )
        elif consumer != expected:
            errors.append(
                f'TcFxSocket "{prim}" socket={socket!r} consumerKey '
                f'{consumer!r} != canonical {expected!r}'
            )

        if consumer not in known_consumers:
            errors.append(
                f'TcFxSocket "{prim}" consumerKey {consumer!r} not found '
                f'in CorruptionGlobals'
            )

    missing_kit = sorted(REQUIRED_KIT_SOCKETS - sockets_seen)
    if missing_kit:
        errors.append(
            'FX fixture missing kit sockets: ' + ', '.join(missing_kit)
        )
    return errors


def validate_fx_usda_text(
    text: str,
    *,
    known_consumers: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Validate FX socket USDA text (generic + consumer map gates)."""
    base = validate_usda_text(text)
    consumers = known_consumers
    if consumers is None:
        consumers = corruption_globals_consumer_names()
    parsed = parse_usda_text(text)
    prim_records = list(parsed.get('primRecords') or [])
    extra = _fx_assembly_errors(prim_records, known_consumers=consumers)
    if extra:
        raise UsdValidationError('; '.join(extra))
    return {
        **base,
        'fxOk': True,
        'sockets': _socket_entries(prim_records),
    }


def validate_fx_fixture(name: str = 'telegraph_sockets') -> Dict[str, Any]:
    """Validate an FX fixture file under ``fixtures/fx/``."""
    path = resolve_fx_fixture(name)
    text = path.read_text(encoding='utf-8')
    result = validate_fx_usda_text(text)
    result['path'] = str(path)
    result['name'] = path.stem
    return result


def load_fx_sockets(name: str = 'telegraph_sockets') -> Dict[str, Any]:
    """Load FX socket fixture into a CorruptionGlobals consumer map.

    Returns socket rows, ``socketToConsumer`` dict, and notes. Does not
    touch gameplay loaders or require Panda / Hydra / ``pxr``.
    """
    path = resolve_fx_fixture(name)
    validate_fx_fixture(name)
    text = path.read_text(encoding='utf-8')
    parsed = parse_usda_text(text)
    prim_records = list(parsed.get('primRecords') or [])
    entries = _socket_entries(prim_records)
    socket_to_consumer = {
        e['socket']: e['consumerKey'] for e in entries if e['socket']
    }
    # Fixture-level metadata lives on the container Xform (no special kind).
    root_custom: Dict[str, Any] = {}
    for rec in prim_records:
        custom = rec.get('customData') or {}
        if custom.get('fixtureId'):
            root_custom = dict(custom)
            break
    if not root_custom:
        root_custom = dict(parsed.get('customData') or {})

    return {
        'name': path.stem,
        'path': str(path),
        'fixtureId': root_custom.get('fixtureId'),
        'archetype': root_custom.get('archetype'),
        'sockets': entries,
        'socketToConsumer': socket_to_consumer,
        'canonicalMap': dict(SOCKET_CONSUMER_KEYS),
        'requiredKitSockets': sorted(REQUIRED_KIT_SOCKETS),
        'kinds': list(parsed.get('kinds') or []),
        'prims': list(parsed.get('prims') or []),
        'fxSocketNotes': FX_SOCKET_NOTES,
        'meshHeavy': False,
        'mode': 'text',
    }


def telegraph_sockets() -> Dict[str, Any]:
    """Convenience: load the shipped telegraph FX socket fixture."""
    return load_fx_sockets('telegraph_sockets')


def consumer_key_for_socket(socket: str) -> str:
    """Resolve a socket name to its CorruptionGlobals consumer key."""
    key = str(socket or '').strip().lower()
    if key not in SOCKET_CONSUMER_KEYS:
        raise FxSocketError(f'unknown FX socket: {socket!r}')
    return SOCKET_CONSUMER_KEYS[key]
