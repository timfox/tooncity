"""Rubber-hose impact squash/stretch juice for Oswald stretch-punch melee.

Shared helpers so MeleeCombat, demo hostiles, and corrupt hit-reacts share one
cartoon scale curve: brief flat squash → tall recover stretch → settle.
Combo finishers use playFinisherSlam for a heavier rubber-hose slam beat.
Launcher hang uses buildLaunchHangInterval + spawnCreamHangSparkles for a
readable airborne float with cream sparkle before fall (spawnHangSparks stays
as the cream-disabled fallback).
Combo counter HUD uses playComboCounterPop + spawnComboInkFlecks +
spawnComboCreamSparkles for a brief rubber-hose number pop with ink flecks
and cream sparkle on each connect.
Soft-lock reticle uses playSoftLockReticlePop + spawnSoftLockAccents for a
cream/ink hose pop when soft-lock acquires or snaps a corrupt target.
Hit connect uses spawnHitSparkFlecks for short cream/ink fleck sparkles that
layer with the impact squash silhouette.
Hitstop freeze uses pauseIntervals / freezeActorPlayRates so the impact
silhouette sticks before launch juice resumes.
No keyblades / no KH framing — Toontown rubber-hose only.
"""

import random
from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec3, Vec4

from direct.interval.IntervalGlobal import (
    LerpColorScaleInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from . import HackSlashConfig


def resolveVisualNode(target):
    """Pick a scalable node for hit juice (visualRoot / geom / _visual / self)."""
    if target is None:
        return None
    for attr in ('visualRoot', 'geom', '_visual'):
        node = getattr(target, attr, None)
        if node is not None:
            try:
                if not node.isEmpty():
                    return node
            except Exception:
                return node
    try:
        if hasattr(target, 'isEmpty') and target.isEmpty():
            return None
    except Exception:
        return None
    return target


def _tupleScale(xyz, base=None):
    sx, sy, sz = xyz[0], xyz[1], xyz[2]
    if base is None:
        return Point3(sx, sy, sz)
    return Point3(base[0] * sx, base[1] * sy, base[2] * sz)


def _playScalePulse(node, squashRow, stretchRow, settleSec, finishScale=None,
                    name='hackslashScalePulse'):
    """Shared squash → stretch → settle start. Returns a started Sequence."""
    if node is None:
        return None
    try:
        if hasattr(node, 'isEmpty') and node.isEmpty():
            return None
    except Exception:
        return None

    try:
        baseScale = node.getScale()
    except Exception:
        return None

    settle = finishScale if finishScale is not None else baseScale
    sx, sy, sz, squashSec = squashRow[0], squashRow[1], squashRow[2], squashRow[3]
    tx, ty, tz, stretchSec = (
        stretchRow[0], stretchRow[1], stretchRow[2], stretchRow[3])

    ival = Sequence(
        LerpScaleInterval(
            node, squashSec, _tupleScale((sx, sy, sz), baseScale)),
        LerpScaleInterval(
            node, stretchSec, _tupleScale((tx, ty, tz), baseScale)),
        LerpScaleInterval(node, settleSec, settle),
        name=name,
    )
    ival.start()
    return ival


def playImpactSquash(node, hitIndex=0, finishScale=None, name='hackslashImpactSquash'):
    """Brief scale squash → recover stretch → settle. Returns a started Sequence.

    Tunables come from HackSlashConfig.HIT_IMPACT_*. Callers own cleanup via
    finish() on the returned interval (or pass finishScale to snap back).
    """
    squashRow = HackSlashConfig.HIT_IMPACT_SQUASH[
        min(hitIndex, len(HackSlashConfig.HIT_IMPACT_SQUASH) - 1)]
    stretchRow = HackSlashConfig.HIT_IMPACT_STRETCH[
        min(hitIndex, len(HackSlashConfig.HIT_IMPACT_STRETCH) - 1)]
    return _playScalePulse(
        node, squashRow, stretchRow, HackSlashConfig.HIT_IMPACT_SETTLE_SEC,
        finishScale=finishScale, name=name)


def playFinisherSlam(node, finishScale=None, name='hackslashFinisherSlam'):
    """Last-hit rubber-hose slam: bigger pancake squash → taller stretch settle.

    Distinct from mid-combo HIT_IMPACT so the stretch-punch finisher reads as a
    cartoon thud without changing earlier combo hits.
    """
    return _playScalePulse(
        node,
        HackSlashConfig.FINISHER_SLAM_SQUASH,
        HackSlashConfig.FINISHER_SLAM_STRETCH,
        HackSlashConfig.FINISHER_SLAM_SETTLE_SEC,
        finishScale=finishScale,
        name=name)


def sampleShakeOffset(amplitude):
    """One-frame random camera offset for optional finisher screen shake."""
    amp = float(amplitude)
    if amp <= 0.0:
        return Vec3(0.0, 0.0, 0.0)
    return Vec3(
        (random.random() * 2.0 - 1.0) * amp,
        (random.random() * 2.0 - 1.0) * amp * 0.55,
        (random.random() * 2.0 - 1.0) * amp * 0.85,
    )


def playPlayerHitReact(node, finishScale=None, name='hackslashPlayerHitReact'):
    """Player-side hit-react: flatter squash, springy stretch recover."""
    sx, sy, sz, squashSec = HackSlashConfig.PLAYER_HIT_REACT_SQUASH
    tx, ty, tz, stretchSec = HackSlashConfig.PLAYER_HIT_REACT_STRETCH
    return _playScalePulse(
        node,
        (sx, sy, sz, squashSec),
        (tx, ty, tz, stretchSec),
        HackSlashConfig.PLAYER_HIT_REACT_SETTLE_SEC,
        finishScale=finishScale if finishScale is not None else Point3(1.0, 1.0, 1.0),
        name=name)


def buildLaunchHangInterval(node, peak, hangSec, hoverAmp, stretchScale,
                             name='hackslashLaunchHang'):
    """Apex float: slight hover bob + flat squash → tall spring (does not start).

    Replaces a frozen Wait at peak so launched corrupt toons read as rubber-hose
    hang before fall. Returns a Sequence, or Wait(hangSec) if node/timing unusable.
    """
    hangSec = max(0.0, float(hangSec))
    if hangSec <= 0.0 or node is None:
        return Wait(hangSec) if hangSec > 0.0 else Wait(0.0)

    hoverAmp = max(0.0, float(hoverAmp))
    hover = Point3(peak[0], peak[1], peak[2] + hoverAmp)
    # Split hang: rise bob, then settle; squash overlaps the rise, stretch the settle.
    upSec = hangSec * 0.42
    downSec = max(0.01, hangSec - upSec)
    sx, sy, sz, squashSec = HackSlashConfig.LAUNCH_HANG_SQUASH
    tx, ty, tz, stretchSec = HackSlashConfig.LAUNCH_HANG_STRETCH
    # Cap scale beats inside the hang window so timing never overruns.
    squashSec = min(float(squashSec), upSec)
    stretchSec = min(float(stretchSec), downSec)
    squashScale = Point3(sx, sy, sz)
    hangStretch = Point3(tx, ty, tz)
    holdStretch = stretchScale if stretchScale is not None else hangStretch

    return Sequence(
        Parallel(
            LerpPosInterval(node, upSec, hover, blendType='easeOut'),
            Sequence(
                LerpScaleInterval(
                    node, squashSec, squashScale, blendType='easeOut'),
                LerpScaleInterval(
                    node, max(0.01, upSec - squashSec), squashScale),
            ),
        ),
        Parallel(
            LerpPosInterval(node, downSec, peak, blendType='easeIn'),
            Sequence(
                LerpScaleInterval(
                    node, stretchSec, hangStretch, blendType='easeOut'),
                LerpScaleInterval(
                    node, max(0.01, downSec - stretchSec), holdStretch),
            ),
        ),
        name=name,
    )


def spawnHangSparks(origin, parent=None, name='hackslashHangSparks'):
    """Warm cartoon spark pops at apex. Returns (Parallel|None, nodeList).

    Caller owns cleanup of returned nodes (pause Parallel then removeNode).
    """
    count = int(HackSlashConfig.LAUNCH_HANG_SPARK_COUNT)
    if count <= 0 or origin is None:
        return None, []

    parentNP = parent
    if parentNP is None:
        try:
            parentNP = render  # noqa: F821
        except Exception:
            return None, []

    size = float(HackSlashConfig.LAUNCH_HANG_SPARK_SIZE)
    drift = float(HackSlashConfig.LAUNCH_HANG_SPARK_DRIFT)
    lift = float(HackSlashConfig.LAUNCH_HANG_SPARK_LIFT)
    sec = float(HackSlashConfig.LAUNCH_HANG_SPARK_SEC)
    r, g, b, a = HackSlashConfig.LAUNCH_HANG_SPARK_COLOR
    nodes = []
    parts = []

    for i in range(count):
        try:
            cm = CardMaker('%s-%s' % (name, i))
            cm.setFrame(-size, size, -size, size)
            spark = parentNP.attachNewNode(cm.generate())
            spark.setTransparency(TransparencyAttrib.MAlpha)
            spark.setColor(r, g, b, 1)
            spark.setColorScale(r, g, b, a)
            angle = (2.0 * pi * i) / float(count) + 0.35
            ox = cos(angle) * 0.35
            oy = sin(angle) * 0.35
            spark.setPos(
                origin[0] + ox,
                origin[1] + oy,
                origin[2] + lift * 0.35)
            spark.setScale(0.45 + 0.08 * (i % 3))
            spark.setBin('transparent', 22)
            spark.setDepthWrite(False)
            spark.setBillboardPointEye()
        except Exception:
            continue

        end = Point3(
            spark.getX() + cos(angle) * drift,
            spark.getY() + sin(angle) * drift,
            spark.getZ() + lift + 0.12 * (i % 2))
        parts.append(Parallel(
            LerpPosInterval(spark, sec, end, blendType='easeOut'),
            LerpScaleInterval(spark, sec, 0.04, blendType='easeIn'),
            LerpColorScaleInterval(
                spark, sec, Vec4(r, g, b, 0), blendType='easeIn'),
        ))
        nodes.append(spark)

    if not parts:
        return None, []
    ival = Parallel(*parts, name=name)
    return ival, nodes


def clearHangSparks(nodes):
    """Remove spark CardMaker nodes spawned for a launch hang."""
    for np in list(nodes or []):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass


def _hangCreamTablePick(table, hitIndex):
    """Pick a per-hit hang-cream tunable (scalar or mid/finisher tuple)."""
    if isinstance(table, (tuple, list)):
        if not table:
            return 0
        return table[min(max(0, int(hitIndex)), len(table) - 1)]
    return table


def spawnCreamHangSparkles(origin, hitIndex=0, parent=None,
                           name='hackslashCreamHangSparkles'):
    """Cream flecks + soft halo at juggle hang apex. Returns (Parallel|None, nodes).

    World-space rubber-hose cream glitter meant to layer with
    buildLaunchHangInterval — not KH glitter, and not aspect2d (CreamSlamFlashFx
    owns the finisher screen flash). Caller owns cleanup.
    """
    if origin is None or not getattr(
            HackSlashConfig, 'LAUNCH_HANG_CREAM_ENABLED', True):
        return None, []

    parentNP = parent
    if parentNP is None:
        try:
            parentNP = render  # noqa: F821
        except Exception:
            return None, []

    creamCount = int(_hangCreamTablePick(
        HackSlashConfig.LAUNCH_HANG_CREAM_COUNT, hitIndex))
    streakCount = int(_hangCreamTablePick(
        HackSlashConfig.LAUNCH_HANG_CREAM_STREAK_COUNT, hitIndex))
    if creamCount + streakCount <= 0 and not getattr(
            HackSlashConfig, 'LAUNCH_HANG_CREAM_HALO_ENABLED', True):
        return None, []

    size = float(HackSlashConfig.LAUNCH_HANG_CREAM_SIZE)
    streakSize = float(HackSlashConfig.LAUNCH_HANG_CREAM_STREAK_SIZE)
    drift = float(_hangCreamTablePick(
        HackSlashConfig.LAUNCH_HANG_CREAM_DRIFT, hitIndex))
    lift = float(HackSlashConfig.LAUNCH_HANG_CREAM_LIFT)
    sec = float(HackSlashConfig.LAUNCH_HANG_CREAM_SEC)
    ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])

    nodes = []
    parts = []

    def _spawnFleck(index, total, color, endColor, liftBias, nameSuffix,
                    cardSize, elongated=False):
        if total <= 0:
            return
        r, g, b, a = color
        er, eg, eb, ea = endColor
        angle = (2.0 * pi * index) / float(max(1, total)) + liftBias
        try:
            cm = CardMaker('%s-%s-%s' % (name, nameSuffix, index))
            if elongated or index % 2 == 1:
                cm.setFrame(
                    -cardSize * 0.35, cardSize * 0.35,
                    -cardSize * 1.35, cardSize * 1.35)
            else:
                cm.setFrame(
                    -cardSize, cardSize, -cardSize * 0.85, cardSize * 0.85)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, a)
            start = Point3(
                ox + cos(angle) * 0.22,
                oy + sin(angle) * 0.22,
                oz + lift * 0.2 + 0.06 * (index % 3))
            fleck.setPos(start)
            fleck.setScale(0.5 + 0.12 * (index % 3))
            fleck.setBin('transparent', 23)
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return
        end = Point3(
            start[0] + cos(angle) * drift,
            start[1] + sin(angle) * drift,
            start[2] + lift + 0.14 * (index % 2))
        parts.append(Parallel(
            LerpPosInterval(fleck, sec, end, blendType='easeOut'),
            LerpScaleInterval(fleck, sec, 0.04, blendType='easeIn'),
            LerpColorScaleInterval(
                fleck, sec, Vec4(er, eg, eb, ea), blendType='easeIn'),
        ))
        nodes.append(fleck)

    for i in range(creamCount):
        _spawnFleck(
            i, creamCount,
            HackSlashConfig.LAUNCH_HANG_CREAM_COLOR,
            HackSlashConfig.LAUNCH_HANG_CREAM_END,
            0.22, 'cream', size)
    for i in range(streakCount):
        _spawnFleck(
            i, streakCount,
            HackSlashConfig.LAUNCH_HANG_CREAM_STREAK_COLOR,
            HackSlashConfig.LAUNCH_HANG_CREAM_STREAK_END,
            0.55, 'streak', streakSize, elongated=True)

    if getattr(HackSlashConfig, 'LAUNCH_HANG_CREAM_HALO_ENABLED', True):
        half = float(HackSlashConfig.LAUNCH_HANG_CREAM_HALO_HALF)
        startScale = float(HackSlashConfig.LAUNCH_HANG_CREAM_HALO_START)
        peakScale = float(HackSlashConfig.LAUNCH_HANG_CREAM_HALO_PEAK)
        haloSec = float(HackSlashConfig.LAUNCH_HANG_CREAM_HALO_SEC)
        peakA = float(HackSlashConfig.LAUNCH_HANG_CREAM_HALO_PEAK_ALPHA)
        hr, hg, hb, _ha = HackSlashConfig.LAUNCH_HANG_CREAM_HALO_COLOR
        try:
            cm = CardMaker('%s-halo' % name)
            cm.setFrame(-half, half, -half, half)
            halo = parentNP.attachNewNode(cm.generate())
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(hr, hg, hb, 1)
            halo.setColorScale(hr, hg, hb, peakA)
            halo.setPos(ox, oy, oz + lift * 0.15)
            halo.setScale(startScale)
            halo.setBin('transparent', 22)
            halo.setDepthWrite(False)
            halo.setBillboardPointEye()
            parts.append(Parallel(
                LerpScaleInterval(
                    halo, max(0.01, haloSec), peakScale, blendType='easeOut'),
                Sequence(
                    Wait(max(0.0, haloSec * 0.2)),
                    LerpColorScaleInterval(
                        halo, max(0.01, haloSec * 0.8),
                        Vec4(hr, hg, hb, 0), blendType='easeIn'),
                ),
            ))
            nodes.append(halo)
        except Exception:
            pass

    if not parts:
        return None, []
    ival = Parallel(*parts, name=name)
    ival.start()
    return ival, nodes


def clearCreamHangSparkles(nodes):
    """Remove cream hang sparkle / halo CardMaker nodes."""
    clearHangSparks(nodes)


def playComboCounterPop(node, settleScale, name='hackslashComboHosePop'):
    """aspect2d combo HUD: flat squash → tall stretch → settle. Starts + returns.

    settleScale is the uniform TextNode scale to land on. Squash/stretch
    multipliers come from HackSlashConfig.COMBO_COUNTER_*.
    """
    if node is None:
        return None
    try:
        if hasattr(node, 'isEmpty') and node.isEmpty():
            return None
    except Exception:
        return None

    settle = max(0.001, float(settleScale))
    sx, sy, sz, squashSec = HackSlashConfig.COMBO_COUNTER_SQUASH
    tx, ty, tz, stretchSec = HackSlashConfig.COMBO_COUNTER_STRETCH
    settleSec = float(HackSlashConfig.COMBO_COUNTER_SETTLE_SEC)
    settlePt = Point3(settle, settle, settle)
    squashPt = Point3(settle * sx, settle * sy, settle * sz)
    stretchPt = Point3(settle * tx, settle * ty, settle * tz)

    try:
        node.setScale(settlePt)
    except Exception:
        return None

    ival = Sequence(
        LerpScaleInterval(node, float(squashSec), squashPt, blendType='easeOut'),
        LerpScaleInterval(
            node, float(stretchSec), stretchPt, blendType='easeOut'),
        LerpScaleInterval(node, settleSec, settlePt, blendType='easeIn'),
        name=name,
    )
    ival.start()
    return ival


