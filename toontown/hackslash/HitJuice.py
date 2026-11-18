"""Rubber-hose impact squash/stretch juice for Oswald stretch-punch melee.

Shared helpers so MeleeCombat, demo hostiles, and corrupt hit-reacts share one
cartoon scale curve: brief flat squash → tall recover stretch → settle.
Combo finishers use playFinisherSlam for a heavier rubber-hose slam beat.
No keyblades / no KH framing — Toontown rubber-hose only.
"""

import random

from panda3d.core import Point3, Vec3

from direct.interval.IntervalGlobal import LerpScaleInterval, Sequence

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
