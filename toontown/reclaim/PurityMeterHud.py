"""Readable pollution→purity meter during street reclaim (aspect2d).

CardMaker bar + Oswald-flavored label — rubber-hose Toontown tone, no
Kingdom Hearts / keyblade branding. Driven by DistributedReclaimDirector.

On purity advances: short squash→stretch→settle fill pop, matching pct tick,
sunny cream flecks at the fill tip, StreetSparkle/EntryCream-style cream
shimmer flecks along the filled bar, then a delayed cream aftershock
(softer flecks settling downward + soft halo) — same residual grammar as
cheer cream aftershock — then a soft cream wash pulse (CheerCreamWashPulse /
WaveClearCreamWashPulse vocabulary).

Wave start (pack spawn): further-deepened sunny cream rim + whole-meter
squash→stretch hose-pop with richer rising cream flecks / soft halo past
#280 so wave begin reads juicier still — distinct from mid-wave warm
rim-flash cream (#213 / #234 / #275 / #302), wave-clear mid-screen sparkle
(#229 / #273 / #297), purity-complete hose settle (#225 / #266 / #292),
and secured-lock green hold (#209 / #261 / #286).

Purity complete (after celebration settles): further-deepened soft tall
stretch → longer settle on the full meter with richer settling pure-cream
flecks / soft halo so the finish reads juicier still (past #266) — not
wave-start squash→stretch + rising cream (#220 / #239 / #280), not
secured-lock green soft uniform scale + tip-near green-cream sparkle
(#209 / #243 / #261 / #286), and not mid-wave warm rim-flash / wave-clear
sparkle (#234 / #275 / #229 / #273).

Mid-wave purity pressure (director tip): further-deepened warm triple-pulse
contested rim flash + richer local cream flecks / soft halo past #275 when
purity stalls or ink pressure rises — rubber-hose urgency after re-creep #194
so danger reads juicier still (distinct from secured-lock #209 / #261 / #286,
wave-clear sparkle #229 / #273 / #297, complete hose settle #225 / #266 / #292,
wave-start sunny hose cream).
Full reclaim secured lock: brief cream/green rim confirm + juicier soft meter
hose-pop that purity is locked (pairs with deepened SecuredLockSparkleFx
green-cream flecks / aftershock / pitch sting — tip-near, not wave-clear
sparkle #229 / #273 / #297, rim-flash cream #234 / #275, or wave-start hose
#239).
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
        self._warnCreamNPs = []
        self._warnCreamHaloNP = None
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

    def popWaveStart(self):
        """Further-deepened sunny cream rim + hose pop when a wave starts.

        Squash→stretch→settle on the meter root with richer rising cream
        flecks / soft halo past #280 so pack-wave begin reads juicier
        still — not mid-wave warm rim-flash cream warn (#213 / #234 /
        #275 / #302), not wave-clear mid-screen sparkle (#229 / #273 /
        #297), not purity-complete hose settle (#225 / #266 / #292), and
        not secured-lock green hold + soft uniform scale (#209 / #261 /
        #286).
        """
        if not getattr(ReclaimGlobals, 'WAVE_START_METER_POP_ENABLED', True):
            return
        if self._root is None or self._root.isEmpty():
            return
        self._clearPressureWarn()
        rimColor = getattr(
            ReclaimGlobals, 'WAVE_START_METER_RIM_COLOR',
            (1.0, 0.98, 0.54, 0.98))
        rimSec = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_RIM_SEC', 0.40))
        if self._rimNP is not None and not self._rimNP.isEmpty():
            try:
                self._rimNP.setColor(*rimColor)
            except Exception:
                pass

        sqx, sqy, sqz, squashSec = getattr(
            ReclaimGlobals, 'WAVE_START_METER_POP_SQUASH',
            (0.74, 1.0, 0.38, 0.07))
        stx, sty, stz, stretchSec = getattr(
            ReclaimGlobals, 'WAVE_START_METER_POP_STRETCH',
            (1.18, 1.0, 1.54, 0.10))
        settleSec = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_POP_SETTLE_SEC', 0.20))
        try:
            baseScale = self._root.getScale()
            try:
                bx = float(baseScale[0])
                by = float(baseScale[1])
                bz = float(baseScale[2])
            except Exception:
                bx = by = bz = 1.0
        except Exception:
            bx = by = bz = 1.0
        settle = Point3(bx, by, bz)
        squash = Point3(
            bx * float(sqx), by * float(sqy), bz * float(sqz))
        stretch = Point3(
            bx * float(stx), by * float(sty), bz * float(stz))
        try:
            hose = Sequence(
                LerpScaleInterval(
                    self._root, max(0.01, float(squashSec)), squash,
                    blendType='easeOut'),
                LerpScaleInterval(
                    self._root, max(0.01, float(stretchSec)), stretch,
                    blendType='easeOut'),
                LerpScaleInterval(
                    self._root, max(0.01, settleSec), settle,
                    blendType='easeIn'),
                name='reclaimPurityMeterWaveStartHoseCore',
            )
        except Exception:
            return
        hoseDur = (
            max(0.01, float(squashSec))
            + max(0.01, float(stretchSec))
            + max(0.01, settleSec))
        holdAfter = max(0.01, rimSec - hoseDur)
        creamPart = self._buildWaveStartCreamJuice()
        if creamPart is not None:
            juice = Parallel(
                hose,
                creamPart,
                name='reclaimPurityMeterWaveStartJuice',
            )
        else:
            juice = hose
        self._warnIval = Sequence(
            juice,
            Wait(holdAfter),
            Func(self._onPressureWarnDone),
            name='reclaimPurityMeterWaveStartHose',
        )
        self._warnIval.start()

    def _buildWaveStartCreamJuice(self):
        """Sunny rising cream flecks + soft halo layered on wave-start hose."""
        if not getattr(
                ReclaimGlobals, 'WAVE_START_METER_CREAM_ENABLED', True):
            return None
        if self._root is None or self._root.isEmpty():
            return None
        self._clearWarnCream()

        parts = []
        haloPart = self._spawnWaveStartCreamHalo()
        if haloPart is not None:
            parts.append(haloPart)
        fleckParts = self._spawnWaveStartCreamFlecks()
        if fleckParts:
            parts.extend(fleckParts)
        if not parts:
            return None
        return Parallel(*parts, name='reclaimPurityMeterWaveStartCream')

    def _spawnWaveStartCreamHalo(self):
        """Richer sunny cream halo that blooms with the wave-start hose pop."""
        if not getattr(
                ReclaimGlobals, 'WAVE_START_METER_CREAM_HALO_ENABLED', True):
            return None
        if self._root is None or self._root.isEmpty():
            return None
        half = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_HALO_HALF', 0.098))
        start = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_HALO_START', 0.32))
        peak = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_HALO_PEAK', 1.52))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_HALO_SEC', 0.38))
        peakA = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_HALO_PEAK_ALPHA', 0.24))
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_HALO_COLOR',
            (1.0, 0.99, 0.70, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_BIN', 48))
        try:
            cm = CardMaker('reclaim-purity-meter-wave-start-halo')
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = self._root.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, 0)
            halo.setPos(0, 0, 0)
            halo.setScale(start)
            halo.setBin('fixed', binSort)
            halo.setDepthTest(False)
            halo.setDepthWrite(False)
        except Exception:
            return None
        self._warnCreamHaloNP = halo
        return Sequence(
            Parallel(
                LerpScaleInterval(
                    halo, max(0.01, sec * 0.45), peak, blendType='easeOut'),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.35),
                    Vec4(r, g, b, peakA), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(
                    halo, max(0.01, sec * 0.55), peak * 1.06,
                    blendType='easeIn'),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.55),
                    Vec4(r, g, b, 0.0), blendType='easeIn'),
            ),
            name='reclaimPurityMeterWaveStartHalo',
        )

    def _spawnWaveStartCreamFlecks(self):
        """Richer sunny cream chips rising off the meter on wave-start hose."""
        count = int(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_COUNT', 10))
        if count <= 0 or self._root is None or self._root.isEmpty():
            return []
        halfW = float(ReclaimGlobals.PURITY_METER_WIDTH) * 0.5
        halfH = float(ReclaimGlobals.PURITY_METER_HEIGHT) * 0.5
        size = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_SIZE', 0.017))
        rise = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_RISE', 0.18))
        spread = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_SPREAD', 0.30))
        sec = float(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_SEC', 0.42))
        r, g, b, a = getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_COLOR',
            (1.0, 0.99, 0.64, 0.98))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_END_COLOR',
            (1.0, 0.96, 0.46, 0.0))
        fleckBin = int(getattr(
            ReclaimGlobals, 'WAVE_START_METER_CREAM_BIN', 48))

        parts = []
        for i in range(count):
            try:
                cm = CardMaker('reclaim-purity-meter-wave-start-cream-%s' % i)
                # Alternate chip / streak so the sunny begin cream pops.
                if i % 2:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.25, size * 1.25)
                else:
                    cm.setFrame(-size, size, -size * 0.35, size * 0.35)
                fleck = self._root.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                # Fan along the bar top — rising begin pop, not radial warn burst.
                t = (float(i) / max(1.0, float(count - 1))) - 0.5
                start = Point3(t * halfW * 1.6, 0, halfH * 0.4)
                fleck.setPos(start)
                fleck.setScale(0.40 + 0.12 * (i % 3))
                fleck.setBin('fixed', fleckBin + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
            except Exception:
                continue

            end = Point3(
                start[0] + t * spread * 0.35,
                0,
                start[2] + rise * (0.75 + 0.08 * (i % 3)))
            peak = 1.20 + 0.10 * (i % 2)
            parts.append(Sequence(
                Parallel(
                    LerpColorScaleInterval(
                        fleck, 0.04, Vec4(r, g, b, a), blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec * 0.28), peak, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec * 0.72), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec * 0.72), 0.05, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec * 0.72),
                        Vec4(er, eg, eb, ea), blendType='easeIn'),
                ),
            ))
            self._warnCreamNPs.append(fleck)
        return parts

    def warnPressure(self):
        """Further-deepened warm triple-pulse contested rim flash + cream.

        Danger blink on the meter rim with richer local warm cream chips /
        soft halo past #275 so mid-wave pressure reads juicier still — not
        secured-lock green hold / whole-meter hose-pop (#209 / #261 / #286),
        not wave-start sunny hose (#220 / #239), not wave-clear mid-screen
        sparkle (#229 / #273 / #297), and not purity-complete hose settle
        (#225 / #266 / #292).
        """
        if not getattr(ReclaimGlobals, 'PURITY_PRESSURE_TIP_ENABLED', True):
            return
        if not getattr(ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_ENABLED', True):
            return
        if self._rimNP is None or self._rimNP.isEmpty():
            return
        self._clearPressureWarn()
        warnColor = getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_WARN_COLOR',
            (1.0, 0.70, 0.38, 1.0))
        pulses = max(1, int(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_PULSES', 3)))
        onSec = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_ON_SEC', 0.11))
        offSec = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_OFF_SEC', 0.04))
        holdSec = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_HOLD_SEC',
            getattr(ReclaimGlobals, 'PURITY_PRESSURE_RIM_WARN_SEC', 0.24)))
        scalePeak = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_SCALE', 1.40))

        parts = []
        for i in range(pulses):
            peakSec = holdSec if i == pulses - 1 else onSec
            parts.append(self._buildRimWarnPulse(warnColor, peakSec, scalePeak))
            if i < pulses - 1:
                parts.append(Func(self._applyRimColor))
                parts.append(Wait(max(0.01, offSec)))
        creamPart = self._buildRimWarnCreamJuice()
        if creamPart is not None:
            flashCore = Sequence(*parts, name='reclaimPurityMeterPressureFlash')
            self._warnIval = Sequence(
                Parallel(
                    flashCore,
                    creamPart,
                    name='reclaimPurityMeterPressureWarnJuice'),
                Func(self._onPressureWarnDone),
                name='reclaimPurityMeterPressureWarn',
            )
        else:
            parts.append(Func(self._onPressureWarnDone))
            self._warnIval = Sequence(
                *parts,
                name='reclaimPurityMeterPressureWarn',
            )
        self._warnIval.start()

    def _buildRimWarnPulse(self, warnColor, peakSec, scalePeak):
        """One warn on-beat: snap warn color + soft rim-only scale nudge."""
        peakSec = max(0.05, float(peakSec))
        scalePeak = max(1.0, float(scalePeak))
        colorBeat = Sequence(
            Func(self._setRimWarnColor, warnColor),
            Wait(peakSec),
        )
        if scalePeak <= 1.001:
            return colorBeat
        try:
            scaleBeat = Sequence(
                LerpScaleInterval(
                    self._rimNP, max(0.01, peakSec * 0.42),
                    Point3(scalePeak, 1.0, scalePeak),
                    blendType='easeOut'),
                LerpScaleInterval(
                    self._rimNP, max(0.01, peakSec * 0.58),
                    Point3(1.0, 1.0, 1.0),
                    blendType='easeIn'),
            )
        except Exception:
            return colorBeat
        return Parallel(colorBeat, scaleBeat)

    def _buildRimWarnCreamJuice(self):
        """Warm cream flecks + soft halo layered on the rim flash."""
        if not getattr(
                ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_ENABLED', True):
            return None
        if self._root is None or self._root.isEmpty():
            return None
        self._clearWarnCream()

        parts = []
        haloPart = self._spawnRimWarnCreamHalo()
        if haloPart is not None:
            parts.append(haloPart)
        fleckParts = self._spawnRimWarnCreamFlecks()
        if fleckParts:
            parts.extend(fleckParts)
        if not parts:
            return None
        return Parallel(*parts, name='reclaimPurityMeterPressureCream')

    def _spawnRimWarnCreamHalo(self):
        """Soft warm cream halo that blooms with the rim flash."""
        if not getattr(
                ReclaimGlobals,
                'PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_ENABLED', True):
            return None
        if self._root is None or self._root.isEmpty():
            return None
        half = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_HALF', 0.096))
        start = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_START', 0.34))
        peak = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_PEAK', 1.48))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_SEC', 0.36))
        peakA = float(getattr(
            ReclaimGlobals,
            'PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_PEAK_ALPHA', 0.26))
        r, g, b, a = getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_HALO_COLOR',
            (1.0, 0.96, 0.76, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_BIN', 48))
        try:
            cm = CardMaker('reclaim-purity-meter-pressure-halo')
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = self._root.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, 0)
            halo.setPos(0, 0, 0)
            halo.setScale(start)
            halo.setBin('fixed', binSort)
            halo.setDepthTest(False)
            halo.setDepthWrite(False)
        except Exception:
            return None
        self._warnCreamHaloNP = halo
        return Sequence(
            Parallel(
                LerpScaleInterval(
                    halo, max(0.01, sec * 0.45), peak, blendType='easeOut'),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.35),
                    Vec4(r, g, b, peakA), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(
                    halo, max(0.01, sec * 0.55), peak * 1.08,
                    blendType='easeIn'),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.55),
                    Vec4(r, g, b, 0.0), blendType='easeIn'),
            ),
            name='reclaimPurityMeterPressureHalo',
        )

    def _spawnRimWarnCreamFlecks(self):
        """Warm cream chips that burst off the meter rim during pressure flash."""
        count = int(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_COUNT', 9))
        if count <= 0 or self._root is None or self._root.isEmpty():
            return []
        halfW = float(ReclaimGlobals.PURITY_METER_WIDTH) * 0.5
        halfH = float(ReclaimGlobals.PURITY_METER_HEIGHT) * 0.5
        pad = float(ReclaimGlobals.PURITY_METER_RIM_PAD)
        size = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_SIZE', 0.016))
        drift = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_DRIFT', 0.16))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_SEC', 0.40))
        r, g, b, a = getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_COLOR',
            (1.0, 0.97, 0.72, 1.0))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_END_COLOR',
            (1.0, 0.92, 0.52, 0.0))
        fleckBin = int(getattr(
            ReclaimGlobals, 'PURITY_PRESSURE_RIM_FLASH_CREAM_BIN', 48))

        parts = []
        for i in range(count):
            try:
                cm = CardMaker('reclaim-purity-meter-pressure-cream-%s' % i)
                # Alternate chip / streak so the warn cream pops.
                if i % 2:
                    cm.setFrame(-size * 1.35, size * 1.35, -size * 0.45, size * 0.45)
                else:
                    cm.setFrame(-size, size, -size, size)
                fleck = self._root.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                angle = (2.0 * pi * i) / float(count) + 0.22
                # Start along the outer rim edge (not mid-screen sparkle origin).
                start = Point3(
                    cos(angle) * (halfW + pad * 0.6),
                    0,
                    sin(angle) * (halfH + pad * 0.8))
                fleck.setPos(start)
                fleck.setScale(0.45 + 0.1 * (i % 3))
                fleck.setBin('fixed', fleckBin + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
            except Exception:
                continue

            end = Point3(
                start[0] + cos(angle) * drift,
                0,
                start[2] + sin(angle) * drift * 0.85 + 0.02)
            peak = 1.15 + 0.08 * (i % 2)
            parts.append(Sequence(
                Parallel(
                    LerpColorScaleInterval(
                        fleck, 0.04, Vec4(r, g, b, a), blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec * 0.30), peak, blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec * 0.70), end, blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec * 0.70), 0.05, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec * 0.70),
                        Vec4(er, eg, eb, ea), blendType='easeIn'),
                ),
            ))
            self._warnCreamNPs.append(fleck)
        return parts

    def _setRimWarnColor(self, color):
        if self._rimNP is None or self._rimNP.isEmpty():
            return
        try:
            self._rimNP.setColor(*color)
        except Exception:
            pass

    def _resetRimScale(self):
        if self._rimNP is None or self._rimNP.isEmpty():
            return
        try:
            self._rimNP.setScale(1.0, 1.0, 1.0)
        except Exception:
            pass

    def _resetRootScale(self):
        if self._root is None or self._root.isEmpty():
            return
        try:
            self._root.setScale(1.0, 1.0, 1.0)
        except Exception:
            pass

    def settleComplete(self):
        """Further-deepened soft tall stretch → settle after purity celebration.

        Finish-read hose on the full meter with richer settling pure-cream
        flecks / soft halo so reclaim finish reads juicier still (past #266)
        — not wave-start squash→stretch + rising cream (#220 / #239 / #280)
        and not secured-lock green soft uniform scale + tip-near green-cream
        sparkle (#209 / #243 / #261 / #286).
        """
        if not getattr(
                ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_ENABLED', True):
            return
        if self._root is None or self._root.isEmpty():
            return
        self._clearPressureWarn()
        rimColor = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_RIM_COLOR',
            (1.0, 0.99, 0.80, 0.98))
        rimSec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_RIM_SEC', 0.48))
        if self._rimNP is not None and not self._rimNP.isEmpty():
            try:
                self._rimNP.setColor(*rimColor)
            except Exception:
                pass

        stx, sty, stz, stretchSec = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_STRETCH',
            (1.12, 1.0, 1.40, 0.11))
        settleSec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_SEC', 0.28))
        try:
            baseScale = self._root.getScale()
            try:
                bx = float(baseScale[0])
                by = float(baseScale[1])
                bz = float(baseScale[2])
            except Exception:
                bx = by = bz = 1.0
        except Exception:
            bx = by = bz = 1.0
        settle = Point3(bx, by, bz)
        stretch = Point3(
            bx * float(stx), by * float(sty), bz * float(stz))
        try:
            hose = Sequence(
                LerpScaleInterval(
                    self._root, max(0.01, float(stretchSec)), stretch,
                    blendType='easeOut'),
                LerpScaleInterval(
                    self._root, max(0.01, settleSec), settle,
                    blendType='easeIn'),
                name='reclaimPurityMeterCompleteSettleHoseCore',
            )
        except Exception:
            return
        hoseDur = (
            max(0.01, float(stretchSec))
            + max(0.01, settleSec))
        holdAfter = max(0.01, rimSec - hoseDur)
        creamPart = self._buildCompleteSettleCreamJuice()
        if creamPart is not None:
            juice = Parallel(
                hose,
                creamPart,
                name='reclaimPurityMeterCompleteSettleJuice',
            )
        else:
            juice = hose
        self._warnIval = Sequence(
            juice,
            Wait(holdAfter),
            Func(self._onPressureWarnDone),
            name='reclaimPurityMeterCompleteSettle',
        )
        self._warnIval.start()

    def _buildCompleteSettleCreamJuice(self):
        """Richer settling pure-cream flecks + soft halo on complete hose."""
        if not getattr(
                ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_ENABLED',
                True):
            return None
        if self._root is None or self._root.isEmpty():
            return None
        self._clearWarnCream()

        parts = []
        haloPart = self._spawnCompleteSettleCreamHalo()
        if haloPart is not None:
            parts.append(haloPart)
        fleckParts = self._spawnCompleteSettleCreamFlecks()
        if fleckParts:
            parts.extend(fleckParts)
        if not parts:
            return None
        return Parallel(*parts, name='reclaimPurityMeterCompleteSettleCream')

    def _spawnCompleteSettleCreamHalo(self):
        """Softer-bloom pure-cream halo with the complete hose settle."""
        if not getattr(
                ReclaimGlobals,
                'PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_ENABLED', True):
            return None
        if self._root is None or self._root.isEmpty():
            return None
        half = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_HALF',
            0.102))
        start = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_START',
            0.34))
        peak = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_PEAK',
            1.48))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_SEC',
            0.38))
        peakA = float(getattr(
            ReclaimGlobals,
            'PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_PEAK_ALPHA', 0.21))
        r, g, b, a = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_HALO_COLOR',
            (1.0, 0.99, 0.84, 1.0))
        binSort = int(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_BIN', 48))
        try:
            cm = CardMaker('reclaim-purity-meter-complete-settle-halo')
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = self._root.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, 0)
            halo.setPos(0, 0, 0)
            halo.setScale(start)
            halo.setBin('fixed', binSort)
            halo.setDepthTest(False)
            halo.setDepthWrite(False)
        except Exception:
            return None
        self._warnCreamHaloNP = halo
        return Sequence(
            Parallel(
                LerpScaleInterval(
                    halo, max(0.01, sec * 0.45), peak, blendType='easeOut'),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.35),
                    Vec4(r, g, b, peakA), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(
                    halo, max(0.01, sec * 0.55), peak * 1.05,
                    blendType='easeIn'),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.55),
                    Vec4(r, g, b, 0.0), blendType='easeIn'),
            ),
            name='reclaimPurityMeterCompleteSettleHalo',
        )

    def _spawnCompleteSettleCreamFlecks(self):
        """Richer pure-cream chips that settle downward on complete hose."""
        count = int(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_COUNT', 10))
        if count <= 0 or self._root is None or self._root.isEmpty():
            return []
        halfW = float(ReclaimGlobals.PURITY_METER_WIDTH) * 0.5
        halfH = float(ReclaimGlobals.PURITY_METER_HEIGHT) * 0.5
        size = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_SIZE', 0.018))
        fall = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_FALL', 0.17))
        spread = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_SPREAD', 0.28))
        sec = float(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_SEC', 0.40))
        r, g, b, a = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_COLOR',
            (1.0, 0.99, 0.80, 0.98))
        er, eg, eb, ea = getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_END_COLOR',
            (1.0, 0.96, 0.62, 0.0))
        fleckBin = int(getattr(
            ReclaimGlobals, 'PURITY_COMPLETE_METER_SETTLE_CREAM_BIN', 48))

        parts = []
        for i in range(count):
            try:
                cm = CardMaker(
                    'reclaim-purity-meter-complete-settle-cream-%s' % i)
                # Alternate chip / streak — quieter residual of finish cream.
                if i % 2:
                    cm.setFrame(
                        -size * 0.35, size * 0.35, -size * 1.20, size * 1.20)
                else:
                    cm.setFrame(-size, size, -size * 0.85, size * 0.85)
                fleck = self._root.attachNewNode(cm.generate())
                fleck.setTransparency(TransparencyAttrib.MAlpha)
                fleck.setColor(r, g, b, 1)
                fleck.setColorScale(r, g, b, 0)
                # Fan along the bar — settle downward, not rising wave-start.
                t = (float(i) / max(1.0, float(count - 1))) - 0.5
                start = Point3(t * halfW * 1.5, 0, halfH * 0.55)
                fleck.setPos(start)
                fleck.setScale(0.38 + 0.10 * (i % 3))
                fleck.setBin('fixed', fleckBin + (i % 2))
                fleck.setDepthTest(False)
                fleck.setDepthWrite(False)
            except Exception:
                continue

            end = Point3(
                start[0] + t * spread * 0.40,
                0,
                start[2] - fall * (0.70 + 0.10 * (i % 3)))
            peak = 1.12 + 0.08 * (i % 2)
            stagger = 0.014 * (i % 3)
            parts.append(Sequence(
                Wait(stagger),
                Parallel(
                    LerpColorScaleInterval(
                        fleck, 0.045, Vec4(r, g, b, a), blendType='easeOut'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec * 0.28), peak,
                        blendType='easeOut'),
                ),
                Parallel(
                    LerpPosInterval(
                        fleck, max(0.01, sec * 0.72), end, blendType='easeIn'),
                    LerpScaleInterval(
                        fleck, max(0.01, sec * 0.72), 0.05, blendType='easeIn'),
                    LerpColorScaleInterval(
                        fleck, max(0.01, sec * 0.72),
                        Vec4(er, eg, eb, ea), blendType='easeIn'),
                ),
            ))
            self._warnCreamNPs.append(fleck)
        return parts

    def confirmSecured(self):
        """Brief cream/green rim + juicier soft uniform meter pop on lock.

        Soft ease scale (not squash→stretch wave-start hose #239, not warm
        rim-flash cream #234, not complete settle stretch→settle) + green
        rim hold — pairs with deepened tip-near green-cream sparkle sting.
        """
        if not getattr(ReclaimGlobals, 'SECURED_LOCK_TIP_ENABLED', True):
            return
        if self._rimNP is None or self._rimNP.isEmpty():
            return
        self._clearPressureWarn()
        lockColor = getattr(
            ReclaimGlobals, 'SECURED_LOCK_RIM_COLOR',
            (0.55, 1.0, 0.72, 0.88))
        hold = float(getattr(ReclaimGlobals, 'SECURED_LOCK_RIM_SEC', 0.85))
        try:
            self._rimNP.setColor(*lockColor)
        except Exception:
            return
        # Soft meter hose-pop — HUD sting cousin of the secured tip pop.
        popParts = []
        if self._root is not None and not self._root.isEmpty():
            popScale = float(getattr(
                ReclaimGlobals, 'SECURED_LOCK_METER_POP_SCALE', 1.20))
            popSec = float(getattr(
                ReclaimGlobals, 'SECURED_LOCK_METER_POP_SEC', 0.12))
            try:
                baseScale = self._root.getScale()
                try:
                    bx = float(baseScale[0])
                    by = float(baseScale[1])
                    bz = float(baseScale[2])
                except Exception:
                    bx = by = bz = 1.0
                popParts.append(Sequence(
                    LerpScaleInterval(
                        self._root, max(0.01, popSec),
                        Point3(bx * popScale, by * popScale, bz * popScale),
                        blendType='easeOut'),
                    LerpScaleInterval(
                        self._root, 0.14,
                        Point3(bx, by, bz),
                        blendType='easeInOut'),
                ))
            except Exception:
                popParts = []
        body = Parallel(*popParts) if popParts else Wait(0.01)
        self._warnIval = Sequence(
            body,
            Wait(max(0.05, hold)),
            Func(self._onPressureWarnDone),
            name='reclaimPurityMeterSecuredConfirm',
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
        self._clearWarnCream()
        self._resetRimScale()
        self._resetRootScale()
        self._applyRimColor()

    def _clearPressureWarn(self):
        if self._warnIval is not None:
            try:
                self._warnIval.finish()
            except Exception:
                pass
            self._warnIval = None
        self._clearWarnCream()
        self._resetRimScale()
        self._resetRootScale()
        self._applyRimColor()

    def _clearWarnCream(self):
        """Remove rim-flash cream flecks / halo without touching fill shimmer."""
        if self._warnCreamHaloNP is not None:
            try:
                if not self._warnCreamHaloNP.isEmpty():
                    self._warnCreamHaloNP.removeNode()
            except Exception:
                pass
            self._warnCreamHaloNP = None
        for np in self._warnCreamNPs:
            if np is not None and not np.isEmpty():
                try:
                    np.removeNode()
                except Exception:
                    pass
        self._warnCreamNPs = []

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
