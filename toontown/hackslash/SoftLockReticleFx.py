"""Rubber-hose soft-lock reticle pop for hackslash melee.

World-space cream brackets over the sticky soft-lock target. On acquire/snap,
plays a short squash → stretch → settle hose pop plus cream/ink accent flecks
and a brief FOV punch. Toontown spiritual-sequel tone only — no keyblades /
no KH branding.
"""

from panda3d.core import CardMaker, Point3, TransparencyAttrib

from direct.interval.IntervalGlobal import Func, Sequence
from direct.interval.LerpInterval import LerpFunc

from . import HackSlashConfig
from . import HitJuice


class SoftLockReticleFx(object):
    """Owns the soft-lock reticle node, snap pop, accents, and FOV punch."""

    def __init__(self, avatar, hitStop=None, beforeFov=None, fovBusy=None):
        self.avatar = avatar
        # Optional HitStopFx — FOV punch defers while connect freeze is live.
        self._hitStop = hitStop
        # Optional MeleeCombat FOV restore so soft-lock / finisher share lens.
        self._beforeFov = beforeFov
        # Optional gate — yield when finisher (or other) FOV already owns camLens.
        self._fovBusy = fovBusy
        self._root = None
        self._target = None
        self._popIval = None
        self._accentIval = None
        self._accentNodes = []
        self._fovIval = None
        self._baseFov = None
        self._pendingFov = False

    def clear(self):
        """Stop juice and remove reticle + accents."""
        self._pendingFov = False
        self.restoreFov()
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
        self._pendingFov = False
        self.restoreFov()
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
        self._flushPendingFov()
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
            # Still request FOV even if accents can't place.
            self._requestFovPunch()
            return
        accentIval, nodes = HitJuice.spawnSoftLockAccents(
            origin, parent=parent,
            name=self.avatar.uniqueName('hackslashSoftLockAccents'))
        self._accentIval = accentIval
        self._accentNodes = nodes
        self._requestFovPunch()

    def cancelPendingFov(self):
        """Drop a deferred soft-lock FOV punch (e.g. finisher took the lens)."""
        self._pendingFov = False

    def _fovIsBusy(self):
        if self._fovBusy is None:
            return False
        try:
            return bool(self._fovBusy())
        except Exception:
            return False

    def _requestFovPunch(self):
        """Queue or play the soft-lock FOV kick; defer during HitStopFx."""
        if not getattr(HackSlashConfig, 'SOFT_LOCK_FOV_ENABLED', True):
            return
        punch = float(getattr(HackSlashConfig, 'SOFT_LOCK_FOV_PUNCH', 0.0))
        if punch <= 0.0:
            return
        # Yield if finisher (or other) FOV already owns the lens.
        if self._fovIsBusy():
            self._pendingFov = False
            return
        # Compose with #68: don't fight mid-freeze FOV — flush after resume.
        if self._hitStop is not None and self._hitStop.isActive():
            self._pendingFov = True
            return
        self._pendingFov = False
        self._playFovPunch()

    def _flushPendingFov(self):
        if not self._pendingFov:
            return
        if self._fovIsBusy():
            self._pendingFov = False
            return
        if self._hitStop is not None and self._hitStop.isActive():
            return
        self._pendingFov = False
        self._playFovPunch()

    def _playFovPunch(self):
        """Quick FOV kick on soft-lock acquire — milder than finisher punch."""
        if self._fovIsBusy():
            return
        if self._beforeFov is not None:
            try:
                self._beforeFov()
            except Exception:
                pass
        self.restoreFov()
        try:
            lens = base.camLens  # noqa: F821
        except Exception:
            return
        try:
            self._baseFov = lens.getFov()
            baseFov = (
                float(self._baseFov[0])
                if hasattr(self._baseFov, '__getitem__')
                else float(self._baseFov))
        except Exception:
            return
        punch = float(HackSlashConfig.SOFT_LOCK_FOV_PUNCH)
        peak = baseFov + punch
        inSec = float(HackSlashConfig.SOFT_LOCK_FOV_IN_SEC)
        outSec = float(HackSlashConfig.SOFT_LOCK_FOV_OUT_SEC)

        def setFov(v):
            try:
                lens.setFov(v)
            except Exception:
                pass

        self._fovIval = Sequence(
            LerpFunc(
                setFov,
                fromData=baseFov,
                toData=peak,
                duration=inSec),
            LerpFunc(
                setFov,
                fromData=peak,
                toData=baseFov,
                duration=outSec),
            Func(self.restoreFov),
            name=self.avatar.uniqueName('hackslashSoftLockFovPunch'),
        )
        self._fovIval.start()

    def restoreFov(self):
        """Cancel soft-lock FOV ival and restore the captured base FOV."""
        if self._fovIval:
            try:
                self._fovIval.pause()
            except Exception:
                pass
            self._fovIval = None
        if self._baseFov is None:
            return
        try:
            lens = base.camLens  # noqa: F821
            if hasattr(self._baseFov, '__getitem__'):
                lens.setFov(self._baseFov[0], self._baseFov[1])
            else:
                lens.setFov(self._baseFov)
        except Exception:
            pass
        self._baseFov = None

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
