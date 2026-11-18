"""Client street-geom tint driven by PollutionManager's pollutionPropTint hook.

Applies a mild hood-specific colorScale to the loaded street geom (town_top_level
/ place.loader.geom) — not to `render` — so reclaim purity bloom and campaign
handoff that animate render colorScale keep working.
"""

from direct.directnotify import DirectNotifyGlobal
from panda3d.core import Vec4

from toontown.corruption import CorruptionGlobals


class PollutionPropTint:
    """Listens for pollutionPropTint and tints street props under geom."""

    notify = DirectNotifyGlobal.directNotify.newCategory('PollutionPropTint')

    def __init__(self):
        self._active = False
        self._tintedGeom = None
        self._lastZoneId = None

    def start(self):
        if self._active:
            return
        self._active = True
        messenger.accept(
            'pollutionPropTint', self, self.__onPropTint, [], 1)
        messenger.accept(
            'purityRestoreFx', self, self.__onPurityRestore, [], 1)
        messenger.accept(
            'localToonLeftZone', self, self.__onLeftZone, [], 1)

    def stop(self):
        if not self._active:
            return
        self._active = False
        messenger.ignore('pollutionPropTint', self)
        messenger.ignore('purityRestoreFx', self)
        messenger.ignore('localToonLeftZone', self)
        self.clear()

    def clear(self):
        geom = self._tintedGeom
        self._tintedGeom = None
        self._lastZoneId = None
        if geom is None:
            return
        try:
            if not geom.isEmpty():
                geom.clearColorScale()
        except Exception:
            pass

    def __streetGeom(self):
        """Resolve current street geom without touching render colorScale."""
        try:
            place = base.cr.playGame.getPlace()
        except Exception:
            return None
        if place is None:
            return None
        loader = getattr(place, 'loader', None)
        if loader is None:
            return None
        geom = getattr(loader, 'geom', None)
        if geom is None or geom.isEmpty():
            return None
        return geom

    def __onPropTint(self, zoneId, level):
        level = CorruptionGlobals.clampPollution(level)
        if level <= CorruptionGlobals.POLLUTION_PURE:
            self.clear()
            return

        geom = self.__streetGeom()
        if geom is None:
            # Street not loaded yet; nothing safe to tint.
            return

        # If we switched streets, drop previous geom tint first.
        if self._tintedGeom is not None and self._tintedGeom != geom:
            self.clear()

        r, g, b = CorruptionGlobals.hoodPropTint(zoneId, level)
        try:
            geom.setColorScale(Vec4(r, g, b, 1.0))
        except Exception:
            self.notify.debug('prop tint skipped (geom unavailable)')
            return
        self._tintedGeom = geom
        self._lastZoneId = zoneId

    def __onPurityRestore(self, zoneId):
        # Reclaim/campaign purity moment: lift prop ink immediately.
        # PollutionManager also sends pollutionPropTint(zone, 0) on clear.
        self.clear()

    def __onLeftZone(self, *args):
        self.clear()