def spawnComboInkFlecks(origin, parent=None, name='hackslashComboInkFlecks'):
    """Tiny aspect2d ink flecks near the combo counter. Returns (Parallel|None, nodes).

    Caller owns cleanup (pause Parallel then clearComboInkFlecks).
    """
    count = int(HackSlashConfig.COMBO_COUNTER_FLECK_COUNT)
    if count <= 0 or origin is None:
        return None, []

    parentNP = parent
    if parentNP is None:
        try:
            parentNP = aspect2d  # noqa: F821
        except Exception:
            return None, []

    size = float(HackSlashConfig.COMBO_COUNTER_FLECK_SIZE)
    drift = float(HackSlashConfig.COMBO_COUNTER_FLECK_DRIFT)
    sec = float(HackSlashConfig.COMBO_COUNTER_FLECK_SEC)
    r, g, b, a = HackSlashConfig.COMBO_COUNTER_FLECK_COLOR
    er, eg, eb, ea = HackSlashConfig.COMBO_COUNTER_FLECK_END_COLOR
    ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])

    nodes = []
    parts = []
    for i in range(count):
        try:
            cm = CardMaker('%s-%s' % (name, i))
            cm.setFrame(-size, size, -size, size)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, a)
            angle = (2.0 * pi * i) / float(count) + 0.55
            # Spread sideways/up from the HUD number — tiny ink flecks, not sparks.
            start = Point3(
                ox + cos(angle) * 0.03,
                oy,
                oz + sin(angle) * 0.02 + 0.02)
            fleck.setPos(start)
            fleck.setScale(0.55 + 0.12 * (i % 3))
            fleck.setBin('fixed', 56)
            fleck.setDepthWrite(False)
        except Exception:
            continue

        end = Point3(
            start[0] + cos(angle) * drift,
            oy,
            start[2] + abs(sin(angle)) * drift + 0.04)
        parts.append(Parallel(
            LerpPosInterval(fleck, sec, end, blendType='easeOut'),
            LerpScaleInterval(fleck, sec, 0.05, blendType='easeIn'),
            LerpColorScaleInterval(
                fleck, sec, Vec4(er, eg, eb, ea), blendType='easeIn'),
        ))
        nodes.append(fleck)

    if not parts:
        return None, []
    ival = Parallel(*parts, name=name)
    ival.start()
    return ival, nodes


