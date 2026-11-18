"""Soft cream / pastel drip contrast layered on IdleInkDripFx.

Sunny Toontown cream chips that drip with ambient idle ink — purity contrast
against dark pollution drips, not another ink spray. Composes lift / period
with IdleInkDripFx.idleInkLook. Wired from DistributedCorruptToon beside
IdleInkDrip (start / pause / resume / clear together). Client only.
Toontown spiritual sequel — no keyblades / no KH branding.
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


def idleCreamDripLook(archetype=None, finaleLook=None):
    """Resolve cream idle-drip tunables; compose lift/period with idle ink look."""
    look = dict(getattr(
        CorruptionGlobals, 'IDLE_CREAM_DRIP_LOOK', {}) or {})
    # Lazy import avoids circular load with IdleInkDripFx.
    try:
        from toontown.corruption.IdleInkDripFx import idleInkLook
        ink = idleInkLook(archetype, finaleLook=finaleLook)
        look.setdefault('lift', float(ink.get('lift', 2.05)))
        # Offset period slightly so cream drips don't sync-lock with ink.
        inkPeriod = float(ink.get('periodSec', 2.15))
        look.setdefault(
            'periodSec',
            inkPeriod * float(look.get('periodScale', 1.18)))
        look.setdefault(
            'settleSec',
            float(ink.get('settleSec', 0.55)) + float(
                look.get('settleBias', 0.22)))
    except Exception:
        look.setdefault('lift', 2.05)
        look.setdefault('periodSec', 2.55)
        look.setdefault('settleSec', 0.75)
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'IDLE_CREAM_DRIP_BIN', 41)))
    return look


class IdleCreamDripContrast(object):
    """Owns looping soft cream drips parented under a CorruptToon (vs idle ink)."""

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
        """Begin sparse looping cream drips under `parent`. Returns loop or None."""
        self.clear()
        if not getattr(CorruptionGlobals, 'IDLE_CREAM_DRIP_ENABLED', True):
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
        self._look = idleCreamDripLook(archetype, finaleLook=finaleLook)
        self._paused = False
        period = max(0.7, float(self._look.get('periodSec', 2.55)))
        settle = float(self._look.get('settleSec', 0.75))
        self._loopIval = Sequence(
            Wait(settle),
            Func(self._emitBurst),
            Wait(period),
            name='corruptIdleCreamDripLoop',
        )
        self._loopIval.loop()
        return self._loopIval

    def pause(self):
        """Stop emitting + clear drips so telegraph juice owns the frame."""
        self._paused = True
        if self._loopIval is not None:
            try:
                self._loopIval.pause()
            except Exception:
                pass
        self._clearBurst()

    def resume(self):
        """Resume cream contrast drips after telegraph / hit recovery."""
        if not getattr(CorruptionGlobals, 'IDLE_CREAM_DRIP_ENABLED', True):
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
        """Spawn one cheap cream drip cycle (1–2 drops, no splat)."""
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
        count = max(1, int(look.get('dripCount', 1)))
        for i in range(count):
            part = self._spawnDrip(self._parent, origin, look, i, count)
            if part is not None:
                parts.append(part)
        if not parts:
            return
        self._burstIval = Sequence(
            Parallel(*parts),
            Func(self._clearBurst),
            name='corruptIdleCreamDripBurst',
        )
        self._burstIval.start()

    def _spawnDrip(self, parentNP, origin, look, index, count):
        """Soft cream / pastel drip — contrast to idle ink, not ink-colored."""
        try:
            colors = look.get('dripColors') or (
                getattr(CorruptionGlobals, 'IDLE_CREAM_DRIP_COLORS', ()) or
                ((1.0, 0.97, 0.82, 0.72),))
            color = colors[index % len(colors)]
            endColors = look.get('dripEndColors') or (
                getattr(
                    CorruptionGlobals, 'IDLE_CREAM_DRIP_END_COLORS', ()) or
                ((1.0, 0.94, 0.55, 0.0),))
            endColor = endColors[index % len(endColors)]

            # Phase-offset from IdleInkDripFx (ink uses +0.85) so cream reads
            # as a second drip layer beside pollution ink.
            angle = (
                (2.0 * pi * index) / max(1, count)
                + 2.05
                + (0.11 * (index % 3)))
            spread = float(look.get('dripSpread', 0.38)) * (
                0.45 + 0.2 * (index % 3))
            fall = float(look.get('dripFall', 0.85)) * (
                0.75 + 0.12 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * spread,
                origin[1] + cos(angle) * spread * 0.5,
                origin[2] - fall,
            )
            half = float(look.get('dripHalf', 0.1))
            # Alternate soft cream chips vs thin pastel streaks.
            if index % 2 == 0:
                cm = CardMaker('corrupt-idle-cream-drip-%s' % index)
                cm.setFrame(-half, half, -half * 1.05, half * 1.05)
                startScale = Point3(0.4, 0.4, 0.5)
                midScale = Point3(0.7, 0.7, 1.05)
                endScale = Point3(1.1, 1.1, 0.18)
            else:
                cm = CardMaker('corrupt-idle-cream-streak-%s' % index)
                cm.setFrame(-half * 0.28, half * 0.28, -half * 1.65, half * 1.65)
                startScale = Point3(0.32, 0.32, 0.65)
                midScale = Point3(0.42, 0.42, 1.25)
                endScale = Point3(0.95, 0.22, 0.12)
            drip = parentNP.attachNewNode(cm.generate())
            start = Point3(
                origin[0] + sin(angle) * spread * 0.14,
                origin[1] + cos(angle) * spread * 0.1,
                origin[2] - 0.05 * index,
            )
            drip.setPos(start)
            drip.setBillboardPointEye()
            drip.setTransparency(TransparencyAttrib.MAlpha)
            # Mild pastel variance so cream drips aren't a flat plate.
            tint = 0.92 + 0.08 * ((index * 2) % 5) / 4.0
            drip.setColor(
                min(1.45, color[0] * tint),
                min(1.45, color[1] * tint),
                min(1.45, color[2] * tint),
                color[3])
            drip.setScale(startScale)
            drip.setBin('fixed', int(look.get('binSort', 41)))
            drip.setDepthWrite(False)
            self._nodes.append(drip)
            travel = float(look.get('dripSec', 0.58))
            delay = float(look.get('dripStagger', 0.06)) * index
            er, eg, eb, ea = endColor
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(drip, travel, end, blendType='easeIn'),
                    Sequence(
                        LerpScaleInterval(drip, travel * 0.45, midScale),
                        LerpScaleInterval(drip, travel * 0.55, endScale),
                    ),
                    LerpColorScaleInterval(
                        drip, travel, Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None
