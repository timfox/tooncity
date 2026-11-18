"""Tunables for the rubber-hose melee prototype."""

# Attack input. Classic Toontown uses Delete for pies and Ctrl for jump;
# F is free for "Fight" and stays out of the way of pie toss.
ATTACK_KEY = 'f'
ATTACK_KEY_ALT = 'mouse1'

# Soft-target cone (degrees half-angle) and range (Panda units / feet-ish).
TARGET_RANGE = 14.0
TARGET_HALF_ANGLE_DEG = 55.0
# Sticky lock: hold current target well past a brief glance (soft-lock feel).
TARGET_LOCK_HOLD_SEC = 3.5
TARGET_STICKY_RANGE = 18.0
TARGET_STICKY_HALF_ANGLE_DEG = 95.0

# Soft-lock target cycle — manual next/prev among sticky-range hostiles so
# players can switch focus mid rubber-hose melee (KH-feel targeting without
# KH branding / keyblades). Tab next, ` (backquote, beside Tab) prev.
# Uses sticky cone so mid-fight switches stay readable. Cooldown stops key
# repeat spam from double-firing snaps.
TARGET_CYCLE_ENABLED = True
TARGET_CYCLE_NEXT_KEY = 'tab'
TARGET_CYCLE_PREV_KEY = '`'
TARGET_CYCLE_COOLDOWN_SEC = 0.12
TARGET_CYCLE_RANGE = 18.0
TARGET_CYCLE_HALF_ANGLE_DEG = 95.0

# Soft-lock cycle reticle pulse — brief rubber-hose pulse when Tab/` switches
# the sticky lock so the new target reads clearly (tracking feel without the
# full acquire snap FOV / accents spam). Milder/snappier than
# SOFT_LOCK_RETICLE_* hose pop. Deepened cream cue (#210 deepen): stronger
# cycle cream ring + quiet cycle cream wash so cycling reads juicier —
# distinct from acquire reticle pulse (#92) and i-frame cream wash deepen
# (#228). SOFT_LOCK_CYCLE_PULSE_ENABLED = False drops the cycle pulse only
# (cycle still switches lock).
SOFT_LOCK_CYCLE_PULSE_ENABLED = True
# (sx, sy, sz, sec) multipliers of settle scale — flat then tall, snappier.
SOFT_LOCK_CYCLE_PULSE_SQUASH = (1.35, 1.35, 0.72, 0.035)
SOFT_LOCK_CYCLE_PULSE_STRETCH = (0.82, 0.82, 1.28, 0.05)
SOFT_LOCK_CYCLE_PULSE_SETTLE_SEC = 0.06
# Deepened cream pulse ring on cycle — juicier than original #210 ring,
# still quieter/faster than acquire ring (#92). Reuses acquire ring half /
# colors / bin; peak/sec/alpha deepened. SOFT_LOCK_CYCLE_PULSE_RING_ENABLED
# = False drops the ring only.
SOFT_LOCK_CYCLE_PULSE_RING_ENABLED = True
SOFT_LOCK_CYCLE_PULSE_RING_PEAK = 1.90
SOFT_LOCK_CYCLE_PULSE_RING_SEC = 0.18
SOFT_LOCK_CYCLE_PULSE_RING_PEAK_ALPHA = 0.58

# Soft-lock cycle cream wash — quiet aspect2d veil after deepened cycle
# cream ring so Tab/` switches read juicier. SoftLockCreamWashPulse (#155)
# / SoftLockFovCreamWashPulse (#160) grammar; quieter/faster under acquire
# reticle wash. Cream/pastel only. Distinct from dodge i-frame cream wash
# deepen (#228). Toggle SOFT_LOCK_CYCLE_CREAM_WASH_ENABLED = False drops
# wash only (cycle pulse + ring still fire).
SOFT_LOCK_CYCLE_CREAM_WASH_ENABLED = True
SOFT_LOCK_CYCLE_CREAM_WASH_DELAY_SEC = 0.12  # after cycle start; mid-ring
SOFT_LOCK_CYCLE_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SOFT_LOCK_CYCLE_CREAM_WASH_PEAK = 0.06
SOFT_LOCK_CYCLE_CREAM_WASH_MID = 0.035
SOFT_LOCK_CYCLE_CREAM_WASH_IN_SEC = 0.04
SOFT_LOCK_CYCLE_CREAM_WASH_PULSE_SEC = 0.06
SOFT_LOCK_CYCLE_CREAM_WASH_HOLD_SEC = 0.03
SOFT_LOCK_CYCLE_CREAM_WASH_OUT_SEC = 0.18
SOFT_LOCK_CYCLE_CREAM_WASH_BIN = 27  # under acquire reticle wash (28)


def softLockCyclePulseScaleKeys(settle=None):
    """Return (settle_xyz, squash_xyz, stretch_xyz) for cycle reticle pulse.

    Pure helper for HitJuice.playSoftLockCyclePulse and headless tests.
    Each xyz is a 3-tuple of floats (uniform settle × cycle squash/stretch).
    """
    if settle is None:
        settle = SOFT_LOCK_RETICLE_SETTLE_SCALE
    settle = max(0.001, float(settle))
    sx, sy, sz, _squashSec = SOFT_LOCK_CYCLE_PULSE_SQUASH
    tx, ty, tz, _stretchSec = SOFT_LOCK_CYCLE_PULSE_STRETCH
    return (
        (settle, settle, settle),
        (settle * float(sx), settle * float(sy), settle * float(sz)),
        (settle * float(tx), settle * float(ty), settle * float(tz)),
    )


def softLockCycleCreamWashPeakAtSec(delay=None, inSec=None):
    """Seconds from cycle pulse start until cycle cream wash reaches peak."""
    if delay is None:
        delay = SOFT_LOCK_CYCLE_CREAM_WASH_DELAY_SEC
    if inSec is None:
        inSec = SOFT_LOCK_CYCLE_CREAM_WASH_IN_SEC
    return max(0.0, float(delay)) + max(0.0, float(inSec))


# Combo: 3 stretch punches, cartoon cadence with overshoot on the finisher.
COMBO_LENGTH = 3
COMBO_WINDOW_SEC = 0.55
COMBO_RECOVERY_SEC = 0.35

# Per-hit anim names (existing toon anims) and play rates for rubber-hose snap.
# Rates > 1 read as snappy cartoon timing; finisher slows slightly for weight.
COMBO_ANIMS = ('swing', 'throw', 'sound')
COMBO_PLAY_RATES = (1.85, 2.1, 1.25)
COMBO_DAMAGE = (8, 12, 28)

# Hitstop / freeze on connect — pauses juice + anims so the impact silhouette
# sticks before launch / hop / FOV punch. Longer on finisher. Client juice only.
HITSTOP_ENABLED = True
HITSTOP_SEC = (0.05, 0.065, 0.12)
HITSTOP_FREEZE_ANIMS = True

# Camera FOV punch + settle on finisher slam connect (degrees).
# Punch widens the lens, out drops into a brief rubber-hose undershoot,
# then settle eases back to base — juicier slam impact after air-juggle
# cancel→slam (#196) without KH branding. Soft-lock FOV yields while this runs.
FINISHER_FOV_PUNCH = 17.5
FINISHER_FOV_IN_SEC = 0.045
FINISHER_FOV_OUT_SEC = 0.12
# Degrees *below* base during the settle undershoot (0 disables settle beat).
FINISHER_FOV_SETTLE = 3.0
FINISHER_FOV_SETTLE_SEC = 0.14


def finisherFovPunchKeys(baseFov, punch=None, settle=None):
    """Return (base, peak, trough, rest) FOV degrees for slam punch+settle.

    Pure helper for MeleeCombatController._playFinisherFovPunch and headless
    tests. trough is base - settle (undershoot); rest is always base.
    """
    base = float(baseFov)
    if punch is None:
        punch = FINISHER_FOV_PUNCH
    if settle is None:
        settle = FINISHER_FOV_SETTLE
    punch = max(0.0, float(punch))
    settle = max(0.0, float(settle))
    peak = base + punch
    trough = base - settle
    return (base, peak, trough, base)

# Optional brief camera shake on finisher (applied after soft-lock each tick).
# Keep amplitude small — cartoon thud, not earthquake.
FINISHER_SHAKE_ENABLED = True
FINISHER_SHAKE_AMPLITUDE = 0.42
FINISHER_SHAKE_SEC = 0.14

# Soft-lock camera / facing nudge while melee is enabled (per-tick lerp).
# Idle stays mild; mid-combo adds a soft orbit/pull for readable framing without
# hard-locking (smart-cam + page-up/down still win).
LOCK_FACE_LERP = 0.12
LOCK_CAM_LERP = 0.08
LOCK_CAM_LOOK_HEIGHT = 1.4
# Mid-combo soft-lock boost — readable melee framing, still yields to player cam.
LOCK_COMBO_FACE_LERP = 0.22
LOCK_COMBO_CAM_LERP = 0.16
LOCK_COMBO_ORBIT_LERP = 0.12
LOCK_COMBO_ORBIT_LATERAL = 1.4
LOCK_COMBO_ORBIT_PULL = 0.65
LOCK_COMBO_ORBIT_LIFT = 0.28
# After LocalAvatar.updateSmartCamera (priority 47) so the bias sticks a frame.
LOCK_CAM_TASK_PRIORITY = 50