def clearComboInkFlecks(nodes):
    """Remove ink-fleck CardMaker nodes spawned for a combo counter pop."""
    for np in list(nodes or []):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass


def spawnComboCreamSparkles(origin, parent=None, name='hackslashComboCreamSparkles'):
    """aspect2d cream flecks + thin streaks near the combo counter tick.

    Layers with playComboCounterPop + spawnComboInkFlecks — warm cream glitter,
    not KH sparkles. Returns (Parallel|None, nodes). Caller owns cleanup.
    """
    if origin is None or not getattr(
            HackSlashConfig, 'COMBO_COUNTER_CREAM_ENABLED', True):
        return None, []

    creamCount = int(HackSlashConfig.COMBO_COUNTER_CREAM_COUNT)
    streakCount = int(HackSlashConfig.COMBO_COUNTER_CREAM_STREAK_COUNT)
    if creamCount + streakCount <= 0:
        return None, []

    parentNP = parent
    if parentNP is None:
        try:
            parentNP = aspect2d  # noqa: F821
        except Exception:
            return None, []

    size = float(HackSlashConfig.COMBO_COUNTER_CREAM_SIZE)
    streakSize = float(HackSlashConfig.COMBO_COUNTER_CREAM_STREAK_SIZE)
    drift = float(HackSlashConfig.COMBO_COUNTER_CREAM_DRIFT)
    sec = float(HackSlashConfig.COMBO_COUNTER_CREAM_SEC)
    binSort = int(HackSlashConfig.COMBO_COUNTER_CREAM_BIN)
    ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])

    nodes = []
    parts = []

    def _spawn(index, total, color, endColor, liftBias, nameSuffix, cardSize,
               elongated=False):
        if total <= 0:
            return
        r, g, b, a = color
        er, eg, eb, ea = endColor
        angle = (2.0 * pi * index) / float(max(1, total)) + liftBias
        try:
            cm = CardMaker('%s-%s-%s' % (name, nameSuffix, index))
            if elongated:
                cm.setFrame(
                    -cardSize * 0.35, cardSize * 0.35,
                    -cardSize * 1.6, cardSize * 1.6)
            else:
                cm.setFrame(-cardSize, cardSize, -cardSize, cardSize)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, a)
            # Orbit a bit farther than ink flecks so cream reads as sparkle.
            start = Point3(
                ox + cos(angle) * 0.045,
                oy,
                oz + sin(angle) * 0.03 + 0.03)
            fleck.setPos(start)
            fleck.setScale(0.6 + 0.1 * (index % 3))
            if elongated:
                fleck.setR(angle * 57.3)
            fleck.setBin('fixed', binSort)
            fleck.setDepthWrite(False)
        except Exception:
            return
        end = Point3(
            start[0] + cos(angle) * drift,
            oy,
            start[2] + abs(sin(angle)) * drift + 0.05)
        parts.append(Parallel(
            LerpPosInterval(fleck, sec, end, blendType='easeOut'),
            LerpScaleInterval(fleck, sec, 0.04, blendType='easeIn'),
            LerpColorScaleInterval(
                fleck, sec, Vec4(er, eg, eb, ea), blendType='easeIn'),
        ))
        nodes.append(fleck)

    for i in range(creamCount):
        _spawn(
            i, creamCount,
            HackSlashConfig.COMBO_COUNTER_CREAM_COLOR,
            HackSlashConfig.COMBO_COUNTER_CREAM_END,
            0.35, 'cream', size)
    for i in range(streakCount):
        _spawn(
            i, streakCount,
            HackSlashConfig.COMBO_COUNTER_CREAM_STREAK_COLOR,
            HackSlashConfig.COMBO_COUNTER_CREAM_STREAK_END,
            0.9, 'streak', streakSize, elongated=True)

    if not parts:
        return None, []
    ival = Parallel(*parts, name=name)
    ival.start()
    return ival, nodes


