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
# Post-betrayal hub stain (HubStain / CampaignDirectorAI): after finale
# victory while Corrupted Oswald chase is still pending, TTC receives
# authored pollution fog so the hub is not a pristine sunny plaza.
# Chase clear / replay wipe washes it. Gameplay world consequence — not
# cream FX, not OswaldPresence deepen. HUB_STAIN_ENABLED = False drops
# hub pollution only (betrayal chase / epilogue tips remain).
# No keyblades / KH branding.
HUB_STAIN_ENABLED = True
HUB_STAIN_POLLUTION = 0.42  # readable fog; under street seed caps
HUB_STAIN_MSG = (
    "Oswald's ink reaches Toon Central — the hub is stained!")
HUB_STAIN_CLEAR_MSG = (
    "Toon Central's stain lifts — purity holds at the hub.")
# Plaza confront placemarker when hub is stained (HubStainConfront).
# Complements pollution fog — not OswaldPresence trusted-face deepen.
# HUB_STAIN_CONFRONT_ENABLED = False drops placemarker + tip only (fog remains).
HUB_STAIN_CONFRONT_ENABLED = True
HUB_STAIN_CONFRONT_LABEL = "Oswald's stain"
HUB_STAIN_CONFRONT_TIP = (
    "Oswald's ink stains the plaza — wash the betrayal chase!  |  "
    'F fight  |  C campaign')
HUB_STAIN_CONFRONT_FORWARD = 5.5
# Washed-plaza epilogue beat after chase clear (HubEpilogueBeat).
# Complements HubStainConfront (pending stain): once fog washes, TTC gets
# an authored celebration placemarker + absence confirmation tip — not
# HUD plate / HUB_VICTORY_TIP alone. HUB_EPILOGUE_BEAT_ENABLED = False
# drops world placemarker + tip only (epilogue handoff plate / hub tip
# remain). Not cream FX, not OswaldPresence deepen. No keyblades / KH.
HUB_EPILOGUE_BEAT_ENABLED = True
HUB_EPILOGUE_BEAT_LABEL = 'Plaza washed'
HUB_EPILOGUE_BEAT_ABSENCE = "Oswald's gone — plaza pure"
HUB_EPILOGUE_BEAT_TIP = (
    "Toon Central plaza is washed clean — Oswald's absence holds. "
    'Replay from hub / C on Loopy!  |  F fight  |  C campaign')
HUB_EPILOGUE_BEAT_FORWARD = 5.5
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
        # Fraction fallback; waveScripts own Act 1 beats (Smudge → Brute → Snare).
        'bruteFraction': 0.0,
        'snareFraction': 0.0,
        'waveScripts': (
            ('ink', 'ink', 'ink'),
            ('ink', 'ink', 'brute'),
            ('snare', 'ink', 'brute'),
        ),
        'banner': 'Act 1 — Oswald calls for help! Corruption stains Loopy Lane!',
        # Mid-act Loopy approach tip (PlayEntry, after trusted street entry):
        # Oswald still the helper — smile sticks a rubbery half-beat —
        # foreshadow only before Punchline handoff (no Silly twist spoilers /
        # no "Oswald caused it"). Early entry tip stays sunny STREET_PACK.
        'approachTip': (
            'Oswald: smile sticks a rubbery half-beat — '
            '"Ink\'s stubborn today—" then tips his ears: keep reclaiming!  |  '
            'F fight Smudges  |  Shift dodge  |  C campaign'),
        # Client celebration copy (title / Oswald tip / next-street cue).
        # Mid-act trust fracture: still a cheer, smile holds a rubbery beat
        # too long — foreshadow only (no Silly twist spoilers).
        'handoffTitle': 'LOOPY LANE IS PURE!',
        'handoff': (
            'Oswald cheers: Loopy Lane is pure again! '
            'Smile holds a rubbery beat too long… '
            'Next: Punchline Place.'),
        'nextCue': (
            'Oswald points the tunnel → Punchline Place — '
            'grin still stretchy'),
        'nextStreet': 'Punchline Place',
        'trustFracture': True,
    },
    {
        'id': 'punchline',
        'name': 'Punchline Place',
        'zoneId': ToontownGlobals.PunchlinePlace,
        'seedPollution': 0.70,
        'packSize': 4,
        'maxPacks': 4,
        'corruptHp': 40,
        'corruptName': 'Ink Smudge',
        # Mix Gunk Gagsters (gag-lob puddle) + Brutes + Balloon Snares.
        'bruteFraction': 0.3,
        'bruteWaveStart': 1,
        'bruteName': 'Sludge Brute',
        'snareFraction': 0.2,
        'snareWaveStart': 1,
        'snareName': 'Balloon Snare',
        'gagsterFraction': 0.3,
        'gagsterWaveStart': 1,
        'gagsterName': 'Gunk Gagster',
        # Scripted sludge beats (Snare + Gagster → swarm → Brute pair → elite).
        'waveScripts': (
            ('snare', 'gagster', 'ink', 'brute'),
            ('snare', 'gagster', 'gagster', 'brute', 'ink'),
            ('snare', 'gagster', 'brute', 'brute', 'ink'),
            ('snare', 'gagster', 'gagster', 'brute', 'snare', 'ink'),
        ),
        'banner': (
            'Act 2 — Oswald leads the reclaim — '
            'Punchline Place is drowning in sludge!'),
        # Act-entry tip (PlayEntry) — Oswald trusted lead + Gagster/Brute/Snare.
        # Deepens Loopy mid-act unease (#190): cheer feels a half-beat off —
        # foreshadow only (no Silly twist spoilers). Hose-pop tunables below.
        'entryTip': (
            'Oswald leads Act 2 — cheer feels a half-beat off — '
            'Punchline Place sludge: explore → '
            'F fight Gunk Gagsters, Sludge Brutes & Balloon Snares → reclaim  |  '
            'Shift dodge  |  C campaign'),
        # Punchline clear deepens trust fracture: still a cheer, rubber-hose
        # grin hangs odd again — foreshadow only (no Silly twist spoilers).
        'handoffTitle': 'PUNCHLINE PLACE LAUGHS CLEAN!',
        'handoff': (
            'Oswald points ahead: Punchline laughs clean! '
            'Cheer stretches rubbery again… '
            'Next: Silly Street.'),
        'nextCue': (
            'Oswald steers you on → Silly Street — '
            'smile still a half-beat late'),
        'nextStreet': 'Silly Street',
        'trustFracture': True,
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
        # Boss fight stays Overlord-only (no Brute / Snare / Gagster mix).
        'bruteFraction': 0.0,
        'snareFraction': 0.0,
        'gagsterFraction': 0.0,
        # P1: solo Overlord → twin swell (matches Silly STREET_PACKS).
        'waveScripts': (
            ('ink',),
            ('ink', 'ink'),
        ),
        'banner': (
            'Finale Phase 1 — Oswald stands with you against '
            'the Ink Overlord on Silly Street!'),
        # Act-entry tip (PlayEntry) — Oswald lead + Ink Overlord cues.
        # Deepens Punchline unease (#198): cheer feels wrong beside the
        # Overlord fight ahead — foreshadow only (no twist spoilers /
        # no "Oswald caused it"). Hose-pop tunables below.
        'entryTip': (
            'Oswald leads Act 3 — cheer feels wrong on this street — '
            'Silly Street finale: explore → '
            'F fight the Ink Overlord → reclaim  |  '
            'Shift dodge  |  C campaign'),
        # Tip-only unease: longer fracture hose settle on entry. Do NOT set
        # trustFracture here — victory / twist stay on the sunny reveal path.
        'entryTipUnease': True,
        # Mid-act Silly Street approach tip (PlayEntry, after entry tip):
        # Oswald almost confesses — uneasy half-truth before the finale
        # reveal. Deepens #200 Overlord foreshadow; still no full twist
        # spoiler / no "Oswald caused the corruption" / no KH branding.
        'approachTip': (
            'Oswald almost confesses — "the ink… maybe my gag went wrong—" '
            'then laughs too loud: Overlord first!  |  '
            'F fight  |  Shift dodge  |  C campaign'),
        # Twist: trusted Oswald was the source of the neighborhood pollution.
        # betrayalHandoff: CampaignHandoff lands a hose-pop plate when
        # oswaldRevealSting / oswaldRevealBanner fires (after purity cheer).
        'handoffTitle': 'VICTORY…?',
        'handoff': (
            'Oswald smiles too wide. '
            'The ink corrupting Toon City was his all along.'),
        'nextCue': 'Oswald caused the corruption',
        'nextStreet': None,
        'finale': True,
        'betrayalHandoff': True,
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
            'gagsterFraction': 0.0,
            # Unleashed Overlord swells — still Overlord-only (ink tokens).
            'waveScripts': (
                ('ink', 'ink'),
                ('ink', 'ink'),
                ('ink', 'ink', 'ink'),
            ),
            # Smudge adds on wave 2+ — arena pressure beside Unleashed AI.
            'addWaveStart': 2,
            'addCount': 2,
            'addHp': 25,
            'addName': 'Ink Smudge',
        },
    },
)

