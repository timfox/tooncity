"""Rubber-hose cream sparkle during air-juggle hang.

World-space cream flecks + soft cream halo at the launcher apex so suspended
corrupt toons read before fall, then a delayed cream aftershock (softer flecks
+ residual halo) settles — same residual grammar as perfect-dodge / hit cream
aftershock. Layers with HitJuice hang hover/squash and does not fight
CreamSlamFlashFx (aspect2d finisher connect flash). Toontown spiritual-sequel
tone only — no keyblades / no KH branding.
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


class CreamHangSparkleFx(object):
    """Owns cream hang sparkle burst + delayed cream aftershock at apex."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._sparkleIval = None
        self._nodes = []
        self._haloNP = None

    def play(self, origin=None, hitIndex=0, parent=None):
        """Spawn cream hang sparkles + delayed cream aftershock.

        Returns started Sequence or None. `origin` is render-space hang peak.
        Falls back to classic hang sparks when LAUNCH_HANG_CREAM_ENABLED is
        False (no aftershock on the classic path).
        """
        self.clear()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None

        if origin is None:
            return None
        try:
            origin = Point3(
                float(origin[0]), float(origin[1]), float(origin[2]))
        except Exception:
            return None

        useCream = getattr(
            HackSlashConfig, 'LAUNCH_HANG_CREAM_ENABLED', True)
        if useCream:
            sparkleIval, nodes = HitJuice.spawnCreamHangSparkles(
                origin,
                hitIndex=hitIndex,
                parent=parentNP,
                name=self.avatar.uniqueName('hackslashCreamHangSparkles'))
        else:
            sparkleIval, nodes = HitJuice.spawnHangSparks(
                origin,
                parent=parentNP,
                name=self.avatar.uniqueName('hackslashHangSparks'))

        if sparkleIval is None and not nodes:
            return None

        self._sparkleIval = sparkleIval
        self._nodes = list(nodes)
        # Cream path starts inside HitJuice; classic hang sparks need a start.
        if sparkleIval is not None and not useCream:
            try:
                sparkleIval.start()
            except Exception:
                HitJuice.clearCreamHangSparkles(nodes)
                self._sparkleIval = None
                self._nodes = []
                return None
        try:
            if useCream:
                sec = float(HackSlashConfig.LAUNCH_HANG_CREAM_SEC)
            else:
                sec = float(HackSlashConfig.LAUNCH_HANG_SPARK_SEC)
        except Exception:
            sec = 0.28

        # Residual cream aftershock after the apex hang sparkle settles.
        aftershock = None
        if useCream:
            aftershock = self._buildAftershock(parentNP, origin, hitIndex)
        if aftershock is not None:
            # Sparkle Parallel already started; hold its lifetime beside aftershock.
            self._ival = Sequence(
                Parallel(
                    Wait(sec + 0.04),
                    aftershock,
                ),
                Func(self.clear),
                name=self.avatar.uniqueName('hackslashCreamHangSparkle'),
            )
        else:
            self._ival = Sequence(
                Wait(sec + 0.04),
                Func(self.clear),
                name=self.avatar.uniqueName('hackslashCreamHangSparkle'),
            )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop the burst/aftershock and remove every cream hang node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._sparkleIval is not None:
            try:
                self._sparkleIval.pause()
            except Exception:
                pass
            self._sparkleIval = None
        if self._haloNP is not None:
            self._retireNode(self._haloNP)
            self._haloNP = None
        HitJuice.clearCreamHangSparkles(self._nodes)
        self._nodes = []

    def _buildAftershock(self, parentNP, origin, hitIndex):
        """Delayed soft cream flecks (+ optional halo) after hang sparkle."""
        if not getattr(
                HackSlashConfig, 'LAUNCH_HANG_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig, 'LAUNCH_HANG_CREAM_AFTERSHOCK_DELAY_SEC', 0.2))
        parts = []

        if getattr(
                HackSlashConfig,
                'LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = int(self._tablePick(
            getattr(
                HackSlashConfig,
                'LAUNCH_HANG_CREAM_AFTERSHOCK_COUNT', (0, 3, 4)),
            hitIndex))
        streakCount = int(self._tablePick(
            getattr(
                HackSlashConfig,
                'LAUNCH_HANG_CREAM_AFTERSHOCK_STREAK_COUNT', (0, 1, 2)),
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
        half = float(HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_HALF)
        startScale = float(
            HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_START)
        peakScale = float(
            HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_PEAK)
        sec = float(HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_SEC)
        peakA = float(
            HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA)
        r, g, b, _a = HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_HALO_COLOR
        lift = float(getattr(
            HackSlashConfig, 'LAUNCH_HANG_CREAM_LIFT', 0.55))
        try:
            cm = CardMaker('hackslash-hang-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin[0], origin[1], origin[2] + lift * 0.1)
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
        """Softer cream fleck / streak that settles — residual hang aftershock."""
        count = max(1, int(total))
        if elongated:
            size = float(
                HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_STREAK_SIZE)
            r, g, b, a = (
                HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_STREAK_COLOR)
            er, eg, eb, ea = (
                HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_STREAK_END)
            nameSuffix = 'streak'
            angleBias = 0.55
        else:
            size = float(HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_SIZE)
            r, g, b, a = HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_COLOR
            er, eg, eb, ea = HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_END
            nameSuffix = 'cream'
            angleBias = 0.22
        drift = float(HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_DRIFT)
        sec = float(HackSlashConfig.LAUNCH_HANG_CREAM_AFTERSHOCK_SEC)
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            cm = CardMaker(
                'hackslash-hang-cream-aftershock-%s-%s' % (nameSuffix, index))
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

        # Settle downward — residual cream, not the apex outward glitter.
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
