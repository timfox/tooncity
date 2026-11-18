"""Rubber-hose cream wash pulse on polluted reclaim-street entry shimmer.

Fullscreen soft cream veil that pulses with EntryCreamShimmerFx — StreetColorWash
overlay grammar as a discrete entry beat (sibling of PurityCompleteCreamWashFx,
softer / not a purity payoff). Owns reclaim STREET_PACK zone enter only;
composes with PlayEntry ink edge vignette, progressive StreetColorWash, and
entry cream shimmer flecks. Toontown spiritual-sequel tone only — no keyblades /
no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.reclaim import ReclaimGlobals


class EntryCreamWashPulseFxClient(DirectObject):
    """Listens for reclaim-street zone enter and plays a soft cream wash pulse."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._washNP = None
        self._armedZone = None
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('localToonLeftZone', self._onLeftZone)
        self.accept('purityRestoreFx', self._onPurity)
        self.accept('purityRestoreSettled', self._onSettled)
        # Boot once so a cold start mid-street still gets the wash pulse.
        try:
            taskMgr.doMethodLater(  # noqa: F821
                2.15, self._bootZone, 'reclaimEntryCreamWashPulseBoot')
        except Exception:
            pass

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('reclaimEntryCreamWashPulseBoot')  # noqa: F821
        except Exception:
            pass
        self.clear()

    def _bootZone(self, task):
        if hasattr(base, 'localAvatar'):  # noqa: F821
            self._onZoneChange(getattr(base.localAvatar, 'zoneId', None))
        return task.done

    def _onZoneChange(self, zoneId=None):
        if zoneId is None and hasattr(base, 'localAvatar'):  # noqa: F821
            zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return
        zoneId = int(zoneId)
        # Leaving a reclaim street — drop any lingering wash pulse.
        if self._armedZone is not None and zoneId != self._armedZone:
            self.clear()
            self._armedZone = None
        pack = ReclaimGlobals.streetPack(zoneId)
        if pack is None:
            return
        if not self._streetIsPolluted(zoneId, pack):
            self.clear()
            return
        self._armedZone = zoneId
        self.playPulse()

    def _onLeftZone(self, *args):
        self._armedZone = None
        self.clear()

    def _onPurity(self, zoneId=None):
        # Soft-clear so purity cream wash / sparkle own the payoff beat.
        self.clear()

    def _onSettled(self, zoneId=None):
        self.clear()

    def _streetIsPolluted(self, zoneId, pack=None):
        """True when local pollution (or STREET_PACK seed) still stains."""
        minLevel = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_MIN_POLLUTION',
            getattr(ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_MIN_POLLUTION', 0.08)))
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is not None:
            try:
                level = float(pm.getPollution(zoneId))
                if level >= minLevel:
                    return True
                # Known pure (reclaim cleared) — skip cream entry wash pulse.
                if zoneId in getattr(pm, 'zonePollution', {}):
                    return False
            except Exception:
                pass
        if pack is None:
            pack = ReclaimGlobals.streetPack(zoneId)
        if pack is None:
            return False
        return float(pack.get('seedPollution', 0.0)) >= minLevel

    def playPulse(self):
        """Two-beat cream wash pulse under entry shimmer (bright → settle → fade)."""
        if not getattr(ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        cream = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_COLOR', None)
        if cream is None:
            cream = getattr(
                ReclaimGlobals, 'STREET_WASH_CREAM', (1.0, 0.97, 0.82))
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_PEAK', 0.16))
        mid = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_MID', 0.09))
        inSec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_IN_SEC', 0.08))
        pulseSec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_PULSE_SEC', 0.14))
        holdSec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_HOLD_SEC', 0.12))
        outSec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_OUT_SEC', 0.50))
        binSort = int(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_PULSE_BIN', 32))

        try:
            cm = CardMaker('reclaim-entry-cream-wash-pulse')
            # Full-frame veil — StreetColorWash / purity-complete pulse grammar.
            cm.setFrame(-2, 2, -2, 2)
            wash = parent.attachNewNode(cm.generate())
            wash.setTransparency(TransparencyAttrib.MAlpha)
            wash.setColor(r, g, b, 1)
            wash.setColorScale(r, g, b, 0)
            wash.setBin('fixed', binSort)
            wash.setDepthTest(False)
            wash.setDepthWrite(False)
            self._washNP = wash
        except Exception:
            self._washNP = None
            return

        # Soft two-beat under EntryCreamShimmerFx center veil + flecks (bin 36).
        self._ival = Sequence(
            LerpColorScaleInterval(
                wash, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            LerpColorScaleInterval(
                wash, max(0.01, pulseSec), Vec4(r, g, b, mid),
                blendType='easeInOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                wash, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
            Func(self.clear),
            name='reclaimEntryCreamWashPulse',
        )
        self._ival.start()

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        wash = self._washNP
        self._washNP = None
        if wash is None:
            return
        try:
            if not wash.isEmpty():
                wash.removeNode()
        except Exception:
            pass


_client = None


def ensureEntryCreamWashPulseFxClient():
    global _client
    if _client is None:
        _client = EntryCreamWashPulseFxClient()
    return _client