# Hub PlayEntry tip — points new players at Act 1 without magic words / zone ids.
# Soft next-street cues reuse hubPlayEntryTip(nextStreet=…) after a handoff.
# STATE_VICTORY + chaseCleared=0 → chase-pending tip (stain still marks hub).
# STATE_VICTORY + chaseCleared=1 → hubVictoryReplayTip (soft-end washed copy).
HUB_TIP = (
    'Oswald needs you on Loopy Lane — hop the tunnel and reclaim purity!  |  '
    'C campaign')
HUB_CHASE_PENDING_TIP = (
    "Oswald's stain still marks the hub — wash the betrayal chase!  |  "
    'C campaign')
HUB_VICTORY_TIP = (
    "Campaign complete — Oswald's stain is washed. "
    'Replay from hub / C on Loopy Lane!  |  C campaign')


def hubPlayEntryTip(face=None, nextStreet=None, victory=False,
                    chasePending=False):
    """Player-facing hub tip. nextStreet overrides Loopy after a handoff.

    When ``victory`` is True with ``chasePending``, return the chase-pending
    tip (do not claim the stain is washed). When ``victory`` alone, return
    the soft-end replay tip after chase clear.
    """
    if victory and chasePending:
        return hubChasePendingTip(face=face)
    if victory:
        return hubVictoryReplayTip(face=face)
    face = face or RECLAIM_FACE
    street = nextStreet or ACTS[0]['name']
    return (
        '%s needs you on %s — hop the tunnel and reclaim purity!  |  '
        'C campaign' % (face, street))


def hubChasePendingTip(face=None):
    """Hub tip while STATE_VICTORY but Corrupted Oswald chase still pending."""
    tip = HUB_CHASE_PENDING_TIP
    if tip:
        return str(tip)
    face = face or RECLAIM_FACE
    return (
        "%s's stain still marks the hub — wash the betrayal chase!  |  "
        'C campaign' % face)


def hubVictoryReplayTip(face=None):
    """Hub tip after campaign victory / chase-clear epilogue (soft end)."""
    tip = HUB_VICTORY_TIP
    if tip:
        return str(tip)
    face = face or RECLAIM_FACE
    return (
        'Campaign complete — %s\'s stain is washed. '
        'Replay from hub / C on Loopy Lane!  |  C campaign' % face)


def handoffTravelHint(nextAct, face=None):
    """Next-street travel line — no zone ids / ~startcampaign."""
    face = face or RECLAIM_FACE
    name = (nextAct or {}).get('name') or 'the next street'
    return (
        'Head to %s — %s will field the packs when you arrive.'
        % (name, face))


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
# Deepened cream hose settle after Punchline tip trust/fracture bounce
# (#198 / #227 / #256 deepen). Juicier outward overshoot → rest → micro
# rebound → rest past #256 so the Act 2 unease tip lands rubber-hose and
# reads juicier — handoff cream edge settle rebound twin (#240/#271) on
# the tip bar. Armed on tipHose='punchline' only. Distinct from Silly
# almost-confess tip cream hose settle (#232/#279 — taller/longer primary
# overshoot, no tip rebound) and Silly Overlord tip cream wash +
# aftershock deepen (#251/#279 — wash flecks/halo, not tip scale).
# PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED = False drops this cream
# settle + rebound only (hose pop + trust/fracture settle + cream wash
# remain). No keyblades / KH branding.
PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED = True
PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT = (1.10, 1.0, 1.15, 0.075)  # juicier than #256 (1.08/1.12/0.065)
PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC = 0.11  # was 0.10 @ #256
PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND = (1.035, 1.0, 1.06, 0.045)  # juicier micro bounce past #256; under betrayal
PUNCHLINE_ACT_TIP_CREAM_HOSE_SETTLE_REBOUND_REST_SEC = 0.07  # was 0.06 @ #256

# Soft cream wash pulse after Punchline Act 2 tip hose pop (#91).
# Act-banner / trust wash grammar (#154/#145) — delayed two-beat aspect2d
# veil on PlayEntry tipHose='punchline' path only. Soft under the tip bar;
# cream / pastel only. A touch quieter / shorter than handoff wash (#141)
# — tip lands without glitter hang (trust / act-banner wash twin). Wash
# delay tracks the juicier cream hose settle past #256. Loopy / default
# tip hose stay wash-free; Silly tip wash lives in its own module.
# Act-enter / trust / handoff / victory / finale washes live in their own
# modules. PUNCHLINE_ACT_TIP_CREAM_WASH_ENABLED = False drops wash only
# (hose pop + trust settle + cream hose settle remain). No keyblades / KH
# branding.
PUNCHLINE_ACT_TIP_CREAM_WASH_ENABLED = True
PUNCHLINE_ACT_TIP_CREAM_WASH_DELAY_SEC = 0.70  # after play; after cream hose settle + rebound past #256
PUNCHLINE_ACT_TIP_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
PUNCHLINE_ACT_TIP_CREAM_WASH_PEAK = 0.13  # was 0.12; soft veil rides juicier hose
PUNCHLINE_ACT_TIP_CREAM_WASH_MID = 0.08  # was 0.07
PUNCHLINE_ACT_TIP_CREAM_WASH_IN_SEC = 0.08  # was 0.07
PUNCHLINE_ACT_TIP_CREAM_WASH_PULSE_SEC = 0.13  # was 0.12
PUNCHLINE_ACT_TIP_CREAM_WASH_HOLD_SEC = 0.12  # was 0.10
PUNCHLINE_ACT_TIP_CREAM_WASH_OUT_SEC = 0.40  # soft settle, no glitter hang (was 0.36)
# Above ink entry vignette (48); soft veil settle under tip bar.
PUNCHLINE_ACT_TIP_CREAM_WASH_BIN = 49

# Silly Street Act 3 entry tip — tip-matched hose pop, slightly heavier for
# the Ink Overlord finale beat. entryTipUnease deepens Punchline half-beat
# off (#198): cheer feels wrong beside the Overlord fight — foreshadow only
# (no twist spoilers). Soft sunny settle kept as fallback; PlayEntry swaps
# to OSWALD_TRUST_FRACTURE_* when entryTipUnease is armed. Mid-act approach
# tip (approachTip) almost-confesses an uneasy half-truth after entry —
# same fracture hose settle, still no full twist spoil. No KH branding.
SILLY_ACT_TIP_POP_SQUASH = (1.68, 1.0, 0.46, 0.05)   # sx, sy, sz, sec
SILLY_ACT_TIP_POP_STRETCH = (0.70, 1.0, 1.52, 0.08)
SILLY_ACT_TIP_POP_SETTLE_SEC = 0.10
SILLY_ACT_TIP_TRUST_SETTLE_OVERSHOOT = (0.88, 1.0, 1.18, 0.07)
SILLY_ACT_TIP_TRUST_SETTLE_REST_SEC = 0.09
# Deepened cream hose settle after Silly tip fracture bounce (#207 /
# #232 / #279 deepen). Juicier outward overshoot → rest so the almost-
# confess / trust-fracture tip lands rubber-hose and readable past #279 —
# Punchline tip cream hose settle twin on the tip bar, taller/longer
# primary overshoot for Act 3 unease (no tip rebound — Punchline deepen
# owns that micro bounce; betrayal banner owns climax rebound). Armed on
# tipHose='silly' only (entry foreshadow + mid-act approachTip). Distinct
# from Punchline tip cream hose deepen (#256 / #284), finale betrayal
# banner (#235 / #260 / #288), and victory twist sting (#244).
# SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED = False drops this cream settle
# only (hose pop + trust/fracture settle + cream wash remain).
# No keyblades / KH branding.
SILLY_ACT_TIP_CREAM_HOSE_SETTLE_ENABLED = True
SILLY_ACT_TIP_CREAM_HOSE_SETTLE_OVERSHOOT = (1.13, 1.0, 1.20, 0.09)  # juicier than #279 (1.11/1.17/0.08)
SILLY_ACT_TIP_CREAM_HOSE_SETTLE_REST_SEC = 0.13  # was 0.12 @ #279
# Delay after Silly Street enter before the mid-act almost-confess tip
# replaces the entry tip (PlayEntry). Longer than SILLY_AUTO_RECLAIM so
# the explore / entry foreshadow beat lands first.
SILLY_APPROACH_TIP_DELAY_SEC = 3.85
# Delay after Loopy Lane enter before the mid-act unease tip replaces the
# trusted street entry tip (PlayEntry). Longer than LOOPY_AUTO_RECLAIM so
# Oswald trust stays intact early; Punchline entryTip deepens the beat.
# No cream hose / wash deepen — copy + fracture tipHose settle only.
LOOPY_APPROACH_TIP_DELAY_SEC = 3.45

