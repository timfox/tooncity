"""Street-pack USD composition (text mode, no Hydra / no pxr required).

Composes ASCII ``.usda`` layer stacks under ``fixtures/streets/`` into a
resolved stage dict: street-root metadata, spawn stands, reclaim volumes,
and active look. Later layers win on colliding ``customData`` keys for the
same prim name (USD opinion order, simplified).

Default Loopy Lane stack mirrors the adoption plan::

    loopy_lane.usda
      ← packs/loopy_smudge.usda
      ← looks/polluted.usda | looks/pure.usda
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from toontown.usd.bridge import FIXTURES_DIR, parse_usda_text

STREETS_DIR = FIXTURES_DIR / 'streets'

# Known street packs: street stem → (pack stem, default look).
_STREET_DEFAULTS = {
    'loopy_lane': {
        'pack': 'loopy_smudge',
        'look': 'polluted',
        'rootPrim': 'LoopyLane',
    },
}

_LOOK_KINDS = frozenset({'TcMaterialLook', 'TcLightLook'})


class UsdComposeError(ValueError):
    """Raised when a street-pack composition stack cannot be resolved."""


def streets_dir() -> Path:
    return STREETS_DIR


def loopy_lane_dir() -> Path:
    return STREETS_DIR / 'loopy_lane'


def list_street_packs() -> List[str]:
    """Return street fixture directory names under ``fixtures/streets/``."""
    if not STREETS_DIR.is_dir():
        return []
    return sorted(p.name for p in STREETS_DIR.iterdir() if p.is_dir())


def _layer_paths(
    street: str,
    *,
    pack: str,
    look: str,
) -> List[Path]:
    root = STREETS_DIR / street
    if not root.is_dir():
        raise UsdComposeError(f'unknown street fixture directory: {street}')
    base = root / f'{street}.usda'
    pack_path = root / 'packs' / f'{pack}.usda'
    look_path = root / 'looks' / f'{look}.usda'
    missing = [str(p) for p in (base, pack_path, look_path) if not p.is_file()]
    if missing:
        raise UsdComposeError(
            f'missing composition layers for street={street!r} '
            f'pack={pack!r} look={look!r}: {missing}'
        )
    return [base, pack_path, look_path]


def layer_stack_for(
    street: str = 'loopy_lane',
    *,
    pack: Optional[str] = None,
    look: Optional[str] = None,
) -> List[Path]:
    """Resolve absolute layer paths for a street / pack / look stack."""
    defaults = _STREET_DEFAULTS.get(street, {})
    pack_name = pack or defaults.get('pack')
    look_name = look or defaults.get('look', 'polluted')
    if not pack_name:
        raise UsdComposeError(
            f'pack required for street={street!r} (no default registered)'
        )
    return _layer_paths(street, pack=pack_name, look=look_name)


def _merge_custom(
    base: Dict[str, Any],
    overlay: Dict[str, Any],
) -> Dict[str, Any]:
    merged = dict(base)
    merged.update(overlay)
    return merged


def _compose_prim_map(
    layers: Sequence[Tuple[Path, Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """Merge per-prim records across layers; later layers win on keys."""
    by_name: Dict[str, Dict[str, Any]] = {}
    for path, parsed in layers:
        for rec in parsed.get('primRecords') or []:
            name = rec.get('name')
            if not name:
                continue
            existing = by_name.get(name)
            if existing is None:
                by_name[name] = {
                    'name': name,
                    'kind': rec.get('kind'),
                    'customData': dict(rec.get('customData') or {}),
                    'layer': path.name,
                    'layers': [path.name],
                }
                continue
            existing['customData'] = _merge_custom(
                existing.get('customData') or {},
                rec.get('customData') or {},
            )
            # Prefer non-None kind from later layer.
            if rec.get('kind'):
                existing['kind'] = rec.get('kind')
            existing['layer'] = path.name
            existing['layers'] = list(existing.get('layers') or []) + [path.name]
    return by_name


def _street_root(prims: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    roots = [
        p for p in prims.values()
        if p.get('kind') == 'TcStreetRoot'
    ]
    if not roots:
        # Fallback: prefer known root prim name, else first prim with zoneId.
        for p in prims.values():
            custom = p.get('customData') or {}
            if 'zoneId' in custom or 'packId' in custom:
                return p
        raise UsdComposeError('composed stage has no TcStreetRoot')
    # Prefer the root that carries packId when multiple.
    for p in reversed(roots):
        if (p.get('customData') or {}).get('packId'):
            return p
    return roots[-1]


def _spawn_stands(prims: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    stands: List[Dict[str, Any]] = []
    for p in prims.values():
        if p.get('kind') != 'TcSpawnStand':
            continue
        custom = p.get('customData') or {}
        stands.append({
            'name': p['name'],
            'archetype': custom.get('archetype'),
            'standIndex': custom.get('standIndex'),
            'customData': dict(custom),
        })
    stands.sort(key=lambda s: (
        s['standIndex'] if isinstance(s['standIndex'], int) else 10**9,
        s['name'],
    ))
    return stands


def _reclaim_volumes(prims: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    volumes: List[Dict[str, Any]] = []
    for p in prims.values():
        if p.get('kind') != 'TcReclaimVolume':
            continue
        custom = p.get('customData') or {}
        volumes.append({
            'name': p['name'],
            'seedPollution': custom.get('seedPollution'),
            'customData': dict(custom),
        })
    volumes.sort(key=lambda v: v['name'])
    return volumes


def _active_looks(prims: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    looks: List[Dict[str, Any]] = []
    for p in prims.values():
        if p.get('kind') not in _LOOK_KINDS:
            continue
        custom = p.get('customData') or {}
        looks.append({
            'name': p['name'],
            'kind': p.get('kind'),
            'look': custom.get('look'),
            'customData': dict(custom),
        })
    looks.sort(key=lambda x: x['name'])
    return looks


def compose_layers(
    layer_paths: Sequence[Path],
    *,
    street: Optional[str] = None,
    pack: Optional[str] = None,
    look: Optional[str] = None,
) -> Dict[str, Any]:
    """Compose an ordered list of USDA layer paths into a stage dict."""
    if not layer_paths:
        raise UsdComposeError('compose_layers requires at least one layer')

    loaded: List[Tuple[Path, Dict[str, Any]]] = []
    for path in layer_paths:
        path = Path(path)
        if not path.is_file():
            raise UsdComposeError(f'layer not found: {path}')
        text = path.read_text(encoding='utf-8')
        if not text.startswith('#usda'):
            raise UsdComposeError(f'not ASCII USDA: {path}')
        if '\x00' in text:
            raise UsdComposeError(f'binary USDA not supported: {path}')
        loaded.append((path, parse_usda_text(text)))

    prims = _compose_prim_map(loaded)
    root = _street_root(prims)
    root_custom = dict(root.get('customData') or {})
    stands = _spawn_stands(prims)
    volumes = _reclaim_volumes(prims)
    looks = _active_looks(prims)

    seed = None
    if volumes:
        seed = volumes[0].get('seedPollution')
    if seed is None:
        seed = root_custom.get('seedPollution')

    kinds: List[str] = []
    seen = set()
    for _path, parsed in loaded:
        for kind in parsed.get('kinds') or []:
            if kind not in seen:
                seen.add(kind)
                kinds.append(kind)

    stage: Dict[str, Any] = {
        'street': street,
        'pack': pack,
        'look': look,
        'layers': [str(p) for p, _ in loaded],
        'layerNames': [p.name for p, _ in loaded],
        'rootPrim': root.get('name'),
        'zoneId': root_custom.get('zoneId'),
        'packId': root_custom.get('packId'),
        'hood': root_custom.get('hood'),
        'bamPath': root_custom.get('bamPath'),
        'seedPollution': seed,
        'spawnStands': stands,
        'reclaimVolumes': volumes,
        'looks': looks,
        'prims': {name: dict(rec) for name, rec in prims.items()},
        'kinds': kinds,
        'mode': 'text',
    }
    return stage


def compose_street_pack(
    street: str = 'loopy_lane',
    *,
    pack: Optional[str] = None,
    look: Optional[str] = None,
) -> Dict[str, Any]:
    """Compose a street pack layer stack under ``fixtures/streets/<street>/``."""
    defaults = _STREET_DEFAULTS.get(street, {})
    pack_name = pack or defaults.get('pack')
    look_name = look or defaults.get('look', 'polluted')
    paths = layer_stack_for(street, pack=pack_name, look=look_name)
    return compose_layers(
        paths,
        street=street,
        pack=pack_name,
        look=look_name,
    )


def compose_loopy_lane(*, look: str = 'polluted') -> Dict[str, Any]:
    """Compose Loopy Lane + loopy-smudge pack + look opinion (headless)."""
    return compose_street_pack('loopy_lane', pack='loopy_smudge', look=look)


def iter_loopy_layer_texts() -> Iterable[Tuple[str, str]]:
    """Yield ``(relative_name, text)`` for all Loopy Lane USDA fixtures."""
    root = loopy_lane_dir()
    if not root.is_dir():
        return
    for path in sorted(root.rglob('*.usda')):
        rel = str(path.relative_to(root)).replace('\\', '/')
        yield rel, path.read_text(encoding='utf-8')
