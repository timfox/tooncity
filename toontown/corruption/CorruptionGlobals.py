"""Shared constants for pollution and corrupt toon enemies."""

# Pollution scalar: 0.0 = pure neighborhood, 1.0 = fully polluted.
POLLUTION_PURE = 0.0
POLLUTION_FULL = 1.0
POLLUTION_DEFAULT = POLLUTION_PURE

# Fixed-point helper matching DC uint16/1000(0-1).
POLLUTION_SCALE = 1000

# Default spawn / combat values.
CORRUPT_TOON_DEFAULT_HP = 30
CORRUPT_TOON_DEFAULT_NAME = 'Corrupt Toon'

# Archetypes — Smudge melee, Brute spit tank, Balloon Snare zip/lash,
# Gunk Gagster gag-lob puddle (Punchline fourth), Corrupted Oswald
# (finale betrayal chase — short post-victory consequence fight).
ARCHETYPE_INK = 0
ARCHETYPE_BRUTE = 1
ARCHETYPE_SNARE = 2
ARCHETYPE_GAGSTER = 3
ARCHETYPE_CORRUPT_OSWALD = 4
ARCHETYPE_STATS = {
    # Act 1 spine + Overlord P2 adds: ink-dash rush + close splat secondary
    # so swarm pressure has move identity (not default smack fodder).
    ARCHETYPE_INK: {
        'name': 'Ink Smudge',
        'hpScale': 1.0,
        'chaseSpeed': 9.0,
        # Engage from mid-range so the ink dash can rush the gap.
        'meleeRange': 5.8,
        'attackHitRange': 5.5,
        'attackNearMissRange': 6.5,
        'attackDamage': 2,
        'telegraphDelay': 0.55,
        'attackCooldown': 1.75,
        'actorScale': 1.08,
        'actorTint': (0.18, 0.06, 0.28, 1.0),
        # Swarm rush — dash then hit (default attackMove).
        'attackMove': 'ink_dash',
        'dashDist': 3.2,
        'dashHitRange': 5.5,
        'dashNearMissRange': 6.5,
        'dashDamage': 2,
        # Close secondary — purple ink splat AoE when already in their face.
        'splatMeleeRange': 3.2,
        'splatHitRange': 4.0,
        'splatNearMissRange': 5.0,
        'splatDamage': 3,
        'splatTelegraphDelay': 0.42,
        'splatCooldown': 1.55,
    },
    ARCHETYPE_BRUTE: {
        'name': 'Sludge Brute',
        'hpScale': 1.75,
        'chaseSpeed': 5.2,
        # Engage from hold-plant range so planted Brutes actually spit.
        'meleeRange': 7.6,
        # Land splash radius (projectile travel owns mid-range reach).
        'attackHitRange': 3.5,
        'attackNearMissRange': 5.0,
        'attackDamage': 4,
        'telegraphDelay': 0.9,
        'attackCooldown': 2.35,
        'actorScale': 1.38,
        'actorTint': (0.12, 0.28, 0.1, 1.0),
        # Real spit projectile (not instant long-range smack) + close slam.
        'attackMove': 'spit',
        'spitMaxRange': 11.0,
        'spitTravelSec': 0.32,
        'spitTrailTickSec': 0.1,
        'spitTrailRadius': 1.6,
        'spitTrailDamage': 1,
        # Tank secondary — heavy close slam when the toon is in their face.
        'slamMeleeRange': 4.2,
        'slamHitRange': 4.8,
        'slamNearMissRange': 5.8,
        'slamDamage': 5,
        'slamTelegraphDelay': 0.55,
        'slamCooldown': 2.0,
    },
    # Punchline zip-flier: fragile balloon that lashes with a rubber-hose string.
    ARCHETYPE_SNARE: {
        'name': 'Balloon Snare',
        'hpScale': 0.7,
        'chaseSpeed': 13.5,
        'meleeRange': 3.8,
        'attackHitRange': 7.2,  # string-lash reach
        'attackDamage': 2,
        'telegraphDelay': 0.38,
        'attackCooldown': 1.35,
        'actorScale': 0.82,
        'actorTint': (0.55, 0.22, 0.08, 1.0),
    },
    # Punchline gag-lobber: stands back, telegraphs a bounce-bomb, then
    # resolves a teal puddle trap at the target's wind-up position (AoE
    # land + short linger sludge hazard: tick DoT / slow while inside).
    ARCHETYPE_GAGSTER: {
        'name': 'Gunk Gagster',
        'hpScale': 1.15,
        'chaseSpeed': 7.4,
        'meleeRange': 8.5,  # lob engage — stands off like a gag thrower
        'attackHitRange': 5.0,  # puddle radius around lobbed landing
        'attackNearMissRange': 7.5,
        'attackDamage': 3,
        'telegraphDelay': 0.78,
        'attackCooldown': 2.15,
        'actorScale': 1.12,
        'actorTint': (0.06, 0.32, 0.38, 1.0),  # teal gunk
        'attackMove': 'gag_lob',
        # Lingering sludge after land — trap fantasy vs one-shot AoE.
        'puddleLingerSec': 2.5,
        'puddleLingerTickSec': 0.5,
        'puddleLingerTickDamage': 1,
        'puddleLingerSlowFactor': 0.55,
    },
    # Finale betrayal chase: trusted Oswald turns ink-corrupt — distinct
    # betrayal kit (lunge dash + close stain burst + shove), not smack reskin
    # / crimson Ink Smudge. Not Overlord phase combat; not a full new act.
    ARCHETYPE_CORRUPT_OSWALD: {
        'name': 'Corrupted Oswald',
        'hpScale': 1.35,
        'defaultHp': 48,
        'chaseSpeed': 12.2,
        # Engage from mid-range so the betrayal lunge can rush the gap.
        'meleeRange': 6.4,
        'attackHitRange': 5.2,
        'attackNearMissRange': 6.4,
        'attackDamage': 3,
        'telegraphDelay': 0.38,
        'attackCooldown': 1.55,
        'actorScale': 1.18,
        # Crimson-shadow tint — reads as betrayal stain vs street purple ink.
        'actorTint': (0.42, 0.08, 0.14, 1.0),
        # False-friend rush — dash then hit (default attackMove).
        'attackMove': 'betrayal_lunge',
        'lungeDashDist': 4.5,
        'lungeHitRange': 5.2,
        'lungeNearMissRange': 6.4,
        'lungeDamage': 3,
        # Close secondary — crimson stain burst AoE when already in his face.
        'burstMeleeRange': 3.6,
        'burstHitRange': 4.5,
        'burstNearMissRange': 5.6,
        'burstDamage': 4,
        'burstTelegraphDelay': 0.32,
        'burstCooldown': 1.25,
        # Hit shove — knock the toon away (opposite Balloon Snare yank).
        'shoveDist': 2.1,
    },
}


def normalizeArchetype(archetype):
    """Clamp unknown ids to Ink Smudge."""
    try:
        value = int(archetype)
    except (TypeError, ValueError):
        return ARCHETYPE_INK
    if value in ARCHETYPE_STATS:
        return value
    return ARCHETYPE_INK


def archetypeStats(archetypeId):
    return ARCHETYPE_STATS[normalizeArchetype(archetypeId)]


def archetypeDefaultHp(archetype):
    """Base HP before DistributedCorruptToonAI applies hpScale."""
    stats = archetypeStats(archetype)
    # Prefer explicit default when present; else use global base.
    if 'defaultHp' in stats:
        return int(stats['defaultHp'])
    return CORRUPT_TOON_DEFAULT_HP


def archetypeDefaultName(archetype):
    return str(archetypeStats(archetype).get('name', CORRUPT_TOON_DEFAULT_NAME))


ARCHETYPE_NAMES = {
    ARCHETYPE_INK: 'Ink Smudge',
    ARCHETYPE_BRUTE: 'Sludge Brute',
    ARCHETYPE_SNARE: 'Balloon Snare',
    ARCHETYPE_GAGSTER: 'Gunk Gagster',
    ARCHETYPE_CORRUPT_OSWALD: 'Corrupted Oswald',
}

# Defeating one corrupt toon reduces local pollution by this amount.
# Slice 3 reclaim loop will tune pack sizes against this contribution.
POLLUTION_PER_DEFEAT = 0.15

# Magic-word pollute/purify default step when no amount is given.
POLLUTION_STEP_DEFAULT = 0.25

# Chase / aggro / telegraphed melee (Depth D2).
AI_TICK_DT = 0.25
AGGRO_RANGE = 35.0
MELEE_RANGE = 4.5
ATTACK_HIT_RANGE = 5.5
# Planar radius for i-frame near-miss sparkle (outside hit, still "almost").
ATTACK_NEAR_MISS_RANGE = 8.0
CHASE_SPEED = 9.0
ATTACK_TELEGRAPH_DELAY = 0.55
ATTACK_DAMAGE = 2
ATTACK_COOLDOWN = 1.75
# Client death pop (~0.4s body + ~0.45s splat) must finish before AI delete.
DEFEAT_DELETE_DELAY = 0.95

# ---------------------------------------------------------------------------
# Archetype role AI — pack composition after combat starts.
#
# Wave scripts place Snare-front / Gagster lob / Brute rear, but every unit
# independently nearest-chasing collapses that intent into the same scrum.
# Role AI keeps street archetypes distinct during chase (not cream FX):
#   Smudge  → orbit / weave (circle dash-engage ring; pack splits by side)
#   Gagster → kite (hold lob ring / backpedal when pressed)
#   Brute   → hold (plant in spit range; sluggish close)
#   Snare   → flank (approach via perpendicular offset, then lash)
#   Oswald  → press / circle (aggressive close + mid-range circle for lunge)
#   Overlord → hold / circle (plant for rain/slam/surge; mid circle between
#              telegraphs — gated by finalePhase / ``_isOverlord()``, not
#              archetype id; shares ARCHETYPE_INK with Smudge)
# ROLE_AI_ENABLED = False restores legacy nearest-chase for all archetypes.
# Wired from DistributedCorruptToonAI.__roleMoveToward / __moveTowardXY.
# ---------------------------------------------------------------------------
ROLE_AI_ENABLED = True
ROLE_CHASE = 'chase'
ROLE_ORBIT = 'orbit'
ROLE_PRESS = 'press'
ROLE_CIRCLE = 'circle'
ROLE_KITE = 'kite'
ROLE_HOLD = 'hold'
ROLE_FLANK = 'flank'

# Ink Smudge orbit / weave — circle the dash-engage ring; packs split CW/CCW.
SMUDGE_ORBIT_PREFERRED = 5.6  # weave ring (at/under meleeRange 5.8 so dash fires)
SMUDGE_ORBIT_BAND = 1.1  # half-width comfort band around preferred
SMUDGE_ORBIT_CLOSE_DIST = 13.0  # beyond this, close toward ring before weaving
SMUDGE_ORBIT_WEAVE = 4.0  # tangential lead so the goal keeps them circling
SMUDGE_ORBIT_SPEED_SCALE = 1.08  # slight zip on the weave arc

# Corrupted Oswald press / circle — betrayal chase approach asymmetry.
# Far: snappy press toward the circle ring; mid: circle for angled lunge;
# close: press onto the toon for stain_burst (not Smudge orbit retreat).
OSWALD_PRESS_PREFERRED = 5.8  # circle ring (at/under meleeRange 6.4 so lunge fires)
OSWALD_PRESS_BAND = 1.2  # half-width comfort band around preferred
OSWALD_PRESS_CLOSE_DIST = 14.0  # beyond this, press toward ring before circling
OSWALD_PRESS_CIRCLE = 3.8  # tangential lead so the goal keeps him circling
OSWALD_PRESS_SPEED_SCALE = 1.18  # snappy betrayal press-in
OSWALD_CIRCLE_SPEED_SCALE = 1.10  # zip on the circle arc

# Ink Overlord hold / circle — climax approach between rain/slam/surge.
# Far: measured approach toward the hold ring; mid: circle for angled
# telegraph; in-band / close: hold plant (face toon) so rain/slam/surge
# still fire — not Smudge orbit retreat, not Oswald press-onto-toon.
# Preferred sits under P1 rain meleeRange (8.0) so engage still owns the hit.
OVERLORD_CIRCLE_PREFERRED = 6.6  # hold/circle ring (under P1 rain engage 8.0)
OVERLORD_CIRCLE_BAND = 1.2  # half-width comfort band around preferred
OVERLORD_CIRCLE_CLOSE_DIST = 15.0  # beyond this, approach toward ring before circling
OVERLORD_CIRCLE_LEAD = 4.0  # tangential lead so the goal keeps him circling
OVERLORD_APPROACH_SPEED_SCALE = 0.92  # measured close — not frantic nearest-chase
OVERLORD_CIRCLE_SPEED_SCALE = 1.06  # slight zip on the between-telegraph arc

# Gunk Gagster kite — stand off on a lob ring; retreat when the toon closes.
GAGSTER_KITE_PREFERRED = 9.5  # ring radius (near meleeRange 8.5)
GAGSTER_KITE_BAND = 1.4  # half-width comfort band around preferred
GAGSTER_KITE_RETREAT_SPEED_SCALE = 1.2  # snappier backpedal than lob approach

# Sludge Brute hold — plant once inside hold range; slow approach otherwise.
BRUTE_HOLD_RANGE = 7.8  # stop chasing (spit-ready plant; near meleeRange 7.6)
BRUTE_HOLD_CHASE_SPEED_SCALE = 0.55  # sluggish close so tank doesn't race Snare

# Balloon Snare flank — close via perpendicular offset, then engage for lash.
SNARE_FLANK_OFFSET = 5.5  # planar flank radius around the toon
SNARE_FLANK_CLOSE_DIST = 11.0  # beyond this, close in before committing to flank
SNARE_FLANK_SPEED_SCALE = 1.05  # slight zip on the flank arc


def archetypeCombatRole(archetype):
    """Return street / Oswald role-AI mode (orbit/press/kite/hold/flank).

    Ink Overlord (finalePhase ≥ 1) shares ``ARCHETYPE_INK`` with Smudge —
    callers use ``overlordCombatRole()`` when ``_isOverlord()``. Unknown ids
    clamp via normalizeArchetype.
    """
    if not ROLE_AI_ENABLED:
        return ROLE_CHASE
    aid = normalizeArchetype(archetype)
    if aid == ARCHETYPE_INK:
        return ROLE_ORBIT
    if aid == ARCHETYPE_CORRUPT_OSWALD:
        return ROLE_PRESS
    if aid == ARCHETYPE_GAGSTER:
        return ROLE_KITE
    if aid == ARCHETYPE_BRUTE:
        return ROLE_HOLD
    if aid == ARCHETYPE_SNARE:
        return ROLE_FLANK
    return ROLE_CHASE


def overlordCombatRole():
    """Return Overlord between-telegraph role (hold / circle).

    Distinct from Smudge ``ROLE_ORBIT`` despite shared ``ARCHETYPE_INK``.
    ``ROLE_AI_ENABLED = False`` restores legacy nearest-chase.
    """
    if not ROLE_AI_ENABLED:
        return ROLE_CHASE
    return ROLE_CIRCLE


def roleMoveGoal(role, sx, sy, tx, ty, preferred=None, band=None,
                 holdRange=None, flankOffset=None, flankCloseDist=None,
                 flankSide=1, weave=None, orbitCloseDist=None,
                 pressCircle=None, pressCloseDist=None,
                 circleLead=None, circleCloseDist=None):
    """Planar (gx, gy, action) for role-aware chase.

    ``action`` is one of ``chase`` / ``approach`` / ``retreat`` / ``hold`` /
    ``flank`` / ``orbit`` / ``press`` / ``circle``. ``hold`` means stay put
    (gx, gy == sx, sy). Default / unknown roles chase straight at the toon.
    """
    role = str(role or ROLE_CHASE)
    sx = float(sx)
    sy = float(sy)
    tx = float(tx)
    ty = float(ty)
    dx = sx - tx
    dy = sy - ty
    dist = (dx * dx + dy * dy) ** 0.5

    if role == ROLE_ORBIT:
        if preferred is None:
            preferred = SMUDGE_ORBIT_PREFERRED
        if band is None:
            band = SMUDGE_ORBIT_BAND
        if weave is None:
            weave = SMUDGE_ORBIT_WEAVE
        if orbitCloseDist is None:
            orbitCloseDist = SMUDGE_ORBIT_CLOSE_DIST
        preferred = max(0.5, float(preferred))
        band = max(0.0, float(band))
        weave = max(0.0, float(weave))
        orbitCloseDist = max(preferred, float(orbitCloseDist))
        side = 1.0 if float(flankSide) >= 0.0 else -1.0
        if dist < 1e-6:
            return (tx + preferred, ty, 'retreat')
        ux = dx / dist
        uy = dy / dist
        # Tangential weave direction (same left/right split as Snare flank).
        wx = (-uy) * side
        wy = (ux) * side
        if dist > orbitCloseDist:
            # Far: close toward preferred ring (not straight onto the toon).
            return (tx + ux * preferred, ty + uy * preferred, 'approach')
        # Goal on preferred ring, advanced along tangent (orbit / weave).
        gx = tx + ux * preferred + wx * weave
        gy = ty + uy * preferred + wy * weave
        rdx = gx - tx
        rdy = gy - ty
        rdist = (rdx * rdx + rdy * rdy) ** 0.5
        if rdist > 1e-6:
            gx = tx + rdx / rdist * preferred
            gy = ty + rdy / rdist * preferred
        if dist < preferred - band:
            return (gx, gy, 'retreat')
        return (gx, gy, 'orbit')

    if role == ROLE_PRESS:
        if preferred is None:
            preferred = OSWALD_PRESS_PREFERRED
        if band is None:
            band = OSWALD_PRESS_BAND
        if pressCircle is None:
            pressCircle = OSWALD_PRESS_CIRCLE
        if pressCloseDist is None:
            pressCloseDist = OSWALD_PRESS_CLOSE_DIST
        preferred = max(0.5, float(preferred))
        band = max(0.0, float(band))
        pressCircle = max(0.0, float(pressCircle))
        pressCloseDist = max(preferred, float(pressCloseDist))
        side = 1.0 if float(flankSide) >= 0.0 else -1.0
        if dist < 1e-6:
            # On top of the toon — keep pressing (stain_burst range).
            return (tx, ty, 'press')
        ux = dx / dist
        uy = dy / dist
        if dist < preferred - band:
            # Inside the circle band: press onto the toon for stain_burst.
            return (tx, ty, 'press')
        if dist > pressCloseDist:
            # Far: snappy press toward preferred circle ring.
            return (tx + ux * preferred, ty + uy * preferred, 'press')
        # Mid: circle on preferred ring (angled betrayal_lunge approach).
        wx = (-uy) * side
        wy = (ux) * side
        gx = tx + ux * preferred + wx * pressCircle
        gy = ty + uy * preferred + wy * pressCircle
        rdx = gx - tx
        rdy = gy - ty
        rdist = (rdx * rdx + rdy * rdy) ** 0.5
        if rdist > 1e-6:
            gx = tx + rdx / rdist * preferred
            gy = ty + rdy / rdist * preferred
        return (gx, gy, 'circle')

    if role == ROLE_CIRCLE:
        # Overlord hold / circle — plant in-band; circle mid; approach far.
        if preferred is None:
            preferred = OVERLORD_CIRCLE_PREFERRED
        if band is None:
            band = OVERLORD_CIRCLE_BAND
        if circleLead is None:
            circleLead = OVERLORD_CIRCLE_LEAD
        if circleCloseDist is None:
            circleCloseDist = OVERLORD_CIRCLE_CLOSE_DIST
        preferred = max(0.5, float(preferred))
        band = max(0.0, float(band))
        circleLead = max(0.0, float(circleLead))
        circleCloseDist = max(preferred, float(circleCloseDist))
        side = 1.0 if float(flankSide) >= 0.0 else -1.0
        if dist < 1e-6 or dist <= preferred + band:
            # In comfort band / on top of toon — hold plant for telegraph.
            return (sx, sy, 'hold')
        ux = dx / dist
        uy = dy / dist
        if dist > circleCloseDist:
            # Far: measured approach toward preferred hold ring.
            return (tx + ux * preferred, ty + uy * preferred, 'approach')
        # Mid: circle on preferred ring (angled rain/slam/surge approach).
        wx = (-uy) * side
        wy = (ux) * side
        gx = tx + ux * preferred + wx * circleLead
        gy = ty + uy * preferred + wy * circleLead
        rdx = gx - tx
        rdy = gy - ty
        rdist = (rdx * rdx + rdy * rdy) ** 0.5
        if rdist > 1e-6:
            gx = tx + rdx / rdist * preferred
            gy = ty + rdy / rdist * preferred
        return (gx, gy, 'circle')

    if role == ROLE_KITE:
        if preferred is None:
            preferred = GAGSTER_KITE_PREFERRED
        if band is None:
            band = GAGSTER_KITE_BAND
        preferred = max(0.5, float(preferred))
        band = max(0.0, float(band))
        if dist < 1e-6:
            return (tx + preferred, ty, 'retreat')
        ux = dx / dist
        uy = dy / dist
        gx = tx + ux * preferred
        gy = ty + uy * preferred
        if dist < preferred - band:
            return (gx, gy, 'retreat')
        if dist > preferred + band:
            return (gx, gy, 'approach')
        return (sx, sy, 'hold')

    if role == ROLE_HOLD:
        if holdRange is None:
            holdRange = BRUTE_HOLD_RANGE
        holdRange = max(0.5, float(holdRange))
        if dist <= holdRange:
            return (sx, sy, 'hold')
        return (tx, ty, 'approach')

    if role == ROLE_FLANK:
        if flankOffset is None:
            flankOffset = SNARE_FLANK_OFFSET
        if flankCloseDist is None:
            flankCloseDist = SNARE_FLANK_CLOSE_DIST
        flankOffset = max(0.5, float(flankOffset))
        flankCloseDist = max(flankOffset, float(flankCloseDist))
        side = 1.0 if float(flankSide) >= 0.0 else -1.0
        # Far out: close first so flank doesn't orbit at aggro edge.
        if dist > flankCloseDist or dist < 1e-6:
            return (tx, ty, 'approach')
        # Perpendicular to toon→self: (-dy, dx) / (dy, -dx).
        ux = dx / dist
        uy = dy / dist
        gx = tx + (-uy) * side * flankOffset
        gy = ty + (ux) * side * flankOffset
        return (gx, gy, 'flank')

    # Plain chase (disabled / unknown).
    return (tx, ty, 'chase')


def roleMoveSpeedScale(role, action=None):
    """Chase-speed multiplier for a role action (1.0 = archetype chaseSpeed)."""
    role = str(role or ROLE_CHASE)
    action = str(action or '')
    if role == ROLE_ORBIT:
        return float(SMUDGE_ORBIT_SPEED_SCALE)
    if role == ROLE_PRESS:
        if action == 'circle':
            return float(OSWALD_CIRCLE_SPEED_SCALE)
        return float(OSWALD_PRESS_SPEED_SCALE)
    if role == ROLE_CIRCLE:
        if action == 'circle':
            return float(OVERLORD_CIRCLE_SPEED_SCALE)
        if action == 'approach':
            return float(OVERLORD_APPROACH_SPEED_SCALE)
        return 1.0
    if role == ROLE_KITE and action == 'retreat':
        return float(GAGSTER_KITE_RETREAT_SPEED_SCALE)
    if role == ROLE_HOLD:
        return float(BRUTE_HOLD_CHASE_SPEED_SCALE)
    if role == ROLE_FLANK:
        return float(SNARE_FLANK_SPEED_SCALE)
    return 1.0


def snareFlankSide(doId):
    """Stable left/right flank / orbit / press / Overlord-circle side from doId.

    Even doIds weave / flank / circle one way; odd the other, so packs split
    around the toon instead of stacking on one shoulder.
    """
    try:
        return 1 if (int(doId) % 2 == 0) else -1
    except (TypeError, ValueError):
        return 1

# Visual ink / sickly palette (not classic cog gray).
CORRUPT_TINT = (0.22, 0.05, 0.32, 0.92)
CORRUPT_TINT_HOT = (0.55, 0.12, 0.75, 1.0)
CORRUPT_ARM_TINT = (0.12, 0.02, 0.18, 0.78)
# DNA Actor base multiply — keeps silhouette readable as ink-black toon.
CORRUPT_ACTOR_TINT = (0.18, 0.06, 0.28, 1.0)
CORRUPT_ACTOR_SCALE = 1.08
CORRUPT_FOG_COLOR = (0.18, 0.12, 0.22)
# Peak exponential fog density at pollution 1.0 (readable street ink haze).
CORRUPT_FOG_EXP_MAX = 0.022

# Density ramp: presented fog/haze lerps toward zone pollution as packs rise/clear.
# Ease-in curve (>1) keeps low corruption mild and high corruption thick.
POLLUTION_FOG_DENSITY_CURVE = 1.35
POLLUTION_FOG_RAMP_SEC = 0.55
POLLUTION_FOG_CLEAR_SEC = 0.9
POLLUTION_FOG_SNAP_DELTA = 0.02
# Fullscreen aspect2d ink wash (behind purity burst bins 56–60).
POLLUTION_HAZE_ALPHA_MAX = 0.30
POLLUTION_HAZE_BIN = 25

# Incomplete-reclaim re-creep: neighborhoods fight back if a street reclaim is
# left unfinished. Secured / pure streets stay pure; contested streets slowly
# re-ink toward POLLUTION_RECREEP_CAP (not full black — leave room to reclaim).
# POLLUTION_RECREEP_ENABLED = False freezes auto re-ink only.
# Street status is AI bookkeeping (PollutionManagerAI); client presentation
# still follows setZonePollution / fog ramp / street audio.
STREET_SECURED = 0       # fully reclaimed / never stained — no auto re-ink
STREET_RECLAIMING = 1    # active reclaim — pause re-creep while packs fight
STREET_CONTESTED = 2     # unfinished reclaim — slow rubber-hose re-ink
STREET_STATUS_NAMES = {
    STREET_SECURED: 'secured',
    STREET_RECLAIMING: 'reclaiming',
    STREET_CONTESTED: 'contested',
}
POLLUTION_RECREEP_ENABLED = True
POLLUTION_RECREEP_TICK_SEC = 2.5
POLLUTION_RECREEP_PER_TICK = 0.04
POLLUTION_RECREEP_CAP = 0.85
# One-shot rubber-hose whisper when ink first seeps after a bail-out.
POLLUTION_RECREEP_MSG = (
    "Whoa — that ink's creeping back! Finish the reclaim before this "
    'street goes goopy again!'
)
# After a finished reclaim, PollutionManagerAI purity-locks the street so
# setPollution rises / re-creep cannot undo full purity. Ambient never-stained
# streets stay SECURED without this lock (still accept ~pollute). Toggle
# STREET_PURITY_LOCK_ENABLED = False soft-opens rises on locked streets only;
# re-creep still skips SECURED / RECLAIMING via streetAllowsRecreep.
STREET_PURITY_LOCK_ENABLED = True
STREET_PURITY_LOCK_MSG = (
    "Street's secured — that ink can't creep back!"
)
# Finished-reclaim purity locks persist across AI restart via thin JSON
# under air.dataFolder (PollutionSecuredSave). Without this, secured
# Loopy/Punchline reopen while campaign progress still says cleared.
# POLLUTION_SECURED_PERSIST_ENABLED = False keeps process-memory locks only.
POLLUTION_SECURED_PERSIST_ENABLED = True
POLLUTION_SECURED_FILENAME = 'pollution_secured.json'

