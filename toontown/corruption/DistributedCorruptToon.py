from panda3d.core import (
    CardMaker, NodePath, TextNode, TransparencyAttrib, Vec4, Point3)

from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNode
from direct.interval.IntervalGlobal import (
    LerpColorScaleInterval, LerpPosInterval, LerpScaleInterval, Parallel,
    Sequence, Func, Wait)

from toontown.corruption import CorruptionGlobals
from toontown.corruption.CorruptDeathPopFx import (
    DeathPopSplat, buildBodyPopInterval, deathPopLook)
from toontown.corruption.BalloonSnareTelegraphFx import BalloonSnareTelegraphString
from toontown.corruption.BruteSpitTelegraphFx import BruteSpitTelegraphGob
from toontown.corruption.CorruptTelegraphInkFx import TelegraphInkDrip
from toontown.corruption.HackSlashTarget import HackSlashTarget
from toontown.corruption.IdleInkDripFx import IdleInkDrip
from toontown.corruption.OverlordPhaseInkRainFx import OverlordPhaseInkRain
from toontown.corruption.OverlordTelegraphCrownFx import OverlordTelegraphCrown
from toontown.corruption.SmudgeInkSplashFx import SmudgeInkSplash
from toontown.corruption.SmudgeInkTelegraphFx import SmudgeInkTelegraphFist


