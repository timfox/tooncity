from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task import Task

from toontown.corruption import CorruptionGlobals


class PollutionManagerAI(DistributedObjectAI):
    """AI authority for per-zone pollution scalars (0 pure .. 1 polluted).

    Incomplete reclaim leaves a street *contested*: residual ink slowly
    re-creeps toward POLLUTION_RECREEP_CAP so neighborhoods fight back.
    Fully reclaimed streets are *purity-locked* (STREET_SECURED + lock set):
    re-creep and pollution rises cannot undo a finished reclaim. Active
    reclaim pauses re-creep via STREET_RECLAIMING and clears the lock so
    seed pollution can land. Ambient never-stained SECURED zones are not
    locked until they hit pure / markStreetSecured.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('PollutionManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        # zoneId -> float in [0, 1]
        self.zonePollution = {}
        # zoneId -> STREET_SECURED / STREET_RECLAIMING / STREET_CONTESTED
        self.streetStatus = {}
        # Finished-reclaim zones — refuse pollution rises until reclaiming.
        self._purityLocked = set()
        # Zones that already got the rubber-hose re-creep whisper this episode.
        self._recreepAnnounced = set()
        self._recreepTaskName = None

    def getPollution(self, zoneId):
        return self.zonePollution.get(zoneId, CorruptionGlobals.POLLUTION_DEFAULT)

    def getStreetStatus(self, zoneId):
        """Return STREET_* bookkeeping for a zone (default secured)."""
        return self.streetStatus.get(
            int(zoneId), CorruptionGlobals.STREET_SECURED)

    def isPurityLocked(self, zoneId):
        """True after a finished reclaim until reclaiming / contested clears it."""
        return int(zoneId) in self._purityLocked

    def setPollution(self, zoneId, level):
        """Set absolute pollution for a zone and broadcast to interested clients."""
        zoneId = int(zoneId)
        clamped = CorruptionGlobals.clampPollution(level)
        previous = self.getPollution(zoneId)
        # Finished reclaim lock — refuse re-stain (re-creep / ~pollute rises).
        if CorruptionGlobals.streetPurityLockBlocksRise(
                self.isPurityLocked(zoneId), clamped, previous):
            self.notify.debug(
                'zone %s purity-locked; refuse pollution rise %.3f -> %.3f' % (
                    zoneId, previous, clamped))
            return previous
        self.zonePollution[zoneId] = clamped
        self.d_setZonePollution(zoneId, clamped)
        if clamped != previous:
            self.notify.debug(
                'zone %s pollution %.3f -> %.3f' % (zoneId, previous, clamped))
        if clamped <= CorruptionGlobals.POLLUTION_PURE and previous > CorruptionGlobals.POLLUTION_PURE:
            # Hook for slice 3 reclaim / purity restore FX.
            messenger.send('pollutionReclaimed', [zoneId])
            # Pure streets stay pure — lock out auto re-ink + rises.
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
        """Full reclaim / pure street — purity-lock; no auto re-ink or rises."""
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = CorruptionGlobals.STREET_SECURED
        self._purityLocked.add(zoneId)
        self._recreepAnnounced.discard(zoneId)
        # Force pure while locked so a finished reclaim cannot keep residual ink.
        if self.getPollution(zoneId) > CorruptionGlobals.POLLUTION_PURE:
            self.zonePollution[zoneId] = CorruptionGlobals.POLLUTION_PURE
            self.d_setZonePollution(zoneId, CorruptionGlobals.POLLUTION_PURE)
        self._refreshRecreepTask()
        self.notify.debug(
            'zone %s street secured + purity-locked (no re-creep)' % zoneId)

    def markStreetReclaiming(self, zoneId):
        """Active reclaim packs — pause re-creep; clear lock so seed can land."""
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = CorruptionGlobals.STREET_RECLAIMING
        self._purityLocked.discard(zoneId)
        self._recreepAnnounced.discard(zoneId)
        self._refreshRecreepTask()
        self.notify.debug('zone %s street reclaiming (re-creep paused)' % zoneId)

    def markStreetContested(self, zoneId):
        """Incomplete reclaim bail-out — residual ink may slowly re-creep."""
        zoneId = int(zoneId)
        self.streetStatus[zoneId] = CorruptionGlobals.STREET_CONTESTED
        self._purityLocked.discard(zoneId)
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
        for zoneId, status in list(self.streetStatus.items()):
            # Secured / reclaiming / purity-locked never re-ink; contested only.
            if not CorruptionGlobals.streetAllowsRecreep(status):
                continue
            if self.isPurityLocked(zoneId):
                continue
            anyContested = True
            level = self.getPollution(zoneId)
            # Pure streets stay pure — even a contested flag won't stain zero.
            if level <= CorruptionGlobals.POLLUTION_PURE:
                continue
            nxt = CorruptionGlobals.pollutionRecreepStep(level)
            if nxt <= level:
                continue
            applied = self.setPollution(zoneId, nxt)
            # Lock / no-op rise — skip whisper.
            if applied <= level:
                continue
            if zoneId not in self._recreepAnnounced:
                self._recreepAnnounced.add(zoneId)
                self._announceRecreep(zoneId)
                messenger.send('pollutionRecreeping', [zoneId, applied])  # noqa: F821

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
        self._purityLocked.clear()
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

    def applyBetrayalHubStain(self, zoneId, level):
        """Author hub pollution after Oswald betrayal (no recreep contested).

        Clears purity lock so a previously sunny HQ can take the stain.
        Status stays SECURED (not CONTESTED) — hub stain is campaign-
        authored, not incomplete-reclaim re-ink.
        """
        zoneId = int(zoneId)
        self._purityLocked.discard(zoneId)
        self.streetStatus[zoneId] = CorruptionGlobals.STREET_SECURED
        self._recreepAnnounced.discard(zoneId)
        self._refreshRecreepTask()
        applied = self.setPollution(zoneId, level)
        self.notify.debug(
            'betrayal hub stain zone %s -> %.3f' % (zoneId, applied))
        return applied

    def clearBetrayalHubStain(self, zoneId):
        """Wash hub stain after chase clear / replay wipe."""
        zoneId = int(zoneId)
        applied = self.setPollution(
            zoneId, CorruptionGlobals.POLLUTION_PURE)
        # setPollution → pure already markStreetSecured; ensure lock.
        if not self.isPurityLocked(zoneId):
            self.markStreetSecured(zoneId)
        self.notify.debug(
            'betrayal hub stain cleared zone %s' % zoneId)
        return applied

    def requestCampaignProgress(self):
        """Client login ask: hydrate + push victory / unlock / chase / reclaimCount."""
        avId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(avId)
        if toon is None:
            return
        self.pushCampaignProgressToAvatar(toon, hydrate=True)

    def pushCampaignProgressToAvatar(self, toon, hydrate=False):
        """Thin per-avatar status push for PlayEntry / OswaldPresence / power.

        Hydrate reads CampaignProgressSave so relog clients see AI-persisted
        STATE_VICTORY / unlockedThrough / chaseCleared / reclaimCount without
        pressing C/R. reclaimCount rehydrates CampaignPower melee bump.
        """
        if toon is None:
            return False
        avId = getattr(toon, 'doId', None)
        if avId is None:
            return False
        unlocked = 0
        state = 0
        chaseCleared = 0
        reclaimCount = 0
        try:
            from toontown.campaign import CampaignProgressSave
            from toontown.campaign.CampaignDirectorAI import getCampaignDirector
            campaign = getCampaignDirector(self.air)
            if hydrate and hasattr(campaign, '_hydrateFromToon'):
                # Loads JSON on first ask / avatar switch; same-toon keep
                # live session (persist already flushed key beats).
                campaign._hydrateFromToon(toon)
            blob = CampaignProgressSave.snapshotFromDirector(campaign)
            unlocked = int(blob.get('unlockedThrough', 0) or 0)
            state = int(blob.get('state', 0) or 0)
            chaseCleared = int(blob.get('chaseCleared', 0) or 0)
            # uint8 DC field — clamp; power bump already caps at POWER_BUMP_MAX.
            reclaimCount = max(0, min(255, int(blob.get('reclaimCount', 0) or 0)))
        except Exception:
            self.notify.warning('pushCampaignProgressToAvatar failed')
            return False
        try:
            self.sendUpdateToAvatarId(
                int(avId),
                'setCampaignProgress',
                [unlocked, state, chaseCleared, reclaimCount])
        except Exception:
            self.notify.debug('setCampaignProgress send failed av=%s' % avId)
            return False
        return True

    def pushCampaignVictoryToAvatar(self, toon, reclaimCount=0):
        """Relay finale campaignVictory to a real client (not AI-local only).

        CampaignDirectorAI still messenger.sends for same-process listeners;
        this DC announce lands PlayEntry / OswaldPresence / chase tip /
        FinalePhaseFx / Handoff accepts on the owning avatar's client.
        """
        if toon is None:
            return False
        avId = getattr(toon, 'doId', None)
        if avId is None:
            return False
        count = max(0, min(255, int(reclaimCount or 0)))
        try:
            self.sendUpdateToAvatarId(
                int(avId),
                'announceCampaignVictory',
                [count])
        except Exception:
            self.notify.debug(
                'announceCampaignVictory send failed av=%s' % avId)
            return False
        return True

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
            # STREET_PACKS R path — soft-gate Punchline/Silly behind act
            # unlock (Loopy stays open). Prefer campaign when live on this
            # street. Logic lives on DistributedReclaimDirectorAI.
            try:
                from toontown.reclaim.DistributedReclaimDirectorAI import (
                    DistributedReclaimDirectorAI)
                msg = DistributedReclaimDirectorAI.startStreetPackForToon(
                    self.air, toon, force=False)
            except Exception:
                self.notify.warning('requestStreetEvent reclaim failed')
                return
        try:
            if hasattr(toon, 'd_setSystemMessage'):
                toon.d_setSystemMessage(0, str(msg)[:200])
        except Exception:
            pass
