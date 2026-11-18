from panda3d.core import TextNode, Vec4

from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import (
    Func, LerpColorScaleInterval, Parallel, Sequence, Wait)

from toontown.campaign import CampaignGlobals
from toontown.corruption import CorruptionGlobals
from toontown.reclaim import ReclaimGlobals


class DistributedReclaimDirector(DistributedObject.DistributedObject):
    """Client reclaim feedback: status HUD, wave banners, purity restore FX."""

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
        self._hintNP = None
        self._statusNP = None
        self._demoHintNP = None
        self._restoreIval = None

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        base.cr.reclaimDirector = self
        self.accept('pollutionChanged', self.__onPollutionChanged)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        # zoneId is assigned by the interest system once we are in the street.
        self.reclaimZoneId = getattr(self, 'zoneId', 0)

    def disable(self):
        self.ignoreAll()
        self.__clearHud()
        if self._restoreIval is not None:
            self._restoreIval.finish()
            self._restoreIval = None
        if getattr(base.cr, 'reclaimDirector', None) is self:
            del base.cr.reclaimDirector
        DistributedObject.DistributedObject.disable(self)

    def setState(self, state):
        self.state = int(state)
        if self.state == ReclaimGlobals.STATE_IDLE:
            self.__clearHud()
        elif self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__showStatusHud()

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
            self.__showBanner(ReclaimGlobals.BANNER_START, (1.0, 0.92, 0.45, 1.0))
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
        wave = max(1, int(waveIndex))
        if self.finalePhase >= 1:
            label = ReclaimGlobals.FINALE_PACK_BANNER.get(
                self.finalePhase, ReclaimGlobals.waveLabel(wave, self.maxWaves))
            title = ReclaimGlobals.WAVE_BANNER_FMT % (wave, self.maxWaves, label)
            color = (
                (1.0, 0.5, 0.95, 1.0) if self.finalePhase < 2
                else (1.0, 0.35, 0.25, 1.0))
            self.__showBanner(title, color, hold=2.2)
            self.__showSubBanner(
                '%s  ·  %s inbound' % (
                    'Overlord pack' if self.finalePhase < 2 else 'Unleashed pack',
                    int(count)),
                color,
                hold=2.2)
        else:
            label = ReclaimGlobals.waveLabel(wave, self.maxWaves)
            title = ReclaimGlobals.WAVE_BANNER_FMT % (wave, self.maxWaves, label)
            self.__showBanner(title, (0.85, 0.55, 1.0, 1.0), hold=2.0)
            self.__showSubBanner(
                '%s  ·  %s inbound' % (ReclaimGlobals.BANNER_PACK, int(count)),
                (0.95, 0.8, 1.0, 1.0),
                hold=2.0)
        self.__showStatusHud()

    def announceWaveCleared(self, waveIndex):
        self.__showBanner(
            ReclaimGlobals.BANNER_WAVE_CLEARED,
            (0.7, 0.95, 1.0, 1.0),
            hold=1.4)
        self.__showSubBanner(
            'Wave %s down — next surge incoming' % int(waveIndex),
            (0.85, 0.95, 1.0, 1.0),
            hold=1.4)

    def announceReclaimComplete(self):
        self.__showBanner(
            ReclaimGlobals.BANNER_COMPLETE, (0.55, 1.0, 0.7, 1.0), hold=3.4)
        self.__showSubBanner(
            ReclaimGlobals.BANNER_COMPLETE_SUB, (0.85, 1.0, 0.9, 1.0), hold=3.4)
        self.__playRestoreFx()
        self.__hideStatusHud()
        self.__hideDemoHint()

    def __onPollutionChanged(self, zoneId, level):
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return
        if hasattr(base, 'localAvatar') and getattr(base.localAvatar, 'zoneId', None) == zoneId:
            self.pollutionHint = level
            self.__showStatusHud()

    def __showBanner(self, text, color, hold=2.2):
        self.__hideBanner()
        tn = TextNode('reclaim-banner')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(*color)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0, 0, 0, 0.75)
        np = aspect2d.attachNewNode(tn)
        np.setScale(0.09)
        np.setPos(0, 0, 0.78)
        self._bannerNP = np
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

    def __showStatusHud(self):
        """Persistent player-facing reclaim status (wave / corruption / pack)."""
        wave = max(self.waveIndex, 1 if self.state == ReclaimGlobals.STATE_ACTIVE else 0)
        text = ReclaimGlobals.STATUS_FMT % (
            wave,
            self.maxWaves,
            self.pollutionHint * 100.0,
            self.packAlive)
        if self.finalePhase >= 1:
            text = 'Overlord P%s  |  %s' % (self.finalePhase, text)
        if self._statusNP is not None and not self._statusNP.isEmpty():
            self._statusNP.node().setText(text)
            return
        tn = TextNode('reclaim-status')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        statusColor = (0.95, 0.88, 1.0, 1.0)
        if self.finalePhase >= 2:
            statusColor = (1.0, 0.55, 0.45, 1.0)
        elif self.finalePhase == 1:
            statusColor = (1.0, 0.7, 1.0, 1.0)
        tn.setTextColor(*statusColor)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.75)
        np = aspect2d.attachNewNode(tn)
        np.setScale(0.042)
        np.setPos(0, 0, 0.62)
        self._statusNP = np

        # Keep a compact corruption readout as a secondary cue.
        hint = ReclaimGlobals.POLLUTION_HINT_FMT % (self.pollutionHint * 100.0)
        if self._hintNP is not None and not self._hintNP.isEmpty():
            self._hintNP.node().setText(hint)
        else:
            htn = TextNode('reclaim-pollution-hint')
            htn.setText(hint)
            htn.setAlign(TextNode.ACenter)
            htn.setTextColor(0.75, 0.55, 0.95, 1.0)
            htn.setShadow(0.04, 0.04)
            htn.setShadowColor(0, 0, 0, 0.7)
            hnp = aspect2d.attachNewNode(htn)
            hnp.setScale(0.036)
            hnp.setPos(0, 0, 0.56)
            self._hintNP = hnp

    def __hideStatusHud(self):
        if self._statusNP is not None and not self._statusNP.isEmpty():
            self._statusNP.removeNode()
        self._statusNP = None
        if self._hintNP is not None and not self._hintNP.isEmpty():
            self._hintNP.removeNode()
        self._hintNP = None

    def __showDemoHint(self):
        if self._demoHintNP is not None and not self._demoHintNP.isEmpty():
            return
        tn = TextNode('reclaim-demo-hint')
        tn.setText(ReclaimGlobals.DEMO_HINT)
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
        """Purity restore moment: burst, sting/NPC hooks, lingering glow."""
        if self._restoreIval is not None:
            self._restoreIval.finish()
        messenger.send('purityRestoreFx', [self.reclaimZoneId])
        messenger.send('purityRestoreSting', [self.reclaimZoneId])
        messenger.send('npcCheerStub', [self.reclaimZoneId])
        # Two-beat wash: ink lifts, then a warm purity bloom settles.
        self._restoreIval = Sequence(
            Parallel(
                LerpColorScaleInterval(render, 0.12, Vec4(1.55, 1.6, 1.35, 1.0)),
                Func(messenger.send, 'purityBurstPulse', [self.reclaimZoneId, 1]),
            ),
            LerpColorScaleInterval(render, 0.35, Vec4(1.15, 1.25, 1.05, 1.0)),
            Parallel(
                LerpColorScaleInterval(render, 0.55, Vec4(1.05, 1.12, 0.98, 1.0)),
                Func(messenger.send, 'purityBurstPulse', [self.reclaimZoneId, 2]),
            ),
            Wait(0.35),
            LerpColorScaleInterval(render, 0.7, Vec4(1, 1, 1, 1)),
            Func(render.clearColorScale),
            Func(messenger.send, 'purityRestoreSettled', [self.reclaimZoneId]),
        )
        self._restoreIval.start()

    def __clearHud(self):
        self.__hideBanner()
        self.__hideSubBanner()
        self.__hideStatusHud()
        self.__hideDemoHint()
