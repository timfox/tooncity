from panda3d.core import (
    CardMaker, NodePath, TextNode, TransparencyAttrib, Vec4, Point3)

from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedNode
from direct.interval.IntervalGlobal import (
    LerpColorScaleInterval, LerpPosInterval, LerpScaleInterval, Parallel,
    Sequence, Func, Wait)
from direct.task import Task

from toontown.corruption import CorruptionGlobals
from toontown.corruption.CorruptDeathPopFx import (
    DeathPopSplat, buildBodyPopInterval, deathPopLook)
from toontown.reclaim.BossHpBarHud import (
    releaseCorruptToon as releaseBossHpBar,
    syncFromCorruptToon as syncBossHpBar)
from toontown.corruption.BalloonSnareTelegraphFx import BalloonSnareTelegraphString
from toontown.corruption.BruteSludgeSplashFx import BruteSludgeSplash
from toontown.corruption.BruteSpitCreamSplashFx import BruteSpitCreamSplash
from toontown.corruption.BruteSpitTelegraphFx import BruteSpitTelegraphGob
from toontown.corruption.CorruptTelegraphCreamSparkleFx import TelegraphCreamSparkles
from toontown.corruption.CorruptTelegraphCreamWarnFx import TelegraphCreamWarnFlecks
from toontown.corruption.CorruptTelegraphCreamWashFx import TelegraphCreamWashPulse
from toontown.corruption.CorruptTelegraphInkFx import TelegraphInkDrip
from toontown.corruption.GagsterPuddleCreamSplashFx import GagsterPuddleCreamSplash
from toontown.corruption.GagsterPuddleTelegraphFx import GagsterPuddleTelegraphWarn
from toontown.corruption.HackSlashTarget import HackSlashTarget
from toontown.corruption.CorruptSilhouetteCreamRimFx import SilhouetteCreamRimFlecks
from toontown.corruption.CorruptSilhouetteCreamSparkleFx import SilhouetteCreamSparkles
from toontown.corruption.CorruptSilhouetteCreamWashFx import SilhouetteCreamWashPulse
from toontown.corruption.IdleCreamDripContrastFx import IdleCreamDripContrast
from toontown.corruption.IdleCreamDripSparkleFx import IdleCreamDripSparkles
from toontown.corruption.IdleCreamWashPulseFx import IdleCreamWashPulse
from toontown.corruption.IdleInkDripFx import IdleInkDrip
from toontown.corruption.OverlordHitCreamWashFx import OverlordHitCreamWashPulse
from toontown.corruption.OverlordMagentaInkSplashFx import OverlordMagentaInkSplash
from toontown.corruption.OverlordPhaseInkRainFx import OverlordPhaseInkRain
from toontown.corruption.OverlordTelegraphCrownFx import OverlordTelegraphCrown
from toontown.corruption.OverlordTelegraphPunchFx import (
    OverlordTelegraphPunch, overlordTelegraphAnimSecs)
from toontown.corruption.OswaldBetrayalSplashFx import OswaldBetrayalSplash
from toontown.corruption.OswaldBetrayalTelegraphFx import (
    OswaldBetrayalTelegraphStain)
from toontown.corruption.SmudgeHitCreamSplashFx import SmudgeHitCreamSplash
from toontown.corruption.SmudgeHitCreamWashFx import SmudgeHitCreamWashPulse
from toontown.corruption.SmudgeInkSplashFx import SmudgeInkSplash
from toontown.corruption.SmudgeInkTelegraphFx import SmudgeInkTelegraphFist
from toontown.corruption.SnareStringCounterCreamSplashFx import (
    SnareStringCounterCreamSplash)