# Soft cream wash pulse + delayed cream aftershock after Silly Act 3 tip
# hose pop (#95) / Overlord foreshadow / almost-confess tip (#200 / #251 /
# #279 deepen). Act-banner / Punchline tip wash grammar deepened past
# #279 — juicier two-beat aspect2d veil on PlayEntry tipHose='silly' path
# only, then richer flecks + halo settle under the tip bar so the
# almost-confess / foreshadow tip reads juicier before the boss. Cream /
# pastel only. Still quieter / shorter than handoff wash (#141) and
# victory glitter hang — tip foreshadow residual, not twist payoff.
# Distinct from victory twist sting cream deepen (#244) and betrayal
# banner cream hose settle (#235 / #288); tip bar cream hose settle
# deepen (#232 / #279 / this PR) stays on the scale path. Loopy /
# Punchline / default tip hose stay wash-free. Act-enter / trust /
# handoff / victory / finale washes live in their own modules.
# SILLY_ACT_TIP_CREAM_WASH_ENABLED = False drops wash + aftershock only
# (hose pop + trust settle + cream hose settle remain).
# No keyblades / KH branding.
SILLY_ACT_TIP_CREAM_WASH_ENABLED = True
SILLY_ACT_TIP_CREAM_WASH_DELAY_SEC = 0.68  # after play; after deepened cream hose settle past #279
SILLY_ACT_TIP_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SILLY_ACT_TIP_CREAM_WASH_PEAK = 0.15  # past #279; under victory (0.16)
SILLY_ACT_TIP_CREAM_WASH_MID = 0.10  # was 0.09 @ #279
SILLY_ACT_TIP_CREAM_WASH_IN_SEC = 0.07
SILLY_ACT_TIP_CREAM_WASH_PULSE_SEC = 0.14  # was 0.13 @ #279
SILLY_ACT_TIP_CREAM_WASH_HOLD_SEC = 0.16  # was 0.14 @ #279
SILLY_ACT_TIP_CREAM_WASH_OUT_SEC = 0.48  # soft settle rides tip residual
# Above ink entry vignette (48); soft veil settle under tip bar.
SILLY_ACT_TIP_CREAM_WASH_BIN = 49
# Soft cream fleck / halo residual after Silly tip wash. Tip-bar origin
# (near PLAY_ENTRY_TIP_POS), quieter than victory twist aftershock (#244)
# and not a betrayal title hose settle (#235 / #288). Deepened past #279.
# SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ENABLED = False drops residual only.
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ENABLED = True
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.18  # after wash starts
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.72)  # under tip bar
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COUNT = 5  # under victory wash (6); was 5 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_SIZE = 0.017  # was 0.016 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_DRIFT = 0.30  # was 0.28 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_FALL = 0.23  # was 0.21 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_SEC = 0.40  # was 0.36 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.78)
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
# Above wash bin (49); soft residual under tip bar.
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_BIN = 51
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.42  # was 0.40 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_START = 0.26
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.22  # was 1.18 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.33  # was 0.30 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.14  # was 0.13 @ #279
SILLY_ACT_TIP_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

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

# Mid-act Oswald trust fracture (Loopy + Punchline clears / tips).
# Off-tone trust foreshadow only — no twist spoilers / no KH branding.
# Hose settle holds a rubbery beat longer than sunny trust (#76); cream
# edge cools toward a soft shadow fleck settle (ActBannerCreamEdgeFx).
# Punchline deepens Loopy unease (#190); Silly Act 3 entry tip reuses the
# longer settle via entryTipUnease (Overlord foreshadow) without arming
# finale trustFracture — victory / twist stay sunny until reveal.
OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT = (0.88, 1.0, 1.18, 0.09)
OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC = 0.14
OSWALD_TRUST_FRACTURE_SUB_COLOR = (0.88, 0.92, 0.86, 1.0)
# Cooler cream frame + shadow-fade flecks on trust-fracture handoffs.
# Composes with carnival confetti (#57) — replaces sunny handoff cream edge
# on trustFracture acts only (Loopy + Punchline). Silly victory stays sunny
# until twist reveal.
# OSWALD_TRUST_FRACTURE_CREAM_EDGE_ENABLED = False drops fracture edge only
# (carnival + hose settle remain).
OSWALD_TRUST_FRACTURE_CREAM_EDGE_ENABLED = True
OSWALD_TRUST_FRACTURE_CREAM_EDGE_COLOR = (0.90, 0.93, 0.86, 1.0)  # cool cream
OSWALD_TRUST_FRACTURE_CREAM_EDGE = 0.28  # strip thickness in aspect2d units
OSWALD_TRUST_FRACTURE_CREAM_EDGE_PEAK = 0.36
OSWALD_TRUST_FRACTURE_CREAM_EDGE_PULSE = 0.20  # mid-beat alpha after peak
OSWALD_TRUST_FRACTURE_CREAM_EDGE_IN_SEC = 0.08
OSWALD_TRUST_FRACTURE_CREAM_EDGE_HOLD_SEC = 0.12  # held a beat (unease)
OSWALD_TRUST_FRACTURE_CREAM_EDGE_PULSE_SEC = 0.14
OSWALD_TRUST_FRACTURE_CREAM_EDGE_OUT_SEC = 0.40  # soft shadow settle
# Below handoff plate/title bins (60/62); above ink entry vignette (48).
OSWALD_TRUST_FRACTURE_CREAM_EDGE_BIN = 55
OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_COUNT = 5
OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_SIZE = 0.020
OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_DRIFT = 0.16
OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_SEC = 0.32
OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_COLOR = (0.82, 0.86, 0.90, 0.82)
OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_END_COLOR = (0.28, 0.26, 0.34, 0.0)
# Flecks cluster near the handoff plate (root ~z 0.42).
OSWALD_TRUST_FRACTURE_CREAM_EDGE_FLECK_ORIGIN = (0.0, 0.0, 0.42)

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
# OSWALD_TRUST_BANNER_CREAM_WASH_ENABLED = False drops wash (+ wash
# aftershock) only (hose settle + cream edge remain). No keyblades / KH
# branding.
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

