"""Rubber-hose soft-lock reticle pop for hackslash melee.

World-space cream brackets over the sticky soft-lock target. On acquire/snap,
plays a short squash → stretch → settle hose pop plus cream/ink accent flecks.
Toontown spiritual-sequel tone only — no keyblades / no KH branding.
"""

from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib

from . import HackSlashConfig
from . import HitJuice


class SoftLockReticleFx(object):
    """Owns the soft-lock reticle node, snap pop, and accent flecks."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._root = None
        self._target = None
        self._popIval = None
        self._accentIval = None
        self._accentNodes = []

    def clear(self):
        """Stop juice and remove reticle + accents."""
        self._clearPop()
        self._clearAccents()
        self._target = None
        if self._root is not None:
            try:
                if not self._root.isEmpty():
                    self._root.removeNode()
            except Exception:
                pass
            self._root = None

    def hide(self):
        """Drop lock without destroying the helper (melee still enabled)."""
        self._clearPop()
        self._clearAccents()
        self._target = None
        if self._root is not None:
            try:
                self._root.hide()
            except Exception:
                pass

    def attach(self, target, snapped=False):
        """Follow target; if snapped, play the hose pop + cream/ink accents."""
        if target is None:
            self.hide()
            return
        self._ensureRoot()
        if self._root is None:
            return
        self._target = target
        try:
            self._root.show()
        except Exception:
            pass
        self._followTarget()
        if snapped:
            self.playSnapPop()

    def tick(self):
        """Keep the reticle parked above the current soft-lock target."""
        if self._target is None or self._root is None:
            return
        self._followTarget()

    def playSnapPop(self):
        """Brief rubber-hose scale pop + cream/ink accent flecks at the reticle."""
        if self._root is None:
            return
        self._clearPop()
        self._clearAccents()
        settle = float(HackSlashConfig.SOFT_LOCK_RETICLE_SETTLE_SCALE)
        self._popIval = HitJuice.playSoftLockReticlePop(
            self._root, settle,
            name=self.avatar.uniqueName('hackslashSoftLockReticlePop'))
        try:
            origin = self._root.getPos(render)  # noqa: F821
            parent = render  # noqa: F821
        except Exception:
            return
        accentIval, nodes = HitJuice.spawnSoftLockAccents(
            origin, parent=parent,
            name=self.avatar.uniqueName('hackslashSoftLockAccents'))
        self._accentIval = accentIval
        self._accentNodes = nodes

    def _ensureRoot(self):
        if self._root is not None:
            try:
                if not self._root.isEmpty():
                    return
            except Exception:
                self._root = None
        try:
            parent = render  # noqa: F821
        except Exception:
            return
        try:
            root = parent.attachNewNode(
                self.avatar.uniqueName('hackslashSoftLockReticle'))
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setBin('transparent', 26)
            root.setDepthWrite(False)
            root.setBillboardPointEye()
            half = float(HackSlashConfig.SOFT_LOCK_RETICLE_HALF)
            thick = float(HackSlashConfig.SOFT_LOCK_RETICLE_THICK)
            cr, cg, cb, ca = HackSlashConfig.SOFT_LOCK_RETICLE_COLOR
            ir, ig, ib, ia = HackSlashConfig.SOFT_LOCK_RETICLE_INK_COLOR
            # Four cream brackets + tiny ink diamond — reads as a cartoon lock,
            # not a KH command menu / keyblade lock-on glyph.
            for i, (hx, hz, ink) in enumerate((
                    (-half, half * 0.55, False),
                    (half, half * 0.55, False),
                    (-half, -half * 0.55, False),
                    (half, -half * 0.55, False),
                    (0.0, 0.0, True),
            )):
                cm = CardMaker('hackslash-softlock-arm-%s' % i)
                if ink:
                    cm.setFrame(-thick * 0.7, thick * 0.7, -thick * 0.7, thick * 0.7)
                else:
                    cm.setFrame(-thick, thick, -thick * 2.2, thick * 2.2)
                arm = root.attachNewNode(cm.generate())
                arm.setPos(hx, 0, hz)
                if ink:
                    arm.setColor(ir, ig, ib, 1)
                    arm.setColorScale(ir, ig, ib, ia)
                else:
                    arm.setColor(cr, cg, cb, 1)
                    arm.setColorScale(cr, cg, cb, ca)
                    # Rotate corner brackets so they read as L-shaped corners.
                    arm.setR(45.0 if (hx * hz) > 0 else -45.0)
            settle = float(HackSlashConfig.SOFT_LOCK_RETICLE_SETTLE_SCALE)
            root.setScale(settle, settle, settle)
            self._root = root
        except Exception:
            self._root = None

    def _followTarget(self):
        if self._root is None or self._target is None:
            return
        try:
            if hasattr(self._target, 'getHackSlashPos'):
                pos = self._target.getHackSlashPos()
            else:
                pos = self._target.getPos(render)  # noqa: F821
            lift = float(HackSlashConfig.SOFT_LOCK_RETICLE_LIFT)
            self._root.setPos(pos[0], pos[1], pos[2] + lift)
        except Exception:
            self.hide()

    def _clearPop(self):
        HitJuice.finishInterval(
            self._popIval, self._root,
            restoreScale=Point3(
                float(HackSlashConfig.SOFT_LOCK_RETICLE_SETTLE_SCALE),
                float(HackSlashConfig.SOFT_LOCK_RETICLE_SETTLE_SCALE),
                float(HackSlashConfig.SOFT_LOCK_RETICLE_SETTLE_SCALE)))
        self._popIval = None

    def _clearAccents(self):
        if self._accentIval is not None:
            try:
                self._accentIval.pause()
            except Exception:
                pass
            self._accentIval = None
        HitJuice.clearSoftLockAccents(self._accentNodes)
        self._accentNodes = []
