"""Client-visible campaign handoff banners + melee power bump on reclaim.

Act clears (Loopy → Punchline → Silly) play as a short Toontown reclaim
celebration — Oswald as the trusted face, title hose-pop, clear next-street
cue — not a single toast line. Finale victory keeps the Oswald twist beat.
After Corrupted Oswald chase clear, an epilogue soft-end plate points the
hub replay tip (twist→soft-end authored beat — not cream FX deepen).
HubEpilogueBeat adds the washed-plaza world placemarker beyond this plate.

Title lands with the same squash→stretch→settle rubber-hose scale pop as
PlayEntry tip/act-enter banners (tunables in CampaignGlobals). Early/mid
trusted Oswald lead clears also settle-bounce the title and hose-pop the
Oswald cheer/lead subtitle, framed by a soft cream edge pulse and a
delayed soft cream wash pulse (no carnival / no twist spoilers). Loopy
PlayEntry arms a mid-act unease approach tip (smile sticks a rubbery
half-beat) before Punchline handoff while early street entry stays
trusted. Loopy and Punchline clears arm mid-act trust fracture: off-tone
cheer copy + cooler cream edge that settles into soft shadow flecks
(still no Silly twist spoilers). Act
handoffs fire a short confetti / streamer + cream-sparkle pop
(CampaignHandoffConfetti) framed by a soft cream edge pulse with a
juicier deepened rubber-hose scale settle past #271 (overshoot → rest →
micro rebound) and a delayed soft cream wash pulse tuned to the carnival
glitter — no KH / keyblade framing. Distinct from tip/title cream hose
settles.
Campaign victory fires a soft cream confetti swell + cream
sparkle on the purity cheer only, framed by a victory-tuned cream edge
and a delayed soft cream wash pulse with a residual cream aftershock
(flecks + soft halo); it clears before the Oswald twist / FinalePhaseFx
reveal so the bittersweet sting stays intact. When Silly finale betrayal
reveal fires (oswaldRevealBanner), a dedicated betrayal handoff plate
hose-pops the twist copy with a juicier deepened cream hose settle past
#260 (overshoot → rest → micro rebound) so the twist lands juicier —
complements almost-confess tip (#207) — and a deepened victory/confetti
cream sting (VictoryTwistConfettiSting: juicier chips + taller micro cream
pop rebound + richer soft cream aftershock, past #265) lands the hollow
cheer that Oswald caused the corruption. Distinct from act handoff cream
edge settle deepen (#240/#271), Punchline tip cream hose rebound
(#256/#284 — tip bar, not betrayal title), betrayal banner cream hose
(#235/#260/#288), victory twist sting (#265/#300), and Silly
almost-confess tip (#232/#279/#294).
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
    clearFinaleRevealCreamEdge,
    clearHandoffCreamEdge,
    clearOswaldTrustBannerCreamEdge,
    clearOswaldTrustFractureCreamEdge,
    clearVictoryCreamEdge,
    playFinaleRevealCreamEdge,
    playHandoffCreamEdge,
    playOswaldTrustBannerCreamEdge,
    playOswaldTrustFractureCreamEdge,
    playVictoryCreamEdge,
)
from toontown.campaign.CampaignHandoffConfetti import (
    clearHandoffConfetti,
    clearVictoryCreamSwell,
    playHandoffConfetti,
    playVictoryCreamSwell,
)
from toontown.campaign.CampaignPower import (
    applyPowerBump,
    streetClearRewardEnabled,
    streetClearRewardPayload,
)
from toontown.campaign.HandoffCreamWashFx import (
    clearHandoffCreamWash,
    playHandoffCreamWash,
)
from toontown.campaign.OswaldTrustCreamWashFx import (
    clearOswaldTrustCreamWash,
    playOswaldTrustCreamWash,
)
from toontown.campaign.VictoryCreamWashFx import (
    clearVictoryCreamWash,
    playVictoryCreamWash,
)
from toontown.campaign.VictoryTwistConfettiSting import (
    clearVictoryTwistConfettiSting,
    playVictoryTwistConfettiSting,
)

# Celebration timing — readable rubber-hose reclaim beat, not a flash toast.
# Title settle/pop tunables live in CampaignGlobals (HANDOFF_TITLE_*).
_SUB_SCALE = 0.048
_CUE_SCALE = 0.052
_POWER_SCALE = 0.036
_REWARD_SCALE = 0.034
_HOLD_SEC = 4.6
_CARD_COLOR = (0.12, 0.28, 0.22, 0.55)
_BETRAYAL_CARD_COLOR = (0.18, 0.08, 0.10, 0.62)
_TITLE_COLOR = Vec4(0.55, 1.0, 0.78, 1)
_SUB_COLOR = Vec4(0.95, 1.0, 0.88, 1)
_CUE_COLOR = Vec4(1.0, 0.92, 0.42, 1)
_POWER_COLOR = Vec4(0.75, 0.95, 1.0, 1)
_REWARD_COLOR = Vec4(1.0, 0.88, 0.42, 1)
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
        # AI absolute reclaimCount mirrored via campaignProgressSync / PM.
        # Kept separate so sync-before-purity can raise power without
        # advancing the live local watermark ahead of purityRestore.
        self._syncedReclaimCount = 0
        # First progress sync this session adopts absolute reclaimCount
        # (login hydrate). Later persist pushes only refresh _synced*.
        self._powerHydrated = False
        self._finaleClears = 0
        self._betrayalArmed = False
        self._epilogueShown = False
        self.accept('purityRestoreFx', self._onPurityRestore)
        self.accept('campaignVictory', self._onVictory)
        self.accept('campaignPhase', self._onPhase)
        self.accept('reclaimFinalePhase', self._onReclaimFinalePhase)
        # FinalePhaseFx playTransition sting banner — readable P1→P2 hose
        # plate (campaignPhase skips phase >= 2; orphan → accept).
        stingMsg = getattr(
            CampaignGlobals, 'FINALE_PHASE_STING_BANNER_MSG',
            'finalePhaseStingBanner')
        self.accept(stingMsg, self._onFinalePhaseStingBanner)
        # FinalePhaseFx fires this when the betrayal AV sting lands — handoff
        # plate owns the readable twist copy (hose-pop, not plain TextNode).
        self.accept('oswaldRevealBanner', self._onOswaldBetrayalBanner)
        # Chase-clear epilogue soft-end (AI-local + client watch rebroadcast).
        self.accept('oswaldBetrayalChaseCleared', self._onChaseCleared)
        self.accept('campaignEpilogue', self._onChaseCleared)
        # Login / hydrate: re-apply POWER_BUMP from AI-persisted reclaimCount
        # so mid-campaign relog keeps melee scale (silent — no handoff plate).
        syncMsg = getattr(
            CampaignGlobals, 'CAMPAIGN_PROGRESS_SYNC_MSG',
            'campaignProgressSync')
        self.accept(syncMsg, self._onCampaignProgressSync)

    def destroy(self):
        self.ignoreAll()
        self._clear()

    def _onReclaimFinalePhase(self, phaseIndex):
        # Keep a client-side phase counter so purity messaging stays honest.
        phase = int(phaseIndex)
        if phase >= 1:
            self._finaleClears = max(self._finaleClears, phase - 1)

    def _pollutionReclaimCount(self):
        """Thin read of PollutionManager.campaignReclaimCount (0 if unknown)."""
        try:
            cr = getattr(base, 'cr', None)  # noqa: F821
            if cr is None:
                return 0
            pm = getattr(cr, 'pollutionManager', None)
            if pm is None:
                return 0
            return max(0, int(getattr(pm, 'campaignReclaimCount', 0) or 0))
        except Exception:
            return 0

    def _applyReclaimPower(self, count):
        """Idempotent COMBO_DAMAGE scale to an absolute reclaim watermark."""
        count = max(0, int(count or 0))
        self._localReclaimCount = max(self._localReclaimCount, count)
        return applyPowerBump(self._localReclaimCount)

    def _onCampaignProgressSync(
            self, unlockedThrough=0, state=0, chaseCleared=0, reclaimCount=0):
        """Silent power rehydrate from AI reclaimCount (login / persist push).

        First sync this session adopts the absolute count (login hydrate).
        Later persist pushes refresh the synced watermark only — so a
        sync-before-purity race cannot stack an extra live +=1 on top.
        Power always matches max(local, synced).
        """
        count = max(0, int(reclaimCount or 0))
        self._syncedReclaimCount = max(self._syncedReclaimCount, count)
        if not self._powerHydrated:
            self._localReclaimCount = count
            self._powerHydrated = True
        applyPowerBump(max(self._localReclaimCount, self._syncedReclaimCount))

    def _onPurityRestore(self, zoneId):
        # Live street clear: advance one, but absorb AI absolute when progress
        # sync already landed for this clear (sync-before-purity dedupe).
        self._powerHydrated = True
        synced = max(self._syncedReclaimCount, self._pollutionReclaimCount())
        if synced > self._localReclaimCount:
            # Sync raced ahead — adopt absolute, do not stack +=1.
            mult = self._applyReclaimPower(synced)
        else:
            mult = self._applyReclaimPower(self._localReclaimCount + 1)
        # Street-trophy jellybean / laff line — client mirror of AI award
        # (CampaignPower.awardStreetClearReward). Beyond COMBO_DAMAGE bump.
        rewardLine = self._streetClearRewardLine(zoneId)
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
                    rewardLine=rewardLine,
                    nextStreet=None)
            else:
                # Purity cheer only — betrayal handoff plate lands the twist
                # when oswaldRevealBanner fires (synced with FinalePhaseFx AV).
                self._betrayalArmed = bool(act.get('betrayalHandoff', True))
                self._celebrate(
                    'TOON CITY IS SAVED!',
                    subtitle='%s leads the neighborhood cheer' % face,
                    nextCue='Purity holds…',
                    color=_VICTORY_COLOR,
                    powerMult=mult,
                    rewardLine=rewardLine,
                    nextStreet=None,
                    holdSec=2.4,
                    creamSwell=True)
            return
        if act is None:
            self._celebrate(
                'Neighborhood reclaimed!',
                subtitle='%s tips his hat — corruption washed clean' % face,
                nextCue='Scout the next polluted street',
                color=_TITLE_COLOR,
                powerMult=mult,
                rewardLine=rewardLine,
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
        # trustFracture (Loopy + Punchline): off-tone cheer + cool cream/shadow.
        self._celebrate(
            title,
            subtitle=subtitle,
            nextCue=nextCue,
            color=_TITLE_COLOR,
            powerMult=mult,
            rewardLine=rewardLine,
            nextStreet=nextStreet,
            confetti=True,
            trustSettle=True,
            trustFracture=bool(act.get('trustFracture')))

    def _streetClearRewardLine(self, zoneId):
        """Handoff plate line for jellybean / laff street trophy (or None)."""
        if not streetClearRewardEnabled():
            return None
        try:
            payload = streetClearRewardPayload(
                reclaimCount=self._localReclaimCount, zoneId=zoneId)
        except Exception:
            return None
        line = payload.get('handoff') if payload else None
        return line or None

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
        # Purity cheer (+ cream confetti swell). Twist copy is owned by the
        # betrayal handoff plate on oswaldRevealBanner — cream swell stays
        # cheer-only so the bittersweet sting stays intact. Fallback twist
        # onDone only when betrayal handoff is not armed.
        face = _face()
        tease = getattr(CampaignGlobals, 'FINALE_TWIST_TEASE', '')
        teaseColor = Vec4(*getattr(
            CampaignGlobals, 'FINALE_TWIST_TEASE_COLOR',
            (1.0, 0.55, 0.35, 1.0)))
        finale = None
        for act in CampaignGlobals.ACTS:
            if act.get('finale'):
                finale = act
                break
        betrayalOwnsTwist = bool(
            finale and finale.get('betrayalHandoff', True) and tease)
        if betrayalOwnsTwist:
            self._betrayalArmed = True
        if not tease or betrayalOwnsTwist:
            self._celebrate(
                'TOON CITY IS SAVED!',
                subtitle='%s leads the neighborhood cheer' % face,
                nextCue=('Purity holds…' if betrayalOwnsTwist else
                         'Purity holds — take a victory lap!'),
                color=_VICTORY_COLOR,
                powerMult=None,
                nextStreet=None,
                holdSec=2.4 if betrayalOwnsTwist else None,
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

    def _onChaseCleared(self, doId=0):
        """Land epilogue soft-end plate after Corrupted Oswald chase clear."""
        if not bool(getattr(
                CampaignGlobals, 'CAMPAIGN_EPILOGUE_ENABLED', True)):
            return
        if self._epilogueShown:
            return
        self._epilogueShown = True
        self._showEpilogueHandoff()
        # Washed-plaza world beat beyond this HUD plate (HubEpilogueBeat).
        self._refreshHubEpilogueBeat()

    def _refreshHubEpilogueBeat(self):
        """Arm TTC washed-plaza placemarker after chase-clear soft-end."""
        try:
            from toontown.campaign.HubEpilogueBeat import (
                refreshHubEpilogueBeat)
            refreshHubEpilogueBeat()
        except Exception:
            pass

    def _showEpilogueHandoff(self):
        """Hose-pop soft-end plate: stain washed → hub replay tip."""
        from toontown.campaign.OswaldBetrayalChase import (
            epilogueCue, epilogueSub, epilogueTitle)

        title = epilogueTitle()
        subtitle = epilogueSub()
        cue = epilogueCue()
        hold = float(getattr(
            CampaignGlobals, 'CAMPAIGN_EPILOGUE_HOLD_SEC', 3.6))
        # Point soft cue at Loopy so hub / rematch latch stays discoverable.
        nextStreet = CampaignGlobals.ACTS[0]['name']
        self._celebrate(
            title,
            subtitle=subtitle,
            nextCue=cue,
            color=_VICTORY_COLOR,
            powerMult=None,
            nextStreet=nextStreet,
            holdSec=hold,
            trustSettle=True)

    def _onOswaldBetrayalBanner(self, title=''):
        """Land the betrayal handoff plate when Silly finale reveal fires."""
        if not self._betrayalArmed:
            # Still land if finale act asks for betrayal handoff (messenger
            # may arrive without a prior purity/victory cheer on this client).
            finale = None
            for act in CampaignGlobals.ACTS:
                if act.get('finale'):
                    finale = act
                    break
            if not (finale and finale.get('betrayalHandoff', True)):
                return
        self._betrayalArmed = False
        self._showBetrayalHandoff(title=title)

    def _showBetrayalHandoff(self, title=''):
        """Hose-pop handoff plate that lands Oswald caused the corruption."""
        face = _face()
        finale = None
        for act in CampaignGlobals.ACTS:
            if act.get('finale'):
                finale = act
                break
        banner = (
            title
            or getattr(CampaignGlobals, 'FINALE_REVEAL_BANNER', '')
            or (finale.get('handoffTitle') if finale else None)
            or 'OSWALD CAUSED THE CORRUPTION')
        subtitle = getattr(
            CampaignGlobals, 'FINALE_REVEAL_SUB', '') or (
            finale.get('handoff') if finale else '') or (
            '%s smiles too wide — the ink was his all along' % face)
        cue = getattr(
            CampaignGlobals, 'FINALE_BETRAYAL_HANDOFF_CUE', '') or (
            finale.get('nextCue') if finale else '') or (
            'Oswald caused the corruption')
        color = Vec4(*getattr(
            CampaignGlobals, 'FINALE_REVEAL_BANNER_COLOR',
            (1.0, 0.42, 0.28, 1.0)))
        hold = float(getattr(
            CampaignGlobals, 'FINALE_BETRAYAL_HANDOFF_HOLD_SEC', 3.8))
        self._celebrate(
            banner,
            subtitle=subtitle,
            nextCue=cue,
            color=color,
            powerMult=None,
            nextStreet=None,
            holdSec=hold,
            betrayalHandoff=True)

    def _onPhase(self, phaseIndex, message):
        # Skip duplicate flash when finale phase FX already own phase 2 —
        # readable P2 plate lands via finalePhaseStingBanner accept.
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

    def _onFinalePhaseStingBanner(self, phase=0, title=''):
        """Accept FinalePhaseFx sting banner → readable P1→P2 hose plate.

        FOV/flash sting already fired in FinalePhaseFx; this owns the
        hose-pop copy that campaignPhase skips for phase >= 2. PlayEntry
        thin-accepts the same messenger for the tip bar (no soft-next latch).
        No cream deepen / no KH branding.
        """
        if not bool(getattr(
                CampaignGlobals, 'FINALE_PHASE_STING_PLATE_ENABLED', True)):
            return
        self._showFinalePhaseStingPlate(phase=phase, title=title)

    def _showFinalePhaseStingPlate(self, phase=0, title=''):
        """Hose-pop phase-transition plate for Overlord P1→P2 sting."""
        face = _face()
        phase = max(1, int(phase or 1))
        banner = (
            title
            or CampaignGlobals.FINALE_PHASE_BANNER.get(phase)
            or 'FINALE PHASE %s' % phase)
        subtitle = CampaignGlobals.FINALE_PHASE_SUB.get(
            phase, '%s rallies the reclaim!' % face)
        cue = CampaignGlobals.finalePhaseStingCueText(phase)
        color = _FINALE_P2_COLOR if phase >= 2 else _PHASE_COLOR
        hold = float(getattr(
            CampaignGlobals, 'FINALE_PHASE_STING_HOLD_SEC', 3.2))
        self._celebrate(
            banner,
            subtitle=subtitle,
            nextCue=cue,
            color=color,
            powerMult=None,
            nextStreet=None,
            holdSec=hold,
            emitHandoffCue=False)

    def _celebrate(self, title, subtitle='', nextCue='', color=_TITLE_COLOR,
                   powerMult=None, rewardLine=None, nextStreet=None,
                   holdSec=None, onDone=None,
                   confetti=False, trustSettle=False, creamSwell=False,
                   trustFracture=False, betrayalHandoff=False,
                   emitHandoffCue=True):
        """Staged rubber-hose celebration: card → title pop → cue → hold."""
        self._clear()
        root = aspect2d.attachNewNode('campaign-handoff-root')  # noqa: F821
        # Betrayal plate sits a touch lower so FinalePhaseFx shadow/flash
        # still read above the ink sting without covering the title.
        root.setPos(0, 0, 0.36 if betrayalHandoff else 0.42)
        root.setTransparency(TransparencyAttrib.MAlpha)
        root.setColorScale(1, 1, 1, 0)
        self._rootNP = root
        hold = _HOLD_SEC if holdSec is None else float(holdSec)

        if betrayalHandoff:
            # Soft cream edge frame under the twist plate — FinalePhaseFx
            # still owns flash/shadow/aftershock; plate owns readable copy.
            try:
                playFinaleRevealCreamEdge()
            except Exception:
                pass
            # Deepened bittersweet victory/confetti cream sting past #265 —
            # juicier chips + taller micro cream pop rebound + richer soft
            # cream aftershock so the hollow cheer that Oswald caused the
            # corruption lands readable (#82 swell already cleared).
            try:
                origin = getattr(
                    CampaignGlobals, 'VICTORY_TWIST_CONFETTI_ORIGIN',
                    (0.0, 0.0, 0.34))
                playVictoryTwistConfettiSting(origin=origin)
            except Exception:
                pass
        elif creamSwell:
            # Soft cream swell under the purity victory plate only.
            try:
                origin = getattr(
                    CampaignGlobals, 'VICTORY_CREAM_SWELL_ORIGIN',
                    (0.0, 0.0, 0.36))
                playVictoryCreamSwell(origin=origin)
            except Exception:
                pass
            # Cream edge frame tuned to victory cream confetti / sparkle
            # (#82/#105). Cheer-only — twist / phase stay edge-free.
            try:
                playVictoryCreamEdge()
            except Exception:
                pass
            # Soft cream wash pulse + delayed cream aftershock after cream
            # edge / sparkle (#129/#105) — melee / perfect-dodge wash +
            # entry / purity-complete aftershock grammar. Cheer-only.
            try:
                playVictoryCreamWash()
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
            if trustFracture:
                # Mid-act unease: cool cream → soft shadow flecks
                # (Loopy + Punchline). Carnival stays; sunny edge/wash swap.
                try:
                    playOswaldTrustFractureCreamEdge()
                except Exception:
                    pass
            else:
                # Cream edge frame tuned to cream-sparkle carnival banners (#99).
                # Early/mid trusted Oswald only — twist / phase stay edge-free.
                try:
                    playHandoffCreamEdge()
                except Exception:
                    pass
                # Soft cream wash pulse after cream edge / sparkle (#124/#99) —
                # victory / melee / perfect-dodge wash grammar. Handoff-only.
                try:
                    playHandoffCreamWash()
                except Exception:
                    pass
        elif trustSettle:
            # Trust hose-settle without carnival — keep #117 trust cream edge.
            try:
                playOswaldTrustBannerCreamEdge()
            except Exception:
                pass
            # Soft cream wash pulse + delayed cream aftershock after trust
            # cream edge (#117) — finale reveal wash aftershock grammar
            # (#176) / victory (#168). Trusted early/mid only.
            try:
                playOswaldTrustCreamWash()
            except Exception:
                pass

        try:
            cm = CardMaker('campaign-handoff-card')
            # Extra lower band when street-trophy reward sits under power bump.
            cardBottom = -0.34 if (rewardLine or powerMult is not None) else -0.28
            cm.setFrame(-1.15, 1.15, cardBottom, 0.22)
            card = root.attachNewNode(cm.generate())
            card.setTransparency(TransparencyAttrib.MAlpha)
            card.setColor(*(
                _BETRAYAL_CARD_COLOR if betrayalHandoff else _CARD_COLOR))
            card.setBin('fixed', 60)
            card.setDepthTest(False)
            card.setDepthWrite(False)
        except Exception:
            pass

        titleScale = float(getattr(
            CampaignGlobals, 'HANDOFF_TITLE_SCALE', 0.078))
        if betrayalHandoff:
            titleScale = float(getattr(
                CampaignGlobals, 'HANDOFF_TITLE_SCALE', 0.078)) * 0.95
        titleNP = self._makeLine(
            root, 'campaign-handoff-title', title, color, titleScale, 0.08)
        subScale = float(getattr(
            CampaignGlobals, 'OSWALD_TRUST_SUB_SCALE', _SUB_SCALE))
        if not trustSettle and not betrayalHandoff:
            subScale = _SUB_SCALE
        subNP = None
        if subtitle:
            subColor = _SUB_COLOR
            if betrayalHandoff:
                betr = getattr(
                    CampaignGlobals, 'FINALE_BETRAYAL_SUB_COLOR', None)
                if betr is not None:
                    subColor = Vec4(*betr)
                else:
                    subColor = Vec4(*getattr(
                        CampaignGlobals, 'FINALE_REVEAL_SUB_COLOR',
                        (1.0, 0.72, 0.48, 1.0)))
            elif trustFracture:
                frac = getattr(
                    CampaignGlobals, 'OSWALD_TRUST_FRACTURE_SUB_COLOR', None)
                if frac is not None:
                    subColor = Vec4(*frac)
            subNP = self._makeLine(
                root, 'campaign-handoff-sub', subtitle, subColor,
                subScale, -0.02)
            subNP.setColorScale(1, 1, 1, 0)
        cueText = nextCue
        if nextStreet and nextStreet not in (nextCue or ''):
            cueText = nextCue or ('Next street → %s' % nextStreet)
        cueNP = None
        if cueText:
            cueColor = _CUE_COLOR
            if betrayalHandoff:
                betrCue = getattr(
                    CampaignGlobals, 'FINALE_BETRAYAL_CUE_COLOR', None)
                if betrCue is not None:
                    cueColor = Vec4(*betrCue)
            cueNP = self._makeLine(
                root, 'campaign-handoff-cue', cueText, cueColor,
                _CUE_SCALE, -0.11)
            cueNP.setColorScale(1, 1, 1, 0)
            cueNP.setScale(_CUE_SCALE * 0.55)
        powerNP = None
        rewardNP = None
        # Power bump + street-trophy reward share the lower plate band.
        powerZ = -0.20
        rewardZ = -0.20
        if powerMult is not None and rewardLine:
            powerZ = -0.18
            rewardZ = -0.26
        if powerMult is not None:
            powerNP = self._makeLine(
                root, 'campaign-handoff-power',
                'Melee power  x%.2f' % float(powerMult),
                _POWER_COLOR, _POWER_SCALE, powerZ)
            powerNP.setColorScale(1, 1, 1, 0)
        if rewardLine:
            rewardNP = self._makeLine(
                root, 'campaign-handoff-reward',
                str(rewardLine),
                _REWARD_COLOR, _REWARD_SCALE, rewardZ)
            rewardNP.setColorScale(1, 1, 1, 0)

        parts = [
            LerpColorScaleInterval(root, 0.18, Vec4(1, 1, 1, 1)),
            self._titleHosePopInterval(
                titleNP, titleScale, trustSettle=trustSettle,
                trustFracture=trustFracture,
                betrayalHandoff=betrayalHandoff),
        ]
        if subNP is not None:
            if trustSettle or betrayalHandoff:
                # Oswald trusted cheer/lead subtitle — tip-matched hose settle.
                # Betrayal plate also hose-pops the twist sub for readability.
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
        if rewardNP is not None:
            parts.append(Sequence(
                Wait(0.62),
                LerpColorScaleInterval(rewardNP, 0.2, Vec4(1, 1, 1, 1)),
            ))

        if emitHandoffCue:
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

    def _titleHosePopInterval(self, titleNP, settleScale, trustSettle=False,
                              trustFracture=False, betrayalHandoff=False):
        """Tip-matched squash → stretch → settle on the handoff title.

        Early/mid Oswald trusted reclaim-lead clears append a soft
        overshoot → rest settle bounce after the hose pop. Trust fracture
        holds the settle a rubbery beat longer (mid-act unease). Betrayal
        handoff holds even longer so the twist title lands hard, then a
        juicier deepened cream hose settle past #260 (overshoot → rest →
        micro rebound) so the twist plate reads juicier.
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
        if trustSettle or betrayalHandoff:
            if betrayalHandoff:
                ox, oy, oz, overSec = getattr(
                    CampaignGlobals, 'FINALE_BETRAYAL_SETTLE_OVERSHOOT',
                    (0.86, 1.0, 1.22, 0.10))
                restSec = float(getattr(
                    CampaignGlobals, 'FINALE_BETRAYAL_SETTLE_REST_SEC',
                    0.16))
            elif trustFracture:
                ox, oy, oz, overSec = getattr(
                    CampaignGlobals, 'OSWALD_TRUST_FRACTURE_SETTLE_OVERSHOOT',
                    (0.88, 1.0, 1.18, 0.09))
                restSec = float(getattr(
                    CampaignGlobals, 'OSWALD_TRUST_FRACTURE_SETTLE_REST_SEC',
                    0.14))
            else:
                ox, oy, oz, overSec = getattr(
                    CampaignGlobals, 'OSWALD_TRUST_BANNER_SETTLE_OVERSHOOT',
                    (0.90, 1.0, 1.14, 0.07))
                restSec = float(getattr(
                    CampaignGlobals, 'OSWALD_TRUST_BANNER_SETTLE_REST_SEC',
                    0.09))
            overPt = Point3(settle * ox, settle * oy, settle * oz)
            parts.append(LerpScaleInterval(
                titleNP, float(overSec), overPt, blendType='easeOut'))
            parts.append(LerpScaleInterval(
                titleNP, restSec, settlePt, blendType='easeIn'))
        # Juicier deepened cream hose settle past #260 after betrayal settle
        # — climax twist land (tip cream hose rebound twin; distinct from
        # Punchline #227/#256/#284 tip bar and Silly #232/#279 almost-
        # confess tip).
        if betrayalHandoff and bool(getattr(
                CampaignGlobals, 'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_ENABLED',
                True)):
            creamOver = getattr(
                CampaignGlobals, 'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_OVERSHOOT',
                None)
            cx = cy = cz = creamOverSec = None
            if creamOver:
                try:
                    cx, cy, cz, creamOverSec = creamOver
                    creamOverSec = float(creamOverSec)
                except Exception:
                    creamOverSec = None
            if creamOverSec is not None and creamOverSec > 0.0:
                creamRestSec = float(getattr(
                    CampaignGlobals,
                    'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REST_SEC', 0.15))
                creamOverPt = Point3(
                    settle * float(cx), settle * float(cy), settle * float(cz))
                parts.append(LerpScaleInterval(
                    titleNP, max(0.01, creamOverSec), creamOverPt,
                    blendType='easeOut'))
                parts.append(LerpScaleInterval(
                    titleNP, max(0.01, creamRestSec), settlePt,
                    blendType='easeIn'))
                # Micro rebound after cream overshoot→rest (past #260).
                creamRebound = getattr(
                    CampaignGlobals,
                    'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND', None)
                rx = ry = rz = reboundSec = None
                if creamRebound:
                    try:
                        rx, ry, rz, reboundSec = creamRebound
                        reboundSec = float(reboundSec)
                    except Exception:
                        reboundSec = None
                if reboundSec is not None and reboundSec > 0.0:
                    reboundRestSec = float(getattr(
                        CampaignGlobals,
                        'FINALE_BETRAYAL_CREAM_HOSE_SETTLE_REBOUND_REST_SEC',
                        0.08))
                    reboundPt = Point3(
                        settle * float(rx), settle * float(ry),
                        settle * float(rz))
                    parts.append(LerpScaleInterval(
                        titleNP, max(0.01, reboundSec), reboundPt,
                        blendType='easeOut'))
                    parts.append(LerpScaleInterval(
                        titleNP, max(0.01, reboundRestSec), settlePt,
                        blendType='easeIn'))
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
            clearVictoryTwistConfettiSting()
        except Exception:
            pass
        try:
            clearHandoffCreamEdge()
        except Exception:
            pass
        try:
            clearHandoffCreamWash()
        except Exception:
            pass
        try:
            clearVictoryCreamEdge()
        except Exception:
            pass
        try:
            clearVictoryCreamWash()
        except Exception:
            pass
        try:
            clearOswaldTrustBannerCreamEdge()
        except Exception:
            pass
        try:
            clearOswaldTrustFractureCreamEdge()
        except Exception:
            pass
        try:
            clearOswaldTrustCreamWash()
        except Exception:
            pass
        try:
            clearFinaleRevealCreamEdge()
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
