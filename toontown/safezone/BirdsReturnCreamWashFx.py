"""Rubber-hose cream wash when TTC playground pollution clears / birds return.

Fullscreen soft cream veil that settles when reclaim-street pollution drops
to pure on the Toontown Central hub (or purityRestoreFx fires while the
hub breadcrumbs are live) — same PerfectDodgeCreamWashPulse /
PunchlineTipCreamWashPulse / CheerCreamWashPulse overlay grammar as a brief
explore settle beat. Pairs with PollutionStreetAudio pure-street birds
return (#55) so the neighborhood feeling clean reads juicily.

Cream deepen past #262: brighter peak → longer mid hold on the veil,
then denser rising cream chirp flecks + stronger skyward halo residual
(not crumb pip blot #241, not fog edge rim #236, not the original
veil-only wash #226, not #246/#262 alone). Soft under HUD; cream /
pastel only (not ink). Client only. Safezone package — Toontown
spiritual sequel (no KH props, names, or branding).
"""

from __future__ import annotations

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

# Tunables live here (safezone-only scope — do not edit CorruptionGlobals).
BIRDS_RETURN_CREAM_WASH_ENABLED = True
# Land during pure-street birds fade-in (#55 FADE_IN_SEC ≈ 0.55).
BIRDS_RETURN_CREAM_WASH_DELAY_SEC = 0.42
# Cream deepen past #262: brighter peak + longer mid linger than #226/#246/#262.
BIRDS_RETURN_CREAM_WASH_PEAK = 0.16
BIRDS_RETURN_CREAM_WASH_MID = 0.095
BIRDS_RETURN_CREAM_WASH_IN_SEC = 0.09
BIRDS_RETURN_CREAM_WASH_PULSE_SEC = 0.16
BIRDS_RETURN_CREAM_WASH_HOLD_SEC = 0.20
BIRDS_RETURN_CREAM_WASH_OUT_SEC = 0.50
BIRDS_RETURN_CREAM_WASH_BIN = 46
BIRDS_RETURN_CREAM_WASH_COLOR = (1.0, 0.98, 0.82)
# Collapse pollutionChanged + purityRestoreFx double-fires (birds debounce ≈ 2.5).
BIRDS_RETURN_CREAM_WASH_DEBOUNCE_SEC = 2.2
# Match PollutionStreetAudio polluted→pure flip threshold when readable.
BIRDS_RETURN_CREAM_WASH_AUDIO_THRESHOLD = 0.05

# Rising cream chirp residual — denser birds-return deepen past #262.
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_ENABLED = True
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_DELAY_SEC = 0.13
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_COUNT = 7
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SEC = 0.42
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SIZE = 0.018
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_RISE = 0.42  # upward chirp — not fall
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SPREAD = 0.64
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_ORIGIN = (0.0, 0.0, 0.10)
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_COLOR = (1.0, 0.98, 0.78, 0.92)
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_END_COLOR = (1.0, 0.94, 0.58, 0.0)
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_BIN = 47
# Soft skyward halo — stronger than #262; not crumb pip (#241) / fog rim (#236).
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_ENABLED = True
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_HALF = 0.50
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_START = 0.26
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_PEAK = 1.26  # not pip 1.48 / rim 1.22 / #262 1.18
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_SEC = 0.30
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA = 0.145
BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_COLOR = (1.0, 0.98, 0.84, 1.0)


def birdsReturnCreamWashParams():
    """Pure timing / alpha for birds-return cream wash deepen past #262.

    Headless-safe — no Panda geom. Distinct from placemarker (#230) /
    crumb (#241) local cream mid+pip, fog edge cream rim (#236), the
    original veil-only birds wash (#226), first deepen (#246), and
    second deepen (#262).
    """
    return {
        'enabled': bool(BIRDS_RETURN_CREAM_WASH_ENABLED),
        'delaySec': float(BIRDS_RETURN_CREAM_WASH_DELAY_SEC),
        'peak': float(BIRDS_RETURN_CREAM_WASH_PEAK),
        'mid': float(BIRDS_RETURN_CREAM_WASH_MID),
        'inSec': float(BIRDS_RETURN_CREAM_WASH_IN_SEC),
        'pulseSec': float(BIRDS_RETURN_CREAM_WASH_PULSE_SEC),
        'holdSec': float(BIRDS_RETURN_CREAM_WASH_HOLD_SEC),
        'outSec': float(BIRDS_RETURN_CREAM_WASH_OUT_SEC),
        'bin': int(BIRDS_RETURN_CREAM_WASH_BIN),
        'debounceSec': float(BIRDS_RETURN_CREAM_WASH_DEBOUNCE_SEC),
        'audioThreshold': float(BIRDS_RETURN_CREAM_WASH_AUDIO_THRESHOLD),
        'color': tuple(BIRDS_RETURN_CREAM_WASH_COLOR),
        'aftershockEnabled': bool(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_ENABLED),
        'aftershockDelaySec': float(
            BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_DELAY_SEC),
        'aftershockCount': int(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_COUNT),
        'aftershockSec': float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SEC),
        'aftershockRise': float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_RISE),
        'aftershockSpread': float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SPREAD),
        'aftershockHaloPeak': float(
            BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_PEAK),
        'aftershockHaloSec': float(
            BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_SEC),
        'aftershockHaloPeakAlpha': float(
            BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA),
    }


