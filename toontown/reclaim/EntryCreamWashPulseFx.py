"""Rubber-hose cream wash pulse on polluted reclaim-street entry shimmer.

Fullscreen soft cream veil that pulses with EntryCreamShimmerFx — StreetColorWash
overlay grammar as a discrete entry beat (sibling of PurityCompleteCreamWashFx,
softer / not a purity payoff). A delayed cream aftershock (softer flecks settling
downward + soft halo) follows the wash pulse — same residual grammar as
wave-clear cream aftershock (#127) and cheer cream aftershock (#118). Owns
reclaim STREET_PACK zone enter only; composes with PlayEntry ink edge vignette,
progressive StreetColorWash, and entry cream shimmer flecks. Toontown
spiritual-sequel tone only — no keyblades / no KH branding.
"""

from math import cos, pi

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.reclaim import ReclaimGlobals


class EntryCreamWashPulseFxClient(DirectObject):
    """Listens for reclaim-street zone enter; owns cream wash pulse + aftershock."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._washPlayIval = None
        self._washNP = None
        self._fleckNPs = []
        self._haloNP = None
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
        # Leaving a reclaim street — drop any lingering wash pulse / aftershock.
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
        """Two-beat cream wash pulse under entry shimmer + delayed aftershock."""
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
        washIval = Sequence(
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
            name='reclaimEntryCreamWashPulseVeil',
        )
        self._washPlayIval = washIval
        try:
            washIval.start()
        except Exception:
            self.clear()
            return

        washLifetime = inSec + pulseSec + holdSec + outSec
        origin = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_ORIGIN',
            getattr(ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_ORIGIN',
                    (0.0, 0.0, -0.08)))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.08

        aftershock = self._buildAftershock(parent, ox, oy, oz)
        if aftershock is not None:
            # Wash Sequence already started; hold its lifetime beside aftershock.
            self._ival = Sequence(
                Parallel(
                    Wait(washLifetime + 0.04),
                    aftershock,
                ),
                Func(self.clear),
                name='reclaimEntryCreamWashPulse',
            )
        else:
            self._ival = Sequence(
                Wait(washLifetime + 0.04),
                Func(self.clear),
                name='reclaimEntryCreamWashPulse',
            )
        self._ival.start()

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after entry cream wash."""
        if not getattr(ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_DELAY_SEC', 0.22))
        parts = []

        if getattr(ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_COUNT', 5))
        sec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_SEC', 0.32))
        for i in range(count):
            part = self._spawnAftershockFleck(
                parent, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parent, ox, oy, oz):
        half = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_HALF', 0.48))
        startScale = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_START', 0.26))
        peakScale = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_PEAK', 1.15))
        sec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_SEC', 0.26))
        peakA = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA', 0.12))
        r, g, b, _a = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_BIN', 34))
        try:
            cm = CardMaker('reclaim-entry-cream-wash-aftershock-halo')
            # Soft oval halo under entry shimmer — quieter than wave-clear residual.
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = parent.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(ox, oy, oz)
            halo.setScale(startScale)
            halo.setBin('fixed', binSort)
            halo.setDepthTest(False)
            halo.setDepthWrite(False)
        except Exception:
            return None
        self._haloNP = halo
        return Parallel(
            LerpScaleInterval(
                halo, max(0.01, sec), peakScale, blendType='easeOut'),
            Sequence(
                Wait(max(0.0, sec * 0.2)),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.8), Vec4(r, g, b, 0),
                    blendType='easeIn'),
            ),
        )

    def _spawnAftershockFleck(self, parent, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles downward — residual wash aftershock."""
        count = max(1, int(total))
        size = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_SIZE', 0.015))
        drift = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_DRIFT', 0.28))
        fall = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_FALL', 0.22))
        r, g, b, a = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.78))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_WASH_AFTERSHOCK_BIN', 34))
        angle = (2.0 * pi * index) / float(count) + 0.28
        try:
            cm = CardMaker('reclaim-entry-cream-wash-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the entry wash.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.20, size * 1.20, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = ox + cos(angle) * 0.07
            startZ = oz + 0.012 * (index % 3)
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.28 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream, not the entry shimmer's outward rise.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            oy,
            startZ - fall - 0.04 * (index % 3))
        peak = 1.05 + 0.08 * (index % 2)
        self._fleckNPs.append(fleck)
        stagger = 0.016 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.28), peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(
                    fleck, max(0.01, sec * 0.72), end, blendType='easeIn'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.72), 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.72), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def clear(self):
        """Stop wash/aftershock and remove every cream entry wash node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._washPlayIval is not None:
            try:
                self._washPlayIval.pause()
            except Exception:
                pass
            self._washPlayIval = None
        wash = self._washNP
        self._washNP = None
        if wash is not None and not wash.isEmpty():
            try:
                wash.removeNode()
            except Exception:
                pass
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in self._fleckNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []


_client = None


def ensureEntryCreamWashPulseFxClient():
    global _client
    if _client is None:
        _client = EntryCreamWashPulseFxClient()
    return _client
