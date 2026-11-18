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
# Gunk Gagster gag-lob puddle — Punchline-forward; default reclaim keeps 0.
GAGSTER_WAVE_START = 2
GAGSTER_FRACTION = 0.0
GAGSTER_NAME = 'Gunk Gagster'

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
# Gunk Gagsters + Brutes + Balloon Snares from wave 1. Silly is the Act 3
# Overlord finale street (Oswald still trusted — twist stays campaign P2
# reveal). Campaign C still uses ACTS params; this table keeps discoverable
# auto-reclaim matched to each hood fantasy. No keyblades / KH branding.
# Keys match DistributedReclaimDirectorAI.start() kwargs (+ copy helpers).
_STREET_PACK_START_KEYS = (
    'seedPollution', 'packSize', 'maxPacks', 'corruptHp', 'corruptName',
    'bruteFraction', 'bruteWaveStart', 'bruteName',
    'snareFraction', 'snareWaveStart', 'snareName',
    'gagsterFraction', 'gagsterWaveStart', 'gagsterName',
    'waveScripts',
    # Silly Overlord street reclaim uses P1 rain AI (campaign owns P2).
    'finalePhase',
)
# Optional per-wave archetype scripts (tokens or ints). When present for a
# wave, composition + pack size follow the script; otherwise fractions +
# WAVE_SIZE_BONUS keep the legacy escalate path. Tokens are Toontown-tone
# aliases for Ink Smudge / Sludge Brute / Balloon Snare / Gunk Gagster —
# no KH branding.
WAVE_SCRIPT_TOKENS = {
    'ink': 0,
    'smudge': 0,
    'ink_smudge': 0,
    'ink-smudge': 0,
    'brute': 1,
    'sludge': 1,
    'sludge_brute': 1,
    'sludge-brute': 1,
    'snare': 2,
    'balloon': 2,
    'balloon_snare': 2,
    'balloon-snare': 2,
    'gagster': 3,
    'gunk': 3,
    'gunk_gagster': 3,
    'gunk-gagster': 3,
    'gag': 3,
}
STREET_PACKS = {
    # Act 1 — Loopy Lane ink street (first hood / melee tutorial).
    # Scripted beats: Smudge tutorial → Brute intro → Snare joins → mixed.
    # Fraction fields remain as fallback when a wave has no script.
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
        # Per-wave scripts (Smudge tutorial → Brute → Snare → mixed elite).
        'waveScripts': (
            ('ink', 'ink', 'ink'),
            ('ink', 'ink', 'brute'),
            ('snare', 'ink', 'brute', 'ink'),
            ('snare', 'ink', 'brute', 'snare', 'ink'),
        ),
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
    # Scripted beats: Snare-front + Gagster lob → Gagster swarm → Brute pair
    # → elite mix. Gunk Gagster is a real fourth archetype (not a Smudge rename).
    ToontownGlobals.PunchlinePlace: {
        'packId': 'punchline-sludge',
        'name': 'Punchline Place',
        'seedPollution': 0.70,
        'packSize': 4,
        'maxPacks': 4,
        'corruptHp': 40,
        'corruptName': 'Ink Smudge',
        'bruteFraction': 0.3,
        'bruteWaveStart': 1,
        'bruteName': 'Sludge Brute',
        'snareFraction': 0.2,
        'snareWaveStart': 1,
        'snareName': 'Balloon Snare',
        'gagsterFraction': 0.3,
        'gagsterWaveStart': 1,
        'gagsterName': 'Gunk Gagster',
        'waveScripts': (
            ('snare', 'gagster', 'ink', 'brute'),
            ('snare', 'gagster', 'gagster', 'brute', 'ink'),
            ('snare', 'gagster', 'brute', 'brute', 'ink'),
            ('snare', 'gagster', 'gagster', 'brute', 'snare', 'ink'),
        ),
        'bannerStart': 'OSWALD: RECLAIM PUNCHLINE PLACE!',
        'bannerStartSub': (
            'Explore the sludge street — then stretch-punch '
            'Gunk Gagsters, Brutes & Balloon Snares!'),
        'bannerStartColor': (0.72, 0.92, 0.55, 1.0),
        'bannerComplete': 'PUNCHLINE PLACE LAUGHS CLEAN!',
        'bannerCompleteSub': (
            'Oswald tips his ears — Silly Street finale awaits!'),
        'demoHint': (
            'Oswald: dodge Gagster lobs & Brute spit, snip Snares  |  '
            'F fight  |  C campaign'),
        'playEntryTip': (
            'Oswald: Punchline Place — explore the sludge  →  '
            'F fight packs  →  reclaim  |  Shift dodge  |  C campaign'),
        'autoFlash': (
            'Oswald fields Punchline sludge packs — '
            'Gunk Gagsters, Brutes & Balloon Snares!'),
        'reclaimLiveFlash': (
            'PUNCHLINE RECLAIM LIVE — clear Gagsters, Brutes & Snares with F!'),
        'statusLabel': 'SLUDGE',
    },
    # Act 3 — Silly Street Ink Overlord finale (third hood).
    # Scripted Overlord beats only (no Brute / Snare) — twin swell on wave 2.
    # Oswald stays the trusted lead; twist is campaign P2 only.
    ToontownGlobals.SillyStreet: {
        'packId': 'silly-overlord',
        'name': 'Silly Street',
        'seedPollution': 0.75,
        'packSize': 1,
        'maxPacks': 2,
        'corruptHp': 90,
        'corruptName': 'Ink Overlord',
        # Boss street — Overlord only (no Brute / Snare / Gagster mix).
        'bruteFraction': 0.0,
        'snareFraction': 0.0,
        'gagsterFraction': 0.0,
        'waveScripts': (
            ('ink',),
            ('ink', 'ink'),
        ),
        # P1 rising-rain combat AI (campaign phase2 owns Unleashed + adds).
        'finalePhase': 1,
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

# Cream edge pulse framing wave-announce banners (aspect2d border strips).
# Soft rubber-hose cream frame that pops with the plate — lighter than wave-clear
# center burst (#73) and opposite of PlayEntry ink edge vignette (corruption).
# Sunny cream only; no keyblades / KH branding.
WAVE_ANNOUNCE_CREAM_EDGE_ENABLED = True
WAVE_ANNOUNCE_CREAM_EDGE_COLOR = (1.0, 0.97, 0.82, 1.0)
WAVE_ANNOUNCE_CREAM_EDGE = 0.28  # strip thickness in aspect2d units
WAVE_ANNOUNCE_CREAM_EDGE_PEAK = 0.42
WAVE_ANNOUNCE_CREAM_EDGE_PULSE = 0.28  # mid-beat alpha after peak
WAVE_ANNOUNCE_CREAM_EDGE_IN_SEC = 0.08
WAVE_ANNOUNCE_CREAM_EDGE_HOLD_SEC = 0.10
WAVE_ANNOUNCE_CREAM_EDGE_PULSE_SEC = 0.12
WAVE_ANNOUNCE_CREAM_EDGE_OUT_SEC = 0.36
# Below wave-clear cream burst (52); above purity meter (45) / entry shimmer (36).
WAVE_ANNOUNCE_CREAM_EDGE_BIN = 50
WAVE_ANNOUNCE_CREAM_EDGE_FLECK_COUNT = 6
WAVE_ANNOUNCE_CREAM_EDGE_FLECK_SIZE = 0.022
WAVE_ANNOUNCE_CREAM_EDGE_FLECK_DRIFT = 0.18
WAVE_ANNOUNCE_CREAM_EDGE_FLECK_SEC = 0.28
WAVE_ANNOUNCE_CREAM_EDGE_FLECK_COLOR = (1.0, 0.96, 0.62, 0.9)
WAVE_ANNOUNCE_CREAM_EDGE_FLECK_END_COLOR = (1.0, 0.92, 0.45, 0.0)
# Flecks cluster near the wave plate (banner ~z 0.78).
WAVE_ANNOUNCE_CREAM_EDGE_FLECK_ORIGIN = (0.0, 0.0, 0.72)
# StreetSparkle-style cream sparkle flecks layered on the cream edge pulse.
# Rising chip/cross glitter along the top cream frame — quieter than full-purity
# StreetSparkle (#77); tip flecks (#87) stay as the short drift cousins.
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_ENABLED = True
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_COUNT = 8
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_SIZE = 0.018
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_RISE = 0.30
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_SPREAD = 1.10
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_SEC = 0.36
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_COLOR = (1.0, 0.98, 0.72, 0.90)
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_END_COLOR = (1.0, 0.94, 0.55, 0.0)
# Along the top cream strip (edge ~z 1.0 - EDGE); below tip-fleck origin.
WAVE_ANNOUNCE_CREAM_EDGE_SPARKLE_ORIGIN = (0.0, 0.0, 0.68)
# Wave-announce cream wash pulse — soft aspect2d veil after cream edge sparkle
# (#113) / cream edge (#87). Purity-fill / wave-clear / cheer cream wash
# grammar. Quieter than wave-clear wash (#144) / cheer wash (#142);
# cream/pastel only. Toggle WAVE_ANNOUNCE_CREAM_EDGE_WASH_ENABLED = False
# drops wash only.
WAVE_ANNOUNCE_CREAM_EDGE_WASH_ENABLED = True
WAVE_ANNOUNCE_CREAM_EDGE_WASH_DELAY_SEC = 0.40  # after edge pulse; after sparkle (~0.36)
WAVE_ANNOUNCE_CREAM_EDGE_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
WAVE_ANNOUNCE_CREAM_EDGE_WASH_PEAK = 0.09
WAVE_ANNOUNCE_CREAM_EDGE_WASH_MID = 0.045
WAVE_ANNOUNCE_CREAM_EDGE_WASH_IN_SEC = 0.05
WAVE_ANNOUNCE_CREAM_EDGE_WASH_PULSE_SEC = 0.09
WAVE_ANNOUNCE_CREAM_EDGE_WASH_HOLD_SEC = 0.06
WAVE_ANNOUNCE_CREAM_EDGE_WASH_OUT_SEC = 0.34
WAVE_ANNOUNCE_CREAM_EDGE_WASH_BIN = 48  # soft veil under edge (50) / flecks (51) / sparkles (52)

# Wave-start purity meter hose pop — brief rubber-hose squash→stretch→settle on
# the whole meter when a pack wave begins so wave begin reads clearly.
# Distinct from mid-wave rim-only danger flash (#213) and secured-lock green
# hold + soft uniform scale (#209). Sunny cream rim accent only; no KH branding.
# Toggle WAVE_START_METER_POP_ENABLED = False drops meter pop only (announce
# plate / cream edge still fire).
WAVE_START_METER_POP_ENABLED = True
WAVE_START_METER_POP_SQUASH = (0.88, 1.0, 0.62, 0.05)  # sx, sy, sz, sec
WAVE_START_METER_POP_STRETCH = (1.10, 1.0, 1.28, 0.07)
WAVE_START_METER_POP_SETTLE_SEC = 0.10
WAVE_START_METER_RIM_COLOR = (1.0, 0.94, 0.55, 0.78)  # sunny cream, not warn/lock
WAVE_START_METER_RIM_SEC = 0.22

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
# Cream shimmer flecks along the filled bar on purity tick (StreetSparkle /
# EntryCreamShimmer chip style). Layers with tip flecks — sunny pastel only.
PURITY_METER_FILL_SHIMMER_ENABLED = True
PURITY_METER_FILL_SHIMMER_COUNT = 7
PURITY_METER_FILL_SHIMMER_SIZE = 0.011
PURITY_METER_FILL_SHIMMER_RISE = 0.055
PURITY_METER_FILL_SHIMMER_SEC = 0.28
PURITY_METER_FILL_SHIMMER_COLOR = (1.0, 0.98, 0.72, 0.92)
PURITY_METER_FILL_SHIMMER_END_COLOR = (1.0, 0.94, 0.55, 0.0)
# Above meter fill (45) / tip flecks (48); below street sparkle (50).
PURITY_METER_FILL_SHIMMER_BIN = 49
# Delayed cream aftershock after purity fill cream shimmer (PurityMeterHud).
# Residual soft flecks settle downward along the filled span + optional soft
# cream halo — same residual grammar as cheer cream aftershock (#118). Quieter
# / smaller than mid-screen cheer aftershock. Cream/pastel only.
PURITY_METER_FILL_AFTERSHOCK_ENABLED = True
PURITY_METER_FILL_AFTERSHOCK_DELAY_SEC = 0.18
PURITY_METER_FILL_AFTERSHOCK_COUNT = 4
PURITY_METER_FILL_AFTERSHOCK_SIZE = 0.009
PURITY_METER_FILL_AFTERSHOCK_DRIFT = 0.045
PURITY_METER_FILL_AFTERSHOCK_FALL = 0.04
PURITY_METER_FILL_AFTERSHOCK_SEC = 0.32
PURITY_METER_FILL_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.82)
PURITY_METER_FILL_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
# Above fill shimmer (49); below street sparkle (50).
PURITY_METER_FILL_AFTERSHOCK_BIN = 50
PURITY_METER_FILL_AFTERSHOCK_HALO_ENABLED = True
PURITY_METER_FILL_AFTERSHOCK_HALO_HALF = 0.055
PURITY_METER_FILL_AFTERSHOCK_HALO_START = 0.35
PURITY_METER_FILL_AFTERSHOCK_HALO_PEAK = 1.35
PURITY_METER_FILL_AFTERSHOCK_HALO_SEC = 0.26
PURITY_METER_FILL_AFTERSHOCK_HALO_PEAK_ALPHA = 0.16
PURITY_METER_FILL_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)
# Purity-fill cream wash pulse — soft aspect2d veil after cream aftershock
# (#123) / fill shimmer (#90). Cheer / wave-clear / entry / purity cream wash
# grammar. Quieter than cheer wash (#142) / purity-complete wash (#104);
# cream/pastel only. Toggle PURITY_METER_FILL_CREAM_WASH_ENABLED = False
# drops wash only.
PURITY_METER_FILL_CREAM_WASH_ENABLED = True
PURITY_METER_FILL_CREAM_WASH_DELAY_SEC = 0.40  # after shimmer; after aftershock (0.18)
PURITY_METER_FILL_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
PURITY_METER_FILL_CREAM_WASH_PEAK = 0.09
PURITY_METER_FILL_CREAM_WASH_MID = 0.045
PURITY_METER_FILL_CREAM_WASH_IN_SEC = 0.05
PURITY_METER_FILL_CREAM_WASH_PULSE_SEC = 0.09
PURITY_METER_FILL_CREAM_WASH_HOLD_SEC = 0.06
PURITY_METER_FILL_CREAM_WASH_OUT_SEC = 0.34
PURITY_METER_FILL_CREAM_WASH_BIN = 48  # soft veil under fill shimmer (49) / aftershock (50)