def clearComboCreamSparkles(nodes):
    """Remove cream-sparkle CardMaker nodes from a combo counter tick."""
    clearComboInkFlecks(nodes)


def playSoftLockReticlePop(node, settleScale, name='hackslashSoftLockReticlePop'):
    """World soft-lock reticle: flat squash → tall stretch → settle. Starts.

    settleScale is the uniform NodePath scale to land on. Squash/stretch
    multipliers come from HackSlashConfig.SOFT_LOCK_RETICLE_*.
    """
    if node is None:
        return None
    try:
        if hasattr(node, 'isEmpty') and node.isEmpty():
            return None
    except Exception:
        return None

    settle = max(0.001, float(settleScale))
    sx, sy, sz, squashSec = HackSlashConfig.SOFT_LOCK_RETICLE_SQUASH
    tx, ty, tz, stretchSec = HackSlashConfig.SOFT_LOCK_RETICLE_STRETCH
    settleSec = float(HackSlashConfig.SOFT_LOCK_RETICLE_SETTLE_SEC)
    settlePt = Point3(settle, settle, settle)
    squashPt = Point3(settle * sx, settle * sy, settle * sz)
    stretchPt = Point3(settle * tx, settle * ty, settle * tz)

    try:
        node.setScale(settlePt)
    except Exception:
        return None

    ival = Sequence(
        LerpScaleInterval(node, float(squashSec), squashPt, blendType='easeOut'),
        LerpScaleInterval(
            node, float(stretchSec), stretchPt, blendType='easeOut'),
        LerpScaleInterval(node, settleSec, settlePt, blendType='easeIn'),
        name=name,
    )
    ival.start()
    return ival


