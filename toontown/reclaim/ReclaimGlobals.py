"""Tunables for the one-street neighborhood reclaim demo."""

from toontown.toonbase import ToontownGlobals

# Preferred first hood street for the reclaim loop (familiar pathing / art).
DEFAULT_RECLAIM_STREET = ToontownGlobals.LoopyLane

# Session starts partially polluted so fog + tint are readable immediately.
RECLAIM_START_POLLUTION = 0.60

# Pack sizing: POLLUTION_PER_DEFEAT is 0.15 → ~4 defeats clear 0.60.
PACK_SIZE = 3
MAX_PACKS = 4
SPAWN_FORWARD = 8.0
SPAWN_SPACING = 3.0

# Director FSM states (mirrored on client for banner / HUD).
STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_COMPLETE = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_COMPLETE: 'complete',
}

# Client feedback copy.
BANNER_START = 'RECLAIM THIS STREET!'
BANNER_PACK = 'Corrupt pack inbound!'
BANNER_COMPLETE = 'PURITY RESTORED!'
POLLUTION_HINT_FMT = 'Pollution  %.0f%%'
DEMO_HINT = (
    'Reclaim: clear Corrupt Toons with melee (~hackslash 0)  |  '
    '~stopreclaim to end'
)
