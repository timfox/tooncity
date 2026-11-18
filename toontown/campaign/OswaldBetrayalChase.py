"""Short corrupted-Oswald chase after finale betrayal.

Gameplay payload for the Oswald twist: CampaignDirectorAI schedules a
thin ARCHETYPE_CORRUPT_OSWALD spawn after Silly finale victory / reveal.
Oswald carries a distinct betrayal attack kit (lunge + stain burst +
shove) from CorruptionGlobals — not a crimson Smudge smack reskin.
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


def chaseAttackMove():
    """Primary betrayal kit move from ARCHETYPE_CORRUPT_OSWALD stats."""
    stats = CorruptionGlobals.archetypeStats(
        CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD)
    move = str(stats.get('attackMove', 'betrayal_lunge') or 'betrayal_lunge')
    if not getattr(CorruptionGlobals, 'OSWALD_BETRAYAL_KIT_ENABLED', True):
        return 'smack'
    return move


def chaseTip():
    return str(getattr(
        CampaignGlobals, 'OSWALD_BETRAYAL_CHASE_TIP',
        'Oswald turns on you — betrayal lunge inbound!  |  '
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


def chaseCombatDefeated(corrupt):
    """True only after intentional combat defeat (hp≤0 / ``_defeated``).

    Zone leave, DO despawn, or a missing doId must NOT count as clear —
    those leave ``chaseCleared=0`` so hydrate / resume can re-field the
    wash fight. ``corrupt is None`` is never a defeat.
    """
    if corrupt is None:
        return False
    if bool(getattr(corrupt, '_defeated', False)):
        return True
    try:
        hp = int(getattr(corrupt, 'hp', 0) or 0)
    except Exception:
        hp = 0
    return hp <= 0


def epilogueEnabled():
    return bool(getattr(CampaignGlobals, 'CAMPAIGN_EPILOGUE_ENABLED', True))


def epilogueTitle():
    return str(getattr(
        CampaignGlobals, 'CAMPAIGN_EPILOGUE_TITLE', 'STAIN WASHED'))


def epilogueSub():
    return str(getattr(
        CampaignGlobals, 'CAMPAIGN_EPILOGUE_SUB',
        "Oswald's smile is gone — purity holds for real this time."))


def epilogueCue():
    return str(getattr(
        CampaignGlobals, 'CAMPAIGN_EPILOGUE_CUE',
        'Replay from Toon Central hub — C on Loopy Lane to start over'))


def spawnCorruptOswald(air, toon, zoneId=None, forward=None):
    """Spawn one fightable Corrupted Oswald near `toon`. Returns AI or None.

    Archetype stats already carry the betrayal attack kit
    (``betrayal_lunge`` / ``stain_burst``); this hook only fields HP/name/
    pose so the chase fights like the twist, not a smack reskin.
    """
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
    # Pin kit identity at spawn so a future HP override cannot drop the move.
    _kitMove = chaseAttackMove()
    corrupt = DistributedCorruptToonAI(
        air, name=name, maxHp=hp, archetype=archetype, finalePhase=0)
    corrupt.hp = corrupt.maxHp
    if _kitMove and hasattr(corrupt, '_stats'):
        try:
            corrupt._stats = dict(corrupt._stats)
            corrupt._stats['attackMove'] = _kitMove
        except Exception:
            pass

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
    new distributed announce (messenger is process-local).     After clear,
    accepts ``oswaldBetrayalChaseCleared`` (same-process) and also watches
    for Corrupted Oswald combat defeat (hp≤0) so real clients still fire
    the campaign epilogue — zone leave / DO despawn must not soft-end.
    """

    def __init__(self):
        DirectObject.__init__(self)
        self._tipNP = None
        self._bannerNP = None
        self._ival = None
        self._armed = False
        self._cueLatched = False
        self._chaseDoId = None
        self._sawChase = False
        self._epilogueLatched = False
        self._watchTask = None
        # campaignVictory is local when available; oswaldRevealBanner is the
        # reliable finale client path from FinalePhaseFx.
        self.accept('campaignVictory', self._onVictory)
        self.accept('oswaldRevealBanner', self._onReveal)
        self.accept('oswaldBetrayalChase', self._onChaseSpawned)
        # AI-local clear + client-emitted clear after defeat watch.
        self.accept('oswaldBetrayalChaseCleared', self._onChaseCleared)

    def destroy(self):
        self.ignoreAll()
        self._stopChaseWatch()
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
        try:
            self._chaseDoId = int(doId) if doId else None
        except Exception:
            self._chaseDoId = None
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
            self._startChaseWatch()

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

    def _startChaseWatch(self):
        """Poll for Corrupted Oswald defeat so epilogue fires on real clients.

        AI ``messenger.send('oswaldBetrayalChaseCleared')`` is process-local;
        watching the live DistributedCorruptToon bridges that gap without a
        new DC field. Keeps betrayal kit spawn identity intact.
        """
        if not epilogueEnabled():
            return
        self._stopChaseWatch()
        period = max(0.2, float(getattr(
            CampaignGlobals, 'CAMPAIGN_EPILOGUE_WATCH_SEC', 0.45)))
        self._watchTask = 'oswald-betrayal-chase-clear-watch'
        try:
            taskMgr.doMethodLater(  # noqa: F821
                period, self._pollChaseClear, self._watchTask)
        except Exception:
            self._watchTask = None

    def _stopChaseWatch(self):
        name = self._watchTask
        self._watchTask = None
        if not name:
            return
        try:
            taskMgr.remove(name)  # noqa: F821
        except Exception:
            pass

    def _pollChaseClear(self, task):
        if self._epilogueLatched:
            self._watchTask = None
            return task.done
        # Prefer intentional combat defeat (hp≤0 / _defeated) even while the
        # DO is still in the map during DEFEAT_DELETE_DELAY.
        defeated = self._findCorruptOswald(includeDefeated=True)
        if defeated is not None and chaseCombatDefeated(defeated):
            try:
                self._chaseDoId = int(getattr(defeated, 'doId', 0) or 0) or (
                    self._chaseDoId)
            except Exception:
                pass
            doId = int(self._chaseDoId or 0)
            self._watchTask = None
            self._emitChaseCleared(doId)
            return task.done
        alive = self._findCorruptOswald(includeDefeated=False)
        if alive is not None:
            self._sawChase = True
            try:
                self._chaseDoId = int(getattr(alive, 'doId', 0) or 0) or (
                    self._chaseDoId)
            except Exception:
                pass
            return task.again
        # Absent without defeat evidence (zone leave / DO despawn) — keep
        # watching; do NOT false-clear / epilogue.
        return task.again

    def _findLiveCorruptOswald(self):
        """Fightable Corrupted Oswald only (hp>0). Kept for callers/tests."""
        return self._findCorruptOswald(includeDefeated=False)

    def _findCorruptOswald(self, includeDefeated=False):
        cr = getattr(base, 'cr', None)  # noqa: F821
        if cr is None:
            return None
        doMap = getattr(cr, 'doId2do', None) or {}
        wantId = CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD
        wantName = chaseName().lower()
        # Prefer tracked doId when AI same-process spawn announced it.
        if self._chaseDoId:
            obj = doMap.get(int(self._chaseDoId))
            if obj is not None and self._isChaseCorruptOswald(
                    obj, wantId, wantName, includeDefeated=includeDefeated):
                return obj
        for obj in list(doMap.values()):
            if self._isChaseCorruptOswald(
                    obj, wantId, wantName, includeDefeated=includeDefeated):
                return obj
        return None

    def _isLiveCorruptOswald(self, obj, wantId, wantName):
        return self._isChaseCorruptOswald(
            obj, wantId, wantName, includeDefeated=False)

    def _isChaseCorruptOswald(self, obj, wantId, wantName, includeDefeated=False):
        if obj is None:
            return False
        try:
            if getattr(obj, 'isDeleted', lambda: False)():
                return False
        except Exception:
            pass
        if not includeDefeated and chaseCombatDefeated(obj):
            return False
        try:
            archetype = int(getattr(obj, 'archetype', -1))
            if hasattr(obj, 'getArchetype'):
                archetype = int(obj.getArchetype())
        except Exception:
            archetype = -1
        if archetype == int(wantId):
            return True
        name = str(getattr(obj, 'name', '') or '').lower()
        return bool(wantName) and wantName in name

    def _onChaseCleared(self, doId=0):
        """Accept AI / peer clear — fire epilogue once (no clear rebroadcast)."""
        self._fireEpilogue(doId, rebroadcastClear=False)

    def _emitChaseCleared(self, doId=0):
        """Watch-origin clear — broadcast so Handoff/PlayEntry hear it."""
        self._fireEpilogue(doId, rebroadcastClear=True)

    def _fireEpilogue(self, doId=0, rebroadcastClear=False):
        if self._epilogueLatched:
            return
        if not epilogueEnabled():
            return
        self._epilogueLatched = True
        self._stopChaseWatch()
        self._clearNodes()
        try:
            doId = int(doId or self._chaseDoId or 0)
        except Exception:
            doId = 0
        # Real clients never see AI messenger.send — watch path rebroadcasts
        # the clear token; both paths emit campaignEpilogue for PlayEntry.
        if rebroadcastClear:
            try:
                messenger.send(  # noqa: F821
                    'oswaldBetrayalChaseCleared', [doId])
            except Exception:
                pass
        try:
            messenger.send('campaignEpilogue', [doId])  # noqa: F821
        except Exception:
            pass

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
        self._chaseDoId = None
        self._sawChase = False
        # Keep _epilogueLatched so a destroy/recreate mid-session does not
        # double-fire; ensureOswaldBetrayalChaseClient is process-singleton.


_client = None


def ensureOswaldBetrayalChaseClient():
    global _client
    if _client is None:
        _client = OswaldBetrayalChaseClient()
    return _client
