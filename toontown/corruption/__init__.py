"""Corrupt toons and neighborhood pollution (Toontown spiritual sequel).

CorruptToons prefer ink-tinted Toon Actor / DNA silhouettes (card fallback),
chase, and telegraph attacks: Ink Smudge purple melee wind-up, Sludge Brute
green spit telegraph + traveling ink blob on hit, Balloon Snare amber
string-lash + vine zip. Between telegraphs, IdleInkDripFx plays sparse
ambient rubber-hose ink drips (archetype-tinted pollution presence).
Telegraphs play CorruptTelegraphInkFx (short rubber-hose ink drip / splat
pop) and pause idle drips for the wind-up. Ink Smudge wind-ups also flash
SmudgeInkTelegraphFx (purple rubber-hose ink-fist pop). Ink Smudge hits and
deaths also flash SmudgeInkSplashFx (cheap purple rubber-hose ink splash for
swarm readability; composes with telegraph / death / idle ink looks). Sludge
Brute wind-ups also flash BruteSpitTelegraphFx (green rubber-hose spit-gob
pop). Sludge Brute hits and deaths also flash BruteSludgeSplashFx (cheap
green rubber-hose sludge splash; composes with spit / death / idle looks).
Balloon Snare wind-ups also flash BalloonSnareTelegraphFx (amber
rubber-hose string-lash pop). Balloon Snare hits and deaths also flash
SnareStringSnapSplashFx (cheap amber rubber-hose string-snap splash;
composes with string / death / idle looks). Ink Overlord phase telegraphs also flash
OverlordTelegraphCrownFx (rubber-hose ink crown / silhouette) plus
OverlordPhaseInkRainFx (ink rain / ink fall shower). Defeat plays
CorruptDeathPopFx (rubber-hose ink splat / balloon pop). Clearing them lowers
per-zone pollution via PollutionManager; hitting 0.0 unlocks purity restore
(reclaim / campaign).

Pollution fog / ink haze / color grade / street-prop tint are hood-biased
(Loopy purple ink, Punchline sludge green, Silly hot magenta) via
CorruptionGlobals bias tables and PollutionPropTint on street geom. Fog
density and haze opacity ramp with zone corruption (lerp as reclaim rises or
clears). Street music crossfades to a darker encounter bed while polluted and
back to the hood bed on purity restore (PollutionStreetAudio; pairs with
reclaim cheer/sting), plus a short rubber-hose birds ambient bed fade-in.
"""
