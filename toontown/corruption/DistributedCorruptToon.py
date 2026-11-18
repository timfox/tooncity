from panda3d.core import (
    CardMaker, NodePath, TextNode, TransparencyAttrib, Vec4, Point3)

from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNode
from direct.interval.IntervalGlobal import (
    LerpColorScaleInterval, LerpScaleInterval, Parallel, Sequence, Func)

from toontown.corruption import CorruptionGlobals
from toontown.corruption.HackSlashTarget import HackSlashTarget


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
        self._purityFlashIval = None

    def generate(self):
        self.assign(render.attachNewNode('DistributedCorruptToon'))
        self.__buildGeom()
        DistributedNode.DistributedNode.generate(self)

    def announceGenerate(self):
        DistributedNode.DistributedNode.announceGenerate(self)
        self.reparentTo(render)
        self.__startInkPulse()

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
                     '_telegraphIval', '_purityFlashIval'):
            ival = getattr(self, attr, None)
            if ival is not None:
                ival.finish()
                setattr(self, attr, None)

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
            toon.setScale(CorruptionGlobals.CORRUPT_ACTOR_SCALE)
            # Ink-black multiply — corruption read stays strong over DNA colors.
            toon.setColorScale(*CorruptionGlobals.CORRUPT_ACTOR_TINT)
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
        text.setTextColor(0.9, 0.55, 1.0, 1.0)
        text.setShadow(0.05, 0.05)
        self.nametagNP = self.attachNewNode(text)
        self.nametagNP.setScale(0.42)
        z = 3.6 if self._useActor else 3.35
        self.nametagNP.setPos(0, 0, z)
        self.nametagNP.setBillboardPointEye()

    def __startInkPulse(self):
        if self.visualRoot is None:
            return
        if self._pulseIval is not None:
            self._pulseIval.finish()
        hot = Vec4(*CorruptionGlobals.CORRUPT_TINT_HOT)
        cool = Vec4(1.0, 1.0, 1.0, 1.0)
        self._pulseIval = Sequence(
            Parallel(
                LerpColorScaleInterval(self.visualRoot, 0.7, hot),
                LerpScaleInterval(self.visualRoot, 0.7, Point3(1.06, 1.06, 0.94)),
            ),
            Parallel(
                LerpColorScaleInterval(self.visualRoot, 0.7, cool),
                LerpScaleInterval(self.visualRoot, 0.7, Point3(0.96, 0.96, 1.05)),
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

    def setHp(self, hp):
        self.hp = int(hp)

    def getHp(self):
        return self.hp

    def setMaxHp(self, maxHp):
        self.maxHp = int(maxHp)

    def getMaxHp(self):
        return self.maxHp

    def announceAttackTelegraph(self):
        """AI wind-up: stretch / ink flare so standing still is punishable."""
        if self._telegraphIval is not None:
            self._telegraphIval.finish()
        if self._pulseIval is not None:
            self._pulseIval.pause()
        target = self.visualRoot if self.visualRoot is not None else self
        self._telegraphIval = Sequence(
            Parallel(
                LerpScaleInterval(target, 0.22, Point3(1.55, 1.55, 0.55)),
                LerpColorScaleInterval(target, 0.22, Vec4(1.9, 0.35, 2.2, 1.0)),
            ),
            Parallel(
                LerpScaleInterval(target, 0.18, Point3(0.75, 0.75, 1.45)),
                LerpColorScaleInterval(target, 0.18, Vec4(0.7, 0.2, 1.0, 1.0)),
            ),
            LerpScaleInterval(target, 0.12, Point3(1.0, 1.0, 1.0)),
            Func(self.__resumePulse),
        )
        self._telegraphIval.start()

    def announceAttackHit(self):
        # Brief slam cue after AI damage lands.
        target = self.visualRoot if self.visualRoot is not None else self
        Sequence(
            LerpScaleInterval(target, 0.08, Point3(1.35, 1.35, 0.7)),
            LerpScaleInterval(target, 0.1, Point3(1.0, 1.0, 1.0)),
        ).start()
        # Client-readable cue so melee can flash i-frames / dodge window.
        messenger.send('corruptToonHitPlayer', [self])

    def __resumePulse(self):
        if self._pulseIval is not None and not self._defeatedHidden():
            self._pulseIval.resume()

    def _defeatedHidden(self):
        return self.isHidden() or self.hp <= 0

    def announceDefeat(self):
        if self._defeatIval is not None:
            self._defeatIval.finish()
        if self._pulseIval is not None:
            self._pulseIval.finish()
            self._pulseIval = None
        if self._telegraphIval is not None:
            self._telegraphIval.finish()
            self._telegraphIval = None
        target = self.visualRoot if self.visualRoot is not None else self
        # Satisfying ink splat + purity reclaim flash tied to pollution drop.
        self._defeatIval = Sequence(
            Parallel(
                LerpScaleInterval(target, 0.18, Point3(1.85, 1.85, 0.12)),
                LerpColorScaleInterval(target, 0.18, Vec4(1.8, 1.5, 2.2, 1.0)),
            ),
            Parallel(
                LerpScaleInterval(self, 0.22, Point3(0.02, 0.02, 0.02)),
                LerpColorScaleInterval(target, 0.22, Vec4(1.4, 1.6, 1.1, 0.0)),
            ),
            Func(self.__playPurityReclaimPop),
            Func(self.hide),
        )
        self._defeatIval.start()

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
        if self._hitIval is not None:
            self._hitIval.finish()
        stretch = 1.18 + 0.14 * hitIndex
        squash = 0.68 - 0.04 * hitIndex
        target = self.visualRoot if self.visualRoot is not None else (
            self.geom if self.geom is not None else self)
        self._hitIval = Sequence(
            Parallel(
                LerpScaleInterval(target, 0.06, (stretch, stretch, squash)),
                LerpColorScaleInterval(target, 0.06, Vec4(1.7, 0.65, 2.0, 1)),
            ),
            Parallel(
                LerpScaleInterval(target, 0.1, (0.88, 0.88, 1.22)),
                LerpColorScaleInterval(target, 0.1, Vec4(1, 1, 1, 1)),
            ),
            LerpScaleInterval(target, 0.08, (1, 1, 1)),
        )
        self._hitIval.start()
        try:
            away = self.getPos(render) - attacker.getPos(render)
            away.setZ(0)
            if away.length() > 0.01:
                away.normalize()
                self.setPos(self.getPos() + away * (0.7 + 0.25 * hitIndex))
        except Exception:
            pass