# Purity-complete fog cream dissolve — sunny cream/pastel lift of street fog
# when purityRestoreFx fires. Matches POLLUTION_FOG_CLEAR_SEC density ramp
# (#38) + StreetSparkle chip/fleck patterns. Not ink; no KH branding.
# FOG_CREAM_DISSOLVE_ENABLED = False drops cream tint + overlay only;
# density clear ramp still runs.
FOG_CREAM_DISSOLVE_ENABLED = True
FOG_CREAM_DISSOLVE_SEC = POLLUTION_FOG_CLEAR_SEC
FOG_CREAM_DISSOLVE_COLOR = (1.0, 0.97, 0.82)  # sunny cream fog tint
FOG_CREAM_DISSOLVE_HAZE_PEAK = 0.20
FOG_CREAM_DISSOLVE_BIN = 26  # above ink haze (25), below street sparkle (50)
FOG_CREAM_DISSOLVE_ORIGIN = (0.0, 0.0, -0.28)
FOG_CREAM_DISSOLVE_SHIMMER_IN_SEC = 0.08
FOG_CREAM_DISSOLVE_SHIMMER_HOLD_SEC = 0.22
FOG_CREAM_DISSOLVE_SHIMMER_OUT_SEC = 0.58
FOG_CREAM_DISSOLVE_FLECK_COUNT = 14
FOG_CREAM_DISSOLVE_FLECK_SIZE = 0.024
FOG_CREAM_DISSOLVE_FLECK_RISE = 0.78
FOG_CREAM_DISSOLVE_FLECK_SPREAD = 1.40
FOG_CREAM_DISSOLVE_FLECK_SEC = 0.68
FOG_CREAM_DISSOLVE_FLECK_COLOR = (1.0, 0.98, 0.72, 0.95)
FOG_CREAM_DISSOLVE_FLECK_END_COLOR = (1.0, 0.94, 0.55, 0.0)
FOG_CREAM_DISSOLVE_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.95),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.9),    # soft peach pastel
    (0.98, 0.94, 0.88, 0.88),  # warm parchment
)

# Purity-complete hood corruption tint cream fade — PollutionPropTint geom
# colorScale lifts sunny cream/pastel when purityRestoreFx fires (hood tint
# #13). Matches FOG_CREAM_DISSOLVE_* timing / cream palette (#100). Not ink;
# no KH branding. HOOD_TINT_CREAM_FADE_ENABLED = False snaps clear like before.
HOOD_TINT_CREAM_FADE_ENABLED = True
HOOD_TINT_CREAM_FADE_SEC = POLLUTION_FOG_CLEAR_SEC
HOOD_TINT_CREAM_FADE_COLOR = FOG_CREAM_DISSOLVE_COLOR  # sunny cream geom lift
HOOD_TINT_CREAM_FADE_HAZE_PEAK = 0.12  # soft veil under fog dissolve (26)
HOOD_TINT_CREAM_FADE_BIN = 27  # above fog dissolve (26), below street wash (28)
HOOD_TINT_CREAM_FADE_ORIGIN = (0.0, 0.0, -0.18)
HOOD_TINT_CREAM_FADE_SHIMMER_IN_SEC = 0.07
HOOD_TINT_CREAM_FADE_SHIMMER_HOLD_SEC = 0.18
HOOD_TINT_CREAM_FADE_SHIMMER_OUT_SEC = 0.55
HOOD_TINT_CREAM_FADE_FLECK_COUNT = 8
HOOD_TINT_CREAM_FADE_FLECK_SIZE = 0.018
HOOD_TINT_CREAM_FADE_FLECK_RISE = 0.55
HOOD_TINT_CREAM_FADE_FLECK_SPREAD = 1.10
HOOD_TINT_CREAM_FADE_FLECK_SEC = 0.58
HOOD_TINT_CREAM_FADE_FLECK_COLOR = (1.0, 0.98, 0.78, 0.88)
HOOD_TINT_CREAM_FADE_FLECK_END_COLOR = (1.0, 0.95, 0.62, 0.0)
HOOD_TINT_CREAM_FADE_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.90),  # sunny cream
    (1.0, 0.94, 0.70, 0.86),  # butter pastel
    (1.0, 0.90, 0.80, 0.84),  # soft peach
)

# Street-entry rubber-hose ink vignette (PlayEntry on polluted ACTS streets).
# Edge darken flashes in, then fades as the tip bar appears — not a KH sting.
ENTRY_VIGNETTE_IN_SEC = 0.10
ENTRY_VIGNETTE_HOLD_SEC = 0.16
ENTRY_VIGNETTE_OUT_SEC = 0.55
ENTRY_VIGNETTE_TIP_DELAY_SEC = 0.22
ENTRY_VIGNETTE_TIP_FADE_SEC = 0.38
ENTRY_VIGNETTE_PEAK_ALPHA = 0.78
ENTRY_VIGNETTE_EDGE = 0.42  # strip thickness in aspect2d units
ENTRY_VIGNETTE_BIN = 48  # above haze (25), below handoff/celebration (60+)
# Minimum presented pollution to fire the entry vignette (skip clean streets).
ENTRY_VIGNETTE_MIN_POLLUTION = 0.08
# Fallback ink when hood fog bias is unavailable.
ENTRY_VIGNETTE_INK = (0.06, 0.02, 0.10, 1.0)

# Per-street ambient corruption look (branch zone ids).
# fog: RGB base; fogExpScale: density multiplier vs CORRUPT_FOG_EXP_MAX
# gradeDrop: how hard render RGB falls with pollution (higher = darker channel)
# propTint: multiply applied to street geom under pollutionPropTint
# Default / Loopy = purple ink wash.
HOOD_POLLUTION_BIAS = {
    # Loopy Lane — classic purple ink fog.
    2200: {
        'id': 'loopy',
        'fog': (0.18, 0.12, 0.22),
        'fogExpScale': 1.0,
        'gradeDrop': (0.42, 0.50, 0.28),
        'propTint': (0.72, 0.62, 0.85),
    },
    # Punchline Place — swampy sludge / gag-gunk green-brown.
    2300: {
        'id': 'punchline',
        'fog': (0.16, 0.20, 0.10),
        'fogExpScale': 1.12,
        'gradeDrop': (0.38, 0.28, 0.48),
        'propTint': (0.78, 0.82, 0.58),
    },
    # Silly Street — hot magenta / black-ink finale bias.
    2100: {
        'id': 'silly',
        'fog': (0.24, 0.06, 0.18),
        'fogExpScale': 1.22,
        'gradeDrop': (0.30, 0.55, 0.35),
        'propTint': (0.88, 0.55, 0.78),
    },
}

_DEFAULT_HOOD_BIAS = HOOD_POLLUTION_BIAS[2200]

# Telegraph / impact presentation (client AV punch; AI timings unchanged).
# Ink Smudge = purple melee; Sludge Brute = green spit; Balloon Snare = amber
# lash; Gunk Gagster = teal gag-lob puddle; Corrupted Oswald = betrayal crimson
# lunge (not Smudge purple fallthrough).
TELEGRAPH_CHARGE_COLOR = (2.15, 0.25, 2.4, 1.0)
TELEGRAPH_HOLD_COLOR = (1.55, 0.2, 1.85, 1.0)

# Corrupted Oswald telegraph body charge — hot betrayal crimson (not purple).
# Client AV only; AI timings unchanged. Distinct from TELEGRAPH_CHARGE_COLOR.
OSWALD_TELEGRAPH_CHARGE_COLOR = (2.25, 0.35, 0.55, 1.0)
OSWALD_TELEGRAPH_HOLD_COLOR = (1.65, 0.22, 0.38, 1.0)
# Wider crouch → tall thin lunge stretch (betrayal_lunge wind-up read).
OSWALD_TELEGRAPH_SQUASH = (2.05, 1.55, 0.38)
OSWALD_TELEGRAPH_MID = (1.75, 1.35, 0.48)
OSWALD_TELEGRAPH_STRETCH = (0.55, 0.85, 1.95)

# Corrupted Oswald telegraph stain-lunge pop — short rubber-hose crimson charge
# on announceAttackTelegraph (client only). Distinct from Smudge purple fist,
# Brute spit, Snare string, Gagster puddle. No cream deepen.
OSWALD_TELEGRAPH_STAIN_LOOK = {
    'id': 'betrayal-crimson-lunge',
    'lift': 2.25,
    'scale': 1.05,
    'peakAlpha': 0.97,
    'fadeInSec': 0.04,
    'holdSec': 0.14,
    'fadeOutSec': 0.2,
    # Forward-lean lunge: flatter squash → taller forward stretch.
    'squash': (1.95, 0.95, 0.32),
    'stretch': (0.58, 1.05, 2.05),
    'squashSec': 0.045,
    'stretchSec': 0.12,
    'settleSec': 0.12,
    'wobbleDeg': 18.0,
    'fistHalf': 0.34,
    'rimScale': 1.36,
    'hotHalf': 0.12,
    'fistColor': (0.88, 0.16, 0.24, 1.0),
    'rimColor': (1.35, 0.42, 0.48, 1.0),
    'flashColor': (1.55, 0.38, 0.45, 1.0),
    'smearCount': 5,
    'smearHalf': 0.1,
    'smearSec': 0.26,
    'smearSpread': 1.05,
    'smearColor': (0.95, 0.22, 0.32, 0.92),
    'binSort': 43,
}

# Ink Smudge telegraph ink-fist pop — short rubber-hose purple melee charge on
# announceAttackTelegraph (client only). Distinct from shared TELEGRAPH_INK_DRIP_*
# drips and from Brute spit / Snare string silhouettes: punch-fist ink blob.
SMUDGE_TELEGRAPH_INK_LOOK = {
    'id': 'purple-ink-fist',
    'lift': 2.2,
    'scale': 1.0,
    'peakAlpha': 0.96,
    'fadeInSec': 0.04,
    'holdSec': 0.15,
    'fadeOutSec': 0.22,
    'squash': (1.75, 1.0, 0.38),
    'stretch': (0.7, 1.0, 1.85),
    'squashSec': 0.05,
    'stretchSec': 0.11,
    'settleSec': 0.13,
    'wobbleDeg': 14.0,
    'fistHalf': 0.36,
    'rimScale': 1.32,
    'hotHalf': 0.13,
    'fistColor': (0.55, 0.18, 0.95, 1.0),
    'rimColor': (1.15, 0.45, 1.55, 1.0),
    'flashColor': (1.35, 0.45, 1.7, 1.0),
    'smearCount': 4,
    'smearHalf': 0.11,
    'smearSec': 0.28,
    'smearSpread': 0.95,
    'smearColor': (0.75, 0.28, 1.15, 0.9),
    'binSort': 42,
}

# Ink Smudge hit/death ink splash — cheap rubber-hose purple splash for swarm
# readability (client only). Composes with SmudgeInkTelegraphFx / CorruptDeathPopFx
# / IdleInkDripFx palettes via SmudgeInkSplashFx.smudgeInkSplashLook. Hit is the
# cheap pack-scan cue; death layers a slightly larger splash with DeathPop.
# Hit path also arms SmudgeHitCreamSplashFx (cream splash + aftershock — see
# SMUDGE_HIT_CREAM_SPLASH_* / SMUDGE_HIT_CREAM_AFTERSHOCK_* below) and
# SmudgeHitCreamWashFx (soft cream wash — see SMUDGE_HIT_CREAM_WASH_* below).
SMUDGE_INK_SPLASH_LOOK = {
    'hit': {
        'id': 'smudge-hit-splash',
        'lift': 2.05,
        'peakAlpha': 0.94,
        'splatHalf': 0.26,
        'splatPeak': 1.55,
        'splatSec': 0.18,
        'rimScale': 1.26,
        'smearCount': 3,
        'smearHalf': 0.09,
        'smearSec': 0.2,
        'smearSpread': 0.75,
        'fleckCount': 2,
        'fleckHalf': 0.11,
        'fleckDist': 1.05,
        'fleckLift': 0.4,
        'fleckSec': 0.22,
        'dripCount': 1,
        'dripHalf': 0.08,
        'dripSpread': 0.22,
        'dripFall': 0.7,
        'dripSec': 0.32,
        'dripStagger': 0.03,
        'binSort': 45,
    },
    'death': {
        'id': 'smudge-death-splash',
        'lift': 1.55,
        'peakAlpha': 0.97,
        'splatHalf': 0.38,
        'splatPeak': 2.05,
        'splatSec': 0.26,
        'rimScale': 1.35,
        'smearCount': 4,
        'smearHalf': 0.12,
        'smearSec': 0.28,
        'smearSpread': 1.15,
        'fleckCount': 4,
        'fleckHalf': 0.16,
        'fleckDist': 1.75,
        'fleckLift': 0.7,
        'fleckSec': 0.3,
        'dripCount': 2,
        'dripHalf': 0.1,
        'dripSpread': 0.35,
        'dripFall': 1.05,
        'dripSec': 0.42,
        'dripStagger': 0.04,
        'binSort': 46,
    },
}

# Corrupted Oswald hit/death betrayal splash — cheap rubber-hose crimson splash
# so tagged/popped Oswald reads as twist fight, not street Smudge purple
# (client only). Composes with OswaldBetrayalTelegraphFx / CorruptDeathPopFx
# / IdleInkDripFx palettes via OswaldBetrayalSplashFx.oswaldBetrayalSplashLook.
# No cream deepen — ink/stain AV only.
OSWALD_BETRAYAL_SPLASH_LOOK = {
    'hit': {
        'id': 'oswald-hit-splash',
        'lift': 2.15,
        'peakAlpha': 0.95,
        'splatHalf': 0.3,
        'splatPeak': 1.7,
        'splatSec': 0.2,
        'rimScale': 1.3,
        'smearCount': 4,
        'smearHalf': 0.1,
        'smearSec': 0.22,
        'smearSpread': 0.9,
        'fleckCount': 3,
        'fleckHalf': 0.12,
        'fleckDist': 1.2,
        'fleckLift': 0.5,
        'fleckSec': 0.24,
        'dripCount': 2,
        'dripHalf': 0.09,
        'dripSpread': 0.28,
        'dripFall': 0.85,
        'dripSec': 0.34,
        'dripStagger': 0.03,
        'binSort': 45,
        # Explicit crimson — do not inherit Smudge purple defaults.
        'splatColor': (0.92, 0.22, 0.3, 1.0),
        'rimColor': (1.35, 0.4, 0.48, 1.0),
        'smearColor': (0.95, 0.25, 0.35, 0.92),
        'fleckColor': (0.78, 0.14, 0.22, 0.95),
        'dripColor': (0.72, 0.12, 0.18, 0.95),
        'streakColor': (1.05, 0.35, 0.42, 0.9),
    },
    'death': {
        'id': 'oswald-death-splash',
        'lift': 1.6,
        'peakAlpha': 0.98,
        'splatHalf': 0.42,
        'splatPeak': 2.2,
        'splatSec': 0.28,
        'rimScale': 1.38,
        'smearCount': 5,
        'smearHalf': 0.13,
        'smearSec': 0.3,
        'smearSpread': 1.25,
        'fleckCount': 5,
        'fleckHalf': 0.16,
        'fleckDist': 1.9,
        'fleckLift': 0.8,
        'fleckSec': 0.32,
        'dripCount': 3,
        'dripHalf': 0.11,
        'dripSpread': 0.4,
        'dripFall': 1.15,
        'dripSec': 0.44,
        'dripStagger': 0.04,
        'binSort': 46,
        'splatColor': (0.95, 0.2, 0.28, 1.0),
        'rimColor': (1.45, 0.38, 0.45, 1.0),
        'smearColor': (1.0, 0.28, 0.36, 0.94),
        'fleckColor': (0.72, 0.14, 0.2, 0.95),
        'dripColor': (0.68, 0.1, 0.16, 0.95),
        'streakColor': (1.1, 0.32, 0.4, 0.92),
    },
}

# Sludge Brute hit/death sludge splash — cheap rubber-hose green splash so
# tagged/popped Brutes stay scannable (client only). Composes with
# BruteSpitTelegraphFx / CorruptDeathPopFx / IdleInkDripFx palettes via
# BruteSludgeSplashFx.bruteSludgeSplashLook. Hit is the cheap scan cue;
# death layers a slightly larger splash with DeathPop. Slightly bulkier than
# SMUDGE_INK_SPLASH_LOOK to match Brute silhouette.
BRUTE_SLUDGE_SPLASH_LOOK = {
    'hit': {
        'id': 'brute-hit-splash',
        'lift': 2.25,
        'peakAlpha': 0.95,
        'splatHalf': 0.32,
        'splatPeak': 1.7,
        'splatSec': 0.2,
        'rimScale': 1.28,
        'smearCount': 3,
        'smearHalf': 0.11,
        'smearSec': 0.22,
        'smearSpread': 0.9,
        'fleckCount': 3,
        'fleckHalf': 0.13,
        'fleckDist': 1.25,
        'fleckLift': 0.35,
        'fleckSec': 0.24,
        'dripCount': 2,
        'dripHalf': 0.1,
        'dripSpread': 0.28,
        'dripFall': 0.85,
        'dripSec': 0.36,
        'dripStagger': 0.03,
        'binSort': 45,
    },
    'death': {
        'id': 'brute-death-splash',
        'lift': 1.75,
        'peakAlpha': 0.98,
        'splatHalf': 0.45,
        'splatPeak': 2.25,
        'splatSec': 0.28,
        'rimScale': 1.38,
        'smearCount': 4,
        'smearHalf': 0.14,
        'smearSec': 0.3,
        'smearSpread': 1.3,
        'fleckCount': 5,
        'fleckHalf': 0.18,
        'fleckDist': 2.0,
        'fleckLift': 0.65,
        'fleckSec': 0.32,
        'dripCount': 3,
        'dripHalf': 0.12,
        'dripSpread': 0.42,
        'dripFall': 1.2,
        'dripSec': 0.46,
        'dripStagger': 0.04,
        'binSort': 46,
    },
}

# Balloon Snare hit/death string-snap splash — cheap rubber-hose amber splash
# so tagged/popped Snares stay scannable (client only). Composes with
# BalloonSnareTelegraphFx / CorruptDeathPopFx / IdleInkDripFx palettes via
# SnareStringSnapSplashFx.snareStringSnapSplashLook. Hit is the cheap scan
# cue; death layers a slightly larger splash with DeathPop. Snappier / thinner
# than SMUDGE_INK_SPLASH_LOOK to match fragile zip-flier silhouette; horizontal
# smear bias reads as a rubber string break (not ink blob / sludge gob).
SNARE_STRING_SNAP_SPLASH_LOOK = {
    'hit': {
        'id': 'snare-hit-splash',
        'lift': 1.95,
        'peakAlpha': 0.94,
        'splatHalf': 0.24,
        'splatPeak': 1.5,
        'splatSec': 0.16,
        'rimScale': 1.3,
        'smearCount': 3,
        'smearHalf': 0.08,
        'smearSec': 0.18,
        'smearSpread': 0.95,
        'fleckCount': 2,
        'fleckHalf': 0.1,
        'fleckDist': 1.15,
        'fleckLift': 0.45,
        'fleckSec': 0.2,
        'dripCount': 1,
        'dripHalf': 0.07,
        'dripSpread': 0.26,
        'dripFall': 0.72,
        'dripSec': 0.3,
        'dripStagger': 0.03,
        'binSort': 45,
    },
    'death': {
        'id': 'snare-death-splash',
        'lift': 1.4,
        'peakAlpha': 0.97,
        'splatHalf': 0.36,
        'splatPeak': 2.0,
        'splatSec': 0.24,
        'rimScale': 1.36,
        'smearCount': 4,
        'smearHalf': 0.11,
        'smearSec': 0.26,
        'smearSpread': 1.25,
        'fleckCount': 4,
        'fleckHalf': 0.14,
        'fleckDist': 1.85,
        'fleckLift': 0.75,
        'fleckSec': 0.28,
        'dripCount': 2,
        'dripHalf': 0.09,
        'dripSpread': 0.38,
        'dripFall': 1.0,
        'dripSec': 0.4,
        'dripStagger': 0.04,
        'binSort': 46,
    },
}

# Ink Overlord hit/death magenta ink splash — cheap rubber-hose magenta /
# crimson splash so tagged/popped Overlord reads as boss, not street Smudge
# (client only). Composes with OverlordTelegraphCrownFx /
# OverlordPhaseInkRainFx / CorruptDeathPopFx / IdleInkDripFx palettes via
# OverlordMagentaInkSplashFx.overlordMagentaInkSplashLook; phase charge
# retints P1 magenta vs P2 crimson. Bulkier than SMUDGE_INK_SPLASH_LOOK /
# BRUTE_SLUDGE_SPLASH_LOOK to match boss silhouette. Hit is the cheap scan
# cue; death layers a slightly larger splash with DeathPop.
OVERLORD_MAGENTA_INK_SPLASH_LOOK = {
    'hit': {
        'id': 'overlord-hit-splash',
        'lift': 2.55,
        'peakAlpha': 0.96,
        'splatHalf': 0.36,
        'splatPeak': 1.85,
        'splatSec': 0.22,
        'rimScale': 1.32,
        'smearCount': 4,
        'smearHalf': 0.12,
        'smearSec': 0.24,
        'smearSpread': 1.05,
        'fleckCount': 4,
        'fleckHalf': 0.15,
        'fleckDist': 1.55,
        'fleckLift': 0.55,
        'fleckSec': 0.26,
        'dripCount': 2,
        'dripHalf': 0.1,
        'dripSpread': 0.34,
        'dripFall': 0.95,
        'dripSec': 0.38,
        'dripStagger': 0.03,
        'binSort': 46,
    },
    'death': {
        'id': 'overlord-death-splash',
        'lift': 2.05,
        'peakAlpha': 0.98,
        'splatHalf': 0.52,
        'splatPeak': 2.45,
        'splatSec': 0.3,
        'rimScale': 1.4,
        'smearCount': 5,
        'smearHalf': 0.15,
        'smearSec': 0.32,
        'smearSpread': 1.45,
        'fleckCount': 6,
        'fleckHalf': 0.2,
        'fleckDist': 2.25,
        'fleckLift': 0.85,
        'fleckSec': 0.34,
        'dripCount': 3,
        'dripHalf': 0.13,
        'dripSpread': 0.48,
        'dripFall': 1.35,
        'dripSec': 0.48,
        'dripStagger': 0.04,
        'binSort': 47,
    },
}

# Soft cream wash pulse after Overlord magenta ink splash (hit only) —
# aspect2d veil after OverlordMagentaInkSplashFx (#88) smack (client only).
# Matches CorruptTelegraphCreamWashFx (#157) / CorruptSilhouetteCreamWashFx
# (#153) / CorruptDeathCreamWashFx (#119) two-beat grammar. Delay composed
# via OverlordHitCreamWashFx.overlordHitCreamWashLook →
# overlordMagentaInkSplashLook('hit'). Soft cream/pastel contrast against
# magenta / crimson ink. OVERLORD_HIT_CREAM_WASH_ENABLED = False drops wash
# only (magenta splash stays). Death path keeps splash + death cream wash.
OVERLORD_HIT_CREAM_WASH_ENABLED = True
OVERLORD_HIT_CREAM_WASH_DELAY_SEC = 0.16  # fallback; look prefers splash compose
OVERLORD_HIT_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
OVERLORD_HIT_CREAM_WASH_PEAK = 0.08  # quieter than death (0.14) / melee (0.10);
# above telegraph (0.065) so boss hit reads against magenta ink
OVERLORD_HIT_CREAM_WASH_MID = 0.045
OVERLORD_HIT_CREAM_WASH_IN_SEC = 0.06
OVERLORD_HIT_CREAM_WASH_PULSE_SEC = 0.10
OVERLORD_HIT_CREAM_WASH_HOLD_SEC = 0.08
OVERLORD_HIT_CREAM_WASH_OUT_SEC = 0.38
OVERLORD_HIT_CREAM_WASH_BIN = 40  # soft veil under magenta splash (46)
OVERLORD_HIT_CREAM_WASH_LOOK = {
    'id': 'overlord-hit-cream-wash',
    # delaySec composed with overlordMagentaInkSplashLook('hit') when played.
    'delaySec': OVERLORD_HIT_CREAM_WASH_DELAY_SEC,
    'delayScale': 0.72,
    'color': OVERLORD_HIT_CREAM_WASH_COLOR,
    'peak': OVERLORD_HIT_CREAM_WASH_PEAK,
    'mid': OVERLORD_HIT_CREAM_WASH_MID,
    'inSec': OVERLORD_HIT_CREAM_WASH_IN_SEC,
    'pulseSec': OVERLORD_HIT_CREAM_WASH_PULSE_SEC,
    'holdSec': OVERLORD_HIT_CREAM_WASH_HOLD_SEC,
    'outSec': OVERLORD_HIT_CREAM_WASH_OUT_SEC,
    'binSort': OVERLORD_HIT_CREAM_WASH_BIN,
}

