"""Air-local campaign director: multi-act reclaim progression."""

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
        self.unlockedThrough = 0  # highest act index the player may start
        self._activeZoneId = None
        self.accept('neighborhoodReclaimed', self.__onNeighborhoodReclaimed)

    def statusText(self):
        if self.state == CampaignGlobals.STATE_VICTORY:
            return (
                'Campaign VICTORY — Toon City purity restored! '
                'Reclaims: %s. ~startcampaign to replay.'
                % self.reclaimCount)
        act = CampaignGlobals.ACTS[min(
            self.actIndex, len(CampaignGlobals.ACTS) - 1)]
        unlocked = [
            CampaignGlobals.ACTS[i]['name']
            for i in range(self.unlockedThrough + 1)
        ]
        return (
            'Campaign %s | act %s/%s (%s zone %s) | reclaims %s | '
            'unlocked: %s | hub %s (%s)'
            % (
                CampaignGlobals.STATE_NAMES.get(self.state, '?'),
                self.actIndex + 1,
                len(CampaignGlobals.ACTS),
                act['name'],
                act['zoneId'],
                self.reclaimCount,
                ', '.join(unlocked),
                CampaignGlobals.HUB_NAME,
                CampaignGlobals.HUB_ZONE,
            ))

    def startCampaign(self, toon):
        """Begin or resume the current unlocked act in the invoker's zone."""
        if self.state == CampaignGlobals.STATE_VICTORY:
            self.actIndex = 0
            self.unlockedThrough = 0
            self.reclaimCount = 0

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
        self.state = CampaignGlobals.STATE_ACTIVE
        act = CampaignGlobals.ACTS[self.actIndex]
        return (
            'Advanced to act %s: %s (zone %s). Teleport there, then '
            '~startcampaign. %s'
            % (self.actIndex + 1, act['name'], act['zoneId'], act['banner']))

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

        director = DistributedReclaimDirectorAI(self.air, zoneId=zoneId)
        director.generateWithRequired(zoneId)
        directors[zoneId] = director
        self._activeZoneId = zoneId
        director.start(
            zoneId,
            (toon.getX(), toon.getY(), toon.getZ()),
            toon.getH(),
            seedPollution=act.get('seedPollution'),
            packSize=act.get('packSize'),
            maxPacks=act.get('maxPacks'),
            corruptHp=act.get('corruptHp'),
            corruptName=act.get('corruptName'))
        return (
            '%s Reclaim started in %s (zone %s, pollution %.2f, pack %s, hp %s). '
            'Enable melee with ~hackslash 0.'
            % (
                act['banner'],
                act['name'],
                zoneId,
                act.get('seedPollution', ReclaimGlobals.RECLAIM_START_POLLUTION),
                act.get('packSize', ReclaimGlobals.PACK_SIZE),
                act.get('corruptHp', '?'),
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

    def __onNeighborhoodReclaimed(self, zoneId):
        zoneId = int(zoneId)
        if self.state != CampaignGlobals.STATE_ACTIVE:
            return
        act = CampaignGlobals.ACTS[self.actIndex]
        if zoneId != int(act['zoneId']):
            return

        self.reclaimCount += 1
        self.notify.info(
            'campaign reclaimed act %s zone %s (count %s)'
            % (act['id'], zoneId, self.reclaimCount))

        if act.get('finale'):
            self.state = CampaignGlobals.STATE_VICTORY
            self._activeZoneId = None
            messenger.send('campaignVictory', [self.reclaimCount])
            return

        nextIndex = self.actIndex + 1
        if nextIndex < len(CampaignGlobals.ACTS):
            self.unlockedThrough = max(self.unlockedThrough, nextIndex)
            self.actIndex = nextIndex
            self._activeZoneId = None
            nxt = CampaignGlobals.ACTS[nextIndex]
            messenger.send('campaignActUnlocked', [nextIndex, nxt['zoneId']])
        else:
            self.state = CampaignGlobals.STATE_VICTORY
            self._activeZoneId = None
            messenger.send('campaignVictory', [self.reclaimCount])


def getCampaignDirector(air):
    director = getattr(air, 'campaignDirector', None)
    if director is None:
        director = CampaignDirectorAI(air)
        air.campaignDirector = director
    return director
