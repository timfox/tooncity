from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import Func, LerpFunctionInterval, Sequence
from panda3d.core import CardMaker, Fog, TransparencyAttrib, Vec4

from toontown.corruption import CorruptionGlobals
from toontown.corruption import PollutionFogCreamDissolveFx
from toontown.corruption import PollutionHoodTintCreamFadeFx
from toontown.corruption import PollutionPropTint
from toontown.corruption import PollutionStreetAudio


class PollutionManager(DistributedObject.DistributedObject):
    """Client mirror of per-zone pollution; fog + haze + color grade + prop tint + audio.

    Fog density, ink haze overlay, hood color grade, and prop tint all follow a
    presented pollution level that lerps toward the zone's true corruption so
    reclaim packs visibly thicken/clear the street atmosphere. On purity
    complete, fog cream-dissolves (sunny pastel tint + flecks) via
    PollutionFogCreamDissolveFx and hood prop tint cream-fades via
    PollutionHoodTintCreamFadeFx while the density clear ramp still runs.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('PollutionManager')
    neverDisable = 1

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.zonePollution = {}
        self._fog = None
        self._hazeNP = None
        self._activeZoneId = None
        self._lastLevel = CorruptionGlobals.POLLUTION_PURE
        self._presentedLevel = CorruptionGlobals.POLLUTION_PURE
        self._targetLevel = CorruptionGlobals.POLLUTION_PURE
        self._rampIval = None
        self._propTint = None
        self._streetAudio = None
        self._creamDissolve = None
        self._creamDissolveBlend = 0.0
        self._hoodTintCreamFade = None

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.accept('localToonLeftZone', self.__handleLeftZone)
        self.accept('localAvatarZoneChange', self.__handleZoneChange)
        base.cr.pollutionManager = self
        # Hood-specific street geom tint (listens to pollutionPropTint).
        self._propTint = PollutionPropTint.PollutionPropTint()
        self._propTint.start()
        # Polluted vs pure street music beds (listens to pollutionChanged / purity).
        self._streetAudio = PollutionStreetAudio.PollutionStreetAudio()
        self._streetAudio.start()
        # Purity-complete cream dissolve of fog / haze (listens to purityRestoreFx).
        self._creamDissolve = (
            PollutionFogCreamDissolveFx.PollutionFogCreamDissolveFx(self))
        self._creamDissolve.start()
        # Purity-complete cream fade of hood prop tint (listens to purityRestoreFx).
        self._hoodTintCreamFade = (
            PollutionHoodTintCreamFadeFx.PollutionHoodTintCreamFadeFx(
                self._propTint))
        self._hoodTintCreamFade.start()

    def disable(self):
        self.ignoreAll()
        self.__finishRamp()
        self.__clearPresentation()
        if self._hoodTintCreamFade is not None:
            self._hoodTintCreamFade.stop()
            self._hoodTintCreamFade = None
        if self._creamDissolve is not None:
            self._creamDissolve.stop()
            self._creamDissolve = None
        self._creamDissolveBlend = 0.0
        if self._streetAudio is not None:
            self._streetAudio.stop()
            self._streetAudio = None
        if self._propTint is not None:
            self._propTint.stop()
            self._propTint = None
        if getattr(base.cr, 'pollutionManager', None) is self:
            del base.cr.pollutionManager
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        self.__finishRamp()
        self.__clearPresentation()
        if self._hoodTintCreamFade is not None:
            self._hoodTintCreamFade.stop()
            self._hoodTintCreamFade = None
        if self._creamDissolve is not None:
            self._creamDissolve.stop()
            self._creamDissolve = None
        self._creamDissolveBlend = 0.0
        if self._streetAudio is not None:
            self._streetAudio.stop()
            self._streetAudio = None
        if self._propTint is not None:
            self._propTint.stop()
            self._propTint = None
        DistributedObject.DistributedObject.delete(self)

    def beginCreamDissolve(self):
        """Arm cream fog tint for the in-flight purity clear ramp."""
        if not getattr(CorruptionGlobals, 'FOG_CREAM_DISSOLVE_ENABLED', True):
            return
        self._creamDissolveBlend = 0.0
        # Refresh presentation so an in-flight clear picks up cream tint.
        zoneId = self._activeZoneId
        if zoneId is not None and self._presentedLevel > CorruptionGlobals.POLLUTION_PURE:
            self.__setPresentedLevel(zoneId, self._presentedLevel)

    def setCreamDissolveBlend(self, blend):
        """0..1 cream mix into fog/haze color (driven by dissolve FX)."""
        self._creamDissolveBlend = max(0.0, min(1.0, float(blend)))
        zoneId = self._activeZoneId
        if zoneId is None:
            return
        if self._presentedLevel <= CorruptionGlobals.POLLUTION_PURE:
            return
        self.__setPresentedLevel(zoneId, self._presentedLevel)

    def finishCreamDissolve(self):
        """Drop cream tint after dissolve overlay finishes."""
        if self._creamDissolveBlend == 0.0:
            return
        self._creamDissolveBlend = 0.0
        zoneId = self._activeZoneId
        if zoneId is not None and self._presentedLevel > CorruptionGlobals.POLLUTION_PURE:
            self.__setPresentedLevel(zoneId, self._presentedLevel)

    def getPollution(self, zoneId=None):
        if zoneId is None:
            if hasattr(base, 'localAvatar'):
                zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return CorruptionGlobals.POLLUTION_DEFAULT
        return self.zonePollution.get(zoneId, CorruptionGlobals.POLLUTION_DEFAULT)

    def setZonePollution(self, zoneId, netLevel):
        level = CorruptionGlobals.pollutionFromNet(netLevel)
        self.zonePollution[zoneId] = level
        messenger.send('pollutionChanged', [zoneId, level])
        if hasattr(base, 'localAvatar') and getattr(base.localAvatar, 'zoneId', None) == zoneId:
            self.__applyLocalPresentation(zoneId, level)

    def d_requestZonePollution(self, zoneId):
        self.sendUpdate('requestZonePollution', [zoneId])

    def d_requestStreetEvent(self, eventType):
        """0=start reclaim in this street, 1=start/resume campaign act."""
        self.sendUpdate('requestStreetEvent', [int(eventType)])

    def d_requestHackSlashIFrame(self, durationMs):
        """Tell AI the local toon is invulnerable for durationMs (capped server-side)."""
        self.sendUpdate('requestHackSlashIFrame', [max(0, int(durationMs))])

    def __handleZoneChange(self, zoneId=None):
        if zoneId is None and hasattr(base, 'localAvatar'):
            zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return
        self._activeZoneId = zoneId
        if zoneId not in self.zonePollution:
            self.d_requestZonePollution(zoneId)
        # Snap on street enter so the incoming hood look lands immediately.
        self.__applyLocalPresentation(zoneId, self.getPollution(zoneId), snap=True)

    def __handleLeftZone(self, *args):
        self.__finishRamp()
        self.__clearPresentation()

    def __finishRamp(self, complete=False):
        """Stop an in-flight density ramp.

        complete=False keeps the current presented level (retarget mid-ramp).
        complete=True runs the interval to its end state.
        """
        if self._rampIval is None:
            return
        ival = self._rampIval
        self._rampIval = None
        try:
            if complete:
                ival.finish()
            else:
                ival.pause()
        except Exception:
            pass

    def __applyLocalPresentation(self, zoneId, level, snap=False):
        """Hood-biased fog + ink haze + color grade with density ramp."""
        level = CorruptionGlobals.clampPollution(level)
        self._activeZoneId = zoneId
        self._lastLevel = level
        self._targetLevel = level

        delta = abs(level - self._presentedLevel)
        if snap or delta <= CorruptionGlobals.POLLUTION_FOG_SNAP_DELTA:
            self.__finishRamp(complete=False)
            self.__setPresentedLevel(zoneId, level)
            return

        # Pause (don't finish) so retargets continue from current density.
        self.__finishRamp(complete=False)
        start = self._presentedLevel
        duration = CorruptionGlobals.pollutionFogRampDuration(start, level)
        if duration <= 0.0:
            self.__setPresentedLevel(zoneId, level)
            return

        def setPresented(t, z=zoneId, a=start, b=level):
            presented = a + (b - a) * float(t)
            self.__setPresentedLevel(z, presented)

        self._rampIval = Sequence(
            LerpFunctionInterval(
                setPresented, fromData=0.0, toData=1.0, duration=duration),
            Func(self.__setPresentedLevel, zoneId, level),
        )
        self._rampIval.start()

    def __setPresentedLevel(self, zoneId, level):
        """Apply fog / haze / grade / prop tint for the presented density."""
        level = CorruptionGlobals.clampPollution(level)
        self._presentedLevel = level

        if level <= CorruptionGlobals.POLLUTION_PURE:
            self.__clearFogAndHaze()
            messenger.send('pollutionPropTint', [zoneId, 0.0])
            messenger.send('pollutionColorGrade', [zoneId, 0.0])
            if not self.__restoreBloomActive():
                render.clearColorScale()
            return

        if self._fog is None:
            self._fog = Fog('CorruptionFog')
            render.setFog(self._fog)

        creamBlend = self._creamDissolveBlend
        if creamBlend > 0.001:
            fogR, fogG, fogB = CorruptionGlobals.hoodFogCreamDissolveColor(
                zoneId, level, creamBlend)
        else:
            fogR, fogG, fogB = CorruptionGlobals.hoodFogColor(zoneId, level)
        self._fog.setColor(fogR, fogG, fogB)
        self._fog.setExpDensity(CorruptionGlobals.hoodFogExpDensity(zoneId, level))

        # Scene color grade beyond fog: hood-biased desaturation.
        # Skip while reclaim purity bloom owns render colorScale.
        if not self.__restoreBloomActive():
            tintR, tintG, tintB = CorruptionGlobals.hoodColorGrade(zoneId, level)
            # Soft cream lift into the grade while fog dissolves.
            if creamBlend > 0.001:
                cr, cg, cb = CorruptionGlobals.FOG_CREAM_DISSOLVE_COLOR
                lift = 0.35 * creamBlend
                tintR = tintR + (float(cr) - tintR) * lift
                tintG = tintG + (float(cg) - tintG) * lift
                tintB = tintB + (float(cb) - tintB) * lift
            render.setColorScale(Vec4(tintR, tintG, tintB, 1.0))

        self.__applyHaze(zoneId, level, fogR, fogG, fogB)

        # Hooks for street props / future art to tint without hard coupling.
        messenger.send('pollutionPropTint', [zoneId, level])
        messenger.send('pollutionColorGrade', [zoneId, level])

    def __applyHaze(self, zoneId, level, fogR, fogG, fogB):
        """Fullscreen ink wash that thickens with presented pollution."""
        alpha = CorruptionGlobals.hoodHazeAlpha(zoneId, level)
        if alpha <= 0.001:
            self.__clearHaze()
            return
        self.__ensureHaze()
        if self._hazeNP is None:
            return
        try:
            self._hazeNP.setColorScale(fogR, fogG, fogB, alpha)
            self._hazeNP.show()
        except Exception:
            self.__clearHaze()

    def __ensureHaze(self):
        if self._hazeNP is not None and not self._hazeNP.isEmpty():
            return
        self._hazeNP = None
        try:
            cm = CardMaker('pollution-ink-haze')
            cm.setFrame(-2, 2, -2, 2)
            haze = aspect2d.attachNewNode(cm.generate())  # noqa: F821
            haze.setTransparency(TransparencyAttrib.MAlpha)
            haze.setBin('fixed', CorruptionGlobals.POLLUTION_HAZE_BIN)
            haze.setDepthTest(False)
            haze.setDepthWrite(False)
            haze.setColorScale(0, 0, 0, 0)
            self._hazeNP = haze
        except Exception:
            self.notify.debug('ink haze overlay unavailable')
            self._hazeNP = None

    def __clearHaze(self):
        haze = self._hazeNP
        self._hazeNP = None
        if haze is None:
            return
        try:
            if not haze.isEmpty():
                haze.removeNode()
        except Exception:
            pass

    def __clearFogAndHaze(self):
        if self._fog is not None:
            render.clearFog()
            self._fog = None
        self.__clearHaze()

    def __restoreBloomActive(self):
        reclaim = getattr(base.cr, 'reclaimDirector', None)
        return (
            reclaim is not None
            and getattr(reclaim, '_restoreIval', None) is not None)

    def __clearPresentation(self):
        self.__finishRamp()
        self._creamDissolveBlend = 0.0
        self.__clearFogAndHaze()
        # Avoid stomping an in-flight purity restore bloom on render.
        if not self.__restoreBloomActive():
            render.clearColorScale()
        self._presentedLevel = CorruptionGlobals.POLLUTION_PURE
        self._targetLevel = CorruptionGlobals.POLLUTION_PURE
        self._lastLevel = CorruptionGlobals.POLLUTION_PURE
        if self._activeZoneId is not None:
            messenger.send('pollutionPropTint', [self._activeZoneId, 0.0])
            messenger.send('pollutionColorGrade', [self._activeZoneId, 0.0])
