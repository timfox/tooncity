from panda3d.core import TextNode, Vec4

from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import (
    Func, LerpColorScaleInterval, Parallel, Sequence, Wait)

from toontown.corruption import CorruptionGlobals
from toontown.reclaim import ReclaimGlobals


class DistributedReclaimDirector(DistributedObject.DistributedObject):
    """Client reclaim feedback: banner, pollution hint, purity restore FX."""

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedReclaimDirector')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.state = ReclaimGlobals.STATE_IDLE
        self.reclaimZoneId = 0
        self.pollutionHint = CorruptionGlobals.POLLUTION_PURE
        self._bannerNP = None
        self._hintNP = None
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

    def setPollutionHint(self, netLevel):
        self.pollutionHint = CorruptionGlobals.pollutionFromNet(netLevel)
        if self.state == ReclaimGlobals.STATE_ACTIVE:
            self.__showPollutionHint()

    def announceReclaimStart(self):
        self.__showBanner(ReclaimGlobals.BANNER_START, (1.0, 0.92, 0.45, 1.0))
        self.__showDemoHint()
        self.__showPollutionHint()

    def announcePackSpawn(self, count):
        self.__showBanner(
            '%s (%s)' % (ReclaimGlobals.BANNER_PACK, int(count)),
            (0.85, 0.55, 1.0, 1.0),
            hold=1.6)

    def announceReclaimComplete(self):
        self.__showBanner(ReclaimGlobals.BANNER_COMPLETE, (0.55, 1.0, 0.7, 1.0), hold=2.8)
        self.__playRestoreFx()
        self.__hidePollutionHint()
        self.__hideDemoHint()

    def __onPollutionChanged(self, zoneId, level):
        if self.state != ReclaimGlobals.STATE_ACTIVE:
            return
        if hasattr(base, 'localAvatar') and getattr(base.localAvatar, 'zoneId', None) == zoneId:
            self.pollutionHint = level
            self.__showPollutionHint()

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

    def __showPollutionHint(self):
        text = ReclaimGlobals.POLLUTION_HINT_FMT % (self.pollutionHint * 100.0)
        if self._hintNP is not None and not self._hintNP.isEmpty():
            self._hintNP.node().setText(text)
            return
        tn = TextNode('reclaim-pollution-hint')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(0.75, 0.55, 0.95, 1.0)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.7)
        np = aspect2d.attachNewNode(tn)
        np.setScale(0.048)
        np.setPos(0, 0, 0.68)
        self._hintNP = np

    def __hidePollutionHint(self):
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
        """Hook: brief purity flash; fog clear already handled by PollutionManager."""
        if self._restoreIval is not None:
            self._restoreIval.finish()
        messenger.send('purityRestoreFx', [self.reclaimZoneId])
        self._restoreIval = Sequence(
            LerpColorScaleInterval(render, 0.2, Vec4(1.35, 1.4, 1.2, 1.0)),
            LerpColorScaleInterval(render, 0.55, Vec4(1, 1, 1, 1)),
            Func(render.clearColorScale),
        )
        self._restoreIval.start()

    def __clearHud(self):
        self.__hideBanner()
        self.__hidePollutionHint()
        self.__hideDemoHint()
