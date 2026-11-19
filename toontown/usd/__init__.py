"""OpenUSD foothold for Toon City (authoring / compose → bake or bridge).

ASCII USDA fixtures, prim conventions (``schemas.md``), headless
validators, bridge stub, street-pack compose, character kits, combat
FX socket → CorruptionGlobals map, offline BAM/DNA bake-plan stub, and
feature-flagged SafeZone/Town runtime overlay hook (metadata only).
No Hydra, no pxr hard dependency.
"""

from __future__ import annotations

from typing import Any

from toontown.usd.bake_plan import plan_from_fixture, plan_to_json
from toontown.usd.bridge import load_fixture
from toontown.usd.character_kit import (
    ink_smudge_kit,
    load_kit,
    validate_kit,
)
from toontown.usd.compose import compose_loopy_lane, compose_street_pack
from toontown.usd.fx_sockets import (
    load_fx_sockets,
    telegraph_sockets,
    validate_fx_fixture,
)
from toontown.usd.runtime_hook import (
    apply_overlay_metadata,
    load_street_overlay,
    try_apply_street_overlay,
)
from toontown.usd.validate import validate_fixture


def bake_fixture(*args: Any, **kwargs: Any):
    """Lazy re-export so ``python -m toontown.usd.bake_bam`` stays clean."""
    from toontown.usd.bake_bam import bake_fixture as _bake_fixture
    return _bake_fixture(*args, **kwargs)


__all__ = (
    'apply_overlay_metadata',
    'bake_fixture',
    'compose_loopy_lane',
    'compose_street_pack',
    'ink_smudge_kit',
    'load_fixture',
    'load_fx_sockets',
    'load_kit',
    'load_street_overlay',
    'plan_from_fixture',
    'plan_to_json',
    'telegraph_sockets',
    'try_apply_street_overlay',
    'validate_fixture',
    'validate_fx_fixture',
    'validate_kit',
)
