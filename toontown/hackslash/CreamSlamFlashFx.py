"""Rubber-hose cream slam flash on combo-finisher connect.

Warm cream aspect2d flash + expanding cream ring when the 3rd stretch-punch
slam lands. Layers with SlamDustFx (feet thud), HitJuice finisher slam scale,
HitStopFx freeze (flash reads during the stick), and soft-lock FOV (#74) —
finisher FOV still owns the lens after resume. Toontown spiritual-sequel tone
only — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from . import HackSlashConfig


class CreamSlamFlashFx(object):
    """Owns one short cream screen flash + ring for finisher slam connects."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._flashNP = None
        self._ringNP = None

    def play(self):
        """Spawn cream flash + ring. Returns started Sequence or None."""
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

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name=self.avatar.uniqueName('hackslashCreamSlamFlash'),
        )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop the flash and remove cream nodes."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        for attr in ('_flashNP', '_ringNP'):
            np = getattr(self, attr, None)
            setattr(self, attr, None)
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass

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
