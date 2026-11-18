"""Rising cream / pastel sparkle flecks on CorruptToon silhouette cream rim.

Sunny Toontown cream chips that rise from the silhouette cream rim edge —
purity sparkle contrast, not another ink spray. Composes lift / period with
CorruptSilhouetteCreamRimFx.silhouetteCreamRimLook and borrows twinkle
size/timing from IdleCreamDripSparkleFx.idleCreamDripSparkleLook so rising
rim sparkles sit beside rim orbit flecks (#114) and idle cream drip sparkles
(#125) without sync-locking. Wired from DistributedCorruptToon beside
IdleInkDrip + IdleCreamDripContrast + IdleCreamDripSparkles +
SilhouetteCreamRimFlecks (start / pause / resume / clear together). Client
only. Toontown spiritual sequel — no keyblades / no KH branding.
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


def silhouetteCreamSparkleLook(archetype=None, finaleLook=None):
    """Resolve rising rim-sparkle tunables; compose with rim + drip sparkle."""
    look = dict(getattr(
        CorruptionGlobals, 'SILHOUETTE_CREAM_SPARKLE_LOOK', {}) or {})
    # Lazy import avoids circular load with CorruptSilhouetteCreamRimFx.
    try:
        from toontown.corruption.CorruptSilhouetteCreamRimFx import (
            silhouetteCreamRimLook)
        rim = silhouetteCreamRimLook(archetype, finaleLook=finaleLook)
        look.setdefault('lift', float(rim.get('lift', 2.05)))
        # Offset period so rising sparkles don't sync-lock with rim OR drip sparkle.
        rimPeriod = float(rim.get('periodSec', 1.85))
        look.setdefault(
            'periodSec',
            rimPeriod * float(look.get('periodScale', 0.64)))
        look.setdefault(
            'settleSec',
            float(rim.get('settleSec', 0.55)) + float(
                look.get('settleBias', -0.08)))
        look.setdefault(
            'rimRadius', float(rim.get('rimRadius', 0.72)) * float(
                look.get('rimRadiusScale', 0.96)))
        look.setdefault(
            'rimZJitter', float(rim.get('rimZJitter', 0.22)) * float(
                look.get('rimZJitterScale', 0.7)))
    except Exception:
        look.setdefault('lift', 2.05)
        look.setdefault('periodSec', 1.18)
        look.setdefault('settleSec', 0.47)
        look.setdefault('rimRadius', 0.69)
        look.setdefault('rimZJitter', 0.15)
    # Prefer idle cream drip sparkle grammar sizes when unset.
    try:
        from toontown.corruption.IdleCreamDripSparkleFx import (
            idleCreamDripSparkleLook)
        sparkle = idleCreamDripSparkleLook(archetype, finaleLook=finaleLook)
        look.setdefault(
            'fleckHalf', float(sparkle.get('fleckHalf', 0.07)) * float(
                look.get('fleckHalfScale', 0.88)))
        look.setdefault(
            'fleckSec', float(sparkle.get('fleckSec', 0.36)) * float(
                look.get('fleckSecScale', 1.12)))
    except Exception:
        look.setdefault('fleckHalf', 0.06)
        look.setdefault('fleckSec', 0.4)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_SPARKLE_BIN', 44)))
    return look


class SilhouetteCreamSparkles(object):
    """Owns looping rising cream sparkle flecks parented under a CorruptToon."""

    def __init__(self):
        self._loopIval = None
        self._burstIval = None
        self._nodes = []
        self._paused = False
        self._parent = None
        self._archetype = CorruptionGlobals.ARCHETYPE_INK
        self._finaleLook = None
        self._look = None

    def start(self, parent, archetype=None, finaleLook=None):
        """Begin sparse looping rising rim sparkles under `parent`. Returns loop or None."""
        self.clear()
        if not getattr(
                CorruptionGlobals, 'SILHOUETTE_CREAM_SPARKLE_ENABLED', True):
            return None
        if parent is None:
            return None
        try:
            if parent.isEmpty():
                return None
        except Exception:
            return None
        self._parent = parent
        self._archetype = archetype
        self._finaleLook = finaleLook
        self._look = silhouetteCreamSparkleLook(archetype, finaleLook=finaleLook)
        self._paused = False
        period = max(0.45, float(self._look.get('periodSec', 1.18)))
        settle = max(0.05, float(self._look.get('settleSec', 0.47)))
        self._loopIval = Sequence(
            Wait(settle),
            Func(self._emitBurst),
            Wait(period),
            name='corruptSilhouetteCreamSparkleLoop',
        )
        self._loopIval.loop()
        return self._loopIval

    def pause(self):
        """Stop emitting + clear sparkles so telegraph juice owns the frame."""
        self._paused = True
        if self._loopIval is not None:
            try:
                self._loopIval.pause()
            except Exception:
                pass
        self._clearBurst()

    def resume(self):
        """Resume rising rim sparkles after telegraph / hit recovery."""
        if not getattr(
                CorruptionGlobals, 'SILHOUETTE_CREAM_SPARKLE_ENABLED', True):
            return
        if self._parent is None:
            return
        try:
            if self._parent.isEmpty():
                return
        except Exception:
            return
        self._paused = False
        if self._loopIval is not None:
            try:
                self._loopIval.resume()
                return
            except Exception:
                pass
        self.start(
            self._parent,
            archetype=self._archetype,
            finaleLook=self._finaleLook,
        )

    def clear(self):
        self._paused = True
        if self._loopIval is not None:
            try:
                self._loopIval.pause()
            except Exception:
                pass
            self._loopIval = None
        self._clearBurst()
        self._parent = None
        self._look = None

    def _clearBurst(self):
        if self._burstIval is not None:
            try:
                self._burstIval.pause()
            except Exception:
                pass
            self._burstIval = None
        for np in self._nodes:
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []

    def _emitBurst(self):
        """Spawn one cheap rising cream sparkle cycle on the silhouette rim."""
        if self._paused or self._parent is None or self._look is None:
            return
        try:
            if self._parent.isEmpty():
                return
        except Exception:
            return
        self._clearBurst()
        look = self._look
        try:
            origin = Point3(0.0, 0.0, float(look.get('lift', 2.05)))
        except Exception:
            origin = Point3(0.0, 0.0, 2.05)
        parts = []
        count = max(1, int(look.get('fleckCount', 2)))
        for i in range(count):
            part = self._spawnFleck(self._parent, origin, look, i, count)
            if part is not None:
                parts.append(part)
        if not parts:
            return
        self._burstIval = Sequence(
            Parallel(*parts),
            Func(self._clearBurst),
            name='corruptSilhouetteCreamSparkleBurst',
        )
        self._burstIval.start()

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Soft cream / pastel sparkle — starts on rim, rises (not orbit drift)."""
        try:
            colors = look.get('fleckColors') or (
                getattr(
                    CorruptionGlobals, 'SILHOUETTE_CREAM_SPARKLE_COLORS', ()) or
                ((1.0, 0.97, 0.82, 0.84),))
            color = colors[index % len(colors)]
            endColors = look.get('fleckEndColors') or (
                getattr(
                    CorruptionGlobals,
                    'SILHOUETTE_CREAM_SPARKLE_END_COLORS', ()) or
                ((1.0, 0.94, 0.55, 0.0),))
            endColor = endColors[index % len(endColors)]

            # Phase-offset from rim (+0.95) and drip sparkle (+2.05+0.55) so
            # rising chips read as a fourth cream layer on the silhouette edge.
            angle = (
                (2.0 * pi * index) / max(1, count)
                + 0.95
                + 1.35
                + (0.19 * (index % 3)))
            rim = float(look.get('rimRadius', 0.69)) * (
                0.84 + 0.11 * (index % 4))
            start = Point3(
                origin[0] + sin(angle) * rim,
                origin[1] + cos(angle) * rim * 0.55,
                origin[2] + float(look.get('rimZJitter', 0.15)) * (
                    -0.2 + 0.35 * (index % 3)),
            )
            # Mostly rise — tiny outward so motion reads vertical, not rim orbit.
            out = float(look.get('fleckDist', 0.12)) * (
                0.35 + 0.2 * (index % 3))
            lift = float(look.get('fleckLift', 0.55)) * (
                0.65 + 0.28 * (index % 3))
            end = Point3(
                start[0] + sin(angle) * out,
                start[1] + cos(angle) * out * 0.45,
                start[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.06))
            # Idle-cream-drip sparkle grammar: soft chips vs thin pastel streaks.
            if index % 2 == 0:
                cm = CardMaker('corrupt-silhouette-cream-sparkle-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.2, 0.2, 0.26)
                midScale = Point3(1.1, 1.1, 0.75)
                endScale = Point3(1.5, 1.5, 0.08)
            else:
                cm = CardMaker(
                    'corrupt-silhouette-cream-sparkle-streak-%s' % index)
                cm.setFrame(
                    -half * 0.26, half * 0.26, -half * 1.45, half * 1.45)
                startScale = Point3(0.18, 0.18, 0.4)
                midScale = Point3(0.5, 0.5, 1.2)
                endScale = Point3(1.05, 0.16, 0.08)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(start)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            # Mild pastel variance so rising sparkles aren't a flat cream plate.
            tint = 0.92 + 0.08 * ((index * 7) % 5) / 4.0
            fleck.setColor(
                min(1.45, color[0] * tint),
                min(1.45, color[1] * tint),
                min(1.45, color[2] * tint),
                color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 44)))
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.4))
            delay = float(look.get('fleckStagger', 0.038)) * index
            er, eg, eb, ea = endColor
            # Twinkle: pop scale mid-way (sparkle) then fade while rising.
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.32, midScale),
                        LerpScaleInterval(fleck, travel * 0.68, endScale),
                    ),
                    LerpColorScaleInterval(
                        fleck, travel, Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None
