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