def shouldPlayBirdsReturnCreamWash(prevLevel, newLevel, threshold=None):
    """True on polluted → pure flip (birds-return audio cousin).

    Pure helper for AST / headless tests. Uses audio threshold so wash
    lands with PollutionStreetAudio birds bed, not only exact 0.0.
    """
    if threshold is None:
        threshold = BIRDS_RETURN_CREAM_WASH_AUDIO_THRESHOLD
    try:
        prev = float(prevLevel)
        new = float(newLevel)
        thresh = float(threshold)
    except (TypeError, ValueError):
        return False
    return prev > thresh and new <= thresh


class BirdsReturnCreamWashPulse(object):
    """Owns aspect2d cream wash + rising chirp residual on birds-return."""

    def __init__(self):
        self._ival = None
        self._washNP = None
        self._fleckNPs = []
        self._haloNP = None
        self._lastPlayT = -1.0e9

    def _debounced(self):
        gap = float(BIRDS_RETURN_CREAM_WASH_DEBOUNCE_SEC)
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            try:
                import time
                now = time.time()
            except Exception:
                return False
        if now - self._lastPlayT < gap:
            return True
        self._lastPlayT = now
        return False

    def play(self, delay=None):
        """Arm delayed cream wash + rising chirp aftershock. Returns Sequence or None."""
        if not BIRDS_RETURN_CREAM_WASH_ENABLED:
            return None
        if self._debounced():
            return None
        self.clear(retireClock=False)
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = BIRDS_RETURN_CREAM_WASH_COLOR
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.98, 0.78

        peak = float(BIRDS_RETURN_CREAM_WASH_PEAK)
        mid = float(BIRDS_RETURN_CREAM_WASH_MID)
        inSec = float(BIRDS_RETURN_CREAM_WASH_IN_SEC)
        pulseSec = float(BIRDS_RETURN_CREAM_WASH_PULSE_SEC)
        holdSec = float(BIRDS_RETURN_CREAM_WASH_HOLD_SEC)
        outSec = float(BIRDS_RETURN_CREAM_WASH_OUT_SEC)
        binSort = int(BIRDS_RETURN_CREAM_WASH_BIN)
        if delay is None:
            delay = float(BIRDS_RETURN_CREAM_WASH_DELAY_SEC)

        try:
            cm = CardMaker('safezone-birds-return-cream-wash')
            # Full-frame veil — tip / cheer / dodge-cancel wash grammar.
            cm.setFrame(-2, 2, -2, 2)
            wash = parent.attachNewNode(cm.generate())
            wash.setTransparency(TransparencyAttrib.MAlpha)
            wash.setColor(r, g, b, 1)
            wash.setColorScale(r, g, b, 0)
            wash.setBin('fixed', binSort)
            wash.setDepthTest(False)
            wash.setDepthWrite(False)
            self._washNP = wash
        except Exception:
            self._washNP = None
            return None

        # Delayed juicier two-beat with birds fade-in: bright → settle → fade.
        washVeil = Sequence(
            LerpColorScaleInterval(
                wash, max(0.01, inSec), Vec4(r, g, b, peak),
                blendType='easeOut'),
            LerpColorScaleInterval(
                wash, max(0.01, pulseSec), Vec4(r, g, b, mid),
                blendType='easeInOut'),
            Wait(max(0.0, holdSec)),
            LerpColorScaleInterval(
                wash, max(0.01, outSec), Vec4(r, g, b, 0),
                blendType='easeIn'),
            name='safezoneBirdsReturnCreamWashVeil',
        )

        origin = BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_ORIGIN
        try:
            ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
        except Exception:
            ox, oy, oz = 0.0, 0.0, 0.10

        aftershock = self._buildAftershock(parent, ox, oy, oz)
        if aftershock is not None:
            body = Parallel(washVeil, aftershock)
        else:
            body = washVeil

        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
            body,
            Wait(0.04),
            Func(self.clear),
            name='safezoneBirdsReturnCreamWash',
        )
        self._ival.start()
        return self._ival

    def _buildAftershock(self, parent, ox, oy, oz):
        """Rising cream chirp flecks + soft skyward halo (birds-return deepen)."""
        if not BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_ENABLED:
            return None
        delay = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_DELAY_SEC)
        parts = []

        if BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_ENABLED:
            halo = self._spawnAftershockHalo(parent, ox, oy, oz)
            if halo is not None:
                parts.append(halo)

        count = int(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_COUNT)
        sec = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SEC)
        for i in range(count):
            part = self._spawnChirpFleck(parent, ox, oy, oz, i, count, sec)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnAftershockHalo(self, parent, ox, oy, oz):
        """Soft skyward cream halo — not crumb pip / fog rim local bloom."""
        half = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_HALF)
        startScale = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_START)
        peakScale = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_PEAK)
        sec = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_SEC)
        peakA = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_PEAK_ALPHA)
        r, g, b, _a = BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_HALO_COLOR
        binSort = int(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_BIN)
        try:
            cm = CardMaker('safezone-birds-return-cream-wash-sky-halo')
            # Soft oval halo above center — skyward residual of the wash veil.
            cm.setFrame(-half, half, -half * 0.48, half * 0.48)
            halo = parent.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(ox, oy, oz + 0.06)
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

    def _spawnChirpFleck(self, parent, ox, oy, oz, index, total, sec):
        """Rising cream chip — birds-return chirp residual (not settle fall)."""
        count = max(1, int(total))
        size = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SIZE)
        rise = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_RISE)
        spread = float(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_SPREAD)
        r, g, b, a = BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_COLOR
        er, eg, eb, ea = BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_END_COLOR
        binSort = int(BIRDS_RETURN_CREAM_WASH_AFTERSHOCK_BIN)
        angle = (2.0 * pi * index) / float(count) + 0.22
        try:
            cm = CardMaker(
                'safezone-birds-return-cream-wash-chirp-%s' % index)
            # Alternate chip / cross — rubber-hose cream glitter.
            if (index % 3) == 0:
                cm.setFrame(
                    -size * 0.35, size * 0.35, -size * 1.25, size * 1.25)
            elif (index % 3) == 1:
                cm.setFrame(
                    -size * 1.25, size * 1.25, -size * 0.35, size * 0.35)
            else:
                cm.setFrame(-size, size, -size * 0.9, size * 0.9)
            fleck = parent.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            t = (float(index) / max(1, count - 1)) - 0.5
            startX = ox + t * spread * 0.55 + cos(angle) * 0.04
            startZ = oz + 0.012 * (index % 3) + sin(angle) * 0.02
            fleck.setPos(startX, oy, startZ)
            fleck.setScale(0.32 + 0.08 * (index % 3))
            fleck.setBin('fixed', binSort + 1 + (index % 2))
            fleck.setDepthTest(False)
            fleck.setDepthWrite(False)
        except Exception:
            return None

        # Rise skyward — birds-return chirp, not combat settle fall.
        end = Point3(
            startX + cos(angle) * 0.08,
            oy,
            startZ + rise * (0.55 + 0.45 * ((index % 4) / 3.0)))
        peak = 1.12 + 0.08 * (index % 2)
        self._fleckNPs.append(fleck)
        stagger = 0.018 * index
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.26), peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(
                    fleck, max(0.01, sec * 0.74), end, blendType='easeOut'),
                LerpScaleInterval(
                    fleck, max(0.01, sec * 0.74), 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, max(0.01, sec * 0.74), Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def clear(self, retireClock=True):
        """Stop wash/aftershock and remove every cream wash node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        wash = self._washNP
        self._washNP = None
        if wash is not None:
            try:
                if not wash.isEmpty():
                    wash.removeNode()
            except Exception:
                pass
        if self._haloNP is not None:
            try:
                if not self._haloNP.isEmpty():
                    self._haloNP.removeNode()
            except Exception:
                pass
            self._haloNP = None
        for np in self._fleckNPs:
            if np is not None:
                try:
                    if not np.isEmpty():
                        np.removeNode()
                except Exception:
                    pass
        self._fleckNPs = []


_birdsReturnWashFx = None


def _getBirdsReturnWashFx():
    global _birdsReturnWashFx
    if _birdsReturnWashFx is None:
        _birdsReturnWashFx = BirdsReturnCreamWashPulse()
    return _birdsReturnWashFx


def playBirdsReturnCreamWash(delay=None):
    """Fire soft cream wash pulse + rising chirp residual on TTC birds-return."""
    return _getBirdsReturnWashFx().play(delay=delay)


def clearBirdsReturnCreamWash():
    """Tear down any in-flight birds-return cream wash pulse / aftershock."""
    if _birdsReturnWashFx is not None:
        _birdsReturnWashFx.clear()