# Soft-lock hit assist — one-shot yaw/aim nudge on melee connect against the
# sticky soft-lock target so combo strings stay glued without hard lock.
# Stronger than per-tick LOCK_FACE_LERP but hard-capped; deadzone skips tiny
# error. Deepened past #278 so soft-lock connect glue reads juicier still
# (#204 / #254 / #278 deepen+). LOCK_HIT_ASSIST_ENABLED = False drops assist +
# cream wash (tick nudge stays).
LOCK_HIT_ASSIST_ENABLED = True
LOCK_HIT_ASSIST_YAW_FRAC = 0.70
LOCK_HIT_ASSIST_YAW_MAX_DEG = 30.0
LOCK_HIT_ASSIST_CAM_FRAC = 0.42
LOCK_HIT_ASSIST_DEADZONE_DEG = 2.0

# Soft-lock hit-assist cream wash — soft aspect2d veil the instant connect
# yaw/aim nudge fires (#204 / #254 / #278 deepen+) so hit assist reads juicier
# still. SoftLock FOV / SoftLockCycle / DodgeCancel cream wash grammar.
# Quieter / faster than hit-spark cream wash (#147) so combo strings stay
# readable; cream/pastel only. Distinct from soft-lock cycle reticle cream
# deepen (#233), hurt wash cream deepen (#247 / #263 / #287), i-frame cream
# wash (#296), combo edge cream (#291), and dodge-cancel cream flash (#281).
# Toggle LOCK_HIT_ASSIST_CREAM_WASH_ENABLED = False drops wash (+ aftershock)
# only — assist yaw/cam still fire.
LOCK_HIT_ASSIST_CREAM_WASH_ENABLED = True
LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC = 0.0  # fire with nudge — no settle lag
LOCK_HIT_ASSIST_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
LOCK_HIT_ASSIST_CREAM_WASH_PEAK = 0.098
LOCK_HIT_ASSIST_CREAM_WASH_MID = 0.062
LOCK_HIT_ASSIST_CREAM_WASH_IN_SEC = 0.03
LOCK_HIT_ASSIST_CREAM_WASH_PULSE_SEC = 0.09
LOCK_HIT_ASSIST_CREAM_WASH_HOLD_SEC = 0.06
LOCK_HIT_ASSIST_CREAM_WASH_OUT_SEC = 0.28
LOCK_HIT_ASSIST_CREAM_WASH_BIN = 26  # under cycle wash (27) / hit wash (28)

# Soft-lock hit-assist cream wash aftershock — residual cream flecks + soft
# halo after the assist flash so connect glue still reads. Deepened past #278
# (more flecks + stronger halo). Same grammar as dodge-cancel / hurt-stagger
# cream wash aftershock, quieter because assists fire often mid-combo.
# Cream/pastel only. Toggle
# LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_ENABLED = True
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.03  # after flash starts
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, 0.04)
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_COUNT = 5
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_SIZE = 0.015
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_DRIFT = 0.22
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_FALL = 0.145
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_SEC = 0.22
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.78)
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_BIN = 28  # over assist wash veil (26)
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.38
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_START = 0.20
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.22
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.18
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.11
LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)


def hitAssistCreamWashPeakAtSec(delay=None, inSec=None):
    """Seconds from assist nudge until cream wash flash reaches peak alpha."""
    if delay is None:
        delay = LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC
    if inSec is None:
        inSec = LOCK_HIT_ASSIST_CREAM_WASH_IN_SEC
    return max(0.0, float(delay)) + max(0.0, float(inSec))


def hitAssistCreamWashAftershockAtSec(delay=None):
    """Seconds from assist nudge until cream wash aftershock residual begins."""
    if delay is None:
        delay = LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_DELAY_SEC
    return max(0.0, float(delay))

# Soft-lock reticle hose pop — when acquire/snap lands on a corrupt/hostile.
# Warm cream brackets + ink flecks; rubber-hose squash → stretch → settle.
# Toontown spiritual-sequel tone only — no keyblades / no KH branding.
SOFT_LOCK_RETICLE_LIFT = 2.35
SOFT_LOCK_RETICLE_HALF = 0.42
SOFT_LOCK_RETICLE_THICK = 0.08
SOFT_LOCK_RETICLE_SETTLE_SCALE = 1.0
# (sx, sy, sz, sec) multipliers of settle scale — flat then tall like combo HUD.
SOFT_LOCK_RETICLE_SQUASH = (1.55, 1.55, 0.55, 0.05)
SOFT_LOCK_RETICLE_STRETCH = (0.7, 0.7, 1.45, 0.07)
SOFT_LOCK_RETICLE_SETTLE_SEC = 0.09
SOFT_LOCK_RETICLE_COLOR = (1.0, 0.96, 0.72, 0.92)
SOFT_LOCK_RETICLE_INK_COLOR = (0.2, 0.06, 0.26, 0.85)
SOFT_LOCK_ACCENT_CREAM_COUNT = 3
SOFT_LOCK_ACCENT_INK_COUNT = 4
SOFT_LOCK_ACCENT_SIZE = 0.14
SOFT_LOCK_ACCENT_DRIFT = 0.85
SOFT_LOCK_ACCENT_SEC = 0.22
SOFT_LOCK_ACCENT_CREAM_COLOR = (1.0, 0.95, 0.55, 0.95)
SOFT_LOCK_ACCENT_CREAM_END = (1.0, 0.9, 0.45, 0.0)
SOFT_LOCK_ACCENT_INK_COLOR = (0.22, 0.06, 0.28, 0.9)
SOFT_LOCK_ACCENT_INK_END = (0.38, 0.1, 0.42, 0.0)

# Soft-lock acquire FOV punch — brief rubber-hose kick when snap lands.
# Milder/shorter than FINISHER_FOV_*; defers while HitStopFx is active so it
# composes with connect freeze (#68) instead of fighting mid-hitstop FOV.
SOFT_LOCK_FOV_ENABLED = True
SOFT_LOCK_FOV_PUNCH = 5.5
SOFT_LOCK_FOV_IN_SEC = 0.04
SOFT_LOCK_FOV_OUT_SEC = 0.12

# Soft-lock FOV cream wash pulse — soft aspect2d veil after FOV punch (#74).
# Reticle cream wash (#155) / juggle cream wash (#150) grammar. Quieter than
# reticle wash; armed when FOV punch actually plays (incl. HitStopFx flush).
# SOFT_LOCK_FOV_CREAM_WASH_ENABLED = False drops wash only.
SOFT_LOCK_FOV_CREAM_WASH_ENABLED = True
SOFT_LOCK_FOV_CREAM_WASH_DELAY_SEC = 0.22  # after FOV start; past in+out (~0.16)
SOFT_LOCK_FOV_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SOFT_LOCK_FOV_CREAM_WASH_PEAK = 0.07
SOFT_LOCK_FOV_CREAM_WASH_MID = 0.04
SOFT_LOCK_FOV_CREAM_WASH_IN_SEC = 0.05
SOFT_LOCK_FOV_CREAM_WASH_PULSE_SEC = 0.07
SOFT_LOCK_FOV_CREAM_WASH_HOLD_SEC = 0.04
SOFT_LOCK_FOV_CREAM_WASH_OUT_SEC = 0.26
SOFT_LOCK_FOV_CREAM_WASH_BIN = 27  # under reticle wash (28) / soft-lock pulse

# Soft-lock acquire cream pulse ring — expanding pastel cream ring on snap.
# Layers with SoftLockReticleFx hose pop + accents + FOV punch (#52/#74).
# Cream/pastel only — no ink, no keyblades / no KH branding.
SOFT_LOCK_PULSE_RING_ENABLED = True
SOFT_LOCK_PULSE_RING_HALF = 0.48
SOFT_LOCK_PULSE_RING_START = 0.4
SOFT_LOCK_PULSE_RING_PEAK = 2.15
SOFT_LOCK_PULSE_RING_SEC = 0.24
SOFT_LOCK_PULSE_RING_PEAK_ALPHA = 0.62
SOFT_LOCK_PULSE_RING_COLOR = (1.0, 0.96, 0.78, 0.95)
SOFT_LOCK_PULSE_RING_END = (1.0, 0.92, 0.62, 0.0)
SOFT_LOCK_PULSE_RING_BIN = 25

# Soft-lock cream wash pulse — soft aspect2d veil after cream pulse ring
# (#92). Combo / juggle / finisher / dodge cream wash grammar. Quieter settle
# beat after acquire snap; cream/pastel only. Toggle
# SOFT_LOCK_CREAM_WASH_ENABLED = False drops wash only.
SOFT_LOCK_CREAM_WASH_ENABLED = True
SOFT_LOCK_CREAM_WASH_DELAY_SEC = 0.36  # after snap; after pulse ring (0.24)
SOFT_LOCK_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
SOFT_LOCK_CREAM_WASH_PEAK = 0.09
SOFT_LOCK_CREAM_WASH_MID = 0.05
SOFT_LOCK_CREAM_WASH_IN_SEC = 0.05
SOFT_LOCK_CREAM_WASH_PULSE_SEC = 0.08
SOFT_LOCK_CREAM_WASH_HOLD_SEC = 0.05
SOFT_LOCK_CREAM_WASH_OUT_SEC = 0.30
SOFT_LOCK_CREAM_WASH_BIN = 28  # soft veil under soft-lock pulse (25+) / HUD

# Brief aspect2d white flash on connect (beyond hitstop).
HIT_FLASH_PEAK_ALPHA = 0.38
HIT_FLASH_IN_SEC = 0.03
HIT_FLASH_OUT_SEC = 0.10

