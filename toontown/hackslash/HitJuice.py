"""Rubber-hose impact squash/stretch juice for Oswald stretch-punch melee.

Shared helpers so MeleeCombat, demo hostiles, and corrupt hit-reacts share one
cartoon scale curve: brief flat squash → tall recover stretch → settle.
Combo finishers use playFinisherSlam for a heavier rubber-hose slam beat.
Launcher hang uses buildLaunchHangInterval + spawnHangSparks for a readable
airborne float before fall.
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