# Mid-wave purity pressure tip — contested rubber-hose whisper after incomplete
# reclaim re-creep (#194). Client-only: when purity stalls or ink rises mid-wave
# with packs still alive, director shows a short HUD tip + meter rim warn.
# Toggle PURITY_PRESSURE_TIP_ENABLED = False drops whisper + rim warn only.
# Sunny/warm Toontown tone — no KH branding.
PURITY_PRESSURE_TIP_ENABLED = True
PURITY_PRESSURE_MIN_WAVE = 1  # waveIndex >= this counts as mid-wave pressure
PURITY_PRESSURE_STALL_SEC = 8.0
PURITY_PRESSURE_RISE_THRESHOLD = 0.04  # pollution bump that counts as ink pressure
PURITY_PRESSURE_ADVANCE_THRESHOLD = 0.04  # purity climb that resets stall clock
PURITY_PRESSURE_COOLDOWN_SEC = 12.0
PURITY_PRESSURE_TIP_HOLD_SEC = 2.4
PURITY_PRESSURE_TIP_SCALE = 0.038
PURITY_PRESSURE_TIP_POS = (0.0, 0.0, 0.40)  # under purity meter (z 0.50)
PURITY_PRESSURE_TIP_COLOR = (1.0, 0.88, 0.55, 1.0)
PURITY_PRESSURE_TIP_POP_SCALE = 0.052
PURITY_PRESSURE_TIP_POP_SEC = 0.10
PURITY_PRESSURE_REASON_STALL = 'stall'
PURITY_PRESSURE_REASON_RISE = 'rise'
PURITY_PRESSURE_TIP_STALL = (
    "Whoa — purity's stalling! Keep punching or the ink digs in!"
)
PURITY_PRESSURE_TIP_RISE = (
    "Ink's pushing back! Don't let this wave go contested!"
)
# Contested rim flash on PurityMeterHud when the tip whispers (#213 deepen).
# Warm triple-pulse cream-accent blink so mid-wave pressure reads juicier —
# distinct from secured-lock green hold + whole-meter hose-pop (#209),
# wave-clear mid-screen cream sparkle (#229), and purity-complete meter
# hose settle (#225). No KH branding.
# Toggle PURITY_PRESSURE_RIM_FLASH_ENABLED = False drops flash + cream flecks.
PURITY_PRESSURE_RIM_FLASH_ENABLED = True
PURITY_PRESSURE_RIM_WARN_COLOR = (1.0, 0.62, 0.42, 0.90)  # creamier warm danger
PURITY_PRESSURE_RIM_FLASH_PULSES = 3
PURITY_PRESSURE_RIM_FLASH_ON_SEC = 0.09
PURITY_PRESSURE_RIM_FLASH_OFF_SEC = 0.06
PURITY_PRESSURE_RIM_FLASH_HOLD_SEC = 0.16  # final peak dwell
PURITY_PRESSURE_RIM_FLASH_SCALE = 1.24  # rim-only nudge (not whole meter)
# Legacy alias kept for older reads; flash hold prefers FLASH_HOLD_SEC.
PURITY_PRESSURE_RIM_WARN_SEC = 0.16
# Warm cream flecks + soft halo layered on the rim flash so contested danger
# pops juicier without restaging wave-clear glitter or complete hose settle.
# Local to the purity meter root. Toggle
# PURITY_PRESSURE_RIM_FLASH_CREAM_ENABLED = False drops flecks + halo only.
PURITY_PRESSURE_RIM_FLASH_CREAM_ENABLED = True
PURITY_PRESSURE_RIM_FLASH_CREAM_COUNT = 5
PURITY_PRESSURE_RIM_FLASH_CREAM_SIZE = 0.012
PURITY_PRESSURE_RIM_FLASH_CREAM_DRIFT = 0.10
PURITY_PRESSURE_RIM_FLASH_CREAM_SEC = 0.28
PURITY_PRESSURE_RIM_FLASH_CREAM_COLOR = (1.0, 0.94, 0.68, 0.92)
PURITY_PRESSURE_RIM_FLASH_CREAM_END_COLOR = (1.0, 0.88, 0.48, 0.0)
PURITY_PRESSURE_RIM_FLASH_CREAM_BIN = 48  # over meter rim (45); under fill shimmer (49)
PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_ENABLED = True
PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_HALF = 0.072
PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_START = 0.42
PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_PEAK = 1.28
PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_SEC = 0.24
PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_PEAK_ALPHA = 0.18
PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_COLOR = (1.0, 0.93, 0.72, 1.0)

