from panda3d.core import CardMaker, TextNode, TransparencyAttrib, Vec4

from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import (
    Func, LerpColorScaleInterval, LerpScaleInterval, Parallel, Sequence, Wait)

from toontown.campaign import CampaignGlobals
from toontown.corruption import CorruptionGlobals
from toontown.reclaim import ReclaimGlobals
from toontown.reclaim.PurityMeterHud import PurityMeterHud
from toontown.reclaim.StreetColorWash import StreetColorWash


class DistributedReclaimDirector(DistributedObject.DistributedObject):
    """Client reclaim feedback: status HUD, wave banners, purity restore FX.

    Mid-wave purity pressure: short rubber-hose tip whisper + meter rim warn
    when purity stalls or ink rises while packs are still alive (contested
    feel after incomplete re-creep #194). Full clear confirms the secured
    purity lock with a short tip + meter rim so re-creep cannot undo it.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedReclaimDirector')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.state = ReclaimGlobals.STATE_IDLE
        self.reclaimZoneId = 0
        self.pollutionHint = CorruptionGlobals.POLLUTION_PURE
        self.waveIndex = 0
        self.maxWaves = ReclaimGlobals.MAX_PACKS
        self.packAlive = 0
        self.finalePhase = 0
        self._bannerNP = None
        self._subBannerNP = None
        self._telegraphCueNP = None
        self._hintNP = None
        self._statusNP = None
        self._demoHintNP = None
        self._pressureTipNP = None
        self._securedTipNP = None
        self._purityMeter = PurityMeterHud()
        self._streetWash = StreetColorWash()
        self._restoreIval = None
        self._burstFlashNP = None
        self._burstRingNP = None
        self._puritySfx = None
        self._pressureLastPurity = None
        self._pressureLastAdvanceT = None
        self._pressureLastPollution = None
        self._pressureCooldownUntil = 0.0
        self._pressureTaskName = None

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        base.cr.reclaimDirector = self
        self.accept('pollutionChanged', self.__onPollutionChanged)
        # Overlord wind-up cue (P1 magenta vs P2 crimson) from CorruptToon AV.
        self.accept('finaleTelegraphCue', self.__onFinaleTelegraphCue)
        # Polluted STREET_PACK enter cream shimmer + soft wash pulse
        # (wash client also owns delayed cream aftershock + settle cream wash;
        # also via ReclaimCheer).
        try:
            from toontown.reclaim.EntryCreamShimmerFx import (
                ensureEntryCreamShimmerFxClient)
            ensureEntryCreamShimmerFxClient()
        except Exception:
            pass
        try:
            from toontown.reclaim.EntryCreamWashPulseFx import (
                ensureEntryCreamWashPulseFxClient)
            ensureEntryCreamWashPulseFxClient()
        except Exception:
            pass

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        # zoneId is assigned by the interest system once we are in the street.
        self.reclaimZoneId = getattr(self, 'zoneId', 0)

    def disable(self):
        self.ignoreAll()
        self.__stopPressureWatch()
        self.__cancelSecuredHudHold()
        self.__clearHud()
        if self._restoreIval is not None:
            self._restoreIval.finish()
            self._restoreIval = None
        self.__clearPurityBurstOverlay()
        self._puritySfx = None
        if self._purityMeter is not None:
            self._purityMeter.destroy()
        if self._streetWash is not None:
            self._streetWash.destroy()
        if getattr(base.cr, 'reclaimDirector', None) is self:
            del base.cr.reclaimDirector
        DistributedObject.DistributedObject.disable(self)

    def setState(self, state):
        self.state = int(state)
        zoneId = self.reclaimZoneId or getattr(self, 'zoneId', 0)
        if self.state == ReclaimGlobals.STATE_IDLE:
            self.__stopPressureWatch()
            self.__cancelSecuredHudHold()
            if self._streetWash is not None:
                self._streetWash.setActive(False, zoneId=zoneId)
            self.__clearHud()
        elif self.state == ReclaimGlobals.STATE_ACTIVE:
            if self._streetWash is not None:
                self._streetWash.setActive(True, zoneId=zoneId)
                self._streetWash.update(zoneId, self.pollutionHint, snap=True)
            self.__armPurityPressure()
            self.__showStatusHud()
        elif self.state == ReclaimGlobals.STATE_COMPLETE:
            self.__stopPressureWatch()
            # Purity burst owns the payoff; wash soft-clears via messengers.
            if self._streetWash is not None:
                self._streetWash.setActive(False, zoneId=zoneId)

    def setPollutionHint(self, netLevel):
        self.pollutionHint = CorruptionGlobals.pollutionFromNet(netLevel)
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__showStatusHud()

    def setWaveIndex(self, waveIndex):
        self.waveIndex = int(waveIndex)
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__showStatusHud()

    def setMaxWaves(self, maxWaves):
        self.maxWaves = max(1, int(maxWaves))
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__showStatusHud()

    def setPackAlive(self, count):
        self.packAlive = max(0, int(count))
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__showStatusHud()

    def setFinalePhase(self, phase):
        self.finalePhase = max(0, int(phase))
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__showStatusHud()

    def announceReclaimStart(self):
        zoneId = self.reclaimZoneId or getattr(self, 'zoneId', 0)
        if self.finalePhase >= 1:
            title = CampaignGlobals.FINALE_PHASE_BANNER.get(
                self.finalePhase, ReclaimGlobals.BANNER_START)
            sub = CampaignGlobals.FINALE_PHASE_SUB.get(self.finalePhase, '')
            color = (
                (1.0, 0.45, 0.95, 1.0) if self.finalePhase < 2
                else (1.0, 0.28, 0.22, 1.0))
            self.__showBanner(title, color, hold=2.8)
            if sub:
                self.__showSubBanner(sub, color, hold=2.8)
        else:
            # STREET_PACK start plate (Loopy ink / Punchline sludge / Silly).
            title = ReclaimGlobals.streetBannerStart(
                zoneId, finalePhase=self.finalePhase)
            color = ReclaimGlobals.streetBannerStartColor(
                zoneId, finalePhase=self.finalePhase)
            self.__showBanner(title, color, hold=2.8)
            sub = ReclaimGlobals.streetBannerStartSub(
                zoneId, finalePhase=self.finalePhase)
            if sub:
                self.__showSubBanner(sub, color, hold=2.8)
        # Discoverable play: arm melee without demo dummies when reclaim goes live.
        av = getattr(base, 'localAvatar', None)
        if av is not None and hasattr(av, 'enableHackSlashMelee'):
            try:
                av.enableHackSlashMelee(spawnHostiles=False)
            except Exception:
                pass
        if self.finalePhase >= 1:
            try:
                from toontown.campaign.FinalePhaseFx import ensureFinalePhaseFxClient
                ensureFinalePhaseFxClient()
            except Exception:
                pass
        messenger.send('announceReclaimStart', [])
        messenger.send('reclaimFinalePhase', [self.finalePhase])
        if self._streetWash is not None:
            self._streetWash.setActive(True, zoneId=zoneId)
            self._streetWash.update(zoneId, self.pollutionHint, snap=True)
        self.__armPurityPressure()
        self.__showDemoHint()
        self.__showStatusHud()

    def announceFinalePhaseTransition(self, phaseIndex):
        """Boss flip sting — FOV / flash / ink slam via FinalePhaseFx."""
        phase = max(1, int(phaseIndex))
        self.finalePhase = phase
        try:
            from toontown.campaign.FinalePhaseFx import ensureFinalePhaseFxClient
            ensureFinalePhaseFxClient()
        except Exception:
            pass
        messenger.send('finalePhaseTransition', [phase])
        title = CampaignGlobals.FINALE_PHASE_BANNER.get(
            phase, 'FINALE PHASE %s' % phase)
        color = (1.0, 0.22, 0.28, 1.0)
        self.__showBanner(title, color, hold=3.2)
        self.__showSubBanner(
            CampaignGlobals.FINALE_PHASE_SUB.get(
                phase, 'Phase transition!'),
            color,
            hold=3.2)
        # Banner-only campaignPhase (sting already fired above).
        messenger.send('campaignPhase', [max(0, phase - 1), title])

    def announcePackSpawn(self, count, waveIndex=1):
        """Short rubber-hose wave plate when a reclaim pack wave starts."""
        wave = max(1, int(waveIndex))
        zoneId = self.reclaimZoneId or getattr(self, 'zoneId', 0)
        hold = getattr(ReclaimGlobals, 'WAVE_ANNOUNCE_HOLD_SEC', 2.35)
        title = ReclaimGlobals.waveAnnounceTitle(
            wave, self.maxWaves, zoneId=zoneId, finalePhase=self.finalePhase)
        if self.finalePhase >= 1:
            # Boss streets keep Overlord flavor on the Oswald tip line.
            color = (
                (1.0, 0.5, 0.95, 1.0) if self.finalePhase < 2
                else (1.0, 0.35, 0.25, 1.0))
            tip = ReclaimGlobals.FINALE_PACK_BANNER.get(
                self.finalePhase,
                ReclaimGlobals.waveOswaldTip(
                    wave, self.maxWaves, zoneId=zoneId, packCount=count))
            if int(count) > 0:
                tip = '%s  ·  pack of %s' % (tip, int(count))
            self.__showBanner(title, color, hold=hold, pop=True)
            self.__showSubBanner(tip, color, hold=hold)
        else:
            mainColor, subColor = ReclaimGlobals.waveAnnounceColors(zoneId)
            tip = ReclaimGlobals.waveOswaldTip(
                wave, self.maxWaves, zoneId=zoneId, packCount=count)
            self.__showBanner(title, mainColor, hold=hold, pop=True)
            self.__showSubBanner(tip, subColor, hold=hold)
        # Cream edge pulse frames the announce plate (WaveCreamBurstFx).
        try:
            from toontown.reclaim.WaveCreamBurstFx import (
                ensureWaveCreamBurstFxClient)
            ensureWaveCreamBurstFxClient()
        except Exception:
            pass
        messenger.send(
            'reclaimWaveAnnounce', [self.reclaimZoneId, wave])
        # Fresh mid-wave beat — reset stall clock so announce plate isn't
        # immediately followed by a pressure whisper.
        self.__armPurityPressure(resetStall=True)
        self.__showStatusHud()

    def announceWaveCleared(self, waveIndex):
        # Light banner pop + cheer pitch swell + cream burst between packs.
        hold = float(getattr(ReclaimGlobals, 'WAVE_CLEAR_BANNER_HOLD_SEC', 1.4))
        bannerColor = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_BANNER_COLOR', (1.0, 0.94, 0.62, 1.0))
        subColor = getattr(
            ReclaimGlobals, 'WAVE_CLEAR_SUB_BANNER_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        self.__showBanner(
            ReclaimGlobals.BANNER_WAVE_CLEARED,
            bannerColor,
            hold=hold, pop=True)
        zoneId = self.reclaimZoneId or getattr(self, 'zoneId', 0)
        self.__showSubBanner(
            ReclaimGlobals.waveClearedOswaldTip(waveIndex, zoneId=zoneId),
            subColor,
            hold=hold)
        try:
            from toontown.reclaim.ReclaimCheer import ensureReclaimCheerClient
            ensureReclaimCheerClient()
        except Exception:
            pass
        try:
            from toontown.reclaim.WaveCreamBurstFx import (
                ensureWaveCreamBurstFxClient)
            ensureWaveCreamBurstFxClient()
        except Exception:
            pass
        # Cream shimmer hang + aftershock + wash + sparkle after wave-clear burst.
        try:
            from toontown.reclaim.WaveClearCreamShimmerFx import (
                ensureWaveClearCreamShimmerFxClient)
            ensureWaveClearCreamShimmerFxClient()
        except Exception:
            pass
        messenger.send(
            'reclaimWaveCleared', [self.reclaimZoneId, int(waveIndex)])

    def announceReclaimComplete(self):
        self.__hideTelegraphCue()
        self.__stopPressureWatch()
        zoneId = self.reclaimZoneId or getattr(self, 'zoneId', 0)
        completeTitle = ReclaimGlobals.streetBannerComplete(
            zoneId, finalePhase=self.finalePhase)
        completeColor = (0.55, 1.0, 0.7, 1.0)
        if ReclaimGlobals.streetPackId(zoneId) == 'punchline-sludge':
            completeColor = (0.72, 0.92, 0.55, 1.0)
        self.__showBanner(
            completeTitle, completeColor,
            hold=3.4, pop=True)
        # Finale P2 clear: purity cheer + soft Oswald-twist tease (copy only).
        if self.finalePhase >= 2:
            self.__showSubBanner(
                CampaignGlobals.FINALE_TWIST_TEASE,
                CampaignGlobals.FINALE_TWIST_TEASE_COLOR,
                hold=3.8)
            # Readable AV reveal sting (banner + FOV/flash/SFX) via FinalePhaseFx.
            # Delayed inside the client so purity cheer lands first.
            try:
                from toontown.campaign.FinalePhaseFx import ensureFinalePhaseFxClient
                ensureFinalePhaseFxClient()
            except Exception:
                pass
            messenger.send('oswaldRevealSting', [0])
        else:
            self.__showSubBanner(
                ReclaimGlobals.streetBannerCompleteSub(
                    zoneId, finalePhase=self.finalePhase),
                (0.85, 1.0, 0.9, 1.0),
                hold=3.4)
        # Secured purity-lock tip + meter rim before tearing down the HUD.
        self.__confirmSecuredLock(zoneId)
        self.__playRestoreFx()
        self.__hideDemoHint()

    def __onPollutionChanged(self, zoneId, level):
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return
        if hasattr(base, 'localAvatar') and getattr(base.localAvatar, 'zoneId', None) == zoneId:
            self.pollutionHint = level
            if self._streetWash is not None:
                self._streetWash.update(zoneId, level)
            self.__showStatusHud()
            self.__evaluatePurityPressure()

    def __showBanner(self, text, color, hold=2.2, pop=False):
        self.__hideBanner()
        tn = TextNode('reclaim-banner')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(*color)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0, 0, 0, 0.75)
        np = aspect2d.attachNewNode(tn)
        baseScale = 0.09
        np.setScale(baseScale)
        np.setPos(0, 0, 0.78)
        self._bannerNP = np
        if pop:
            # Soft rubber-hose scale punch (wave announce + purity payoff).
            popScale = getattr(
                ReclaimGlobals, 'WAVE_BANNER_POP_SCALE_ANNOUNCE',
                ReclaimGlobals.PURITY_BANNER_POP_SCALE)
            popSec = getattr(
                ReclaimGlobals, 'WAVE_BANNER_POP_SEC_ANNOUNCE',
                ReclaimGlobals.PURITY_BANNER_POP_SEC)
            # Purity complete keeps the bigger pop when hold is long.
            if hold >= 3.0:
                popScale = ReclaimGlobals.PURITY_BANNER_POP_SCALE
                popSec = ReclaimGlobals.PURITY_BANNER_POP_SEC
            Sequence(
                LerpScaleInterval(np, popSec, popScale),
                LerpScaleInterval(np, 0.22, baseScale),
            ).start()
        taskMgr.doMethodLater(
            hold, self.__bannerTimeout, self.uniqueName('reclaim-banner'))

    def __bannerTimeout(self, task):
        self.__hideBanner()
        return task.done

    def __hideBanner(self):
        taskMgr.remove(self.uniqueName('reclaim-banner'))
        if self._bannerNP is not None and not self._bannerNP.isEmpty():
            self._bannerNP.removeNode()
        self._bannerNP = None

    def __showSubBanner(self, text, color, hold=2.0):
        self.__hideSubBanner()
        tn = TextNode('reclaim-sub-banner')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(*color)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.7)
        np = aspect2d.attachNewNode(tn)
        np.setScale(0.045)
        np.setPos(0, 0, 0.70)
        self._subBannerNP = np
        taskMgr.doMethodLater(
            hold, self.__subBannerTimeout, self.uniqueName('reclaim-sub-banner'))

    def __subBannerTimeout(self, task):
        self.__hideSubBanner()
        return task.done

    def __hideSubBanner(self):
        taskMgr.remove(self.uniqueName('reclaim-sub-banner'))
        if self._subBannerNP is not None and not self._subBannerNP.isEmpty():
            self._subBannerNP.removeNode()
        self._subBannerNP = None

    def __finaleStatusColor(self):
        if self.finalePhase >= 2:
            return (1.0, 0.55, 0.45, 1.0)
        if self.finalePhase == 1:
            return (1.0, 0.7, 1.0, 1.0)
        return (0.95, 0.88, 1.0, 1.0)

    def __onFinaleTelegraphCue(self, phaseIndex, cueText, cueColor):
        """Brief phase-colored wind-up chip during Overlord telegraphs."""
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return
        if int(getattr(self, 'finalePhase', 0) or 0) < 1:
            return
        self.__showTelegraphCue(str(cueText), tuple(cueColor), hold=0.85)

    def __showTelegraphCue(self, text, color, hold=0.85):
        self.__hideTelegraphCue()
        tn = TextNode('reclaim-finale-telegraph-cue')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(*color)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0, 0, 0, 0.8)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        np.setScale(0.055)
        np.setPos(0, 0, 0.68)
        self._telegraphCueNP = np
        taskMgr.doMethodLater(  # noqa: F821
            hold, self.__telegraphCueTimeout,
            self.uniqueName('reclaim-finale-telegraph-cue'))

    def __telegraphCueTimeout(self, task):
        self.__hideTelegraphCue()
        return task.done

    def __hideTelegraphCue(self):
        taskMgr.remove(self.uniqueName('reclaim-finale-telegraph-cue'))  # noqa: F821
        if self._telegraphCueNP is not None and not self._telegraphCueNP.isEmpty():
            self._telegraphCueNP.removeNode()
        self._telegraphCueNP = None

    def __showStatusHud(self):
        """Persistent player-facing reclaim status (wave / pack + purity meter)."""
        wave = max(self.waveIndex, 1 if self.state == ReclaimGlobals.STATE_ACTIVE else 0)
        text = ReclaimGlobals.STATUS_FMT % (
            wave,
            self.maxWaves,
            self.pollutionHint * 100.0,
            self.packAlive)
        zoneId = self.reclaimZoneId or getattr(self, 'zoneId', 0)
        if self.finalePhase >= 1:
            phaseLabel = CampaignGlobals.FINALE_PHASE_HUD.get(
                self.finalePhase, 'OVERLORD · P%s' % self.finalePhase)
            text = '%s  |  %s' % (phaseLabel, text)
        else:
            hoodLabel = ReclaimGlobals.streetStatusLabel(
                zoneId, finalePhase=self.finalePhase)
            if hoodLabel:
                text = '%s  |  %s' % (hoodLabel, text)
        statusColor = self.__finaleStatusColor()
        if (self.finalePhase < 1
                and ReclaimGlobals.streetPackId(zoneId) == 'punchline-sludge'):
            statusColor = (0.78, 0.95, 0.62, 1.0)
        if self._statusNP is not None and not self._statusNP.isEmpty():
            node = self._statusNP.node()
            node.setText(text)
            node.setTextColor(*statusColor)
        else:
            tn = TextNode('reclaim-status')
            tn.setText(text)
            tn.setAlign(TextNode.ACenter)
            tn.setTextColor(*statusColor)
            tn.setShadow(0.04, 0.04)
            tn.setShadowColor(0, 0, 0, 0.75)
            np = aspect2d.attachNewNode(tn)  # noqa: F821
            np.setScale(0.042)
            np.setPos(0, 0, 0.62)
            self._statusNP = np

        # Visual pollution→purity bar (replaces the old text-only corruption hint).
        self.__hidePollutionHint()
        if self._purityMeter is not None:
            self._purityMeter.update(
                self.pollutionHint, finalePhase=self.finalePhase)
        # Rubber-hose cream wash on street geom + soft veil as purity fills
        # (StreetColorWash also owns delayed cream aftershock on advances).
        if self._streetWash is not None and self.state == ReclaimGlobals.STATE_ACTIVE:
            self._streetWash.setActive(True, zoneId=zoneId)
            self._streetWash.update(zoneId, self.pollutionHint)
        self.__evaluatePurityPressure()

    def __hidePollutionHint(self):
        if self._hintNP is not None and not self._hintNP.isEmpty():
            self._hintNP.removeNode()
        self._hintNP = None

    def __hideStatusHud(self):
        self.__hideTelegraphCue()
        self.__hidePressureTip()
        self.__hideSecuredLockTip()
        if self._statusNP is not None and not self._statusNP.isEmpty():
            self._statusNP.removeNode()
        self._statusNP = None
        self.__hidePollutionHint()
        if self._purityMeter is not None:
            self._purityMeter.hide()

    def __showDemoHint(self):
        if self._demoHintNP is not None and not self._demoHintNP.isEmpty():
            return
        zoneId = self.reclaimZoneId or getattr(self, 'zoneId', 0)
        tn = TextNode('reclaim-demo-hint')
        tn.setText(ReclaimGlobals.streetDemoHint(
            zoneId, finalePhase=self.finalePhase))
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(1.0, 1.0, 0.8, 1.0)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.7)
        np = aspect2d.attachNewNode(tn)
        np.setScale(0.035)
        np.setPos(0, 0, -0.92)
        self._demoHintNP = np

    def __hideDemoHint(self):
        if self._demoHintNP is not None and not self._demoHintNP.isEmpty():
            self._demoHintNP.removeNode()
        self._demoHintNP = None

    def __playRestoreFx(self):
        """Purity restore moment: HUD burst + sting + brief render bloom.

        Overlay flash/ring stay on aspect2d so hood geom prop tint / fog
        grade (PollutionPropTint / PollutionManager) are never stomped.
        Camera FOV punch + rays/sparks + soft FOV cream wash pulse live in
        PurityBurstFx (messenger). StreetSparkleFx adds horizon cream glitter
        on purityRestoreFx (composes with StreetColorWash soft-clear + wave
        cream burst). PurityCompleteCreamWashFx pulses a StreetColorWash-style
        cream veil under that sparkle and owns a delayed cream aftershock
        (flecks + halo) + settle cream wash. ReclaimCheer + CheerCreamSparkleFx
        layer pitch swell cream flecks + delayed cream aftershock + soft cream
        wash pulse.
        """
        if self._restoreIval is not None:
            self._restoreIval.finish()
        self.__clearPurityBurstOverlay()
        try:
            from toontown.reclaim.PurityBurstFx import ensurePurityBurstFxClient
            ensurePurityBurstFxClient()
        except Exception:
            pass
        try:
            from toontown.reclaim.StreetSparkleFx import (
                ensureStreetSparkleFxClient)
            ensureStreetSparkleFxClient()
        except Exception:
            pass
        try:
            from toontown.reclaim.PurityCompleteCreamWashFx import (
                ensurePurityCompleteCreamWashFxClient)
            ensurePurityCompleteCreamWashFxClient()
        except Exception:
            pass
        # Pitch swell + cream flecks + aftershock + wash (arms CheerCreamSparkleFx).
        try:
            from toontown.reclaim.ReclaimCheer import ensureReclaimCheerClient
            ensureReclaimCheerClient()
        except Exception:
            pass
        messenger.send('purityRestoreFx', [self.reclaimZoneId])
        messenger.send('purityRestoreSting', [self.reclaimZoneId])
        messenger.send('npcCheerStub', [self.reclaimZoneId])
        self.__playPurityStingSfx()
        self.__spawnPurityBurstOverlay()
        # Stronger two-beat wash: bright lift, then warm settle.
        self._restoreIval = Sequence(
            Parallel(
                LerpColorScaleInterval(render, 0.09, Vec4(1.85, 1.9, 1.5, 1.0)),
                Func(messenger.send, 'purityBurstPulse', [self.reclaimZoneId, 1]),
            ),
            LerpColorScaleInterval(render, 0.26, Vec4(1.3, 1.4, 1.12, 1.0)),
            Parallel(
                LerpColorScaleInterval(render, 0.48, Vec4(1.1, 1.18, 1.02, 1.0)),
                Func(messenger.send, 'purityBurstPulse', [self.reclaimZoneId, 2]),
            ),
            Wait(0.35),
            LerpColorScaleInterval(render, 0.7, Vec4(1, 1, 1, 1)),
            Func(render.clearColorScale),
            Func(self.__clearPurityBurstOverlay),
            Func(messenger.send, 'purityRestoreSettled', [self.reclaimZoneId]),
        )
        self._restoreIval.start()

    def __playPurityStingSfx(self):
        """Fire an existing celebration SFX if the asset is present."""
        try:
            if self._puritySfx is None:
                self._puritySfx = base.loader.loadSfx(ReclaimGlobals.PURITY_STING_SFX)
            if self._puritySfx is not None:
                try:
                    self._puritySfx.setVolume(ReclaimGlobals.PURITY_STING_VOLUME)
                except Exception:
                    pass
                base.playSfx(self._puritySfx)
        except Exception:
            # Missing phase audio in a stripped checkout — visual burst still pays off.
            self.notify.debug('purity sting sfx unavailable')

    def __spawnPurityBurstOverlay(self):
        """Warm full-screen flash + expanding ring — readable payoff beat."""
        try:
            cm = CardMaker('reclaim-purity-flash')
            cm.setFrame(-2, 2, -2, 2)
            flash = aspect2d.attachNewNode(cm.generate())
            flash.setTransparency(TransparencyAttrib.MAlpha)
            r, g, b, _a = ReclaimGlobals.PURITY_BURST_COLOR
            flash.setColor(r, g, b, 1)
            flash.setColorScale(r, g, b, 0)
            flash.setBin('fixed', 58)
            flash.setDepthTest(False)
            flash.setDepthWrite(False)
            self._burstFlashNP = flash

            rcm = CardMaker('reclaim-purity-ring')
            rcm.setFrame(-0.55, 0.55, -0.55, 0.55)
            ring = aspect2d.attachNewNode(rcm.generate())
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setColor(r, g, b, 1)
            ring.setColorScale(r, g, b, 0.85)
            ring.setScale(0.35)
            ring.setPos(0, 0, 0.1)
            ring.setBin('fixed', 59)
            ring.setDepthTest(False)
            ring.setDepthWrite(False)
            self._burstRingNP = ring

            peak = ReclaimGlobals.PURITY_BURST_PEAK_ALPHA
            Sequence(
                LerpColorScaleInterval(
                    flash, ReclaimGlobals.PURITY_BURST_IN_SEC,
                    Vec4(r, g, b, peak)),
                Wait(ReclaimGlobals.PURITY_BURST_HOLD_SEC),
                LerpColorScaleInterval(
                    flash, ReclaimGlobals.PURITY_BURST_OUT_SEC,
                    Vec4(r, g, b, 0)),
            ).start()
            Sequence(
                Parallel(
                    LerpScaleInterval(
                        ring, ReclaimGlobals.PURITY_RING_SEC,
                        ReclaimGlobals.PURITY_RING_PEAK_SCALE),
                    LerpColorScaleInterval(
                        ring, ReclaimGlobals.PURITY_RING_SEC,
                        Vec4(r, g, b, 0)),
                ),
            ).start()
        except Exception:
            self.__clearPurityBurstOverlay()

    def __clearPurityBurstOverlay(self):
        for attr in ('_burstFlashNP', '_burstRingNP'):
            np = getattr(self, attr, None)
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
            setattr(self, attr, None)

    def __now(self):
        try:
            return float(globalClock.getFrameTime())  # noqa: F821
        except Exception:
            return 0.0

    def __armPurityPressure(self, resetStall=False):
        """Seed mid-wave pressure clocks and start the stall watcher task."""
        now = self.__now()
        purity = 1.0 - float(self.pollutionHint or 0.0)
        if self._pressureLastPurity is None or resetStall:
            self._pressureLastPurity = purity
            self._pressureLastAdvanceT = now
        if self._pressureLastPollution is None or resetStall:
            self._pressureLastPollution = float(self.pollutionHint or 0.0)
        if resetStall:
            self._pressureLastPurity = purity
            self._pressureLastAdvanceT = now
            self._pressureLastPollution = float(self.pollutionHint or 0.0)
        self.__ensurePressureWatch()

    def __ensurePressureWatch(self):
        if not getattr(ReclaimGlobals, 'PURITY_PRESSURE_TIP_ENABLED', True):
            self.__stopPressureWatch()
            return
        if self._pressureTaskName is not None:
            return
        self._pressureTaskName = self.uniqueName('reclaim-purity-pressure')
        try:
            taskMgr.doMethodLater(  # noqa: F821
                1.0, self.__pressureWatchTick, self._pressureTaskName)
        except Exception:
            self._pressureTaskName = None

    def __stopPressureWatch(self):
        if self._pressureTaskName is not None:
            try:
                taskMgr.remove(self._pressureTaskName)  # noqa: F821
            except Exception:
                pass
            self._pressureTaskName = None
        self.__hidePressureTip()
        self._pressureLastPurity = None
        self._pressureLastAdvanceT = None
        self._pressureLastPollution = None
        self._pressureCooldownUntil = 0.0

    def __pressureWatchTick(self, task):
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            self._pressureTaskName = None
            return task.done
        self.__evaluatePurityPressure()
        return task.again

    def __evaluatePurityPressure(self):
        """Whisper when purity stalls or ink rises mid-wave (contested feel)."""
        if not getattr(ReclaimGlobals, 'PURITY_PRESSURE_TIP_ENABLED', True):
            return
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return
        if not ReclaimGlobals.isMidWavePressureContext(
                self.state, self.waveIndex, self.packAlive):
            # Keep clocks warm so the first mid-wave beat gets a full stall window.
            self.__armPurityPressure(resetStall=False)
            if self._pressureLastAdvanceT is None:
                self._pressureLastAdvanceT = self.__now()
            if self._pressureLastPollution is None:
                self._pressureLastPollution = float(self.pollutionHint or 0.0)
            return

        now = self.__now()
        pollution = float(self.pollutionHint or 0.0)
        purity = 1.0 - pollution
        advanceFloor = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_ADVANCE_THRESHOLD',
            ReclaimGlobals.PURITY_METER_POP_THRESHOLD))

        if self._pressureLastPurity is None:
            self._pressureLastPurity = purity
            self._pressureLastAdvanceT = now
        elif purity > float(self._pressureLastPurity) + advanceFloor:
            self._pressureLastPurity = purity
            self._pressureLastAdvanceT = now

        if self._pressureLastPollution is None:
            self._pressureLastPollution = pollution
        pollutionDelta = pollution - float(self._pressureLastPollution)
        # Always track the latest ink level so small noise doesn't stack.
        if pollution <= float(self._pressureLastPollution):
            self._pressureLastPollution = pollution

        if self._pressureLastAdvanceT is None:
            self._pressureLastAdvanceT = now
        stallAge = max(0.0, now - float(self._pressureLastAdvanceT))

        if now < float(self._pressureCooldownUntil or 0.0):
            # Still cool down — absorb ink rise so we don't fire immediately after.
            if pollutionDelta > 0.0:
                self._pressureLastPollution = pollution
            return

        reason = ReclaimGlobals.purityPressureReason(
            pollutionDelta, stallAge)
        if reason is None:
            return

        tip = ReclaimGlobals.purityPressureTipText(reason)
        self.__showPressureTip(tip)
        if self._purityMeter is not None:
            try:
                self._purityMeter.warnPressure()
            except Exception:
                pass
        cooldown = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_COOLDOWN_SEC', 12.0))
        self._pressureCooldownUntil = now + max(0.5, cooldown)
        self._pressureLastPollution = pollution
        # Stall tips also refresh the advance clock so we don't re-fire next tick.
        if reason == ReclaimGlobals.PURITY_PRESSURE_REASON_STALL:
            self._pressureLastAdvanceT = now
            self._pressureLastPurity = purity

    def __showPressureTip(self, text, hold=None):
        """Short rubber-hose HUD whisper under the purity meter."""
        self.__hidePressureTip()
        if hold is None:
            hold = float(getattr(
                ReclaimGlobals, 'PURITY_PRESSURE_TIP_HOLD_SEC', 2.4))
        color = getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_TIP_COLOR',
            (1.0, 0.88, 0.55, 1.0))
        baseScale = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_TIP_SCALE', 0.038))
        pos = getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_TIP_POS', (0.0, 0.0, 0.40))
        tn = TextNode('reclaim-purity-pressure-tip')
        tn.setText(str(text))
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(*color)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.75)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        np.setScale(baseScale)
        np.setPos(*pos)
        self._pressureTipNP = np
        popScale = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_TIP_POP_SCALE', 0.052))
        popSec = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_TIP_POP_SEC', 0.10))
        try:
            Sequence(
                LerpScaleInterval(np, popSec, popScale, blendType='easeOut'),
                LerpScaleInterval(np, 0.16, baseScale, blendType='easeIn'),
                name='reclaimPurityPressureTipHose',
            ).start()
        except Exception:
            pass
        taskMgr.doMethodLater(  # noqa: F821
            max(0.4, float(hold)),
            self.__pressureTipTimeout,
            self.uniqueName('reclaim-purity-pressure-tip'))

    def __pressureTipTimeout(self, task):
        self.__hidePressureTip()
        return task.done

    def __hidePressureTip(self):
        taskMgr.remove(self.uniqueName('reclaim-purity-pressure-tip'))  # noqa: F821
        if self._pressureTipNP is not None and not self._pressureTipNP.isEmpty():
            try:
                self._pressureTipNP.removeNode()
            except Exception:
                pass
        self._pressureTipNP = None

    def __confirmSecuredLock(self, zoneId):
        """HUD/tip confirmation that finished reclaim purity is locked."""
        if not getattr(ReclaimGlobals, 'SECURED_LOCK_TIP_ENABLED', True):
            self.__hideStatusHud()
            return
        tip = ReclaimGlobals.securedLockTipText(zoneId)
        self.__showSecuredLockTip(tip)
        if self._purityMeter is not None:
            try:
                self._purityMeter.confirmSecured()
            except Exception:
                pass
        hold = float(getattr(ReclaimGlobals, 'SECURED_LOCK_HUD_HOLD_SEC', 1.15))
        self.__cancelSecuredHudHold()
        try:
            taskMgr.doMethodLater(  # noqa: F821
                max(0.2, hold),
                self.__securedHudTimeout,
                self.uniqueName('reclaim-secured-hud'))
        except Exception:
            self.__hideStatusHud()

    def __securedHudTimeout(self, task):
        self.__hideStatusHud()
        return task.done

    def __cancelSecuredHudHold(self):
        try:
            taskMgr.remove(self.uniqueName('reclaim-secured-hud'))  # noqa: F821
        except Exception:
            pass

    def __showSecuredLockTip(self, text, hold=None):
        """Brief rubber-hose tip confirming the secured purity lock."""
        self.__hideSecuredLockTip()
        if hold is None:
            hold = getattr(ReclaimGlobals, 'SECURED_LOCK_TIP_HOLD_SEC', 2.8)
        color = getattr(
            ReclaimGlobals, 'SECURED_LOCK_TIP_COLOR',
            (0.72, 1.0, 0.82, 1.0))
        scale = float(getattr(ReclaimGlobals, 'SECURED_LOCK_TIP_SCALE', 0.038))
        pos = getattr(
            ReclaimGlobals, 'SECURED_LOCK_TIP_POS', (0.0, 0.0, 0.40))
        popScale = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_TIP_POP_SCALE', 0.052))
        popSec = float(getattr(
            ReclaimGlobals, 'SECURED_LOCK_TIP_POP_SEC', 0.10))
        tn = TextNode('reclaim-secured-lock-tip')
        tn.setText(str(text))
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(*color)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.7)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        np.setScale(scale)
        np.setPos(*pos)
        self._securedTipNP = np
        try:
            Sequence(
                LerpScaleInterval(np, popSec, popScale),
                LerpScaleInterval(np, 0.16, scale),
                name='reclaimSecuredLockTipHose',
            ).start()
        except Exception:
            pass
        taskMgr.doMethodLater(  # noqa: F821
            max(0.4, float(hold)),
            self.__securedLockTipTimeout,
            self.uniqueName('reclaim-secured-lock-tip'))

    def __securedLockTipTimeout(self, task):
        self.__hideSecuredLockTip()
        return task.done

    def __hideSecuredLockTip(self):
        taskMgr.remove(self.uniqueName('reclaim-secured-lock-tip'))  # noqa: F821
        if self._securedTipNP is not None and not self._securedTipNP.isEmpty():
            try:
                self._securedTipNP.removeNode()
            except Exception:
                pass
        self._securedTipNP = None

    def __clearHud(self):
        self.__hideBanner()
        self.__hideSubBanner()
        self.__hidePressureTip()
        self.__cancelSecuredHudHold()
        self.__hideSecuredLockTip()
        self.__hideStatusHud()
        self.__hideDemoHint()
        self.__clearPurityBurstOverlay()
        if self._streetWash is not None:
            self._streetWash.setActive(False)
