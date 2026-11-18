"""Cream / pastel rim flecks on CorruptToon silhouettes.

Sunny Toontown cream chips that sparkle along the ink silhouette rim —
purity contrast against dark Actor/DNA (or card) silhouettes, not another
ink spray. Composes lift / period with IdleCreamDripContrastFx.idleCreamDripLook
so rim flecks sit beside idle cream drips. Wired from DistributedCorruptToon
beside IdleInkDrip + IdleCreamDripContrast (start / pause / resume / clear
together). Client only. Toontown spiritual sequel — no keyblades / no KH
branding.
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


def silhouetteCreamRimLook(archetype=None, finaleLook=None):
    """Resolve cream rim-fleck tunables; compose lift/period with idle cream."""
    look = dict(getattr(
        CorruptionGlobals, 'SILHOUETTE_CREAM_RIM_LOOK', {}) or {})
    # Lazy import avoids circular load with IdleCreamDripContrastFx.
    try:
        from toontown.corruption.IdleCreamDripContrastFx import idleCreamDripLook
        cream = idleCreamDripLook(archetype, finaleLook=finaleLook)
        look.setdefault('lift', float(cream.get('lift', 2.05)))
        # Offset period so rim flecks don't sync-lock with cream drips.
        creamPeriod = float(cream.get('periodSec', 2.55))
        look.setdefault(
            'periodSec',
            creamPeriod * float(look.get('periodScale', 0.72)))
        look.setdefault(
            'settleSec',
            float(cream.get('settleSec', 0.75)) + float(
                look.get('settleBias', -0.12)))
    except Exception:
        look.setdefault('lift', 2.05)
        look.setdefault('periodSec', 1.85)
        look.setdefault('settleSec', 0.55)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_RIM_BIN', 42)))
    return look


class SilhouetteCreamRimFlecks(object):
    """Owns looping soft cream rim flecks parented under a CorruptToon."""

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
        """Begin sparse looping cream rim flecks under `parent`. Returns loop or None."""
        self.clear()
        if not getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_RIM_ENABLED', True):
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
        self._look = silhouetteCreamRimLook(archetype, finaleLook=finaleLook)
        self._paused = False
        period = max(0.55, float(self._look.get('periodSec', 1.85)))
        settle = max(0.05, float(self._look.get('settleSec', 0.55)))
        self._loopIval = Sequence(
            Wait(settle),
            Func(self._emitBurst),
            Wait(period),
            name='corruptSilhouetteCreamRimLoop',
        )
        self._loopIval.loop()
        return self._loopIval

    def pause(self):
        """Stop emitting + clear flecks so telegraph juice owns the frame."""
        self._paused = True
        if self._loopIval is not None:
            try:
                self._loopIval.pause()
            except Exception:
                pass
        self._clearBurst()

    def resume(self):
        """Resume cream rim flecks after telegraph / hit recovery."""
        if not getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_RIM_ENABLED', True):
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
        """Spawn one cheap cream rim fleck cycle (orbit chips, not drips)."""
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
        count = max(1, int(look.get('fleckCount', 3)))
        for i in range(count):
            part = self._spawnFleck(self._parent, origin, look, i, count)
            if part is not None:
                parts.append(part)
        if not parts:
            return
        self._burstIval = Sequence(
            Parallel(*parts),
            Func(self._clearBurst),
            name='corruptSilhouetteCreamRimBurst',
        )
        self._burstIval.start()

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Soft cream / pastel rim fleck — sits on silhouette edge, not a drip."""
        try:
            colors = look.get('fleckColors') or (
                getattr(CorruptionGlobals, 'SILHOUETTE_CREAM_RIM_COLORS', ()) or
                ((1.0, 0.97, 0.82, 0.78),))
            color = colors[index % len(colors)]
            endColors = look.get('fleckEndColors') or (
                getattr(
                    CorruptionGlobals, 'SILHOUETTE_CREAM_RIM_END_COLORS', ()) or
                ((1.0, 0.94, 0.55, 0.0),))
            endColor = endColors[index % len(endColors)]

            # Ring around silhouette mid — phase-offset from cream drip angles
            # (cream drip uses +2.05) so rim chips read as a separate layer.
            angle = (
                (2.0 * pi * index) / max(1, count)
                + 0.95
                + (0.13 * (index % 3)))
            rim = float(look.get('rimRadius', 0.72)) * (
                0.82 + 0.12 * (index % 4))
            # Start on the silhouette rim, drift slightly outward + up.
            start = Point3(
                origin[0] + sin(angle) * rim,
                origin[1] + cos(angle) * rim * 0.55,
                origin[2] + float(look.get('rimZJitter', 0.22)) * (
                    -0.35 + 0.4 * (index % 3)),
            )
            out = float(look.get('fleckDist', 0.38)) * (
                0.55 + 0.2 * (index % 3))
            lift = float(look.get('fleckLift', 0.28)) * (
                0.45 + 0.22 * (index % 3))
            end = Point3(
                start[0] + sin(angle) * out,
                start[1] + cos(angle) * out * 0.55,
                start[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.09))
            # Alternate soft chips vs thin pastel rim streaks.
            if index % 2 == 0:
                cm = CardMaker('corrupt-silhouette-cream-rim-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.35, 0.35, 0.4)
                midScale = Point3(0.95, 0.95, 0.55)
                endScale = Point3(1.35, 1.35, 0.12)
            else:
                cm = CardMaker('corrupt-silhouette-cream-rim-streak-%s' % index)
                cm.setFrame(
                    -half * 0.32, half * 0.32, -half * 1.4, half * 1.4)
                startScale = Point3(0.28, 0.28, 0.55)
                midScale = Point3(0.48, 0.48, 1.05)
                endScale = Point3(1.05, 0.2, 0.12)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(start)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            # Mild pastel variance so rim flecks aren't a flat cream plate.
            tint = 0.92 + 0.08 * ((index * 3) % 5) / 4.0
            fleck.setColor(
                min(1.45, color[0] * tint),
                min(1.45, color[1] * tint),
                min(1.45, color[2] * tint),
                color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 42)))
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.42))
            delay = float(look.get('fleckStagger', 0.04)) * index
            er, eg, eb, ea = endColor
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.4, midScale),
                        LerpScaleInterval(fleck, travel * 0.6, endScale),
                    ),
                    LerpColorScaleInterval(
                        fleck, travel, Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None
