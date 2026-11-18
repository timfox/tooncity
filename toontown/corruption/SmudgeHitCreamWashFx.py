"""Rubber-hose cream wash pulse after Smudge purple ink splash (hit only).

Fullscreen soft cream veil that settles *after* SmudgeInkSplashFx (#75) +
SmudgeHitCreamSplashFx cream splash/aftershock on Ink Smudge hits —
CorruptTelegraphCreamWashFx (#157) / OverlordHitCreamWashFx (#161) /
CorruptSilhouetteCreamWashFx (#153) / CorruptDeathCreamWashFx (#119)
overlay grammar as a brief street-hit settle beat against purple ink. Soft
under world-space splash; cream / pastel only (not ink). Wired from
DistributedCorruptToon hit reaction beside SmudgeInkSplash +
SmudgeHitCreamSplash (hit path only — death keeps splash + death cream wash).
Client only. Toontown spiritual sequel — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    Sequence,
    Wait,
)

from toontown.corruption import CorruptionGlobals


def smudgeHitCreamWashLook():
    """Resolve Smudge hit cream-wash tunables; compose delay with purple splash."""
    look = dict(getattr(
        CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_LOOK', {}) or {})
    # Lazy import avoids circular load with Smudge ink splash.
    try:
        from toontown.corruption.SmudgeInkSplashFx import smudgeInkSplashLook
        splash = smudgeInkSplashLook('hit')
        splatSec = float(splash.get('splatSec', 0.18))
        # Land wash as purple splat settles — not sync-locked with smack peak.
        look.setdefault(
            'delaySec',
            splatSec * float(look.get('delayScale', 0.72)))
    except Exception:
        look.setdefault(
            'delaySec',
            float(getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_DELAY_SEC',
                0.13)))
    look.setdefault(
        'binSort',
        int(getattr(CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_BIN', 40)))
    return look


class SmudgeHitCreamWashPulse(object):
    """Owns a brief aspect2d cream wash pulse after Smudge hit purple splash."""

    def __init__(self):
        self._ival = None
        self._washNP = None

    def play(self, delay=None):
        """Arm delayed two-beat cream wash. Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_ENABLED', True):
            return None
        self.clear()
        look = smudgeHitCreamWashLook()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return None

        cream = getattr(
            CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_COLOR', None)
        if cream is None:
            cream = look.get('color') or (1.0, 0.97, 0.82)
        try:
            r, g, b = float(cream[0]), float(cream[1]), float(cream[2])
        except Exception:
            r, g, b = 1.0, 0.97, 0.82

        peak = float(look.get(
            'peak',
            getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_PEAK', 0.07)))
        mid = float(look.get(
            'mid',
            getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_MID', 0.04)))
        inSec = float(look.get(
            'inSec',
            getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_IN_SEC', 0.06)))
        pulseSec = float(look.get(
            'pulseSec',
            getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_PULSE_SEC',
                0.10)))
        holdSec = float(look.get(
            'holdSec',
            getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_HOLD_SEC',
                0.08)))
        outSec = float(look.get(
            'outSec',
            getattr(
                CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_OUT_SEC',
                0.38)))
        binSort = int(look.get(
            'binSort',
            getattr(CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_BIN', 40)))
        if delay is None:
            delay = float(look.get(
                'delaySec',
                getattr(
                    CorruptionGlobals, 'SMUDGE_HIT_CREAM_WASH_DELAY_SEC',
                    0.13)))

        try:
            cm = CardMaker('smudge-hit-cream-wash')
            # Full-frame veil — telegraph / overlord-hit / death cream wash grammar.
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

        # Delayed two-beat after purple splash: bright → settle → fade
        # (quieter than death #119 peak 0.14 / melee #134 peak 0.10 /
        # overlord hit #161 peak 0.08; above telegraph #157 peak 0.065 so
        # Smudge hit reads against purple ink without boss intensity).
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
            name='smudgeHitCreamWash',
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
