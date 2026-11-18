"""Ambient idle ink drip on CorruptToons between attack telegraphs.

Subtle rubber-hose pollution presence — sparse drips from the silhouette,
cheaper and quieter than CorruptTelegraphInkFx telegraph pops. Wired from
DistributedCorruptToon so idle presence pauses while telegraph juice owns
the frame. Archetype palette (purple / sludge green / amber); Overlord
retints from finale phase colors. Toontown spiritual sequel only — no
keyblades / no KH framing.
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


def idleInkLook(archetype, finaleLook=None):
    """Resolve soft idle drip palette; finale look can override colors."""
    try:
        aid = int(archetype)
    except (TypeError, ValueError):
        aid = CorruptionGlobals.ARCHETYPE_INK
    looks = CorruptionGlobals.IDLE_INK_DRIP_LOOK
    look = dict(looks.get(aid, looks[CorruptionGlobals.ARCHETYPE_INK]))
    if finaleLook:
        # Soft retint toward Overlord charge so P1/P2 idle still reads.
        charge = finaleLook.get('telegraphCharge')
        if charge and len(charge) >= 3:
            look['dripColor'] = (
                min(1.05, charge[0] * 0.28),
                min(1.05, charge[1] * 0.28),
                min(1.05, charge[2] * 0.28),
                float(look.get('dripColor', (0, 0, 0, 0.55))[3]),
            )
            look['streakColor'] = (
                min(1.15, charge[0] * 0.38),
                min(1.15, charge[1] * 0.38),
                min(1.15, charge[2] * 0.38),
                float(look.get('streakColor', (0, 0, 0, 0.5))[3]),
            )
    return look


class IdleInkDrip(object):
    """Owns looping ambient ink drips parented under a CorruptToon."""

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
        """Begin sparse looping drips under `parent`. Returns loop or None."""
        self.clear()
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
        self._look = idleInkLook(archetype, finaleLook=finaleLook)
        self._paused = False
        period = max(0.6, float(self._look.get('periodSec', 2.0)))
        # First drip after a short settle so spawn/telegraph don't stack.
        settle = float(self._look.get('settleSec', 0.45))
        self._loopIval = Sequence(
            Wait(settle),
            Func(self._emitBurst),
            Wait(period),
            name='corruptIdleInkDripLoop',
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
        """Resume ambient drips after telegraph / hit recovery."""
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
        # Loop was lost — restart from current look.
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
        """Spawn one cheap drip cycle (1–2 drops, no splat)."""
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
            origin = Point3(0.0, 0.0, float(look.get('lift', 2.0)))
        except Exception:
            origin = Point3(0.0, 0.0, 2.0)
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
            name='corruptIdleInkDripBurst',
        )
        self._burstIval.start()

    def _spawnDrip(self, parentNP, origin, look, index, count):
        """Soft rubber-hose drip falling from chest height (parent-local)."""
        try:
            angle = (2.0 * pi * index) / max(1, count) + 0.85
            spread = float(look['dripSpread']) * (0.4 + 0.18 * (index % 3))
            fall = float(look['dripFall']) * (0.8 + 0.1 * (index % 3))
            end = Point3(
                origin[0] + sin(angle) * spread,
                origin[1] + cos(angle) * spread * 0.45,
                origin[2] - fall,
            )
            half = float(look['dripHalf'])
            if index % 2 == 0:
                cm = CardMaker('corrupt-idle-drip-%s' % index)
                cm.setFrame(-half, half, -half * 1.2, half * 1.2)
                startScale = Point3(0.45, 0.45, 0.55)
                midScale = Point3(0.65, 0.65, 1.15)
                endScale = Point3(1.05, 1.05, 0.2)
                color = look['dripColor']
            else:
                cm = CardMaker('corrupt-idle-streak-%s' % index)
                cm.setFrame(-half * 0.3, half * 0.3, -half * 1.8, half * 1.8)
                startScale = Point3(0.35, 0.35, 0.7)
                midScale = Point3(0.45, 0.45, 1.35)
                endScale = Point3(0.9, 0.25, 0.15)
                color = look['streakColor']
            drip = parentNP.attachNewNode(cm.generate())
            start = Point3(
                origin[0] + sin(angle) * spread * 0.12,
                origin[1] + cos(angle) * spread * 0.08,
                origin[2] - 0.06 * index,
            )
            drip.setPos(start)
            drip.setBillboardPointEye()
            drip.setTransparency(TransparencyAttrib.MAlpha)
            tint = 0.9 + 0.08 * ((index * 3) % 4) / 3.0
            drip.setColor(
                min(1.2, color[0] * tint),
                min(1.2, color[1] * tint),
                min(1.2, color[2] * tint),
                color[3])
            drip.setScale(startScale)
            drip.setBin('fixed', int(look.get('binSort', 40)))
            drip.setDepthWrite(False)
            self._nodes.append(drip)
            travel = float(look['dripSec'])
            delay = float(look.get('dripStagger', 0.04)) * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(drip, travel, end, blendType='easeIn'),
                    Sequence(
                        LerpScaleInterval(drip, travel * 0.45, midScale),
                        LerpScaleInterval(drip, travel * 0.55, endScale),
                    ),
                    LerpColorScaleInterval(
                        drip, travel, Vec4(1, 1, 1, 0), blendType='easeIn'),
                ),
            )
        except Exception:
            return None
