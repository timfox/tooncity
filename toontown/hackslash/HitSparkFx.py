"""Rubber-hose cream/ink fleck sparkles on melee hit connect.

Client juice when a stretch-punch lands: short cream spark streaks + ink
flecks burst at the hit, then a delayed cream spark aftershock, then a soft
cream wash pulse + residual cream wash aftershock — layered with the
existing impact squash silhouette. Cream aftershock + wash + wash aftershock
are pastel-only (no ink). Toontown spiritual-sequel tone only — no keyblades /
no KH branding.
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

from . import HackSlashConfig
from . import HitJuice
from .HitSparkCreamWashFx import HitSparkCreamWashPulse


class HitSparkFx(object):
    """Owns spark burst + cream aftershock + cream wash + wash aftershock."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._fleckIval = None
        self._nodes = []
        self._haloNP = None
        self._creamWash = None

    def play(self, origin=None, hitIndex=0, parent=None):
        """Spawn cream/ink flecks + cream aftershock + delayed cream wash aftershock.

        Returns started Sequence or None. `origin` is render-space; defaults
        to the local avatar at HIT_SPARK_LIFT.
        """
        if not getattr(HackSlashConfig, 'HIT_SPARK_ENABLED', True):
            return None
        self.clear()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None

        if origin is None:
            try:
                pos = self.avatar.getPos(parentNP)
                origin = Point3(
                    pos[0], pos[1],
                    pos[2] + float(HackSlashConfig.HIT_SPARK_LIFT))
            except Exception:
                return None
        else:
            try:
                origin = Point3(
                    float(origin[0]), float(origin[1]), float(origin[2]))
            except Exception:
                return None

        fleckIval, nodes = HitJuice.spawnHitSparkFlecks(
            origin,
            hitIndex=hitIndex,
            parent=parentNP,
            name=self.avatar.uniqueName('hackslashHitSparkFlecks'))
        if fleckIval is None and not nodes:
            return None

        self._fleckIval = fleckIval
        self._nodes = list(nodes)

        try:
            fleckSec = float(HackSlashConfig.HIT_SPARK_SEC)
        except Exception:
            fleckSec = 0.2

        # Residual cream spark aftershock after the initial fleck burst settles.
        aftershock = self._buildAftershock(parentNP, origin, hitIndex)
        if aftershock is not None:
            # Fleck Parallel already started; hold its lifetime beside aftershock.
            burst = Parallel(
                Wait(fleckSec + 0.02),
                aftershock,
            )
        else:
            burst = Wait(fleckSec + 0.02)

        # Soft cream wash pulse + wash aftershock — perfect-dodge grammar (#171).
        washHold = 0.0
        try:
            wash = HitSparkCreamWashPulse()
            if wash.play() is not None:
                self._creamWash = wash
                # Hold teardown beside delayed wash + residual aftershock so
                # clear() doesn't kill the veil/flecks mid-pulse (wash
                # self-clears too).
                washDuration = (
                    float(getattr(
                        HackSlashConfig, 'HIT_SPARK_CREAM_WASH_IN_SEC',
                        0.05))
                    + float(getattr(
                        HackSlashConfig, 'HIT_SPARK_CREAM_WASH_PULSE_SEC',
                        0.09))
                    + float(getattr(
                        HackSlashConfig, 'HIT_SPARK_CREAM_WASH_HOLD_SEC',
                        0.06))
                    + float(getattr(
                        HackSlashConfig, 'HIT_SPARK_CREAM_WASH_OUT_SEC',
                        0.34)))
                aftershockTail = 0.0
                if getattr(
                        HackSlashConfig,
                        'HIT_SPARK_CREAM_WASH_AFTERSHOCK_ENABLED', True):
                    aftershockTail = (
                        float(getattr(
                            HackSlashConfig,
                            'HIT_SPARK_CREAM_WASH_AFTERSHOCK_DELAY_SEC',
                            0.22))
                        + float(getattr(
                            HackSlashConfig,
                            'HIT_SPARK_CREAM_WASH_AFTERSHOCK_SEC',
                            0.28))
                        + 0.05)
                washHold = (
                    float(getattr(
                        HackSlashConfig, 'HIT_SPARK_CREAM_WASH_DELAY_SEC',
                        0.36))
                    + max(washDuration, aftershockTail)
                    + 0.04)
            else:
                self._creamWash = None
        except Exception:
            self._creamWash = None

        hold = [burst]
        if washHold > 0.0:
            hold.append(Wait(washHold))

        self._ival = Sequence(
            Parallel(*hold),
            Func(self.clear),
            name=self.avatar.uniqueName('hackslashHitSpark'),
        )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop burst/aftershock/wash/wash-aftershock; remove fleck/halo/wash nodes."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        wash = self._creamWash
        self._creamWash = None
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        if self._fleckIval is not None:
            try:
                self._fleckIval.pause()
            except Exception:
                pass
            self._fleckIval = None
        if self._haloNP is not None:
            self._retireNode(self._haloNP)
            self._haloNP = None
        HitJuice.clearHitSparkFlecks(self._nodes)
        self._nodes = []

    def _buildAftershock(self, parentNP, origin, hitIndex):
        """Delayed soft cream sparks (+ optional halo) after the fleck pop."""
        if not getattr(
                HackSlashConfig, 'HIT_SPARK_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig, 'HIT_SPARK_CREAM_AFTERSHOCK_DELAY_SEC', 0.18))
        parts = []

        if getattr(
                HackSlashConfig,
                'HIT_SPARK_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = int(self._tablePick(
            getattr(
                HackSlashConfig, 'HIT_SPARK_CREAM_AFTERSHOCK_COUNT', (3, 4, 5)),
            hitIndex))
        streakCount = int(self._tablePick(
            getattr(
                HackSlashConfig,
                'HIT_SPARK_CREAM_AFTERSHOCK_STREAK_COUNT', (1, 2, 2)),
            hitIndex))
        for i in range(creamCount):
            part = self._spawnAftershockSpark(
                parentNP, origin, i, creamCount, elongated=False)
            if part is not None:
                parts.append(part)
        for i in range(streakCount):
            part = self._spawnAftershockSpark(
                parentNP, origin, i, streakCount, elongated=True)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parentNP, origin):
        half = float(HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_HALO_HALF)
        startScale = float(
            HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_HALO_START)
        peakScale = float(HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_HALO_PEAK)
        sec = float(HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_HALO_SEC)
        peakA = float(
            HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA)
        r, g, b, _a = HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_HALO_COLOR
        try:
            cm = CardMaker('hackslash-hit-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            halo.setBin('transparent', 22)
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

    def _spawnAftershockSpark(self, parentNP, origin, index, total,
                              elongated=False):
        """Softer cream spark that settles downward — residual aftershock."""
        count = max(1, int(total))
        if elongated:
            size = float(
                HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_STREAK_SIZE)
            r, g, b, a = HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_STREAK_COLOR
            er, eg, eb, ea = (
                HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_STREAK_END)
            nameSuffix = 'streak'
            angleBias = 0.55
        else:
            size = float(HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_SIZE)
            r, g, b, a = HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_COLOR
            er, eg, eb, ea = HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_END
            nameSuffix = 'cream'
            angleBias = 0.22
        drift = float(HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_DRIFT)
        sec = float(HackSlashConfig.HIT_SPARK_CREAM_AFTERSHOCK_SEC)
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            cm = CardMaker(
                'hackslash-hit-cream-aftershock-%s-%s' % (nameSuffix, index))
            if elongated:
                cm.setFrame(
                    -size * 0.35, size * 0.35,
                    -size * 1.15, size * 1.15)
            else:
                cm.setFrame(
                    -size, size, -size * 0.85, size * 0.85)
            spark = parentNP.attachNewNode(cm.generate())
            spark.setTransparency(TransparencyAttrib.MAlpha)
            spark.setColor(r, g, b, 1)
            spark.setColorScale(r, g, b, 0)
            spark.setPos(
                origin[0] + cos(angle) * 0.1,
                origin[1] + sin(angle) * 0.1,
                origin[2] + 0.03 * (index % 2))
            spark.setScale(0.28 + 0.08 * (index % 3))
            spark.setBin('transparent', 25)
            spark.setDepthWrite(False)
            spark.setBillboardPointEye()
        except Exception:
            return None

        # Settle downward — residual cream, not the initial outward glitter.
        end = Point3(
            origin[0] + cos(angle) * drift * 0.55,
            origin[1] + sin(angle) * drift * 0.55,
            origin[2] - 0.5 - 0.1 * (index % 3))
        peak = size * (1.2 + 0.1 * (index % 2))
        self._nodes.append(spark)
        stagger = 0.02 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    spark, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    spark, sec * 0.28, peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(spark, sec * 0.72, end, blendType='easeIn'),
                LerpScaleInterval(
                    spark, sec * 0.72, 0.04, blendType='easeIn'),
                LerpColorScaleInterval(
                    spark, sec * 0.72, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def _tablePick(self, table, hitIndex):
        """Pick a per-hit tunable; scalars still work for older configs."""
        if isinstance(table, (int, float)):
            return float(table)
        return float(table[min(max(0, int(hitIndex)), len(table) - 1)])

    def _retireNode(self, np):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass
