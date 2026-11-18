"""Client spectacle when a street hits purity restore.

FOV camera punch + layered aspect2d juice on top of the director's flash/ring.
Mirrors FinalePhaseFx / MeleeCombat finisher patterns, but warmer and cleaner
so reclaim reads as a KH×Toontown payoff — never stomps hood geom tint/fog.
"""

from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpFunc,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.reclaim import ReclaimGlobals


class PurityBurstFxClient(DirectObject):
    """Listens for purity restore messengers and plays camera + overlay juice."""

    def __init__(self):
        DirectObject.__init__(self)
        self._fovIval = None
        self._camIval = None
        self._layerIval = None
        self._baseFov = None
        self._baseCamPos = None
        self._rayNPs = []
        self._sparkNPs = []
        self._outerRingNP = None
        # Director fires purityRestoreFx then purityRestoreSting; bind sting only
        # so we do not double-punch the camera / overlay layers.
        self.accept('purityRestoreSting', self._onRestore)
        self.accept('purityBurstPulse', self._onPulse)
        self.accept('purityRestoreSettled', self._onSettled)

    def destroy(self):
        self.ignoreAll()
        self._clear()

    def _onRestore(self, zoneId=None):
        self.playBurst()

    def _onPulse(self, zoneId=None, beat=1):
        # Second bloom beat gets a lighter FOV tick so the two-wash reads.
        if int(beat) == 2:
            self._playFovPunch(
                punch=ReclaimGlobals.PURITY_FOV_PUNCH * 0.45,
                inSec=0.05,
                outSec=0.28,
            )

    def _onSettled(self, zoneId=None):
        self._restoreFov()
        self._restoreCamera()
        self._clearLayers()

    def playBurst(self):
        """Main reclaim payoff: FOV punch + rays/sparks + soft camera bob."""
        self._clear()
        self._playFovPunch(
            punch=ReclaimGlobals.PURITY_FOV_PUNCH,
            inSec=ReclaimGlobals.PURITY_FOV_IN_SEC,
            outSec=ReclaimGlobals.PURITY_FOV_OUT_SEC,
        )
        self._playCameraBob()
        self._spawnJuiceLayers()

    def _playFovPunch(self, punch, inSec, outSec):
        self._restoreFov()
        try:
            lens = base.camLens  # noqa: F821
            self._baseFov = lens.getFov()
            baseFov = (
                float(self._baseFov[0])
                if hasattr(self._baseFov, '__getitem__')
                else float(self._baseFov))
        except Exception:
            self._baseFov = None
            return

        peak = baseFov + float(punch)

        def setFov(v):
            try:
                lens.setFov(v)
            except Exception:
                pass

        self._fovIval = Sequence(
            LerpFunc(
                setFov,
                fromData=baseFov,
                toData=peak,
                duration=max(0.01, float(inSec))),
            LerpFunc(
                setFov,
                fromData=peak,
                toData=baseFov,
                duration=max(0.01, float(outSec))),
            Func(self._restoreFov),
            name='purityBurstFovPunch',
        )
        self._fovIval.start()

    def _restoreFov(self):
        if self._fovIval:
            try:
                self._fovIval.pause()
            except Exception:
                pass
            self._fovIval = None
        if self._baseFov is None:
            return
        try:
            lens = base.camLens  # noqa: F821
            if hasattr(self._baseFov, '__getitem__'):
                lens.setFov(self._baseFov[0], self._baseFov[1])
            else:
                lens.setFov(self._baseFov)
        except Exception:
            pass
        self._baseFov = None

    def _playCameraBob(self):
        """Brief KH-style pull-back then settle — readable without dizzying."""
        self._restoreCamera()
        try:
            cam = base.camera  # noqa: F821
            self._baseCamPos = Point3(cam.getPos())
        except Exception:
            self._baseCamPos = None
            return

        pull = float(ReclaimGlobals.PURITY_CAM_PULL)
        lift = float(ReclaimGlobals.PURITY_CAM_LIFT)
        peak = Point3(
            self._baseCamPos[0],
            self._baseCamPos[1] - pull,
            self._baseCamPos[2] + lift,
        )
        try:
            self._camIval = Sequence(
                LerpPosInterval(
                    cam,
                    ReclaimGlobals.PURITY_CAM_IN_SEC,
                    peak,
                    blendType='easeOut'),
                LerpPosInterval(
                    cam,
                    ReclaimGlobals.PURITY_CAM_OUT_SEC,
                    self._baseCamPos,
                    blendType='easeInOut'),
                Func(self._restoreCamera),
                name='purityBurstCamBob',
            )
            self._camIval.start()
        except Exception:
            self._restoreCamera()

    def _restoreCamera(self):
        if self._camIval:
            try:
                self._camIval.pause()
            except Exception:
                pass
            self._camIval = None
        if self._baseCamPos is None:
            return
        try:
            cam = base.camera  # noqa: F821
            cam.setPos(self._baseCamPos)
        except Exception:
            pass
        self._baseCamPos = None

    def _spawnJuiceLayers(self):
        """Outer ring + soft sunburst rays + spark pops on aspect2d."""
        self._clearLayers()
        r, g, b, _a = ReclaimGlobals.PURITY_BURST_COLOR
        parts = []

        try:
            rcm = CardMaker('purity-outer-ring')
            rcm.setFrame(-0.7, 0.7, -0.7, 0.7)
            ring = aspect2d.attachNewNode(rcm.generate())  # noqa: F821
            ring.setTransparency(TransparencyAttrib.MAlpha)
            ring.setColor(r, g, b, 1)
            ring.setColorScale(r, g, b, 0.7)
            ring.setScale(0.45)
            ring.setPos(0, 0, 0.08)
            ring.setBin('fixed', 57)
            ring.setDepthTest(False)
            ring.setDepthWrite(False)
            self._outerRingNP = ring
            parts.append(Sequence(
                Parallel(
                    LerpScaleInterval(
                        ring,
                        ReclaimGlobals.PURITY_OUTER_RING_SEC,
                        ReclaimGlobals.PURITY_OUTER_RING_PEAK),
                    LerpColorScaleInterval(
                        ring,
                        ReclaimGlobals.PURITY_OUTER_RING_SEC,
                        Vec4(r, g, b, 0)),
                ),
            ))
        except Exception:
            self._outerRingNP = None

        rayCount = int(ReclaimGlobals.PURITY_RAY_COUNT)
        for i in range(rayCount):
            try:
                angle = (2.0 * pi * i) / max(1, rayCount)
                cm = CardMaker('purity-ray-%s' % i)
                cm.setFrame(-0.04, 0.04, 0.0, 0.55)
                ray = aspect2d.attachNewNode(cm.generate())  # noqa: F821
                ray.setTransparency(TransparencyAttrib.MAlpha)
                ray.setColor(r, g, b, 1)
                ray.setColorScale(r, g, b, 0.0)
                ray.setPos(0, 0, 0.05)
                ray.setR(angle * 180.0 / pi)
                ray.setScale(0.55)
                ray.setBin('fixed', 56)
                ray.setDepthTest(False)
                ray.setDepthWrite(False)
                self._rayNPs.append(ray)
                peakA = ReclaimGlobals.PURITY_RAY_PEAK_ALPHA
                parts.append(Sequence(
                    LerpColorScaleInterval(
                        ray, 0.08, Vec4(r, g, b, peakA)),
                    Parallel(
                        LerpScaleInterval(
                            ray, ReclaimGlobals.PURITY_RAY_SEC, 1.35),
                        LerpColorScaleInterval(
                            ray, ReclaimGlobals.PURITY_RAY_SEC,
                            Vec4(r, g, b, 0)),
                    ),
                ))
            except Exception:
                pass

        sparkCount = int(ReclaimGlobals.PURITY_SPARK_COUNT)
        for i in range(sparkCount):
            try:
                angle = (2.0 * pi * (i + 0.5)) / max(1, sparkCount)
                dist = 0.22 + (0.08 * (i % 3))
                cm = CardMaker('purity-spark-%s' % i)
                cm.setFrame(-0.045, 0.045, -0.045, 0.045)
                spark = aspect2d.attachNewNode(cm.generate())  # noqa: F821
                spark.setTransparency(TransparencyAttrib.MAlpha)
                spark.setColor(1.0, 1.0, 0.92, 1)
                spark.setColorScale(1, 1, 0.92, 0)
                spark.setPos(
                    sin(angle) * dist * 0.35,
                    0,
                    0.08 + cos(angle) * dist * 0.55)
                spark.setScale(0.35)
                spark.setBin('fixed', 60)
                spark.setDepthTest(False)
                spark.setDepthWrite(False)
                self._sparkNPs.append(spark)
                delay = 0.04 * i
                parts.append(Sequence(
                    Wait(delay),
                    Parallel(
                        LerpColorScaleInterval(
                            spark, 0.1, Vec4(1, 1, 0.92, 0.95)),
                        LerpScaleInterval(spark, 0.1, 1.0),
                    ),
                    Parallel(
                        LerpPosInterval(
                            spark, ReclaimGlobals.PURITY_SPARK_SEC,
                            Point3(
                                sin(angle) * (dist + 0.55) * 0.55,
                                0,
                                0.08 + cos(angle) * (dist + 0.55) * 0.75)),
                        LerpColorScaleInterval(
                            spark, ReclaimGlobals.PURITY_SPARK_SEC,
                            Vec4(1, 1, 0.92, 0)),
                        LerpScaleInterval(spark, ReclaimGlobals.PURITY_SPARK_SEC, 0.2),
                    ),
                ))
            except Exception:
                pass

        if not parts:
            return
        self._layerIval = Sequence(
            Parallel(*parts),
            Func(self._clearLayers),
            name='purityBurstJuiceLayers',
        )
        self._layerIval.start()

    def _clearLayers(self):
        if self._layerIval:
            try:
                self._layerIval.pause()
            except Exception:
                pass
            self._layerIval = None
        for attr in ('_outerRingNP',):
            np = getattr(self, attr, None)
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
            setattr(self, attr, None)
        for np in self._rayNPs + self._sparkNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._rayNPs = []
        self._sparkNPs = []

    def _clear(self):
        self._restoreFov()
        self._restoreCamera()
        self._clearLayers()


_client = None


def ensurePurityBurstFxClient():
    global _client
    if _client is None:
        _client = PurityBurstFxClient()
    return _client
