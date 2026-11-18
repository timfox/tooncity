"""Rubber-hose cream / pastel fade of hood corruption tint on purity complete.

When purityRestoreFx fires, PollutionPropTint's hood-biased street geom
colorScale lifts through sunny cream instead of snapping clear — plus a soft
aspect2d veil and rising glitter flecks under the fog cream dissolve layer.
Matches fog cream dissolve (#100 / FOG_CREAM_DISSOLVE_*) and hood tint (#13)
patterns. Client only. Toontown spiritual sequel — no keyblades / no KH branding.
"""

from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpFunctionInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from toontown.corruption import CorruptionGlobals


class PollutionHoodTintCreamFadeFx(object):
    """Listens for purity restore; cream-fades hood prop tint + soft flecks."""

    notify = DirectNotifyGlobal.directNotify.newCategory(
        'PollutionHoodTintCreamFadeFx')

    def __init__(self, propTint=None):
        self._propTint = propTint
        self._active = False
        self._ival = None
        self._shimmerNP = None
        self._fleckNPs = []

    def start(self):
        if self._active:
            return
        self._active = True
        messenger.accept(  # noqa: F821
            'purityRestoreFx', self, self.__onPurityRestore, [], 1)
        messenger.accept(  # noqa: F821
            'purityRestoreSettled', self, self.__onSettled, [], 1)
        messenger.accept(  # noqa: F821
            'localToonLeftZone', self, self.__onLeftZone, [], 1)

    def stop(self):
        if not self._active:
            return
        self._active = False
        messenger.ignore('purityRestoreFx', self)  # noqa: F821
        messenger.ignore('purityRestoreSettled', self)  # noqa: F821
        messenger.ignore('localToonLeftZone', self)  # noqa: F821
        self.clear()

    def __onPurityRestore(self, zoneId=None):
        self.playFade(zoneId)

    def __onSettled(self, zoneId=None):
        self.clear()

    def __onLeftZone(self, *args):
        self.clear()

    def playFade(self, zoneId=None):
        """Cream-fade hood prop tint + soft veil / flecks (fog-dissolve family)."""
        if not getattr(
                CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_ENABLED', True):
            return
        # Tear down prior overlay only — do not finishPropTint before we arm,
        # or beginCreamFade loses the hood ink capture.
        self._clearOverlay(finishTint=False)
        propTint = self._propTint
        if propTint is not None:
            try:
                propTint.beginCreamFade()
            except Exception:
                self.notify.debug('hood tint cream fade skipped')

        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            self._finishPropTintFade()
            return

        origin = getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_ORIGIN',
            (0.0, 0.0, -0.18))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.18

        r, g, b = getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_COLOR',
            CorruptionGlobals.FOG_CREAM_DISSOLVE_COLOR)
        binSort = int(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_BIN', 27))

        parts = []
        shimmerPart = self._spawnShimmer(parent, ox, oy, oz, r, g, b, binSort)
        if shimmerPart is not None:
            parts.append(shimmerPart)
        parts.extend(self._spawnFlecks(parent, ox, oy, oz, binSort))

        # Ink → sunny cream over the clear window, then clear geom (no ink snap-back).
        fadeSec = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_SEC',
            CorruptionGlobals.POLLUTION_FOG_CLEAR_SEC))
        if propTint is not None and fadeSec > 0.0:
            def setBlend(t, tint=propTint):
                try:
                    tint.setCreamFadeBlend(float(t))
                except Exception:
                    pass

            parts.append(Sequence(
                LerpFunctionInterval(
                    setBlend, fromData=0.0, toData=1.0,
                    duration=max(0.01, fadeSec),
                    blendType='easeOut'),
                Func(self._finishPropTintFade),
            ))

        if not parts:
            self._finishPropTintFade()
            return

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='pollutionHoodTintCreamFade',
        )
        self._ival.start()

    def _finishPropTintFade(self):
        propTint = self._propTint
        if propTint is None:
            return
        try:
            propTint.finishCreamFade()
        except Exception:
            pass

    def _spawnShimmer(self, parent, ox, oy, oz, r, g, b, binSort):
        """Soft cream veil — hood tint dissolve bed under fog dissolve flecks."""
        peak = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_HAZE_PEAK', 0.12))
        inSec = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_SHIMMER_IN_SEC', 0.07))
        holdSec = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_SHIMMER_HOLD_SEC', 0.18))
        outSec = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_SHIMMER_OUT_SEC', 0.55))
        try:
            cm = CardMaker('pollution-hood-tint-cream-fade-shimmer')
            # Narrower band than fog dissolve — reads as geom wash lift.
            cm.setFrame(-1.6, 1.6, -0.55, 0.40)
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
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_FLECK_COUNT', 8))
        if count <= 0:
            return []
        size = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_FLECK_SIZE', 0.018))
        rise = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_FLECK_RISE', 0.55))
        spread = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_FLECK_SPREAD', 1.10))
        sec = float(getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_FLECK_SEC', 0.58))
        colors = getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_FLECK_COLORS', None)
        if not colors:
            colors = (
                getattr(
                    CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_FLECK_COLOR',
                    (1.0, 0.98, 0.78, 0.88)),
            )
        endColor = getattr(
            CorruptionGlobals, 'HOOD_TINT_CREAM_FADE_FLECK_END_COLOR',
            (1.0, 0.95, 0.62, 0.0))

        parts = []
        for i in range(count):
            try:
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.42
                color = colors[i % len(colors)]
                r, g, b, a = color
                # Alternate chip / cross fleck — StreetSparkle cream glitter.
                cm = CardMaker('pollution-hood-tint-cream-fade-fleck-%s' % i)
                if (i % 3) == 0:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.35, size * 1.35)
                elif (i % 3) == 1:
                    cm.setFrame(
                        -size * 1.35, size * 1.35, -size * 0.35, size * 0.35)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = parent.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                startX = ox + t * spread + cos(angle) * 0.04
                startZ = oz + 0.02 * (i % 4) + sin(angle) * 0.02
                fleck.setPos(startX, oy, startZ)
                fleck.setScale(0.35 + 0.1 * (i % 4))
                fleck.setBin('fixed', binSort + 1 + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._fleckNPs.append(fleck)
            except Exception:
                continue

            er, eg, eb, ea = endColor
            end = Point3(
                startX + cos(angle) * 0.12,
                oy,
                startZ + rise * (0.55 + 0.45 * ((i % 5) / 4.0)))
            delay = 0.025 * i
            twinkle = 0.045 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, twinkle, 1.12, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec), 0.05, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
        return parts

    def clear(self):
        self._clearOverlay(finishTint=True)

    def _clearOverlay(self, finishTint=True):
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
        if finishTint:
            self._finishPropTintFade()
