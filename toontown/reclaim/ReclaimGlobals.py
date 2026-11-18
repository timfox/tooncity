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

# Per-street reclaim packs for auto / R / ~startreclaim (PlayEntry path).
# Loopy is the Act 1 tutorial street: Ink Smudge wave 1, later Brutes.
# Punchline is the Act 2 explore → fight → reclaim beat: denser sludge,
# Brutes + Balloon Snares from wave 1. Silly is the Act 3 Overlord finale
# street (Oswald still trusted — twist stays campaign P2 reveal). Campaign C
# still uses ACTS params; this table keeps discoverable auto-reclaim matched
# to each hood fantasy. No keyblades / KH branding.
# Keys match DistributedReclaimDirectorAI.start() kwargs (+ copy helpers).
_STREET_PACK_START_KEYS = (
    'seedPollution', 'packSize', 'maxPacks', 'corruptHp', 'corruptName',
    'bruteFraction', 'bruteWaveStart', 'bruteName',
    'snareFraction', 'snareWaveStart', 'snareName',
)
STREET_PACKS = {
    # Act 1 — Loopy Lane ink street (first hood / melee tutorial).
    # Smudge-first; Brutes (+ light Snares) from wave 2 — mirrors default
    # reclaim mix so auto / R / ~startreclaim match the familiar Loopy beat.
    ToontownGlobals.LoopyLane: {
        'packId': 'loopy-smudge',
        'name': 'Loopy Lane',
        'seedPollution': 0.55,
        'packSize': 3,
        'maxPacks': 4,
        'corruptHp': 30,
        'corruptName': 'Ink Smudge',
        # Wave 1 = pure Smudge; later waves introduce ~⅓ Brutes + light Snares.
        'bruteFraction': 0.34,
        'bruteWaveStart': 2,
        'bruteName': 'Sludge Brute',
        'snareFraction': 0.22,
        'snareWaveStart': 2,
        'snareName': 'Balloon Snare',
        'bannerStart': 'OSWALD: RECLAIM LOOPY LANE!',
        'bannerStartSub': (
            'Explore the inky street — then stretch-punch '
            'Ink Smudges with Oswald!'),
        'bannerStartColor': (1.0, 0.92, 0.45, 1.0),
        'bannerComplete': 'LOOPY LANE IS PURE!',
        'bannerCompleteSub': (
            'Oswald tips his ears — Punchline Place is next!'),
        'demoHint': (
            'Oswald: stretch-punch Ink Smudges  |  '
            'F fight  |  C campaign'),
        'playEntryTip': (
            'Oswald: Loopy Lane — explore the ink  →  '
            'F fight Smudges  →  reclaim  |  Shift dodge  |  C campaign'),
        'autoFlash': (
            'Oswald fields Loopy ink packs — Ink Smudges inbound!'),
        'reclaimLiveFlash': (
            'LOOPY RECLAIM LIVE — clear Ink Smudges with F!'),
        'statusLabel': 'INK',
    },
    # Act 2 — Punchline Place sludge street (second hood).
    ToontownGlobals.PunchlinePlace: {
        'packId': 'punchline-sludge',
        'name': 'Punchline Place',
        'seedPollution': 0.70,
        'packSize': 4,
        'maxPacks': 4,
        'corruptHp': 40,
        'corruptName': 'Gunk Gagster',
        'bruteFraction': 0.4,
        'bruteWaveStart': 1,
        'bruteName': 'Sludge Brute',
        'snareFraction': 0.25,
        'snareWaveStart': 1,
        'snareName': 'Balloon Snare',
        'bannerStart': 'OSWALD: RECLAIM PUNCHLINE PLACE!',
        'bannerStartSub': (
            'Explore the sludge street — then stretch-punch '
            'Brutes & Balloon Snares!'),
        'bannerStartColor': (0.72, 0.92, 0.55, 1.0),
        'bannerComplete': 'PUNCHLINE PLACE LAUGHS CLEAN!',
        'bannerCompleteSub': (
            'Oswald tips his ears — Silly Street finale awaits!'),
        'demoHint': (
            'Oswald: dodge Brute spit, snip Balloon Snares  |  '
            'F fight  |  C campaign'),
        'playEntryTip': (
            'Oswald: Punchline Place — explore the sludge  →  '
            'F fight packs  →  reclaim  |  Shift dodge  |  C campaign'),
        'autoFlash': (
            'Oswald fields Punchline sludge packs — '
            'Brutes & Balloon Snares!'),
        'reclaimLiveFlash': (
            'PUNCHLINE RECLAIM LIVE — clear Brutes & Snares with F!'),
        'statusLabel': 'SLUDGE',
    },
    # Act 3 — Silly Street Ink Overlord finale (third hood).
    # Mirrors ACTS finale P1 spawn mix for auto / R / ~startreclaim.
    # Oswald stays the trusted lead; twist is campaign P2 only.
    ToontownGlobals.SillyStreet: {
        'packId': 'silly-overlord',
        'name': 'Silly Street',
        'seedPollution': 0.75,
        'packSize': 1,
        'maxPacks': 2,
        'corruptHp': 90,
        'corruptName': 'Ink Overlord',
        # Boss street — Overlord only (no Brute / Snare mix).
        'bruteFraction': 0.0,
        'snareFraction': 0.0,
        'bannerStart': 'OSWALD: RECLAIM SILLY STREET!',
        'bannerStartSub': (
            'Explore the magenta ink — then stretch-punch '
            'the Ink Overlord with Oswald!'),
        'bannerStartColor': (1.0, 0.55, 0.95, 1.0),
        'bannerComplete': 'SILLY STREET HOLDS THE LINE!',
        'bannerCompleteSub': (
            'Oswald tips his ears — neighborhood cheer returns!'),
        'demoHint': (
            'Oswald: stretch-punch the Ink Overlord  |  '
            'F fight  |  C campaign'),
        'playEntryTip': (
            'Oswald: Silly Street finale — explore the ink  →  '
            'F fight Overlord  →  reclaim  |  Shift dodge  |  C campaign'),
        'autoFlash': (
            'Oswald fields Silly Street packs — Ink Overlord inbound!'),
        'reclaimLiveFlash': (
            'SILLY RECLAIM LIVE — clear the Ink Overlord with F!'),
        'statusLabel': 'OVERLORD',
    },
}
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
WAVE_BANNER_COLOR_SILLY = (1.0, 0.55, 0.95, 1.0)
WAVE_SUB_BANNER_COLOR_SILLY = (1.0, 0.82, 0.98, 1.0)

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
# Rubber-hose tick/fill pop when a pack reclaim bumps purity.
# Fill: flat squash → tall stretch (X may briefly overshoot purity) → settle.
# Pct text gets a matching uniform hose tick; cream flecks pop at the fill tip.
PURITY_METER_POP_THRESHOLD = 0.04
PURITY_METER_POP_SQUASH = (0.92, 1.0, 0.55, 0.05)   # sx, sy, sz multipliers, sec
PURITY_METER_POP_STRETCH = (1.06, 1.0, 1.62, 0.07)
PURITY_METER_POP_SETTLE_SEC = 0.10
# Legacy single-beat Z peak kept for callers / docs; hose sequence supersedes it.
PURITY_METER_POP_SEC = 0.09
PURITY_METER_POP_SCALE_Z = 1.55
# Pct TextNode tick (multipliers of PURITY_METER_PCT_SCALE).
PURITY_METER_PCT_POP_SQUASH = (1.45, 1.0, 0.58, 0.05)
PURITY_METER_PCT_POP_STRETCH = (0.78, 1.0, 1.42, 0.07)
PURITY_METER_PCT_POP_SETTLE_SEC = 0.09
# Sunny cream flecks at the advancing fill tip (purity, not ink).
PURITY_METER_TICK_FLECK_COUNT = 4
PURITY_METER_TICK_FLECK_SIZE = 0.014
PURITY_METER_TICK_FLECK_DRIFT = 0.085
PURITY_METER_TICK_FLECK_SEC = 0.18
PURITY_METER_TICK_FLECK_COLOR = (1.0, 0.96, 0.62, 0.95)
PURITY_METER_TICK_FLECK_END_COLOR = (1.0, 0.92, 0.45, 0.0)
PURITY_METER_TICK_FLECK_BIN = 48

