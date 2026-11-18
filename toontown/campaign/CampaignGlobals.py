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

# Soft cream wash pulse after Punchline Act 2 tip hose pop (#91).
# Act-banner / trust wash grammar (#154/#145) — delayed two-beat aspect2d
# veil on PlayEntry tipHose='punchline' path only. Soft under the tip bar;
# cream / pastel only. A touch quieter / shorter than handoff wash (#141)
# — tip lands without glitter hang (trust / act-banner wash twin). Loopy /
# default tip hose stay wash-free; Silly tip wash lives in its own module.
# Act-enter / trust / handoff / victory / finale washes live in their own
# modules. PUNCHLINE_ACT_TIP_CREAM_WASH_ENABLED = False drops wash only
# (hose pop + trust settle remain). No keyblades / KH branding.
PUNCHLINE_ACT_TIP_CREAM_WASH_ENABLED = True
PUNCHLINE_ACT_TIP_CREAM_WASH_DELAY_SEC = 0.36  # after play; after hose settle
PUNCHLINE_ACT_TIP_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
PUNCHLINE_ACT_TIP_CREAM_WASH_PEAK = 0.12
PUNCHLINE_ACT_TIP_CREAM_WASH_MID = 0.07
PUNCHLINE_ACT_TIP_CREAM_WASH_IN_SEC = 0.07
PUNCHLINE_ACT_TIP_CREAM_WASH_PULSE_SEC = 0.12
PUNCHLINE_ACT_TIP_CREAM_WASH_HOLD_SEC = 0.10
PUNCHLINE_ACT_TIP_CREAM_WASH_OUT_SEC = 0.36  # soft settle, no glitter hang
# Above ink entry vignette (48); soft veil settle under tip bar.
PUNCHLINE_ACT_TIP_CREAM_WASH_BIN = 49

# Silly Street Act 3 entry tip — tip-matched hose pop, slightly heavier for
# the Ink Overlord finale beat. Oswald stays the trusted mid-campaign lead
# on this tip (no twist spoilers). Soft trust settle matches Punchline tip
# #91 / act-banner #76. Toontown spiritual sequel — no keyblades / KH branding.
SILLY_ACT_TIP_POP_SQUASH = (1.68, 1.0, 0.46, 0.05)   # sx, sy, sz, sec
SILLY_ACT_TIP_POP_STRETCH = (0.70, 1.0, 1.52, 0.08)
SILLY_ACT_TIP_POP_SETTLE_SEC = 0.10
SILLY_ACT_TIP_TRUST_SETTLE_OVERSHOOT = (0.88, 1.0, 1.18, 0.07)
SILLY_ACT_TIP_TRUST_SETTLE_REST_SEC = 0.09

# Soft cream wash pulse after Silly Act 3 tip hose pop (#95).
# Act-banner / Punchline tip wash grammar (#154/#158) — delayed two-beat
# aspect2d veil on PlayEntry tipHose='silly' path only. Soft under the tip
# bar; cream / pastel only. A touch quieter / shorter than handoff wash
# (#141) — tip lands without glitter hang (trust / act-banner / Punchline
# tip wash twin). Loopy / Punchline / default tip hose stay wash-free.
# Act-enter / trust / handoff / victory / finale washes live in their own
# modules. SILLY_ACT_TIP_CREAM_WASH_ENABLED = False drops wash only (hose
# pop + trust settle remain). No keyblades / KH branding.
SILLY_ACT_TIP_CREAM_WASH_ENABLED = True
SILLY_ACT_TIP_CREAM_WASH_DELAY_SEC = 0.36  # after play; after hose settle
SILLY_ACT_TIP_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SILLY_ACT_TIP_CREAM_WASH_PEAK = 0.12
SILLY_ACT_TIP_CREAM_WASH_MID = 0.07
SILLY_ACT_TIP_CREAM_WASH_IN_SEC = 0.07
SILLY_ACT_TIP_CREAM_WASH_PULSE_SEC = 0.12
SILLY_ACT_TIP_CREAM_WASH_HOLD_SEC = 0.10
SILLY_ACT_TIP_CREAM_WASH_OUT_SEC = 0.36  # soft settle, no glitter hang
# Above ink entry vignette (48); soft veil settle under tip bar.
SILLY_ACT_TIP_CREAM_WASH_BIN = 49

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