# Delayed cream aftershock after Oswald trust cream wash (#145). Finale
# reveal cream wash aftershock grammar (#176) / victory (#168) / entry /
# purity-complete (#132/#136) — quieter flecks settle downward with a soft
# cream halo under the trust plate. Oswald trusted early/mid path only;
# owned by OswaldTrustCreamWashFx. Quieter than finale / victory wash
# aftershock — trust settles fire more often with no glitter hang.
# OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_ENABLED = False drops wash
# aftershock only (wash + hose settle + cream edge remain). No keyblades /
# KH branding.
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_ENABLED = True
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.22  # after wash starts
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, 0.32)  # under plate
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_COUNT = 5
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_SIZE = 0.015
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_DRIFT = 0.28
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_FALL = 0.22
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_SEC = 0.34
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.74)
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
# Above wash veil (54); rides with cream edge (55) residual.
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_BIN = 55
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.44
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_HALO_START = 0.28
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.14
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.28
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.11
OSWALD_TRUST_BANNER_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

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
# Brief rubber-hose scale settle after handoff cream edge peak (#124 /
# #222 / #240 / #271 deepen). Juicier overshoot → rest → micro rebound →
# rest past #271 so Loopy→Punchline→Silly neighborhood transitions read
# carnival-juicy and the cream frame lands readable — Oswald trust banner
# settle (#76) twin on the carnival edge. Distinct from Punchline tip
# cream hose (#227/#256/#284), Silly tip / almost-confess hose
# (#232/#279/#294), and finale betrayal cream hose (#235/#260/#288) —
# those settle tip/title bars; this settles the sunny edge frame only.
# HANDOFF_CREAM_EDGE_SETTLE_ENABLED = False drops settle only (edge +
# sparkle + wash remain). No keyblades / KH branding.
HANDOFF_CREAM_EDGE_SETTLE_ENABLED = True
HANDOFF_CREAM_EDGE_SETTLE_OVERSHOOT = (1.12, 1.0, 1.18, 0.11)  # juicier than #271 (1.10/1.16/0.10)
HANDOFF_CREAM_EDGE_SETTLE_REST_SEC = 0.10  # was 0.09 @ #271
HANDOFF_CREAM_EDGE_SETTLE_REBOUND = (1.05, 1.0, 1.08, 0.06)  # juicier micro bounce past #271
HANDOFF_CREAM_EDGE_SETTLE_REBOUND_REST_SEC = 0.10  # was 0.09 @ #271

# Soft cream wash pulse after handoff cream edge / sparkle (#124/#99).
# Perfect-dodge / melee hit / victory / Oswald-trust cream wash grammar —
# delayed two-beat aspect2d veil on Loopy→Punchline (and act) carnival
# handoffs only. Soft under edge strips (bin 55) / plate (60); cream /
# pastel only. Still shorter hang than victory wash (#138) — handoffs
# fire more often. Wash delay tracks the juicier edge settle past #271.
# Oswald trust / finale-reveal wash live separately; phase stays
# wash-free here. HANDOFF_CREAM_WASH_ENABLED = False drops wash only
# (carnival + sparkle + edge remain). No keyblades / KH branding.
HANDOFF_CREAM_WASH_ENABLED = True
HANDOFF_CREAM_WASH_DELAY_SEC = 0.60  # after play; after juicier edge settle past #271
HANDOFF_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
HANDOFF_CREAM_WASH_PEAK = 0.16  # soft bump with settle deepen past #271
HANDOFF_CREAM_WASH_MID = 0.10
HANDOFF_CREAM_WASH_IN_SEC = 0.07
HANDOFF_CREAM_WASH_PULSE_SEC = 0.14
HANDOFF_CREAM_WASH_HOLD_SEC = 0.10
HANDOFF_CREAM_WASH_OUT_SEC = 0.44  # rides with handoff glitter hang (~0.68)
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

# Delayed cream aftershock after victory cream wash (#138) / confetti swell
# (#82). Entry / purity-complete cream aftershock grammar (#132/#136) —
# quieter flecks settle downward with a soft cream halo under the victory
# plate. Victory-path only; clears with wash before Oswald twist /
# FinalePhaseFx reveal. VICTORY_CREAM_AFTERSHOCK_ENABLED = False drops
# aftershock only (wash + swell + sparkle + edge remain). No keyblades /
# KH branding.
VICTORY_CREAM_AFTERSHOCK_ENABLED = True
VICTORY_CREAM_AFTERSHOCK_DELAY_SEC = 0.22  # after wash starts
VICTORY_CREAM_AFTERSHOCK_ORIGIN = (0.0, 0.0, 0.22)  # under victory plate
VICTORY_CREAM_AFTERSHOCK_COUNT = 6
VICTORY_CREAM_AFTERSHOCK_SIZE = 0.017
VICTORY_CREAM_AFTERSHOCK_DRIFT = 0.32
VICTORY_CREAM_AFTERSHOCK_FALL = 0.26
VICTORY_CREAM_AFTERSHOCK_SEC = 0.36
VICTORY_CREAM_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.82)
VICTORY_CREAM_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
# Above wash veil (54); below cream edge (58) / plate (60).
VICTORY_CREAM_AFTERSHOCK_BIN = 56
VICTORY_CREAM_AFTERSHOCK_HALO_ENABLED = True
VICTORY_CREAM_AFTERSHOCK_HALO_HALF = 0.52
VICTORY_CREAM_AFTERSHOCK_HALO_START = 0.28
VICTORY_CREAM_AFTERSHOCK_HALO_PEAK = 1.22
VICTORY_CREAM_AFTERSHOCK_HALO_SEC = 0.30
VICTORY_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.15
VICTORY_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

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