# On-screen combo counter (ticks on hackslash-hit; fades after break).
# Parked lower-left so reclaim banners / soft-lock hints stay readable up top.
COMBO_COUNTER_POS = (-0.95, 0.0, -0.42)
COMBO_COUNTER_BASE_SCALE = 0.11
# Rubber-hose HUD pop on each increment: flat squash → tall stretch → settle.
# Multipliers apply to settle scale (sx = width, sz = height on aspect2d TextNode).
COMBO_COUNTER_SQUASH = (1.65, 1.0, 0.52, 0.05)
COMBO_COUNTER_STRETCH = (0.72, 1.0, 1.48, 0.07)
COMBO_COUNTER_SETTLE_SEC = 0.10
COMBO_BREAK_SEC = 1.15
COMBO_FADE_SEC = 0.45
COMBO_COUNTER_LABEL = 'PUNCH'
# Color ramps slightly warmer as the string climbs (still readable on busy streets).
COMBO_COUNTER_COLORS = (
    (1.0, 0.95, 0.55, 1.0),
    (1.0, 0.85, 0.35, 1.0),
    (1.0, 0.7, 0.25, 1.0),
    (1.0, 0.55, 0.2, 1.0),
)
# Tiny ink flecks that flick off the counter on increment (cartoon ink, not KH).
COMBO_COUNTER_FLECK_COUNT = 3
COMBO_COUNTER_FLECK_SIZE = 0.016
COMBO_COUNTER_FLECK_DRIFT = 0.11
COMBO_COUNTER_FLECK_SEC = 0.2
COMBO_COUNTER_FLECK_COLOR = (0.18, 0.06, 0.22, 0.9)
COMBO_COUNTER_FLECK_END_COLOR = (0.35, 0.12, 0.4, 0.0)
# Cream sparkle layer on the same tick/pop — composes with hose pop + ink flecks.
# Warm cream glitter (aspect2d), not KH sparkles / no keyblade branding.
COMBO_COUNTER_CREAM_ENABLED = True
COMBO_COUNTER_CREAM_COUNT = 3
COMBO_COUNTER_CREAM_STREAK_COUNT = 2
COMBO_COUNTER_CREAM_SIZE = 0.014
COMBO_COUNTER_CREAM_STREAK_SIZE = 0.01
COMBO_COUNTER_CREAM_DRIFT = 0.13
COMBO_COUNTER_CREAM_SEC = 0.18
COMBO_COUNTER_CREAM_COLOR = (1.0, 0.96, 0.72, 0.95)
COMBO_COUNTER_CREAM_END = (1.0, 0.92, 0.55, 0.0)
COMBO_COUNTER_CREAM_STREAK_COLOR = (1.0, 0.98, 0.82, 0.9)
COMBO_COUNTER_CREAM_STREAK_END = (1.0, 0.9, 0.5, 0.0)
COMBO_COUNTER_CREAM_BIN = 57
# Delayed cream aftershock after the combo-counter cream tick sparkle (#85).
# Same residual grammar as PERFECT_DODGE_CREAM_AFTERSHOCK_* /
# LAUNCH_HANG_CREAM_AFTERSHOCK_* — softer cream flecks + soft halo that settle
# on aspect2d. Cream/pastel only (no ink). No keyblades / no KH branding.
COMBO_COUNTER_CREAM_AFTERSHOCK_ENABLED = True
COMBO_COUNTER_CREAM_AFTERSHOCK_DELAY_SEC = 0.16
COMBO_COUNTER_CREAM_AFTERSHOCK_COUNT = 2
COMBO_COUNTER_CREAM_AFTERSHOCK_STREAK_COUNT = 1
COMBO_COUNTER_CREAM_AFTERSHOCK_SIZE = 0.011
COMBO_COUNTER_CREAM_AFTERSHOCK_STREAK_SIZE = 0.008
COMBO_COUNTER_CREAM_AFTERSHOCK_DRIFT = 0.1
COMBO_COUNTER_CREAM_AFTERSHOCK_SEC = 0.28
COMBO_COUNTER_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.88)
COMBO_COUNTER_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
COMBO_COUNTER_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.85)
COMBO_COUNTER_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_ENABLED = True
COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_HALF = 0.07
COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_START = 0.45
COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_PEAK = 1.55
COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_SEC = 0.26
COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.22
COMBO_COUNTER_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)
COMBO_COUNTER_CREAM_AFTERSHOCK_BIN = 58

# Combo-counter cream wash pulse — soft aspect2d veil after cream aftershock
# (#116). Finisher / melee-hit / dodge-trail cream wash grammar. Quieter than
# finisher wash (counter ticks fire more often); cream/pastel only. Toggle
# COMBO_COUNTER_CREAM_WASH_ENABLED = False drops wash (+ wash aftershock).
COMBO_COUNTER_CREAM_WASH_ENABLED = True
COMBO_COUNTER_CREAM_WASH_DELAY_SEC = 0.34  # after tick; after aftershock (0.16)
COMBO_COUNTER_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
COMBO_COUNTER_CREAM_WASH_PEAK = 0.09
COMBO_COUNTER_CREAM_WASH_MID = 0.05
COMBO_COUNTER_CREAM_WASH_IN_SEC = 0.05
COMBO_COUNTER_CREAM_WASH_PULSE_SEC = 0.08
COMBO_COUNTER_CREAM_WASH_HOLD_SEC = 0.05
COMBO_COUNTER_CREAM_WASH_OUT_SEC = 0.30
COMBO_COUNTER_CREAM_WASH_BIN = 28  # soft veil under soft-lock pulse (25+) / HUD

# Combo-counter cream wash aftershock — residual cream flecks + soft halo after
# the wash pulse (#147). Same grammar as HIT_SPARK_CREAM_WASH_AFTERSHOCK_*
# (#174) / PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_* (#171); quieter than melee-hit
# wash aftershock (counter ticks fire more often). Distinct from tick cream
# aftershock (#116). Cream/pastel only. Toggle
# COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_ENABLED = True
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.22  # after wash starts
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.08)
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_COUNT = 3
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_SIZE = 0.011
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_DRIFT = 0.20
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_FALL = 0.16
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_SEC = 0.26
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.64)
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_BIN = 30  # over wash veil (28)
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.36
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_HALO_START = 0.20
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.00
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.22
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.08
COMBO_COUNTER_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Combo-counter cream edge pop — local cream border strips framing the punch
# counter when it ticks so the string reads clearly (KH-feel HUD readability,
# Toontown cream only). Act-banner / wave-announce cream edge grammar, snappier
# because ticks fire often. Deepened past #267 (#237 / #224 deepen): juicier
# still peak/hold/scale/thickness + richer local cream edge aftershock so
# combo hits read juicier — distinct from hurt-stagger cream wash deepen
# (#287), dodge-cancel cream flash (#281), i-frame cream wash (#228 / #272),
# and aim-nudge cream deepen (#254). Soft under counter TextNode (bin 55).
# Toggle COMBO_COUNTER_CREAM_EDGE_ENABLED = False drops the edge pop
# (+ edge aftershock).
COMBO_COUNTER_CREAM_EDGE_ENABLED = True
COMBO_COUNTER_CREAM_EDGE_COLOR = (1.0, 0.97, 0.82, 1.0)  # sunny cream
COMBO_COUNTER_CREAM_EDGE = 0.032  # strip thickness in aspect2d units
COMBO_COUNTER_CREAM_EDGE_HALF_W = 0.22  # local frame half-width around text
COMBO_COUNTER_CREAM_EDGE_HALF_H = 0.08  # local frame half-height around text
COMBO_COUNTER_CREAM_EDGE_PEAK = 0.84
COMBO_COUNTER_CREAM_EDGE_PULSE = 0.58  # mid-beat alpha after peak
COMBO_COUNTER_CREAM_EDGE_IN_SEC = 0.04
COMBO_COUNTER_CREAM_EDGE_HOLD_SEC = 0.07
COMBO_COUNTER_CREAM_EDGE_PULSE_SEC = 0.10
COMBO_COUNTER_CREAM_EDGE_OUT_SEC = 0.22
COMBO_COUNTER_CREAM_EDGE_SCALE_PEAK = 1.44  # soft outward pop on the frame
COMBO_COUNTER_CREAM_EDGE_BIN = 54  # under counter TextNode (55) / flecks (56+)

# Combo-counter cream edge aftershock — residual cream flecks + soft halo
# local to the punch-counter frame after the deepened-past-#267 edge pop so
# ticks still read juicier. Same residual grammar as combo cream wash
# aftershock / i-frame cream wash aftershock, quieter + tighter (ticks fire
# often; stays on the HUD frame — not a fullscreen wash). Distinct from
# hurt wash (#287), dodge-cancel flash (#281), i-frame wash (#228 / #272),
# and aim-nudge cream (#254). Toggle
# COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_ENABLED = False drops aftershock only.
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_ENABLED = True
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_DELAY_SEC = 0.06  # after edge start; mid-pop
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_COUNT = 5
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_SIZE = 0.013
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_DRIFT = 0.14
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_FALL = 0.12
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_SEC = 0.28
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.84)
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_BIN = 53  # under edge strips (54)
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_ENABLED = True
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_HALF = 0.18
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_START = 0.35
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_PEAK = 1.35
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_SEC = 0.24
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_PEAK_ALPHA = 0.22
COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)


def comboCounterCreamEdgePeakAtSec(inSec=None):
    """Seconds from tick until cream edge pop reaches peak alpha."""
    if inSec is None:
        inSec = COMBO_COUNTER_CREAM_EDGE_IN_SEC
    return max(0.0, float(inSec))


def comboCounterCreamEdgeAftershockAtSec(delay=None):
    """Seconds from tick until cream edge aftershock residual begins."""
    if delay is None:
        delay = COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_DELAY_SEC
    return max(0.0, float(delay))


