"""Real-time rubber-hose melee controller.

Combo-ish swings with cartoon squash/stretch timing and soft targeting.
Client-local prototype — does not enter turn-based battle FSM.
"""

from panda3d.core import CardMaker, Point3, TextNode, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    ActorInterval,
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.interval.LerpInterval import LerpFunc
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

from otp.avatar import Emote

from . import HackSlashConfig
from .DemoHostile import spawnDemoHostiles
from .SoftTarget import SoftTargetFinder


class MeleeCombatController(DirectObject):
    notify = None

    def __init__(self, avatar):
        DirectObject.__init__(self)
        self.avatar = avatar
        self.enabled = False
        self.comboIndex = 0
        self.comboWindowOpen = False
        self.busy = False
        self._swingIval = None
        self._hoseIval = None
        self._hitstopIval = None
        self._fovIval = None
        self._flashIval = None
        self._flashNP = None
        self._origScale = None
        self._baseFov = None
        self.targetFinder = SoftTargetFinder(avatar)
        self._hintNP = None
        self._lockHintNP = None
        self._taskName = avatar.uniqueName('hackslashMeleeTick')

    def enable(self, spawnHostiles=True):
        if self.enabled:
            return
        self.enabled = True
        self.comboIndex = 0
        self.comboWindowOpen = False
        self.busy = False
        self.avatar.hackSlashDemoHostiles = getattr(
            self.avatar, 'hackSlashDemoHostiles', []) or []
        if spawnHostiles and not self.avatar.hackSlashDemoHostiles:
            self.avatar.hackSlashDemoHostiles = spawnDemoHostiles(self.avatar)
        self.accept(HackSlashConfig.ATTACK_KEY, self._onAttackPressed)
        self.accept(HackSlashConfig.ATTACK_KEY_ALT, self._onAttackPressed)
        self._showHint(HackSlashConfig.DEMO_HINT)
        taskMgr.add(self._tick, self._taskName)  # noqa: F821

    def disable(self):
        if not self.enabled:
            self._cleanupHostiles()
            return
        self.enabled = False
        self.ignore(HackSlashConfig.ATTACK_KEY)
        self.ignore(HackSlashConfig.ATTACK_KEY_ALT)
        taskMgr.remove(self._taskName)  # noqa: F821
        self._finishSwing()
        self._restoreScale()
        self._clearHitstop()
        self._restoreFov()
        self._clearHitFlash()
        self.targetFinder.clear()
        self._hideHint()
        self._hideLockHint()
        self._cleanupHostiles()
        self.comboIndex = 0
        self.comboWindowOpen = False
        self.busy = False

    def destroy(self):
        self.disable()
        self.ignoreAll()

    def isEnabled(self):
        return self.enabled

    def _cleanupHostiles(self):
        hostiles = getattr(self.avatar, 'hackSlashDemoHostiles', None) or []
        for h in hostiles:
            try:
                h.cleanup()
            except Exception:
                pass
        self.avatar.hackSlashDemoHostiles = []

    def _tick(self, task):
        if not self.enabled:
            return Task.done
        target = self.targetFinder.acquire()
        if target is not None:
            name = target.getHackSlashName()
            hp = target.getHackSlashHp()
            self._showLockHint('%s  [%d]' % (name, hp))
            self._nudgeTowardLock(target)
        else:
            self._hideLockHint()
        return Task.cont

    def _nudgeTowardLock(self, target):
        """Subtle avatar + camera lean toward the sticky soft-lock target."""
        try:
            pos = target.getHackSlashPos()
        except Exception:
            return
        # Soft heads-up: lerp facing instead of snapping (keeps locomotion feel).
        try:
            av = self.avatar
            curH = av.getH(render)  # noqa: F821
            av.headsUp(pos)
            wantH = av.getH(render)  # noqa: F821
            av.setH(render, curH)  # noqa: F821
            delta = ((wantH - curH + 180.0) % 360.0) - 180.0
            av.setH(render, curH + delta * HackSlashConfig.LOCK_FACE_LERP)  # noqa: F821
        except Exception:
            pass
        # Soft camera look-at nudge: blend a fraction of lookAt toward the lock.
        try:
            look = Point3(pos)
            look.setZ(look.getZ() + HackSlashConfig.LOCK_CAM_LOOK_HEIGHT)
            cam = base.camera  # noqa: F821
            curHpr = cam.getHpr()
            cam.lookAt(look)
            wantHpr = cam.getHpr()
            cam.setHpr(curHpr)
            t = HackSlashConfig.LOCK_CAM_LERP
            cam.setHpr(
                curHpr[0] + (((wantHpr[0] - curHpr[0] + 180.0) % 360.0) - 180.0) * t,
                curHpr[1] + (wantHpr[1] - curHpr[1]) * t,
                curHpr[2] + (wantHpr[2] - curHpr[2]) * t,
            )
        except Exception:
            pass

    def _onAttackPressed(self):
        if not self.enabled:
            return
        if getattr(self.avatar.controlManager.currentControls, 'isAirborne', 0):
            return
        # Presenting a pie — don't overlap classic toss.
        if getattr(self.avatar, 'tossPieStart', None) is not None:
            return
        if self.busy and not self.comboWindowOpen:
            return

        messenger.send('wakeup')  # noqa: F821
        if self.comboWindowOpen and self.comboIndex < HackSlashConfig.COMBO_LENGTH:
            hitIndex = self.comboIndex
        else:
            hitIndex = 0
            self.comboIndex = 0

        self._startSwing(hitIndex)

    def _startSwing(self, hitIndex):
        self._finishSwing()
        self.busy = True
        self.comboWindowOpen = False
        self.comboIndex = hitIndex

        target = self.targetFinder.acquire()
        if target is not None:
            self._faceTarget(target)

        anim = HackSlashConfig.COMBO_ANIMS[
            min(hitIndex, len(HackSlashConfig.COMBO_ANIMS) - 1)]
        rate = HackSlashConfig.COMBO_PLAY_RATES[
            min(hitIndex, len(HackSlashConfig.COMBO_PLAY_RATES) - 1)]
        damage = HackSlashConfig.COMBO_DAMAGE[
            min(hitIndex, len(HackSlashConfig.COMBO_DAMAGE) - 1)]

        Emote.globalEmote.disableBody(self.avatar, 'hackslashMelee')

        # Hit check slightly after wind-up for readable cartoon timing.
        hitDelay = max(0.05, 0.12 / rate)
        windowStart = max(hitDelay + 0.05, 0.22 / rate)
        windowEnd = windowStart + HackSlashConfig.COMBO_WINDOW_SEC
        recovery = HackSlashConfig.COMBO_RECOVERY_SEC

        try:
            animIval = ActorInterval(
                self.avatar, anim, playRate=rate, name='hackslashSwingAnim')
        except Exception:
            # Fallback if anim missing on this toon species / phase.
            animIval = Wait(0.35 / rate)

        self._playHosePulse(hitIndex)

        def openWindow():
            self.comboWindowOpen = True
            self.comboIndex = hitIndex + 1

        def closeWindowAndRecover():
            self.comboWindowOpen = False

        def finish():
            self.busy = False
            self.comboWindowOpen = False
            if self.comboIndex >= HackSlashConfig.COMBO_LENGTH:
                self.comboIndex = 0
            Emote.globalEmote.releaseBody(self.avatar, 'hackslashMelee')
            self._restoreScale()
            # Return to locomotion anim state without forcing Happy if airborne.
            try:
                if not getattr(self.avatar.controlManager.currentControls, 'isAirborne', 0):
                    self.avatar.setAnimState('Happy', 1.0)
            except Exception:
                pass

        self._swingIval = Parallel(
            Sequence(animIval),
            Sequence(
                Wait(hitDelay),
                Func(self._resolveHit, damage, hitIndex, target),
                Wait(max(0.0, windowStart - hitDelay)),
                Func(openWindow),
                Wait(HackSlashConfig.COMBO_WINDOW_SEC),
                Func(closeWindowAndRecover),
                Wait(recovery),
                Func(finish),
            ),
            name=self.avatar.uniqueName('hackslashSwing'),
        )
        self._swingIval.start()

    def _resolveHit(self, damage, hitIndex, preacquired):
        target = preacquired
        if target is None or not target.isHackSlashAlive():
            target = self.targetFinder.acquire()
        if target is None:
            return
        if not self._inHitRange(target):
            # Still allow slightly generous finisher reach.
            if hitIndex < HackSlashConfig.COMBO_LENGTH - 1:
                return
            if self.targetFinder._distance(target) > HackSlashConfig.TARGET_RANGE * 0.85:
                return
        landed = False
        try:
            if hasattr(target, 'applyHackSlashHit'):
                landed = bool(target.applyHackSlashHit(damage, hitIndex, self.avatar))
            elif hasattr(target, 'takeHackSlashDamage'):
                # Corruption AI-style API fallback if a target skips the client bridge.
                attackerId = getattr(self.avatar, 'doId', None)
                landed = bool(target.takeHackSlashDamage(damage, attackerId))
        except Exception:
            landed = False
        if landed:
            messenger.send('hackslash-hit', [self.avatar, target, damage, hitIndex])  # noqa: F821
            self._playHitstop(hitIndex)
            self._playHitFlash()
            if hitIndex >= HackSlashConfig.COMBO_LENGTH - 1:
                self._playFinisherFovPunch()

    def _playHitstop(self, hitIndex):
        """Brief attack freeze so contacts read as rubber-hose impacts."""
        self._clearHitstop()
        stopSec = HackSlashConfig.HITSTOP_SEC[
            min(hitIndex, len(HackSlashConfig.HITSTOP_SEC) - 1)]
        # Pause the swing / hose intervals so the hit silhouette sticks.
        try:
            if self._swingIval:
                self._swingIval.pause()
        except Exception:
            pass
        try:
            if self._hoseIval:
                self._hoseIval.pause()
        except Exception:
            pass
        name = self.avatar.uniqueName('hackslashHitstop')
        taskMgr.remove(name)  # noqa: F821
        taskMgr.doMethodLater(stopSec, self._resumeAfterHitstop, name)  # noqa: F821

    def _resumeAfterHitstop(self, task):
        try:
            if self._swingIval:
                self._swingIval.resume()
        except Exception:
            pass
        try:
            if self._hoseIval:
                self._hoseIval.resume()
        except Exception:
            pass
        return Task.done

    def _clearHitstop(self):
        name = self.avatar.uniqueName('hackslashHitstop')
        try:
            taskMgr.remove(name)  # noqa: F821
        except Exception:
            pass
        try:
            if self._swingIval:
                self._swingIval.resume()
        except Exception:
            pass
        try:
            if self._hoseIval:
                self._hoseIval.resume()
        except Exception:
            pass

    def _playHitFlash(self):
        """Brief full-screen white flash so connects read beyond hitstop alone."""
        self._clearHitFlash()
        try:
            cm = CardMaker('hackslash-hit-flash')
            cm.setFrame(-2, 2, -2, 2)
            np = aspect2d.attachNewNode(cm.generate())  # noqa: F821
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setColor(1, 1, 1, 1)
            np.setColorScale(1, 1, 1, 0)
            np.setBin('fixed', 60)
            np.setDepthTest(False)
            np.setDepthWrite(False)
            self._flashNP = np
            peak = HackSlashConfig.HIT_FLASH_PEAK_ALPHA
            self._flashIval = Sequence(
                LerpColorScaleInterval(
                    np, HackSlashConfig.HIT_FLASH_IN_SEC, Vec4(1, 1, 1, peak)),
                LerpColorScaleInterval(
                    np, HackSlashConfig.HIT_FLASH_OUT_SEC, Vec4(1, 1, 1, 0)),
                Func(self._clearHitFlash),
                name=self.avatar.uniqueName('hackslashHitFlash'),
            )
            self._flashIval.start()
        except Exception:
            self._clearHitFlash()

    def _clearHitFlash(self):
        if self._flashIval:
            try:
                self._flashIval.pause()
            except Exception:
                pass
            self._flashIval = None
        if self._flashNP and not self._flashNP.isEmpty():
            try:
                self._flashNP.removeNode()
            except Exception:
                pass
        self._flashNP = None

    def _playFinisherFovPunch(self):
        """Quick FOV kick on the 3rd hit so finishers feel heavier."""
        self._restoreFov()
        try:
            lens = base.camLens  # noqa: F821
        except Exception:
            return
        try:
            self._baseFov = lens.getFov()
            baseFov = float(self._baseFov[0]) if hasattr(self._baseFov, '__getitem__') else float(self._baseFov)
        except Exception:
            return
        punch = HackSlashConfig.FINISHER_FOV_PUNCH
        peak = baseFov + punch

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
                duration=HackSlashConfig.FINISHER_FOV_IN_SEC),
            LerpFunc(
                setFov,
                fromData=peak,
                toData=baseFov,
                duration=HackSlashConfig.FINISHER_FOV_OUT_SEC),
            Func(self._restoreFov),
            name=self.avatar.uniqueName('hackslashFovPunch'),
        )
        self._fovIval.start()

    def _restoreFov(self):
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

    def _inHitRange(self, target):
        dist = self.targetFinder._distance(target)
        return dist <= (HackSlashConfig.HIT_FORWARD + HackSlashConfig.HIT_RADIUS)

    def _faceTarget(self, target):
        try:
            pos = target.getHackSlashPos()
            self.avatar.headsUp(pos)
        except Exception:
            pass

    def _playHosePulse(self, hitIndex):
        self._restoreScale()
        av = self.avatar
        self._origScale = av.getScale()
        sx, sy, sz, dur = HackSlashConfig.HOSE_SQUASH[
            min(hitIndex, len(HackSlashConfig.HOSE_SQUASH) - 1)]
        recover = HackSlashConfig.HOSE_STRETCH_RECOVER
        baseScale = self._origScale
        self._hoseIval = Sequence(
            LerpScaleInterval(
                av, dur,
                Point3(baseScale[0] * sx, baseScale[1] * sy, baseScale[2] * sz)),
            LerpScaleInterval(av, recover, baseScale),
        )
        self._hoseIval.start()

    def _restoreScale(self):
        if self._hoseIval:
            self._hoseIval.finish()
            self._hoseIval = None
        if self._origScale is not None:
            try:
                self.avatar.setScale(self._origScale)
            except Exception:
                pass
            self._origScale = None

    def _finishSwing(self):
        if self._swingIval:
            self._swingIval.pause()
            self._swingIval = None
        try:
            Emote.globalEmote.releaseBody(self.avatar, 'hackslashMelee')
        except Exception:
            pass

    def _showHint(self, text):
        self._hideHint()
        tn = TextNode('hackslash-hint')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(1, 1, 0.75, 1)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.7)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        np.setScale(0.045)
        np.setPos(0, 0, 0.92)
        self._hintNP = np

    def _hideHint(self):
        if self._hintNP and not self._hintNP.isEmpty():
            self._hintNP.removeNode()
        self._hintNP = None

    def _showLockHint(self, text):
        if self._lockHintNP and not self._lockHintNP.isEmpty():
            self._lockHintNP.node().setText(text)
            return
        tn = TextNode('hackslash-lock')
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(1, 0.55, 1, 1)
        tn.setShadow(0.04, 0.04)
        tn.setShadowColor(0, 0, 0, 0.7)
        np = aspect2d.attachNewNode(tn)  # noqa: F821
        np.setScale(0.05)
        np.setPos(0, 0, 0.84)
        self._lockHintNP = np

    def _hideLockHint(self):
        if self._lockHintNP and not self._lockHintNP.isEmpty():
            self._lockHintNP.removeNode()
        self._lockHintNP = None
