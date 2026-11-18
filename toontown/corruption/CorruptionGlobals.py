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

# Archetypes — Smudge melee, Brute spit tank, Balloon Snare zip/lash.
ARCHETYPE_INK = 0
ARCHETYPE_BRUTE = 1
ARCHETYPE_SNARE = 2
ARCHETYPE_STATS = {
    ARCHETYPE_INK: {
        'name': 'Ink Smudge',
        'hpScale': 1.0,
        'chaseSpeed': 9.0,
        'meleeRange': 4.5,
        'attackHitRange': 5.5,
        'attackDamage': 2,
        'telegraphDelay': 0.55,
        'attackCooldown': 1.75,
        'actorScale': 1.08,
        'actorTint': (0.18, 0.06, 0.28, 1.0),
    },
    ARCHETYPE_BRUTE: {
        'name': 'Sludge Brute',
        'hpScale': 1.75,
        'chaseSpeed': 5.2,
        'meleeRange': 6.0,
        'attackHitRange': 11.0,  # longer spit reach
        'attackDamage': 4,
        'telegraphDelay': 0.9,
        'attackCooldown': 2.35,
        'actorScale': 1.38,
        'actorTint': (0.12, 0.28, 0.1, 1.0),
    },
    # Punchline zip-flier: fragile balloon that lashes with a rubber-hose string.
    ARCHETYPE_SNARE: {
        'name': 'Balloon Snare',
        'hpScale': 0.7,
        'chaseSpeed': 13.5,
        'meleeRange': 3.8,
        'attackHitRange': 7.2,  # string-lash reach
        'attackDamage': 2,
        'telegraphDelay': 0.38,
        'attackCooldown': 1.35,
        'actorScale': 0.82,
        'actorTint': (0.55, 0.22, 0.08, 1.0),
    },
}


def normalizeArchetype(archetype):
    """Clamp unknown ids to Ink Smudge."""
    try:
        value = int(archetype)
    except (TypeError, ValueError):
        return ARCHETYPE_INK
    if value in ARCHETYPE_STATS:
        return value
    return ARCHETYPE_INK


def archetypeStats(archetypeId):
    return ARCHETYPE_STATS[normalizeArchetype(archetypeId)]


def archetypeDefaultHp(archetype):
    """Base HP before DistributedCorruptToonAI applies hpScale."""
    stats = archetypeStats(archetype)
    # Prefer explicit default when present; else use global base.
    if 'defaultHp' in stats:
        return int(stats['defaultHp'])
    return CORRUPT_TOON_DEFAULT_HP


def archetypeDefaultName(archetype):
    return str(archetypeStats(archetype).get('name', CORRUPT_TOON_DEFAULT_NAME))


ARCHETYPE_NAMES = {
    ARCHETYPE_INK: 'Ink Smudge',
    ARCHETYPE_BRUTE: 'Sludge Brute',
    ARCHETYPE_SNARE: 'Balloon Snare',
}

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
# Planar radius for i-frame near-miss sparkle (outside hit, still "almost").
ATTACK_NEAR_MISS_RANGE = 8.0
CHASE_SPEED = 9.0
ATTACK_TELEGRAPH_DELAY = 0.55
ATTACK_DAMAGE = 2
ATTACK_COOLDOWN = 1.75
# Client death pop (~0.4s body + ~0.45s splat) must finish before AI delete.
DEFEAT_DELETE_DELAY = 0.95

# Visual ink / sickly palette (not classic cog gray).
CORRUPT_TINT = (0.22, 0.05, 0.32, 0.92)
CORRUPT_TINT_HOT = (0.55, 0.12, 0.75, 1.0)
CORRUPT_ARM_TINT = (0.12, 0.02, 0.18, 0.78)
# DNA Actor base multiply — keeps silhouette readable as ink-black toon.
CORRUPT_ACTOR_TINT = (0.18, 0.06, 0.28, 1.0)
CORRUPT_ACTOR_SCALE = 1.08
CORRUPT_FOG_COLOR = (0.18, 0.12, 0.22)
# Peak exponential fog density at pollution 1.0 (readable street ink haze).
CORRUPT_FOG_EXP_MAX = 0.022

# Density ramp: presented fog/haze lerps toward zone pollution as packs rise/clear.
# Ease-in curve (>1) keeps low corruption mild and high corruption thick.
POLLUTION_FOG_DENSITY_CURVE = 1.35
POLLUTION_FOG_RAMP_SEC = 0.55
POLLUTION_FOG_CLEAR_SEC = 0.9
POLLUTION_FOG_SNAP_DELTA = 0.02
# Fullscreen aspect2d ink wash (behind purity burst bins 56–60).
POLLUTION_HAZE_ALPHA_MAX = 0.30
POLLUTION_HAZE_BIN = 25

# Purity-complete fog cream dissolve — sunny cream/pastel lift of street fog
# when purityRestoreFx fires. Matches POLLUTION_FOG_CLEAR_SEC density ramp
# (#38) + StreetSparkle chip/fleck patterns. Not ink; no KH branding.
# FOG_CREAM_DISSOLVE_ENABLED = False drops cream tint + overlay only;
# density clear ramp still runs.
FOG_CREAM_DISSOLVE_ENABLED = True
FOG_CREAM_DISSOLVE_SEC = POLLUTION_FOG_CLEAR_SEC
FOG_CREAM_DISSOLVE_COLOR = (1.0, 0.97, 0.82)  # sunny cream fog tint
FOG_CREAM_DISSOLVE_HAZE_PEAK = 0.20
FOG_CREAM_DISSOLVE_BIN = 26  # above ink haze (25), below street sparkle (50)
FOG_CREAM_DISSOLVE_ORIGIN = (0.0, 0.0, -0.28)
FOG_CREAM_DISSOLVE_SHIMMER_IN_SEC = 0.08
FOG_CREAM_DISSOLVE_SHIMMER_HOLD_SEC = 0.22
FOG_CREAM_DISSOLVE_SHIMMER_OUT_SEC = 0.58
FOG_CREAM_DISSOLVE_FLECK_COUNT = 14
FOG_CREAM_DISSOLVE_FLECK_SIZE = 0.024
FOG_CREAM_DISSOLVE_FLECK_RISE = 0.78
FOG_CREAM_DISSOLVE_FLECK_SPREAD = 1.40
FOG_CREAM_DISSOLVE_FLECK_SEC = 0.68
FOG_CREAM_DISSOLVE_FLECK_COLOR = (1.0, 0.98, 0.72, 0.95)
FOG_CREAM_DISSOLVE_FLECK_END_COLOR = (1.0, 0.94, 0.55, 0.0)
FOG_CREAM_DISSOLVE_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.95),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.9),    # soft peach pastel
    (0.98, 0.94, 0.88, 0.88),  # warm parchment
)

# Purity-complete hood corruption tint cream fade — PollutionPropTint geom
# colorScale lifts sunny cream/pastel when purityRestoreFx fires (hood tint
# #13). Matches FOG_CREAM_DISSOLVE_* timing / cream palette (#100). Not ink;
# no KH branding. HOOD_TINT_CREAM_FADE_ENABLED = False snaps clear like before.
HOOD_TINT_CREAM_FADE_ENABLED = True
HOOD_TINT_CREAM_FADE_SEC = POLLUTION_FOG_CLEAR_SEC
HOOD_TINT_CREAM_FADE_COLOR = FOG_CREAM_DISSOLVE_COLOR  # sunny cream geom lift
HOOD_TINT_CREAM_FADE_HAZE_PEAK = 0.12  # soft veil under fog dissolve (26)
HOOD_TINT_CREAM_FADE_BIN = 27  # above fog dissolve (26), below street wash (28)
HOOD_TINT_CREAM_FADE_ORIGIN = (0.0, 0.0, -0.18)
HOOD_TINT_CREAM_FADE_SHIMMER_IN_SEC = 0.07
HOOD_TINT_CREAM_FADE_SHIMMER_HOLD_SEC = 0.18
HOOD_TINT_CREAM_FADE_SHIMMER_OUT_SEC = 0.55
HOOD_TINT_CREAM_FADE_FLECK_COUNT = 8
HOOD_TINT_CREAM_FADE_FLECK_SIZE = 0.018
HOOD_TINT_CREAM_FADE_FLECK_RISE = 0.55
HOOD_TINT_CREAM_FADE_FLECK_SPREAD = 1.10
HOOD_TINT_CREAM_FADE_FLECK_SEC = 0.58
HOOD_TINT_CREAM_FADE_FLECK_COLOR = (1.0, 0.98, 0.78, 0.88)
HOOD_TINT_CREAM_FADE_FLECK_END_COLOR = (1.0, 0.95, 0.62, 0.0)
HOOD_TINT_CREAM_FADE_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.90),  # sunny cream
    (1.0, 0.94, 0.70, 0.86),  # butter pastel
    (1.0, 0.90, 0.80, 0.84),  # soft peach
)

# Street-entry rubber-hose ink vignette (PlayEntry on polluted ACTS streets).
# Edge darken flashes in, then fades as the tip bar appears — not a KH sting.
ENTRY_VIGNETTE_IN_SEC = 0.10
ENTRY_VIGNETTE_HOLD_SEC = 0.16
ENTRY_VIGNETTE_OUT_SEC = 0.55
ENTRY_VIGNETTE_TIP_DELAY_SEC = 0.22
ENTRY_VIGNETTE_TIP_FADE_SEC = 0.38
ENTRY_VIGNETTE_PEAK_ALPHA = 0.78
ENTRY_VIGNETTE_EDGE = 0.42  # strip thickness in aspect2d units
ENTRY_VIGNETTE_BIN = 48  # above haze (25), below handoff/celebration (60+)
# Minimum presented pollution to fire the entry vignette (skip clean streets).
ENTRY_VIGNETTE_MIN_POLLUTION = 0.08
# Fallback ink when hood fog bias is unavailable.
ENTRY_VIGNETTE_INK = (0.06, 0.02, 0.10, 1.0)

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
# Ink Smudge = purple melee; Sludge Brute = green spit; Balloon Snare = amber lash.
TELEGRAPH_CHARGE_COLOR = (2.15, 0.25, 2.4, 1.0)
TELEGRAPH_HOLD_COLOR = (1.55, 0.2, 1.85, 1.0)

