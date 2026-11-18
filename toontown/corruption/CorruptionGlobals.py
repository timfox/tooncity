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
ATTACK_HIT_FLASH_COLOR = (1.0, 0.55, 1.0, 1.0)
ATTACK_HIT_FLASH_PEAK = 0.55
ATTACK_HIT_FLASH_IN = 0.04
ATTACK_HIT_FLASH_OUT = 0.14
# Existing Toontown SFX — wind-up whoosh + collision thud.
TELEGRAPH_SFX = 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg'
ATTACK_HIT_SFX = 'phase_3.5/audio/sfx/AV_collision.ogg'
TELEGRAPH_SFX_VOLUME = 0.55
ATTACK_HIT_SFX_VOLUME = 0.75

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

# Defeat pop juice — rubber-hose ink splat / balloon pop on announceDefeat.
# Per-archetype palette so Smudge (purple), Brute (green), Snare (amber) read.
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
