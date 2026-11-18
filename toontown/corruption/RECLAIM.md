# Corruption → reclaim (slice 3 hookup)

This package is the slice 2 foundation for neighborhood reclaim:

1. `PollutionManager` holds per-zone pollution `0..1` (pure → polluted).
2. `DistributedCorruptToon` stubs spawn in a zone (magic word `~spawncorrupt`).
3. Defeating a corrupt toon calls `PollutionManagerAI.onCorruptToonDefeated`, which lowers that zone's scalar by `POLLUTION_PER_DEFEAT`.
4. When pollution hits `0.0`, AI emits `pollutionReclaimed` for purity restore FX / NPC cheer (slice 3).

Demo without melee PR: `~pollute`, `~purify`, `~spawncorrupt`. Soft-lock / hits should target `HackSlashTarget` once slice 1 merges.