# Secured purity lock tip — after full reclaim, confirm ink cannot re-creep
# (#194 complement). Client HUD tip + meter rim confirm; AI lock lives on
# PollutionManagerAI._purityLocked. Toggle SECURED_LOCK_TIP_ENABLED = False
# drops tip + rim confirm only (AI lock still holds). No KH branding.
SECURED_LOCK_TIP_ENABLED = True
SECURED_LOCK_TIP = (
    "Street's secured! That ink can't creep back — purity's locked in!"
)
SECURED_LOCK_TIP_HOLD_SEC = 2.8
SECURED_LOCK_TIP_SCALE = 0.038
SECURED_LOCK_TIP_POS = (0.0, 0.0, 0.40)  # under purity meter (z 0.50)
SECURED_LOCK_TIP_COLOR = (0.72, 1.0, 0.82, 1.0)
SECURED_LOCK_TIP_POP_SCALE = 0.052
SECURED_LOCK_TIP_POP_SEC = 0.10
SECURED_LOCK_RIM_COLOR = (0.55, 1.0, 0.72, 0.88)
SECURED_LOCK_RIM_SEC = 0.85
# Keep purity meter visible briefly so the secured rim confirm reads.
SECURED_LOCK_HUD_HOLD_SEC = 1.15
# Secured-lock purity sparkle sting — short green-cream flecks + quiet pitch
# sting when the street purity lock seals (#205). Distinct from mid-wave
# pressure tip (#202), wave-clear cream sparkle, cheer flecks, and
# StreetSparkle horizon glitter. Toggle SECURED_LOCK_SPARKLE_ENABLED = False
# drops flecks + sting; tip/rim still fire. No KH branding.
SECURED_LOCK_SPARKLE_ENABLED = True
SECURED_LOCK_SPARKLE_DELAY_SEC = 0.04
SECURED_LOCK_SPARKLE_ORIGIN = (0.0, 0.0, 0.42)  # near tip / under meter
SECURED_LOCK_SPARKLE_COUNT = 7
SECURED_LOCK_SPARKLE_SIZE = 0.017
SECURED_LOCK_SPARKLE_RISE = 0.22
SECURED_LOCK_SPARKLE_SPREAD = 0.48
SECURED_LOCK_SPARKLE_SEC = 0.30
SECURED_LOCK_SPARKLE_BIN = 54  # above cheer flecks (53); under purity burst
SECURED_LOCK_SPARKLE_COLOR = (0.78, 1.0, 0.86, 0.92)  # green-cream lock glitter
SECURED_LOCK_SPARKLE_END_COLOR = (0.55, 1.0, 0.72, 0.0)
# Quiet cheer-cousin pitch sting (not the full purity whistle on restore).
SECURED_LOCK_STING_ENABLED = True
SECURED_LOCK_STING_SFX = 'phase_3.5/audio/sfx/AV_jump_2.ogg'
SECURED_LOCK_STING_VOLUME = 0.55
SECURED_LOCK_STING_PITCH_START = 0.92
SECURED_LOCK_STING_PITCH_PEAK = 1.28
SECURED_LOCK_STING_PITCH_END = 1.08
SECURED_LOCK_STING_SWELL_SEC = 0.10
SECURED_LOCK_STING_SETTLE_SEC = 0.10
# Soft meter hose-pop when secured rim confirms (HUD sting cousin of tip pop).
SECURED_LOCK_METER_POP_SCALE = 1.12
SECURED_LOCK_METER_POP_SEC = 0.09

