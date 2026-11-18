from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from panda3d.core import Fog, Vec4

from toontown.corruption import CorruptionGlobals


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

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.accept('localToonLeftZone', self.__handleLeftZone)
        self.accept('localAvatarZoneChange', self.__handleZoneChange)
        base.cr.pollutionManager = self

    def disable(self):
        self.ignoreAll()
        self.__clearPresentation()
        if getattr(base.cr, 'pollutionManager', None) is self:
            del base.cr.pollutionManager
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        self.__clearPresentation()
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
        """Fog + ink color grade + prop-tint messenger hooks (depth D3)."""
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
        # Fog densifies and drifts toward ink purple as pollution rises.
        fogR = CorruptionGlobals.CORRUPT_FOG_COLOR[0] * (0.7 + 0.3 * level)
        fogG = CorruptionGlobals.CORRUPT_FOG_COLOR[1] * (0.75 + 0.25 * level)
        fogB = CorruptionGlobals.CORRUPT_FOG_COLOR[2]
        self._fog.setColor(fogR, fogG, fogB)
        self._fog.setExpDensity(CorruptionGlobals.CORRUPT_FOG_EXP_MAX * level)

        # Scene color grade beyond fog: desaturate toward sickly ink.
        # Keep mild enough that melee readability survives high pollution.
        tintR = 1.0 - (0.42 * level)
        tintG = 1.0 - (0.50 * level)
        tintB = 1.0 - (0.28 * level)
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