# Mid/finisher launcher juice (upward juggle feel on the target).
LAUNCH_HIT_INDEX = 1  # 2nd hit starts the juggle; finisher lifts more
LAUNCH_HEIGHT = (0.0, 1.85, 3.1)
LAUNCH_UP_SEC = (0.0, 0.12, 0.16)
# Readable rubber-hose hang/float at apex before fall (hover + squash + sparkle).
LAUNCH_HANG_SEC = (0.0, 0.18, 0.28)
LAUNCH_HANG_HOVER = (0.0, 0.28, 0.45)
LAUNCH_HANG_SQUASH = (1.45, 1.45, 0.48, 0.07)
LAUNCH_HANG_STRETCH = (0.65, 0.65, 1.55, 0.1)
LAUNCH_HANG_SPARK_COUNT = 5
LAUNCH_HANG_SPARK_SIZE = 0.16
LAUNCH_HANG_SPARK_DRIFT = 0.75
LAUNCH_HANG_SPARK_LIFT = 0.4
LAUNCH_HANG_SPARK_SEC = 0.24
LAUNCH_HANG_SPARK_COLOR = (1.0, 0.95, 0.55, 0.95)
# Cream sparkle at hang apex — world-space flecks + soft halo (not aspect2d).
# Layers with hang hover/squash; does not fight CreamSlamFlashFx screen flash.
# Per-hit tuples index like LAUNCH_* (0 unused / mid / finisher).
LAUNCH_HANG_CREAM_ENABLED = True
LAUNCH_HANG_CREAM_COUNT = (0, 5, 7)
LAUNCH_HANG_CREAM_STREAK_COUNT = (0, 2, 3)
LAUNCH_HANG_CREAM_SIZE = 0.18
LAUNCH_HANG_CREAM_STREAK_SIZE = 0.12
LAUNCH_HANG_CREAM_DRIFT = (0.0, 0.9, 1.15)
LAUNCH_HANG_CREAM_LIFT = 0.55
LAUNCH_HANG_CREAM_SEC = 0.28
LAUNCH_HANG_CREAM_COLOR = (1.0, 0.96, 0.72, 0.95)
LAUNCH_HANG_CREAM_END = (1.0, 0.92, 0.55, 0.0)
LAUNCH_HANG_CREAM_STREAK_COLOR = (1.0, 0.98, 0.82, 0.9)
LAUNCH_HANG_CREAM_STREAK_END = (1.0, 0.9, 0.5, 0.0)
LAUNCH_HANG_CREAM_HALO_ENABLED = True
LAUNCH_HANG_CREAM_HALO_HALF = 0.45
LAUNCH_HANG_CREAM_HALO_START = 0.4
LAUNCH_HANG_CREAM_HALO_PEAK = 1.85
LAUNCH_HANG_CREAM_HALO_SEC = 0.26
LAUNCH_HANG_CREAM_HALO_PEAK_ALPHA = 0.42
LAUNCH_HANG_CREAM_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)
# Delayed cream aftershock after air-juggle hang sparkle — residual flecks/halo.
# Same grammar as PERFECT_DODGE_CREAM_AFTERSHOCK_* / HIT_SPARK_CREAM_AFTERSHOCK_*;
# cream/pastel only. Per-hit tuples index like LAUNCH_* (0 unused / mid / finisher).
LAUNCH_HANG_CREAM_AFTERSHOCK_ENABLED = True
LAUNCH_HANG_CREAM_AFTERSHOCK_DELAY_SEC = 0.2
LAUNCH_HANG_CREAM_AFTERSHOCK_COUNT = (0, 3, 4)
LAUNCH_HANG_CREAM_AFTERSHOCK_STREAK_COUNT = (0, 1, 2)
LAUNCH_HANG_CREAM_AFTERSHOCK_SIZE = 0.12
LAUNCH_HANG_CREAM_AFTERSHOCK_STREAK_SIZE = 0.09
LAUNCH_HANG_CREAM_AFTERSHOCK_DRIFT = 0.65
LAUNCH_HANG_CREAM_AFTERSHOCK_SEC = 0.38
LAUNCH_HANG_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.88)
LAUNCH_HANG_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
LAUNCH_HANG_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.85)
LAUNCH_HANG_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_ENABLED = True
LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_HALF = 0.42
LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_START = 0.32
LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_PEAK = 1.55
LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_SEC = 0.32
LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.26
LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)
# Air-juggle hang cream wash pulse — soft aspect2d veil after cream aftershock
# (#111). Combo / finisher / dodge-trail cream wash grammar. Soft settle beat
# after hang sparkle (#83). LAUNCH_HANG_CREAM_ENABLED = False drops cream path
# (sparkle + aftershock + wash). LAUNCH_HANG_CREAM_WASH_ENABLED = False drops
# wash only.
LAUNCH_HANG_CREAM_WASH_ENABLED = True
LAUNCH_HANG_CREAM_WASH_DELAY_SEC = 0.40  # after play; after aftershock (0.20)
LAUNCH_HANG_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
LAUNCH_HANG_CREAM_WASH_PEAK = 0.10
LAUNCH_HANG_CREAM_WASH_MID = 0.06
LAUNCH_HANG_CREAM_WASH_IN_SEC = 0.05
LAUNCH_HANG_CREAM_WASH_PULSE_SEC = 0.09
LAUNCH_HANG_CREAM_WASH_HOLD_SEC = 0.06
LAUNCH_HANG_CREAM_WASH_OUT_SEC = 0.34
LAUNCH_HANG_CREAM_WASH_BIN = 28  # soft veil under soft-lock pulse (25+) / HUD
LAUNCH_DOWN_SEC = (0.0, 0.16, 0.22)
# Local toon hop cue on finisher so the juggle reads as a shared air beat.
FINISHER_SELF_HOP = 1.15
FINISHER_SELF_UP_SEC = 0.11
FINISHER_SELF_DOWN_SEC = 0.2

# Air-juggle → slam cancel window. Mid-combo launch hangs the target; after
# rise settles into hang, F/LMB cancels into the stretch-punch finisher slam
# so aerial combo control reads clean (KH-feel rubber-hose without keyblades /
# KH branding). Early rise can buffer until the window opens.
JUGGLE_CANCEL_ENABLED = True
# Seconds after launch start before cancel-into-slam opens (after mid rise).
JUGGLE_CANCEL_START_SEC = 0.12
# How long cancel-into-slam stays open (covers hang + early fall).
JUGGLE_CANCEL_WINDOW_SEC = 0.45
# Buffer F/LMB pressed during early rise; fire when the cancel window opens.
JUGGLE_CANCEL_BUFFER = True


def juggleCancelSlamHitIndex(comboLength=None):
    """Finisher/slam hit index for air-juggle cancel-into-slam."""
    if comboLength is None:
        comboLength = COMBO_LENGTH
    return max(0, int(comboLength) - 1)


def isJuggleCancelWindowOpen(armed, openAt, until, now):
    """True while an air-juggle cancel→slam window is live."""
    if not armed:
        return False
    now = float(now)
    return float(openAt) <= now < float(until)


# I-frame / dodge cue after CorruptToon smacks the local toon.
IFRAME_SEC = 0.55
IFRAME_FLASH_ALPHA = 0.55

# Hurt stagger → recovery cancel. After a CorruptToon smack, brief committed
# stagger then a short cancel window into dodge (Shift/X) or melee (F/LMB) so
# combat stays rubber-hose responsive — KH-feel without keyblades / KH branding.
# Early stagger can buffer attack/dodge until the cancel window opens.
HURT_STAGGER_ENABLED = True
# Seconds of committed hurt stagger before cancel-into-dodge/melee opens
# (covers squash + early stretch of PLAYER_HIT_REACT_*).
HURT_STAGGER_SEC = 0.14
# How long cancel-into-dodge/melee stays open after stagger settles.
HURT_RECOVERY_CANCEL_WINDOW_SEC = 0.38
# Buffer F/LMB or Shift/X pressed during stagger; fire when cancel opens.
HURT_RECOVERY_CANCEL_BUFFER = True

# Hurt-stagger cream wash pulse — soft aspect2d veil during committed stagger
# (#199 / #215 / #247 / #263) so the smack still reads juicy before F/Shift
# cancel opens. Hit / perfect-dodge / soft-lock FOV cream wash grammar.
# Deepened past #263 so getting hit and recovering reads juicier still:
# brighter peak + longer mid hold + richer residual. Quieter than hit-connect
# wash (smacks fire often); peaks before HURT_STAGGER_SEC. Cream/pastel only.
# Distinct from dodge-cancel cream flash deepen (#242 / #257 / #281) — fires
# on smack stagger, not Shift→F cancel — and from i-frame cream wash deepen
# (#228 / #272) — settles during hurt lockout, not mid-roll invuln. Toggle
# HURT_STAGGER_CREAM_WASH_ENABLED = False drops wash (+ wash aftershock).
HURT_STAGGER_CREAM_WASH_ENABLED = True
HURT_STAGGER_CREAM_WASH_DELAY_SEC = 0.04  # early in stagger; before cancel open
HURT_STAGGER_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
HURT_STAGGER_CREAM_WASH_PEAK = 0.099
HURT_STAGGER_CREAM_WASH_MID = 0.075
HURT_STAGGER_CREAM_WASH_IN_SEC = 0.04
HURT_STAGGER_CREAM_WASH_PULSE_SEC = 0.11
HURT_STAGGER_CREAM_WASH_HOLD_SEC = 0.10
HURT_STAGGER_CREAM_WASH_OUT_SEC = 0.42
HURT_STAGGER_CREAM_WASH_BIN = 27  # under hit wash (28) / soft-lock pulse