# Cream splash + delayed cream aftershock on Ink Smudge hit / splash
# (after purple SmudgeInkSplashFx #75). Sunny cream / pastel contrast against
# purple ink so basic corrupt packs read juicier. Deepened mid-body hit
# juice beyond #259: juicier splat/flecks + thicker radial cream hose smears
# (SmudgeInkSplashFx punch-smear cousin) + wider settle aftershock —
# distinct from Snare whip (#269) / Brute drip (#264) / Gunk bloom (#276).
# Same residual grammar as TELEGRAPH_CREAM_WARN_AFTERSHOCK_*. Client only.
# No keyblades / KH branding.
# SMUDGE_HIT_CREAM_SPLASH_ENABLED = False drops splash + aftershock.
# SMUDGE_HIT_CREAM_AFTERSHOCK_ENABLED = False drops aftershock only.
# SMUDGE_HIT_CREAM_SPLASH_SMEAR_ENABLED = False drops hose smears only.
SMUDGE_HIT_CREAM_SPLASH_ENABLED = True
SMUDGE_HIT_CREAM_SPLASH_DELAY_SEC = 0.06  # fallback; look prefers purple compose
SMUDGE_HIT_CREAM_SPLASH_BIN = 46  # above purple ink splash (45)
SMUDGE_HIT_CREAM_SPLASH_COLOR = (1.0, 0.97, 0.82, 0.98)  # sunny cream
SMUDGE_HIT_CREAM_SPLASH_RIM_COLOR = (1.0, 0.98, 0.88, 0.8)
SMUDGE_HIT_CREAM_SPLASH_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.94),  # sunny cream
    (1.0, 0.96, 0.62, 0.88),  # butter
    (1.0, 0.9, 0.78, 0.84),   # soft peach pastel
)
# Radial cream hose smears — mid-body punch-smear readability (not Snare
# horizontal whip / Brute vertical drip / Gunk flat puddle bloom).
SMUDGE_HIT_CREAM_SPLASH_SMEAR_ENABLED = True
SMUDGE_HIT_CREAM_SPLASH_SMEAR_COUNT = 4  # thicker radial hose vs #259 (3)
SMUDGE_HIT_CREAM_SPLASH_SMEAR_HALF = 0.12
SMUDGE_HIT_CREAM_SPLASH_SMEAR_SPREAD = 1.12
SMUDGE_HIT_CREAM_SPLASH_SMEAR_SEC = 0.25
SMUDGE_HIT_CREAM_SPLASH_SMEAR_PEAK_ALPHA = 0.94
SMUDGE_HIT_CREAM_SPLASH_SMEAR_COLOR = (1.0, 0.97, 0.84, 0.94)
SMUDGE_HIT_CREAM_SPLASH_LOOK = {
    'id': 'smudge-hit-cream-splash',
    # lift / delaySec composed with smudgeInkSplashLook('hit') when played.
    'lift': 2.05,
    'delaySec': SMUDGE_HIT_CREAM_SPLASH_DELAY_SEC,
    'delayScale': 0.28,
    'peakAlpha': 0.98,
    'splatHalf': 0.34,  # juicier mid-body core vs #259 (0.3)
    'splatPeak': 1.88,
    'splatSec': 0.19,
    'rimScale': 1.42,
    'splatColor': SMUDGE_HIT_CREAM_SPLASH_COLOR,
    'rimColor': SMUDGE_HIT_CREAM_SPLASH_RIM_COLOR,
    'fleckCount': 7,  # deepened vs #259 (6); radial pack spray
    'fleckHalf': 0.12,
    'fleckDist': 1.28,
    'fleckLift': 0.55,  # taller mid-body spray (vs Snare string-lash height)
    'fleckSec': 0.26,
    'fleckColors': SMUDGE_HIT_CREAM_SPLASH_FLECK_COLORS,
    'smearEnabled': SMUDGE_HIT_CREAM_SPLASH_SMEAR_ENABLED,
    'smearCount': SMUDGE_HIT_CREAM_SPLASH_SMEAR_COUNT,
    'smearHalf': SMUDGE_HIT_CREAM_SPLASH_SMEAR_HALF,
    'smearSpread': SMUDGE_HIT_CREAM_SPLASH_SMEAR_SPREAD,
    'smearSec': SMUDGE_HIT_CREAM_SPLASH_SMEAR_SEC,
    'smearPeakAlpha': SMUDGE_HIT_CREAM_SPLASH_SMEAR_PEAK_ALPHA,
    'smearColor': SMUDGE_HIT_CREAM_SPLASH_SMEAR_COLOR,
    'binSort': SMUDGE_HIT_CREAM_SPLASH_BIN,
}
SMUDGE_HIT_CREAM_AFTERSHOCK_ENABLED = True
SMUDGE_HIT_CREAM_AFTERSHOCK_DELAY_SEC = 0.12
SMUDGE_HIT_CREAM_AFTERSHOCK_COUNT = 6  # deepened pack residual vs #259 (5)
SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_COUNT = 3
SMUDGE_HIT_CREAM_AFTERSHOCK_SIZE = 0.12
SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_SIZE = 0.16
SMUDGE_HIT_CREAM_AFTERSHOCK_DRIFT = 0.92  # wider radial settle vs #259
SMUDGE_HIT_CREAM_AFTERSHOCK_FALL = 0.58
SMUDGE_HIT_CREAM_AFTERSHOCK_SEC = 0.38
SMUDGE_HIT_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.92)
SMUDGE_HIT_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.9)
SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_ENABLED = True
SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_HALF = 0.62
SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_START = 0.26
SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_PEAK = 1.8
SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_SEC = 0.34
SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.3
SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Soft cream wash pulse after Smudge purple ink splash (hit only) —
# aspect2d veil after SmudgeInkSplashFx (#75) smack (client only).
# Matches OverlordHitCreamWashFx (#161) / CorruptTelegraphCreamWashFx (#157)
# / CorruptSilhouetteCreamWashFx (#153) / CorruptDeathCreamWashFx (#119)
# two-beat grammar. Delay composed via SmudgeHitCreamWashFx.smudgeHitCreamWashLook
# → smudgeInkSplashLook('hit'). Soft cream/pastel contrast against purple ink.
# SMUDGE_HIT_CREAM_WASH_ENABLED = False drops wash only (purple splash stays).
# Death path keeps splash + death cream wash. Street Smudge only (not Overlord).
SMUDGE_HIT_CREAM_WASH_ENABLED = True
SMUDGE_HIT_CREAM_WASH_DELAY_SEC = 0.13  # fallback; look prefers splash compose
SMUDGE_HIT_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SMUDGE_HIT_CREAM_WASH_PEAK = 0.07  # quieter than death (0.14) / melee (0.10) /
# overlord hit (0.08); above telegraph (0.065) so Smudge hit reads vs purple ink
SMUDGE_HIT_CREAM_WASH_MID = 0.04
SMUDGE_HIT_CREAM_WASH_IN_SEC = 0.06
SMUDGE_HIT_CREAM_WASH_PULSE_SEC = 0.10
SMUDGE_HIT_CREAM_WASH_HOLD_SEC = 0.08
SMUDGE_HIT_CREAM_WASH_OUT_SEC = 0.38
SMUDGE_HIT_CREAM_WASH_BIN = 40  # soft veil under purple splash (45)
SMUDGE_HIT_CREAM_WASH_LOOK = {
    'id': 'smudge-hit-cream-wash',
    # delaySec composed with smudgeInkSplashLook('hit') when played.
    'delaySec': SMUDGE_HIT_CREAM_WASH_DELAY_SEC,
    'delayScale': 0.72,
    'color': SMUDGE_HIT_CREAM_WASH_COLOR,
    'peak': SMUDGE_HIT_CREAM_WASH_PEAK,
    'mid': SMUDGE_HIT_CREAM_WASH_MID,
    'inSec': SMUDGE_HIT_CREAM_WASH_IN_SEC,
    'pulseSec': SMUDGE_HIT_CREAM_WASH_PULSE_SEC,
    'holdSec': SMUDGE_HIT_CREAM_WASH_HOLD_SEC,
    'outSec': SMUDGE_HIT_CREAM_WASH_OUT_SEC,
    'binSort': SMUDGE_HIT_CREAM_WASH_BIN,
}
ATTACK_HIT_FLASH_COLOR = (1.0, 0.55, 1.0, 1.0)
ATTACK_HIT_FLASH_PEAK = 0.55
ATTACK_HIT_FLASH_IN = 0.04
ATTACK_HIT_FLASH_OUT = 0.14
# Existing Toontown SFX — wind-up whoosh + collision thud.
TELEGRAPH_SFX = 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg'
ATTACK_HIT_SFX = 'phase_3.5/audio/sfx/AV_collision.ogg'
TELEGRAPH_SFX_VOLUME = 0.55
ATTACK_HIT_SFX_VOLUME = 0.75

# Telegraph ink drip / splat pop — short rubber-hose readability juice on
# announceAttackTelegraph (client only; AI timings unchanged). Distinct from
# defeat DeathPop spray: drips fall down + tiny chest splat, not a burst.
TELEGRAPH_INK_DRIP_LOOK = {
    ARCHETYPE_INK: {
        'id': 'ink-drip',
        'lift': 2.15,
        'splatHalf': 0.42,
        'splatPeak': 1.85,
        'splatSec': 0.22,
        'splatColor': (0.55, 0.18, 0.85, 0.92),
        'dripCount': 4,
        'dripHalf': 0.16,
        'dripSpread': 0.55,
        'dripFall': 1.45,
        'dripSec': 0.38,
        'dripColor': (0.38, 0.1, 0.58, 0.95),
        'streakColor': (0.62, 0.22, 0.92, 0.9),
    },
    ARCHETYPE_BRUTE: {
        'id': 'sludge-drip',
        'lift': 2.45,
        'splatHalf': 0.52,
        'splatPeak': 2.05,
        'splatSec': 0.24,
        'splatColor': (0.28, 0.78, 0.22, 0.92),
        'dripCount': 5,
        'dripHalf': 0.2,
        'dripSpread': 0.7,
        'dripFall': 1.65,
        'dripSec': 0.42,
        'dripColor': (0.18, 0.62, 0.16, 0.95),
        'streakColor': (0.35, 0.9, 0.28, 0.9),
    },
    ARCHETYPE_SNARE: {
        'id': 'amber-drip',
        'lift': 1.95,
        'splatHalf': 0.36,
        'splatPeak': 1.7,
        'splatSec': 0.18,
        'splatColor': (0.95, 0.55, 0.18, 0.92),
        'dripCount': 3,
        'dripHalf': 0.14,
        'dripSpread': 0.85,
        'dripFall': 1.15,
        'dripSec': 0.32,
        'dripColor': (0.88, 0.45, 0.12, 0.95),
        'streakColor': (1.05, 0.65, 0.22, 0.9),
    },
    ARCHETYPE_GAGSTER: {
        'id': 'teal-gunk-drip',
        'lift': 2.25,
        'splatHalf': 0.44,
        'splatPeak': 1.9,
        'splatSec': 0.22,
        'splatColor': (0.22, 0.82, 0.88, 0.92),
        'dripCount': 4,
        'dripHalf': 0.17,
        'dripSpread': 0.65,
        'dripFall': 1.35,
        'dripSec': 0.4,
        'dripColor': (0.12, 0.62, 0.7, 0.95),
        'streakColor': (0.35, 0.95, 0.98, 0.9),
    },
    ARCHETYPE_CORRUPT_OSWALD: {
        'id': 'betrayal-crimson-drip',
        'lift': 2.2,
        'splatHalf': 0.46,
        'splatPeak': 1.95,
        'splatSec': 0.2,
        'splatColor': (0.92, 0.28, 0.32, 0.94),
        'dripCount': 4,
        'dripHalf': 0.16,
        'dripSpread': 0.58,
        'dripFall': 1.4,
        'dripSec': 0.36,
        'dripColor': (0.72, 0.12, 0.18, 0.95),
        'streakColor': (1.05, 0.35, 0.42, 0.9),
    },
}

# Telegraph cream / pastel warn flecks — sunny purity chips layered on
# announceAttackTelegraph with CorruptTelegraphInkFx / silhouette pops
# (client only). Contrast to ink drip (cream floats out; ink falls). Not ink;
# matches reclaim / death-cream / hit-spark cream family.
# TELEGRAPH_CREAM_WARN_ENABLED = False drops flecks + aftershock.
TELEGRAPH_CREAM_WARN_ENABLED = True
TELEGRAPH_CREAM_WARN_BIN = 43
TELEGRAPH_CREAM_WARN_COLORS = (
    (1.0, 0.97, 0.82, 0.95),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.9),    # soft peach pastel
    (0.98, 0.94, 0.88, 0.88),  # warm parchment
)
TELEGRAPH_CREAM_WARN_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
TELEGRAPH_CREAM_WARN_LOOK = {
    'id': 'telegraph-cream-warn',
    # lift composed with telegraphInkLook when played; this is the fallback.
    'lift': 2.15,
    'fleckCount': 5,
    'fleckHalf': 0.12,
    'fleckDist': 1.15,
    'fleckLift': 0.55,
    'fleckSec': 0.24,
    'fleckColors': TELEGRAPH_CREAM_WARN_COLORS,
    'fleckEndColors': TELEGRAPH_CREAM_WARN_END_COLORS,
    'binSort': TELEGRAPH_CREAM_WARN_BIN,
}

# Delayed cream aftershock after telegraph cream warn flecks — residual
# soft halo + flecks/streaks that settle downward (cream/pastel only).
# Same grammar as HIT_SPARK_CREAM_AFTERSHOCK_* / PERFECT_DODGE_CREAM_AFTERSHOCK_*.
# TELEGRAPH_CREAM_WARN_AFTERSHOCK_ENABLED = False drops aftershock only.
TELEGRAPH_CREAM_WARN_AFTERSHOCK_ENABLED = True
TELEGRAPH_CREAM_WARN_AFTERSHOCK_DELAY_SEC = 0.18
TELEGRAPH_CREAM_WARN_AFTERSHOCK_COUNT = 3
TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_COUNT = 2
TELEGRAPH_CREAM_WARN_AFTERSHOCK_SIZE = 0.11
TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_SIZE = 0.16
TELEGRAPH_CREAM_WARN_AFTERSHOCK_DRIFT = 0.7
TELEGRAPH_CREAM_WARN_AFTERSHOCK_SEC = 0.38
TELEGRAPH_CREAM_WARN_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.88)
TELEGRAPH_CREAM_WARN_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.85)
TELEGRAPH_CREAM_WARN_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_ENABLED = True
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_HALF = 0.48
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_START = 0.3
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_PEAK = 1.55
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_SEC = 0.32
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_PEAK_ALPHA = 0.26
TELEGRAPH_CREAM_WARN_AFTERSHOCK_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)

# Rising cream sparkle flecks on telegraph cream warn — soft sunny chips that
# rise from the CorruptTelegraphCreamWarnFx warn spray (client only).
# Compose lift / warn radius via CorruptTelegraphCreamSparkleFx.telegraphCreamSparkleLook
# → telegraphCreamWarnLook (#102); fleck size/timing/rise borrows silhouette
# cream sparkle (#131) twinkle grammar. Distinct from outward warn flecks and
# settling aftershock: starts near warn spray, rises mostly upward with twinkle.
# Not ink-colored. TELEGRAPH_CREAM_SPARKLE_ENABLED = False drops rising sparkles only.
TELEGRAPH_CREAM_SPARKLE_ENABLED = True
TELEGRAPH_CREAM_SPARKLE_BIN = 44
TELEGRAPH_CREAM_SPARKLE_COLORS = (
    (1.0, 0.97, 0.82, 0.88),  # sunny cream
    (1.0, 0.96, 0.62, 0.82),  # butter
    (1.0, 0.9, 0.78, 0.78),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.74),  # warm parchment
)
TELEGRAPH_CREAM_SPARKLE_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
TELEGRAPH_CREAM_SPARKLE_LOOK = {
    'id': 'telegraph-cream-sparkle',
    # lift / warnRadius composed with telegraphCreamWarnLook when played; fallbacks below.
    'lift': 2.15,
    'startDelaySec': 0.04,
    'fleckCount': 3,
    'fleckHalf': 0.065,
    'fleckHalfScale': 1.05,
    'warnRadius': 0.48,
    'warnRadiusScale': 0.42,
    'warnZJitter': 0.19,
    'warnZJitterScale': 0.35,
    'fleckDist': 0.14,
    'fleckDistScale': 1.15,
    'fleckLift': 0.6,
    'fleckLiftScale': 1.08,
    'fleckSec': 0.37,
    'fleckSecScale': 0.92,
    'fleckStagger': 0.038,
    'fleckColors': TELEGRAPH_CREAM_SPARKLE_COLORS,
    'fleckEndColors': TELEGRAPH_CREAM_SPARKLE_END_COLORS,
    'binSort': TELEGRAPH_CREAM_SPARKLE_BIN,
}

# Soft cream wash pulse on telegraph cream warn / sparkle stack — aspect2d
# veil after warn flecks (#102) + aftershock (#121) + rising sparkles (#135)
# (client only). Matches CorruptSilhouetteCreamWashFx (#153) /
# IdleCreamWashPulseFx (#146) / CorruptDeathCreamWashFx (#119) two-beat
# grammar. Delay composed via CorruptTelegraphCreamWashFx.telegraphCreamWashLook
# → telegraphCreamSparkleLook. Soft cream/pastel contrast against ink telegraph.
# TELEGRAPH_CREAM_WASH_ENABLED = False drops wash only (warn / sparkle stay).
TELEGRAPH_CREAM_WASH_ENABLED = True
TELEGRAPH_CREAM_WASH_DELAY_SEC = 0.30  # fallback; look prefers sparkle compose
TELEGRAPH_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
TELEGRAPH_CREAM_WASH_PEAK = 0.065  # quieter than death (0.14) / melee (0.10);
# slightly above idle (0.055) / silhouette (0.05) so telegraph event reads
TELEGRAPH_CREAM_WASH_MID = 0.036
TELEGRAPH_CREAM_WASH_IN_SEC = 0.06
TELEGRAPH_CREAM_WASH_PULSE_SEC = 0.10
TELEGRAPH_CREAM_WASH_HOLD_SEC = 0.08
TELEGRAPH_CREAM_WASH_OUT_SEC = 0.40
TELEGRAPH_CREAM_WASH_BIN = 39  # soft veil under telegraph flecks (43) / sparkles (44)
TELEGRAPH_CREAM_WASH_LOOK = {
    'id': 'telegraph-cream-wash',
    # delaySec composed with telegraphCreamSparkleLook when played; fallbacks below.
    'delaySec': TELEGRAPH_CREAM_WASH_DELAY_SEC,
    'delayScale': 0.72,
    'delayBias': 0.12,
    'color': TELEGRAPH_CREAM_WASH_COLOR,
    'peak': TELEGRAPH_CREAM_WASH_PEAK,
    'mid': TELEGRAPH_CREAM_WASH_MID,
    'inSec': TELEGRAPH_CREAM_WASH_IN_SEC,
    'pulseSec': TELEGRAPH_CREAM_WASH_PULSE_SEC,
    'holdSec': TELEGRAPH_CREAM_WASH_HOLD_SEC,
    'outSec': TELEGRAPH_CREAM_WASH_OUT_SEC,
    'binSort': TELEGRAPH_CREAM_WASH_BIN,
}

# Ambient idle ink drip — sparse rubber-hose pollution presence between
# telegraphs (client only). Cheaper than TELEGRAPH_INK_DRIP_*: 1–2 drips,
# no splat pop, longer period, lower alpha. Pauses while telegraph juice
# owns the frame. Overlord retints via IdleInkDripFx.idleInkLook(finaleLook).
IDLE_INK_DRIP_LOOK = {
    ARCHETYPE_INK: {
        'id': 'ink-idle',
        'lift': 2.05,
        'periodSec': 2.15,
        'settleSec': 0.55,
        'dripCount': 1,
        'dripHalf': 0.11,
        'dripSpread': 0.32,
        'dripFall': 0.95,
        'dripSec': 0.55,
        'dripStagger': 0.05,
        'dripColor': (0.32, 0.08, 0.48, 0.55),
        'streakColor': (0.48, 0.16, 0.72, 0.48),
        'binSort': 39,
    },
    ARCHETYPE_BRUTE: {
        'id': 'sludge-idle',
        'lift': 2.35,
        'periodSec': 2.45,
        'settleSec': 0.65,
        'dripCount': 2,
        'dripHalf': 0.14,
        'dripSpread': 0.4,
        'dripFall': 1.1,
        'dripSec': 0.62,
        'dripStagger': 0.07,
        'dripColor': (0.14, 0.48, 0.12, 0.55),
        'streakColor': (0.22, 0.68, 0.18, 0.48),
        'binSort': 39,
    },
    ARCHETYPE_SNARE: {
        'id': 'amber-idle',
        'lift': 1.85,
        'periodSec': 1.85,
        'settleSec': 0.4,
        'dripCount': 1,
        'dripHalf': 0.09,
        'dripSpread': 0.55,
        'dripFall': 0.75,
        'dripSec': 0.48,
        'dripStagger': 0.04,
        'dripColor': (0.72, 0.36, 0.1, 0.5),
        'streakColor': (0.88, 0.5, 0.16, 0.42),
        'binSort': 39,
    },
    ARCHETYPE_GAGSTER: {
        'id': 'teal-gunk-idle',
        'lift': 2.15,
        'periodSec': 2.05,
        'settleSec': 0.5,
        'dripCount': 2,
        'dripHalf': 0.12,
        'dripSpread': 0.42,
        'dripFall': 1.0,
        'dripSec': 0.58,
        'dripStagger': 0.06,
        'dripColor': (0.1, 0.48, 0.55, 0.55),
        'streakColor': (0.22, 0.72, 0.78, 0.48),
        'binSort': 39,
    },
    ARCHETYPE_CORRUPT_OSWALD: {
        'id': 'betrayal-crimson-idle',
        'lift': 2.1,
        'periodSec': 1.95,
        'settleSec': 0.48,
        'dripCount': 2,
        'dripHalf': 0.12,
        'dripSpread': 0.4,
        'dripFall': 0.98,
        'dripSec': 0.52,
        'dripStagger': 0.05,
        'dripColor': (0.55, 0.1, 0.14, 0.55),
        'streakColor': (0.82, 0.22, 0.28, 0.48),
        'binSort': 39,
    },
}

# Idle cream / pastel drip contrast — soft sunny chips layered with
# IdleInkDripFx between telegraphs (client only). Cream drips fall beside
# dark ink (phase-offset); not ink-colored. Compose lift/period via
# IdleCreamDripContrastFx.idleCreamDripLook → idleInkLook.
# IDLE_CREAM_DRIP_ENABLED = False drops cream drips only (ink idle stays).
IDLE_CREAM_DRIP_ENABLED = True
IDLE_CREAM_DRIP_BIN = 41
IDLE_CREAM_DRIP_COLORS = (
    (1.0, 0.97, 0.82, 0.72),  # sunny cream
    (1.0, 0.96, 0.62, 0.68),  # butter
    (1.0, 0.9, 0.78, 0.65),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.62),  # warm parchment
)
IDLE_CREAM_DRIP_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
IDLE_CREAM_DRIP_LOOK = {
    'id': 'idle-cream-drip',
    # lift / period composed with idleInkLook when played; these are fallbacks.
    'lift': 2.05,
    'periodSec': 2.55,
    'periodScale': 1.18,
    'settleSec': 0.75,
    'settleBias': 0.22,
    'dripCount': 1,
    'dripHalf': 0.1,
    'dripSpread': 0.38,
    'dripFall': 0.85,
    'dripSec': 0.58,
    'dripStagger': 0.06,
    'dripColors': IDLE_CREAM_DRIP_COLORS,
    'dripEndColors': IDLE_CREAM_DRIP_END_COLORS,
    'binSort': IDLE_CREAM_DRIP_BIN,
}

# Silhouette cream / pastel rim flecks — soft sunny chips sparkling along the
# ink Actor/DNA (or card) silhouette rim between telegraphs (client only).
# Compose lift/period via CorruptSilhouetteCreamRimFx.silhouetteCreamRimLook
# → idleCreamDripLook. Distinct from falling IdleCreamDripContrastFx drips:
# rim flecks orbit/drift off the silhouette edge. Not ink-colored.
# SILHOUETTE_CREAM_RIM_ENABLED = False drops rim flecks only (idle cream stays).
SILHOUETTE_CREAM_RIM_ENABLED = True
SILHOUETTE_CREAM_RIM_BIN = 42
SILHOUETTE_CREAM_RIM_COLORS = (
    (1.0, 0.97, 0.82, 0.78),  # sunny cream
    (1.0, 0.96, 0.62, 0.72),  # butter
    (1.0, 0.9, 0.78, 0.68),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.65),  # warm parchment
)
SILHOUETTE_CREAM_RIM_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
SILHOUETTE_CREAM_RIM_LOOK = {
    'id': 'silhouette-cream-rim',
    # lift / period composed with idleCreamDripLook when played; fallbacks below.
    'lift': 2.05,
    'periodSec': 1.85,
    'periodScale': 0.72,
    'settleSec': 0.55,
    'settleBias': -0.12,
    'fleckCount': 3,
    'fleckHalf': 0.09,
    'rimRadius': 0.72,
    'rimZJitter': 0.22,
    'fleckDist': 0.38,
    'fleckLift': 0.28,
    'fleckSec': 0.42,
    'fleckStagger': 0.04,
    'fleckColors': SILHOUETTE_CREAM_RIM_COLORS,
    'fleckEndColors': SILHOUETTE_CREAM_RIM_END_COLORS,
    'binSort': SILHOUETTE_CREAM_RIM_BIN,
}

# Idle cream drip sparkle flecks — soft sunny chips twinkling along the
# IdleCreamDripContrastFx drip path between telegraphs (client only).
# Compose lift/period via IdleCreamDripSparkleFx.idleCreamDripSparkleLook
# → idleCreamDripLook; fleck size/timing borrows silhouette cream rim (#114)
# sparkle grammar. Distinct from falling drips and silhouette rim orbit:
# tighter radius near cream drip angles, twinkle pop scale. Not ink-colored.
# IDLE_CREAM_DRIP_SPARKLE_ENABLED = False drops sparkles only (cream drip stays).
IDLE_CREAM_DRIP_SPARKLE_ENABLED = True
IDLE_CREAM_DRIP_SPARKLE_BIN = 43
IDLE_CREAM_DRIP_SPARKLE_COLORS = (
    (1.0, 0.97, 0.82, 0.82),  # sunny cream
    (1.0, 0.96, 0.62, 0.76),  # butter
    (1.0, 0.9, 0.78, 0.72),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.68),  # warm parchment
)
IDLE_CREAM_DRIP_SPARKLE_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
IDLE_CREAM_DRIP_SPARKLE_LOOK = {
    'id': 'idle-cream-drip-sparkle',
    # lift / period composed with idleCreamDripLook when played; fallbacks below.
    'lift': 2.05,
    'periodSec': 1.48,
    'periodScale': 0.58,
    'settleSec': 0.55,
    'settleBias': -0.18,
    'fleckCount': 2,
    'fleckHalf': 0.07,
    'fleckHalfScale': 0.78,
    'sparkleRadius': 0.42,
    'dripBias': 0.18,
    'fleckDist': 0.22,
    'fleckLift': 0.18,
    'fleckSec': 0.36,
    'fleckSecScale': 0.85,
    'fleckStagger': 0.035,
    'fleckColors': IDLE_CREAM_DRIP_SPARKLE_COLORS,
    'fleckEndColors': IDLE_CREAM_DRIP_SPARKLE_END_COLORS,
    'binSort': IDLE_CREAM_DRIP_SPARKLE_BIN,
}

# Idle cream wash pulse — soft aspect2d veil between telegraphs (client only).
# Matches CorruptDeathCreamWashFx (#119) / HitSparkCreamWashFx (#134) two-beat
# grammar; quieter ambient contrast against IdleInkDripFx. Compose period via
# IdleCreamWashPulseFx.idleCreamWashLook → idleCreamDripSparkleLook; delayed
# cream aftershock (IDLE_CREAM_WASH_AFTERSHOCK_*) settles after each wash
# (#172 / #132 grammar). Toggle IDLE_CREAM_WASH_ENABLED /
# IDLE_CREAM_WASH_AFTERSHOCK_ENABLED.
# IDLE_CREAM_WASH_ENABLED = False drops wash (and therefore aftershock).
IDLE_CREAM_WASH_ENABLED = True
IDLE_CREAM_WASH_DELAY_SEC = 0.0  # loop settle handles spacing
IDLE_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
IDLE_CREAM_WASH_PEAK = 0.055  # quieter than death (0.14) / melee hit (0.10)
IDLE_CREAM_WASH_MID = 0.032
IDLE_CREAM_WASH_IN_SEC = 0.07
IDLE_CREAM_WASH_PULSE_SEC = 0.12
IDLE_CREAM_WASH_HOLD_SEC = 0.10
IDLE_CREAM_WASH_OUT_SEC = 0.48
IDLE_CREAM_WASH_BIN = 36  # soft veil under death wash (38) / idle drips
IDLE_CREAM_WASH_LOOK = {
    'id': 'idle-cream-wash',
    # period composed with idleCreamDripSparkleLook when played; fallbacks below.
    'periodSec': 3.2,
    'periodScale': 2.15,
    'settleSec': 1.05,
    'settleBias': 0.48,
    'delaySec': IDLE_CREAM_WASH_DELAY_SEC,
    'color': IDLE_CREAM_WASH_COLOR,
    'peak': IDLE_CREAM_WASH_PEAK,
    'mid': IDLE_CREAM_WASH_MID,
    'inSec': IDLE_CREAM_WASH_IN_SEC,
    'pulseSec': IDLE_CREAM_WASH_PULSE_SEC,
    'holdSec': IDLE_CREAM_WASH_HOLD_SEC,
    'outSec': IDLE_CREAM_WASH_OUT_SEC,
    'binSort': IDLE_CREAM_WASH_BIN,
}

# Delayed cream aftershock after each idle cream wash pulse — residual flecks
# settling + soft halo (IdleCreamWashPulseFx). Same grammar as
# DEATH_CREAM_WASH_AFTERSHOCK_* (#172) / ENTRY_CREAM_WASH_AFTERSHOCK_* (#132);
# world-space settle matches TELEGRAPH_CREAM_WARN_AFTERSHOCK_*. Quieter than
# death aftershock (ambient idle). IDLE_CREAM_WASH_AFTERSHOCK_ENABLED = False
# drops aftershock only.
IDLE_CREAM_WASH_AFTERSHOCK_ENABLED = True
IDLE_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.32  # from pulse arm
IDLE_CREAM_WASH_AFTERSHOCK_LIFT = 1.10  # fallback; prefers idleCreamDripLook lift * 0.55
IDLE_CREAM_WASH_AFTERSHOCK_COUNT = 4
IDLE_CREAM_WASH_AFTERSHOCK_SIZE = 0.09
IDLE_CREAM_WASH_AFTERSHOCK_DRIFT = 0.48
IDLE_CREAM_WASH_AFTERSHOCK_FALL = 0.42
IDLE_CREAM_WASH_AFTERSHOCK_SEC = 0.30
IDLE_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.62)
IDLE_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
IDLE_CREAM_WASH_AFTERSHOCK_BIN = 37  # above wash (36); soft residual
IDLE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
IDLE_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.42
IDLE_CREAM_WASH_AFTERSHOCK_HALO_START = 0.24
IDLE_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.25
IDLE_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.26
IDLE_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.12
IDLE_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Silhouette cream rim rising sparkle flecks — soft sunny chips rising from
# the CorruptSilhouetteCreamRimFx rim edge between telegraphs (client only).
# Compose lift/period via CorruptSilhouetteCreamSparkleFx.silhouetteCreamSparkleLook
# → silhouetteCreamRimLook; fleck size/timing borrows idle cream drip sparkle
# (#125) twinkle grammar. Distinct from rim orbit (#114) and drip-path sparkle:
# starts on rim, rises mostly upward with twinkle pop. Not ink-colored.
# SILHOUETTE_CREAM_SPARKLE_ENABLED = False drops rising sparkles only (rim stays).
SILHOUETTE_CREAM_SPARKLE_ENABLED = True
SILHOUETTE_CREAM_SPARKLE_BIN = 44
SILHOUETTE_CREAM_SPARKLE_COLORS = (
    (1.0, 0.97, 0.82, 0.84),  # sunny cream
    (1.0, 0.96, 0.62, 0.78),  # butter
    (1.0, 0.9, 0.78, 0.74),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.7),  # warm parchment
)
SILHOUETTE_CREAM_SPARKLE_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
SILHOUETTE_CREAM_SPARKLE_LOOK = {
    'id': 'silhouette-cream-sparkle',
    # lift / period composed with silhouetteCreamRimLook when played; fallbacks below.
    'lift': 2.05,
    'periodSec': 1.18,
    'periodScale': 0.64,
    'settleSec': 0.47,
    'settleBias': -0.08,
    'fleckCount': 2,
    'fleckHalf': 0.06,
    'fleckHalfScale': 0.88,
    'rimRadius': 0.69,
    'rimRadiusScale': 0.96,
    'rimZJitter': 0.15,
    'rimZJitterScale': 0.7,
    'fleckDist': 0.12,
    'fleckLift': 0.55,
    'fleckSec': 0.4,
    'fleckSecScale': 1.12,
    'fleckStagger': 0.038,
    'fleckColors': SILHOUETTE_CREAM_SPARKLE_COLORS,
    'fleckEndColors': SILHOUETTE_CREAM_SPARKLE_END_COLORS,
    'binSort': SILHOUETTE_CREAM_SPARKLE_BIN,
}

