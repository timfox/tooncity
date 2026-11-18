"""Per-avatar campaign unlock persistence (AI dataFolder JSON).

`CampaignDirectorAI.unlockedThrough` / actIndex used to live only in the
air process, so explore→fight→reclaim progress reset on logout / district
restart. This module stores a thin per-toon blob beside other AI JSON
saves (buildings / track records) — no DistributedToon avatar schema.

Client hub tip + OswaldPresence + CampaignHandoff power mirror the blob
after relog via a thin PollutionManager status push (`setCampaignProgress`
incl. reclaimCount); see `clientMirrorFromProgress`. Mid-chase Corrupted
Oswald remaining HP is stored as ``chaseHp`` so resume / relog does not
full-heal the wash fight. Finished-reclaim ``securedZones`` mirrors
PollutionManagerAI purity locks so AI restart + relog reseal cleared
streets. Pure helpers are panda-free so headless tests can exercise
sanitize / round-trip / mirror flags without Direct / Astron.
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
        # 1 after Corrupted Oswald chase clear (epilogue soft-end).
        'chaseCleared': 0,
        # Remaining Corrupted Oswald HP mid-chase (0 = full / unset).
        # Resume / relog must not full-heal a damaged wash fight.
        'chaseHp': 0,
        # 1 after first E-talk meet with trusted Oswald (first-meet tip).
        # Durable trust beat — survives relog; not wiped on campaign replay.
        'oswaldMet': 0,
        # 1 after first reclaim cheer from trusted Oswald (cheer-on-clear).
        # Durable trust beat — survives relog; not wiped on campaign replay.
        'oswaldCheered': 0,
        # Finished-reclaim street zoneIds purity-locked for this avatar.
        # Mirrors PollutionManagerAI._purityLocked so AI restart + relog
        # can re-seal cleared streets while unlocks still say cleared.
        'securedZones': [],
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
    chaseCleared = _int('chaseCleared', 0, 0, 1)
    # Ceiling is generous; spawn clamps against live chase maxHp.
    chaseHp = _int('chaseHp', 0, 0, 9999)
    # Mid-chase HP only matters while victory + uncleared chase.
    if chaseCleared or state != int(CampaignGlobals.STATE_VICTORY):
        chaseHp = 0
    oswaldMet = _int('oswaldMet', 0, 0, 1)
    oswaldCheered = _int('oswaldCheered', 0, 0, 1)
    # Explicit list wins when present (contested replay may drop a zone
    # while unlockedThrough still says the act was cleared). Older blobs
    # without the key migrate from unlocks / victory so AI restart still
    # reseals cleared streets.
    hasExplicitSecured = 'securedZones' in raw
    securedRaw = raw.get('securedZones', [])
    if isinstance(securedRaw, (str, bytes)):
        securedRaw = []
    if not isinstance(securedRaw, (list, tuple, set)):
        securedRaw = []
    securedZones = set()
    for item in securedRaw:
        try:
            zoneId = int(item)
        except (TypeError, ValueError):
            continue
        if zoneId > 0:
            securedZones.add(zoneId)
    if not hasExplicitSecured:
        acts = getattr(CampaignGlobals, 'ACTS', ()) or ()
        for i, act in enumerate(acts):
            if i < unlocked or state == int(CampaignGlobals.STATE_VICTORY):
                try:
                    zoneId = int(act.get('zoneId', 0) or 0)
                except (TypeError, ValueError):
                    zoneId = 0
                if zoneId > 0:
                    securedZones.add(zoneId)
    return {
        'unlockedThrough': unlocked,
        'actIndex': actIndex,
        'reclaimCount': reclaimCount,
        'state': state,
        'finalePhase': finalePhase,
        'chaseCleared': chaseCleared,
        'chaseHp': chaseHp,
        'oswaldMet': oswaldMet,
        'oswaldCheered': oswaldCheered,
        'securedZones': sorted(securedZones),
    }


def snapshotFromDirector(director):
    """Build a sanitizable blob from a live CampaignDirectorAI."""
    chaseCleared = getattr(director, 'chaseCleared', None)
    if chaseCleared is None:
        chaseCleared = getattr(director, '_chaseCleared', 0)
    chaseHp = getattr(director, 'chaseHp', None)
    if chaseHp is None:
        chaseHp = getattr(director, '_chaseHp', 0)
    oswaldMet = getattr(director, 'oswaldMet', None)
    if oswaldMet is None:
        oswaldMet = getattr(director, '_oswaldMet', 0)
    oswaldCheered = getattr(director, 'oswaldCheered', None)
    if oswaldCheered is None:
        oswaldCheered = getattr(director, '_oswaldCheered', 0)
    securedZones = getattr(director, 'securedZones', None)
    if securedZones is None:
        securedZones = getattr(director, '_securedZones', [])
    return sanitizeProgress({
        'unlockedThrough': getattr(director, 'unlockedThrough', 0),
        'actIndex': getattr(director, 'actIndex', 0),
        'reclaimCount': getattr(director, 'reclaimCount', 0),
        'state': getattr(director, 'state', CampaignGlobals.STATE_IDLE),
        'finalePhase': getattr(director, '_finalePhase', 0),
        'chaseCleared': chaseCleared,
        'chaseHp': chaseHp,
        'oswaldMet': oswaldMet,
        'oswaldCheered': oswaldCheered,
        'securedZones': list(securedZones or []),
    })


def applyProgressToDirector(director, progress):
    """Hydrate director fields from a sanitized progress blob."""
    blob = sanitizeProgress(progress)
    director.unlockedThrough = blob['unlockedThrough']
    director.actIndex = blob['actIndex']
    director.reclaimCount = blob['reclaimCount']
    director.state = blob['state']
    director._finalePhase = blob['finalePhase']
    director.chaseCleared = int(blob.get('chaseCleared', 0) or 0)
    director.chaseHp = int(blob.get('chaseHp', 0) or 0)
    director.oswaldMet = int(blob.get('oswaldMet', 0) or 0)
    director.oswaldCheered = int(blob.get('oswaldCheered', 0) or 0)
    director.securedZones = list(blob.get('securedZones') or [])
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


def softNextStreetFromProgress(progress):
    """Hub soft-next street name for mid-campaign resume, or None.

    Fresh Act 1 (unlockedThrough 0) keeps the generic Loopy invite.
    STATE_VICTORY yields None so the victory / epilogue tip wins.
    Otherwise point at the act cursor street (resume target after relog).
    """
    blob = sanitizeProgress(progress)
    if int(blob.get('state', 0)) == int(CampaignGlobals.STATE_VICTORY):
        return None
    unlocked = int(blob.get('unlockedThrough', 0) or 0)
    actIndex = int(blob.get('actIndex', 0) or 0)
    if unlocked <= 0 and actIndex <= 0:
        return None
    acts = getattr(CampaignGlobals, 'ACTS', ()) or ()
    if not acts:
        return None
    idx = max(0, min(actIndex, len(acts) - 1))
    name = acts[idx].get('name')
    return str(name) if name else None


def clientMirrorFromProgress(progress):
    """Derive client presentation flags from a sanitized progress blob.

    Used after login / hydrate so PlayEntry hub tip, OswaldPresence, and
    CampaignHandoff power match AI-persisted victory / unlock /
    chaseCleared / reclaimCount (not session-only `_victoryEpilogue` /
    `_betrayed` / `_localReclaimCount`).
    """
    blob = sanitizeProgress(progress)
    state = int(blob.get('state', CampaignGlobals.STATE_IDLE) or 0)
    chaseCleared = int(blob.get('chaseCleared', 0) or 0)
    unlockedThrough = int(blob.get('unlockedThrough', 0) or 0)
    actIndex = int(blob.get('actIndex', 0) or 0)
    reclaimCount = int(blob.get('reclaimCount', 0) or 0)
    oswaldMet = int(blob.get('oswaldMet', 0) or 0)
    oswaldCheered = int(blob.get('oswaldCheered', 0) or 0)
    securedZones = list(blob.get('securedZones') or [])
    victory = state == int(CampaignGlobals.STATE_VICTORY)
    # Twist already landed once STATE_VICTORY — hide trusted Oswald whether
    # the betrayal chase is still pending or already washed.
    betrayed = victory
    return {
        'unlockedThrough': unlockedThrough,
        'actIndex': actIndex,
        'state': state,
        'chaseCleared': chaseCleared,
        'reclaimCount': reclaimCount,
        'oswaldMet': oswaldMet,
        'oswaldCheered': oswaldCheered,
        'securedZones': securedZones,
        'victoryEpilogue': victory,
        'betrayed': betrayed,
        'softNextStreet': softNextStreetFromProgress(blob),
        'chasePending': bool(victory and not chaseCleared),
    }

