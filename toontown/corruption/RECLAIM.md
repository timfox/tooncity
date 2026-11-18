# Corruption → reclaim (slice 3)

## Loop

1. `PollutionManager` holds per-zone pollution `0..1` (pure → polluted).
2. `~startreclaim` generates a `DistributedReclaimDirector` in the invoker zone,
   seeds partial pollution, and spawns escalating CorruptToon waves (size/HP grow).
3. Melee (`~hackslash 0`) soft-targets CorruptToons; `applyHackSlashHit` →
   `requestHackSlashHit` → AI `takeHackSlashDamage`.
4. Defeats lower pollution via `PollutionManagerAI.onCorruptToonDefeated`.
   HUD shows wave / corruption % / pack remaining; scene tint + fog react to pollution.
   Fog / color grade / street-prop tint are **hood-specific** (Loopy purple ink,
   Punchline sludge green-brown, Silly hot magenta) via `HOOD_POLLUTION_BIAS`
   and `PollutionPropTint` (geom colorScale — does not stomp reclaim render bloom).
5. At `0.0`, director announces reclaim complete and client plays a stronger purity
   restore moment (banner + bloom + sting/NPC cheer messenger hooks).

## Demo

Preferred street: Toontown Central Loopy Lane (`2200`).
Compare ambient corruption on Punchline (`2300`) and Silly (`2100`) with `~pollute`.

```
~startreclaim
~hackslash 0
# clear packs with F / LMB
# optional: ~spawncorrupt 2   or   ~stopreclaim
```

Manual pollution tools still work: `~pollute`, `~purify`, `~spawncorrupt`.

## Depth D2 enemy demo

```
~spawncorrupt 2
~hackslash 0
# CorruptToons prefer ink-tinted Toon Actor silhouettes (DNA clone of you
# when available), else improved card limbs. Chase + telegraph + splat stay.
# Melee (F / LMB) splat-defeats them; purity pop + pollution drop.
```