from toontown.corruption.SnareStringSnapSplashFx import SnareStringSnapSplash


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
        self._telegraphMove = ''
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
        self._gagsterTelegraphSfx = None
        self._gagsterHitSfx = None
        # Finale Overlord phase SFX caches keyed by phase index.
        self._finaleTelegraphSfx = {}
        self._finaleHitSfx = {}
        self._spitBlobIval = None
        self._spitBlobNP = None
        self._stringLashIval = None
        self._stringLashNP = None
        self._gagLobIval = None
        self._gagLobNP = None
        self._gagPuddleIval = None
        self._gagPuddleNP = None
        self._gagsterSludgeSlow = None
        self._deathPopSplat = None
        self._telegraphInkDrip = None
        self._telegraphCreamWarn = None
        self._telegraphCreamSparkle = None
        self._telegraphCreamWash = None
        self._idleInkDrip = None
        self._idleCreamDrip = None
        self._idleCreamDripSparkle = None
        self._idleCreamWash = None
        self._silhouetteCreamRim = None
        self._silhouetteCreamSparkle = None
        self._silhouetteCreamWash = None
        self._overlordCrown = None
        self._overlordInkRain = None
        self._overlordTelegraphPunch = None
        self._overlordMagentaInkSplash = None
        self._overlordHitCreamWash = None
        self._snareTelegraphString = None
        self._snareStringSnapSplash = None
        self._snareStringCounterCreamSplash = None
        self._snareStringCounterTask = None
        self._snareStringCounterArmed = False
        self._snareStringCounterUntil = 0.0
        # Brute spit / Gagster lob dedicated counter schedule tasks (thin
        # client hooks — MeleeCombat owns the rewarded opener window).
        self._bruteSpitCounterTask = None
        self._gagsterLobCounterTask = None
        self._bruteTelegraphSpit = None
        self._bruteSludgeSplash = None
        self._bruteSpitCreamSplash = None
        self._smudgeTelegraphInk = None
        self._smudgeInkSplash = None
        self._smudgeHitCreamWash = None
        self._oswaldTelegraphStain = None
        self._oswaldBetrayalSplash = None
        self._gagsterTelegraphPuddle = None
        self._gagsterPuddleCreamSplash = None
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
        self.__startIdleCreamDrip()
        self.__startIdleCreamDripSparkle()
        self.__startIdleCreamWash()
        self.__startSilhouetteCreamRim()
        self.__startSilhouetteCreamSparkle()
        self.__startSilhouetteCreamWash()

    def disable(self):
        releaseBossHpBar(self)
        self.__stopIntervals()
        self.detachNode()
        DistributedNode.DistributedNode.disable(self)

    def delete(self):
        releaseBossHpBar(self)
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
                     '_spitBlobIval', '_stringLashIval',
                     '_gagLobIval', '_gagPuddleIval'):
            ival = getattr(self, attr, None)
            if ival is not None:
                ival.finish()
                setattr(self, attr, None)
        self.__clearAttackFlash()
        self.__clearSpitBlob()
        self.__clearStringLash()
        self.__clearGagLob()
        self.__clearGagPuddle()
        self.__clearTelegraphInkDrip()
        self.__clearTelegraphCreamWarn()
        self.__clearTelegraphCreamSparkle()
        self.__clearTelegraphCreamWash()
        self.__clearIdleInkDrip()
        self.__clearIdleCreamDrip()
        self.__clearIdleCreamDripSparkle()
        self.__clearIdleCreamWash()
        self.__clearSilhouetteCreamRim()
        self.__clearSilhouetteCreamSparkle()
        self.__clearSilhouetteCreamWash()
        self.__clearOverlordTelegraphCrown()
        self.__clearOverlordPhaseInkRain()
        self.__clearOverlordTelegraphPunch()
        self.__clearOverlordMagentaInkSplash()
        self.__clearOverlordHitCreamWash()
        self.__clearSnareTelegraphString()
        self.__clearSnareStringSnapSplash()
        self.__clearSnareStringCounterCreamSplash()
        self.__clearSnareStringSnapCounter()
        self.__clearBruteSpitCounter()
        self.__clearGagsterLobCounter()
        self.__clearOswaldBetrayalLungeCounter()
        self.__clearOswaldStainBurstCounter()
        self.__clearOverlordRainCounter()
        self.__clearOverlordSlamCounter()
        self.__clearOverlordInkSurgeCounter()
        self.__clearBruteTelegraphSpit()
        self.__clearBruteSludgeSplash()
        self.__clearBruteSpitCreamSplash()
        self.__clearSmudgeTelegraphInk()
        self.__clearSmudgeInkSplash()
        self.__clearSmudgeHitCreamSplash()
        self.__clearSmudgeHitCreamWash()
        self.__clearOswaldTelegraphStain()
        self.__clearOswaldBetrayalSplash()
        self.__clearGagsterTelegraphPuddle()
        self.__clearGagsterPuddleCreamSplash()
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
        syncBossHpBar(self)

    def getName(self):
        return self.name

    def setArchetype(self, archetype):
        self.archetype = int(archetype)
        self.__applyArchetypeLook()
        # Retint ambient idle drips when archetype arrives after generate.
        if getattr(self, '_idleInkDrip', None) is not None:
            self.__startIdleInkDrip()
        if getattr(self, '_idleCreamDrip', None) is not None:
            self.__startIdleCreamDrip()
        if getattr(self, '_idleCreamDripSparkle', None) is not None:
            self.__startIdleCreamDripSparkle()
        if getattr(self, '_idleCreamWash', None) is not None:
            self.__startIdleCreamWash()
        if getattr(self, '_silhouetteCreamRim', None) is not None:
            self.__startSilhouetteCreamRim()
        if getattr(self, '_silhouetteCreamSparkle', None) is not None:
            self.__startSilhouetteCreamSparkle()
        if getattr(self, '_silhouetteCreamWash', None) is not None:
            self.__startSilhouetteCreamWash()
        syncBossHpBar(self)

    def getArchetype(self):
        return int(getattr(self, 'archetype', CorruptionGlobals.ARCHETYPE_INK))

    def __applyArchetypeLook(self):
        """Scale/tint for Smudge / Brute / Snare / Gagster (finale look wins)."""
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
        syncBossHpBar(self)

    def getHp(self):
        return self.hp

    def setMaxHp(self, maxHp):
        self.maxHp = int(maxHp)
        syncBossHpBar(self)

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

    def __isGunkGagster(self):
        """True when this enemy should use Gunk Gagster gag-lob / puddle AV."""
        return (
            int(getattr(self, 'archetype', CorruptionGlobals.ARCHETYPE_INK))
            == CorruptionGlobals.ARCHETYPE_GAGSTER)

    def __isCorruptOswald(self):
        """True when this enemy should use Corrupted Oswald betrayal AV."""
        return (
            int(getattr(self, 'archetype', CorruptionGlobals.ARCHETYPE_INK))
            == CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD)

    def __isInkOverlord(self):
        """True when finale phase look is active (Ink Overlord boss)."""
        look, phase = self.__finalePhaseLook()
        return bool(look) and int(phase) >= 1

    def announceAttackTelegraph(self, moveId=''):
        """Strong wind-up: charged squash, ink/spit/lash/lob flare — dodgeable.

        ``moveId`` carries the AI attack move so Overlord AV can read rain vs
        slam vs ink_surge distinctly (street kits pass their attackMove).
        """
        if self._telegraphIval is not None:
            self._telegraphIval.finish()
        if self._attackHitIval is not None:
            self._attackHitIval.finish()
            self._attackHitIval = None
        if self._pulseIval is not None:
            self._pulseIval.pause()
        self._telegraphMove = str(moveId or '')
        target = self.visualRoot if self.visualRoot is not None else self
        look, phase = self.__finalePhaseLook()
        isBrute = self.__isBruteSpit()
        isSnare = self.__isBalloonSnare()
        isGagster = self.__isGunkGagster()
        isOswald = self.__isCorruptOswald()
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
        elif isGagster:
            # Teal gag-lob wind-up — crouch then upward toss stretch.
            charge = Vec4(*CorruptionGlobals.GAGSTER_TELEGRAPH_CHARGE_COLOR)
            hold = Vec4(*CorruptionGlobals.GAGSTER_TELEGRAPH_HOLD_COLOR)
            squash = Point3(*CorruptionGlobals.GAGSTER_TELEGRAPH_SQUASH)
            mid = Point3(*CorruptionGlobals.GAGSTER_TELEGRAPH_MID)
            stretch = Point3(*CorruptionGlobals.GAGSTER_TELEGRAPH_STRETCH)
        elif isOswald:
            # Betrayal crimson lunge — not Smudge purple fallthrough.
            charge = Vec4(*CorruptionGlobals.OSWALD_TELEGRAPH_CHARGE_COLOR)
            hold = Vec4(*CorruptionGlobals.OSWALD_TELEGRAPH_HOLD_COLOR)
            squash = Point3(*CorruptionGlobals.OSWALD_TELEGRAPH_SQUASH)
            mid = Point3(*CorruptionGlobals.OSWALD_TELEGRAPH_MID)
            stretch = Point3(*CorruptionGlobals.OSWALD_TELEGRAPH_STRETCH)
        else:
            # Ink Smudge melee telegraph — purple charge (unchanged).
            charge = Vec4(*CorruptionGlobals.TELEGRAPH_CHARGE_COLOR)
            hold = Vec4(*CorruptionGlobals.TELEGRAPH_HOLD_COLOR)
            squash = Point3(1.85, 1.85, 0.42)
            mid = Point3(1.65, 1.65, 0.5)
            stretch = Point3(0.62, 0.62, 1.7)
        self.__playOptionalActorPose('angry')
        self.__playTelegraphSfx()
        # Pause ambient idle drips / sparkles / wash / rim flecks so telegraph juice owns the frame.
        self.__pauseIdleInkDrip()
        self.__pauseIdleCreamDrip()
        self.__pauseIdleCreamDripSparkle()
        self.__pauseIdleCreamWash()
        self.__pauseSilhouetteCreamRim()
        self.__pauseSilhouetteCreamSparkle()
        self.__pauseSilhouetteCreamWash()
        self.__playTelegraphInkDrip(look)
        # Cream / pastel warn flecks — contrast layer on ink drip / silhouette.
        self.__playTelegraphCreamWarn(look)
        # Rising cream / pastel sparkles from the telegraph cream warn spray.
        self.__playTelegraphCreamSparkle(look)
        # Soft cream wash pulse against ink telegraph (silhouette / idle wash vocab).
        self.__playTelegraphCreamWash(look)
        # Ink Smudge-only: purple ink-fist telegraph pop for melee wind-up read.
        if ((not look) and (not isBrute) and (not isSnare)
                and (not isGagster) and (not isOswald)):
            self.__playSmudgeTelegraphInk()
        else:
            self.__clearSmudgeTelegraphInk()
        # Corrupted Oswald-only: crimson stain-lunge telegraph (not Smudge).
        # betrayal_lunge / stain_burst also arm Snare-like dedicated
        # counter→melee windows (thin messenger hooks; interrupt ≠ counter).
        telegraphMove = str(getattr(self, '_telegraphMove', '') or '')
        if isOswald and not look:
            self.__playOswaldTelegraphStain()
            if ((not telegraphMove) or telegraphMove in (
                    'betrayal_lunge', 'smack')):
                self.__scheduleOswaldBetrayalLungeCounter()
                self.__clearOswaldStainBurstCounter()
            elif telegraphMove == 'stain_burst':
                self.__scheduleOswaldStainBurstCounter()
                self.__clearOswaldBetrayalLungeCounter()
            else:
                self.__clearOswaldBetrayalLungeCounter()
                self.__clearOswaldStainBurstCounter()
        else:
            self.__clearOswaldTelegraphStain()
            self.__clearOswaldBetrayalLungeCounter()
            self.__clearOswaldStainBurstCounter()
        # Sludge Brute-only: green spit-gob telegraph pop for ranged spit read.
        # Spit move also arms a Snare-like dedicated counter→melee window
        # (thin messenger hook; slam stays commit-through / no counter).
        if isBrute and not look:
            self.__playBruteTelegraphSpit()
            if telegraphMove == 'spit':
                self.__scheduleBruteSpitCounter()
            else:
                self.__clearBruteSpitCounter()
        else:
            self.__clearBruteTelegraphSpit()
            self.__clearBruteSpitCounter()
        # Balloon Snare-only: amber string-lash telegraph pop for zip/lash read.
        if isSnare and not look:
            self.__playSnareTelegraphString()
            # After the string pops readable, arm a short punish→melee window.
            self.__scheduleSnareStringSnapCounter()
        else:
            self.__clearSnareTelegraphString()
            self.__clearSnareStringSnapCounter()
        # Gunk Gagster-only: teal bounce-pie + cream/ink puddle warn for lob read.
        # gag_lob also arms a Snare-like dedicated counter→melee window.
        if isGagster and not look:
            self.__playGagsterTelegraphPuddle()
            if (not telegraphMove) or telegraphMove == 'gag_lob':
                self.__scheduleGagsterLobCounter()
            else:
                self.__clearGagsterLobCounter()
        else:
            self.__clearGagsterTelegraphPuddle()
            self.__clearGagsterLobCounter()
        # Overlord-only: crown always; rain shower only on rain; danger-ring
        # warn on rain / slam / ink_surge with move-scaled footprint.
        # rain / slam / ink_surge also arm Snare-like dedicated
        # counter→melee windows by move id (thin messenger hooks;
        # interrupt ≠ counter).
        if look and phase >= 1:
            overlordMove = (
                CorruptionGlobals.normalizeOverlordTelegraphMove(
                    getattr(self, '_telegraphMove', ''))
                or 'rain')
            self.__playOverlordTelegraphCrown(look, phase)
            if CorruptionGlobals.overlordTelegraphShowsInkRain(overlordMove):
                self.__playOverlordPhaseInkRain(look, phase)
            else:
                self.__clearOverlordPhaseInkRain()
            if CorruptionGlobals.overlordTelegraphShowsPunchWarn(overlordMove):
                self.__playOverlordTelegraphPunchWarn(
                    look, phase, moveId=overlordMove)
            else:
                self.__clearOverlordTelegraphPunch()
            # Phase + move HUD cue so rain / slam / surge read mid-wind-up.
            messenger.send(  # noqa: F821
                'finaleTelegraphCue',
                [phase,
                 CorruptionGlobals.overlordTelegraphMoveHudCue(
                     overlordMove, phase, look),
                 look.get('hudColor', (1.0, 0.55, 1.0, 1.0))])
            if overlordMove == 'rain':
                self.__scheduleOverlordRainCounter()
                self.__clearOverlordSlamCounter()
                self.__clearOverlordInkSurgeCounter()
            elif overlordMove == 'slam':
                self.__scheduleOverlordSlamCounter()
                self.__clearOverlordRainCounter()
                self.__clearOverlordInkSurgeCounter()
            elif overlordMove == 'ink_surge':
                self.__scheduleOverlordInkSurgeCounter()
                self.__clearOverlordRainCounter()
                self.__clearOverlordSlamCounter()
            else:
                self.__clearOverlordRainCounter()
                self.__clearOverlordSlamCounter()
                self.__clearOverlordInkSurgeCounter()
        else:
            self.__clearOverlordTelegraphCrown()
            self.__clearOverlordPhaseInkRain()
            self.__clearOverlordTelegraphPunch()
            self.__clearOverlordRainCounter()
            self.__clearOverlordSlamCounter()
            self.__clearOverlordInkSurgeCounter()
        # Hold the charged pose across most of ATTACK_TELEGRAPH_DELAY so the
        # wind-up reads clearly before announceAttackHit's slam lands.
        # Overlord uses phase-aware timings so stretch lingers until impact.
        if look:
            anim = overlordTelegraphAnimSecs(finaleLook=look, phase=phase)
            squashSec = float(anim['squashSec'])
            midSec = float(anim['midSec'])
            stretchSec = float(anim['stretchSec'])
            holdSec = float(anim['holdSec'])
            recoverSec = float(anim['recoverSec'])
        else:
            squashSec = 0.12
            midSec = 0.18
            stretchSec = 0.14
            holdSec = 0.12
            recoverSec = 0.1
        self._telegraphIval = Sequence(
            Parallel(
                LerpScaleInterval(target, squashSec, squash),
                LerpColorScaleInterval(target, squashSec, charge),
            ),
            Parallel(
                LerpScaleInterval(target, midSec, mid),
                LerpColorScaleInterval(target, midSec, hold),
            ),
            Parallel(
                LerpScaleInterval(target, stretchSec, stretch),
                LerpColorScaleInterval(target, stretchSec, charge),
            ),
            # Linger stretched so the strike pose sticks until impact.
            # On miss (no announceAttackHit), ease back and resume ink pulse.
            Wait(holdSec),
            Parallel(
                LerpScaleInterval(target, recoverSec, Point3(1.0, 1.0, 1.0)),
                LerpColorScaleInterval(target, recoverSec, Vec4(1, 1, 1, 1)),
            ),
            Func(self.__resumePulse),
        )
        self._telegraphIval.start()

    def announceAttackHit(self):
        """Impact feedback when AI damage lands — slam, flash, thud/spit/lash/lob."""
        # Pause (don't finish) so telegraph's miss-recovery Funcs don't snap.
        if self._telegraphIval is not None:
            try:
                self._telegraphIval.pause()
            except Exception:
                pass
            self._telegraphIval = None
        # Clear telegraph drip / cream warn / sparkle / wash / crown / rain /
        # punch warn / snare / spit / smudge fist / gagster puddle warn so
        # impact owns the frame.
        self.__clearTelegraphInkDrip()
        self.__clearTelegraphCreamWarn()
        self.__clearTelegraphCreamSparkle()
        self.__clearTelegraphCreamWash()
        self.__clearOverlordTelegraphCrown()
        self.__clearOverlordPhaseInkRain()
        self.__clearOverlordTelegraphPunch()
        self.__clearSnareTelegraphString()
        # Impact lands on the player — drop any pending telegraph counters.
        self.__clearSnareStringSnapCounter()
        self.__clearOswaldBetrayalLungeCounter()
        self.__clearOswaldStainBurstCounter()
        self.__clearOverlordRainCounter()
        self.__clearOverlordSlamCounter()
        self.__clearOverlordInkSurgeCounter()
        self.__clearBruteTelegraphSpit()
        self.__clearSmudgeTelegraphInk()
        self.__clearOswaldTelegraphStain()
        self.__clearGagsterTelegraphPuddle()
        if self._attackHitIval is not None:
            self._attackHitIval.finish()
        target = self.visualRoot if self.visualRoot is not None else self
        look, phase = self.__finalePhaseLook()
        isBrute = self.__isBruteSpit()
        isSnare = self.__isBalloonSnare()
        isGagster = self.__isGunkGagster()
        isOswald = self.__isCorruptOswald()
        if look:
            impactScale = Point3(*look['impactScale'])
            impactColor = Vec4(*look['impactColor'])
            rebound = Vec4(*look.get(
                'rebound', (1.1, 0.55, 1.35, 1.0)))
            anim = overlordTelegraphAnimSecs(finaleLook=look, phase=phase)
            slamSec = float(anim['impactSlamSec'])
            reboundSec = float(anim['impactReboundSec'])
            settleSec = float(anim['impactSettleSec'])
            reboundScale = Point3(*look.get(
                'impactReboundScale', (0.85, 0.85, 1.25)))
        elif isBrute:
            impactScale = Point3(1.7, 1.7, 0.48)
            impactColor = Vec4(0.55, 2.35, 0.4, 1.0)
            rebound = Vec4(0.55, 1.25, 0.4, 1.0)
            slamSec = 0.06
            reboundSec = 0.1
            settleSec = 0.12
            reboundScale = Point3(0.85, 0.85, 1.25)
        elif isSnare:
            impactScale = Point3(2.15, 0.55, 0.7)
            impactColor = Vec4(2.4, 1.55, 0.4, 1.0)
            rebound = Vec4(1.35, 0.85, 0.35, 1.0)
            slamSec = 0.06
            reboundSec = 0.1
            settleSec = 0.12
            reboundScale = Point3(0.85, 0.85, 1.25)
        elif isGagster:
            impactScale = Point3(1.45, 1.45, 0.7)
            impactColor = Vec4(0.45, 2.15, 2.35, 1.0)
            rebound = Vec4(0.45, 1.15, 1.25, 1.0)
            slamSec = 0.06
            reboundSec = 0.1
            settleSec = 0.12
            reboundScale = Point3(0.85, 0.85, 1.25)
        elif isOswald:
            # Betrayal crimson impact — not Smudge purple.
            impactScale = Point3(1.7, 1.45, 0.5)
            impactColor = Vec4(2.35, 0.55, 0.65, 1.0)
            rebound = Vec4(1.45, 0.35, 0.42, 1.0)
            slamSec = 0.06
            reboundSec = 0.1
            settleSec = 0.12
            reboundScale = Point3(0.85, 0.85, 1.25)
        else:
            impactScale = Point3(1.55, 1.55, 0.55)
            impactColor = Vec4(2.2, 0.9, 2.4, 1.0)
            rebound = Vec4(1.1, 0.55, 1.35, 1.0)
            slamSec = 0.06
            reboundSec = 0.1
            settleSec = 0.12
            reboundScale = Point3(0.85, 0.85, 1.25)
        self.__playAttackHitSfx()
        self.__playAttackHitFlash()
        if look:
            # Overlord impact ground punch bloom — warn ring already cleared.
            self.__playOverlordTelegraphPunchImpact(look, phase)
        if isBrute:
            self.__playSpitBlob()
        elif isSnare:
            self.__playStringLash()
        elif isGagster:
            self.__playGagLob()
        self.__playOptionalActorPose('neutral')
        self._attackHitIval = Sequence(
            Parallel(
                LerpScaleInterval(target, slamSec, impactScale),
                LerpColorScaleInterval(target, slamSec, impactColor),
            ),
            Parallel(
                LerpScaleInterval(target, reboundSec, reboundScale),
                LerpColorScaleInterval(target, reboundSec, rebound),
            ),
            Parallel(
                LerpScaleInterval(target, settleSec, Point3(1.0, 1.0, 1.0)),
                LerpColorScaleInterval(target, settleSec, Vec4(1, 1, 1, 1)),
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
        # Drop Overlord warn ring / crown / rain so dodge owns the recover beat.
        self.__clearOverlordTelegraphCrown()
        self.__clearOverlordPhaseInkRain()
        self.__clearOverlordTelegraphPunch()
        # Hackslash listens and plays perfect-dodge ink sparkle juice.
        messenger.send('corruptToonAttackDodged', [self])  # noqa: F821

    def __resumePulse(self):
        if self._pulseIval is not None and not self._defeatedHidden():
            self._pulseIval.resume()
        # Ambient pollution drips / sparkles / wash / rim flecks resume with the idle pulse.
        self.__resumeIdleInkDrip()
        self.__resumeIdleCreamDrip()
        self.__resumeIdleCreamDripSparkle()
        self.__resumeIdleCreamWash()
        self.__resumeSilhouetteCreamRim()
        self.__resumeSilhouetteCreamSparkle()
        self.__resumeSilhouetteCreamWash()

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
        if self._gagsterTelegraphSfx is None:
            try:
                self._gagsterTelegraphSfx = base.loader.loadSfx(
                    CorruptionGlobals.GAGSTER_TELEGRAPH_SFX)
            except Exception:
                self._gagsterTelegraphSfx = False
        if self._gagsterHitSfx is None:
            try:
                self._gagsterHitSfx = base.loader.loadSfx(
                    CorruptionGlobals.GAGSTER_ATTACK_HIT_SFX)
            except Exception:
                self._gagsterHitSfx = False

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
        elif self.__isGunkGagster() and self._gagsterTelegraphSfx:
            sfx = self._gagsterTelegraphSfx
            volume = CorruptionGlobals.GAGSTER_TELEGRAPH_SFX_VOLUME
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
        elif self.__isGunkGagster() and self._gagsterHitSfx:
            sfx = self._gagsterHitSfx
            volume = CorruptionGlobals.GAGSTER_ATTACK_HIT_SFX_VOLUME
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
            elif self.__isGunkGagster():
                color = CorruptionGlobals.GAGSTER_HIT_FLASH_COLOR
                peak = CorruptionGlobals.GAGSTER_HIT_FLASH_PEAK
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
            # Match AI spit projectile travel so land AV tracks flight time.
            travel = float(getattr(
                CorruptionGlobals, 'BRUTE_SPIT_TRAVEL_SEC',
                CorruptionGlobals.BRUTE_SPIT_BLOB_TRAVEL))
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
            # Cream splash aftershock so spit land reads juicy vs green ink.
            self.__playBruteSpitCreamSplash(end)
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

    def __playGagLob(self):
        """Teal gunk pie arcs from Gagster toward the local toon, then puddles."""
        self.__clearGagLob()
        try:
            start = self.getPos(render)
            start.setZ(start.getZ() + CorruptionGlobals.GAGSTER_LOB_Z)
            end = start + Point3(0, 7, -1.5)
            la = getattr(base, 'localAvatar', None)
            if la is not None and not la.isEmpty():
                end = la.getPos(render)
                end.setZ(end.getZ() + 0.35)
            mid = Point3(
                (start.getX() + end.getX()) * 0.5,
                (start.getY() + end.getY()) * 0.5,
                max(start.getZ(), end.getZ()) + CorruptionGlobals.GAGSTER_LOB_ARC_Z)
            cm = CardMaker('gagster-gunk-lob')
            half = CorruptionGlobals.GAGSTER_LOB_SCALE
            cm.setFrame(-half, half, -half, half)
            blob = render.attachNewNode(cm.generate())
            blob.setPos(start)
            blob.setBillboardPointEye()
            blob.setTransparency(TransparencyAttrib.MAlpha)
            color = CorruptionGlobals.GAGSTER_LOB_COLOR
            blob.setColor(color[0], color[1], color[2], color[3])
            blob.setBin('fixed', 40)
            blob.setDepthWrite(False)
            travel = float(CorruptionGlobals.GAGSTER_LOB_TRAVEL)
            halfTravel = travel * 0.5
            self._gagLobNP = blob
            self._gagLobIval = Sequence(
                Parallel(
                    LerpPosInterval(blob, halfTravel, mid, blendType='easeOut'),
                    LerpScaleInterval(
                        blob, halfTravel, Point3(1.15, 1.15, 1.15),
                        startScale=Point3(0.55, 0.55, 0.55)),
                ),
                Parallel(
                    LerpPosInterval(blob, halfTravel, end, blendType='easeIn'),
                    LerpScaleInterval(blob, halfTravel, Point3(1.45, 1.45, 0.7)),
                ),
                Func(self.__clearGagLob),
                Func(self.__playGagPuddle, end),
            )
            self._gagLobIval.start()
        except Exception:
            self.__clearGagLob()

    def __clearGagLob(self):
        if self._gagLobIval is not None:
            try:
                self._gagLobIval.pause()
            except Exception:
                pass
            self._gagLobIval = None
        if self._gagLobNP is not None:
            try:
                if not self._gagLobNP.isEmpty():
                    self._gagLobNP.removeNode()
            except Exception:
                pass
            self._gagLobNP = None

    def __playGagPuddle(self, landPos):
        """Flat teal puddle ring at the lob landing — trap-readable splat.

        When linger hazard is armed, hold the ring through the sludge window
        so the DoT / slow zone stays readable (gameplay trap, not cream FX).
        """
        self.__clearGagPuddle()
        try:
            cm = CardMaker('gagster-gunk-puddle')
            half = float(CorruptionGlobals.GAGSTER_PUDDLE_HALF)
            cm.setFrame(-half, half, -half, half)
            puddle = render.attachNewNode(cm.generate())
            puddle.setPos(landPos)
            puddle.setP(-90)
            puddle.setTransparency(TransparencyAttrib.MAlpha)
            color = CorruptionGlobals.GAGSTER_PUDDLE_COLOR
            puddle.setColor(color[0], color[1], color[2], color[3])
            puddle.setBin('fixed', 38)
            puddle.setDepthWrite(False)
            peak = float(CorruptionGlobals.GAGSTER_PUDDLE_PEAK)
            sec = float(CorruptionGlobals.GAGSTER_PUDDLE_SEC)
            lingerOn = bool(getattr(
                CorruptionGlobals, 'GAGSTER_PUDDLE_LINGER_ENABLED', True))
            lingerSec = float(getattr(
                CorruptionGlobals, 'GAGSTER_PUDDLE_LINGER_SEC', 0.0) or 0.0)
            if not lingerOn:
                lingerSec = 0.0
            bloomSec = sec * 0.45
            fadeSec = sec * 0.55
            holdSec = max(0.0, lingerSec)
            self._gagPuddleNP = puddle
            parts = [
                LerpScaleInterval(
                    puddle, bloomSec, Point3(peak, peak, 1.0),
                    startScale=Point3(0.35, 0.35, 1.0)),
            ]
            if holdSec > 0.0:
                parts.append(Wait(holdSec))
            parts.extend([
                Parallel(
                    LerpScaleInterval(
                        puddle, fadeSec,
                        Point3(peak * 1.15, peak * 1.15, 1.0)),
                    LerpColorScaleInterval(puddle, fadeSec, Vec4(1, 1, 1, 0)),
                ),
                Func(self.__clearGagPuddle),
            ])
            self._gagPuddleIval = Sequence(*parts)
            self._gagPuddleIval.start()
            # Cream splash aftershock so the trap land reads juicy vs teal ink.
            self.__playGagsterPuddleCreamSplash(landPos)
            # Client walk-slow while overlapping the linger sludge radius.
            if holdSec > 0.0:
                radius = float(CorruptionGlobals.archetypeStats(
                    CorruptionGlobals.ARCHETYPE_GAGSTER).get(
                        'attackHitRange',
                        CorruptionGlobals.GAGSTER_PUDDLE_LINGER_RADIUS))
                until = CorruptionGlobals.gagsterPuddleLingerUntil(
                    globalClock.getFrameTime(), holdSec)  # noqa: F821
                self.__armGagsterSludgeSlow(landPos, radius, until)
        except Exception:
            self.__clearGagPuddle()

    def __armGagsterSludgeSlow(self, landPos, radius, until):
        """Apply LocalAvatar walk-slow while standing in linger sludge."""
        self.__clearGagsterSludgeSlow()
        self._gagsterSludgeSlow = {
            'pos': landPos,
            'radius': float(radius),
            'until': float(until),
            'active': False,
        }
        taskMgr.add(  # noqa: F821
            self.__tickGagsterSludgeSlow,
            self.uniqueName('gagster-sludge-slow'))

    def __tickGagsterSludgeSlow(self, task):
        state = getattr(self, '_gagsterSludgeSlow', None)
        if state is None:
            return Task.done
        now = globalClock.getFrameTime()  # noqa: F821
        if now >= float(state['until']):
            self.__clearGagsterSludgeSlow()
            return Task.done
        la = getattr(base, 'localAvatar', None)  # noqa: F821
        inside = False
        if la is not None:
            try:
                if not la.isEmpty():
                    dx = float(la.getX(render)) - float(state['pos'].getX())
                    dy = float(la.getY(render)) - float(state['pos'].getY())
                    inside = CorruptionGlobals.isInsideGagsterPuddle(
                        dx, dy, state['radius'])
            except Exception:
                inside = False
        if inside and not state['active']:
            try:
                if hasattr(la, 'setWalkSpeedSlow'):
                    la.setWalkSpeedSlow()
                    state['active'] = True
            except Exception:
                pass
        elif (not inside) and state['active']:
            try:
                if hasattr(la, 'setWalkSpeedNormal'):
                    la.setWalkSpeedNormal()
            except Exception:
                pass
            state['active'] = False
        return Task.cont

    def __clearGagsterSludgeSlow(self):
        state = getattr(self, '_gagsterSludgeSlow', None)
        self._gagsterSludgeSlow = None
        try:
            taskMgr.remove(self.uniqueName('gagster-sludge-slow'))  # noqa: F821
        except Exception:
            pass
        if state and state.get('active'):
            la = getattr(base, 'localAvatar', None)  # noqa: F821
            try:
                if la is not None and hasattr(la, 'setWalkSpeedNormal'):
                    la.setWalkSpeedNormal()
            except Exception:
                pass

    def __clearGagPuddle(self):
        self.__clearGagsterSludgeSlow()
        if self._gagPuddleIval is not None:
            try:
                self._gagPuddleIval.pause()
            except Exception:
                pass
            self._gagPuddleIval = None
        if self._gagPuddleNP is not None:
            try:
                if not self._gagPuddleNP.isEmpty():
                    self._gagPuddleNP.removeNode()
            except Exception:
                pass
            self._gagPuddleNP = None

    def announceDefeat(self):
        releaseBossHpBar(self)
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
        if self._gagLobIval is not None:
            self._gagLobIval.finish()
            self._gagLobIval = None
        if self._gagPuddleIval is not None:
            self._gagPuddleIval.finish()
            self._gagPuddleIval = None
        self.__clearAttackFlash()
        self.__clearSpitBlob()
        self.__clearStringLash()
        self.__clearGagLob()
        self.__clearGagPuddle()
        self.__clearTelegraphInkDrip()
        self.__clearTelegraphCreamWarn()
        self.__clearTelegraphCreamSparkle()
        self.__clearTelegraphCreamWash()
        self.__clearIdleInkDrip()
        self.__clearIdleCreamDrip()
        self.__clearIdleCreamDripSparkle()
        self.__clearIdleCreamWash()
        self.__clearSilhouetteCreamRim()
        self.__clearSilhouetteCreamSparkle()
        self.__clearSilhouetteCreamWash()
        self.__clearOverlordTelegraphCrown()
        self.__clearOverlordPhaseInkRain()
        self.__clearOverlordTelegraphPunch()
        self.__clearOverlordMagentaInkSplash()
        self.__clearOverlordHitCreamWash()
        self.__clearSnareTelegraphString()
        self.__clearSnareStringSnapSplash()
        self.__clearSnareStringCounterCreamSplash()
        self.__clearSnareStringSnapCounter()
        self.__clearBruteSpitCounter()
        self.__clearGagsterLobCounter()
        self.__clearOswaldBetrayalLungeCounter()
        self.__clearOswaldStainBurstCounter()
        self.__clearOverlordRainCounter()
        self.__clearOverlordSlamCounter()
        self.__clearOverlordInkSurgeCounter()
        self.__clearBruteTelegraphSpit()
        self.__clearBruteSludgeSplash()
        self.__clearBruteSpitCreamSplash()
        self.__clearSmudgeTelegraphInk()
        self.__clearSmudgeInkSplash()
        self.__clearSmudgeHitCreamSplash()
        self.__clearSmudgeHitCreamWash()
        self.__clearOswaldTelegraphStain()
        self.__clearOswaldBetrayalSplash()
        self.__clearGagsterTelegraphPuddle()
        self.__clearGagsterPuddleCreamSplash()
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
        # Ink Overlord: magenta/crimson splash so boss pop reads vs street Smudge.
        if self.__isInkOverlord():
            self.__playOverlordMagentaInkSplash(splatPos, kind='death')
        # Ink Smudge: extra cheap purple splash so swarm deaths stay scannable.
        elif self.getArchetype() == CorruptionGlobals.ARCHETYPE_INK:
            self.__playSmudgeInkSplash(splatPos, kind='death')
        # Sludge Brute: green sludge splash so tank pops stay scannable.
        elif self.getArchetype() == CorruptionGlobals.ARCHETYPE_BRUTE:
            self.__playBruteSludgeSplash(splatPos, kind='death')
        # Balloon Snare: amber string-snap splash so zip-flier pops stay scannable.
        elif self.getArchetype() == CorruptionGlobals.ARCHETYPE_SNARE:
            self.__playSnareStringSnapSplash(splatPos, kind='death')
        # Corrupted Oswald: crimson betrayal splash — not Smudge purple.
        elif self.getArchetype() == CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD:
            self.__playOswaldBetrayalSplash(splatPos, kind='death')
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

    def __playTelegraphCreamWarn(self, finaleLook=None):
        """Cream / pastel warn flecks at telegraph start (contrast to ink)."""
        self.__clearTelegraphCreamWarn()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        flecks = TelegraphCreamWarnFlecks()
        self._telegraphCreamWarn = flecks
        flecks.play(
            pos,
            archetype=self.getArchetype(),
            finaleLook=finaleLook,
        )

    def __clearTelegraphCreamWarn(self):
        flecks = getattr(self, '_telegraphCreamWarn', None)
        if flecks is not None:
            try:
                flecks.clear()
            except Exception:
                pass
        self._telegraphCreamWarn = None

    def __playTelegraphCreamSparkle(self, finaleLook=None):
        """Rising cream / pastel sparkles from telegraph cream warn spray."""
        self.__clearTelegraphCreamSparkle()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        sparkles = TelegraphCreamSparkles()
        self._telegraphCreamSparkle = sparkles
        sparkles.play(
            pos,
            archetype=self.getArchetype(),
            finaleLook=finaleLook,
        )

    def __clearTelegraphCreamSparkle(self):
        sparkles = getattr(self, '_telegraphCreamSparkle', None)
        if sparkles is not None:
            try:
                sparkles.clear()
            except Exception:
                pass
        self._telegraphCreamSparkle = None

    def __playTelegraphCreamWash(self, finaleLook=None):
        """Soft cream wash pulse against ink telegraph cream warn / sparkle."""
        self.__clearTelegraphCreamWash()
        wash = TelegraphCreamWashPulse()
        self._telegraphCreamWash = wash
        wash.play(
            archetype=self.getArchetype(),
            finaleLook=finaleLook,
        )

    def __clearTelegraphCreamWash(self):
        wash = getattr(self, '_telegraphCreamWash', None)
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        self._telegraphCreamWash = None

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

    def __startIdleCreamDrip(self):
        """Cream / pastel contrast drips layered on idle ink (client-only)."""
        self.__clearIdleCreamDrip()
        if self._defeatedHidden():
            return
        parent = self.visualRoot if self.visualRoot is not None else self
        look, _phase = self.__finalePhaseLook()
        drip = IdleCreamDripContrast()
        self._idleCreamDrip = drip
        drip.start(
            parent,
            archetype=self.getArchetype(),
            finaleLook=look,
        )

    def __pauseIdleCreamDrip(self):
        drip = getattr(self, '_idleCreamDrip', None)
        if drip is not None:
            try:
                drip.pause()
            except Exception:
                pass

    def __resumeIdleCreamDrip(self):
        if self._defeatedHidden():
            return
        drip = getattr(self, '_idleCreamDrip', None)
        if drip is None:
            self.__startIdleCreamDrip()
            return
        try:
            drip.resume()
        except Exception:
            self.__startIdleCreamDrip()

    def __clearIdleCreamDrip(self):
        drip = getattr(self, '_idleCreamDrip', None)
        if drip is not None:
            try:
                drip.clear()
            except Exception:
                pass
        self._idleCreamDrip = None

    def __startIdleCreamDripSparkle(self):
        """Cream / pastel sparkle flecks on idle cream drip (client-only)."""
        self.__clearIdleCreamDripSparkle()
        if self._defeatedHidden():
            return
        parent = self.visualRoot if self.visualRoot is not None else self
        look, _phase = self.__finalePhaseLook()
        sparkles = IdleCreamDripSparkles()
        self._idleCreamDripSparkle = sparkles
        sparkles.start(
            parent,
            archetype=self.getArchetype(),
            finaleLook=look,
        )

    def __pauseIdleCreamDripSparkle(self):
        sparkles = getattr(self, '_idleCreamDripSparkle', None)
        if sparkles is not None:
            try:
                sparkles.pause()
            except Exception:
                pass

    def __resumeIdleCreamDripSparkle(self):
        if self._defeatedHidden():
            return
        sparkles = getattr(self, '_idleCreamDripSparkle', None)
        if sparkles is None:
            self.__startIdleCreamDripSparkle()
            return
        try:
            sparkles.resume()
        except Exception:
            self.__startIdleCreamDripSparkle()

    def __clearIdleCreamDripSparkle(self):
        sparkles = getattr(self, '_idleCreamDripSparkle', None)
        if sparkles is not None:
            try:
                sparkles.clear()
            except Exception:
                pass
        self._idleCreamDripSparkle = None

    def __startIdleCreamWash(self):
        """Soft cream wash + delayed cream aftershock against idle ink drips."""
        self.__clearIdleCreamWash()
        if self._defeatedHidden():
            return
        parent = self.visualRoot if self.visualRoot is not None else self
        look, _phase = self.__finalePhaseLook()
        wash = IdleCreamWashPulse()
        self._idleCreamWash = wash
        wash.start(
            parent,
            archetype=self.getArchetype(),
            finaleLook=look,
        )

    def __pauseIdleCreamWash(self):
        wash = getattr(self, '_idleCreamWash', None)
        if wash is not None:
            try:
                wash.pause()
            except Exception:
                pass

    def __resumeIdleCreamWash(self):
        if self._defeatedHidden():
            return
        wash = getattr(self, '_idleCreamWash', None)
        if wash is None:
            self.__startIdleCreamWash()
            return
        try:
            wash.resume()
        except Exception:
            self.__startIdleCreamWash()

    def __clearIdleCreamWash(self):
        wash = getattr(self, '_idleCreamWash', None)
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        self._idleCreamWash = None

    def __startSilhouetteCreamRim(self):
        """Cream / pastel rim flecks on the ink silhouette (client-only)."""
        self.__clearSilhouetteCreamRim()
        if self._defeatedHidden():
            return
        parent = self.visualRoot if self.visualRoot is not None else self
        look, _phase = self.__finalePhaseLook()
        flecks = SilhouetteCreamRimFlecks()
        self._silhouetteCreamRim = flecks
        flecks.start(
            parent,
            archetype=self.getArchetype(),
            finaleLook=look,
        )

    def __pauseSilhouetteCreamRim(self):
        flecks = getattr(self, '_silhouetteCreamRim', None)
        if flecks is not None:
            try:
                flecks.pause()
            except Exception:
                pass

    def __resumeSilhouetteCreamRim(self):
        if self._defeatedHidden():
            return
        flecks = getattr(self, '_silhouetteCreamRim', None)
        if flecks is None:
            self.__startSilhouetteCreamRim()
            return
        try:
            flecks.resume()
        except Exception:
            self.__startSilhouetteCreamRim()

    def __clearSilhouetteCreamRim(self):
        flecks = getattr(self, '_silhouetteCreamRim', None)
        if flecks is not None:
            try:
                flecks.clear()
            except Exception:
                pass
        self._silhouetteCreamRim = None

    def __startSilhouetteCreamSparkle(self):
        """Rising cream / pastel sparkle flecks on silhouette cream rim (client-only)."""
        self.__clearSilhouetteCreamSparkle()
        if self._defeatedHidden():
            return
        parent = self.visualRoot if self.visualRoot is not None else self
        look, _phase = self.__finalePhaseLook()
        sparkles = SilhouetteCreamSparkles()
        self._silhouetteCreamSparkle = sparkles
        sparkles.start(
            parent,
            archetype=self.getArchetype(),
            finaleLook=look,
        )

    def __pauseSilhouetteCreamSparkle(self):
        sparkles = getattr(self, '_silhouetteCreamSparkle', None)
        if sparkles is not None:
            try:
                sparkles.pause()
            except Exception:
                pass

    def __resumeSilhouetteCreamSparkle(self):
        if self._defeatedHidden():
            return
        sparkles = getattr(self, '_silhouetteCreamSparkle', None)
        if sparkles is None:
            self.__startSilhouetteCreamSparkle()
            return
        try:
            sparkles.resume()
        except Exception:
            self.__startSilhouetteCreamSparkle()

    def __clearSilhouetteCreamSparkle(self):
        sparkles = getattr(self, '_silhouetteCreamSparkle', None)
        if sparkles is not None:
            try:
                sparkles.clear()
            except Exception:
                pass
        self._silhouetteCreamSparkle = None

    def __startSilhouetteCreamWash(self):
        """Soft cream wash pulse against ink silhouette (client-only)."""
        self.__clearSilhouetteCreamWash()
        if self._defeatedHidden():
            return
        parent = self.visualRoot if self.visualRoot is not None else self
        look, _phase = self.__finalePhaseLook()
        wash = SilhouetteCreamWashPulse()
        self._silhouetteCreamWash = wash
        wash.start(
            parent,
            archetype=self.getArchetype(),
            finaleLook=look,
        )

    def __pauseSilhouetteCreamWash(self):
        wash = getattr(self, '_silhouetteCreamWash', None)
        if wash is not None:
            try:
                wash.pause()
            except Exception:
                pass

    def __resumeSilhouetteCreamWash(self):
        if self._defeatedHidden():
            return
        wash = getattr(self, '_silhouetteCreamWash', None)
        if wash is None:
            self.__startSilhouetteCreamWash()
            return
        try:
            wash.resume()
        except Exception:
            self.__startSilhouetteCreamWash()

    def __clearSilhouetteCreamWash(self):
        wash = getattr(self, '_silhouetteCreamWash', None)
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        self._silhouetteCreamWash = None

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

    def __playOverlordTelegraphPunchWarn(
            self, finaleLook=None, phase=1, moveId=''):
        """Ground danger-ring warn — Overlord phase telegraphs only."""
        self.__clearOverlordTelegraphPunch()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        punch = OverlordTelegraphPunch()
        self._overlordTelegraphPunch = punch
        punch.playWarn(
            pos, finaleLook=finaleLook, phase=phase, moveId=moveId)

    def __playOverlordTelegraphPunchImpact(
            self, finaleLook=None, phase=1, moveId=''):
        """Ground impact punch bloom — Overlord attack hit only."""
        self.__clearOverlordTelegraphPunch()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        punch = OverlordTelegraphPunch()
        self._overlordTelegraphPunch = punch
        if not moveId:
            moveId = getattr(self, '_telegraphMove', '') or ''
        punch.playImpact(
            pos, finaleLook=finaleLook, phase=phase, moveId=moveId)

    def __clearOverlordTelegraphPunch(self):
        punch = getattr(self, '_overlordTelegraphPunch', None)
        if punch is not None:
            try:
                punch.clear()
            except Exception:
                pass
        self._overlordTelegraphPunch = None

    def __playOverlordMagentaInkSplash(self, pos=None, kind='hit'):
        """Magenta/crimson ink splash — Ink Overlord hit / death only."""
        look, phase = self.__finalePhaseLook()
        if not look or int(phase) < 1:
            return
        self.__clearOverlordMagentaInkSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = OverlordMagentaInkSplash()
        self._overlordMagentaInkSplash = splash
        splash.play(pos, kind=kind, finaleLook=look, phase=phase)

    def __clearOverlordMagentaInkSplash(self):
        splash = getattr(self, '_overlordMagentaInkSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._overlordMagentaInkSplash = None

    def __playOverlordHitCreamWash(self):
        """Soft cream wash after Overlord magenta hit splash (hit path only)."""
        look, phase = self.__finalePhaseLook()
        if not look or int(phase) < 1:
            return
        self.__clearOverlordHitCreamWash()
        wash = OverlordHitCreamWashPulse()
        self._overlordHitCreamWash = wash
        wash.play(finaleLook=look, phase=phase)

    def __clearOverlordHitCreamWash(self):
        wash = getattr(self, '_overlordHitCreamWash', None)
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        self._overlordHitCreamWash = None

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

    def __scheduleSnareStringSnapCounter(self):
        """After string telegraph reads, arm a short punish→melee counter window.

        Client-only cue — MeleeCombat listens and reuses the perfect-dodge
        counter opener path so telegraph punish and dodge punish rhyme.
        Tracks local juice eligibility so a successful counter hit can fire
        cream splash / aftershock without leaving corruption/.
        """
        self.__clearSnareStringSnapCounter()
        if not getattr(
                CorruptionGlobals, 'SNARE_STRING_COUNTER_ENABLED', True):
            return
        delay = float(getattr(
            CorruptionGlobals, 'SNARE_STRING_COUNTER_ARM_DELAY_SEC', 0.14))
        window = float(getattr(
            CorruptionGlobals, 'SNARE_STRING_COUNTER_WINDOW_SEC', 0.48))
        event = str(getattr(
            CorruptionGlobals, 'SNARE_STRING_COUNTER_EVENT',
            'corruptSnareStringSnapCounter'))

        def _fire(task=None):
            self._snareStringCounterTask = None
            try:
                now = globalClock.getFrameTime()  # noqa: F821
            except Exception:
                now = 0.0
            self._snareStringCounterArmed = True
            self._snareStringCounterUntil = (
                CorruptionGlobals.snareStringCounterUntil(now, window))
            try:
                messenger.send(event, [self, window])  # noqa: F821
            except Exception:
                pass
            return Task.done

        if delay <= 0.0:
            _fire()
            return
        try:
            self._snareStringCounterTask = taskMgr.doMethodLater(  # noqa: F821
                delay, _fire, self.uniqueName('snare-string-counter'))
        except Exception:
            self._snareStringCounterTask = None
            _fire()

    def __clearSnareStringSnapCounter(self):
        taskName = None
        try:
            taskName = self.uniqueName('snare-string-counter')
        except Exception:
            taskName = None
        if taskName:
            try:
                taskMgr.remove(taskName)  # noqa: F821
            except Exception:
                pass
        self._snareStringCounterTask = None
        self._snareStringCounterArmed = False
        self._snareStringCounterUntil = 0.0

    def __scheduleBruteSpitCounter(self):
        """After spit telegraph reads, arm a short punish→melee counter window.

        Thin client cue — MeleeCombat listens and reuses the perfect-dodge
        counter opener path (same as Snare string-snap). Gameplay timing only.
        """
        self.__clearBruteSpitCounter()
        if not getattr(
                CorruptionGlobals, 'BRUTE_SPIT_COUNTER_ENABLED', True):
            return
        delay = float(getattr(
            CorruptionGlobals, 'BRUTE_SPIT_COUNTER_ARM_DELAY_SEC', 0.22))
        window = float(getattr(
            CorruptionGlobals, 'BRUTE_SPIT_COUNTER_WINDOW_SEC', 0.55))
        event = str(getattr(
            CorruptionGlobals, 'BRUTE_SPIT_COUNTER_EVENT',
            'corruptBruteSpitCounter'))

        def _fire(task=None):
            self._bruteSpitCounterTask = None
            try:
                messenger.send(event, [self, window])  # noqa: F821
            except Exception:
                pass
            return Task.done

        if delay <= 0.0:
            _fire()
            return
        try:
            self._bruteSpitCounterTask = taskMgr.doMethodLater(  # noqa: F821
                delay, _fire, self.uniqueName('brute-spit-counter'))
        except Exception:
            self._bruteSpitCounterTask = None
            _fire()

    def __clearBruteSpitCounter(self):
        taskName = None
        try:
            taskName = self.uniqueName('brute-spit-counter')
        except Exception:
            taskName = None
        if taskName:
            try:
                taskMgr.remove(taskName)  # noqa: F821
            except Exception:
                pass
        self._bruteSpitCounterTask = None

    def __scheduleGagsterLobCounter(self):
        """After lob telegraph reads, arm a short punish→melee counter window.

        Thin client cue — MeleeCombat listens and reuses the perfect-dodge
        counter opener path (same as Snare string-snap). Gameplay timing only.
        """
        self.__clearGagsterLobCounter()
        if not getattr(
                CorruptionGlobals, 'GAGSTER_LOB_COUNTER_ENABLED', True):
            return
        delay = float(getattr(
            CorruptionGlobals, 'GAGSTER_LOB_COUNTER_ARM_DELAY_SEC', 0.18))
        window = float(getattr(
            CorruptionGlobals, 'GAGSTER_LOB_COUNTER_WINDOW_SEC', 0.52))
        event = str(getattr(
            CorruptionGlobals, 'GAGSTER_LOB_COUNTER_EVENT',
            'corruptGagsterLobCounter'))

        def _fire(task=None):
            self._gagsterLobCounterTask = None
            try:
                messenger.send(event, [self, window])  # noqa: F821
            except Exception:
                pass
            return Task.done

        if delay <= 0.0:
            _fire()
            return
        try:
            self._gagsterLobCounterTask = taskMgr.doMethodLater(  # noqa: F821
                delay, _fire, self.uniqueName('gagster-lob-counter'))
        except Exception:
            self._gagsterLobCounterTask = None
            _fire()

    def __clearGagsterLobCounter(self):
        taskName = None
        try:
            taskName = self.uniqueName('gagster-lob-counter')
        except Exception:
            taskName = None
        if taskName:
            try:
                taskMgr.remove(taskName)  # noqa: F821
            except Exception:
                pass
        self._gagsterLobCounterTask = None

    def __scheduleOswaldBetrayalLungeCounter(self):
        """After betrayal-lunge telegraph reads, arm a short punish→melee window.

        Thin client cue — MeleeCombat listens and reuses the perfect-dodge
        counter opener path (same as Snare / Brute spit / Gagster lob).
        Gameplay timing only.
        """
        self.__clearOswaldBetrayalLungeCounter()
        if not getattr(
                CorruptionGlobals, 'OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED',
                True):
            return
        delay = float(getattr(
            CorruptionGlobals, 'OSWALD_BETRAYAL_LUNGE_COUNTER_ARM_DELAY_SEC',
            0.12))
        window = float(getattr(
            CorruptionGlobals, 'OSWALD_BETRAYAL_LUNGE_COUNTER_WINDOW_SEC',
            0.48))
        event = str(getattr(
            CorruptionGlobals, 'OSWALD_BETRAYAL_LUNGE_COUNTER_EVENT',
            'corruptOswaldBetrayalLungeCounter'))

        def _fire(task=None):
            self._oswaldBetrayalLungeCounterTask = None
            try:
                messenger.send(event, [self, window])  # noqa: F821
            except Exception:
                pass
            return Task.done

        if delay <= 0.0:
            _fire()
            return
        try:
            self._oswaldBetrayalLungeCounterTask = taskMgr.doMethodLater(  # noqa: F821
                delay, _fire, self.uniqueName('oswald-betrayal-lunge-counter'))
        except Exception:
            self._oswaldBetrayalLungeCounterTask = None
            _fire()

    def __clearOswaldBetrayalLungeCounter(self):
        taskName = None
        try:
            taskName = self.uniqueName('oswald-betrayal-lunge-counter')
        except Exception:
            taskName = None
        if taskName:
            try:
                taskMgr.remove(taskName)  # noqa: F821
            except Exception:
                pass
        self._oswaldBetrayalLungeCounterTask = None

    def __scheduleOswaldStainBurstCounter(self):
        """After stain-burst telegraph reads, arm a short punish→melee window.

        Thin client cue — MeleeCombat listens and reuses the perfect-dodge
        counter opener path. Gameplay timing only.
        """
        self.__clearOswaldStainBurstCounter()
        if not getattr(
                CorruptionGlobals, 'OSWALD_STAIN_BURST_COUNTER_ENABLED', True):
            return
        delay = float(getattr(
            CorruptionGlobals, 'OSWALD_STAIN_BURST_COUNTER_ARM_DELAY_SEC',
            0.10))
        window = float(getattr(
            CorruptionGlobals, 'OSWALD_STAIN_BURST_COUNTER_WINDOW_SEC', 0.44))
        event = str(getattr(
            CorruptionGlobals, 'OSWALD_STAIN_BURST_COUNTER_EVENT',
            'corruptOswaldStainBurstCounter'))

        def _fire(task=None):
            self._oswaldStainBurstCounterTask = None
            try:
                messenger.send(event, [self, window])  # noqa: F821
            except Exception:
                pass
            return Task.done

        if delay <= 0.0:
            _fire()
            return
        try:
            self._oswaldStainBurstCounterTask = taskMgr.doMethodLater(  # noqa: F821
                delay, _fire, self.uniqueName('oswald-stain-burst-counter'))
        except Exception:
            self._oswaldStainBurstCounterTask = None
            _fire()

    def __clearOswaldStainBurstCounter(self):
        taskName = None
        try:
            taskName = self.uniqueName('oswald-stain-burst-counter')
        except Exception:
            taskName = None
        if taskName:
            try:
                taskMgr.remove(taskName)  # noqa: F821
            except Exception:
                pass
        self._oswaldStainBurstCounterTask = None

    def __scheduleOverlordRainCounter(self):
        """After rain telegraph reads, arm a short punish→melee counter window.

        Thin client cue — MeleeCombat listens and reuses the perfect-dodge
        counter opener path (same as Snare / Oswald). Gameplay timing only.
        """
        self.__clearOverlordRainCounter()
        if not getattr(
                CorruptionGlobals, 'OVERLORD_RAIN_COUNTER_ENABLED', True):
            return
        delay = float(getattr(
            CorruptionGlobals, 'OVERLORD_RAIN_COUNTER_ARM_DELAY_SEC', 0.22))
        window = float(getattr(
            CorruptionGlobals, 'OVERLORD_RAIN_COUNTER_WINDOW_SEC', 0.55))
        event = str(getattr(
            CorruptionGlobals, 'OVERLORD_RAIN_COUNTER_EVENT',
            'corruptOverlordRainCounter'))

        def _fire(task=None):
            self._overlordRainCounterTask = None
            try:
                messenger.send(event, [self, window])  # noqa: F821
            except Exception:
                pass
            return Task.done

        if delay <= 0.0:
            _fire()
            return
        try:
            self._overlordRainCounterTask = taskMgr.doMethodLater(  # noqa: F821
                delay, _fire, self.uniqueName('overlord-rain-counter'))
        except Exception:
            self._overlordRainCounterTask = None
            _fire()

    def __clearOverlordRainCounter(self):
        taskName = None
        try:
            taskName = self.uniqueName('overlord-rain-counter')
        except Exception:
            taskName = None
        if taskName:
            try:
                taskMgr.remove(taskName)  # noqa: F821
            except Exception:
                pass
        self._overlordRainCounterTask = None

    def __scheduleOverlordSlamCounter(self):
        """After slam telegraph reads, arm a short punish→melee counter window.

        Thin client cue — MeleeCombat listens and reuses the perfect-dodge
        counter opener path. Gameplay timing only.
        """
        self.__clearOverlordSlamCounter()
        if not getattr(
                CorruptionGlobals, 'OVERLORD_SLAM_COUNTER_ENABLED', True):
            return
        delay = float(getattr(
            CorruptionGlobals, 'OVERLORD_SLAM_COUNTER_ARM_DELAY_SEC', 0.12))
        window = float(getattr(
            CorruptionGlobals, 'OVERLORD_SLAM_COUNTER_WINDOW_SEC', 0.42))
        event = str(getattr(
            CorruptionGlobals, 'OVERLORD_SLAM_COUNTER_EVENT',
            'corruptOverlordSlamCounter'))

        def _fire(task=None):
            self._overlordSlamCounterTask = None
            try:
                messenger.send(event, [self, window])  # noqa: F821
            except Exception:
                pass
            return Task.done

        if delay <= 0.0:
            _fire()
            return
        try:
            self._overlordSlamCounterTask = taskMgr.doMethodLater(  # noqa: F821
                delay, _fire, self.uniqueName('overlord-slam-counter'))
        except Exception:
            self._overlordSlamCounterTask = None
            _fire()

    def __clearOverlordSlamCounter(self):
        taskName = None
        try:
            taskName = self.uniqueName('overlord-slam-counter')
        except Exception:
            taskName = None
        if taskName:
            try:
                taskMgr.remove(taskName)  # noqa: F821
            except Exception:
                pass
        self._overlordSlamCounterTask = None

    def __scheduleOverlordInkSurgeCounter(self):
        """After ink_surge telegraph reads, arm a short punish→melee window.

        Thin client cue — MeleeCombat listens and reuses the perfect-dodge
        counter opener path. Gameplay timing only.
        """
        self.__clearOverlordInkSurgeCounter()
        if not getattr(
                CorruptionGlobals, 'OVERLORD_INK_SURGE_COUNTER_ENABLED', True):
            return
        delay = float(getattr(
            CorruptionGlobals, 'OVERLORD_INK_SURGE_COUNTER_ARM_DELAY_SEC',
            0.14))
        window = float(getattr(
            CorruptionGlobals, 'OVERLORD_INK_SURGE_COUNTER_WINDOW_SEC', 0.48))
        event = str(getattr(
            CorruptionGlobals, 'OVERLORD_INK_SURGE_COUNTER_EVENT',
            'corruptOverlordInkSurgeCounter'))

        def _fire(task=None):
            self._overlordInkSurgeCounterTask = None
            try:
                messenger.send(event, [self, window])  # noqa: F821
            except Exception:
                pass
            return Task.done

        if delay <= 0.0:
            _fire()
            return
        try:
            self._overlordInkSurgeCounterTask = taskMgr.doMethodLater(  # noqa: F821
                delay, _fire, self.uniqueName('overlord-ink-surge-counter'))
        except Exception:
            self._overlordInkSurgeCounterTask = None
            _fire()

    def __clearOverlordInkSurgeCounter(self):
        taskName = None
        try:
            taskName = self.uniqueName('overlord-ink-surge-counter')
        except Exception:
            taskName = None
        if taskName:
            try:
                taskMgr.remove(taskName)  # noqa: F821
            except Exception:
                pass
        self._overlordInkSurgeCounterTask = None

    def __consumeSnareStringCounterCreamSplash(self):
        """If string-snap counter juice is live, play cream splash and spend it.

        Returns True when cream splash armed. Hit-grace covers stretch-punch
        contact that lands just after the rewarded F window expires.
        """
        if not getattr(
                CorruptionGlobals,
                'SNARE_STRING_COUNTER_CREAM_SPLASH_ENABLED', True):
            return False
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            now = 0.0
        armed = bool(getattr(self, '_snareStringCounterArmed', False))
        until = float(getattr(self, '_snareStringCounterUntil', 0.0) or 0.0)
        eligible = CorruptionGlobals.isSnareStringCounterCreamSplashEligible(
            armed, until, now)
        # Spend eligibility either way so only the first rewarded hit juices.
        self._snareStringCounterArmed = False
        self._snareStringCounterUntil = 0.0
        if not eligible:
            return False
        self.__playSnareStringCounterCreamSplash()
        return True

    def __playSnareStringCounterCreamSplash(self, pos=None):
        """Cream splash + delayed aftershock — successful string-snap counter."""
        if self.getArchetype() != CorruptionGlobals.ARCHETYPE_SNARE:
            return
        self.__clearSnareStringCounterCreamSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = SnareStringCounterCreamSplash()
        self._snareStringCounterCreamSplash = splash
        splash.play(pos)

    def __clearSnareStringCounterCreamSplash(self):
        splash = getattr(self, '_snareStringCounterCreamSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._snareStringCounterCreamSplash = None

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

    def __playBruteSpitCreamSplash(self, pos=None):
        """Cream splash + delayed aftershock — Sludge Brute spit land only."""
        if not self.__isBruteSpit():
            return
        if not getattr(
                CorruptionGlobals,
                'BRUTE_SPIT_CREAM_SPLASH_ENABLED', True):
            return
        self.__clearBruteSpitCreamSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = BruteSpitCreamSplash()
        self._bruteSpitCreamSplash = splash
        splash.play(pos)

    def __clearBruteSpitCreamSplash(self):
        splash = getattr(self, '_bruteSpitCreamSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._bruteSpitCreamSplash = None

    def __playGagsterTelegraphPuddle(self):
        """Teal bounce-pie + cream/ink puddle warn — Gunk Gagster wind-ups only."""
        self.__clearGagsterTelegraphPuddle()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        warnPos = None
        la = getattr(base, 'localAvatar', None)  # noqa: F821
        if la is not None:
            try:
                if not la.isEmpty():
                    warnPos = la.getPos(render)
            except Exception:
                warnPos = None
        warn = GagsterPuddleTelegraphWarn()
        self._gagsterTelegraphPuddle = warn
        warn.play(pos, warnPos=warnPos)

    def __clearGagsterTelegraphPuddle(self):
        warn = getattr(self, '_gagsterTelegraphPuddle', None)
        if warn is not None:
            try:
                warn.clear()
            except Exception:
                pass
        self._gagsterTelegraphPuddle = None

    def __playGagsterPuddleCreamSplash(self, pos=None):
        """Cream splash + delayed aftershock — Gunk Gagster puddle land only."""
        if not self.__isGunkGagster():
            return
        if not getattr(
                CorruptionGlobals,
                'GAGSTER_PUDDLE_CREAM_SPLASH_ENABLED', True):
            return
        self.__clearGagsterPuddleCreamSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = GagsterPuddleCreamSplash()
        self._gagsterPuddleCreamSplash = splash
        splash.play(pos)

    def __clearGagsterPuddleCreamSplash(self):
        splash = getattr(self, '_gagsterPuddleCreamSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._gagsterPuddleCreamSplash = None

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

    def __playSmudgeHitCreamSplash(self, pos=None):
        """Cream splash + delayed aftershock — Ink Smudge hit path only."""
        if self.getArchetype() != CorruptionGlobals.ARCHETYPE_INK:
            return
        if self.__isInkOverlord():
            return
        if not getattr(
                CorruptionGlobals,
                'SMUDGE_HIT_CREAM_SPLASH_ENABLED', True):
            return
        self.__clearSmudgeHitCreamSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = SmudgeHitCreamSplash()
        self._smudgeHitCreamSplash = splash
        splash.play(pos)

    def __clearSmudgeHitCreamSplash(self):
        splash = getattr(self, '_smudgeHitCreamSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._smudgeHitCreamSplash = None

    def __playSmudgeHitCreamWash(self):
        """Soft cream wash after Smudge purple hit splash (hit path only)."""
        if self.getArchetype() != CorruptionGlobals.ARCHETYPE_INK:
            return
        if self.__isInkOverlord():
            return
        self.__clearSmudgeHitCreamWash()
        wash = SmudgeHitCreamWashPulse()
        self._smudgeHitCreamWash = wash
        wash.play()

    def __clearSmudgeHitCreamWash(self):
        wash = getattr(self, '_smudgeHitCreamWash', None)
        if wash is not None:
            try:
                wash.clear()
            except Exception:
                pass
        self._smudgeHitCreamWash = None

    def __playOswaldTelegraphStain(self):
        """Crimson stain-lunge telegraph — Corrupted Oswald wind-ups only."""
        self.__clearOswaldTelegraphStain()
        try:
            pos = self.getPos(render)
        except Exception:
            return
        stain = OswaldBetrayalTelegraphStain()
        self._oswaldTelegraphStain = stain
        stain.play(pos)

    def __clearOswaldTelegraphStain(self):
        stain = getattr(self, '_oswaldTelegraphStain', None)
        if stain is not None:
            try:
                stain.clear()
            except Exception:
                pass
        self._oswaldTelegraphStain = None

    def __playOswaldBetrayalSplash(self, pos=None, kind='hit'):
        """Crimson betrayal splash — Corrupted Oswald hit / death only."""
        if self.getArchetype() != CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD:
            return
        self.__clearOswaldBetrayalSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = OswaldBetrayalSplash()
        self._oswaldBetrayalSplash = splash
        splash.play(pos, kind=kind)

    def __clearOswaldBetrayalSplash(self):
        splash = getattr(self, '_oswaldBetrayalSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._oswaldBetrayalSplash = None

    def __playBruteSludgeSplash(self, pos=None, kind='hit'):
        """Green sludge splash — Sludge Brute hit / death readability only."""
        if self.getArchetype() != CorruptionGlobals.ARCHETYPE_BRUTE:
            return
        self.__clearBruteSludgeSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = BruteSludgeSplash()
        self._bruteSludgeSplash = splash
        splash.play(pos, kind=kind)

    def __clearBruteSludgeSplash(self):
        splash = getattr(self, '_bruteSludgeSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._bruteSludgeSplash = None

    def __playSnareStringSnapSplash(self, pos=None, kind='hit'):
        """Amber string-snap splash — Balloon Snare hit / death readability only."""
        if self.getArchetype() != CorruptionGlobals.ARCHETYPE_SNARE:
            return
        self.__clearSnareStringSnapSplash()
        if pos is None:
            try:
                pos = self.getPos(render)
            except Exception:
                return
        splash = SnareStringSnapSplash()
        self._snareStringSnapSplash = splash
        splash.play(pos, kind=kind)

    def __clearSnareStringSnapSplash(self):
        splash = getattr(self, '_snareStringSnapSplash', None)
        if splash is not None:
            try:
                splash.clear()
            except Exception:
                pass
        self._snareStringSnapSplash = None

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
        """Bridge SoftTarget/MeleeCombat → AI requestHackSlashHit RPC.

        hitIndex travels with damage so AI can arm juggle-hang stun on launch
        beats (mid/finisher) — hang juice alone is client-only.
        """
        if not self.isHackSlashAlive():
            return False
        amount = max(0, int(damage))
        if amount <= 0:
            return False
        idx = max(0, min(255, int(hitIndex)))
        self.sendUpdate('requestHackSlashHit', [amount, idx])
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
        # Ink Overlord: magenta/crimson splash so boss hits read vs street Smudge.
        if self.__isInkOverlord():
            self.__pauseIdleInkDrip()
            self.__pauseIdleCreamDrip()
            self.__pauseIdleCreamDripSparkle()
            self.__pauseIdleCreamWash()
            self.__pauseSilhouetteCreamRim()
            self.__pauseSilhouetteCreamSparkle()
            self.__pauseSilhouetteCreamWash()
            self.__playOverlordMagentaInkSplash(kind='hit')
            self.__playOverlordHitCreamWash()
            Sequence(
                Wait(0.32),
                Func(self.__resumeIdleInkDrip),
                Func(self.__resumeIdleCreamDrip),
                Func(self.__resumeIdleCreamDripSparkle),
                Func(self.__resumeIdleCreamWash),
                Func(self.__resumeSilhouetteCreamRim),
                Func(self.__resumeSilhouetteCreamSparkle),
                Func(self.__resumeSilhouetteCreamWash),
            ).start()
        # Ink Smudge: cheap purple splash so tagged Smudges read in a swarm.
        elif self.getArchetype() == CorruptionGlobals.ARCHETYPE_INK:
            self.__pauseIdleInkDrip()
            self.__pauseIdleCreamDrip()
            self.__pauseIdleCreamDripSparkle()
            self.__pauseIdleCreamWash()
            self.__pauseSilhouetteCreamRim()
            self.__pauseSilhouetteCreamSparkle()
            self.__pauseSilhouetteCreamWash()
            self.__playSmudgeInkSplash(kind='hit')
            self.__playSmudgeHitCreamSplash()
            self.__playSmudgeHitCreamWash()
            # Brief resume so idle drips / sparkles / wash / rim flecks return after splash.
            Sequence(
                Wait(0.28),
                Func(self.__resumeIdleInkDrip),
                Func(self.__resumeIdleCreamDrip),
                Func(self.__resumeIdleCreamDripSparkle),
                Func(self.__resumeIdleCreamWash),
                Func(self.__resumeSilhouetteCreamRim),
                Func(self.__resumeSilhouetteCreamSparkle),
                Func(self.__resumeSilhouetteCreamWash),
            ).start()
        # Sludge Brute: cheap green splash so tagged Brutes read vs Smudges.
        elif self.getArchetype() == CorruptionGlobals.ARCHETYPE_BRUTE:
            self.__pauseIdleInkDrip()
            self.__pauseIdleCreamDrip()
            self.__pauseIdleCreamDripSparkle()
            self.__pauseIdleCreamWash()
            self.__pauseSilhouetteCreamRim()
            self.__pauseSilhouetteCreamSparkle()
            self.__pauseSilhouetteCreamWash()
            self.__playBruteSludgeSplash(kind='hit')
            Sequence(
                Wait(0.3),
                Func(self.__resumeIdleInkDrip),
                Func(self.__resumeIdleCreamDrip),
                Func(self.__resumeIdleCreamDripSparkle),
                Func(self.__resumeIdleCreamWash),
                Func(self.__resumeSilhouetteCreamRim),
                Func(self.__resumeSilhouetteCreamSparkle),
                Func(self.__resumeSilhouetteCreamWash),
            ).start()
        # Balloon Snare: cheap amber splash so tagged Snares read vs pack.
        # Successful string-snap counter punish also fires cream splash /
        # aftershock so the rewarded window feels juicy (#203 juice).
        elif self.getArchetype() == CorruptionGlobals.ARCHETYPE_SNARE:
            self.__pauseIdleInkDrip()
            self.__pauseIdleCreamDrip()
            self.__pauseIdleCreamDripSparkle()
            self.__pauseIdleCreamWash()
            self.__pauseSilhouetteCreamRim()
            self.__pauseSilhouetteCreamSparkle()
            self.__pauseSilhouetteCreamWash()
            self.__playSnareStringSnapSplash(kind='hit')
            self.__consumeSnareStringCounterCreamSplash()
            Sequence(
                Wait(0.26),
                Func(self.__resumeIdleInkDrip),
                Func(self.__resumeIdleCreamDrip),
                Func(self.__resumeIdleCreamDripSparkle),
                Func(self.__resumeIdleCreamWash),
                Func(self.__resumeSilhouetteCreamRim),
                Func(self.__resumeSilhouetteCreamSparkle),
                Func(self.__resumeSilhouetteCreamWash),
            ).start()
        # Corrupted Oswald: crimson betrayal splash — twist fight, not Smudge.
        elif self.getArchetype() == CorruptionGlobals.ARCHETYPE_CORRUPT_OSWALD:
            self.__pauseIdleInkDrip()
            self.__pauseIdleCreamDrip()
            self.__pauseIdleCreamDripSparkle()
            self.__pauseIdleCreamWash()
            self.__pauseSilhouetteCreamRim()
            self.__pauseSilhouetteCreamSparkle()
            self.__pauseSilhouetteCreamWash()
            self.__playOswaldBetrayalSplash(kind='hit')
            Sequence(
                Wait(0.28),
                Func(self.__resumeIdleInkDrip),
                Func(self.__resumeIdleCreamDrip),
                Func(self.__resumeIdleCreamDripSparkle),
                Func(self.__resumeIdleCreamWash),
                Func(self.__resumeSilhouetteCreamRim),
                Func(self.__resumeSilhouetteCreamSparkle),
                Func(self.__resumeSilhouetteCreamWash),
            ).start()
        try:
            away = self.getPos(render) - attacker.getPos(render)
            away.setZ(0)
            if away.length() > 0.01:
                away.normalize()
                self.setPos(self.getPos() + away * (0.7 + 0.25 * hitIndex))
        except Exception:
            pass