# Purity-complete meter hose settle — after restore celebration settles
# (purityRestoreSettled), soft tall stretch → longer settle on the full meter
# so the finish reads clearly. Distinct from wave-start squash→stretch pop
# (#220) and secured-lock green soft uniform scale (#209). Sunny pure cream
# rim accent only; no KH branding. Toggle PURITY_COMPLETE_METER_SETTLE_ENABLED
# = False drops meter settle only (celebration / lock tip still fire).
PURITY_COMPLETE_METER_SETTLE_ENABLED = True
# Mild tall stretch (no flat squash — that is wave-start's signature).
PURITY_COMPLETE_METER_SETTLE_STRETCH = (1.05, 1.0, 1.22, 0.08)  # sx, sy, sz, sec
PURITY_COMPLETE_METER_SETTLE_SEC = 0.16
PURITY_COMPLETE_METER_SETTLE_RIM_COLOR = (1.0, 0.97, 0.70, 0.82)  # pure cream
PURITY_COMPLETE_METER_SETTLE_RIM_SEC = 0.28
# Keep meter up through restore celebration + hose settle (not just lock confirm).
PURITY_COMPLETE_METER_SETTLE_HUD_HOLD_SEC = 0.55

# Polluted reclaim-street entry cream shimmer (aspect2d center veil + flecks).
# Soft lift for tip readability against ink fog — not a purity payoff.
# Composes with EntryCreamWashPulseFx (bin 32), PlayEntry ink edge vignette
# (bin 48), StreetColorWash (28), and StreetSparkleFx full-purity glitter (50).
# Sunny cream only — no KH blue.
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

