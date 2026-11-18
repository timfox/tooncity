"""Rubber-hose dodge-roll afterimage / smear trail.

Client juice for the Shift/X i-frame roll: brief translucent smear ghosts
(and tiny spark pops) drip behind the toon while rolling. Wired from
MeleeCombat dodge start/end so hit-squash / hitstop paths stay untouched.

Toontown spiritual-sequel tone only — no keyblades / no KH branding.
"""

from math import cos, sin

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpPosInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
)
from direct.task import Task

from . import HackSlashConfig


class DodgeTrailFx(object):
    """Owns the drip task + ghost nodes for one avatar's dodge roll."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._taskName = avatar.uniqueName('hackslashDodgeTrail')
        self._ghosts = []
        self._nextSpawnAt = 0.0
        self._active = False
        self._spawnIndex = 0

    def start(self):
        """Begin dripping afterimages for the active dodge window."""
        self.stop(clearGhosts=False)
        self._active = True
        self._spawnIndex = 0
        self._nextSpawnAt = 0.0
        self._spawnGhost(initial=True)
        try:
            taskMgr.add(self._tick, self._taskName)  # noqa: F821
        except Exception:
            self._active = False

    def stop(self, clearGhosts=False):
        """Stop spawning; existing ghosts keep fading unless cleared."""
        self._active = False
        try:
            taskMgr.remove(self._taskName)  # noqa: F821
        except Exception:
            pass
        if clearGhosts:
            self.clear()

    def clear(self):
        """Hard-stop and remove every ghost/spark immediately."""
        self.stop(clearGhosts=False)
        for entry in list(self._ghosts):
            self._destroyEntry(entry)
        self._ghosts = []

    def _tick(self, task):
        if not self._active:
            return Task.done
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            return Task.done
        if now >= self._nextSpawnAt:
            self._spawnGhost()
            self._nextSpawnAt = now + float(HackSlashConfig.DODGE_TRAIL_SPAWN_SEC)
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
