"""TTC hub stain beat after Oswald betrayal / victory.

After finale victory (betrayal), Toontown Central (`HUB_ZONE`) receives an
authored pollution fog so the hub is no longer a pristine sunny plaza while
the Corrupted Oswald chase is still pending. Chase clear / replay wipe
washes the hub back to pure. Gameplay world consequence — not cream FX,
not OswaldPresence NPC deepen. Toontown spiritual sequel — no keyblades /
KH branding.
"""

from __future__ import annotations

from toontown.campaign import CampaignGlobals
from toontown.corruption import CorruptionGlobals


def hubStainEnabled():
    return bool(getattr(CampaignGlobals, 'HUB_STAIN_ENABLED', True))


def hubStainZone():
    return int(getattr(CampaignGlobals, 'HUB_ZONE', 2000))


def hubStainLevel():
    """Visible fog amount — under street seed caps, readable on TTC."""
    raw = getattr(CampaignGlobals, 'HUB_STAIN_POLLUTION', 0.42)
    try:
        level = float(raw)
    except (TypeError, ValueError):
        level = 0.42
    return CorruptionGlobals.clampPollution(level)


def hubStainWanted(state, chaseCleared=0):
    """True while victory landed and the stain wash (chase) is still pending.

    ``chaseCleared=1`` means Oswald's stain is washed — hub goes pure again.
    Replay wipe leaves STATE_VICTORY, so callers clear via sync after wipe.
    """
    if not hubStainEnabled():
        return False
    try:
        victory = int(state) == int(CampaignGlobals.STATE_VICTORY)
    except (TypeError, ValueError):
        victory = state == CampaignGlobals.STATE_VICTORY
    if not victory:
        return False
    return int(chaseCleared or 0) == 0


def hubStainMsg():
    return str(getattr(
        CampaignGlobals, 'HUB_STAIN_MSG',
        "Oswald's ink reaches Toon Central — the hub is stained!"))


def hubStainClearMsg():
    return str(getattr(
        CampaignGlobals, 'HUB_STAIN_CLEAR_MSG',
        "Toon Central's stain lifts — purity holds at the hub."))


def applyHubStain(air, level=None):
    """Author pollution fog on HUB_ZONE via PollutionManagerAI.

    Clears any purity lock so the betrayal stain can land on a previously
    sunny hub. Does **not** mark contested (no ambient re-creep on HQ).
    Returns the applied pollution level, or None when skipped.
    """
    if not hubStainEnabled() or air is None:
        return None
    pollutionMgr = getattr(air, 'pollutionManager', None)
    if pollutionMgr is None:
        return None
    zoneId = hubStainZone()
    if level is None:
        level = hubStainLevel()
    else:
        level = CorruptionGlobals.clampPollution(level)
    if level <= CorruptionGlobals.POLLUTION_PURE:
        return CorruptionGlobals.POLLUTION_PURE
    # Finished-reclaim lock would refuse the rise — hub stain is authored.
    locked = getattr(pollutionMgr, '_purityLocked', None)
    if locked is not None:
        try:
            locked.discard(int(zoneId))
        except Exception:
            pass
    apply = getattr(pollutionMgr, 'applyBetrayalHubStain', None)
    if callable(apply):
        return apply(zoneId, level)
    setPollution = getattr(pollutionMgr, 'setPollution', None)
    if not callable(setPollution):
        return None
    return setPollution(zoneId, level)


def clearHubStain(air):
    """Wash HUB_ZONE back to pure (chase clear / replay wipe)."""
    if air is None:
        return None
    pollutionMgr = getattr(air, 'pollutionManager', None)
    if pollutionMgr is None:
        return None
    zoneId = hubStainZone()
    clear = getattr(pollutionMgr, 'clearBetrayalHubStain', None)
    if callable(clear):
        return clear(zoneId)
    setPollution = getattr(pollutionMgr, 'setPollution', None)
    if not callable(setPollution):
        return None
    return setPollution(zoneId, CorruptionGlobals.POLLUTION_PURE)


def syncHubStain(air, state, chaseCleared=0, tellToon=None):
    """Apply or clear hub stain from live campaign state. Returns wanted bool."""
    wanted = hubStainWanted(state, chaseCleared=chaseCleared)
    if wanted:
        applied = applyHubStain(air)
        if applied is not None and tellToon is not None:
            msg = hubStainMsg()
            if msg:
                try:
                    tellToon(msg)
                except Exception:
                    pass
        try:
            messenger.send(  # noqa: F821
                'hubStainApplied', [hubStainZone(), float(applied or 0.0)])
        except Exception:
            pass
    else:
        cleared = clearHubStain(air)
        if cleared is not None and tellToon is not None:
            # Only whisper wash when we actually had a prior stain to clear.
            # Callers that always sync on hydrate should pass tellToon=None
            # for quiet re-entry, or gate the whisper themselves.
            pass
        try:
            messenger.send(  # noqa: F821
                'hubStainCleared', [hubStainZone()])
        except Exception:
            pass
    return wanted
