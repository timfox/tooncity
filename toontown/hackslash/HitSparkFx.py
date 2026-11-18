"""Rubber-hose cream/ink fleck sparkles on melee hit connect.

Client juice when a stretch-punch lands: short cream spark streaks + ink
flecks burst at the hit, layered with the existing impact squash silhouette.
Toontown spiritual-sequel tone only — no keyblades / no KH branding.
"""

from panda3d.core import Point3

from direct.interval.IntervalGlobal import Func, Sequence, Wait

from . import HackSlashConfig
from . import HitJuice


class HitSparkFx(object):
    """Owns one short world-space cream/ink spark burst at a hit connect."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._ival = None
        self._fleckIval = None
        self._nodes = []

    def play(self, origin=None, hitIndex=0, parent=None):
        """Spawn cream/ink fleck sparkles. Returns started Sequence or None.

        `origin` is render-space; defaults to the local avatar at HIT_SPARK_LIFT.
        """
        if not getattr(HackSlashConfig, 'HIT_SPARK_ENABLED', True):
            return None
        self.clear()
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None

        if origin is None:
            try:
                pos = self.avatar.getPos(parentNP)
                origin = Point3(
                    pos[0], pos[1],
                    pos[2] + float(HackSlashConfig.HIT_SPARK_LIFT))
            except Exception:
                return None
        else:
            try:
                origin = Point3(
                    float(origin[0]), float(origin[1]), float(origin[2]))
            except Exception:
                return None

        fleckIval, nodes = HitJuice.spawnHitSparkFlecks(
            origin,
            hitIndex=hitIndex,
            parent=parentNP,
            name=self.avatar.uniqueName('hackslashHitSparkFlecks'))
        if fleckIval is None and not nodes:
            return None

        self._fleckIval = fleckIval
        self._nodes = nodes
        try:
            sec = float(HackSlashConfig.HIT_SPARK_SEC)
        except Exception:
            sec = 0.2
        # Fleck Parallel already started; hold then retire nodes.
        self._ival = Sequence(
            Wait(sec + 0.02),
            Func(self.clear),
            name=self.avatar.uniqueName('hackslashHitSpark'),
        )
        self._ival.start()
        return self._ival

    def clear(self):
        """Stop the burst and remove every cream/ink fleck node."""
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        if self._fleckIval is not None:
            try:
                self._fleckIval.pause()
            except Exception:
                pass
            self._fleckIval = None
        HitJuice.clearHitSparkFlecks(self._nodes)
        self._nodes = []
