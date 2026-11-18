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

# Mid-street wave escalation (base packSize/HP grow each wave).
WAVE_SIZE_BONUS = 1
WAVE_HP_SCALE = 0.18
WAVE_SPAWN_DELAY = 1.4
WAVE_MAX_EXTRA = 3

# Sludge Brute mix for default reclaim (Ink Smudge stays majority).
# Wave 1 = pure Smudge; later waves introduce ~⅓ tanks.
BRUTE_WAVE_START = 2
BRUTE_FRACTION = 0.34
BRUTE_NAME = 'Sludge Brute'
SMUDGE_NAME = 'Ink Smudge'
# Balloon Snare zip/lash — mid waves only (never Loopy wave-1 Smudge-only).
SNARE_WAVE_START = 2
SNARE_FRACTION = 0.22
SNARE_NAME = 'Balloon Snare'

# Director FSM states (mirrored on client for banner / HUD).
STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_COMPLETE = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_COMPLETE: 'complete',
}

# Client feedback copy — Oswald is the trusted reclaim lead (twist at finale).
BANNER_START = 'OSWALD: RECLAIM THIS STREET!'
BANNER_PACK = 'Corrupt pack inbound!'
BANNER_COMPLETE = 'PURITY RESTORED!'
BANNER_COMPLETE_SUB = 'Oswald tips his ears — neighborhood cheer returns!'
BANNER_WAVE_CLEARED = 'Wave cleared — hold the street!'
POLLUTION_HINT_FMT = 'Corruption  %.0f%%'
STATUS_FMT = 'Wave %s/%s  |  Corruption %.0f%%  |  Pack %s'
DEMO_HINT = (
    'Oswald: clear Corrupt Toons with melee (~hackslash 0)  |  '
    '~stopreclaim to end'
)
# Finale pack banners keep the street reading as a boss fight.
FINALE_PACK_BANNER = {
    1: 'Ink Overlord swell — Oswald holds the line!',
    2: "Unleashed ink tide — Oswald's cheer rings hollow!",
}

# Wave-start announce (readable rubber-hose plate on pack spawn).
# Title reads "Wave 2 of 4 — Ink packs inbound"; Oswald tip sits under it.
WAVE_ANNOUNCE_HOLD_SEC = 2.35
WAVE_BANNER_POP_SCALE_ANNOUNCE = 0.125
WAVE_BANNER_POP_SEC_ANNOUNCE = 0.12
WAVE_BANNER_COLOR = (1.0, 0.88, 0.42, 1.0)
WAVE_SUB_BANNER_COLOR = (1.0, 0.96, 0.82, 1.0)
WAVE_BANNER_COLOR_PUNCHLINE = (0.72, 0.92, 0.55, 1.0)
WAVE_SUB_BANNER_COLOR_PUNCHLINE = (0.88, 0.98, 0.78, 1.0)

# Persistent reclaim purity meter (aspect2d bar: pollution → purity fill).
# Empty bar = street still inky; fills warm as packs clear pollution.
PURITY_METER_POS = (0.0, 0.0, 0.50)
PURITY_METER_WIDTH = 0.72
PURITY_METER_HEIGHT = 0.038
PURITY_METER_RIM_PAD = 0.012
PURITY_METER_BIN = 45
PURITY_METER_LABEL = 'PURITY'
PURITY_METER_LABEL_SCALE = 0.038
PURITY_METER_LABEL_Z = 0.055
PURITY_METER_PCT_FMT = '%.0f%%'
PURITY_METER_PCT_SCALE = 0.034
PURITY_METER_PCT_Z = -0.002
PURITY_METER_TRACK_COLOR = (0.12, 0.08, 0.16, 0.82)
PURITY_METER_RIM_COLOR = (0.95, 0.88, 0.55, 0.55)
PURITY_METER_RIM_FINALE_P1 = (1.0, 0.55, 0.95, 0.65)
PURITY_METER_RIM_FINALE_P2 = (1.0, 0.35, 0.28, 0.7)
# Fill lerps ink-purple → sunny Toontown cream as purity rises.
PURITY_METER_FILL_POLLUTED = (0.42, 0.18, 0.55, 0.95)
PURITY_METER_FILL_PURE = (1.0, 0.95, 0.55, 0.98)
PURITY_METER_LABEL_COLOR = (1.0, 0.96, 0.78, 1.0)
PURITY_METER_PCT_COLOR = (1.0, 1.0, 0.9, 1.0)
PURITY_METER_PCT_POLLUTED = (0.85, 0.55, 0.95, 1.0)
PURITY_METER_PCT_PURE = (0.55, 0.95, 0.65, 1.0)
# Rubber-hose pop when a pack reclaim bumps purity.
PURITY_METER_POP_THRESHOLD = 0.04
PURITY_METER_POP_SEC = 0.09
PURITY_METER_POP_SCALE_Z = 1.55

