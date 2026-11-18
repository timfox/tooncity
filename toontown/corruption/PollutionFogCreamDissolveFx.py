"""Rubber-hose cream / pastel fog dissolve on street purity complete.

When purityRestoreFx fires, PollutionManager's ink fog/haze lifts through a
sunny cream dissolve — palette shift toward cream plus a soft aspect2d veil
and rising glitter flecks. Matches fog density clear ramp (#38 /
POLLUTION_FOG_CLEAR_SEC) and StreetSparkle / death-cream fleck chip patterns.
Client only. Toontown spiritual sequel — no keyblades / no KH branding.
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


class PollutionFogCreamDissolveFx(object):
    """Listens for purity restore; cream-tints fog clear + overlay flecks."""

    notify = DirectNotifyGlobal.directNotify.newCategory(
        'PollutionFogCreamDissolveFx')

    def __init__(self, pollutionManager=None):
        self._pm = pollutionManager
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
        self.playDissolve(zoneId)

    def __onSettled(self, zoneId=None):
        self.clear()

    def __onLeftZone(self, *args):
        self.clear()

    def playDissolve(self, zoneId=None):
        """Cream-tint fog clear + soft veil / flecks (StreetSparkle family)."""
        if not getattr(CorruptionGlobals, 'FOG_CREAM_DISSOLVE_ENABLED', True):
            return
        self.clear()
        pm = self._pm
        if pm is not None:
            try:
                pm.beginCreamDissolve()
            except Exception:
                self.notify.debug('cream dissolve tint skipped')

        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return

        origin = getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_ORIGIN',
            (0.0, 0.0, -0.28))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, -0.28

        r, g, b = getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_COLOR',
            (1.0, 0.97, 0.82))
        binSort = int(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_BIN', 26))

        parts = []
        shimmerPart = self._spawnShimmer(parent, ox, oy, oz, r, g, b, binSort)
        if shimmerPart is not None:
            parts.append(shimmerPart)
        parts.extend(self._spawnFlecks(parent, ox, oy, oz, binSort))

        # Blend cream into PollutionManager fog/haze over the clear window.
        dissolveSec = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_SEC',
            CorruptionGlobals.POLLUTION_FOG_CLEAR_SEC))
        if pm is not None and dissolveSec > 0.0:
            def setBlend(t, manager=pm):
                try:
                    manager.setCreamDissolveBlend(float(t))
                except Exception:
                    pass

            parts.append(Sequence(
                LerpFunctionInterval(
                    setBlend, fromData=0.0, toData=1.0,
                    duration=max(0.01, dissolveSec * 0.42),
                    blendType='easeOut'),
                LerpFunctionInterval(
                    setBlend, fromData=1.0, toData=0.0,
                    duration=max(0.01, dissolveSec * 0.58),
                    blendType='easeIn'),
                Func(self._finishManagerDissolve),
            ))

        if not parts:
            self._finishManagerDissolve()
            return

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='pollutionFogCreamDissolve',
        )
        self._ival.start()

    def _finishManagerDissolve(self):
        pm = self._pm
        if pm is None:
            return
        try:
            pm.finishCreamDissolve()
        except Exception:
            pass

    def _spawnShimmer(self, parent, ox, oy, oz, r, g, b, binSort):
        """Soft mid-low cream veil — dissolving fog bed, not purity flash."""
        peak = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_HAZE_PEAK', 0.20))
        inSec = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_SHIMMER_IN_SEC', 0.08))
        holdSec = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_SHIMMER_HOLD_SEC', 0.22))
        outSec = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_SHIMMER_OUT_SEC', 0.58))
        try:
            cm = CardMaker('pollution-fog-cream-dissolve-shimmer')
            # Wide fog-plane band — sits on ink haze as it cream-dissolves.
            cm.setFrame(-2.0, 2.0, -0.72, 0.48)
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
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_FLECK_COUNT', 14))
        if count <= 0:
            return []
        size = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_FLECK_SIZE', 0.024))
        rise = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_FLECK_RISE', 0.78))
        spread = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_FLECK_SPREAD', 1.40))
        sec = float(getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_FLECK_SEC', 0.68))
        colors = getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_FLECK_COLORS', None)
        if not colors:
            colors = (
                getattr(
                    CorruptionGlobals, 'FOG_CREAM_DISSOLVE_FLECK_COLOR',
                    (1.0, 0.98, 0.72, 0.95)),
            )
        endColor = getattr(
            CorruptionGlobals, 'FOG_CREAM_DISSOLVE_FLECK_END_COLOR',
            (1.0, 0.94, 0.55, 0.0))

        parts = []
        for i in range(count):
            try:
                t = (float(i) / max(1, count - 1)) - 0.5
                angle = (2.0 * pi * i) / float(count) + 0.28
                color = colors[i % len(colors)]
                r, g, b, a = color
                # Alternate chip / cross fleck — StreetSparkle cream glitter.
                cm = CardMaker('pollution-fog-cream-dissolve-fleck-%s' % i)
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
                startX = ox + t * spread + cos(angle) * 0.05
                startZ = oz + 0.025 * (i % 4) + sin(angle) * 0.025
                fleck.setPos(startX, oy, startZ)
                fleck.setScale(0.4 + 0.1 * (i % 4))
                fleck.setBin('fixed', binSort + 1 + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
                self._fleckNPs.append(fleck)
            except Exception:
                continue

            er, eg, eb, ea = endColor
            end = Point3(
                startX + cos(angle) * 0.14,
                oy,
                startZ + rise * (0.55 + 0.45 * ((i % 5) / 4.0)))
            delay = 0.02 * i
            twinkle = 0.05 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, twinkle, 1.15, blendType='easeOut'),
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
        self._finishManagerDissolve()
