"""Cream splash + delayed cream aftershock on Ink Smudge hit / splash.

World-space CardMaker juice that fires on Smudge melee hit beside
SmudgeInkSplashFx (#75) purple ink — sunny cream / pastel contrast so basic
corrupt packs read juicier. Deepened mid-body hit juice: juicier splat/flecks,
radial cream hose smears (SmudgeInkSplashFx punch-smear cousin), then a wider
settling aftershock (halo + residual flecks) — distinct from Snare counter
cream deepen (#245, horizontal whip), Brute spit cream deepen (#249, vertical
drip), and Gunk puddle cream deepen (#238, flat ground bloom). Same residual
grammar as telegraph cream warn aftershock (#121). Soft under purple splash;
cream / pastel only (not ink). Wired from DistributedCorruptToon hit reaction
beside SmudgeInkSplash + SmudgeHitCreamWashFx (hit path only — death keeps
splash + death cream wash). Client only. Toontown spiritual sequel — no
keyblades / no KH branding.
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

from toontown.corruption import CorruptionGlobals


def smudgeHitCreamSplashLook():
    """Resolve cream splash palette / motion; compose with purple ink splash."""
    look = dict(getattr(
        CorruptionGlobals, 'SMUDGE_HIT_CREAM_SPLASH_LOOK', {}) or {})
    # Lazy import avoids circular load with Smudge ink splash.
    try:
        from toontown.corruption.SmudgeInkSplashFx import smudgeInkSplashLook
        purple = smudgeInkSplashLook('hit')
        look.setdefault('lift', float(purple.get('lift', 2.05)))
        # Land cream as purple splat settles — ahead of cream wash (#165).
        splatSec = float(purple.get('splatSec', 0.18))
        look.setdefault(
            'delaySec',
            splatSec * float(look.get('delayScale', 0.32)))
    except Exception:
        look.setdefault('lift', 2.05)
        look.setdefault(
            'delaySec',
            float(getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_SPLASH_DELAY_SEC', 0.06)))
    look.setdefault(
        'binSort',
        int(getattr(
            CorruptionGlobals, 'SMUDGE_HIT_CREAM_SPLASH_BIN', 46)))
    return look


class SmudgeHitCreamSplash(object):
    """Owns brief cream splash + delayed cream aftershock at a world position."""

    def __init__(self):
        self._ival = None
        self._nodes = []
        self._haloNP = None

    def play(self, pos, parent=None, delay=None):
        """Spawn cream splash + aftershock at `pos`. Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_SPLASH_ENABLED', True):
            return None
        self.clear()
        look = smudgeHitCreamSplashLook()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look.get('lift', 2.05)))

        if delay is None:
            delay = float(look.get(
                'delaySec',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_DELAY_SEC', 0.06)))

        parts = []
        splat = self._spawnSplat(parentNP, origin, look)
        if splat is not None:
            parts.append(splat)

        smearCount = max(0, int(look.get('smearCount', 0)))
        if look.get(
                'smearEnabled',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_SMEAR_ENABLED', True)):
            for i in range(smearCount):
                part = self._spawnHoseSmear(parentNP, origin, look, i)
                if part is not None:
                    parts.append(part)

        fleckCount = max(0, int(look.get('fleckCount', 0)))
        for i in range(fleckCount):
            part = self._spawnFleck(parentNP, origin, look, i, fleckCount)
            if part is not None:
                parts.append(part)

        if not parts:
            return None

        splashParallel = Parallel(*parts)
        aftershock = self._buildAftershock(parentNP, origin)
        body = splashParallel
        if aftershock is not None:
            body = Parallel(splashParallel, aftershock)

        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            body,
            Func(self.clear),
            name='smudgeHitCreamSplash',
        )
        self._ival.start()
        return self._ival

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in list(self._nodes):
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []

    def _spawnSplat(self, parentNP, origin, look):
        """Tiny billboard cream blob — Smudge hit pack-scan cream core."""
        try:
            half = float(look.get('splatHalf', 0.24))
            cm = CardMaker('smudge-hit-cream-splash-core')
            cm.setFrame(-half, half, -half * 0.92, half * 0.92)
            splat = parentNP.attachNewNode(cm.generate())
            splat.setPos(origin)
            splat.setBillboardPointEye()
            splat.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get(
                'splatColor',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_COLOR',
                    (1.0, 0.97, 0.82, 0.94)))
            splat.setColor(color[0], color[1], color[2], color[3])
            splat.setColorScale(1, 1, 1, 0)
            splat.setScale(0.32)
            splat.setBin('fixed', int(look.get('binSort', 46)))
            splat.setDepthWrite(False)
            self._nodes.append(splat)

            rimHalf = half * float(look.get('rimScale', 1.28))
            cmRim = CardMaker('smudge-hit-cream-splash-rim')
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.9, rimHalf * 0.9)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin)
            rim.setBillboardPointEye()
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look.get(
                'rimColor',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_RIM_COLOR',
                    (1.0, 0.98, 0.88, 0.7)))
            rim.setColor(rimColor[0], rimColor[1], rimColor[2], rimColor[3])
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.28)
            rim.setBin('fixed', int(look.get('binSort', 46)) - 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('splatPeak', 1.5))
            sec = float(look.get('splatSec', 0.15))
            peakA = float(look.get('peakAlpha', 0.94))
            return Parallel(
                Sequence(
                    LerpColorScaleInterval(
                        splat, sec * 0.25, Vec4(1, 1, 1, peakA),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        splat, sec * 0.75, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(splat, sec, peak, blendType='easeOut'),
                Sequence(
                    LerpColorScaleInterval(
                        rim, sec * 0.2, Vec4(1, 1, 1, 0.65),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        rim, sec * 0.8, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                LerpScaleInterval(
                    rim, sec, peak * 1.14, blendType='easeOut'),
            )
        except Exception:
            return None

    def _spawnHoseSmear(self, parentNP, origin, look, index):
        """Radial cream hose smear — mid-body punch-smear cue.

        Distinct from Snare horizontal whip filaments (#245), Brute vertical
        drip filaments (#249), and Gunk flat puddle-plane bloom (#238):
        outward cream smear matching purple SmudgeInkSplashFx punch-smear
        grammar so pack hits read as rubber-hose cream against ink.
        """
        try:
            side = -1.0 if (index % 2) == 0 else 1.0
            t = 0.42 + 0.22 * (index // 2)
            # Radial mid-body bias — punch-smear cousin, not sideways whip.
            angle = (pi * 0.4) + side * (0.32 + 0.18 * index)
            spread = float(look.get(
                'smearSpread',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_SMEAR_SPREAD', 0.95)))
            end = Point3(
                origin[0] + cos(angle) * spread * t,
                origin[1] + sin(angle) * spread * 0.5,
                origin[2] + 0.06 + sin(pi * 0.22 * index) * 0.22,
            )
            half = float(look.get(
                'smearHalf',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_SMEAR_HALF', 0.1)))
            cm = CardMaker(
                'smudge-hit-cream-splash-smear-%s' % index)
            # Soft elongated frame — cream hose smear, not whip / drip / bloom.
            cm.setFrame(-half, half, -half * 1.1, half * 1.1)
            smear = parentNP.attachNewNode(cm.generate())
            start = Point3(
                origin[0] + side * 0.05,
                origin[1] + 0.04,
                origin[2] + 0.04 * ((index % 3) - 1),
            )
            smear.setPos(start)
            smear.setBillboardPointEye()
            smear.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get(
                'smearColor',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_SMEAR_COLOR',
                    (1.0, 0.97, 0.84, 0.92)))
            tint = 0.9 + 0.08 * (index % 3)
            smear.setColor(
                min(1.4, color[0] * tint),
                min(1.4, color[1] * tint),
                min(1.4, color[2] * tint),
                color[3])
            smear.setColorScale(1, 1, 1, 0)
            smear.setScale(Point3(0.5, 0.5, 0.65))
            smear.setBin('fixed', int(look.get('binSort', 46)) + 1)
            smear.setDepthWrite(False)
            self._nodes.append(smear)
            travel = float(look.get(
                'smearSec',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_SMEAR_SEC', 0.22)))
            peakA = float(look.get(
                'smearPeakAlpha',
                getattr(
                    CorruptionGlobals,
                    'SMUDGE_HIT_CREAM_SPLASH_SMEAR_PEAK_ALPHA',
                    0.9)))
            delay = 0.012 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(smear, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(
                            smear, travel * 0.4, Point3(1.2, 0.7, 1.3),
                            blendType='easeOut'),
                        LerpScaleInterval(
                            smear, travel * 0.6, Point3(0.35, 0.25, 1.55),
                            blendType='easeIn'),
                    ),
                    Sequence(
                        LerpColorScaleInterval(
                            smear, travel * 0.22, Vec4(1, 1, 1, peakA),
                            blendType='easeOut'),
                        LerpColorScaleInterval(
                            smear, travel * 0.78, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
            )
        except Exception:
            return None

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Outward cream fleck — telegraph cream warn / Smudge hit cousin."""
        try:
            angle = (2.0 * pi * index) / max(1, count) + (0.16 * (index % 3))
            dist = float(look.get('fleckDist', 1.0)) * (
                0.55 + 0.16 * (index % 4))
            lift = float(look.get('fleckLift', 0.38)) * (
                0.4 + 0.18 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * dist,
                origin[1] + cos(angle) * dist,
                origin[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.1))
            if index % 2 == 0:
                cm = CardMaker(
                    'smudge-hit-cream-splash-fleck-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.35, 0.35, 0.35)
                midScale = Point3(1.15, 1.15, 0.55)
                endScale = Point3(1.45, 1.45, 0.12)
            else:
                cm = CardMaker(
                    'smudge-hit-cream-splash-streak-%s' % index)
                cm.setFrame(
                    -half * 0.32, half * 0.32, -half * 1.45, half * 1.45)
                startScale = Point3(0.28, 0.28, 0.6)
                midScale = Point3(0.5, 0.5, 1.35)
                endScale = Point3(1.2, 0.2, 0.14)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(origin)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            colors = look.get('fleckColors') or getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_SPLASH_FLECK_COLORS',
                ((1.0, 0.97, 0.82, 0.9),))
            color = colors[index % len(colors)]
            fleck.setColor(color[0], color[1], color[2], color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 46)) + 1)
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.2))
            delay = 0.01 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.45, midScale),
                        LerpScaleInterval(fleck, travel * 0.55, endScale),
                    ),
                    LerpColorScaleInterval(
                        fleck, travel, Vec4(1, 1, 1, 0), blendType='easeIn'),
                ),
            )
        except Exception:
            return None

    def _buildAftershock(self, parentNP, origin):
        """Delayed soft cream flecks (+ optional halo) after the cream splash."""
        if not getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_DELAY_SEC', 0.16))
        parts = []

        if getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = max(0, int(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_COUNT', 4)))
        streakCount = max(0, int(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_COUNT', 1)))
        for i in range(creamCount):
            part = self._spawnAftershockSpark(
                parentNP, origin, i, creamCount, elongated=False)
            if part is not None:
                parts.append(part)
        for i in range(streakCount):
            part = self._spawnAftershockSpark(
                parentNP, origin, i, streakCount, elongated=True)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parentNP, origin):
        half = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_HALF', 0.46))
        startScale = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_START', 0.28))
        peakScale = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_PEAK', 1.5))
        sec = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_SEC', 0.3))
        peakA = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA', 0.22))
        r, g, b, _a = getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        try:
            cm = CardMaker('smudge-hit-cream-aftershock-halo')
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            binSort = int(getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_SPLASH_BIN', 46))
            halo.setBin('fixed', binSort - 1)
            halo.setDepthWrite(False)
            halo.setBillboardPointEye()
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

    def _spawnAftershockSpark(self, parentNP, origin, index, total,
                              elongated=False):
        """Softer cream fleck / streak that settles — residual aftershock."""
        count = max(1, int(total))
        if elongated:
            size = float(getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_SIZE', 0.12))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_COLOR',
                (1.0, 0.98, 0.82, 0.82))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_AFTERSHOCK_STREAK_END',
                (1.0, 0.9, 0.5, 0.0))
            nameSuffix = 'streak'
            angleBias = 0.42
        else:
            size = float(getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_AFTERSHOCK_SIZE', 0.1))
            r, g, b, a = getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_AFTERSHOCK_COLOR',
                (1.0, 0.96, 0.72, 0.85))
            er, eg, eb, ea = getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_AFTERSHOCK_END',
                (1.0, 0.92, 0.55, 0.0))
            nameSuffix = 'cream'
            angleBias = 0.18
        drift = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_DRIFT', 0.62))
        fall = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_FALL', 0.4))
        sec = float(getattr(
            CorruptionGlobals,
            'SMUDGE_HIT_CREAM_AFTERSHOCK_SEC', 0.34))
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            cm = CardMaker(
                'smudge-hit-cream-aftershock-%s-%s' % (
                    nameSuffix, index))
            if elongated:
                cm.setFrame(
                    -size * 0.35, size * 0.35,
                    -size * 1.15, size * 1.15)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            spark = parentNP.attachNewNode(cm.generate())
            spark.setTransparency(TransparencyAttrib.MAlpha)
            spark.setColor(r, g, b, 1)
            spark.setColorScale(r, g, b, a)
            spark.setPos(
                origin[0] + cos(angle) * 0.1,
                origin[1] + sin(angle) * 0.1,
                origin[2] + 0.02 * (index % 2))
            spark.setScale(0.26 + 0.06 * (index % 3))
            binSort = int(getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_SPLASH_BIN', 46))
            spark.setBin('fixed', binSort)
            spark.setDepthWrite(False)
            spark.setBillboardPointEye()
        except Exception:
            return None

        # Settle sideways / slightly down after purple ink splash.
        end = Point3(
            origin[0] + cos(angle) * drift * 0.6,
            origin[1] + sin(angle) * drift * 0.6,
            origin[2] - fall - 0.06 * (index % 3))
        peak = size * (1.15 + 0.08 * (index % 2))
        self._nodes.append(spark)
        stagger = 0.02 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    spark, max(0.01, sec), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
                LerpPosInterval(
                    spark, max(0.01, sec), end, blendType='easeIn'),
                Sequence(
                    LerpScaleInterval(
                        spark, max(0.01, sec * 0.4), peak,
                        blendType='easeOut'),
                    LerpScaleInterval(
                        spark, max(0.01, sec * 0.6), 0.12,
                        blendType='easeIn'),
                ),
            ),
        )
