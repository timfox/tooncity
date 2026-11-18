from panda3d.core import (
    CardMaker, NodePath, TextNode, TransparencyAttrib, Vec4, Point3)
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNode
from direct.interval.IntervalGlobal import (
    LerpColorScaleInterval, LerpScaleInterval, Parallel, Sequence, Func)

from toontown.corruption import CorruptionGlobals
from toontown.corruption.HackSlashTarget import HackSlashTarget


class DistributedCorruptToon(DistributedNode.DistributedNode, HackSlashTarget):
    """Client stub: dark placeholder geom until toon-mesh overrides land."""

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCorruptToon')

    def __init__(self, cr):
        DistributedNode.DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'DistributedCorruptToon')
        self.hp = CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP
        self.maxHp = CorruptionGlobals.CORRUPT_TOON_DEFAULT_HP
        self.name = CorruptionGlobals.CORRUPT_TOON_DEFAULT_NAME
        self.geom = None
        self.nametagNP = None
        self.shadow = None
        self._defeatIval = None
        self._hitIval = None

    def generate(self):
        self.assign(render.attachNewNode('DistributedCorruptToon'))
        self.__buildStubGeom()
        DistributedNode.DistributedNode.generate(self)

    def announceGenerate(self):
        DistributedNode.DistributedNode.announceGenerate(self)
        self.reparentTo(render)

    def disable(self):
        if self._defeatIval is not None:
            self._defeatIval.finish()
            self._defeatIval = None
        if self._hitIval is not None:
            self._hitIval.finish()
            self._hitIval = None
        self.detachNode()
        DistributedNode.DistributedNode.disable(self)

    def delete(self):
        if self.geom is not None:
            self.geom.removeNode()
            self.geom = None
        if self.nametagNP is not None:
            self.nametagNP.removeNode()
            self.nametagNP = None
        if self.shadow is not None:
            self.shadow.removeNode()
            self.shadow = None
        DistributedNode.DistributedNode.delete(self)

    def __buildStubGeom(self):
        # Stacked cards approximate a rubber-hose silhouette without DNA deps.
        cm = CardMaker('corrupt-body')
        cm.setFrame(-0.6, 0.6, 0.0, 2.2)
        body = self.attachNewNode(cm.generate())
        body.setColor(*CorruptionGlobals.CORRUPT_TINT)
        body.setBillboardPointEye()
        body.setTransparency(TransparencyAttrib.MAlpha)

        head = CardMaker('corrupt-head')
        head.setFrame(-0.45, 0.45, 0.0, 0.9)
        headNP = self.attachNewNode(head.generate())
        headNP.setPos(0, 0, 2.15)
        headNP.setColor(0.15, 0.05, 0.22, 1.0)
        headNP.setBillboardPointEye()

        self.geom = body

        try:
            self.shadow = loader.loadModel('phase_3/models/props/drop_shadow')
            self.shadow.setScale(0.4)
            self.shadow.setColor(0, 0, 0, 0.45)
            self.shadow.setZ(0.025)
            self.shadow.reparentTo(self)
        except Exception:
            self.shadow = None

        text = TextNode('corrupt-name')
        text.setText(self.name)
        text.setAlign(TextNode.ACenter)
        text.setTextColor(0.85, 0.55, 1.0, 1.0)
        text.setShadow(0.05, 0.05)
        self.nametagNP = self.attachNewNode(text)
        self.nametagNP.setScale(0.45)
        self.nametagNP.setPos(0, 0, 3.3)
        self.nametagNP.setBillboardPointEye()

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

    def announceDefeat(self):
        if self._defeatIval is not None:
            self._defeatIval.finish()
        # Splat / squash cue for rubber-hose fantasy.
        self._defeatIval = Sequence(
            LerpScaleInterval(self, 0.2, Point3(1.4, 1.4, 0.2)),
            LerpScaleInterval(self, 0.15, Point3(0.05, 0.05, 0.05)),
            Func(self.hide),
        )
        self._defeatIval.start()

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
        stretch = 1.12 + 0.12 * hitIndex
        squash = 0.72 - 0.04 * hitIndex
        target = self.geom if self.geom is not None else self
        self._hitIval = Sequence(
            Parallel(
                LerpScaleInterval(target, 0.06, (stretch, stretch, squash)),
                LerpColorScaleInterval(target, 0.06, Vec4(1.6, 0.7, 1.9, 1)),
            ),
            Parallel(
                LerpScaleInterval(target, 0.1, (0.9, 0.9, 1.2)),
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