# Reclaim-complete purity burst (HUD overlay + sting).
# Overlay lives on aspect2d so hood geom tint / fog grade stay untouched.
PURITY_BURST_PEAK_ALPHA = 0.78
PURITY_BURST_IN_SEC = 0.07
PURITY_BURST_HOLD_SEC = 0.14
PURITY_BURST_OUT_SEC = 0.58
PURITY_BURST_COLOR = (1.0, 1.0, 0.82, 1.0)
PURITY_RING_PEAK_SCALE = 2.55
PURITY_RING_SEC = 0.52
PURITY_BANNER_POP_SCALE = 0.14
PURITY_BANNER_POP_SEC = 0.16
# Existing toon SFX — light celebration sting, optional if asset missing.
PURITY_STING_SFX = 'phase_4/audio/sfx/AA_sound_whistle.ogg'
PURITY_STING_VOLUME = 0.9
# Second cheer beat (jump) layered by ReclaimCheer client.
PURITY_CHEER_SFX = 'phase_3.5/audio/sfx/AV_jump_2.ogg'
# Rubber-hose cheer pitch swell (SFX playRate ramp on wave clear / purity).
# Start low → peak bright → soft settle; wave clear stays quieter than purity.
CHEER_PITCH_START = 0.78
CHEER_PITCH_PEAK = 1.42
CHEER_PITCH_END = 1.06
CHEER_PITCH_SWELL_SEC = 0.16
CHEER_PITCH_SETTLE_SEC = 0.14
CHEER_PITCH_VOLUME = 0.88
CHEER_PITCH_VOLUME_WAVE = 0.7
# Light avatar squash on wave clear (full bounce stays on purity restore).
WAVE_CLEAR_BOUNCE_PEAK = 1.08
WAVE_CLEAR_BOUNCE_SEC = 0.1

# Cartoon camera punch on purity restore (between finisher 12° and finale 18°).
PURITY_FOV_PUNCH = 15.0
PURITY_FOV_IN_SEC = 0.07
PURITY_FOV_OUT_SEC = 0.38
# Soft camera pull-back / lift (local camera space units).
PURITY_CAM_PULL = 0.85
PURITY_CAM_LIFT = 0.22
PURITY_CAM_IN_SEC = 0.09
PURITY_CAM_OUT_SEC = 0.42
# Extra aspect2d juice layered by PurityBurstFx (rays / outer ring / sparks).
PURITY_OUTER_RING_PEAK = 3.1
PURITY_OUTER_RING_SEC = 0.7
PURITY_RAY_COUNT = 8
PURITY_RAY_PEAK_ALPHA = 0.55
PURITY_RAY_SEC = 0.48
PURITY_SPARK_COUNT = 10
PURITY_SPARK_SEC = 0.42

