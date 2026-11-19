"""OpenUSD foothold for Toon City (authoring / compose → bake or bridge).

Spike package only: ASCII USDA fixtures, headless text parse, and a thin
bridge stub. No Hydra, no gameplay loader hooks, no pxr hard dependency.
"""

from __future__ import annotations

from toontown.usd.bridge import load_fixture
from toontown.usd.validate import validate_fixture

__all__ = (
    'load_fixture',
    'validate_fixture',
)
