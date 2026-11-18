"""Client-local demo hostiles for the melee foundation.

Stand-ins until CorruptToon (slice 2) lands. Spawns as ink-tinted billboards
in front of the player so soft-target + combo can be exercised without AI.
"""

from panda3d.core import (
    BitMask32,
    CardMaker,
    CollisionNode,
    CollisionSphere,
    NodePath,
    TextNode,
    TransparencyAttrib,
    Vec3,
    Vec4,
)

from direct.interval.IntervalGlobal import (
    LerpColorScaleInterval,
    LerpScaleInterval,
    Sequence,
)

from .SoftTarget import HackSlashTarget
from . import HackSlashConfig


class DemoHostile(HackSlashTarget, NodePath):

    def __init__(self, index, parent, pos):
        NodePath.__init__(self, 'hackslash-demo-hostile-%d' % index)
        self.reparentTo(parent)
        self.setPos(pos)
        self.index = index
        self.maxHp = HackSlashConfig.DEMO_HOSTILE_HP
        self.hp = self.maxHp
        self._hitIval = None

        cm = CardMaker('corrupt-card')
        cm.setFrame(-0.9, 0.9, 0.0, 2.4)
        card = self.attachNewNode(cm.generate())
        card.setBillboardPointEye()
        card.setTransparency(TransparencyAttrib.MAlpha)
        card.setColor(0.25, 0.05, 0.35, 0.85)
        self._visual = card

        cm2 = CardMaker('corrupt-card-arm')
        cm2.setFrame(-1.6, 1.6, 0.8, 1.2)
        arm = self.attachNewNode(cm2.generate())
        arm.setBillboardPointEye()
        arm.setTransparency(TransparencyAttrib.MAlpha)
        arm.setColor(0.15, 0.0, 0.2, 0.7)
        self._arm = arm

        label = TextNode('hostile-hp')
        label.setText(self._labelText())
        label.setAlign(TextNode.ACenter)
        label.setTextColor(1, 0.85, 1, 1)
        self._labelNP = self.attachNewNode(label)
        self._labelNP.setScale(0.55)
        self._labelNP.setPos(0, 0, 2.7)
        self._labelNP.setBillboardPointEye()

        cs = CollisionSphere(0, 0, 1.0, 1.1)
        cn = CollisionNode('hackslashHostile-%d' % index)
        cn.addSolid(cs)
        cn.setIntoCollideMask(BitMask32.bit(21))
        cn.setFromCollideMask(BitMask32.allOff())
        self._coll = self.attachNewNode(cn)
        self.setTag('hackslashHostile', str(index))
        self.setPythonTag('hackSlashTarget', self)

    def _labelText(self):
        return '%s\n%d/%d' % (
            HackSlashConfig.DEMO_HOSTILE_NAME, max(0, self.hp), self.maxHp)

    def isHackSlashTarget(self):
        return True

    def isHackSlashAlive(self):
        return self.hp > 0 and not self.isEmpty()

    def getHackSlashHp(self):
        return self.hp

    def getHackSlashName(self):
        return HackSlashConfig.DEMO_HOSTILE_NAME

    def getHackSlashPos(self):
        return self.getPos(render)  # noqa: F821

    def applyHackSlashHit(self, damage, hitIndex, attacker):
        if not self.isHackSlashAlive():
            return False
        self.hp = max(0, self.hp - int(damage))
        self._labelNP.node().setText(self._labelText())
        self._playHitReaction(hitIndex, attacker)
        if self.hp <= 0:
            self._playDefeat()
        return True

    def _playHitReaction(self, hitIndex, attacker=None):
        """Ink flash + knockback; scale squash/stretch is owned by MeleeCombat HitJuice."""
        if self._hitIval:
            self._hitIval.finish()
        self._hitIval = Sequence(
            LerpColorScaleInterval(self._visual, 0.06, Vec4(1.5, 0.6, 1.8, 1)),
            LerpColorScaleInterval(self._visual, 0.14, Vec4(1, 1, 1, 1)),
        )
        self._hitIval.start()
        try:
            if attacker is None:
                return
            away = self.getPos(render) - attacker.getPos(render)  # noqa: F821
            away.setZ(0)
            if away.length() > 0.01:
                away.normalize()
                self.setPos(self.getPos() + away * (0.85 + 0.3 * hitIndex))
        except Exception:
            pass

    def _playDefeat(self):
        if self._hitIval:
            self._hitIval.finish()
        self._hitIval = Sequence(
            LerpScaleInterval(self, 0.2, (1.6, 1.6, 0.05)),
            LerpColorScaleInterval(self, 0.15, Vec4(1, 1, 1, 0)),
        )
        self._hitIval.start()
        self._coll.stash()

    def cleanup(self):
        if self._hitIval:
            self._hitIval.finish()
            self._hitIval = None
        if not self.isEmpty():
            self.removeNode()


def spawnDemoHostiles(avatar, count=None):
    """Place demo hostiles in an arc in front of the local toon."""
    if count is None:
        count = HackSlashConfig.DEMO_HOSTILE_COUNT
    hostiles = []
    origin = avatar.getPos(render)  # noqa: F821
    quat = avatar.getQuat(render)  # noqa: F821
    forward = quat.getForward()
    forward.setZ(0)
    if forward.length() < 0.01:
        forward = Vec3(0, 1, 0)
    else:
        forward.normalize()
    right = quat.getRight()
    right.setZ(0)
    if right.length() < 0.01:
        right = Vec3(1, 0, 0)
    else:
        right.normalize()

    spacing = HackSlashConfig.DEMO_HOSTILE_SPACING
    for i in range(count):
        offset = (i - (count - 1) / 2.0) * (spacing * 0.65)
        pos = origin + forward * (spacing + 1.5) + right * offset
        pos.setZ(origin.getZ())
        hostiles.append(DemoHostile(i, render, pos))  # noqa: F821
    return hostiles
