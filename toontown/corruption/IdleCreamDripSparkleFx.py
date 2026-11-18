"""Cream / pastel sparkle flecks layered on IdleCreamDripContrastFx.

Sunny Toontown cream chips that twinkle beside falling idle cream drips —
purity sparkle contrast, not another ink spray. Reuses silhouette cream rim
(#114) sparkle grammar (orbit/drift chips + twinkle scale) while composing
lift / period with IdleCreamDripContrastFx.idleCreamDripLook so sparkles sit
on the cream drip layer without sync-locking drips or rim flecks. Idle cream
wash pulses softly against ink drips beside this sparkle layer.
Wired from DistributedCorruptToon beside IdleInkDrip + IdleCreamDripContrast +
IdleCreamWashPulse + SilhouetteCreamRimFlecks (start / pause / resume / clear
together). Client only. Toontown spiritual sequel — no keyblades / no KH branding.
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


def idleCreamDripSparkleLook(archetype=None, finaleLook=None):
    """Resolve cream drip-sparkle tunables; compose lift/period with idle cream."""
    look = dict(getattr(
        CorruptionGlobals, 'IDLE_CREAM_DRIP_SPARKLE_LOOK', {}) or {})
    # Lazy import avoids circular load with IdleCreamDripContrastFx.
    try:
        from toontown.corruption.IdleCreamDripContrastFx import idleCreamDripLook
        cream = idleCreamDripLook(archetype, finaleLook=finaleLook)
        look.setdefault('lift', float(cream.get('lift', 2.05)))
        # Offset period so sparkles don't sync-lock with cream drips OR rim.
        creamPeriod = float(cream.get('periodSec', 2.55))
        look.setdefault(
            'periodSec',
            creamPeriod * float(look.get('periodScale', 0.58)))
        look.setdefault(
            'settleSec',
            float(cream.get('settleSec', 0.75)) + float(
                look.get('settleBias', -0.18)))
    except Exception:
        look.setdefault('lift', 2.05)
        look.setdefault('periodSec', 1.48)
        look.setdefault('settleSec', 0.55)
    # Prefer silhouette rim sparkle grammar sizes when unset.
    try:
        from toontown.corruption.CorruptSilhouetteCreamRimFx import (
            silhouetteCreamRimLook)
        rim = silhouetteCreamRimLook(archetype, finaleLook=finaleLook)
        look.setdefault(
            'fleckHalf', float(rim.get('fleckHalf', 0.09)) * float(
                look.get('fleckHalfScale', 0.78)))
        look.setdefault(
            'fleckSec', float(rim.get('fleckSec', 0.42)) * float(
                look.get('fleckSecScale', 0.85)))
    except Exception:
        look.setdefault('fleckHalf', 0.07)
        look.setdefault('fleckSec', 0.36)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'IDLE_CREAM_DRIP_SPARKLE_BIN', 43)))
    return look


class IdleCreamDripSparkles(object):
    """Owns looping soft cream sparkle flecks parented under a CorruptToon."""

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
        """Begin sparse looping cream sparkles under `parent`. Returns loop or None."""
        self.clear()
        if not getattr(CorruptionGlobals, 'IDLE_CREAM_DRIP_SPARKLE_ENABLED', True):
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
        self._look = idleCreamDripSparkleLook(archetype, finaleLook=finaleLook)
        self._paused = False
        period = max(0.45, float(self._look.get('periodSec', 1.48)))
        settle = max(0.05, float(self._look.get('settleSec', 0.55)))
        self._loopIval = Sequence(
            Wait(settle),
            Func(self._emitBurst),
            Wait(period),
            name='corruptIdleCreamDripSparkleLoop',
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
        """Resume cream drip sparkles after telegraph / hit recovery."""
        if not getattr(CorruptionGlobals, 'IDLE_CREAM_DRIP_SPARKLE_ENABLED', True):
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
        """Spawn one cheap cream sparkle cycle near cream drip path."""
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
            name='corruptIdleCreamDripSparkleBurst',
        )
        self._burstIval.start()

    def _spawnFleck(self, parentNP, origin, look, index, count):
        """Soft cream / pastel sparkle — rim grammar, near cream drip angles."""
        try:
            colors = look.get('fleckColors') or (
                getattr(
                    CorruptionGlobals, 'IDLE_CREAM_DRIP_SPARKLE_COLORS', ()) or
                ((1.0, 0.97, 0.82, 0.82),))
            color = colors[index % len(colors)]
            endColors = look.get('fleckEndColors') or (
                getattr(
                    CorruptionGlobals,
                    'IDLE_CREAM_DRIP_SPARKLE_END_COLORS', ()) or
                ((1.0, 0.94, 0.55, 0.0),))
            endColor = endColors[index % len(endColors)]

            # Phase-offset from cream drip (+2.05) and rim (+0.95) so sparkles
            # read as a third cream layer twinkling along the drip path.
            angle = (
                (2.0 * pi * index) / max(1, count)
                + 2.05
                + 0.55
                + (0.17 * (index % 3)))
            # Tighter than silhouette rim — sit near falling cream drips.
            rim = float(look.get('sparkleRadius', 0.42)) * (
                0.78 + 0.14 * (index % 4))
            start = Point3(
                origin[0] + sin(angle) * rim,
                origin[1] + cos(angle) * rim * 0.5,
                origin[2] - float(look.get('dripBias', 0.18)) * (
                    0.35 + 0.35 * (index % 3)),
            )
            out = float(look.get('fleckDist', 0.22)) * (
                0.45 + 0.22 * (index % 3))
            lift = float(look.get('fleckLift', 0.18)) * (
                0.4 + 0.25 * (index % 3))
            end = Point3(
                start[0] + sin(angle) * out,
                start[1] + cos(angle) * out * 0.5,
                start[2] + lift,
            )
            half = float(look.get('fleckHalf', 0.07))
            # Silhouette-rim sparkle grammar: soft chips vs thin pastel streaks.
            if index % 2 == 0:
                cm = CardMaker('corrupt-idle-cream-drip-sparkle-%s' % index)
                cm.setFrame(-half, half, -half * 0.9, half * 0.9)
                startScale = Point3(0.22, 0.22, 0.28)
                midScale = Point3(1.05, 1.05, 0.7)
                endScale = Point3(1.45, 1.45, 0.1)
            else:
                cm = CardMaker(
                    'corrupt-idle-cream-drip-sparkle-streak-%s' % index)
                cm.setFrame(
                    -half * 0.28, half * 0.28, -half * 1.35, half * 1.35)
                startScale = Point3(0.2, 0.2, 0.42)
                midScale = Point3(0.55, 0.55, 1.15)
                endScale = Point3(1.1, 0.18, 0.1)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(start)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            # Mild pastel variance so sparkles aren't a flat cream plate.
            tint = 0.92 + 0.08 * ((index * 5) % 5) / 4.0
            fleck.setColor(
                min(1.45, color[0] * tint),
                min(1.45, color[1] * tint),
                min(1.45, color[2] * tint),
                color[3])
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 43)))
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)
            travel = float(look.get('fleckSec', 0.36))
            delay = float(look.get('fleckStagger', 0.035)) * index
            er, eg, eb, ea = endColor
            # Twinkle: pop scale mid-way (sparkle) then fade out.
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, travel, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(fleck, travel * 0.35, midScale),
                        LerpScaleInterval(fleck, travel * 0.65, endScale),
                    ),
                    LerpColorScaleInterval(
                        fleck, travel, Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None
