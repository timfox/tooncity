"""Client street-geom tint driven by PollutionManager's pollutionPropTint hook.

Applies a mild hood-specific colorScale to the loaded street geom (town_top_level
/ place.loader.geom) — not to `render` — so reclaim purity bloom and campaign
handoff that animate render colorScale keep working.

On street purity complete, hood corruption tint cream-fades toward sunny
cream/pastel (HOOD_TINT_CREAM_FADE_*) instead of snapping clear — matches fog
cream dissolve (#100). Toontown spiritual sequel — no keyblades / no KH branding.
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
        self._lastLevel = CorruptionGlobals.POLLUTION_PURE
        self._creamFadeBlend = 0.0
        self._creamFading = False
        self._fadeInkRgb = None

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

    def beginCreamFade(self):
        """Arm cream geom tint for the in-flight purity clear window."""
        if not getattr(
                CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_ENABLED', True):
            return
        zoneId = self._lastZoneId
        # Hold a readable ink capture even if density already dipped.
        level = max(float(self._lastLevel), 0.18)
        if zoneId is None:
            try:
                zoneId = getattr(base.localAvatar, 'zoneId', None)
            except Exception:
                zoneId = None
        if zoneId is not None:
            self._lastZoneId = zoneId
            self._fadeInkRgb = CorruptionGlobals.hoodPropTint(zoneId, level)
        elif self._fadeInkRgb is None:
            self._fadeInkRgb = (0.78, 0.70, 0.88)
        self._creamFading = True
        self._creamFadeBlend = 0.0
        self.__applyCreamPresented()

    def setCreamFadeBlend(self, blend):
        """0..1 cream mix into hood prop tint (driven by cream-fade FX)."""
        self._creamFadeBlend = max(0.0, min(1.0, float(blend)))
        if not self._creamFading:
            return
        self.__applyCreamPresented()

    def finishCreamFade(self):
        """Drop cream geom tint after fade overlay finishes."""
        if not self._creamFading and self._creamFadeBlend == 0.0:
            return
        self._creamFading = False
        self._creamFadeBlend = 0.0
        self._fadeInkRgb = None
        self.clear()

    def clear(self):
        self._creamFading = False
        self._creamFadeBlend = 0.0
        self._fadeInkRgb = None
        geom = self._tintedGeom
        self._tintedGeom = None
        self._lastZoneId = None
        self._lastLevel = CorruptionGlobals.POLLUTION_PURE
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

    def __applyRgb(self, r, g, b, zoneId=None):
        geom = self.__streetGeom()
        if geom is None:
            return False
        if self._tintedGeom is not None and self._tintedGeom != geom:
            prev = self._tintedGeom
            self._tintedGeom = None
            try:
                if prev is not None and not prev.isEmpty():
                    prev.clearColorScale()
            except Exception:
                pass
        try:
            geom.setColorScale(Vec4(r, g, b, 1.0))
        except Exception:
            self.notify.debug('prop tint skipped (geom unavailable)')
            return False
        self._tintedGeom = geom
        if zoneId is not None:
            self._lastZoneId = zoneId
        return True

    def __applyCreamPresented(self):
        zoneId = self._lastZoneId
        if zoneId is None:
            return
        r, g, b = CorruptionGlobals.hoodPropTintCreamFadeColor(
            zoneId, self._lastLevel, self._creamFadeBlend,
            inkRgb=self._fadeInkRgb)
        self.__applyRgb(r, g, b, zoneId=zoneId)

    def __onPropTint(self, zoneId, level):
        level = CorruptionGlobals.clampPollution(level)
        self._lastLevel = level
        self._lastZoneId = zoneId

        if level <= CorruptionGlobals.POLLUTION_PURE:
            # Density clear finished — cream fade FX still owns geom until
            # finishCreamFade; don't snap ink off mid-cream lift. Reclaim's
            # POLLUTION_FOG_CLEAR_SEC ramp usually keeps presented level > 0
            # long enough for purityRestoreFx to arm the fade first.
            if self._creamFading:
                self.__applyCreamPresented()
                return
            self.clear()
            return

        if self._creamFading:
            # Keep ink capture tracking the density ramp under cream blend.
            self._fadeInkRgb = CorruptionGlobals.hoodPropTint(zoneId, level)
            self.__applyCreamPresented()
            return

        r, g, b = CorruptionGlobals.hoodPropTint(zoneId, level)
        if not self.__applyRgb(r, g, b, zoneId=zoneId):
            return

    def __onPurityRestore(self, zoneId):
        # Reclaim/campaign purity moment: cream-fade hood tint (FX arms blend).
        # PollutionManager also sends pollutionPropTint(zone, 0) on clear.
        if getattr(
                CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_ENABLED', True):
            if zoneId is not None:
                self._lastZoneId = zoneId
            # Capture ink now so a late FX start still has a hood base.
            if self._tintedGeom is not None and self._fadeInkRgb is None:
                level = max(float(self._lastLevel), 0.18)
                self._fadeInkRgb = CorruptionGlobals.hoodPropTint(
                    self._lastZoneId or zoneId, level)
            return
        self.clear()

    def __onLeftZone(self, *args):
        self.clear()
