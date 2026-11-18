"""Act table for the Toon City multi-hood reclaim campaign.

Story (Tim): Oswald is the trusted toon leading the reclaim — players believe
he is the hero. Silly/finale victory copy reveals he caused the corruption.
Combat is rubber-hose Oswald stretch punches (combo, soft-lock, dodge,
readable telegraphs). Lore is a spiritual sequel to Toontown — no keyblades.
"""

from toontown.toonbase import ToontownGlobals

# Pure HQ — Oswald's story hub, lightly threatened but not a reclaim act.
HUB_ZONE = ToontownGlobals.ToontownCentral
HUB_NAME = 'Toontown Central'
PROTAGONIST = 'Oswald'
# Alias used by handoff / PlayEntry celebration UX.
RECLAIM_FACE = PROTAGONIST

# Per reclaim: multiplicative bump applied to HackSlashConfig.COMBO_DAMAGE.
POWER_BUMP_PER_RECLAIM = 0.08
POWER_BUMP_MAX = 0.40

# Escalating reclaim acts: explore → fight → reclaim → next hood.
# Finale: two-phase Ink Overlord under Oswald's lead, then twist.
ACTS = (
    {
        'id': 'loopy',
        'name': 'Loopy Lane',
        'zoneId': ToontownGlobals.LoopyLane,
        'seedPollution': 0.55,
        'packSize': 3,
        'maxPacks': 3,
        'corruptHp': 30,
        'corruptName': 'Ink Smudge',
        # Pure Smudge packs — Act 1 stays the familiar melee tutorial.
        'bruteFraction': 0.0,
        'snareFraction': 0.0,
        'banner': 'Act 1 — Oswald calls for help! Corruption stains Loopy Lane!',
        # Client celebration copy (title / Oswald tip / next-street cue).
        'handoffTitle': 'LOOPY LANE IS PURE!',
        'handoff': (
            'Oswald cheers: Loopy Lane is pure again! '
            'Next: Punchline Place.'),
        'nextCue': 'Oswald points the tunnel → Punchline Place',
        'nextStreet': 'Punchline Place',
    },
    {
        'id': 'punchline',
        'name': 'Punchline Place',
        'zoneId': ToontownGlobals.PunchlinePlace,
        'seedPollution': 0.70,
        'packSize': 4,
        'maxPacks': 4,
        'corruptHp': 40,
        'corruptName': 'Gunk Gagster',
        # Mix Brutes (tank spit) + Balloon Snares (zip/lash) with Smudges.
        'bruteFraction': 0.4,
        'bruteWaveStart': 1,
        'bruteName': 'Sludge Brute',
        'snareFraction': 0.25,
        'snareWaveStart': 1,
        'snareName': 'Balloon Snare',
        'banner': (
            'Act 2 — Oswald leads the reclaim — '
            'Punchline Place is drowning in sludge!'),
        # Act-entry tip (PlayEntry) — Oswald trusted lead + Brute/Snare cues.
        # Mid-campaign only; no twist spoilers. Hose-pop tunables below.
        'entryTip': (
            'Oswald leads Act 2 — Punchline Place sludge: explore → '
            'F fight Sludge Brutes & Balloon Snares → reclaim  |  '
            'Shift dodge  |  C campaign'),
        'handoffTitle': 'PUNCHLINE PLACE LAUGHS CLEAN!',
        'handoff': (
            'Oswald points ahead: Punchline laughs clean! '
            'Finale awaits on Silly Street.'),
        'nextCue': 'Oswald steers you on → Silly Street finale',
        'nextStreet': 'Silly Street',
    },
    {
        'id': 'finale',
        'name': 'Silly Street Finale',
        'zoneId': ToontownGlobals.SillyStreet,
        'seedPollution': 0.75,
        'packSize': 1,
        'maxPacks': 2,
        'corruptHp': 90,
        'corruptName': 'Ink Overlord',
        # Boss fight stays Overlord-only (no Brute / Snare mix).
        'bruteFraction': 0.0,
        'snareFraction': 0.0,
        'banner': (
            'Finale Phase 1 — Oswald stands with you against '
            'the Ink Overlord on Silly Street!'),
        # Act-entry tip (PlayEntry) — Oswald trusted lead + Ink Overlord cues.
        # Mid-campaign tip only; no twist spoilers. Hose-pop tunables below.
        'entryTip': (
            'Oswald leads Act 3 — Silly Street finale: explore → '
            'F fight the Ink Overlord → reclaim  |  '
            'Shift dodge  |  C campaign'),
        # Twist: trusted Oswald was the source of the neighborhood pollution.
        'handoffTitle': 'VICTORY…?',
        'handoff': (
            'Oswald smiles too wide. '
            'The ink corrupting Toon City was his all along.'),
        'nextCue': 'Oswald caused the corruption',
        'nextStreet': None,
        'finale': True,
        # Client-readable phase index (1-based) for reclaim director / telegraphs.
        'finalePhase': 1,
        # Phase 2 overrides after the first Silly Street reclaim clears.
        'phase2': {
            'seedPollution': 0.95,
            'packSize': 2,
            'maxPacks': 3,
            'corruptHp': 160,
            'corruptName': 'Ink Overlord Unleashed',
            'banner': (
                'Finale Phase 2 — Ink Overlord Unleashed! '
                'Oswald urges you to finish it!'),
            'finalePhase': 2,
            'transitionSting': True,
            'bruteFraction': 0.0,
            'snareFraction': 0.0,
        },
    },
)

