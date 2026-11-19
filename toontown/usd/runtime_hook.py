"""SafeZone / Town loader USD street-overlay hook (metadata only).

Feature flag ``want-usd-street-overlay`` (default **off**). When enabled
with a fixture street / path, loads a composed overlay and returns a dict
consumed by :func:`apply_overlay_metadata` (pollution seed + spawn stand
list). No Hydra, no geom rewrite, no hard ``pxr`` dependency.

Callsites in ``TownLoader`` / ``SafeZoneLoader`` / reclaim enter stash the
applied metadata only — DNA/BAM load paths stay unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from toontown.usd.compose import (
    STREETS_DIR,
    UsdComposeError,
    compose_layers,
    compose_street_pack,
    list_street_packs,
)

# Config / PRC names (Panda ConfigVariableBool / String).
WANT_USD_STREET_OVERLAY = 'want-usd-street-overlay'
USD_STREET_OVERLAY_PATH = 'usd-street-overlay-path'
USD_STREET_OVERLAY_LOOK = 'usd-street-overlay-look'

# Canonical branch zone → street fixture directory stem.
ZONE_TO_STREET = {
    2200: 'loopy_lane',
}

RUNTIME_HOOK_NOTES = (
    'Feature-flagged USD street overlay (want-usd-street-overlay). '
    'Metadata only: pollution seed + spawn stand list from composed '
    'fixtures. No Hydra, no DNA rewrite, no pxr required for default CI.'
)


class UsdRuntimeHookError(ValueError):
    """Raised when an enabled overlay cannot be resolved or composed."""


def _config_holder():
    """Best-effort ``base`` / ``simbase`` for GetBool / GetString."""
    import builtins
    for holder_name in ('base', 'simbase'):
        holder = getattr(builtins, holder_name, None)
        if holder is not None and getattr(holder, 'config', None) is not None:
            return holder
    return None


def _config_get_bool(name: str, default: bool = False) -> bool:
    """Read a bool config flag without requiring Panda at import time."""
    try:
        from panda3d.core import ConfigVariableBool  # type: ignore
        return bool(ConfigVariableBool(name, default).value)
    except Exception:
        pass
    holder = _config_holder()
    if holder is not None:
        try:
            return bool(holder.config.GetBool(name, default))
        except Exception:
            pass
    return bool(default)


def _config_get_string(name: str, default: str = '') -> str:
    """Read a string config without requiring Panda at import time."""
    try:
        from panda3d.core import ConfigVariableString  # type: ignore
        return str(ConfigVariableString(name, default).value)
    except Exception:
        pass
    holder = _config_holder()
    if holder is not None:
        try:
            return str(holder.config.GetString(name, default))
        except Exception:
            pass
    return str(default)


def is_usd_street_overlay_wanted(
    enabled: Optional[bool] = None,
) -> bool:
    """Return whether the street-overlay hook is active (default off)."""
    if enabled is not None:
        return bool(enabled)
    return _config_get_bool(WANT_USD_STREET_OVERLAY, False)


def street_for_zone(zone_id: Optional[int]) -> Optional[str]:
    """Map a canonical branch / reclaim zone id to a street fixture stem."""
    if zone_id is None:
        return None
    try:
        zid = int(zone_id)
    except (TypeError, ValueError):
        return None
    return ZONE_TO_STREET.get(zid)


def resolve_overlay_source(
    *,
    street: Optional[str] = None,
    path: Optional[Union[str, Path]] = None,
    zone_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Resolve how to load an overlay (street pack name or raw layer paths).

    Returns a dict with either ``street`` (compose via street pack stack) or
    ``layers`` (explicit USDA paths). Raises when nothing can be resolved.
    """
    if path is not None and str(path).strip():
        raw = Path(str(path).strip())
        if raw.is_dir():
            # Directory of a street fixture (…/loopy_lane).
            stem = raw.name
            if (raw / f'{stem}.usda').is_file() or stem in list_street_packs():
                return {'street': stem, 'path': str(raw)}
            raise UsdRuntimeHookError(
                f'overlay path is a directory without street base: {raw}'
            )
        if raw.is_file() and raw.suffix.lower() == '.usda':
            return {'layers': [raw], 'path': str(raw)}
        # Treat as street stem / relative street name.
        stem = raw.name[:-5] if raw.name.endswith('.usda') else raw.name
        if stem in list_street_packs() or (STREETS_DIR / stem).is_dir():
            return {'street': stem, 'path': str(path)}
        raise UsdRuntimeHookError(f'overlay path not found: {path}')

    if street:
        stem = street[:-5] if street.endswith('.usda') else street
        if stem in list_street_packs() or (STREETS_DIR / stem).is_dir():
            return {'street': stem}
        raise UsdRuntimeHookError(f'unknown street overlay: {street!r}')

    mapped = street_for_zone(zone_id)
    if mapped:
        return {'street': mapped, 'zoneId': int(zone_id)}

    cfg_path = _config_get_string(USD_STREET_OVERLAY_PATH, '')
    if cfg_path.strip():
        return resolve_overlay_source(path=cfg_path.strip())

    raise UsdRuntimeHookError(
        'usd street overlay enabled but no street / path / zone mapping'
    )


