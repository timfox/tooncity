# Toon City USD prim conventions (`Tc` / `tc:`)

Human schema card for authoring + headless validation. Plugin schemas may
land later; until then fixtures use `customData` markers (`tc:kind`, …).
Tone is Oswald / Toontown reclaim — **no outside franchise branding or prop vocabulary**.

Validated by `toontown.usd.validate` (PR 2). Headless only; no Hydra.

## Prim / API kinds

| Kind | Purpose | Required / notable `tc:` fields |
| --- | --- | --- |
| `TcStreetRoot` | Street or playground composition root | **`tc:zoneId`** (int), **`tc:packId`** (string); optional `tc:hood`, `tc:bamPath` |
| `TcReclaimVolume` | Pollution / reclaim bounds | `tc:seedPollution` (float) |
| `TcSpawnStand` | Corrupt pack / ambush stand | **`tc:archetype`** allow-list (below); optional `tc:standIndex` |
| `TcProp` | Prop with bake targets | `tc:bamPath` and/or `tc:dnaCode` |
| `TcCharacterKit` | Character assembly | variant sets `pure` / `ink` / `oswaldTrusted` |
| `TcLodGroup` | LOD container | children named exactly `lod1000`, `lod500`, `lod250` |
| `TcMaterialLook` | Material look bind | `pure` vs `polluted` |
| `TcAnimClip` | Clip ↔ Actor anim key | clip name matches Actor dict key |
| `TcFxSocket` | Empty Xform for FX attach | telegraph / hit / death / cream sockets |
| `TcCameraShot` | Optional cinematic camera | tooling / shot lists only — not soft-lock |
| `TcLightLook` | Pure vs polluted light set | bake intensity/color tables |

## LOD names

Toon Actor LOD bands are **1000 / 500 / 250**. Under a `TcLodGroup`, child
prims (or any prim named `lodN`) must use exactly:

- `lod1000`
- `lod500`
- `lod250`

Any other `lod###` name fails validation.

## Spawn archetype allow-list

`tc:archetype` on `TcSpawnStand` must be one of the reclaim tokens (matches
`ReclaimGlobals.WAVE_SCRIPT_TOKENS` short forms):

| Token | Maps to |
| --- | --- |
| `ink` | Ink Smudge |
| `brute` | Sludge Brute |
| `snare` | Balloon Snare |
| `gag` | Gunk Gagster |
| `oswald` | Corrupted Oswald (finale betrayal) |

Longer aliases (`ink_smudge`, `gagster`, …) belong in wave scripts, not USD
archetype fields — keep USD tokens short and stable.

## Banned tokens (outside franchise branding)

Prim paths, layer comments, and `customData` must not use outside franchise
branding, prop names, or related character tokens. The headless validator
owns the exact ban list (`toontown.usd.validate`); keep schema docs and
fixtures free of those strings.

## Composition sketch (street packs)

```
tc/streets/loopy_lane/
  loopy_lane.usda          # base geometry refs + vis
  packs/loopy_smudge.usda  # sublayer: volumes, stands, banners metadata
  looks/polluted.usda      # opinion: materials/lights ink
  looks/pure.usda          # opinion: purity restore
```

`packId` values must match `ReclaimGlobals.STREET_PACKS` (`loopy-smudge`,
`punchline-sludge`, `silly-overlord`). Runtime reclaim still flips pollution
scalars / FX in Python; USD owns authoring composition.

## Character kit bake → Actor (corrupt ink)

`fixtures/kits/ink_smudge_kit.usda` is the Ink Smudge (`ink` variant)
assembly. Headless map: `toontown.usd.character_kit.load_kit`.

- LOD prims `lod1000` / `lod500` / `lod250` carry `tc:bamPath` under
  `phase_3/models/char/…` — bake into Actor LOD parts matching
  `Toon.setLODs()` (bands 1000 / 500 / 250).
- Material looks `pure` / `ink` bind to tint hooks used by corruption;
  FX sockets (`telegraph` / `hit` / `death` / `cream`) are empty
  attach Xforms only.
- **Do not** replace `DistributedCorruptToon` CardMaker silhouette
  fallback yet — Actor DNA path stays primary; kit BAM paths are a
  future feature-flagged feed.

## Combat FX sockets → CorruptionGlobals

`fixtures/fx/telegraph_sockets.usda` declares empty `TcFxSocket` Xforms
for telegraph / hit / death / cream (plus layered cream hooks). Each
socket carries `tc:consumerKey` naming a `CorruptionGlobals` LOOK
attribute (`TELEGRAPH_INK_DRIP_LOOK`, `DEATH_POP_LOOK`, …). Headless map:
`toontown.usd.fx_sockets.load_fx_sockets`. String table only — no mesh
FX, no Hydra, no gameplay wiring.

## Runtime street overlay hook (metadata only)

Feature flag `want-usd-street-overlay` (default **off**). Optional
`usd-street-overlay-path` / `usd-street-overlay-look`. When enabled,
`toontown.usd.runtime_hook` composes a street fixture stack and
`apply_overlay_metadata` returns pollution seed + spawn stand list for
TownLoader / SafeZoneLoader / reclaim enter to stash — no Hydra, no DNA
rewrite, no `pxr` required.

## Fixture reference

See `fixtures/schema_kitchen_sink.usda` for a single ASCII stage that
declares every kind above with valid LOD names and archetype tokens.
Character kits live under `fixtures/kits/` (see `ink_smudge_kit.usda`).
Combat FX sockets live under `fixtures/fx/` (see `telegraph_sockets.usda`).