# Ink Smudge telegraph ink-fist pop — short rubber-hose purple melee charge on
# announceAttackTelegraph (client only). Distinct from shared TELEGRAPH_INK_DRIP_*
# drips and from Brute spit / Snare string silhouettes: punch-fist ink blob.
SMUDGE_TELEGRAPH_INK_LOOK = {
    'id': 'purple-ink-fist',
    'lift': 2.2,
    'scale': 1.0,
    'peakAlpha': 0.96,
    'fadeInSec': 0.04,
    'holdSec': 0.15,
    'fadeOutSec': 0.22,
    'squash': (1.75, 1.0, 0.38),
    'stretch': (0.7, 1.0, 1.85),
    'squashSec': 0.05,
    'stretchSec': 0.11,
    'settleSec': 0.13,
    'wobbleDeg': 14.0,
    'fistHalf': 0.36,
    'rimScale': 1.32,
    'hotHalf': 0.13,
    'fistColor': (0.55, 0.18, 0.95, 1.0),
    'rimColor': (1.15, 0.45, 1.55, 1.0),
    'flashColor': (1.35, 0.45, 1.7, 1.0),
    'smearCount': 4,
    'smearHalf': 0.11,
    'smearSec': 0.28,
    'smearSpread': 0.95,
    'smearColor': (0.75, 0.28, 1.15, 0.9),
    'binSort': 42,
}

# Ink Smudge hit/death ink splash — cheap rubber-hose purple splash for swarm
# readability (client only). Composes with SmudgeInkTelegraphFx / CorruptDeathPopFx
# / IdleInkDripFx palettes via SmudgeInkSplashFx.smudgeInkSplashLook. Hit is the
# cheap pack-scan cue; death layers a slightly larger splash with DeathPop.
# Hit path also arms SmudgeHitCreamWashFx (soft cream wash — see
# SMUDGE_HIT_CREAM_WASH_* below).
SMUDGE_INK_SPLASH_LOOK = {
    'hit': {
        'id': 'smudge-hit-splash',
        'lift': 2.05,
        'peakAlpha': 0.94,
        'splatHalf': 0.26,
        'splatPeak': 1.55,
        'splatSec': 0.18,
        'rimScale': 1.26,
        'smearCount': 3,
        'smearHalf': 0.09,
        'smearSec': 0.2,
        'smearSpread': 0.75,
        'fleckCount': 2,
        'fleckHalf': 0.11,
        'fleckDist': 1.05,
        'fleckLift': 0.4,
        'fleckSec': 0.22,
        'dripCount': 1,
        'dripHalf': 0.08,
        'dripSpread': 0.22,
        'dripFall': 0.7,
        'dripSec': 0.32,
        'dripStagger': 0.03,
        'binSort': 45,
    },
    'death': {
        'id': 'smudge-death-splash',
        'lift': 1.55,
        'peakAlpha': 0.97,
        'splatHalf': 0.38,
        'splatPeak': 2.05,
        'splatSec': 0.26,
        'rimScale': 1.35,
        'smearCount': 4,
        'smearHalf': 0.12,
        'smearSec': 0.28,
        'smearSpread': 1.15,
        'fleckCount': 4,
        'fleckHalf': 0.16,
        'fleckDist': 1.75,
        'fleckLift': 0.7,
        'fleckSec': 0.3,
        'dripCount': 2,
        'dripHalf': 0.1,
        'dripSpread': 0.35,
        'dripFall': 1.05,
        'dripSec': 0.42,
        'dripStagger': 0.04,
        'binSort': 46,
    },
}

# Sludge Brute hit/death sludge splash — cheap rubber-hose green splash so
# tagged/popped Brutes stay scannable (client only). Composes with
# BruteSpitTelegraphFx / CorruptDeathPopFx / IdleInkDripFx palettes via
# BruteSludgeSplashFx.bruteSludgeSplashLook. Hit is the cheap scan cue;
# death layers a slightly larger splash with DeathPop. Slightly bulkier than
# SMUDGE_INK_SPLASH_LOOK to match Brute silhouette.
BRUTE_SLUDGE_SPLASH_LOOK = {
    'hit': {
        'id': 'brute-hit-splash',
        'lift': 2.25,
        'peakAlpha': 0.95,
        'splatHalf': 0.32,
        'splatPeak': 1.7,
        'splatSec': 0.2,
        'rimScale': 1.28,
        'smearCount': 3,
        'smearHalf': 0.11,
        'smearSec': 0.22,
        'smearSpread': 0.9,
        'fleckCount': 3,
        'fleckHalf': 0.13,
        'fleckDist': 1.25,
        'fleckLift': 0.35,
        'fleckSec': 0.24,
        'dripCount': 2,
        'dripHalf': 0.1,
        'dripSpread': 0.28,
        'dripFall': 0.85,
        'dripSec': 0.36,
        'dripStagger': 0.03,
        'binSort': 45,
    },
    'death': {
        'id': 'brute-death-splash',
        'lift': 1.75,
        'peakAlpha': 0.98,
        'splatHalf': 0.45,
        'splatPeak': 2.25,
        'splatSec': 0.28,
        'rimScale': 1.38,
        'smearCount': 4,
        'smearHalf': 0.14,
        'smearSec': 0.3,
        'smearSpread': 1.3,
        'fleckCount': 5,
        'fleckHalf': 0.18,
        'fleckDist': 2.0,
        'fleckLift': 0.65,
        'fleckSec': 0.32,
        'dripCount': 3,
        'dripHalf': 0.12,
        'dripSpread': 0.42,
        'dripFall': 1.2,
        'dripSec': 0.46,
        'dripStagger': 0.04,
        'binSort': 46,
    },
}

# Balloon Snare hit/death string-snap splash — cheap rubber-hose amber splash
# so tagged/popped Snares stay scannable (client only). Composes with
# BalloonSnareTelegraphFx / CorruptDeathPopFx / IdleInkDripFx palettes via
# SnareStringSnapSplashFx.snareStringSnapSplashLook. Hit is the cheap scan
# cue; death layers a slightly larger splash with DeathPop. Snappier / thinner
# than SMUDGE_INK_SPLASH_LOOK to match fragile zip-flier silhouette; horizontal
# smear bias reads as a rubber string break (not ink blob / sludge gob).
SNARE_STRING_SNAP_SPLASH_LOOK = {
    'hit': {
        'id': 'snare-hit-splash',
        'lift': 1.95,
        'peakAlpha': 0.94,
        'splatHalf': 0.24,
        'splatPeak': 1.5,
        'splatSec': 0.16,
        'rimScale': 1.3,
        'smearCount': 3,
        'smearHalf': 0.08,
        'smearSec': 0.18,
        'smearSpread': 0.95,
        'fleckCount': 2,
        'fleckHalf': 0.1,
        'fleckDist': 1.15,
        'fleckLift': 0.45,
        'fleckSec': 0.2,
        'dripCount': 1,
        'dripHalf': 0.07,
        'dripSpread': 0.26,
        'dripFall': 0.72,
        'dripSec': 0.3,
        'dripStagger': 0.03,
        'binSort': 45,
    },
    'death': {
        'id': 'snare-death-splash',
        'lift': 1.4,
        'peakAlpha': 0.97,
        'splatHalf': 0.36,
        'splatPeak': 2.0,
        'splatSec': 0.24,
        'rimScale': 1.36,
        'smearCount': 4,
        'smearHalf': 0.11,
        'smearSec': 0.26,
        'smearSpread': 1.25,
        'fleckCount': 4,
        'fleckHalf': 0.14,
        'fleckDist': 1.85,
        'fleckLift': 0.75,
        'fleckSec': 0.28,
        'dripCount': 2,
        'dripHalf': 0.09,
        'dripSpread': 0.38,
        'dripFall': 1.0,
        'dripSec': 0.4,
        'dripStagger': 0.04,
        'binSort': 46,
    },
}

# Ink Overlord hit/death magenta ink splash — cheap rubber-hose magenta /
# crimson splash so tagged/popped Overlord reads as boss, not street Smudge
# (client only). Composes with OverlordTelegraphCrownFx /
# OverlordPhaseInkRainFx / CorruptDeathPopFx / IdleInkDripFx palettes via
# OverlordMagentaInkSplashFx.overlordMagentaInkSplashLook; phase charge
# retints P1 magenta vs P2 crimson. Bulkier than SMUDGE_INK_SPLASH_LOOK /
# BRUTE_SLUDGE_SPLASH_LOOK to match boss silhouette. Hit is the cheap scan
# cue; death layers a slightly larger splash with DeathPop.
OVERLORD_MAGENTA_INK_SPLASH_LOOK = {
    'hit': {
        'id': 'overlord-hit-splash',
        'lift': 2.55,
        'peakAlpha': 0.96,
        'splatHalf': 0.36,
        'splatPeak': 1.85,
        'splatSec': 0.22,
        'rimScale': 1.32,
        'smearCount': 4,
        'smearHalf': 0.12,
        'smearSec': 0.24,
        'smearSpread': 1.05,
        'fleckCount': 4,
        'fleckHalf': 0.15,
        'fleckDist': 1.55,
        'fleckLift': 0.55,
        'fleckSec': 0.26,
        'dripCount': 2,
        'dripHalf': 0.1,
        'dripSpread': 0.34,
        'dripFall': 0.95,
        'dripSec': 0.38,
        'dripStagger': 0.03,
        'binSort': 46,
    },
    'death': {
        'id': 'overlord-death-splash',
        'lift': 2.05,
        'peakAlpha': 0.98,
        'splatHalf': 0.52,
        'splatPeak': 2.45,
        'splatSec': 0.3,
        'rimScale': 1.4,
        'smearCount': 5,
        'smearHalf': 0.15,
        'smearSec': 0.32,
        'smearSpread': 1.45,
        'fleckCount': 6,
        'fleckHalf': 0.2,
        'fleckDist': 2.25,
        'fleckLift': 0.85,
        'fleckSec': 0.34,
        'dripCount': 3,
        'dripHalf': 0.13,
        'dripSpread': 0.48,
        'dripFall': 1.35,
        'dripSec': 0.48,
        'dripStagger': 0.04,
        'binSort': 47,
    },
}