def spawnSoftLockAccents(origin, parent=None, name='hackslashSoftLockAccents'):
    """Cream + ink flecks at a soft-lock snap. Returns (Parallel|None, nodes).

    Caller owns cleanup (pause Parallel then clearSoftLockAccents).
    """
    if origin is None:
        return None, []

    parentNP = parent
    if parentNP is None:
        try:
            parentNP = render  # noqa: F821
        except Exception:
            return None, []

    size = float(HackSlashConfig.SOFT_LOCK_ACCENT_SIZE)
    drift = float(HackSlashConfig.SOFT_LOCK_ACCENT_DRIFT)
    sec = float(HackSlashConfig.SOFT_LOCK_ACCENT_SEC)
    creamCount = int(HackSlashConfig.SOFT_LOCK_ACCENT_CREAM_COUNT)
    inkCount = int(HackSlashConfig.SOFT_LOCK_ACCENT_INK_COUNT)
    if creamCount + inkCount <= 0:
        return None, []

    ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])
    nodes = []
    parts = []

    def _spawn(index, total, color, endColor, liftBias, nameSuffix):
        if total <= 0:
            return
        r, g, b, a = color
        er, eg, eb, ea = endColor
        angle = (2.0 * pi * index) / float(max(1, total)) + liftBias
        try:
            cm = CardMaker('%s-%s-%s' % (name, nameSuffix, index))
            cm.setFrame(-size, size, -size, size)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, a)
            start = Point3(
                ox + cos(angle) * 0.12,
                oy + sin(angle) * 0.12,
                oz + 0.04 * (index % 2))
            fleck.setPos(start)
            fleck.setScale(0.5 + 0.12 * (index % 3))
            fleck.setBin('transparent', 27)
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return
        end = Point3(
            start[0] + cos(angle) * drift,
            start[1] + sin(angle) * drift,
            start[2] + 0.25 + 0.1 * (index % 2))
        parts.append(Parallel(
            LerpPosInterval(fleck, sec, end, blendType='easeOut'),
            LerpScaleInterval(fleck, sec, 0.05, blendType='easeIn'),
            LerpColorScaleInterval(
                fleck, sec, Vec4(er, eg, eb, ea), blendType='easeIn'),
        ))
        nodes.append(fleck)

    for i in range(creamCount):
        _spawn(
            i, creamCount,
            HackSlashConfig.SOFT_LOCK_ACCENT_CREAM_COLOR,
            HackSlashConfig.SOFT_LOCK_ACCENT_CREAM_END,
            0.2, 'cream')
    for i in range(inkCount):
        _spawn(
            i, inkCount,
            HackSlashConfig.SOFT_LOCK_ACCENT_INK_COLOR,
            HackSlashConfig.SOFT_LOCK_ACCENT_INK_END,
            0.85, 'ink')

    if not parts:
        return None, []
    ival = Parallel(*parts, name=name)
    ival.start()
    return ival, nodes