# Client presentation for Silly Street Ink Overlord phases (1 / 2).
FINALE_PHASE_BANNER = {
    1: 'OSWALD vs THE OVERLORD',
    2: 'INK OVERLORD UNLEASHED',
}
# Keep P1/P2 telegraph distinctions from Overlord phase telegraphs (#31).
FINALE_PHASE_SUB = {
    1: 'Oswald stands with you — magenta swell, tall rubber wind-up + rise SFX!',
    2: (
        "Oswald's cheer rings hollow — crimson fury, "
        'wider squash, hotter slam + phase-2 sting!'),
}
# Compact HUD phase labels (status strip + telegraph cue).
FINALE_PHASE_HUD = {
    1: 'OVERLORD · P1 RISE',
    2: 'OVERLORD · P2 UNLEASHED',
}
# PlayEntry tip bar — Oswald / combat cue strip at street enter.
# Short rubber-hose scale pop when the tip appears (Toontown spiritual
# sequel — no keyblades / KH branding). Tunables live here so PlayEntry
# stays out of corruption/ while smudge telegraph juice lands elsewhere.
PLAY_ENTRY_TIP_SCALE = 0.042
PLAY_ENTRY_TIP_POS = (0.0, 0.0, -0.92)
# Flat squash → tall stretch → settle (multipliers of PLAY_ENTRY_TIP_SCALE).
PLAY_ENTRY_TIP_POP_SQUASH = (1.55, 1.0, 0.55, 0.05)   # sx, sy, sz, sec
PLAY_ENTRY_TIP_POP_STRETCH = (0.78, 1.0, 1.42, 0.08)
PLAY_ENTRY_TIP_POP_SETTLE_SEC = 0.10

# Punchline Place Act 2 entry tip — tip-matched hose pop, slightly punchier
# for the Brute/Snare sludge beat. Oswald stays the trusted mid-campaign
# lead (no twist spoilers). Soft trust settle matches act-banner #76.
# Toontown spiritual sequel — no keyblades / KH branding.
PUNCHLINE_ACT_TIP_POP_SQUASH = (1.62, 1.0, 0.50, 0.05)   # sx, sy, sz, sec
PUNCHLINE_ACT_TIP_POP_STRETCH = (0.74, 1.0, 1.48, 0.08)
PUNCHLINE_ACT_TIP_POP_SETTLE_SEC = 0.10
PUNCHLINE_ACT_TIP_TRUST_SETTLE_OVERSHOOT = (0.90, 1.0, 1.16, 0.07)
PUNCHLINE_ACT_TIP_TRUST_SETTLE_REST_SEC = 0.09