# Silhouette cream wash pulse — soft aspect2d veil between telegraphs
# (client only). Matches IdleCreamWashPulseFx (#146) / CorruptDeathCreamWashFx
# (#119) two-beat grammar; quieter ambient contrast against the ink silhouette
# cream rim + rising sparkle stack. Compose period via
# CorruptSilhouetteCreamWashFx.silhouetteCreamWashLook → silhouetteCreamSparkleLook;
# delayed cream aftershock (SILHOUETTE_CREAM_WASH_AFTERSHOCK_*) settles after
# each wash (#177 / #172 grammar). Toggle SILHOUETTE_CREAM_WASH_ENABLED /
# SILHOUETTE_CREAM_WASH_AFTERSHOCK_ENABLED.
# SILHOUETTE_CREAM_WASH_ENABLED = False drops wash (and therefore aftershock).
SILHOUETTE_CREAM_WASH_ENABLED = True
SILHOUETTE_CREAM_WASH_DELAY_SEC = 0.0  # loop settle handles spacing
SILHOUETTE_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SILHOUETTE_CREAM_WASH_PEAK = 0.05  # quieter than idle (0.055) / death (0.14)
SILHOUETTE_CREAM_WASH_MID = 0.028
SILHOUETTE_CREAM_WASH_IN_SEC = 0.07
SILHOUETTE_CREAM_WASH_PULSE_SEC = 0.12
SILHOUETTE_CREAM_WASH_HOLD_SEC = 0.10
SILHOUETTE_CREAM_WASH_OUT_SEC = 0.48
SILHOUETTE_CREAM_WASH_BIN = 37  # soft veil between idle wash (36) / death (38)
SILHOUETTE_CREAM_WASH_LOOK = {
    'id': 'silhouette-cream-wash',
    # period composed with silhouetteCreamSparkleLook when played; fallbacks below.
    'periodSec': 2.85,
    'periodScale': 2.4,
    'settleSec': 0.99,
    'settleBias': 0.52,
    'delaySec': SILHOUETTE_CREAM_WASH_DELAY_SEC,
    'color': SILHOUETTE_CREAM_WASH_COLOR,
    'peak': SILHOUETTE_CREAM_WASH_PEAK,
    'mid': SILHOUETTE_CREAM_WASH_MID,
    'inSec': SILHOUETTE_CREAM_WASH_IN_SEC,
    'pulseSec': SILHOUETTE_CREAM_WASH_PULSE_SEC,
    'holdSec': SILHOUETTE_CREAM_WASH_HOLD_SEC,
    'outSec': SILHOUETTE_CREAM_WASH_OUT_SEC,
    'binSort': SILHOUETTE_CREAM_WASH_BIN,
}

# Delayed cream aftershock after each silhouette cream wash pulse — residual
# flecks settling + soft halo (CorruptSilhouetteCreamWashFx). Same grammar as
# IDLE_CREAM_WASH_AFTERSHOCK_* (#177) / DEATH_CREAM_WASH_AFTERSHOCK_* (#172);
# world-space settle matches TELEGRAPH_CREAM_WARN_AFTERSHOCK_* (#121). Quieter
# than idle aftershock (ambient silhouette). SILHOUETTE_CREAM_WASH_AFTERSHOCK_ENABLED
# = False drops aftershock only.
SILHOUETTE_CREAM_WASH_AFTERSHOCK_ENABLED = True
SILHOUETTE_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.32  # from pulse arm
SILHOUETTE_CREAM_WASH_AFTERSHOCK_LIFT = 2.05  # fallback; prefers silhouetteCreamRimLook lift * 0.55
SILHOUETTE_CREAM_WASH_AFTERSHOCK_COUNT = 4
SILHOUETTE_CREAM_WASH_AFTERSHOCK_SIZE = 0.08
SILHOUETTE_CREAM_WASH_AFTERSHOCK_DRIFT = 0.48
SILHOUETTE_CREAM_WASH_AFTERSHOCK_FALL = 0.42
SILHOUETTE_CREAM_WASH_AFTERSHOCK_SEC = 0.30
SILHOUETTE_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.58)
SILHOUETTE_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
SILHOUETTE_CREAM_WASH_AFTERSHOCK_BIN = 38  # above wash (37); soft residual
SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.42
SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_START = 0.24
SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.25
SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.26
SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.10
SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Sludge Brute spit telegraph — swamp green, wider squash, squirt SFX.
# Distinct from Ink Smudge purple melee so ranged wind-up reads at a glance.
BRUTE_TELEGRAPH_CHARGE_COLOR = (0.45, 2.2, 0.35, 1.0)
BRUTE_TELEGRAPH_HOLD_COLOR = (0.3, 1.65, 0.22, 1.0)
BRUTE_TELEGRAPH_SQUASH = (2.35, 2.35, 0.32)
BRUTE_TELEGRAPH_MID = (2.05, 2.05, 0.42)
BRUTE_TELEGRAPH_STRETCH = (0.48, 0.48, 1.95)
BRUTE_TELEGRAPH_SFX = 'phase_4/audio/sfx/AA_squirt_seltzer.ogg'
BRUTE_TELEGRAPH_SFX_VOLUME = 0.7
BRUTE_ATTACK_HIT_SFX = 'phase_4/audio/sfx/AA_squirt_glasswater.ogg'
BRUTE_ATTACK_HIT_SFX_VOLUME = 0.8
BRUTE_HIT_FLASH_COLOR = (0.45, 1.05, 0.35, 1.0)
BRUTE_HIT_FLASH_PEAK = 0.62
# Client-only ink blob that travels toward the local toon on spit hit.
# Travel sec tracks AI BRUTE_SPIT_TRAVEL_SEC so AV flight matches projectile.
BRUTE_SPIT_BLOB_COLOR = (0.18, 0.72, 0.22, 0.92)
BRUTE_SPIT_BLOB_SCALE = 0.55
BRUTE_SPIT_BLOB_TRAVEL = 0.32
BRUTE_SPIT_BLOB_Z = 2.4

# ---------------------------------------------------------------------------
# Sludge Brute spit projectile + slam secondary (gameplay identity).
# Gap scan #4: was AV blob + longer __resolveSingleTargetHit smack — Punchline
# pack read as tinted Smudge at AI level. BRUTE_SPIT_PROJECTILE_ENABLED = False
# falls back to instant single-target spit smack; BRUTE_SLAM_SECONDARY_ENABLED
# = False keeps spit-only. Not cream FX deepen.
# ---------------------------------------------------------------------------
BRUTE_SPIT_PROJECTILE_ENABLED = True
BRUTE_SPIT_TRAVEL_SEC = 0.32
BRUTE_SPIT_MAX_RANGE = 11.0
BRUTE_SPIT_LAND_RADIUS = 3.5
BRUTE_SPIT_TRAIL_TICK_SEC = 0.1
BRUTE_SPIT_TRAIL_RADIUS = 1.6
BRUTE_SPIT_TRAIL_DAMAGE = 1
BRUTE_SLAM_SECONDARY_ENABLED = True
BRUTE_SLAM_MELEE_RANGE = 4.2


def bruteSpitTravelSec(stats=None):
    """Seconds for spit projectile to travel origin → clamped aim."""
    if stats and 'spitTravelSec' in stats:
        return max(0.05, float(stats['spitTravelSec']))
    return max(0.05, float(BRUTE_SPIT_TRAVEL_SEC))


def bruteSpitMaxRange(stats=None):
    """Planar max aim distance from Brute (projectile reach)."""
    if stats and 'spitMaxRange' in stats:
        return max(0.5, float(stats['spitMaxRange']))
    return max(0.5, float(BRUTE_SPIT_MAX_RANGE))


def bruteSpitLandRadius(stats=None):
    """Splash radius at spit land (also default attackHitRange)."""
    if stats and 'attackHitRange' in stats:
        return max(0.5, float(stats['attackHitRange']))
    return max(0.5, float(BRUTE_SPIT_LAND_RADIUS))


def bruteSpitTrailTickSec(stats=None):
    if stats and 'spitTrailTickSec' in stats:
        return max(0.05, float(stats['spitTrailTickSec']))
    return max(0.05, float(BRUTE_SPIT_TRAIL_TICK_SEC))


def bruteSpitTrailRadius(stats=None):
    if stats and 'spitTrailRadius' in stats:
        return max(0.25, float(stats['spitTrailRadius']))
    return max(0.25, float(BRUTE_SPIT_TRAIL_RADIUS))


def bruteSpitTrailDamage(stats=None):
    if stats and 'spitTrailDamage' in stats:
        return max(1, int(stats['spitTrailDamage']))
    return max(1, int(BRUTE_SPIT_TRAIL_DAMAGE))


def bruteSpitAimPos(sx, sy, aimX, aimY, maxRange=None):
    """Clamp spit aim XY to ``maxRange`` from origin (sx, sy).

    Returns (lx, ly) on the origin→aim ray. Coincident / zero max → origin.
    """
    if maxRange is None:
        maxRange = BRUTE_SPIT_MAX_RANGE
    maxRange = max(0.0, float(maxRange))
    sx = float(sx)
    sy = float(sy)
    dx = float(aimX) - sx
    dy = float(aimY) - sy
    dist = (dx * dx + dy * dy) ** 0.5
    if dist < 1e-6 or maxRange <= 0.0:
        return (sx, sy)
    if dist <= maxRange:
        return (sx + dx, sy + dy)
    return (sx + dx / dist * maxRange, sy + dy / dist * maxRange)


def bruteSpitPosAtFrac(ox, oy, lx, ly, frac):
    """Planar spit position at flight fraction ``frac`` in [0, 1]."""
    t = max(0.0, min(1.0, float(frac)))
    return (float(ox) + (float(lx) - float(ox)) * t,
            float(oy) + (float(ly) - float(oy)) * t)


def isInsideBruteSpitSplash(dx, dy, radius):
    """True when planar offset is inside a spit splash / trail circle."""
    r = max(0.0, float(radius))
    return (float(dx) * float(dx) + float(dy) * float(dy)) <= (r * r)


def bruteSlamMeleeRange(stats=None):
    if stats and 'slamMeleeRange' in stats:
        return max(0.5, float(stats['slamMeleeRange']))
    return max(0.5, float(BRUTE_SLAM_MELEE_RANGE))


def brutePickAttackMove(dist, stats=None):
    """Choose Brute ``spit`` vs close ``slam`` from planar distance.

    Spit is the default attackMove; slam is the tank secondary when the toon
    is inside slamMeleeRange. Returns ``spit`` when slam secondary is off.
    """
    if not BRUTE_SLAM_SECONDARY_ENABLED:
        return 'spit'
    if float(dist) <= bruteSlamMeleeRange(stats):
        return 'slam'
    return 'spit'

# Sludge Brute telegraph spit-gob pop — short rubber-hose green spit charge on
# announceAttackTelegraph (client only). Distinct from hit-time BRUTE_SPIT_BLOB_*
# travel and from generic TELEGRAPH_INK_DRIP sludge drips: forward spit silhouette.
BRUTE_TELEGRAPH_SPIT_LOOK = {
    'id': 'sludge-spit-gob',
    'lift': 2.55,
    'scale': 1.0,
    'peakAlpha': 0.97,
    'fadeInSec': 0.04,
    'holdSec': 0.16,
    'fadeOutSec': 0.24,
    'squash': (1.65, 1.0, 0.42),
    'stretch': (0.55, 1.0, 2.15),
    'squashSec': 0.05,
    'stretchSec': 0.12,
    'settleSec': 0.14,
    'wobbleDeg': 12.0,
    'gobHalf': 0.38,
    'rimScale': 1.28,
    'hotHalf': 0.14,
    'gobColor': (0.22, 0.85, 0.28, 1.0),
    'rimColor': (0.55, 1.2, 0.42, 1.0),
    'flashColor': (0.55, 1.35, 0.4, 1.0),
    'dropletCount': 4,
    'dropletHalf': 0.1,
    'dropletSec': 0.3,
    'dropletSpread': 1.05,
    'dropletColor': (0.35, 0.95, 0.3, 0.9),
    'binSort': 44,
}

# Cream splash + delayed cream aftershock on Sludge Brute spit impact /
# telegraph land (after spit-gob telegraph). Sunny cream / pastel contrast
# against green BRUTE_SPIT_BLOB_* so the tank spit reads juicy. Deepened spit-
# land juice beyond #264 (#249 / #223 deepen): juicier splat/flecks + thicker
# vertical cream drip filaments (spit-gob fall read) + heavier downward
# settle aftershock — distinct from Snare counter cream deepen (#269 / #245,
# horizontal whip filaments), Gunk puddle cream deepen (#276 / #238, flat
# ground bloom), and Smudge hit cream deepen (#283 / #259, radial hose
# smears). Same residual grammar as TELEGRAPH_CREAM_WARN_AFTERSHOCK_*.
# Client only. No keyblades / KH branding.
# BRUTE_SPIT_CREAM_SPLASH_ENABLED = False drops splash + aftershock.
# BRUTE_SPIT_CREAM_AFTERSHOCK_ENABLED = False drops aftershock only.
# BRUTE_SPIT_CREAM_SPLASH_DRIP_ENABLED = False drops drip filaments only.
BRUTE_SPIT_CREAM_SPLASH_ENABLED = True
BRUTE_SPIT_CREAM_SPLASH_DELAY_SEC = 0.2  # fallback; look prefers spit travel compose
BRUTE_SPIT_CREAM_SPLASH_LIFT = 0.46  # above spit land pos (beyond #264 0.42)
BRUTE_SPIT_CREAM_SPLASH_BIN = 41  # above green spit blob (40)
BRUTE_SPIT_CREAM_SPLASH_COLOR = (1.0, 0.97, 0.82, 0.99)  # sunny cream
BRUTE_SPIT_CREAM_SPLASH_RIM_COLOR = (1.0, 0.98, 0.88, 0.86)
BRUTE_SPIT_CREAM_SPLASH_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.97),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.88),   # soft peach pastel
    (0.98, 0.94, 0.68, 0.86), # swamp-butter pastel — spit gob pop
)
# Vertical cream drip filaments — spit-gob fall readability (not Snare
# horizontal whip / Gunk flat puddle bloom / Smudge radial hose).
BRUTE_SPIT_CREAM_SPLASH_DRIP_ENABLED = True
BRUTE_SPIT_CREAM_SPLASH_DRIP_COUNT = 5  # beyond #264 (4)
BRUTE_SPIT_CREAM_SPLASH_DRIP_HALF = 0.1
BRUTE_SPIT_CREAM_SPLASH_DRIP_FALL = 1.25  # taller spit-gob drip (beyond #264 1.1)
BRUTE_SPIT_CREAM_SPLASH_DRIP_SEC = 0.28
BRUTE_SPIT_CREAM_SPLASH_DRIP_PEAK_ALPHA = 0.96
BRUTE_SPIT_CREAM_SPLASH_DRIP_COLOR = (1.0, 0.97, 0.84, 0.96)
BRUTE_SPIT_CREAM_SPLASH_LOOK = {
    'id': 'brute-spit-cream-splash',
    # lift / delaySec composed with BRUTE_SPIT_BLOB_TRAVEL when played.
    'lift': BRUTE_SPIT_CREAM_SPLASH_LIFT,
    'delaySec': BRUTE_SPIT_CREAM_SPLASH_DELAY_SEC,
    'delayScale': 0.76,  # snappier pop as green spit blob lands (beyond #264 0.82)
    'peakAlpha': 0.99,
    'splatHalf': 0.38,  # juicier spit-land core vs #264 (0.34) / #249 (0.3)
    'splatPeak': 2.05,
    'splatSec': 0.21,
    'rimScale': 1.48,
    'splatColor': BRUTE_SPIT_CREAM_SPLASH_COLOR,
    'rimColor': BRUTE_SPIT_CREAM_SPLASH_RIM_COLOR,
    'fleckCount': 8,  # beyond #264 (7); spit gob spray, under Overlord cream punch
    'fleckHalf': 0.13,
    'fleckDist': 1.28,
    'fleckLift': 0.62,  # taller spit-gob spray (beyond #264 0.55)
    'fleckSec': 0.28,
    'fleckColors': BRUTE_SPIT_CREAM_SPLASH_FLECK_COLORS,
    'dripEnabled': BRUTE_SPIT_CREAM_SPLASH_DRIP_ENABLED,
    'dripCount': BRUTE_SPIT_CREAM_SPLASH_DRIP_COUNT,
    'dripHalf': BRUTE_SPIT_CREAM_SPLASH_DRIP_HALF,
    'dripFall': BRUTE_SPIT_CREAM_SPLASH_DRIP_FALL,
    'dripSec': BRUTE_SPIT_CREAM_SPLASH_DRIP_SEC,
    'dripPeakAlpha': BRUTE_SPIT_CREAM_SPLASH_DRIP_PEAK_ALPHA,
    'dripColor': BRUTE_SPIT_CREAM_SPLASH_DRIP_COLOR,
    'binSort': BRUTE_SPIT_CREAM_SPLASH_BIN,
}
BRUTE_SPIT_CREAM_AFTERSHOCK_ENABLED = True
BRUTE_SPIT_CREAM_AFTERSHOCK_DELAY_SEC = 0.1
BRUTE_SPIT_CREAM_AFTERSHOCK_COUNT = 7  # beyond #264 (6) / #249 (5)
BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_COUNT = 4
BRUTE_SPIT_CREAM_AFTERSHOCK_SIZE = 0.13
BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_SIZE = 0.16
BRUTE_SPIT_CREAM_AFTERSHOCK_DRIFT = 0.88
BRUTE_SPIT_CREAM_AFTERSHOCK_FALL = 0.8  # heavier downward settle (beyond #264 0.68)
BRUTE_SPIT_CREAM_AFTERSHOCK_SEC = 0.4
BRUTE_SPIT_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.94)
BRUTE_SPIT_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.92)
BRUTE_SPIT_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_ENABLED = True
BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_HALF = 0.72  # wider spit-land halo (beyond #264 0.62)
BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_START = 0.26
BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_PEAK = 1.9
BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_SEC = 0.36
BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.3
BRUTE_SPIT_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Balloon Snare string-lash — warm amber, horizontal rubber stretch, vine zip.
# Reads opposite Brute spit (tall green) and Smudge melee (purple squash).
SNARE_TELEGRAPH_CHARGE_COLOR = (2.35, 1.45, 0.35, 1.0)
SNARE_TELEGRAPH_HOLD_COLOR = (1.95, 1.1, 0.28, 1.0)
SNARE_TELEGRAPH_SQUASH = (0.55, 0.55, 1.55)
SNARE_TELEGRAPH_MID = (1.15, 1.15, 1.15)
SNARE_TELEGRAPH_STRETCH = (2.55, 0.42, 0.55)  # horizontal rubber-hose lash
SNARE_TELEGRAPH_SFX = 'phase_4/audio/sfx/MG_sfx_vine_game_jump.ogg'
SNARE_TELEGRAPH_SFX_VOLUME = 0.72
SNARE_ATTACK_HIT_SFX = 'phase_4/audio/sfx/MG_sfx_vine_game_fall.ogg'
SNARE_ATTACK_HIT_SFX_VOLUME = 0.78
SNARE_HIT_FLASH_COLOR = (1.15, 0.72, 0.28, 1.0)
SNARE_HIT_FLASH_PEAK = 0.58
# Client-only string line that snaps toward the local toon on lash hit.
SNARE_LASH_COLOR = (0.95, 0.55, 0.12, 0.95)
SNARE_LASH_HALF_W = 0.12
SNARE_LASH_HALF_H = 0.55
SNARE_LASH_TRAVEL = 0.18
SNARE_LASH_Z = 2.1

# Balloon Snare string-lash yank — short planar reel toward the zip-flier when
# the lash lands (not damage-only). Archetype identity: string pulls you in.
# Gameplay displace — not cream FX deepen. SNARE_LASH_YANK_ENABLED = False
# restores damage-only resolve. Wired from DistributedCorruptToonAI
# __resolveSingleTargetHit + thin hackslash hurt-react lerp.
SNARE_LASH_YANK_ENABLED = True
SNARE_LASH_YANK_DIST = 2.35  # planar units toward Snare
SNARE_LASH_YANK_STOP = 1.4  # never pull closer than this gap
SNARE_LASH_YANK_SEC = 0.11  # client lerp duration (hackslash hurt react)


def snareLashYankDelta(sx, sy, tx, ty, dist=None, stop=None):
    """Planar (dx, dy) to add to toon at (tx, ty) to reel toward Snare (sx, sy).

    Pulls up to ``dist`` but never closer than ``stop`` to the Snare. Returns
    (0.0, 0.0) if already inside the stop radius or coincident.
    """
    if dist is None:
        dist = SNARE_LASH_YANK_DIST
    if stop is None:
        stop = SNARE_LASH_YANK_STOP
    dist = max(0.0, float(dist))
    stop = max(0.0, float(stop))
    dx = float(sx) - float(tx)
    dy = float(sy) - float(ty)
    planar = (dx * dx + dy * dy) ** 0.5
    if planar <= stop or planar < 1e-6 or dist <= 0.0:
        return (0.0, 0.0)
    pull = min(dist, planar - stop)
    if pull <= 0.0:
        return (0.0, 0.0)
    return (dx / planar * pull, dy / planar * pull)


def snareLashYankPos(sx, sy, tx, ty, dist=None, stop=None):
    """Return (nx, ny) after applying :func:`snareLashYankDelta`."""
    ddx, ddy = snareLashYankDelta(sx, sy, tx, ty, dist=dist, stop=stop)
    return (float(tx) + ddx, float(ty) + ddy)


# ---------------------------------------------------------------------------
# Ink Smudge ink-dash + splat secondary (gameplay identity).
# Gap scan #7: Act 1 spine + Overlord P2 adds were default smack fodder while
# Brute/Snare/Gagster/Oswald had distinct kits. INK_SMUDGE_KIT_ENABLED = False
# restores legacy smack. INK_SPLAT_SECONDARY_ENABLED = False keeps dash-only.
# Wired from DistributedCorruptToonAI.__beginAttack / __resolveInk*.
# Not cream FX deepen. No keyblades / KH branding.
# ---------------------------------------------------------------------------
INK_SMUDGE_KIT_ENABLED = True
INK_DASH_ENABLED = True
INK_SPLAT_SECONDARY_ENABLED = True
INK_DASH_DIST = 3.2  # planar dash toward the toon on resolve (shorter than Oswald)
INK_DASH_STOP = 0.75  # never overshoot past this gap to the toon
INK_SPLAT_MELEE_RANGE = 3.2  # pick splat when inside this engage


def inkSplatMeleeRange(stats=None):
    if stats and 'splatMeleeRange' in stats:
        return max(0.5, float(stats['splatMeleeRange']))
    return max(0.5, float(INK_SPLAT_MELEE_RANGE))


def inkDashDist(stats=None):
    if stats and 'dashDist' in stats:
        return max(0.0, float(stats['dashDist']))
    return max(0.0, float(INK_DASH_DIST))


def inkPickAttackMove(dist, stats=None):
    """Choose Ink Smudge ``ink_dash`` vs close ``ink_splat``.

    Dash is the default attackMove (swarm rush). Splat is the close secondary
    when the toon is inside splatMeleeRange. Returns ``ink_dash`` when the kit
    or splat secondary is off; ``smack`` when the whole kit is disabled.
    """
    if not INK_SMUDGE_KIT_ENABLED:
        return 'smack'
    if not INK_SPLAT_SECONDARY_ENABLED:
        return 'ink_dash'
    if float(dist) <= inkSplatMeleeRange(stats):
        return 'ink_splat'
    return 'ink_dash'


def inkDashPos(sx, sy, tx, ty, dash=None, stop=None):
    """Planar Smudge position after dashing toward (tx, ty).

    Advances up to ``dash`` but never closer than ``stop`` to the toon so the
    rush does not overshoot through them. Returns (sx, sy) if already inside
    the stop gap or coincident.
    """
    if dash is None:
        dash = INK_DASH_DIST
    if stop is None:
        stop = INK_DASH_STOP
    dash = max(0.0, float(dash))
    stop = max(0.0, float(stop))
    sx = float(sx)
    sy = float(sy)
    dx = float(tx) - sx
    dy = float(ty) - sy
    planar = (dx * dx + dy * dy) ** 0.5
    if planar <= stop or planar < 1e-6 or dash <= 0.0:
        return (sx, sy)
    step = min(dash, planar - stop)
    if step <= 0.0:
        return (sx, sy)
    return (sx + dx / planar * step, sy + dy / planar * step)


# ---------------------------------------------------------------------------
# Corrupted Oswald betrayal attack kit — not a crimson Smudge smack reskin.
#
# Finale chase identity: false-friend ``betrayal_lunge`` (dash then hit) as
# the default attackMove, close ``stain_burst`` AoE secondary when the toon
# is already in his face, and a planar ``betrayal_shove`` knockback on hit
# (opposite Balloon Snare yank). Gameplay kit — not cream FX deepen.
# OSWALD_BETRAYAL_KIT_ENABLED = False restores legacy smack for Oswald.
# Wired from DistributedCorruptToonAI.__beginAttack / __resolveOswald* /
# thin OswaldBetrayalChase spawn tip. No keyblades / KH branding.
# ---------------------------------------------------------------------------
OSWALD_BETRAYAL_KIT_ENABLED = True
OSWALD_BETRAYAL_LUNGE_ENABLED = True
OSWALD_STAIN_BURST_SECONDARY_ENABLED = True
OSWALD_BETRAYAL_SHOVE_ENABLED = True
OSWALD_BETRAYAL_LUNGE_DASH = 4.5  # planar dash toward the toon on resolve
OSWALD_BETRAYAL_LUNGE_STOP = 0.85  # never overshoot past this gap to the toon
OSWALD_STAIN_BURST_MELEE_RANGE = 3.6  # pick burst when inside this engage
OSWALD_BETRAYAL_SHOVE_DIST = 2.1  # planar knockback away from Oswald
OSWALD_BETRAYAL_SHOVE_SEC = 0.12  # client hurt-react lerp (hackslash)


def oswaldBurstMeleeRange(stats=None):
    if stats and 'burstMeleeRange' in stats:
        return max(0.5, float(stats['burstMeleeRange']))
    return max(0.5, float(OSWALD_STAIN_BURST_MELEE_RANGE))


def oswaldLungeDashDist(stats=None):
    if stats and 'lungeDashDist' in stats:
        return max(0.0, float(stats['lungeDashDist']))
    return max(0.0, float(OSWALD_BETRAYAL_LUNGE_DASH))


def oswaldShoveDist(stats=None):
    if stats and 'shoveDist' in stats:
        return max(0.0, float(stats['shoveDist']))
    return max(0.0, float(OSWALD_BETRAYAL_SHOVE_DIST))


def oswaldPickAttackMove(dist, stats=None):
    """Choose Oswald ``betrayal_lunge`` vs close ``stain_burst``.

    Lunge is the default attackMove (false-friend rush). Stain burst is the
    close secondary when the toon is inside burstMeleeRange. Returns
    ``betrayal_lunge`` when the kit or burst secondary is off.
    """
    if not OSWALD_BETRAYAL_KIT_ENABLED:
        return 'smack'
    if not OSWALD_STAIN_BURST_SECONDARY_ENABLED:
        return 'betrayal_lunge'
    if float(dist) <= oswaldBurstMeleeRange(stats):
        return 'stain_burst'
    return 'betrayal_lunge'


