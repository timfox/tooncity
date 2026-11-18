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

# Combo: 3 stretch punches, cartoon cadence with overshoot on the finisher.
COMBO_LENGTH = 3
COMBO_WINDOW_SEC = 0.55
COMBO_RECOVERY_SEC = 0.35

# Per-hit anim names (existing toon anims) and play rates for rubber-hose snap.
# Rates > 1 read as snappy cartoon timing; finisher slows slightly for weight.
COMBO_ANIMS = ('swing', 'throw', 'sound')
COMBO_PLAY_RATES = (1.85, 2.1, 1.25)
COMBO_DAMAGE = (8, 12, 28)

# Hitstop (global brief pause) on connect — longer on finisher.
HITSTOP_SEC = (0.045, 0.055, 0.11)

# Camera FOV punch on finisher (degrees added, then restored).
# Slightly hotter than mid-combo so the stretch-punch slam reads.
FINISHER_FOV_PUNCH = 16.0
FINISHER_FOV_IN_SEC = 0.05
FINISHER_FOV_OUT_SEC = 0.2

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

# Brief aspect2d white flash on connect (beyond hitstop).
HIT_FLASH_PEAK_ALPHA = 0.38
HIT_FLASH_IN_SEC = 0.03
HIT_FLASH_OUT_SEC = 0.10

# On-screen combo counter (ticks on hackslash-hit; fades after break).
# Parked lower-left so reclaim banners / soft-lock hints stay readable up top.
COMBO_COUNTER_POS = (-0.95, 0.0, -0.42)
COMBO_COUNTER_BASE_SCALE = 0.11
COMBO_COUNTER_POP_SCALE = 0.16
COMBO_COUNTER_POP_SEC = 0.08
COMBO_COUNTER_SETTLE_SEC = 0.12
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

# Mid/finisher launcher juice (upward juggle feel on the target).
LAUNCH_HIT_INDEX = 1  # 2nd hit starts the juggle; finisher lifts more
LAUNCH_HEIGHT = (0.0, 1.85, 3.1)
LAUNCH_UP_SEC = (0.0, 0.12, 0.16)
LAUNCH_HANG_SEC = (0.0, 0.06, 0.14)
LAUNCH_DOWN_SEC = (0.0, 0.16, 0.22)
# Local toon hop cue on finisher so the juggle reads as a shared air beat.
FINISHER_SELF_HOP = 1.15
FINISHER_SELF_UP_SEC = 0.11
FINISHER_SELF_DOWN_SEC = 0.2

# I-frame / dodge cue after CorruptToon smacks the local toon.
IFRAME_SEC = 0.55
IFRAME_FLASH_ALPHA = 0.55

# Player-initiated dodge roll (Shift; Space stays jump).
DODGE_KEY = 'shift'
DODGE_KEY_ALT = 'x'
DODGE_DURATION_SEC = 0.28
DODGE_IFRAME_SEC = 0.42
DODGE_DISTANCE = 6.5
DODGE_COOLDOWN_SEC = 0.65
DODGE_SQUASH = (0.55, 0.55, 1.45, 0.12)

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

# Combo-finisher slam — bigger rubber-hose than HIT_IMPACT row 2 so the last
# stretch-punch reads as a readable slam (flat pancake → tall spring → settle).
FINISHER_SLAM_SQUASH = (2.2, 2.2, 0.2, 0.085)
FINISHER_SLAM_STRETCH = (0.38, 0.38, 2.05, 0.15)
FINISHER_SLAM_SETTLE_SEC = 0.11

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
    'Stretch punches: F/LMB  |  Shift/X dodge  |  soft-lock cam  |  ~melee'
)