class DistributedCorruptToon(DistributedNode.DistributedNode, HackSlashTarget):
    """Client corrupt enemy: ink toon Actor when possible, else card silhouette."""

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCorruptToon')

    def __init__(self, cr):
        DistributedNode.DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'DistributedCorruptToon')
        self.hp = CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP
        self.maxHp = CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP
        self.name = CorruptionGlobals.CORRUPT_TOON_DEFAULT_NAME
        self.geom = None
        self.armGeom = None
        self.headGeom = None
        self.legGeomL = None
        self.legGeomR = None
        self.toonActor = None
        self.visualRoot = None
        self.nametagNP = None
        self.shadow = None
        self._useActor = False
        self._moving = False
        self._lastPos = None
        self._defeatIval = None
        self._hitIval = None
        self._pulseIval = None
        self._telegraphIval = None
        self._attackHitIval = None
        self._attackFlashNP = None
        self._attackFlashIval = None
        self._purityFlashIval = None
        self._telegraphSfx = None
        self._attackHitSfx = None
        self._bruteTelegraphSfx = None
        self._bruteHitSfx = None
        self._snareTelegraphSfx = None
        self._snareHitSfx = None
        # Finale Overlord phase SFX caches keyed by phase index.
        self._finaleTelegraphSfx = {}
        self._finaleHitSfx = {}
        self._spitBlobIval = None
        self._spitBlobNP = None
        self._stringLashIval = None
        self._stringLashNP = None
        self._deathPopSplat = None
        self._telegraphInkDrip = None
        self._idleInkDrip = None
        self._overlordCrown = None
        self._overlordInkRain = None
        self._snareTelegraphString = None
        self._bruteTelegraphSpit = None
        self._smudgeTelegraphInk = None
        self._smudgeInkSplash = None
        self.archetype = CorruptionGlobals.ARCHETYPE_INK

    def generate(self):
        self.assign(render.attachNewNode('DistributedCorruptToon'))
        self.__buildGeom()
        DistributedNode.DistributedNode.generate(self)

    def announceGenerate(self):
        DistributedNode.DistributedNode.announceGenerate(self)
        self.reparentTo(render)
        self.__applyArchetypeLook()
        self.__startInkPulse()
        self.__startIdleInkDrip()

    def disable(self):
        self.__stopIntervals()
        self.detachNode()
        DistributedNode.DistributedNode.disable(self)

    def delete(self):
        self.__stopIntervals()
        self.__cleanupActor()
        for attr in ('geom', 'armGeom', 'headGeom', 'legGeomL', 'legGeomR',
                     'visualRoot', 'nametagNP', 'shadow'):
            np = getattr(self, attr, None)
            if np is not None and not np.isEmpty():
                np.removeNode()
            setattr(self, attr, None)
        DistributedNode.DistributedNode.delete(self)

    def __cleanupActor(self):
        actor = self.toonActor
        self.toonActor = None
        if actor is None:
            return
        try:
            actor.stop()
        except Exception:
            pass
        try:
            actor.delete()
        except Exception:
            try:
                if not actor.isEmpty():
                    actor.removeNode()
            except Exception:
                pass

    def __stopIntervals(self):
        for attr in ('_defeatIval', '_hitIval', '_pulseIval',
                     '_telegraphIval', '_attackHitIval',
                     '_attackFlashIval', '_purityFlashIval',
                     '_spitBlobIval', '_stringLashIval'):
            ival = getattr(self, attr, None)
            if ival is not None:
                ival.finish()
                setattr(self, attr, None)
        self.__clearAttackFlash()
        self.__clearSpitBlob()
        self.__clearStringLash()
        self.__clearTelegraphInkDrip()
        self.__clearIdleInkDrip()
        self.__clearOverlordTelegraphCrown()
        self.__clearOverlordPhaseInkRain()
        self.__clearSnareTelegraphString()
        self.__clearBruteTelegraphSpit()
        self.__clearSmudgeTelegraphInk()
        self.__clearSmudgeInkSplash()
        self.__clearDeathPopSplat()

    def __buildGeom(self):
        self.visualRoot = self.attachNewNode('corrupt-visual')
        if self.__tryBuildActorSilhouette():
            self._useActor = True
        else:
            self._useActor = False
            self.__buildCardSilhouette()
        self.__buildShadowAndNametag()

    def __tryBuildActorSilhouette(self):
        """Prefer a real Toon Actor / DNA-tinted silhouette when assets load."""
        try:
            from toontown.toon import Toon, ToonDNA
        except Exception:
            self.notify.debug('Toon/ToonDNA import failed; using card silhouette')
            return False

        try:
            dna = ToonDNA.ToonDNA()
            cloned = False
            try:
                local = getattr(base, 'localAvatar', None)
                style = getattr(local, 'style', None) if local is not None else None
                if style is not None and hasattr(style, 'makeNetString'):
                    dna.makeFromNetString(style.makeNetString())
                    cloned = True
            except Exception:
                cloned = False
            if not cloned:
                seed = int(getattr(self, 'doId', 0) or 1)
                dna.newToonRandom(seed=seed, gender='m')

            toon = Toon.Toon()
            toon.setDNA(dna)
            toon.reparentTo(self.visualRoot)
            toon.setPos(0, 0, 0)
            toon.setH(0)
            look, _phase = self.__finalePhaseLook()
            stats = CorruptionGlobals.archetypeStats(self.archetype)
            actorScale = (
                float(look['actorScale']) if look
                else float(stats.get('actorScale', CorruptionGlobals.CORRUPT_ACTOR_SCALE)))
            toon.setScale(actorScale)
            # Ink / sludge multiply — archetype tint, Overlord phase can override.
            tint = (
                look.get('actorTint') if look and look.get('actorTint')
                else stats.get('actorTint', CorruptionGlobals.CORRUPT_ACTOR_TINT))
            toon.setColorScale(*tint)
            try:
                toon.stopBlink()
            except Exception:
                pass
            try:
                toon.stopLookAround()
            except Exception:
                pass
            try:
                if getattr(toon, 'dropShadow', None) is not None:
                    toon.dropShadow.hide()
            except Exception:
                pass
            try:
                if getattr(toon, 'nametag3d', None) is not None:
                    toon.nametag3d.hide()
            except Exception:
                pass
            try:
                if getattr(toon, 'nametag', None) is not None:
                    toon.nametag.unmanage(base.marginManager)
            except Exception:
                pass
            try:
                toon.loop('neutral')
            except Exception:
                pass

            self.toonActor = toon
            self.geom = toon
            self.notify.debug(
                'CorruptToon Actor silhouette ready (cloned=%s)' % cloned)
            return True
        except Exception:
            self.notify.debug(
                'CorruptToon Actor build failed; falling back to cards')
            self.__cleanupActor()
            # Clear any partial nodes under visualRoot before cards.
            if self.visualRoot is not None and not self.visualRoot.isEmpty():
                for child in self.visualRoot.getChildren():
                    child.removeNode()
            return False

    def __buildCardSilhouette(self):
        """Improved rubber-hose ink cards when DNA/Actor assets are unavailable."""
        cm = CardMaker('corrupt-body')
        cm.setFrame(-0.7, 0.7, 0.55, 2.15)
        body = self.visualRoot.attachNewNode(cm.generate())
        body.setColor(*CorruptionGlobals.CORRUPT_TINT)
        body.setBillboardPointEye()
        body.setTransparency(TransparencyAttrib.MAlpha)
        self.geom = body

        arm = CardMaker('corrupt-arm')
        arm.setFrame(-1.85, 1.85, 0.95, 1.35)
        armNP = self.visualRoot.attachNewNode(arm.generate())
        armNP.setColor(*CorruptionGlobals.CORRUPT_ARM_TINT)
        armNP.setBillboardPointEye()
        armNP.setTransparency(TransparencyAttrib.MAlpha)
        self.armGeom = armNP

        head = CardMaker('corrupt-head')
        head.setFrame(-0.55, 0.55, 0.0, 1.05)
        headNP = self.visualRoot.attachNewNode(head.generate())
        headNP.setPos(0, 0, 2.15)
        headNP.setColor(0.1, 0.02, 0.16, 1.0)
        headNP.setBillboardPointEye()
        headNP.setTransparency(TransparencyAttrib.MAlpha)
        self.headGeom = headNP

        legL = CardMaker('corrupt-leg-l')
        legL.setFrame(-0.55, -0.08, 0.0, 0.7)
        legLNP = self.visualRoot.attachNewNode(legL.generate())
        legLNP.setColor(0.14, 0.03, 0.22, 0.9)
        legLNP.setBillboardPointEye()
        legLNP.setTransparency(TransparencyAttrib.MAlpha)
        self.legGeomL = legLNP

        legR = CardMaker('corrupt-leg-r')
        legR.setFrame(0.08, 0.55, 0.0, 0.7)
        legRNP = self.visualRoot.attachNewNode(legR.generate())
        legRNP.setColor(0.14, 0.03, 0.22, 0.9)
        legRNP.setBillboardPointEye()
        legRNP.setTransparency(TransparencyAttrib.MAlpha)
        self.legGeomR = legRNP

    def __buildShadowAndNametag(self):
        try:
            self.shadow = loader.loadModel('phase_3/models/props/drop_shadow')
            self.shadow.setScale(0.5 if self._useActor else 0.45)
            self.shadow.setColor(0.05, 0.0, 0.1, 0.55)
            self.shadow.setZ(0.025)
            self.shadow.reparentTo(self)
        except Exception:
            self.shadow = None

        text = TextNode('corrupt-name')
        text.setText(self.name)
        text.setAlign(TextNode.ACenter)
        look, _phase = self.__finalePhaseLook()
        if look:
            text.setTextColor(*look['nameColor'])
        else:
            text.setTextColor(0.9, 0.55, 1.0, 1.0)
        text.setShadow(0.05, 0.05)
        self.nametagNP = self.attachNewNode(text)
        tagScale = 0.52 if look else 0.42
        self.nametagNP.setScale(tagScale)
        z = 3.6 if self._useActor else 3.35
        if look:
            z += 0.35 * (float(look.get('actorScale', 1.0)) - 1.0)
        self.nametagNP.setPos(0, 0, z)
        self.nametagNP.setBillboardPointEye()

    def __startInkPulse(self):
        if self.visualRoot is None:
            return
        if self._pulseIval is not None:
            self._pulseIval.finish()
        look, phase = self.__finalePhaseLook()
        if look:
            hot = Vec4(*look['pulseHot'])
            amp = float(look.get('pulseAmp', 0.08))
        else:
            hot = Vec4(*CorruptionGlobals.CORRUPT_TINT_HOT)
            amp = 0.06
        cool = Vec4(1.0, 1.0, 1.0, 1.0)
        up = Point3(1.0 + amp, 1.0 + amp, 1.0 - amp * 0.8)
        down = Point3(1.0 - amp, 1.0 - amp, 1.0 + amp)
        beat = 0.55 if phase >= 2 else 0.7
        self._pulseIval = Sequence(
            Parallel(
                LerpColorScaleInterval(self.visualRoot, beat, hot),
                LerpScaleInterval(self.visualRoot, beat, up),
            ),
            Parallel(
                LerpColorScaleInterval(self.visualRoot, beat, cool),
                LerpScaleInterval(self.visualRoot, beat, down),
            ),
        )
        self._pulseIval.loop()

    def setXYZH(self, x, y, z, h):
        DistributedNode.DistributedNode.setXYZH(self, x, y, z, h)
        self.__updateMoveAnim(Point3(x, y, z))

    def setXYZ(self, x, y, z):
        DistributedNode.DistributedNode.setXYZ(self, x, y, z)
        self.__updateMoveAnim(Point3(x, y, z))

    def __updateMoveAnim(self, pos):
        if not self._useActor or self.toonActor is None:
            self._lastPos = pos
            return
        moving = False
        if self._lastPos is not None:
            delta = pos - self._lastPos
            delta.setZ(0)
            moving = delta.lengthSquared() > 0.04
        self._lastPos = pos
        if moving == self._moving:
            return
        self._moving = moving
        try:
            self.toonActor.loop('run' if moving else 'neutral')
        except Exception:
            try:
                self.toonActor.loop('walk' if moving else 'neutral')
            except Exception:
                pass

    def setName(self, name):
        self.name = name
        if self.nametagNP is not None:
            self.nametagNP.node().setText(name)

    def getName(self):
        return self.name

    def setArchetype(self, archetype):
        self.archetype = int(archetype)
        self.__applyArchetypeLook()
        # Retint ambient idle drips when archetype arrives after generate.
        if getattr(self, '_idleInkDrip', None) is not None:
            self.__startIdleInkDrip()

    def getArchetype(self):
        return int(getattr(self, 'archetype', CorruptionGlobals.ARCHETYPE_INK))

    def __applyArchetypeLook(self):
        """Scale/tint for Smudge / Brute / Snare (finale phase look still wins)."""
        look, _phase = self.__finalePhaseLook()
        stats = CorruptionGlobals.archetypeStats(self.archetype)
        scale = (
            float(look['actorScale']) if look
            else float(stats.get('actorScale', CorruptionGlobals.CORRUPT_ACTOR_SCALE)))
        tint = (
            look.get('actorTint') if look and look.get('actorTint')
            else stats.get('actorTint', CorruptionGlobals.CORRUPT_ACTOR_TINT))
        target = self.toonActor if self.toonActor is not None else self.visualRoot
        if target is None:
            return
        try:
            target.setScale(scale)
            target.setColorScale(*tint)
        except Exception:
            pass

    def setHp(self, hp):
        self.hp = int(hp)

    def getHp(self):
        return self.hp

    def setMaxHp(self, maxHp):
        self.maxHp = int(maxHp)

    def getMaxHp(self):
        return self.maxHp

    def __finalePhaseLook(self):
        """Resolve Ink Overlord phase look from reclaim director or name."""
        phase = 0
        reclaim = getattr(base.cr, 'reclaimDirector', None)  # noqa: F821
        if reclaim is not None:
            phase = int(getattr(reclaim, 'finalePhase', 0) or 0)
        if phase < 1:
            name = (self.name or '').lower()
            if 'unleashed' in name:
                phase = 2
            elif 'overlord' in name:
                phase = 1
        return CorruptionGlobals.finalePhaseLook(phase), phase

    def __isBruteSpit(self):
        """True when this enemy should use Sludge Brute spit presentation."""
        return (
            int(getattr(self, 'archetype', CorruptionGlobals.ARCHETYPE_INK))
            == CorruptionGlobals.ARCHETYPE_BRUTE)

    def __isBalloonSnare(self):
        """True when this enemy should use Balloon Snare string-lash AV."""
        return (
            int(getattr(self, 'archetype', CorruptionGlobals.ARCHETYPE_INK))
            == CorruptionGlobals.ARCHETYPE_SNARE)

    def announceAttackTelegraph(self):
        """Strong wind-up: charged squash, ink/spit/lash flare — dodgeable."""
        if self._telegraphIval is not None:
            self._telegraphIval.finish()
        if self._attackHitIval is not None:
            self._attackHitIval.finish()
            self._attackHitIval = None
        if self._pulseIval is not None:
            self._pulseIval.pause()
        target = self.visualRoot if self.visualRoot is not None else self
        look, phase = self.__finalePhaseLook()
        isBrute = self.__isBruteSpit()
        isSnare = self.__isBalloonSnare()
        if look:
            charge = Vec4(*look['telegraphCharge'])
            hold = Vec4(*look['telegraphHold'])
            squash = Point3(*look['squash'])
            stretch = Point3(*look['stretch'])
            if look.get('mid'):
                mid = Point3(*look['mid'])
            else:
                mid = Point3(
                    squash[0] * 0.88, squash[1] * 0.88,
                    max(0.4, squash[2] * 1.2))
        elif isBrute:
            # Distinct green spit wind-up — wider squash, taller stretch.
            charge = Vec4(*CorruptionGlobals.BRUTE_TELEGRAPH_CHARGE_COLOR)
            hold = Vec4(*CorruptionGlobals.BRUTE_TELEGRAPH_HOLD_COLOR)
            squash = Point3(*CorruptionGlobals.BRUTE_TELEGRAPH_SQUASH)
            mid = Point3(*CorruptionGlobals.BRUTE_TELEGRAPH_MID)
            stretch = Point3(*CorruptionGlobals.BRUTE_TELEGRAPH_STRETCH)
        elif isSnare:
            # Amber rubber-hose string lash — horizontal stretch, quick zip.
            charge = Vec4(*CorruptionGlobals.SNARE_TELEGRAPH_CHARGE_COLOR)
            hold = Vec4(*CorruptionGlobals.SNARE_TELEGRAPH_HOLD_COLOR)
            squash = Point3(*CorruptionGlobals.SNARE_TELEGRAPH_SQUASH)
            mid = Point3(*CorruptionGlobals.SNARE_TELEGRAPH_MID)
            stretch = Point3(*CorruptionGlobals.SNARE_TELEGRAPH_STRETCH)
        else:
            # Ink Smudge melee telegraph — purple charge (unchanged).
            charge = Vec4(*CorruptionGlobals.TELEGRAPH_CHARGE_COLOR)
            hold = Vec4(*CorruptionGlobals.TELEGRAPH_HOLD_COLOR)
            squash = Point3(1.85, 1.85, 0.42)
            mid = Point3(1.65, 1.65, 0.5)
            stretch = Point3(0.62, 0.62, 1.7)
        self.__playOptionalActorPose('angry')
        self.__playTelegraphSfx()
        # Pause ambient idle drips so telegraph splat/drip owns the frame.
        self.__pauseIdleInkDrip()
        self.__playTelegraphInkDrip(look)
        # Ink Smudge-only: purple ink-fist telegraph pop for melee wind-up read.
        if (not look) and (not isBrute) and (not isSnare):
            self.__playSmudgeTelegraphInk()
        else:
            self.__clearSmudgeTelegraphInk()
        # Sludge Brute-only: green spit-gob telegraph pop for ranged spit read.
        if isBrute and not look:
            self.__playBruteTelegraphSpit()
        else:
            self.__clearBruteTelegraphSpit()
        # Balloon Snare-only: amber string-lash telegraph pop for zip/lash read.
        if isSnare and not look:
            self.__playSnareTelegraphString()
        else:
            self.__clearSnareTelegraphString()
        # Overlord-only: ink crown + ink rain for phase telegraph read.
        if look and phase >= 1:
            self.__playOverlordTelegraphCrown(look, phase)
            self.__playOverlordPhaseInkRain(look, phase)
            # Phase HUD cue so P1 magenta vs P2 crimson reads mid-wind-up.
            messenger.send(  # noqa: F821
                'finaleTelegraphCue',
                [phase, look.get('hudCue', 'OVERLORD P%s' % phase),
                 look.get('hudColor', (1.0, 0.55, 1.0, 1.0))])
        else:
            self.__clearOverlordTelegraphCrown()
            self.__clearOverlordPhaseInkRain()
        # Hold the charged pose across most of ATTACK_TELEGRAPH_DELAY so the
        # wind-up reads clearly before announceAttackHit's slam lands.
        self._telegraphIval = Sequence(
            Parallel(
                LerpScaleInterval(target, 0.12, squash),
                LerpColorScaleInterval(target, 0.12, charge),
            ),
            Parallel(
                LerpScaleInterval(target, 0.18, mid),
                LerpColorScaleInterval(target, 0.18, hold),
            ),
            Parallel(
                LerpScaleInterval(target, 0.14, stretch),
                LerpColorScaleInterval(target, 0.14, charge),
            ),
            # Linger stretched so the strike pose sticks until impact.
            # On miss (no announceAttackHit), ease back and resume ink pulse.
            Wait(0.12),
            Parallel(
                LerpScaleInterval(target, 0.1, Point3(1.0, 1.0, 1.0)),
                LerpColorScaleInterval(target, 0.1, Vec4(1, 1, 1, 1)),
            ),
            Func(self.__resumePulse),
        )
        self._telegraphIval.start()

    def announceAttackHit(self):
        """Impact feedback when AI damage lands — slam, flash, thud/spit/lash."""
        # Pause (don't finish) so telegraph's miss-recovery Funcs don't snap.
        if self._telegraphIval is not None:
            try:
                self._telegraphIval.pause()
            except Exception:
                pass
            self._telegraphIval = None
        # Clear telegraph drip / crown / rain / snare / spit / smudge fist so impact owns the frame.
        self.__clearTelegraphInkDrip()
        self.__clearOverlordTelegraphCrown()
        self.__clearOverlordPhaseInkRain()
        self.__clearSnareTelegraphString()
        self.__clearBruteTelegraphSpit()
        self.__clearSmudgeTelegraphInk()
        if self._attackHitIval is not None:
            self._attackHitIval.finish()
        target = self.visualRoot if self.visualRoot is not None else self
        look, _phase = self.__finalePhaseLook()
        isBrute = self.__isBruteSpit()
        isSnare = self.__isBalloonSnare()
        if look:
            impactScale = Point3(*look['impactScale'])
            impactColor = Vec4(*look['impactColor'])
            rebound = Vec4(*look.get(
                'rebound', (1.1, 0.55, 1.35, 1.0)))
        elif isBrute:
            impactScale = Point3(1.7, 1.7, 0.48)
            impactColor = Vec4(0.55, 2.35, 0.4, 1.0)
            rebound = Vec4(0.55, 1.25, 0.4, 1.0)
        elif isSnare:
            impactScale = Point3(2.15, 0.55, 0.7)
            impactColor = Vec4(2.4, 1.55, 0.4, 1.0)
            rebound = Vec4(1.35, 0.85, 0.35, 1.0)
        else:
            impactScale = Point3(1.55, 1.55, 0.55)
            impactColor = Vec4(2.2, 0.9, 2.4, 1.0)
            rebound = Vec4(1.1, 0.55, 1.35, 1.0)
        self.__playAttackHitSfx()
        self.__playAttackHitFlash()
        if isBrute:
            self.__playSpitBlob()
        elif isSnare:
            self.__playStringLash()
        self.__playOptionalActorPose('neutral')
        self._attackHitIval = Sequence(
            Parallel(
                LerpScaleInterval(target, 0.06, impactScale),
                LerpColorScaleInterval(target, 0.06, impactColor),
            ),
            Parallel(
                LerpScaleInterval(target, 0.1, Point3(0.85, 0.85, 1.25)),
                LerpColorScaleInterval(target, 0.1, rebound),
            ),
            Parallel(
                LerpScaleInterval(target, 0.12, Point3(1.0, 1.0, 1.0)),
                LerpColorScaleInterval(target, 0.12, Vec4(1, 1, 1, 1)),
            ),
            Func(self.__resumePulse),
        )
        self._attackHitIval.start()
        # Client-readable cue so melee can flash i-frames / dodge window (#12).
        messenger.send('corruptToonHitPlayer', [self])

    def announceAttackDodged(self):
        """Telegraph resolved into dodge i-frames / near-miss — sparkle cue."""
        # Ease telegraph pose out if it is still holding the stretch.
        if self._telegraphIval is not None:
            try:
                self._telegraphIval.pause()
            except Exception:
                pass
            self._telegraphIval = None
            target = self.visualRoot if self.visualRoot is not None else self
            try:
                target.setScale(1.0, 1.0, 1.0)
                target.setColorScale(1, 1, 1, 1)
            except Exception:
                pass
            self.__resumePulse()
        # Hackslash listens and plays perfect-dodge ink sparkle juice.
        messenger.send('corruptToonAttackDodged', [self])  # noqa: F821

    def __resumePulse(self):
        if self._pulseIval is not None and not self._defeatedHidden():
            self._pulseIval.resume()
        # Ambient pollution drips resume with the idle pulse between telegraphs.
        self.__resumeIdleInkDrip()

    def _defeatedHidden(self):
        return self.isHidden() or self.hp <= 0

    def __ensureSfx(self):
        if self._telegraphSfx is None:
            try:
                self._telegraphSfx = base.loader.loadSfx(
                    CorruptionGlobals.TELEGRAPH_SFX)
            except Exception:
                self._telegraphSfx = False
        if self._attackHitSfx is None:
            try:
                self._attackHitSfx = base.loader.loadSfx(
                    CorruptionGlobals.ATTACK_HIT_SFX)
            except Exception:
                self._attackHitSfx = False
        if self._bruteTelegraphSfx is None:
            try:
                self._bruteTelegraphSfx = base.loader.loadSfx(
                    CorruptionGlobals.BRUTE_TELEGRAPH_SFX)
            except Exception:
                self._bruteTelegraphSfx = False
        if self._bruteHitSfx is None:
            try:
                self._bruteHitSfx = base.loader.loadSfx(
                    CorruptionGlobals.BRUTE_ATTACK_HIT_SFX)
            except Exception:
                self._bruteHitSfx = False
        if self._snareTelegraphSfx is None:
            try:
                self._snareTelegraphSfx = base.loader.loadSfx(
                    CorruptionGlobals.SNARE_TELEGRAPH_SFX)
            except Exception:
                self._snareTelegraphSfx = False
        if self._snareHitSfx is None:
            try:
                self._snareHitSfx = base.loader.loadSfx(
                    CorruptionGlobals.SNARE_ATTACK_HIT_SFX)
            except Exception:
                self._snareHitSfx = False

    def __loadFinalePhaseSfx(self, cache, phase, path):
        """Lazy-load a finale-phase SFX into the given cache dict."""
        if phase in cache:
            return cache[phase]
        try:
            cache[phase] = base.loader.loadSfx(path)  # noqa: F821
        except Exception:
            cache[phase] = False
        return cache[phase]

    def __playTelegraphSfx(self):
        self.__ensureSfx()
        look, phase = self.__finalePhaseLook()
        if look and look.get('telegraphSfx'):
            sfx = self.__loadFinalePhaseSfx(
                self._finaleTelegraphSfx, phase, look['telegraphSfx'])
            volume = float(look.get(
                'telegraphSfxVolume',
                CorruptionGlobals.TELEGRAPH_SFX_VOLUME))
        elif self.__isBruteSpit() and self._bruteTelegraphSfx:
            sfx = self._bruteTelegraphSfx
            volume = CorruptionGlobals.BRUTE_TELEGRAPH_SFX_VOLUME
        elif self.__isBalloonSnare() and self._snareTelegraphSfx:
            sfx = self._snareTelegraphSfx
            volume = CorruptionGlobals.SNARE_TELEGRAPH_SFX_VOLUME
        else:
            sfx = self._telegraphSfx
            volume = CorruptionGlobals.TELEGRAPH_SFX_VOLUME
        if not sfx:
            return
        try:
            sfx.setVolume(volume)
            base.playSfx(sfx, node=self)
        except Exception:
            try:
                base.playSfx(sfx)
            except Exception:
                pass

    def __playAttackHitSfx(self):
        self.__ensureSfx()
        look, phase = self.__finalePhaseLook()
        if look and look.get('hitSfx'):
            sfx = self.__loadFinalePhaseSfx(
                self._finaleHitSfx, phase, look['hitSfx'])
            volume = float(look.get(
                'hitSfxVolume',
                CorruptionGlobals.ATTACK_HIT_SFX_VOLUME))
        elif self.__isBruteSpit() and self._bruteHitSfx:
            sfx = self._bruteHitSfx
            volume = CorruptionGlobals.BRUTE_ATTACK_HIT_SFX_VOLUME
        elif self.__isBalloonSnare() and self._snareHitSfx:
            sfx = self._snareHitSfx
            volume = CorruptionGlobals.SNARE_ATTACK_HIT_SFX_VOLUME
        else:
            sfx = self._attackHitSfx
            volume = CorruptionGlobals.ATTACK_HIT_SFX_VOLUME
        if not sfx:
            return
        try:
            sfx.setVolume(volume)
            base.playSfx(sfx, node=self)
        except Exception:
            try:
                base.playSfx(sfx)
            except Exception:
                pass

    def __playOptionalActorPose(self, animName):
        if not self._useActor or self.toonActor is None:
            return
        try:
            self.toonActor.play(animName)
        except Exception:
            try:
                self.toonActor.loop(animName)
            except Exception:
                pass

    def __playAttackHitFlash(self):
        """Brief ink/spit flash so corrupt smacks read without a combat HUD."""
        self.__clearAttackFlash()
        try:
            cm = CardMaker('corrupt-attack-hit-flash')
            cm.setFrame(-2, 2, -2, 2)
            np = aspect2d.attachNewNode(cm.generate())
            look, _phase = self.__finalePhaseLook()
            if look:
                color = look['hitFlash']
                peak = float(look.get('hitFlashPeak',
                                      CorruptionGlobals.ATTACK_HIT_FLASH_PEAK))
            elif self.__isBruteSpit():
                color = CorruptionGlobals.BRUTE_HIT_FLASH_COLOR
                peak = CorruptionGlobals.BRUTE_HIT_FLASH_PEAK
            elif self.__isBalloonSnare():
                color = CorruptionGlobals.SNARE_HIT_FLASH_COLOR
                peak = CorruptionGlobals.SNARE_HIT_FLASH_PEAK
            else:
                color = CorruptionGlobals.ATTACK_HIT_FLASH_COLOR
                peak = CorruptionGlobals.ATTACK_HIT_FLASH_PEAK
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setColor(color[0], color[1], color[2], 1)
            np.setColorScale(1, 1, 1, 0)
            np.setBin('fixed', 58)
            np.setDepthTest(False)
            np.setDepthWrite(False)
            self._attackFlashNP = np
            self._attackFlashIval = Sequence(
                LerpColorScaleInterval(
                    np, CorruptionGlobals.ATTACK_HIT_FLASH_IN,
                    Vec4(1, 1, 1, peak)),
                LerpColorScaleInterval(
                    np, CorruptionGlobals.ATTACK_HIT_FLASH_OUT,
                    Vec4(1, 1, 1, 0)),
                Func(self.__clearAttackFlash),
            )
            self._attackFlashIval.start()
        except Exception:
            self.__clearAttackFlash()

    def __clearAttackFlash(self):
        if self._attackFlashIval is not None:
            try:
                self._attackFlashIval.pause()
            except Exception:
                pass
            self._attackFlashIval = None
        if self._attackFlashNP is not None:
            try:
                if not self._attackFlashNP.isEmpty():
                    self._attackFlashNP.removeNode()
            except Exception:
                pass
            self._attackFlashNP = None

    def __playSpitBlob(self):
        """Simple green ink blob flying from Brute toward the local toon."""
        self.__clearSpitBlob()
        try:
            start = self.getPos(render)
            start.setZ(start.getZ() + CorruptionGlobals.BRUTE_SPIT_BLOB_Z)
            end = start + Point3(0, 6, 0)
            la = getattr(base, 'localAvatar', None)
            if la is not None and not la.isEmpty():
                end = la.getPos(render)
                end.setZ(end.getZ() + 2.0)
            cm = CardMaker('brute-spit-blob')
            half = CorruptionGlobals.BRUTE_SPIT_BLOB_SCALE
            cm.setFrame(-half, half, -half, half)
            blob = render.attachNewNode(cm.generate())
            blob.setPos(start)
            blob.setBillboardPointEye()
            blob.setTransparency(TransparencyAttrib.MAlpha)
            color = CorruptionGlobals.BRUTE_SPIT_BLOB_COLOR
            blob.setColor(color[0], color[1], color[2], color[3])
            blob.setBin('fixed', 40)
            blob.setDepthWrite(False)
            travel = float(CorruptionGlobals.BRUTE_SPIT_BLOB_TRAVEL)
            self._spitBlobNP = blob
            self._spitBlobIval = Sequence(
                Parallel(
                    LerpPosInterval(blob, travel, end, blendType='easeIn'),
                    LerpScaleInterval(
                        blob, travel, Point3(1.35, 1.35, 1.35),
                        startScale=Point3(0.55, 0.55, 0.55)),
                ),
                Parallel(
                    LerpScaleInterval(blob, 0.08, Point3(2.2, 2.2, 0.35)),
                    LerpColorScaleInterval(blob, 0.08, Vec4(1, 1, 1, 0)),
                ),
                Func(self.__clearSpitBlob),
            )
            self._spitBlobIval.start()
        except Exception:
            self.__clearSpitBlob()

    def __clearSpitBlob(self):
        if self._spitBlobIval is not None:
            try:
                self._spitBlobIval.pause()
            except Exception:
                pass
            self._spitBlobIval = None
        if self._spitBlobNP is not None:
            try:
                if not self._spitBlobNP.isEmpty():
                    self._spitBlobNP.removeNode()
            except Exception:
                pass
            self._spitBlobNP = None

    def __playStringLash(self):
        """Thin amber string line snapping from Snare toward the local toon."""
        self.__clearStringLash()
        try:
            start = self.getPos(render)
            start.setZ(start.getZ() + CorruptionGlobals.SNARE_LASH_Z)
            end = start + Point3(0, 5, 0)
            la = getattr(base, 'localAvatar', None)
            if la is not None and not la.isEmpty():
                end = la.getPos(render)
                end.setZ(end.getZ() + 1.8)
            cm = CardMaker('snare-string-lash')
            cm.setFrame(
                -CorruptionGlobals.SNARE_LASH_HALF_W,
                CorruptionGlobals.SNARE_LASH_HALF_W,
                -CorruptionGlobals.SNARE_LASH_HALF_H,
                CorruptionGlobals.SNARE_LASH_HALF_H)
            lash = render.attachNewNode(cm.generate())
            lash.setPos(start)
            lash.setBillboardPointEye()
            lash.setTransparency(TransparencyAttrib.MAlpha)
            color = CorruptionGlobals.SNARE_LASH_COLOR
            lash.setColor(color[0], color[1], color[2], color[3])
            lash.setBin('fixed', 40)
            lash.setDepthWrite(False)
            travel = float(CorruptionGlobals.SNARE_LASH_TRAVEL)
            self._stringLashNP = lash
            self._stringLashIval = Sequence(
                Parallel(
                    LerpPosInterval(lash, travel, end, blendType='easeIn'),
                    LerpScaleInterval(
                        lash, travel, Point3(0.55, 0.55, 2.4),
                        startScale=Point3(1.0, 1.0, 0.45)),
                ),
                Parallel(
                    LerpScaleInterval(lash, 0.06, Point3(2.4, 0.2, 0.2)),
                    LerpColorScaleInterval(lash, 0.06, Vec4(1, 1, 1, 0)),
                ),
                Func(self.__clearStringLash),
            )
            self._stringLashIval.start()
        except Exception:
            self.__clearStringLash()

    def __clearStringLash(self):
        if self._stringLashIval is not None:
            try:
                self._stringLashIval.pause()
            except Exception:
                pass
            self._stringLashIval = None
        if self._stringLashNP is not None:
            try:
                if not self._stringLashNP.isEmpty():
                    self._stringLashNP.removeNode()
            except Exception:
                pass
            self._stringLashNP = None

    def announceDefeat(self):
        if self._defeatIval is not None:
            self._defeatIval.finish()
        if self._pulseIval is not None:
            self._pulseIval.finish()
            self._pulseIval = None
        if self._telegraphIval is not None:
            self._telegraphIval.finish()
            self._telegraphIval = None
        if self._attackHitIval is not None:
            self._attackHitIval.finish()
            self._attackHitIval = None
        if self._spitBlobIval is not None:
            self._spitBlobIval.finish()
            self._spitBlobIval = None
        if self._stringLashIval is not None:
            self._stringLashIval.finish()
            self._stringLashIval = None
        self.__clearAttackFlash()
        self.__clearSpitBlob()
        self.__clearStringLash()
        self.__clearTelegraphInkDrip()
        self.__clearIdleInkDrip()
        self.__clearOverlordTelegraphCrown()
        self.__clearOverlordPhaseInkRain()
        self.__clearSnareTelegraphString()
        self.__clearBruteTelegraphSpit()
        self.__clearSmudgeTelegraphInk()
        self.__clearSmudgeInkSplash()
        self.__clearDeathPopSplat()
        target = self.visualRoot if self.visualRoot is not None else self
        look = deathPopLook(self.getArchetype())
        bodyPop = buildBodyPopInterval(target, look=look)
        # Rubber-hose ink splat / balloon pop + purity reclaim flash.
        try:
            splatPos = self.getPos(render)
        except Exception:
            splatPos = Point3(0, 0, 0)
        self._deathPopSplat = DeathPopSplat()
        self._deathPopSplat.play(splatPos, archetype=self.getArchetype())
        # Ink Smudge: extra cheap purple splash so swarm deaths stay scannable.
        if self.getArchetype() == CorruptionGlobals.ARCHETYPE_INK:
            self.__playSmudgeInkSplash(splatPos, kind='death')
        if bodyPop is None:
            self.__playPurityReclaimPop()
            self.hide()
            return
        self._defeatIval = Sequence(
            bodyPop,
            Func(self.__playPurityReclaimPop),
            Func(self.hide),
        )
        self._defeatIval.start()

    def __clearDeathPopSplat(self):
        splat = getattr(self, '_deathPopSplat', None)
        if splat is not None:
            try:
                splat.clear()
            except Exception:
                pass
        self._deathPopSplat = None

    def __playTelegraphInkDrip(self, finaleLook=None):
        """Short rubber-hose ink drip / splat pop on attack telegraph."""
        self.__clearTelegraphInkDrip()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        drip = TelegraphInkDrip()
        self._telegraphInkDrip = drip
        drip.play(
            pos,
            archetype=self.getArchetype(),
            finaleLook=finaleLook,
        )

    def __clearTelegraphInkDrip(self):
        drip = getattr(self, '_telegraphInkDrip', None)
        if drip is not None:
            try:
                drip.clear()
            except Exception:
                pass
        self._telegraphInkDrip = None

    def __startIdleInkDrip(self):
        """Ambient pollution drips between telegraphs (client-only presence)."""
        self.__clearIdleInkDrip()
        if self._defeatedHidden():
            return
        parent = self.visualRoot if self.visualRoot is not None else self
        look, _phase = self.__finalePhaseLook()
        drip = IdleInkDrip()
        self._idleInkDrip = drip
        drip.start(
            parent,
            archetype=self.getArchetype(),
            finaleLook=look,
        )

    def __pauseIdleInkDrip(self):
        drip = getattr(self, '_idleInkDrip', None)
        if drip is not None:
            try:
                drip.pause()
            except Exception:
                pass

    def __resumeIdleInkDrip(self):
        if self._defeatedHidden():
            return
        drip = getattr(self, '_idleInkDrip', None)
        if drip is None:
            self.__startIdleInkDrip()
            return
        try:
            drip.resume()
        except Exception:
            self.__startIdleInkDrip()

    def __clearIdleInkDrip(self):
        drip = getattr(self, '_idleInkDrip', None)
        if drip is not None:
            try:
                drip.clear()
            except Exception:
                pass
        self._idleInkDrip = None

    def __playOverlordTelegraphCrown(self, finaleLook=None, phase=1):
        """Ink crown / silhouette flash — Overlord phase telegraphs only."""
        self.__clearOverlordTelegraphCrown()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        crown = OverlordTelegraphCrown()
        self._overlordCrown = crown
        crown.play(pos, finaleLook=finaleLook, phase=phase)

    def __clearOverlordTelegraphCrown(self):
        crown = getattr(self, '_overlordCrown', None)
        if crown is not None:
            try:
                crown.clear()
            except Exception:
                pass
        self._overlordCrown = None

    def __playOverlordPhaseInkRain(self, finaleLook=None, phase=1):
        """Ink rain / ink fall shower — Overlord phase telegraphs only."""
        self.__clearOverlordPhaseInkRain()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        rain = OverlordPhaseInkRain()
        self._overlordInkRain = rain
        rain.play(pos, finaleLook=finaleLook, phase=phase)

    def __clearOverlordPhaseInkRain(self):
        rain = getattr(self, '_overlordInkRain', None)
        if rain is not None:
            try:
                rain.clear()
            except Exception:
                pass
        self._overlordInkRain = None

    def __playSnareTelegraphString(self):
        """Amber string-lash telegraph pop — Balloon Snare wind-ups only."""
        self.__clearSnareTelegraphString()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        lash = BalloonSnareTelegraphString()
        self._snareTelegraphString = lash
        lash.play(pos)

    def __clearSnareTelegraphString(self):
        lash = getattr(self, '_snareTelegraphString', None)
        if lash is not None:
            try:
                lash.clear()
            except Exception:
                pass
        self._snareTelegraphString = None

    def __playBruteTelegraphSpit(self):
        """Green spit-gob telegraph pop — Sludge Brute wind-ups only."""
        self.__clearBruteTelegraphSpit()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        spit = BruteSpitTelegraphGob()
        self._bruteTelegraphSpit = spit
        spit.play(pos)

    def __clearBruteTelegraphSpit(self):
        spit = getattr(self, '_bruteTelegraphSpit', None)
        if spit is not None:
            try:
                spit.clear()
            except Exception:
                pass
        self._bruteTelegraphSpit = None

    def __playSmudgeTelegraphInk(self):
        """Purple ink-fist telegraph pop — Ink Smudge melee wind-ups only."""
        self.__clearSmudgeTelegraphInk()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        fist = SmudgeInkTelegraphFist()
        self._smudgeTelegraphInk = fist
        fist.play(pos)

    def __clearSmudgeTelegraphInk(self):
        fist = getattr(self, '_smudgeTelegraphInk', None)
        if fist is not None:
            try:
                fist.clear()
            except Exception:
                pass
        self._smudgeTelegraphInk = None

    def __playSmudgeInkSplash(self, pos=None, kind='hit'):
        """Purple ink splash — Ink Smudge hit / death swarm readability only."""
        if self.getArchetype() != CorruptionGlobals.ARCHETYPE_INK:
            return
        self.__clearSmudgeInkSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = SmudgeInkSplash()
        self._smudgeInkSplash = splash
        splash.play(pos, kind=kind)

    def __clearSmudgeInkSplash(self):
        splash = getattr(self, '_smudgeInkSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._smudgeInkSplash = None

    def __playPurityReclaimPop(self):
        """Local feedback that defeating this enemy reclaimed pollution."""
        messenger.send('corruptToonDefeatedFx', [
            getattr(self, 'zoneId', None),
            self.getPos(render) if not self.isEmpty() else Point3(0, 0, 0),
        ])
        if self._purityFlashIval is not None:
            self._purityFlashIval.finish()
        # Soft purity tick on the scene — complements PollutionManager fog drop.
        self._purityFlashIval = Sequence(
            LerpColorScaleInterval(render, 0.12, Vec4(1.25, 1.35, 1.15, 1.0)),
            LerpColorScaleInterval(render, 0.35, Vec4(1, 1, 1, 1)),
        )
        self._purityFlashIval.start()
        try:
            if hasattr(base, 'localAvatar'):
                base.localAvatar.setSystemMessage(
                    0, 'Purity reclaimed! Corruption fades...')
        except Exception:
            pass

    def getHackSlashName(self):
        return self.name

    def getHackSlashPos(self):
        return self.getPos(render)

    def takeHackSlashDamage(self, amount, attackerId=None):
        # Damage is AI-authoritative; client prediction can land later.
        return 0

    def applyHackSlashHit(self, damage, hitIndex, attacker):
        """Bridge SoftTarget/MeleeCombat → AI requestHackSlashHit RPC."""
        if not self.isHackSlashAlive():
            return False
        amount = max(0, int(damage))
        if amount <= 0:
            return False
        self.sendUpdate('requestHackSlashHit', [amount])
        self.__playHitReaction(hitIndex, attacker)
        return True

    def __playHitReaction(self, hitIndex, attacker):
        """Ink flash + knockback; scale squash/stretch owned by hackslash HitJuice."""
        if self._hitIval is not None:
            self._hitIval.finish()
        target = self.visualRoot if self.visualRoot is not None else (
            self.geom if self.geom is not None else self)
        self._hitIval = Sequence(
            LerpColorScaleInterval(target, 0.06, Vec4(1.7, 0.65, 2.0, 1)),
            LerpColorScaleInterval(target, 0.14, Vec4(1, 1, 1, 1)),
        )
        self._hitIval.start()
        # Ink Smudge: cheap purple splash so tagged Smudges read in a swarm.
        if self.getArchetype() == CorruptionGlobals.ARCHETYPE_INK:
            self.__pauseIdleInkDrip()
            self.__playSmudgeInkSplash(kind='hit')
            # Brief resume so idle drips return after the splash owns the frame.
            Sequence(Wait(0.28), Func(self.__resumeIdleInkDrip)).start()
        try:
            away = self.getPos(render) - attacker.getPos(render)
            away.setZ(0)
            if away.length() > 0.01:
                away.normalize()
                self.setPos(self.getPos() + away * (0.7 + 0.25 * hitIndex))
        except Exception:
            pass