# Silly Street Act 3 entry tip — tip-matched hose pop, slightly heavier for
# the Ink Overlord finale beat. Oswald stays the trusted mid-campaign lead
# on this tip (no twist spoilers). Soft trust settle matches Punchline tip
# #91 / act-banner #76. Toontown spiritual sequel — no keyblades / KH branding.
SILLY_ACT_TIP_POP_SQUASH = (1.68, 1.0, 0.46, 0.05)   # sx, sy, sz, sec
SILLY_ACT_TIP_POP_STRETCH = (0.70, 1.0, 1.52, 0.08)
SILLY_ACT_TIP_POP_SETTLE_SEC = 0.10
SILLY_ACT_TIP_TRUST_SETTLE_OVERSHOOT = (0.88, 1.0, 1.18, 0.07)
SILLY_ACT_TIP_TRUST_SETTLE_REST_SEC = 0.09

# PlayEntry act-enter flash banner (ACTS['banner'] / reclaim cues).
# Same squash→stretch→settle hose pop as the tip bar — readable act beat
# without touching reclaim/ wave banners. No keyblades / KH branding.
PLAY_ENTRY_BANNER_SCALE = 0.06
PLAY_ENTRY_BANNER_POS = (0.0, 0.0, 0.72)
PLAY_ENTRY_BANNER_HOLD_SEC = 2.4
PLAY_ENTRY_BANNER_FADE_IN_SEC = 0.15
PLAY_ENTRY_BANNER_FADE_OUT_SEC = 0.35
PLAY_ENTRY_BANNER_POP_SQUASH = (1.48, 1.0, 0.58, 0.05)   # sx, sy, sz, sec
PLAY_ENTRY_BANNER_POP_STRETCH = (0.80, 1.0, 1.38, 0.09)
PLAY_ENTRY_BANNER_POP_SETTLE_SEC = 0.11

# CampaignHandoff celebration title — rubber-hose scale pop on act clears.
# Matches PlayEntry tip/banner hose pattern; cue keeps a lighter settle.
# Oswald twist / victory copy unchanged — juice only. No KH branding.
HANDOFF_TITLE_SCALE = 0.078
HANDOFF_TITLE_POP_SQUASH = (1.42, 1.0, 0.62, 0.06)   # sx, sy, sz, sec
HANDOFF_TITLE_POP_STRETCH = (0.82, 1.0, 1.36, 0.10)
HANDOFF_TITLE_POP_SETTLE_SEC = 0.12

# Early/mid Oswald trusted reclaim-lead banners (Act 1/2 enter + handoff).
# Extra rubber-hose settle bounce after tip/act squash→stretch→settle, plus
# hose-pop on the Oswald cheer/lead subtitle. FinalePhaseFx twist reveal
# stays separate — do not weaken the end-game sting. No KH branding.
OSWALD_TRUST_BANNER_SETTLE_OVERSHOOT = (0.90, 1.0, 1.14, 0.07)  # sx, sy, sz, sec
OSWALD_TRUST_BANNER_SETTLE_REST_SEC = 0.09
# Handoff Oswald trust subtitle (cheers / points the tunnel) — tip-matched.
OSWALD_TRUST_SUB_SCALE = 0.048
OSWALD_TRUST_SUB_POP_SQUASH = (1.50, 1.0, 0.56, 0.05)   # sx, sy, sz, sec
OSWALD_TRUST_SUB_POP_STRETCH = (0.80, 1.0, 1.40, 0.08)
OSWALD_TRUST_SUB_POP_SETTLE_SEC = 0.10

# Campaign handoff confetti / streamer pop (CampaignHandoffConfetti).
# Short rubber-hose carnival burst on Loopy→Punchline (and act) handoffs.
# Toontown spiritual sequel — no keyblades / KH branding.
HANDOFF_CONFETTI_COUNT = 10
HANDOFF_STREAMER_COUNT = 5
HANDOFF_CONFETTI_SIZE = 0.028
HANDOFF_STREAMER_FRAME = (-0.012, 0.012, -0.09, 0.09)
HANDOFF_CONFETTI_DRIFT = 0.55
HANDOFF_STREAMER_DRIFT = 0.72
HANDOFF_CONFETTI_SEC = 0.72
HANDOFF_STREAMER_SEC = 0.85
HANDOFF_CONFETTI_ORIGIN = (0.0, 0.0, 0.38)
# Carnival reclaim palette — mint / cream / gold / coral / sky.
HANDOFF_CONFETTI_COLORS = (
    (0.55, 1.0, 0.78, 0.95),
    (1.0, 0.95, 0.55, 0.95),
    (1.0, 0.55, 0.45, 0.95),
    (0.55, 0.85, 1.0, 0.95),
    (1.0, 0.78, 0.95, 0.95),
    (0.95, 1.0, 0.88, 0.95),
)
HANDOFF_STREAMER_COLORS = (
    (1.0, 0.92, 0.42, 0.95),
    (0.45, 0.95, 0.72, 0.95),
    (1.0, 0.62, 0.48, 0.95),
    (0.65, 0.82, 1.0, 0.95),
)

