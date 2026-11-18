"""Per-avatar campaign unlock persistence (AI dataFolder JSON).

`CampaignDirectorAI.unlockedThrough` / actIndex used to live only in the
air process, so explore→fight→reclaim progress reset on logout / district
restart. This module stores a thin per-toon blob beside other AI JSON
saves (buildings / track records) — no DC / avatar schema change.

Pure helpers are panda-free so headless tests can exercise sanitize /
round-trip without Direct / Astron.
"""

from __future__ import annotations

import json
import os

from toontown.campaign import CampaignGlobals

# Filename under air.dataFolder (optional shard prefix via progressPath).
PROGRESS_FILENAME = getattr(
    CampaignGlobals, 'CAMPAIGN_PROGRESS_FILENAME', 'campaign_progress.json')


def progressPath(dataFolder, shard=None):
    """Resolve JSON path under the AI data folder (buildings twin)."""
    folder = dataFolder or ''
    if folder and not folder.endswith(('/', '\\')):
        folder = folder + '/'
    shardPart = ''
    if shard is not None and str(shard) != '':
        shardPart = '%s_' % shard
    name = PROGRESS_FILENAME
    return '%s%s%s' % (folder, shardPart, name)


def defaultProgress():
    """Fresh campaign: Act 1 unlocked only."""
    return {
        'unlockedThrough': 0,
        'actIndex': 0,
        'reclaimCount': 0,
        'state': int(CampaignGlobals.STATE_IDLE),
        'finalePhase': 0,
    }


def sanitizeProgress(raw, numActs=None):
    """Clamp / coerce a raw blob into a safe progress dict."""
    if numActs is None:
        numActs = len(CampaignGlobals.ACTS)
    numActs = max(1, int(numActs))
    maxIndex = numActs - 1
    base = defaultProgress()
    if not isinstance(raw, dict):
        return base

    def _int(key, default, lo, hi):
        try:
            value = int(raw.get(key, default))
        except (TypeError, ValueError):
            value = default
        return max(lo, min(hi, value))

    unlocked = _int('unlockedThrough', 0, 0, maxIndex)
    actIndex = _int('actIndex', unlocked, 0, maxIndex)
    # Act cursor cannot run ahead of unlocks.
    if actIndex > unlocked:
        actIndex = unlocked
    reclaimCount = _int('reclaimCount', 0, 0, 9999)
    state = _int(
        'state', CampaignGlobals.STATE_IDLE,
        CampaignGlobals.STATE_IDLE, CampaignGlobals.STATE_VICTORY)
    finalePhase = _int('finalePhase', 0, 0, 1)
    return {
        'unlockedThrough': unlocked,
        'actIndex': actIndex,
        'reclaimCount': reclaimCount,
        'state': state,
        'finalePhase': finalePhase,
    }


def snapshotFromDirector(director):
    """Build a sanitizable blob from a live CampaignDirectorAI."""
    return sanitizeProgress({
        'unlockedThrough': getattr(director, 'unlockedThrough', 0),
        'actIndex': getattr(director, 'actIndex', 0),
        'reclaimCount': getattr(director, 'reclaimCount', 0),
        'state': getattr(director, 'state', CampaignGlobals.STATE_IDLE),
        'finalePhase': getattr(director, '_finalePhase', 0),
    })


def applyProgressToDirector(director, progress):
    """Hydrate director fields from a sanitized progress blob."""
    blob = sanitizeProgress(progress)
    director.unlockedThrough = blob['unlockedThrough']
    director.actIndex = blob['actIndex']
    director.reclaimCount = blob['reclaimCount']
    director.state = blob['state']
    director._finalePhase = blob['finalePhase']
    return blob


def loadAll(path):
    """Load {avatarIdStr: progressDict}. Missing / bad file → {}."""
    if not path:
        return {}
    try:
        with open(path, 'r') as handle:
            data = json.load(handle)
    except (IOError, OSError, ValueError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    for key, value in data.items():
        out[str(key)] = sanitizeProgress(value)
    return out


def saveAll(path, data):
    """Atomic-ish write of the progress map (backup rename like buildings)."""
    if not path:
        return False
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError:
            return False
    clean = {}
    if isinstance(data, dict):
        for key, value in data.items():
            clean[str(key)] = sanitizeProgress(value)
    backup = path + '.bu'
    try:
        if os.path.exists(path):
            try:
                os.rename(path, backup)
            except OSError:
                pass
        with open(path, 'w') as handle:
            json.dump(clean, handle, indent=2, sort_keys=True)
            handle.write('\n')
        if os.path.exists(backup):
            try:
                os.remove(backup)
            except OSError:
                pass
        return True
    except (IOError, OSError, TypeError, ValueError):
        # Best-effort restore from backup.
        try:
            if os.path.exists(backup) and not os.path.exists(path):
                os.rename(backup, path)
        except OSError:
            pass
        return False


def readAvatar(path, avId):
    """Return sanitized progress for avId, or None if absent."""
    if avId is None:
        return None
    data = loadAll(path)
    key = str(int(avId))
    if key not in data:
        return None
    return data[key]


def writeAvatar(path, avId, progress):
    """Upsert one avatar's progress and flush to disk."""
    if avId is None or not path:
        return False
    data = loadAll(path)
    data[str(int(avId))] = sanitizeProgress(progress)
    return saveAll(path, data)