# Soft cream wash pulse after Overlord magenta ink splash (hit only) —
# aspect2d veil after OverlordMagentaInkSplashFx (#88) smack (client only).
# Matches CorruptTelegraphCreamWashFx (#157) / CorruptSilhouetteCreamWashFx
# (#153) / CorruptDeathCreamWashFx (#119) two-beat grammar. Delay composed
# via OverlordHitCreamWashFx.overlordHitCreamWashLook →
# overlordMagentaInkSplashLook('hit'). Soft cream/pastel contrast against
# magenta / crimson ink. OVERLORD_HIT_CREAM_WASH_ENABLED = False drops wash
# only (magenta splash stays). Death path keeps splash + death cream wash.
OVERLORD_HIT_CREAM_WASH_ENABLED = True
OVERLORD_HIT_CREAM_WASH_DELAY_SEC = 0.16  # fallback; look prefers splash compose
OVERLORD_HIT_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
OVERLORD_HIT_CREAM_WASH_PEAK = 0.08  # quieter than death (0.14) / melee (0.10);
# above telegraph (0.065) so boss hit reads against magenta ink
OVERLORD_HIT_CREAM_WASH_MID = 0.045
OVERLORD_HIT_CREAM_WASH_IN_SEC = 0.06
OVERLORD_HIT_CREAM_WASH_PULSE_SEC = 0.10
OVERLORD_HIT_CREAM_WASH_HOLD_SEC = 0.08
OVERLORD_HIT_CREAM_WASH_OUT_SEC = 0.38
OVERLORD_HIT_CREAM_WASH_BIN = 40  # soft veil under magenta splash (46)
OVERLORD_HIT_CREAM_WASH_LOOK = {
    'id': 'overlord-hit-cream-wash',
    # delaySec composed with overlordMagentaInkSplashLook('hit') when played.
    'delaySec': OVERLORD_HIT_CREAM_WASH_DELAY_SEC,
    'delayScale': 0.72,
    'color': OVERLORD_HIT_CREAM_WASH_COLOR,
    'peak': OVERLORD_HIT_CREAM_WASH_PEAK,
    'mid': OVERLORD_HIT_CREAM_WASH_MID,
    'inSec': OVERLORD_HIT_CREAM_WASH_IN_SEC,
    'pulseSec': OVERLORD_HIT_CREAM_WASH_PULSE_SEC,
    'holdSec': OVERLORD_HIT_CREAM_WASH_HOLD_SEC,
    'outSec': OVERLORD_HIT_CREAM_WASH_OUT_SEC,
    'binSort': OVERLORD_HIT_CREAM_WASH_BIN,
}

# Soft cream wash pulse after Smudge purple ink splash (hit only) —
# aspect2d veil after SmudgeInkSplashFx (#75) smack (client only).
# Matches OverlordHitCreamWashFx (#161) / CorruptTelegraphCreamWashFx (#157)
# / CorruptSilhouetteCreamWashFx (#153) / CorruptDeathCreamWashFx (#119)
# two-beat grammar. Delay composed via SmudgeHitCreamWashFx.smudgeHitCreamWashLook
# → smudgeInkSplashLook('hit'). Soft cream/pastel contrast against purple ink.
# SMUDGE_HIT_CREAM_WASH_ENABLED = False drops wash only (purple splash stays).
# Death path keeps splash + death cream wash. Street Smudge only (not Overlord).
SMUDGE_HIT_CREAM_WASH_ENABLED = True
SMUDGE_HIT_CREAM_WASH_DELAY_SEC = 0.13  # fallback; look prefers splash compose
SMUDGE_HIT_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SMUDGE_HIT_CREAM_WASH_PEAK = 0.07  # quieter than death (0.14) / melee (0.10) /
# overlord hit (0.08); above telegraph (0.065) so Smudge hit reads vs purple ink
SMUDGE_HIT_CREAM_WASH_MID = 0.04
SMUDGE_HIT_CREAM_WASH_IN_SEC = 0.06
SMUDGE_HIT_CREAM_WASH_PULSE_SEC = 0.10
SMUDGE_HIT_CREAM_WASH_HOLD_SEC = 0.08
SMUDGE_HIT_CREAM_WASH_OUT_SEC = 0.38
SMUDGE_HIT_CREAM_WASH_BIN = 40  # soft veil under purple splash (45)
SMUDGE_HIT_CREAM_WASH_LOOK = {
    'id': 'smudge-hit-cream-wash',
    # delaySec composed with smudgeInkSplashLook('hit') when played.
    'delaySec': SMUDGE_HIT_CREAM_WASH_DELAY_SEC,
    'delayScale': 0.72,
    'color': SMUDGE_HIT_CREAM_WASH_COLOR,
    'peak': SMUDGE_HIT_CREAM_WASH_PEAK,
    'mid': SMUDGE_HIT_CREAM_WASH_MID,
    'inSec': SMUDGE_HIT_CREAM_WASH_IN_SEC,
    'pulseSec': SMUDGE_HIT_CREAM_WASH_PULSE_SEC,
    'holdSec': SMUDGE_HIT_CREAM_WASH_HOLD_SEC,
    'outSec': SMUDGE_HIT_CREAM_WASH_OUT_SEC,
    'binSort': SMUDGE_HIT_CREAM_WASH_BIN,
}
ATTACK_HIT_FLASH_COLOR = (1.0, 0.55, 1.0, 1.0)
ATTACK_HIT_FLASH_PEAK = 0.55
ATTACK_HIT_FLASH_IN = 0.04
ATTACK_HIT_FLASH_OUT = 0.14
# Existing Toontown SFX — wind-up whoosh + collision thud.
TELEGRAPH_SFX = 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg'
ATTACK_HIT_SFX = 'phase_3.5/audio/sfx/AV_collision.ogg'
TELEGRAPH_SFX_VOLUME = 0.55
ATTACK_HIT_SFX_VOLUME = 0.75

# Telegraph ink drip / splat pop — short rubber-hose readability juice on
# announceAttackTelegraph (client only; AI timings unchanged). Distinct from
# defeat DeathPop spray: drips fall down + tiny chest splat, not a burst.
TELEGRAPH_INK_DRIP_LOOK = {
    ARCHETYPE_INK: {
        'id': 'ink-drip',
        'lift': 2.15,
        'splatHalf': 0.42,
        'splatPeak': 1.85,
        'splatSec': 0.22,
        'splatColor': (0.55, 0.18, 0.85, 0.92),
        'dripCount': 4,
        'dripHalf': 0.16,
        'dripSpread': 0.55,
        'dripFall': 1.45,
        'dripSec': 0.38,
        'dripColor': (0.38, 0.1, 0.58, 0.95),
        'streakColor': (0.62, 0.22, 0.92, 0.9),
    },
    ARCHETYPE_BRUTE: {
        'id': 'sludge-drip',
        'lift': 2.45,
        'splatHalf': 0.52,
        'splatPeak': 2.05,
        'splatSec': 0.24,
        'splatColor': (0.28, 0.78, 0.22, 0.92),
        'dripCount': 5,
        'dripHalf': 0.2,
        'dripSpread': 0.7,
        'dripFall': 1.65,
        'dripSec': 0.42,
        'dripColor': (0.18, 0.62, 0.16, 0.95),
        'streakColor': (0.35, 0.9, 0.28, 0.9),
    },
    ARCHETYPE_SNARE: {
        'id': 'amber-drip',
        'lift': 1.95,
        'splatHalf': 0.36,
        'splatPeak': 1.7,
        'splatSec': 0.18,
        'splatColor': (0.95, 0.55, 0.18, 0.92),
        'dripCount': 3,
        'dripHalf': 0.14,
        'dripSpread': 0.85,
        'dripFall': 1.15,
        'dripSec': 0.32,
        'dripColor': (0.88, 0.45, 0.12, 0.95),
        'streakColor': (1.05, 0.65, 0.22, 0.9),
    },
}

# Telegraph cream / pastel warn flecks — sunny purity chips layered on
# announceAttackTelegraph with CorruptTelegraphInkFx / silhouette pops
# (client only). Contrast to ink drip (cream floats out; ink falls). Not ink;
# matches reclaim / death-cream / hit-spark cream family.
# TELEGRAPH_CREAM_WARN_ENABLED = False drops flecks + aftershock.
TELEGRAPH_CREAM_WARN_ENABLED = True
TELEGRAPH_CREAM_WARN_BIN = 43
TELEGRAPH_CREAM_WARN_COLORS = (
    (1.0, 0.97, 0.82, 0.95),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.9),    # soft peach pastel
    (0.98, 0.94, 0.88, 0.88),  # warm parchment
)
TELEGRAPH_CREAM_WARN_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
TELEGRAPH_CREAM_WARN_LOOK = {
    'id': 'telegraph-cream-warn',
    # lift composed with telegraphInkLook when played; this is the fallback.
    'lift': 2.15,
    'fleckCount': 5,
    'fleckHalf': 0.12,
    'fleckDist': 1.15,
    'fleckLift': 0.55,
    'fleckSec': 0.24,
    'fleckColors': TELEGRAPH_CREAM_WARN_COLORS,
    'fleckEndColors': TELEGRAPH_CREAM_WARN_END_COLORS,
    'binSort': TELEGRAPH_CREAM_WARN_BIN,
}

