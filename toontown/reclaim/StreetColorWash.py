"""Rubber-hose street cream wash during reclaim purity progress.

As packs clear ink, street geom tint + a soft aspect2d cream veil wash
toward pure Toontown cream. Owned by DistributedReclaimDirector — does not
stomp PollutionManager fog / reclaim purity-burst render bloom.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpFunctionInterval,
    Sequence,
)

from toontown.corruption import CorruptionGlobals
from toontown.reclaim import ReclaimGlobals


def _lerpRgb(a, b, t):
    t = max(0.0, min(1.0, float(t)))
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    )


class StreetColorWash(object):
    """Progressive cream wash: geom tint + mild fullscreen veil."""

    def __init__(self):
        self._active = False
        self._zoneId = 0
        self._purity = 0.0
        self._presentedPurity = 0.0
        self._overlayNP = None
        self._tintedGeom = None
        self._rampIval = None
        self._clearIval = None
        self._listening = False

    def start(self):
        """Listen for prop-tint hooks so we re-apply after PollutionPropTint."""
        if self._listening:
            return
        self._listening = True
        messenger.accept(  # noqa: F821
            'pollutionPropTint', self, self.__onPropTint, [], 1)
        messenger.accept(  # noqa: F821
            'purityRestoreFx', self, self.__onPurityRestore, [], 1)
        messenger.accept(  # noqa: F821
            'purityRestoreSettled', self, self.__onPuritySettled, [], 1)
        messenger.accept(  # noqa: F821
            'localToonLeftZone', self, self.__onLeftZone, [], 1)

    def stop(self):
        if not self._listening:
            self.clear(snap=True)
            return
        self._listening = False
        messenger.ignore('pollutionPropTint', self)  # noqa: F821
        messenger.ignore('purityRestoreFx', self)  # noqa: F821
        messenger.ignore('purityRestoreSettled', self)  # noqa: F821
        messenger.ignore('localToonLeftZone', self)  # noqa: F821
        self.clear(snap=True)

    def destroy(self):
        self.stop()

    def setActive(self, active, zoneId=0):
        """Enable wash while reclaim STATE_ACTIVE; clear when idle."""
        self._active = bool(active)
        if zoneId:
            self._zoneId = int(zoneId)
        if self._active:
            self.start()
        else:
            self.clear(snap=False)

    def update(self, zoneId, pollution, snap=False):
        """Drive wash from pollution scalar (0 pure … 1 full)."""
        if not self._active:
            return
        zoneId = int(zoneId or self._zoneId or 0)
        if zoneId:
            self._zoneId = zoneId
        pollution = max(0.0, min(1.0, float(pollution)))
        purity = 1.0 - pollution
        self._purity = purity
        self.start()

        delta = abs(purity - self._presentedPurity)
        if snap or delta <= 0.01:
            self.__finishRamp()
            self.__applyPresented(purity)
            return

        self.__finishRamp()
        start = self._presentedPurity
        duration = float(ReclaimGlobals.STREET_WASH_LERP_SEC)
        # Bigger purity jumps (pack clears) get a touch more settle.
        if purity > start:
            duration = max(
                duration,
                float(ReclaimGlobals.STREET_WASH_ADVANCE_SEC))

        def setPresented(t, a=start, b=purity):
            self.__applyPresented(a + (b - a) * float(t))

        self._rampIval = Sequence(
            LerpFunctionInterval(
                setPresented, fromData=0.0, toData=1.0, duration=duration),
            Func(self.__applyPresented, purity),
            name='reclaimStreetCreamWashRamp',
        )
        self._rampIval.start()

    def clear(self, snap=False):
        """Drop overlay + geom cream override."""
        self.__finishRamp()
        if self._clearIval is not None:
            try:
                self._clearIval.finish()
            except Exception:
                pass
            self._clearIval = None

        if snap or self._overlayNP is None:
            self.__clearOverlay()
            self.__clearGeomTint()
            self._presentedPurity = 0.0
            self._purity = 0.0
            return

        # Soft fade so purity burst / idle handoff doesn't flash.
        overlay = self._overlayNP
        cream = ReclaimGlobals.STREET_WASH_CREAM
        sec = float(ReclaimGlobals.STREET_WASH_CLEAR_SEC)
        self._clearIval = Sequence(
            LerpColorScaleInterval(
                overlay, sec, Vec4(cream[0], cream[1], cream[2], 0.0),
                blendType='easeIn'),
            Func(self.__clearOverlay),
            Func(self.__clearGeomTint),
            Func(self.__markCleared),
            name='reclaimStreetCreamWashClear',
        )
        self._clearIval.start()

    def __markCleared(self):
        self._presentedPurity = 0.0
        self._purity = 0.0
        self._clearIval = None

    def __finishRamp(self):
        if self._rampIval is None:
            return
        ival = self._rampIval
        self._rampIval = None
        try:
            ival.pause()
        except Exception:
            pass

    def __applyPresented(self, purity):
        purity = max(0.0, min(1.0, float(purity)))
        self._presentedPurity = purity
        strength = float(ReclaimGlobals.STREET_WASH_STRENGTH)
        blend = max(0.0, min(1.0, purity * strength))
        cream = ReclaimGlobals.STREET_WASH_CREAM

        # Geom: hood ink tint → sunny cream as purity fills.
        pollution = 1.0 - purity
        ink = CorruptionGlobals.hoodPropTint(self._zoneId, pollution)
        rgb = _lerpRgb(ink, cream, blend)
        self.__applyGeomTint(rgb[0], rgb[1], rgb[2])

        # Soft cream veil (readable hose atmosphere, never opaque).
        peak = float(ReclaimGlobals.STREET_WASH_OVERLAY_PEAK_ALPHA)
        alpha = peak * blend
        self.__applyOverlay(cream[0], cream[1], cream[2], alpha)

    def __streetGeom(self):
        try:
            place = base.cr.playGame.getPlace()  # noqa: F821
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

    def __applyGeomTint(self, r, g, b):
        geom = self.__streetGeom()
        if geom is None:
            return
        if self._tintedGeom is not None and self._tintedGeom != geom:
            self.__clearGeomTint()
        try:
            geom.setColorScale(Vec4(r, g, b, 1.0))
        except Exception:
            return
        self._tintedGeom = geom

    def __clearGeomTint(self):
        geom = self._tintedGeom
        self._tintedGeom = None
        if geom is None:
            return
        try:
            if not geom.isEmpty():
                geom.clearColorScale()
        except Exception:
            pass

    def __ensureOverlay(self):
        if self._overlayNP is not None and not self._overlayNP.isEmpty():
            return self._overlayNP
        self._overlayNP = None
        try:
            cm = CardMaker('reclaim-street-cream-wash')
            cm.setFrame(-2, 2, -2, 2)
            wash = aspect2d.attachNewNode(cm.generate())  # noqa: F821
            wash.setTransparency(TransparencyAttrib.MAlpha)
            wash.setBin('fixed', int(ReclaimGlobals.STREET_WASH_OVERLAY_BIN))
            wash.setDepthTest(False)
            wash.setDepthWrite(False)
            wash.setColorScale(1, 1, 1, 0)
            self._overlayNP = wash
        except Exception:
            self._overlayNP = None
        return self._overlayNP

    def __applyOverlay(self, r, g, b, alpha):
        if alpha <= 0.001:
            self.__clearOverlay()
            return
        wash = self.__ensureOverlay()
        if wash is None:
            return
        try:
            wash.setColorScale(r, g, b, alpha)
            wash.show()
        except Exception:
            self.__clearOverlay()

    def __clearOverlay(self):
        wash = self._overlayNP
        self._overlayNP = None
        if wash is None:
            return
        try:
            if not wash.isEmpty():
                wash.removeNode()
        except Exception:
            pass

    def __onPropTint(self, zoneId, level):
        """Re-apply cream blend after PollutionPropTint writes geom colorScale."""
        if not self._active:
            return
        if zoneId and int(zoneId) != int(self._zoneId or 0):
            # Keep following the reclaim street only.
            if self._zoneId:
                return
        # Snap to presented purity so PollutionPropTint can't flash ink back.
        self.__applyPresented(self._presentedPurity)

    def __onPurityRestore(self, zoneId):
        # Soft-clear progressive wash; PurityCompleteCreamWashFx owns the
        # discrete cream pulse layered with StreetSparkleFx.
        if zoneId and self._zoneId and int(zoneId) != int(self._zoneId):
            return
        self._active = False
        self.clear(snap=False)

    def __onPuritySettled(self, zoneId):
        if zoneId and self._zoneId and int(zoneId) != int(self._zoneId):
            return
        self.clear(snap=True)

    def __onLeftZone(self, *args):
        self.clear(snap=True)
