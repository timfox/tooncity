from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from panda3d.core import Fog, Vec4

from toontown.corruption import CorruptionGlobals


class PollutionManager(DistributedObject.DistributedObject):
    """Client mirror of per-zone pollution; drives light fog tint for demos."""

    notify = DirectNotifyGlobal.directNotify.newCategory('PollutionManager')
    neverDisable = 1

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.zonePollution = {}
        self._fog = None
        self._activeZoneId = None

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.accept('localToonLeftZone', self.__handleLeftZone)
        self.accept('localAvatarZoneChange', self.__handleZoneChange)
        base.cr.pollutionManager = self

    def disable(self):
        self.ignoreAll()
        self.__clearFog()
        if getattr(base.cr, 'pollutionManager', None) is self:
            del base.cr.pollutionManager
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        self.__clearFog()
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
        self.__clearFog()

    def __applyLocalPresentation(self, zoneId, level):
        """Minimal visual driver until slice 3 reclaim FX lands."""
        self._activeZoneId = zoneId
        if level <= CorruptionGlobals.POLLUTION_PURE:
            self.__clearFog()
            return
        if self._fog is None:
            self._fog = Fog('CorruptionFog')
            self._fog.setColor(*CorruptionGlobals.CORRUPT_FOG_COLOR)
            render.setFog(self._fog)
        exp = CorruptionGlobals.CORRUPT_FOG_EXP_MAX * level
        self._fog.setExpDensity(exp)
        # Subtle scene tint toward ink when polluted.
        tint = 1.0 - (0.35 * level)
        render.setColorScale(Vec4(tint, tint * 0.95, tint * 1.05, 1.0))

    def __clearFog(self):
        if self._fog is not None:
            render.clearFog()
            self._fog = None
        render.clearColorScale()