# CampaignHandoff betrayal plate when oswaldRevealBanner fires (after cheer).
# Hose-pop handoff grammar lands the twist — complements almost-confess tip
# (#207) and FinalePhaseFx AV (flash/shadow/cream). No carnival / no KH.
FINALE_BETRAYAL_HANDOFF_CUE = (
    "The trusted ally's smile was the stain all along")
FINALE_BETRAYAL_HANDOFF_HOLD_SEC = 3.8

# Short corrupted-Oswald chase / arena after finale betrayal (gameplay
# payload — not cream FX). CampaignDirectorAI schedules a thin
# ARCHETYPE_CORRUPT_OSWALD spawn after the reveal delay; client tip arms
# the chase beat. Toontown spiritual sequel — no keyblades / KH branding.
# OSWALD_BETRAYAL_CHASE_ENABLED = False drops spawn + tip only (betrayal
# plate / reveal sting remain).
OSWALD_BETRAYAL_CHASE_ENABLED = True
OSWALD_BETRAYAL_CHASE_NAME = 'Corrupted Oswald'
# Seconds after campaignVictory before spawn (covers reveal delay + plate).
OSWALD_BETRAYAL_CHASE_DELAY_SEC = 3.15
# Optional override HP base (archetype defaultHp used when <= 0).
OSWALD_BETRAYAL_CHASE_HP = 0
OSWALD_BETRAYAL_CHASE_SPAWN_FORWARD = 7.5
OSWALD_BETRAYAL_CHASE_TIP = (
    'Oswald turns on you — betrayal lunge inbound!  |  '
    'F fight  |  Shift dodge')
OSWALD_BETRAYAL_CHASE_BANNER = 'CORRUPTED OSWALD CHASE!'
OSWALD_BETRAYAL_CHASE_MSG = (
    'Oswald sheds the smile — dodge the betrayal lunge and wash the stain!')
OSWALD_BETRAYAL_CHASE_CLEAR_MSG = (
    "Oswald's stain is washed — purity holds for real this time!")
# Tip lands slightly after spawn so the enemy is already fielded.
OSWALD_BETRAYAL_CHASE_TIP_DELAY_SEC = 0.35
# C / hydrate mid-victory while chaseCleared=0 — resume, do not replay-wipe.
OSWALD_BETRAYAL_CHASE_RESUME_MSG = (
    'Oswald betrayal chase still pending — stain wash resumes! '
    'Clear the chase, then C on Loopy to replay.')

# Campaign epilogue after Corrupted Oswald chase clear (gameplay soft-end).
# Client accepts oswaldBetrayalChaseCleared → CampaignHandoff plate + PlayEntry
# hub victory replay tip. Not cream FX; keeps betrayal kit / presence intact.
# CAMPAIGN_EPILOGUE_ENABLED = False drops chase-clear handoff + hub victory
# tip only (clear system message + chase spawn remain).
CAMPAIGN_EPILOGUE_ENABLED = True
CAMPAIGN_EPILOGUE_TITLE = 'STAIN WASHED'
CAMPAIGN_EPILOGUE_SUB = (
    "Oswald's smile is gone — purity holds for real this time.")
CAMPAIGN_EPILOGUE_CUE = (
    'Replay from Toon Central hub — C on Loopy Lane to start over')
CAMPAIGN_EPILOGUE_HOLD_SEC = 3.6
# Client watch polls for Corrupted Oswald defeat when AI messenger is
# process-local (real clients never see AI messenger.send).
CAMPAIGN_EPILOGUE_WATCH_SEC = 0.45

# Trusted Oswald hub/street NPC-style presence (meet the trust face
# before twist). Rubber-hose CardMaker body + nametag + short E-talk
# greet interact — plaza-anchored deepen (beyond spawn-near-avatar
# CardMaker stub) + reclaim cheer beat; still stub-shippable, not a
# full DistributedNPC / DNA toon / companion AI. Complements tip/banner
# copy + betrayal chase (#313); does not deepen cream FX. Hide after
# finale reveal / chase (and on AI-persisted STATE_VICTORY sync) so the
# trusted lead is gone once the twist lands. OSWALD_PRESENCE_ENABLED =
# False drops world stub + greet + cheer only (HUB_TIP / ACTS tips /
# betrayal chase remain). No keyblades / KH.
OSWALD_PRESENCE_ENABLED = True
OSWALD_PRESENCE_LABEL = 'Oswald'
OSWALD_PRESENCE_PLATE = 'OSWALD'
OSWALD_PRESENCE_HUB_GREET = (
    'Oswald waves from the plaza — "Loopy Lane needs us first!"  |  '
    'Hop the tunnel  |  C campaign')
OSWALD_PRESENCE_STREET_GREET = (
    'Oswald tips his ears — "I\'ll field the packs — stretch-punch ready!"  |  '
    'F fight  |  Shift dodge  |  C campaign')
# Once-ever trust beat after the first E-talk meet (survives relog via
# CampaignProgressSave.oswaldMet). Later zone visits keep hub/street greets.
OSWALD_PRESENCE_FIRST_MEET_TIP = (
    'You met Oswald — trust the plaza lead! He\'ll point the reclaim.  |  '
    'Hop a tunnel  |  C campaign')
OSWALD_PRESENCE_CHEER_TIP = (
    'Oswald cheers — "Street\'s clean! On to the next!"  |  '
    'Hop the tunnel  |  C campaign')
