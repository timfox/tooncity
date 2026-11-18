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

# Hitstop / freeze on connect — pauses juice + anims so the impact silhouette
# sticks before launch / hop / FOV punch. Longer on finisher. Client juice only.
HITSTOP_ENABLED = True
HITSTOP_SEC = (0.05, 0.065, 0.12)
HITSTOP_FREEZE_ANIMS = True

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
# PERFECT_DODGE_CREAM_WASH_ENABLED = False drops wash only.
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
# HIT_SPARK_CREAM_WASH_ENABLED = False drops wash only.
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
    'Stretch punches: F/LMB  |  Shift/X dodge  |  soft-lock cam  |  ~melee'
)
