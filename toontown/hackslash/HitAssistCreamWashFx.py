"""Rubber-hose cream wash on soft-lock hit-assist aim nudge.

Fullscreen soft cream veil that flashes *when* melee connect against the
sticky soft-lock fires the one-shot yaw/aim nudge (#204 / #254 / #278
deepen+) — SoftLock FOV / SoftLockCycle / DodgeCancel cream wash overlay
grammar as a brief glue-assist juice beat so hit assist reads juicier still.
Deepened past #278: brighter peak / longer mid hold, plus a richer residual
cream wash aftershock (more flecks + stronger halo). Soft under HUD; cream /
pastel only (not ink). Quieter/faster than hit-spark cream wash (#147) so
combo strings stay readable; distinct from soft-lock cycle reticle cream
deepen (#233) — fires on connect assist, not Tab/` cycle — from hurt wash
cream deepen (#247 / #263 / #287) — player landing soft-lock hits, not
getting smacked — and from i-frame cream wash (#296), combo edge cream
(#291), and dodge-cancel cream flash (#281). Wired from
MeleeCombatController._assistAimOnHit when a real yaw nudge lands. Client
only. Toontown spiritual sequel — no keyblades / no KH branding.
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


class HitAssistCreamWashPulse(object):
    """Owns aspect2d cream wash flash + residual aftershock on hit-assist nudge."""

    def __init__(self):
        self._ival = None
        self._washPlayIval = None
        self._washNP = None
        self._fleckNPs = []
        self._haloNP = None

    def play(self, delay=None):
        """Arm snappy two-beat cream wash + aftershock. Returns Sequence or None."""
        if not getattr(
                HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_PEAK', 0.098))
        mid = float(getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_MID', 0.062))
        inSec = float(getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_IN_SEC', 0.03))
        pulseSec = float(getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_PULSE_SEC', 0.09))
        holdSec = float(getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_HOLD_SEC', 0.06))
        outSec = float(getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_OUT_SEC', 0.28))
        binSort = int(getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_BIN', 26))
        if delay is None:
            delay = float(getattr(
                HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_DELAY_SEC', 0.0))

        try:
            cm = CardMaker('hackslash-hit-assist-cream-wash')
            # Full-frame veil — soft-lock FOV / cycle / dodge-cancel grammar.
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

        # Immediate snappy flash on assist nudge: bright → settle → fade.
        # Deepened past #278 peak + mid so soft-lock connect glue reads juicier.
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
            name='hackslashHitAssistCreamWashVeil',
        )

        origin = getattr(
            HackSlashConfig, 'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_ORIGIN',
            (0.0, 0.0, 0.04))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.04

        aftershock = self._buildAftershock(parent, ox, oy, oz)

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
            Wait(0.03),
            Func(self.clear),
            name='hackslashHitAssistCreamWash',
        )
        self._ival.start()
        return self._ival

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after assist cream flash."""
        if not getattr(
                HackSlashConfig,
                'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_DELAY_SEC', 0.03))
        parts = []

        if getattr(
                HackSlashConfig,
                'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_COUNT', 5))
        sec = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_SEC', 0.22))
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
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_HALF', 0.38))
        startScale = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_START', 0.20))
        peakScale = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_PEAK', 1.22))
        sec = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_SEC', 0.18))
        peakA = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.11))
        r, g, b, _a = getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_BIN', 28))
        try:
            cm = CardMaker(
                'hackslash-hit-assist-cream-wash-aftershock-halo')
            # Soft oval halo — quiet residual of the aim-nudge cream flash.
            cm.setFrame(-half, half, -half * 0.48, half * 0.48)
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
                Wait(max(0.0, sec * 0.18)),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.82), Vec4(r, g, b, 0),
                    blendType='easeIn'),
            ),
        )

    def _spawnAftershockFleck(self, parent, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles after the assist cream flash."""
        count = max(1, int(total))
        size = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_SIZE', 0.015))
        drift = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_DRIFT', 0.22))
        fall = float(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_FALL', 0.145))
        r, g, b, a = getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.78))
        er, eg, eb, ea = getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            HackSlashConfig,
            'LOCK_HIT_ASSIST_CREAM_WASH_AFTERSHOCK_BIN', 28))
        angle = (2.0 * pi * index) / float(count) + 0.22
        try:
            cm = CardMaker(
                'hackslash-hit-assist-cream-wash-aftershock-%s' % index)
            # Alternate chip / cross — residual of the aim-nudge cream flash.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.15, size * 1.15)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.15, size * 1.15, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.80, size * 0.80)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = ox + cos(angle) * 0.08
            startZ = oz + 0.012 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.30 + 0.07 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle outward/down — residual cream after the assist flash.
        end = Point3(
            startX + cos(angle) * drift * 0.60,
            oy,
            startZ - fall - 0.030 * (index % 3))
        peak = 1.05 + 0.07 * (index % 2)
        self._fleckNPs.append(fleck)
        stagger = 0.010 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.035, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.24), peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(
                    fleck, max(0.01, sec * 0.76), end, blendType='easeIn'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.76), 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.76), Vec4(er, eg, eb, ea),
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