OSWALD_PRESENCE_INTERACT_PROMPT = 'E — Talk to Oswald'
OSWALD_PRESENCE_INTERACT_EVENT = 'oswaldPresenceInteract'
OSWALD_PRESENCE_MET_MSG = 'oswaldPresenceMet'
OSWALD_PRESENCE_MET_SYNC_MSG = 'oswaldMetSync'
OSWALD_PRESENCE_CHEER_MSG = 'oswaldPresenceCheer'
# Authored TTC plaza lead stand (x, y, z, h) — near HQ plaza approach,
# not spawn-relative to the local toon. Streets keep near-avatar offset.
OSWALD_PRESENCE_HUB_POS = (-48.0, 28.0, -0.55, -100.0)
# World stub placement relative to the local toon on street enter.
OSWALD_PRESENCE_SPAWN_FORWARD = 6.5
OSWALD_PRESENCE_SPAWN_RIGHT = 2.25
# Grounded NPC body (legacy MARKER_* kept as fallback aliases).
OSWALD_PRESENCE_BODY_Z = 0.0
OSWALD_PRESENCE_BODY_SCALE = 1.0
OSWALD_PRESENCE_NAMETAG_Z = 3.15
OSWALD_PRESENCE_NAMETAG_SCALE = 0.55
OSWALD_PRESENCE_MARKER_Z = 2.8
OSWALD_PRESENCE_MARKER_SCALE = 1.2
OSWALD_PRESENCE_INTERACT_RADIUS = 12.0
OSWALD_PRESENCE_POLL_SEC = 0.35
OSWALD_PRESENCE_GREET_HOLD_SEC = 3.2
OSWALD_PRESENCE_CHEER_HOLD_SEC = 2.4
OSWALD_PRESENCE_IDLE_BOB = True
OSWALD_PRESENCE_CHEER_ON_RECLAIM = True
# Sunny trusted body (readable on TTC / streets — not ink purple).
OSWALD_PRESENCE_BODY_COLOR = (0.22, 0.58, 0.96, 1.0)
OSWALD_PRESENCE_MARKER_COLOR = (0.18, 0.52, 0.92, 1.0)
OSWALD_PRESENCE_TIP_COLOR = (0.95, 0.98, 1.0, 1.0)
OSWALD_PRESENCE_HIDE_ON_BETRAYAL = True

FINALE_BETRAYAL_SETTLE_OVERSHOOT = (0.86, 1.0, 1.22, 0.10)
FINALE_BETRAYAL_SETTLE_REST_SEC = 0.16
FINALE_BETRAYAL_SUB_COLOR = (1.0, 0.78, 0.62, 1.0)
FINALE_BETRAYAL_CUE_COLOR = (1.0, 0.88, 0.52, 1.0)
# Deepened cream hose settle after betrayal title settle (#212 / #235 /
# #260 deepen). Juicier outward overshoot → rest → micro rebound → rest
# past #260 so the twist handoff plate lands rubber-hose and reads
# juicier — Punchline tip cream hose rebound twin (#256 / #284) on the
# finale betrayal banner only. Juicier climax than tip settles (#227 /
# #232 / #256 / #284). Distinct from act handoff cream edge settle
# rebound (#240 — settles sunny edge frame, not title), Silly almost-
# confess tip (#232/#279), and victory twist confetti sting (#244/#273).
# FINALE_BETRAYAL_CREAM_HOSE_SETTLE_ENABLED = False drops this cream
# settle + rebound only (hose pop + betrayal settle + cream edge remain).
# No keyblades / KH branding.
FINALE_BETRAYAL_CREAM_HOSE_SETTLE_ENABLED = True
FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT = (1.16, 1.0, 1.26, 0.10)  # juicier than #260 (1.14/1.22/0.09)
FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REST_SEC = 0.15  # was 0.14 @ #260
FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND = (1.05, 1.0, 1.09, 0.055)  # juicier micro bounce past #260
FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND_REST_SEC = 0.08  # was 0.07 @ #260

# Victory/confetti sting on Oswald twist (VictoryTwistConfettiSting /
# #217 / #244 / #265 deepen). Fires with the betrayal handoff plate
# (#212) after sunny #82 cream swell has cleared — juicier bittersweet
# cream + warm coral chips + taller micro cream pop rebound + richer
# soft cream aftershock so the finale twist payoff reads deeper past
# #265. Not a second triumphant carnival; not the victory cream swell.
# Distinct from FinaleCreamAftershock flash/ring (#86), act handoff
# cream edge settle deepen (#240), betrayal banner cream hose deepen
# (#235 / #260 / #288), Punchline tip cream hose (#256 / #284), and
# Silly almost-confess tip (#232 / #279 / #294) — those settle
# frames/titles/tips; this deepens the confetti sting cream under the
# plate. No keyblades / KH branding.
VICTORY_TWIST_CONFETTI_ENABLED = True
VICTORY_TWIST_CONFETTI_DELAY_SEC = 0.16  # after plate hose-pop starts
VICTORY_TWIST_CONFETTI_ORIGIN = (0.0, 0.0, 0.34)  # under betrayal plate
# Above cream edge (56) / reveal aftershock (58); under title bin (62+) read.
VICTORY_TWIST_CONFETTI_BIN = 61
VICTORY_TWIST_CONFETTI_FLASH_COLOR = (1.0, 0.87, 0.68, 1.0)  # warmer cream blush
VICTORY_TWIST_CONFETTI_FLASH_PEAK = 0.25  # juicier than #265 (0.23); under #82 (0.28)
VICTORY_TWIST_CONFETTI_FLASH_IN_SEC = 0.05
VICTORY_TWIST_CONFETTI_FLASH_HOLD_SEC = 0.09  # was 0.08 @ #265
VICTORY_TWIST_CONFETTI_FLASH_OUT_SEC = 0.52  # was 0.48 @ #265
VICTORY_TWIST_CONFETTI_COUNT = 13  # keep under #82 swell (14); juicier chips via size/pop
VICTORY_TWIST_CONFETTI_SIZE = 0.032  # was 0.030 @ #265
VICTORY_TWIST_CONFETTI_DRIFT = 0.68  # was 0.62 @ #265
VICTORY_TWIST_CONFETTI_FALL = 0.29  # hollow settle, not carnival lift (was 0.26)
VICTORY_TWIST_CONFETTI_SEC = 0.96  # was 0.90 @ #265; still under #82 (1.05)
VICTORY_TWIST_CONFETTI_POP = 1.84  # squash peak — juicier cream snap past #265 (1.72)
# Micro second cream rebound after squash/stretch before settle drift.
VICTORY_TWIST_CONFETTI_POP_REBOUND = 1.28  # was 1.22 @ #265
VICTORY_TWIST_CONFETTI_POP_REBOUND_SEC = 0.055  # was 0.05 @ #265
VICTORY_TWIST_CONFETTI_COLORS = (
    (1.0, 0.95, 0.80, 0.96),   # soft cream
    (1.0, 0.84, 0.60, 0.94),   # warm coral
    (1.0, 0.74, 0.50, 0.92),   # twist peach
    (0.99, 0.92, 0.64, 0.94),  # pastel gold
    (1.0, 0.68, 0.50, 0.90),   # hollow cheer blush
)
VICTORY_TWIST_CONFETTI_STREAK_COUNT = 6  # was 5 @ #265
VICTORY_TWIST_CONFETTI_STREAK_SIZE = 0.017  # was 0.016 @ #265
VICTORY_TWIST_CONFETTI_STREAK_DRIFT = 0.54  # was 0.50 @ #265
VICTORY_TWIST_CONFETTI_STREAK_SEC = 0.78  # was 0.72 @ #265
VICTORY_TWIST_CONFETTI_STREAK_COLORS = (
    (1.0, 0.97, 0.84, 0.90),
    (1.0, 0.80, 0.58, 0.88),
    (1.0, 0.90, 0.68, 0.86),
    (1.0, 0.86, 0.62, 0.84),
    (1.0, 0.72, 0.52, 0.82),
    (1.0, 0.78, 0.56, 0.84),
)
# Soft cream aftershock after deepened twist confetti — richer settle
# flecks + halo past #265 so the hollow cheer hangs readable without
# restaging #82 swell or FinaleCreamAftershock (#86). Toggle
# VICTORY_TWIST_CONFETTI_AFTERSHOCK_ENABLED = False drops residual only.
VICTORY_TWIST_CONFETTI_AFTERSHOCK_ENABLED = True
VICTORY_TWIST_CONFETTI_AFTERSHOCK_DELAY_SEC = 0.16  # sooner hang than #265 (0.18)
VICTORY_TWIST_CONFETTI_AFTERSHOCK_COUNT = 8  # was 7 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_SIZE = 0.021  # was 0.019 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_DRIFT = 0.40  # was 0.36 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_FALL = 0.30  # was 0.28 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_SEC = 0.44  # was 0.40 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_COLOR = (1.0, 0.96, 0.78, 0.90)
VICTORY_TWIST_CONFETTI_AFTERSHOCK_END_COLOR = (1.0, 0.86, 0.50, 0.0)
# Under confetti chips (61+); above reveal cream edge (56).
VICTORY_TWIST_CONFETTI_AFTERSHOCK_BIN = 60
VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_ENABLED = True
VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_HALF = 0.50  # was 0.46 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_START = 0.22  # was 0.24 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_PEAK = 1.38  # was 1.30 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_SEC = 0.38  # was 0.34 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_PEAK_ALPHA = 0.18  # was 0.16 @ #265
VICTORY_TWIST_CONFETTI_AFTERSHOCK_HALO_COLOR = (1.0, 0.92, 0.74, 1.0)

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
# FINALE_REVEAL_CREAM_WASH_ENABLED = False drops wash (+ wash aftershock)
# only (sting aftershock + edge remain). No keyblades / KH branding.
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

# Delayed cream aftershock after finale reveal cream wash (#149). Victory
# cream wash aftershock grammar (#168) / entry / purity-complete (#132/#136)
# — quieter flecks settle downward with a soft cream halo under held twist
# copy. Oswald-twist path only; owned by FinaleRevealCreamWashFx (separate
# from sting FinaleCreamAftershockFx #86). Quieter than victory wash
# aftershock so the truth sting stays bittersweet.
# FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_ENABLED = False drops wash aftershock
# only (wash + sting aftershock + edge remain). No keyblades / KH branding.
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_ENABLED = True
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.22  # after wash starts
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, 0.08)  # under twist
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_COUNT = 6
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_SIZE = 0.016
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_DRIFT = 0.30
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_FALL = 0.24
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_SEC = 0.36
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.78)
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
# Above wash veil (54); below cream edge (56) / sting aftershock (58).
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_BIN = 55
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.48
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_START = 0.28
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.18
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.30
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.13
FINALE_REVEAL_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

STATE_IDLE = 0
STATE_ACTIVE = 1
STATE_VICTORY = 2

STATE_NAMES = {
    STATE_IDLE: 'idle',
    STATE_ACTIVE: 'active',
    STATE_VICTORY: 'victory',
}

# Per-avatar act unlock persistence (CampaignProgressSave / AI dataFolder).
# Survives logout + district restart without a DistributedToon DC field.
# CAMPAIGN_PROGRESS_ENABLED = False keeps session-only director memory.
CAMPAIGN_PROGRESS_ENABLED = True
CAMPAIGN_PROGRESS_FILENAME = 'campaign_progress.json'

# Client login mirror — PollutionManager pushes unlockedThrough / state /
# chaseCleared / reclaimCount; PlayEntry + OswaldPresence + CampaignHandoff
# accept this messenger so hub tip, trusted presence, and melee POWER_BUMP
# match story state after relog (not session-only).
CAMPAIGN_PROGRESS_SYNC_MSG = 'campaignProgressSync'

# Live finale reclaim complete — AI messenger + PollutionManager
# announceCampaignVictory rebroadcast so real clients hear the same event
# (PlayEntry / OswaldPresence / chase tip / FinalePhaseFx / Handoff).
CAMPAIGN_VICTORY_MSG = 'campaignVictory'