# Campaign victory cream confetti swell (CampaignHandoffConfetti).
# Soft rubber-hose cream burst on the purity cheer ("TOON CITY IS SAVED!")
# only — clears before the Oswald twist / FinalePhaseFx reveal so the
# bittersweet sting stays intact. Separate from carnival HANDOFF_CONFETTI_*
# (act clears) and from the reveal shadow flash. No keyblades / KH branding.
VICTORY_CREAM_SWELL_ENABLED = True
VICTORY_CREAM_SWELL_ORIGIN = (0.0, 0.0, 0.36)
VICTORY_CREAM_SWELL_BIN = 61
# Soft cream wash flash under the victory plate (not a white slam).
VICTORY_CREAM_FLASH_COLOR = (1.0, 0.97, 0.84, 1.0)
VICTORY_CREAM_FLASH_PEAK = 0.28
VICTORY_CREAM_FLASH_IN_SEC = 0.06
VICTORY_CREAM_FLASH_HOLD_SEC = 0.08
VICTORY_CREAM_FLASH_OUT_SEC = 0.42
# Expanding cream ring — the "swell" read.
VICTORY_CREAM_RING_PEAK = 2.15
VICTORY_CREAM_RING_SEC = 0.55
VICTORY_CREAM_RING_PEAK_ALPHA = 0.42
VICTORY_CREAM_RING_COLOR = (1.0, 0.96, 0.78, 1.0)
# Cream confetti chips — warmer / softer than carnival handoff palette.
VICTORY_CREAM_CONFETTI_COUNT = 14
VICTORY_CREAM_CONFETTI_SIZE = 0.030
VICTORY_CREAM_CONFETTI_DRIFT = 0.78
VICTORY_CREAM_CONFETTI_SEC = 1.05
VICTORY_CREAM_CONFETTI_COLORS = (
    (1.0, 0.97, 0.82, 0.95),
    (1.0, 0.94, 0.68, 0.95),
    (0.98, 0.92, 0.55, 0.92),
    (1.0, 0.98, 0.90, 0.90),
    (0.95, 0.88, 0.62, 0.92),
    (1.0, 0.90, 0.72, 0.90),
)
# Soft cream streamers — fewer, slower than act-handoff carnival ribbons.
VICTORY_CREAM_STREAMER_COUNT = 4
VICTORY_CREAM_STREAMER_FRAME = (-0.011, 0.011, -0.10, 0.10)
VICTORY_CREAM_STREAMER_DRIFT = 0.88
VICTORY_CREAM_STREAMER_SEC = 1.15
VICTORY_CREAM_STREAMER_COLORS = (
    (1.0, 0.95, 0.62, 0.92),
    (1.0, 0.98, 0.82, 0.90),
    (0.98, 0.90, 0.55, 0.90),
    (1.0, 0.92, 0.72, 0.88),
)

# Explicit Oswald twist after P2 clear (shown after purity victory flash).
FINALE_TWIST_TEASE = 'Victory…? Oswald caused the corruption.'
FINALE_TWIST_TEASE_COLOR = (1.0, 0.55, 0.35, 1.0)
# Readable AV reveal sting (FinalePhaseFx) after Silly finale victory / purity.
# Toontown-sequel voice — no keyblades / KH branding.
FINALE_REVEAL_BANNER = 'OSWALD CAUSED THE CORRUPTION'
FINALE_REVEAL_SUB = (
    'That trusted smile… the ink staining Toon City was his all along.')
