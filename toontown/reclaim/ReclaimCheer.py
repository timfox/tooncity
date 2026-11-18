"""Neighborhood cheer when a street is purified.

Listens for reclaim purity messengers and plays a local Happy/wave beat plus
a short celebration SFX so the fantasy pays off beyond the aspect2d burst.
"""

from panda3d.core import Point3, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpHprInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.reclaim import ReclaimGlobals


class ReclaimCheerClient(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self._cheerIval = None
        self._sfx = None
        self.accept('npcCheerStub', self._onCheer)
        self.accept('purityRestoreFx', self._onCheer)

    def destroy(self):
        self.ignoreAll()
        if self._cheerIval:
            try:
                self._cheerIval.finish()
            except Exception:
                pass
            self._cheerIval = None

    def _onCheer(self, zoneId=None):
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None:
            return
        self._playSfx()
        self._bounceLocal(av)
        self._nudgeNearby(av)

    def _playSfx(self):
        try:
            path = getattr(
                ReclaimGlobals, 'PURITY_CHEER_SFX',
                'phase_3.5/audio/sfx/AV_jump_2.ogg')
            if self._sfx is None:
                self._sfx = base.loader.loadSfx(path)  # noqa: F821
            if self._sfx is not None:
                try:
                    self._sfx.setVolume(0.9)
                except Exception:
                    pass
                base.playSfx(self._sfx)  # noqa: F821
        except Exception:
            pass

    def _bounceLocal(self, av):
        if self._cheerIval:
            try:
                self._cheerIval.finish()
            except Exception:
                pass
        try:
            av.setAnimState('Happy', 1.15)
        except Exception:
            pass
        try:
            startH = av.getH()
            self._cheerIval = Sequence(
                Parallel(
                    LerpScaleInterval(av, 0.12, Point3(1.15, 1.15, 0.85)),
                    LerpHprInterval(av, 0.12, Point3(startH + 12, 0, 0)),
                ),
                Parallel(
                    LerpScaleInterval(av, 0.16, Point3(0.9, 0.9, 1.2)),
                    LerpHprInterval(av, 0.16, Point3(startH - 10, 0, 0)),
                ),
                Parallel(
                    LerpScaleInterval(av, 0.18, Point3(1, 1, 1)),
                    LerpHprInterval(av, 0.18, Point3(startH, 0, 0)),
                ),
                Wait(0.05),
                Func(self._tryWave, av),
            )
            self._cheerIval.start()
        except Exception:
            self._tryWave(av)

    def _tryWave(self, av):
        try:
            from otp.avatar import Emote
            # Wave / applause-ish if available; Happy already set above.
            if hasattr(Emote, 'globalEmote') and Emote.globalEmote:
                Emote.globalEmote.doEmote(av, 1)  # Wave index commonly 1
        except Exception:
            try:
                av.setAnimState('Wave', 1.0)
            except Exception:
                pass

    def _nudgeNearby(self, localAv):
        """Tiny squash on other toons in-zone so the street feels populated."""
        cr = getattr(base, 'cr', None)  # noqa: F821
        if cr is None:
            return
        zoneId = getattr(localAv, 'zoneId', None)
        for do in list(getattr(cr, 'doId2do', {}).values()):
            if do is localAv:
                continue
            if getattr(do, 'zoneId', None) != zoneId:
                continue
            if not hasattr(do, 'setAnimState'):
                continue
            try:
                do.setAnimState('Happy', 1.0)
                Sequence(
                    LerpScaleInterval(do, 0.1, Point3(1.1, 1.1, 0.9)),
                    LerpScaleInterval(do, 0.15, Point3(1, 1, 1)),
                ).start()
            except Exception:
                pass


_client = None


def ensureReclaimCheerClient():
    global _client
    if _client is None:
        _client = ReclaimCheerClient()
    return _client
