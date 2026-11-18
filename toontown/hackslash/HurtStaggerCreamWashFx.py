"""Rubber-hose cream wash aftershock after player hurt stagger.

Fullscreen soft cream veil + residual flecks that settle *during* the
committed hurt stagger (#199 / #215) — HitSparkCreamWashPulse /
PerfectDodgeCreamWashPulse overlay grammar as a brief smack→recovery juice
beat so the hit still reads juicy before the F/Shift cancel window opens.
Deepened so getting hit and recovering reads juicier: brighter peak / longer
mid hold, plus a richer residual cream wash aftershock (more flecks + stronger
halo) that settles into the recovery cancel. Soft under HUD; cream / pastel
only (not ink). Distinct from dodge-cancel cream flash deepen (#242) — fires
on smack stagger, not Shift→F cancel — and from i-frame cream wash deepen
(#228) — settles during hurt lockout, not mid-roll invuln. Wired from
MeleeCombatController._armHurtRecoveryCancelWindow. Client only. Toontown
spiritual sequel — no keyblades / no KH branding.
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


class HurtStaggerCreamWashPulse(object):
    """Owns aspect2d cream wash pulse + residual wash aftershock on hurt."""

    def __init__(self):
        self._ival = None
        self._washPlayIval = None
        self._washNP = None
        self._fleckNPs = []
        self._haloNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash + aftershock. Returns Sequence or None."""
        if not getattr(
                HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_PEAK', 0.095))
        mid = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_MID', 0.055))
        inSec = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_IN_SEC', 0.04))
        pulseSec = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_PULSE_SEC', 0.09))
        holdSec = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_HOLD_SEC', 0.07))
        outSec = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_OUT_SEC', 0.34))
        binSort = int(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_BIN', 27))
        if delay is None:
            delay = float(getattr(
                HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_DELAY_SEC', 0.04))

        try:
            cm = CardMaker('hackslash-hurt-stagger-cream-wash')
            # Full-frame veil — hit / perfect-dodge / soft-lock wash grammar.
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

        # Early two-beat during committed stagger: bright → settle → fade.
        # Deepened peak + mid hold so smack→recovery reads juicier.
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
            name='hackslashHurtStaggerCreamWashVeil',
        )

        origin = getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_ORIGIN',
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
            name='hackslashHurtStaggerCreamWash',
        )
        self._ival.start()
        return self._ival

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after hurt cream wash."""
        if not getattr(
                HackSlashConfig,
                'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig,
            'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_DELAY_SEC', 0.10))
        parts = []

        if getattr(
                HackSlashConfig,
                'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_COUNT', 4))
        sec = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_SEC', 0.28))
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
            'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_HALF', 0.40))
        startScale = float(getattr(
            HackSlashConfig,
            'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_START', 0.24))
        peakScale = float(getattr(
            HackSlashConfig,
            'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_PEAK', 1.12))
        sec = float(getattr(
            HackSlashConfig,
            'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_SEC', 0.24))
        peakA = float(getattr(
            HackSlashConfig,
            'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.10))
        r, g, b, _a = getattr(
            HackSlashConfig,
            'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_BIN', 29))
        try:
            cm = CardMaker('hackslash-hurt-stagger-cream-wash-aftershock-halo')
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
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_SIZE', 0.013))
        drift = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_DRIFT', 0.22))
        fall = float(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_FALL', 0.18))
        r, g, b, a = getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.72))
        er, eg, eb, ea = getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            HackSlashConfig, 'HURT_STAGGER_CREAM_WASH_AFTERSHOCK_BIN', 29))
        angle = (2.0 * pi * index) / float(count) + 0.28
        try:
            cm = CardMaker(
                'hackslash-hurt-stagger-cream-wash-aftershock-%s' % index)
            # Alternate chip / cross / soft diamond — juicier residual settle.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.35, size * 1.35)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.35, size * 1.35, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size * 1.05, size * 1.05, -size * 0.90, size * 0.90)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = ox + cos(angle) * 0.08
            startZ = oz + 0.014 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.32 + 0.10 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream after the hurt wash pulse.
        end = Point3(
            startX + cos(angle) * drift * 0.60,
            oy,
            startZ - fall - 0.05 * (index % 3))
        peak = 1.12 + 0.10 * (index % 2)
        self._fleckNPs.append(fleck)
        stagger = 0.014 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.06, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.30), peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(
                    fleck, max(0.01, sec * 0.70), end, blendType='easeIn'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.70), 0.04, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.70), Vec4(er, eg, eb, ea),
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
