"""Campaign power bump + street-clear slice reward.

Mutates HackSlashConfig.COMBO_DAMAGE in place from a stored baseline so
campaign depth can ship without rewriting the combat package.

Login / hydrate re-applies via CampaignHandoff._onCampaignProgressSync
using AI-persisted reclaimCount (PollutionManager setCampaignProgress)
so mid-campaign relog keeps the same melee scale as an unbroken session.
Live purityRestore and progress sync share an idempotent watermark
(max / absorb) so sync-before-purity cannot double-apply COMBO_DAMAGE.

Street-clear rewards (jellybeans + laff toon-up, trophy-style copy) sit
beside the power bump so reclaim payoff is thicker than COMBO_DAMAGE
alone — Open Toontown slice grammar, not cream FX / not KH.
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
    """Scale combo damage by reclaim progress. Returns the multiplier used.

    Mutates the local (client) HackSlashConfig.COMBO_DAMAGE for juice.
    AI hostile HP drain uses the same POWER_BUMP_* math via
    HackSlashConfig.comboDamageTableFromReclaimCount + reclaimCount on
    CampaignDirectorAI — keep both paths on the shared helper.
    """
    _ensureBaseline()
    per = CampaignGlobals.POWER_BUMP_PER_RECLAIM
    cap = CampaignGlobals.POWER_BUMP_MAX
    hs = None
    try:
        from toontown.hackslash import HackSlashConfig as hs
    except Exception:
        hs = None

    if hs is not None and hasattr(hs, 'powerBumpMultiplier'):
        mult = hs.powerBumpMultiplier(
            reclaimCount, perReclaim=per, bumpMax=cap)
    else:
        bump = min(cap, max(0.0, float(reclaimCount or 0) * float(per)))
        mult = 1.0 + bump

    if hs is not None and hasattr(hs, 'comboDamageTableFromReclaimCount'):
        table = hs.comboDamageTableFromReclaimCount(
            reclaimCount,
            baseTable=_BASE_DAMAGE,
            perReclaim=per,
            bumpMax=cap)
    else:
        table = tuple(
            max(1, int(round(d * mult))) for d in _BASE_DAMAGE)

    if hs is not None:
        try:
            hs.COMBO_DAMAGE = table
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


def streetClearRewardEnabled():
    """True when jellybean / laff street-clear awards are armed."""
    return bool(getattr(
        CampaignGlobals, 'STREET_CLEAR_REWARD_ENABLED', True))


def streetClearRewardMsgName():
    """Messenger name for street-clear reward (PlayEntry / Handoff accept)."""
    if hasattr(CampaignGlobals, 'streetClearRewardMsgName'):
        try:
            return CampaignGlobals.streetClearRewardMsgName()
        except Exception:
            pass
    return getattr(
        CampaignGlobals, 'STREET_CLEAR_REWARD_MSG', 'streetClearReward')


def emitStreetClearReward(
        zoneId=0, beans=0, laff=0, trophy='', ensureClients=True):
    """Send streetClearReward so tip / plate accepts can latch.

    AI award path uses ensureClients=False (no client imports). Client
    purity mirror (CampaignHandoff) ensures PlayEntry + Handoff first so
    the formerly orphan messenger has live accepts (no cream / no KH).
    """
    if ensureClients:
        try:
            from toontown.campaign.PlayEntry import ensurePlayEntryClient
            ensurePlayEntryClient()
        except Exception:
            pass
        try:
            from toontown.campaign.CampaignHandoff import (
                ensureCampaignHandoffClient)
            ensureCampaignHandoffClient()
        except Exception:
            pass
    msg = streetClearRewardMsgName()
    try:
        messenger.send(  # noqa: F821
            msg,
            [int(zoneId or 0), int(beans or 0), int(laff or 0), trophy or ''])
    except Exception:
        pass


def streetClearJellybeans(reclaimCount=1):
    """Jellybeans for one street clear (scales gently with reclaim depth)."""
    base = int(getattr(CampaignGlobals, 'STREET_CLEAR_JELLYBEANS', 20) or 0)
    bonus = int(getattr(
        CampaignGlobals, 'STREET_CLEAR_JELLYBEANS_BONUS_PER_RECLAIM', 0) or 0)
    cap = int(getattr(
        CampaignGlobals, 'STREET_CLEAR_JELLYBEANS_MAX', max(base, 0)) or 0)
    count = max(1, int(reclaimCount or 1))
    # First clear = base; each prior clear adds bonus, capped.
    total = base + bonus * max(0, count - 1)
    if cap > 0:
        total = min(cap, total)
    return max(0, int(total))


def streetClearLaff():
    """Laff toon-up granted on street clear (0 disables heal)."""
    return max(0, int(getattr(CampaignGlobals, 'STREET_CLEAR_LAFF', 0) or 0))


def streetClearTrophyLabel(zoneId=None, streetName=None):
    """Trophy-style label for whisper / handoff (street name filled in)."""
    name = streetName
    if not name:
        name = streetNameForZone(zoneId) or 'Street'
    fmt = getattr(
        CampaignGlobals, 'STREET_CLEAR_TROPHY_FMT',
        'Street Trophy: %s reclaimed!')
    try:
        return fmt % name
    except Exception:
        return 'Street Trophy: %s reclaimed!' % name


def streetNameForZone(zoneId):
    """Resolve a readable street name from campaign ACTS (fallback None)."""
    if zoneId is None:
        return None
    try:
        zoneId = int(zoneId)
    except Exception:
        return None
    for act in getattr(CampaignGlobals, 'ACTS', ()) or ():
        try:
            if int(act.get('zoneId', 0) or 0) == zoneId:
                return act.get('name') or act.get('id') or None
        except Exception:
            continue
    return None


def streetClearRewardPayload(reclaimCount=1, zoneId=None, streetName=None):
    """Pure reward dict for tests / handoff / AI award (no toon mutation)."""
    beans = streetClearJellybeans(reclaimCount)
    laff = streetClearLaff()
    trophy = streetClearTrophyLabel(zoneId=zoneId, streetName=streetName)
    msgFmt = getattr(
        CampaignGlobals, 'STREET_CLEAR_REWARD_MSG_FMT',
        '%s  +%s jellybeans  +%s laff')
    try:
        whisper = msgFmt % (trophy, beans, laff)
    except Exception:
        whisper = '%s  +%s jellybeans  +%s laff' % (trophy, beans, laff)
    handoffFmt = getattr(
        CampaignGlobals, 'STREET_CLEAR_REWARD_HANDOFF_FMT',
        'Street Trophy  +%s beans  +%s laff')
    try:
        handoff = handoffFmt % (beans, laff)
    except Exception:
        handoff = 'Street Trophy  +%s beans  +%s laff' % (beans, laff)
    return {
        'enabled': streetClearRewardEnabled(),
        'jellybeans': beans,
        'laff': laff,
        'trophy': trophy,
        'whisper': whisper,
        'handoff': handoff,
        'zoneId': None if zoneId is None else int(zoneId),
        'reclaimCount': max(1, int(reclaimCount or 1)),
    }


def awardStreetClearReward(toon, reclaimCount=1, zoneId=None, streetName=None):
    """Grant jellybeans + laff toon-up and whisper trophy copy.

    Returns the reward payload dict, or None when disabled / no toon.
    Tolerates missing addMoney / toonUp (headless stubs still get payload).
    """
    if toon is None or not streetClearRewardEnabled():
        return None
    payload = streetClearRewardPayload(
        reclaimCount=reclaimCount, zoneId=zoneId, streetName=streetName)
    beans = int(payload['jellybeans'])
    laff = int(payload['laff'])
    if beans > 0:
        try:
            if hasattr(toon, 'addMoney'):
                toon.addMoney(beans)
        except Exception:
            pass
    if laff > 0:
        try:
            if hasattr(toon, 'toonUp'):
                toon.toonUp(laff)
        except Exception:
            pass
    whisper = payload.get('whisper') or ''
    if whisper:
        try:
            if hasattr(toon, 'd_setSystemMessage'):
                toon.d_setSystemMessage(0, str(whisper)[:200])
            elif hasattr(toon, 'setSystemMessage'):
                toon.setSystemMessage(0, str(whisper)[:200])
        except Exception:
            pass
    emitStreetClearReward(
        zoneId=payload.get('zoneId') or 0,
        beans=beans,
        laff=laff,
        trophy=payload.get('trophy') or '',
        # AI process — skip client ensure imports.
        ensureClients=False)
    return payload
