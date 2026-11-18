"""Client spectacle for Ink Overlord finale phase transitions + Oswald reveal.

FOV punch + fullscreen flash + render color slam — mirrors hackslash /
purity-restore patterns so the phase flip reads as a boss moment.

On Silly finale victory / twist, plays a short readable AV reveal sting
(banner + FOV/flash + rubber-hose Oswald silhouette shadow flash +
optional SFX) that Oswald caused the corruption, then a soft cream
aftershock framed by a quieter cream edge pulse and a delayed soft cream
wash pulse that support the beat without undoing it. Composes with #82
victory cream swell (cheer only — cleared before reveal) and #129
victory cream edge. Toontown spiritual sequel — no keyblades / no KH
branding.
"""

from panda3d.core import CardMaker, TextNode, TransparencyAttrib, Vec3, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpFunc,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
from toontown.campaign.ActBannerCreamEdgeFx import (
    clearFinaleRevealCreamEdge,
    playFinaleRevealCreamEdge,
)
from toontown.campaign.FinaleCreamAftershockFx import (
    clearFinaleCreamAftershock,
    playFinaleCreamAftershock,
)
from toontown.campaign.FinaleRevealCreamWashFx import (
    clearFinaleRevealCreamWash,
    playFinaleRevealCreamWash,
)
from toontown.corruption import CorruptionGlobals


