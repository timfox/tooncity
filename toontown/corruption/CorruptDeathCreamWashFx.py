"""Rubber-hose cream wash pulse + delayed cream aftershock after death flecks.

Fullscreen soft cream veil that settles *after* the sunny death fleck burst —
PurityCompleteCreamWashFx / EntryCreamWashPulseFx overlay grammar as a brief
defeat wash. A delayed cream aftershock (softer flecks settling downward +
soft halo) follows the wash — same residual grammar as entry cream wash
aftershock (#132) and purity-complete cream aftershock (#136); world-space
settle matches telegraph cream warn aftershock (#121). Soft under world-space
flecks + rising death cream sparkles; cream / pastel only (not ink). Wired
from DeathPopSplat.play beside DeathCreamFleckBurst + DeathCreamSparkles.
Client only. Toontown spiritual sequel — no keyblades / no KH branding.
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


class DeathCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse + delayed cream aftershock."""

    def __init__(self):
        self._ival = None
        self._washPlayIval = None
        self._washNP = None
        self._haloNP = None
        self._fleckNPs = []

    def play(self, delay=None, pos=None, parent=None, archetype=None):
        """Arm delayed two-beat cream wash + aftershock. Returns Sequence or None."""
        if not getattr(CorruptionGlobals, 'DEATH_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            aspectParent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(CorruptionGlobals, 'DEATH_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_PEAK', 0.14))
        mid = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_MID', 0.08))
        inSec = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_IN_SEC', 0.06))
        pulseSec = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_PULSE_SEC', 0.10))
        holdSec = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_HOLD_SEC', 0.08))
        outSec = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_OUT_SEC', 0.42))
        binSort = int(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_BIN', 38))
        if delay is None:
            delay = float(getattr(
                CorruptionGlobals, 'DEATH_CREAM_WASH_DELAY_SEC', 0.20))
        delay = max(0.0, float(delay))

        try:
            cm = CardMaker('corrupt-death-cream-wash')
            # Full-frame veil — reclaim purity / entry cream wash grammar.
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
            return None

        # Delayed two-beat after fleck burst: bright pop → soft settle → fade.
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
            name='corruptDeathCreamWashVeil',
        )
        self._washPlayIval = washIval
        try:
            washIval.start()
        except Exception:
            self.clear()
            return None

        washLifetime = (
            delay + inSec + pulseSec + holdSec + outSec)
        aftershock = self._buildAftershock(
            pos, parent=parent, archetype=archetype)
        if aftershock is not None:
            # Wash Sequence already started; hold its lifetime beside aftershock.
            self._ival = Sequence(
                Parallel(
                    Wait(washLifetime + 0.04),
                    aftershock,
                ),
                Func(self.clear),
                name='corruptDeathCreamWash',
            )
        else:
            self._ival = Sequence(
                Wait(washLifetime + 0.04),
                Func(self.clear),
                name='corruptDeathCreamWash',
            )
        self._ival.start()
        return self._ival

    def _buildAftershock(self, pos, parent=None, archetype=None):
        """Delayed soft cream flecks (+ optional halo) after death cream wash."""
        if not getattr(
                CorruptionGlobals,
                'DEATH_CREAM_WASH_AFTERSHOCK_ENABLED', True):
            return None
        if pos is None:
            return None

        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None

        lift = float(getattr(
            CorruptionGlobals, 'DEATH_CREAM_WASH_AFTERSHOCK_LIFT', 1.35))
        try:
            from toontown.corruption.CorruptDeathCreamFleckFx import (
                deathCreamFleckLook)
            fleck = deathCreamFleckLook(archetype)
            lift = float(fleck.get('lift', lift))
        except Exception:
            pass
        try:
            origin = Point3(
                float(pos[0]), float(pos[1]), float(pos[2]) + lift)
        except Exception:
            origin = Point3(0, 0, lift)

        delay = float(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_DELAY_SEC', 0.36))
        parts = []

        if getattr(
                CorruptionGlobals,
                'DEATH_CREAM_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = max(0, int(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_COUNT', 5)))
        fleckSec = float(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_SEC', 0.34))
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
            'DEATH_CREAM_WASH_AFTERSHOCK_HALO_HALF', 0.50))
        startScale = float(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_HALO_START', 0.28))
        peakScale = float(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_HALO_PEAK', 1.45))
        sec = float(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_HALO_SEC', 0.30))
        peakA = float(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.22))
        r, g, b, _a = getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_BIN', 46))
        try:
            cm = CardMaker('corrupt-death-cream-wash-aftershock-halo')
            # Soft oval halo under flecks / rising sparkles — quieter residual.
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
            'DEATH_CREAM_WASH_AFTERSHOCK_SIZE', 0.12))
        drift = float(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_DRIFT', 0.65))
        fall = float(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_FALL', 0.55))
        r, g, b, a = getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.80))
        er, eg, eb, ea = getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            CorruptionGlobals,
            'DEATH_CREAM_WASH_AFTERSHOCK_BIN', 46))
        angle = (2.0 * pi * index) / float(count) + 0.31
        try:
            cm = CardMaker(
                'corrupt-death-cream-wash-aftershock-%s' % index)
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
            startX = origin[0] + cos(angle) * 0.12
            startY = origin[1] + sin(angle) * 0.12
            startZ = origin[2] + 0.04 * (index % 3)
            fleck.setPos(startX, startY, startZ)
            fleck.setScale(0.28 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return None

        # Settle downward — residual cream, not rising death sparkles / fleck spray.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            startY + sin(angle) * drift * 0.55,
            startZ - fall - 0.08 * (index % 3))
        peak = size * (1.15 + 0.1 * (index % 2))
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

    def clear(self):
        """Stop wash/aftershock and remove every cream death-wash node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
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
