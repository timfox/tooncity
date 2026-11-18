# Corruption → reclaim (slice 3)

## Discoverable play smoke (preferred)

Happy path needs **no magic words**: enter Loopy → Punchline → Silly, use on-screen
**F / Shift / C** (auto melee + auto packs via `toontown/campaign/PlayEntry.py`).

Full step checklist (Project store): `docs/loopy-to-silly-smoke.md`
(absolute: `/cursor/stores/bc-ca83d784-15c5-4fcc-9fbe-2cab276c6f17/docs/loopy-to-silly-smoke.md`).

Sections below remain **debug / magic-word** fallbacks.

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
   restore moment (banner + bloom + sting + FOV/camera punch + rays/sparks via
   `PurityBurstFx` + `ReclaimCheer` local Happy/wave + nearby nudge).

## Discoverable play (preferred)

Walk onto Loopy / Punchline / Silly: `PlayEntry` auto-arms melee and auto-starts
reclaim packs. Fight with **F**, dodge with **Shift**, campaign with **C**.
No `~spawncorrupt` required for the happy path.

## Demo (magic words still work)

Preferred street: Toontown Central Loopy Lane (`2200`).
Compare ambient corruption on Punchline (`2300`) and Silly (`2100`) with `~pollute`.

```
~startreclaim
~hackslash 0
# clear packs with F / LMB
# optional: ~spawncorrupt 2   or   ~stopreclaim
```

Manual pollution tools still work: `~pollute`, `~purify`, `~spawncorrupt`.

## Archetype spawn mix

- Loopy campaign / reclaim wave 1: Ink Smudge only (`bruteFraction`/`snareFraction` 0, wave starts at 2)
- Default reclaim waves 2+: ~⅓ Sludge Brutes + ~⅕ Balloon Snares
- Punchline campaign: Brutes + Balloon Snares from wave 1
- Silly finale: Overlord only (no Brute / Snare mix)

```
~spawncorrupt 2 0 0   # Ink Smudge
~spawncorrupt 1 0 1   # Sludge Brute
~spawncorrupt 1 0 2   # Balloon Snare
```

## Depth D2 enemy demo

```
~spawncorrupt 2
~hackslash 0
# CorruptToons prefer ink-tinted Toon Actor silhouettes (DNA clone of you
# when available), else improved card limbs. Chase AI unchanged; telegraph
# wind-up + impact flash/SFX punch so smacks read without a combat HUD.
# Melee (F / LMB) splat-defeats them; purity pop + pollution drop.
```

## Sludge Brute spit demo

```
~spawncorrupt 1 40 1
# or ~spawnbrute 1 40 1
~hackslash 0
# Brute: green squash telegraph + squirt SFX, then ink blob flies at you on hit.
# Compare ~spawncorrupt 1   (Ink Smudge keeps purple melee telegraph).
```

## Balloon Snare string-lash demo

```
~spawncorrupt 1 0 2
# or ~spawnsnare 1 0 2
~hackslash 0
# Snare: amber horizontal rubber stretch + vine zip SFX, string line snaps on hit.
# Fast fragile zip-flier — distinct from Smudge melee and Brute spit.
```

## Ink Overlord finale phases

Silly Street campaign (`~advancecampaign force` to skip ahead, then
`~startcampaign` on zone `2100`):

1. **Phase 1 — Rising**: magenta telegraph squash/stretch, larger Overlord scale,
   HUD shows `Overlord P1`.
2. Clear packs → purity beat → director restarts **Phase 2**.
3. **Phase 2 — Unleashed**: crimson telegraphs, hotter hit flash, FOV + fullscreen
   ink slam transition sting (`announceFinalePhaseTransition`).
4. Clear again → campaign victory.

