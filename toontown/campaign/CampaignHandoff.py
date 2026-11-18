"""Client-visible campaign handoff banners + melee power bump on reclaim.

Act clears (Loopy → Punchline → Silly) play as a short Toontown reclaim
celebration — Oswald as the trusted face, title hose-pop, clear next-street
cue — not a single toast line. Finale victory keeps the Oswald twist beat.

Title lands with the same squash→stretch→settle rubber-hose scale pop as
PlayEntry tip/act-enter banners (tunables in CampaignGlobals). Early/mid
trusted Oswald lead clears also settle-bounce the title and hose-pop the
Oswald cheer/lead subtitle. Act handoffs fire a short confetti / streamer
+ cream-sparkle pop (CampaignHandoffConfetti) framed by a soft cream edge
pulse tuned to the carnival glitter — no KH / keyblade framing. Campaign
victory fires a soft cream confetti swell on the purity cheer only; it
clears before the Oswald twist / FinalePhaseFx reveal so the bittersweet
sting stays intact.
"""

from panda3d.core import CardMaker, Point3, TextNode, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
from toontown.campaign.ActBannerCreamEdgeFx import (
    clearHandoffCreamEdge,
    clearOswaldTrustBannerCreamEdge,
    playHandoffCreamEdge,
    playOswaldTrustBannerCreamEdge,
)
from toontown.campaign.CampaignHandoffConfetti import (
    clearHandoffConfetti,
    clearVictoryCreamSwell,
    playHandoffConfetti,
    playVictoryCreamSwell,
)
from toontown.campaign.CampaignPower import applyPowerBump

# Celebration timing — readable rubber-hose reclaim beat, not a flash toast.
# Title settle/pop tunables live in CampaignGlobals (HANDOFF_TITLE_*).
_SUB_SCALE = 0.048
_CUE_SCALE = 0.052
_POWER_SCALE = 0.036
_HOLD_SEC = 4.6
_CARD_COLOR = (0.12, 0.28, 0.22, 0.55)
_TITLE_COLOR = Vec4(0.55, 1.0, 0.78, 1)
_SUB_COLOR = Vec4(0.95, 1.0, 0.88, 1)
_CUE_COLOR = Vec4(1.0, 0.92, 0.42, 1)
_POWER_COLOR = Vec4(0.75, 0.95, 1.0, 1)
_VICTORY_COLOR = Vec4(1.0, 0.95, 0.45, 1)
_TWIST_COLOR = Vec4(1.0, 0.55, 0.35, 1)
_PHASE_COLOR = Vec4(1.0, 0.55, 0.35, 1)
_FINALE_P2_COLOR = Vec4(1.0, 0.35, 0.55, 1)


def _face():
    return getattr(
        CampaignGlobals, 'RECLAIM_FACE',
        getattr(CampaignGlobals, 'PROTAGONIST', 'Oswald'))