FINALE_REVEAL_BANNER_COLOR = (1.0, 0.42, 0.28, 1.0)
FINALE_REVEAL_SUB_COLOR = (1.0, 0.72, 0.48, 1.0)
# Hold purity cheer first, then land the twist sting as its own beat.
FINALE_REVEAL_DELAY_SEC = 2.45
FINALE_REVEAL_HOLD_SEC = 3.6

# Oswald shadow flash — rubber-hose silhouette on the reveal sting.
# Trusted lead shape → ink shadow that sells the twist. Campaign-owned
# tunables (keep out of corruption/ while ink-drip ships). No KH branding.
FINALE_REVEAL_SHADOW_COLOR = (0.04, 0.02, 0.06, 1.0)
FINALE_REVEAL_SHADOW_PEAK_ALPHA = 0.92
# Sit under title/sub banners so the twist copy stays readable.
FINALE_REVEAL_SHADOW_POS = (0.0, 0.0, -0.28)
FINALE_REVEAL_SHADOW_SCALE = 0.45
# Squash → tall stretch → settle (reads as rubber-hose rabbit ears).
FINALE_REVEAL_SHADOW_SQUASH = (1.35, 1.0, 0.55)
FINALE_REVEAL_SHADOW_STRETCH = (0.72, 1.0, 1.55)
FINALE_REVEAL_SHADOW_SQUASH_SEC = 0.07
FINALE_REVEAL_SHADOW_STRETCH_SEC = 0.12
FINALE_REVEAL_SHADOW_SETTLE_SEC = 0.18
FINALE_REVEAL_SHADOW_FADE_IN_SEC = 0.06
FINALE_REVEAL_SHADOW_HOLD_SEC = 0.28
FINALE_REVEAL_SHADOW_FADE_OUT_SEC = 0.55
FINALE_REVEAL_SHADOW_BIN = 101

# Cream aftershock after Oswald reveal sting (FinaleCreamAftershockFx).
# Soft residual cream flash/ring/flecks that land *after* the ink flash /
# silhouette sting — supports the twist beat without undoing it or
# replaying #82 victory cream swell (cleared before reveal). Quieter,
# downward-settling, below victory swell bins. No keyblades / KH branding.
FINALE_REVEAL_CREAM_AFTERSHOCK_ENABLED = True
# Delay from sting Parallel start so ink/shadow land first.
FINALE_REVEAL_CREAM_AFTERSHOCK_DELAY_SEC = 0.72
FINALE_REVEAL_CREAM_AFTERSHOCK_ORIGIN = (0.0, 0.0, 0.08)
# Below victory swell (61) and banners; above wash/meter noise.
FINALE_REVEAL_CREAM_AFTERSHOCK_BIN = 58
FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_COLOR = (1.0, 0.96, 0.82, 1.0)
FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_PEAK = 0.18
FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_IN_SEC = 0.08
FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_HOLD_SEC = 0.06
FINALE_REVEAL_CREAM_AFTERSHOCK_FLASH_OUT_SEC = 0.55
FINALE_REVEAL_CREAM_AFTERSHOCK_RING_COLOR = (1.0, 0.94, 0.74, 1.0)
FINALE_REVEAL_CREAM_AFTERSHOCK_RING_START = 0.28
FINALE_REVEAL_CREAM_AFTERSHOCK_RING_PEAK = 1.85
FINALE_REVEAL_CREAM_AFTERSHOCK_RING_SEC = 0.62
FINALE_REVEAL_CREAM_AFTERSHOCK_RING_PEAK_ALPHA = 0.28
FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_COUNT = 8
FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_SIZE = 0.022
FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_DRIFT = 0.42
FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_SEC = 0.85
FINALE_REVEAL_CREAM_AFTERSHOCK_FLECK_COLORS = (
    (1.0, 0.97, 0.84, 0.88),
    (1.0, 0.93, 0.70, 0.85),
    (0.98, 0.90, 0.58, 0.82),
    (1.0, 0.98, 0.90, 0.80),
    (0.96, 0.88, 0.64, 0.84),
)

STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_VICTORY = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_VICTORY: 'victory',
}
