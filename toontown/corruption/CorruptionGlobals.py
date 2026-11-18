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

# Per-street ambient corruption look (branch zone ids).
# fog: RGB base; fogExpScale: density multiplier vs CORRUPT_FOG_EXP_MAX
# gradeDrop: how hard render RGB falls with pollution (higher = darker channel)
# propTint: multiply applied to street geom under pollutionPropTint
# Default / Loopy = purple ink wash.
HOOD_POLLUTION_BIAS = {
    # Loopy Lane — classic purple ink fog.
    2200: {
        'id': 'loopy',
        'fog': (0.18, 0.12, 0.22),
        'fogExpScale': 1.0,
        'gradeDrop': (0.42, 0.50, 0.28),
        'propTint': (0.72, 0.62, 0.85),
    },
    # Punchline Place — swampy sludge / gag-gunk green-brown.
    2300: {
        'id': 'punchline',
        'fog': (0.16, 0.20, 0.10),
        'fogExpScale': 1.12,
        'gradeDrop': (0.38, 0.28, 0.48),
        'propTint': (0.78, 0.82, 0.58),
    },
    # Silly Street — hot magenta / black-ink finale bias.
    2100: {
        'id': 'silly',
        'fog': (0.24, 0.06, 0.18),
        'fogExpScale': 1.22,
        'gradeDrop': (0.30, 0.55, 0.35),
        'propTint': (0.88, 0.55, 0.78),
    },
}

_DEFAULT_HOOD_BIAS = HOOD_POLLUTION_BIAS[2200]

# Telegraph / impact presentation (client AV punch; AI timings unchanged).
TELEGRAPH_CHARGE_COLOR = (2.15, 0.25, 2.4, 1.0)
TELEGRAPH_HOLD_COLOR = (1.55, 0.2, 1.85, 1.0)
ATTACK_HIT_FLASH_COLOR = (1.0, 0.55, 1.0, 1.0)
ATTACK_HIT_FLASH_PEAK = 0.55
ATTACK_HIT_FLASH_IN = 0.04
ATTACK_HIT_FLASH_OUT = 0.14
# Existing Toontown SFX — wind-up whoosh + collision thud.
TELEGRAPH_SFX = 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg'
ATTACK_HIT_SFX = 'phase_3.5/audio/sfx/AV_collision.ogg'
TELEGRAPH_SFX_VOLUME = 0.55
ATTACK_HIT_SFX_VOLUME = 0.75

# Ink Overlord finale phase looks (client-readable; AI timings unchanged).
# Phase 1 = rising magenta swell; Phase 2 = crimson unleashed fury.
FINALE_PHASE_LOOK = {
    1: {
        'id': 'rising',
        'telegraphCharge': (2.35, 0.3, 2.65, 1.0),
        'telegraphHold': (1.65, 0.22, 2.0, 1.0),
        'squash': (2.15, 2.15, 0.34),
        'stretch': (0.48, 0.48, 1.95),
        'impactScale': (1.7, 1.7, 0.48),
        'impactColor': (2.4, 0.85, 2.55, 1.0),
        'pulseHot': (0.85, 0.18, 1.05, 1.0),
        'hitFlash': (1.05, 0.4, 1.15, 1.0),
        'hitFlashPeak': 0.72,
        'actorScale': 1.28,
        'nameColor': (1.0, 0.55, 1.0, 1.0),
        'pulseAmp': 0.1,
    },
    2: {
        'id': 'unleashed',
        'telegraphCharge': (2.7, 0.12, 0.28, 1.0),
        'telegraphHold': (2.0, 0.08, 0.18, 1.0),
        'squash': (2.55, 2.55, 0.26),
        'stretch': (0.36, 0.36, 2.35),
        'impactScale': (1.95, 1.95, 0.4),
        'impactColor': (2.6, 0.55, 0.35, 1.0),
        'pulseHot': (1.35, 0.12, 0.22, 1.0),
        'hitFlash': (1.15, 0.18, 0.12, 1.0),
        'hitFlashPeak': 0.9,
        'actorScale': 1.48,
        'nameColor': (1.0, 0.32, 0.22, 1.0),
        'pulseAmp': 0.16,
    },
}

# Phase-transition sting (FOV / flash / render slam).
FINALE_STING_FOV_PUNCH = 18.0
FINALE_STING_FOV_IN = 0.08
FINALE_STING_FOV_OUT = 0.42
FINALE_STING_FLASH_PEAK = 0.92
FINALE_STING_FLASH_COLOR = (1.15, 0.2, 0.55, 1.0)
FINALE_STING_RENDER_PEAK = (1.85, 0.35, 1.15, 1.0)
FINALE_STING_RENDER_HOLD = (1.35, 0.45, 0.75, 1.0)


def finalePhaseLook(phaseIndex):
    """Return presentation dict for Ink Overlord phase, or None."""
    try:
        phase = int(phaseIndex)
    except (TypeError, ValueError):
        return None
    return FINALE_PHASE_LOOK.get(phase)


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


def branchZoneForPollution(zoneId):
    """Map any street/interior zone to its branch (street) id for bias lookup."""
    try:
        z = int(zoneId)
    except (TypeError, ValueError):
        return 2200
    branch = z - (z % 100)
    if z % 1000 >= 500:
        branch -= 500
    return branch


def hoodPollutionBias(zoneId):
    """Return fog/grade/prop bias dict for a zone (falls back to Loopy)."""
    return HOOD_POLLUTION_BIAS.get(branchZoneForPollution(zoneId), _DEFAULT_HOOD_BIAS)


def hoodFogColor(zoneId, level):
    """Fog RGB scaled by pollution level for this hood."""
    bias = hoodPollutionBias(zoneId)
    fog = bias['fog']
    lvl = clampPollution(level)
    return (
        fog[0] * (0.7 + 0.3 * lvl),
        fog[1] * (0.75 + 0.25 * lvl),
        fog[2],
    )


def hoodFogExpDensity(zoneId, level):
    """Exponential fog density for this hood at pollution level."""
    bias = hoodPollutionBias(zoneId)
    return CORRUPT_FOG_EXP_MAX * float(bias.get('fogExpScale', 1.0)) * clampPollution(level)


def hoodColorGrade(zoneId, level):
    """Render color-scale RGB (alpha 1) for hood-specific sickly grade."""
    bias = hoodPollutionBias(zoneId)
    drop = bias['gradeDrop']
    lvl = clampPollution(level)
    return (
        1.0 - (drop[0] * lvl),
        1.0 - (drop[1] * lvl),
        1.0 - (drop[2] * lvl),
    )


def hoodPropTint(zoneId, level):
    """Street-geom multiply RGB for pollutionPropTint (1,1,1 when pure)."""
    lvl = clampPollution(level)
    if lvl <= POLLUTION_PURE:
        return (1.0, 1.0, 1.0)
    bias = hoodPollutionBias(zoneId)
    target = bias['propTint']
    # Lerp white → hood prop tint by pollution.
    return (
        1.0 - (1.0 - target[0]) * lvl,
        1.0 - (1.0 - target[1]) * lvl,
        1.0 - (1.0 - target[2]) * lvl,
    )