# Polluted reclaim-street entry cream shimmer (aspect2d center veil + flecks).
# Soft lift for tip readability against ink fog — not a purity payoff.
# Composes with PlayEntry ink edge vignette (bin 48), StreetColorWash (28),
# and StreetSparkleFx full-purity glitter (50). Sunny cream only — no KH blue.
ENTRY_CREAM_SHIMMER_ENABLED = True
ENTRY_CREAM_SHIMMER_MIN_POLLUTION = 0.08
ENTRY_CREAM_SHIMMER_ORIGIN = (0.0, 0.0, -0.08)
ENTRY_CREAM_SHIMMER_COLOR = (1.0, 0.97, 0.82, 1.0)
# Above wash veil (28) / haze (25); below purity meter (45) + ink vignette (48).
ENTRY_CREAM_SHIMMER_BIN = 36
ENTRY_CREAM_SHIMMER_PEAK = 0.18
ENTRY_CREAM_SHIMMER_IN_SEC = 0.10
ENTRY_CREAM_SHIMMER_HOLD_SEC = 0.20
ENTRY_CREAM_SHIMMER_OUT_SEC = 0.48
ENTRY_CREAM_SHIMMER_FLECK_COUNT = 8
ENTRY_CREAM_SHIMMER_FLECK_SIZE = 0.018
ENTRY_CREAM_SHIMMER_FLECK_RISE = 0.38
ENTRY_CREAM_SHIMMER_FLECK_SPREAD = 0.95
ENTRY_CREAM_SHIMMER_FLECK_SEC = 0.42
ENTRY_CREAM_SHIMMER_FLECK_COLOR = (1.0, 0.98, 0.72, 0.88)
ENTRY_CREAM_SHIMMER_FLECK_END_COLOR = (1.0, 0.94, 0.55, 0.0)

