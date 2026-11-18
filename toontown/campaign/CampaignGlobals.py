"""Act table for the Toontown spiritual-sequel reclaim campaign.

Combat feel borrows KH-style readability (telegraphs, lock-on, combos) —
no keyblades. Protagonist Oswald; end-game twist: he caused the corruption.
"""

from toontown.toonbase import ToontownGlobals

# Pure HQ — story hub, lightly threatened but not a reclaim act.
HUB_ZONE = ToontownGlobals.ToontownCentral
HUB_NAME = 'Toontown Central'

# Per reclaim: multiplicative bump applied to HackSlashConfig.COMBO_DAMAGE.
POWER_BUMP_PER_RECLAIM = 0.08
POWER_BUMP_MAX = 0.40

# Escalating reclaim acts: explore → fight → reclaim → next hood.
# Finale = two-phase Ink Overlord; leave copy room for Oswald twist beat.
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
        'banner': 'Act 1 — Corruption stains Loopy Lane!',
        'handoff': 'Loopy Lane is pure again! Next: Punchline Place (zone 2300).',
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
        'banner': 'Act 2 — Punchline Place is drowning in sludge!',
        'handoff': 'Punchline Place laughs clean! Finale awaits on Silly Street (zone 2100).',
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
        'banner': 'Finale Phase 1 — The Ink Overlord rises on Silly Street!',
        # Victory copy stays purity-first; Oswald twist lands via FINALE_TWIST_TEASE.
        'handoff': 'Toon City is saved! Purity restored across every neighborhood.',
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
            'banner': 'Finale Phase 2 — Ink Overlord Unleashed! Finish it!',
            'finalePhase': 2,
            'transitionSting': True,
            'bruteFraction': 0.0,
            'snareFraction': 0.0,
        },
    },
)

# Client presentation for Silly Street Ink Overlord phases (1 / 2).
FINALE_PHASE_BANNER = {
    1: 'INK OVERLORD RISES',
    2: 'INK OVERLORD UNLEASHED',
}
FINALE_PHASE_SUB = {
    1: 'Magenta swell — tall rubber wind-up + rise SFX!',
    2: 'Crimson fury — wider squash, hotter slam + phase-2 sting!',
}
# Compact HUD phase labels (status strip + telegraph cue).
FINALE_PHASE_HUD = {
    1: 'OVERLORD · P1 RISE',
    2: 'OVERLORD · P2 UNLEASHED',
}
# Soft twist tease after P2 clear — room for Oswald-caused-it beat (no full dialogue).
FINALE_TWIST_TEASE = '…but who stained the ink first?'
FINALE_TWIST_TEASE_COLOR = (0.85, 0.75, 1.0, 1.0)

STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_VICTORY = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_VICTORY: 'victory',
}