# Cream edge pulse framing PlayEntry act-enter banners (aspect2d border strips).
# Soft rubber-hose cream frame that pops with the act banner hose (#70) —
# mirrors reclaim wave-announce cream edge (#87). Sunny cream / pastel only;
# opposite of polluted ink edge vignette. No keyblades / KH branding.
PLAY_ENTRY_BANNER_CREAM_EDGE_ENABLED = True
PLAY_ENTRY_BANNER_CREAM_EDGE_COLOR = (1.0, 0.97, 0.82, 1.0)
PLAY_ENTRY_BANNER_CREAM_EDGE = 0.28  # strip thickness in aspect2d units
PLAY_ENTRY_BANNER_CREAM_EDGE_PEAK = 0.42
PLAY_ENTRY_BANNER_CREAM_EDGE_PULSE = 0.28  # mid-beat alpha after peak
PLAY_ENTRY_BANNER_CREAM_EDGE_IN_SEC = 0.08
PLAY_ENTRY_BANNER_CREAM_EDGE_HOLD_SEC = 0.10
PLAY_ENTRY_BANNER_CREAM_EDGE_PULSE_SEC = 0.12
PLAY_ENTRY_BANNER_CREAM_EDGE_OUT_SEC = 0.36
# Above ink entry vignette (48); below handoff / celebration plates (60+).
PLAY_ENTRY_BANNER_CREAM_EDGE_BIN = 50
PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_COUNT = 6
PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_SIZE = 0.022
PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_DRIFT = 0.18
PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_SEC = 0.28
PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_COLOR = (1.0, 0.96, 0.62, 0.9)
PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_END_COLOR = (1.0, 0.92, 0.45, 0.0)
# Flecks cluster near the act banner (PLAY_ENTRY_BANNER_POS ~z 0.72).
PLAY_ENTRY_BANNER_CREAM_EDGE_FLECK_ORIGIN = (0.0, 0.0, 0.72)

# Soft cream wash pulse after act-enter banner cream edge (#110).
# Trust / handoff / victory / finale-reveal wash grammar (#145/#141/#138/#149)
# — delayed two-beat aspect2d veil on PlayEntry ACTS creamEdge path only.
# Soft under edge strips (bin 50); cream / pastel only. A touch quieter /
# shorter than handoff wash (#141) — act-enter banners fire without glitter
# hang (trust wash twin). Reclaim cue flashes stay wash-free. Other campaign
# washes live in their own modules.
# PLAY_ENTRY_BANNER_CREAM_WASH_ENABLED = False drops wash only (hose pop +
# cream edge remain). No keyblades / KH branding.
PLAY_ENTRY_BANNER_CREAM_WASH_ENABLED = True
PLAY_ENTRY_BANNER_CREAM_WASH_DELAY_SEC = 0.36  # after play; after edge peak
PLAY_ENTRY_BANNER_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
PLAY_ENTRY_BANNER_CREAM_WASH_PEAK = 0.12
PLAY_ENTRY_BANNER_CREAM_WASH_MID = 0.07
PLAY_ENTRY_BANNER_CREAM_WASH_IN_SEC = 0.07
PLAY_ENTRY_BANNER_CREAM_WASH_PULSE_SEC = 0.12
PLAY_ENTRY_BANNER_CREAM_WASH_HOLD_SEC = 0.10
PLAY_ENTRY_BANNER_CREAM_WASH_OUT_SEC = 0.36  # soft settle, no glitter hang
# Under cream edge (50); above ink entry vignette (48); soft veil settle.
PLAY_ENTRY_BANNER_CREAM_WASH_BIN = 49

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

