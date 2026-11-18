"""Campaign power bump — light melee damage scale from reclaim count.

Mutates HackSlashConfig.COMBO_DAMAGE in place from a stored baseline so
campaign depth can ship without rewriting the combat package.

Login / hydrate re-applies via CampaignHandoff._onCampaignProgressSync
using AI-persisted reclaimCount (PollutionManager setCampaignProgress)
so mid-campaign relog keeps the same melee scale as an unbroken session.
"""

from toontown.campaign import CampaignGlobals

_BASE_DAMAGE = None


def _ensureBaseline():
    global _BASE_DAMAGE
    if _BASE_DAMAGE is not None:
        return
    try:
        from toontown.hackslash import HackSlashConfig
        _BASE_DAMAGE = tuple(HackSlashConfig.COMBO_DAMAGE)
    except Exception:
        _BASE_DAMAGE = (8, 12, 28)


def applyPowerBump(reclaimCount):
    """Scale combo damage by reclaim progress. Returns the multiplier used."""
    _ensureBaseline()
    bump = min(
        CampaignGlobals.POWER_BUMP_MAX,
        max(0.0, float(reclaimCount) * CampaignGlobals.POWER_BUMP_PER_RECLAIM))
    mult = 1.0 + bump
    try:
        from toontown.hackslash import HackSlashConfig
        HackSlashConfig.COMBO_DAMAGE = tuple(
            max(1, int(round(d * mult))) for d in _BASE_DAMAGE)
    except Exception:
        pass
    return mult


def resetPowerBump():
    """Restore baseline melee damage (campaign replay)."""
    _ensureBaseline()
    try:
        from toontown.hackslash import HackSlashConfig
        HackSlashConfig.COMBO_DAMAGE = tuple(_BASE_DAMAGE)
    except Exception:
        pass
