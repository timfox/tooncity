"""Rubber-hose cream wash when TTC playground pollution clears / birds return.

Fullscreen soft cream veil that settles when reclaim-street pollution drops
to pure on the Toontown Central hub (or purityRestoreFx fires while the
hub breadcrumbs are live) — same PerfectDodgeCreamWashPulse /
PunchlineTipCreamWashPulse / CheerCreamWashPulse overlay grammar as a brief
explore settle beat. Pairs with PollutionStreetAudio pure-street birds
return (#55) so the neighborhood feeling clean reads juicily. Soft under
HUD; cream / pastel only (not ink). Client only. Safezone package —
Toontown spiritual sequel (no KH props, names, or branding).
"""

from __future__ import annotations

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

# Tunables live here (safezone-only scope — do not edit CorruptionGlobals).
BIRDS_RETURN_CREAM_WASH_ENABLED = True
# Land during pure-street birds fade-in (#55 FADE_IN_SEC ≈ 0.55).
BIRDS_RETURN_CREAM_WASH_DELAY_SEC = 0.42
BIRDS_RETURN_CREAM_WASH_PEAK = 0.10
BIRDS_RETURN_CREAM_WASH_MID = 0.055
BIRDS_RETURN_CREAM_WASH_IN_SEC = 0.08
BIRDS_RETURN_CREAM_WASH_PULSE_SEC = 0.14
BIRDS_RETURN_CREAM_WASH_HOLD_SEC = 0.10
BIRDS_RETURN_CREAM_WASH_OUT_SEC = 0.40
BIRDS_RETURN_CREAM_WASH_BIN = 46
BIRDS_RETURN_CREAM_WASH_COLOR = (1.0, 0.97, 0.82)
# Collapse pollutionChanged + purityRestoreFx double-fires (birds debounce ≈ 2.5).
BIRDS_RETURN_CREAM_WASH_DEBOUNCE_SEC = 2.2
# Match PollutionStreetAudio polluted→pure flip threshold when readable.
BIRDS_RETURN_CREAM_WASH_AUDIO_THRESHOLD = 0.05


def birdsReturnCreamWashParams():
    """Pure timing / alpha for birds-return cream wash.

    Headless-safe — no Panda geom. Distinct from placemarker (#211) /
    crumb (#216) scale pulses and playground fog edge breath (#221).
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
    """Owns a brief aspect2d cream wash pulse on birds-return / purify."""

    def __init__(self):
        self._ival = None
        self._washNP = None
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
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
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
            r, g, b = 1.0, 0.97, 0.82

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

        # Delayed two-beat with birds fade-in: bright → settle → fade.
        self._ival = Sequence(
            Wait(max(0.0, float(delay))),
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
            Func(self.clear),
            name='safezoneBirdsReturnCreamWash',
        )
        self._ival.start()
        return self._ival

    def clear(self, retireClock=True):
        """Stop wash pulse and remove the cream wash node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        wash = self._washNP
        self._washNP = None
        if wash is None:
            return
        try:
            if not wash.isEmpty():
                wash.removeNode()
        except Exception:
            pass


_birdsReturnWashFx = None


def _getBirdsReturnWashFx():
    global _birdsReturnWashFx
    if _birdsReturnWashFx is None:
        _birdsReturnWashFx = BirdsReturnCreamWashPulse()
    return _birdsReturnWashFx


def playBirdsReturnCreamWash(delay=None):
    """Fire soft cream wash pulse on TTC birds-return / pollution clear."""
    return _getBirdsReturnWashFx().play(delay=delay)


def clearBirdsReturnCreamWash():
    """Tear down any in-flight birds-return cream wash pulse."""
    if _birdsReturnWashFx is not None:
        _birdsReturnWashFx.clear()