# Cream edge pulse framing early/mid Oswald trust handoff banners.
# Composes with trust hose settle (#76) — mirrors act-enter cream edge (#110)
# / wave-announce cream edge (#87). Sunny cream / pastel only; trusted-hero
# mid-campaign beat (no twist spoilers). No keyblades / KH branding.
OSWALD_TRUST_BANNER_CREAM_EDGE_ENABLED = True
OSWALD_TRUST_BANNER_CREAM_EDGE_COLOR = (1.0, 0.97, 0.82, 1.0)
OSWALD_TRUST_BANNER_CREAM_EDGE = 0.28  # strip thickness in aspect2d units
OSWALD_TRUST_BANNER_CREAM_EDGE_PEAK = 0.42
OSWALD_TRUST_BANNER_CREAM_EDGE_PULSE = 0.28  # mid-beat alpha after peak
OSWALD_TRUST_BANNER_CREAM_EDGE_IN_SEC = 0.08
OSWALD_TRUST_BANNER_CREAM_EDGE_HOLD_SEC = 0.10
OSWALD_TRUST_BANNER_CREAM_EDGE_PULSE_SEC = 0.12
OSWALD_TRUST_BANNER_CREAM_EDGE_OUT_SEC = 0.36
# Below handoff plate/title bins (60/62); above ink entry vignette (48).
OSWALD_TRUST_BANNER_CREAM_EDGE_BIN = 55
OSWALD_TRUST_BANNER_CREAM_EDGE_FLECK_COUNT = 6
OSWALD_TRUST_BANNER_CREAM_EDGE_FLECK_SIZE = 0.022
OSWALD_TRUST_BANNER_CREAM_EDGE_FLECK_DRIFT = 0.18
OSWALD_TRUST_BANNER_CREAM_EDGE_FLECK_SEC = 0.28
OSWALD_TRUST_BANNER_CREAM_EDGE_FLECK_COLOR = (1.0, 0.96, 0.62, 0.9)
OSWALD_TRUST_BANNER_CREAM_EDGE_FLECK_END_COLOR = (1.0, 0.92, 0.45, 0.0)
# Flecks cluster near the handoff plate (root ~z 0.42).
OSWALD_TRUST_BANNER_CREAM_EDGE_FLECK_ORIGIN = (0.0, 0.0, 0.42)

# Soft cream wash pulse after Oswald trust banner cream edge (#117).
# Handoff / victory cream wash grammar (#141/#138) — delayed two-beat
# aspect2d veil on early/mid trusted Oswald settle only (no carnival).
# Soft under edge strips (bin 55) / plate (60); cream / pastel only. A
# touch quieter / shorter than handoff wash (#141) — trust settles fire
# without glitter hang. Twist / victory / phase / carnival stay on their
# own wash modules (no twist spoilers here).
# OSWALD_TRUST_BANNER_CREAM_WASH_ENABLED = False drops wash only (hose
# settle + cream edge remain). No keyblades / KH branding.
OSWALD_TRUST_BANNER_CREAM_WASH_ENABLED = True
OSWALD_TRUST_BANNER_CREAM_WASH_DELAY_SEC = 0.36  # after play; after edge peak
OSWALD_TRUST_BANNER_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
OSWALD_TRUST_BANNER_CREAM_WASH_PEAK = 0.12
OSWALD_TRUST_BANNER_CREAM_WASH_MID = 0.07
OSWALD_TRUST_BANNER_CREAM_WASH_IN_SEC = 0.07
OSWALD_TRUST_BANNER_CREAM_WASH_PULSE_SEC = 0.12
OSWALD_TRUST_BANNER_CREAM_WASH_HOLD_SEC = 0.10
OSWALD_TRUST_BANNER_CREAM_WASH_OUT_SEC = 0.36  # soft settle, no glitter hang
# Under cream edge (55) / plate (60); soft veil settle beat.
OSWALD_TRUST_BANNER_CREAM_WASH_BIN = 54

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

