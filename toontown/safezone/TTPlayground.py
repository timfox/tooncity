from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from . import Playground
import random
from toontown.launcher import DownloadForceAcknowledge
from direct.task.Task import Task
from toontown.hood import ZoneUtil
from toontown.safezone import CorruptStreetBreadcrumb

class TTPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        Playground.Playground.load(self)

    def unload(self):
        Playground.Playground.unload(self)

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        taskMgr.doMethodLater(1, self.__birds, 'TT-birds')
        # Polluted Loopy / Punchline / Silly tunnel placemarkers (hub explore).
        CorruptStreetBreadcrumb.ensureCorruptStreetBreadcrumbs(self)
        # Trusted Oswald hub presence stub (meet before twist — campaign).
        try:
            from toontown.campaign.OswaldPresence import (
                refreshOswaldPresenceHub)
            refreshOswaldPresenceHub()
        except Exception:
            pass
        # Post-betrayal hub stain confront placemarker (fog + plaza label).
        try:
            from toontown.campaign.HubStainConfront import (
                refreshHubStainConfront)
            refreshHubStainConfront()
        except Exception:
            pass
        # Washed-plaza epilogue beat after chase clear (beyond plate + tip).
        try:
            from toontown.campaign.HubEpilogueBeat import (
                refreshHubEpilogueBeat)
            refreshHubEpilogueBeat()
        except Exception:
            pass

    def exit(self):
        CorruptStreetBreadcrumb.stopCorruptStreetBreadcrumbs()
        try:
            from toontown.campaign.OswaldPresence import (
                stopOswaldPresenceClient)
            stopOswaldPresenceClient()
        except Exception:
            pass
        try:
            from toontown.campaign.HubStainConfront import (
                stopHubStainConfront)
            stopHubStainConfront()
        except Exception:
            pass
        try:
            from toontown.campaign.HubEpilogueBeat import (
                stopHubEpilogueBeat)
            stopHubEpilogueBeat()
        except Exception:
            pass
        Playground.Playground.exit(self)
        taskMgr.remove('TT-birds')

    def __birds(self, task):
        base.playSfx(random.choice(self.loader.birdSound))
        t = random.random() * 20.0 + 1
        taskMgr.doMethodLater(t, self.__birds, 'TT-birds')
        return Task.done

    def doRequestLeave(self, requestStatus):
        self.fsm.request('trialerFA', [requestStatus])

    def enterDFA(self, requestStatus):
        doneEvent = 'dfaDoneEvent'
        self.accept(doneEvent, self.enterDFACallback, [requestStatus])
        self.dfa = DownloadForceAcknowledge.DownloadForceAcknowledge(doneEvent)
        hood = ZoneUtil.getCanonicalZoneId(requestStatus['hoodId'])
        if hood == ToontownGlobals.MyEstate:
            self.dfa.enter(base.cr.hoodMgr.getPhaseFromHood(ToontownGlobals.MyEstate))
        elif hood == ToontownGlobals.GoofySpeedway:
            self.dfa.enter(base.cr.hoodMgr.getPhaseFromHood(ToontownGlobals.GoofySpeedway))
        elif hood == ToontownGlobals.PartyHood:
            self.dfa.enter(base.cr.hoodMgr.getPhaseFromHood(ToontownGlobals.PartyHood))
        else:
            self.dfa.enter(5)

    def showPaths(self):
        from toontown.classicchars import CCharPaths
        from toontown.toonbase import TTLocalizer
        self.showPathPoints(CCharPaths.getPaths(TTLocalizer.Mickey))