# Polluted reclaim-street entry cream wash pulse (StreetColorWash veil grammar).
# Soft full-screen cream pop with EntryCreamShimmerFx — sibling of purity-complete
# cream wash pulse (#104), softer / not a payoff flash. Progressive wash stays
# separate. Sunny pastel only — no KH blue. Above progressive wash (28); below
# entry shimmer (36) / ink vignette (48).
ENTRY_CREAM_WASH_PULSE_ENABLED = True
ENTRY_CREAM_WASH_PULSE_MIN_POLLUTION = 0.08
ENTRY_CREAM_WASH_PULSE_COLOR = (1.0, 0.97, 0.82)
ENTRY_CREAM_WASH_PULSE_BIN = 32
ENTRY_CREAM_WASH_PULSE_PEAK = 0.16
ENTRY_CREAM_WASH_PULSE_MID = 0.09
ENTRY_CREAM_WASH_PULSE_IN_SEC = 0.08
ENTRY_CREAM_WASH_PULSE_PULSE_SEC = 0.14
ENTRY_CREAM_WASH_PULSE_HOLD_SEC = 0.12
ENTRY_CREAM_WASH_PULSE_OUT_SEC = 0.50
# Cream aftershock after entry cream wash pulse (#109) — residual flecks settle
# downward with a soft cream halo (wave-clear cream aftershock #127 grammar).
# Quieter than wave-clear residual; settle cream wash arms after this residual.
# Sunny pastel only; no KH blue. Above wash pulse (32); below entry shimmer (36).
ENTRY_CREAM_WASH_AFTERSHOCK_ENABLED = True
ENTRY_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.22
ENTRY_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.08)
ENTRY_CREAM_WASH_AFTERSHOCK_COUNT = 5
ENTRY_CREAM_WASH_AFTERSHOCK_SIZE = 0.015
ENTRY_CREAM_WASH_AFTERSHOCK_DRIFT = 0.28
ENTRY_CREAM_WASH_AFTERSHOCK_FALL = 0.22
ENTRY_CREAM_WASH_AFTERSHOCK_SEC = 0.32
ENTRY_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.78)
ENTRY_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
ENTRY_CREAM_WASH_AFTERSHOCK_BIN = 34
ENTRY_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
ENTRY_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.48
ENTRY_CREAM_WASH_AFTERSHOCK_HALO_START = 0.26
ENTRY_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.15
ENTRY_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.26
ENTRY_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.12
ENTRY_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)
# Soft cream wash pulse after entry cream aftershock (#132) / wash pulse (#109).
# Cheer (#142) / FOV purity (#164) / wave-clear (#144) cream wash grammar.
# Quieter than the entry wash pulse (peak 0.16); cream/pastel only. Arms from
# EntryCreamWashPulseFx.playPulse (delay relative to pulse start). Toggle
# ENTRY_AFTERSHOCK_CREAM_WASH_ENABLED = False drops settle wash only.
ENTRY_AFTERSHOCK_CREAM_WASH_ENABLED = True
ENTRY_AFTERSHOCK_CREAM_WASH_DELAY_SEC = 0.40  # after pulse; after aftershock (0.22)
ENTRY_AFTERSHOCK_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
ENTRY_AFTERSHOCK_CREAM_WASH_PEAK = 0.09
ENTRY_AFTERSHOCK_CREAM_WASH_MID = 0.045
ENTRY_AFTERSHOCK_CREAM_WASH_IN_SEC = 0.05
ENTRY_AFTERSHOCK_CREAM_WASH_PULSE_SEC = 0.09
ENTRY_AFTERSHOCK_CREAM_WASH_HOLD_SEC = 0.06
ENTRY_AFTERSHOCK_CREAM_WASH_OUT_SEC = 0.34
ENTRY_AFTERSHOCK_CREAM_WASH_BIN = 30  # soft veil under wash pulse (32) / aftershock (34)

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
# Cream aftershock after progressive street cream wash (#69) — residual flecks
# settle downward + soft halo when purity advances (pack clear). Same grammar
# as entry wash aftershock (#132), wave-clear aftershock (#127), purity-complete
# aftershock (#136). Quieter than entry residual; not a second wash pulse.
# Above progressive wash (28); below entry wash pulse (32). Sunny pastel only;
# no KH blue. Toggle STREET_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
STREET_WASH_AFTERSHOCK_ENABLED = True
STREET_WASH_AFTERSHOCK_DELAY_SEC = 0.22
STREET_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.10)
STREET_WASH_AFTERSHOCK_COUNT = 5
STREET_WASH_AFTERSHOCK_SIZE = 0.014
STREET_WASH_AFTERSHOCK_DRIFT = 0.26
STREET_WASH_AFTERSHOCK_FALL = 0.20
STREET_WASH_AFTERSHOCK_SEC = 0.32
STREET_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.76)
STREET_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
STREET_WASH_AFTERSHOCK_BIN = 30
STREET_WASH_AFTERSHOCK_HALO_ENABLED = True
STREET_WASH_AFTERSHOCK_HALO_HALF = 0.46
STREET_WASH_AFTERSHOCK_HALO_START = 0.24
STREET_WASH_AFTERSHOCK_HALO_PEAK = 1.12
STREET_WASH_AFTERSHOCK_HALO_SEC = 0.26
STREET_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.11
STREET_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Purity-complete cream wash pulse (StreetColorWash veil grammar).
# Full-screen soft cream pop on purityRestoreFx, layered under StreetSparkleFx
# horizon glitter. Progressive wash still soft-clears separately. Sunny pastel
# only — no KH blue. Above progressive wash (28); below sparkle (50).
PURITY_COMPLETE_CREAM_WASH_ENABLED = True
PURITY_COMPLETE_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)
PURITY_COMPLETE_CREAM_WASH_BIN = 40
PURITY_COMPLETE_CREAM_WASH_PEAK = 0.28
PURITY_COMPLETE_CREAM_WASH_MID = 0.16
PURITY_COMPLETE_CREAM_WASH_IN_SEC = 0.07
PURITY_COMPLETE_CREAM_WASH_PULSE_SEC = 0.12
PURITY_COMPLETE_CREAM_WASH_HOLD_SEC = 0.10
PURITY_COMPLETE_CREAM_WASH_OUT_SEC = 0.55