class CampaignHandoffClient(DirectObject):
    """Shows next-hood / phase / victory copy when streets are reclaimed."""

    def __init__(self):
        DirectObject.__init__(self)
        self._rootNP = None
        self._ival = None
        self._localReclaimCount = 0
        self._finaleClears = 0
        self.accept('purityRestoreFx', self._onPurityRestore)
        self.accept('campaignVictory', self._onVictory)
        self.accept('campaignPhase', self._onPhase)
        self.accept('reclaimFinalePhase', self._onReclaimFinalePhase)

    def destroy(self):
        self.ignoreAll()
        self._clear()

    def _onReclaimFinalePhase(self, phaseIndex):
        # Keep a client-side phase counter so purity messaging stays honest.
        phase = int(phaseIndex)
        if phase >= 1:
            self._finaleClears = max(self._finaleClears, phase - 1)

    def _onPurityRestore(self, zoneId):
        self._localReclaimCount += 1
        mult = applyPowerBump(self._localReclaimCount)
        face = _face()
        act, nxt = self._actsForZone(zoneId)
        if act and act.get('finale'):
            self._finaleClears += 1
            if self._finaleClears <= 1:
                phase2 = act.get('phase2') or {}
                self._celebrate(
                    phase2.get('banner') or 'Finale Phase 2!',
                    subtitle='%s urges you on — the Overlord is not done!' % face,
                    nextCue='Stay on Silly Street — Phase 2 packs inbound',
                    color=_FINALE_P2_COLOR,
                    powerMult=mult,
                    nextStreet=None)
            else:
                tease = getattr(
                    CampaignGlobals, 'FINALE_TWIST_TEASE', '') or (
                    act.get('nextCue') or 'Oswald caused the corruption')
                self._celebrate(
                    act.get('handoffTitle') or 'VICTORY…?',
                    subtitle=act.get('handoff') or (
                        '%s smiles too wide…' % face),
                    nextCue=tease,
                    color=_TWIST_COLOR,
                    powerMult=mult,
                    nextStreet=None)
            return
        if act is None:
            self._celebrate(
                'Neighborhood reclaimed!',
                subtitle='%s tips his hat — corruption washed clean' % face,
                nextCue='Scout the next polluted street',
                color=_TITLE_COLOR,
                powerMult=mult,
                nextStreet=None,
                confetti=True,
                trustSettle=True)
            return
        title = act.get('handoffTitle') or (
            '%s IS PURE!' % act.get('name', 'Street').upper())
        subtitle = act.get('handoff') or (
            '%s beams — another street saved!' % face)
        if nxt is not None:
            nextStreet = (
                act.get('nextStreet') or nxt.get('name') or 'the next hood')
            nextCue = act.get('nextCue') or (
                '%s points the way → %s' % (face, nextStreet))
        else:
            nextStreet = None
            nextCue = act.get('nextCue') or (
                'Take a victory lap with %s' % face)
        # Loopy→Punchline (and act) handoffs: confetti + Oswald trust settle.
        self._celebrate(
            title,
            subtitle=subtitle,
            nextCue=nextCue,
            color=_TITLE_COLOR,
            powerMult=mult,
            nextStreet=nextStreet,
            confetti=True,
            trustSettle=True)

    def _actsForZone(self, zoneId):
        zoneId = int(zoneId)
        for i, act in enumerate(CampaignGlobals.ACTS):
            if int(act['zoneId']) == zoneId:
                nxt = (
                    CampaignGlobals.ACTS[i + 1]
                    if i + 1 < len(CampaignGlobals.ACTS) else None)
                return act, nxt
        return None, None

    def _onVictory(self, reclaimCount=0):
        # Purity cheer (+ cream confetti swell), then Oswald twist tease.
        # Cream swell is cheer-only — twist / FinalePhaseFx reveal stay
        # bittersweet (no carnival after the truth lands).
        face = _face()
        tease = getattr(CampaignGlobals, 'FINALE_TWIST_TEASE', '')
        teaseColor = Vec4(*getattr(
            CampaignGlobals, 'FINALE_TWIST_TEASE_COLOR',
            (1.0, 0.55, 0.35, 1.0)))
        if not tease:
            self._celebrate(
                'TOON CITY IS SAVED!',
                subtitle='%s leads the neighborhood cheer' % face,
                nextCue='Purity holds — take a victory lap!',
                color=_VICTORY_COLOR,
                powerMult=None,
                nextStreet=None,
                creamSwell=True)
            return

        self._clear()
        self._celebrate(
            'TOON CITY IS SAVED!',
            subtitle='%s leads the neighborhood cheer' % face,
            nextCue='Purity holds…',
            color=_VICTORY_COLOR,
            powerMult=None,
            nextStreet=None,
            holdSec=2.4,
            creamSwell=True,
            onDone=lambda: self._celebrate(
                'VICTORY…?',
                subtitle=tease,
                nextCue="Oswald's smile was the stain all along",
                color=teaseColor,
                powerMult=None,
                nextStreet=None,
                holdSec=3.8))

    def _onPhase(self, phaseIndex, message):
        # Skip duplicate flash when finale phase FX already own phase 2.
        phase = int(phaseIndex) + 1
        if phase >= 2:
            return
        face = _face()
        self._celebrate(
            'PHASE %s' % phase,
            subtitle=message or ('%s rallies the reclaim!' % face),
            nextCue='Clear the street — reclaim purity!',
            color=_PHASE_COLOR,
            powerMult=None,
            nextStreet=None)

    def _celebrate(self, title, subtitle='', nextCue='', color=_TITLE_COLOR,
                   powerMult=None, nextStreet=None, holdSec=None, onDone=None,
                   confetti=False, trustSettle=False, creamSwell=False):
        """Staged rubber-hose celebration: card → title pop → cue → hold."""
        self._clear()
        root = aspect2d.attachNewNode('campaign-handoff-root')  # noqa: F821
        root.setPos(0, 0, 0.42)
        root.setTransparency(TransparencyAttrib.MAlpha)
        root.setColorScale(1, 1, 1, 0)
        self._rootNP = root
        hold = _HOLD_SEC if holdSec is None else float(holdSec)

        if creamSwell:
            # Soft cream swell under the purity victory plate only.
            try:
                origin = getattr(
                    CampaignGlobals, 'VICTORY_CREAM_SWELL_ORIGIN',
                    (0.0, 0.0, 0.36))
                playVictoryCreamSwell(origin=origin)
            except Exception:
                pass
        elif confetti:
            # Short carnival burst beside the banner — act handoff juice only.
            try:
                origin = getattr(
                    CampaignGlobals, 'HANDOFF_CONFETTI_ORIGIN',
                    (0.0, 0.0, 0.38))
                playHandoffConfetti(origin=origin)
            except Exception:
                pass
            # Cream edge frame tuned to cream-sparkle carnival banners (#99).
            # Early/mid trusted Oswald only — twist / victory / phase stay edge-free.
            try:
                playHandoffCreamEdge()
            except Exception:
                pass
        elif trustSettle:
            # Trust hose-settle without carnival — keep #117 trust cream edge.
            try:
                playOswaldTrustBannerCreamEdge()
            except Exception:
                pass

        try:
            cm = CardMaker('campaign-handoff-card')
            cm.setFrame(-1.15, 1.15, -0.28, 0.22)
            card = root.attachNewNode(cm.generate())
            card.setTransparency(TransparencyAttrib.MAlpha)
            card.setColor(*_CARD_COLOR)
            card.setBin('fixed', 60)
            card.setDepthTest(False)
            card.setDepthWrite(False)
        except Exception:
            pass

        titleScale = float(getattr(
            CampaignGlobals, 'HANDOFF_TITLE_SCALE', 0.078))
        titleNP = self._makeLine(
            root, 'campaign-handoff-title', title, color, titleScale, 0.08)
        subScale = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_SUB_SCALE', _SUB_SCALE))
        if not trustSettle:
            subScale = _SUB_SCALE
        subNP = None
        if subtitle:
            subNP = self._makeLine(
                root, 'campaign-handoff-sub', subtitle, _SUB_COLOR,
                subScale, -0.02)
            subNP.setColorScale(1, 1, 1, 0)
        cueText = nextCue
        if nextStreet and nextStreet not in (nextCue or ''):
            cueText = nextCue or ('Next street → %s' % nextStreet)
        cueNP = None
        if cueText:
            cueNP = self._makeLine(
                root, 'campaign-handoff-cue', cueText, _CUE_COLOR,
                _CUE_SCALE, -0.11)
            cueNP.setColorScale(1, 1, 1, 0)
            cueNP.setScale(_CUE_SCALE * 0.55)
        powerNP = None
        if powerMult is not None:
            powerNP = self._makeLine(
                root, 'campaign-handoff-power',
                'Melee power  x%.2f' % float(powerMult),
                _POWER_COLOR, _POWER_SCALE, -0.20)
            powerNP.setColorScale(1, 1, 1, 0)

        parts = [
            LerpColorScaleInterval(root, 0.18, Vec4(1, 1, 1, 1)),
            self._titleHosePopInterval(
                titleNP, titleScale, trustSettle=trustSettle),
        ]
        if subNP is not None:
            if trustSettle:
                # Oswald trusted cheer/lead subtitle — tip-matched hose settle.
                parts.append(Sequence(
                    Wait(0.22),
                    Parallel(
                        LerpColorScaleInterval(
                            subNP, 0.2, Vec4(1, 1, 1, 1)),
                        self._trustSubHosePopInterval(subNP, subScale),
                    ),
                ))
            else:
                parts.append(Sequence(
                    Wait(0.22),
                    LerpColorScaleInterval(subNP, 0.2, Vec4(1, 1, 1, 1)),
                ))
        if cueNP is not None:
            parts.append(Sequence(
                Wait(0.42),
                Parallel(
                    LerpColorScaleInterval(cueNP, 0.18, Vec4(1, 1, 1, 1)),
                    LerpScaleInterval(cueNP, 0.22, _CUE_SCALE * 1.08),
                ),
                LerpScaleInterval(cueNP, 0.14, _CUE_SCALE),
            ))
        if powerNP is not None:
            parts.append(Sequence(
                Wait(0.55),
                LerpColorScaleInterval(powerNP, 0.2, Vec4(1, 1, 1, 1)),
            ))

        try:
            messenger.send(  # noqa: F821
                'campaignHandoffCue',
                [nextStreet, cueText or nextCue or title])
        except Exception:
            pass

        tail = [Func(self._clear)]
        if onDone is not None:
            tail = [Func(onDone)]

        self._ival = Sequence(
            Parallel(*parts),
            Wait(hold),
            LerpColorScaleInterval(root, 0.35, Vec4(1, 1, 1, 0)),
            *tail,
            name='campaignHandoffCelebrate',
        )
        self._ival.start()

    def _titleHosePopInterval(self, titleNP, settleScale, trustSettle=False):
        """Tip-matched squash → stretch → settle on the handoff title.

        Early/mid Oswald trusted reclaim-lead clears append a soft
        overshoot → rest settle bounce after the hose pop.
        """
        settle = float(settleScale)
        sx, sy, sz, squashSec = getattr(
            CampaignGlobals, 'HANDOFF_TITLE_POP_SQUASH',
            (1.42, 1.0, 0.62, 0.06))
        tx, ty, tz, stretchSec = getattr(
            CampaignGlobals, 'HANDOFF_TITLE_POP_STRETCH',
            (0.82, 1.0, 1.36, 0.10))
        settleSec = float(getattr(
            CampaignGlobals, 'HANDOFF_TITLE_POP_SETTLE_SEC', 0.12))
        settlePt = Point3(settle, settle, settle)
        squashPt = Point3(settle * sx, settle * sy, settle * sz)
        stretchPt = Point3(settle * tx, settle * ty, settle * tz)
        try:
            titleNP.setScale(settlePt)
        except Exception:
            return Sequence(name='campaignHandoffTitleHosePopEmpty')
        parts = [
            LerpScaleInterval(
                titleNP, float(squashSec), squashPt, blendType='easeOut'),
            LerpScaleInterval(
                titleNP, float(stretchSec), stretchPt, blendType='easeOut'),
            LerpScaleInterval(
                titleNP, settleSec, settlePt, blendType='easeIn'),
        ]
        if trustSettle:
            ox, oy, oz, overSec = getattr(
                CampaignGlobals, 'OSWALD_TRUST_BANNER_SETTLE_OVERSHOOT',
                (0.90, 1.0, 1.14, 0.07))
            restSec = float(getattr(
                CampaignGlobals, 'OSWALD_TRUST_BANNER_SETTLE_REST_SEC', 0.09))
            overPt = Point3(settle * ox, settle * oy, settle * oz)
            parts.append(LerpScaleInterval(
                titleNP, float(overSec), overPt, blendType='easeOut'))
            parts.append(LerpScaleInterval(
                titleNP, restSec, settlePt, blendType='easeIn'))
        return Sequence(*parts, name='campaignHandoffTitleHosePop')

    def _trustSubHosePopInterval(self, subNP, settleScale):
        """Tip-matched squash → stretch → settle on Oswald trust subtitle."""
        settle = float(settleScale)
        sx, sy, sz, squashSec = getattr(
            CampaignGlobals, 'OSWALD_TRUST_SUB_POP_SQUASH',
            (1.50, 1.0, 0.56, 0.05))
        tx, ty, tz, stretchSec = getattr(
            CampaignGlobals, 'OSWALD_TRUST_SUB_POP_STRETCH',
            (0.80, 1.0, 1.40, 0.08))
        settleSec = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_SUB_POP_SETTLE_SEC', 0.10))
        settlePt = Point3(settle, settle, settle)
        squashPt = Point3(settle * sx, settle * sy, settle * sz)
        stretchPt = Point3(settle * tx, settle * ty, settle * tz)
        try:
            subNP.setScale(settlePt)
        except Exception:
            return Sequence(name='campaignHandoffTrustSubHosePopEmpty')
        return Sequence(
            LerpScaleInterval(
                subNP, float(squashSec), squashPt, blendType='easeOut'),
            LerpScaleInterval(
                subNP, float(stretchSec), stretchPt, blendType='easeOut'),
            LerpScaleInterval(
                subNP, settleSec, settlePt, blendType='easeIn'),
            name='campaignHandoffTrustSubHosePop',
        )

    def _makeLine(self, parent, name, text, color, scale, z):
        tn = TextNode(name)
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(color[0], color[1], color[2], 1)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0, 0, 0, 0.8)
        tn.setWordwrap(28)
        np = parent.attachNewNode(tn)
        np.setScale(scale)
        np.setPos(0, 0, z)
        np.setBin('fixed', 62)
        np.setDepthTest(False)
        np.setDepthWrite(False)
        return np

    def _clear(self):
        if self._ival:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        try:
            clearHandoffConfetti()
        except Exception:
            pass
        try:
            clearVictoryCreamSwell()
        except Exception:
            pass
        try:
            clearHandoffCreamEdge()
        except Exception:
            pass
        try:
            clearOswaldTrustBannerCreamEdge()
        except Exception:
            pass
        if self._rootNP and not self._rootNP.isEmpty():
            self._rootNP.removeNode()
        self._rootNP = None


_client = None


def ensureCampaignHandoffClient():
    global _client
    if _client is None:
        _client = CampaignHandoffClient()
    return _client
