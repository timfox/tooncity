"""Brief rubber-hose hitstop / freeze on melee hit connect.

Pauses juice intervals and zeros actor play rates so the impact silhouette
sticks for a beat, then resumes. Client-only — Toontown spiritual-sequel
tone, no keyblades / no KH branding.
"""

from direct.task import Task

from . import HackSlashConfig
from . import HitJuice


class HitStopFx(object):
    """Owns one short freeze window for Oswald stretch-punch connects."""

    def __init__(self, avatar):
        self.avatar = avatar
        self._active = False
        self._intervals = ()
        self._actors = ()
        self._savedRates = []
        self._onDone = None
        self._taskName = avatar.uniqueName('hackslashHitstop')

    def play(self, stopSec, intervals=(), actors=(), onDone=None):
        """Freeze intervals + actor anims for stopSec, then resume.

        Returns True when a freeze was scheduled. `onDone` runs after resume
        (or immediately when stopSec is zero / disabled).
        """
        if not getattr(HackSlashConfig, 'HITSTOP_ENABLED', True):
            if onDone:
                try:
                    onDone()
                except Exception:
                    pass
            return False

        self.clear(resume=True, runDone=False)
        stopSec = max(0.0, float(stopSec))
        self._onDone = onDone
        if stopSec <= 0.0:
            self._fireDone()
            return False

        self._intervals = tuple(ival for ival in intervals if ival)
        self._actors = tuple(actor for actor in actors if actor is not None)
        HitJuice.pauseIntervals(self._intervals)
        self._savedRates = HitJuice.freezeActorPlayRates(self._actors)
        self._active = True
        try:
            taskMgr.remove(self._taskName)  # noqa: F821
        except Exception:
            pass
        taskMgr.doMethodLater(stopSec, self._resumeTask, self._taskName)  # noqa: F821
        return True

    def _resumeTask(self, task):
        self.clear(resume=True, runDone=True)
        return Task.done

    def clear(self, resume=True, runDone=False):
        """Cancel the freeze timer; optionally resume paused juice/anims."""
        try:
            taskMgr.remove(self._taskName)  # noqa: F821
        except Exception:
            pass
        if resume and self._active:
            HitJuice.resumeIntervals(self._intervals)
            HitJuice.restoreActorPlayRates(self._savedRates)
        self._active = False
        self._intervals = ()
        self._actors = ()
        self._savedRates = []
        if runDone:
            self._fireDone()
        else:
            self._onDone = None

    def _fireDone(self):
        cb = self._onDone
        self._onDone = None
        if cb:
            try:
                cb()
            except Exception:
                pass

    def isActive(self):
        return self._active
