"""Readable pollution→purity meter during street reclaim (aspect2d).

CardMaker bar + Oswald-flavored label — rubber-hose Toontown tone, no
Kingdom Hearts / keyblade branding. Driven by DistributedReclaimDirector.

On purity advances: short squash→stretch→settle fill pop, matching pct tick,
sunny cream flecks at the fill tip, StreetSparkle/EntryCream-style cream
shimmer flecks along the filled bar, then a delayed cream aftershock
(softer flecks settling downward + soft halo) — same residual grammar as
cheer cream aftershock — then a soft cream wash pulse (CheerCreamWashPulse /
WaveClearCreamWashPulse vocabulary).

Mid-wave purity pressure (director tip): brief contested rim warn flash when
purity stalls or ink pressure rises — rubber-hose urgency after re-creep #194.
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
    Wait,
)

from toontown.reclaim import ReclaimGlobals
from toontown.reclaim.PurityFillCreamWashFx import PurityFillCreamWashPulse


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
        self._shimmerIval = None
        self._shimmerNPs = []
        self._shimmerPlayIval = None
        self._haloNP = None
        self._creamWash = None
        self._lastPopPurity = None
        self._warnIval = None
        self._finalePhase = 0

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
        self._clearFillShimmer()
        self._clearPressureWarn()
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
        self._finalePhase = 0

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
        self._finalePhase = int(finalePhase or 0)

        fillColor = _lerpColor(
            ReclaimGlobals.PURITY_METER_FILL_POLLUTED,
            ReclaimGlobals.PURITY_METER_FILL_PURE,
            purity)

        # Skip rim snap while contested pressure warn is playing.
        if not self._isPressureWarnPlaying():
            self._applyRimColor()

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

    def warnPressure(self):
        """Brief contested rim flash when mid-wave purity pressure whispers."""
        if not getattr(ReclaimGlobals, 'PURITY_PRESSURE_TIP_ENABLED', True):
            return
        if self._rimNP is None or self._rimNP.isEmpty():
            return
        self._clearPressureWarn()
        warnColor = getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_WARN_COLOR',
            (1.0, 0.55, 0.35, 0.78))
        hold = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_WARN_SEC', 0.55))
        try:
            self._rimNP.setColor(*warnColor)
        except Exception:
            return
        self._warnIval = Sequence(
            Wait(max(0.05, hold)),
            Func(self._onPressureWarnDone),
            name='reclaimPurityMeterPressureWarn',
        )
        self._warnIval.start()

    def _baseRimColor(self):
        phase = int(self._finalePhase or 0)
        if phase >= 2:
            return ReclaimGlobals.PURITY_METER_RIM_FINALE_P2
        if phase == 1:
            return ReclaimGlobals.PURITY_METER_RIM_FINALE_P1
        return ReclaimGlobals.PURITY_METER_RIM_COLOR

    def _applyRimColor(self):
        if self._rimNP is None or self._rimNP.isEmpty():
            return
        try:
            self._rimNP.setColor(*self._baseRimColor())
        except Exception:
            pass

    def _isPressureWarnPlaying(self):
        return self._warnIval is not None and self._warnIval.isPlaying()

    def _onPressureWarnDone(self):
        self._warnIval = None
        self._applyRimColor()

    def _clearPressureWarn(self):
        if self._warnIval is not None:
            try:
                self._warnIval.finish()
            except Exception:
                pass
            self._warnIval = None
        self._applyRimColor()

    def _isPopPlaying(self):
        return self._popIval is not None and self._popIval.isPlaying()

    def _isPctPopPlaying(self):
        return self._pctPopIval is not None and self._pctPopIval.isPlaying()

    def _popTick(self):
        """Hose fill pop + pct tick + tip flecks + cream shimmer + aftershock + wash."""
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
        self._spawnFillShimmerFlecks()

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

    def _spawnFillShimmerFlecks(self):
        """Cream shimmer along fill + aftershock + delayed cream wash."""
        self._clearFillShimmer()
        if not getattr(ReclaimGlobals, 'PURITY_METER_FILL_SHIMMER_ENABLED', True):
            return
        if self._root is None or self._root.isEmpty() or self._purity is None:
            return
        count = int(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_SHIMMER_COUNT', 7))
        if count <= 0:
            return

        purity = max(0.001, float(self._purity))
        halfW = ReclaimGlobals.PURITY_METER_WIDTH * 0.5
        fillW = purity * ReclaimGlobals.PURITY_METER_WIDTH
        size = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_SHIMMER_SIZE', 0.011))
        rise = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_SHIMMER_RISE', 0.055))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_SHIMMER_SEC', 0.28))
        r, g, b, a = getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_SHIMMER_COLOR',
            (1.0, 0.98, 0.72, 0.92))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_SHIMMER_END_COLOR',
            (1.0, 0.94, 0.55, 0.0))
        fleckBin = int(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_SHIMMER_BIN', 49))

        parts = []
        for i in range(count):
            try:
                # Spread along the filled span (left edge → tip).
                t = float(i) / float(max(1, count - 1))
                angle = (2.0 * pi * i) / float(count) + 0.28
                cm = CardMaker('reclaim-purity-meter-fill-shimmer-%s' % i)
                # Alternate chip / cross fleck — rubber-hose cream glitter.
                if (i % 3) == 0:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.25, size * 1.25)
                elif (i % 3) == 1:
                    cm.setFrame(
                        -size * 1.25, size * 1.25, -size * 0.35, size * 0.35)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = self._root.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                startX = -halfW + t * fillW + cos(angle) * 0.008
                startZ = sin(angle) * 0.012 + 0.006 * (i % 3)
                fleck.setPos(startX, 0, startZ)
                fleck.setScale(0.4 + 0.08 * (i % 3))
                fleck.setBin('fixed', fleckBin + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
            except Exception:
                continue

            end = Point3(
                startX + cos(angle) * 0.02,
                0,
                startZ + rise * (0.55 + 0.45 * ((i % 4) / 3.0)))
            delay = 0.016 * i
            twinkle = 0.04 + 0.01 * (i % 3)
            parts.append(Sequence(
                Wait(delay),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, twinkle, Vec4(r, g, b, a),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, twinkle, 1.1, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec), 0.05, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec), Vec4(er, eg, eb, ea),
                        blendType='easeIn'),
                ),
            ))
            self._shimmerNPs.append(fleck)

        if not parts:
            return

        # Shimmer Parallel starts immediately; aftershock + wash ride beside it.
        shimmerIval = Parallel(*parts, name='reclaimPurityMeterFillShimmer')
        self._shimmerPlayIval = shimmerIval
        try:
            shimmerIval.start()
        except Exception:
            self._clearFillShimmer()
            return

        aftershock = self._buildFillAftershock(halfW, fillW)
        if aftershock is not None:
            # Shimmer Parallel already started; hold its lifetime beside aftershock.
            burst = Parallel(
                Wait(sec + 0.04),
                aftershock,
            )
        else:
            burst = Wait(sec + 0.04)

        # Soft cream wash pulse after cream aftershock — cheer / wave-clear grammar.
        washHold = 0.0
        try:
            wash = PurityFillCreamWashPulse()
            if wash.play() is not None:
                self._creamWash = wash
                # Hold teardown beside delayed wash so clear() doesn't
                # kill the veil mid-pulse (wash self-clears too).
                washHold = (
                    float(getattr(
                        ReclaimGlobals,
                        'PURITY_METER_FILL_CREAM_WASH_DELAY_SEC', 0.40))
                    + float(getattr(
                        ReclaimGlobals,
                        'PURITY_METER_FILL_CREAM_WASH_IN_SEC', 0.05))
                    + float(getattr(
                        ReclaimGlobals,
                        'PURITY_METER_FILL_CREAM_WASH_PULSE_SEC', 0.09))
                    + float(getattr(
                        ReclaimGlobals,
                        'PURITY_METER_FILL_CREAM_WASH_HOLD_SEC', 0.06))
                    + float(getattr(
                        ReclaimGlobals,
                        'PURITY_METER_FILL_CREAM_WASH_OUT_SEC', 0.34))
                    + 0.02)
            else:
                self._creamWash = None
        except Exception:
            self._creamWash = None

        hold = [burst]
        if washHold > 0.0:
            hold.append(Wait(washHold))

        self._shimmerIval = Sequence(
            Parallel(*hold),
            Func(self._clearFillShimmer),
            name='reclaimPurityMeterFillShimmerSeq',
        )
        self._shimmerIval.start()

    def _buildFillAftershock(self, halfW, fillW):
        """Delayed soft cream flecks (+ optional halo) after fill shimmer."""
        if not getattr(ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_ENABLED', True):
            return None
        if self._root is None or self._root.isEmpty():
            return None
        delay = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_DELAY_SEC', 0.18))
        parts = []

        # Soft cream halo centered on the filled span midpoint.
        midX = -halfW + fillW * 0.5
        if getattr(ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnFillAftershockHalo(midX)
            if halo is not None:
                parts.append(halo)

        count = int(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_COUNT', 4))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_SEC', 0.32))
        for i in range(count):
            part = self._spawnFillAftershockFleck(halfW, fillW, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnFillAftershockHalo(self, midX):
        half = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_HALO_HALF', 0.055))
        startScale = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_HALO_START', 0.35))
        peakScale = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_HALO_PEAK', 1.35))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_HALO_SEC', 0.26))
        peakA = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_HALO_PEAK_ALPHA', 0.16))
        r, g, b, _a = getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_BIN', 50))
        try:
            cm = CardMaker('reclaim-purity-meter-fill-aftershock-halo')
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = self._root.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(midX, 0, 0)
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

    def _spawnFillAftershockFleck(self, halfW, fillW, index, total, sec):
        """Softer cream chip that settles downward along the filled span."""
        count = max(1, int(total))
        size = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_SIZE', 0.009))
        drift = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_DRIFT', 0.045))
        fall = float(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_FALL', 0.04))
        r, g, b, a = getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_COLOR',
            (1.0, 0.97, 0.78, 0.82))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_END_COLOR',
            (1.0, 0.93, 0.58, 0.0))
        binSort = int(getattr(
            ReclaimGlobals, 'PURITY_METER_FILL_AFTERSHOCK_BIN', 50))
        # Spread residual flecks along the filled span (left → tip).
        t = float(index) / float(max(1, count - 1))
        angle = (2.0 * pi * index) / float(count) + 0.35
        try:
            cm = CardMaker('reclaim-purity-meter-fill-aftershock-%s' % index)
            # Alternate chip / cross — quieter residual of the shimmer glitter.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.20, size * 1.20, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = self._root.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            startX = -halfW + t * fillW + cos(angle) * 0.006
            startZ = 0.008 * (index % 3)
            fleck.setPos(startX, 0, startZ)
            fleck.setScale(0.28 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Settle downward — residual cream, not the shimmer's outward rise.
        end = Point3(
            startX + cos(angle) * drift * 0.55,
            0,
            startZ - fall - 0.01 * (index % 3))
        peak = 1.05 + 0.08 * (index % 2)
        self._shimmerNPs.append(fleck)
        stagger = 0.018 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.28), peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(
                    fleck, max(0.01, sec * 0.72), end, blendType='easeIn'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.72), 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.72), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

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

    def _clearFillShimmer(self):
        """Stop fill shimmer/aftershock/wash and remove every cream fill node."""
        if self._shimmerIval is not None:
            try:
                self._shimmerIval.pause()
            except Exception:
                pass
            self._shimmerIval = None
        if self._shimmerPlayIval is not None:
            try:
                self._shimmerPlayIval.pause()
            except Exception:
                pass
            self._shimmerPlayIval = None
        wash = self._creamWash
        self._creamWash = None
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in self._shimmerNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._shimmerNPs = []
