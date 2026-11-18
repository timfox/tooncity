"""Rubber-hose cream wash pulse after dodge i-frame cream/ink pulse.

Fullscreen soft cream veil that settles *after* DodgeTrailFx i-frame
cream/ink pulse (#66 / #166 / #228) — SoftLockFovCreamWashPulse (#160) /
SoftLockCreamWashPulse (#155) / DodgeTrailCreamWashPulse (#139) overlay
grammar as a brief i-frame settle beat so invuln windows read clearly.
Deepened past #228 so dodge invuln reads juicier still: brighter peak /
longer mid hold, plus a richer residual cream wash aftershock (more flecks
+ stronger halo). Soft under / at most equal to trail wash (#139); cream /
pastel only (not ink). Distinct from hurt-stagger cream wash deepen
(#247 / #263) — mid-roll invuln, not smack lockout — and from dodge-cancel
cream flash (#242 / #257). Wired from DodgeTrailFx._spawnPulse on the
first pulse of a dodge so wash follows a real pulse. Client only.
Toontown spiritual sequel — no keyblades / no KH branding.
"""

from math import cos, pi

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

from . import HackSlashConfig


class DodgeIFrameCreamWashPulse(object):
    """Owns aspect2d cream wash pulse + residual wash aftershock on i-frame."""

    def __init__(self):
        self._ival = None
        self._washPlayIval = None
        self._washNP = None
        self._fleckNPs = []
        self._haloNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash + aftershock. Returns Sequence or None."""
        if not getattr(
                HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_PEAK', 0.098))
        mid = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_MID', 0.065))
        inSec = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_IN_SEC', 0.05))
        pulseSec = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_PULSE_SEC', 0.10))
        holdSec = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_HOLD_SEC', 0.10))
        outSec = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_OUT_SEC', 0.36))
        binSort = int(getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_BIN', 27))
        if delay is None:
            delay = float(getattr(
                HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_DELAY_SEC',
                0.16))

        try:
            cm = CardMaker('hackslash-dodge-iframe-cream-wash')
            # Full-frame veil — FOV / reticle / trail wash grammar.
            cm.setFrame(-2, 2, -2, 2)
            wash = parent.attachNewNode(cm.generate())
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

        # Delayed two-beat after first i-frame pulse: bright → settle → fade.
        # Deepened-past peak + mid hold so invuln still reads juicier mid-roll.
        washVeil = Sequence(
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
            name='hackslashDodgeIFrameCreamWashVeil',
        )

        origin = getattr(
            HackSlashConfig, 'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ORIGIN',
            (0.0, 0.0, -0.08))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.08

        aftershock = self._buildAftershock(parent, ox, oy, oz)

        # Arm wash + residual aftershock after the shared delay from play.
        if aftershock is not None:
            body = Parallel(
                washVeil,
                aftershock,
            )
        else:
            body = washVeil

        self._washPlayIval = None
        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            body,
            Wait(0.04),
            Func(self.clear),
            name='hackslashDodgeIFrameCreamWash',
        )
        self._ival.start()
        return self._ival

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after i-frame cream wash."""
        if not getattr(
                HackSlashConfig,
                'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_DELAY_SEC', 0.10))
        parts = []

        if getattr(
                HackSlashConfig,
                'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_COUNT', 4))
        sec = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_SEC', 0.28))
        for i in range(count):
            part = self._spawnAftershockFleck(
                parent, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parent, ox, oy, oz):
        half = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_HALF', 0.38))
        startScale = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_START', 0.20))
        peakScale = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_PEAK', 1.10))
        sec = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_SEC', 0.22))
        peakA = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.09))
        r, g, b, _a = getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_BIN', 29))
        try:
            cm = CardMaker(
                'hackslash-dodge-iframe-cream-wash-aftershock-halo')
            # Soft oval halo under HUD — quieter residual of the wash veil.
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

    def _spawnAftershockFleck(self, parent, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles downward — residual wash aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_SIZE', 0.013))
        drift = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_DRIFT', 0.22))
        fall = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_FALL', 0.18))
        r, g, b, a = getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.72))
        er, eg, eb, ea = getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_PULSE_CREAM_WASH_AFTERSHOCK_BIN', 29))
        angle = (2.0 * pi * index) / float(count) + 0.28
        try:
            cm = CardMaker(
                'hackslash-dodge-iframe-cream-wash-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the cream wash.
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

        # Settle downward — residual cream after the i-frame wash pulse.
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

    def clear(self):
        """Stop wash/aftershock and remove every cream wash node."""
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
        for np in self._fleckNPs:
            if np is not None:
                try:
                    if not np.isEmpty():
                        np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []
