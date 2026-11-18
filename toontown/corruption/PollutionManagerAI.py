from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task import Task

from toontown.corruption import CorruptionGlobals


class PollutionManagerAI(DistributedObjectAI):
    """AI authority for per-zone pollution scalars (0 pure .. 1 polluted).

    Incomplete reclaim leaves a street *contested*: residual ink slowly
    re-creeps toward POLLUTION_RECREEP_CAP so neighborhoods fight back.
    Fully reclaimed / pure streets stay *secured* (no auto re-ink). Active
    reclaim pauses re-creep via STREET_RECLAIMING.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('PollutionManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        # zoneId -> float in [0, 1]
        self.zonePollution = {}
        # zoneId -> STREET_SECURED / STREET_RECLAIMING / STREET_CONTESTED
        self.streetStatus = {}
        # Zones that already got the rubber-hose re-creep whisper this episode.
        self._recreepAnnounced = set()
        self._recreepTaskName = None

    def getPollution(self, zoneId):
        return self.zonePollution.get(zoneId, CorruptionGlobals.POLLUTION_DEFAULT)

    def getStreetStatus(self, zoneId):
        """Return STREET_* bookkeeping for a zone (default secured)."""
        return self.streetStatus.get(
            int(zoneId), CorruptionGlobals.STREET_SECURED)

    def setPollution(self, zoneId, level):
        """Set absolute pollution for a zone and broadcast to interested clients."""
        zoneId = int(zoneId)
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
            # Pure streets stay pure — lock out auto re-ink.
            self.markStreetSecured(zoneId)
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

    def markStreetSecured(self, zoneId):
        """Full reclaim / pure street — no auto re-ink."""
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = CorruptionGlobals.STREET_SECURED
        self._recreepAnnounced.discard(zoneId)
        self._refreshRecreepTask()
        self.notify.debug('zone %s street secured (no re-creep)' % zoneId)

    def markStreetReclaiming(self, zoneId):
        """Active reclaim packs — pause re-creep while the fight is on."""
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = CorruptionGlobals.STREET_RECLAIMING
        self._recreepAnnounced.discard(zoneId)
        self._refreshRecreepTask()
        self.notify.debug('zone %s street reclaiming (re-creep paused)' % zoneId)

    def markStreetContested(self, zoneId):
        """Incomplete reclaim bail-out — residual ink may slowly re-creep."""
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = CorruptionGlobals.STREET_CONTESTED
        self._recreepAnnounced.discard(zoneId)
        self._refreshRecreepTask()
        self.notify.debug(
            'zone %s street contested (re-creep armed, pollution %.3f)' % (
                zoneId, self.getPollution(zoneId)))

    def _anyContestedStreet(self):
        contested = CorruptionGlobals.STREET_CONTESTED
        for status in self.streetStatus.values():
            if status == contested:
                return True
        return False

    def _refreshRecreepTask(self):
        """Start or stop the slow re-ink tick from current street statuses."""
        want = (
            CorruptionGlobals.POLLUTION_RECREEP_ENABLED
            and self._anyContestedStreet())
        if want:
            self._ensureRecreepTask()
        else:
            self._stopRecreepTask()

    def _ensureRecreepTask(self):
        if self._recreepTaskName is not None:
            return
        self._recreepTaskName = self.uniqueName('pollution-recreep')
        taskMgr.doMethodLater(  # noqa: F821
            float(CorruptionGlobals.POLLUTION_RECREEP_TICK_SEC),
            self.__recreepTick,
            self._recreepTaskName)

    def _stopRecreepTask(self):
        if self._recreepTaskName is None:
            return
        try:
            taskMgr.remove(self._recreepTaskName)  # noqa: F821
        except Exception:
            pass
        self._recreepTaskName = None

    def __recreepTick(self, task):
        """Slowly re-ink contested streets; pure / secured stay clean."""
        if not CorruptionGlobals.POLLUTION_RECREEP_ENABLED:
            self._recreepTaskName = None
            return Task.done

        anyContested = False
        contested = CorruptionGlobals.STREET_CONTESTED
        for zoneId, status in list(self.streetStatus.items()):
            if status != contested:
                continue
            anyContested = True
            level = self.getPollution(zoneId)
            # Pure streets stay pure — even a contested flag won't stain zero.
            if level <= CorruptionGlobals.POLLUTION_PURE:
                continue
            nxt = CorruptionGlobals.pollutionRecreepStep(level)
            if nxt <= level:
                continue
            self.setPollution(zoneId, nxt)
            # Avoid markStreetSecured side-effects if somehow capped at pure.
            if zoneId not in self._recreepAnnounced:
                self._recreepAnnounced.add(zoneId)
                self._announceRecreep(zoneId)
                messenger.send('pollutionRecreeping', [zoneId, nxt])  # noqa: F821

        if not anyContested:
            self._recreepTaskName = None
            return Task.done
        return Task.again

    def _announceRecreep(self, zoneId):
        """Best-effort rubber-hose whisper to toons still on the street."""
        msg = str(CorruptionGlobals.POLLUTION_RECREEP_MSG)[:200]
        try:
            for do in list(self.air.doId2do.values()):
                if getattr(do, 'zoneId', None) != zoneId:
                    continue
                if hasattr(do, 'd_setSystemMessage'):
                    do.d_setSystemMessage(0, msg)
        except Exception:
            self.notify.debug('re-creep whisper skipped for zone %s' % zoneId)

    def delete(self):
        self._stopRecreepTask()
        self.streetStatus.clear()
        self._recreepAnnounced.clear()
        DistributedObjectAI.delete(self)

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
            # Prefer campaign attach when a campaign act is already live for
            # this street — stops street-pack R from racing past C unlocks.
            try:
                from toontown.campaign import CampaignGlobals
                from toontown.campaign.CampaignDirectorAI import (
                    getCampaignDirector)
                zoneId = int(toon.zoneId)
                campaign = getCampaignDirector(self.air)
                if campaign.state == CampaignGlobals.STATE_ACTIVE:
                    act = CampaignGlobals.ACTS[campaign.actIndex]
                    if zoneId == int(act['zoneId']):
                        msg = campaign.startCampaign(toon)
                        try:
                            if hasattr(toon, 'd_setSystemMessage'):
                                toon.d_setSystemMessage(0, str(msg)[:200])
                        except Exception:
                            pass
                        return
            except Exception:
                self.notify.warning(
                    'requestStreetEvent campaign-prefer check failed')
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
                # Hood street packs (Loopy / Punchline / Silly) deepen auto / R.
                packKwargs = ReclaimGlobals.streetPackParams(zoneId)
                director.start(
                    zoneId,
                    (toon.getX(), toon.getY(), toon.getZ()),
                    toon.getH(),
                    **packKwargs)
                packId = ReclaimGlobals.streetPackId(zoneId)
                if packId:
                    msg = 'Reclaim started (%s)' % packId
                else:
                    msg = 'Reclaim packs inbound — press F to fight!'
            except Exception:
                self.notify.warning('requestStreetEvent reclaim failed')
                return
        try:
            if hasattr(toon, 'd_setSystemMessage'):
                toon.d_setSystemMessage(0, str(msg)[:200])
        except Exception:
            pass