def clearSoftLockAccents(nodes):
    """Remove cream/ink accent CardMaker nodes from a soft-lock snap."""
    for np in list(nodes or []):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass


def _hitSparkTablePick(table, hitIndex):
    """Pick a per-hit tunable; scalars still work for older configs."""
    if isinstance(table, (int, float)):
        return float(table)
    return float(table[min(max(0, int(hitIndex)), len(table) - 1)])


def spawnHitSparkFlecks(origin, hitIndex=0, parent=None,
                        name='hackslashHitSparkFlecks'):
    """Cream + ink fleck sparkles at a melee connect. Returns (Parallel|None, nodes).

    Short rubber-hose burst meant to layer with playImpactSquash /
    playFinisherSlam — not KH glitter. Caller owns cleanup (pause Parallel
    then clearHitSparkFlecks).
    """
    if origin is None or not getattr(HackSlashConfig, 'HIT_SPARK_ENABLED', True):
        return None, []

    parentNP = parent
    if parentNP is None:
        try:
            parentNP = render  # noqa: F821
        except Exception:
            return None, []

    creamCount = int(_hitSparkTablePick(
        HackSlashConfig.HIT_SPARK_CREAM_COUNT, hitIndex))
    inkCount = int(_hitSparkTablePick(
        HackSlashConfig.HIT_SPARK_INK_COUNT, hitIndex))
    streakCount = int(_hitSparkTablePick(
        HackSlashConfig.HIT_SPARK_STREAK_COUNT, hitIndex))
    if creamCount + inkCount + streakCount <= 0:
        return None, []

    size = float(HackSlashConfig.HIT_SPARK_SIZE)
    streakSize = float(HackSlashConfig.HIT_SPARK_STREAK_SIZE)
    drift = float(_hitSparkTablePick(HackSlashConfig.HIT_SPARK_DRIFT, hitIndex))
    liftBurst = float(HackSlashConfig.HIT_SPARK_LIFT_BURST)
    sec = float(HackSlashConfig.HIT_SPARK_SEC)
    ox, oy, oz = float(origin[0]), float(origin[1]), float(origin[2])

    nodes = []
    parts = []

    def _spawnFleck(index, total, color, endColor, liftBias, nameSuffix,
                    cardSize, elongated=False):
        if total <= 0:
            return
        r, g, b, a = color
        er, eg, eb, ea = endColor
        angle = (2.0 * pi * index) / float(max(1, total)) + liftBias
        try:
            cm = CardMaker('%s-%s-%s' % (name, nameSuffix, index))
            # Alternate fat blobs vs thin streaks for rubber-hose variety.
            if elongated or index % 2 == 1:
                cm.setFrame(
                    -cardSize * 0.35, cardSize * 0.35,
                    -cardSize * 1.25, cardSize * 1.25)
            else:
                cm.setFrame(-cardSize, cardSize, -cardSize * 0.85, cardSize * 0.85)
            fleck = parentNP.attachNewNode(cm.generate())
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, a)
            start = Point3(
                ox + cos(angle) * 0.14,
                oy + sin(angle) * 0.14,
                oz + 0.05 * (index % 3))
            fleck.setPos(start)
            fleck.setScale(0.5 + 0.14 * (index % 3))
            fleck.setBin('transparent', 24)
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return
        end = Point3(
            start[0] + cos(angle) * drift,
            start[1] + sin(angle) * drift,
            start[2] + liftBurst + 0.12 * (index % 2))
        parts.append(Parallel(
            LerpPosInterval(fleck, sec, end, blendType='easeOut'),
            LerpScaleInterval(fleck, sec, 0.04, blendType='easeIn'),
            LerpColorScaleInterval(
                fleck, sec, Vec4(er, eg, eb, ea), blendType='easeIn'),
        ))
        nodes.append(fleck)

    for i in range(creamCount):
        _spawnFleck(
            i, creamCount,
            HackSlashConfig.HIT_SPARK_CREAM_COLOR,
            HackSlashConfig.HIT_SPARK_CREAM_END,
            0.18, 'cream', size)
    for i in range(inkCount):
        _spawnFleck(
            i, inkCount,
            HackSlashConfig.HIT_SPARK_INK_COLOR,
            HackSlashConfig.HIT_SPARK_INK_END,
            0.9, 'ink', size)
    for i in range(streakCount):
        _spawnFleck(
            i, streakCount,
            HackSlashConfig.HIT_SPARK_STREAK_COLOR,
            HackSlashConfig.HIT_SPARK_STREAK_END,
            0.45, 'streak', streakSize, elongated=True)

    if not parts:
        return None, []
    ival = Parallel(*parts, name=name)
    ival.start()
    return ival, nodes


