"""Real-time rubber-hose Oswald stretch-punch melee controller.

Combo fists with cartoon squash/stretch timing and soft targeting.
Client-local prototype — does not enter turn-based battle FSM.
"""

from panda3d.core import CardMaker, Point3, TextNode, TransparencyAttrib, Vec3, Vec4

from direct.interval.IntervalGlobal import (
    ActorInterval,
    Func,
    LerpColorScaleInterval,
    LerpPosInterval,
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
from . import HitJuice
from .CreamHangSparkleFx import CreamHangSparkleFx
from .CreamSlamFlashFx import CreamSlamFlashFx
from .DemoHostile import spawnDemoHostiles
from .DodgePerfectFx import DodgePerfectFx
from .DodgeTrailFx import DodgeTrailFx
from .HitSparkFx import HitSparkFx
from .HitStopFx import HitStopFx
from .SlamDustFx import SlamDustFx
from .SoftLockReticleFx import SoftLockReticleFx
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
        self._impactIval = None
        self._playerHitReactIval = None
        self._fovIval = None
        self._flashIval = None
        self._flashNP = None
        self._launchIval = None
        self._dodgeIval = None
        self._iframeUntil = 0.0
        self._dodgeIFrameUntil = 0.0
        self._dodgeReadyAt = 0.0
        self._dodging = False
        self._dodgeTrail = DodgeTrailFx(avatar)
        self._dodgePerfect = DodgePerfectFx(avatar)
        self._hitStop = HitStopFx(avatar)
        self._hitSpark = HitSparkFx(avatar)
        self._slamDust = SlamDustFx(avatar)
        self._creamSlamFlash = CreamSlamFlashFx(avatar)
        self._creamHangSparkle = CreamHangSparkleFx(avatar)
        # Soft-lock FOV punch defers while HitStopFx is active (#68 compose).
        self._softLockReticle = SoftLockReticleFx(
            avatar,
            hitStop=self._hitStop,
            beforeFov=self._restoreFov,
            fovBusy=lambda: self._fovIval is not None)
        self._pendingConnectTarget = None
        self._pendingConnectHitIndex = None
        self._origScale = None
        self._baseFov = None
        self._shakeAmp = 0.0
        self._shakeUntil = 0.0
        self._comboHits = 0
        self._comboNP = None
        self._comboIval = None
        self._comboFleckIval = None
        self._comboFleckNodes = []
        self._comboCreamIval = None
        self._comboCreamNodes = []
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
        self._iframeUntil = 0.0
        self._dodgeIFrameUntil = 0.0
        self._dodgeReadyAt = 0.0
        self._dodging = False
        self._comboHits = 0
        self.avatar.hackSlashDemoHostiles = getattr(
            self.avatar, 'hackSlashDemoHostiles', []) or []
        if spawnHostiles and not self.avatar.hackSlashDemoHostiles:
            self.avatar.hackSlashDemoHostiles = spawnDemoHostiles(self.avatar)
        self.accept(HackSlashConfig.ATTACK_KEY, self._onAttackPressed)
        self.accept(HackSlashConfig.ATTACK_KEY_ALT, self._onAttackPressed)
        self.accept(HackSlashConfig.DODGE_KEY, self._onDodgePressed)
        self.accept(HackSlashConfig.DODGE_KEY_ALT, self._onDodgePressed)
        self.accept('corruptToonHitPlayer', self._onCorruptHitPlayer)
        self.accept('corruptToonAttackDodged', self._onCorruptAttackDodged)
        self.accept('hackslash-hit', self._onHackSlashHit)
        self._showHint(HackSlashConfig.DEMO_HINT)
        # Run after smart-cam so soft-lock look/orbit bias applies for the frame.
        taskMgr.add(  # noqa: F821
            self._tick, self._taskName,
            priority=HackSlashConfig.LOCK_CAM_TASK_PRIORITY)

    def disable(self):
        if not self.enabled:
            self._cleanupHostiles()
            return
        self.enabled = False
        self.ignore(HackSlashConfig.ATTACK_KEY)
        self.ignore(HackSlashConfig.ATTACK_KEY_ALT)
        self.ignore(HackSlashConfig.DODGE_KEY)
        self.ignore(HackSlashConfig.DODGE_KEY_ALT)
        self.ignore('corruptToonHitPlayer')
        self.ignore('corruptToonAttackDodged')
        self.ignore('hackslash-hit')
        taskMgr.remove(self._taskName)  # noqa: F821
        taskMgr.remove(self.avatar.uniqueName('hackslashComboBreak'))  # noqa: F821
        self._finishSwing()
        self._restoreScale()
        self._clearImpactJuice()
        self._clearPlayerHitReact()
        self._clearHitstop()
        self._restoreFov()
        self._clearFinisherShake()
        self._clearHitFlash()
        self._clearLaunch()
        self._clearDodge()
        self._clearPerfectDodge()
        self._clearHitSpark()
        self._clearSlamDust()
        self._clearCreamSlamFlash()
        self._clearSoftLockReticle()
        self._clearComboCounter()
        self._iframeUntil = 0.0
        self._dodgeIFrameUntil = 0.0
        self._dodging = False
        self._comboHits = 0
        self.targetFinder.clear()
        self._hideHint()
        self._hideLockHint()
        self._cleanupHostiles()
        self.comboIndex = 0
        self.comboWindowOpen = False
        self.busy = False

    def destroy(self):
        self.disable()
        try:
            self._dodgeTrail.clear()
        except Exception:
            pass
        try:
            self._dodgePerfect.clear()
        except Exception:
            pass
        try:
            self._hitSpark.clear()
        except Exception:
            pass
        try:
            self._slamDust.clear()
        except Exception:
            pass
        try:
            self._creamSlamFlash.clear()
        except Exception:
            pass
        try:
            self._creamHangSparkle.clear()
        except Exception:
            pass
        try:
            self._softLockReticle.clear()
        except Exception:
            pass
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
        snapped = self.targetFinder.didSnap()
        if target is not None:
            name = target.getHackSlashName()
            hp = target.getHackSlashHp()
            self._showLockHint('%s  [%d]' % (name, hp))
            self._updateSoftLockReticle(target, snapped=snapped)
            self._nudgeTowardLock(target)
        else:
            self._hideLockHint()
            self._hideSoftLockReticle()
            # Still flush deferred soft-lock FOV if hitstop just ended.
            try:
                self._softLockReticle.tick()
            except Exception:
                pass
        # Always after soft-lock so finisher thud isn't lerped away.
        self._applyFinisherShake()
        return Task.cont

    def _updateSoftLockReticle(self, target, snapped=False):
        """Follow soft-lock target; hose-pop + cream pulse ring + FOV on snap."""
        try:
            self._softLockReticle.attach(target, snapped=bool(snapped))
            # Flush deferred soft-lock FOV after HitStopFx resumes.
            self._softLockReticle.tick()
        except Exception:
            pass

    def _hideSoftLockReticle(self):
        try:
            self._softLockReticle.hide()
        except Exception:
            pass

    def _clearSoftLockReticle(self):
        try:
            self._softLockReticle.clear()
        except Exception:
            pass

    def _nudgeTowardLock(self, target):
        """Subtle avatar + camera lean toward the sticky soft-lock target.

        Idle: mild facing/look-at bias. Mid-combo: stronger look-at plus a soft
        lateral orbit/pull so the locked corrupt stays readable — never a hard
        lock; page-up/down free-look still wins.
        """
        try:
            pos = target.getHackSlashPos()
        except Exception:
            return
        inCombo = bool(self.busy)
        faceLerp = (
            HackSlashConfig.LOCK_COMBO_FACE_LERP
            if inCombo else HackSlashConfig.LOCK_FACE_LERP)
        camLerp = (
            HackSlashConfig.LOCK_COMBO_CAM_LERP
            if inCombo else HackSlashConfig.LOCK_CAM_LERP)

        # Soft heads-up: lerp facing instead of snapping (keeps locomotion feel).
        try:
            av = self.avatar
            curH = av.getH(render)  # noqa: F821
            av.headsUp(pos)
            wantH = av.getH(render)  # noqa: F821
            av.setH(render, curH)  # noqa: F821
            delta = ((wantH - curH + 180.0) % 360.0) - 180.0
            av.setH(render, curH + delta * faceLerp)  # noqa: F821
        except Exception:
            pass

        # Yield to explicit page-up / page-down camera angles.
        if getattr(self.avatar, 'isPageUp', 0) or getattr(self.avatar, 'isPageDown', 0):
            return

        # Soft camera look-at nudge: blend a fraction of lookAt toward the lock.
        try:
            look = Point3(pos)
            look.setZ(look.getZ() + HackSlashConfig.LOCK_CAM_LOOK_HEIGHT)
            cam = base.camera  # noqa: F821
            curHpr = cam.getHpr()
            cam.lookAt(look)
            wantHpr = cam.getHpr()
            cam.setHpr(curHpr)
            cam.setHpr(
                curHpr[0] + (((wantHpr[0] - curHpr[0] + 180.0) % 360.0) - 180.0) * camLerp,
                curHpr[1] + (wantHpr[1] - curHpr[1]) * camLerp,
                curHpr[2] + (wantHpr[2] - curHpr[2]) * camLerp,
            )
        except Exception:
            pass

        if inCombo:
            self._orbitCamTowardLock(pos)

    def _orbitCamTowardLock(self, targetPos):
        """Soft lateral orbit + pull-back while a combo string is live.

        Applied as a per-frame bias on top of smart-cam (does not accumulate):
        peek past the shoulder toward the lock and ease back slightly so both
        toon and corrupt stay in frame.
        """
        try:
            cam = base.camera  # noqa: F821
            av = self.avatar
            curPos = cam.getPos()
            toTarget = Vec3(targetPos - av.getPos(render))  # noqa: F821
            toTarget.setZ(0.0)
            right = av.getQuat(render).getRight()  # noqa: F821
            right.setZ(0.0)
            side = 0.0
            if right.lengthSquared() > 1e-4 and toTarget.lengthSquared() > 1e-4:
                right.normalize()
                toTarget.normalize()
                # Target on avatar-right → orbit cam +X (peek that shoulder).
                side = max(-1.0, min(1.0, right.dot(toTarget)))
            lateral = HackSlashConfig.LOCK_COMBO_ORBIT_LATERAL * side
            pull = HackSlashConfig.LOCK_COMBO_ORBIT_PULL
            lift = HackSlashConfig.LOCK_COMBO_ORBIT_LIFT
            t = HackSlashConfig.LOCK_COMBO_ORBIT_LERP
            # Smart-cam resets pos each frame; bias is offset * t (no drift).
            cam.setPos(
                curPos[0] + lateral * t,
                curPos[1] - pull * t,
                curPos[2] + lift * t,
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
            # Squash first so hitstop freezes on the impact silhouette.
            self._playConnectImpactJuice(hitIndex, target)
            # Flash reads during the freeze; launch / hop / FOV wait for resume.
            # Finisher swaps white HIT_FLASH for warm cream slam flash + ring.
            if hitIndex >= HackSlashConfig.COMBO_LENGTH - 1:
                self._playCreamSlamFlash()
            else:
                self._playHitFlash()
            self._playHitstop(hitIndex, target=target)
        else:
            # Whiff inside a live string soft-breaks the on-screen counter.
            if self._comboHits > 0:
                self._armComboBreak(delay=0.35)

    def _launchTiming(self, table, hitIndex):
        """Pick per-hit timing/height; scalars still work for older configs."""
        if isinstance(table, (int, float)):
            return float(table)
        return float(table[min(hitIndex, len(table) - 1)])

    def _onHackSlashHit(self, avatar=None, target=None, damage=0, hitIndex=0):
        """Tick the on-screen combo counter for any local melee connect."""
        if not self.enabled:
            return
        if avatar is not None and avatar is not self.avatar:
            return
        self._comboHits += 1
        self._showComboCounter(self._comboHits)
        self._armComboBreak()

    def _armComboBreak(self, delay=None):
        name = self.avatar.uniqueName('hackslashComboBreak')
        taskMgr.remove(name)  # noqa: F821
        hold = HackSlashConfig.COMBO_BREAK_SEC if delay is None else float(delay)
        taskMgr.doMethodLater(hold, self._breakComboCounter, name)  # noqa: F821

    def _breakComboCounter(self, task):
        self._fadeComboCounter()
        return Task.done

    def _showComboCounter(self, hits):
        """Readable punch counter — rubber-hose squash/stretch pop on connect."""
        text = '%d %s' % (int(hits), HackSlashConfig.COMBO_COUNTER_LABEL)
        colors = HackSlashConfig.COMBO_COUNTER_COLORS
        color = colors[min(max(0, hits - 1), len(colors) - 1)]
        if self._comboNP is None or self._comboNP.isEmpty():
            tn = TextNode('hackslash-combo')
            tn.setText(text)
            tn.setAlign(TextNode.ACenter)
            tn.setTextColor(*color)
            tn.setShadow(0.05, 0.05)
            tn.setShadowColor(0, 0, 0, 0.8)
            np = aspect2d.attachNewNode(tn)  # noqa: F821
            np.setPos(*HackSlashConfig.COMBO_COUNTER_POS)
            np.setScale(HackSlashConfig.COMBO_COUNTER_BASE_SCALE)
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setColorScale(1, 1, 1, 1)
            np.setBin('fixed', 55)
            self._comboNP = np
        else:
            node = self._comboNP.node()
            node.setText(text)
            node.setTextColor(*color)
            self._comboNP.setColorScale(1, 1, 1, 1)
            self._comboNP.show()

        if self._comboIval:
            try:
                self._comboIval.pause()
            except Exception:
                pass
            self._comboIval = None
        self._clearComboFlecks()
        baseScale = HackSlashConfig.COMBO_COUNTER_BASE_SCALE
        # Slight size climb so long strings stay readable as a reward.
        grow = min(0.04, 0.008 * max(0, hits - 1))
        settle = baseScale + grow
        self._comboIval = HitJuice.playComboCounterPop(
            self._comboNP, settle,
            name=self.avatar.uniqueName('hackslashComboPop'))
        try:
            fleckOrigin = self._comboNP.getPos()
            parent = aspect2d  # noqa: F821
        except Exception:
            fleckOrigin = None
            parent = None
        if fleckOrigin is not None:
            fleckIval, flecks = HitJuice.spawnComboInkFlecks(
                fleckOrigin, parent=parent,
                name=self.avatar.uniqueName('hackslashComboFlecks'))
            self._comboFleckIval = fleckIval
            self._comboFleckNodes = flecks
            # Cream sparkle + delayed cream aftershock on the same tick.
            creamIval, creamNodes = HitJuice.spawnComboCreamSparkles(
                fleckOrigin, parent=parent,
                name=self.avatar.uniqueName('hackslashComboCream'))
            self._comboCreamIval = creamIval
            self._comboCreamNodes = creamNodes

    def _fadeComboCounter(self):
        if self._comboNP is None or self._comboNP.isEmpty():
            self._comboHits = 0
            return
        self._clearComboFlecks()
        if self._comboIval:
            try:
                self._comboIval.pause()
            except Exception:
                pass
        np = self._comboNP
        self._comboIval = Sequence(
            LerpColorScaleInterval(
                np, HackSlashConfig.COMBO_FADE_SEC, Vec4(1, 1, 1, 0)),
            Func(self._clearComboCounter),
            name=self.avatar.uniqueName('hackslashComboFade'),
        )
        self._comboIval.start()
        self._comboHits = 0

    def _clearComboFlecks(self):
        if self._comboFleckIval is not None:
            try:
                self._comboFleckIval.pause()
            except Exception:
                pass
            self._comboFleckIval = None
        HitJuice.clearComboInkFlecks(self._comboFleckNodes)
        self._comboFleckNodes = []
        if self._comboCreamIval is not None:
            try:
                self._comboCreamIval.pause()
            except Exception:
                pass
            self._comboCreamIval = None
        HitJuice.clearComboCreamSparkles(self._comboCreamNodes)
        self._comboCreamNodes = []

    def _clearComboCounter(self):
        taskMgr.remove(self.avatar.uniqueName('hackslashComboBreak'))  # noqa: F821
        self._clearComboFlecks()
        if self._comboIval:
            try:
                self._comboIval.pause()
            except Exception:
                pass
            self._comboIval = None
        if self._comboNP and not self._comboNP.isEmpty():
            try:
                self._comboNP.removeNode()
            except Exception:
                pass
        self._comboNP = None
        self._comboHits = 0

    def _playLauncher(self, target, hitIndex):
        """Upward juggle with readable rubber-hose hang/float before fall."""
        self._clearLaunch()
        try:
            node = target
            if hasattr(target, 'visualRoot') and target.visualRoot is not None:
                node = target.visualRoot
            start = node.getPos()
        except Exception:
            return
        lift = self._launchTiming(HackSlashConfig.LAUNCH_HEIGHT, hitIndex)
        if lift <= 0.01:
            return
        upSec = self._launchTiming(HackSlashConfig.LAUNCH_UP_SEC, hitIndex)
        hangSec = self._launchTiming(HackSlashConfig.LAUNCH_HANG_SEC, hitIndex)
        downSec = self._launchTiming(HackSlashConfig.LAUNCH_DOWN_SEC, hitIndex)
        hoverAmp = self._launchTiming(HackSlashConfig.LAUNCH_HANG_HOVER, hitIndex)
        peak = Point3(start[0], start[1], start[2] + lift)
        stretch = (
            Point3(0.7, 0.7, 1.65)
            if hitIndex >= HackSlashConfig.COMBO_LENGTH - 1
            else Point3(0.75, 0.75, 1.55))
        hangIval = HitJuice.buildLaunchHangInterval(
            node, peak, hangSec, hoverAmp, stretch,
            name=self.avatar.uniqueName('hackslashLaunchHang'))

        def startCreamHangSparkle():
            # World-space cream flecks + halo at apex, then delayed cream
            # aftershock — HitJuice hang still owns hover/squash;
            # CreamSlamFlashFx stays aspect2d on connect.
            try:
                parent = render  # noqa: F821
            except Exception:
                parent = None
            self._creamHangSparkle.play(
                origin=peak, hitIndex=hitIndex, parent=parent)

        self._launchIval = Sequence(
            Parallel(
                LerpPosInterval(node, upSec, peak),
                LerpScaleInterval(node, upSec, stretch),
            ),
            Func(startCreamHangSparkle),
            hangIval,
            Parallel(
                LerpPosInterval(node, downSec, start),
                LerpScaleInterval(node, downSec, Point3(1.0, 1.0, 1.0)),
            ),
            Func(self._clearLaunchSparks),
            name=self.avatar.uniqueName('hackslashLaunch'),
        )
        self._launchIval.start()

    def _playFinisherSelfHop(self):
        """Brief local hop so the finisher juggle feels shared / airborne."""
        if getattr(self, '_selfHopIval', None):
            try:
                self._selfHopIval.finish()
            except Exception:
                pass
            self._selfHopIval = None
        try:
            start = self.avatar.getPos(render)  # noqa: F821
            peak = Point3(
                start[0], start[1],
                start[2] + HackSlashConfig.FINISHER_SELF_HOP)
        except Exception:
            return
        try:
            controls = self.avatar.controlManager.currentControls
            setattr(controls, 'isAirborne', 1)
        except Exception:
            controls = None

        def clearAir():
            try:
                if controls is not None:
                    setattr(controls, 'isAirborne', 0)
            except Exception:
                pass
            self._selfHopIval = None

        self._selfHopIval = Sequence(
            Parallel(
                LerpPosInterval(
                    self.avatar, HackSlashConfig.FINISHER_SELF_UP_SEC, peak,
                    other=render),  # noqa: F821
                LerpScaleInterval(
                    self.avatar, HackSlashConfig.FINISHER_SELF_UP_SEC,
                    Point3(0.85, 0.85, 1.25)),
            ),
            Parallel(
                LerpPosInterval(
                    self.avatar, HackSlashConfig.FINISHER_SELF_DOWN_SEC, start,
                    other=render),  # noqa: F821
                LerpScaleInterval(
                    self.avatar, HackSlashConfig.FINISHER_SELF_DOWN_SEC,
                    Point3(1.0, 1.0, 1.0)),
            ),
            Func(clearAir),
            name=self.avatar.uniqueName('hackslashSelfHop'),
        )
        self._selfHopIval.start()

    def _clearLaunchSparks(self):
        try:
            self._creamHangSparkle.clear()
        except Exception:
            pass

    def _clearLaunch(self):
        if self._launchIval:
            try:
                self._launchIval.finish()
            except Exception:
                pass
            self._launchIval = None
        self._clearLaunchSparks()

    def _onCorruptHitPlayer(self, corrupt=None):
        """Readable i-frame / dodge window after a CorruptToon smack."""
        if not self.enabled:
            return
        # Active dodge already covers this beat — skip the hit-react flash.
        if self.isInvulnerable():
            return
        now = globalClock.getFrameTime()  # noqa: F821
        self._iframeUntil = now + HackSlashConfig.IFRAME_SEC
        self.avatar.hackSlashIFrameUntil = self._iframeUntil
        self._reportIFrameToAI(HackSlashConfig.IFRAME_SEC)
        # Rubber-hose player hit-react: flat squash → stretch recover + tiny stop.
        self._playPlayerHitReact()
        self._playTinyHitstop(HackSlashConfig.PLAYER_HIT_REACT_HITSTOP_SEC)
        # Stronger flash than normal hit confirm so the window is obvious.
        self._playHitFlash(peakAlpha=HackSlashConfig.IFRAME_FLASH_ALPHA)
        messenger.send('hackslash-iframe', [self.avatar, HackSlashConfig.IFRAME_SEC])  # noqa: F821

    def _onCorruptAttackDodged(self, corrupt=None):
        """Telegraph resolved into Shift/X dodge i-frames — ink sparkle juice."""
        if not self.enabled:
            return
        # Only celebrate player-initiated dodge windows, not post-hit i-frames.
        if not self.isDodgeInvulnerable():
            return
        self._playPerfectDodge()

    def _reportIFrameToAI(self, durationSec):
        """So CorruptToonAI can skip takeDamage during the window."""
        try:
            pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
            if pm is not None and hasattr(pm, 'd_requestHackSlashIFrame'):
                pm.d_requestHackSlashIFrame(int(float(durationSec) * 1000.0))
        except Exception:
            pass

    def _onDodgePressed(self):
        """Brief rubber-hose dash with i-frames (Shift / X)."""
        if not self.enabled or self._dodging:
            return
        now = globalClock.getFrameTime()  # noqa: F821
        if now < self._dodgeReadyAt:
            return
        self._dodging = True
        self._dodgeReadyAt = now + HackSlashConfig.DODGE_COOLDOWN_SEC
        self._iframeUntil = now + HackSlashConfig.DODGE_IFRAME_SEC
        self._dodgeIFrameUntil = self._iframeUntil
        self.avatar.hackSlashIFrameUntil = self._iframeUntil
        self._reportIFrameToAI(HackSlashConfig.DODGE_IFRAME_SEC)
        messenger.send(
            'hackslash-iframe',
            [self.avatar, HackSlashConfig.DODGE_IFRAME_SEC])  # noqa: F821
        self._playHitFlash(peakAlpha=0.28)
        try:
            start = self.avatar.getPos(render)  # noqa: F821
            forward = render.getRelativeVector(  # noqa: F821
                self.avatar, Point3(0, 1, 0))
            forward.setZ(0)
            if forward.lengthSquared() < 1e-4:
                end = start
            else:
                forward.normalize()
                end = start + forward * HackSlashConfig.DODGE_DISTANCE
        except Exception:
            self._dodging = False
            return
        sx, sy, sz, squashSec = HackSlashConfig.DODGE_SQUASH
        self._clearDodge()
        self._dodgeIval = Parallel(
            Sequence(
                LerpPosInterval(
                    self.avatar, HackSlashConfig.DODGE_DURATION_SEC, end,
                    other=render),  # noqa: F821
                Func(self._finishDodge),
            ),
            Sequence(
                LerpScaleInterval(
                    self.avatar, squashSec, Point3(sx, sy, sz)),
                LerpScaleInterval(
                    self.avatar,
                    HackSlashConfig.DODGE_DURATION_SEC - squashSec,
                    Point3(1.0, 1.0, 1.0)),
            ),
            name=self.avatar.uniqueName('hackslashDodge'),
        )
        self._dodgeIval.start()
        # Afterimage smear + i-frame cream/ink pulse — isolated helper.
        try:
            self._dodgeTrail.start(
                iframeSec=HackSlashConfig.DODGE_IFRAME_SEC)
        except Exception:
            pass

    def _finishDodge(self):
        self._dodging = False
        self._dodgeIval = None
        try:
            self._dodgeTrail.stop(clearGhosts=False)
        except Exception:
            pass
        try:
            self.avatar.setScale(1.0, 1.0, 1.0)
        except Exception:
            pass

    def _clearDodge(self):
        if self._dodgeIval:
            try:
                self._dodgeIval.finish()
            except Exception:
                pass
            self._dodgeIval = None
        self._dodging = False
        try:
            self._dodgeTrail.clear()
        except Exception:
            pass

    def _playPerfectDodge(self):
        """Ink sparkle / star pop + cream star aftershock at the local toon."""
        try:
            self._dodgePerfect.play()
        except Exception:
            pass
        self._playHitFlash(peakAlpha=HackSlashConfig.PERFECT_DODGE_FLASH_ALPHA)
        messenger.send('hackslash-perfect-dodge', [self.avatar])  # noqa: F821

    def _clearPerfectDodge(self):
        try:
            self._dodgePerfect.clear()
        except Exception:
            pass

    def isInvulnerable(self):
        return globalClock.getFrameTime() < self._iframeUntil  # noqa: F821

    def isDodgeInvulnerable(self):
        """True only during Shift/X dodge i-frames (not post-hit window)."""
        return globalClock.getFrameTime() < self._dodgeIFrameUntil  # noqa: F821

    def _playHitstop(self, hitIndex, target=None):
        """Brief rubber-hose freeze so connects stick before launch juice."""
        stopSec = HackSlashConfig.HITSTOP_SEC[
            min(hitIndex, len(HackSlashConfig.HITSTOP_SEC) - 1)]
        self._pendingConnectTarget = target
        self._pendingConnectHitIndex = hitIndex
        self._playTinyHitstop(
            stopSec, target=target, onDone=self._afterConnectHitstop)

    def _playTinyHitstop(self, stopSec, target=None, onDone=None):
        """Pause swing / hose / impact juice + anims so the silhouette sticks."""
        targetIval = None
        if target is not None:
            targetIval = getattr(target, '_hackslashImpactIval', None)
        intervals = (
            self._swingIval,
            self._hoseIval,
            self._impactIval,
            self._playerHitReactIval,
            targetIval,
        )
        actors = (self.avatar, target)
        self._hitStop.play(
            stopSec, intervals=intervals, actors=actors, onDone=onDone)

    def _afterConnectHitstop(self):
        """Resume deferred connect juice after the freeze window."""
        target = self._pendingConnectTarget
        hitIndex = self._pendingConnectHitIndex
        self._pendingConnectTarget = None
        self._pendingConnectHitIndex = None
        if hitIndex is None:
            return
        if hitIndex >= HackSlashConfig.LAUNCH_HIT_INDEX:
            self._playLauncher(target, hitIndex)
        if hitIndex >= HackSlashConfig.COMBO_LENGTH - 1:
            self._playFinisherFovPunch()
            self._playFinisherShake()
            self._playFinisherSelfHop()

    def _clearHitstop(self):
        self._pendingConnectTarget = None
        self._pendingConnectHitIndex = None
        try:
            self._hitStop.clear(resume=True, runDone=False)
        except Exception:
            pass

    def _playHitFlash(self, peakAlpha=None):
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
            peak = (
                HackSlashConfig.HIT_FLASH_PEAK_ALPHA
                if peakAlpha is None else float(peakAlpha))
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
        # Drop any soft-lock FOV punch so finisher owns the lens cleanly.
        try:
            self._softLockReticle.cancelPendingFov()
            self._softLockReticle.restoreFov()
        except Exception:
            pass
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

    def _playFinisherShake(self):
        """Arm a brief camera thud after soft-lock each tick (optional)."""
        if not HackSlashConfig.FINISHER_SHAKE_ENABLED:
            return
        amp = float(HackSlashConfig.FINISHER_SHAKE_AMPLITUDE)
        sec = float(HackSlashConfig.FINISHER_SHAKE_SEC)
        if amp <= 0.0 or sec <= 0.0:
            return
        self._shakeAmp = amp
        try:
            self._shakeUntil = globalClock.getFrameTime() + sec  # noqa: F821
        except Exception:
            self._shakeUntil = sec

    def _applyFinisherShake(self):
        """Decay-random camera offset — cartoon thud, not a long quake."""
        if self._shakeAmp <= 0.0:
            return
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            self._clearFinisherShake()
            return
        remaining = self._shakeUntil - now
        if remaining <= 0.0:
            self._clearFinisherShake()
            return
        total = max(0.01, float(HackSlashConfig.FINISHER_SHAKE_SEC))
        amp = self._shakeAmp * (remaining / total)
        offset = HitJuice.sampleShakeOffset(amp)
        try:
            cam = base.camera  # noqa: F821
            pos = cam.getPos()
            cam.setPos(pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2])
        except Exception:
            self._clearFinisherShake()

    def _clearFinisherShake(self):
        self._shakeAmp = 0.0
        self._shakeUntil = 0.0

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

    def _playConnectImpactJuice(self, hitIndex, target=None):
        """On connect: replace wind-up hose with impact squash → stretch recover.

        Also pulses the target visual when present so corrupt/demo hit-reacts
        share the same rubber-hose curve (targets may layer color/knockback).
        """
        self._clearImpactJuice()
        # End wind-up hose so impact silhouette owns the scale beat.
        if self._hoseIval:
            try:
                self._hoseIval.pause()
            except Exception:
                pass
            self._hoseIval = None
        av = self.avatar
        if self._origScale is None:
            try:
                self._origScale = Point3(1.0, 1.0, 1.0)
            except Exception:
                self._origScale = Point3(1.0, 1.0, 1.0)
        # Snap back to pre-swing scale so wind-up multipliers don't compound.
        try:
            av.setScale(self._origScale)
        except Exception:
            pass
        isFinisher = hitIndex >= HackSlashConfig.COMBO_LENGTH - 1
        if isFinisher:
            self._impactIval = HitJuice.playFinisherSlam(
                av,
                finishScale=self._origScale,
                name=av.uniqueName('hackslashFinisherSlam'),
            )
            self._playSlamDust(target)
        else:
            self._impactIval = HitJuice.playImpactSquash(
                av,
                hitIndex=hitIndex,
                finishScale=self._origScale,
                name=av.uniqueName('hackslashImpactSquash'),
            )
        # Cream/ink fleck sparkles layer with the squash silhouette.
        self._playHitSpark(hitIndex, target)
        # Target hit-react scale — DemoHostile / CorruptToon may also tint.
        visual = HitJuice.resolveVisualNode(target)
        if visual is not None and visual is not av:
            try:
                # Tag so overlapping target reactions can finish prior juice.
                prev = getattr(target, '_hackslashImpactIval', None)
                HitJuice.finishInterval(prev)
            except Exception:
                pass
            if isFinisher:
                targetIval = HitJuice.playFinisherSlam(
                    visual,
                    finishScale=Point3(1.0, 1.0, 1.0),
                    name='hackslashTargetFinisherSlam',
                )
            else:
                targetIval = HitJuice.playImpactSquash(
                    visual,
                    hitIndex=hitIndex,
                    finishScale=Point3(1.0, 1.0, 1.0),
                    name='hackslashTargetImpact',
                )
            try:
                setattr(target, '_hackslashImpactIval', targetIval)
            except Exception:
                pass

    def _playHitSpark(self, hitIndex, target=None):
        """Cream/ink flecks + delayed cream spark aftershock — layers with squash."""
        origin = None
        lift = float(HackSlashConfig.HIT_SPARK_LIFT)
        if target is not None:
            try:
                if hasattr(target, 'getHackSlashPos'):
                    pos = target.getHackSlashPos()
                else:
                    pos = target.getPos(render)  # noqa: F821
                origin = Point3(pos[0], pos[1], pos[2] + lift)
            except Exception:
                origin = None
        try:
            self._hitSpark.play(origin=origin, hitIndex=hitIndex)
        except Exception:
            pass

    def _clearHitSpark(self):
        try:
            self._hitSpark.clear()
        except Exception:
            pass

    def _playSlamDust(self, target=None):
        """Short rubber-hose dust / ink puff at feet on finisher slam connect."""
        origin = None
        # Prefer target feet when present so the thud reads on the hit.
        if target is not None:
            try:
                if hasattr(target, 'getHackSlashPos'):
                    origin = target.getHackSlashPos()
                else:
                    origin = target.getPos(render)  # noqa: F821
            except Exception:
                origin = None
        try:
            self._slamDust.play(origin=origin)
        except Exception:
            pass

    def _clearSlamDust(self):
        try:
            self._slamDust.clear()
        except Exception:
            pass

    def _playCreamSlamFlash(self):
        """Warm cream slam flash + hang + cream aftershock — during hitstop."""
        # Drop any mid-combo white flash so cream owns the screen punch.
        # CreamSlamFlashFx still owns hang (#107) + cream aftershock settle.
        self._clearHitFlash()
        try:
            self._creamSlamFlash.play()
        except Exception:
            pass

    def _clearCreamSlamFlash(self):
        try:
            self._creamSlamFlash.clear()
        except Exception:
            pass

    def _clearImpactJuice(self):
        HitJuice.finishInterval(
            self._impactIval, self.avatar, restoreScale=self._origScale)
        self._impactIval = None

    def _playPlayerHitReact(self):
        """Flat squash → springy stretch when a corrupt smack lands."""
        self._clearPlayerHitReact()
        # Don't fight an in-flight dodge / hose scale pulse.
        if self._dodging:
            return
        self._playerHitReactIval = HitJuice.playPlayerHitReact(
            self.avatar,
            finishScale=Point3(1.0, 1.0, 1.0),
            name=self.avatar.uniqueName('hackslashPlayerHitReact'),
        )

    def _clearPlayerHitReact(self):
        HitJuice.finishInterval(
            self._playerHitReactIval, self.avatar,
            restoreScale=Point3(1.0, 1.0, 1.0))
        self._playerHitReactIval = None

    def _restoreScale(self):
        if self._hoseIval:
            self._hoseIval.finish()
            self._hoseIval = None
        self._clearImpactJuice()
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