# Delayed cream aftershock after telegraph cream warn flecks — residual
# soft halo + flecks/streaks that settle downward (cream/pastel only).
# Same grammar as HIT_SPARK_CREAM_AFTERSHOCK_* / PERFECT_DODGE_CREAM_AFTERSHOCK_*.
# TELEGRAPH_CREAM_WARN_AFTERSHOCK_ENABLED = False drops aftershock only.
TELEGRAPH_CREAM_WARN_AFTERSHOCK_ENABLED = True
TELEGRAPH_CREAM_WARN_AFTERSHOCK_DELAY_SEC = 0.18
TELEGRAPH_CREAM_WARN_AFTERSHOCK_COUNT = 3
TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_COUNT = 2
TELEGRAPH_CREAM_WARN_AFTERSHOCK_SIZE = 0.11
TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_SIZE = 0.16
TELEGRAPH_CREAM_WARN_AFTERSHOCK_DRIFT = 0.7
TELEGRAPH_CREAM_WARN_AFTERSHOCK_SEC = 0.38
TELEGRAPH_CREAM_WARN_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.88)
TELEGRAPH_CREAM_WARN_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.85)
TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_ENABLED = True
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_HALF = 0.48
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_START = 0.3
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_PEAK = 1.55
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_SEC = 0.32
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_PEAK_ALPHA = 0.26
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)

# Rising cream sparkle flecks on telegraph cream warn — soft sunny chips that
# rise from the CorruptTelegraphCreamWarnFx warn spray (client only).
# Compose lift / warn radius via CorruptTelegraphCreamSparkleFx.telegraphCreamSparkleLook
# → telegraphCreamWarnLook (#102); fleck size/timing/rise borrows silhouette
# cream sparkle (#131) twinkle grammar. Distinct from outward warn flecks and
# settling aftershock: starts near warn spray, rises mostly upward with twinkle.
# Not ink-colored. TELEGRAPH_CREAM_SPARKLE_ENABLED = False drops rising sparkles only.
TELEGRAPH_CREAM_SPARKLE_ENABLED = True
TELEGRAPH_CREAM_SPARKLE_BIN = 44
TELEGRAPH_CREAM_SPARKLE_COLORS = (
    (1.0, 0.97, 0.82, 0.88),  # sunny cream
    (1.0, 0.96, 0.62, 0.82),  # butter
    (1.0, 0.9, 0.78, 0.78),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.74),  # warm parchment
)
TELEGRAPH_CREAM_SPARKLE_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
TELEGRAPH_CREAM_SPARKLE_LOOK = {
    'id': 'telegraph-cream-sparkle',
    # lift / warnRadius composed with telegraphCreamWarnLook when played; fallbacks below.
    'lift': 2.15,
    'startDelaySec': 0.04,
    'fleckCount': 3,
    'fleckHalf': 0.065,
    'fleckHalfScale': 1.05,
    'warnRadius': 0.48,
    'warnRadiusScale': 0.42,
    'warnZJitter': 0.19,
    'warnZJitterScale': 0.35,
    'fleckDist': 0.14,
    'fleckDistScale': 1.15,
    'fleckLift': 0.6,
    'fleckLiftScale': 1.08,
    'fleckSec': 0.37,
    'fleckSecScale': 0.92,
    'fleckStagger': 0.038,
    'fleckColors': TELEGRAPH_CREAM_SPARKLE_COLORS,
    'fleckEndColors': TELEGRAPH_CREAM_SPARKLE_END_COLORS,
    'binSort': TELEGRAPH_CREAM_SPARKLE_BIN,
}

# Soft cream wash pulse on telegraph cream warn / sparkle stack — aspect2d
# veil after warn flecks (#102) + aftershock (#121) + rising sparkles (#135)
# (client only). Matches CorruptSilhouetteCreamWashFx (#153) /
# IdleCreamWashPulseFx (#146) / CorruptDeathCreamWashFx (#119) two-beat
# grammar. Delay composed via CorruptTelegraphCreamWashFx.telegraphCreamWashLook
# → telegraphCreamSparkleLook. Soft cream/pastel contrast against ink telegraph.
# TELEGRAPH_CREAM_WASH_ENABLED = False drops wash only (warn / sparkle stay).
TELEGRAPH_CREAM_WASH_ENABLED = True
TELEGRAPH_CREAM_WASH_DELAY_SEC = 0.30  # fallback; look prefers sparkle compose
TELEGRAPH_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
TELEGRAPH_CREAM_WASH_PEAK = 0.065  # quieter than death (0.14) / melee (0.10);
# slightly above idle (0.055) / silhouette (0.05) so telegraph event reads
TELEGRAPH_CREAM_WASH_MID = 0.036
TELEGRAPH_CREAM_WASH_IN_SEC = 0.06
TELEGRAPH_CREAM_WASH_PULSE_SEC = 0.10
TELEGRAPH_CREAM_WASH_HOLD_SEC = 0.08
TELEGRAPH_CREAM_WASH_OUT_SEC = 0.40
TELEGRAPH_CREAM_WASH_BIN = 39  # soft veil under telegraph flecks (43) / sparkles (44)
TELEGRAPH_CREAM_WASH_LOOK = {
    'id': 'telegraph-cream-wash',
    # delaySec composed with telegraphCreamSparkleLook when played; fallbacks below.
    'delaySec': TELEGRAPH_CREAM_WASH_DELAY_SEC,
    'delayScale': 0.72,
    'delayBias': 0.12,
    'color': TELEGRAPH_CREAM_WASH_COLOR,
    'peak': TELEGRAPH_CREAM_WASH_PEAK,
    'mid': TELEGRAPH_CREAM_WASH_MID,
    'inSec': TELEGRAPH_CREAM_WASH_IN_SEC,
    'pulseSec': TELEGRAPH_CREAM_WASH_PULSE_SEC,
    'holdSec': TELEGRAPH_CREAM_WASH_HOLD_SEC,
    'outSec': TELEGRAPH_CREAM_WASH_OUT_SEC,
    'binSort': TELEGRAPH_CREAM_WASH_BIN,
}

# Ambient idle ink drip — sparse rubber-hose pollution presence between
# telegraphs (client only). Cheaper than TELEGRAPH_INK_DRIP_*: 1–2 drips,
# no splat pop, longer period, lower alpha. Pauses while telegraph juice
# owns the frame. Overlord retints via IdleInkDripFx.idleInkLook(finaleLook).
IDLE_INK_DRIP_LOOK = {
    ARCHETYPE_INK: {
        'id': 'ink-idle',
        'lift': 2.05,
        'periodSec': 2.15,
        'settleSec': 0.55,
        'dripCount': 1,
        'dripHalf': 0.11,
        'dripSpread': 0.32,
        'dripFall': 0.95,
        'dripSec': 0.55,
        'dripStagger': 0.05,
        'dripColor': (0.32, 0.08, 0.48, 0.55),
        'streakColor': (0.48, 0.16, 0.72, 0.48),
        'binSort': 39,
    },
    ARCHETYPE_BRUTE: {
        'id': 'sludge-idle',
        'lift': 2.35,
        'periodSec': 2.45,
        'settleSec': 0.65,
        'dripCount': 2,
        'dripHalf': 0.14,
        'dripSpread': 0.4,
        'dripFall': 1.1,
        'dripSec': 0.62,
        'dripStagger': 0.07,
        'dripColor': (0.14, 0.48, 0.12, 0.55),
        'streakColor': (0.22, 0.68, 0.18, 0.48),
        'binSort': 39,
    },
    ARCHETYPE_SNARE: {
        'id': 'amber-idle',
        'lift': 1.85,
        'periodSec': 1.85,
        'settleSec': 0.4,
        'dripCount': 1,
        'dripHalf': 0.09,
        'dripSpread': 0.55,
        'dripFall': 0.75,
        'dripSec': 0.48,
        'dripStagger': 0.04,
        'dripColor': (0.72, 0.36, 0.1, 0.5),
        'streakColor': (0.88, 0.5, 0.16, 0.42),
        'binSort': 39,
    },
}

# Idle cream / pastel drip contrast — soft sunny chips layered with
# IdleInkDripFx between telegraphs (client only). Cream drips fall beside
# dark ink (phase-offset); not ink-colored. Compose lift/period via
# IdleCreamDripContrastFx.idleCreamDripLook → idleInkLook.
# IDLE_CREAM_DRIP_ENABLED = False drops cream drips only (ink idle stays).
IDLE_CREAM_DRIP_ENABLED = True
IDLE_CREAM_DRIP_BIN = 41
IDLE_CREAM_DRIP_COLORS = (
    (1.0, 0.97, 0.82, 0.72),  # sunny cream
    (1.0, 0.96, 0.62, 0.68),  # butter
    (1.0, 0.9, 0.78, 0.65),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.62),  # warm parchment
)
IDLE_CREAM_DRIP_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
IDLE_CREAM_DRIP_LOOK = {
    'id': 'idle-cream-drip',
    # lift / period composed with idleInkLook when played; these are fallbacks.
    'lift': 2.05,
    'periodSec': 2.55,
    'periodScale': 1.18,
    'settleSec': 0.75,
    'settleBias': 0.22,
    'dripCount': 1,
    'dripHalf': 0.1,
    'dripSpread': 0.38,
    'dripFall': 0.85,
    'dripSec': 0.58,
    'dripStagger': 0.06,
    'dripColors': IDLE_CREAM_DRIP_COLORS,
    'dripEndColors': IDLE_CREAM_DRIP_END_COLORS,
    'binSort': IDLE_CREAM_DRIP_BIN,
}

# Silhouette cream / pastel rim flecks — soft sunny chips sparkling along the
# ink Actor/DNA (or card) silhouette rim between telegraphs (client only).
# Compose lift/period via CorruptSilhouetteCreamRimFx.silhouetteCreamRimLook
# → idleCreamDripLook. Distinct from falling IdleCreamDripContrastFx drips:
# rim flecks orbit/drift off the silhouette edge. Not ink-colored.
# SILHOUETTE_CREAM_RIM_ENABLED = False drops rim flecks only (idle cream stays).
SILHOUETTE_CREAM_RIM_ENABLED = True
SILHOUETTE_CREAM_RIM_BIN = 42
SILHOUETTE_CREAM_RIM_COLORS = (
    (1.0, 0.97, 0.82, 0.78),  # sunny cream
    (1.0, 0.96, 0.62, 0.72),  # butter
    (1.0, 0.9, 0.78, 0.68),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.65),  # warm parchment
)
SILHOUETTE_CREAM_RIM_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
SILHOUETTE_CREAM_RIM_LOOK = {
    'id': 'silhouette-cream-rim',
    # lift / period composed with idleCreamDripLook when played; fallbacks below.
    'lift': 2.05,
    'periodSec': 1.85,
    'periodScale': 0.72,
    'settleSec': 0.55,
    'settleBias': -0.12,
    'fleckCount': 3,
    'fleckHalf': 0.09,
    'rimRadius': 0.72,
    'rimZJitter': 0.22,
    'fleckDist': 0.38,
    'fleckLift': 0.28,
    'fleckSec': 0.42,
    'fleckStagger': 0.04,
    'fleckColors': SILHOUETTE_CREAM_RIM_COLORS,
    'fleckEndColors': SILHOUETTE_CREAM_RIM_END_COLORS,
    'binSort': SILHOUETTE_CREAM_RIM_BIN,
}

# Idle cream drip sparkle flecks — soft sunny chips twinkling along the
# IdleCreamDripContrastFx drip path between telegraphs (client only).
# Compose lift/period via IdleCreamDripSparkleFx.idleCreamDripSparkleLook
# → idleCreamDripLook; fleck size/timing borrows silhouette cream rim (#114)
# sparkle grammar. Distinct from falling drips and silhouette rim orbit:
# tighter radius near cream drip angles, twinkle pop scale. Not ink-colored.
# IDLE_CREAM_DRIP_SPARKLE_ENABLED = False drops sparkles only (cream drip stays).
IDLE_CREAM_DRIP_SPARKLE_ENABLED = True
IDLE_CREAM_DRIP_SPARKLE_BIN = 43
IDLE_CREAM_DRIP_SPARKLE_COLORS = (
    (1.0, 0.97, 0.82, 0.82),  # sunny cream
    (1.0, 0.96, 0.62, 0.76),  # butter
    (1.0, 0.9, 0.78, 0.72),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.68),  # warm parchment
)
IDLE_CREAM_DRIP_SPARKLE_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
IDLE_CREAM_DRIP_SPARKLE_LOOK = {
    'id': 'idle-cream-drip-sparkle',
    # lift / period composed with idleCreamDripLook when played; fallbacks below.
    'lift': 2.05,
    'periodSec': 1.48,
    'periodScale': 0.58,
    'settleSec': 0.55,
    'settleBias': -0.18,
    'fleckCount': 2,
    'fleckHalf': 0.07,
    'fleckHalfScale': 0.78,
    'sparkleRadius': 0.42,
    'dripBias': 0.18,
    'fleckDist': 0.22,
    'fleckLift': 0.18,
    'fleckSec': 0.36,
    'fleckSecScale': 0.85,
    'fleckStagger': 0.035,
    'fleckColors': IDLE_CREAM_DRIP_SPARKLE_COLORS,
    'fleckEndColors': IDLE_CREAM_DRIP_SPARKLE_END_COLORS,
    'binSort': IDLE_CREAM_DRIP_SPARKLE_BIN,
}

# Idle cream wash pulse — soft aspect2d veil between telegraphs (client only).
# Matches CorruptDeathCreamWashFx (#119) / HitSparkCreamWashFx (#134) two-beat
# grammar; quieter ambient contrast against IdleInkDripFx. Compose period via
# IdleCreamWashPulseFx.idleCreamWashLook → idleCreamDripSparkleLook.
# IDLE_CREAM_WASH_ENABLED = False drops wash only (drips / sparkles stay).
IDLE_CREAM_WASH_ENABLED = True
IDLE_CREAM_WASH_DELAY_SEC = 0.0  # loop settle handles spacing
IDLE_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
IDLE_CREAM_WASH_PEAK = 0.055  # quieter than death (0.14) / melee hit (0.10)
IDLE_CREAM_WASH_MID = 0.032
IDLE_CREAM_WASH_IN_SEC = 0.07
IDLE_CREAM_WASH_PULSE_SEC = 0.12
IDLE_CREAM_WASH_HOLD_SEC = 0.10
IDLE_CREAM_WASH_OUT_SEC = 0.48
IDLE_CREAM_WASH_BIN = 36  # soft veil under death wash (38) / idle drips
IDLE_CREAM_WASH_LOOK = {
    'id': 'idle-cream-wash',
    # period composed with idleCreamDripSparkleLook when played; fallbacks below.
    'periodSec': 3.2,
    'periodScale': 2.15,
    'settleSec': 1.05,
    'settleBias': 0.48,
    'delaySec': IDLE_CREAM_WASH_DELAY_SEC,
    'color': IDLE_CREAM_WASH_COLOR,
    'peak': IDLE_CREAM_WASH_PEAK,
    'mid': IDLE_CREAM_WASH_MID,
    'inSec': IDLE_CREAM_WASH_IN_SEC,
    'pulseSec': IDLE_CREAM_WASH_PULSE_SEC,
    'holdSec': IDLE_CREAM_WASH_HOLD_SEC,
    'outSec': IDLE_CREAM_WASH_OUT_SEC,
    'binSort': IDLE_CREAM_WASH_BIN,
}

# Silhouette cream rim rising sparkle flecks — soft sunny chips rising from
# the CorruptSilhouetteCreamRimFx rim edge between telegraphs (client only).
# Compose lift/period via CorruptSilhouetteCreamSparkleFx.silhouetteCreamSparkleLook
# → silhouetteCreamRimLook; fleck size/timing borrows idle cream drip sparkle
# (#125) twinkle grammar. Distinct from rim orbit (#114) and drip-path sparkle:
# starts on rim, rises mostly upward with twinkle pop. Not ink-colored.
# SILHOUETTE_CREAM_SPARKLE_ENABLED = False drops rising sparkles only (rim stays).
SILHOUETTE_CREAM_SPARKLE_ENABLED = True
SILHOUETTE_CREAM_SPARKLE_BIN = 44
SILHOUETTE_CREAM_SPARKLE_COLORS = (
    (1.0, 0.97, 0.82, 0.84),  # sunny cream
    (1.0, 0.96, 0.62, 0.78),  # butter
    (1.0, 0.9, 0.78, 0.74),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.7),  # warm parchment
)
SILHOUETTE_CREAM_SPARKLE_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
SILHOUETTE_CREAM_SPARKLE_LOOK = {
    'id': 'silhouette-cream-sparkle',
    # lift / period composed with silhouetteCreamRimLook when played; fallbacks below.
    'lift': 2.05,
    'periodSec': 1.18,
    'periodScale': 0.64,
    'settleSec': 0.47,
    'settleBias': -0.08,
    'fleckCount': 2,
    'fleckHalf': 0.06,
    'fleckHalfScale': 0.88,
    'rimRadius': 0.69,
    'rimRadiusScale': 0.96,
    'rimZJitter': 0.15,
    'rimZJitterScale': 0.7,
    'fleckDist': 0.12,
    'fleckLift': 0.55,
    'fleckSec': 0.4,
    'fleckSecScale': 1.12,
    'fleckStagger': 0.038,
    'fleckColors': SILHOUETTE_CREAM_SPARKLE_COLORS,
    'fleckEndColors': SILHOUETTE_CREAM_SPARKLE_END_COLORS,
    'binSort': SILHOUETTE_CREAM_SPARKLE_BIN,
}

# Silhouette cream wash pulse — soft aspect2d veil between telegraphs
# (client only). Matches IdleCreamWashPulseFx (#146) / CorruptDeathCreamWashFx
# (#119) two-beat grammar; quieter ambient contrast against the ink silhouette
# cream rim + rising sparkle stack. Compose period via
# CorruptSilhouetteCreamWashFx.silhouetteCreamWashLook → silhouetteCreamSparkleLook.
# SILHOUETTE_CREAM_WASH_ENABLED = False drops wash only (rim / sparkles stay).
SILHOUETTE_CREAM_WASH_ENABLED = True
SILHOUETTE_CREAM_WASH_DELAY_SEC = 0.0  # loop settle handles spacing
SILHOUETTE_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SILHOUETTE_CREAM_WASH_PEAK = 0.05  # quieter than idle (0.055) / death (0.14)
SILHOUETTE_CREAM_WASH_MID = 0.028
SILHOUETTE_CREAM_WASH_IN_SEC = 0.07
SILHOUETTE_CREAM_WASH_PULSE_SEC = 0.12
SILHOUETTE_CREAM_WASH_HOLD_SEC = 0.10
SILHOUETTE_CREAM_WASH_OUT_SEC = 0.48
SILHOUETTE_CREAM_WASH_BIN = 37  # soft veil between idle wash (36) / death (38)
SILHOUETTE_CREAM_WASH_LOOK = {
    'id': 'silhouette-cream-wash',
    # period composed with silhouetteCreamSparkleLook when played; fallbacks below.
    'periodSec': 2.85,
    'periodScale': 2.4,
    'settleSec': 0.99,
    'settleBias': 0.52,
    'delaySec': SILHOUETTE_CREAM_WASH_DELAY_SEC,
    'color': SILHOUETTE_CREAM_WASH_COLOR,
    'peak': SILHOUETTE_CREAM_WASH_PEAK,
    'mid': SILHOUETTE_CREAM_WASH_MID,
    'inSec': SILHOUETTE_CREAM_WASH_IN_SEC,
    'pulseSec': SILHOUETTE_CREAM_WASH_PULSE_SEC,
    'holdSec': SILHOUETTE_CREAM_WASH_HOLD_SEC,
    'outSec': SILHOUETTE_CREAM_WASH_OUT_SEC,
    'binSort': SILHOUETTE_CREAM_WASH_BIN,
}

