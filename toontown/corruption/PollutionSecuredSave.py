"""District-wide SECURED purity-lock persistence (AI dataFolder JSON).

``PollutionManagerAI._purityLocked`` / ``streetStatus`` used to live only in
the air process, so finished-reclaim streets reopened after AI restart while
campaign progress still said cleared. This module stores a thin secured-zone
set beside other AI JSON saves — panda-free so headless tests can round-trip
without Direct / Astron.
"""

from __future__ import annotations

import json
import os

from toontown.corruption import CorruptionGlobals

SECURED_FILENAME = getattr(
    CorruptionGlobals, 'POLLUTION_SECURED_FILENAME', 'pollution_secured.json')


def securedPath(dataFolder, shard=None):
    """Resolve JSON path under the AI data folder (campaign_progress twin)."""
    folder = dataFolder or ''
    if folder and not folder.endswith(('/', '\\')):
        folder = folder + '/'
    shardPart = ''
    if shard is not None and str(shard) != '':
        shardPart = '%s_' % shard
    return '%s%s%s' % (folder, shardPart, SECURED_FILENAME)


def defaultSecured():
    """Fresh district: no finished-reclaim purity locks yet."""
    return {
        'securedZones': [],
    }


def sanitizeSecured(raw):
    """Clamp / coerce a raw blob into a safe secured-zone dict."""
    base = defaultSecured()
    if not isinstance(raw, dict):
        return base
    zones = raw.get('securedZones', [])
    if isinstance(zones, (str, bytes)):
        zones = []
    if not isinstance(zones, (list, tuple, set)):
        zones = []
    clean = set()
    for item in zones:
        try:
            zoneId = int(item)
        except (TypeError, ValueError):
            continue
        if zoneId <= 0:
            continue
        clean.add(zoneId)
    return {
        'securedZones': sorted(clean),
    }


def snapshotFromManager(manager):
    """Build a sanitizable blob from a live PollutionManagerAI."""
    locked = getattr(manager, '_purityLocked', None) or set()
    return sanitizeSecured({'securedZones': list(locked)})


def applySecuredToManager(manager, secured, mark=True):
    """Hydrate purity locks onto a PollutionManagerAI from a secured blob.

    When ``mark`` is True (default), calls ``markStreetSecured`` so pollution
    is forced pure and recreep tasks refresh. When False, only mutates
    bookkeeping (used by tests / quiet restore without side effects).
    """
    blob = sanitizeSecured(secured)
    zones = blob.get('securedZones') or []
    if not zones:
        return blob
    markFn = getattr(manager, 'markStreetSecured', None) if mark else None
    for zoneId in zones:
        if callable(markFn):
            # Skip persist-on-mark while hydrating (caller persists once).
            try:
                markFn(zoneId, persist=False)
            except TypeError:
                markFn(zoneId)
            continue
        # Quiet bookkeeping fallback.
        locked = getattr(manager, '_purityLocked', None)
        status = getattr(manager, 'streetStatus', None)
        if isinstance(locked, set):
            locked.add(int(zoneId))
        if isinstance(status, dict):
            status[int(zoneId)] = getattr(
                CorruptionGlobals, 'STREET_SECURED', 0)
    return blob


def loadSecured(path):
    """Load secured blob from disk. Missing / bad file → empty defaults."""
    if not path:
        return defaultSecured()
    try:
        with open(path, 'r') as handle:
            data = json.load(handle)
    except (IOError, OSError, ValueError, TypeError):
        return defaultSecured()
    return sanitizeSecured(data)


def saveSecured(path, secured):
    """Atomic-ish write of the secured-zone blob (backup rename)."""
    if not path:
        return False
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError:
            return False
    clean = sanitizeSecured(secured)
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
        try:
            if os.path.exists(backup) and not os.path.exists(path):
                os.rename(backup, path)
        except OSError:
            pass
        return False


def mergeZone(secured, zoneId):
    """Return a new blob with zoneId added to securedZones."""
    blob = sanitizeSecured(secured)
    zones = set(blob.get('securedZones') or [])
    try:
        zones.add(int(zoneId))
    except (TypeError, ValueError):
        return blob
    return sanitizeSecured({'securedZones': list(zones)})


def dropZone(secured, zoneId):
    """Return a new blob with zoneId removed from securedZones."""
    blob = sanitizeSecured(secured)
    zones = set(blob.get('securedZones') or [])
    try:
        zones.discard(int(zoneId))
    except (TypeError, ValueError):
        return blob
    return sanitizeSecured({'securedZones': list(zones)})