# Cream sparkle flecks layered on hood handoff confetti (#57).
# Soft cream/pastel glitter on Loopy→Punchline (and act) carnival pops —
# warm sparkle, not a second victory cream swell (#82). Oswald stays the
# trusted mid-campaign reclaim lead. No keyblades / KH branding.
HANDOFF_CREAM_SPARKLE_ENABLED = True
HANDOFF_CREAM_SPARKLE_COUNT = 8
HANDOFF_CREAM_SPARKLE_STREAK_COUNT = 4
HANDOFF_CREAM_SPARKLE_SIZE = 0.016
HANDOFF_CREAM_SPARKLE_STREAK_SIZE = 0.012
HANDOFF_CREAM_SPARKLE_DRIFT = 0.48
HANDOFF_CREAM_SPARKLE_SEC = 0.68
# Above carnival chips (64) / streamers (63) so cream glitter reads on top.
HANDOFF_CREAM_SPARKLE_BIN = 66
# Cream / soft pastel only — warmer than carnival mint/coral/sky.
HANDOFF_CREAM_SPARKLE_COLORS = (
    (1.0, 0.97, 0.84, 0.95),
    (1.0, 0.94, 0.70, 0.92),
    (0.98, 0.92, 0.58, 0.90),
    (1.0, 0.98, 0.90, 0.90),
    (0.96, 0.88, 0.64, 0.88),
    (1.0, 0.90, 0.74, 0.90),
)

# Cream edge pulse framing hood handoff cream-sparkle carnival banners (#99).
# Composes act/trust cream edge (#110/#117) with handoff cream sparkle —
# sunny frame around the Loopy→Punchline (and act) carnival pop. Tuned a
# touch longer than trust settle edge so the frame rides with cream glitter
# (~0.68s). Early/mid trusted Oswald only — twist / phase paths stay
# edge-free (victory cream edge is a separate VICTORY_CREAM_EDGE_* path).
# No keyblades / KH branding.
HANDOFF_CREAM_EDGE_ENABLED = True
HANDOFF_CREAM_EDGE_COLOR = (1.0, 0.97, 0.82, 1.0)
HANDOFF_CREAM_EDGE = 0.28  # strip thickness in aspect2d units
HANDOFF_CREAM_EDGE_PEAK = 0.40
HANDOFF_CREAM_EDGE_PULSE = 0.26  # mid-beat alpha after peak
HANDOFF_CREAM_EDGE_IN_SEC = 0.08
HANDOFF_CREAM_EDGE_HOLD_SEC = 0.12
HANDOFF_CREAM_EDGE_PULSE_SEC = 0.14
HANDOFF_CREAM_EDGE_OUT_SEC = 0.48  # covers cream sparkle hang
# Below handoff plate/title (60/62); above ink vignette (48); under sparkle (66).
HANDOFF_CREAM_EDGE_BIN = 55
HANDOFF_CREAM_EDGE_FLECK_COUNT = 7
HANDOFF_CREAM_EDGE_FLECK_SIZE = 0.022
HANDOFF_CREAM_EDGE_FLECK_DRIFT = 0.20
HANDOFF_CREAM_EDGE_FLECK_SEC = 0.32
HANDOFF_CREAM_EDGE_FLECK_COLOR = (1.0, 0.96, 0.62, 0.9)
HANDOFF_CREAM_EDGE_FLECK_END_COLOR = (1.0, 0.92, 0.45, 0.0)
# Tip flecks near the handoff plate / carnival origin (~z 0.40).
HANDOFF_CREAM_EDGE_FLECK_ORIGIN = (0.0, 0.0, 0.40)
# Rising cream-sparkle flecks along the cream edge (wave-edge #113 twin).
# Uses handoff cream-sparkle warmth (#99); disable drops sparkles only.
HANDOFF_CREAM_EDGE_SPARKLE_ENABLED = True
HANDOFF_CREAM_EDGE_SPARKLE_COUNT = 8
HANDOFF_CREAM_EDGE_SPARKLE_SIZE = 0.016
HANDOFF_CREAM_EDGE_SPARKLE_RISE = 0.28
HANDOFF_CREAM_EDGE_SPARKLE_SPREAD = 1.05
HANDOFF_CREAM_EDGE_SPARKLE_SEC = 0.40
HANDOFF_CREAM_EDGE_SPARKLE_COLOR = (1.0, 0.97, 0.78, 0.90)
HANDOFF_CREAM_EDGE_SPARKLE_END_COLOR = (1.0, 0.94, 0.58, 0.0)
HANDOFF_CREAM_EDGE_SPARKLE_ORIGIN = (0.0, 0.0, 0.38)

