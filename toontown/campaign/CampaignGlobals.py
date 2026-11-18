"""Act table for the KH×Toontown multi-hood reclaim campaign."""

from toontown.toonbase import ToontownGlobals

# Pure HQ — story hub, lightly threatened but not a reclaim act.
HUB_ZONE = ToontownGlobals.ToontownCentral
HUB_NAME = 'Toontown Central'

# Escalating reclaim acts: explore → fight → reclaim → next hood.
# Finale uses a boss-scale CorruptToon and heavier pollution.
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
        'banner': 'Act 1 — Corruption stains Loopy Lane!',
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
        'banner': 'Act 2 — Punchline Place is drowning in sludge!',
    },
    {
        'id': 'finale',
        'name': 'Silly Street Finale',
        'zoneId': ToontownGlobals.SillyStreet,
        'seedPollution': 0.90,
        'packSize': 1,
        'maxPacks': 2,
        'corruptHp': 120,
        'corruptName': 'Ink Overlord',
        'banner': 'Finale — Defeat the Ink Overlord and reclaim Silly Street!',
        'finale': True,
    },
)

STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_VICTORY = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_VICTORY: 'victory',
}
