from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from panda3d.core import Fog, Vec4

from toontown.corruption import CorruptionGlobals
from toontown.corruption import PollutionPropTint


class PollutionManager(DistributedObject.DistributedObject):
    """Client mirror of per-zone pollution; fog + color grade + prop tint hooks."""

    notify = DirectNotifyGlobal.directNotify.newCategory('PollutionManager')
    neverDisable = 1

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.zonePollution = {}
        self._fog = None
        self._activeZoneId = None
        self._lastLevel = CorruptionGlobals.POLLUTION_PURE
        self._propTint = None

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.accept('localToonLeftZone', self.__handleLeftZone)
        self.accept('localAvatarZoneChange', self.__handleZoneChange)
        base.cr.pollutionManager = self
        # Hood-specific street geom tint (listens to pollutionPropTint).
        self._propTint = PollutionPropTint.PollutionPropTint()
        self._propTint.start()

    def disable(self):
        self.ignoreAll()
        self.__clearPresentation()
        if self._propTint is not None:
            self._propTint.stop()
            self._propTint = None
        if getattr(base.cr, 'pollutionManager', None) is self:
            del base.cr.pollutionManager
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        self.__clearPresentation()
        if self._propTint is not None:
            self._propTint.stop()
            self._propTint = None
        DistributedObject.DistributedObject.delete(self)

    def getPollution(self, zoneId=None):
        if zoneId is None:
            if hasattr(base, 'localAvatar'):
                zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return CorruptionGlobals.POLLUTION_DEFAULT
        return self.zonePollution.get(zoneId, CorruptionGlobals.POLLUTION_DEFAULT)

    def setZonePollution(self, zoneId, netLevel):
        level = CorruptionGlobals.pollutionFromNet(netLevel)
        self.zonePollution[zoneId] = level
        messenger.send('pollutionChanged', [zoneId, level])
        if hasattr(base, 'localAvatar') and getattr(base.localAvatar, 'zoneId', None) == zoneId:
            self.__applyLocalPresentation(zoneId, level)

    def d_requestZonePollution(self, zoneId):
        self.sendUpdate('requestZonePollution', [zoneId])

    def d_requestStreetEvent(self, eventType):
        """0=start reclaim in this street, 1=start/resume campaign act."""
        self.sendUpdate('requestStreetEvent', [int(eventType)])

    def __handleZoneChange(self, zoneId=None):
        if zoneId is None and hasattr(base, 'localAvatar'):
            zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return
        self._activeZoneId = zoneId
        if zoneId not in self.zonePollution:
            self.d_requestZonePollution(zoneId)
        self.__applyLocalPresentation(zoneId, self.getPollution(zoneId))

    def __handleLeftZone(self, *args):
        self.__clearPresentation()

    def __applyLocalPresentation(self, zoneId, level):
        """Hood-biased fog + ink color grade + prop-tint messenger hooks."""
        self._activeZoneId = zoneId
        self._lastLevel = level
        if level <= CorruptionGlobals.POLLUTION_PURE:
            self.__clearPresentation()
            messenger.send('pollutionPropTint', [zoneId, 0.0])
            messenger.send('pollutionColorGrade', [zoneId, 0.0])
            return

        if self._fog is None:
            self._fog = Fog('CorruptionFog')
            render.setFog(self._fog)

        fogR, fogG, fogB = CorruptionGlobals.hoodFogColor(zoneId, level)
        self._fog.setColor(fogR, fogG, fogB)
        self._fog.setExpDensity(CorruptionGlobals.hoodFogExpDensity(zoneId, level))

        # Scene color grade beyond fog: hood-biased desaturation.
        # Keep mild enough that melee readability survives high pollution.
        tintR, tintG, tintB = CorruptionGlobals.hoodColorGrade(zoneId, level)
        render.setColorScale(Vec4(tintR, tintG, tintB, 1.0))

        # Hooks for street props / future art to tint without hard coupling.
        messenger.send('pollutionPropTint', [zoneId, level])
        messenger.send('pollutionColorGrade', [zoneId, level])

    def __clearPresentation(self):
        if self._fog is not None:
            render.clearFog()
            self._fog = None
        # Avoid stomping an in-flight purity restore bloom on render.
        reclaim = getattr(base.cr, 'reclaimDirector', None)
        restoreActive = (
            reclaim is not None
            and getattr(reclaim, '_restoreIval', None) is not None)
        if not restoreActive:
            render.clearColorScale()
        self._lastLevel = CorruptionGlobals.POLLUTION_PURE