# Soft cream wash pulse after handoff cream edge / sparkle (#124/#99).
# Perfect-dodge / melee hit / victory / Oswald-trust cream wash grammar —
# delayed two-beat aspect2d veil on Loopy→Punchline (and act) carnival
# handoffs only. Soft under edge strips (bin 55) / plate (60); cream /
# pastel only. A touch quieter / shorter than victory wash (#138) —
# handoffs fire more often. Oswald trust / finale-reveal wash live
# separately; phase stays wash-free here. HANDOFF_CREAM_WASH_ENABLED =
# False drops wash only (carnival + sparkle + edge remain). No keyblades /
# KH branding.
HANDOFF_CREAM_WASH_ENABLED = True
HANDOFF_CREAM_WASH_DELAY_SEC = 0.40  # after play; after edge peak (~0.20)
HANDOFF_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
HANDOFF_CREAM_WASH_PEAK = 0.14
HANDOFF_CREAM_WASH_MID = 0.08
HANDOFF_CREAM_WASH_IN_SEC = 0.07
HANDOFF_CREAM_WASH_PULSE_SEC = 0.12
HANDOFF_CREAM_WASH_HOLD_SEC = 0.10
HANDOFF_CREAM_WASH_OUT_SEC = 0.40  # rides with handoff glitter hang (~0.68)
# Under cream edge (55) / plate (60); soft veil settle beat.
HANDOFF_CREAM_WASH_BIN = 54

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

# Cream sparkle flecks layered on victory cream confetti swell (#82).
# Soft cream/pastel glitter above cream chips/streamers on the purity cheer
# only — same family as hood handoff cream sparkle (#99), scaled for the
# wider victory swell. Clears with the swell before Oswald twist /
# FinalePhaseFx reveal. No keyblades / KH branding.
VICTORY_CREAM_SPARKLE_ENABLED = True
VICTORY_CREAM_SPARKLE_COUNT = 10
VICTORY_CREAM_SPARKLE_STREAK_COUNT = 5
VICTORY_CREAM_SPARKLE_SIZE = 0.018
VICTORY_CREAM_SPARKLE_STREAK_SIZE = 0.013
VICTORY_CREAM_SPARKLE_DRIFT = 0.58
VICTORY_CREAM_SPARKLE_SEC = 0.88
# Above swell chips (bin+2) / streamers (bin+1) so glitter reads on top.
VICTORY_CREAM_SPARKLE_BIN = 65
# Cream / soft pastel only — matches victory swell warmth.
VICTORY_CREAM_SPARKLE_COLORS = (
    (1.0, 0.97, 0.84, 0.95),
    (1.0, 0.94, 0.70, 0.92),
    (0.98, 0.92, 0.58, 0.90),
    (1.0, 0.98, 0.90, 0.90),
    (0.96, 0.88, 0.64, 0.88),
    (1.0, 0.90, 0.74, 0.90),
)

