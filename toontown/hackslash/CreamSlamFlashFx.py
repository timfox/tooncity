"""Rubber-hose cream slam flash on combo-finisher connect.

Warm cream aspect2d flash + expanding cream ring when the 3rd stretch-punch
slam lands, then a delayed cream sparkle hang (soft veil + flecks/streaks)
so the slam settles sunny — same residual grammar as HitSparkFx cream
aftershock. Layers with SlamDustFx (feet thud), HitJuice finisher slam scale,
HitStopFx freeze (flash reads during the stick), and soft-lock FOV (#74) —
finisher FOV still owns the lens after resume. Toontown spiritual-sequel tone
only — no keyblades / no KH branding.
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


class CreamSlamFlashFx(object):
    """Owns cream screen flash + ring, then delayed cream sparkle hang."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._flashNP = None
        self._ringNP = None
        self._hangVeilNP = None
        self._hangNodes = []

    def play(self):
        """Spawn cream flash + ring, then delayed sparkle hang.

        Returns started Sequence or None.
        """
        if not getattr(HackSlashConfig, 'FINISHER_CREAM_SLAM_FLASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        r, g, b, _a = HackSlashConfig.FINISHER_CREAM_SLAM_FLASH_COLOR
        binSort = int(HackSlashConfig.FINISHER_CREAM_SLAM_FLASH_BIN)
        parts = []

        flashPart = self._spawnFlash(parent, r, g, b, binSort)
        if flashPart is not None:
            parts.append(flashPart)

        ringPart = self._spawnRing(parent, r, g, b, binSort)
        if ringPart is not None:
            parts.append(ringPart)

        if not parts:
            return None

        hang = self._buildSparkleHang(parent)
        if hang is not None:
            # Flash/ring Parallel already owns the connect punch; hang rides
            # beside it so residual cream lingers after the slam settles.
            self._ival = Sequence(
                Parallel(
                    Parallel(*parts),
                    hang,
                ),
                Func(self.clear),
                name=self.avatar.uniqueName('hackslashCreamSlamFlash'),
            )
        else:
            self._ival = Sequence(
                Parallel(*parts),
                Func(self.clear),
                name=self.avatar.uniqueName('hackslashCreamSlamFlash'),
            )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop the flash/hang and remove cream nodes."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        for attr in ('_flashNP', '_ringNP', '_hangVeilNP'):
            np = getattr(self, attr, None)
            setattr(self, attr, None)
            self._retireNode(np)
        for np in self._hangNodes:
            self._retireNode(np)
        self._hangNodes = []

    def _spawnFlash(self, parent, r, g, b, binSort):
        peak = float(HackSlashConfig.FINISHER_CREAM_SLAM_FLASH_PEAK)
        inSec = float(HackSlashConfig.FINISHER_CREAM_SLAM_FLASH_IN_SEC)
        holdSec = float(HackSlashConfig.FINISHER_CREAM_SLAM_FLASH_HOLD_SEC)
        outSec = float(HackSlashConfig.FINISHER_CREAM_SLAM_FLASH_OUT_SEC)
        try:
            cm = CardMaker('hackslash-cream-slam-flash')
            cm.setFrame(-2.0, 2.0, -2.0, 2.0)
            flash = parent.attachNewNode(cm.generate())
            flash.setTransparency(TransparencyAttrib.MAlpha)
            flash.setColor(r, g, b, 1)
            flash.setColorScale(r, g, b, 0)
            flash.setBin('fixed', binSort)
            flash.setDepthTest(False)
            flash.setDepthWrite(False)
            self._flashNP = flash
        except Exception:
            self._flashNP = None
            return None
        return Sequence(
            LerpColorScaleInterval(
                flash, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                flash, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
        )

    def _spawnRing(self, parent, r, g, b, binSort):
        if not getattr(HackSlashConfig, 'FINISHER_CREAM_SLAM_RING_ENABLED', True):
            return None
        half = float(HackSlashConfig.FINISHER_CREAM_SLAM_RING_HALF)
        startScale = float(HackSlashConfig.FINISHER_CREAM_SLAM_RING_START)
        peakScale = float(HackSlashConfig.FINISHER_CREAM_SLAM_RING_PEAK)
        sec = float(HackSlashConfig.FINISHER_CREAM_SLAM_RING_SEC)
        peakA = float(HackSlashConfig.FINISHER_CREAM_SLAM_RING_PEAK_ALPHA)
        oz = float(HackSlashConfig.FINISHER_CREAM_SLAM_RING_Z)
        try:
            cm = CardMaker('hackslash-cream-slam-ring')
            cm.setFrame(-half, half, -half, half)
            ring = parent.attachNewNode(cm.generate())
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setColor(r, g, b, 1)
            ring.setColorScale(r, g, b, peakA)
            ring.setPos(0.0, 0.0, oz)
            ring.setScale(startScale)
            ring.setBin('fixed', binSort + 1)
            ring.setDepthTest(False)
            ring.setDepthWrite(False)
            self._ringNP = ring
        except Exception:
            self._ringNP = None
            return None
        return Parallel(
            LerpScaleInterval(
                ring, max(0.01, sec), peakScale, blendType='easeOut'),
            Sequence(
                Wait(max(0.0, sec * 0.25)),
                LerpColorScaleInterval(
                    ring, max(0.01, sec * 0.75), Vec4(r, g, b, 0),
                    blendType='easeIn'),
            ),
        )

    def _buildSparkleHang(self, parent):
        """Delayed soft cream veil + flecks after the slam flash settles."""
        if not getattr(
                HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_DELAY_SEC', 0.24))
        parts = []

        veil = self._spawnHangVeil(parent)
        if veil is not None:
            parts.append(veil)

        creamCount = int(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_COUNT', 6))
        streakCount = int(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_STREAK_COUNT', 3))
        for i in range(creamCount):
            part = self._spawnHangSpark(
                parent, i, creamCount, elongated=False)
            if part is not None:
                parts.append(part)
        for i in range(streakCount):
            part = self._spawnHangSpark(
                parent, i, streakCount, elongated=True)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnHangVeil(self, parent):
        """Soft mid-screen cream veil — residual hang, not a second flash."""
        if not getattr(
                HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_VEIL_ENABLED',
                True):
            return None
        r, g, b, _a = getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_VEIL_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        peak = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_VEIL_PEAK', 0.14))
        inSec = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_VEIL_IN_SEC', 0.07))
        holdSec = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_VEIL_HOLD_SEC', 0.22))
        outSec = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_VEIL_OUT_SEC', 0.36))
        binSort = int(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_BIN', 59))
        oz = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_ORIGIN_Z', 0.04))
        try:
            cm = CardMaker('hackslash-cream-slam-sparkle-hang-veil')
            # Open center band — hang glitter bed under the slam flash bin.
            cm.setFrame(-1.45, 1.45, -0.55, 0.52)
            veil = parent.attachNewNode(cm.generate())
            veil.setTransparency(TransparencyAttrib.MAlpha)
            veil.setColor(r, g, b, 1)
            veil.setColorScale(r, g, b, 0)
            veil.setPos(0.0, 0.0, oz)
            veil.setBin('fixed', binSort)
            veil.setDepthTest(False)
            veil.setDepthWrite(False)
            self._hangVeilNP = veil
        except Exception:
            self._hangVeilNP = None
            return None
        return Sequence(
            LerpColorScaleInterval(
                veil, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                veil, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
        )

    def _spawnHangSpark(self, parent, index, total, elongated=False):
        """Softer cream fleck / streak that settles — residual aftershock hang."""
        count = max(1, int(total))
        if elongated:
            size = float(getattr(
                HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_STREAK_SIZE',
                0.012))
            r, g, b, a = getattr(
                HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_STREAK_COLOR',
                (1.0, 0.98, 0.82, 0.88))
            er, eg, eb, ea = getattr(
                HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_STREAK_END',
                (1.0, 0.9, 0.5, 0.0))
            nameSuffix = 'streak'
            angleBias = 0.48
        else:
            size = float(getattr(
                HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_SIZE', 0.016))
            r, g, b, a = getattr(
                HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_COLOR',
                (1.0, 0.96, 0.72, 0.9))
            er, eg, eb, ea = getattr(
                HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_END',
                (1.0, 0.92, 0.55, 0.0))
            nameSuffix = 'cream'
            angleBias = 0.2
        drift = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_DRIFT', 0.42))
        settle = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_SETTLE', 0.28))
        sec = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_SEC', 0.4))
        binSort = int(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_BIN', 59))
        oz = float(getattr(
            HackSlashConfig, 'FINISHER_CREAM_SPARKLE_HANG_ORIGIN_Z', 0.04))
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            cm = CardMaker(
                'hackslash-cream-slam-sparkle-hang-%s-%s' % (
                    nameSuffix, index))
            if elongated:
                cm.setFrame(
                    -size * 0.35, size * 0.35,
                    -size * 1.2, size * 1.2)
            else:
                cm.setFrame(-size, size, -size * 0.9, size * 0.9)
            spark = parent.attachNewNode(cm.generate())
            spark.setTransparency(TransparencyAttrib.MAlpha)
            spark.setColor(r, g, b, 1)
            spark.setColorScale(r, g, b, 0)
            startX = cos(angle) * 0.08
            startZ = oz + sin(angle) * 0.05 + 0.012 * (index % 3)
            spark.setPos(startX, 0.0, startZ)
            spark.setScale(0.3 + 0.08 * (index % 3))
            spark.setBin('fixed', binSort + 1 + (index % 2))
            spark.setDepthTest(False)
            spark.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream hang, not the slam flash punch.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            0.0,
            startZ - settle * (0.55 + 0.2 * (index % 3)))
        peak = 1.05 + 0.08 * (index % 2)
        self._hangNodes.append(spark)
        stagger = 0.018 * (index % 4)
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
                    spark, sec * 0.72, 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    spark, sec * 0.72, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def _retireNode(self, np):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass
