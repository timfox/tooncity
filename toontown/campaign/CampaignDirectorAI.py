"""Air-local campaign director: multi-act reclaim progression + finale phases."""

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
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
        self.accept('neighborhoodReclaimed', self.__onNeighborhoodReclaimed)

    def statusText(self):
        if self.state == CampaignGlobals.STATE_VICTORY:
            return (
                'Campaign VICTORY — purity restored, but Oswald caused '
                'the corruption! Reclaims: %s. ~startcampaign to replay.'
                % self.reclaimCount)
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
            'Campaign %s | act %s/%s (%s zone %s)%s | reclaims %s | '
            'unlocked: %s | hub %s (%s)'
            % (
                CampaignGlobals.STATE_NAMES.get(self.state, '?'),
                self.actIndex + 1,
                len(CampaignGlobals.ACTS),
                act['name'],
                act['zoneId'],
                phaseNote,
                self.reclaimCount,
                ', '.join(unlocked),
                CampaignGlobals.HUB_NAME,
                CampaignGlobals.HUB_ZONE,
            ))

    def startCampaign(self, toon):
        """Begin or resume the current unlocked act in the invoker's zone."""
        self._lastToonId = getattr(toon, 'doId', None)
        if self.state == CampaignGlobals.STATE_VICTORY:
            self.actIndex = 0
            self.unlockedThrough = 0
            self.reclaimCount = 0
            self._finalePhase = 0

        self.state = CampaignGlobals.STATE_ACTIVE
        act = CampaignGlobals.ACTS[self.actIndex]
        zoneId = int(toon.zoneId)
        if zoneId != int(act['zoneId']):
            return (
                '%s Go to %s (zone %s), then ~startcampaign again. '
                'Hub HQ: %s (%s).'
                % (
                    act['banner'],
                    act['name'],
                    act['zoneId'],
                    CampaignGlobals.HUB_NAME,
                    CampaignGlobals.HUB_ZONE,
                ))
        return self._startActReclaim(toon, act)

    def advanceCampaign(self, toon, force=False):
        """Unlock / jump to the next act (moderator force for demos)."""
        self._lastToonId = getattr(toon, 'doId', None)
        if self.state == CampaignGlobals.STATE_VICTORY:
            return 'Campaign already complete. ~startcampaign to replay.'

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
        self._tellToon(
            toon,
            'NEXT HOOD: %s (zone %s). %s'
            % (act['name'], act['zoneId'], act['banner']))
        return (
            'Advanced to act %s: %s (zone %s). Teleport there, then '
            '~startcampaign. %s'
            % (self.actIndex + 1, act['name'], act['zoneId'], act['banner']))

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
            'banner': act.get('banner'),
            'finalePhase': 0,
            'transitionSting': False,
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
            finalePhase=params.get('finalePhase', 0),
            transitionSting=params.get('transitionSting', False))
        banner = params.get('banner') or act.get('banner')
        self._tellToon(toon, banner)
        phaseTag = ''
        if params.get('finalePhase'):
            phaseTag = ' finalePhase=%s' % params.get('finalePhase')
        return (
            '%s Reclaim started in %s (zone %s, pollution %.2f, pack %s, hp %s)%s. '
            'Enable melee with ~hackslash 0.'
            % (
                banner,
                act['name'],
                zoneId,
                params.get('seedPollution', ReclaimGlobals.RECLAIM_START_POLLUTION),
                params.get('packSize', ReclaimGlobals.PACK_SIZE),
                params.get('corruptHp', '?'),
                phaseTag,
            ))

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
            return

        nextIndex = self.actIndex + 1
        if nextIndex < len(CampaignGlobals.ACTS):
            self.unlockedThrough = max(self.unlockedThrough, nextIndex)
            self.actIndex = nextIndex
            self._finalePhase = 0
            self._activeZoneId = None
            nxt = CampaignGlobals.ACTS[nextIndex]
            self._tellToon(
                toon,
                '%s Teleport to zone %s and ~startcampaign.'
                % (handoff, nxt['zoneId']))
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
