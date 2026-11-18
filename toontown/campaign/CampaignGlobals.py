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

STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_VICTORY = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_VICTORY: 'victory',
}