# Progressive street cream wash while reclaim purity fills (geom + soft veil).
# Matches purity-meter / burst cream — rubber-hose sunny clear, not KH blue.
# Overlay bin sits above pollution ink haze (25) and below purity meter (45).
STREET_WASH_CREAM = (1.0, 0.97, 0.82)
STREET_WASH_STRENGTH = 1.0
STREET_WASH_OVERLAY_PEAK_ALPHA = 0.20
STREET_WASH_OVERLAY_BIN = 28
STREET_WASH_LERP_SEC = 0.32
STREET_WASH_ADVANCE_SEC = 0.42
STREET_WASH_CLEAR_SEC = 0.55

# Full-purity / reclaim-complete street sparkle (horizon cream glitter).
# Layers with StreetColorWash soft-clear + PurityBurstFx FOV/rays; bigger than
# wave cream burst (#73). Sunny Toontown cream only — no KH blue / keyblades.
STREET_SPARKLE_ENABLED = True
STREET_SPARKLE_ORIGIN = (0.0, 0.0, -0.42)
STREET_SPARKLE_COLOR = (1.0, 0.97, 0.82, 1.0)
STREET_SPARKLE_BIN = 50
STREET_SPARKLE_SHIMMER_PEAK = 0.22
STREET_SPARKLE_SHIMMER_IN_SEC = 0.08
STREET_SPARKLE_SHIMMER_HOLD_SEC = 0.18
STREET_SPARKLE_SHIMMER_OUT_SEC = 0.55
STREET_SPARKLE_COUNT = 16
STREET_SPARKLE_SIZE = 0.022
STREET_SPARKLE_RISE = 0.72
STREET_SPARKLE_SPREAD = 1.35
STREET_SPARKLE_SEC = 0.62
STREET_SPARKLE_FLECK_COLOR = (1.0, 0.98, 0.72, 0.95)
STREET_SPARKLE_FLECK_END_COLOR = (1.0, 0.94, 0.55, 0.0)

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

