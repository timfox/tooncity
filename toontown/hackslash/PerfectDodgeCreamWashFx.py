"""Rubber-hose cream wash pulse after perfect-dodge cream aftershock.

Fullscreen soft cream veil that settles *after* DodgePerfectFx cream star
aftershock (#89) — EntryCreamWashPulseFx / PurityCompleteCreamWashFx overlay
grammar as a brief perfect-dodge settle beat. Soft under world-space stars;
cream / pastel only (not ink). Wired from DodgePerfectFx.play beside the
cream aftershock. Client only. Toontown spiritual sequel — no keyblades /
no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from . import HackSlashConfig


class PerfectDodgeCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after perfect-dodge aftershock."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_PEAK', 0.12))
        mid = float(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_MID', 0.07))
        inSec = float(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_IN_SEC', 0.06))
        pulseSec = float(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_PULSE_SEC', 0.10))
        holdSec = float(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_HOLD_SEC', 0.08))
        outSec = float(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_OUT_SEC', 0.40))
        binSort = int(getattr(
            HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_BIN', 28))
        if delay is None:
            delay = float(getattr(
                HackSlashConfig, 'PERFECT_DODGE_CREAM_WASH_DELAY_SEC', 0.40))

        try:
            cm = CardMaker('hackslash-perfect-dodge-cream-wash')
            # Full-frame veil — reclaim entry / purity cream wash grammar.
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

        # Delayed two-beat after cream aftershock: bright → settle → fade.
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
            name='hackslashPerfectDodgeCreamWash',
        )
        self._ival.start()
        return self._ival

    def clear(self):
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
