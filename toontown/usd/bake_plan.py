"""Deterministic offline bake plans for Toon City USD props (BAM + DNA).

Given an ASCII USDA fixture (e.g. ``smoke_prop.usda``), emit a stable
JSON-serializable bake plan: target ``phase_*/models/….bam`` path and DNA
code string. Pure Python / stdlib — no ``egg2bam``, no Hydra, no Panda
display.

Real geometry conversion is intentionally out of scope here; see
``bake_bam.HOOK_POINTS`` for where future workers plug in.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from toontown.usd.bridge import load_fixture, parse_usda_text, resolve_fixture

# Bump when bake-plan JSON shape changes in a breaking way.
SCHEMA_VERSION = 1

# Stable top-level key order for deterministic JSON dumps.
_PLAN_KEY_ORDER: Sequence[str] = (
    'schemaVersion',
    'source',
    'sourcePath',
    'kind',
    'primName',
    'bamPath',
    'dnaCode',
    'hood',
    'zoneId',
    'packId',
    'dryRun',
    'status',
    'workers',
    'customData',
)


class BakePlanError(ValueError):
    """Raised when a fixture cannot yield a prop bake plan."""


def _first_prop_record(prim_records: Sequence[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    for rec in prim_records:
        if rec.get('kind') == 'TcProp':
            return dict(rec)
    return None


def _ordered_plan(raw: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a new dict with stable key order (extras appended sorted)."""
    out: Dict[str, Any] = {}
    for key in _PLAN_KEY_ORDER:
        if key in raw:
            out[key] = raw[key]
    for key in sorted(k for k in raw.keys() if k not in out):
        out[key] = raw[key]
    return out


def plan_from_parsed(
    parsed: Mapping[str, Any],
    *,
    source: str,
    source_path: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Build a bake plan from ``parse_usda_text`` / bridge output.

    Requires a ``TcProp`` with ``tc:bamPath`` and ``tc:dnaCode``.
    """
    prim_records = list(parsed.get('primRecords') or [])
    flat_custom = dict(parsed.get('customData') or {})

    prop = _first_prop_record(prim_records)
    if prop is None:
        # Flat customData path (legacy / skim without per-prim kinds).
        if 'TcProp' not in (parsed.get('kinds') or []) and flat_custom.get('kind') != 'TcProp':
            raise BakePlanError(
                f'{source}: no TcProp prim found for offline bake plan'
            )
        prop_custom = flat_custom
        prim_name = (parsed.get('prims') or [None])[0]
    else:
        prop_custom = dict(prop.get('customData') or {})
        # Prefer prop-local fields; fill gaps from flattened stage customData.
        for key, value in flat_custom.items():
            prop_custom.setdefault(key, value)
        prim_name = prop.get('name')

    bam_path = prop_custom.get('bamPath')
    dna_code = prop_custom.get('dnaCode')
    if not bam_path:
        raise BakePlanError(
            f'{source}: TcProp missing required tc:bamPath '
            f'(expected phase_*/models/….bam)'
        )
    if not dna_code:
        raise BakePlanError(
            f'{source}: TcProp missing required tc:dnaCode'
        )

    bam_str = str(bam_path)
    if not bam_str.endswith('.bam'):
        raise BakePlanError(
            f'{source}: tc:bamPath must end with .bam, got {bam_str!r}'
        )
    if 'phase_' not in bam_str or '/models/' not in bam_str:
        raise BakePlanError(
            f'{source}: tc:bamPath must look like phase_*/models/….bam, '
            f'got {bam_str!r}'
        )

    # Document which offline workers would run for a real bake (stubs only).
    workers: List[Dict[str, str]] = [
        {
            'id': 'usd_to_egg',
            'role': 'Convert USDA geom → EGG (or direct mesh IR)',
            'status': 'stub',
        },
        {
            'id': 'egg2bam',
            'role': 'Run egg2bam → phase_*/models/….bam',
            'status': 'stub',
        },
        {
            'id': 'dna_register',
            'role': 'Register DNA storage code string for PropPool / DNA',
            'status': 'stub',
        },
    ]

    plan = {
        'schemaVersion': SCHEMA_VERSION,
        'source': source,
        'sourcePath': source_path,
        'kind': 'TcProp',
        'primName': prim_name,
        'bamPath': bam_str,
        'dnaCode': str(dna_code),
        'hood': prop_custom.get('hood'),
        'zoneId': prop_custom.get('zoneId'),
        'packId': prop_custom.get('packId'),
        'dryRun': bool(dry_run),
        'status': 'planned' if dry_run else 'pending',
        'workers': workers,
        'customData': {
            k: prop_custom[k]
            for k in sorted(prop_custom.keys())
        },
    }
    return _ordered_plan(plan)


def plan_from_fixture(
    name: str,
    *,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Load a fixture and return a deterministic prop bake plan dict."""
    path = resolve_fixture(name)
    text = path.read_text(encoding='utf-8')
    if '\x00' in text:
        raise BakePlanError(f'Fixture must be ASCII USDA text: {path.name}')
    parsed = parse_usda_text(text)
    return plan_from_parsed(
        parsed,
        source=path.stem,
        source_path=str(path),
        dry_run=dry_run,
    )


def plan_from_bridge(
    name: str,
    *,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Build a bake plan using ``bridge.load_fixture`` metadata + re-parse.

    Prefer ``plan_from_fixture`` for CI; this helper keeps bridge and bake
    plan fields aligned when tooling already holds a bridge dict.
    """
    bridge_plan = load_fixture(name)
    path = Path(bridge_plan['path'])
    text = path.read_text(encoding='utf-8')
    parsed = parse_usda_text(text)
    return plan_from_parsed(
        parsed,
        source=bridge_plan.get('name') or path.stem,
        source_path=str(path),
        dry_run=dry_run,
    )


def plan_to_json(
    plan: Mapping[str, Any],
    *,
    indent: int = 2,
) -> str:
    """Serialize a bake plan to deterministic JSON (sorted keys, stable)."""
    ordered = _ordered_plan(plan)
    return json.dumps(
        ordered,
        indent=indent,
        sort_keys=False,
        ensure_ascii=True,
        separators=(',', ': '),
    ) + '\n'


def write_plan_json(
    plan: Mapping[str, Any],
    dest: Path,
    *,
    indent: int = 2,
) -> Path:
    """Write bake plan JSON to ``dest``; return the path."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(plan_to_json(plan, indent=indent), encoding='utf-8')
    return dest