# Hurt-stagger cream wash aftershock — residual cream flecks + soft halo after
# the wash pulse. Same grammar as HIT_SPARK_CREAM_WASH_AFTERSHOCK_* (#174) /
# PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_* (#171); deepened past #263 so recovery
# still reads after the veil (more flecks + stronger halo), quieter + earlier
# so flecks settle near cancel open. Cream/pastel only. Toggle
# HURT_STAGGER_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_ENABLED = True
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.08  # after wash starts
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.08)
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_COUNT = 6
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_SIZE = 0.017
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_DRIFT = 0.30
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_FALL = 0.24
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_SEC = 0.36
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.84)
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_BIN = 29  # over hurt wash veil (27)
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.48
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_START = 0.32
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.35
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.32
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.14
HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)


def isHurtRecoveryCancelWindowOpen(armed, openAt, until, now):
    """True while a hurt-stagger recovery cancel→dodge/melee window is live."""
    if not armed:
        return False
    now = float(now)
    return float(openAt) <= now < float(until)


def hurtStaggerTotalSec(stagger=None, window=None):
    """Total committed stagger + recovery cancel length."""
    if stagger is None:
        stagger = HURT_STAGGER_SEC
    if window is None:
        window = HURT_RECOVERY_CANCEL_WINDOW_SEC
    return max(0.0, float(stagger)) + max(0.0, float(window))


def hurtStaggerCreamWashPeakAtSec(delay=None, inSec=None):
    """Seconds from arm until cream wash reaches peak alpha (during stagger)."""
    if delay is None:
        delay = HURT_STAGGER_CREAM_WASH_DELAY_SEC
    if inSec is None:
        inSec = HURT_STAGGER_CREAM_WASH_IN_SEC
    return max(0.0, float(delay)) + max(0.0, float(inSec))


def hurtStaggerCreamWashAftershockAtSec(delay=None):
    """Seconds from wash start until cream wash aftershock residual begins."""
    if delay is None:
        delay = HURT_STAGGER_CREAM_WASH_AFTERSHOCK_DELAY_SEC
    return max(0.0, float(delay))


# Player-initiated dodge roll (Shift; Space stays jump).
DODGE_KEY = 'shift'
DODGE_KEY_ALT = 'x'
DODGE_DURATION_SEC = 0.28
DODGE_IFRAME_SEC = 0.42
DODGE_DISTANCE = 6.5
DODGE_COOLDOWN_SEC = 0.65
DODGE_SQUASH = (0.55, 0.55, 1.45, 0.12)

# Dodge → melee cancel window. Early roll is committed; late in the dash /
# as i-frames settle, F/LMB cancels remaining recovery into a fresh stretch-
# punch so Shift→F combo flow reads clean. Input during commitment can buffer
# until the window opens. Toontown spiritual-sequel tone — no keyblades / KH.
DODGE_CANCEL_ENABLED = True
# Seconds after dodge start before cancel-into-melee opens (late in the roll).
DODGE_CANCEL_START_SEC = 0.16
# How long the cancel-into-melee window stays open after it opens.
DODGE_CANCEL_WINDOW_SEC = 0.40
# Buffer F/LMB pressed during early dodge; fire when the cancel window opens.
DODGE_CANCEL_BUFFER = True

# Dodge-cancel cream wash flash — soft aspect2d veil the instant F/LMB cancels
# late-dodge recovery into stretch-punch (#186 / #219 / #242 / #257) so
# Shift→F reads clearly. SoftLock FOV / dodge-trail / hurt-stagger cream wash
# grammar. Deepened past #257 so dodge→melee windows read juicier still:
# brighter peak + longer mid hold + richer residual. Snappier than dodge-trail
# settle wash; cream/pastel only. Distinct from i-frame cream wash deepen
# (#228 / #272), combo cream edge deepen (#237), and hurt-stagger cream wash
# deepen (#247 / #263) — fires on intentional Shift→F cancel, not mid-roll
# invuln or smack stagger. Toggle DODGE_CANCEL_CREAM_WASH_ENABLED = False
# drops the cancel flash (+ aftershock).
DODGE_CANCEL_CREAM_WASH_ENABLED = True
DODGE_CANCEL_CREAM_WASH_DELAY_SEC = 0.0  # fire on cancel — no settle lag
DODGE_CANCEL_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
DODGE_CANCEL_CREAM_WASH_PEAK = 0.16
DODGE_CANCEL_CREAM_WASH_MID = 0.095
DODGE_CANCEL_CREAM_WASH_IN_SEC = 0.03
DODGE_CANCEL_CREAM_WASH_PULSE_SEC = 0.09
DODGE_CANCEL_CREAM_WASH_HOLD_SEC = 0.07
DODGE_CANCEL_CREAM_WASH_OUT_SEC = 0.32
DODGE_CANCEL_CREAM_WASH_BIN = 28  # with dodge-trail wash; under soft-lock pulse

# Dodge-cancel cream wash flash aftershock — residual cream flecks + soft halo
# after the cancel flash so Shift→F still reads. Same grammar as i-frame /
# hurt-stagger cream wash aftershock; deepened past #257 (more flecks +
# stronger halo), snappier because cancel is intentional. Cream/pastel only.
# Toggle DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock
# only.
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_ENABLED = True
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.04  # after flash starts
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, 0.0)
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_COUNT = 6
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_SIZE = 0.016
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_DRIFT = 0.30
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_FALL = 0.18
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_SEC = 0.28
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.82)
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_BIN = 30  # over cancel wash veil (28)
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.46
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_START = 0.28
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.28
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.24
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.13
DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)


def dodgeCancelCreamWashPeakAtSec(delay=None, inSec=None):
    """Seconds from cancel until cream wash flash reaches peak alpha."""
    if delay is None:
        delay = DODGE_CANCEL_CREAM_WASH_DELAY_SEC
    if inSec is None:
        inSec = DODGE_CANCEL_CREAM_WASH_IN_SEC
    return max(0.0, float(delay)) + max(0.0, float(inSec))


def dodgeCancelCreamWashAftershockAtSec(delay=None):
    """Seconds from cancel until cream flash aftershock residual begins."""
    if delay is None:
        delay = DODGE_CANCEL_CREAM_WASH_AFTERSHOCK_DELAY_SEC
    return max(0.0, float(delay))

# Perfect-dodge counter → melee. When dodge i-frames eat a CorruptToon
# telegraph, open a short rewarded cancel window into the next stretch-punch
# opener (damage bump + snappy rate). Builds on DODGE_CANCEL_* (#186) and
# perfect-dodge juice — rubber-hose punish feel, no keyblades / KH branding.
PERFECT_DODGE_COUNTER_ENABLED = True
# Seconds the rewarded counter window stays open after the perfect-dodge beat.
PERFECT_DODGE_COUNTER_WINDOW_SEC = 0.50
# Opener damage multiplier while the counter window is consumed.
PERFECT_DODGE_COUNTER_DAMAGE_MULT = 1.5
# Opener play-rate multiplier for a snappier counter punch.
PERFECT_DODGE_COUNTER_RATE_MULT = 1.2
# Buffer F/LMB pressed just as perfect dodge fires; flush on the melee tick.
PERFECT_DODGE_COUNTER_BUFFER = True


def perfectDodgeCounterOpenerDamage(baseDamage, mult=None):
    """Rewarded stretch-punch opener damage after a perfect dodge."""
    if mult is None:
        mult = PERFECT_DODGE_COUNTER_DAMAGE_MULT
    return max(1, int(round(float(baseDamage) * float(mult))))


def perfectDodgeCounterOpenerRate(baseRate, mult=None):
    """Snappier stretch-punch opener play rate after a perfect dodge."""
    if mult is None:
        mult = PERFECT_DODGE_COUNTER_RATE_MULT
    return float(baseRate) * float(mult)


def isPerfectDodgeCounterWindowOpen(armed, until, now):
    """True while a perfect-dodge counter→melee window is live."""
    return bool(armed) and float(now) < float(until)

# Dodge roll afterimage / smear trail (Shift/X i-frame roll juice).
# Warm cartoon smear ghosts drip behind the toon — not KH blue streaks.
DODGE_TRAIL_SPAWN_SEC = 0.045
DODGE_TRAIL_FADE_SEC = 0.2
DODGE_TRAIL_MAX_GHOSTS = 6
DODGE_TRAIL_COLOR = (1.0, 0.88, 0.45, 0.55)
DODGE_TRAIL_END_COLOR = (1.0, 0.95, 0.7, 0.0)
DODGE_TRAIL_HALF_W = 0.55
DODGE_TRAIL_HALF_H = 1.35
DODGE_TRAIL_STRETCH = (0.75, 1.55, 1.15)
DODGE_TRAIL_LIFT = 1.1
DODGE_TRAIL_SPARK_COUNT = 2
DODGE_TRAIL_SPARK_SIZE = 0.18
DODGE_TRAIL_SPARK_DRIFT = 0.55
DODGE_TRAIL_SPARK_COLOR = (1.0, 0.97, 0.75, 0.9)

