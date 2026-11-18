"""Neighborhood cheer when a street is purified — or a reclaim wave clears.

Listens for reclaim purity / wave-clear messengers and plays a local Happy/wave
beat plus a short rubber-hose cheer SFX with a pitch swell so the fantasy pays
off beyond the aspect2d burst.
"""

from panda3d.core import Point3

from direct.interval.IntervalGlobal import (
    Func,
    LerpFunc,
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
        self._pitchIval = None
        self._sfx = None
        self._lastCheerT = -1.0
        # Purity restore: director may fire both stub + purityRestoreFx.
        self.accept('npcCheerStub', self._onPurityCheer)
        self.accept('purityRestoreFx', self._onPurityCheer)
        self.accept('reclaimWaveCleared', self._onWaveCleared)

    def destroy(self):
        self.ignoreAll()
        self._stopPitch()
        if self._cheerIval:
            try:
                self._cheerIval.finish()
            except Exception:
                pass
            self._cheerIval = None

    def _onPurityCheer(self, zoneId=None):
        if self._debounce():
            return
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None:
            return
        self._playPitchSwell(
            volume=getattr(ReclaimGlobals, 'CHEER_PITCH_VOLUME', 0.88))
        self._bounceLocal(av, full=True)
        self._nudgeNearby(av)

    def _onWaveCleared(self, zoneId=None, waveIndex=0):
        if self._debounce(minGap=0.2):
            return
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None:
            return
        self._playPitchSwell(
            volume=getattr(ReclaimGlobals, 'CHEER_PITCH_VOLUME_WAVE', 0.7))
        # Light HUD-adjacent bounce: soft squash only (purity keeps the big beat).
        self._bounceLocal(av, full=False)

    def _debounce(self, minGap=0.35):
        """Collapse duplicate purity messengers into one cheer beat."""
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            return False
        if now - self._lastCheerT < float(minGap):
            return True
        self._lastCheerT = now
        return False

    def _stopPitch(self):
        if self._pitchIval:
            try:
                self._pitchIval.finish()
            except Exception:
                pass
            self._pitchIval = None

    def _ensureSfx(self):
        if self._sfx is not None:
            return self._sfx
        try:
            path = getattr(
                ReclaimGlobals, 'PURITY_CHEER_SFX',
                'phase_3.5/audio/sfx/AV_jump_2.ogg')
            self._sfx = base.loader.loadSfx(path)  # noqa: F821
        except Exception:
            self._sfx = None
        return self._sfx

    def _playPitchSwell(self, volume=0.88):
        """Short cartoon pitch ramp: low → bright peak → soft settle."""
        sfx = self._ensureSfx()
        if sfx is None:
            return
        self._stopPitch()
        start = float(getattr(ReclaimGlobals, 'CHEER_PITCH_START', 0.78))
        peak = float(getattr(ReclaimGlobals, 'CHEER_PITCH_PEAK', 1.42))
        end = float(getattr(ReclaimGlobals, 'CHEER_PITCH_END', 1.06))
        swellSec = float(getattr(ReclaimGlobals, 'CHEER_PITCH_SWELL_SEC', 0.16))
        settleSec = float(getattr(ReclaimGlobals, 'CHEER_PITCH_SETTLE_SEC', 0.14))

        def setRate(r):
            try:
                sfx.setPlayRate(float(r))
            except Exception:
                pass

        def startSfx():
            try:
                sfx.setPlayRate(start)
            except Exception:
                pass
            try:
                sfx.setVolume(float(volume))
            except Exception:
                pass
            try:
                base.playSfx(sfx)  # noqa: F821
            except Exception:
                pass

        self._pitchIval = Sequence(
            Func(startSfx),
            LerpFunc(
                setRate,
                fromData=start,
                toData=peak,
                duration=max(0.01, swellSec)),
            LerpFunc(
                setRate,
                fromData=peak,
                toData=end,
                duration=max(0.01, settleSec)),
            name='reclaimCheerPitchSwell',
        )
        self._pitchIval.start()

    def _bounceLocal(self, av, full=True):
        if self._cheerIval:
            try:
                self._cheerIval.finish()
            except Exception:
                pass
        try:
            av.setAnimState('Happy', 1.15 if full else 1.05)
        except Exception:
            pass
        try:
            startH = av.getH()
            if full:
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
            else:
                peak = float(getattr(
                    ReclaimGlobals, 'WAVE_CLEAR_BOUNCE_PEAK', 1.08))
                sec = float(getattr(
                    ReclaimGlobals, 'WAVE_CLEAR_BOUNCE_SEC', 0.1))
                self._cheerIval = Sequence(
                    LerpScaleInterval(av, sec, Point3(peak, peak, 0.92)),
                    LerpScaleInterval(av, sec * 1.15, Point3(1, 1, 1)),
                )
            self._cheerIval.start()
        except Exception:
            if full:
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