def oswaldLungeDashPos(sx, sy, tx, ty, dash=None, stop=None):
    """Planar Oswald position after dashing toward (tx, ty).

    Advances up to ``dash`` but never closer than ``stop`` to the toon so the
    lunge does not overshoot through them. Returns (sx, sy) if already inside
    the stop gap or coincident.
    """
    if dash is None:
        dash = OSWALD_BETRAYAL_LUNGE_DASH
    if stop is None:
        stop = OSWALD_BETRAYAL_LUNGE_STOP
    dash = max(0.0, float(dash))
    stop = max(0.0, float(stop))
    sx = float(sx)
    sy = float(sy)
    dx = float(tx) - sx
    dy = float(ty) - sy
    planar = (dx * dx + dy * dy) ** 0.5
    if planar <= stop or planar < 1e-6 or dash <= 0.0:
        return (sx, sy)
    step = min(dash, planar - stop)
    if step <= 0.0:
        return (sx, sy)
    return (sx + dx / planar * step, sy + dy / planar * step)


def oswaldBetrayalShoveDelta(sx, sy, tx, ty, dist=None):
    """Planar (dx, dy) to add to toon at (tx, ty) to shove away from Oswald.

    Opposite of :func:`snareLashYankDelta` — betrayal push, not string reel.
    Returns (0.0, 0.0) when ``dist`` is zero. Coincident toons shove along +Y.
    """
    if dist is None:
        dist = OSWALD_BETRAYAL_SHOVE_DIST
    dist = max(0.0, float(dist))
    if dist <= 0.0:
        return (0.0, 0.0)
    dx = float(tx) - float(sx)
    dy = float(ty) - float(sy)
    planar = (dx * dx + dy * dy) ** 0.5
    if planar < 1e-6:
        return (0.0, dist)
    return (dx / planar * dist, dy / planar * dist)


def oswaldBetrayalShovePos(sx, sy, tx, ty, dist=None):
    """Return (nx, ny) after applying :func:`oswaldBetrayalShoveDelta`."""
    ddx, ddy = oswaldBetrayalShoveDelta(sx, sy, tx, ty, dist=dist)
    return (float(tx) + ddx, float(ty) + ddy)


# Balloon Snare telegraph string-lash pop — short rubber-hose amber whip on
# announceAttackTelegraph (client only). Distinct from hit-time SNARE_LASH_*
# snap and from generic TELEGRAPH_INK_DRIP amber drips: horizontal lash silhouette.
SNARE_TELEGRAPH_STRING_LOOK = {
    'id': 'amber-string-lash',
    'lift': 2.05,
    'scale': 1.0,
    'peakAlpha': 0.96,
    'fadeInSec': 0.04,
    'holdSec': 0.14,
    'fadeOutSec': 0.22,
    'squash': (0.45, 1.0, 1.55),
    'stretch': (2.35, 1.0, 0.42),
    'squashSec': 0.05,
    'stretchSec': 0.1,
    'settleSec': 0.12,
    'whipDeg': 18.0,
    'stringHalfW': 0.55,
    'stringHalfH': 0.08,
    'knotHalf': 0.11,
    'tipHalf': 0.1,
    'stringColor': (0.95, 0.55, 0.12, 1.0),
    'tipColor': (1.15, 0.75, 0.28, 1.0),
    'flashColor': (1.25, 0.8, 0.35, 1.0),
    'streakCount': 3,
    'streakHalf': 0.12,
    'streakSec': 0.28,
    'streakSpread': 1.15,
    'streakColor': (1.05, 0.65, 0.22, 0.9),
    'binSort': 43,
}

# Balloon Snare string-snap counter window — after the amber string telegraph
# pops readable, open a short player punish window into melee. Synergizes with
# hackslash perfect-dodge counter (same rewarded opener path). Snare mid-
# telegraph melee can interrupt the wind-up so the zip-flier feels fair.
# Toontown spiritual-sequel tone — no keyblades / KH branding.
SNARE_STRING_COUNTER_ENABLED = True
# Seconds after announceAttackTelegraph before the counter window arms
# (lets the string-lash pop read first).
SNARE_STRING_COUNTER_ARM_DELAY_SEC = 0.14
# How long the rewarded counter→melee window stays open once armed.
SNARE_STRING_COUNTER_WINDOW_SEC = 0.48
# Planar range — only arm the local player's counter when this Snare is a
# readable melee threat (covers string-lash hit reach + a little slack).
SNARE_STRING_COUNTER_RANGE = 10.5
# Opener damage / play-rate multipliers while the string-snap counter is spent
# (match perfect-dodge counter feel so telegraph punish and dodge punish rhyme).
SNARE_STRING_COUNTER_DAMAGE_MULT = 1.5
SNARE_STRING_COUNTER_RATE_MULT = 1.2
# Cancel Snare wind-up when melee lands mid-telegraph (AI interrupt).
SNARE_STRING_COUNTER_INTERRUPT = True
# Extend the same snare-style mid-telegraph melee cancel to Punchline kits:
# Brute spit + Gagster lob wind-ups only (not Brute slam — tank secondary
# stays commit-through). AI path in
# DistributedCorruptToonAI.__maybeInterruptMeleeTelegraph.
# Dedicated counter→melee windows (below) are separate from interrupt cancel.
BRUTE_SPIT_MELEE_INTERRUPT = True
GAGSTER_LOB_MELEE_INTERRUPT = True
# Overlord climax telegraphs (rain / slam / ink_surge) — same mid-telegraph
# melee cancel as street kits so boss punish skill matches Punchline packs.
# Dedicated Overlord counter windows by move id are below (interrupt ≠ counter).
# No cream / no KH.
OVERLORD_RAIN_MELEE_INTERRUPT = True
OVERLORD_SLAM_MELEE_INTERRUPT = True
OVERLORD_INK_SURGE_MELEE_INTERRUPT = True
# Ink Smudge swarm telegraphs (ink_dash / ink_splat) — same mid-telegraph
# melee cancel as street kits / Overlord / Oswald so Act 1 + P2-add swarm
# punish skill matches the archetype ladder. Dedicated Smudge counters below.
# No cream / no KH.
INK_DASH_MELEE_INTERRUPT = True
INK_SPLAT_MELEE_INTERRUPT = True
# Corrupted Oswald betrayal telegraphs (betrayal_lunge / stain_burst) — same
# mid-telegraph melee cancel as Snare / Brute spit / Gagster lob so the twist
# chase punish skill matches Punchline kits. Shove stays hit-applied (not a
# telegraph move). Dedicated Oswald counter windows are below. No cream / no KH.
OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT = True
OSWALD_STAIN_BURST_MELEE_INTERRUPT = True
# Messenger name — DistributedCorruptToon → MeleeCombat thin hook.
SNARE_STRING_COUNTER_EVENT = 'corruptSnareStringSnapCounter'

# Sludge Brute spit telegraph → dedicated counter window (Snare-like).
# After the green spit-gob telegraph reads, arm a short punish→melee window.
# Distinct from mid-spit interrupt cancel and from slam (commit-through).
# No cream deepen in this window — gameplay timing only. No keyblades / KH.
BRUTE_SPIT_COUNTER_ENABLED = True
BRUTE_SPIT_COUNTER_ARM_DELAY_SEC = 0.22
BRUTE_SPIT_COUNTER_WINDOW_SEC = 0.55
# Planar range — spit engage + slack so a readable Brute can be punished.
BRUTE_SPIT_COUNTER_RANGE = 12.0
BRUTE_SPIT_COUNTER_DAMAGE_MULT = 1.5
BRUTE_SPIT_COUNTER_RATE_MULT = 1.2
BRUTE_SPIT_COUNTER_EVENT = 'corruptBruteSpitCounter'

# Gunk Gagster gag-lob telegraph → dedicated counter window (Snare-like).
# After the teal bounce-pie / puddle warn reads, arm a short punish→melee
# window. Distinct from mid-lob interrupt cancel. No cream / no KH.
GAGSTER_LOB_COUNTER_ENABLED = True
GAGSTER_LOB_COUNTER_ARM_DELAY_SEC = 0.18
GAGSTER_LOB_COUNTER_WINDOW_SEC = 0.52
# Planar range — lob kite ring + slack for a readable Gagster punish.
GAGSTER_LOB_COUNTER_RANGE = 11.0
GAGSTER_LOB_COUNTER_DAMAGE_MULT = 1.5
GAGSTER_LOB_COUNTER_RATE_MULT = 1.2
GAGSTER_LOB_COUNTER_EVENT = 'corruptGagsterLobCounter'

# Corrupted Oswald betrayal_lunge telegraph → dedicated counter window
# (Snare-like). After the crimson stain-lunge telegraph reads, arm a short
# punish→melee window. Distinct from mid-lunge interrupt cancel. Fits inside
# the short Oswald telegraphDelay. No cream / no KH.
OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED = True
OSWALD_BETRAYAL_LUNGE_COUNTER_ARM_DELAY_SEC = 0.12
OSWALD_BETRAYAL_LUNGE_COUNTER_WINDOW_SEC = 0.48
# Planar range — lunge engage + dash slack so a readable Oswald can be punished.
OSWALD_BETRAYAL_LUNGE_COUNTER_RANGE = 9.0
OSWALD_BETRAYAL_LUNGE_COUNTER_DAMAGE_MULT = 1.5
OSWALD_BETRAYAL_LUNGE_COUNTER_RATE_MULT = 1.2
OSWALD_BETRAYAL_LUNGE_COUNTER_EVENT = 'corruptOswaldBetrayalLungeCounter'

# Corrupted Oswald stain_burst telegraph → dedicated counter window
# (Snare-like). After the close crimson burst telegraph reads, arm a short
# punish→melee window. Distinct from mid-burst interrupt cancel. Fits inside
# burstTelegraphDelay. No cream / no KH.
OSWALD_STAIN_BURST_COUNTER_ENABLED = True
OSWALD_STAIN_BURST_COUNTER_ARM_DELAY_SEC = 0.10
OSWALD_STAIN_BURST_COUNTER_WINDOW_SEC = 0.44
# Planar range — close burst engage + slack for a readable face-range punish.
OSWALD_STAIN_BURST_COUNTER_RANGE = 7.0
OSWALD_STAIN_BURST_COUNTER_DAMAGE_MULT = 1.5
OSWALD_STAIN_BURST_COUNTER_RATE_MULT = 1.2
OSWALD_STAIN_BURST_COUNTER_EVENT = 'corruptOswaldStainBurstCounter'

# Ink Overlord rain telegraph → dedicated counter window (Snare-like).
# After the magenta rain / danger-ring telegraph reads, arm a short
# punish→melee window by move id. Distinct from mid-rain interrupt cancel.
# Fits inside the shorter P2 rain telegraphDelay. No cream / no KH.
OVERLORD_RAIN_COUNTER_ENABLED = True
OVERLORD_RAIN_COUNTER_ARM_DELAY_SEC = 0.22
OVERLORD_RAIN_COUNTER_WINDOW_SEC = 0.55
# Planar range — rain puddle near-miss + slack so a readable Overlord can
# be punished from the mid-range rain band.
OVERLORD_RAIN_COUNTER_RANGE = 15.0
OVERLORD_RAIN_COUNTER_DAMAGE_MULT = 1.5
OVERLORD_RAIN_COUNTER_RATE_MULT = 1.2
OVERLORD_RAIN_COUNTER_EVENT = 'corruptOverlordRainCounter'

# Ink Overlord slam telegraph → dedicated counter window (Snare-like).
# After the close slam danger-ring telegraph reads, arm a short
# punish→melee window. Distinct from mid-slam interrupt cancel. Fits inside
# the shorter P2 slamTelegraphDelay. No cream / no KH.
OVERLORD_SLAM_COUNTER_ENABLED = True
OVERLORD_SLAM_COUNTER_ARM_DELAY_SEC = 0.12
OVERLORD_SLAM_COUNTER_WINDOW_SEC = 0.42
# Planar range — slam near-miss + slack for a readable close-range punish.
OVERLORD_SLAM_COUNTER_RANGE = 8.5
OVERLORD_SLAM_COUNTER_DAMAGE_MULT = 1.5
OVERLORD_SLAM_COUNTER_RATE_MULT = 1.2
OVERLORD_SLAM_COUNTER_EVENT = 'corruptOverlordSlamCounter'

# Ink Overlord ink_surge telegraph → dedicated counter window (Snare-like).
# After the mid surge danger-ring telegraph reads, arm a short
# punish→melee window. Distinct from mid-surge interrupt cancel. Fits inside
# surgeTelegraphDelay. No cream / no KH.
OVERLORD_INK_SURGE_COUNTER_ENABLED = True
OVERLORD_INK_SURGE_COUNTER_ARM_DELAY_SEC = 0.14
OVERLORD_INK_SURGE_COUNTER_WINDOW_SEC = 0.48
# Planar range — surge near-miss + slack for a readable mid-range punish.
OVERLORD_INK_SURGE_COUNTER_RANGE = 10.0
OVERLORD_INK_SURGE_COUNTER_DAMAGE_MULT = 1.5
OVERLORD_INK_SURGE_COUNTER_RATE_MULT = 1.2
OVERLORD_INK_SURGE_COUNTER_EVENT = 'corruptOverlordInkSurgeCounter'

# Ink Smudge ink_dash telegraph → dedicated counter window (Snare-like).
# After the purple ink-fist rush telegraph reads, arm a short punish→melee
# window. Distinct from mid-dash interrupt cancel. Fits inside telegraphDelay.
# No cream / no KH.
INK_DASH_COUNTER_ENABLED = True
INK_DASH_COUNTER_ARM_DELAY_SEC = 0.16
INK_DASH_COUNTER_WINDOW_SEC = 0.50
# Planar range — dash engage + rush slack so a readable Smudge can be punished.
INK_DASH_COUNTER_RANGE = 8.5
INK_DASH_COUNTER_DAMAGE_MULT = 1.5
INK_DASH_COUNTER_RATE_MULT = 1.2
INK_DASH_COUNTER_EVENT = 'corruptInkDashCounter'

# Ink Smudge ink_splat telegraph → dedicated counter window (Snare-like).
# After the close purple splat telegraph reads, arm a short punish→melee
# window. Distinct from mid-splat interrupt cancel. Fits inside
# splatTelegraphDelay. No cream / no KH.
INK_SPLAT_COUNTER_ENABLED = True
INK_SPLAT_COUNTER_ARM_DELAY_SEC = 0.12
INK_SPLAT_COUNTER_WINDOW_SEC = 0.46
# Planar range — close splat engage + slack for a readable face-range punish.
INK_SPLAT_COUNTER_RANGE = 6.5
INK_SPLAT_COUNTER_DAMAGE_MULT = 1.5
INK_SPLAT_COUNTER_RATE_MULT = 1.2
INK_SPLAT_COUNTER_EVENT = 'corruptInkSplatCounter'


def isMeleeInterruptibleTelegraph(archetype, move):
    """True when stretch-punch mid-telegraph should cancel this wind-up.

    Snare: any string telegraph when SNARE_STRING_COUNTER_INTERRUPT.
    Brute: spit only (slam stays commit-through).
    Gagster: gag_lob only.
    Overlord (ARCHETYPE_INK + rain/slam/ink_surge move ids): when the matching
    OVERLORD_*_MELEE_INTERRUPT flag is on — climax punish parity with street kits.
    Smudge (ARCHETYPE_INK + ink_dash / ink_splat): when the matching
    INK_*_MELEE_INTERRUPT flag is on — Act 1 / P2-add swarm punish parity.
    Oswald (ARCHETYPE_CORRUPT_OSWALD + betrayal_lunge / stain_burst): when the
    matching OSWALD_*_MELEE_INTERRUPT flag is on — twist chase punish parity.
    """
    aid = normalizeArchetype(archetype)
    moveName = str(move or 'smack')
    if aid == ARCHETYPE_SNARE:
        return bool(SNARE_STRING_COUNTER_INTERRUPT)
    if aid == ARCHETYPE_BRUTE and moveName == 'spit':
        return bool(BRUTE_SPIT_MELEE_INTERRUPT)
    if aid == ARCHETYPE_GAGSTER and moveName == 'gag_lob':
        return bool(GAGSTER_LOB_MELEE_INTERRUPT)
    # Overlord + Smudge share ARCHETYPE_INK; move ids distinguish kits.
    # Smudge never telegraphs rain / slam / ink_surge; Overlord never
    # telegraphs ink_dash / ink_splat.
    if aid == ARCHETYPE_INK:
        if moveName == 'rain':
            return bool(OVERLORD_RAIN_MELEE_INTERRUPT)
        if moveName == 'slam':
            return bool(OVERLORD_SLAM_MELEE_INTERRUPT)
        if moveName == 'ink_surge':
            return bool(OVERLORD_INK_SURGE_MELEE_INTERRUPT)
        if moveName == 'ink_dash':
            return bool(INK_DASH_MELEE_INTERRUPT)
        if moveName == 'ink_splat':
            return bool(INK_SPLAT_MELEE_INTERRUPT)
    if aid == ARCHETYPE_CORRUPT_OSWALD:
        # Default attackMove is betrayal_lunge; empty/smack aliases the lunge.
        if moveName in ('betrayal_lunge', 'smack', ''):
            return bool(OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT)
        if moveName == 'stain_burst':
            return bool(OSWALD_STAIN_BURST_MELEE_INTERRUPT)
    return False


def snareStringCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after a Snare string-snap counter."""
    if mult is None:
        mult = SNARE_STRING_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def snareStringCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after a Snare string-snap counter."""
    if mult is None:
        mult = SNARE_STRING_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isSnareStringCounterWindowOpen(armed, until, now):
    """True while a Balloon Snare string-snap counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def snareStringCounterArmAt(now, delay=None):
    """Absolute time when the string-snap counter should arm after telegraph."""
    if delay is None:
        delay = SNARE_STRING_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def snareStringCounterUntil(armedAt, window=None):
    """Absolute expiry for a string-snap counter window armed at armedAt."""
    if window is None:
        window = SNARE_STRING_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def isDedicatedTelegraphCounterMove(archetype, move):
    """True when this telegraph should arm a Snare-like dedicated counter window.

    Snare: any string telegraph when SNARE_STRING_COUNTER_ENABLED.
    Brute: spit only (slam stays commit-through, no counter).
    Gagster: gag_lob only.
    Oswald: betrayal_lunge / stain_burst when the matching COUNTER_ENABLED flag.
    Overlord (ARCHETYPE_INK + rain/slam/ink_surge): when the matching
    OVERLORD_*_COUNTER_ENABLED flag is on — climax punish parity with street
    kits after move-id telegraph + melee interrupt.
    Smudge (ARCHETYPE_INK + ink_dash / ink_splat): when the matching
    INK_*_COUNTER_ENABLED flag is on — Act 1 / P2-add swarm punish parity.
    Interrupt cancel (isMeleeInterruptibleTelegraph) is separate.
    """
    aid = normalizeArchetype(archetype)
    moveName = str(move or 'smack')
    if aid == ARCHETYPE_SNARE:
        return bool(SNARE_STRING_COUNTER_ENABLED)
    if aid == ARCHETYPE_BRUTE and moveName == 'spit':
        return bool(BRUTE_SPIT_COUNTER_ENABLED)
    if aid == ARCHETYPE_GAGSTER and moveName == 'gag_lob':
        return bool(GAGSTER_LOB_COUNTER_ENABLED)
    if aid == ARCHETYPE_CORRUPT_OSWALD:
        if moveName in ('betrayal_lunge', 'smack', ''):
            return bool(OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED)
        if moveName == 'stain_burst':
            return bool(OSWALD_STAIN_BURST_COUNTER_ENABLED)
    # Overlord + Smudge share ARCHETYPE_INK; move ids distinguish kits.
    if aid == ARCHETYPE_INK:
        if moveName == 'rain':
            return bool(OVERLORD_RAIN_COUNTER_ENABLED)
        if moveName == 'slam':
            return bool(OVERLORD_SLAM_COUNTER_ENABLED)
        if moveName == 'ink_surge':
            return bool(OVERLORD_INK_SURGE_COUNTER_ENABLED)
        if moveName == 'ink_dash':
            return bool(INK_DASH_COUNTER_ENABLED)
        if moveName == 'ink_splat':
            return bool(INK_SPLAT_COUNTER_ENABLED)
    return False


def bruteSpitCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after a Brute spit counter."""
    if mult is None:
        mult = BRUTE_SPIT_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def bruteSpitCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after a Brute spit counter."""
    if mult is None:
        mult = BRUTE_SPIT_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isBruteSpitCounterWindowOpen(armed, until, now):
    """True while a Sludge Brute spit counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def bruteSpitCounterArmAt(now, delay=None):
    """Absolute time when the spit counter should arm after telegraph."""
    if delay is None:
        delay = BRUTE_SPIT_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def bruteSpitCounterUntil(armedAt, window=None):
    """Absolute expiry for a spit counter window armed at armedAt."""
    if window is None:
        window = BRUTE_SPIT_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def gagsterLobCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after a Gagster lob counter."""
    if mult is None:
        mult = GAGSTER_LOB_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def gagsterLobCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after a Gagster lob counter."""
    if mult is None:
        mult = GAGSTER_LOB_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isGagsterLobCounterWindowOpen(armed, until, now):
    """True while a Gunk Gagster lob counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def gagsterLobCounterArmAt(now, delay=None):
    """Absolute time when the lob counter should arm after telegraph."""
    if delay is None:
        delay = GAGSTER_LOB_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def gagsterLobCounterUntil(armedAt, window=None):
    """Absolute expiry for a lob counter window armed at armedAt."""
    if window is None:
        window = GAGSTER_LOB_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def oswaldBetrayalLungeCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after an Oswald betrayal-lunge counter."""
    if mult is None:
        mult = OSWALD_BETRAYAL_LUNGE_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def oswaldBetrayalLungeCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after an Oswald lunge counter."""
    if mult is None:
        mult = OSWALD_BETRAYAL_LUNGE_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isOswaldBetrayalLungeCounterWindowOpen(armed, until, now):
    """True while a Corrupted Oswald betrayal-lunge counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def oswaldBetrayalLungeCounterArmAt(now, delay=None):
    """Absolute time when the betrayal-lunge counter should arm after telegraph."""
    if delay is None:
        delay = OSWALD_BETRAYAL_LUNGE_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def oswaldBetrayalLungeCounterUntil(armedAt, window=None):
    """Absolute expiry for a betrayal-lunge counter window armed at armedAt."""
    if window is None:
        window = OSWALD_BETRAYAL_LUNGE_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def oswaldStainBurstCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after an Oswald stain-burst counter."""
    if mult is None:
        mult = OSWALD_STAIN_BURST_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def oswaldStainBurstCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after an Oswald stain-burst counter."""
    if mult is None:
        mult = OSWALD_STAIN_BURST_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isOswaldStainBurstCounterWindowOpen(armed, until, now):
    """True while a Corrupted Oswald stain-burst counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def oswaldStainBurstCounterArmAt(now, delay=None):
    """Absolute time when the stain-burst counter should arm after telegraph."""
    if delay is None:
        delay = OSWALD_STAIN_BURST_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def oswaldStainBurstCounterUntil(armedAt, window=None):
    """Absolute expiry for a stain-burst counter window armed at armedAt."""
    if window is None:
        window = OSWALD_STAIN_BURST_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def overlordRainCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after an Overlord rain counter."""
    if mult is None:
        mult = OVERLORD_RAIN_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def overlordRainCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after an Overlord rain counter."""
    if mult is None:
        mult = OVERLORD_RAIN_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isOverlordRainCounterWindowOpen(armed, until, now):
    """True while an Overlord rain counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def overlordRainCounterArmAt(now, delay=None):
    """Absolute time when the rain counter should arm after telegraph."""
    if delay is None:
        delay = OVERLORD_RAIN_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def overlordRainCounterUntil(armedAt, window=None):
    """Absolute expiry for a rain counter window armed at armedAt."""
    if window is None:
        window = OVERLORD_RAIN_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def overlordSlamCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after an Overlord slam counter."""
    if mult is None:
        mult = OVERLORD_SLAM_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def overlordSlamCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after an Overlord slam counter."""
    if mult is None:
        mult = OVERLORD_SLAM_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isOverlordSlamCounterWindowOpen(armed, until, now):
    """True while an Overlord slam counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def overlordSlamCounterArmAt(now, delay=None):
    """Absolute time when the slam counter should arm after telegraph."""
    if delay is None:
        delay = OVERLORD_SLAM_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def overlordSlamCounterUntil(armedAt, window=None):
    """Absolute expiry for a slam counter window armed at armedAt."""
    if window is None:
        window = OVERLORD_SLAM_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def overlordInkSurgeCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after an Overlord ink_surge counter."""
    if mult is None:
        mult = OVERLORD_INK_SURGE_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def overlordInkSurgeCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after an Overlord ink_surge counter."""
    if mult is None:
        mult = OVERLORD_INK_SURGE_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isOverlordInkSurgeCounterWindowOpen(armed, until, now):
    """True while an Overlord ink_surge counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def overlordInkSurgeCounterArmAt(now, delay=None):
    """Absolute time when the ink_surge counter should arm after telegraph."""
    if delay is None:
        delay = OVERLORD_INK_SURGE_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def overlordInkSurgeCounterUntil(armedAt, window=None):
    """Absolute expiry for an ink_surge counter window armed at armedAt."""
    if window is None:
        window = OVERLORD_INK_SURGE_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def inkDashCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after an Ink Smudge ink_dash counter."""
    if mult is None:
        mult = INK_DASH_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def inkDashCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after an Ink Smudge ink_dash counter."""
    if mult is None:
        mult = INK_DASH_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isInkDashCounterWindowOpen(armed, until, now):
    """True while an Ink Smudge ink_dash counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def inkDashCounterArmAt(now, delay=None):
    """Absolute time when the ink_dash counter should arm after telegraph."""
    if delay is None:
        delay = INK_DASH_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def inkDashCounterUntil(armedAt, window=None):
    """Absolute expiry for an ink_dash counter window armed at armedAt."""
    if window is None:
        window = INK_DASH_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


def inkSplatCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after an Ink Smudge ink_splat counter."""
    if mult is None:
        mult = INK_SPLAT_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def inkSplatCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after an Ink Smudge ink_splat counter."""
    if mult is None:
        mult = INK_SPLAT_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isInkSplatCounterWindowOpen(armed, until, now):
    """True while an Ink Smudge ink_splat counter→melee window is live."""
    return bool(armed) and float(now) < float(until)


def inkSplatCounterArmAt(now, delay=None):
    """Absolute time when the ink_splat counter should arm after telegraph."""
    if delay is None:
        delay = INK_SPLAT_COUNTER_ARM_DELAY_SEC
    return float(now) + max(0.0, float(delay))


def inkSplatCounterUntil(armedAt, window=None):
    """Absolute expiry for an ink_splat counter window armed at armedAt."""
    if window is None:
        window = INK_SPLAT_COUNTER_WINDOW_SEC
    return float(armedAt) + max(0.0, float(window))


# Cream splash + delayed cream aftershock on successful Balloon Snare
# string-snap punish/counter (#203 window). Sunny cream / pastel contrast
# against amber SnareStringSnapSplashFx so the rewarded hit reads juicy.
# Deepened string-snap juice beyond #269 (#245 deepen): juicier splat/flecks
# + thicker horizontal cream whip filaments (rubber-string break read) +
# wider sideways settle aftershock — distinct from Gunk puddle cream deepen
# (#276 / #238, flat ground bloom), Smudge hit cream deepen (#283 / #259,
# radial hose smears), and Brute spit cream deepen (#289 / #264, vertical
# drip). Same residual grammar as TELEGRAPH_CREAM_WARN_AFTERSHOCK_*.
# Client only. No keyblades / KH branding.
# SNARE_STRING_COUNTER_CREAM_SPLASH_ENABLED = False drops splash + aftershock.
# SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_ENABLED = False drops aftershock only.
# SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_ENABLED = False drops whip filaments only.
SNARE_STRING_COUNTER_CREAM_SPLASH_ENABLED = True
# Extra seconds after the counter window expires where a late swing hit may
# still earn cream juice (covers stretch-punch hit delay after F spend).
SNARE_STRING_COUNTER_CREAM_HIT_GRACE_SEC = 0.28
SNARE_STRING_COUNTER_CREAM_SPLASH_DELAY_SEC = 0.035  # fallback; look prefers amber compose
SNARE_STRING_COUNTER_CREAM_SPLASH_BIN = 46  # above amber snap splash (45)
SNARE_STRING_COUNTER_CREAM_SPLASH_COLOR = (1.0, 0.97, 0.82, 0.99)  # sunny cream
SNARE_STRING_COUNTER_CREAM_SPLASH_RIM_COLOR = (1.0, 0.98, 0.88, 0.86)
SNARE_STRING_COUNTER_CREAM_SPLASH_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.97),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.88),   # soft peach pastel
    (1.0, 0.94, 0.7, 0.86),   # warm lemon pastel — string snap pop
)
# Horizontal cream whip filaments — rubber-string break readability (not
# Gunk flat puddle bloom / Smudge radial hose / Brute vertical drip).
SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_ENABLED = True
SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_COUNT = 4  # beyond #269 (3)
SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_HALF = 0.14
SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_SPREAD = 1.5  # wider string whip (beyond #269 1.32)
SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_SEC = 0.26
SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_PEAK_ALPHA = 0.95
SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_COLOR = (1.0, 0.97, 0.84, 0.96)
SNARE_STRING_COUNTER_CREAM_SPLASH_LOOK = {
    'id': 'snare-string-counter-cream-splash',
    # lift / delaySec composed with snareStringSnapSplashLook('hit') when played.
    'lift': 1.95,
    'delaySec': SNARE_STRING_COUNTER_CREAM_SPLASH_DELAY_SEC,
    'delayScale': 0.2,  # snappier pop as amber snap settles (beyond #269 0.24)
    'peakAlpha': 0.99,
    'splatHalf': 0.36,  # juicier counter core vs #269 (0.32) / #245 (0.28)
    'splatPeak': 2.0,
    'splatSec': 0.21,
    'rimScale': 1.5,
    'splatColor': SNARE_STRING_COUNTER_CREAM_SPLASH_COLOR,
    'rimColor': SNARE_STRING_COUNTER_CREAM_SPLASH_RIM_COLOR,
    'fleckCount': 7,  # beyond #269 (6) / #245 (5); string whip spray beside Gunk bloom
    'fleckHalf': 0.13,
    'fleckDist': 1.5,  # wider horizontal whip spray (beyond #269 1.35)
    'fleckLift': 0.26,  # stay near string-lash height (vs Smudge/Brute taller spray)
    'fleckSec': 0.28,
    'fleckColors': SNARE_STRING_COUNTER_CREAM_SPLASH_FLECK_COLORS,
    'whipEnabled': SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_ENABLED,
    'whipCount': SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_COUNT,
    'whipHalf': SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_HALF,
    'whipSpread': SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_SPREAD,
    'whipSec': SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_SEC,
    'whipPeakAlpha': SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_PEAK_ALPHA,
    'whipColor': SNARE_STRING_COUNTER_CREAM_SPLASH_WHIP_COLOR,
    'binSort': SNARE_STRING_COUNTER_CREAM_SPLASH_BIN,
}
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_ENABLED = True
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_DELAY_SEC = 0.1
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_COUNT = 6  # beyond #269 (5) / #245 (4)
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_STREAK_COUNT = 4
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_SIZE = 0.13
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_STREAK_SIZE = 0.16
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_DRIFT = 1.12  # wider horizontal settle (beyond #269 0.98)
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_FALL = 0.3  # lighter fall — string lash stays sideways
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_SEC = 0.4
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.94)
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.92)
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_ENABLED = True
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_HALF = 0.7  # wider string-lash halo (beyond #269 0.6)
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_START = 0.26
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_PEAK = 1.9
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_SEC = 0.36
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.32
SNARE_STRING_COUNTER_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)


def isSnareStringCounterCreamSplashEligible(armed, until, now, grace=None):
    """True while a successful string-snap counter hit may fire cream splash.

    Extends the live counter window by a short hit-grace so stretch-punch
    contact that lands just after F spend still earns the cream juice.
    """
    if not armed:
        return False
    if grace is None:
        grace = SNARE_STRING_COUNTER_CREAM_HIT_GRACE_SEC
    return float(now) < (float(until) + max(0.0, float(grace)))


# Gunk Gagster gag-lob — teal bounce-bomb wind-up, arcing pie lob, puddle splat.
# Reads apart from Brute spit (green linear), Snare lash (amber horizontal),
# and Smudge melee (purple squash).
GAGSTER_TELEGRAPH_CHARGE_COLOR = (0.35, 2.05, 2.25, 1.0)
GAGSTER_TELEGRAPH_HOLD_COLOR = (0.25, 1.55, 1.75, 1.0)
GAGSTER_TELEGRAPH_SQUASH = (1.35, 1.35, 0.55)  # wind-up crouch before lob
GAGSTER_TELEGRAPH_MID = (0.85, 0.85, 1.45)
GAGSTER_TELEGRAPH_STRETCH = (0.7, 0.7, 1.85)  # toss stretch upward
GAGSTER_TELEGRAPH_SFX = 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg'
GAGSTER_TELEGRAPH_SFX_VOLUME = 0.7
GAGSTER_ATTACK_HIT_SFX = 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg'
GAGSTER_ATTACK_HIT_SFX_VOLUME = 0.82
GAGSTER_HIT_FLASH_COLOR = (0.35, 0.95, 1.05, 1.0)
GAGSTER_HIT_FLASH_PEAK = 0.6
# Client-only arcing gunk pie that lob-lands as a puddle ring on hit resolve.
GAGSTER_LOB_COLOR = (0.15, 0.78, 0.85, 0.94)
GAGSTER_LOB_SCALE = 0.48
GAGSTER_LOB_TRAVEL = 0.34
GAGSTER_LOB_ARC_Z = 3.8
GAGSTER_LOB_Z = 2.3
GAGSTER_PUDDLE_COLOR = (0.12, 0.62, 0.7, 0.88)
GAGSTER_PUDDLE_HALF = 1.15
GAGSTER_PUDDLE_PEAK = 2.35
GAGSTER_PUDDLE_SEC = 0.28

# Lingering sludge hazard after Gunk Gagster puddle land (gameplay trap).
# Initial resolve stays a one-shot AoE at wind-up XY; then the puddle ticks
# DoT and stamps a short slow while toons stay inside. Punchline identity —
# not cream FX deepen. GAGSTER_PUDDLE_LINGER_ENABLED = False restores
# one-shot-only land damage.
GAGSTER_PUDDLE_LINGER_ENABLED = True
GAGSTER_PUDDLE_LINGER_SEC = 2.5
GAGSTER_PUDDLE_LINGER_TICK_SEC = 0.5
GAGSTER_PUDDLE_LINGER_TICK_DAMAGE = 1
# Planar radius fallback when archetype attackHitRange is missing.
GAGSTER_PUDDLE_LINGER_RADIUS = 5.0
# Client walk slow + AI stamp refresh while standing in sludge.
GAGSTER_PUDDLE_LINGER_SLOW_FACTOR = 0.55
GAGSTER_PUDDLE_LINGER_SLOW_SEC = 0.65


def gagsterPuddleLingerUntil(landAt, lingerSec=None):
    """Absolute expiry for a Gunk Gagster linger sludge hazard."""
    if lingerSec is None:
        lingerSec = GAGSTER_PUDDLE_LINGER_SEC
    return float(landAt) + max(0.0, float(lingerSec))


def gagsterPuddleLingerTickCount(lingerSec=None, tickSec=None):
    """How many DoT ticks fit inside a linger window (excludes land hit)."""
    if lingerSec is None:
        lingerSec = GAGSTER_PUDDLE_LINGER_SEC
    if tickSec is None:
        tickSec = GAGSTER_PUDDLE_LINGER_TICK_SEC
    linger = max(0.0, float(lingerSec))
    tick = max(0.05, float(tickSec))
    if linger <= 0.0:
        return 0
    # First tick fires after one interval; last tick must still be < until.
    return int(linger // tick)


def isInsideGagsterPuddle(dx, dy, radius):
    """True when planar offset is inside the linger / land puddle radius."""
    r = max(0.0, float(radius))
    return (float(dx) * float(dx) + float(dy) * float(dy)) <= (r * r)


def isGagsterPuddleSlowActive(until, now):
    """True while an AI-stamped Gagster sludge slow window is live."""
    return float(now) < float(until)


def gagsterPuddleSlowUntil(now, slowSec=None):
    """Absolute expiry for a sludge-slow refresh stamped on a tick."""
    if slowSec is None:
        slowSec = GAGSTER_PUDDLE_LINGER_SLOW_SEC
    return float(now) + max(0.0, float(slowSec))


def gagsterPuddleLingerTickDamage(stats=None):
    """Per-tick DoT while standing in linger sludge (min 1 when enabled)."""
    if stats is None:
        stats = {}
    raw = stats.get(
        'puddleLingerTickDamage', GAGSTER_PUDDLE_LINGER_TICK_DAMAGE)
    return max(1, int(raw))


# Cream splash + delayed cream aftershock on Gunk Gagster puddle land /
# splash (after telegraph puddle warn #197). Sunny cream / pastel contrast
# against teal GAGSTER_PUDDLE_* so the trap impact reads juicy. Deepened
# ground-trap juice beyond #276 (#238 deepen): juicier splat/flecks +
# thicker flat cream bloom on the puddle plane + wider settle aftershock —
# distinct from Smudge hit cream deepen (#283 / #259, radial hose), Brute
# spit cream deepen (#289 / #264, vertical drip), and Snare counter cream
# deepen (#293 / #269, horizontal whip). Same residual grammar as
# TELEGRAPH_CREAM_WARN_AFTERSHOCK_* / Snare counter cream splash (#214).
# Client only. No keyblades / KH branding.
# GAGSTER_PUDDLE_CREAM_SPLASH_ENABLED = False drops splash + aftershock.
# GAGSTER_PUDDLE_CREAM_AFTERSHOCK_ENABLED = False drops aftershock only.
# GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_ENABLED = False drops ground bloom only.
GAGSTER_PUDDLE_CREAM_SPLASH_ENABLED = True
GAGSTER_PUDDLE_CREAM_SPLASH_DELAY_SEC = 0.035  # fallback; look prefers puddle compose
GAGSTER_PUDDLE_CREAM_SPLASH_LIFT = 0.56  # above flat teal puddle ring (beyond #276 0.52)
GAGSTER_PUDDLE_CREAM_SPLASH_BIN = 40  # above teal puddle (38)
GAGSTER_PUDDLE_CREAM_SPLASH_COLOR = (1.0, 0.97, 0.82, 0.99)  # sunny cream
GAGSTER_PUDDLE_CREAM_SPLASH_RIM_COLOR = (1.0, 0.98, 0.88, 0.86)
GAGSTER_PUDDLE_CREAM_SPLASH_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.97),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.88),   # soft peach pastel
    (1.0, 0.94, 0.7, 0.86),   # warm lemon pastel — trap pop
)
# Flat cream bloom on the puddle plane — ground-trap readability (not
# Smudge mid-body billboard / Brute spit drip / Snare whip).
GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_ENABLED = True
GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_HALF = 1.0  # beyond #276 (0.85)
GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_PEAK = 2.65  # thicker trap-plane bloom
GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_SEC = 0.32
GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_PEAK_ALPHA = 0.72
GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_COLOR = (1.0, 0.97, 0.84, 0.8)
GAGSTER_PUDDLE_CREAM_SPLASH_LOOK = {
    'id': 'gagster-puddle-cream-splash',
    # lift / delaySec composed with GAGSTER_PUDDLE_SEC when played.
    'lift': GAGSTER_PUDDLE_CREAM_SPLASH_LIFT,
    'delaySec': GAGSTER_PUDDLE_CREAM_SPLASH_DELAY_SEC,
    'delayScale': 0.12,  # snappier pop as teal puddle blooms (beyond #276 0.15)
    'peakAlpha': 0.99,
    'splatHalf': 0.4,  # juicier trap land core vs #276 (0.36) / #238 (0.32)
    'splatPeak': 2.15,
    'splatSec': 0.22,
    'rimScale': 1.52,
    'splatColor': GAGSTER_PUDDLE_CREAM_SPLASH_COLOR,
    'rimColor': GAGSTER_PUDDLE_CREAM_SPLASH_RIM_COLOR,
    'fleckCount': 8,  # beyond #276 (7) / #238 (6)
    'fleckHalf': 0.14,
    'fleckDist': 1.65,  # wider puddle-plane spray (beyond #276 1.5)
    'fleckLift': 0.4,  # stay low over the trap ring
    'fleckSec': 0.3,
    'fleckColors': GAGSTER_PUDDLE_CREAM_SPLASH_FLECK_COLORS,
    'bloomEnabled': GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_ENABLED,
    'bloomHalf': GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_HALF,
    'bloomPeak': GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_PEAK,
    'bloomSec': GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_SEC,
    'bloomPeakAlpha': GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_PEAK_ALPHA,
    'bloomColor': GAGSTER_PUDDLE_CREAM_SPLASH_BLOOM_COLOR,
    'binSort': GAGSTER_PUDDLE_CREAM_SPLASH_BIN,
}
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_ENABLED = True
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_DELAY_SEC = 0.1
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_COUNT = 7  # beyond #276 (6) trap residual
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_STREAK_COUNT = 4
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_SIZE = 0.14
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_STREAK_SIZE = 0.16
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_DRIFT = 1.25  # wider settle across puddle plane
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_FALL = 0.3  # soft onto the trap ring
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_SEC = 0.42
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.94)
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.92)
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_ENABLED = True
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_HALF = 0.78  # wider puddle-plane halo (beyond #276 0.68)
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_START = 0.26
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_PEAK = 2.05
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_SEC = 0.38
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.34
GAGSTER_PUDDLE_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Gunk Gagster telegraph puddle warn — short rubber-hose teal bounce-pie +
# cream/ink ground puddle warn on announceAttackTelegraph (client only).
# Distinct from hit-time GAGSTER_LOB_* / GAGSTER_PUDDLE_* and from Brute spit /
# Snare string / Smudge fist telegraphs: lob charge silhouette + landing trap
# warn so Punchline players can dodge out during wind-up.
GAGSTER_TELEGRAPH_PUDDLE_LOOK = {
    'id': 'teal-gag-puddle-warn',
    'lift': 2.35,
    'scale': 1.0,
    'peakAlpha': 0.97,
    'fadeInSec': 0.04,
    'holdSec': 0.18,
    'fadeOutSec': 0.26,
    'squash': (1.55, 1.0, 0.48),
    'stretch': (0.62, 1.0, 2.05),
    'squashSec': 0.05,
    'stretchSec': 0.12,
    'settleSec': 0.14,
    'bounceDeg': 14.0,
    'pieHalf': 0.36,
    'rimScale': 1.3,
    'hotHalf': 0.13,
    'pieColor': (0.18, 0.82, 0.88, 1.0),
    'creamRimColor': (1.15, 1.05, 0.82, 1.0),
    'flashColor': (0.45, 1.35, 1.45, 1.0),
    'dropletCount': 4,
    'dropletHalf': 0.09,
    'dropletSec': 0.3,
    'dropletSpread': 0.85,
    'dropletColor': (0.22, 0.85, 0.9, 0.9),
    # Ground cream/ink puddle warn at predicted lob landing.
    'puddleLift': 0.1,
    'puddleHalf': 1.05,
    'puddlePeak': 2.2,
    'puddleDelay': 0.06,
    'puddleInSec': 0.14,
    'puddleHoldSec': 0.28,
    'puddleOutSec': 0.32,
    'puddleInkColor': (0.12, 0.62, 0.72, 0.82),
    'puddleCreamColor': (1.12, 1.02, 0.78, 0.72),
    'puddleCreamScale': 1.22,
    'puddleCreamPeakScale': 1.12,
    'creamFleckCount': 5,
    'creamFleckHalf': 0.1,
    'creamFleckSec': 0.34,
    'creamFleckSpread': 1.05,
    'creamFleckLift': 0.55,
    'creamFleckColor': (1.15, 1.05, 0.8, 0.92),
    'binSort': 44,
}

# Defeat pop juice — rubber-hose ink splat / balloon pop on announceDefeat.
# Per-archetype palette so Smudge (purple), Brute (green), Snare (amber) read.
# Cream fleck burst (DEATH_CREAM_FLECK_*) layers sunny purity chips on top via
# CorruptDeathCreamFleckFx — not ink. Toggle DEATH_CREAM_FLECK_ENABLED.
# Rising cream sparkles (DEATH_CREAM_SPARKLE_*) rise from the fleck burst via
# CorruptDeathCreamSparkleFx — telegraph / silhouette cream sparkle grammar.
# Toggle DEATH_CREAM_SPARKLE_ENABLED.
# Soft cream wash (DEATH_CREAM_WASH_*) pulses after the fleck burst via
# CorruptDeathCreamWashFx — reclaim purity-wash grammar; delayed cream
# aftershock (DEATH_CREAM_WASH_AFTERSHOCK_*) settles after wash / sparkle
# (#132 / #136 grammar). Toggle DEATH_CREAM_WASH_ENABLED /
# DEATH_CREAM_WASH_AFTERSHOCK_ENABLED.
DEATH_POP_SFX_VOLUME = 0.78
DEATH_POP_LOOK = {
    ARCHETYPE_INK: {
        'id': 'ink-splat',
        'burstScale': (1.75, 1.75, 1.75),
        'pancakeScale': (2.15, 2.15, 0.1),
        'vanishScale': (0.02, 0.02, 0.02),
        'burstSec': 0.07,
        'pancakeSec': 0.12,
        'vanishSec': 0.18,
        'burstColor': (2.0, 1.35, 2.4, 1.0),
        'pancakeColor': (1.55, 0.85, 1.9, 1.0),
        'fadeColor': (1.2, 1.35, 1.05, 0.0),
        'lift': 1.35,
        'ringHalf': 0.85,
        'ringPeak': 2.6,
        'ringSec': 0.32,
        'ringColor': (0.55, 0.2, 0.85, 0.9),
        'dropletCount': 8,
        'dropletHalf': 0.28,
        'dropletDist': 2.4,
        'dropletLift': 1.1,
        'dropletSec': 0.34,
        'dropletColor': (0.42, 0.12, 0.62, 0.95),
        'sfx': 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg',
        'sfxVolume': 0.72,
    },
    ARCHETYPE_BRUTE: {
        'id': 'sludge-splat',
        'burstScale': (1.95, 1.95, 1.55),
        'pancakeScale': (2.55, 2.55, 0.08),
        'vanishScale': (0.02, 0.02, 0.02),
        'burstSec': 0.08,
        'pancakeSec': 0.14,
        'vanishSec': 0.2,
        'burstColor': (0.85, 2.2, 0.55, 1.0),
        'pancakeColor': (0.55, 1.55, 0.35, 1.0),
        'fadeColor': (0.7, 1.25, 0.55, 0.0),
        'lift': 1.55,
        'ringHalf': 1.05,
        'ringPeak': 2.9,
        'ringSec': 0.36,
        'ringColor': (0.25, 0.75, 0.22, 0.92),
        'dropletCount': 9,
        'dropletHalf': 0.34,
        'dropletDist': 2.85,
        'dropletLift': 0.85,
        'dropletSec': 0.38,
        'dropletColor': (0.22, 0.68, 0.18, 0.95),
        'sfx': 'phase_4/audio/sfx/AA_squirt_glasswater.ogg',
        'sfxVolume': 0.8,
    },
    ARCHETYPE_SNARE: {
        'id': 'balloon-pop',
        'burstScale': (2.25, 2.25, 2.25),
        'pancakeScale': (2.85, 2.85, 0.12),
        'vanishScale': (0.02, 0.02, 0.02),
        'burstSec': 0.06,
        'pancakeSec': 0.1,
        'vanishSec': 0.16,
        'burstColor': (2.4, 1.55, 0.45, 1.0),
        'pancakeColor': (1.85, 1.05, 0.28, 1.0),
        'fadeColor': (1.45, 1.15, 0.55, 0.0),
        'lift': 1.15,
        'ringHalf': 0.75,
        'ringPeak': 3.1,
        'ringSec': 0.28,
        'ringColor': (0.95, 0.55, 0.15, 0.92),
        'dropletCount': 7,
        'dropletHalf': 0.24,
        'dropletDist': 2.65,
        'dropletLift': 1.35,
        'dropletSec': 0.3,
        'dropletColor': (0.9, 0.48, 0.12, 0.95),
        'sfx': 'phase_3/audio/sfx/GUI_balloon_popup.ogg',
        'sfxVolume': 0.85,
    },
    ARCHETYPE_GAGSTER: {
        'id': 'gunk-pie-splat',
        'burstScale': (1.85, 1.85, 1.65),
        'pancakeScale': (2.45, 2.45, 0.1),
        'vanishScale': (0.02, 0.02, 0.02),
        'burstSec': 0.07,
        'pancakeSec': 0.13,
        'vanishSec': 0.19,
        'burstColor': (0.55, 2.15, 2.35, 1.0),
        'pancakeColor': (0.35, 1.55, 1.75, 1.0),
        'fadeColor': (0.55, 1.25, 1.35, 0.0),
        'lift': 1.4,
        'ringHalf': 0.95,
        'ringPeak': 2.8,
        'ringSec': 0.34,
        'ringColor': (0.18, 0.72, 0.78, 0.9),
        'dropletCount': 8,
        'dropletHalf': 0.3,
        'dropletDist': 2.55,
        'dropletLift': 1.05,
        'dropletSec': 0.36,
        'dropletColor': (0.15, 0.62, 0.7, 0.95),
        'sfx': 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg',
        'sfxVolume': 0.78,
    },
    ARCHETYPE_CORRUPT_OSWALD: {
        'id': 'betrayal-crimson-splat',
        'burstScale': (1.95, 1.95, 1.85),
        'pancakeScale': (2.55, 2.55, 0.1),
        'vanishScale': (0.02, 0.02, 0.02),
        'burstSec': 0.07,
        'pancakeSec': 0.12,
        'vanishSec': 0.18,
        'burstColor': (2.35, 0.85, 0.75, 1.0),
        'pancakeColor': (1.85, 0.45, 0.4, 1.0),
        'fadeColor': (1.35, 0.85, 0.7, 0.0),
        'lift': 1.45,
        'ringHalf': 0.95,
        'ringPeak': 2.85,
        'ringSec': 0.33,
        'ringColor': (0.85, 0.22, 0.28, 0.92),
        'dropletCount': 9,
        'dropletHalf': 0.28,
        'dropletDist': 2.5,
        'dropletLift': 1.15,
        'dropletSec': 0.34,
        'dropletColor': (0.72, 0.14, 0.2, 0.95),
        'sfx': 'phase_3.5/audio/sfx/AV_collision.ogg',
        'sfxVolume': 0.8,
    },
}

# Defeat cream / pastel fleck burst — sunny purity chips layered on
# CorruptDeathPopFx ink splat (client only). Not ink; matches reclaim /
# hit-spark cream family. DEATH_CREAM_FLECK_ENABLED = False drops flecks only.
DEATH_CREAM_FLECK_ENABLED = True
DEATH_CREAM_FLECK_BIN = 47
DEATH_CREAM_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.95),  # sunny cream
    (1.0, 0.96, 0.62, 0.92),  # butter
    (1.0, 0.9, 0.78, 0.9),    # soft peach pastel
    (0.98, 0.94, 0.88, 0.88),  # warm parchment
)
DEATH_CREAM_FLECK_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
DEATH_CREAM_FLECK_LOOK = {
    'id': 'death-cream-fleck',
    # lift composed with deathPopLook when played; this is the fallback.
    'lift': 1.35,
    'fleckCount': 7,
    'fleckHalf': 0.18,
    'fleckDist': 2.05,
    'fleckLift': 1.35,
    'fleckSec': 0.32,
    'fleckColors': DEATH_CREAM_FLECK_COLORS,
    'fleckEndColors': DEATH_CREAM_FLECK_END_COLORS,
    'binSort': DEATH_CREAM_FLECK_BIN,
}

# Rising cream sparkle flecks on death cream fleck burst — soft sunny chips
# that rise from CorruptDeathCreamFleckFx (#94) (client only).
# Compose lift / burst radius via CorruptDeathCreamSparkleFx.deathCreamSparkleLook
# → deathCreamFleckLook; fleck size/timing/rise borrows telegraph cream sparkle
# (#135) / silhouette cream sparkle (#131) twinkle grammar. Distinct from
# outward death flecks and soft cream wash (#119): starts near fleck spray,
# rises mostly upward with twinkle. Not ink-colored.
# DEATH_CREAM_SPARKLE_ENABLED = False drops rising sparkles only.
DEATH_CREAM_SPARKLE_ENABLED = True
DEATH_CREAM_SPARKLE_BIN = 48  # above flecks (47); soft rising chips
DEATH_CREAM_SPARKLE_COLORS = (
    (1.0, 0.97, 0.82, 0.88),  # sunny cream
    (1.0, 0.96, 0.62, 0.82),  # butter
    (1.0, 0.9, 0.78, 0.78),   # soft peach pastel
    (0.98, 0.94, 0.88, 0.74),  # warm parchment
)
DEATH_CREAM_SPARKLE_END_COLORS = (
    (1.0, 0.94, 0.55, 0.0),
    (1.0, 0.9, 0.45, 0.0),
    (1.0, 0.85, 0.7, 0.0),
    (0.98, 0.92, 0.8, 0.0),
)
DEATH_CREAM_SPARKLE_LOOK = {
    'id': 'death-cream-sparkle',
    # lift / burstRadius composed with deathCreamFleckLook when played; fallbacks below.
    'lift': 1.35,
    'startDelaySec': 0.08,
    'startDelayBias': 0.04,
    'fleckCount': 4,
    'fleckHalf': 0.07,
    'fleckHalfScale': 1.08,
    'burstRadius': 0.57,
    'burstRadiusScale': 0.28,
    'burstZJitter': 0.3,
    'burstZJitterScale': 0.22,
    'fleckDist': 0.17,
    'fleckDistScale': 1.2,
    'fleckLift': 0.69,
    'fleckLiftScale': 1.15,
    'fleckSec': 0.39,
    'fleckSecScale': 1.05,
    'fleckStagger': 0.038,
    'fleckColors': DEATH_CREAM_SPARKLE_COLORS,
    'fleckEndColors': DEATH_CREAM_SPARKLE_END_COLORS,
    'binSort': DEATH_CREAM_SPARKLE_BIN,
}

# Defeat cream wash pulse — soft aspect2d veil after DEATH_CREAM_FLECK_* burst
# (client only). Matches reclaim PurityCompleteCreamWashFx /
# EntryCreamWashPulseFx two-beat grammar; quieter than street purity payoff.
# DEATH_CREAM_WASH_ENABLED = False drops wash (and therefore aftershock).
DEATH_CREAM_WASH_ENABLED = True
DEATH_CREAM_WASH_DELAY_SEC = 0.20  # after fleck burst start
DEATH_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
DEATH_CREAM_WASH_PEAK = 0.14
DEATH_CREAM_WASH_MID = 0.08
DEATH_CREAM_WASH_IN_SEC = 0.06
DEATH_CREAM_WASH_PULSE_SEC = 0.10
DEATH_CREAM_WASH_HOLD_SEC = 0.08
DEATH_CREAM_WASH_OUT_SEC = 0.42
DEATH_CREAM_WASH_BIN = 38  # under flecks (47); soft veil

# Delayed cream aftershock after death cream wash / sparkle path — residual
# flecks settling + soft halo (CorruptDeathCreamWashFx). Same grammar as
# ENTRY_CREAM_WASH_AFTERSHOCK_* (#132) / PURITY_COMPLETE_CREAM_AFTERSHOCK_*
# (#136); world-space settle matches TELEGRAPH_CREAM_WARN_AFTERSHOCK_*.
# DEATH_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
DEATH_CREAM_WASH_AFTERSHOCK_ENABLED = True
DEATH_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.36  # from fleck/wash arm (~0.16 after wash)
DEATH_CREAM_WASH_AFTERSHOCK_LIFT = 1.35  # fallback; prefers deathCreamFleckLook lift
DEATH_CREAM_WASH_AFTERSHOCK_COUNT = 5
DEATH_CREAM_WASH_AFTERSHOCK_SIZE = 0.12
DEATH_CREAM_WASH_AFTERSHOCK_DRIFT = 0.65
DEATH_CREAM_WASH_AFTERSHOCK_FALL = 0.55
DEATH_CREAM_WASH_AFTERSHOCK_SEC = 0.34
DEATH_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.80)
DEATH_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
DEATH_CREAM_WASH_AFTERSHOCK_BIN = 46  # under flecks (47); soft residual
DEATH_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
DEATH_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.50
DEATH_CREAM_WASH_AFTERSHOCK_HALO_START = 0.28
DEATH_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.45
DEATH_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.30
DEATH_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.22
DEATH_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Overlord telegraph ink crown / silhouette flash — short rubber-hose juice
# above the boss on announceAttackTelegraph when a finale phase look is active.
# Distinct from street CorruptTelegraphInkFx drips: crown silhouette reads as
# boss wind-up. Hold bumped so crown rides the danger-ring warn beat.
# Client only; AI timings unchanged. No KH branding.
OVERLORD_TELEGRAPH_CROWN_LOOK = {
    'id': 'ink-crown',
    'lift': 3.35,
    'scale': 1.0,
    'peakAlpha': 0.95,
    'fadeInSec': 0.05,
    'holdSec': 0.26,
    'fadeOutSec': 0.28,
    'squash': (1.4, 1.0, 0.55),
    'stretch': (0.7, 1.0, 1.55),
    'squashSec': 0.06,
    'stretchSec': 0.1,
    'settleSec': 0.14,
    'bodyColor': (0.06, 0.02, 0.08, 1.0),
    'rimColor': (0.85, 0.25, 0.95, 1.0),
    'flashColor': (1.15, 0.45, 1.25, 1.0),
    'binSort': 44,
}

# Overlord phase ink rain / ink fall — denser shower from above the boss on
# phase telegraphs (alongside OverlordTelegraphCrownFx). Taller / wider than
# street TELEGRAPH_INK_DRIP_*; P2 bumps dropCount via OverlordPhaseInkRainFx.
# Client only; AI timings unchanged. No KH branding.
OVERLORD_PHASE_INK_RAIN_LOOK = {
    'id': 'ink-rain',
    'lift': 5.4,
    'fall': 4.2,
    'spread': 1.55,
    'dropCount': 7,
    'dropHalf': 0.16,
    'fallSec': 0.48,
    'staggerSec': 0.03,
    'peakAlpha': 0.92,
    'dropColor': (0.28, 0.08, 0.42, 0.92),
    'streakColor': (0.55, 0.18, 0.78, 0.88),
    # Slightly earlier / wider puddle so rain landing reads with the danger ring.
    'puddleHalf': 0.72,
    'puddleLift': 0.08,
    'puddlePeak': 2.65,
    'puddleDelay': 0.10,
    'puddleInSec': 0.14,
    'puddleHoldSec': 0.18,
    'puddleOutSec': 0.26,
    'puddleColor': (0.12, 0.04, 0.18, 0.7),
    'binSort': 43,
}

# Overlord telegraph punch cream deepen — ground danger-ring warn + impact
# bloom on announceAttackTelegraph / announceAttackHit (client only). Beyond
# #255 (#208 deepen): juicier cream/pastel rim + denser radial cream phase
# flecks on the warn footprint + wider cream impact aftershock so P1/P2 phase
# shifts read juicier still. Distinct from Brute spit cream deepen (#289 /
# #264, vertical drip), Snare splash cream deepen (#293 / #269, horizontal
# whip), Smudge hit cream deepen (#283 / #259, mid-body hose), and Gunk puddle
# cream deepen (#299 / #276, flat trap-plane bloom) — Overlord cream stays
# ground-plane radial around the phase telegraph punch. Composes with crown +
# ink rain; phase charge colors tint via OverlordTelegraphPunchFx. AI timings
# unchanged. No KH branding / keyblades.
# OVERLORD_TELEGRAPH_PUNCH_ENABLED = False drops warn + impact + cream.
# OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_ENABLED = False drops warn flecks only.
# OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_ENABLED = False drops impact cream
# aftershock only.
OVERLORD_TELEGRAPH_PUNCH_ENABLED = True
OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_ENABLED = True
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_ENABLED = True
OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_COUNT = 7  # beyond #255 (6)
OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_HALF = 0.13  # beyond #255 (0.11)
OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_SEC = 0.32  # beyond #255 (0.28)
OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_LIFT = 0.28  # beyond #255 (0.22)
OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_COLORS = (
    (1.0, 0.97, 0.82, 0.96),  # sunny cream
    (1.0, 0.96, 0.62, 0.9),   # butter
    (1.0, 0.9, 0.78, 0.86),   # soft peach pastel
    (0.98, 0.88, 1.0, 0.84),  # soft lilac cream — phase magenta cousin
)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_DELAY_SEC = 0.07
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_COUNT = 6  # beyond #255 (5)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_STREAK_COUNT = 3  # beyond #255 (2)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_SIZE = 0.14  # beyond #255 (0.12)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_STREAK_SIZE = 0.18  # beyond #255 (0.16)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_DRIFT = 1.0  # beyond #255 (0.85)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_SEC = 0.4  # beyond #255 (0.36)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.92)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.9)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_ENABLED = True
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_HALF = 0.72  # beyond #255 (0.62)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_START = 0.26
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_PEAK = 1.9  # beyond #255 (1.7)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_SEC = 0.38  # beyond #255 (0.34)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.3  # beyond #255 (0.26)
OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)
OVERLORD_TELEGRAPH_PUNCH_LOOK = {
    'id': 'overlord-telegraph-punch',
    # Ground warn ring — footprint scales from overlordPhaseCombat hit range.
    'warnHalf': 2.8,  # deepened beyond #255 (2.7) / #208 (2.6)
    'warnHitRangeScale': 0.32,
    'p2WarnScale': 1.16,  # beyond #255 (1.14)
    'p2WarnPeakScale': 1.12,  # beyond #255 (1.1)
    'warnLift': 0.1,
    'warnPeak': 1.08,  # beyond #255 (1.06)
    'warnFillScale': 0.92,
    'warnRimScale': 1.18,  # juicier cream rim beyond #255 (1.12) / #208 (1.05)
    'warnInSec': 0.09,
    'warnPulseSec': 0.18,
    'warnOutSec': 0.24,
    'warnPeakAlpha': 0.94,  # beyond #255 (0.92)
    'warnRimPeakAlpha': 0.97,  # cream rim punchier vs ink fill
    'holdSec': 0.42,
    'holdSecP1': 0.48,
    'holdSecP2': 0.32,
    'warnColorP1': (2.4, 0.35, 2.7, 0.6),
    'warnColorP2': (2.7, 0.18, 0.22, 0.68),
    # Cream / pastel rim — sunny contrast against magenta / crimson fill.
    'warnRimColorP1': (1.0, 0.96, 0.82, 0.92),
    'warnRimColorP2': (1.0, 0.92, 0.7, 0.94),
    'binSort': 42,
    # Radial cream phase flecks — ground-plane ring chips (not Brute drip /
    # Snare whip / Gunk trap bloom / Smudge hose).
    'creamFleckEnabled': OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_ENABLED,
    'creamFleckCount': OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_COUNT,
    'creamFleckHalf': OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_HALF,
    'creamFleckSec': OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_SEC,
    'creamFleckLift': OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_LIFT,
    'creamFleckColors': OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_COLORS,
    # Impact ground punch bloom — juicier land cue after the warn holds.
    'impactHalf': 1.7,  # beyond #255 (1.55)
    'impactLift': 0.08,
    'impactPeak': 3.15,  # beyond #255 (2.95)
    'impactInSec': 0.05,
    'impactHoldSec': 0.07,
    'impactOutSec': 0.26,  # beyond #255 (0.24)
    'impactPeakAlpha': 0.97,
    'impactColorP1': (2.55, 0.55, 2.7, 0.9),
    'impactColorP2': (2.85, 0.35, 0.2, 0.96),
    'impactBin': 45,
    # Cream impact rim + aftershock — phase punch settle (ground bloom).
    'impactCreamRimScale': 1.38,  # beyond #255 (1.28)
    'impactCreamRimColor': (1.0, 0.97, 0.84, 0.88),
    'impactCreamRimPeakAlpha': 0.94,  # beyond #255 (0.9)
    'creamAftershockEnabled': (
        OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_ENABLED),
}

# Client AV telegraph / impact timing defaults per Overlord phase.
# Sum of squash+mid+stretch+hold ≈ AI telegraphDelay so stretch lingers
# until impact cuts in (fair punish window). Miss path still recovers.
OVERLORD_TELEGRAPH_ANIM_DEFAULTS = {
    'p1': {
        # Rising rain — longer hold (AI telegraphDelay 0.85).
        'telegraphSquashSec': 0.10,
        'telegraphMidSec': 0.14,
        'telegraphStretchSec': 0.12,
        'telegraphHoldSec': 0.48,
        'telegraphRecoverSec': 0.10,
        'impactSlamSec': 0.05,
        'impactReboundSec': 0.09,
        'impactSettleSec': 0.14,
    },
    'p2': {
        # Unleashed — snappier wind-up (AI telegraphDelay 0.68 / slam 0.38).
        'telegraphSquashSec': 0.08,
        'telegraphMidSec': 0.10,
        'telegraphStretchSec': 0.10,
        'telegraphHoldSec': 0.34,
        'telegraphRecoverSec': 0.08,
        'impactSlamSec': 0.04,
        'impactReboundSec': 0.08,
        'impactSettleSec': 0.12,
    },
}

# Ink Overlord finale phase looks (client-readable; AI timings unchanged).
# Phase 1 = rising magenta swell; Phase 2 = crimson unleashed fury.
# Keep P1/P2 telegraphs readable at a glance: color, rubber scale, SFX, HUD cue.
FINALE_PHASE_LOOK = {
    1: {
        'id': 'rising',
        # Magenta swell — tall rubber hose, pie whoosh wind-up.
        'telegraphCharge': (2.55, 0.28, 2.85, 1.0),
        'telegraphHold': (1.85, 0.2, 2.15, 1.0),
        'squash': (2.45, 2.45, 0.24),
        'mid': (2.15, 2.15, 0.38),
        'stretch': (0.38, 0.38, 2.25),
        # AV timing — stretch holds across most of P1 telegraphDelay (0.85).
        'telegraphSquashSec': 0.10,
        'telegraphMidSec': 0.14,
        'telegraphStretchSec': 0.12,
        'telegraphHoldSec': 0.48,
        'telegraphRecoverSec': 0.10,
        'impactScale': (2.05, 2.05, 0.36),
        'impactColor': (2.65, 0.7, 2.8, 1.0),
        'impactSlamSec': 0.05,
        'impactReboundSec': 0.09,
        'impactSettleSec': 0.14,
        'impactReboundScale': (0.72, 0.72, 1.42),
        'rebound': (1.35, 0.4, 1.65, 1.0),
        'pulseHot': (0.95, 0.15, 1.15, 1.0),
        'hitFlash': (1.2, 0.32, 1.3, 1.0),
        'hitFlashPeak': 0.84,
        'actorScale': 1.32,
        'actorTint': (0.32, 0.06, 0.42, 1.0),
        'nameColor': (1.0, 0.5, 1.0, 1.0),
        'pulseAmp': 0.12,
        # Distinct from P2 crimson slam — lighter Silly rise whoosh.
        'telegraphSfx': 'phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseOne.ogg',
        'telegraphSfxVolume': 0.78,
        'hitSfx': 'phase_3.5/audio/sfx/AA_pie_throw_only.ogg',
        'hitSfxVolume': 0.7,
        'hudCue': 'P1 MAGENTA SWELL',
        'hudColor': (1.0, 0.45, 1.0, 1.0),
    },
    2: {
        'id': 'unleashed',
        # Crimson fury — wider squash, taller stretch, heavier slam SFX.
        'telegraphCharge': (2.9, 0.1, 0.22, 1.0),
        'telegraphHold': (2.25, 0.06, 0.14, 1.0),
        'squash': (3.05, 3.05, 0.16),
        'mid': (2.55, 2.55, 0.28),
        'stretch': (0.24, 0.24, 2.85),
        # AV timing — snappier Unleashed wind-up (telegraphDelay 0.68).
        'telegraphSquashSec': 0.08,
        'telegraphMidSec': 0.10,
        'telegraphStretchSec': 0.10,
        'telegraphHoldSec': 0.34,
        'telegraphRecoverSec': 0.08,
        'impactScale': (2.45, 2.45, 0.26),
        'impactColor': (2.95, 0.35, 0.18, 1.0),
        'impactSlamSec': 0.04,
        'impactReboundSec': 0.08,
        'impactSettleSec': 0.12,
        'impactReboundScale': (0.62, 0.62, 1.55),
        'rebound': (1.65, 0.22, 0.18, 1.0),
        'pulseHot': (1.55, 0.1, 0.16, 1.0),
        'hitFlash': (1.32, 0.1, 0.06, 1.0),
        'hitFlashPeak': 0.98,
        'actorScale': 1.58,
        'actorTint': (0.42, 0.05, 0.08, 1.0),
        'nameColor': (1.0, 0.28, 0.18, 1.0),
        'pulseAmp': 0.2,
        # Distinct from P1 magenta rise — hotter Silly phase-two sting.
        'telegraphSfx': 'phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseTwo.ogg',
        'telegraphSfxVolume': 0.88,
        'hitSfx': 'phase_3.5/audio/sfx/AV_collision.ogg',
        'hitSfxVolume': 0.92,
        'hudCue': 'P2 CRIMSON FURY',
        'hudColor': (1.0, 0.28, 0.18, 1.0),
    },
}

# Ink Overlord AI combat (server) — phase-differentiated beyond Smudge chase.
# Client ink-rain / crown telegraph already plays on announceAttackTelegraph;
# these tunables make the resolve match: P1 rising rain + close slam
# (two-note Rising kit), P2 enrage rain + mid ink_surge + close slam
# (three-note Unleashed kit). Radii track OVERLORD_PHASE_INK_RAIN_LOOK
# spread/puddle. No KH branding — rubber-hose Oswald stretch-punch fight only.
OVERLORD_PHASE_COMBAT = {
    1: {
        'id': 'rising-rain',
        # Slower boss walk — telegraph rain owns the mid-range beat.
        'chaseSpeed': 7.2,
        # Engage rain from mid-range (matches ink-rain spread / puddle).
        'meleeRange': 8.0,
        'attackHitRange': 9.5,
        'attackNearMissRange': 12.0,
        'attackDamage': 4,
        'telegraphDelay': 0.85,
        'attackCooldown': 2.45,
        # Rain hits every toon in the puddle, not just the chase target.
        'aoe': True,
        'moveMode': 'rising',
        # Lingering sludge after rain resolve — arena trap vs one-shot AoE.
        'rainLingerSec': 3.0,
        'rainLingerTickSec': 0.5,
        'rainLingerTickDamage': 1,
        'rainLingerSlowFactor': 0.5,
        # Close-range slam — second Rising pressure beyond rain-only so Silly
        # climax is not one-note before HP-threshold Unleash. Slower / softer
        # than P2 slam; no ink_surge on P1 (surge stays Unleashed-only).
        'slamHitRange': 4.6,
        'slamNearMissRange': 6.8,
        'slamDamage': 3,
        'slamTelegraphDelay': 0.55,
        'slamCooldown': 1.65,
        'slamMeleeRange': 4.4,
        # Tight linger sludge after close slam — rain parity, smaller footprint.
        'slamLingerSec': 2.0,
        'slamLingerTickSec': 0.5,
        'slamLingerTickDamage': 1,
        'slamLingerSlowFactor': 0.55,
    },
    2: {
        'id': 'unleashed-enrage',
        # Enrage chase — closes gaps between denser rains.
        'chaseSpeed': 11.8,
        'meleeRange': 9.0,
        'attackHitRange': 11.5,
        'attackNearMissRange': 14.5,
        'attackDamage': 6,
        'telegraphDelay': 0.68,
        'attackCooldown': 1.55,
        'aoe': True,
        'moveMode': 'enrage',
        # Lingering sludge after rain resolve — denser Unleashed arena trap.
        'rainLingerSec': 3.5,
        'rainLingerTickSec': 0.5,
        'rainLingerTickDamage': 2,
        'rainLingerSlowFactor': 0.45,
        # Close-range slam when the player is already in the ink — faster
        # single-target pressure between rain volleys.
        'slamHitRange': 5.5,
        'slamNearMissRange': 8.0,
        'slamDamage': 5,
        'slamTelegraphDelay': 0.38,
        'slamCooldown': 1.15,
        'slamMeleeRange': 5.2,
        # Close slam linger — denser Unleashed foot-trap vs Rising.
        'slamLingerSec': 2.5,
        'slamLingerTickSec': 0.5,
        'slamLingerTickDamage': 1,
        'slamLingerSlowFactor': 0.5,
        # Mid-range ink surge — planar rush then landing AoE (third Unleashed
        # note between slam and rain). Longer than Smudge ink_dash.
        'surgeMaxRange': 8.0,
        'surgeDash': 4.6,
        'surgeStop': 1.1,
        'surgeHitRange': 7.0,
        'surgeNearMissRange': 9.5,
        'surgeDamage': 6,
        'surgeTelegraphDelay': 0.48,
        'surgeCooldown': 1.35,
        # Mid surge linger — landing puddle owns the gap-close XY.
        'surgeLingerSec': 2.75,
        'surgeLingerTickSec': 0.5,
        'surgeLingerTickDamage': 2,
        'surgeLingerSlowFactor': 0.5,
    },
}

# Lingering sludge hazard after Ink Overlord rain resolve (gameplay trap).
# Initial rain resolve stays a one-shot AoE around the boss XY; then the
# magenta puddle ticks DoT and stamps a short slow while toons stay inside.
# Silly climax arena control — Gagster-like linger, not cream FX deepen.
# OVERLORD_RAIN_LINGER_ENABLED = False restores one-shot-only rain damage.
# No KH branding / keyblades.
OVERLORD_RAIN_LINGER_ENABLED = True
OVERLORD_RAIN_LINGER_SEC = 3.0
OVERLORD_RAIN_LINGER_TICK_SEC = 0.5
OVERLORD_RAIN_LINGER_TICK_DAMAGE = 1
# Planar radius fallback when phase combat attackHitRange is missing (P1).
OVERLORD_RAIN_LINGER_RADIUS = 9.5
# Client walk slow + AI stamp refresh while standing in rain sludge.
OVERLORD_RAIN_LINGER_SLOW_FACTOR = 0.5
OVERLORD_RAIN_LINGER_SLOW_SEC = 0.7


def overlordRainLingerUntil(landAt, lingerSec=None):
    """Absolute expiry for an Overlord ink-rain linger sludge hazard."""
    if lingerSec is None:
        lingerSec = OVERLORD_RAIN_LINGER_SEC
    return float(landAt) + max(0.0, float(lingerSec))


def overlordRainLingerTickCount(lingerSec=None, tickSec=None):
    """How many DoT ticks fit inside a rain linger window (excludes land hit)."""
    if lingerSec is None:
        lingerSec = OVERLORD_RAIN_LINGER_SEC
    if tickSec is None:
        tickSec = OVERLORD_RAIN_LINGER_TICK_SEC
    linger = max(0.0, float(lingerSec))
    tick = max(0.05, float(tickSec))
    if linger <= 0.0:
        return 0
    # First tick fires after one interval; last tick must still be < until.
    return int(linger // tick)


def isInsideOverlordRainLinger(dx, dy, radius):
    """True when planar offset is inside the rain linger / land puddle radius."""
    r = max(0.0, float(radius))
    return (float(dx) * float(dx) + float(dy) * float(dy)) <= (r * r)


def isOverlordRainSlowActive(until, now):
    """True while an AI-stamped Overlord rain sludge slow window is live."""
    return float(now) < float(until)


def overlordRainSlowUntil(now, slowSec=None):
    """Absolute expiry for a rain-sludge-slow refresh stamped on a tick."""
    if slowSec is None:
        slowSec = OVERLORD_RAIN_LINGER_SLOW_SEC
    return float(now) + max(0.0, float(slowSec))


def overlordRainLingerTickDamage(stats=None):
    """Per-tick DoT while standing in rain linger sludge (min 1 when enabled)."""
    if stats is None:
        stats = {}
    raw = stats.get(
        'rainLingerTickDamage', OVERLORD_RAIN_LINGER_TICK_DAMAGE)
    return max(1, int(raw))


# Lingering sludge hazard after Ink Overlord close slam resolve.
# Slam was one-shot single-target; rain already owns floor (#362). Arm a
# tight Gagster-like linger at the slam XY so Rising / Unleashed slam
# leaves readable space control. OVERLORD_SLAM_LINGER_ENABLED = False
# restores one-shot-only slam. No cream deepen / no KH.
OVERLORD_SLAM_LINGER_ENABLED = True
OVERLORD_SLAM_LINGER_SEC = 2.0
OVERLORD_SLAM_LINGER_TICK_SEC = 0.5
OVERLORD_SLAM_LINGER_TICK_DAMAGE = 1
# Planar radius fallback when phase combat slamHitRange is missing (P1).
OVERLORD_SLAM_LINGER_RADIUS = 4.6
OVERLORD_SLAM_LINGER_SLOW_FACTOR = 0.55
OVERLORD_SLAM_LINGER_SLOW_SEC = 0.65


def overlordSlamLingerUntil(landAt, lingerSec=None):
    """Absolute expiry for an Overlord slam linger sludge hazard."""
    if lingerSec is None:
        lingerSec = OVERLORD_SLAM_LINGER_SEC
    return float(landAt) + max(0.0, float(lingerSec))


def overlordSlamLingerTickCount(lingerSec=None, tickSec=None):
    """How many DoT ticks fit inside a slam linger window (excludes land hit)."""
    if lingerSec is None:
        lingerSec = OVERLORD_SLAM_LINGER_SEC
    if tickSec is None:
        tickSec = OVERLORD_SLAM_LINGER_TICK_SEC
    linger = max(0.0, float(lingerSec))
    tick = max(0.05, float(tickSec))
    if linger <= 0.0:
        return 0
    return int(linger // tick)


def isInsideOverlordSlamLinger(dx, dy, radius):
    """True when planar offset is inside the slam linger puddle radius."""
    return isInsideOverlordRainLinger(dx, dy, radius)


def isOverlordSlamSlowActive(until, now):
    """True while an AI-stamped Overlord slam sludge slow window is live."""
    return float(now) < float(until)


def overlordSlamSlowUntil(now, slowSec=None):
    """Absolute expiry for a slam-sludge-slow refresh stamped on a tick."""
    if slowSec is None:
        slowSec = OVERLORD_SLAM_LINGER_SLOW_SEC
    return float(now) + max(0.0, float(slowSec))


def overlordSlamLingerTickDamage(stats=None):
    """Per-tick DoT while standing in slam linger sludge (min 1 when enabled)."""
    if stats is None:
        stats = {}
    raw = stats.get(
        'slamLingerTickDamage', OVERLORD_SLAM_LINGER_TICK_DAMAGE)
    return max(1, int(raw))


# Lingering sludge hazard after Ink Overlord ink_surge resolve.
# Surge was hit + gap-close only; rain owns floor (#362). Arm a mid-band
# linger at the post-dash XY so Unleashed three-note kit shares space
# control. OVERLORD_INK_SURGE_LINGER_ENABLED = False restores one-shot
# surge. No cream deepen / no KH.
OVERLORD_INK_SURGE_LINGER_ENABLED = True
OVERLORD_INK_SURGE_LINGER_SEC = 2.75
OVERLORD_INK_SURGE_LINGER_TICK_SEC = 0.5
OVERLORD_INK_SURGE_LINGER_TICK_DAMAGE = 1
# Planar radius fallback when phase combat surgeHitRange is missing (P2).
OVERLORD_INK_SURGE_LINGER_RADIUS = 7.0
OVERLORD_INK_SURGE_LINGER_SLOW_FACTOR = 0.5
OVERLORD_INK_SURGE_LINGER_SLOW_SEC = 0.7


def overlordInkSurgeLingerUntil(landAt, lingerSec=None):
    """Absolute expiry for an Overlord ink_surge linger sludge hazard."""
    if lingerSec is None:
        lingerSec = OVERLORD_INK_SURGE_LINGER_SEC
    return float(landAt) + max(0.0, float(lingerSec))


def overlordInkSurgeLingerTickCount(lingerSec=None, tickSec=None):
    """How many DoT ticks fit inside an ink_surge linger window."""
    if lingerSec is None:
        lingerSec = OVERLORD_INK_SURGE_LINGER_SEC
    if tickSec is None:
        tickSec = OVERLORD_INK_SURGE_LINGER_TICK_SEC
    linger = max(0.0, float(lingerSec))
    tick = max(0.05, float(tickSec))
    if linger <= 0.0:
        return 0
    return int(linger // tick)


def isInsideOverlordInkSurgeLinger(dx, dy, radius):
    """True when planar offset is inside the ink_surge linger puddle radius."""
    return isInsideOverlordRainLinger(dx, dy, radius)


def isOverlordInkSurgeSlowActive(until, now):
    """True while an AI-stamped Overlord ink_surge sludge slow is live."""
    return float(now) < float(until)


def overlordInkSurgeSlowUntil(now, slowSec=None):
    """Absolute expiry for an ink_surge-sludge-slow refresh stamped on a tick."""
    if slowSec is None:
        slowSec = OVERLORD_INK_SURGE_LINGER_SLOW_SEC
    return float(now) + max(0.0, float(slowSec))


def overlordInkSurgeLingerTickDamage(stats=None):
    """Per-tick DoT while standing in ink_surge linger sludge (min 1)."""
    if stats is None:
        stats = {}
    raw = stats.get(
        'surgeLingerTickDamage', OVERLORD_INK_SURGE_LINGER_TICK_DAMAGE)
    return max(1, int(raw))


# ---------------------------------------------------------------------------
# Overlord P1 Rising slam — second Rising pressure beyond rain (TC-342).
# P1 was rain-only; close slam gives a two-note kit before Unleash. Soft /
# slow vs P2 slam. OVERLORD_P1_SLAM_ENABLED = False restores rain-only.
# ---------------------------------------------------------------------------
OVERLORD_P1_SLAM_ENABLED = True

# ---------------------------------------------------------------------------
# Overlord P2 ink surge — third Unleashed pressure pattern (#327).
# P2 was two-note (rain AoE / close slam). Mid-range ink_surge dashes then
# lands a self-centered AoE so climax combat reads three notes. Not cream FX.
# OVERLORD_INK_SURGE_ENABLED = False restores legacy rain-or-slam picker.
# ---------------------------------------------------------------------------
OVERLORD_INK_SURGE_ENABLED = True
OVERLORD_INK_SURGE_MAX_RANGE = 8.0
OVERLORD_INK_SURGE_DASH = 4.6
OVERLORD_INK_SURGE_STOP = 1.1

# P2 Smudge adds — wave 2+ while Unleashed packSize keeps Overlord(s).
OVERLORD_P2_ADD_WAVE_START = 2
OVERLORD_P2_ADD_COUNT = 2
OVERLORD_P2_ADD_HP = 25
OVERLORD_P2_ADD_NAME = 'Ink Smudge'
OVERLORD_P2_ADD_SPACING = 3.4
OVERLORD_P2_ADD_FORWARD = 4.5

# Phase-transition sting (FOV / flash / render slam).
FINALE_STING_FOV_PUNCH = 18.0
FINALE_STING_FOV_IN = 0.08
FINALE_STING_FOV_OUT = 0.42
FINALE_STING_FLASH_PEAK = 0.92
FINALE_STING_FLASH_COLOR = (1.15, 0.2, 0.55, 1.0)
FINALE_STING_RENDER_PEAK = (1.85, 0.35, 1.15, 1.0)
FINALE_STING_RENDER_HOLD = (1.35, 0.45, 0.75, 1.0)

# Oswald reveal sting — colder ink wash after Silly finale victory / twist.
# Existing Toontown SFX only (optional if asset missing in stripped checkouts).
OSWALD_REVEAL_FOV_PUNCH = 14.0
OSWALD_REVEAL_FOV_IN = 0.1
OSWALD_REVEAL_FOV_OUT = 0.55
OSWALD_REVEAL_FLASH_PEAK = 0.78
OSWALD_REVEAL_FLASH_COLOR = (0.95, 0.22, 0.38, 1.0)
OSWALD_REVEAL_RENDER_PEAK = (1.55, 0.28, 0.42, 1.0)
OSWALD_REVEAL_RENDER_HOLD = (1.25, 0.38, 0.48, 1.0)
OSWALD_REVEAL_SFX = 'phase_4/audio/sfx/tt_s_prp_sillyMeterPhaseTwo.ogg'
OSWALD_REVEAL_SFX_VOLUME = 0.82

# Polluted vs pure street music beds (existing Toontown BGM — no new assets).
# Encounter bed lives in phase_3.5 with street loaders, so TT streets can play it.
POLLUTED_STREET_MUSIC = 'phase_3.5/audio/bgm/encntr_general_bg.ogg'
POLLUTED_STREET_MUSIC_VOLUME = 0.72
PURE_STREET_MUSIC_VOLUME = 0.8
POLLUTION_AUDIO_THRESHOLD = 0.05
POLLUTION_AUDIO_CROSSFADE_SEC = 1.25
# Snappier return so reclaim cheer / purity sting (#21) land together.
POLLUTION_AUDIO_RESTORE_CROSSFADE_SEC = 0.85

# Pure-street birds return — short rubber-hose ambient bed when pollution
# clears (existing SZ playground bird chirps; no new assets / no KH branding).
PURE_STREET_BIRDS_SFX = (
    'phase_4/audio/sfx/SZ_TC_bird1.ogg',
    'phase_4/audio/sfx/SZ_TC_bird2.ogg',
    'phase_4/audio/sfx/SZ_TC_bird3.ogg',
)
PURE_STREET_BIRDS_VOLUME = 0.62
PURE_STREET_BIRDS_FADE_IN_SEC = 0.55
PURE_STREET_BIRDS_HOLD_SEC = 2.4
PURE_STREET_BIRDS_FADE_OUT_SEC = 0.9
# Collapse pollutionChanged + purityRestoreFx double-fires into one bed.
PURE_STREET_BIRDS_DEBOUNCE_SEC = 2.5
# Extra chirp sprinkles during the hold (rubber-hose cheerful return).
PURE_STREET_BIRDS_CHIRP_COUNT = 3
PURE_STREET_BIRDS_CHIRP_VOLUME = 0.48


def finalePhaseLook(phaseIndex):
    """Return presentation dict for Ink Overlord phase, or None."""
    try:
        phase = int(phaseIndex)
    except (TypeError, ValueError):
        return None
    return FINALE_PHASE_LOOK.get(phase)


def normalizeFinalePhase(phaseIndex):
    """Clamp to a known Overlord phase (0 = not Overlord)."""
    try:
        phase = int(phaseIndex)
    except (TypeError, ValueError):
        return 0
    if phase in OVERLORD_PHASE_COMBAT:
        return phase
    return 0


# ---------------------------------------------------------------------------
# Boss / chase / Elite·Ambush HP bar (client HUD).
# Ink Overlord + Corrupted Oswald + Elite/Ambush-prefixed pack hostiles
# (same rename tokens soft-lock already prefers). Readable life bar from
# synced setHp/setMaxHp. Not cream FX deepen; no KH.
# BOSS_HP_BAR_ENABLED = False hides the bar without touching combat AI.
# ---------------------------------------------------------------------------
BOSS_HP_BAR_ENABLED = True
BOSS_HP_BAR_POS = (0.0, 0.0, 0.82)  # above purity meter (z 0.50)
BOSS_HP_BAR_WIDTH = 0.78
BOSS_HP_BAR_HEIGHT = 0.042
BOSS_HP_BAR_RIM_PAD = 0.014
BOSS_HP_BAR_BIN = 52  # over purity meter (45); under flash bins ~56+
BOSS_HP_BAR_LABEL_SCALE = 0.042
BOSS_HP_BAR_LABEL_Z = 0.062
BOSS_HP_BAR_PCT_SCALE = 0.036
BOSS_HP_BAR_PCT_Z = -0.002
BOSS_HP_BAR_TRACK_COLOR = (0.10, 0.04, 0.12, 0.88)
BOSS_HP_BAR_RIM_COLOR = (0.55, 0.22, 0.55, 0.72)
BOSS_HP_BAR_LABEL_COLOR = (1.0, 0.92, 0.95, 1.0)
BOSS_HP_BAR_PCT_COLOR = (1.0, 0.96, 0.9, 1.0)
# Fill / rim by subject — Overlord phase, Oswald betrayal, Elite/Ambush pack.
BOSS_HP_BAR_FILL_OVERLORD_P1 = (0.95, 0.28, 0.95, 0.96)
BOSS_HP_BAR_FILL_OVERLORD_P2 = (0.95, 0.22, 0.16, 0.98)
BOSS_HP_BAR_FILL_OSWALD = (0.92, 0.28, 0.22, 0.96)
BOSS_HP_BAR_FILL_ELITE = (0.95, 0.58, 0.18, 0.96)  # ink-amber elite pack
BOSS_HP_BAR_FILL_AMBUSH = (0.18, 0.72, 0.78, 0.96)  # flank-teal ambush
BOSS_HP_BAR_RIM_OVERLORD_P1 = (1.0, 0.55, 1.0, 0.72)
BOSS_HP_BAR_RIM_OVERLORD_P2 = (1.0, 0.32, 0.22, 0.78)
BOSS_HP_BAR_RIM_OSWALD = (1.0, 0.42, 0.3, 0.75)
BOSS_HP_BAR_RIM_ELITE = (1.0, 0.72, 0.28, 0.75)
BOSS_HP_BAR_RIM_AMBUSH = (0.35, 0.88, 0.92, 0.75)
BOSS_HP_BAR_DEFAULT_OVERLORD_LABEL = 'Ink Overlord'
BOSS_HP_BAR_DEFAULT_OSWALD_LABEL = 'Corrupted Oswald'


def resolveBossHpBarFinalePhase(finalePhase=0, name=''):
    """Resolve Overlord phase from the hostile's own phase and/or name.

    Callers must pass the hostile's own finalePhase — never reclaim-director
    street phase alone, or P2 Smudge adds would steal the singleton bar
    from the Overlord (same anti-pattern as soft-lock prefer).
    """
    phase = normalizeFinalePhase(finalePhase)
    if phase >= 1:
        return phase
    text = (name or '').lower()
    if 'unleashed' in text:
        return 2
    if 'overlord' in text:
        return 1
    return 0


# Soft-lock prefer tiers — lower int wins. Binary prefer (#339/#375) made
# Ambush outrank Overlord by distance during Unleashed adds + ambush beats;
# tiered rank keeps climax/twist above Elite above Ambush above fodder.
SOFT_LOCK_PRIORITY_TIER_BOSS = 0
SOFT_LOCK_PRIORITY_TIER_ELITE = 1
SOFT_LOCK_PRIORITY_TIER_AMBUSH = 2
SOFT_LOCK_PRIORITY_TIER_FODDER = 3


def isElitePreferName(name=''):
    """True for Elite pack rename prefix (``Elite ``).

    Matches ReclaimGlobals.ELITE_NAME_PREFIX without importing reclaim.
    Bare ``Elite`` without the trailing space is not a pack rename.
    """
    return (name or '').lower().startswith('elite ')


def isAmbushPreferName(name=''):
    """True for Ambush pack rename prefix (``Ambush ``).

    Matches ReclaimGlobals.AMBUSH_NAME_PREFIX without importing reclaim.
    Bare ``Ambush`` without the trailing space is not a pack rename.
    """
    return (name or '').lower().startswith('ambush ')


def isEliteOrAmbushPreferName(name=''):
    """True for Elite / Ambush pack rename prefixes (soft-lock + HP bar).

    Matches ReclaimGlobals.ELITE_NAME_PREFIX / AMBUSH_NAME_PREFIX without
    importing reclaim (avoids CorruptionGlobals ↔ ReclaimGlobals cycle).
    Bare ``Elite`` / ``Ambush`` tokens without the trailing space are not
    pack renames.
    """
    return isElitePreferName(name) or isAmbushPreferName(name)


def softLockPriorityTier(archetype=0, name='', finalePhase=0):
    """Soft-lock prefer tier — lower int wins (boss > elite > ambush > fodder).

    Overlord (name tokens / per-toon finalePhase) and Corrupted Oswald share
    the boss tier. Elite rename outranks Ambush rename; plain pack fodder
    is last. Callers must pass the hostile's own finalePhase — never
    reclaim-director street phase alone, or P2 Smudge adds would steal
    priority from the Overlord.
    """
    try:
        aid = int(archetype)
    except (TypeError, ValueError):
        aid = ARCHETYPE_INK
    if aid == ARCHETYPE_CORRUPT_OSWALD:
        return SOFT_LOCK_PRIORITY_TIER_BOSS
    text = (name or '').lower()
    if 'overlord' in text or 'unleashed' in text:
        return SOFT_LOCK_PRIORITY_TIER_BOSS
    if normalizeFinalePhase(finalePhase) >= 1:
        return SOFT_LOCK_PRIORITY_TIER_BOSS
    if isElitePreferName(name):
        return SOFT_LOCK_PRIORITY_TIER_ELITE
    if isAmbushPreferName(name):
        return SOFT_LOCK_PRIORITY_TIER_AMBUSH
    return SOFT_LOCK_PRIORITY_TIER_FODDER


def isSoftLockPrioritySubject(archetype=0, name='', finalePhase=0):
    """True when soft-lock should prefer this hostile over pack adds.

    Corrupted Oswald (archetype), Ink Overlord (name tokens and/or
    per-toon finalePhase), and Elite/Ambush-prefixed pack hostiles
    (``Elite `` / ``Ambush `` rename tokens from ReclaimGlobals). Callers
    must pass the hostile's own finalePhase — never reclaim-director
    street phase alone, or P2 Smudge adds would steal priority from the
    Overlord. Prefer softLockPriorityTier when ranking among subjects.
    """
    return softLockPriorityTier(
        archetype, name=name, finalePhase=finalePhase) < (
            SOFT_LOCK_PRIORITY_TIER_FODDER)


def isBossOrChaseHpBarSubject(archetype=0, name='', finalePhase=0):
    """True for Overlord, Corrupted Oswald, or Elite/Ambush pack hostiles.

    Parity with soft-lock prefer (#375): mid-wave Elite / Ambush renames
    that already steal Tab focus also drive the readable life bar.
    Callers must pass the hostile's own finalePhase — never reclaim-director
    street phase alone, or P2 Smudge adds would steal the bar from the
    Overlord.
    """
    if not BOSS_HP_BAR_ENABLED:
        return False
    try:
        aid = int(archetype)
    except (TypeError, ValueError):
        aid = ARCHETYPE_INK
    if aid == ARCHETYPE_CORRUPT_OSWALD:
        return True
    if isEliteOrAmbushPreferName(name):
        return True
    return resolveBossHpBarFinalePhase(finalePhase, name) >= 1


def bossHpBarRatio(hp, maxHp):
    """Clamped 0..1 life fraction for the boss/chase bar fill."""
    try:
        cur = float(hp)
        ceiling = float(maxHp)
    except (TypeError, ValueError):
        return 0.0
    if ceiling <= 0.0:
        return 0.0
    return max(0.0, min(1.0, cur / ceiling))


def bossHpBarLabel(name='', archetype=0, finalePhase=0):
    """Readable bar title — prefers live name, else archetype/overlord default."""
    text = str(name or '').strip()
    if text:
        return text
    try:
        aid = int(archetype)
    except (TypeError, ValueError):
        aid = ARCHETYPE_INK
    if aid == ARCHETYPE_CORRUPT_OSWALD:
        return BOSS_HP_BAR_DEFAULT_OSWALD_LABEL
    phase = resolveBossHpBarFinalePhase(finalePhase, name)
    if phase >= 1:
        return BOSS_HP_BAR_DEFAULT_OVERLORD_LABEL
    return CORRUPT_TOON_DEFAULT_NAME


def bossHpBarFillColor(archetype=0, finalePhase=0, name=''):
    """Fill RGBA for the active boss/chase/Elite·Ambush subject."""
    try:
        aid = int(archetype)
    except (TypeError, ValueError):
        aid = ARCHETYPE_INK
    if aid == ARCHETYPE_CORRUPT_OSWALD:
        return BOSS_HP_BAR_FILL_OSWALD
    text = (name or '').lower()
    if text.startswith('elite '):
        return BOSS_HP_BAR_FILL_ELITE
    if text.startswith('ambush '):
        return BOSS_HP_BAR_FILL_AMBUSH
    phase = resolveBossHpBarFinalePhase(finalePhase, name)
    if phase >= 2:
        return BOSS_HP_BAR_FILL_OVERLORD_P2
    return BOSS_HP_BAR_FILL_OVERLORD_P1


def bossHpBarRimColor(archetype=0, finalePhase=0, name=''):
    """Outer rim RGBA matching fill subject."""
    try:
        aid = int(archetype)
    except (TypeError, ValueError):
        aid = ARCHETYPE_INK
    if aid == ARCHETYPE_CORRUPT_OSWALD:
        return BOSS_HP_BAR_RIM_OSWALD
    text = (name or '').lower()
    if text.startswith('elite '):
        return BOSS_HP_BAR_RIM_ELITE
    if text.startswith('ambush '):
        return BOSS_HP_BAR_RIM_AMBUSH
    phase = resolveBossHpBarFinalePhase(finalePhase, name)
    if phase >= 2:
        return BOSS_HP_BAR_RIM_OVERLORD_P2
    return BOSS_HP_BAR_RIM_OVERLORD_P1


def overlordPhaseCombat(phaseIndex):
    """Return AI combat dict for Ink Overlord phase, or None."""
    phase = normalizeFinalePhase(phaseIndex)
    if phase < 1:
        return None
    return OVERLORD_PHASE_COMBAT.get(phase)


def overlordSlamMeleeRange(stats=None):
    """Close slam engage for Rising / Unleashed Overlord."""
    if stats and 'slamMeleeRange' in stats:
        return max(0.5, float(stats['slamMeleeRange']))
    if stats and 'slamHitRange' in stats:
        return max(0.5, float(stats['slamHitRange']))
    return 5.2


def overlordSurgeMaxRange(stats=None):
    """Outer engage for mid-range ink_surge (inside this, outside slam)."""
    if stats and 'surgeMaxRange' in stats:
        return max(0.5, float(stats['surgeMaxRange']))
    return max(0.5, float(OVERLORD_INK_SURGE_MAX_RANGE))


def overlordSurgeDashDist(stats=None):
    if stats and 'surgeDash' in stats:
        return max(0.0, float(stats['surgeDash']))
    return max(0.0, float(OVERLORD_INK_SURGE_DASH))


def overlordSurgeStop(stats=None):
    if stats and 'surgeStop' in stats:
        return max(0.0, float(stats['surgeStop']))
    return max(0.0, float(OVERLORD_INK_SURGE_STOP))


def overlordPickRisingMove(dist, stats=None):
    """Choose Rising move: close slam, else rain.

    Two-note P1 kit (TC-342 / gap scan #8). Soft close slam between rain
    volleys so Silly climax is not rain-only before HP-threshold Unleash.
    With slam disabled, stays on rain. Never picks ink_surge (P2 only).
    """
    if not OVERLORD_P1_SLAM_ENABLED:
        return 'rain'
    if float(dist) <= overlordSlamMeleeRange(stats):
        return 'slam'
    return 'rain'


def overlordPickEnrageMove(dist, stats=None):
    """Choose Unleashed move: close slam, mid ink_surge, else rain.

    Three-note P2 kit (#327). With surge disabled, falls back to
    rain-or-slam. Rising P1 uses ``overlordPickRisingMove`` instead.
    """
    slamRange = overlordSlamMeleeRange(stats)
    if float(dist) <= slamRange:
        return 'slam'
    if not OVERLORD_INK_SURGE_ENABLED:
        return 'rain'
    if float(dist) <= overlordSurgeMaxRange(stats):
        return 'ink_surge'
    return 'rain'


# Overlord telegraph move ids (announceAttackTelegraph string). Client AV
# branches rain shower vs close slam warn vs mid surge warn — fair punish
# read as kits deepen. Street attackMove strings normalize to '' here.
# No cream deepen / no KH branding.
OVERLORD_TELEGRAPH_MOVES = frozenset(('rain', 'slam', 'ink_surge'))
OVERLORD_TELEGRAPH_MOVE_HUD = {
    'rain': 'RAIN',
    'slam': 'SLAM',
    'ink_surge': 'SURGE',
}


def normalizeOverlordTelegraphMove(moveId):
    """Return ``rain`` / ``slam`` / ``ink_surge``, or '' for non-Overlord moves."""
    move = str(moveId or '').strip().lower()
    if move in OVERLORD_TELEGRAPH_MOVES:
        return move
    return ''


def overlordTelegraphShowsInkRain(moveId):
    """Ink-rain shower is rain-only — slam/surge keep crown + danger ring."""
    return normalizeOverlordTelegraphMove(moveId) == 'rain'


def overlordTelegraphShowsPunchWarn(moveId):
    """Danger-ring warn for all three Overlord notes (distinct radii)."""
    return bool(normalizeOverlordTelegraphMove(moveId))


def overlordTelegraphMoveHitRange(moveId, phase=1, combat=None):
    """Warn-ring hit range for the telegraphed Overlord move.

    Rain uses rain AoE ``attackHitRange``; slam / ink_surge use their
    own hit bands so the danger footprint matches the resolve.
    """
    move = normalizeOverlordTelegraphMove(moveId) or 'rain'
    table = combat if combat is not None else overlordPhaseCombat(phase)
    table = table or {}
    if move == 'slam':
        return max(0.5, float(table.get(
            'slamHitRange', table.get('attackHitRange', 5.5))))
    if move == 'ink_surge':
        return max(0.5, float(table.get(
            'surgeHitRange', table.get('attackHitRange', 7.5))))
    return max(0.5, float(table.get('attackHitRange', 9.5)))


def overlordTelegraphMoveHudCue(moveId, phase=1, finaleLook=None):
    """Phase HUD chip text that names the incoming Overlord move."""
    move = normalizeOverlordTelegraphMove(moveId) or 'rain'
    label = OVERLORD_TELEGRAPH_MOVE_HUD.get(move, move.upper())
    base = ''
    if finaleLook:
        base = str(finaleLook.get('hudCue', '') or '').strip()
    try:
        phaseIndex = max(1, int(phase))
    except (TypeError, ValueError):
        phaseIndex = 1
    if base:
        return '%s · %s' % (base, label)
    return 'OVERLORD P%s · %s' % (phaseIndex, label)


def overlordSurgePos(sx, sy, tx, ty, dash=None, stop=None):
    """Planar Overlord position after mid-range ink surge toward (tx, ty).

    Advances up to ``dash`` but never closer than ``stop`` so the rush does
    not overshoot through the toon. Longer boss step than Smudge ink_dash.
    """
    if dash is None:
        dash = OVERLORD_INK_SURGE_DASH
    if stop is None:
        stop = OVERLORD_INK_SURGE_STOP
    dash = max(0.0, float(dash))
    stop = max(0.0, float(stop))
    sx = float(sx)
    sy = float(sy)
    dx = float(tx) - sx
    dy = float(ty) - sy
    planar = (dx * dx + dy * dy) ** 0.5
    if planar <= stop or planar < 1e-6 or dash <= 0.0:
        return (sx, sy)
    step = min(dash, planar - stop)
    if step <= 0.0:
        return (sx, sy)
    return (sx + dx / planar * step, sy + dy / planar * step)


def overlordP2AddCount(waveIndex, addCount=None, addWaveStart=None):
    """Smudge add count for Unleashed wave, or 0 when adds are not active."""
    try:
        wave = int(waveIndex)
    except (TypeError, ValueError):
        return 0
    start = (
        OVERLORD_P2_ADD_WAVE_START
        if addWaveStart is None else int(addWaveStart))
    if wave < start:
        return 0
    count = OVERLORD_P2_ADD_COUNT if addCount is None else int(addCount)
    return max(0, count)


def clampPollution(level):
    """Clamp a pollution scalar into [0, 1]."""
    try:
        value = float(level)
    except (TypeError, ValueError):
        return POLLUTION_PURE
    if value < POLLUTION_PURE:
        return POLLUTION_PURE
    if value > POLLUTION_FULL:
        return POLLUTION_FULL
    return value


def pollutionToNet(level):
    """Encode 0..1 pollution for DC uint16/1000."""
    return int(round(clampPollution(level) * POLLUTION_SCALE))


def pollutionFromNet(netValue):
    """Decode DC uint16/1000 into 0..1 pollution."""
    return clampPollution(float(netValue) / float(POLLUTION_SCALE))


def branchZoneForPollution(zoneId):
    """Map any street/interior zone to its branch (street) id for bias lookup."""
    try:
        z = int(zoneId)
    except (TypeError, ValueError):
        return 2200
    branch = z - (z % 100)
    if z % 1000 >= 500:
        branch -= 500
    return branch


def hoodPollutionBias(zoneId):
    """Return fog/grade/prop bias dict for a zone (falls back to Loopy)."""
    return HOOD_POLLUTION_BIAS.get(branchZoneForPollution(zoneId), _DEFAULT_HOOD_BIAS)


def pollutionDensityFactor(level):
    """Map pollution 0..1 → density factor with ease-in ramp curve."""
    lvl = clampPollution(level)
    if lvl <= POLLUTION_PURE:
        return 0.0
    curve = float(POLLUTION_FOG_DENSITY_CURVE)
    if curve == 1.0:
        return lvl
    return lvl ** curve


def pollutionFogRampDuration(fromLevel, toLevel):
    """Seconds to lerp fog/haze between two pollution levels."""
    a = clampPollution(fromLevel)
    b = clampPollution(toLevel)
    if abs(b - a) <= POLLUTION_FOG_SNAP_DELTA:
        return 0.0
    # Clearing to pure uses the longer settle so reclaim reads as fog lifting.
    if b <= POLLUTION_PURE < a:
        return float(POLLUTION_FOG_CLEAR_SEC)
    # Scale mid-step ramps by delta so a 0.15 defeat isn't sluggish.
    span = max(0.15, abs(b - a))
    return float(POLLUTION_FOG_RAMP_SEC) * min(1.0, span / 0.25)


def streetStatusName(status):
    """Human label for STREET_* bookkeeping ids."""
    try:
        key = int(status)
    except (TypeError, ValueError):
        return STREET_STATUS_NAMES[STREET_SECURED]
    return STREET_STATUS_NAMES.get(key, STREET_STATUS_NAMES[STREET_SECURED])


def streetAllowsRecreep(status):
    """True only for contested (incomplete-reclaim) streets."""
    try:
        return int(status) == STREET_CONTESTED
    except (TypeError, ValueError):
        return False


def streetPurityLockBlocksRise(locked, newLevel, currentLevel, enabled=None):
    """True when a finished-reclaim purity lock should refuse a pollution rise.

    ``locked`` is AI bookkeeping (PollutionManagerAI._purityLocked), not the
    default STREET_SECURED status for never-stained zones.
    """
    if enabled is None:
        enabled = STREET_PURITY_LOCK_ENABLED
    if not enabled or not locked:
        return False
    try:
        nxt = float(newLevel)
        cur = float(currentLevel)
    except (TypeError, ValueError):
        return False
    return nxt > cur


def pollutionRecreepStep(level, perTick=None, cap=None):
    """Next pollution after one incomplete-reclaim re-creep tick.

    Pure streets stay pure (no stain from zero). Contested residual ink
    creeps toward ``cap`` (default POLLUTION_RECREEP_CAP) by ``perTick``.
    """
    current = clampPollution(level)
    if current <= POLLUTION_PURE:
        return POLLUTION_PURE
    step = (
        float(POLLUTION_RECREEP_PER_TICK)
        if perTick is None else float(perTick))
    if step <= 0.0:
        return current
    limit = (
        float(POLLUTION_RECREEP_CAP) if cap is None else float(cap))
    limit = clampPollution(limit)
    if current >= limit:
        return current
    return clampPollution(min(limit, current + step))


def hoodFogColor(zoneId, level):
    """Fog RGB scaled by pollution density factor for this hood."""
    bias = hoodPollutionBias(zoneId)
    fog = bias['fog']
    dens = pollutionDensityFactor(level)
    return (
        fog[0] * (0.7 + 0.3 * dens),
        fog[1] * (0.75 + 0.25 * dens),
        fog[2],
    )


def hoodFogCreamDissolveColor(zoneId, level, creamBlend):
    """Ink fog RGB mixed toward sunny cream during purity dissolve.

    creamBlend 0 = hood ink fog; 1 = FOG_CREAM_DISSOLVE_COLOR. Density still
    drives how thick the fog reads; this only shifts the palette as it lifts.
    """
    ink = hoodFogColor(zoneId, level)
    blend = max(0.0, min(1.0, float(creamBlend)))
    if blend <= 0.0:
        return ink
    cream = FOG_CREAM_DISSOLVE_COLOR
    return (
        ink[0] + (float(cream[0]) - ink[0]) * blend,
        ink[1] + (float(cream[1]) - ink[1]) * blend,
        ink[2] + (float(cream[2]) - ink[2]) * blend,
    )


def hoodFogExpDensity(zoneId, level):
    """Exponential fog density for this hood at pollution level (ramped)."""
    bias = hoodPollutionBias(zoneId)
    return (
        CORRUPT_FOG_EXP_MAX
        * float(bias.get('fogExpScale', 1.0))
        * pollutionDensityFactor(level))


def hoodHazeAlpha(zoneId, level):
    """Fullscreen ink-haze opacity for this hood at pollution level."""
    dens = pollutionDensityFactor(level)
    if dens <= 0.0:
        return 0.0
    # Slight hood thickener so Silly/Punchline read heavier than Loopy.
    bias = hoodPollutionBias(zoneId)
    scale = float(bias.get('fogExpScale', 1.0))
    return min(0.55, POLLUTION_HAZE_ALPHA_MAX * dens * (0.85 + 0.15 * scale))


def hoodColorGrade(zoneId, level):
    """Render color-scale RGB (alpha 1) for hood-specific sickly grade."""
    bias = hoodPollutionBias(zoneId)
    drop = bias['gradeDrop']
    dens = pollutionDensityFactor(level)
    return (
        1.0 - (drop[0] * dens),
        1.0 - (drop[1] * dens),
        1.0 - (drop[2] * dens),
    )


def hoodPropTint(zoneId, level):
    """Street-geom multiply RGB for pollutionPropTint (1,1,1 when pure)."""
    dens = pollutionDensityFactor(level)
    if dens <= POLLUTION_PURE:
        return (1.0, 1.0, 1.0)
    bias = hoodPollutionBias(zoneId)
    target = bias['propTint']
    # Lerp white → hood prop tint by density factor.
    return (
        1.0 - (1.0 - target[0]) * dens,
        1.0 - (1.0 - target[1]) * dens,
        1.0 - (1.0 - target[2]) * dens,
    )


def hoodPropTintCreamFadeColor(zoneId, level, creamBlend, inkRgb=None):
    """Hood prop-tint RGB mixed toward sunny cream during purity fade.

    creamBlend 0 = hood ink prop tint (or inkRgb capture); 1 =
    HOOD_TINT_CREAM_FADE_COLOR. Density / inkRgb still set how corrupted the
    geom reads; this only shifts the palette as street purity completes.
    """
    if inkRgb is None:
        ink = hoodPropTint(zoneId, level)
    else:
        ink = (
            float(inkRgb[0]), float(inkRgb[1]), float(inkRgb[2]))
    blend = max(0.0, min(1.0, float(creamBlend)))
    if blend <= 0.0:
        return ink
    cream = HOOD_TINT_CREAM_FADE_COLOR
    return (
        ink[0] + (float(cream[0]) - ink[0]) * blend,
        ink[1] + (float(cream[1]) - ink[1]) * blend,
        ink[2] + (float(cream[2]) - ink[2]) * blend,
    )


def entryVignetteInk(zoneId):
    """Near-black rubber-hose ink RGB for street-entry edge vignette."""
    bias = hoodPollutionBias(zoneId)
    fog = bias.get('fog', ENTRY_VIGNETTE_INK[:3])
    # Crush fog toward ink-black so edges read as corruption, not a wash.
    return (
        min(0.14, float(fog[0]) * 0.45),
        min(0.10, float(fog[1]) * 0.40),
        min(0.14, float(fog[2]) * 0.50),
        1.0,
    )