# I-frame cream/ink pulse along the dodge trail (while dodge i-frames live).
# Short rubber-hose cream + ink fleck pops — not KH blue streaks.
DODGE_TRAIL_PULSE_SPAWN_SEC = 0.09
DODGE_TRAIL_PULSE_SEC = 0.18
DODGE_TRAIL_PULSE_CREAM_COUNT = 3
DODGE_TRAIL_PULSE_INK_COUNT = 2
DODGE_TRAIL_PULSE_SIZE = 0.16
DODGE_TRAIL_PULSE_DRIFT = 0.7
DODGE_TRAIL_PULSE_LIFT = 0.15
DODGE_TRAIL_PULSE_CREAM_COLOR = (1.0, 0.96, 0.62, 0.95)
DODGE_TRAIL_PULSE_CREAM_END = (1.0, 0.9, 0.45, 0.0)
DODGE_TRAIL_PULSE_INK_COLOR = (0.2, 0.06, 0.26, 0.9)
DODGE_TRAIL_PULSE_INK_END = (0.38, 0.1, 0.42, 0.0)

# I-frame pulse cream wash — soft aspect2d veil after first dodge i-frame
# cream/ink pulse (#66 / #166 / #228 / #272). SoftLock FOV / reticle cream wash
# grammar (#160 / #155). Deepened past #272 so invuln windows read juicier
# still: brighter peak + longer mid hold while dodge i-frames are live, plus
# a richer residual. Quieter under / at most equal to trail wash (#139);
# cream/pastel only. Distinct from hurt-stagger cream wash deepen (#247 /
# #263 / #287) — mid-roll invuln, not smack lockout — from dodge-cancel cream
# flash (#242 / #257 / #281), combo cream edge deepen (#237 / #267 / #291),
# and aim-nudge cream deepen (#254). Toggle
# DODGE_TRAIL_PULSE_CREAM_WASH_ENABLED = False drops wash (+ wash aftershock).
DODGE_TRAIL_PULSE_CREAM_WASH_ENABLED = True
DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC = 0.16  # after first pulse; mid-iframe
DODGE_TRAIL_PULSE_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
DODGE_TRAIL_PULSE_CREAM_WASH_PEAK = 0.10
DODGE_TRAIL_PULSE_CREAM_WASH_MID = 0.074
DODGE_TRAIL_PULSE_CREAM_WASH_IN_SEC = 0.05
DODGE_TRAIL_PULSE_CREAM_WASH_PULSE_SEC = 0.12
DODGE_TRAIL_PULSE_CREAM_WASH_HOLD_SEC = 0.12
DODGE_TRAIL_PULSE_CREAM_WASH_OUT_SEC = 0.42
DODGE_TRAIL_PULSE_CREAM_WASH_BIN = 27  # under trail wash (28) / soft-lock pulse

# I-frame pulse cream wash aftershock — residual cream flecks + soft halo
# after the wash pulse so the invuln settle still reads. Same grammar as
# HURT_STAGGER_CREAM_WASH_AFTERSHOCK_* / PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_*;
# deepened past #272 (more flecks + stronger halo), still quieter (rolls fire
# often). Cream/pastel only. Toggle
# DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ENABLED = True
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.08  # after wash starts
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.08)
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_COUNT = 5
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_SIZE = 0.015
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_DRIFT = 0.26
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_FALL = 0.20
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_SEC = 0.32
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.78)
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_BIN = 29  # over i-frame wash veil (27)
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.42
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_START = 0.24
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.25
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.26
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.12
DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)


def dodgeIFrameCreamWashPeakAtSec(delay=None, inSec=None):
    """Seconds from first i-frame pulse until cream wash reaches peak alpha."""
    if delay is None:
        delay = DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC
    if inSec is None:
        inSec = DODGE_TRAIL_PULSE_CREAM_WASH_IN_SEC
    return max(0.0, float(delay)) + max(0.0, float(inSec))

# Cream sparkle flecks along the dodge roll trail (while smear drips).
# Pastel cream glitter chips that compose with smear ghosts + i-frame cream/ink
# pulse — cream/pastel only (no ink). Toontown spiritual-sequel tone; no
# keyblades / no KH branding.
DODGE_TRAIL_CREAM_SPARKLE_ENABLED = True
DODGE_TRAIL_CREAM_SPARKLE_SPAWN_SEC = 0.055
DODGE_TRAIL_CREAM_SPARKLE_COUNT = 3
DODGE_TRAIL_CREAM_SPARKLE_STREAK_COUNT = 2
DODGE_TRAIL_CREAM_SPARKLE_SIZE = 0.11
DODGE_TRAIL_CREAM_SPARKLE_STREAK_SIZE = 0.075
DODGE_TRAIL_CREAM_SPARKLE_DRIFT = 0.6
DODGE_TRAIL_CREAM_SPARKLE_SEC = 0.2
DODGE_TRAIL_CREAM_SPARKLE_LIFT = -0.12
DODGE_TRAIL_CREAM_SPARKLE_COLOR = (1.0, 0.97, 0.78, 0.92)
DODGE_TRAIL_CREAM_SPARKLE_END = (1.0, 0.93, 0.58, 0.0)
DODGE_TRAIL_CREAM_SPARKLE_STREAK_COLOR = (1.0, 0.98, 0.85, 0.88)
DODGE_TRAIL_CREAM_SPARKLE_STREAK_END = (1.0, 0.9, 0.5, 0.0)

# Delayed cream aftershock after dodge-roll cream sparkle flecks (#101).
# Same residual grammar as FINISHER_CREAM_AFTERSHOCK_* /
# COMBO_COUNTER_CREAM_AFTERSHOCK_* — softer cream flecks + soft halo that
# settle after each trail sparkle drip. Cream/pastel only (no ink).
DODGE_TRAIL_CREAM_AFTERSHOCK_ENABLED = True
DODGE_TRAIL_CREAM_AFTERSHOCK_DELAY_SEC = 0.16
DODGE_TRAIL_CREAM_AFTERSHOCK_COUNT = 2
DODGE_TRAIL_CREAM_AFTERSHOCK_STREAK_COUNT = 1
DODGE_TRAIL_CREAM_AFTERSHOCK_SIZE = 0.09
DODGE_TRAIL_CREAM_AFTERSHOCK_STREAK_SIZE = 0.065
DODGE_TRAIL_CREAM_AFTERSHOCK_DRIFT = 0.5
DODGE_TRAIL_CREAM_AFTERSHOCK_SEC = 0.34
DODGE_TRAIL_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.86)
DODGE_TRAIL_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
DODGE_TRAIL_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.82)
DODGE_TRAIL_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_ENABLED = True
DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_HALF = 0.38
DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_START = 0.32
DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_PEAK = 1.45
DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_SEC = 0.28
DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.22
DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)

# Dodge-roll cream wash pulse — soft aspect2d veil after cream aftershock
# (#126). Perfect-dodge / melee-hit cream wash grammar. Quieter than
# perfect-dodge wash (rolls fire more often); cream/pastel only. Toggle
# DODGE_TRAIL_CREAM_WASH_ENABLED = False drops wash only.
DODGE_TRAIL_CREAM_WASH_ENABLED = True
DODGE_TRAIL_CREAM_WASH_DELAY_SEC = 0.34  # after start; after aftershock (0.16)
DODGE_TRAIL_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
DODGE_TRAIL_CREAM_WASH_PEAK = 0.10
DODGE_TRAIL_CREAM_WASH_MID = 0.06
DODGE_TRAIL_CREAM_WASH_IN_SEC = 0.05
DODGE_TRAIL_CREAM_WASH_PULSE_SEC = 0.09
DODGE_TRAIL_CREAM_WASH_HOLD_SEC = 0.06
DODGE_TRAIL_CREAM_WASH_OUT_SEC = 0.34
DODGE_TRAIL_CREAM_WASH_BIN = 28  # soft veil under soft-lock pulse (25+) / HUD

# Perfect dodge — Shift/X i-frames eat a CorruptToon telegraph (or near-miss).
# Warm cream star pop + ink flecks; not KH blue / keyblade glitter.
PERFECT_DODGE_STAR_COUNT = 5
PERFECT_DODGE_STAR_SIZE = 0.28
PERFECT_DODGE_STAR_DRIFT = 1.15
PERFECT_DODGE_STAR_SEC = 0.28
PERFECT_DODGE_STAR_COLOR = (1.0, 0.95, 0.55, 0.95)
PERFECT_DODGE_STAR_END_COLOR = (1.0, 0.88, 0.4, 0.0)
PERFECT_DODGE_FLECK_COUNT = 6
PERFECT_DODGE_FLECK_SIZE = 0.12
PERFECT_DODGE_FLECK_DRIFT = 1.35
PERFECT_DODGE_FLECK_SEC = 0.32
PERFECT_DODGE_FLECK_COLOR = (0.22, 0.06, 0.28, 0.9)
PERFECT_DODGE_FLECK_END_COLOR = (0.4, 0.12, 0.45, 0.0)
PERFECT_DODGE_LIFT = 1.35
PERFECT_DODGE_FLASH_ALPHA = 0.32

# Cream star aftershock — residual warm stars after the perfect-dodge pop
# settles (DodgePerfectFx). Softer/later than the initial cream star + ink
# fleck burst; Toontown spiritual-sequel tone only, no keyblades / KH.
PERFECT_DODGE_CREAM_AFTERSHOCK_ENABLED = True
PERFECT_DODGE_CREAM_AFTERSHOCK_DELAY_SEC = 0.22
PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_COUNT = 4
PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_SIZE = 0.22
PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_DRIFT = 0.85
PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_SEC = 0.42
PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_COLOR = (1.0, 0.96, 0.72, 0.88)
PERFECT_DODGE_CREAM_AFTERSHOCK_STAR_END = (1.0, 0.92, 0.55, 0.0)
PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_ENABLED = True
PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_HALF = 0.55
PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_START = 0.35
PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_PEAK = 1.7
PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_SEC = 0.36
PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.28
PERFECT_DODGE_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)