# Cream edge pulse framing victory cream confetti / sparkle banners (#82/#105).
# Composes handoff cream edge (#124) with victory cream swell + sparkle —
# sunny frame around the purity cheer ("TOON CITY IS SAVED!") only. Tuned
# longer than handoff carnival edge so the frame rides with victory glitter
# (~0.88s) and cream chips (~1.05s). Clears before Oswald twist /
# FinalePhaseFx reveal. No keyblades / KH branding.
VICTORY_CREAM_EDGE_ENABLED = True
VICTORY_CREAM_EDGE_COLOR = (1.0, 0.97, 0.82, 1.0)
VICTORY_CREAM_EDGE = 0.28  # strip thickness in aspect2d units
VICTORY_CREAM_EDGE_PEAK = 0.40
VICTORY_CREAM_EDGE_PULSE = 0.26  # mid-beat alpha after peak
VICTORY_CREAM_EDGE_IN_SEC = 0.08
VICTORY_CREAM_EDGE_HOLD_SEC = 0.12
VICTORY_CREAM_EDGE_PULSE_SEC = 0.14
VICTORY_CREAM_EDGE_OUT_SEC = 0.60  # covers victory cream sparkle hang
# Below victory plate/title (60/62); under sparkle (65); above ink vignette (48).
VICTORY_CREAM_EDGE_BIN = 58
VICTORY_CREAM_EDGE_FLECK_COUNT = 8
VICTORY_CREAM_EDGE_FLECK_SIZE = 0.024
VICTORY_CREAM_EDGE_FLECK_DRIFT = 0.22
VICTORY_CREAM_EDGE_FLECK_SEC = 0.36
VICTORY_CREAM_EDGE_FLECK_COLOR = (1.0, 0.96, 0.62, 0.9)
VICTORY_CREAM_EDGE_FLECK_END_COLOR = (1.0, 0.92, 0.45, 0.0)
# Tip flecks near the victory swell origin (~z 0.36).
VICTORY_CREAM_EDGE_FLECK_ORIGIN = (0.0, 0.0, 0.36)
# Rising cream-sparkle flecks along the cream edge (handoff #124 twin).
# Uses victory cream-sparkle warmth (#105); disable drops sparkles only.
VICTORY_CREAM_EDGE_SPARKLE_ENABLED = True
VICTORY_CREAM_EDGE_SPARKLE_COUNT = 10
VICTORY_CREAM_EDGE_SPARKLE_SIZE = 0.018
VICTORY_CREAM_EDGE_SPARKLE_RISE = 0.32
VICTORY_CREAM_EDGE_SPARKLE_SPREAD = 1.15
VICTORY_CREAM_EDGE_SPARKLE_SEC = 0.48
VICTORY_CREAM_EDGE_SPARKLE_COLOR = (1.0, 0.97, 0.78, 0.90)
VICTORY_CREAM_EDGE_SPARKLE_END_COLOR = (1.0, 0.94, 0.58, 0.0)
VICTORY_CREAM_EDGE_SPARKLE_ORIGIN = (0.0, 0.0, 0.36)

# Soft cream wash pulse after victory cream edge / sparkle (#129/#105).
# Perfect-dodge / melee hit / handoff / Oswald-trust cream wash grammar —
# delayed two-beat aspect2d veil on the purity cheer ("TOON CITY IS
# SAVED!") only. Soft under edge strips (bin 58) / plate (60); cream /
# pastel only. Clears before Oswald twist / FinalePhaseFx reveal (which
# arms its own finale-reveal wash). VICTORY_CREAM_WASH_ENABLED = False
# drops wash only (swell + sparkle + edge remain). No keyblades / KH
# branding.
VICTORY_CREAM_WASH_ENABLED = True
VICTORY_CREAM_WASH_DELAY_SEC = 0.48  # after play; after edge peak (~0.20)
VICTORY_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
VICTORY_CREAM_WASH_PEAK = 0.16
VICTORY_CREAM_WASH_MID = 0.09
VICTORY_CREAM_WASH_IN_SEC = 0.07
VICTORY_CREAM_WASH_PULSE_SEC = 0.12
VICTORY_CREAM_WASH_HOLD_SEC = 0.10
VICTORY_CREAM_WASH_OUT_SEC = 0.48  # rides with victory glitter hang
# Under cream edge (58) / plate (60); soft veil settle beat.
VICTORY_CREAM_WASH_BIN = 54

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

