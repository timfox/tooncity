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
   Director marks the street `STREET_RECLAIMING` so incomplete-reclaim re-creep
   pauses while packs are live.
3. Melee (`~hackslash 0`) soft-targets CorruptToons; `applyHackSlashHit` →
   `requestHackSlashHit` → AI `takeHackSlashDamage`.
4. Defeats lower pollution via `PollutionManagerAI.onCorruptToonDefeated`.
   HUD shows wave / corruption % / pack remaining; scene tint + fog react to pollution.
   Fog / ink haze / color grade / street-prop tint are **hood-specific** (Loopy purple
   ink, Punchline sludge green-brown, Silly hot magenta) via `HOOD_POLLUTION_BIAS`
   and `PollutionPropTint` (geom colorScale — does not stomp reclaim render bloom).
   Density **ramps** with zone corruption: as packs thicken pollution, fog exp density
   + aspect2d ink haze + hood tint intensity lerp up; as purity reclaims, they clear
   (`POLLUTION_FOG_*` / `hoodFogExpDensity` / `hoodHazeAlpha` in PollutionManager).
   On full purity, fog **cream-dissolves** (`PollutionFogCreamDissolveFx` /
   `FOG_CREAM_DISSOLVE_*`): ink fog palette shifts sunny cream while density
   clears, plus a soft cream veil + rising flecks (StreetSparkle chip family).
   Hood street-prop tint **cream-fades** (`PollutionHoodTintCreamFadeFx` /
   `HOOD_TINT_CREAM_FADE_*`): geom colorScale lifts sunny cream/pastel over the
   same clear window instead of snapping clear (composes under fog dissolve).
   Street music crossfades via `PollutionStreetAudio`: polluted → darker
   `encntr_general_bg` bed; purity clear → bright hood bed + cheer/sting (#21)
   plus a short faded-in rubber-hose birds ambient return (`SZ_TC_bird*`).
5. At `0.0`, director announces reclaim complete and client plays a stronger purity
   restore moment (banner + bloom + sting + FOV/camera punch + rays/sparks via
   `PurityBurstFx` + fog cream dissolve + `ReclaimCheer` local Happy/wave +
   rubber-hose cheer pitch swell + nearby nudge). Mid-reclaim wave clears fire a
   quieter pitch swell + light bounce via `reclaimWaveCleared`.
   Complete marks the street `STREET_SECURED` and **purity-locks** it — pure
   stays pure (no auto re-ink, no pollution rises until a new reclaim starts).
   Client HUD shows a short secured-lock tip + meter rim confirm.
6. Bail mid-reclaim (`~stopreclaim` / director stop while `STATE_ACTIVE`) marks the
   street `STREET_CONTESTED`. Residual ink slowly re-creeps via
   `PollutionManagerAI` (`POLLUTION_RECREEP_*`) toward `POLLUTION_RECREEP_CAP`;
   fog / tint / street audio follow the rising `setZonePollution`. A one-shot
   rubber-hose whisper warns toons still on the street. Pure / secured /
   purity-locked streets never auto-stain.

## Discoverable play (preferred)

Walk onto Loopy / Punchline / Silly: `PlayEntry` auto-arms melee and auto-starts
reclaim packs. Fight with **F**, dodge with **Shift**, campaign with **C**.
No `~spawncorrupt` required for the happy path.

On polluted ACTS street enter, `PlayEntry` flashes a brief rubber-hose ink **edge
vignette** (hood-tinted) that fades as the tip bar appears
(`ENTRY_VIGNETTE_*` in `CorruptionGlobals`). Skipped once the street is pure.

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

Per-wave `waveScripts` on `STREET_PACKS` / campaign `ACTS` drive pack composition
(and pack size) when present; `bruteFraction` / `snareFraction` / `gagsterFraction`
remain the fallback via `pickPackArchetype`. Scripts use `ink` / `brute` / `snare`
/ `gagster` tokens.

- **Loopy street pack** (`ReclaimGlobals.STREET_PACKS` / `loopy-smudge`, zone `2200`):
  scripted Smudge tutorial → Brute intro → Snare joins → mixed elite
  (seed 0.55, maxPacks 4). PlayEntry tip reads explore → fight → reclaim;
  warm ink-yellow start banner.
- Loopy campaign **C** mirrors that ramp across 3 waves (`ACTS` `waveScripts`);
  fraction fields stay `0` as fallback only.
- **Punchline street pack** (`punchline-sludge`, zone `2300`):
  scripted Snare-front + Gunk Gagster lob → Gagster swarm → Brute pair → elite
  (seed 0.70, maxPacks 4). Gunk Gagster is a real fourth archetype (teal
  gag-lob puddle trap), not a Smudge rename. PlayEntry tip reads explore →
  fight → reclaim; start banner is gag-green.
- Punchline campaign ACTS `waveScripts` stay the source of truth for **C**;
  STREET_PACKS mirrors so discoverable auto-reclaim matches the second-hood beat.
- **Silly street pack** (`silly-overlord`, zone `2100`): Overlord-only scripts
  (solo → twin swell). Starts Rising (`finalePhase` 1); mid-fight HP-threshold
  (`overlordP2HpFrac`) promotes to Unleashed (slam + Smudge adds) without a
  campaign restart. Oswald twist reveal stays campaign P2 only. Campaign
  finale P2 scripts still swell to twin / triple Overlords on **C**.

```
~spawncorrupt 2 0 0   # Ink Smudge
~spawncorrupt 1 0 1   # Sludge Brute
~spawncorrupt 1 0 2   # Balloon Snare
~spawncorrupt 1 0 3   # Gunk Gagster
~spawngagster         # Gunk Gagster shortcut
```

## Depth D2 enemy demo

```
~spawncorrupt 2
~hackslash 0
# CorruptToons prefer ink-tinted Toon Actor silhouettes (DNA clone of you
# when available), else improved card limbs. Chase AI unchanged; between
# telegraphs sparse ambient ink drips (IdleInkDripFx) show pollution
# presence, layered with soft cream / pastel contrast drips
# (IdleCreamDripContrastFx) plus sunny cream / pastel sparkle flecks on
# the cream drip path (IdleCreamDripSparkleFx) plus soft cream wash pulse
# + delayed cream aftershock against ink idle drips (IdleCreamWashPulseFx —
# death cream wash aftershock #172 grammar) plus sunny cream / pastel rim
# flecks on the ink silhouette
# (CorruptSilhouetteCreamRimFx) plus rising cream / pastel sparkle flecks
# on the silhouette cream rim (CorruptSilhouetteCreamSparkleFx) plus soft
# cream wash pulse + delayed cream aftershock against the ink silhouette
# (CorruptSilhouetteCreamWashFx — idle cream wash aftershock #177 grammar).
# Telegraph wind-up pauses idle drips / sparkles / wash / rim flecks and plays
# a short ink drip / splat pop (CorruptTelegraphInkFx) layered with
# sunny cream / pastel warn flecks + delayed cream aftershock
# (CorruptTelegraphCreamWarnFx — contrast to ink) plus rising cream /
# pastel sparkle flecks on the warn spray (CorruptTelegraphCreamSparkleFx)
# plus soft cream wash pulse against ink telegraph
# (CorruptTelegraphCreamWashFx — silhouette / idle cream-wash grammar)
# plus squash/SFX so wind-ups read without a combat HUD; impact flash on hit.
# Ink Smudge also flashes purple ink-fist telegraph pop (SmudgeInkTelegraphFx).
# Melee hits on Smudge flash SmudgeInkSplashFx (cheap purple ink splash)
# then SmudgeHitCreamSplashFx (deepened cream splash beyond #259 + thicker
# radial cream hose smears + wider cream aftershock) so pack hits read
# juicier — distinct from Snare whip / Brute drip / Gunk bloom; plus soft
# cream wash pulse (SmudgeHitCreamWashFx — overlord-hit / telegraph /
# silhouette / death cream-wash grammar);
# Smudge death layers splash with CorruptDeathPopFx for swarm readability.
# Melee hits on Brute flash BruteSludgeSplashFx (cheap green sludge splash);
# Brute spit land also fires BruteSpitCreamSplashFx (deepened cream splash
# beyond #264 + thicker vertical cream drip filaments + heavier downward
# cream aftershock) so the spit impact reads juicier after telegraph —
# distinct from Snare whip / Gunk bloom / Smudge radial hose.
# Brute death layers splash with CorruptDeathPopFx.
# Melee hits on Snare flash SnareStringSnapSplashFx (cheap amber string-snap);
# Snare death layers splash with CorruptDeathPopFx.
# Gunk Gagster lob land flashes a teal puddle ring plus
# GagsterPuddleCreamSplashFx (deepened cream splash beyond #276 + thicker
# flat puddle-plane cream bloom + wider settle aftershock) so the trap
# impact reads juicier after the telegraph puddle warn — distinct from
# Smudge radial hose / Brute vertical drip / Snare whip.
# Melee hits on Ink Overlord flash OverlordMagentaInkSplashFx (magenta /
# crimson, phase-retinted) then soft cream wash pulse
# (OverlordHitCreamWashFx — telegraph / silhouette / death cream-wash
# grammar); Overlord death layers splash with DeathPop (+ death cream wash).
# Melee (F / LMB) splat-defeats them (CorruptDeathPopFx scale burst +
# ink/sludge/balloon droplet spray + CorruptDeathCreamFleckFx sunny
# cream / pastel flecks + CorruptDeathCreamSparkleFx rising cream sparkles
# + CorruptDeathCreamWashFx soft cream wash + delayed cream aftershock);
# purity pop + pollution drop.
```

## Idle cream drip contrast demo

```
~spawncorrupt 2
~hackslash 0
# Watch idle purple ink drips layered with soft cream / pastel drips
# (IdleCreamDripContrastFx). Contrast to IdleInkDripFx.
# IDLE_CREAM_DRIP_ENABLED = False drops cream drips only.
```

## Idle cream drip sparkle fleck demo

```
~spawncorrupt 2
~hackslash 0
# Watch idle cream contrast drips with sunny cream / pastel sparkle
# flecks along the drip path (IdleCreamDripSparkleFx — silhouette rim
# sparkle grammar). Telegraph pauses drips + sparkles + wash + rim flecks.
# IDLE_CREAM_DRIP_SPARKLE_ENABLED = False drops sparkles only.
```

## Idle cream wash pulse demo

```
~spawncorrupt 2
~hackslash 0
# Watch soft cream wash pulse against idle ink drips, then delayed cream
# aftershock (flecks + soft halo)
# (IdleCreamWashPulseFx — death cream wash aftershock #172 grammar,
# quieter ambient). Telegraph pauses wash + aftershock with drips.
# IDLE_CREAM_WASH_ENABLED = False drops wash + aftershock.
# IDLE_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
```

## Silhouette cream rim rising sparkle demo

```
~spawncorrupt 2
~hackslash 0
# Watch cream rim flecks (CorruptSilhouetteCreamRimFx) with sunny cream /
# pastel sparkle flecks rising from the rim edge
# (CorruptSilhouetteCreamSparkleFx — drip-sparkle twinkle grammar).
# Telegraph pauses drips + sparkles + rim + rising rim sparkles + wash.
# SILHOUETTE_CREAM_SPARKLE_ENABLED = False drops rising sparkles only.
```

## Silhouette cream wash pulse demo

```
~spawncorrupt 2
~hackslash 0
# Watch soft cream wash pulse against the ink silhouette, then delayed cream
# aftershock (flecks + soft halo)
# (CorruptSilhouetteCreamWashFx — idle cream wash aftershock #177 grammar,
# quieter ambient). Telegraph pauses wash + aftershock with rim / sparkles.
# SILHOUETTE_CREAM_WASH_ENABLED = False drops wash + aftershock.
# SILHOUETTE_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
```

## Telegraph cream warn fleck demo

```
~spawncorrupt 2
~hackslash 0
# Close range — telegraph shows ink drip / silhouette plus sunny cream /
# pastel warn flecks (CorruptTelegraphCreamWarnFx), then a delayed cream
# aftershock (soft halo + residual flecks settling). Contrast to ink.
# TELEGRAPH_CREAM_WARN_ENABLED = False drops flecks + aftershock.
# TELEGRAPH_CREAM_WARN_AFTERSHOCK_ENABLED = False drops aftershock only.
```

## Telegraph cream warn rising sparkle demo

```
~spawncorrupt 2
~hackslash 0
# Close range — telegraph cream warn flecks with sunny cream / pastel
# sparkle flecks rising from the warn spray
# (CorruptTelegraphCreamSparkleFx — silhouette cream sparkle grammar).
# TELEGRAPH_CREAM_SPARKLE_ENABLED = False drops rising sparkles only.
```

## Telegraph cream wash pulse demo

```
~spawncorrupt 2
~hackslash 0
# Close range — telegraph cream warn / aftershock / rising sparkles, then
# soft cream wash pulse against ink telegraph
# (CorruptTelegraphCreamWashFx — silhouette / idle / death cream-wash
# two-beat grammar). Contrast to ink.
# TELEGRAPH_CREAM_WASH_ENABLED = False drops wash only.
```

## Death cream fleck burst demo

```
~spawncorrupt 1
~hackslash 0
# Land F / LMB until defeat — CorruptDeathPopFx ink splat layers with
# sunny cream / pastel flecks (CorruptDeathCreamFleckFx). Not ink.
# DEATH_CREAM_FLECK_ENABLED = False drops flecks only.
```

## Death cream fleck rising sparkle demo

```
~spawncorrupt 1
~hackslash 0
# Land F / LMB until defeat — cream fleck burst with sunny cream / pastel
# sparkle flecks rising from the burst (CorruptDeathCreamSparkleFx —
# telegraph / silhouette cream sparkle grammar), then soft cream wash +
# delayed cream aftershock.
# DEATH_CREAM_SPARKLE_ENABLED = False drops rising sparkles only.
```

## Death cream wash pulse demo

```
~spawncorrupt 1
~hackslash 0
# Land F / LMB until defeat — cream fleck burst, then soft cream wash
# pulse + delayed cream aftershock (flecks + soft halo)
# (CorruptDeathCreamWashFx; entry / purity-complete aftershock grammar).
# DEATH_CREAM_WASH_ENABLED = False drops wash + aftershock.
# DEATH_CREAM_WASH_AFTERSHOCK_ENABLED = False drops aftershock only.
```

## Ink Smudge telegraph / splash demo

```
~spawncorrupt 2 0 0
~hackslash 0
# Smudge: purple squash + ink-fist telegraph pop (SmudgeInkTelegraphFx)
# + ink drip + cream warn flecks + pie whoosh SFX, then impact flash on hit.
# Land F / LMB — cheap purple ink splash (SmudgeInkSplashFx) on each hit,
# then SmudgeHitCreamSplashFx (deepened cream splash beyond #259 + thicker
# radial cream hose smears + wider cream aftershock) plus soft cream wash
# pulse against purple ink (SmudgeHitCreamWashFx — overlord-hit / telegraph /
# silhouette / death cream-wash grammar). Hit path only; defeat layers a
# larger splash with CorruptDeathPopFx (+ death cream wash).
# SMUDGE_HIT_CREAM_SPLASH_ENABLED = False drops cream splash + aftershock;
# SMUDGE_HIT_CREAM_SPLASH_SMEAR_ENABLED = False drops hose smears only;
# SMUDGE_HIT_CREAM_WASH_ENABLED = False drops wash only.
```

## Sludge Brute spit / splash demo

```
~spawncorrupt 1 40 1
# or ~spawnbrute 1 40 1
~hackslash 0
# Brute: green squash + spit-gob telegraph pop (BruteSpitTelegraphFx)
# + ink drip + squirt SFX, then ink blob on hit. Spit land also fires
# BruteSpitCreamSplashFx (deepened cream splash beyond #264 + thicker
# vertical cream drip filaments + heavier downward cream aftershock) so
# the green tank spit reads juicier after the telegraph — distinct from
# Snare whip / Gunk bloom / Smudge radial hose.
# Land F / LMB — cheap green sludge splash (BruteSludgeSplashFx) on each hit;
# defeat layers a larger splash with CorruptDeathPopFx.
# Compare ~spawncorrupt 1   (Ink Smudge: purple ink-fist telegraph + drip).
```

## Balloon Snare string-lash / splash demo

```
~spawncorrupt 1 0 2
# or ~spawnsnare 1 0 2
~hackslash 0
# Snare: amber horizontal rubber stretch + string-lash telegraph pop
# (BalloonSnareTelegraphFx) + vine zip SFX; string line snaps on hit and
# reels the toon a short planar yank toward the zip-flier (not damage-only).
# After the string telegraph reads, a short string-snap counter window
# arms — F / LMB for a bumped snappy punish opener (same reward path as
# perfect-dodge counter); melee mid-telegraph interrupts the wind-up.
# Land F / LMB — cheap amber string-snap splash (SnareStringSnapSplashFx)
# on each hit; a successful string-snap counter punish also fires a deepened
# cream splash beyond #269 + thicker horizontal cream whip filaments +
# wider sideways cream aftershock (SnareStringCounterCreamSplashFx) so the
# rewarded window feels juicier — distinct from Gunk puddle cream bloom /
# Smudge radial hose / Brute vertical drip.
# Defeat layers a larger splash with CorruptDeathPopFx.
# Fast fragile zip-flier — distinct from Smudge melee and Brute spit.
```

## Ink Overlord finale phases

Silly Street campaign (`~advancecampaign force` to skip ahead, then
`~startcampaign` on zone `2100`). Toontown spiritual-sequel framing —
rubber-hose Oswald stretch-punch combat only, **no keyblades**. Victory
lands the Oswald twist tease (he caused the corruption) **plus** a short
fightable **Corrupted Oswald** chase/arena spawn (`ARCHETYPE_CORRUPT_OSWALD`
via `CampaignDirectorAI` / `OswaldBetrayalChase`) as the betrayal gameplay
consequence — not cream-only. Full dialogue is out of scope here.

1. **Phase 1 — Rising**: magenta telegraph squash/stretch + Silly Meter phase-one
   SFX, ink crown silhouette flash (`OverlordTelegraphCrownFx`), ink rain /
   ink fall shower (`OverlordPhaseInkRainFx`), deepened cream danger-ring
   warn beyond #255 + denser radial cream phase flecks + juicier impact
   punch bloom with wider cream aftershock (`OverlordTelegraphPunchFx`;
   stretch hold tracks telegraphDelay — distinct from Brute spit cream drip
   / Snare whip / Smudge hose / Gunk puddle bloom),
   HUD `OVERLORD · P1 RISE`, wind-up chip `P1 MAGENTA SWELL`.
   **AI**: slower chase + mid-range **ink-rain AoE** (`OVERLORD_PHASE_COMBAT[1]`)
   matching the rain puddle / spread — not Smudge melee smack.
2. Clear packs → purity beat → director restarts **Phase 2**.
3. **Phase 2 — Unleashed**: crimson telegraphs (wider squash / taller stretch) +
   phase-two SFX, hotter crown flash, denser ink rain, snappier cream
   danger-ring / impact punch (juicier cream rim + denser flecks + wider
   aftershock beyond #255),
   hotter hit flash, FOV + fullscreen ink slam transition sting
   (`announceFinalePhaseTransition`), HUD `OVERLORD · P2 UNLEASHED`, wind-up
   chip `P2 CRIMSON FURY`.
   **AI**: enrage chase + wider/faster rain AoE, close-range **slam** when
   the player is already in the ink, plus **Smudge adds** on wave 2+
   (`phase2.addCount` / `OVERLORD_P2_ADD_*`).
4. Clear again → campaign victory + soft twist tease
   (`CampaignGlobals.FINALE_TWIST_TEASE`) → delayed **Corrupted Oswald**
   chase spawn (`OSWALD_BETRAYAL_CHASE_*`; tip + melee arm on client).

Debug Overlord AI without the full campaign: `~spawnoverlord` (P1) /
`~spawnoverlord 1 160 2` (P2) / `~spawncorrupt 1 90 0 1`.
Debug the betrayal chase enemy: `~spawncorruptedoswald` /
`~spawncorrupt 1 0 4`.

## Ink Overlord magenta ink splash demo

```
# Silly finale Overlord (name contains "overlord" / reclaim finalePhase):
~hackslash 0
# Land F / LMB — cheap magenta/crimson ink splash
# (OverlordMagentaInkSplashFx) on each hit; P1 magenta vs P2 crimson.
# Defeat layers a larger splash with CorruptDeathPopFx.
# Distinct from street Smudge purple (SmudgeInkSplashFx).
```

## Ink Overlord hit cream wash pulse demo

```
# Silly finale Overlord (name contains "overlord" / reclaim finalePhase):
~hackslash 0
# Land F / LMB — magenta/crimson ink splash, then soft cream wash pulse
# against magenta ink (OverlordHitCreamWashFx — telegraph / silhouette /
# death cream-wash grammar). Hit path only; death keeps splash + death wash.
# OVERLORD_HIT_CREAM_WASH_ENABLED = False drops wash only.
```