# Perfect-dodge cream wash pulse — soft aspect2d veil after cream aftershock
# (#89). Entry / purity cream wash grammar (CorruptDeathCreamWashFx family).
# Quieter than street purity-complete; cream/pastel only. Toggle
# PERFECT_DODGE_CREAM_WASH_ENABLED = False drops wash (+ wash aftershock).
PERFECT_DODGE_CREAM_WASH_ENABLED = True
PERFECT_DODGE_CREAM_WASH_DELAY_SEC = 0.40  # after play; after aftershock (0.22)
PERFECT_DODGE_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
PERFECT_DODGE_CREAM_WASH_PEAK = 0.12
PERFECT_DODGE_CREAM_WASH_MID = 0.07
PERFECT_DODGE_CREAM_WASH_IN_SEC = 0.06
PERFECT_DODGE_CREAM_WASH_PULSE_SEC = 0.10
PERFECT_DODGE_CREAM_WASH_HOLD_SEC = 0.08
PERFECT_DODGE_CREAM_WASH_OUT_SEC = 0.40
PERFECT_DODGE_CREAM_WASH_BIN = 28  # soft veil under soft-lock pulse (25+) / HUD

# Perfect-dodge cream wash aftershock — residual cream flecks + soft halo
# after the wash pulse (#130). Same grammar as ENTRY_CREAM_WASH_AFTERSHOCK_*
# (#132) / STREET_WASH_AFTERSHOCK_* (#159); quieter than world-space star
# aftershock (#89). Cream/pastel only. Toggle
# PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_ENABLED = True
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.22  # after wash starts
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.08)
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_COUNT = 5
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_SIZE = 0.014
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_DRIFT = 0.26
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_FALL = 0.20
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_SEC = 0.32
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.76)
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_BIN = 30  # over wash veil (28)
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.46
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_START = 0.24
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.12
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.26
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.11
PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Squash / stretch pulses (scale xyz multipliers over short windows).
# Read as exaggerated rubber-hose hit frames, not realistic physics.
HOSE_SQUASH = (
    # (sx, sy, sz, duration)
    (1.45, 1.45, 0.5, 0.09),
    (0.55, 0.55, 1.7, 0.11),
    (1.55, 1.55, 0.45, 0.14),
)
HOSE_STRETCH_RECOVER = 0.14

# Impact juice on connect (attacker + corrupt/demo hit-react).
# Flat squash → tall recover stretch → settle. Heavier on the finisher.
HIT_IMPACT_SQUASH = (
    # (sx, sy, sz, squashSec)
    (1.55, 1.55, 0.48, 0.05),
    (1.7, 1.7, 0.4, 0.055),
    (1.9, 1.9, 0.32, 0.07),
)
HIT_IMPACT_STRETCH = (
    # (sx, sy, sz, stretchSec)
    (0.72, 0.72, 1.38, 0.08),
    (0.62, 0.62, 1.5, 0.09),
    (0.5, 0.5, 1.7, 0.12),
)
HIT_IMPACT_SETTLE_SEC = 0.08

# Hit-connect cream/ink fleck sparkles (world-space CardMaker burst).
# Layers with HIT_IMPACT squash — short rubber-hose cream sparks + ink flecks.
# Toontown spiritual-sequel tone only — no keyblades / no KH branding.
HIT_SPARK_ENABLED = True
HIT_SPARK_LIFT = 1.2
# Per-hit intensity: cream/ink counts and drift scale slightly up the string.
HIT_SPARK_CREAM_COUNT = (3, 4, 5)
HIT_SPARK_INK_COUNT = (3, 4, 5)
HIT_SPARK_STREAK_COUNT = (2, 3, 4)
HIT_SPARK_SIZE = 0.13
HIT_SPARK_STREAK_SIZE = 0.2
HIT_SPARK_DRIFT = (0.75, 0.9, 1.1)
HIT_SPARK_LIFT_BURST = 0.35
HIT_SPARK_SEC = 0.2
HIT_SPARK_CREAM_COLOR = (1.0, 0.96, 0.62, 0.95)
HIT_SPARK_CREAM_END = (1.0, 0.9, 0.45, 0.0)
HIT_SPARK_INK_COLOR = (0.2, 0.06, 0.26, 0.9)
HIT_SPARK_INK_END = (0.38, 0.1, 0.42, 0.0)
HIT_SPARK_STREAK_COLOR = (1.0, 0.97, 0.78, 0.92)
HIT_SPARK_STREAK_END = (1.0, 0.92, 0.55, 0.0)

# Cream spark aftershock — residual warm cream sparks after melee hit flecks
# settle (HitSparkFx). Softer/later than the initial cream/ink fleck burst;
# cream/pastel only (no ink), Toontown spiritual-sequel tone — no keyblades / KH.
HIT_SPARK_CREAM_AFTERSHOCK_ENABLED = True
HIT_SPARK_CREAM_AFTERSHOCK_DELAY_SEC = 0.18
# Per-hit cream spark counts (index like HIT_SPARK_CREAM_COUNT).
HIT_SPARK_CREAM_AFTERSHOCK_COUNT = (3, 4, 5)
HIT_SPARK_CREAM_AFTERSHOCK_STREAK_COUNT = (1, 2, 2)
HIT_SPARK_CREAM_AFTERSHOCK_SIZE = 0.11
HIT_SPARK_CREAM_AFTERSHOCK_STREAK_SIZE = 0.16
HIT_SPARK_CREAM_AFTERSHOCK_DRIFT = 0.7
HIT_SPARK_CREAM_AFTERSHOCK_SEC = 0.38
HIT_SPARK_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.88)
HIT_SPARK_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
HIT_SPARK_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.85)
HIT_SPARK_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
HIT_SPARK_CREAM_AFTERSHOCK_HALO_ENABLED = True
HIT_SPARK_CREAM_AFTERSHOCK_HALO_HALF = 0.48
HIT_SPARK_CREAM_AFTERSHOCK_HALO_START = 0.3
HIT_SPARK_CREAM_AFTERSHOCK_HALO_PEAK = 1.55
HIT_SPARK_CREAM_AFTERSHOCK_HALO_SEC = 0.32
HIT_SPARK_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.26
HIT_SPARK_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)

# Hit-connect cream wash pulse — soft aspect2d veil after cream spark aftershock
# (#96). Perfect-dodge / entry / purity cream wash grammar. Quieter than
# perfect-dodge wash (hits fire more often); cream/pastel only. Toggle
# HIT_SPARK_CREAM_WASH_ENABLED = False drops wash (+ wash aftershock).
HIT_SPARK_CREAM_WASH_ENABLED = True
HIT_SPARK_CREAM_WASH_DELAY_SEC = 0.36  # after play; after aftershock (0.18)
HIT_SPARK_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
HIT_SPARK_CREAM_WASH_PEAK = 0.10
HIT_SPARK_CREAM_WASH_MID = 0.06
HIT_SPARK_CREAM_WASH_IN_SEC = 0.05
HIT_SPARK_CREAM_WASH_PULSE_SEC = 0.09
HIT_SPARK_CREAM_WASH_HOLD_SEC = 0.06
HIT_SPARK_CREAM_WASH_OUT_SEC = 0.34
HIT_SPARK_CREAM_WASH_BIN = 28  # soft veil under soft-lock pulse (25+) / HUD

# Hit-connect cream wash aftershock — residual cream flecks + soft halo after
# the wash pulse (#134). Same grammar as PERFECT_DODGE_CREAM_WASH_AFTERSHOCK_*
# (#171) / ENTRY_CREAM_WASH_AFTERSHOCK_* (#132); quieter than perfect-dodge
# wash aftershock and world-space spark aftershock (#96) — hits fire more
# often. Cream/pastel only. Toggle
# HIT_SPARK_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
HIT_SPARK_CREAM_WASH_AFTERSHOCK_ENABLED = True
HIT_SPARK_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.22  # after wash starts
HIT_SPARK_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, -0.08)
HIT_SPARK_CREAM_WASH_AFTERSHOCK_COUNT = 4
HIT_SPARK_CREAM_WASH_AFTERSHOCK_SIZE = 0.012
HIT_SPARK_CREAM_WASH_AFTERSHOCK_DRIFT = 0.22
HIT_SPARK_CREAM_WASH_AFTERSHOCK_FALL = 0.18
HIT_SPARK_CREAM_WASH_AFTERSHOCK_SEC = 0.28
HIT_SPARK_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.97, 0.78, 0.70)
HIT_SPARK_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.93, 0.58, 0.0)
HIT_SPARK_CREAM_WASH_AFTERSHOCK_BIN = 30  # over wash veil (28)
HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.40
HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_START = 0.22
HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.05
HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.24
HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.09
HIT_SPARK_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.97, 0.82, 1.0)

# Combo-finisher slam — bigger rubber-hose than HIT_IMPACT row 2 so the last
# stretch-punch reads as a readable slam (flat pancake → tall spring → settle).
FINISHER_SLAM_SQUASH = (2.2, 2.2, 0.2, 0.085)
FINISHER_SLAM_STRETCH = (0.38, 0.38, 2.05, 0.15)
FINISHER_SLAM_SETTLE_SEC = 0.11

