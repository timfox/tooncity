"""Rubber-hose cream edge pop on combo-counter HUD tick.

Local cream border strips framing the lower-left punch counter when it
increments — ActBannerCreamEdgeFx / wave-announce cream edge overlay
grammar as a snappy HUD frame so combo reads clearly. Soft under the
counter TextNode; cream / pastel only (not ink). Wired from
MeleeCombatController._showComboCounter beside hose pop + cream sparkle.
Client only. Toontown spiritual sequel — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from . import HackSlashConfig


class ComboCounterCreamEdgePulse(object):
    """Owns a brief aspect2d cream edge pop around the combo counter."""

    def __init__(self):
        self._ival = None
        self._edgeRootNP = None

    def play(self, origin=None):
        """Arm snappy cream edge pop at the counter. Returns Sequence or None."""
        if not getattr(
                HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        if origin is None:
            origin = getattr(
                HackSlashConfig, 'COMBO_COUNTER_POS', (-0.95, 0.0, -0.42))
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = -0.95, 0.0, -0.42

        edgeRoot = self._buildEdgeRoot(parent, ox, oy, oz)
        if edgeRoot is None:
            return None

        peak = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_PEAK', 0.55))
        mid = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_PULSE', 0.32))
        inSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_IN_SEC', 0.04))
        holdSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_HOLD_SEC', 0.02))
        pulseSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_PULSE_SEC', 0.06))
        outSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_OUT_SEC', 0.14))
        scalePeak = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_SCALE_PEAK', 1.18))

        # Rubber-hose two-beat: bright pop → soft settle pulse → fade.
        alphaPart = Sequence(
            LerpColorScaleInterval(
                edgeRoot, max(0.01, inSec), Vec4(1, 1, 1, peak),
                blendType='easeOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                edgeRoot, max(0.01, pulseSec), Vec4(1, 1, 1, mid),
                blendType='easeInOut'),
            LerpColorScaleInterval(
                edgeRoot, max(0.01, outSec), Vec4(1, 1, 1, 0),
                blendType='easeIn'),
        )
        parts = [alphaPart]
        # Soft outward scale pop so the edge "reads" as a tick beat.
        if scalePeak > 1.001:
            scaleIn = max(0.01, inSec + holdSec * 0.5)
            scaleOut = max(
                0.01, pulseSec + outSec + max(0.0, holdSec) * 0.5)
            parts.append(Sequence(
                LerpScaleInterval(
                    edgeRoot, scaleIn, Point3(scalePeak, 1.0, scalePeak),
                    blendType='easeOut'),
                LerpScaleInterval(
                    edgeRoot, scaleOut, Point3(1.0, 1.0, 1.0),
                    blendType='easeIn'),
            ))

        self._ival = Sequence(
            Parallel(*parts),
            Func(self.clear),
            name='hackslashComboCounterCreamEdge',
        )
        self._ival.start()
        return self._ival

    def _buildEdgeRoot(self, parent, ox, oy, oz):
        """Four local cream edge strips framing the punch counter."""
        try:
            halfW = float(getattr(
                HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_HALF_W', 0.22))
            halfH = float(getattr(
                HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_HALF_H', 0.08))
            edge = float(getattr(
                HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE', 0.018))
            binSort = int(getattr(
                HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_BIN', 54))
            cream = getattr(
                HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_COLOR', None)
            if cream is None:
                cream = (1.0, 0.97, 0.82, 1.0)
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])

            root = parent.attachNewNode('hackslash-combo-cream-edge')
            root.setPos(ox, oy, oz)
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', binSort)
            root.setDepthTest(False)
            root.setDepthWrite(False)
            # Top / bottom / left / right — cream frame, open center for text.
            frames = (
                (-halfW - edge, halfW + edge, halfH, halfH + edge),
                (-halfW - edge, halfW + edge, -halfH - edge, -halfH),
                (-halfW - edge, -halfW, -halfH, halfH),
                (halfW, halfW + edge, -halfH, halfH),
            )
            for i, frame in enumerate(frames):
                cm = CardMaker('hackslash-combo-cream-edge-%s' % i)
                cm.setFrame(*frame)
                strip = root.attachNewNode(cm.generate())
                strip.setTransparency(TransparencyAttrib.MAlpha)
                strip.setColor(r, g, b, 1)
                strip.setBin('fixed', binSort)
                strip.setDepthTest(False)
                strip.setDepthWrite(False)
            self._edgeRootNP = root
            return root
        except Exception:
            self._edgeRootNP = None
            return None

    def clear(self):
        """Stop edge pop and remove cream edge nodes."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        root = self._edgeRootNP
        self._edgeRootNP = None
        if root is None:
            return
        try:
            if not root.isEmpty():
                root.removeNode()
        except Exception:
            pass
