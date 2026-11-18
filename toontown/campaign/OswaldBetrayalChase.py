"""Short corrupted-Oswald chase after finale betrayal.

Gameplay payload for the Oswald twist: CampaignDirectorAI schedules a
thin ARCHETYPE_CORRUPT_OSWALD spawn after Silly finale victory / reveal.
Client tip + melee arm land when the chase fields. Not cream FX; not a
full new campaign act. Toontown spiritual sequel — no keyblades / KH.
"""

from __future__ import annotations

import math

from panda3d.core import TextNode, Vec4

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
from toontown.corruption import CorruptionGlobals
from toontown.corruption.DistributedCorruptToonAI import DistributedCorruptToonAI


def chaseEnabled():
    return bool(getattr(CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_ENABLED', True))


def chaseDelaySec():
    return max(0.0, float(getattr(
        CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_DELAY_SEC', 3.15)))


def chaseName():
    return str(getattr(
        CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_NAME', 'Corrupted Oswald'))


def chaseHp():
    hp = int(getattr(CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_HP', 0) or 0)
    if hp > 0:
        return hp
    return CorruptionGlobals.archetypeDefaultHp(
        CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD)


def chaseTip():
    return str(getattr(
        CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_TIP',
        'Oswald turns on you — Corrupted Oswald inbound!  |  '
        'F fight  |  Shift dodge'))


def chaseBanner():
    return str(getattr(
        CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_BANNER',
        'CORRUPTED OSWALD CHASE!'))


def chaseSpawnMsg():
    return str(getattr(
        CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_MSG',
        'Oswald sheds the smile — chase him down and wash the stain!'))


def chaseClearMsg():
    return str(getattr(
        CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_CLEAR_MSG',
        "Oswald's stain is washed — purity holds for real this time!"))


def spawnCorruptOswald(air, toon, zoneId=None, forward=None):
    """Spawn one fightable Corrupted Oswald near `toon`. Returns AI or None."""
    if air is None or toon is None:
        return None
    if zoneId is None:
        zoneId = int(getattr(toon, 'zoneId', 0) or 0)
    zoneId = int(zoneId)
    if zoneId <= 0:
        return None
    if forward is None:
        forward = float(getattr(
            CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_SPAWN_FORWARD', 7.5))
    forward = float(forward)

    archetype = CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD
    name = chaseName()
    hp = chaseHp()
    corrupt = DistributedCorruptToonAI(
        air, name=name, maxHp=hp, archetype=archetype, finalePhase=0)
    corrupt.hp = corrupt.maxHp

    baseX = float(toon.getX())
    baseY = float(toon.getY())
    baseZ = float(toon.getZ())
    heading = float(toon.getH())
    rad = math.radians(heading)
    x = baseX - math.sin(rad) * forward
    y = baseY + math.cos(rad) * forward
    corrupt.setPos(x, y, baseZ)
    corrupt.setH(heading + 180.0)
    corrupt.generateWithRequired(zoneId)
    return corrupt


_TIP_COLOR = Vec4(1.0, 0.55, 0.4, 1.0)
_BANNER_COLOR = Vec4(1.0, 0.42, 0.3, 1.0)


class OswaldBetrayalChaseClient(DirectObject):
    """Client tip / banner timed with the post-betrayal Oswald chase spawn.

    AI schedules the DistributedCorruptToon spawn; this client mirrors the
    same delay from campaignVictory / reveal so the tip lands without a
    new distributed announce (messenger is process-local).
    """

    def __init__(self):
        DirectObject.__init__(self)
        self._tipNP = None
        self._bannerNP = None
        self._ival = None
        self._armed = False
        self._cueLatched = False
        # campaignVictory is local when available; oswaldRevealBanner is the
        # reliable finale client path from FinalePhaseFx.
        self.accept('campaignVictory', self._onVictory)
        self.accept('oswaldRevealBanner', self._onReveal)
        self.accept('oswaldBetrayalChase', self._onChaseSpawned)

    def destroy(self):
        self.ignoreAll()
        self._clear()

    def _onVictory(self, reclaimCount=0):
        if not chaseEnabled():
            return
        # Mirror AI spawn delay from victory so tip syncs with the chase.
        self._scheduleChaseCue(chaseDelaySec())

    def _onReveal(self, title=''):
        # Pre-arm melee when betrayal plate lands so F is ready for chase.
        self._armMelee()
        if not chaseEnabled():
            return
        # Reveal fires ~FINALE_REVEAL_DELAY_SEC after victory; remaining wait
        # until spawn keeps tip aligned if victory messenger was missed.
        revealDelay = float(getattr(
            CampaignGlobals, 'FINALE_REVEAL_DELAY_SEC', 2.45))
        remain = max(0.0, chaseDelaySec() - revealDelay)
        tipPad = max(0.0, float(getattr(
            CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_TIP_DELAY_SEC', 0.35)))
        self._scheduleChaseCue(remain + tipPad)

    def _onChaseSpawned(self, zoneId=0, doId=0):
        # Optional same-process hook (tests / AI-local clients).
        if not chaseEnabled():
            return
        self._armMelee()
        tipDelay = max(0.0, float(getattr(
            CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_TIP_DELAY_SEC', 0.35)))
        self._scheduleChaseCue(tipDelay, force=True)

    def _scheduleChaseCue(self, delaySec, force=False):
        if self._cueLatched and not force:
            return
        self._cueLatched = True
        self._armMelee()
        self._clearIntervals()
        delay = max(0.0, float(delaySec))

        def _show():
            self._showChaseCue()

        if delay <= 0.01:
            _show()
            return
        self._ival = Sequence(
            Wait(delay),
            Func(_show),
            name='oswaldBetrayalChaseTipDelay',
        )
        self._ival.start()

    def _armMelee(self):
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None or not hasattr(av, 'enableHackSlashMelee'):
            return
        try:
            av.enableHackSlashMelee(spawnHostiles=False)
            self._armed = True
        except Exception:
            pass

    def _showChaseCue(self):
        self._clearNodes()
        tip = chaseTip()
        banner = chaseBanner()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        tn = TextNode('oswald-chase-banner')
        tn.setText(banner)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(
            _BANNER_COLOR[0], _BANNER_COLOR[1], _BANNER_COLOR[2], 1)
        tn.setShadow(0.05, 0.05)
        tn.setShadowColor(0, 0, 0, 0.8)
        bannerNP = parent.attachNewNode(tn)
        bannerNP.setScale(0.078)
        bannerNP.setPos(0, 0, 0.28)
        bannerNP.setColorScale(1, 1, 1, 0)
        bannerNP.setBin('fixed', 62)
        bannerNP.setDepthTest(False)
        bannerNP.setDepthWrite(False)
        self._bannerNP = bannerNP

        stn = TextNode('oswald-chase-tip')
        stn.setText(tip)
        stn.setAlign(TextNode.ACenter)
        stn.setWordwrap(28)
        stn.setTextColor(_TIP_COLOR[0], _TIP_COLOR[1], _TIP_COLOR[2], 1)
        stn.setShadow(0.04, 0.04)
        stn.setShadowColor(0, 0, 0, 0.75)
        tipNP = parent.attachNewNode(stn)
        tipNP.setScale(0.045)
        tipNP.setPos(0, 0, 0.18)
        tipNP.setColorScale(1, 1, 1, 0)
        tipNP.setBin('fixed', 62)
        tipNP.setDepthTest(False)
        tipNP.setDepthWrite(False)
        self._tipNP = tipNP

        pop = Parallel(
            Sequence(
                LerpColorScaleInterval(bannerNP, 0.08, Vec4(1, 1, 1, 1)),
                LerpScaleInterval(
                    bannerNP, 0.12, 0.09, startScale=0.055,
                    blendType='easeOut'),
                LerpScaleInterval(
                    bannerNP, 0.1, 0.078, blendType='easeIn'),
            ),
            Sequence(
                Wait(0.06),
                LerpColorScaleInterval(tipNP, 0.1, Vec4(1, 1, 1, 1)),
            ),
        )
        self._ival = Sequence(
            pop,
            Wait(3.4),
            Parallel(
                LerpColorScaleInterval(bannerNP, 0.35, Vec4(1, 1, 1, 0)),
                LerpColorScaleInterval(tipNP, 0.35, Vec4(1, 1, 1, 0)),
            ),
            Func(self._clearNodes),
            name='oswaldBetrayalChaseCue',
        )
        self._ival.start()

    def _clearNodes(self):
        for attr in ('_tipNP', '_bannerNP'):
            np = getattr(self, attr, None)
            if np is not None:
                try:
                    np.removeNode()
                except Exception:
                    pass
            setattr(self, attr, None)

    def _clearIntervals(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None

    def _clear(self):
        self._clearIntervals()
        self._clearNodes()
        self._cueLatched = False


_client = None


def ensureOswaldBetrayalChaseClient():
    global _client
    if _client is None:
        _client = OswaldBetrayalChaseClient()
    return _client