# Rubber-hose cream burst on wave clear (aspect2d flash + flecks + soft ring).
# Lighter cousin of purity restore burst — layers with cheer swell / street wash.
# Sunny Toontown cream only (matches STREET_WASH / purity meter); no KH blue.
WAVE_CLEAR_CREAM_ENABLED = True
WAVE_CLEAR_CREAM_FLASH_PEAK = 0.34
WAVE_CLEAR_CREAM_FLASH_IN_SEC = 0.05
WAVE_CLEAR_CREAM_FLASH_HOLD_SEC = 0.06
WAVE_CLEAR_CREAM_FLASH_OUT_SEC = 0.28
WAVE_CLEAR_CREAM_COLOR = (1.0, 0.97, 0.82, 1.0)
WAVE_CLEAR_CREAM_RING_PEAK = 1.85
WAVE_CLEAR_CREAM_RING_SEC = 0.36
WAVE_CLEAR_CREAM_RING_PEAK_ALPHA = 0.48
WAVE_CLEAR_CREAM_FLECK_COUNT = 8
WAVE_CLEAR_CREAM_FLECK_SIZE = 0.028
WAVE_CLEAR_CREAM_FLECK_DRIFT = 0.42
WAVE_CLEAR_CREAM_FLECK_SEC = 0.32
WAVE_CLEAR_CREAM_FLECK_COLOR = (1.0, 0.96, 0.62, 0.95)
WAVE_CLEAR_CREAM_FLECK_END_COLOR = (1.0, 0.92, 0.45, 0.0)
WAVE_CLEAR_CREAM_ORIGIN = (0.0, 0.0, 0.12)
WAVE_CLEAR_CREAM_BIN = 52
# Warm cream wave-clear banner (was icy cyan; keep rubber-hose sunny).
WAVE_CLEAR_BANNER_COLOR = (1.0, 0.94, 0.62, 1.0)
WAVE_CLEAR_SUB_BANNER_COLOR = (1.0, 0.97, 0.82, 1.0)
WAVE_CLEAR_BANNER_HOLD_SEC = 1.4

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
    ToontownGlobals.SillyStreet: 'Overlord pack inbound',
}
WAVE_INBOUND_FINALE = {
    1: 'Overlord pack inbound',
    2: 'Unleashed pack inbound',
}
# Oswald tip flavor under the wave plate (trusted lead until finale reveal).
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
OSWALD_WAVE_TIPS_SILLY = (
    'Oswald stands with you — stretch-punch the Ink Overlord!',
    'Oswald tips his ears — hold Silly Street!',
    'Oswald: magenta swell incoming — keep punching!',
    'Oswald cheers: final Overlord pack — reclaim Silly!',
)
OSWALD_WAVE_TIPS_DEFAULT = (
    'Oswald tips: stretch-punch the pack!',
    'Oswald tips his ears — hold the street!',
    'Oswald: clear the ink, save the neighborhood!',
    'Oswald cheers: final pack — reclaim it!',
)


def streetPack(zoneId):
    """Return the STREET_PACKS entry for a zone, or None."""
    return STREET_PACKS.get(int(zoneId or 0))


def streetPackId(zoneId):
    """Stable pack id string (e.g. 'punchline-sludge'), or None."""
    pack = streetPack(zoneId)
    if not pack:
        return None
    return pack.get('packId')


def streetPackParams(zoneId):
    """Kwargs for DistributedReclaimDirectorAI.start() from STREET_PACKS.

    Loopy returns Smudge-first with Brutes from wave 2. Punchline returns
    Brute + Snare mix from wave 1. Silly returns Ink Overlord-only finale
    spawn (no Brute / Snare). Empty dict → caller keeps module defaults.
    """
    pack = streetPack(zoneId)
    if not pack:
        return {}
    out = {}
    for key in _STREET_PACK_START_KEYS:
        if key in pack:
            out[key] = pack[key]
    return out


def streetBannerStart(zoneId, finalePhase=0):
    """Start banner title for a street pack (finale uses CampaignGlobals)."""
    if int(finalePhase or 0) >= 1:
        return BANNER_START
    pack = streetPack(zoneId)
    if pack and pack.get('bannerStart'):
        return pack['bannerStart']
    return BANNER_START


def streetBannerStartSub(zoneId, finalePhase=0):
    """Optional start sub-banner (explore → fight beat per street pack)."""
    if int(finalePhase or 0) >= 1:
        return ''
    pack = streetPack(zoneId)
    if pack:
        return pack.get('bannerStartSub') or ''
    return ''


def streetBannerStartColor(zoneId, finalePhase=0):
    """Start banner color; Punchline leans gag-green."""
    if int(finalePhase or 0) >= 1:
        return (1.0, 0.92, 0.45, 1.0)
    pack = streetPack(zoneId)
    if pack and pack.get('bannerStartColor'):
        return tuple(pack['bannerStartColor'])
    return (1.0, 0.92, 0.45, 1.0)


