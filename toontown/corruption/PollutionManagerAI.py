from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.corruption import CorruptionGlobals


class PollutionManagerAI(DistributedObjectAI):
    """AI authority for per-zone pollution scalars (0 pure .. 1 polluted)."""

    notify = DirectNotifyGlobal.directNotify.newCategory('PollutionManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        # zoneId -> float in [0, 1]
        self.zonePollution = {}

    def getPollution(self, zoneId):
        return self.zonePollution.get(zoneId, CorruptionGlobals.POLLUTION_DEFAULT)

    def setPollution(self, zoneId, level):
        """Set absolute pollution for a zone and broadcast to interested clients."""
        clamped = CorruptionGlobals.clampPollution(level)
        previous = self.getPollution(zoneId)
        self.zonePollution[zoneId] = clamped
        self.d_setZonePollution(zoneId, clamped)
        if clamped != previous:
            self.notify.debug(
                'zone %s pollution %.3f -> %.3f' % (zoneId, previous, clamped))
        if clamped <= CorruptionGlobals.POLLUTION_PURE and previous > CorruptionGlobals.POLLUTION_PURE:
            # Hook for slice 3 reclaim / purity restore FX.
            messenger.send('pollutionReclaimed', [zoneId])
        return clamped

    def adjustPollution(self, zoneId, delta):
        """Add delta (negative to purify) and return the new level."""
        return self.setPollution(zoneId, self.getPollution(zoneId) + float(delta))

    def d_setZonePollution(self, zoneId, level):
        self.sendUpdate('setZonePollution', [
            zoneId, CorruptionGlobals.pollutionToNet(level)])

    def requestZonePollution(self, zoneId):
        """Client ask: mirror current value for one zone."""
        self.sendUpdateToAvatarId(
            self.air.getAvatarIdFromSender(),
            'setZonePollution',
            [zoneId, CorruptionGlobals.pollutionToNet(self.getPollution(zoneId))])

    def onCorruptToonDefeated(self, zoneId, amount=None):
        """Reclaim hook: defeating a corrupt toon lowers local pollution."""
        if amount is None:
            amount = CorruptionGlobals.POLLUTION_PER_DEFEAT
        return self.adjustPollution(zoneId, -abs(float(amount)))

    def requestHackSlashIFrame(self, durationMs):
        """Client dodge/hit i-frame window — CorruptToonAI skips takeDamage while active."""
        avId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(avId)
        if toon is None:
            return
        # Cap so a buggy client can't stay invuln forever.
        durationMs = max(0, min(900, int(durationMs)))
        if durationMs <= 0:
            toon.hackSlashIFrameUntil = 0.0
            return
        toon.hackSlashIFrameUntil = (
            globalClock.getFrameTime() + (durationMs / 1000.0))  # noqa: F821

    def requestStreetEvent(self, eventType):
        """Player-facing entry: start reclaim (0) or campaign act (1) in sender zone."""
        avId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(avId)
        if toon is None:
            return
        eventType = int(eventType)
        if eventType == 1:
            try:
                from toontown.campaign.CampaignDirectorAI import getCampaignDirector
                msg = getCampaignDirector(self.air).startCampaign(toon)
            except Exception:
                self.notify.warning('requestStreetEvent campaign failed')
                return
        else:
            try:
                from toontown.reclaim import ReclaimGlobals
                from toontown.reclaim.DistributedReclaimDirectorAI import (
                    DistributedReclaimDirectorAI)
                zoneId = int(toon.zoneId)
                directors = getattr(self.air, 'reclaimDirectors', None)
                if directors is None:
                    directors = {}
                    self.air.reclaimDirectors = directors
                existing = directors.get(zoneId)
                if existing is not None and not existing.isDeleted():
                    if existing.state == ReclaimGlobals.STATE_ACTIVE:
                        return
                    existing.requestDelete()
                    directors.pop(zoneId, None)
                director = DistributedReclaimDirectorAI(self.air, zoneId=zoneId)
                director.generateWithRequired(zoneId)
                directors[zoneId] = director
                director.start(
                    zoneId,
                    (toon.getX(), toon.getY(), toon.getZ()),
                    toon.getH())
                msg = 'Reclaim started in zone %s' % zoneId
            except Exception:
                self.notify.warning('requestStreetEvent reclaim failed')
                return
        try:
            if hasattr(toon, 'd_setSystemMessage'):
                toon.d_setSystemMessage(0, str(msg)[:200])
        except Exception:
            pass