# Sludge Brute spit telegraph — swamp green, wider squash, squirt SFX.
# Distinct from Ink Smudge purple melee so ranged wind-up reads at a glance.
BRUTE_TELEGRAPH_CHARGE_COLOR = (0.45, 2.2, 0.35, 1.0)
BRUTE_TELEGRAPH_HOLD_COLOR = (0.3, 1.65, 0.22, 1.0)
BRUTE_TELEGRAPH_SQUASH = (2.35, 2.35, 0.32)
BRUTE_TELEGRAPH_MID = (2.05, 2.05, 0.42)
BRUTE_TELEGRAPH_STRETCH = (0.48, 0.48, 1.95)
BRUTE_TELEGRAPH_SFX = 'phase_4/audio/sfx/AA_squirt_seltzer.ogg'
BRUTE_TELEGRAPH_SFX_VOLUME = 0.7
BRUTE_ATTACK_HIT_SFX = 'phase_4/audio/sfx/AA_squirt_glasswater.ogg'
BRUTE_ATTACK_HIT_SFX_VOLUME = 0.8
BRUTE_HIT_FLASH_COLOR = (0.45, 1.05, 0.35, 1.0)
BRUTE_HIT_FLASH_PEAK = 0.62
# Client-only ink blob that travels toward the local toon on spit hit.
BRUTE_SPIT_BLOB_COLOR = (0.18, 0.72, 0.22, 0.92)
BRUTE_SPIT_BLOB_SCALE = 0.55
BRUTE_SPIT_BLOB_TRAVEL = 0.28
BRUTE_SPIT_BLOB_Z = 2.4

# Sludge Brute telegraph spit-gob pop — short rubber-hose green spit charge on
# announceAttackTelegraph (client only). Distinct from hit-time BRUTE_SPIT_BLOB_*
# travel and from generic TELEGRAPH_INK_DRIP sludge drips: forward spit silhouette.
BRUTE_TELEGRAPH_SPIT_LOOK = {
    'id': 'sludge-spit-gob',
    'lift': 2.55,
    'scale': 1.0,
    'peakAlpha': 0.97,
    'fadeInSec': 0.04,
    'holdSec': 0.16,
    'fadeOutSec': 0.24,
    'squash': (1.65, 1.0, 0.42),
    'stretch': (0.55, 1.0, 2.15),
    'squashSec': 0.05,
    'stretchSec': 0.12,
    'settleSec': 0.14,
    'wobbleDeg': 12.0,
    'gobHalf': 0.38,
    'rimScale': 1.28,
    'hotHalf': 0.14,
    'gobColor': (0.22, 0.85, 0.28, 1.0),
    'rimColor': (0.55, 1.2, 0.42, 1.0),
    'flashColor': (0.55, 1.35, 0.4, 1.0),
    'dropletCount': 4,
    'dropletHalf': 0.1,
    'dropletSec': 0.3,
    'dropletSpread': 1.05,
    'dropletColor': (0.35, 0.95, 0.3, 0.9),
    'binSort': 44,
}

# Balloon Snare string-lash — warm amber, horizontal rubber stretch, vine zip.
# Reads opposite Brute spit (tall green) and Smudge melee (purple squash).
SNARE_TELEGRAPH_CHARGE_COLOR = (2.35, 1.45, 0.35, 1.0)
SNARE_TELEGRAPH_HOLD_COLOR = (1.95, 1.1, 0.28, 1.0)
SNARE_TELEGRAPH_SQUASH = (0.55, 0.55, 1.55)
SNARE_TELEGRAPH_MID = (1.15, 1.15, 1.15)
SNARE_TELEGRAPH_STRETCH = (2.55, 0.42, 0.55)  # horizontal rubber-hose lash
SNARE_TELEGRAPH_SFX = 'phase_4/audio/sfx/MG_sfx_vine_game_jump.ogg'
SNARE_TELEGRAPH_SFX_VOLUME = 0.72
SNARE_ATTACK_HIT_SFX = 'phase_4/audio/sfx/MG_sfx_vine_game_fall.ogg'
SNARE_ATTACK_HIT_SFX_VOLUME = 0.78
SNARE_HIT_FLASH_COLOR = (1.15, 0.72, 0.28, 1.0)
SNARE_HIT_FLASH_PEAK = 0.58
# Client-only string line that snaps toward the local toon on lash hit.
SNARE_LASH_COLOR = (0.95, 0.55, 0.12, 0.95)
SNARE_LASH_HALF_W = 0.12
SNARE_LASH_HALF_H = 0.55
SNARE_LASH_TRAVEL = 0.18
SNARE_LASH_Z = 2.1

# Balloon Snare telegraph string-lash pop — short rubber-hose amber whip on
# announceAttackTelegraph (client only). Distinct from hit-time SNARE_LASH_*
# snap and from generic TELEGRAPH_INK_DRIP amber drips: horizontal lash silhouette.
SNARE_TELEGRAPH_STRING_LOOK = {
    'id': 'amber-string-lash',
    'lift': 2.05,
    'scale': 1.0,
    'peakAlpha': 0.96,
    'fadeInSec': 0.04,
    'holdSec': 0.14,
    'fadeOutSec': 0.22,
    'squash': (0.45, 1.0, 1.55),
    'stretch': (2.35, 1.0, 0.42),
    'squashSec': 0.05,
    'stretchSec': 0.1,
    'settleSec': 0.12,
    'whipDeg': 18.0,
    'stringHalfW': 0.55,
    'stringHalfH': 0.08,
    'knotHalf': 0.11,
    'tipHalf': 0.1,
    'stringColor': (0.95, 0.55, 0.12, 1.0),
    'tipColor': (1.15, 0.75, 0.28, 1.0),
    'flashColor': (1.25, 0.8, 0.35, 1.0),
    'streakCount': 3,
    'streakHalf': 0.12,
    'streakSec': 0.28,
    'streakSpread': 1.15,
    'streakColor': (1.05, 0.65, 0.22, 0.9),
    'binSort': 43,
}

# Defeat pop juice — rubber-hose ink splat / balloon pop on announceDefeat.
# Per-archetype palette so Smudge (purple), Brute (green), Snare (amber) read.
# Cream fleck burst (DEATH_CREAM_FLECK_*) layers sunny purity chips on top via
# CorruptDeathCreamFleckFx — not ink. Toggle DEATH_CREAM_FLECK_ENABLED.
# Rising cream sparkles (DEATH_CREAM_SPARKLE_*) rise from the fleck burst via
# CorruptDeathCreamSparkleFx — telegraph / silhouette cream sparkle grammar.
# Toggle DEATH_CREAM_SPARKLE_ENABLED.
# Soft cream wash (DEATH_CREAM_WASH_*) pulses after the fleck burst via
# CorruptDeathCreamWashFx — reclaim purity-wash grammar. Toggle
# DEATH_CREAM_WASH_ENABLED.
DEATH_POP_SFX_VOLUME = 0.78
DEATH_POP_LOOK = {
    ARCHETYPE_INK: {
        'id': 'ink-splat',
        'burstScale': (1.75, 1.75, 1.75),
        'pancakeScale': (2.15, 2.15, 0.1),
        'vanishScale': (0.02, 0.02, 0.02),
        'burstSec': 0.07,
        'pancakeSec': 0.12,
        'vanishSec': 0.18,
        'burstColor': (2.0, 1.35, 2.4, 1.0),
        'pancakeColor': (1.55, 0.85, 1.9, 1.0),
        'fadeColor': (1.2, 1.35, 1.05, 0.0),
        'lift': 1.35,
        'ringHalf': 0.85,
        'ringPeak': 2.6,
        'ringSec': 0.32,
        'ringColor': (0.55, 0.2, 0.85, 0.9),
        'dropletCount': 8,
        'dropletHalf': 0.28,
        'dropletDist': 2.4,
        'dropletLift': 1.1,
        'dropletSec': 0.34,
        'dropletColor': (0.42, 0.12, 0.62, 0.95),
        'sfx': 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg',
        'sfxVolume': 0.72,
    },
    ARCHETYPE_BRUTE: {
        'id': 'sludge-splat',
        'burstScale': (1.95, 1.95, 1.55),
        'pancakeScale': (2.55, 2.55, 0.08),
        'vanishScale': (0.02, 0.02, 0.02),
        'burstSec': 0.08,
        'pancakeSec': 0.14,
        'vanishSec': 0.2,
        'burstColor': (0.85, 2.2, 0.55, 1.0),
        'pancakeColor': (0.55, 1.55, 0.35, 1.0),
        'fadeColor': (0.7, 1.25, 0.55, 0.0),
        'lift': 1.55,
        'ringHalf': 1.05,
        'ringPeak': 2.9,
        'ringSec': 0.36,
        'ringColor': (0.25, 0.75, 0.22, 0.92),
        'dropletCount': 9,
        'dropletHalf': 0.34,
        'dropletDist': 2.85,
        'dropletLift': 0.85,
        'dropletSec': 0.38,
        'dropletColor': (0.22, 0.68, 0.18, 0.95),
        'sfx': 'phase_4/audio/sfx/AA_squirt_glasswater.ogg',
        'sfxVolume': 0.8,
    },
    ARCHETYPE_SNARE: {
        'id': 'balloon-pop',
        'burstScale': (2.25, 2.25, 2.25),
        'pancakeScale': (2.85, 2.85, 0.12),
        'vanishScale': (0.02, 0.02, 0.02),
        'burstSec': 0.06,
        'pancakeSec': 0.1,
        'vanishSec': 0.16,
        'burstColor': (2.4, 1.55, 0.45, 1.0),
        'pancakeColor': (1.85, 1.05, 0.28, 1.0),
        'fadeColor': (1.45, 1.15, 0.55, 0.0),
        'lift': 1.15,
        'ringHalf': 0.75,
        'ringPeak': 3.1,
        'ringSec': 0.28,
        'ringColor': (0.95, 0.55, 0.15, 0.92),
        'dropletCount': 7,
        'dropletHalf': 0.24,
        'dropletDist': 2.65,
        'dropletLift': 1.35,
        'dropletSec': 0.3,
        'dropletColor': (0.9, 0.48, 0.12, 0.95),
        'sfx': 'phase_3/audio/sfx/GUI_balloon_popup.ogg',
        'sfxVolume': 0.85,
    },
}