def streetBannerComplete(zoneId, finalePhase=0):
    """Complete banner title (Punchline laughs-clean beat)."""
    if int(finalePhase or 0) >= 2:
        return BANNER_COMPLETE
    pack = streetPack(zoneId)
    if pack and pack.get('bannerComplete'):
        return pack['bannerComplete']
    return BANNER_COMPLETE


def streetBannerCompleteSub(zoneId, finalePhase=0):
    """Complete sub-banner; Punchline cues Silly finale."""
    pack = streetPack(zoneId)
    if pack and pack.get('bannerCompleteSub') and int(finalePhase or 0) < 2:
        return pack['bannerCompleteSub']
    return BANNER_COMPLETE_SUB


def streetDemoHint(zoneId, finalePhase=0):
    """Persistent demo / combat hint under the tip bar."""
    if int(finalePhase or 0) >= 1:
        return DEMO_HINT
    pack = streetPack(zoneId)
    if pack and pack.get('demoHint'):
        return pack['demoHint']
    return DEMO_HINT


def streetPlayEntryTip(zoneId, face='Oswald', fallbackName='this street'):
    """PlayEntry tip for explore → fight → reclaim (hood STREET_PACK aware)."""
    pack = streetPack(zoneId)
    if pack and pack.get('playEntryTip'):
        # Tips already name Oswald; keep face substitution if copy uses %s.
        tip = pack['playEntryTip']
        if '%s' in tip:
            return tip % face
        return tip
    return (
        '%s: CORRUPTION on %s — packs incoming  |  '
        'F fight  |  Shift dodge  |  C campaign' % (face, fallbackName))


def streetAutoFlash(zoneId, face='Oswald'):
    """Flash when PlayEntry auto-fields reclaim packs."""
    pack = streetPack(zoneId)
    if pack and pack.get('autoFlash'):
        return pack['autoFlash']
    return '%s fields the packs — Fight!' % face


def streetReclaimLiveFlash(zoneId, face='Oswald'):
    """Flash when announceReclaimStart lands on the client."""
    pack = streetPack(zoneId)
    if pack and pack.get('reclaimLiveFlash'):
        return pack['reclaimLiveFlash']
    return 'RECLAIM LIVE — %s says clear them with F!' % face


def streetStatusLabel(zoneId, finalePhase=0):
    """Optional status HUD prefix (e.g. SLUDGE on Punchline)."""
    if int(finalePhase or 0) >= 1:
        return None
    pack = streetPack(zoneId)
    if pack:
        return pack.get('statusLabel')
    return None


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
    """Oswald tip line under the wave plate (Loopy / Punchline / Silly)."""
    wave = max(1, int(waveIndex))
    total = max(1, int(maxWaves))
    zone = int(zoneId or 0)
    if zone == ToontownGlobals.LoopyLane:
        tips = OSWALD_WAVE_TIPS_LOOPY
    elif zone == ToontownGlobals.PunchlinePlace:
        tips = OSWALD_WAVE_TIPS_PUNCHLINE
    elif zone == ToontownGlobals.SillyStreet:
        tips = OSWALD_WAVE_TIPS_SILLY
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
    """Warm rubber-hose banner colors (Punchline gag-green / Silly magenta)."""
    zone = int(zoneId or 0)
    if zone == ToontownGlobals.PunchlinePlace:
        return WAVE_BANNER_COLOR_PUNCHLINE, WAVE_SUB_BANNER_COLOR_PUNCHLINE
    if zone == ToontownGlobals.SillyStreet:
        return WAVE_BANNER_COLOR_SILLY, WAVE_SUB_BANNER_COLOR_SILLY
    return WAVE_BANNER_COLOR, WAVE_SUB_BANNER_COLOR


def waveClearedOswaldTip(waveIndex, zoneId=None):
    """Brief Oswald beat between waves (Loopy / Punchline / Silly flavor)."""
    wave = int(waveIndex)
    zone = int(zoneId or 0)
    if zone == ToontownGlobals.LoopyLane:
        return 'Oswald tips his ears — next Loopy pack soon'
    if zone == ToontownGlobals.PunchlinePlace:
        return 'Oswald: Punchline pause — next sludge surge incoming'
    if zone == ToontownGlobals.SillyStreet:
        return 'Oswald: Silly pause — next Overlord swell incoming'
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