WAVE_BANNER_FMT = 'Wave %s of %s — %s'
# Legacy short labels (finale / older callers still use waveLabel).
WAVE_LABELS = (
    'Ink blotches appear!',
    'Corruption thickens!',
    'Ink surge!',
    'Final ink tide!',
)
# Short inbound phrase after the em dash — Toontown rubber-hose tone.
WAVE_INBOUND_DEFAULT = 'Ink packs inbound'
WAVE_INBOUND_BY_ZONE = {
    ToontownGlobals.LoopyLane: 'Ink packs inbound',
    ToontownGlobals.PunchlinePlace: 'Sludge packs inbound',
    ToontownGlobals.SillyStreet: 'Ink packs inbound',
}
WAVE_INBOUND_FINALE = {
    1: 'Overlord pack inbound',
    2: 'Unleashed pack inbound',
}
# Oswald tip flavor under the wave plate (Loopy / Punchline focused).
OSWALD_WAVE_TIPS_LOOPY = (
    'Oswald tips: stretch-punch those Ink Smudges!',
    'Oswald tips his ears — keep Loopy Lane laughing!',
    'Oswald cheers: one more pack and Loopy is pure!',
)
OSWALD_WAVE_TIPS_PUNCHLINE = (
    'Oswald tips: dodge Brute spit, snip Balloon Snares!',
    'Oswald: Punchline Place needs that rubber-hose bounce!',
    'Oswald tips his ears — sludge packs keep coming!',
    'Oswald: last laugh for Punchline — clear this wave!',
)
OSWALD_WAVE_TIPS_DEFAULT = (
    'Oswald tips: stretch-punch the pack!',
    'Oswald tips his ears — hold the street!',
    'Oswald: clear the ink, save the neighborhood!',
    'Oswald cheers: final pack — reclaim it!',
)


def waveLabel(waveIndex, maxWaves):
    """Player-facing label for the current wave (legacy / finale fallback)."""
    waveIndex = max(1, int(waveIndex))
    maxWaves = max(1, int(maxWaves))
    if waveIndex >= maxWaves:
        return WAVE_LABELS[-1]
    idx = min(waveIndex - 1, len(WAVE_LABELS) - 2)
    return WAVE_LABELS[idx]


def waveInboundLabel(zoneId=None, finalePhase=0):
    """Short inbound phrase for the wave-start banner em-dash."""
    phase = int(finalePhase or 0)
    if phase >= 1:
        return WAVE_INBOUND_FINALE.get(phase, WAVE_INBOUND_DEFAULT)
    zone = int(zoneId or 0)
    return WAVE_INBOUND_BY_ZONE.get(zone, WAVE_INBOUND_DEFAULT)


def waveAnnounceTitle(waveIndex, maxWaves, zoneId=None, finalePhase=0):
    """Readable wave-start title, e.g. 'Wave 2 of 4 — Ink packs inbound'."""
    wave = max(1, int(waveIndex))
    total = max(1, int(maxWaves))
    inbound = waveInboundLabel(zoneId=zoneId, finalePhase=finalePhase)
    return WAVE_BANNER_FMT % (wave, total, inbound)


def waveOswaldTip(waveIndex, maxWaves, zoneId=None, packCount=0):
    """Oswald tip line under the wave plate (Loopy / Punchline flavor)."""
    wave = max(1, int(waveIndex))
    total = max(1, int(maxWaves))
    zone = int(zoneId or 0)
    if zone == ToontownGlobals.LoopyLane:
        tips = OSWALD_WAVE_TIPS_LOOPY
    elif zone == ToontownGlobals.PunchlinePlace:
        tips = OSWALD_WAVE_TIPS_PUNCHLINE
    else:
        tips = OSWALD_WAVE_TIPS_DEFAULT
    idx = min(wave - 1, len(tips) - 1)
    tip = tips[idx]
    count = int(packCount or 0)
    if count > 0 and wave >= total:
        return '%s  ·  %s inbound' % (tip, count)
    if count > 0:
        return '%s  ·  pack of %s' % (tip, count)
    return tip


def waveAnnounceColors(zoneId=None):
    """Warm rubber-hose banner colors (Punchline leans gag-green)."""
    zone = int(zoneId or 0)
    if zone == ToontownGlobals.PunchlinePlace:
        return WAVE_BANNER_COLOR_PUNCHLINE, WAVE_SUB_BANNER_COLOR_PUNCHLINE
    return WAVE_BANNER_COLOR, WAVE_SUB_BANNER_COLOR


def waveClearedOswaldTip(waveIndex, zoneId=None):
    """Brief Oswald beat between waves (Loopy / Punchline flavor)."""
    wave = int(waveIndex)
    zone = int(zoneId or 0)
    if zone == ToontownGlobals.LoopyLane:
        return 'Oswald tips his ears — next Loopy pack soon'
    if zone == ToontownGlobals.PunchlinePlace:
        return 'Oswald: Punchline pause — next sludge surge incoming'
    return 'Wave %s down — next surge incoming' % wave