# Defeat cream / pastel fleck burst — sunny purity chips layered on
# CorruptDeathPopFx ink splat (client only). Not ink; matches reclaim /
# hit-spark cream family. DEATH_CREAM_FLECK_ENABLED = False drops flecks only.
DEATH_CREAM_FLECK_ENABLED = True
DEATH_CREAM_FLECK_BIN = 47
DEATH_CREAM_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.95),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.9),    # soft peach pastel
    (0.98, 0.94, 0.88, 0.88),  # warm parchment
)
DEATH_CREAM_FLECK_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
DEATH_CREAM_FLECK_LOOK = {
    'id': 'death-cream-fleck',
    # lift composed with deathPopLook when played; this is the fallback.
    'lift': 1.35,
    'fleckCount': 7,
    'fleckHalf': 0.18,
    'fleckDist': 2.05,
    'fleckLift': 1.35,
    'fleckSec': 0.32,
    'fleckColors': DEATH_CREAM_FLECK_COLORS,
    'fleckEndColors': DEATH_CREAM_FLECK_END_COLORS,
    'binSort': DEATH_CREAM_FLECK_BIN,
}

# Rising cream sparkle flecks on death cream fleck burst — soft sunny chips
# that rise from CorruptDeathCreamFleckFx (#94) (client only).
# Compose lift / burst radius via CorruptDeathCreamSparkleFx.deathCreamSparkleLook
# → deathCreamFleckLook; fleck size/timing/rise borrows telegraph cream sparkle
# (#135) / silhouette cream sparkle (#131) twinkle grammar. Distinct from
# outward death flecks and soft cream wash (#119): starts near fleck spray,
# rises mostly upward with twinkle. Not ink-colored.
# DEATH_CREAM_SPARKLE_ENABLED = False drops rising sparkles only.
DEATH_CREAM_SPARKLE_ENABLED = True
DEATH_CREAM_SPARKLE_BIN = 48  # above flecks (47); soft rising chips
DEATH_CREAM_SPARKLE_COLORS = (
    (1.0, 0.97, 0.82, 0.88),  # sunny cream
    (1.0, 0.96, 0.62, 0.82),  # butter
    (1.0, 0.9, 0.78, 0.78),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.74),  # warm parchment
)
DEATH_CREAM_SPARKLE_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
DEATH_CREAM_SPARKLE_LOOK = {
    'id': 'death-cream-sparkle',
    # lift / burstRadius composed with deathCreamFleckLook when played; fallbacks below.
    'lift': 1.35,
    'startDelaySec': 0.08,
    'startDelayBias': 0.04,
    'fleckCount': 4,
    'fleckHalf': 0.07,
    'fleckHalfScale': 1.08,
    'burstRadius': 0.57,
    'burstRadiusScale': 0.28,
    'burstZJitter': 0.3,
    'burstZJitterScale': 0.22,
    'fleckDist': 0.17,
    'fleckDistScale': 1.2,
    'fleckLift': 0.69,
    'fleckLiftScale': 1.15,
    'fleckSec': 0.39,
    'fleckSecScale': 1.05,
    'fleckStagger': 0.038,
    'fleckColors': DEATH_CREAM_SPARKLE_COLORS,
    'fleckEndColors': DEATH_CREAM_SPARKLE_END_COLORS,
    'binSort': DEATH_CREAM_SPARKLE_BIN,
}

# Defeat cream wash pulse — soft aspect2d veil after DEATH_CREAM_FLECK_* burst
# (client only). Matches reclaim PurityCompleteCreamWashFx /
# EntryCreamWashPulseFx two-beat grammar; quieter than street purity payoff.
# DEATH_CREAM_WASH_ENABLED = False drops wash only.
DEATH_CREAM_WASH_ENABLED = True
DEATH_CREAM_WASH_DELAY_SEC = 0.20  # after fleck burst start
DEATH_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
DEATH_CREAM_WASH_PEAK = 0.14
DEATH_CREAM_WASH_MID = 0.08
DEATH_CREAM_WASH_IN_SEC = 0.06
DEATH_CREAM_WASH_PULSE_SEC = 0.10
DEATH_CREAM_WASH_HOLD_SEC = 0.08
DEATH_CREAM_WASH_OUT_SEC = 0.42
DEATH_CREAM_WASH_BIN = 38  # under flecks (47); soft veil

# Overlord telegraph ink crown / silhouette flash — short rubber-hose juice
# above the boss on announceAttackTelegraph when a finale phase look is active.
# Distinct from street CorruptTelegraphInkFx drips: crown silhouette reads as
# boss wind-up. Client only; AI timings unchanged. No KH branding.
OVERLORD_TELEGRAPH_CROWN_LOOK = {
    'id': 'ink-crown',
    'lift': 3.35,
    'scale': 1.0,
    'peakAlpha': 0.95,
    'fadeInSec': 0.05,
    'holdSec': 0.18,
    'fadeOutSec': 0.32,
    'squash': (1.4, 1.0, 0.55),
    'stretch': (0.7, 1.0, 1.55),
    'squashSec': 0.06,
    'stretchSec': 0.1,
    'settleSec': 0.14,
    'bodyColor': (0.06, 0.02, 0.08, 1.0),
    'rimColor': (0.85, 0.25, 0.95, 1.0),
    'flashColor': (1.15, 0.45, 1.25, 1.0),
    'binSort': 44,
}

# Overlord phase ink rain / ink fall — denser shower from above the boss on
# phase telegraphs (alongside OverlordTelegraphCrownFx). Taller / wider than
# street TELEGRAPH_INK_DRIP_*; P2 bumps dropCount via OverlordPhaseInkRainFx.
# Client only; AI timings unchanged. No KH branding.
OVERLORD_PHASE_INK_RAIN_LOOK = {
    'id': 'ink-rain',
    'lift': 5.4,
    'fall': 4.2,
    'spread': 1.55,
    'dropCount': 7,
    'dropHalf': 0.16,
    'fallSec': 0.48,
    'staggerSec': 0.03,
    'peakAlpha': 0.92,
    'dropColor': (0.28, 0.08, 0.42, 0.92),
    'streakColor': (0.55, 0.18, 0.78, 0.88),
    'puddleHalf': 0.55,
    'puddleLift': 0.08,
    'puddlePeak': 2.4,
    'puddleDelay': 0.16,
    'puddleInSec': 0.18,
    'puddleHoldSec': 0.12,
    'puddleOutSec': 0.28,
    'puddleColor': (0.12, 0.04, 0.18, 0.7),
    'binSort': 43,
}

