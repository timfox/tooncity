"""Corrupt toons and neighborhood pollution (Toontown spiritual sequel).

CorruptToons prefer ink-tinted Toon Actor / DNA silhouettes (card fallback),
chase, and telegraph attacks: Ink Smudge purple melee wind-up, Sludge Brute
green spit telegraph + traveling ink blob on hit, Balloon Snare amber
string-lash + vine zip, Gunk Gagster teal gag-lob puddle trap. Between
telegraphs, IdleInkDripFx plays sparse ambient rubber-hose ink
drips (archetype-tinted pollution presence) layered with
IdleCreamDripContrastFx (soft cream / pastel drips — contrast to idle ink)
plus IdleCreamDripSparkleFx (sunny cream / pastel sparkle flecks along the
cream drip path — silhouette rim sparkle grammar) plus
IdleCreamWashPulseFx (soft cream wash pulse + delayed cream aftershock —
contrast against ink idle drips; death cream wash aftershock #172 grammar)
plus
CorruptSilhouetteCreamRimFx (sunny cream / pastel rim flecks along the
ink silhouette edge) plus CorruptSilhouetteCreamSparkleFx (sunny cream /
pastel sparkle flecks rising from the silhouette cream rim) plus
CorruptSilhouetteCreamWashFx (soft cream wash pulse + delayed cream aftershock —
contrast against the ink silhouette; idle cream wash aftershock #177 grammar).
Telegraphs play CorruptTelegraphInkFx (short
rubber-hose ink drip / splat pop) layered with CorruptTelegraphCreamWarnFx
(sunny cream / pastel warn flecks + delayed cream aftershock — contrast to
ink) plus CorruptTelegraphCreamSparkleFx (sunny cream / pastel sparkle flecks
rising from the telegraph cream warn spray — silhouette cream sparkle
grammar) plus CorruptTelegraphCreamWashFx (soft cream wash pulse — contrast
against ink telegraph; silhouette / idle cream-wash grammar) and pause idle
drips / sparkles / wash / rim flecks for the wind-up. Ink Smudge wind-ups also flash
SmudgeInkTelegraphFx (purple rubber-hose ink-fist pop). Ink Smudge hits and
deaths also flash SmudgeInkSplashFx (cheap purple rubber-hose ink splash for
swarm readability; composes with telegraph / death / idle ink looks); Smudge
hits also fire SmudgeHitCreamSplashFx (brief cream splash + delayed cream
aftershock — sunny cream/pastel juice against purple ink; Brute spit /
Gunk puddle / Snare counter cream-splash grammar) and pulse
SmudgeHitCreamWashFx (soft cream wash — cream/pastel contrast against
purple ink; overlord-hit / telegraph / silhouette / death cream-wash
grammar). Sludge
Brute wind-ups also flash BruteSpitTelegraphFx (green rubber-hose spit-gob
pop). Sludge Brute spit land / splash also fires BruteSpitCreamSplashFx
(brief cream splash + delayed cream aftershock — sunny cream/pastel juice
on the spit impact; telegraph cream warn aftershock grammar / Gunk puddle
cream splash #218). Sludge Brute hits and deaths also flash
BruteSludgeSplashFx (cheap green rubber-hose sludge splash; composes with
spit / death / idle looks).
Balloon Snare wind-ups also flash BalloonSnareTelegraphFx (amber
rubber-hose string-lash pop) and, after the string reads, arm a short
string-snap counter window into melee (SNARE_STRING_COUNTER_*; synchs
with hackslash perfect-dodge counter; mid-telegraph melee interrupts
the wind-up). Successful string-snap punish/counter hits also flash
SnareStringCounterCreamSplashFx (brief cream splash + delayed cream
aftershock — sunny cream/pastel juice on the rewarded window; telegraph
cream warn aftershock grammar). Balloon Snare hits and deaths also flash
SnareStringSnapSplashFx (cheap amber rubber-hose string-snap splash;
composes with string / death / idle looks). Gunk Gagster wind-ups also flash
GagsterPuddleTelegraphFx (teal bounce-pie charge + cream/ink ground puddle
warn at the lob landing). Gunk Gagster puddle land / splash also fires
GagsterPuddleCreamSplashFx (brief cream splash + delayed cream aftershock —
sunny cream/pastel juice on the trap impact; telegraph cream warn aftershock
grammar / Snare counter cream splash #214). Ink Overlord phase telegraphs also flash
OverlordTelegraphCrownFx (rubber-hose ink crown / silhouette) plus
OverlordPhaseInkRainFx (ink rain / ink fall shower) plus
OverlordTelegraphPunchFx (ground danger-ring warn + impact punch bloom;
phase-timed AV squash/stretch hold for fair punish windows). Ink Overlord
hits and deaths also flash OverlordMagentaInkSplashFx (cheap magenta/crimson
rubber-hose ink splash; phase-retinted; composes with crown / rain / death /
idle looks — not street Smudge purple); Overlord hits also pulse
OverlordHitCreamWashFx (soft cream wash — cream/pastel contrast against
magenta ink; telegraph / silhouette / death cream-wash grammar). Defeat plays CorruptDeathPopFx
(rubber-hose ink splat / balloon pop) layered with
CorruptDeathCreamFleckFx (sunny cream / pastel flecks — purity chips,
not ink), CorruptDeathCreamSparkleFx (sunny cream / pastel sparkle flecks
rising from the death cream fleck burst — telegraph / silhouette cream
sparkle grammar), and CorruptDeathCreamWashFx (soft cream wash pulse +
delayed cream aftershock after the fleck / sparkle path — entry /
purity-complete aftershock grammar). Clearing them lowers
per-zone pollution via PollutionManager;
hitting 0.0 unlocks purity restore (reclaim / campaign).

Pollution fog / ink haze / color grade / street-prop tint are hood-biased
(Loopy purple ink, Punchline sludge green, Silly hot magenta) via
CorruptionGlobals bias tables and PollutionPropTint on street geom. Fog
density and haze opacity ramp with zone corruption (lerp as reclaim rises or
clears). On street purity complete, PollutionFogCreamDissolveFx cream-tints
the clearing fog/haze and layers a soft cream veil + rising flecks (matches
density clear ramp + StreetSparkle chip patterns), and
PollutionHoodTintCreamFadeFx cream-fades hood prop tint toward sunny cream
instead of snapping clear (HOOD_TINT_CREAM_FADE_*; same clear window). Street
music crossfades to a darker encounter bed while polluted and back to the
hood bed on purity restore (PollutionStreetAudio; pairs with reclaim
cheer/sting), plus a short rubber-hose birds ambient bed fade-in. Bail out of
an unfinished reclaim and PollutionManagerAI marks the street contested —
residual ink slowly re-creeps (POLLUTION_RECREEP_*); finished reclaim
purity-locks the street so secured / pure streets stay clean.
"""
