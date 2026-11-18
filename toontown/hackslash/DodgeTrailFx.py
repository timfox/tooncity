"""Rubber-hose dodge-roll afterimage / smear trail.

Client juice for the Shift/X i-frame roll: brief translucent smear ghosts
(and tiny spark pops) drip behind the toon while rolling. While dodge
i-frames are active, short cream/ink pulses pop along the trail path.
Cream/pastel sparkle flecks also drip along the smear path (no ink), then
a delayed cream aftershock (softer flecks + soft halo) settles — same
residual grammar as finisher / combo cream aftershock. Wired from
MeleeCombat dodge start/end so hit-squash / hitstop paths stay untouched.

Toontown spiritual-sequel tone only — no keyblades / no KH branding.
"""

from math import cos, pi, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.task import Task

from . import HackSlashConfig


class DodgeTrailFx(object):
    """Owns the drip task + ghost nodes for one avatar's dodge roll."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._taskName = avatar.uniqueName('hackslashDodgeTrail')
        self._ghosts = []
        self._pulses = []
        self._creamSparkles = []
        self._nextSpawnAt = 0.0
        self._nextPulseAt = 0.0
        self._nextCreamSparkleAt = 0.0
        self._iframeUntil = 0.0
        self._active = False
        self._spawnIndex = 0
        self._pulseIndex = 0
        self._creamSparkleIndex = 0

    def start(self, iframeSec=None):
        """Begin dripping afterimages; cream/ink pulse while i-frames live."""
        self.stop(clearGhosts=False)
        self._active = True
        self._spawnIndex = 0
        self._pulseIndex = 0
        self._creamSparkleIndex = 0
        self._nextSpawnAt = 0.0
        self._nextPulseAt = 0.0
        self._nextCreamSparkleAt = 0.0
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            now = 0.0
        if iframeSec is None:
            iframeSec = HackSlashConfig.DODGE_IFRAME_SEC
        self._iframeUntil = now + float(iframeSec)
        self._spawnGhost(initial=True)
        self._spawnPulse()
        self._spawnCreamSparkles()
        try:
            taskMgr.add(self._tick, self._taskName)  # noqa: F821
        except Exception:
            self._active = False
            self._iframeUntil = 0.0

    def stop(self, clearGhosts=False):
        """Stop smear spawning; i-frame pulse may keep ticking until clear."""
        self._active = False
        if clearGhosts:
            self.clear()
            return
        # Keep the task alive while i-frame pulses can still fire.
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            now = 0.0
        if now >= self._iframeUntil:
            try:
                taskMgr.remove(self._taskName)  # noqa: F821
            except Exception:
                pass

    def clear(self):
        """Hard-stop and remove every ghost/spark/pulse/cream fleck/aftershock."""
        self._active = False
        self._iframeUntil = 0.0
        try:
            taskMgr.remove(self._taskName)  # noqa: F821
        except Exception:
            pass
        for entry in list(self._ghosts):
            self._destroyEntry(entry)
        self._ghosts = []
        for entry in list(self._pulses):
            self._destroyPulse(entry)
        self._pulses = []
        for entry in list(self._creamSparkles):
            self._destroyCreamSparkle(entry)
        self._creamSparkles = []

    def _tick(self, task):
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            return Task.done

        iframeLive = now < self._iframeUntil
        if not self._active and not iframeLive:
            return Task.done

        if self._active and now >= self._nextSpawnAt:
            self._spawnGhost()
            self._nextSpawnAt = now + float(HackSlashConfig.DODGE_TRAIL_SPAWN_SEC)

        if iframeLive and now >= self._nextPulseAt:
            self._spawnPulse()
            self._nextPulseAt = now + float(
                HackSlashConfig.DODGE_TRAIL_PULSE_SPAWN_SEC)

        # Cream sparkle flecks drip while the smear trail is active.
        if (self._active
                and getattr(
                    HackSlashConfig, 'DODGE_TRAIL_CREAM_SPARKLE_ENABLED', True)
                and now >= self._nextCreamSparkleAt):
            self._spawnCreamSparkles()
            self._nextCreamSparkleAt = now + float(
                HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_SPAWN_SEC)

        if not self._active and not iframeLive:
            return Task.done
        return Task.cont

    def _spawnGhost(self, initial=False):
        maxGhosts = int(HackSlashConfig.DODGE_TRAIL_MAX_GHOSTS)
        # Drop the oldest finished-or-live entry if we are capped.
        while len(self._ghosts) >= maxGhosts:
            oldest = self._ghosts.pop(0)
            self._destroyEntry(oldest)

        try:
            pos = self.avatar.getPos(render)  # noqa: F821
            heading = self.avatar.getH(render)  # noqa: F821
        except Exception:
            return

        lift = float(HackSlashConfig.DODGE_TRAIL_LIFT)
        ghostPos = Point3(pos[0], pos[1], pos[2] + lift)

        r, g, b, a = HackSlashConfig.DODGE_TRAIL_COLOR
        er, eg, eb, ea = HackSlashConfig.DODGE_TRAIL_END_COLOR
        fadeSec = float(HackSlashConfig.DODGE_TRAIL_FADE_SEC)
        halfW = float(HackSlashConfig.DODGE_TRAIL_HALF_W)
        halfH = float(HackSlashConfig.DODGE_TRAIL_HALF_H)
        sx, sy, sz = HackSlashConfig.DODGE_TRAIL_STRETCH

        # Slight stagger so stacked afterimages read as a smear, not a stack.
        stagger = 0.04 * (self._spawnIndex % 3)
        self._spawnIndex += 1

        try:
            cm = CardMaker('hackslash-dodge-smear-%s' % self._spawnIndex)
            cm.setFrame(-halfW, halfW, -halfH, halfH)
            np = render.attachNewNode(cm.generate())  # noqa: F821
            np.setTransparency(TransparencyAttrib.MAlpha)
            np.setColor(r, g, b, 1)
            np.setColorScale(r, g, b, a if not initial else a * 0.85)
            np.setPos(ghostPos)
            np.setH(heading)
            # Stretch along the roll (local Y) + tall cartoon silhouette.
            np.setScale(sx, sy + stagger, sz)
            np.setBin('transparent', 20)
            np.setDepthWrite(False)
            # Face-ish billboard so the smear stays readable from the cam.
            np.setBillboardPointEye()
        except Exception:
            return

        ival = Sequence(
            Parallel(
                LerpScaleInterval(
                    np, fadeSec, Point3(sx * 0.55, sy * 1.25, sz * 0.7),
                    blendType='easeOut'),
                LerpColorScaleInterval(
                    np, fadeSec, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
            Func(self._retireNode, np),
            name=self.avatar.uniqueName(
                'hackslashDodgeSmear-%s' % self._spawnIndex),
        )
        entry = {'np': np, 'ival': ival, 'sparks': []}
        self._ghosts.append(entry)
        ival.start()
        self._spawnSparks(entry, ghostPos, heading)

    def _spawnSparks(self, entry, ghostPos, heading):
        count = int(HackSlashConfig.DODGE_TRAIL_SPARK_COUNT)
        if count <= 0:
            return
        size = float(HackSlashConfig.DODGE_TRAIL_SPARK_SIZE)
        drift = float(HackSlashConfig.DODGE_TRAIL_SPARK_DRIFT)
        fadeSec = float(HackSlashConfig.DODGE_TRAIL_FADE_SEC) * 0.85
        r, g, b, _a = HackSlashConfig.DODGE_TRAIL_SPARK_COLOR

        # Heading is degrees; convert for a tiny backward/outward drift.
        rad = heading * 0.017453292519943295
        backX = -sin(rad)
        backY = -cos(rad)

        for i in range(count):
            try:
                cm = CardMaker('hackslash-dodge-spark-%s-%s' % (
                    self._spawnIndex, i))
                cm.setFrame(-size, size, -size, size)
                spark = render.attachNewNode(cm.generate())  # noqa: F821
                spark.setTransparency(TransparencyAttrib.MAlpha)
                spark.setColor(r, g, b, 1)
                spark.setColorScale(r, g, b, 0.9)
                side = -1.0 if (i % 2) else 1.0
                spark.setPos(
                    ghostPos[0] + backX * 0.15 + side * 0.2 * (i + 1),
                    ghostPos[1] + backY * 0.15,
                    ghostPos[2] - 0.35 + 0.2 * i)
                spark.setScale(0.55)
                spark.setBin('transparent', 21)
                spark.setDepthWrite(False)
                spark.setBillboardPointEye()
            except Exception:
                continue

            endPos = Point3(
                spark.getX() + backX * drift + side * 0.25,
                spark.getY() + backY * drift,
                spark.getZ() - 0.35)
            sIval = Sequence(
                Parallel(
                    LerpPosInterval(spark, fadeSec, endPos, blendType='easeOut'),
                    LerpScaleInterval(spark, fadeSec, 0.05, blendType='easeIn'),
                    LerpColorScaleInterval(
                        spark, fadeSec, Vec4(r, g, b, 0), blendType='easeIn'),
                ),
                Func(self._retireNode, spark),
            )
            entry['sparks'].append({'np': spark, 'ival': sIval})
            sIval.start()

    def _spawnPulse(self):
        """Short cream/ink fleck pulse at the toon while dodge i-frames live."""
        try:
            pos = self.avatar.getPos(render)  # noqa: F821
        except Exception:
            return

        lift = float(HackSlashConfig.DODGE_TRAIL_LIFT)
        origin = Point3(
            pos[0], pos[1],
            pos[2] + lift + float(HackSlashConfig.DODGE_TRAIL_PULSE_LIFT))
        sec = float(HackSlashConfig.DODGE_TRAIL_PULSE_SEC)
        size = float(HackSlashConfig.DODGE_TRAIL_PULSE_SIZE)
        drift = float(HackSlashConfig.DODGE_TRAIL_PULSE_DRIFT)
        parts = []
        nodes = []
        self._pulseIndex += 1

        creamCount = int(HackSlashConfig.DODGE_TRAIL_PULSE_CREAM_COUNT)
        inkCount = int(HackSlashConfig.DODGE_TRAIL_PULSE_INK_COUNT)
        cr, cg, cb, ca = HackSlashConfig.DODGE_TRAIL_PULSE_CREAM_COLOR
        cer, ceg, ceb, cea = HackSlashConfig.DODGE_TRAIL_PULSE_CREAM_END
        ir, ig, ib, ia = HackSlashConfig.DODGE_TRAIL_PULSE_INK_COLOR
        ier, ieg, ieb, iea = HackSlashConfig.DODGE_TRAIL_PULSE_INK_END

        for i in range(creamCount):
            part, np = self._makePulseFleck(
                origin, i, creamCount, size, drift, sec,
                (cr, cg, cb, ca), (cer, ceg, ceb, cea), ink=False)
            if part is not None:
                parts.append(part)
                nodes.append(np)

        for i in range(inkCount):
            part, np = self._makePulseFleck(
                origin, i, max(1, inkCount), size * 0.85, drift * 1.1, sec,
                (ir, ig, ib, ia), (ier, ieg, ieb, iea), ink=True)
            if part is not None:
                parts.append(part)
                nodes.append(np)

        if not parts:
            return

        ival = Sequence(
            Parallel(*parts),
            Func(self._retirePulseNodes, nodes),
            name=self.avatar.uniqueName(
                'hackslashDodgeTrailPulse-%s' % self._pulseIndex),
        )
        self._pulses.append({'ival': ival, 'nodes': nodes})
        ival.start()

    def _makePulseFleck(self, origin, index, count, size, drift, sec,
                        color, endColor, ink=False):
        count = max(1, int(count))
        angle = (2.0 * pi * index) / float(count) + (0.55 if ink else 0.18)
        r, g, b, a = color
        er, eg, eb, ea = endColor
        try:
            cm = CardMaker('hackslash-dodge-pulse-%s-%s-%s' % (
                self._pulseIndex, 'ink' if ink else 'cream', index))
            cm.setFrame(-size, size, -size * (0.4 if not ink else 1.0),
                        size * (0.4 if not ink else 1.0))
            fleck = render.attachNewNode(cm.generate())  # noqa: F821
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, a)
            fleck.setPos(
                origin[0] + cos(angle) * 0.12,
                origin[1] + sin(angle) * 0.12,
                origin[2] + (0.08 if not ink else -0.05) * (index % 2))
            fleck.setScale(0.4 + 0.12 * (index % 3))
            fleck.setBin('transparent', 22)
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return None, None

        end = Point3(
            origin[0] + cos(angle) * drift,
            origin[1] + sin(angle) * drift,
            origin[2] + (0.25 if not ink else -0.35) - 0.08 * (index % 3))
        peak = 1.35 + 0.15 * (index % 2)
        # Rubber-hose: pop tall, then settle/fade.
        part = Sequence(
            Parallel(
                LerpScaleInterval(
                    fleck, sec * 0.35, peak, blendType='easeOut'),
                LerpPosInterval(
                    fleck, sec * 0.55, end, blendType='easeOut'),
                LerpColorScaleInterval(
                    fleck, sec * 0.55, Vec4(r, g, b, a), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(fleck, sec * 0.45, 0.05, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, sec * 0.45, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )
        return part, fleck

    def _spawnCreamSparkles(self):
        """Cream/pastel sparkle flecks + delayed cream aftershock on trail."""
        if not getattr(
                HackSlashConfig, 'DODGE_TRAIL_CREAM_SPARKLE_ENABLED', True):
            return
        try:
            pos = self.avatar.getPos(render)  # noqa: F821
            heading = self.avatar.getH(render)  # noqa: F821
        except Exception:
            return

        lift = float(HackSlashConfig.DODGE_TRAIL_LIFT)
        origin = Point3(
            pos[0], pos[1],
            pos[2] + lift + float(
                HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_LIFT))
        sec = float(HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_SEC)
        drift = float(HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_DRIFT)
        parts = []
        nodes = []
        aftershockNodes = []
        self._creamSparkleIndex += 1

        creamCount = int(HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_COUNT)
        streakCount = int(
            HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_STREAK_COUNT)
        size = float(HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_SIZE)
        streakSize = float(
            HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_STREAK_SIZE)
        cr, cg, cb, ca = HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_COLOR
        cer, ceg, ceb, cea = HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_END
        sr, sg, sb, sa = HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_STREAK_COLOR
        ser, seg, seb, sea = HackSlashConfig.DODGE_TRAIL_CREAM_SPARKLE_STREAK_END

        # Bias flecks slightly behind the roll so they read as trail glitter.
        rad = heading * 0.017453292519943295
        backX = -sin(rad)
        backY = -cos(rad)
        trailOrigin = Point3(
            origin[0] + backX * 0.22,
            origin[1] + backY * 0.22,
            origin[2])

        for i in range(creamCount):
            part, np = self._makeCreamSparkleFleck(
                trailOrigin, i, creamCount, size, drift, sec,
                (cr, cg, cb, ca), (cer, ceg, ceb, cea), elongated=False,
                backX=backX, backY=backY)
            if part is not None:
                parts.append(part)
                nodes.append(np)

        for i in range(streakCount):
            part, np = self._makeCreamSparkleFleck(
                trailOrigin, i, max(1, streakCount), streakSize,
                drift * 1.15, sec * 0.9,
                (sr, sg, sb, sa), (ser, seg, seb, sea), elongated=True,
                backX=backX, backY=backY)
            if part is not None:
                parts.append(part)
                nodes.append(np)

        if not parts:
            return

        # Residual cream aftershock after this sparkle drip settles.
        aftershock = self._buildCreamAftershock(
            trailOrigin, backX, backY, aftershockNodes)

        layers = [Parallel(*parts)]
        if aftershock is not None:
            layers.append(aftershock)
        allNodes = list(nodes) + list(aftershockNodes)
        ival = Sequence(
            Parallel(*layers),
            Func(self._retirePulseNodes, allNodes),
            name=self.avatar.uniqueName(
                'hackslashDodgeTrailCreamSparkle-%s' % self._creamSparkleIndex),
        )
        self._creamSparkles.append({
            'ival': ival,
            'nodes': allNodes,
        })
        ival.start()

    def _buildCreamAftershock(self, origin, backX, backY, nodeBucket):
        """Delayed soft cream flecks (+ optional halo) after trail sparkle.

        Cream/pastel only — no ink. Same residual grammar as finisher /
        combo cream aftershock.
        """
        if not getattr(
                HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_ENABLED', True):
            return None
        delay = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_DELAY_SEC', 0.16))
        parts = []

        if getattr(
                HackSlashConfig,
                'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_ENABLED', True):
            halo = self._spawnCreamAftershockHalo(origin, nodeBucket)
            if halo is not None:
                parts.append(halo)

        creamCount = int(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_COUNT', 2))
        streakCount = int(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_STREAK_COUNT', 1))
        for i in range(creamCount):
            part = self._spawnCreamAftershockFleck(
                origin, i, creamCount, elongated=False,
                backX=backX, backY=backY, nodeBucket=nodeBucket)
            if part is not None:
                parts.append(part)
        for i in range(streakCount):
            part = self._spawnCreamAftershockFleck(
                origin, i, max(1, streakCount), elongated=True,
                backX=backX, backY=backY, nodeBucket=nodeBucket)
            if part is not None:
                parts.append(part)

        if not parts:
            return None
        return Sequence(
            Wait(max(0.0, delay)),
            Parallel(*parts),
        )

    def _spawnCreamAftershockHalo(self, origin, nodeBucket):
        """Soft cream halo pulse behind residual dodge aftershock flecks."""
        half = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_HALF', 0.38))
        startScale = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_START', 0.32))
        peakScale = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_PEAK', 1.45))
        sec = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_SEC', 0.28))
        peakA = float(getattr(
            HackSlashConfig,
            'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_PEAK_ALPHA', 0.22))
        r, g, b, _a = getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_HALO_COLOR',
            (1.0, 0.96, 0.78, 1.0))
        try:
            cm = CardMaker(
                'hackslash-dodge-cream-aftershock-halo-%s' % (
                    self._creamSparkleIndex,))
            cm.setFrame(-half, half, -half, half)
            halo = render.attachNewNode(cm.generate())  # noqa: F821
            halo.setTransparency(TransparencyAttrib.MAlpha)
            halo.setColor(r, g, b, 1)
            halo.setColorScale(r, g, b, peakA)
            halo.setPos(origin)
            halo.setScale(startScale)
            # Under flecks so residual glitter reads on top of the soft wash.
            halo.setBin('transparent', 22)
            halo.setDepthWrite(False)
            halo.setBillboardPointEye()
        except Exception:
            return None
        nodeBucket.append(halo)
        return Parallel(
            LerpScaleInterval(
                halo, max(0.01, sec), peakScale, blendType='easeOut'),
            Sequence(
                Wait(max(0.0, sec * 0.2)),
                LerpColorScaleInterval(
                    halo, max(0.01, sec * 0.8), Vec4(r, g, b, 0),
                    blendType='easeIn'),
            ),
        )

    def _spawnCreamAftershockFleck(self, origin, index, total, elongated=False,
                                   backX=0.0, backY=0.0, nodeBucket=None):
        """Softer cream fleck / streak that settles — residual trail aftershock."""
        count = max(1, int(total))
        if elongated:
            size = float(getattr(
                HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_STREAK_SIZE',
                0.065))
            r, g, b, a = getattr(
                HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_STREAK_COLOR',
                (1.0, 0.98, 0.82, 0.82))
            er, eg, eb, ea = getattr(
                HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_STREAK_END',
                (1.0, 0.9, 0.5, 0.0))
            nameSuffix = 'streak'
            angleBias = 0.58
        else:
            size = float(getattr(
                HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_SIZE', 0.09))
            r, g, b, a = getattr(
                HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_COLOR',
                (1.0, 0.96, 0.72, 0.86))
            er, eg, eb, ea = getattr(
                HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_END',
                (1.0, 0.92, 0.55, 0.0))
            nameSuffix = 'cream'
            angleBias = 0.26
        drift = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_DRIFT', 0.5))
        sec = float(getattr(
            HackSlashConfig, 'DODGE_TRAIL_CREAM_AFTERSHOCK_SEC', 0.34))
        angle = (
            (2.0 * pi * index) / float(count)
            + angleBias
            + 0.07 * (self._creamSparkleIndex % 3))
        try:
            cm = CardMaker(
                'hackslash-dodge-cream-aftershock-%s-%s-%s' % (
                    self._creamSparkleIndex, nameSuffix, index))
            if elongated:
                cm.setFrame(
                    -size * 0.35, size * 0.35,
                    -size * 1.15, size * 1.15)
            else:
                cm.setFrame(-size, size, -size * 0.85, size * 0.85)
            fleck = render.attachNewNode(cm.generate())  # noqa: F821
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, 0)
            fleck.setPos(
                origin[0] + cos(angle) * 0.08,
                origin[1] + sin(angle) * 0.08,
                origin[2] + 0.03 * (index % 2))
            fleck.setScale(0.28 + 0.08 * (index % 3))
            fleck.setBin('transparent', 24)
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return None

        # Settle downward/back — residual cream, not the sparkle drip punch.
        end = Point3(
            origin[0] + cos(angle) * drift * 0.55 + backX * 0.12,
            origin[1] + sin(angle) * drift * 0.55 + backY * 0.12,
            origin[2] - 0.35 - 0.08 * (index % 3))
        peak = 0.95 + 0.08 * (index % 2)
        if nodeBucket is not None:
            nodeBucket.append(fleck)
        stagger = 0.016 * (index % 3)
        return Sequence(
            Wait(stagger),
            Parallel(
                LerpColorScaleInterval(
                    fleck, 0.05, Vec4(r, g, b, a), blendType='easeOut'),
                LerpScaleInterval(
                    fleck, sec * 0.28, peak, blendType='easeOut'),
            ),
            Parallel(
                LerpPosInterval(fleck, sec * 0.72, end, blendType='easeIn'),
                LerpScaleInterval(
                    fleck, sec * 0.72, 0.04, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, sec * 0.72, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )

    def _makeCreamSparkleFleck(self, origin, index, count, size, drift, sec,
                               color, endColor, elongated=False,
                               backX=0.0, backY=0.0):
        """Sunny cream / pastel fleck — trail glitter, not ink / not KH."""
        count = max(1, int(count))
        # Phase offset from i-frame pulse flecks so both layers stay readable.
        angle = (
            (2.0 * pi * index) / float(count)
            + (0.72 if elongated else 0.4)
            + 0.09 * (self._creamSparkleIndex % 3))
        r, g, b, a = color
        er, eg, eb, ea = endColor
        halfH = size * (0.35 if elongated else 1.0)
        try:
            cm = CardMaker('hackslash-dodge-cream-sparkle-%s-%s-%s' % (
                self._creamSparkleIndex,
                'streak' if elongated else 'fleck',
                index))
            cm.setFrame(-size, size, -halfH, halfH)
            fleck = render.attachNewNode(cm.generate())  # noqa: F821
            fleck.setTransparency(TransparencyAttrib.MAlpha)
            fleck.setColor(r, g, b, 1)
            fleck.setColorScale(r, g, b, a)
            side = -1.0 if (index % 2) else 1.0
            fleck.setPos(
                origin[0] + cos(angle) * 0.1 + side * 0.08,
                origin[1] + sin(angle) * 0.1,
                origin[2] + 0.06 * (index % 3) - 0.04)
            fleck.setScale(0.45 + 0.1 * (index % 3))
            fleck.setBin('transparent', 23)
            fleck.setDepthWrite(False)
            fleck.setBillboardPointEye()
        except Exception:
            return None, None

        end = Point3(
            origin[0] + cos(angle) * drift + backX * (0.2 if elongated else 0.1),
            origin[1] + sin(angle) * drift + backY * (0.2 if elongated else 0.1),
            origin[2] + (0.2 if elongated else -0.15) - 0.06 * (index % 3))
        peak = (1.55 if elongated else 1.25) + 0.12 * (index % 2)
        part = Sequence(
            Parallel(
                LerpScaleInterval(
                    fleck, sec * 0.3, peak, blendType='easeOut'),
                LerpPosInterval(
                    fleck, sec * 0.6, end, blendType='easeOut'),
                LerpColorScaleInterval(
                    fleck, sec * 0.5, Vec4(r, g, b, a), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(fleck, sec * 0.45, 0.04, blendType='easeIn'),
                LerpColorScaleInterval(
                    fleck, sec * 0.45, Vec4(er, eg, eb, ea),
                    blendType='easeIn'),
            ),
        )
        return part, fleck

    def _destroyCreamSparkle(self, entry):
        ival = entry.get('ival')
        if ival is not None:
            try:
                ival.pause()
            except Exception:
                pass
        self._retirePulseNodes(entry.get('nodes'))

    def _retirePulseNodes(self, nodes):
        for np in list(nodes or []):
            self._retireNode(np)

    def _destroyPulse(self, entry):
        ival = entry.get('ival')
        if ival is not None:
            try:
                ival.pause()
            except Exception:
                pass
        self._retirePulseNodes(entry.get('nodes'))

    def _retireNode(self, np):
        try:
            if np is not None and not np.isEmpty():
                np.removeNode()
        except Exception:
            pass

    def _destroyEntry(self, entry):
        ival = entry.get('ival')
        if ival is not None:
            try:
                ival.pause()
            except Exception:
                pass
        for spark in entry.get('sparks') or []:
            sIval = spark.get('ival')
            if sIval is not None:
                try:
                    sIval.pause()
                except Exception:
                    pass
            self._retireNode(spark.get('np'))
        self._retireNode(entry.get('np'))
