"""Rubber-hose cream wash pulse + delayed cream aftershock on corrupt silhouette.

Fullscreen soft cream veil that pulses between telegraphs — IdleCreamWashPulse
(#146) / DeathCreamWashPulse (#119) overlay grammar as a brief ambient
settle beat against the ink silhouette. A delayed cream aftershock (softer
flecks settling downward + soft halo) follows each wash pulse — same residual
grammar as idle cream wash aftershock (#177) / death cream wash aftershock
(#172); world-space settle matches telegraph cream warn aftershock (#121).
Soft under world-space SilhouetteCreamRimFlecks + SilhouetteCreamSparkles;
cream / pastel only (not ink). Wired from DistributedCorruptToon beside
SilhouetteCreamRim + SilhouetteCreamSparkle (start / pause / resume / clear
together). Client only. Toontown spiritual sequel — no keyblades / no KH
branding.
"""

from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from toontown.corruption import CorruptionGlobals


def silhouetteCreamWashLook(archetype=None, finaleLook=None):
    """Resolve silhouette cream-wash tunables; compose period with rim sparkle look."""
    look = dict(getattr(
        CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_LOOK', {}) or {})
    # Lazy import avoids circular load with CorruptSilhouetteCreamSparkleFx.
    try:
        from toontown.corruption.CorruptSilhouetteCreamSparkleFx import (
            silhouetteCreamSparkleLook)
        sparkle = silhouetteCreamSparkleLook(archetype, finaleLook=finaleLook)
        sparklePeriod = float(sparkle.get('periodSec', 1.18))
        # Slower than rising rim sparkles so wash reads as soft ambient settle,
        # not sync-locked with fleck twinkles (or idle cream wash #146).
        look.setdefault(
            'periodSec',
            sparklePeriod * float(look.get('periodScale', 2.4)))
        look.setdefault(
            'settleSec',
            float(sparkle.get('settleSec', 0.47)) + float(
                look.get('settleBias', 0.52)))
    except Exception:
        look.setdefault('periodSec', 2.85)
        look.setdefault('settleSec', 0.99)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_BIN', 37)))
    return look


class SilhouetteCreamWashPulse(object):
    """Owns looping soft aspect2d cream wash pulses + delayed cream aftershock."""

    def __init__(self):
        self._loopIval = None
        self._pulseIval = None
        self._washPlayIval = None
        self._washNP = None
        self._haloNP = None
        self._fleckNPs = []
        self._paused = False
        self._parent = None
        self._archetype = CorruptionGlobals.ARCHETYPE_INK
        self._finaleLook = None
        self._look = None

    def start(self, parent, archetype=None, finaleLook=None):
        """Begin sparse looping cream wash pulses. Returns loop or None.

        `parent` is the silhouette rim / sparkle visual root — wash itself is
        aspect2d; aftershock flecks / halo attach to this parent (idle
        aftershock #177 world-space settle grammar, parent-local like rim
        flecks).
        """
        self.clear()
        if not getattr(
                CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_ENABLED', True):
            return None
        if parent is None:
            return None
        try:
            if parent.isEmpty():
                return None
        except Exception:
            return None
        self._parent = parent
        self._archetype = archetype
        self._finaleLook = finaleLook
        self._look = silhouetteCreamWashLook(archetype, finaleLook=finaleLook)
        self._paused = False
        period = max(1.1, float(self._look.get('periodSec', 2.85)))
        settle = max(0.15, float(self._look.get('settleSec', 0.99)))
        self._loopIval = Sequence(
            Wait(settle),
            Func(self._emitPulse),
            Wait(period),
            name='corruptSilhouetteCreamWashLoop',
        )
        self._loopIval.loop()
        return self._loopIval

    def pause(self):
        """Stop emitting + clear wash so telegraph / hit juice owns the frame."""
        self._paused = True
        if self._loopIval is not None:
            try:
                self._loopIval.pause()
            except Exception:
                pass
        self._clearPulse()

    def resume(self):
        """Resume silhouette cream wash after telegraph / hit recovery."""
        if not getattr(
                CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_ENABLED', True):
            return
        if self._parent is None:
            return
        try:
            if self._parent.isEmpty():
                return
        except Exception:
            return
        self._paused = False
        if self._loopIval is not None:
            try:
                self._loopIval.resume()
                return
            except Exception:
                pass
        self.start(
            self._parent,
            archetype=self._archetype,
            finaleLook=self._finaleLook,
        )

    def clear(self):
        self._paused = True
        if self._loopIval is not None:
            try:
                self._loopIval.pause()
            except Exception:
                pass
            self._loopIval = None
        self._clearPulse()
        self._parent = None
        self._look = None

    def _clearPulse(self):
        """Stop wash/aftershock and remove every cream silhouette-wash node."""
        if self._pulseIval is not None:
            try:
                self._pulseIval.pause()
            except Exception:
                pass
            self._pulseIval = None
        if self._washPlayIval is not None:
            try:
                self._washPlayIval.pause()
            except Exception:
                pass
            self._washPlayIval = None
        wash = self._washNP
        self._washNP = None
        if wash is not None:
            try:
                if not wash.isEmpty():
                    wash.removeNode()
            except Exception:
                pass
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in list(self._fleckNPs):
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._fleckNPs = []

    def _emitPulse(self):
        """One soft two-beat cream wash + delayed cream aftershock."""
        if self._paused or self._look is None:
            return
        self._clearPulse()
        try:
            aspectParent = aspect2d  # noqa: F821
        except Exception:
            return

        cream = getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = self._look.get('color') or (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(self._look.get(
            'peak',
            getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_PEAK', 0.05)))
        mid = float(self._look.get(
            'mid',
            getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_MID', 0.028)))
        inSec = float(self._look.get(
            'inSec',
            getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_IN_SEC', 0.07)))
        pulseSec = float(self._look.get(
            'pulseSec',
            getattr(
                CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_PULSE_SEC', 0.12)))
        holdSec = float(self._look.get(
            'holdSec',
            getattr(
                CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_HOLD_SEC', 0.10)))
        outSec = float(self._look.get(
            'outSec',
            getattr(
                CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_OUT_SEC', 0.48)))
        binSort = int(self._look.get(
            'binSort',
            getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_BIN', 37)))
        delay = float(self._look.get(
            'delaySec',
            getattr(
                CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_DELAY_SEC', 0.0)))
        delay = max(0.0, float(delay))

        try:
            cm = CardMaker('corrupt-silhouette-cream-wash')
            # Full-frame veil — idle / death / reclaim cream wash grammar.
            cm.setFrame(-2, 2, -2, 2)
            wash = aspectParent.attachNewNode(cm.generate())
            wash.setTransparency(TransparencyAttrib.MAlpha)
            wash.setColor(r, g, b, 1)
            wash.setColorScale(r, g, b, 0)
            wash.setBin('fixed', binSort)
            wash.setDepthTest(False)
            wash.setDepthWrite(False)
            self._washNP = wash
        except Exception:
            self._washNP = None
            return

        # Soft two-beat ambient pulse: bright → settle → fade (quieter than
        # death #119 / idle #146 — silhouette contrast against ink rim).
        washIval = Sequence(
            Wait(delay),
            LerpColorScaleInterval(
                wash, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            LerpColorScaleInterval(
                wash, max(0.01, pulseSec), Vec4(r, g, b, mid),
                blendType='easeInOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                wash, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
            name='corruptSilhouetteCreamWashVeil',
        )
        self._washPlayIval = washIval
        try:
            washIval.start()
        except Exception:
            self._clearPulse()
            return

        washDuration = delay + inSec + pulseSec + holdSec + outSec
        aftershock = self._buildAftershock()
        if aftershock is not None:
            # Wash Sequence already started; hold its lifetime beside aftershock.
            self._pulseIval = Sequence(
                Parallel(
                    Wait(washDuration + 0.04),
                    aftershock,
                ),
                Func(self._clearPulse),
                name='corruptSilhouetteCreamWashPulse',
            )
        else:
            self._pulseIval = Sequence(
                Wait(washDuration + 0.04),
                Func(self._clearPulse),
                name='corruptSilhouetteCreamWashPulse',
            )
        self._pulseIval.start()

    def _buildAftershock(self):
        """Delayed soft cream flecks (+ optional halo) after silhouette cream wash."""
        if not getattr(
                CorruptionGlobals,
                'SILHOUETTE_CREAM_WASH_AFTERSHOCK_ENABLED', True):
            return None
        parentNP = self._parent
        if parentNP is None:
            return None
        try:
            if parentNP.isEmpty():
                return None
        except Exception:
            return None

        lift = float(getattr(
            CorruptionGlobals, 'SILHOUETTE_CREAM_WASH_AFTERSHOCK_LIFT', 2.05))
        try:
            from toontown.corruption.CorruptSilhouetteCreamRimFx import (
                silhouetteCreamRimLook)
            rim = silhouetteCreamRimLook(
                self._archetype, finaleLook=self._finaleLook)
            # Slightly below rim lift so residual sits under rim / sparkle path.
            lift = float(rim.get('lift', lift)) * 0.55
        except Exception:
            pass
        origin = Point3(0.0, 0.0, lift)

        delay = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_DELAY_SEC', 0.32))
        parts = []

        if getattr(
                CorruptionGlobals,
                'SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = max(0, int(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_COUNT', 4)))
        fleckSec = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_SEC', 0.30))
        for i in range(creamCount):
            part = self._spawnAftershockFleck(
                parentNP, origin, i, creamCount, fleckSec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parentNP, origin):
        half = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_HALF', 0.42))
        startScale = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_START', 0.24))
        peakScale = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_PEAK', 1.25))
        sec = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_SEC', 0.26))
        peakA = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.10))
        r, g, b, _a = getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_BIN', 38))
        try:
            cm = CardMaker('corrupt-silhouette-cream-wash-aftershock-halo')
            # Soft oval halo under flecks — quieter ambient residual.
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            halo.setBin('fixed', binSort)
            halo.setDepthWrite(False)
            halo.setBillboardPointEye()
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

    def _spawnAftershockFleck(self, parentNP, origin, index, total, sec):
        """Softer cream chip that settles downward — residual wash aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_SIZE', 0.08))
        drift = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_DRIFT', 0.48))
        fall = float(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_FALL', 0.42))
        r, g, b, a = getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.58))
        er, eg, eb, ea = getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            CorruptionGlobals,
            'SILHOUETTE_CREAM_WASH_AFTERSHOCK_BIN', 38))
        angle = (2.0 * pi * index) / float(count) + 0.31
        try:
            cm = CardMaker(
                'corrupt-silhouette-cream-wash-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the cream wash.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.20, size * 1.20, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = origin[0] + cos(angle) * 0.10
            startY = origin[1] + sin(angle) * 0.10
            startZ = origin[2] + 0.03 * (index % 3)
            fleck.setPos(startX, startY, startZ)
            fleck.setScale(0.26 + 0.07 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return None

        # Settle downward — residual cream, not rising rim sparkles / fleck spray.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            startY + sin(angle) * drift * 0.55,
            startZ - fall - 0.06 * (index % 3))
        peak = size * (1.12 + 0.08 * (index % 2))
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
