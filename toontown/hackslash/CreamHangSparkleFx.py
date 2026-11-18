"""Rubber-hose cream sparkle during air-juggle hang.

World-space cream flecks + soft cream halo at the launcher apex so suspended
corrupt toons read before fall. Layers with HitJuice hang hover/squash and
does not fight CreamSlamFlashFx (aspect2d finisher connect flash). Toontown
spiritual-sequel tone only — no keyblades / no KH branding.
"""

from panda3d.core import Point3

from direct.interval.IntervalGlobal import Func, Sequence, Wait

from . import HackSlashConfig
from . import HitJuice


class CreamHangSparkleFx(object):
    """Owns one short cream sparkle burst at an air-juggle hang apex."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._sparkleIval = None
        self._nodes = []

    def play(self, origin=None, hitIndex=0, parent=None):
        """Spawn cream hang sparkles. Returns started Sequence or None.

        `origin` is render-space hang peak. Falls back to classic hang sparks
        when LAUNCH_HANG_CREAM_ENABLED is False.
        """
        self.clear()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None

        if origin is None:
            return None
        try:
            origin = Point3(
                float(origin[0]), float(origin[1]), float(origin[2]))
        except Exception:
            return None

        useCream = getattr(
            HackSlashConfig, 'LAUNCH_HANG_CREAM_ENABLED', True)
        if useCream:
            sparkleIval, nodes = HitJuice.spawnCreamHangSparkles(
                origin,
                hitIndex=hitIndex,
                parent=parentNP,
                name=self.avatar.uniqueName('hackslashCreamHangSparkles'))
        else:
            sparkleIval, nodes = HitJuice.spawnHangSparks(
                origin,
                parent=parentNP,
                name=self.avatar.uniqueName('hackslashHangSparks'))

        if sparkleIval is None and not nodes:
            return None

        self._sparkleIval = sparkleIval
        self._nodes = nodes
        # Cream path starts inside HitJuice; classic hang sparks need a start.
        if sparkleIval is not None and not useCream:
            try:
                sparkleIval.start()
            except Exception:
                HitJuice.clearCreamHangSparkles(nodes)
                self._sparkleIval = None
                self._nodes = []
                return None
        try:
            if useCream:
                sec = float(HackSlashConfig.LAUNCH_HANG_CREAM_SEC)
            else:
                sec = float(HackSlashConfig.LAUNCH_HANG_SPARK_SEC)
        except Exception:
            sec = 0.28
        # Hold then retire nodes once the burst finishes.
        self._ival = Sequence(
            Wait(sec + 0.04),
            Func(self.clear),
            name=self.avatar.uniqueName('hackslashCreamHangSparkle'),
        )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop the burst and remove every cream hang sparkle node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._sparkleIval is not None:
            try:
                self._sparkleIval.pause()
            except Exception:
                pass
            self._sparkleIval = None
        HitJuice.clearCreamHangSparkles(self._nodes)
        self._nodes = []
