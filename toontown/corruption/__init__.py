"""Corrupt toons and neighborhood pollution (Toontown spiritual sequel).

CorruptToons prefer ink-tinted Toon Actor / DNA silhouettes (card fallback),
chase, and telegraph attacks: Ink Smudge purple melee wind-up, Sludge Brute
green spit telegraph + traveling ink blob on hit, Balloon Snare amber
string-lash + vine zip. Telegraphs play CorruptTelegraphInkFx (short
rubber-hose ink drip / splat pop). Defeat plays CorruptDeathPopFx
(rubber-hose ink splat / balloon pop). Clearing them lowers per-zone
pollution via PollutionManager; hitting 0.0 unlocks purity restore
(reclaim / campaign).

Pollution fog / ink haze / color grade / street-prop tint are hood-biased
(Loopy purple ink, Punchline sludge green, Silly hot magenta) via
CorruptionGlobals bias tables and PollutionPropTint on street geom. Fog
density and haze opacity ramp with zone corruption (lerp as reclaim rises or
clears). Street music crossfades to a darker encounter bed while polluted and
back to the hood bed on purity restore (PollutionStreetAudio; pairs with
reclaim cheer/sting).
"""