class FinalePhaseFxClient(DirectObject):
    """Listens for reclaim finale-phase transition + Oswald reveal broadcasts."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._flashNP = None
        self._shadowNP = None
        self._bannerNP = None
        self._subBannerNP = None
        self._baseFov = None
        self._fovIval = None
        self._revealSfx = None
        self.accept('finalePhaseTransition', self._onTransition)
        # Victory / twist paths — client messenger from reclaim director
        # (and campaignVictory when available). Avoids CampaignHandoff edits.
        self.accept('oswaldRevealSting', self._onOswaldReveal)
        self.accept('campaignVictory', self._onCampaignVictory)

    def destroy(self):
        self.ignoreAll()
        self._clear()

    def _onTransition(self, phaseIndex):
        self.playTransition(int(phaseIndex))

    def _onOswaldReveal(self, reclaimCount=0):
        # Default delay lets purity cheer land before the twist sting.
        self.playOswaldReveal()

    def _onCampaignVictory(self, reclaimCount=0):
        # Fallback when victory messenger reaches the client.
        self.playOswaldReveal()

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

        self._playFovPunch(
            punch=CorruptionGlobals.FINALE_STING_FOV_PUNCH,
            inSec=CorruptionGlobals.FINALE_STING_FOV_IN,
            outSec=CorruptionGlobals.FINALE_STING_FOV_OUT,
            name='finalePhaseFovPunch',
        )

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

    def playOswaldReveal(self, delay=None):
        """Short readable AV beat: Oswald caused the corruption."""
        if delay is None:
            delay = float(getattr(
                CampaignGlobals, 'FINALE_REVEAL_DELAY_SEC', 2.45))
        delay = max(0.0, float(delay))
        self._clear()

        def _fire():
            self._runOswaldReveal()

        if delay <= 0.01:
            _fire()
            return
        self._ival = Sequence(
            Wait(delay),
            Func(_fire),
            name='oswaldRevealDelay',
        )
        self._ival.start()

    def _runOswaldReveal(self):
        self._clearFlash()
        self._clearShadow()
        self._clearBanners()
        flashColor = CorruptionGlobals.OSWALD_REVEAL_FLASH_COLOR
        peak = Vec4(*CorruptionGlobals.OSWALD_REVEAL_RENDER_PEAK)
        hold = Vec4(*CorruptionGlobals.OSWALD_REVEAL_RENDER_HOLD)

        try:
            cm = CardMaker('oswald-reveal-flash')
            cm.setFrame(-2, 2, -2, 2)
            np = aspect2d.attachNewNode(cm.generate())  # noqa: F821
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setColor(flashColor[0], flashColor[1], flashColor[2], 1)
            np.setColorScale(1, 1, 1, 0)
            np.setBin('fixed', 102)
            np.setDepthTest(False)
            np.setDepthWrite(False)
            self._flashNP = np
        except Exception:
            self._flashNP = None

        self._shadowNP = self._buildOswaldShadow()

        self._playFovPunch(
            punch=CorruptionGlobals.OSWALD_REVEAL_FOV_PUNCH,
            inSec=CorruptionGlobals.OSWALD_REVEAL_FOV_IN,
            outSec=CorruptionGlobals.OSWALD_REVEAL_FOV_OUT,
            name='oswaldRevealFovPunch',
        )
        self._playRevealSfx()
        self._showRevealBanners()

        parts = []
        if self._flashNP is not None:
            parts.append(Sequence(
                LerpColorScaleInterval(
                    self._flashNP, 0.08,
                    Vec4(1, 1, 1, CorruptionGlobals.OSWALD_REVEAL_FLASH_PEAK)),
                Wait(0.12),
                LerpColorScaleInterval(
                    self._flashNP, 0.55, Vec4(1, 1, 1, 0)),
            ))
        shadowIval = self._buildShadowFlashInterval()
        if shadowIval is not None:
            parts.append(shadowIval)
        parts.append(Sequence(
            LerpColorScaleInterval(render, 0.1, peak),  # noqa: F821
            LerpColorScaleInterval(render, 0.35, hold),  # noqa: F821
            Wait(0.2),
            LerpColorScaleInterval(render, 0.7, Vec4(1, 1, 1, 1)),  # noqa: F821
            Func(render.clearColorScale),  # noqa: F821
        ))

        holdSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_HOLD_SEC', 3.6))
        title = getattr(
            CampaignGlobals, 'FINALE_REVEAL_BANNER',
            CampaignGlobals.FINALE_TWIST_TEASE)
        messenger.send('oswaldRevealBanner', [title])  # noqa: F821

        # Cream aftershock after ink/shadow sting — residual cream that
        # supports the twist (does not replay #82 victory swell).
        aftershockDelay = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_CREAM_AFTERSHOCK_DELAY_SEC', 0.72))
        stingParts = Parallel(*parts) if parts else Wait(0.01)
        self._ival = Sequence(
            Parallel(
                stingParts,
                Sequence(
                    Wait(max(0.0, aftershockDelay)),
                    Func(self._playCreamAftershock),
                ),
            ),
            Wait(max(0.0, holdSec - 1.2)),
            Func(self._fadeRevealBanners),
            Wait(0.45),
            Func(self._clear),
            name='oswaldRevealSting',
        )
        self._ival.start()

    def _playCreamAftershock(self):
        """Soft cream residual after the reveal sting lands.

        Cream aftershock (#86) + quieter cream edge frame (#133) + soft
        cream wash pulse (#145/#141/#138 twin) — Oswald-twist path only;
        mid-campaign stays edge/wash-free of spoilers.
        """
        try:
            playFinaleCreamAftershock()
        except Exception:
            pass
        try:
            playFinaleRevealCreamEdge()
        except Exception:
            pass
        # Soft cream wash pulse after cream edge (#133) — trust / handoff /
        # victory wash grammar (#145/#141/#138). Twist residual only.
        try:
            playFinaleRevealCreamWash()
        except Exception:
            pass

    def _buildOswaldShadow(self):
        """Rubber-hose Oswald silhouette — tall ears, round head, drip feet.

        Layered CardMaker pieces under aspect2d; reads as ink shadow of the
        trusted lead turning into the corruption's cause. No KH props.
        """
        try:
            color = getattr(
                CampaignGlobals, 'FINALE_REVEAL_SHADOW_COLOR',
                (0.04, 0.02, 0.06, 1.0))
            pos = getattr(
                CampaignGlobals, 'FINALE_REVEAL_SHADOW_POS',
                (0.0, 0.0, -0.02))
            scale = float(getattr(
                CampaignGlobals, 'FINALE_REVEAL_SHADOW_SCALE', 0.55))
            binSort = int(getattr(
                CampaignGlobals, 'FINALE_REVEAL_SHADOW_BIN', 101))

            root = aspect2d.attachNewNode('oswald-reveal-shadow')  # noqa: F821
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', binSort)
            root.setDepthTest(False)
            root.setDepthWrite(False)
            root.setPos(pos[0], pos[1], pos[2])
            root.setScale(scale)

            # Local-space pieces (aspect2d units before root scale).
            # Ears first (behind), then head/body/limbs, drip last.
            pieces = (
                # Left ear — tall rubber hose
                ('ear-l', -0.22, 0.55, 0.09, 0.42),
                # Right ear
                ('ear-r', 0.22, 0.55, 0.09, 0.42),
                # Head
                ('head', 0.0, 0.22, 0.28, 0.26),
                # Torso
                ('body', 0.0, -0.12, 0.32, 0.38),
                # Left arm droop
                ('arm-l', -0.38, -0.08, 0.1, 0.28),
                # Right arm droop
                ('arm-r', 0.38, -0.08, 0.1, 0.28),
                # Left foot blob
                ('foot-l', -0.16, -0.48, 0.14, 0.1),
                # Right foot blob
                ('foot-r', 0.16, -0.48, 0.14, 0.1),
                # Ink drip under silhouette — cause-of-corruption read
                ('drip', 0.0, -0.62, 0.08, 0.16),
            )
            for name, cx, cz, halfW, halfH in pieces:
                cm = CardMaker('oswald-shadow-%s' % name)
                cm.setFrame(cx - halfW, cx + halfW, cz - halfH, cz + halfH)
                piece = root.attachNewNode(cm.generate())
                piece.setTransparency(TransparencyAttrib.MAlpha)
                piece.setColor(color[0], color[1], color[2], 1)
                piece.setBin('fixed', binSort)
                piece.setDepthTest(False)
                piece.setDepthWrite(False)
            return root
        except Exception:
            return None

    def _buildShadowFlashInterval(self):
        """Squash → stretch → settle + alpha flash for the Oswald silhouette."""
        shadow = self._shadowNP
        if shadow is None:
            return None
        try:
            if shadow.isEmpty():
                return None
        except Exception:
            return None

        peakA = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_PEAK_ALPHA', 0.92))
        fadeIn = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_FADE_IN_SEC', 0.06))
        holdSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_HOLD_SEC', 0.28))
        fadeOut = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_FADE_OUT_SEC', 0.55))
        squash = getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_SQUASH',
            (1.35, 1.0, 0.55))
        stretch = getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_STRETCH',
            (0.72, 1.0, 1.55))
        squashSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_SQUASH_SEC', 0.07))
        stretchSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_STRETCH_SEC', 0.12))
        settleSec = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_SETTLE_SEC', 0.18))
        baseScale = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_SHADOW_SCALE', 0.55))

        squashScale = Vec3(
            baseScale * squash[0], baseScale * squash[1],
            baseScale * squash[2])
        stretchScale = Vec3(
            baseScale * stretch[0], baseScale * stretch[1],
            baseScale * stretch[2])
        settleScale = Vec3(baseScale, baseScale, baseScale)

        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    shadow, fadeIn, Vec4(1, 1, 1, peakA)),
                Wait(holdSec),
                LerpColorScaleInterval(
                    shadow, fadeOut, Vec4(1, 1, 1, 0)),
                Func(self._clearShadow),
            ),
            Sequence(
                LerpScaleInterval(shadow, squashSec, squashScale),
                LerpScaleInterval(shadow, stretchSec, stretchScale),
                LerpScaleInterval(shadow, settleSec, settleScale),
            ),
            name='oswaldRevealShadowFlash',
        )

    def _showRevealBanners(self):
        title = getattr(
            CampaignGlobals, 'FINALE_REVEAL_BANNER',
            'OSWALD CAUSED THE CORRUPTION')
        sub = getattr(
            CampaignGlobals, 'FINALE_REVEAL_SUB',
            CampaignGlobals.FINALE_TWIST_TEASE)
        titleColor = getattr(
            CampaignGlobals, 'FINALE_REVEAL_BANNER_COLOR',
            CampaignGlobals.FINALE_TWIST_TEASE_COLOR)
        subColor = getattr(
            CampaignGlobals, 'FINALE_REVEAL_SUB_COLOR',
            (1.0, 0.72, 0.48, 1.0))

        try:
            tn = TextNode('oswald-reveal-banner')
            tn.setText(title)
            tn.setAlign(TextNode.ACenter)
            tn.setTextColor(
                titleColor[0], titleColor[1], titleColor[2], 1)
            tn.setShadow(0.05, 0.05)
            tn.setShadowColor(0, 0, 0, 0.8)
            np = aspect2d.attachNewNode(tn)  # noqa: F821
            np.setScale(0.085)
            np.setPos(0, 0, 0.42)
            np.setColorScale(1, 1, 1, 0)
            self._bannerNP = np
        except Exception:
            self._bannerNP = None

        try:
            stn = TextNode('oswald-reveal-sub')
            stn.setText(sub)
            stn.setAlign(TextNode.ACenter)
            stn.setTextColor(subColor[0], subColor[1], subColor[2], 1)
            stn.setShadow(0.04, 0.04)
            stn.setShadowColor(0, 0, 0, 0.75)
            snp = aspect2d.attachNewNode(stn)  # noqa: F821
            snp.setScale(0.048)
            snp.setPos(0, 0, 0.28)
            snp.setColorScale(1, 1, 1, 0)
            self._subBannerNP = snp
        except Exception:
            self._subBannerNP = None

        fades = []
        if self._bannerNP is not None:
            fades.append(
                LerpColorScaleInterval(
                    self._bannerNP, 0.22, Vec4(1, 1, 1, 1)))
        if self._subBannerNP is not None:
            fades.append(
                LerpColorScaleInterval(
                    self._subBannerNP, 0.28, Vec4(1, 1, 1, 1)))
        if fades:
            Parallel(*fades).start()

    def _fadeRevealBanners(self):
        fades = []
        if self._bannerNP is not None and not self._bannerNP.isEmpty():
            fades.append(
                LerpColorScaleInterval(
                    self._bannerNP, 0.4, Vec4(1, 1, 1, 0)))
        if self._subBannerNP is not None and not self._subBannerNP.isEmpty():
            fades.append(
                LerpColorScaleInterval(
                    self._subBannerNP, 0.4, Vec4(1, 1, 1, 0)))
        if fades:
            Parallel(*fades).start()

    def _playRevealSfx(self):
        try:
            if self._revealSfx is None:
                path = CorruptionGlobals.OSWALD_REVEAL_SFX
                self._revealSfx = base.loader.loadSfx(path)  # noqa: F821
            if self._revealSfx:
                try:
                    self._revealSfx.setVolume(
                        CorruptionGlobals.OSWALD_REVEAL_SFX_VOLUME)
                except Exception:
                    pass
                base.playSfx(self._revealSfx)  # noqa: F821
        except Exception:
            self._revealSfx = False

    def _playFovPunch(self, punch, inSec, outSec, name='finaleFovPunch'):
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
            name=name,
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

    def _clearShadow(self):
        if self._shadowNP is not None:
            try:
                if not self._shadowNP.isEmpty():
                    self._shadowNP.removeNode()
            except Exception:
                pass
            self._shadowNP = None

    def _clearBanners(self):
        if self._bannerNP is not None:
            try:
                if not self._bannerNP.isEmpty():
                    self._bannerNP.removeNode()
            except Exception:
                pass
            self._bannerNP = None
        if self._subBannerNP is not None:
            try:
                if not self._subBannerNP.isEmpty():
                    self._subBannerNP.removeNode()
            except Exception:
                pass
            self._subBannerNP = None

    def _clear(self):
        if self._ival:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        self._restoreFov()
        self._clearFlash()
        self._clearShadow()
        self._clearBanners()
        try:
            clearFinaleCreamAftershock()
        except Exception:
            pass
        try:
            clearFinaleRevealCreamEdge()
        except Exception:
            pass
        try:
            clearFinaleRevealCreamWash()
        except Exception:
            pass
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
