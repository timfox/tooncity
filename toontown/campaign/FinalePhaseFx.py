"""Client spectacle for Ink Overlord finale phase transitions.

FOV punch + fullscreen flash + render color slam — mirrors hackslash /
purity-restore patterns so the phase flip reads as a boss moment.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpFunc,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
from toontown.corruption import CorruptionGlobals


class FinalePhaseFxClient(DirectObject):
    """Listens for reclaim finale-phase transition broadcasts."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._flashNP = None
        self._baseFov = None
        self._fovIval = None
        self.accept('finalePhaseTransition', self._onTransition)

    def destroy(self):
        self.ignoreAll()
        self._clear()

    def _onTransition(self, phaseIndex):
        self.playTransition(int(phaseIndex))

    def playTransition(self, phaseIndex):
        """Spectacle sting: flash + FOV + ink render slam."""
        self._clear()
        phase = max(1, int(phaseIndex))
        flashColor = CorruptionGlobals.FINALE_STING_FLASH_COLOR
        if phase >= 2:
            flashColor = (1.25, 0.12, 0.18, 1.0)
        peak = Vec4(*CorruptionGlobals.FINALE_STING_RENDER_PEAK)
        hold = Vec4(*CorruptionGlobals.FINALE_STING_RENDER_HOLD)
        if phase >= 2:
            peak = Vec4(2.0, 0.25, 0.35, 1.0)
            hold = Vec4(1.45, 0.3, 0.4, 1.0)

        try:
            cm = CardMaker('finale-phase-flash')
            cm.setFrame(-2, 2, -2, 2)
            np = aspect2d.attachNewNode(cm.generate())  # noqa: F821
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setColor(flashColor[0], flashColor[1], flashColor[2], 1)
            np.setColorScale(1, 1, 1, 0)
            np.setBin('fixed', 100)
            np.setDepthTest(False)
            np.setDepthWrite(False)
            self._flashNP = np
        except Exception:
            self._flashNP = None

        self._playFovPunch()

        parts = []
        if self._flashNP is not None:
            parts.append(Sequence(
                LerpColorScaleInterval(
                    self._flashNP, 0.06,
                    Vec4(1, 1, 1, CorruptionGlobals.FINALE_STING_FLASH_PEAK)),
                LerpColorScaleInterval(
                    self._flashNP, 0.35, Vec4(1, 1, 1, 0)),
            ))
        parts.append(Sequence(
            LerpColorScaleInterval(render, 0.08, peak),  # noqa: F821
            LerpColorScaleInterval(render, 0.28, hold),  # noqa: F821
            Wait(0.15),
            LerpColorScaleInterval(render, 0.55, Vec4(1, 1, 1, 1)),  # noqa: F821
            Func(render.clearColorScale),  # noqa: F821
        ))

        title = CampaignGlobals.FINALE_PHASE_BANNER.get(
            phase, 'FINALE PHASE %s' % phase)
        messenger.send('finalePhaseStingBanner', [phase, title])  # noqa: F821

        self._ival = Sequence(
            Parallel(*parts) if parts else Wait(0.01),
            Func(self._clearFlash),
            name='finalePhaseTransitionSting',
        )
        self._ival.start()

    def _playFovPunch(self):
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

        peak = baseFov + CorruptionGlobals.FINALE_STING_FOV_PUNCH

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
                duration=CorruptionGlobals.FINALE_STING_FOV_IN),
            LerpFunc(
                setFov,
                fromData=peak,
                toData=baseFov,
                duration=CorruptionGlobals.FINALE_STING_FOV_OUT),
            Func(self._restoreFov),
            name='finalePhaseFovPunch',
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

    def _clearFlash(self):
        if self._flashNP is not None:
            try:
                if not self._flashNP.isEmpty():
                    self._flashNP.removeNode()
            except Exception:
                pass
            self._flashNP = None

    def _clear(self):
        if self._ival:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        self._restoreFov()
        self._clearFlash()
        try:
            render.clearColorScale()  # noqa: F821
        except Exception:
            pass


_client = None


def ensureFinalePhaseFxClient():
    global _client
    if _client is None:
        _client = FinalePhaseFxClient()
    return _client
