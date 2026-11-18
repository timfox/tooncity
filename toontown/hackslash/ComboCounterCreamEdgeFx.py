"""Rubber-hose cream edge pop on combo-counter HUD tick.

Local cream border strips framing the lower-left punch counter when it
increments — ActBannerCreamEdgeFx / wave-announce cream edge overlay
grammar as a snappy HUD frame so combo reads clearly. Deepened past #267
so ticks read juicier still: brighter peak / thicker strips / longer mid
hold / juicier scale pop, plus a richer local cream aftershock (more flecks
+ stronger halo) that settles on the counter frame. Soft under the counter
TextNode; cream / pastel only (not ink). Distinct from hurt-stagger cream
wash deepen (#287), dodge-cancel cream flash (#281), i-frame cream wash
(#228 / #272), and aim-nudge cream deepen (#254) — stays on the local
punch-counter frame, not a fullscreen wash / aim assist cue. Wired from
MeleeCombatController._showComboCounter beside hose pop + cream sparkle.
Client only. Toontown spiritual sequel — no keyblades / no KH branding.
"""

from math import cos, pi

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

from . import HackSlashConfig


class ComboCounterCreamEdgePulse(object):
    """Owns cream edge pop + residual edge aftershock around the combo counter."""

    def __init__(self):
        self._ival = None
        self._edgeRootNP = None
        self._fleckNPs = []
        self._haloNP = None

    def play(self, origin=None):
        """Arm snappy cream edge pop + aftershock. Returns Sequence or None."""
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
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_PEAK', 0.84))
        mid = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_PULSE', 0.58))
        inSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_IN_SEC', 0.04))
        holdSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_HOLD_SEC', 0.07))
        pulseSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_PULSE_SEC', 0.10))
        outSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_OUT_SEC', 0.22))
        scalePeak = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_SCALE_PEAK', 1.44))

        # Rubber-hose two-beat: bright pop → soft settle pulse → fade.
        # Deepened-past-#267 peak / hold so the tick reads juicier still.
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
        edgeParts = [alphaPart]
        # Soft outward scale pop so the edge "reads" as a tick beat.
        if scalePeak > 1.001:
            scaleIn = max(0.01, inSec + holdSec * 0.5)
            scaleOut = max(
                0.01, pulseSec + outSec + max(0.0, holdSec) * 0.5)
            edgeParts.append(Sequence(
                LerpScaleInterval(
                    edgeRoot, scaleIn, Point3(scalePeak, 1.0, scalePeak),
                    blendType='easeOut'),
                LerpScaleInterval(
                    edgeRoot, scaleOut, Point3(1.0, 1.0, 1.0),
                    blendType='easeIn'),
            ))

        edgeBody = Parallel(*edgeParts)
        aftershock = self._buildAftershock(parent, ox, oy, oz)
        if aftershock is not None:
            body = Parallel(edgeBody, aftershock)
        else:
            body = edgeBody

        self._ival = Sequence(
            body,
            Wait(0.02),
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
                HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE', 0.032))
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

    def _buildAftershock(self, parent, ox, oy, oz):
        """Delayed soft cream flecks (+ optional halo) after edge pop."""
        if not getattr(
                HackSlashConfig,
                'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig,
            'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_DELAY_SEC', 0.06))
        parts = []

        if getattr(
                HackSlashConfig,
                'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_COUNT', 5))
        sec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_SEC', 0.28))
        for i in range(count):
            part = self._spawnAftershockFleck(
                parent, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parent, ox, oy, oz):
        half = float(getattr(
            HackSlashConfig,
            'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_HALF', 0.18))
        startScale = float(getattr(
            HackSlashConfig,
            'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_START', 0.35))
        peakScale = float(getattr(
            HackSlashConfig,
            'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_PEAK', 1.35))
        sec = float(getattr(
            HackSlashConfig,
            'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_SEC', 0.24))
        peakA = float(getattr(
            HackSlashConfig,
            'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_PEAK_ALPHA', 0.22))
        r, g, b, _a = getattr(
            HackSlashConfig,
            'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_BIN', 53))
        try:
            cm = CardMaker('hackslash-combo-cream-edge-aftershock-halo')
            # Soft oval halo under the local cream frame — quiet residual.
            cm.setFrame(-half, half, -half * 0.45, half * 0.45)
            halo = parent.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(ox, oy, oz)
            halo.setScale(startScale)
            halo.setBin('fixed', binSort)
            halo.setDepthTest(False)
            halo.setDepthWrite(False)
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

    def _spawnAftershockFleck(self, parent, ox, oy, oz, index, total, sec):
        """Softer cream chip that settles near the counter frame."""
        count = max(1, int(total))
        size = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_SIZE', 0.013))
        drift = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_DRIFT', 0.14))
        fall = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_FALL', 0.12))
        r, g, b, a = getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.84))
        er, eg, eb, ea = getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_EDGE_AFTERSHOCK_BIN', 53))
        angle = (2.0 * pi * index) / float(count) + 0.35
        try:
            cm = CardMaker(
                'hackslash-combo-cream-edge-aftershock-%s' % index)
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.20, size * 1.20, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            fleck.setPos(ox, oy, oz)
            fleck.setBin('fixed', binSort)
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None
        self._fleckNPs.append(fleck)
        dx = cos(angle) * drift
        dz = -abs(fall) * (0.55 + 0.35 * ((index % 3) / 2.0))
        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.25), Vec4(r, g, b, a),
                    blendType='easeOut'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.75), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
            LerpPosInterval(
                fleck, max(0.01, sec), Point3(ox + dx, oy, oz + dz),
                blendType='easeOut'),
            LerpScaleInterval(
                fleck, max(0.01, sec), 0.35, startScale=1.0,
                blendType='easeIn'),
        )

    def clear(self):
        """Stop edge pop and remove cream edge / aftershock nodes."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        root = self._edgeRootNP
        self._edgeRootNP = None
        if root is not None:
            try:
                if not root.isEmpty():
                    root.removeNode()
            except Exception:
                pass
        halo = self._haloNP
        self._haloNP = None
        if halo is not None:
            try:
                if not halo.isEmpty():
                    halo.removeNode()
            except Exception:
                pass
        flecks = self._fleckNPs
        self._fleckNPs = []
        for fleck in flecks:
            try:
                if fleck is not None and not fleck.isEmpty():
                    fleck.removeNode()
            except Exception:
                pass