# Cream edge pulse framing finale reveal cream aftershock banners (#86).
# Composes victory cream edge (#129) with residual cream aftershock —
# soft sunny frame around the Oswald-twist sting only (not mid-campaign).
# Quieter / shorter than victory cheer edge so the truth sting stays
# bittersweet; rides with aftershock fleck hang (~0.85s). No keyblades /
# KH branding.
FINALE_REVEAL_CREAM_EDGE_ENABLED = True
FINALE_REVEAL_CREAM_EDGE_COLOR = (1.0, 0.97, 0.84, 1.0)
FINALE_REVEAL_CREAM_EDGE = 0.26  # strip thickness in aspect2d units
FINALE_REVEAL_CREAM_EDGE_PEAK = 0.32
FINALE_REVEAL_CREAM_EDGE_PULSE = 0.20  # mid-beat alpha after peak
FINALE_REVEAL_CREAM_EDGE_IN_SEC = 0.08
FINALE_REVEAL_CREAM_EDGE_HOLD_SEC = 0.10
FINALE_REVEAL_CREAM_EDGE_PULSE_SEC = 0.12
FINALE_REVEAL_CREAM_EDGE_OUT_SEC = 0.55  # covers aftershock fleck hang
# Under aftershock flash/ring (58+); above ink vignette (48); below reveal
# banners/shadow (101+).
FINALE_REVEAL_CREAM_EDGE_BIN = 56
FINALE_REVEAL_CREAM_EDGE_FLECK_COUNT = 6
FINALE_REVEAL_CREAM_EDGE_FLECK_SIZE = 0.020
FINALE_REVEAL_CREAM_EDGE_FLECK_DRIFT = 0.18
FINALE_REVEAL_CREAM_EDGE_FLECK_SEC = 0.30
FINALE_REVEAL_CREAM_EDGE_FLECK_COLOR = (1.0, 0.96, 0.68, 0.85)
FINALE_REVEAL_CREAM_EDGE_FLECK_END_COLOR = (1.0, 0.92, 0.48, 0.0)
# Tip flecks near aftershock origin (~z 0.08), under held twist copy.
FINALE_REVEAL_CREAM_EDGE_FLECK_ORIGIN = (0.0, 0.0, 0.10)
# Soft cream-sparkle flecks along the cream edge (victory #129 twin,
# quieter residual glitter). Disable drops sparkles only.
FINALE_REVEAL_CREAM_EDGE_SPARKLE_ENABLED = True
FINALE_REVEAL_CREAM_EDGE_SPARKLE_COUNT = 7
FINALE_REVEAL_CREAM_EDGE_SPARKLE_SIZE = 0.014
FINALE_REVEAL_CREAM_EDGE_SPARKLE_RISE = 0.18
FINALE_REVEAL_CREAM_EDGE_SPARKLE_SPREAD = 0.95
FINALE_REVEAL_CREAM_EDGE_SPARKLE_SEC = 0.38
FINALE_REVEAL_CREAM_EDGE_SPARKLE_COLOR = (1.0, 0.97, 0.80, 0.82)
FINALE_REVEAL_CREAM_EDGE_SPARKLE_END_COLOR = (1.0, 0.94, 0.60, 0.0)
FINALE_REVEAL_CREAM_EDGE_SPARKLE_ORIGIN = (0.0, 0.0, 0.10)

# Soft cream wash pulse after finale reveal cream edge / aftershock
# (#133/#86). Trust / handoff / victory cream wash grammar (#145/#141/#138)
# — delayed two-beat aspect2d veil on the Oswald-twist residual only.
# Soft under edge strips (bin 56) / aftershock (58); cream / pastel only.
# Quieter / shorter than victory wash (#138) so the truth sting stays
# bittersweet; rides with aftershock fleck hang (~0.85s). Mid-campaign
# trust / handoff / victory stay on their own wash modules.
# FINALE_REVEAL_CREAM_WASH_ENABLED = False drops wash only (aftershock +
# edge remain). No keyblades / KH branding.
FINALE_REVEAL_CREAM_WASH_ENABLED = True
FINALE_REVEAL_CREAM_WASH_DELAY_SEC = 0.40  # after play; after edge peak
FINALE_REVEAL_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
FINALE_REVEAL_CREAM_WASH_PEAK = 0.13
FINALE_REVEAL_CREAM_WASH_MID = 0.07
FINALE_REVEAL_CREAM_WASH_IN_SEC = 0.07
FINALE_REVEAL_CREAM_WASH_PULSE_SEC = 0.12
FINALE_REVEAL_CREAM_WASH_HOLD_SEC = 0.10
FINALE_REVEAL_CREAM_WASH_OUT_SEC = 0.42  # soft residual settle under twist
# Under cream edge (56) / aftershock (58); soft veil settle beat.
FINALE_REVEAL_CREAM_WASH_BIN = 54

STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_VICTORY = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_VICTORY: 'victory',
}