def clearHitSparkFlecks(nodes):
    """Remove cream/ink hit-spark CardMaker nodes from a melee connect."""
    for np in list(nodes or []):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass


def finishInterval(ival, node=None, restoreScale=None):
    """Stop a juice interval and optionally snap scale back."""
    if ival is not None:
        try:
            ival.finish()
        except Exception:
            try:
                ival.pause()
            except Exception:
                pass
    if node is not None and restoreScale is not None:
        try:
            node.setScale(restoreScale)
        except Exception:
            pass


def pauseIntervals(intervals):
    """Pause every live interval (hitstop freeze)."""
    for ival in intervals or ():
        try:
            if ival:
                ival.pause()
        except Exception:
            pass


def resumeIntervals(intervals):
    """Resume intervals paused by hitstop."""
    for ival in intervals or ():
        try:
            if ival:
                ival.resume()
        except Exception:
            pass


def freezeActorPlayRates(actors):
    """Zero anim play rates so the silhouette freezes. Returns restore tuples.

    Each restore entry is (actor, animName, rate). Empty when freeze is off.
    """
    if not getattr(HackSlashConfig, 'HITSTOP_FREEZE_ANIMS', True):
        return []
    saved = []
    for actor in actors or ():
        if actor is None:
            continue
        try:
            anim = None
            if hasattr(actor, 'getCurrentAnim'):
                anim = actor.getCurrentAnim()
            if not anim:
                continue
            rate = 1.0
            if hasattr(actor, 'getPlayRate'):
                try:
                    rate = float(actor.getPlayRate(anim))
                except Exception:
                    rate = float(actor.getPlayRate())
            if hasattr(actor, 'setPlayRate'):
                actor.setPlayRate(0.0, anim)
                saved.append((actor, anim, rate))
        except Exception:
            pass
    return saved


def restoreActorPlayRates(saved):
    """Restore play rates captured by freezeActorPlayRates."""
    for entry in saved or ():
        try:
            actor, anim, rate = entry
            if actor is None or not anim:
                continue
            if hasattr(actor, 'setPlayRate'):
                actor.setPlayRate(float(rate), anim)
        except Exception:
            pass
