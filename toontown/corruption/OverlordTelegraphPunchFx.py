"""Overlord telegraph danger-ring warn + impact ground punch bloom.

World-space CardMaker juice for Ink Overlord phase wind-ups / hits — a
readable ground danger ring during announceAttackTelegraph (fair punish /
dodge footprint) and a rubber-hose impact punch bloom on announceAttackHit.
Composes beside OverlordTelegraphCrownFx + OverlordPhaseInkRainFx; phase
charge colors tint magenta rise vs crimson unleash. Client only; AI timings
unchanged. Toontown spiritual sequel — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from toontown.corruption import CorruptionGlobals


def overlordTelegraphPunchLook(finaleLook=None, phase=1):
    """Resolve warn-ring / impact-punch palette; phase charge colors tint."""
    look = dict(getattr(
        CorruptionGlobals, 'OVERLORD_TELEGRAPH_PUNCH_LOOK', {}) or {})
    try:
        phaseIndex = max(1, int(phase))
    except (TypeError, ValueError):
        phaseIndex = 1

    # Compose warn footprint with combat hit range when available so the
    # danger ring tracks rain / slam pressure without hard-coding radii.
    combat = CorruptionGlobals.overlordPhaseCombat(phaseIndex)
    if combat:
        hitRange = float(combat.get('attackHitRange', 9.5))
        scale = float(look.get('warnHitRangeScale', 0.30))
        look['warnHalf'] = max(
            float(look.get('warnHalf', 2.6)), hitRange * scale)
        if phaseIndex >= 2:
            # Unleashed: slightly wider / hotter ring; slam still fits inside.
            look['warnHalf'] = float(look['warnHalf']) * float(
                look.get('p2WarnScale', 1.12))
            look['warnPeak'] = float(look.get('warnPeak', 1.0)) * float(
                look.get('p2WarnPeakScale', 1.08))

    if phaseIndex >= 2:
        look['warnColor'] = look.get(
            'warnColorP2', look.get('warnColor', (2.7, 0.18, 0.22, 0.62)))
        look['warnRimColor'] = look.get(
            'warnRimColorP2',
            look.get('warnRimColor', (1.0, 0.72, 0.55, 0.8)))
        look['impactColor'] = look.get(
            'impactColorP2',
            look.get('impactColor', (2.85, 0.35, 0.2, 0.92)))
        look['holdSec'] = float(look.get(
            'holdSecP2', look.get('holdSec', 0.28)))
    else:
        look['warnColor'] = look.get(
            'warnColorP1', look.get('warnColor', (2.4, 0.35, 2.7, 0.55)))
        look['warnRimColor'] = look.get(
            'warnRimColorP1',
            look.get('warnRimColor', (1.0, 0.85, 1.0, 0.75)))
        look['impactColor'] = look.get(
            'impactColorP1',
            look.get('impactColor', (2.55, 0.55, 2.7, 0.85)))
        look['holdSec'] = float(look.get(
            'holdSecP1', look.get('holdSec', 0.42)))

    if finaleLook:
        charge = finaleLook.get('telegraphCharge')
        impact = finaleLook.get('impactColor')
        if charge and len(charge) >= 3:
            # Soft phase-tint override keeps ring readable vs ink rain puddle.
            baseA = float(look['warnColor'][3]) if look.get('warnColor') else 0.55
            look['warnColor'] = (
                min(2.9, charge[0] * 0.95),
                min(2.9, charge[1] * 0.95),
                min(2.9, charge[2] * 0.95),
                baseA,
            )
        if impact and len(impact) >= 3:
            baseA = (
                float(look['impactColor'][3])
                if look.get('impactColor') else 0.88)
            look['impactColor'] = (
                min(2.95, impact[0]),
                min(2.95, impact[1]),
                min(2.95, impact[2]),
                baseA,
            )
    return look


def overlordTelegraphAnimSecs(finaleLook=None, phase=1):
    """Client AV squash/stretch timings for Overlord telegraph wind-up.

    Tuned so the stretched strike pose lingers across most of the AI
    telegraphDelay — impact usually cuts in while still stretched (fair
    punish / dodge read). Falls back to street defaults when keys missing.
    """
    look = finaleLook or {}
    defaults = getattr(
        CorruptionGlobals, 'OVERLORD_TELEGRAPH_ANIM_DEFAULTS', {}) or {}
    try:
        phaseIndex = max(1, int(phase))
    except (TypeError, ValueError):
        phaseIndex = 1
    phaseKey = 'p2' if phaseIndex >= 2 else 'p1'
    phaseDefaults = dict(defaults.get(phaseKey, {}) or {})

    def _sec(key, fallback):
        if key in look:
            try:
                return max(0.04, float(look[key]))
            except (TypeError, ValueError):
                pass
        if key in phaseDefaults:
            try:
                return max(0.04, float(phaseDefaults[key]))
            except (TypeError, ValueError):
                pass
        return float(fallback)

    return {
        'squashSec': _sec('telegraphSquashSec', 0.12),
        'midSec': _sec('telegraphMidSec', 0.18),
        'stretchSec': _sec('telegraphStretchSec', 0.14),
        'holdSec': _sec('telegraphHoldSec', 0.12),
        'recoverSec': _sec('telegraphRecoverSec', 0.10),
        'impactSlamSec': _sec('impactSlamSec', 0.06),
        'impactReboundSec': _sec('impactReboundSec', 0.10),
        'impactSettleSec': _sec('impactSettleSec', 0.12),
    }


class OverlordTelegraphPunch(object):
    """Owns ground danger-ring warn + impact punch bloom for Overlord."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def playWarn(self, pos, finaleLook=None, phase=1, parent=None):
        """Spawn ground danger ring at boss feet. Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals, 'OVERLORD_TELEGRAPH_PUNCH_ENABLED', True):
            return None
        self.clear()
        look = overlordTelegraphPunchLook(finaleLook=finaleLook, phase=phase)
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None

        ring = self._spawnWarnRing(parentNP, pos, look)
        if ring is None:
            return None
        self._ival = Sequence(
            ring,
            Func(self.clear),
            name='overlordTelegraphPunchWarn',
        )
        self._ival.start()
        return self._ival

    def playImpact(self, pos, finaleLook=None, phase=1, parent=None):
        """Spawn impact ground punch bloom. Returns Sequence or None."""
        if not getattr(
                CorruptionGlobals, 'OVERLORD_TELEGRAPH_PUNCH_ENABLED', True):
            return None
        self.clear()
        look = overlordTelegraphPunchLook(finaleLook=finaleLook, phase=phase)
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None

        bloom = self._spawnImpactBloom(parentNP, pos, look)
        if bloom is None:
            return None
        self._ival = Sequence(
            bloom,
            Func(self.clear),
            name='overlordTelegraphPunchImpact',
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
        for np in self._nodes:
            try:
                if np is not None and not np.isEmpty():
                    np.removeNode()
            except Exception:
                pass
        self._nodes = []

    def _spawnWarnRing(self, parentNP, bossPos, look):
        """Phase-tinted danger ring + cream rim — readable rain/slam footprint."""
        try:
            half = float(look.get('warnHalf', 2.6))
            lift = float(look.get('warnLift', 0.09))
            origin = Point3(
                bossPos[0], bossPos[1], float(bossPos[2]) + lift)

            # Soft fill disk under a brighter cream/pastel rim.
            fillHalf = half * float(look.get('warnFillScale', 0.92))
            cmFill = CardMaker('overlord-telegraph-warn-fill')
            cmFill.setFrame(-fillHalf, fillHalf, -fillHalf * 0.55, fillHalf * 0.55)
            fill = parentNP.attachNewNode(cmFill.generate())
            fill.setPos(origin)
            fill.setP(-90)
            fill.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get('warnColor', (2.4, 0.35, 2.7, 0.55))
            fill.setColor(color[0], color[1], color[2], color[3])
            fill.setColorScale(1, 1, 1, 0)
            fill.setScale(0.28)
            fill.setBin('fixed', int(look.get('binSort', 42)))
            fill.setDepthWrite(False)
            self._nodes.append(fill)

            rimHalf = half * float(look.get('warnRimScale', 1.05))
            cmRim = CardMaker('overlord-telegraph-warn-rim')
            # Thin annulus illusion: slightly larger card, lower alpha fill.
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.55, rimHalf * 0.55)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin[0], origin[1], origin[2] + 0.01)
            rim.setP(-90)
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look.get('warnRimColor', (1.0, 0.85, 1.0, 0.75))
            rim.setColor(
                rimColor[0], rimColor[1], rimColor[2], rimColor[3])
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.32)
            rim.setBin('fixed', int(look.get('binSort', 42)) + 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('warnPeak', 1.0))
            fadeIn = float(look.get('warnInSec', 0.10))
            hold = float(look.get('holdSec', 0.42))
            pulse = float(look.get('warnPulseSec', 0.16))
            fadeOut = float(look.get('warnOutSec', 0.22))
            peakA = float(look.get('warnPeakAlpha', 0.9))
            rimPeakA = float(look.get('warnRimPeakAlpha', 0.85))

            # Two-beat pulse so the footprint reads as a committed wind-up,
            # then settles before impact clears the ring.
            return Parallel(
                Sequence(
                    Parallel(
                        LerpScaleInterval(
                            fill, fadeIn, peak, blendType='easeOut'),
                        LerpColorScaleInterval(
                            fill, fadeIn, Vec4(1, 1, 1, peakA),
                            blendType='easeOut'),
                    ),
                    LerpScaleInterval(
                        fill, pulse, peak * 1.08, blendType='easeInOut'),
                    Wait(max(0.0, hold - pulse)),
                    Parallel(
                        LerpScaleInterval(
                            fill, fadeOut, peak * 1.18, blendType='easeIn'),
                        LerpColorScaleInterval(
                            fill, fadeOut, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
                Sequence(
                    Parallel(
                        LerpScaleInterval(
                            rim, fadeIn, peak * 1.02, blendType='easeOut'),
                        LerpColorScaleInterval(
                            rim, fadeIn, Vec4(1, 1, 1, rimPeakA),
                            blendType='easeOut'),
                    ),
                    LerpScaleInterval(
                        rim, pulse, peak * 1.12, blendType='easeInOut'),
                    Wait(max(0.0, hold - pulse)),
                    Parallel(
                        LerpScaleInterval(
                            rim, fadeOut, peak * 1.22, blendType='easeIn'),
                        LerpColorScaleInterval(
                            rim, fadeOut, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
                name='overlordWarnRingHose',
            )
        except Exception:
            return None

    def _spawnImpactBloom(self, parentNP, bossPos, look):
        """Fast rubber-hose ground punch bloom when the Overlord attack lands."""
        try:
            half = float(look.get('impactHalf', 1.35))
            lift = float(look.get('impactLift', 0.08))
            cm = CardMaker('overlord-telegraph-impact-bloom')
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            bloom = parentNP.attachNewNode(cm.generate())
            bloom.setPos(
                bossPos[0], bossPos[1], float(bossPos[2]) + lift)
            bloom.setP(-90)
            bloom.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get('impactColor', (2.55, 0.55, 2.7, 0.85))
            bloom.setColor(color[0], color[1], color[2], color[3])
            bloom.setColorScale(1, 1, 1, 0)
            bloom.setScale(0.25)
            bloom.setBin('fixed', int(look.get('impactBin', 45)))
            bloom.setDepthWrite(False)
            self._nodes.append(bloom)

            peak = float(look.get('impactPeak', 2.6))
            fadeIn = float(look.get('impactInSec', 0.05))
            hold = float(look.get('impactHoldSec', 0.06))
            fadeOut = float(look.get('impactOutSec', 0.22))
            peakA = float(look.get('impactPeakAlpha', 0.95))

            return Sequence(
                Parallel(
                    LerpScaleInterval(
                        bloom, fadeIn, peak, blendType='easeOut'),
                    LerpColorScaleInterval(
                        bloom, fadeIn, Vec4(1, 1, 1, peakA),
                        blendType='easeOut'),
                ),
                Wait(hold),
                Parallel(
                    LerpScaleInterval(
                        bloom, fadeOut, peak * 1.35, blendType='easeIn'),
                    LerpColorScaleInterval(
                        bloom, fadeOut, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
                name='overlordImpactPunchHose',
            )
        except Exception:
            return None
