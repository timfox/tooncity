"""Client-visible campaign handoff banners + melee power bump on reclaim."""

from panda3d.core import TextNode, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
from toontown.campaign.CampaignPower import applyPowerBump


class CampaignHandoffClient(DirectObject):
    """Shows next-hood / phase / victory copy when streets are reclaimed."""

    def __init__(self):
        DirectObject.__init__(self)
        self._bannerNP = None
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
        act, nxt = self._actsForZone(zoneId)
        if act and act.get('finale'):
            self._finaleClears += 1
            if self._finaleClears <= 1:
                phase2 = act.get('phase2') or {}
                self._flash(
                    phase2.get('banner') or 'Finale Phase 2!',
                    Vec4(1.0, 0.35, 0.55, 1))
            else:
                self._flash(
                    act.get('handoff') or 'Toon City is saved!',
                    Vec4(1.0, 0.95, 0.45, 1))
            return
        if nxt is not None:
            msg = act.get('handoff') or (
                'Next hood: %s (zone %s)' % (nxt['name'], nxt['zoneId']))
            self._flash(
                '%s  |  melee x%.2f' % (msg, mult),
                Vec4(0.55, 1.0, 0.75, 1))
        else:
            self._flash(
                'Neighborhood reclaimed!  melee x%.2f' % mult,
                Vec4(0.55, 1.0, 0.75, 1))

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
        # Purity first; soft Oswald-twist tease keeps room for later dialogue.
        self._flash(
            'CAMPAIGN VICTORY!  Toon City is pure',
            Vec4(1.0, 0.95, 0.45, 1))
        tease = getattr(CampaignGlobals, 'FINALE_TWIST_TEASE', '')
        if tease:
            self._flash(
                tease,
                Vec4(*getattr(
                    CampaignGlobals, 'FINALE_TWIST_TEASE_COLOR',
                    (0.85, 0.75, 1.0, 1.0))))

    def _onPhase(self, phaseIndex, message):
        # Skip duplicate flash when FinalePhaseFx / reclaim banners already
        # own the phase-2 transition moment.
        phase = int(phaseIndex) + 1
        if phase >= 2:
            return
        self._flash(
            'PHASE %s — %s' % (phase, message),
            Vec4(1.0, 0.45, 0.85, 1))

    def _flash(self, text, color):
        self._clear()
        tn = TextNode('campaign-handoff')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(color[0], color[1], color[2], 1)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0, 0, 0, 0.75)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        np.setScale(0.065)
        np.setPos(0, 0, 0.55)
        np.setColorScale(1, 1, 1, 0)
        self._bannerNP = np
        self._ival = Sequence(
            LerpColorScaleInterval(np, 0.2, Vec4(1, 1, 1, 1)),
            Wait(3.4),
            LerpColorScaleInterval(np, 0.45, Vec4(1, 1, 1, 0)),
            Func(self._clear),
        )
        self._ival.start()

    def _clear(self):
        if self._ival:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._bannerNP and not self._bannerNP.isEmpty():
            self._bannerNP.removeNode()
        self._bannerNP = None


_client = None


def ensureCampaignHandoffClient():
    global _client
    if _client is None:
        _client = CampaignHandoffClient()
    return _client