# Cream aftershock after purity-complete cream wash (#104) — residual flecks
# settle downward + soft halo after the wash pulse. Same grammar as entry wash
# aftershock (#132), wave-clear aftershock (#127), purity-fill aftershock (#123).
# Settle cream wash arms after this residual. Above wash (40); below
# StreetSparkleFx (50). Sunny pastel only — no KH blue.
PURITY_COMPLETE_CREAM_AFTERSHOCK_ENABLED = True
PURITY_COMPLETE_CREAM_AFTERSHOCK_DELAY_SEC = 0.20
PURITY_COMPLETE_CREAM_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.06)
PURITY_COMPLETE_CREAM_AFTERSHOCK_COUNT = 5
PURITY_COMPLETE_CREAM_AFTERSHOCK_SIZE = 0.016
PURITY_COMPLETE_CREAM_AFTERSHOCK_DRIFT = 0.30
PURITY_COMPLETE_CREAM_AFTERSHOCK_FALL = 0.24
PURITY_COMPLETE_CREAM_AFTERSHOCK_SEC = 0.34
PURITY_COMPLETE_CREAM_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.80)
PURITY_COMPLETE_CREAM_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
PURITY_COMPLETE_CREAM_AFTERSHOCK_BIN = 42
PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_ENABLED = True
PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_HALF = 0.50
PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_START = 0.28
PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_PEAK = 1.18
PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_SEC = 0.28
PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.14
PURITY_COMPLETE_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)
# Soft cream wash pulse after purity-complete cream aftershock (#136) / wash (#104).
# Entry settle (#170) / cheer (#142) / FOV purity (#164) / wave-clear (#144)
# cream wash grammar. Quieter than the purity-complete wash pulse (peak 0.28);
# cream/pastel only. Arms from PurityCompleteCreamWashFx.playPulse (delay
# relative to pulse start). Toggle PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_ENABLED
# = False drops settle wash only.
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_ENABLED = True
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_DELAY_SEC = 0.40  # after pulse; after aftershock (0.20)
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_PEAK = 0.09
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_MID = 0.045
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_IN_SEC = 0.05
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_PULSE_SEC = 0.09
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_HOLD_SEC = 0.06
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_OUT_SEC = 0.34
PURITY_COMPLETE_AFTERSHOCK_CREAM_WASH_BIN = 38  # soft veil under wash (40) / aftershock (42)

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
# Cream sparkle flecks layered on cheer pitch swell (StreetSparkle / EntryCream).
# Short mid-screen chips timed with SFX playRate ramp — not a shimmer hang or
# wave-clear burst restage. Sunny pastel only; no KH blue. Above burst (52).
CHEER_CREAM_SPARKLE_ENABLED = True
CHEER_CREAM_SPARKLE_ORIGIN = (0.0, 0.0, 0.06)
CHEER_CREAM_SPARKLE_BIN = 53
CHEER_CREAM_SPARKLE_COUNT = 12
CHEER_CREAM_SPARKLE_COUNT_WAVE = 7
CHEER_CREAM_SPARKLE_SIZE = 0.020
CHEER_CREAM_SPARKLE_RISE = 0.42
CHEER_CREAM_SPARKLE_RISE_WAVE = 0.28
CHEER_CREAM_SPARKLE_SPREAD = 0.88
CHEER_CREAM_SPARKLE_SPREAD_WAVE = 0.62
CHEER_CREAM_SPARKLE_SEC = 0.34
CHEER_CREAM_SPARKLE_SEC_WAVE = 0.26
CHEER_CREAM_SPARKLE_COLOR = (1.0, 0.98, 0.72, 0.92)
CHEER_CREAM_SPARKLE_END_COLOR = (1.0, 0.94, 0.55, 0.0)
# Delayed cream aftershock after cheer cream sparkle (CheerCreamSparkleFx).
# Residual soft flecks settle downward + optional cream halo — same residual
# grammar as hang / perfect-dodge cream aftershock. Quieter than the sparkle
# pop; wave clear uses fewer/shorter cousins. Cream/pastel only.
CHEER_CREAM_AFTERSHOCK_ENABLED = True
CHEER_CREAM_AFTERSHOCK_DELAY_SEC = 0.22
CHEER_CREAM_AFTERSHOCK_COUNT = 6
CHEER_CREAM_AFTERSHOCK_COUNT_WAVE = 4
CHEER_CREAM_AFTERSHOCK_SIZE = 0.016
CHEER_CREAM_AFTERSHOCK_DRIFT = 0.36
CHEER_CREAM_AFTERSHOCK_FALL = 0.28
CHEER_CREAM_AFTERSHOCK_SEC = 0.38
CHEER_CREAM_AFTERSHOCK_SEC_WAVE = 0.30
CHEER_CREAM_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.82)
CHEER_CREAM_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
CHEER_CREAM_AFTERSHOCK_BIN = 54
CHEER_CREAM_AFTERSHOCK_HALO_ENABLED = True
CHEER_CREAM_AFTERSHOCK_HALO_HALF = 0.38
CHEER_CREAM_AFTERSHOCK_HALO_START = 0.22
CHEER_CREAM_AFTERSHOCK_HALO_PEAK = 1.15
CHEER_CREAM_AFTERSHOCK_HALO_SEC = 0.30
CHEER_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.18
CHEER_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)
# Cheer cream wash pulse — soft aspect2d veil after cream aftershock (#118).
# Hit / perfect-dodge / entry / purity cream wash grammar. Quieter than
# purity-complete wash (cheer also layers with that on restore); cream/pastel
# only. Toggle CHEER_CREAM_WASH_ENABLED = False drops wash only.
CHEER_CREAM_WASH_ENABLED = True
CHEER_CREAM_WASH_DELAY_SEC = 0.40  # after play; after aftershock (0.22)
CHEER_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
CHEER_CREAM_WASH_PEAK = 0.11
CHEER_CREAM_WASH_MID = 0.06
CHEER_CREAM_WASH_IN_SEC = 0.05
CHEER_CREAM_WASH_PULSE_SEC = 0.09
CHEER_CREAM_WASH_HOLD_SEC = 0.06
CHEER_CREAM_WASH_OUT_SEC = 0.36
CHEER_CREAM_WASH_BIN = 50  # soft veil under cheer sparkle flecks (53)
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
# Cream shimmer hang after wave-clear cream burst (EntryCream / StreetSparkle).
# Delayed residual veil + flecks — hang after flash/ring, not a second burst.
# Sunny pastel only; no KH blue. Below burst flash (52); above announce edge (50).
WAVE_CLEAR_CREAM_SHIMMER_ENABLED = True
WAVE_CLEAR_CREAM_SHIMMER_DELAY_SEC = 0.28
WAVE_CLEAR_CREAM_SHIMMER_ORIGIN = (0.0, 0.0, 0.10)
WAVE_CLEAR_CREAM_SHIMMER_COLOR = (1.0, 0.97, 0.82, 1.0)
WAVE_CLEAR_CREAM_SHIMMER_BIN = 51
WAVE_CLEAR_CREAM_SHIMMER_PEAK = 0.16
WAVE_CLEAR_CREAM_SHIMMER_IN_SEC = 0.08
WAVE_CLEAR_CREAM_SHIMMER_HOLD_SEC = 0.34
WAVE_CLEAR_CREAM_SHIMMER_OUT_SEC = 0.52
WAVE_CLEAR_CREAM_SHIMMER_FLECK_COUNT = 10
WAVE_CLEAR_CREAM_SHIMMER_FLECK_SIZE = 0.020
WAVE_CLEAR_CREAM_SHIMMER_FLECK_RISE = 0.48
WAVE_CLEAR_CREAM_SHIMMER_FLECK_SPREAD = 1.05
WAVE_CLEAR_CREAM_SHIMMER_FLECK_SEC = 0.55
WAVE_CLEAR_CREAM_SHIMMER_FLECK_COLOR = (1.0, 0.98, 0.72, 0.90)
WAVE_CLEAR_CREAM_SHIMMER_FLECK_END_COLOR = (1.0, 0.94, 0.55, 0.0)
# Delayed cream aftershock after wave-clear cream shimmer (#93).
# Residual soft flecks settle downward + optional cream halo — same residual
# grammar as purity-fill cream aftershock (#123) / cheer cream aftershock
# (#118). Quieter than the shimmer hang; cream/pastel only. Above shimmer
# flecks (51); shares soft residual band with burst flash (52).
WAVE_CLEAR_CREAM_AFTERSHOCK_ENABLED = True
WAVE_CLEAR_CREAM_AFTERSHOCK_DELAY_SEC = 0.24
WAVE_CLEAR_CREAM_AFTERSHOCK_COUNT = 5
WAVE_CLEAR_CREAM_AFTERSHOCK_SIZE = 0.016
WAVE_CLEAR_CREAM_AFTERSHOCK_DRIFT = 0.32
WAVE_CLEAR_CREAM_AFTERSHOCK_FALL = 0.26
WAVE_CLEAR_CREAM_AFTERSHOCK_SEC = 0.34
WAVE_CLEAR_CREAM_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.82)
WAVE_CLEAR_CREAM_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
WAVE_CLEAR_CREAM_AFTERSHOCK_BIN = 52
WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_ENABLED = True
WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_HALF = 0.42
WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_START = 0.28
WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_PEAK = 1.20
WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_SEC = 0.28
WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.14
WAVE_CLEAR_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)
# Wave-clear cream wash pulse — soft aspect2d veil after cream aftershock
# (#127) / clear shimmer (#93). Cheer (#142) / purity-complete (#104) cream
# wash grammar. Quieter than purity-complete wash; cream/pastel only. Arms
# from WaveClearCreamShimmerFx hang start (after shimmer delay). Toggle
# WAVE_CLEAR_CREAM_WASH_ENABLED = False drops wash only (and wash sparkle).
WAVE_CLEAR_CREAM_WASH_ENABLED = True
WAVE_CLEAR_CREAM_WASH_DELAY_SEC = 0.40  # after hang start; after aftershock (0.24)
WAVE_CLEAR_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
WAVE_CLEAR_CREAM_WASH_PEAK = 0.10
WAVE_CLEAR_CREAM_WASH_MID = 0.05
WAVE_CLEAR_CREAM_WASH_IN_SEC = 0.05
WAVE_CLEAR_CREAM_WASH_PULSE_SEC = 0.09
WAVE_CLEAR_CREAM_WASH_HOLD_SEC = 0.06
WAVE_CLEAR_CREAM_WASH_OUT_SEC = 0.34
WAVE_CLEAR_CREAM_WASH_BIN = 50  # soft veil under shimmer flecks (51) / aftershock (52)
# Cream sparkle flecks after wave-clear cream wash (#144) — CheerCreamSparkle /
# StreetSparkle / wave-edge sparkle rising chip grammar. Deepened pack-clear
# glitter lift during wash settle (#182 deepen) — juicier than the quiet
# residual, still below cheer full / StreetSparkle horizon payoff. Not a
# shimmer hang restage, cheer swell restage, secured-lock green sting (#209),
# or purity-complete meter hose settle (#225). Delay is relative to wash
# start (after WAVE_CLEAR_CREAM_WASH_DELAY_SEC). Sunny pastel only; no KH blue.
# Above wash veil (50); shares cheer sparkle band (53).
# Toggle WAVE_CLEAR_CREAM_SPARKLE_ENABLED = False drops sparkles (+ aftershock).
WAVE_CLEAR_CREAM_SPARKLE_ENABLED = True
WAVE_CLEAR_CREAM_SPARKLE_DELAY_SEC = 0.10  # after wash starts
WAVE_CLEAR_CREAM_SPARKLE_ORIGIN = (0.0, 0.0, 0.08)  # mid-screen; not lock tip / street
WAVE_CLEAR_CREAM_SPARKLE_BIN = 53
WAVE_CLEAR_CREAM_SPARKLE_COUNT = 9
WAVE_CLEAR_CREAM_SPARKLE_SIZE = 0.021
WAVE_CLEAR_CREAM_SPARKLE_RISE = 0.36
WAVE_CLEAR_CREAM_SPARKLE_SPREAD = 0.74
WAVE_CLEAR_CREAM_SPARKLE_SEC = 0.36
WAVE_CLEAR_CREAM_SPARKLE_POP = 1.22  # twinkle scale peak — juicier snap
WAVE_CLEAR_CREAM_SPARKLE_COLOR = (1.0, 0.98, 0.72, 0.94)
WAVE_CLEAR_CREAM_SPARKLE_END_COLOR = (1.0, 0.94, 0.55, 0.0)
# Soft cream sparkle aftershock after the deepened rising flecks — quieter
# settle chips + optional halo (cheer / shimmer aftershock grammar). Owns the
# residual glitter hang so pack clear keeps juice without restaging wash.
# Toggle WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_ENABLED = False drops residual only.
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_ENABLED = True
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_DELAY_SEC = 0.18  # after sparkle start
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_COUNT = 4
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_SIZE = 0.015
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_DRIFT = 0.28
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_FALL = 0.22
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_SEC = 0.30
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.80)
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_BIN = 54
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_ENABLED = True
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_HALF = 0.36
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_START = 0.24
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_PEAK = 1.12
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_SEC = 0.26
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_PEAK_ALPHA = 0.12
WAVE_CLEAR_CREAM_SPARKLE_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)
# Warm cream wave-clear banner (was icy cyan; keep rubber-hose sunny).
WAVE_CLEAR_BANNER_COLOR = (1.0, 0.94, 0.62, 1.0)
WAVE_CLEAR_SUB_BANNER_COLOR = (1.0, 0.97, 0.82, 1.0)
WAVE_CLEAR_BANNER_HOLD_SEC = 1.4

