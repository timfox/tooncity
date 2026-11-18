"""Corrupt toons and neighborhood pollution (KH x Toontown).

CorruptToons prefer ink-tinted Toon Actor / DNA silhouettes (card fallback),
chase, and telegraph attacks: Ink Smudge purple melee wind-up, Sludge Brute
green spit telegraph + traveling ink blob on hit. Clearing them lowers
per-zone pollution via PollutionManager; hitting 0.0 unlocks purity restore
(reclaim / campaign directors).

Pollution fog / color grade / street-prop tint are hood-biased (Loopy purple
ink, Punchline sludge green, Silly hot magenta) via CorruptionGlobals bias
tables and PollutionPropTint on street geom.
"""
