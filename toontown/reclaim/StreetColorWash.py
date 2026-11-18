"""Rubber-hose street cream wash during reclaim purity progress.

As packs clear ink, street geom tint + a soft aspect2d cream veil wash
toward pure Toontown cream. A delayed cream aftershock (softer flecks
settling downward + soft halo) follows purity advances — same residual
grammar as entry cream wash aftershock (#132), wave-clear cream aftershock
(#127), and purity-complete cream aftershock (#136). Owned by
DistributedReclaimDirector — does not stomp PollutionManager fog / reclaim
purity-burst render bloom. Toontown spiritual-sequel tone only — no
keyblades / no KH branding.
"""

from math import cos, pi

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpFunctionInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
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
    """Progressive cream wash: geom tint + mild fullscreen veil + aftershock."""

    def __init__(self):
        self._active = False
        self._zoneId = 0
        self._purity = 0.0
        self._presentedPurity = 0.0
        self._overlayNP = None
        self._tintedGeom = None
        self._rampIval = None
        self._clearIval = None
        self._aftershockIval = None
        self._fleckNPs = []
        self._haloNP = None
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
        advancing = purity > self._presentedPurity + 0.01
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

        # Residual cream aftershock on purity advances (pack clears).
        if advancing:
            self.__playAftershock()

    def clear(self, snap=False):
        """Drop overlay + geom cream override + aftershock residual."""
        self.__finishRamp()
        self.__clearAftershock()
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

    def __playAftershock(self):
        """Arm delayed cream flecks + soft halo after a purity advance."""
        if not getattr(ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_ENABLED', True):
            return
        self.__clearAftershock()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        origin = getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_ORIGIN',
            (0.0, 0.0, -0.10))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.10

        aftershock = self.__buildAftershock(parent, ox, oy, oz)
        if aftershock is None:
            return
        self._aftershockIval = Sequence(
            aftershock,
            Func(self.__clearAftershockNodes),
            name='reclaimStreetCreamWashAftershock',
        )
        try:
            self._aftershockIval.start()
        except Exception:
            self.__clearAftershock()

    def __buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after street wash advance."""
        delay = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_DELAY_SEC', 0.22))
        parts = []

        if getattr(ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self.__spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_COUNT', 5))
        sec = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_SEC', 0.32))
        for i in range(count):
            part = self.__spawnAftershockFleck(
                parent, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def __spawnAftershockHalo(self, parent, ox, oy, oz):
        half = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_HALO_HALF', 0.46))
        startScale = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_HALO_START', 0.24))
        peakScale = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_HALO_PEAK', 1.12))
        sec = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_HALO_SEC', 0.26))
        peakA = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.11))
        r, g, b, _a = getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_BIN', 30))
        try:
            cm = CardMaker('reclaim-street-cream-wash-aftershock-halo')
            # Soft oval halo above progressive wash — quieter residual settle.
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = parent.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(ox, oy, oz)
            halo.setScale(startScale)
            halo.setBin('fixed', binSort)
            halo.setDepthTest(False)
            halo.setDepthWrite(False)
        except Exception:
            return None
        self._haloNP = halo
        return Parallel(
            LerpScaleInterval(
                halo, max(0.01, sec), peakScale, blendType='easeOut'),
            Sequence(
                Wait(max(0.0, sec * 0.2)),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.8), Vec4(r, g, b, 0),
                    blendType='easeIn'),
            ),
        )

    def __spawnAftershockFleck(self, parent, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles downward — residual wash aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_SIZE', 0.014))
        drift = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_DRIFT', 0.26))
        fall = float(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_FALL', 0.20))
        r, g, b, a = getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.76))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            ReclaimGlobals, 'STREET_WASH_AFTERSHOCK_BIN', 30))
        angle = (2.0 * pi * index) / float(count) + 0.26
        try:
            cm = CardMaker('reclaim-street-cream-wash-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of progressive wash.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.20, size * 1.20, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = ox + cos(angle) * 0.07
            startZ = oz + 0.012 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.28 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream, not a second progressive wash.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.04 * (index % 3))
        peak = 1.05 + 0.08 * (index % 2)
        self._fleckNPs.append(fleck)
        stagger = 0.016 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.28), peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(
                    fleck, max(0.01, sec * 0.72), end, blendType='easeIn'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.72), 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.72), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def __clearAftershock(self):
        if self._aftershockIval is not None:
            try:
                self._aftershockIval.pause()
            except Exception:
                pass
            self._aftershockIval = None
        self.__clearAftershockNodes()

    def __clearAftershockNodes(self):
        self._aftershockIval = None
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in self._fleckNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []

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
        # Soft-clear progressive wash + aftershock; EntryCreamWashPulseFx owns
        # the entry cream pulse with shimmer, PurityCompleteCreamWashFx owns
        # the discrete purity pulse + delayed cream aftershock + settle cream
        # wash layered with StreetSparkleFx.
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
