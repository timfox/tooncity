"""Rubber-hose cream wash pulse after combo-counter cream aftershock.

Fullscreen soft cream veil that settles *after* HitJuice combo cream tick
sparkle (#85) + cream aftershock (#116) — FinisherCreamWashPulse /
HitSparkCreamWashPulse / DodgeTrailCreamWashPulse overlay grammar as a
brief punch-counter settle beat. Soft under aspect2d flecks; cream /
pastel only (not ink). Wired from HitJuice.spawnComboCreamSparkles beside
the cream aftershock. Client only. Toontown spiritual sequel — no
keyblades / no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from . import HackSlashConfig


class ComboCounterCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after combo cream aftershock."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_PEAK', 0.09))
        mid = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_MID', 0.05))
        inSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_IN_SEC', 0.05))
        pulseSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_PULSE_SEC', 0.08))
        holdSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_HOLD_SEC', 0.05))
        outSec = float(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_OUT_SEC', 0.30))
        binSort = int(getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_BIN', 28))
        if delay is None:
            delay = float(getattr(
                HackSlashConfig, 'COMBO_COUNTER_CREAM_WASH_DELAY_SEC', 0.34))

        try:
            cm = CardMaker('hackslash-combo-counter-cream-wash')
            # Full-frame veil — finisher / melee-hit / dodge-trail grammar.
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
            name='hackslashComboCounterCreamWash',
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
