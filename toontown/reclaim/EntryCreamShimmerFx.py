"""Rubber-hose cream shimmer on reclaim-street entry while polluted.

Soft center cream veil + light flecks so tip / explore copy stays readable
against ink fog. Owns reclaim STREET_PACK zone enter only — composes with
PlayEntry ink edge vignette (corruption tunables), EntryCreamWashPulseFx
(StreetColorWash-style soft cream pulse under this shimmer, plus delayed cream
aftershock + soft settle cream wash owned by the wash client), StreetColorWash
(active reclaim wash + delayed cream aftershock on purity advances), and
StreetSparkleFx (full-purity horizon glitter). Never a purity payoff flash.
Toontown spiritual-sequel tone only — no keyblades / no KH branding.
"""

from math import cos, pi, sin

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


class EntryCreamShimmerFxClient(DirectObject):
    """Listens for reclaim-street zone enter and plays soft cream shimmer."""

    def __init__(self):
        DirectObject.__init__(self)
        self._ival = None
        self._shimmerNP = None
        self._fleckNPs = []
        self._armedZone = None
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('localToonLeftZone', self._onLeftZone)
        self.accept('purityRestoreFx', self._onPurity)
        self.accept('purityRestoreSettled', self._onSettled)
        # Boot once so a cold start mid-street still gets the shimmer.
        try:
            taskMgr.doMethodLater(  # noqa: F821
                2.1, self._bootZone, 'reclaimEntryCreamShimmerBoot')
        except Exception:
            pass

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('reclaimEntryCreamShimmerBoot')  # noqa: F821
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
        # Leaving a reclaim street — drop any lingering shimmer.
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
        self.playShimmer()

    def _onLeftZone(self, *args):
        self._armedZone = None
        self.clear()

    def _onPurity(self, zoneId=None):
        # Soft-clear so purity sparkle / wash own the payoff beat.
        self.clear()

    def _onSettled(self, zoneId=None):
        self.clear()

    def _streetIsPolluted(self, zoneId, pack=None):
        """True when local pollution (or STREET_PACK seed) still stains."""
        minLevel = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_MIN_POLLUTION', 0.08))
        pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        if pm is not None:
            try:
                level = float(pm.getPollution(zoneId))
                if level >= minLevel:
                    return True
                # Known pure (reclaim cleared) — skip cream entry shimmer.
                if zoneId in getattr(pm, 'zonePollution', {}):
                    return False
            except Exception:
                pass
        if pack is None:
            pack = ReclaimGlobals.streetPack(zoneId)
        if pack is None:
            return False
        return float(pack.get('seedPollution', 0.0)) >= minLevel

    def playShimmer(self):
        """Soft center cream veil + flecks (no FOV / geom — wash owns tint)."""
        if not getattr(ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_ENABLED', True):
            return
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        origin = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_ORIGIN', (0.0, 0.0, -0.08))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.08

        r, g, b, _a = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_BIN', 36))
        parts = []

        shimmerPart = self._spawnShimmer(parent, ox, oy, oz, r, g, b, binSort)
        if shimmerPart is not None:
            parts.append(shimmerPart)

        fleckParts = self._spawnFlecks(parent, ox, oy, oz, binSort)
        parts.extend(fleckParts)

        if not parts:
            return
        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='reclaimEntryCreamShimmer',
        )
        self._ival.start()

    def _spawnShimmer(self, parent, ox, oy, oz, r, g, b, binSort):
        """Soft mid-screen cream veil — lifts tip readability vs ink fog."""
        peak = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_PEAK', 0.18))
        inSec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_IN_SEC', 0.10))
        holdSec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_HOLD_SEC', 0.20))
        outSec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_OUT_SEC', 0.48))
        try:
            cm = CardMaker('reclaim-entry-cream-shimmer')
            # Open center band — ink vignette owns the edges.
            cm.setFrame(-1.35, 1.35, -0.72, 0.55)
            shimmer = parent.attachNewNode(cm.generate())
            shimmer.setTransparency(TransparencyAttrib.MAlpha)
            shimmer.setColor(r, g, b, 1)
            shimmer.setColorScale(r, g, b, 0)
            shimmer.setPos(ox, oy, oz)
            shimmer.setBin('fixed', binSort)
            shimmer.setDepthTest(False)
            shimmer.setDepthWrite(False)
            self._shimmerNP = shimmer
        except Exception:
            self._shimmerNP = None
            return None
        return Sequence(
            LerpColorScaleInterval(
                shimmer, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                shimmer, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
        )

    def _spawnFlecks(self, parent, ox, oy, oz, binSort):
        count = int(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_FLECK_COUNT', 8))
        if count <= 0:
            return []
        size = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_FLECK_SIZE', 0.018))
        rise = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_FLECK_RISE', 0.38))
        spread = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_FLECK_SPREAD', 0.95))
        sec = float(getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_FLECK_SEC', 0.42))
        r, g, b, a = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_FLECK_COLOR',
            (1.0, 0.98, 0.72, 0.88))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'ENTRY_CREAM_SHIMMER_FLECK_END_COLOR',
            (1.0, 0.94, 0.55, 0.0))

        parts = []
        for i in range(count):
            try:
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.28
                cm = CardMaker('reclaim-entry-cream-fleck-%s' % i)
                # Alternate chip / fleck — rubber-hose cream glitter.
                if (i % 3) == 0:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.25, size * 1.25)
                elif (i % 3) == 1:
                    cm.setFrame(
                        -size * 1.25, size * 1.25, -size * 0.35, size * 0.35)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = parent.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                startX = ox + t * spread + cos(angle) * 0.03
                startZ = oz + 0.015 * (i % 3) + sin(angle) * 0.015
                fleck.setPos(startX, oy, startZ)
                fleck.setScale(0.4 + 0.08 * (i % 3))
                fleck.setBin('fixed', binSort + 1 + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._fleckNPs.append(fleck)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.08,
                oy,
                startZ + rise * (0.5 + 0.5 * ((i % 4) / 3.0)))
            delay = 0.018 * i
            twinkle = 0.045 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, twinkle, 1.08, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec), 0.06, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
        return parts

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        shimmer = self._shimmerNP
        self._shimmerNP = None
        if shimmer is not None and not shimmer.isEmpty():
            try:
                shimmer.removeNode()
            except Exception:
                pass
        for np in self._fleckNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []


_client = None


def ensureEntryCreamShimmerFxClient():
    global _client
    if _client is None:
        _client = EntryCreamShimmerFxClient()
    return _client