def load_street_overlay(
    *,
    enabled: Optional[bool] = None,
    street: Optional[str] = None,
    path: Optional[Union[str, Path]] = None,
    pack: Optional[str] = None,
    look: Optional[str] = None,
    zone_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Load a composed street overlay when the feature flag allows it.

    Returns ``None`` when the flag is off (default). When enabled, returns
    a compose stage dict (``seedPollution``, ``spawnStands``, …). Text mode
    only — no ``pxr`` / Hydra.
    """
    if not is_usd_street_overlay_wanted(enabled):
        return None

    look_name = look
    if look_name is None:
        cfg_look = _config_get_string(USD_STREET_OVERLAY_LOOK, '')
        look_name = cfg_look.strip() or None

    source = resolve_overlay_source(
        street=street, path=path, zone_id=zone_id,
    )
    try:
        if source.get('layers'):
            stage = compose_layers(
                source['layers'],
                street=source.get('street'),
                pack=pack,
                look=look_name,
            )
        else:
            stage = compose_street_pack(
                source['street'],
                pack=pack,
                look=look_name or 'polluted',
            )
    except UsdComposeError as exc:
        raise UsdRuntimeHookError(str(exc)) from exc

    stage = dict(stage)
    stage['enabled'] = True
    stage['featureFlag'] = WANT_USD_STREET_OVERLAY
    stage['source'] = {
        k: (str(v) if isinstance(v, Path) else v)
        for k, v in source.items()
    }
    stage['runtimeHookNotes'] = RUNTIME_HOOK_NOTES
    stage['hydra'] = False
    stage['mode'] = stage.get('mode') or 'text'
    return stage


def apply_overlay_metadata(
    overlay: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Pure function: overlay dict → pollution seed + stand list metadata.

    Returns ``None`` when ``overlay`` is ``None`` (flag off / no load).
    Does not touch geom, DNA, Hydra, or reclaim directors.
    """
    if not overlay:
        return None

    stands_raw: Sequence[Dict[str, Any]] = list(
        overlay.get('spawnStands') or []
    )
    stands: List[Dict[str, Any]] = []
    for stand in stands_raw:
        stands.append({
            'name': stand.get('name'),
            'archetype': stand.get('archetype'),
            'standIndex': stand.get('standIndex'),
        })

    seed = overlay.get('seedPollution')
    try:
        seed_f = float(seed) if seed is not None else None
    except (TypeError, ValueError):
        seed_f = None

    zone = overlay.get('zoneId')
    try:
        zone_i = int(zone) if zone is not None else None
    except (TypeError, ValueError):
        zone_i = None

    return {
        'zoneId': zone_i,
        'packId': overlay.get('packId'),
        'hood': overlay.get('hood'),
        'seedPollution': seed_f,
        'spawnStands': stands,
        'standCount': len(stands),
        'look': overlay.get('look'),
        'street': overlay.get('street'),
        'layers': list(overlay.get('layerNames') or []),
        'hydra': False,
        'notes': RUNTIME_HOOK_NOTES,
    }


def try_apply_street_overlay(
    *,
    enabled: Optional[bool] = None,
    street: Optional[str] = None,
    path: Optional[Union[str, Path]] = None,
    pack: Optional[str] = None,
    look: Optional[str] = None,
    zone_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Callsite helper: load overlay (if flag on) and apply metadata.

    Swallows load errors when the flag is off. When the flag is on and
    resolution fails, re-raises ``UsdRuntimeHookError``. Default-off path
    always returns ``None`` without raising.
    """
    if not is_usd_street_overlay_wanted(enabled):
        return None
    overlay = load_street_overlay(
        enabled=True,
        street=street,
        path=path,
        pack=pack,
        look=look,
        zone_id=zone_id,
    )
    return apply_overlay_metadata(overlay)
