"""Readable pollution→purity meter during street reclaim (aspect2d).

CardMaker bar + Oswald-flavored label — rubber-hose Toontown tone, no
Kingdom Hearts / keyblade branding. Driven by DistributedReclaimDirector.

On purity advances: short squash→stretch→settle fill pop, matching pct tick,
and sunny cream flecks at the fill tip.
"""

from math import cos, pi, sin

from panda3d.core import (
    CardMaker,
    Point3,
    TextNode,
    TransparencyAttrib,
    Vec4,
)

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
)

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
        self._pctPopIval = None
        self._fleckIval = None
        self._fleckNPs = []
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
        self._clearFlecks()
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
            if not self._isPctPopPlaying():
                self._pctNP.setScale(ReclaimGlobals.PURITY_METER_PCT_SCALE)

        # Rubber-hose tick/fill pop when purity climbs (packs clearing ink).
        if (not first
                and purity > prev + ReclaimGlobals.PURITY_METER_POP_THRESHOLD):
            self._popTick()

    def _isPopPlaying(self):
        return self._popIval is not None and self._popIval.isPlaying()

    def _isPctPopPlaying(self):
        return self._pctPopIval is not None and self._pctPopIval.isPlaying()

    def _popTick(self):
        """Short hose fill pop + pct tick + cream flecks at the advancing tip."""
        if self._fillNP is None or self._fillNP.isEmpty():
            return
        if (self._lastPopPurity is not None
                and abs(self._purity - self._lastPopPurity)
                < ReclaimGlobals.PURITY_METER_POP_THRESHOLD):
            return
        self._lastPopPurity = self._purity
        self._clearPop()
        self._popFillHose()
        self._popPctHose()
        self._spawnTickFlecks()

    def _popFillHose(self):
        """Fill bar: flat squash → tall stretch (brief X overshoot) → settle."""
        sx = max(0.001, float(self._purity))
        sqx, sqy, sqz, squashSec = ReclaimGlobals.PURITY_METER_POP_SQUASH
        stx, sty, stz, stretchSec = ReclaimGlobals.PURITY_METER_POP_STRETCH
        settleSec = float(ReclaimGlobals.PURITY_METER_POP_SETTLE_SEC)
        settle = Point3(sx, 1.0, 1.0)
        squash = Point3(sx * float(sqx), float(sqy), float(sqz))
        stretch = Point3(
            min(1.0, sx * float(stx)), float(sty), float(stz))
        try:
            self._fillNP.setScale(settle)
        except Exception:
            return
        self._popIval = Sequence(
            LerpScaleInterval(
                self._fillNP, float(squashSec), squash, blendType='easeOut'),
            LerpScaleInterval(
                self._fillNP, float(stretchSec), stretch, blendType='easeOut'),
            LerpScaleInterval(
                self._fillNP, settleSec, settle, blendType='easeIn'),
            Func(self._onPopDone),
            name='reclaimPurityMeterFillHose',
        )
        self._popIval.start()

    def _popPctHose(self):
        """Pct label: flat squash → tall stretch → settle at base scale."""
        if self._pctNP is None or self._pctNP.isEmpty():
            return
        settle = float(ReclaimGlobals.PURITY_METER_PCT_SCALE)
        sqx, sqy, sqz, squashSec = ReclaimGlobals.PURITY_METER_PCT_POP_SQUASH
        stx, sty, stz, stretchSec = ReclaimGlobals.PURITY_METER_PCT_POP_STRETCH
        settleSec = float(ReclaimGlobals.PURITY_METER_PCT_POP_SETTLE_SEC)
        settlePt = Point3(settle, settle, settle)
        squashPt = Point3(settle * sqx, settle * sqy, settle * sqz)
        stretchPt = Point3(settle * stx, settle * sty, settle * stz)
        try:
            self._pctNP.setScale(settlePt)
        except Exception:
            return
        self._pctPopIval = Sequence(
            LerpScaleInterval(
                self._pctNP, float(squashSec), squashPt, blendType='easeOut'),
            LerpScaleInterval(
                self._pctNP, float(stretchSec), stretchPt, blendType='easeOut'),
            LerpScaleInterval(
                self._pctNP, settleSec, settlePt, blendType='easeIn'),
            Func(self._onPctPopDone),
            name='reclaimPurityMeterPctHose',
        )
        self._pctPopIval.start()

    def _spawnTickFlecks(self):
        """Sunny cream flecks popping off the fill tip when purity ticks up."""
        self._clearFlecks()
        if self._root is None or self._root.isEmpty():
            return
        count = int(ReclaimGlobals.PURITY_METER_TICK_FLECK_COUNT)
        if count <= 0 or self._purity is None:
            return

        halfW = ReclaimGlobals.PURITY_METER_WIDTH * 0.5
        # Tip of the fill in root-local space (left edge + purity * width).
        tipX = -halfW + max(0.001, float(self._purity)) * ReclaimGlobals.PURITY_METER_WIDTH
        size = float(ReclaimGlobals.PURITY_METER_TICK_FLECK_SIZE)
        drift = float(ReclaimGlobals.PURITY_METER_TICK_FLECK_DRIFT)
        sec = float(ReclaimGlobals.PURITY_METER_TICK_FLECK_SEC)
        r, g, b, a = ReclaimGlobals.PURITY_METER_TICK_FLECK_COLOR
        er, eg, eb, ea = ReclaimGlobals.PURITY_METER_TICK_FLECK_END_COLOR
        fleckBin = int(ReclaimGlobals.PURITY_METER_TICK_FLECK_BIN)

        parts = []
        for i in range(count):
            try:
                cm = CardMaker('reclaim-purity-meter-tick-%s' % i)
                cm.setFrame(-size, size, -size, size)
                fleck = self._root.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, a)
                angle = (2.0 * pi * i) / float(count) + 0.35
                start = Point3(
                    tipX + cos(angle) * 0.012,
                    0,
                    sin(angle) * 0.018)
                fleck.setPos(start)
                fleck.setScale(0.5 + 0.1 * (i % 3))
                fleck.setBin('fixed', fleckBin)
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
            except Exception:
                continue

            end = Point3(
                start[0] + cos(angle) * drift * 0.85,
                0,
                start[2] + abs(sin(angle)) * drift + 0.03)
            parts.append(Parallel(
                LerpPosInterval(fleck, sec, end, blendType='easeOut'),
                LerpScaleInterval(fleck, sec, 0.04, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, sec, Vec4(er, eg, eb, ea), blendType='easeIn'),
            ))
            self._fleckNPs.append(fleck)

        if not parts:
            return
        self._fleckIval = Sequence(
            Parallel(*parts, name='reclaimPurityMeterTickFlecks'),
            Func(self._clearFlecks),
            name='reclaimPurityMeterTickFlecksSeq',
        )
        self._fleckIval.start()

    def _onPopDone(self):
        self._popIval = None
        # Snap fill to current purity in case another update arrived mid-pop.
        if (self._fillNP is not None and not self._fillNP.isEmpty()
                and self._purity is not None):
            try:
                self._fillNP.setScale(max(0.001, float(self._purity)), 1, 1)
            except Exception:
                pass

    def _onPctPopDone(self):
        self._pctPopIval = None
        if self._pctNP is not None and not self._pctNP.isEmpty():
            try:
                self._pctNP.setScale(ReclaimGlobals.PURITY_METER_PCT_SCALE)
            except Exception:
                pass

    def _clearPop(self):
        if self._popIval is not None:
            try:
                self._popIval.finish()
            except Exception:
                pass
            self._popIval = None
        if self._pctPopIval is not None:
            try:
                self._pctPopIval.finish()
            except Exception:
                pass
            self._pctPopIval = None

    def _clearFlecks(self):
        if self._fleckIval is not None:
            try:
                self._fleckIval.pause()
            except Exception:
                pass
            self._fleckIval = None
        for np in self._fleckNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []
