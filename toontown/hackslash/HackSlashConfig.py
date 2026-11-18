"""Tunables for the rubber-hose melee prototype."""

# Attack input. Classic Toontown uses Delete for pies and Ctrl for jump;
# F is free for "Fight" and stays out of the way of pie toss.
ATTACK_KEY = 'f'
ATTACK_KEY_ALT = 'mouse1'

# Soft-target cone (degrees half-angle) and range (Panda units / feet-ish).
TARGET_RANGE = 14.0
TARGET_HALF_ANGLE_DEG = 55.0
TARGET_LOCK_HOLD_SEC = 1.25

# Combo: 3 hits, KH-ish cadence with cartoon overshoot on the finisher.
COMBO_LENGTH = 3
COMBO_WINDOW_SEC = 0.55
COMBO_RECOVERY_SEC = 0.35

# Per-hit anim names (existing toon anims) and play rates for rubber-hose snap.
# Rates > 1 read as snappy cartoon timing; finisher slows slightly for weight.
COMBO_ANIMS = ('swing', 'throw', 'sound')
COMBO_PLAY_RATES = (1.85, 2.1, 1.35)
COMBO_DAMAGE = (8, 12, 22)

# Squash / stretch pulses (scale xyz multipliers over short windows).
# Read as exaggerated rubber-hose hit frames, not realistic physics.
HOSE_SQUASH = (
    # (sx, sy, sz, duration)
    (1.25, 1.25, 0.65, 0.08),
    (0.7, 0.7, 1.45, 0.1),
    (1.15, 1.15, 0.75, 0.12),
)
HOSE_STRETCH_RECOVER = 0.12

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
DEMO_HINT = 'Hack-Slash demo: press F (or LMB) to melee  |  ~hackslash to toggle'
