"""Client street music beds driven by PollutionManager / reclaim purity.

When a street is polluted, fade the bright neighborhood bed to a darker
encounter bed (existing phase_3.5 BGM — no new binary assets). On reclaim /
purity clear, fade back to the hood music so it pairs with cheer/sting #21.

Uses a sequential fade-out / fade-in switch (musicManager is typically
single-channel) rather than overlapping both tracks.
"""

from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import Func, LerpFunctionInterval, Sequence
from panda3d.core import AudioSound

from toontown.corruption import CorruptionGlobals


class PollutionStreetAudio:
    """Listens for pollution + purity messengers and swaps street music beds."""

    notify = DirectNotifyGlobal.directNotify.newCategory('PollutionStreetAudio')

    def __init__(self):
        self._active = False
        self._pollutedMode = False
        self._pollutedMusic = None
        self._fadeIval = None
        self._zoneId = None
        self._suspendedForBattle = False

    def start(self):
        if self._active:
            return
        self._active = True
        messenger.accept(
            'pollutionChanged', self, self.__onPollutionChanged, [], 1)
        messenger.accept(
            'purityRestoreFx', self, self.__onPurityRestore, [], 1)
        messenger.accept(
            'localToonLeftZone', self, self.__onLeftZone, [], 1)
        # Classic cog battles steal music; re-apply bed when walk resumes.
        messenger.accept(
            'enterBattle', self, self.__onEnterBattle, [], 1)
        taskMgr.add(self.__pollWalkResume, 'pollution-street-audio-walk')

    def stop(self):
        if not self._active:
            return
        self._active = False
        messenger.ignore('pollutionChanged', self)
        messenger.ignore('purityRestoreFx', self)
        messenger.ignore('localToonLeftZone', self)
        messenger.ignore('enterBattle', self)
        taskMgr.remove('pollution-street-audio-walk')
        self._finishFade()
        self._stopPollutedMusic()
        self._pollutedMode = False
        self._suspendedForBattle = False
        self._zoneId = None

    def _finishFade(self):
        if self._fadeIval is not None:
            try:
                self._fadeIval.finish()
            except Exception:
                pass
            self._fadeIval = None

    def _streetMusic(self):
        """Resolve current place.loader.music (bright neighborhood bed)."""
        try:
            place = base.cr.playGame.getPlace()
        except Exception:
            return None
        if place is None:
            return None
        loader = getattr(place, 'loader', None)
        if loader is None:
            return None
        return getattr(loader, 'music', None)

    def _ensurePollutedMusic(self):
        if self._pollutedMusic is not None:
            return self._pollutedMusic
        path = CorruptionGlobals.POLLUTED_STREET_MUSIC
        try:
            self._pollutedMusic = base.loader.loadMusic(path)
        except Exception:
            self.notify.debug('polluted street music unavailable: %s' % path)
            self._pollutedMusic = None
        return self._pollutedMusic

    def _stopPollutedMusic(self):
        music = self._pollutedMusic
        if music is None:
            return
        try:
            music.stop()
        except Exception:
            pass

    def _musicPlaying(self, music):
        if music is None:
            return False
        try:
            return music.status() == AudioSound.PLAYING
        except Exception:
            return False

    def _inClassicBattle(self):
        """True while place FSM is in a turn-based cog battle."""
        try:
            place = base.cr.playGame.getPlace()
        except Exception:
            return False
        if place is None or not hasattr(place, 'fsm'):
            return False
        try:
            state = place.fsm.getCurrentState()
            name = state.getName() if state else ''
        except Exception:
            return False
        return name in ('battle', 'WaitForBattle')

    def __onEnterBattle(self, *args):
        # Cog battles own music; park polluted bed until walk returns.
        self._suspendedForBattle = True
        self._finishFade()
        self._stopPollutedMusic()

    def __pollWalkResume(self, task):
        if not self._active:
            return task.done
        if self._suspendedForBattle and not self._inClassicBattle():
            self._suspendedForBattle = False
            if self._pollutedMode and self._zoneId is not None:
                # Street.exitBattle already restarted bright music — swap back.
                self._fadeSwitchToPolluted(
                    CorruptionGlobals.POLLUTION_AUDIO_CROSSFADE_SEC)
        return task.cont

    def __onPollutionChanged(self, zoneId, level):
        if hasattr(base, 'localAvatar'):
            localZone = getattr(base.localAvatar, 'zoneId', None)
            if localZone is not None and int(localZone) != int(zoneId):
                return
        self._zoneId = zoneId
        level = CorruptionGlobals.clampPollution(level)
        wantPolluted = level > CorruptionGlobals.POLLUTION_AUDIO_THRESHOLD
        if wantPolluted:
            self._enterPolluted()
        else:
            self._enterPure(restoreCrossfade=False)

    def __onPurityRestore(self, zoneId):
        # Pair with ReclaimCheer / purity sting (#21): snappier bright return.
        self._zoneId = zoneId
        self._enterPure(restoreCrossfade=True)

    def __onLeftZone(self, *args):
        self._finishFade()
        self._stopPollutedMusic()
        self._pollutedMode = False
        self._suspendedForBattle = False
        self._zoneId = None

    def _enterPolluted(self):
        if self._inClassicBattle():
            self._pollutedMode = True
            self._suspendedForBattle = True
            return
        if self._pollutedMode and self._musicPlaying(self._pollutedMusic):
            return
        self._pollutedMode = True
        self._fadeSwitchToPolluted(
            CorruptionGlobals.POLLUTION_AUDIO_CROSSFADE_SEC)

    def _enterPure(self, restoreCrossfade=False):
        wasPolluted = self._pollutedMode
        self._pollutedMode = False
        if self._inClassicBattle():
            self._stopPollutedMusic()
            return
        if not wasPolluted and not self._musicPlaying(self._pollutedMusic):
            return
        duration = (
            CorruptionGlobals.POLLUTION_AUDIO_RESTORE_CROSSFADE_SEC
            if restoreCrossfade
            else CorruptionGlobals.POLLUTION_AUDIO_CROSSFADE_SEC)
        self._fadeSwitchToPure(duration)

    def _fadeVolume(self, music, startVol, endVol, duration):
        """Build a volume lerp interval for one music handle."""

        def setVol(t, handle=music, a=startVol, b=endVol):
            if handle is None:
                return
            try:
                handle.setVolume(a + (b - a) * float(t))
            except Exception:
                pass

        return LerpFunctionInterval(
            setVol, fromData=0.0, toData=1.0, duration=max(0.05, duration))

    def _fadeSwitchToPolluted(self, duration):
        polluted = self._ensurePollutedMusic()
        if polluted is None:
            return
        street = self._streetMusic()
        self._finishFade()
        half = max(0.05, float(duration) * 0.5)
        outStart = CorruptionGlobals.PURE_STREET_MUSIC_VOLUME
        if street is not None:
            try:
                outStart = float(street.getVolume())
            except Exception:
                pass
        inVol = CorruptionGlobals.POLLUTED_STREET_MUSIC_VOLUME

        def stopStreet():
            if street is None:
                return
            try:
                street.stop()
                street.setVolume(CorruptionGlobals.PURE_STREET_MUSIC_VOLUME)
            except Exception:
                pass

        def startPolluted():
            try:
                polluted.setLoop(1)
                polluted.setVolume(0.0)
                base.playMusic(polluted, looping=1, interrupt=1, volume=0.0)
                if not self._musicPlaying(polluted):
                    polluted.play()
            except Exception:
                try:
                    polluted.play()
                except Exception:
                    pass

        steps = []
        if street is not None and self._musicPlaying(street):
            steps.append(self._fadeVolume(street, outStart, 0.0, half))
            steps.append(Func(stopStreet))
        else:
            steps.append(Func(stopStreet))
        steps.append(Func(startPolluted))
        steps.append(self._fadeVolume(polluted, 0.0, inVol, half))
        self._fadeIval = Sequence(*steps)
        self._fadeIval.start()

    def _fadeSwitchToPure(self, duration):
        street = self._streetMusic()
        polluted = self._pollutedMusic
        self._finishFade()
        half = max(0.05, float(duration) * 0.5)
        outStart = CorruptionGlobals.POLLUTED_STREET_MUSIC_VOLUME
        if polluted is not None:
            try:
                outStart = float(polluted.getVolume())
            except Exception:
                pass
        inVol = CorruptionGlobals.PURE_STREET_MUSIC_VOLUME

        def stopPolluted():
            self._stopPollutedMusic()
            if polluted is not None:
                try:
                    polluted.setVolume(
                        CorruptionGlobals.POLLUTED_STREET_MUSIC_VOLUME)
                except Exception:
                    pass

        def startStreet():
            if street is None:
                return
            try:
                street.setLoop(1)
                street.setVolume(0.0)
                base.playMusic(street, looping=1, interrupt=1, volume=0.0)
                if not self._musicPlaying(street):
                    street.play()
            except Exception:
                try:
                    street.play()
                except Exception:
                    pass

        steps = []
        if polluted is not None and self._musicPlaying(polluted):
            steps.append(self._fadeVolume(polluted, outStart, 0.0, half))
            steps.append(Func(stopPolluted))
        else:
            steps.append(Func(stopPolluted))
        steps.append(Func(startStreet))
        if street is not None:
            steps.append(self._fadeVolume(street, 0.0, inVol, half))
        self._fadeIval = Sequence(*steps)
        self._fadeIval.start()
