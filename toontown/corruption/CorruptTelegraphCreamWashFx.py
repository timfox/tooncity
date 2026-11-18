"""Rubber-hose cream wash pulse on corrupt telegraph cream warn / sparkle stack.

Fullscreen soft cream veil that settles *after* telegraph cream warn flecks
(#102) + delayed aftershock (#121) + rising cream sparkles (#135) —
SilhouetteCreamWashPulse (#153) / IdleCreamWashPulse (#146) /
DeathCreamWashPulse (#119) overlay grammar as a brief telegraph settle beat
against ink telegraph juice. Soft under world-space warn flecks + rising
sparkles; cream / pastel only (not ink). Wired from DistributedCorruptToon
beside TelegraphCreamWarnFlecks + TelegraphCreamSparkles (play / clear
together). Client only. Toontown spiritual sequel — no keyblades / no KH
branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.corruption import CorruptionGlobals


def telegraphCreamWashLook(archetype=None, finaleLook=None):
    """Resolve telegraph cream-wash tunables; compose delay with sparkle / aftershock."""
    look = dict(getattr(
        CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_LOOK', {}) or {})
    # Lazy import avoids circular load with telegraph cream sparkle / warn.
    try:
        from toontown.corruption.CorruptTelegraphCreamSparkleFx import (
            telegraphCreamSparkleLook)
        sparkle = telegraphCreamSparkleLook(archetype, finaleLook=finaleLook)
        sparkleStart = float(sparkle.get('startDelaySec', 0.04))
        sparkleTravel = float(sparkle.get('fleckSec', 0.37))
        # Land wash after rising sparkles begin settling — not sync-locked
        # with warn pop (#102) or aftershock (#121) / sparkle (#135) start.
        look.setdefault(
            'delaySec',
            sparkleStart + sparkleTravel * float(
                look.get('delayScale', 0.72)))
    except Exception:
        aftershockDelay = float(getattr(
            CorruptionGlobals,
            'TELEGRAPH_CREAM_WARN_AFTERSHOCK_DELAY_SEC', 0.18))
        look.setdefault(
            'delaySec',
            aftershockDelay + float(look.get('delayBias', 0.12)))
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_BIN', 39)))
    return look


class TelegraphCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse on telegraph cream warn stack."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None, archetype=None, finaleLook=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        look = telegraphCreamWashLook(archetype, finaleLook=finaleLook)
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = look.get('color') or (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(look.get(
            'peak',
            getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_PEAK', 0.065)))
        mid = float(look.get(
            'mid',
            getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_MID', 0.036)))
        inSec = float(look.get(
            'inSec',
            getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_IN_SEC', 0.06)))
        pulseSec = float(look.get(
            'pulseSec',
            getattr(
                CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_PULSE_SEC', 0.10)))
        holdSec = float(look.get(
            'holdSec',
            getattr(
                CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_HOLD_SEC', 0.08)))
        outSec = float(look.get(
            'outSec',
            getattr(
                CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_OUT_SEC', 0.40)))
        binSort = int(look.get(
            'binSort',
            getattr(CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_BIN', 39)))
        if delay is None:
            delay = float(look.get(
                'delaySec',
                getattr(
                    CorruptionGlobals, 'TELEGRAPH_CREAM_WASH_DELAY_SEC',
                    0.30)))

        try:
            cm = CardMaker('corrupt-telegraph-cream-wash')
            # Full-frame veil — silhouette / idle / death cream wash grammar.
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

        # Delayed two-beat after warn / sparkle stack: bright → settle → fade
        # (quieter than death #119 / melee #134 — telegraph fires often;
        # slightly above ambient idle #146 / silhouette #153 so the event reads).
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
            name='corruptTelegraphCreamWash',
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
