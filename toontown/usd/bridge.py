"""Thin USD → bake-plan bridge stub (headless, no Panda display).

Reads ASCII ``.usda`` fixtures under ``toontown/usd/fixtures/`` and
returns a bake-plan dict for CI / tooling. Optional ``pxr`` open is a
best-effort enrich path and never required for default CI.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional

FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures'

# Prim kind markers used in spike fixtures (customData / typeName comments).
_KIND_MARKERS = (
    'TcProp',
    'TcStreetRoot',
    'TcSpawnStand',
    'TcReclaimVolume',
)

_CUSTOM_DATA_RE = re.compile(
    r'customData\s*=\s*\{(?P<body>.*?)\}',
    re.DOTALL,
)
_KV_RE = re.compile(
    r'(?:string|int|float|double|bool|token)\s+'
    r'(?:tc:)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*'
    r'(?P<val>"[^"]*"|\'[^\']*\'|[^,\n\}]+)',
)
_DEF_RE = re.compile(
    r'\bdef\s+(?:Xform|Scope|Over|Prim)\s+"([^"]+)"',
)


def fixtures_dir() -> Path:
    return FIXTURES_DIR


def list_fixtures() -> list[str]:
    """Return fixture stem names (no extension) available for load_fixture."""
    if not FIXTURES_DIR.is_dir():
        return []
    return sorted(p.stem for p in FIXTURES_DIR.glob('*.usda'))


def resolve_fixture(name: str) -> Path:
    """Resolve a fixture path by stem or filename.

    Raises FileNotFoundError when the fixture is missing.
    """
    stem = name[:-5] if name.endswith('.usda') else name
    path = FIXTURES_DIR / f'{stem}.usda'
    if not path.is_file():
        raise FileNotFoundError(f'USD fixture not found: {path}')
    return path


def _strip_quotes(raw: str) -> str:
    text = raw.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        return text[1:-1]
    return text


def _coerce(raw: str) -> Any:
    text = _strip_quotes(raw.strip())
    low = text.lower()
    if low in ('true', 'false'):
        return low == 'true'
    try:
        if '.' in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def parse_usda_text(text: str) -> Dict[str, Any]:
    """Pure-Python skim of ASCII USDA for spike metadata.

    Collects prim def names, kind markers, and flattened customData keys
    (``tc:`` prefix optional in source). Does not require ``pxr``.
    """
    kinds = [k for k in _KIND_MARKERS if k in text]
    prims = _DEF_RE.findall(text)
    custom: Dict[str, Any] = {}
    for match in _CUSTOM_DATA_RE.finditer(text):
        body = match.group('body')
        for kv in _KV_RE.finditer(body):
            key = kv.group('key')
            custom[key] = _coerce(kv.group('val'))
    return {
        'kinds': kinds,
        'prims': prims,
        'customData': custom,
        'ascii': True,
    }


def _try_pxr_open(path: Path) -> Optional[Dict[str, Any]]:
    """Optional deeper open when OpenUSD Python bindings are installed."""
    try:
        from pxr import Usd  # type: ignore
    except Exception:
        return None
    try:
        stage = Usd.Stage.Open(str(path))
        if stage is None:
            return {'pxrOpen': False, 'error': 'Usd.Stage.Open returned None'}
        return {
            'pxrOpen': True,
            'rootLayer': stage.GetRootLayer().identifier,
            'primCount': len(list(stage.Traverse())),
        }
    except Exception as exc:  # pragma: no cover - env-specific
        return {'pxrOpen': False, 'error': str(exc)}


def load_fixture(name: str) -> Dict[str, Any]:
    """Load a fixture and return a bake-plan dict (no display / no Panda).

    Always includes ``bamPath``, ``zoneId``, and ``packId`` keys (values may
    be ``None`` when the fixture does not declare them). Text mode works
    without ``pxr``; when ``pxr`` is importable, ``pxr`` metadata is attached.
    """
    path = resolve_fixture(name)
    text = path.read_text(encoding='utf-8')
    if '\x00' in text:
        raise ValueError(f'Fixture must be ASCII USDA text: {path.name}')
    parsed = parse_usda_text(text)
    custom = parsed['customData']

    bam_path = custom.get('bamPath')
    zone_id = custom.get('zoneId')
    pack_id = custom.get('packId')

    plan: Dict[str, Any] = {
        'name': path.stem,
        'path': str(path),
        'bamPath': bam_path,
        'zoneId': zone_id,
        'packId': pack_id,
        'kinds': list(parsed['kinds']),
        'prims': list(parsed['prims']),
        'customData': dict(custom),
        'mode': 'text',
    }
    pxr_info = _try_pxr_open(path)
    if pxr_info is not None:
        plan['pxr'] = pxr_info
        if pxr_info.get('pxrOpen'):
            plan['mode'] = 'pxr'
    return plan