# Finisher slam dust / ink puff at feet (world-space CardMaker burst).
# Warm tan dust ring + dust/ink flecks — cartoon street thud, not KH glitter.
FINISHER_SLAM_DUST_ENABLED = True
FINISHER_SLAM_DUST_LIFT = 0.06
FINISHER_SLAM_DUST_RING_HALF = 0.55
FINISHER_SLAM_DUST_RING_PEAK = 2.55
FINISHER_SLAM_DUST_RING_SEC = 0.28
FINISHER_SLAM_DUST_RING_COLOR = (0.78, 0.62, 0.4, 0.72)
FINISHER_SLAM_DUST_RING_END_COLOR = (0.85, 0.7, 0.48, 0.0)
FINISHER_SLAM_DUST_PUFF_COUNT = 7
FINISHER_SLAM_DUST_PUFF_SIZE = 0.2
FINISHER_SLAM_DUST_PUFF_DRIFT = 1.4
FINISHER_SLAM_DUST_PUFF_LIFT = 0.55
FINISHER_SLAM_DUST_PUFF_SEC = 0.3
FINISHER_SLAM_DUST_PUFF_COLOR = (0.82, 0.66, 0.42, 0.88)
FINISHER_SLAM_DUST_PUFF_END_COLOR = (0.9, 0.75, 0.5, 0.0)
FINISHER_SLAM_DUST_INK_COUNT = 4
FINISHER_SLAM_DUST_INK_SIZE = 0.14
FINISHER_SLAM_DUST_INK_DRIFT = 1.15
FINISHER_SLAM_DUST_INK_LIFT = 0.4
FINISHER_SLAM_DUST_INK_SEC = 0.28
FINISHER_SLAM_DUST_INK_COLOR = (0.2, 0.06, 0.26, 0.9)
FINISHER_SLAM_DUST_INK_END_COLOR = (0.38, 0.1, 0.42, 0.0)

# Finisher cream slam flash — warm aspect2d cream punch + ring on 3rd-hit connect.
# Replaces the generic white HIT_FLASH on finishers so the slam reads creamier.
# Plays during HitStopFx freeze; FOV punch still deferred until resume (#68/#74).
FINISHER_CREAM_SLAM_FLASH_ENABLED = True
FINISHER_CREAM_SLAM_FLASH_COLOR = (1.0, 0.96, 0.78, 1.0)
FINISHER_CREAM_SLAM_FLASH_PEAK = 0.48
FINISHER_CREAM_SLAM_FLASH_IN_SEC = 0.035
FINISHER_CREAM_SLAM_FLASH_HOLD_SEC = 0.045
FINISHER_CREAM_SLAM_FLASH_OUT_SEC = 0.16
FINISHER_CREAM_SLAM_FLASH_BIN = 61
FINISHER_CREAM_SLAM_RING_ENABLED = True
FINISHER_CREAM_SLAM_RING_HALF = 0.55
FINISHER_CREAM_SLAM_RING_START = 0.35
FINISHER_CREAM_SLAM_RING_PEAK = 2.4
FINISHER_CREAM_SLAM_RING_SEC = 0.22
FINISHER_CREAM_SLAM_RING_PEAK_ALPHA = 0.55
FINISHER_CREAM_SLAM_RING_Z = 0.0

# Finisher cream sparkle hang — residual aspect2d veil + flecks after slam flash.
# Same delayed cream aftershock grammar as HIT_SPARK_CREAM_AFTERSHOCK_*; soft hang
# under the flash bin so the slam settles sunny without a second punch.
FINISHER_CREAM_SPARKLE_HANG_ENABLED = True
FINISHER_CREAM_SPARKLE_HANG_DELAY_SEC = 0.24
FINISHER_CREAM_SPARKLE_HANG_BIN = 59
FINISHER_CREAM_SPARKLE_HANG_ORIGIN_Z = 0.04
FINISHER_CREAM_SPARKLE_HANG_COUNT = 6
FINISHER_CREAM_SPARKLE_HANG_STREAK_COUNT = 3
FINISHER_CREAM_SPARKLE_HANG_SIZE = 0.016
FINISHER_CREAM_SPARKLE_HANG_STREAK_SIZE = 0.012
FINISHER_CREAM_SPARKLE_HANG_DRIFT = 0.42
FINISHER_CREAM_SPARKLE_HANG_SETTLE = 0.28
FINISHER_CREAM_SPARKLE_HANG_SEC = 0.4
FINISHER_CREAM_SPARKLE_HANG_COLOR = (1.0, 0.96, 0.72, 0.9)
FINISHER_CREAM_SPARKLE_HANG_END = (1.0, 0.92, 0.55, 0.0)
FINISHER_CREAM_SPARKLE_HANG_STREAK_COLOR = (1.0, 0.98, 0.82, 0.88)
FINISHER_CREAM_SPARKLE_HANG_STREAK_END = (1.0, 0.9, 0.5, 0.0)
FINISHER_CREAM_SPARKLE_HANG_VEIL_ENABLED = True
FINISHER_CREAM_SPARKLE_HANG_VEIL_COLOR = (1.0, 0.97, 0.82, 1.0)
FINISHER_CREAM_SPARKLE_HANG_VEIL_PEAK = 0.14
FINISHER_CREAM_SPARKLE_HANG_VEIL_IN_SEC = 0.07
FINISHER_CREAM_SPARKLE_HANG_VEIL_HOLD_SEC = 0.22
FINISHER_CREAM_SPARKLE_HANG_VEIL_OUT_SEC = 0.36

# Delayed cream aftershock after finisher cream sparkle hang (#107).
# Same residual grammar as LAUNCH_HANG_CREAM_AFTERSHOCK_* /
# COMBO_COUNTER_CREAM_AFTERSHOCK_* — softer cream flecks + soft halo that
# settle after the hang veil/flecks. Delay is from hang fire (not flash).
FINISHER_CREAM_AFTERSHOCK_ENABLED = True
FINISHER_CREAM_AFTERSHOCK_DELAY_SEC = 0.18
FINISHER_CREAM_AFTERSHOCK_COUNT = 3
FINISHER_CREAM_AFTERSHOCK_STREAK_COUNT = 2
FINISHER_CREAM_AFTERSHOCK_SIZE = 0.012
FINISHER_CREAM_AFTERSHOCK_STREAK_SIZE = 0.009
FINISHER_CREAM_AFTERSHOCK_DRIFT = 0.32
FINISHER_CREAM_AFTERSHOCK_SETTLE = 0.22
FINISHER_CREAM_AFTERSHOCK_SEC = 0.34
FINISHER_CREAM_AFTERSHOCK_COLOR = (1.0, 0.96, 0.72, 0.86)
FINISHER_CREAM_AFTERSHOCK_END = (1.0, 0.92, 0.55, 0.0)
FINISHER_CREAM_AFTERSHOCK_STREAK_COLOR = (1.0, 0.98, 0.82, 0.82)
FINISHER_CREAM_AFTERSHOCK_STREAK_END = (1.0, 0.9, 0.5, 0.0)
FINISHER_CREAM_AFTERSHOCK_HALO_ENABLED = True
FINISHER_CREAM_AFTERSHOCK_HALO_HALF = 0.38
FINISHER_CREAM_AFTERSHOCK_HALO_START = 0.4
FINISHER_CREAM_AFTERSHOCK_HALO_PEAK = 1.45
FINISHER_CREAM_AFTERSHOCK_HALO_SEC = 0.28
FINISHER_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA = 0.2
FINISHER_CREAM_AFTERSHOCK_HALO_COLOR = (1.0, 0.96, 0.78, 1.0)
FINISHER_CREAM_AFTERSHOCK_BIN = 58

# Finisher cream wash pulse — soft aspect2d veil after cream aftershock
# (#122). Perfect-dodge / melee-hit / dodge-trail cream wash grammar.
# After hang (0.24) + aftershock (0.18) = 0.42; wash at 0.60. Cream/pastel
# only. Toggle FINISHER_CREAM_WASH_ENABLED = False drops wash only.
FINISHER_CREAM_WASH_ENABLED = True
FINISHER_CREAM_WASH_DELAY_SEC = 0.60  # after play; after aftershock (0.42)
FINISHER_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)  # sunny cream
FINISHER_CREAM_WASH_PEAK = 0.12
FINISHER_CREAM_WASH_MID = 0.07
FINISHER_CREAM_WASH_IN_SEC = 0.06
FINISHER_CREAM_WASH_PULSE_SEC = 0.10
FINISHER_CREAM_WASH_HOLD_SEC = 0.08
FINISHER_CREAM_WASH_OUT_SEC = 0.40
FINISHER_CREAM_WASH_BIN = 28  # soft veil under soft-lock pulse (25+) / HUD

# Player hit-react when a CorruptToon lands a smack (scale juice + tiny hitstop).
PLAYER_HIT_REACT_SQUASH = (1.75, 1.75, 0.38, 0.06)
PLAYER_HIT_REACT_STRETCH = (0.68, 0.68, 1.42, 0.1)
PLAYER_HIT_REACT_SETTLE_SEC = 0.1
PLAYER_HIT_REACT_HITSTOP_SEC = 0.04

# Melee hit sphere relative to the toon (forward reach).
HIT_FORWARD = 3.2
HIT_RADIUS = 2.4
HIT_HEIGHT = 2.0

# Demo hostiles spawned by ~hackslash
DEMO_HOSTILE_COUNT = 3
DEMO_HOSTILE_SPACING = 6.0
DEMO_HOSTILE_HP = 40
DEMO_HOSTILE_NAME = 'Corrupt Dummy'

# On-screen hint while demo mode is active
DEMO_HINT = (
    'Stretch punches: F/LMB  |  combo cream edge deepen  |  '
    'Shift/X dodge i-frame cream wash deepen++  |  '
    'dodge→F cream flash deepen++  |  perfect dodge→F counter  |  '
    'Snare string→F counter  |  juggle→F slam  |  hurt cream wash deepen++→F/Shift  |  '
    'Tab/` soft-lock cycle cream  |  hit soft-lock aim cream deepen+  |  ~melee'
)