def wavePackSize(baseSize, waveIndex):
    """Escalate pack count each wave without exploding spawn count."""
    base = max(1, int(baseSize))
    wave = max(1, int(waveIndex))
    bonus = min(WAVE_MAX_EXTRA, (wave - 1) * WAVE_SIZE_BONUS)
    return base + bonus


def waveCorruptHp(baseHp, waveIndex):
    """Scale corrupt HP upward for later waves."""
    if baseHp is None:
        from toontown.corruption import CorruptionGlobals
        baseHp = CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP
    wave = max(1, int(waveIndex))
    scale = 1.0 + ((wave - 1) * WAVE_HP_SCALE)
    return max(1, int(round(float(baseHp) * scale)))


def pickPackArchetype(waveIndex, slotIndex, packCount, bruteFraction=None,
                      bruteWaveStart=None, snareFraction=None,
                      snareWaveStart=None):
    """Choose Smudge (0), Brute (1), or Balloon Snare (2) for one pack slot.

    Keeps wave-1 / zero-fraction packs as pure Ink Smudge so Loopy demos
    and early reclaim stay familiar. Brutes take rear slots; Snares take
    front slots so zip-lash reads before tank spit.
    """
    from toontown.corruption import CorruptionGlobals
    wave = max(1, int(waveIndex))
    count = max(0, int(packCount))
    if count <= 0:
        return CorruptionGlobals.ARCHETYPE_INK

    bruteStart = (
        BRUTE_WAVE_START if bruteWaveStart is None else int(bruteWaveStart))
    bruteFrac = (
        BRUTE_FRACTION if bruteFraction is None else float(bruteFraction))
    snareStart = (
        SNARE_WAVE_START if snareWaveStart is None else int(snareWaveStart))
    snareFrac = (
        SNARE_FRACTION if snareFraction is None else float(snareFraction))

    bruteSlots = 0
    if wave >= bruteStart and bruteFrac > 0.0:
        bruteSlots = max(1, int(round(count * bruteFrac)))
        bruteSlots = min(bruteSlots, count)
    snareSlots = 0
    if wave >= snareStart and snareFrac > 0.0:
        snareSlots = max(1, int(round(count * snareFrac)))
        snareSlots = min(snareSlots, count)
    # Leave at least one Smudge when the pack has room.
    if bruteSlots + snareSlots >= count and count > 1:
        overflow = bruteSlots + snareSlots - (count - 1)
        while overflow > 0 and snareSlots > 0:
            snareSlots -= 1
            overflow -= 1
        while overflow > 0 and bruteSlots > 0:
            bruteSlots -= 1
            overflow -= 1

    slot = int(slotIndex)
    if bruteSlots and slot >= (count - bruteSlots):
        return CorruptionGlobals.ARCHETYPE_BRUTE
    if snareSlots and slot < snareSlots:
        return CorruptionGlobals.ARCHETYPE_SNARE
    return CorruptionGlobals.ARCHETYPE_INK


def packSlotName(archetype, smudgeName=None, bruteName=None, snareName=None,
                 slotIndex=0, packCount=1):
    """Display name for a pack slot (numbered when pack has multiples)."""
    from toontown.corruption import CorruptionGlobals
    arch = CorruptionGlobals.normalizeArchetype(archetype)
    if arch == CorruptionGlobals.ARCHETYPE_BRUTE:
        base = bruteName or BRUTE_NAME
    elif arch == CorruptionGlobals.ARCHETYPE_SNARE:
        base = snareName or SNARE_NAME
    else:
        base = smudgeName or SMUDGE_NAME
    if packCount > 1 and int(slotIndex) > 0:
        return '%s %s' % (base, int(slotIndex) + 1)
    return base


def packSlotHp(archetype, baseHp, waveIndex):
    """Wave-scaled base HP for a pack slot.

    Brute tankiness comes from DistributedCorruptToonAI hpScale — do not
    pre-multiply here or HP double-scales.
    """
    return waveCorruptHp(baseHp, waveIndex)
