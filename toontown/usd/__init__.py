"""OpenUSD foothold for Toon City (authoring / compose → bake or bridge).

ASCII USDA fixtures, prim conventions (``schemas.md``), headless
validators, bridge stub, street-pack compose, character kits, and
offline BAM/DNA bake-plan stub. No Hydra, no gameplay loader hooks,
no pxr hard dependency.
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
from toontown.usd.validate import validate_fixture


def bake_fixture(*args: Any, **kwargs: Any):
    """Lazy re-export so ``python -m toontown.usd.bake_bam`` stays clean."""
    from toontown.usd.bake_bam import bake_fixture as _bake_fixture
    return _bake_fixture(*args, **kwargs)


__all__ = (
    'bake_fixture',
    'compose_loopy_lane',
    'compose_street_pack',
    'ink_smudge_kit',
    'load_fixture',
    'load_kit',
    'plan_from_fixture',
    'plan_to_json',
    'validate_fixture',
    'validate_kit',
)
