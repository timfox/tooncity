"""Overlord telegraph danger-ring warn + impact ground punch cream deepen.

World-space CardMaker juice for Ink Overlord phase wind-ups / hits — a
readable ground danger ring during announceAttackTelegraph (fair punish /
dodge footprint) and a rubber-hose impact punch bloom on announceAttackHit.
Deepened cream punch beyond #255 (#208 deepen): juicier cream/pastel rim +
denser radial cream phase flecks on the warn footprint + wider cream impact
aftershock so P1/P2 phase shifts read juicier still. Distinct from Brute spit
cream deepen (#289 / #264, vertical drip), Snare splash cream deepen (#293 /
#269, horizontal whip), Smudge hit cream deepen (#283 / #259, mid-body hose),
and Gunk puddle cream deepen (#299 / #276, flat trap-plane bloom) — Overlord
cream stays ground-plane radial around the phase telegraph punch. Composes
beside OverlordTelegraphCrownFx + OverlordPhaseInkRainFx; phase charge colors
tint magenta rise vs crimson unleash. Client only; AI timings unchanged.
Toontown spiritual sequel — no keyblades / no KH branding.
"""

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
        scale = float(look.get('warnHitRangeScale', 0.32))
        look['warnHalf'] = max(
            float(look.get('warnHalf', 2.8)), hitRange * scale)
        if phaseIndex >= 2:
            # Unleashed: slightly wider / hotter ring; slam still fits inside.
            look['warnHalf'] = float(look['warnHalf']) * float(
                look.get('p2WarnScale', 1.14))
            look['warnPeak'] = float(look.get('warnPeak', 1.06)) * float(
                look.get('p2WarnPeakScale', 1.1))

    if phaseIndex >= 2:
        look['warnColor'] = look.get(
            'warnColorP2', look.get('warnColor', (2.7, 0.18, 0.22, 0.66)))
        look['warnRimColor'] = look.get(
            'warnRimColorP2',
            look.get('warnRimColor', (1.0, 0.92, 0.7, 0.9)))
        look['impactColor'] = look.get(
            'impactColorP2',
            look.get('impactColor', (2.85, 0.35, 0.2, 0.94)))
        look['holdSec'] = float(look.get(
            'holdSecP2', look.get('holdSec', 0.28)))
    else:
        look['warnColor'] = look.get(
            'warnColorP1', look.get('warnColor', (2.4, 0.35, 2.7, 0.58)))
        look['warnRimColor'] = look.get(
            'warnRimColorP1',
            look.get('warnRimColor', (1.0, 0.96, 0.82, 0.88)))
        look['impactColor'] = look.get(
            'impactColorP1',
            look.get('impactColor', (2.55, 0.55, 2.7, 0.88)))
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
    """Owns ground danger-ring warn + cream deepen + impact punch bloom."""

    def __init__(self):
        self._ival = None
        self._nodes = []

    def playWarn(self, pos, finaleLook=None, phase=1, parent=None):
        """Spawn ground danger ring + cream flecks. Returns Sequence or None."""
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
        parts = [ring]
        flecks = self._spawnWarnCreamFlecks(parentNP, pos, look)
        if flecks is not None:
            parts.append(flecks)
        self._ival = Sequence(
            Parallel(*parts, name='overlordWarnCreamPunch'),
            Func(self.clear),
            name='overlordTelegraphPunchWarn',
        )
        self._ival.start()
        return self._ival

    def playImpact(self, pos, finaleLook=None, phase=1, parent=None):
        """Spawn impact punch bloom + cream aftershock. Returns Sequence or None."""
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
        parts = [bloom]
        aftershock = self._buildImpactCreamAftershock(parentNP, pos, look)
        if aftershock is not None:
            parts.append(aftershock)
        self._ival = Sequence(
            Parallel(*parts, name='overlordImpactCreamPunch'),
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
        """Phase-tinted danger ring + juicier cream rim — rain/slam footprint."""
        try:
            half = float(look.get('warnHalf', 2.7))
            lift = float(look.get('warnLift', 0.1))
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
            color = look.get('warnColor', (2.4, 0.35, 2.7, 0.58))
            fill.setColor(color[0], color[1], color[2], color[3])
            fill.setColorScale(1, 1, 1, 0)
            fill.setScale(0.28)
            fill.setBin('fixed', int(look.get('binSort', 42)))
            fill.setDepthWrite(False)
            self._nodes.append(fill)

            rimHalf = half * float(look.get('warnRimScale', 1.12))
            cmRim = CardMaker('overlord-telegraph-warn-rim')
            # Thin annulus illusion: slightly larger card, lower alpha fill.
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.55, rimHalf * 0.55)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin[0], origin[1], origin[2] + 0.01)
            rim.setP(-90)
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look.get('warnRimColor', (1.0, 0.96, 0.82, 0.88))
            rim.setColor(
                rimColor[0], rimColor[1], rimColor[2], rimColor[3])
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.32)
            rim.setBin('fixed', int(look.get('binSort', 42)) + 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('warnPeak', 1.06))
            fadeIn = float(look.get('warnInSec', 0.09))
            hold = float(look.get('holdSec', 0.42))
            pulse = float(look.get('warnPulseSec', 0.18))
            fadeOut = float(look.get('warnOutSec', 0.24))
            peakA = float(look.get('warnPeakAlpha', 0.92))
            rimPeakA = float(look.get('warnRimPeakAlpha', 0.94))

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
                        fill, pulse, peak * 1.1, blendType='easeInOut'),
                    Wait(max(0.0, hold - pulse)),
                    Parallel(
                        LerpScaleInterval(
                            fill, fadeOut, peak * 1.2, blendType='easeIn'),
                        LerpColorScaleInterval(
                            fill, fadeOut, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
                Sequence(
                    Parallel(
                        LerpScaleInterval(
                            rim, fadeIn, peak * 1.04, blendType='easeOut'),
                        LerpColorScaleInterval(
                            rim, fadeIn, Vec4(1, 1, 1, rimPeakA),
                            blendType='easeOut'),
                    ),
                    LerpScaleInterval(
                        rim, pulse, peak * 1.16, blendType='easeInOut'),
                    Wait(max(0.0, hold - pulse)),
                    Parallel(
                        LerpScaleInterval(
                            rim, fadeOut, peak * 1.28, blendType='easeIn'),
                        LerpColorScaleInterval(
                            rim, fadeOut, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
                name='overlordWarnRingHose',
            )
        except Exception:
            return None

    def _spawnWarnCreamFlecks(self, parentNP, bossPos, look):
        """Radial cream phase flecks along the danger-ring edge.

        Ground-plane chips (+ thin radial streaks beyond #255) that pop
        outward from the warn footprint — phase telegraph cream read.
        Distinct from Brute vertical drip (#289 / #264), Snare horizontal
        whip (#293 / #269), Smudge mid-body hose (#283 / #259), and Gunk
        flat trap bloom (#299 / #276).
        """
        if not look.get(
                'creamFleckEnabled',
                getattr(
                    CorruptionGlobals,
                    'OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_ENABLED', True)):
            return None
        count = max(0, int(look.get(
            'creamFleckCount',
            getattr(
                CorruptionGlobals,
                'OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_COUNT', 7))))
        if count <= 0:
            return None
        parts = []
        for i in range(count):
            part = self._spawnWarnCreamFleck(parentNP, bossPos, look, i, count)
            if part is not None:
                parts.append(part)
        if not parts:
            return None
        return Parallel(*parts, name='overlordWarnCreamFlecks')

    def _spawnWarnCreamFleck(self, parentNP, bossPos, look, index, count):
        """One cream chip / radial streak riding the warn ring edge."""
        try:
            half = float(look.get('warnHalf', 2.8))
            lift = float(look.get('warnLift', 0.1))
            fleckLift = float(look.get(
                'creamFleckLift',
                getattr(
                    CorruptionGlobals,
                    'OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_LIFT', 0.28)))
            origin = Point3(
                bossPos[0], bossPos[1], float(bossPos[2]) + lift)
            # Ring-edge radial — phase footprint chips, not drip / whip /
            # trap bloom. Beyond #255: alternate soft chip vs thin radial
            # streak so denser flecks still read as ring chips.
            angle = (2.0 * pi * index) / float(count) + 0.22 * (index % 3)
            radius = half * (0.78 + 0.08 * (index % 3))
            start = Point3(
                origin[0] + cos(angle) * radius * 0.52,
                origin[1] + sin(angle) * radius * 0.52,
                origin[2] + 0.04,
            )
            end = Point3(
                origin[0] + cos(angle) * radius * 1.18,
                origin[1] + sin(angle) * radius * 1.18,
                origin[2] + fleckLift * (0.55 + 0.18 * (index % 3)),
            )
            fleckHalf = float(look.get(
                'creamFleckHalf',
                getattr(
                    CorruptionGlobals,
                    'OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_HALF', 0.13)))
            elongated = (index % 2 == 1)
            if elongated:
                cm = CardMaker(
                    'overlord-telegraph-cream-fleck-streak-%s' % index)
                # Thin radial streak along the ring — still ground-plane
                # radial (not Snare sideways whip / Brute vertical drip).
                cm.setFrame(
                    -fleckHalf * 0.38, fleckHalf * 0.38,
                    -fleckHalf * 1.35, fleckHalf * 1.35)
                startScale = 0.3
                midScale = 1.28
                endScale = 0.28
            else:
                cm = CardMaker('overlord-telegraph-cream-fleck-%s' % index)
                cm.setFrame(
                    -fleckHalf, fleckHalf, -fleckHalf * 0.9, fleckHalf * 0.9)
                startScale = 0.32
                midScale = 1.28
                endScale = 0.32
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setPos(start)
            fleck.setBillboardPointEye()
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            colors = look.get(
                'creamFleckColors',
                getattr(
                    CorruptionGlobals,
                    'OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_COLORS', ())) or ()
            if colors:
                color = colors[index % len(colors)]
            else:
                color = (1.0, 0.97, 0.82, 0.9)
            fleck.setColor(color[0], color[1], color[2], color[3])
            fleck.setColorScale(1, 1, 1, 0)
            fleck.setScale(startScale)
            fleck.setBin('fixed', int(look.get('binSort', 42)) + 2)
            fleck.setDepthWrite(False)
            self._nodes.append(fleck)

            sec = float(look.get(
                'creamFleckSec',
                getattr(
                    CorruptionGlobals,
                    'OVERLORD_TELEGRAPH_PUNCH_CREAM_FLECK_SEC', 0.32)))
            peakA = float(color[3]) if len(color) > 3 else 0.9
            delay = 0.016 * index
            return Sequence(
                Wait(delay),
                Parallel(
                    LerpPosInterval(fleck, sec, end, blendType='easeOut'),
                    Sequence(
                        LerpScaleInterval(
                            fleck, sec * 0.35, midScale, blendType='easeOut'),
                        LerpScaleInterval(
                            fleck, sec * 0.65, endScale, blendType='easeIn'),
                    ),
                    Sequence(
                        LerpColorScaleInterval(
                            fleck, sec * 0.25, Vec4(1, 1, 1, peakA),
                            blendType='easeOut'),
                        LerpColorScaleInterval(
                            fleck, sec * 0.75, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
            )
        except Exception:
            return None

    def _spawnImpactBloom(self, parentNP, bossPos, look):
        """Fast rubber-hose ground punch bloom + cream rim on attack land."""
        try:
            half = float(look.get('impactHalf', 1.7))
            lift = float(look.get('impactLift', 0.08))
            origin = Point3(
                bossPos[0], bossPos[1], float(bossPos[2]) + lift)
            cm = CardMaker('overlord-telegraph-impact-bloom')
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            bloom = parentNP.attachNewNode(cm.generate())
            bloom.setPos(origin)
            bloom.setP(-90)
            bloom.setTransparency(TransparencyAttrib.MAlpha)
            color = look.get('impactColor', (2.55, 0.55, 2.7, 0.9))
            bloom.setColor(color[0], color[1], color[2], color[3])
            bloom.setColorScale(1, 1, 1, 0)
            bloom.setScale(0.24)
            bloom.setBin('fixed', int(look.get('impactBin', 45)))
            bloom.setDepthWrite(False)
            self._nodes.append(bloom)

            rimHalf = half * float(look.get('impactCreamRimScale', 1.38))
            cmRim = CardMaker('overlord-telegraph-impact-cream-rim')
            cmRim.setFrame(-rimHalf, rimHalf, -rimHalf * 0.55, rimHalf * 0.55)
            rim = parentNP.attachNewNode(cmRim.generate())
            rim.setPos(origin[0], origin[1], origin[2] + 0.01)
            rim.setP(-90)
            rim.setTransparency(TransparencyAttrib.MAlpha)
            rimColor = look.get(
                'impactCreamRimColor', (1.0, 0.97, 0.84, 0.88))
            rim.setColor(
                rimColor[0], rimColor[1], rimColor[2], rimColor[3])
            rim.setColorScale(1, 1, 1, 0)
            rim.setScale(0.2)
            rim.setBin('fixed', int(look.get('impactBin', 45)) + 1)
            rim.setDepthWrite(False)
            self._nodes.append(rim)

            peak = float(look.get('impactPeak', 3.15))
            fadeIn = float(look.get('impactInSec', 0.05))
            hold = float(look.get('impactHoldSec', 0.07))
            fadeOut = float(look.get('impactOutSec', 0.26))
            peakA = float(look.get('impactPeakAlpha', 0.97))
            rimPeakA = float(look.get('impactCreamRimPeakAlpha', 0.94))

            return Parallel(
                Sequence(
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
                            bloom, fadeOut, peak * 1.42, blendType='easeIn'),
                        LerpColorScaleInterval(
                            bloom, fadeOut, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
                Sequence(
                    Parallel(
                        LerpScaleInterval(
                            rim, fadeIn, peak * 1.08, blendType='easeOut'),
                        LerpColorScaleInterval(
                            rim, fadeIn, Vec4(1, 1, 1, rimPeakA),
                            blendType='easeOut'),
                    ),
                    Wait(hold),
                    Parallel(
                        LerpScaleInterval(
                            rim, fadeOut, peak * 1.5, blendType='easeIn'),
                        LerpColorScaleInterval(
                            rim, fadeOut, Vec4(1, 1, 1, 0),
                            blendType='easeIn'),
                    ),
                ),
                name='overlordImpactPunchHose',
            )
        except Exception:
            return None

    def _buildImpactCreamAftershock(self, parentNP, bossPos, look):
        """Delayed cream halo + residual flecks after impact punch bloom.

        Ground-plane settle aftershock — phase punch residual beyond #255.
        Same residual grammar as telegraph cream warn aftershock (#121);
        distinct from Brute spit drip settle (#289 / #264), Snare whip
        residual (#293 / #269), and Gunk trap-plane bloom (#299 / #276).
        """
        if not look.get(
                'creamAftershockEnabled',
                getattr(
                    CorruptionGlobals,
                    'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_ENABLED',
                    True)):
            return None
        delay = float(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_DELAY_SEC', 0.07))
        lift = float(look.get('impactLift', 0.08))
        origin = Point3(
            bossPos[0], bossPos[1], float(bossPos[2]) + lift)
        parts = []
        if getattr(
                CorruptionGlobals,
                'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_ENABLED',
                True):
            halo = self._spawnImpactCreamHalo(parentNP, origin)
            if halo is not None:
                parts.append(halo)

        creamCount = max(0, int(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_COUNT', 6)))
        streakCount = max(0, int(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_STREAK_COUNT', 3)))
        for i in range(creamCount):
            part = self._spawnImpactCreamSpark(
                parentNP, origin, i, creamCount, elongated=False)
            if part is not None:
                parts.append(part)
        for i in range(streakCount):
            part = self._spawnImpactCreamSpark(
                parentNP, origin, i, streakCount, elongated=True)
            if part is not None:
                parts.append(part)
        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts, name='overlordImpactCreamAftershock'),
        )

    def _spawnImpactCreamHalo(self, parentNP, origin):
        half = float(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_HALF', 0.72))
        startScale = float(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_START', 0.26))
        peakScale = float(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_PEAK', 1.9))
        sec = float(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_SEC', 0.38))
        peakA = float(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA',
            0.3))
        r, g, b, _a = getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.97, 0.82, 1.0))
        try:
            cm = CardMaker('overlord-telegraph-cream-aftershock-halo')
            cm.setFrame(-half, half, -half * 0.55, half * 0.55)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setPos(origin)
            halo.setP(-90)
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1.0)
            halo.setColorScale(1, 1, 1, 0)
            halo.setScale(startScale)
            halo.setBin('fixed', 44)
            halo.setDepthWrite(False)
            self._nodes.append(halo)
            return Sequence(
                Parallel(
                    LerpScaleInterval(
                        halo, sec * 0.4, peakScale, blendType='easeOut'),
                    LerpColorScaleInterval(
                        halo, sec * 0.35, Vec4(1, 1, 1, peakA),
                        blendType='easeOut'),
                ),
                Parallel(
                    LerpScaleInterval(
                        halo, sec * 0.6, peakScale * 1.22, blendType='easeIn'),
                    LerpColorScaleInterval(
                        halo, sec * 0.65, Vec4(1, 1, 1, 0),
                        blendType='easeIn'),
                ),
            )
        except Exception:
            return None

    def _spawnImpactCreamSpark(
            self, parentNP, origin, index, total, elongated=False):
        """Residual cream fleck / streak after impact punch — radial settle."""
        count = max(1, int(total))
        if elongated:
            size = float(getattr(
                CorruptionGlobals,
                'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_STREAK_SIZE',
                0.18))
            color = getattr(
                CorruptionGlobals,
                'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_STREAK_COLOR',
                (1.0, 0.98, 0.82, 0.9))
            endColor = getattr(
                CorruptionGlobals,
                'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_STREAK_END',
                (1.0, 0.9, 0.5, 0.0))
            angleBias = 0.35
        else:
            size = float(getattr(
                CorruptionGlobals,
                'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_SIZE', 0.14))
            color = getattr(
                CorruptionGlobals,
                'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_COLOR',
                (1.0, 0.96, 0.72, 0.92))
            endColor = getattr(
                CorruptionGlobals,
                'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_END',
                (1.0, 0.92, 0.55, 0.0))
            angleBias = 0.12
        drift = float(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_DRIFT', 1.0))
        sec = float(getattr(
            CorruptionGlobals,
            'OVERLORD_TELEGRAPH_PUNCH_CREAM_AFTERSHOCK_SEC', 0.4))
        angle = (2.0 * pi * index) / float(count) + angleBias
        try:
            kind = 'streak' if elongated else 'fleck'
            cm = CardMaker(
                'overlord-telegraph-cream-aftershock-%s-%s' % (kind, index))
            if elongated:
                cm.setFrame(-size * 0.35, size * 0.35, -size * 1.2, size * 1.2)
            else:
                cm.setFrame(-size, size, -size * 0.9, size * 0.9)
            spark = parentNP.attachNewNode(cm.generate())
            spark.setPos(origin)
            spark.setBillboardPointEye()
            spark.setTransparency(TransparencyAttrib.MAlpha)
            spark.setColor(color[0], color[1], color[2], color[3])
            spark.setColorScale(1, 1, 1, 0)
            spark.setScale(0.38)
            spark.setBin('fixed', 44)
            spark.setDepthWrite(False)
            self._nodes.append(spark)
        except Exception:
            return None

        # Radial ground settle — phase punch residual (not drip / whip /
        # Gunk trap bloom).
        end = Point3(
            origin[0] + cos(angle) * drift * (0.72 + 0.12 * (index % 3)),
            origin[1] + sin(angle) * drift * (0.72 + 0.12 * (index % 3)),
            origin[2] + 0.08 + 0.05 * (index % 3))
        peak = size * (1.25 + 0.1 * (index % 2))
        stagger = 0.016 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpPosInterval(spark, sec, end, blendType='easeOut'),
                Sequence(
                    LerpScaleInterval(
                        spark, sec * 0.3, peak * 4.4, blendType='easeOut'),
                    LerpScaleInterval(
                        spark, sec * 0.7, peak * 1.15, blendType='easeIn'),
                ),
                Sequence(
                    LerpColorScaleInterval(
                        spark, sec * 0.22, Vec4(1, 1, 1, color[3]),
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        spark, sec * 0.78,
                        Vec4(endColor[0], endColor[1], endColor[2], 0),
                        blendType='easeIn'),
                ),
            ),
        )
