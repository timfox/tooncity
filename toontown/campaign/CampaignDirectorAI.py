"""Air-local campaign director: multi-act reclaim progression + finale phases."""

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from toontown.campaign import CampaignGlobals
from toontown.campaign.OswaldBetrayalChase import (
    chaseClearMsg,
    chaseDelaySec,
    chaseEnabled,
    chaseSpawnMsg,
    spawnCorruptOswald,
)
from toontown.reclaim import ReclaimGlobals
from toontown.reclaim.DistributedReclaimDirectorAI import DistributedReclaimDirectorAI


class CampaignDirectorAI(DirectObject):
    """Tracks act unlocks and starts reclaim directors per act zone."""

    notify = DirectNotifyGlobal.directNotify.newCategory('CampaignDirectorAI')

    def __init__(self, air):
        DirectObject.__init__(self)
        self.air = air
        self.state = CampaignGlobals.STATE_IDLE
        self.actIndex = 0
        self.reclaimCount = 0
        self.unlockedThrough = 0
        self._activeZoneId = None
        self._finalePhase = 0
        self._lastToonId = None
        self._oswaldChaseDoId = None
        self._oswaldChaseTask = None
        self._oswaldChaseWatch = None
        self.accept('neighborhoodReclaimed', self.__onNeighborhoodReclaimed)

    def statusText(self):
        if self.state == CampaignGlobals.STATE_VICTORY:
            chaseNote = ''
            if chaseEnabled():
                chaseNote = ' Corrupted-Oswald chase after betrayal.'
            return (
                'Campaign VICTORY — purity restored, but Oswald caused '
                'the corruption!%s Reclaims: %s. Replay from %s / C on Loopy.'
                % (chaseNote, self.reclaimCount, CampaignGlobals.HUB_NAME))
        act = CampaignGlobals.ACTS[min(
            self.actIndex, len(CampaignGlobals.ACTS) - 1)]
        unlocked = [
            CampaignGlobals.ACTS[i]['name']
            for i in range(self.unlockedThrough + 1)
        ]
        phaseNote = ''
        if act.get('finale'):
            phaseNote = ' | finale phase %s/2' % (self._finalePhase + 1)
        return (
            'Campaign %s | act %s/%s (%s)%s | reclaims %s | '
            'unlocked: %s | hub %s'
            % (
                CampaignGlobals.STATE_NAMES.get(self.state, '?'),
                self.actIndex + 1,
                len(CampaignGlobals.ACTS),
                act['name'],
                phaseNote,
                self.reclaimCount,
                ', '.join(unlocked),
                CampaignGlobals.HUB_NAME,
            ))

    def startCampaign(self, toon):
        """Begin or resume the current unlocked act in the invoker's zone."""
        self._lastToonId = getattr(toon, 'doId', None)
        if self.state == CampaignGlobals.STATE_VICTORY:
            self.actIndex = 0
            self.unlockedThrough = 0
            self.reclaimCount = 0
            self._finalePhase = 0
            self._cancelOswaldBetrayalChase()

        self.state = CampaignGlobals.STATE_ACTIVE
        act = CampaignGlobals.ACTS[self.actIndex]
        zoneId = int(toon.zoneId)
        if zoneId != int(act['zoneId']):
            face = getattr(
                CampaignGlobals, 'RECLAIM_FACE',
                getattr(CampaignGlobals, 'PROTAGONIST', 'Oswald'))
            return (
                '%s needs you on %s — head there and the reclaim packs '
                'will field.' % (face, act['name']))
        return self._startActReclaim(toon, act)

    def advanceCampaign(self, toon, force=False):
        """Unlock / jump to the next act (moderator force for demos)."""
        self._lastToonId = getattr(toon, 'doId', None)
        if self.state == CampaignGlobals.STATE_VICTORY:
            return (
                'Campaign already complete. Head to %s / press C on Loopy '
                'to replay.' % CampaignGlobals.HUB_NAME)

        nextIndex = self.actIndex + 1
        if nextIndex >= len(CampaignGlobals.ACTS):
            self.state = CampaignGlobals.STATE_VICTORY
            return 'No further acts — campaign victory! ' + self.statusText()

        if not force and nextIndex > self.unlockedThrough:
            return (
                'Act %s is locked. Reclaim the current street first '
                '(or ~advancecampaign force).'
                % (nextIndex + 1))

        self._stopActiveReclaim()
        self.actIndex = nextIndex
        self.unlockedThrough = max(self.unlockedThrough, nextIndex)
        self._finalePhase = 0
        self.state = CampaignGlobals.STATE_ACTIVE
        act = CampaignGlobals.ACTS[self.actIndex]
        hint = CampaignGlobals.handoffTravelHint(act)
        self._tellToon(toon, 'NEXT HOOD: %s. %s' % (act['name'], act['banner']))
        return (
            'Advanced to act %s: %s. %s %s'
            % (self.actIndex + 1, act['name'], hint, act['banner']))

    def _actParams(self, act):
        """Resolve start() kwargs, including finale phase 2 overrides."""
        params = {
            'seedPollution': act.get('seedPollution'),
            'packSize': act.get('packSize'),
            'maxPacks': act.get('maxPacks'),
            'corruptHp': act.get('corruptHp'),
            'corruptName': act.get('corruptName'),
            'bruteFraction': act.get('bruteFraction'),
            'bruteWaveStart': act.get('bruteWaveStart'),
            'bruteName': act.get('bruteName'),
            'snareFraction': act.get('snareFraction'),
            'snareWaveStart': act.get('snareWaveStart'),
            'snareName': act.get('snareName'),
            'gagsterFraction': act.get('gagsterFraction'),
            'gagsterWaveStart': act.get('gagsterWaveStart'),
            'gagsterName': act.get('gagsterName'),
            'waveScripts': act.get('waveScripts'),
            'banner': act.get('banner'),
            'finalePhase': 0,
            'transitionSting': False,
            'addCount': None,
            'addWaveStart': None,
            'addHp': None,
            'addName': None,
        }
        if act.get('finale'):
            if self._finalePhase >= 1:
                phase2 = act.get('phase2') or {}
                params.update(phase2)
                params['finalePhase'] = int(phase2.get('finalePhase', 2))
                params['transitionSting'] = bool(
                    phase2.get('transitionSting', True))
            else:
                params['finalePhase'] = int(act.get('finalePhase', 1))
        return params

    def _startActReclaim(self, toon, act):
        directors = getattr(self.air, 'reclaimDirectors', None)
        if directors is None:
            directors = {}
            self.air.reclaimDirectors = directors

        zoneId = int(act['zoneId'])
        existing = directors.get(zoneId)
        if existing is not None and not existing.isDeleted():
            if existing.state == ReclaimGlobals.STATE_ACTIVE:
                self._activeZoneId = zoneId
                return 'Reclaim already active for %s (zone %s).' % (
                    act['name'], zoneId)
            existing.requestDelete()
            directors.pop(zoneId, None)

        params = self._actParams(act)
        director = DistributedReclaimDirectorAI(self.air, zoneId=zoneId)
        director.generateWithRequired(zoneId)
        directors[zoneId] = director
        self._activeZoneId = zoneId
        director.start(
            zoneId,
            (toon.getX(), toon.getY(), toon.getZ()),
            toon.getH(),
            seedPollution=params.get('seedPollution'),
            packSize=params.get('packSize'),
            maxPacks=params.get('maxPacks'),
            corruptHp=params.get('corruptHp'),
            corruptName=params.get('corruptName'),
            bruteFraction=params.get('bruteFraction'),
            bruteWaveStart=params.get('bruteWaveStart'),
            bruteName=params.get('bruteName'),
            snareFraction=params.get('snareFraction'),
            snareWaveStart=params.get('snareWaveStart'),
            snareName=params.get('snareName'),
            gagsterFraction=params.get('gagsterFraction'),
            gagsterWaveStart=params.get('gagsterWaveStart'),
            gagsterName=params.get('gagsterName'),
            waveScripts=params.get('waveScripts'),
            finalePhase=params.get('finalePhase', 0),
            transitionSting=params.get('transitionSting', False),
            addCount=params.get('addCount'),
            addWaveStart=params.get('addWaveStart'),
            addHp=params.get('addHp'),
            addName=params.get('addName'))
        banner = params.get('banner') or act.get('banner')
        self._tellToon(toon, banner)
        # Player-facing attach copy — melee is auto-armed by PlayEntry.
        return (
            '%s Packs inbound on %s — press F to fight, Shift to dodge!'
            % (banner, act['name']))

    def _stopActiveReclaim(self):
        if self._activeZoneId is None:
            return
        directors = getattr(self.air, 'reclaimDirectors', None) or {}
        director = directors.get(self._activeZoneId)
        if director is not None and not director.isDeleted():
            director.stop()
            director.requestDelete()
            directors.pop(self._activeZoneId, None)
        self._activeZoneId = None

    def _tellToon(self, toon, message):
        if toon is None or not message:
            return
        try:
            if hasattr(toon, 'd_setSystemMessage'):
                toon.d_setSystemMessage(0, str(message)[:200])
            elif hasattr(toon, 'setSystemMessage'):
                toon.setSystemMessage(0, str(message)[:200])
        except Exception:
            pass

    def _toonFromLast(self):
        if self._lastToonId is None:
            return None
        return self.air.doId2do.get(self._lastToonId)

    def _cancelOswaldBetrayalChase(self):
        if self._oswaldChaseTask is not None:
            try:
                taskMgr.remove(self._oswaldChaseTask)  # noqa: F821
            except Exception:
                pass
            self._oswaldChaseTask = None
        if self._oswaldChaseWatch is not None:
            try:
                taskMgr.remove(self._oswaldChaseWatch)  # noqa: F821
            except Exception:
                pass
            self._oswaldChaseWatch = None
        doId = self._oswaldChaseDoId
        self._oswaldChaseDoId = None
        if doId is None:
            return
        corrupt = self.air.doId2do.get(doId)
        if corrupt is None:
            return
        try:
            if not corrupt.isDeleted():
                corrupt.requestDelete()
        except Exception:
            pass

    def _scheduleOswaldBetrayalChase(self, toon, zoneId):
        """After finale betrayal, field a short fightable Oswald chase."""
        self._cancelOswaldBetrayalChase()
        if not chaseEnabled():
            return
        if toon is None:
            toon = self._toonFromLast()
        if toon is None:
            return
        delay = chaseDelaySec()
        self._oswaldChaseTask = 'campaign-oswald-betrayal-chase'
        taskMgr.doMethodLater(  # noqa: F821
            delay,
            self.__spawnOswaldBetrayalChase,
            self._oswaldChaseTask,
            extraArgs=[int(getattr(toon, 'doId', 0) or 0), int(zoneId)],
            appendTask=True)

    def __spawnOswaldBetrayalChase(self, toonId, zoneId, task):
        self._oswaldChaseTask = None
        if not chaseEnabled():
            return Task.done
        toon = self.air.doId2do.get(int(toonId)) if toonId else None
        if toon is None:
            toon = self._toonFromLast()
        if toon is None:
            return Task.done
        # Prefer the toon's live zone so a hub hop still fields nearby.
        liveZone = int(getattr(toon, 'zoneId', 0) or 0) or int(zoneId)
        corrupt = spawnCorruptOswald(self.air, toon, zoneId=liveZone)
        if corrupt is None:
            return Task.done
        self._oswaldChaseDoId = getattr(corrupt, 'doId', None)
        self._tellToon(toon, chaseSpawnMsg())
        try:
            messenger.send(  # noqa: F821
                'oswaldBetrayalChase',
                [liveZone, int(self._oswaldChaseDoId or 0)])
        except Exception:
            pass
        # Watch for defeat so we can land a short clear beat.
        self._oswaldChaseWatch = 'campaign-oswald-betrayal-chase-watch'
        taskMgr.doMethodLater(  # noqa: F821
            0.5,
            self.__watchOswaldBetrayalChase,
            self._oswaldChaseWatch,
            extraArgs=[int(self._oswaldChaseDoId or 0),
                       int(getattr(toon, 'doId', 0) or 0)],
            appendTask=True)
        self.notify.info(
            'oswald betrayal chase spawned doId=%s zone=%s'
            % (self._oswaldChaseDoId, liveZone))
        return Task.done

    def __watchOswaldBetrayalChase(self, doId, toonId, task):
        if doId <= 0:
            self._oswaldChaseWatch = None
            self._oswaldChaseDoId = None
            return Task.done
        corrupt = self.air.doId2do.get(int(doId))
        alive = (
            corrupt is not None
            and not getattr(corrupt, 'isDeleted', lambda: True)()
            and not getattr(corrupt, '_defeated', False)
            and int(getattr(corrupt, 'hp', 0) or 0) > 0)
        if alive:
            return Task.again
        self._oswaldChaseWatch = None
        self._oswaldChaseDoId = None
        toon = self.air.doId2do.get(int(toonId)) if toonId else None
        if toon is None:
            toon = self._toonFromLast()
        self._tellToon(toon, chaseClearMsg())
        try:
            messenger.send('oswaldBetrayalChaseCleared', [int(doId)])  # noqa: F821
        except Exception:
            pass
        return Task.done

    def __onNeighborhoodReclaimed(self, zoneId):
        zoneId = int(zoneId)
        if self.state != CampaignGlobals.STATE_ACTIVE:
            return
        act = CampaignGlobals.ACTS[self.actIndex]
        if zoneId != int(act['zoneId']):
            return

        self.reclaimCount += 1
        toon = self._toonFromLast()
        self.notify.info(
            'campaign reclaimed act %s zone %s (count %s phase %s)'
            % (act['id'], zoneId, self.reclaimCount, self._finalePhase))

        # Finale phase 1 → restart tougher phase 2 before victory.
        if act.get('finale') and self._finalePhase < 1:
            self._finalePhase = 1
            self._activeZoneId = None
            phase2 = act.get('phase2') or {}
            msg = phase2.get('banner') or 'Finale Phase 2!'
            self._tellToon(toon, msg)
            if toon is not None and int(toon.zoneId) == zoneId:
                self._startActReclaim(toon, act)
            return

        handoff = act.get('handoff') or ('%s reclaimed!' % act['name'])
        if act.get('finale'):
            self.state = CampaignGlobals.STATE_VICTORY
            self._activeZoneId = None
            self._finalePhase = 0
            self._tellToon(toon, handoff)
            messenger.send('campaignVictory', [self.reclaimCount])  # noqa: F821
            # Gameplay payload: short corrupted-Oswald chase after betrayal.
            self._scheduleOswaldBetrayalChase(toon, zoneId)
            return

        nextIndex = self.actIndex + 1
        if nextIndex < len(CampaignGlobals.ACTS):
            self.unlockedThrough = max(self.unlockedThrough, nextIndex)
            self.actIndex = nextIndex
            self._finalePhase = 0
            self._activeZoneId = None
            nxt = CampaignGlobals.ACTS[nextIndex]
            # Discoverable handoff — street name only, no zone ids / magic words.
            hint = CampaignGlobals.handoffTravelHint(nxt)
            self._tellToon(toon, '%s %s' % (handoff, hint))
            messenger.send(  # noqa: F821
                'campaignActUnlocked', [nextIndex, nxt['zoneId']])
        else:
            self.state = CampaignGlobals.STATE_VICTORY
            self._activeZoneId = None
            self._tellToon(toon, handoff)
            messenger.send('campaignVictory', [self.reclaimCount])  # noqa: F821


def getCampaignDirector(air):
    director = getattr(air, 'campaignDirector', None)
    if director is None:
        director = CampaignDirectorAI(air)
        air.campaignDirector = director
    return director
