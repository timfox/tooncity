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

# Sludge Brute mix for non-campaign reclaim (Ink Smudge stays majority).
# Wave 1 = pure Smudge; later waves introduce a few tanks.
BRUTE_WAVE_START = 2
BRUTE_FRACTION = 0.34
BRUTE_NAME = 'Sludge Brute'
SMUDGE_NAME = 'Ink Smudge'

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
BANNER_COMPLETE_SUB = 'Neighborhood cheer returns!'
BANNER_WAVE_CLEARED = 'Wave cleared — hold the street!'
POLLUTION_HINT_FMT = 'Corruption  %.0f%%'
STATUS_FMT = 'Wave %s/%s  |  Corruption %.0f%%  |  Pack %s'
DEMO_HINT = (
    'Reclaim: clear Corrupt Toons with melee (~hackslash 0)  |  '
    '~stopreclaim to end'
)
# Finale pack banners keep the street reading as a boss fight.
FINALE_PACK_BANNER = {
    1: 'Ink Overlord swell!',
    2: 'Unleashed ink tide!',
}

# Reclaim-complete purity burst (HUD overlay + sting).
# Overlay lives on aspect2d so hood geom tint / fog grade stay untouched.
PURITY_BURST_PEAK_ALPHA = 0.72
PURITY_BURST_IN_SEC = 0.08
PURITY_BURST_HOLD_SEC = 0.12
PURITY_BURST_OUT_SEC = 0.55
PURITY_BURST_COLOR = (1.0, 1.0, 0.82, 1.0)
PURITY_RING_PEAK_SCALE = 2.4
PURITY_RING_SEC = 0.55
PURITY_BANNER_POP_SCALE = 0.13
PURITY_BANNER_POP_SEC = 0.18
# Existing toon SFX — light celebration sting, optional if asset missing.
PURITY_STING_SFX = 'phase_4/audio/sfx/AA_sound_whistle.ogg'
PURITY_STING_VOLUME = 0.85
# Second cheer beat (jump) layered by ReclaimCheer client.
PURITY_CHEER_SFX = 'phase_3.5/audio/sfx/AV_jump_2.ogg'

WAVE_BANNER_FMT = 'Wave %s/%s — %s'
WAVE_LABELS = (
    'Ink blotches appear!',
    'Corruption thickens!',
    'Ink surge!',
    'Final ink tide!',
)


def waveLabel(waveIndex, maxWaves):
    """Player-facing label for the current wave."""
    waveIndex = max(1, int(waveIndex))
    maxWaves = max(1, int(maxWaves))
    if waveIndex >= maxWaves:
        return WAVE_LABELS[-1]
    idx = min(waveIndex - 1, len(WAVE_LABELS) - 2)
    return WAVE_LABELS[idx]


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
                      bruteWaveStart=None):
    """Choose Smudge (0) or Brute (1) for one pack slot.

    Keeps wave-1 / zero-fraction packs as pure Ink Smudge so Loopy demos
    and early reclaim stay familiar.
    """
    from toontown.corruption import CorruptionGlobals
    wave = max(1, int(waveIndex))
    start = BRUTE_WAVE_START if bruteWaveStart is None else int(bruteWaveStart)
    fraction = BRUTE_FRACTION if bruteFraction is None else float(bruteFraction)
    if wave < start or fraction <= 0.0 or packCount <= 0:
        return CorruptionGlobals.ARCHETYPE_SMUDGE
    # Spread brutes across the pack instead of clumping at the end.
    bruteSlots = max(1, int(round(packCount * fraction)))
    bruteSlots = min(bruteSlots, packCount)
    # Prefer center / rear slots so front-liners still read as Smudge melee.
    startSlot = max(0, packCount - bruteSlots)
    if int(slotIndex) >= startSlot:
        return CorruptionGlobals.ARCHETYPE_BRUTE
    return CorruptionGlobals.ARCHETYPE_SMUDGE


def packSlotName(archetype, smudgeName=None, bruteName=None, slotIndex=0,
                 packCount=1):
    """Display name for a pack slot (numbered when pack has multiples)."""
    from toontown.corruption import CorruptionGlobals
    arch = CorruptionGlobals.normalizeArchetype(archetype)
    if arch == CorruptionGlobals.ARCHETYPE_BRUTE:
        base = bruteName or BRUTE_NAME
    else:
        base = smudgeName or SMUDGE_NAME
    if packCount > 1 and int(slotIndex) > 0:
        return '%s %s' % (base, int(slotIndex) + 1)
    return base


def packSlotHp(archetype, baseHp, waveIndex):
    """HP for a pack slot; Brutes use their higher default when base is unset."""
    from toontown.corruption import CorruptionGlobals
    arch = CorruptionGlobals.normalizeArchetype(archetype)
    if baseHp is None:
        hpBase = CorruptionGlobals.archetypeDefaultHp(arch)
    elif arch == CorruptionGlobals.ARCHETYPE_BRUTE:
        # Campaign/act base HP is tuned for Smudge — bump Brutes ~1.6x.
        hpBase = max(int(baseHp), int(round(float(baseHp) * 1.6)))
    else:
        hpBase = int(baseHp)
    return waveCorruptHp(hpBase, waveIndex)
