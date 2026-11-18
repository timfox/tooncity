"""Shared constants for pollution and corrupt toon enemies."""

# Pollution scalar: 0.0 = pure neighborhood, 1.0 = fully polluted.
POLLUTION_PURE = 0.0
POLLUTION_FULL = 1.0
POLLUTION_DEFAULT = POLLUTION_PURE

# Fixed-point helper matching DC uint16/1000(0-1).
POLLUTION_SCALE = 1000

# Default spawn / combat values.
CORRUPT_TOON_DEFAULT_HP = 30
CORRUPT_TOON_DEFAULT_NAME = 'Corrupt Toon'

# Defeating one corrupt toon reduces local pollution by this amount.
# Slice 3 reclaim loop will tune pack sizes against this contribution.
POLLUTION_PER_DEFEAT = 0.15

# Magic-word pollute/purify default step when no amount is given.
POLLUTION_STEP_DEFAULT = 0.25

# Chase / aggro / telegraphed melee (Depth D2).
AI_TICK_DT = 0.25
AGGRO_RANGE = 35.0
MELEE_RANGE = 4.5
ATTACK_HIT_RANGE = 5.5
CHASE_SPEED = 9.0
ATTACK_TELEGRAPH_DELAY = 0.55
ATTACK_DAMAGE = 2
ATTACK_COOLDOWN = 1.75
DEFEAT_DELETE_DELAY = 0.85

# Visual ink / sickly palette (not classic cog gray).
CORRUPT_TINT = (0.22, 0.05, 0.32, 0.92)
CORRUPT_TINT_HOT = (0.55, 0.12, 0.75, 1.0)
CORRUPT_ARM_TINT = (0.12, 0.02, 0.18, 0.78)
# DNA Actor base multiply — keeps silhouette readable as ink-black toon.
CORRUPT_ACTOR_TINT = (0.18, 0.06, 0.28, 1.0)
CORRUPT_ACTOR_SCALE = 1.08
CORRUPT_FOG_COLOR = (0.18, 0.12, 0.22)
CORRUPT_FOG_EXP_MAX = 0.012


def clampPollution(level):
    """Clamp a pollution scalar into [0, 1]."""
    try:
        value = float(level)
    except (TypeError, ValueError):
        return POLLUTION_PURE
    if value < POLLUTION_PURE:
        return POLLUTION_PURE
    if value > POLLUTION_FULL:
        return POLLUTION_FULL
    return value


def pollutionToNet(level):
    """Encode 0..1 pollution for DC uint16/1000."""
    return int(round(clampPollution(level) * POLLUTION_SCALE))


def pollutionFromNet(netValue):
    """Decode DC uint16/1000 into 0..1 pollution."""
    return clampPollution(float(netValue) / float(POLLUTION_SCALE))