# Ink Overlord finale phase looks (client-readable; AI timings unchanged).
# Phase 1 = rising magenta swell; Phase 2 = crimson unleashed fury.
# Keep P1/P2 telegraphs readable at a glance: color, rubber scale, SFX, HUD cue.
FINALE_PHASE_LOOK = {
    1: {
        'id': 'rising',
        # Magenta swell — tall rubber hose, pie whoosh wind-up.
        'telegraphCharge': (2.55, 0.28, 2.85, 1.0),
        'telegraphHold': (1.85, 0.2, 2.15, 1.0),
        'squash': (2.35, 2.35, 0.28),
        'mid': (2.05, 2.05, 0.42),
        'stretch': (0.42, 0.42, 2.15),
        'impactScale': (1.85, 1.85, 0.42),
        'impactColor': (2.55, 0.75, 2.7, 1.0),
        'rebound': (1.25, 0.45, 1.55, 1.0),
        'pulseHot': (0.95, 0.15, 1.15, 1.0),
        'hitFlash': (1.15, 0.35, 1.25, 1.0),
        'hitFlashPeak': 0.78,
        'actorScale': 1.32,
        'actorTint': (0.32, 0.06, 0.42, 1.0),
        'nameColor': (1.0, 0.5, 1.0, 1.0),
        'pulseAmp': 0.12,
        # Distinct from P2 crimson slam — lighter Silly rise whoosh.
        'telegraphSfx': 'phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseOne.ogg',
        'telegraphSfxVolume': 0.78,
        'hitSfx': 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg',
        'hitSfxVolume': 0.7,
        'hudCue': 'P1 MAGENTA SWELL',
        'hudColor': (1.0, 0.45, 1.0, 1.0),
    },
    2: {
        'id': 'unleashed',
        # Crimson fury — wider squash, taller stretch, heavier slam SFX.
        'telegraphCharge': (2.9, 0.1, 0.22, 1.0),
        'telegraphHold': (2.25, 0.06, 0.14, 1.0),
        'squash': (2.95, 2.95, 0.18),
        'mid': (2.45, 2.45, 0.32),
        'stretch': (0.28, 0.28, 2.75),
        'impactScale': (2.25, 2.25, 0.32),
        'impactColor': (2.85, 0.4, 0.22, 1.0),
        'rebound': (1.55, 0.28, 0.22, 1.0),
        'pulseHot': (1.55, 0.1, 0.16, 1.0),
        'hitFlash': (1.25, 0.12, 0.08, 1.0),
        'hitFlashPeak': 0.95,
        'actorScale': 1.58,
        'actorTint': (0.42, 0.05, 0.08, 1.0),
        'nameColor': (1.0, 0.28, 0.18, 1.0),
        'pulseAmp': 0.2,
        # Distinct from P1 magenta rise — hotter Silly phase-two sting.
        'telegraphSfx': 'phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseTwo.ogg',
        'telegraphSfxVolume': 0.88,
        'hitSfx': 'phase_3.5/audio/sfx/AV_collision.ogg',
        'hitSfxVolume': 0.92,
        'hudCue': 'P2 CRIMSON FURY',
        'hudColor': (1.0, 0.28, 0.18, 1.0),
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

# Oswald reveal sting — colder ink wash after Silly finale victory / twist.
# Existing Toontown SFX only (optional if asset missing in stripped checkouts).
OSWALD_REVEAL_FOV_PUNCH = 14.0
OSWALD_REVEAL_FOV_IN = 0.1
OSWALD_REVEAL_FOV_OUT = 0.55
OSWALD_REVEAL_FLASH_PEAK = 0.78
OSWALD_REVEAL_FLASH_COLOR = (0.95, 0.22, 0.38, 1.0)
OSWALD_REVEAL_RENDER_PEAK = (1.55, 0.28, 0.42, 1.0)
OSWALD_REVEAL_RENDER_HOLD = (1.25, 0.38, 0.48, 1.0)
OSWALD_REVEAL_SFX = 'phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseTwo.ogg'
OSWALD_REVEAL_SFX_VOLUME = 0.82

# Polluted vs pure street music beds (existing Toontown BGM — no new assets).
# Encounter bed lives in phase_3.5 with street loaders, so TT streets can play it.
POLLUTED_STREET_MUSIC = 'phase_3.5/audio/bgm/encntr_general_bg.ogg'
POLLUTED_STREET_MUSIC_VOLUME = 0.72
PURE_STREET_MUSIC_VOLUME = 0.8
POLLUTION_AUDIO_THRESHOLD = 0.05
POLLUTION_AUDIO_CROSSFADE_SEC = 1.25
# Snappier return so reclaim cheer / purity sting (#21) land together.
POLLUTION_AUDIO_RESTORE_CROSSFADE_SEC = 0.85

# Pure-street birds return — short rubber-hose ambient bed when pollution
# clears (existing SZ playground bird chirps; no new assets / no KH branding).
PURE_STREET_BIRDS_SFX = (
    'phase_4/audio/sfx/SZ_TC_bird1.ogg',
    'phase_4/audio/sfx/SZ_TC_bird2.ogg',
    'phase_4/audio/sfx/SZ_TC_bird3.ogg',
)
PURE_STREET_BIRDS_VOLUME = 0.62
PURE_STREET_BIRDS_FADE_IN_SEC = 0.55
PURE_STREET_BIRDS_HOLD_SEC = 2.4
PURE_STREET_BIRDS_FADE_OUT_SEC = 0.9
# Collapse pollutionChanged + purityRestoreFx double-fires into one bed.
PURE_STREET_BIRDS_DEBOUNCE_SEC = 2.5
# Extra chirp sprinkles during the hold (rubber-hose cheerful return).
PURE_STREET_BIRDS_CHIRP_COUNT = 3
PURE_STREET_BIRDS_CHIRP_VOLUME = 0.48


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


def pollutionDensityFactor(level):
    """Map pollution 0..1 → density factor with ease-in ramp curve."""
    lvl = clampPollution(level)
    if lvl <= POLLUTION_PURE:
        return 0.0
    curve = float(POLLUTION_FOG_DENSITY_CURVE)
    if curve == 1.0:
        return lvl
    return lvl ** curve


def pollutionFogRampDuration(fromLevel, toLevel):
    """Seconds to lerp fog/haze between two pollution levels."""
    a = clampPollution(fromLevel)
    b = clampPollution(toLevel)
    if abs(b - a) <= POLLUTION_FOG_SNAP_DELTA:
        return 0.0
    # Clearing to pure uses the longer settle so reclaim reads as fog lifting.
    if b <= POLLUTION_PURE < a:
        return float(POLLUTION_FOG_CLEAR_SEC)
    # Scale mid-step ramps by delta so a 0.15 defeat isn't sluggish.
    span = max(0.15, abs(b - a))
    return float(POLLUTION_FOG_RAMP_SEC) * min(1.0, span / 0.25)


def hoodFogColor(zoneId, level):
    """Fog RGB scaled by pollution density factor for this hood."""
    bias = hoodPollutionBias(zoneId)
    fog = bias['fog']
    dens = pollutionDensityFactor(level)
    return (
        fog[0] * (0.7 + 0.3 * dens),
        fog[1] * (0.75 + 0.25 * dens),
        fog[2],
    )


def hoodFogCreamDissolveColor(zoneId, level, creamBlend):
    """Ink fog RGB mixed toward sunny cream during purity dissolve.

    creamBlend 0 = hood ink fog; 1 = FOG_CREAM_DISSOLVE_COLOR. Density still
    drives how thick the fog reads; this only shifts the palette as it lifts.
    """
    ink = hoodFogColor(zoneId, level)
    blend = max(0.0, min(1.0, float(creamBlend)))
    if blend <= 0.0:
        return ink
    cream = FOG_CREAM_DISSOLVE_COLOR
    return (
        ink[0] + (float(cream[0]) - ink[0]) * blend,
        ink[1] + (float(cream[1]) - ink[1]) * blend,
        ink[2] + (float(cream[2]) - ink[2]) * blend,
    )


def hoodFogExpDensity(zoneId, level):
    """Exponential fog density for this hood at pollution level (ramped)."""
    bias = hoodPollutionBias(zoneId)
    return (
        CORRUPT_FOG_EXP_MAX
        * float(bias.get('fogExpScale', 1.0))
        * pollutionDensityFactor(level))


def hoodHazeAlpha(zoneId, level):
    """Fullscreen ink-haze opacity for this hood at pollution level."""
    dens = pollutionDensityFactor(level)
    if dens <= 0.0:
        return 0.0
    # Slight hood thickener so Silly/Punchline read heavier than Loopy.
    bias = hoodPollutionBias(zoneId)
    scale = float(bias.get('fogExpScale', 1.0))
    return min(0.55, POLLUTION_HAZE_ALPHA_MAX * dens * (0.85 + 0.15 * scale))


def hoodColorGrade(zoneId, level):
    """Render color-scale RGB (alpha 1) for hood-specific sickly grade."""
    bias = hoodPollutionBias(zoneId)
    drop = bias['gradeDrop']
    dens = pollutionDensityFactor(level)
    return (
        1.0 - (drop[0] * dens),
        1.0 - (drop[1] * dens),
        1.0 - (drop[2] * dens),
    )


def hoodPropTint(zoneId, level):
    """Street-geom multiply RGB for pollutionPropTint (1,1,1 when pure)."""
    dens = pollutionDensityFactor(level)
    if dens <= POLLUTION_PURE:
        return (1.0, 1.0, 1.0)
    bias = hoodPollutionBias(zoneId)
    target = bias['propTint']
    # Lerp white → hood prop tint by density factor.
    return (
        1.0 - (1.0 - target[0]) * dens,
        1.0 - (1.0 - target[1]) * dens,
        1.0 - (1.0 - target[2]) * dens,
    )


def hoodPropTintCreamFadeColor(zoneId, level, creamBlend, inkRgb=None):
    """Hood prop-tint RGB mixed toward sunny cream during purity fade.

    creamBlend 0 = hood ink prop tint (or inkRgb capture); 1 =
    HOOD_TINT_CREAM_FADE_COLOR. Density / inkRgb still set how corrupted the
    geom reads; this only shifts the palette as street purity completes.
    """
    if inkRgb is None:
        ink = hoodPropTint(zoneId, level)
    else:
        ink = (
            float(inkRgb[0]), float(inkRgb[1]), float(inkRgb[2]))
    blend = max(0.0, min(1.0, float(creamBlend)))
    if blend <= 0.0:
        return ink
    cream = HOOD_TINT_CREAM_FADE_COLOR
    return (
        ink[0] + (float(cream[0]) - ink[0]) * blend,
        ink[1] + (float(cream[1]) - ink[1]) * blend,
        ink[2] + (float(cream[2]) - ink[2]) * blend,
    )


def entryVignetteInk(zoneId):
    """Near-black rubber-hose ink RGB for street-entry edge vignette."""
    bias = hoodPollutionBias(zoneId)
    fog = bias.get('fog', ENTRY_VIGNETTE_INK[:3])
    # Crush fog toward ink-black so edges read as corruption, not a wash.
    return (
        min(0.14, float(fog[0]) * 0.45),
        min(0.10, float(fog[1]) * 0.40),
        min(0.14, float(fog[2]) * 0.50),
        1.0,
    )