# Cartoon camera punch on purity restore (between finisher 12° and finale 18°).
PURITY_FOV_PUNCH = 15.0
PURITY_FOV_IN_SEC = 0.07
PURITY_FOV_OUT_SEC = 0.38
# Soft cream wash pulse after purity FOV punch (#27) — CheerCreamWashPulse /
# PurityCompleteCreamWashFx vocabulary. Soft under burst rays (56) / sparks
# (60); quieter than purity-complete wash (peak 0.28). Sunny pastel only.
# Toggle PURITY_FOV_CREAM_WASH_ENABLED = False drops wash only.
PURITY_FOV_CREAM_WASH_ENABLED = True
PURITY_FOV_CREAM_WASH_DELAY_SEC = 0.22  # after FOV start; soft-lock FOV wash grammar
PURITY_FOV_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
PURITY_FOV_CREAM_WASH_PEAK = 0.10
PURITY_FOV_CREAM_WASH_MID = 0.05
PURITY_FOV_CREAM_WASH_IN_SEC = 0.05
PURITY_FOV_CREAM_WASH_PULSE_SEC = 0.09
PURITY_FOV_CREAM_WASH_HOLD_SEC = 0.06
PURITY_FOV_CREAM_WASH_OUT_SEC = 0.34
PURITY_FOV_CREAM_WASH_BIN = 54  # soft veil under burst rays (56) / sparks (60)
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
    'Oswald tips: dodge Gagster lobs & Brute spit, snip Balloon Snares!',
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

    Loopy / Punchline / Silly return scripted waveScripts (Smudge tutorial,
    Snare-front sludge, Overlord swell) plus fraction fallbacks. Empty dict
    → caller keeps module defaults.
    """
    pack = streetPack(zoneId)
    if not pack:
        return {}
    out = {}
    for key in _STREET_PACK_START_KEYS:
        if key in pack:
            out[key] = pack[key]
    return out


def normalizeWaveScriptToken(token):
    """Map a waveScripts entry to ARCHETYPE_INK / BRUTE / SNARE / GAGSTER.

    Accepts ints, numeric strings, or Toontown-tone aliases
    (ink/smudge, brute/sludge, snare/balloon, gagster/gunk). Unknown → Ink.
    """
    from toontown.corruption import CorruptionGlobals
    if token is None:
        return CorruptionGlobals.ARCHETYPE_INK
    if isinstance(token, bool):
        return CorruptionGlobals.ARCHETYPE_INK
    if isinstance(token, int):
        return CorruptionGlobals.normalizeArchetype(token)
    text = str(token).strip().lower().replace(' ', '_')
    if not text:
        return CorruptionGlobals.ARCHETYPE_INK
    if text.isdigit() or (text.startswith('-') and text[1:].isdigit()):
        return CorruptionGlobals.normalizeArchetype(int(text))
    mapped = WAVE_SCRIPT_TOKENS.get(text)
    if mapped is not None:
        return CorruptionGlobals.normalizeArchetype(mapped)
    return CorruptionGlobals.ARCHETYPE_INK


def resolveWaveScript(waveScripts, waveIndex):
    """Return normalized archetype list for a wave, or None.

    Supports a 1-based dict ({1: (...), 2: (...)}) or a sequence where
    index 0 is wave 1. Empty / missing waves fall back to fraction mix.
    """
    if not waveScripts:
        return None
    wave = max(1, int(waveIndex))
    raw = None
    if isinstance(waveScripts, dict):
        raw = waveScripts.get(wave)
        if raw is None:
            raw = waveScripts.get(str(wave))
    else:
        try:
            length = len(waveScripts)
        except TypeError:
            return None
        if wave > length:
            return None
        raw = waveScripts[wave - 1]
    if raw is None:
        return None
    if isinstance(raw, (str, bytes)) or not hasattr(raw, '__iter__'):
        raw = (raw,)
    script = [normalizeWaveScriptToken(token) for token in raw]
    if not script:
        return None
    return script


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


def isMidWavePressureContext(state, waveIndex, packAlive, minWave=None):
    """True when an active reclaim wave can whisper purity pressure."""
    if int(state) != STATE_ACTIVE:
        return False
    floor = (
        PURITY_PRESSURE_MIN_WAVE if minWave is None else int(minWave))
    if int(waveIndex) < int(floor):
        return False
    return int(packAlive) > 0


def purityPressureReason(pollutionDelta, stallAgeSec,
                         riseThreshold=None, stallSec=None,
                         enabled=None):
    """Return stall/rise reason for a mid-wave pressure whisper, or None.

    Prefer ink-rise over stall when both fire on the same beat. Callers must
    already gate on ``isMidWavePressureContext`` + cooldown.
    """
    if enabled is None:
        enabled = PURITY_PRESSURE_TIP_ENABLED
    if not enabled:
        return None
    rise = (
        PURITY_PRESSURE_RISE_THRESHOLD
        if riseThreshold is None else float(riseThreshold))
    stall = (
        PURITY_PRESSURE_STALL_SEC if stallSec is None else float(stallSec))
    try:
        delta = float(pollutionDelta)
    except (TypeError, ValueError):
        delta = 0.0
    try:
        age = float(stallAgeSec)
    except (TypeError, ValueError):
        age = 0.0
    if delta >= rise:
        return PURITY_PRESSURE_REASON_RISE
    if age >= stall:
        return PURITY_PRESSURE_REASON_STALL
    return None


def purityPressureTipText(reason):
    """Rubber-hose contested tip copy for a pressure reason."""
    if reason == PURITY_PRESSURE_REASON_RISE:
        return PURITY_PRESSURE_TIP_RISE
    if reason == PURITY_PRESSURE_REASON_STALL:
        return PURITY_PRESSURE_TIP_STALL
    return PURITY_PRESSURE_TIP_STALL


def securedLockTipText(zoneId=None):
    """Rubber-hose tip confirming a finished reclaim purity lock."""
    return SECURED_LOCK_TIP


def wavePackSize(baseSize, waveIndex, waveScript=None):
    """Escalate pack count each wave without exploding spawn count.

    When waveScript is set, the script owns pack size for that beat so
    Loopy / Punchline / Silly compositions stay intentional.
    """
    if waveScript:
        return max(1, len(waveScript))
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
                      snareWaveStart=None, gagsterFraction=None,
                      gagsterWaveStart=None, waveScript=None):
    """Choose Smudge (0), Brute (1), Snare (2), or Gagster (3) for one slot.

    Prefer an explicit waveScript slot when present. Otherwise keep wave-1 /
    zero-fraction packs as pure Ink Smudge so Loopy demos stay familiar.
    Slot layout: Snares front (zip-lash), Gagsters mid (gag-lob), Brutes
    rear (tank spit).
    """
    from toontown.corruption import CorruptionGlobals
    wave = max(1, int(waveIndex))
    count = max(0, int(packCount))
    if count <= 0:
        return CorruptionGlobals.ARCHETYPE_INK

    slot = int(slotIndex)
    if waveScript:
        if 0 <= slot < len(waveScript):
            return CorruptionGlobals.normalizeArchetype(waveScript[slot])
        # Slot past a short script: fall through to fraction fill.

    bruteStart = (
        BRUTE_WAVE_START if bruteWaveStart is None else int(bruteWaveStart))
    bruteFrac = (
        BRUTE_FRACTION if bruteFraction is None else float(bruteFraction))
    snareStart = (
        SNARE_WAVE_START if snareWaveStart is None else int(snareWaveStart))
    snareFrac = (
        SNARE_FRACTION if snareFraction is None else float(snareFraction))
    gagsterStart = (
        GAGSTER_WAVE_START if gagsterWaveStart is None
        else int(gagsterWaveStart))
    gagsterFrac = (
        GAGSTER_FRACTION if gagsterFraction is None else float(gagsterFraction))

    bruteSlots = 0
    if wave >= bruteStart and bruteFrac > 0.0:
        bruteSlots = max(1, int(round(count * bruteFrac)))
        bruteSlots = min(bruteSlots, count)
    snareSlots = 0
    if wave >= snareStart and snareFrac > 0.0:
        snareSlots = max(1, int(round(count * snareFrac)))
        snareSlots = min(snareSlots, count)
    gagsterSlots = 0
    if wave >= gagsterStart and gagsterFrac > 0.0:
        gagsterSlots = max(1, int(round(count * gagsterFrac)))
        gagsterSlots = min(gagsterSlots, count)
    # Leave at least one Smudge when the pack has room.
    if bruteSlots + snareSlots + gagsterSlots >= count and count > 1:
        overflow = bruteSlots + snareSlots + gagsterSlots - (count - 1)
        while overflow > 0 and snareSlots > 0:
            snareSlots -= 1
            overflow -= 1
        while overflow > 0 and gagsterSlots > 0:
            gagsterSlots -= 1
            overflow -= 1
        while overflow > 0 and bruteSlots > 0:
            bruteSlots -= 1
            overflow -= 1

    if bruteSlots and slot >= (count - bruteSlots):
        return CorruptionGlobals.ARCHETYPE_BRUTE
    if snareSlots and slot < snareSlots:
        return CorruptionGlobals.ARCHETYPE_SNARE
    # Mid band between snare front and brute rear for Gagster lobs.
    midStart = snareSlots
    midEnd = count - bruteSlots
    midRoom = max(0, midEnd - midStart)
    gagsterSlots = min(gagsterSlots, midRoom)
    if gagsterSlots and slot >= midStart and slot < midStart + gagsterSlots:
        return CorruptionGlobals.ARCHETYPE_GAGSTER
    return CorruptionGlobals.ARCHETYPE_INK


def packSlotName(archetype, smudgeName=None, bruteName=None, snareName=None,
                 gagsterName=None, slotIndex=0, packCount=1):
    """Display name for a pack slot (numbered when pack has multiples)."""
    from toontown.corruption import CorruptionGlobals
    arch = CorruptionGlobals.normalizeArchetype(archetype)
    if arch == CorruptionGlobals.ARCHETYPE_BRUTE:
        base = bruteName or BRUTE_NAME
    elif arch == CorruptionGlobals.ARCHETYPE_SNARE:
        base = snareName or SNARE_NAME
    elif arch == CorruptionGlobals.ARCHETYPE_GAGSTER:
        base = gagsterName or GAGSTER_NAME
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
