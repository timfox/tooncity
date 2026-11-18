"""Readable pollution→purity meter during street reclaim (aspect2d).

CardMaker bar + Oswald-flavored label — rubber-hose Toontown tone, no
Kingdom Hearts / keyblade branding. Driven by DistributedReclaimDirector.
"""

from panda3d.core import CardMaker, TextNode, TransparencyAttrib

from direct.interval.IntervalGlobal import Func, LerpScaleInterval, Sequence

from toontown.reclaim import ReclaimGlobals


def _lerpColor(a, b, t):
    t = max(0.0, min(1.0, float(t)))
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


class PurityMeterHud(object):
    """Horizontal purity fill bar: empty = polluted, full = pure street."""

    def __init__(self):
        self._root = None
        self._rimNP = None
        self._trackNP = None
        self._fillNP = None
        self._labelNP = None
        self._pctNP = None
        self._purity = None
        self._popIval = None
        self._lastPopPurity = None

    def isShown(self):
        return self._root is not None and not self._root.isEmpty()

    def show(self):
        if self.isShown():
            return
        g = ReclaimGlobals
        halfW = g.PURITY_METER_WIDTH * 0.5
        halfH = g.PURITY_METER_HEIGHT * 0.5
        pad = g.PURITY_METER_RIM_PAD

        root = aspect2d.attachNewNode('reclaim-purity-meter')  # noqa: F821
        root.setPos(*g.PURITY_METER_POS)
        root.setBin('fixed', g.PURITY_METER_BIN)
        root.setDepthTest(False)
        root.setDepthWrite(False)
        self._root = root

        # Soft outer rim (behind track) so the bar reads at a glance.
        rcm = CardMaker('reclaim-purity-meter-rim')
        rcm.setFrame(-halfW - pad, halfW + pad, -halfH - pad, halfH + pad)
        rim = root.attachNewNode(rcm.generate())
        rim.setTransparency(TransparencyAttrib.MAlpha)
        rim.setColor(*g.PURITY_METER_RIM_COLOR)
        rim.setBin('fixed', g.PURITY_METER_BIN - 1)
        self._rimNP = rim

        # Dark track (ink well under the fill).
        tcm = CardMaker('reclaim-purity-meter-track')
        tcm.setFrame(-halfW, halfW, -halfH, halfH)
        track = root.attachNewNode(tcm.generate())
        track.setTransparency(TransparencyAttrib.MAlpha)
        track.setColor(*g.PURITY_METER_TRACK_COLOR)
        self._trackNP = track

        # Fill grows left→right from the track's left edge.
        fcm = CardMaker('reclaim-purity-meter-fill')
        fcm.setFrame(0.0, g.PURITY_METER_WIDTH, -halfH, halfH)
        fill = root.attachNewNode(fcm.generate())
        fill.setPos(-halfW, 0, 0)
        fill.setTransparency(TransparencyAttrib.MAlpha)
        fill.setColor(*g.PURITY_METER_FILL_POLLUTED)
        fill.setScale(0.001, 1, 1)
        self._fillNP = fill

        ltn = TextNode('reclaim-purity-meter-label')
        ltn.setText(g.PURITY_METER_LABEL)
        ltn.setAlign(TextNode.ACenter)
        ltn.setTextColor(*g.PURITY_METER_LABEL_COLOR)
        ltn.setShadow(0.04, 0.04)
        ltn.setShadowColor(0, 0, 0, 0.75)
        label = root.attachNewNode(ltn)
        label.setScale(g.PURITY_METER_LABEL_SCALE)
        label.setPos(0, 0, g.PURITY_METER_LABEL_Z)
        self._labelNP = label

        ptn = TextNode('reclaim-purity-meter-pct')
        ptn.setText('0%')
        ptn.setAlign(TextNode.ACenter)
        ptn.setTextColor(*g.PURITY_METER_PCT_COLOR)
        ptn.setShadow(0.04, 0.04)
        ptn.setShadowColor(0, 0, 0, 0.7)
        pct = root.attachNewNode(ptn)
        pct.setScale(g.PURITY_METER_PCT_SCALE)
        pct.setPos(0, 0, g.PURITY_METER_PCT_Z)
        self._pctNP = pct

        self._lastPopPurity = None

    def hide(self):
        self._clearPop()
        if self._root is not None and not self._root.isEmpty():
            self._root.removeNode()
        self._root = None
        self._rimNP = None
        self._trackNP = None
        self._fillNP = None
        self._labelNP = None
        self._pctNP = None
        self._purity = None
        self._lastPopPurity = None

    def destroy(self):
        self.hide()

    def update(self, pollution, finalePhase=0):
        """Refresh fill from pollution scalar (0 pure … 1 full)."""
        if not self.isShown():
            self.show()

        pollution = max(0.0, min(1.0, float(pollution)))
        purity = 1.0 - pollution
        prev = self._purity
        first = prev is None
        self._purity = purity

        fillColor = _lerpColor(
            ReclaimGlobals.PURITY_METER_FILL_POLLUTED,
            ReclaimGlobals.PURITY_METER_FILL_PURE,
            purity)

        # Finale streets lean magenta / crimson on the rim for boss readability.
        phase = int(finalePhase or 0)
        if phase >= 2:
            rimColor = ReclaimGlobals.PURITY_METER_RIM_FINALE_P2
        elif phase == 1:
            rimColor = ReclaimGlobals.PURITY_METER_RIM_FINALE_P1
        else:
            rimColor = ReclaimGlobals.PURITY_METER_RIM_COLOR

        if self._rimNP is not None and not self._rimNP.isEmpty():
            self._rimNP.setColor(*rimColor)

        if self._fillNP is not None and not self._fillNP.isEmpty():
            # Avoid zero scale (can cull oddly); clamp tiny.
            sx = max(0.001, purity)
            if not self._isPopPlaying():
                self._fillNP.setScale(sx, 1, 1)
            self._fillNP.setColor(*fillColor)

        if self._pctNP is not None and not self._pctNP.isEmpty():
            pctText = ReclaimGlobals.PURITY_METER_PCT_FMT % (purity * 100.0)
            node = self._pctNP.node()
            node.setText(pctText)
            node.setTextColor(*_lerpColor(
                ReclaimGlobals.PURITY_METER_PCT_POLLUTED,
                ReclaimGlobals.PURITY_METER_PCT_PURE,
                purity))

        # Soft rubber-hose pop when purity climbs (packs clearing ink).
        if (not first
                and purity > prev + ReclaimGlobals.PURITY_METER_POP_THRESHOLD):
            self._popFill()

    def _isPopPlaying(self):
        return self._popIval is not None and self._popIval.isPlaying()

    def _popFill(self):
        if self._fillNP is None or self._fillNP.isEmpty():
            return
        if (self._lastPopPurity is not None
                and abs(self._purity - self._lastPopPurity)
                < ReclaimGlobals.PURITY_METER_POP_THRESHOLD):
            return
        self._lastPopPurity = self._purity
        self._clearPop()
        sx = max(0.001, self._purity)
        peakZ = ReclaimGlobals.PURITY_METER_POP_SCALE_Z
        self._popIval = Sequence(
            LerpScaleInterval(
                self._fillNP,
                ReclaimGlobals.PURITY_METER_POP_SEC,
                (sx, 1, peakZ)),
            LerpScaleInterval(
                self._fillNP,
                ReclaimGlobals.PURITY_METER_POP_SEC * 1.2,
                (sx, 1, 1)),
            Func(self._onPopDone),
        )
        self._popIval.start()

    def _onPopDone(self):
        self._popIval = None

    def _clearPop(self):
        if self._popIval is not None:
            try:
                self._popIval.finish()
            except Exception:
                pass
            self._popIval = None
