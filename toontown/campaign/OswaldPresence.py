"""Trusted Oswald hub/street NPC-style presence before the twist.

Players meet Oswald as a rubber-hose body stub + short greet interact on
the TTC hub and campaign streets — the trust face they later lose at the
finale betrayal. Stub-shippable: CardMaker silhouette + nametag (not a
full DistributedNPC / DNA toon, not companion AI, not cream FX).
Suppresses after reveal / betrayal chase, including AI-persisted
STATE_VICTORY mirrored on login. Toontown spiritual sequel — no keyblades /
KH branding.
"""

from __future__ import annotations

import math

from panda3d.core import (
    CardMaker,
    TextNode,
    TransparencyAttrib,
    Vec4,
)

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpHprInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject

from toontown.campaign import CampaignGlobals
from toontown.hood import ZoneUtil


def presenceEnabled():
    return bool(getattr(CampaignGlobals, 'OSWALD_PRESENCE_ENABLED', True))


def presenceLabel():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_LABEL',
        getattr(CampaignGlobals, 'PROTAGONIST', 'Oswald')))


def presencePlate():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_PLATE', 'OSWALD'))


def hubGreetTip():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_HUB_GREET',
        'Oswald waves from the plaza — "Loopy Lane needs us first!"  |  '
        'Hop the tunnel  |  C campaign'))


def streetGreetTip():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_STREET_GREET',
        'Oswald tips his ears — "I\'ll field the packs — '
        'stretch-punch ready!"  |  '
        'F fight  |  Shift dodge  |  C campaign'))


def interactPromptTip():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_INTERACT_PROMPT',
        'E — Talk to Oswald'))


def interactRadius():
    return max(2.0, float(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_INTERACT_RADIUS', 12.0)))


def spawnForward():
    return float(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_SPAWN_FORWARD', 6.5))


def spawnRight():
    return float(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_SPAWN_RIGHT', 2.25))


def hideOnBetrayal():
    return bool(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_HIDE_ON_BETRAYAL', True))


def presenceZoneIds():
    """Hub + campaign ACTS streets where the trusted stub may appear."""
    zones = set()
    hub = getattr(CampaignGlobals, 'HUB_ZONE', None)
    if hub is not None:
        zones.add(int(hub))
    for act in getattr(CampaignGlobals, 'ACTS', ()) or ():
        zid = act.get('zoneId')
        if zid is not None:
            zones.add(int(zid))
    return zones


def greetTipForZone(zoneId):
    """Hub vs street greet copy for the trusted Oswald stub."""
    hub = int(getattr(CampaignGlobals, 'HUB_ZONE', -1))
    try:
        zid = int(zoneId)
    except Exception:
        zid = -1
    if zid == hub:
        return hubGreetTip()
    return streetGreetTip()


def shouldShowPresence(zoneId, betrayed=False):
    """True when the trusted stub should be live in this zone."""
    if not presenceEnabled():
        return False
    if betrayed and hideOnBetrayal():
        return False
    try:
        zid = int(zoneId)
    except Exception:
        return False
    return zid in presenceZoneIds()


# Sunny trusted body (readable on TTC / streets — not ink purple).
_BODY_COLOR = Vec4(0.22, 0.58, 0.96, 1.0)
_HEAD_COLOR = Vec4(0.95, 0.82, 0.55, 1.0)
_EAR_COLOR = Vec4(0.18, 0.18, 0.22, 0.95)
_ARM_COLOR = Vec4(0.95, 0.82, 0.55, 1.0)
_LEG_COLOR = Vec4(0.16, 0.42, 0.78, 0.95)
_TIP_COLOR = Vec4(0.95, 0.98, 1.0, 1.0)
_PROMPT_COLOR = Vec4(0.92, 0.96, 1.0, 1.0)


class OswaldPresenceClient(DirectObject):
    """NPC-style body stub + short greet interact for trusted Oswald.

    AI-free stub: place a rubber-hose silhouette near the local toon on
    hub/street enter, arm E-talk when approached, greet once per zone
    visit, clear after betrayal messengers / persisted victory sync.
    """

    def __init__(self):
        DirectObject.__init__(self)
        self._rootNP = None
        self._bodyNP = None
        self._nametagNP = None
        self._tipNP = None
        self._tipIval = None
        self._promptNP = None
        self._waveIval = None
        self._zoneId = None
        self._greetedZone = None
        self._betrayed = False
        self._markerPos = None
        self._inRange = False
        self._interactArmed = False
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('oswaldRevealBanner', self._onBetrayal)
        self.accept('oswaldRevealSting', self._onBetrayal)
        self.accept('campaignVictory', self._onBetrayal)
        self.accept('oswaldBetrayalChase', self._onBetrayal)
        # Login mirror — AI-persisted STATE_VICTORY must hide trusted Oswald
        # after relog (session-only `_betrayed` is not enough).
        syncMsg = getattr(
            CampaignGlobals, 'CAMPAIGN_PROGRESS_SYNC_MSG',
            'campaignProgressSync')
        self.accept(syncMsg, self._onCampaignProgressSync)
        taskMgr.doMethodLater(  # noqa: F821
            2.15, self._bootZone, 'oswaldPresenceBoot')

    def destroy(self):
        self.ignoreAll()
        try:
            taskMgr.remove('oswaldPresenceBoot')  # noqa: F821
        except Exception:
            pass
        self._stopPoll()
        self._disarmInteract()
        self._clearPrompt()
        self._clearTip()
        self._clearBody()
        self._zoneId = None
        self._greetedZone = None
        self._betrayed = False

    def _bootZone(self, task):
        if hasattr(base, 'localAvatar'):  # noqa: F821
            self._onZoneChange(getattr(base.localAvatar, 'zoneId', None))
        return task.done

    def _onBetrayal(self, *args):
        if not hideOnBetrayal():
            return
        self._betrayed = True
        self._stopPoll()
        self._disarmInteract()
        self._clearPrompt()
        self._clearTip()
        self._clearBody()
        self._zoneId = None
        self._greetedZone = None
        self._inRange = False

    def _onCampaignProgressSync(
            self, unlockedThrough=0, state=0, chaseCleared=0, reclaimCount=0):
        """Apply AI-persisted victory so trusted presence survives relog."""
        try:
            from toontown.campaign import CampaignProgressSave
            mirror = CampaignProgressSave.clientMirrorFromProgress({
                'unlockedThrough': unlockedThrough,
                'state': state,
                'chaseCleared': chaseCleared,
                'reclaimCount': reclaimCount,
            })
        except Exception:
            return
        betrayed = bool(mirror.get('betrayed'))
        if betrayed:
            if not self._betrayed:
                self._onBetrayal()
            else:
                self._betrayed = True
            return
        # Fresh / mid-campaign — trusted face may return (replay wipe).
        wasBetrayed = self._betrayed
        self._betrayed = False
        if wasBetrayed:
            # Re-arm marker in the current zone after a replay wipe sync.
            self._onZoneChange(self._zoneId)

    def _onZoneChange(self, zoneId=None):
        if zoneId is None and hasattr(base, 'localAvatar'):  # noqa: F821
            zoneId = getattr(base.localAvatar, 'zoneId', None)
        if zoneId is None:
            return
        try:
            zoneId = int(ZoneUtil.getBranchZone(int(zoneId)))
        except Exception:
            try:
                zoneId = int(zoneId)
            except Exception:
                return
        self._stopPoll()
        self._disarmInteract()
        self._clearPrompt()
        self._clearTip()
        self._clearBody()
        self._inRange = False
        self._zoneId = zoneId
        if not shouldShowPresence(zoneId, betrayed=self._betrayed):
            return
        self._placeBodyNearAvatar(zoneId)
        self._startPoll()

    def refreshHub(self):
        """Optional hub re-arm (TTPlayground enter)."""
        hub = int(getattr(CampaignGlobals, 'HUB_ZONE', -1))
        if hub > 0:
            self._onZoneChange(hub)

    def _bodyColor(self):
        color = getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_BODY_COLOR', None)
        if color is None:
            color = getattr(
                CampaignGlobals, 'OSWALD_PRESENCE_MARKER_COLOR', None)
        if color is None:
            return _BODY_COLOR
        return Vec4(
            float(color[0]), float(color[1]),
            float(color[2]), float(color[3]))

    def _placeBodyNearAvatar(self, zoneId):
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        parent = getattr(base, 'render', None)  # noqa: F821
        if av is None or parent is None:
            return
        try:
            baseX = float(av.getX())
            baseY = float(av.getY())
            baseZ = float(av.getZ())
            heading = float(av.getH())
        except Exception:
            return
        rad = math.radians(heading)
        forward = spawnForward()
        right = spawnRight()
        # Forward of facing + slight right so the stub reads beside the path.
        x = baseX - math.sin(rad) * forward + math.cos(rad) * right
        y = baseY + math.cos(rad) * forward + math.sin(rad) * right
        z = baseZ + float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_BODY_Z', 0.0))

        root = parent.attachNewNode('oswaldPresenceNpc')
        root.setPos(x, y, z)
        # Face the local toon (NPC-style stand).
        try:
            root.lookAt(av)
            root.setP(0)
            root.setR(0)
        except Exception:
            pass

        bodyColor = self._bodyColor()
        self._buildNpcSilhouette(root, bodyColor)
        self._buildNametag(root, bodyColor)

        # Soft rubber-hose appear pop on the whole body.
        try:
            scale = float(getattr(
                CampaignGlobals, 'OSWALD_PRESENCE_BODY_SCALE', 1.0))
            root.setScale(scale * 0.55)
            Sequence(
                LerpScaleInterval(root, 0.12, scale * 1.12),
                LerpScaleInterval(root, 0.10, scale),
                name='oswaldPresenceNpcPop',
            ).start()
        except Exception:
            pass

        self._rootNP = root
        self._markerPos = (x, y, baseZ)

    def _buildNpcSilhouette(self, root, bodyColor):
        """Rubber-hose CardMaker body — meetable NPC stub, not TextNode-only."""
        bodyRoot = root.attachNewNode('oswaldPresenceBody')

        torso = CardMaker('oswald-npc-torso')
        torso.setFrame(-0.55, 0.55, 0.55, 1.85)
        torsoNP = bodyRoot.attachNewNode(torso.generate())
        torsoNP.setColor(bodyColor)
        torsoNP.setBillboardPointEye()
        torsoNP.setTransparency(TransparencyAttrib.MAlpha)

        arm = CardMaker('oswald-npc-arm')
        arm.setFrame(-1.45, 1.45, 0.95, 1.28)
        armNP = bodyRoot.attachNewNode(arm.generate())
        armNP.setColor(_ARM_COLOR)
        armNP.setBillboardPointEye()
        armNP.setTransparency(TransparencyAttrib.MAlpha)

        head = CardMaker('oswald-npc-head')
        head.setFrame(-0.48, 0.48, 0.0, 0.95)
        headNP = bodyRoot.attachNewNode(head.generate())
        headNP.setPos(0, 0, 1.85)
        headNP.setColor(_HEAD_COLOR)
        headNP.setBillboardPointEye()
        headNP.setTransparency(TransparencyAttrib.MAlpha)

        # Twin rabbit-ear stubs — Oswald silhouette cue without DNA.
        earL = CardMaker('oswald-npc-ear-l')
        earL.setFrame(-0.42, -0.08, 0.85, 1.55)
        earLNP = bodyRoot.attachNewNode(earL.generate())
        earLNP.setPos(0, 0, 1.85)
        earLNP.setColor(_EAR_COLOR)
        earLNP.setBillboardPointEye()
        earLNP.setTransparency(TransparencyAttrib.MAlpha)

        earR = CardMaker('oswald-npc-ear-r')
        earR.setFrame(0.08, 0.42, 0.85, 1.55)
        earRNP = bodyRoot.attachNewNode(earR.generate())
        earRNP.setPos(0, 0, 1.85)
        earRNP.setColor(_EAR_COLOR)
        earRNP.setBillboardPointEye()
        earRNP.setTransparency(TransparencyAttrib.MAlpha)

        legL = CardMaker('oswald-npc-leg-l')
        legL.setFrame(-0.42, -0.06, 0.0, 0.6)
        legLNP = bodyRoot.attachNewNode(legL.generate())
        legLNP.setColor(_LEG_COLOR)
        legLNP.setBillboardPointEye()
        legLNP.setTransparency(TransparencyAttrib.MAlpha)

        legR = CardMaker('oswald-npc-leg-r')
        legR.setFrame(0.06, 0.42, 0.0, 0.6)
        legRNP = bodyRoot.attachNewNode(legR.generate())
        legRNP.setColor(_LEG_COLOR)
        legRNP.setBillboardPointEye()
        legRNP.setTransparency(TransparencyAttrib.MAlpha)

        self._bodyNP = bodyRoot

    def _buildNametag(self, root, bodyColor):
        tn = TextNode('oswaldPresenceNametag')
        tn.setText(presenceLabel())
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(bodyColor)
        try:
            tn.setShadow(0.04, 0.04)
            tn.setShadowColor(0.05, 0.12, 0.28, 0.55)
        except Exception:
            pass
        np = root.attachNewNode(tn)
        np.setPos(0, 0, float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_NAMETAG_Z', 3.15)))
        np.setScale(float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_NAMETAG_SCALE', 0.55)))
        try:
            np.setBillboardPointEye()
        except Exception:
            pass
        self._nametagNP = np

    def _pollTaskName(self):
        return 'oswaldPresencePoll'

    def _startPoll(self):
        self._stopPoll()
        delay = max(0.15, float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_POLL_SEC', 0.35)))
        taskMgr.doMethodLater(  # noqa: F821
            delay, self._pollProximity, self._pollTaskName())

    def _stopPoll(self):
        try:
            taskMgr.remove(self._pollTaskName())  # noqa: F821
        except Exception:
            pass

    def _pollProximity(self, task):
        zoneId = self._zoneId
        if zoneId is None or not shouldShowPresence(
                zoneId, betrayed=self._betrayed):
            return task.done
        av = getattr(base, 'localAvatar', None)  # noqa: F821
        if av is None or self._markerPos is None:
            return task.again
        try:
            ax = float(av.getX())
            ay = float(av.getY())
        except Exception:
            return task.again
        mx, my, _mz = self._markerPos
        dist = math.hypot(ax - mx, ay - my)
        inRange = dist <= interactRadius()
        if inRange and not self._inRange:
            self._onEnterRange(zoneId)
        elif not inRange and self._inRange:
            self._onLeaveRange()
        self._inRange = inRange
        return task.again

    def _onEnterRange(self, zoneId):
        """NPC-style meet: arm short greet interact when player approaches."""
        if self._greetedZone is not None and int(self._greetedZone) == int(
                zoneId):
            return
        self._armInteract(zoneId)
        self._showInteractPrompt()

    def _onLeaveRange(self):
        self._disarmInteract()
        self._clearPrompt()

    def _interactEventName(self):
        return str(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_INTERACT_EVENT',
            'oswaldPresenceInteract'))

    def _armInteract(self, zoneId):
        self._disarmInteract()
        self._interactArmed = True
        # E — classic Toontown talk-to-NPC stub (also accept lowercase).
        self.accept('e', self._onInteractKey, [zoneId])
        self.accept('E', self._onInteractKey, [zoneId])
        # Optional messenger hook for tests / magic words.
        self.accept(self._interactEventName(), self._onInteractKey, [zoneId])

    def _disarmInteract(self):
        if not self._interactArmed:
            self.ignore('e')
            self.ignore('E')
            self.ignore(self._interactEventName())
            return
        self._interactArmed = False
        self.ignore('e')
        self.ignore('E')
        self.ignore(self._interactEventName())

    def _onInteractKey(self, zoneId=None, *args):
        if zoneId is None:
            zoneId = self._zoneId
        if zoneId is None:
            return
        if not self._inRange:
            return
        self._meetOswald(zoneId)

    def _meetOswald(self, zoneId):
        """Short greet interact — body wave + tip (once per zone visit)."""
        if self._greetedZone is not None and int(self._greetedZone) == int(
                zoneId):
            return
        self._greetedZone = int(zoneId)
        self._disarmInteract()
        self._clearPrompt()
        self._playGreetWave()
        tip = greetTipForZone(zoneId)
        self._showGreetTip(tip)
        try:
            messenger.send(  # noqa: F821
                'oswaldPresenceMet', [int(zoneId), presenceLabel()])
        except Exception:
            pass

    def _playGreetWave(self):
        """Rubber-hose tip-of-ears / wave bounce on the NPC body."""
        if self._waveIval is not None:
            try:
                self._waveIval.pause()
            except Exception:
                pass
            self._waveIval = None
        body = self._bodyNP
        if body is None:
            return
        try:
            baseScale = body.getScale()
            self._waveIval = Sequence(
                Parallel(
                    LerpScaleInterval(
                        body, 0.10,
                        (baseScale[0] * 1.08, baseScale[1],
                         baseScale[2] * 1.12)),
                    LerpHprInterval(body, 0.10, (12, 0, 0)),
                ),
                Parallel(
                    LerpScaleInterval(body, 0.12, baseScale),
                    LerpHprInterval(body, 0.12, (0, 0, 0)),
                ),
                LerpHprInterval(body, 0.08, (-8, 0, 0)),
                LerpHprInterval(body, 0.08, (0, 0, 0)),
                name='oswaldPresenceGreetWave',
            )
            self._waveIval.start()
        except Exception:
            self._waveIval = None

    def _showInteractPrompt(self):
        self._clearPrompt()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return
        tn = TextNode('oswaldPresenceInteractPrompt')
        tn.setText(interactPromptTip())
        tn.setAlign(TextNode.ACenter)
        tn.setWordwrap(22)
        tn.setTextColor(_PROMPT_COLOR)
        tipNP = parent.attachNewNode(tn)
        tipNP.setScale(0.038)
        tipNP.setPos(0.0, 0.0, -0.68)
        tipNP.setColorScale(1, 1, 1, 0)
        self._promptNP = tipNP
        try:
            LerpColorScaleInterval(
                tipNP, 0.12, Vec4(1, 1, 1, 1)).start()
        except Exception:
            tipNP.setColorScale(1, 1, 1, 1)

    def _clearPrompt(self):
        if self._promptNP is not None:
            try:
                self._promptNP.removeNode()
            except Exception:
                pass
            self._promptNP = None

    def _showGreetTip(self, tip):
        self._clearTip()
        try:
            parent = aspect2d  # noqa: F821
        except Exception:
            return
        color = getattr(CampaignGlobals, 'OSWALD_PRESENCE_TIP_COLOR', None)
        if color is None:
            tipColor = _TIP_COLOR
        else:
            tipColor = Vec4(
                float(color[0]), float(color[1]),
                float(color[2]), float(color[3]))
        tn = TextNode('oswaldPresenceTip')
        tn.setText(str(tip))
        tn.setAlign(TextNode.ACenter)
        tn.setWordwrap(28)
        tn.setTextColor(tipColor)
        tipNP = parent.attachNewNode(tn)
        tipNP.setScale(0.045)
        tipNP.setPos(0.0, 0.0, -0.78)
        tipNP.setColorScale(1, 1, 1, 0)
        self._tipNP = tipNP
        hold = max(1.0, float(getattr(
            CampaignGlobals, 'OSWALD_PRESENCE_GREET_HOLD_SEC', 3.2)))
        pop = Parallel(
            Sequence(
                LerpScaleInterval(tipNP, 0.08, 0.052),
                LerpScaleInterval(tipNP, 0.10, 0.045),
            ),
            LerpColorScaleInterval(tipNP, 0.12, Vec4(1, 1, 1, 1)),
        )
        self._tipIval = Sequence(
            pop,
            Wait(hold),
            LerpColorScaleInterval(tipNP, 0.28, Vec4(1, 1, 1, 0)),
            Func(self._clearTip),
            name='oswaldPresenceGreetTip',
        )
        self._tipIval.start()

    def _clearTip(self):
        if self._tipIval is not None:
            try:
                self._tipIval.pause()
            except Exception:
                pass
            self._tipIval = None
        if self._tipNP is not None:
            try:
                self._tipNP.removeNode()
            except Exception:
                pass
            self._tipNP = None

    def _clearBody(self):
        if self._waveIval is not None:
            try:
                self._waveIval.pause()
            except Exception:
                pass
            self._waveIval = None
        if self._rootNP is not None:
            try:
                self._rootNP.removeNode()
            except Exception:
                pass
            self._rootNP = None
        self._bodyNP = None
        self._nametagNP = None
        self._markerPos = None


_client = None


def ensureOswaldPresenceClient():
    global _client
    if _client is None:
        _client = OswaldPresenceClient()
    return _client


def refreshOswaldPresenceHub():
    """Thin hub re-arm for TTPlayground enter."""
    client = ensureOswaldPresenceClient()
    try:
        client.refreshHub()
    except Exception:
        pass
    return client


def stopOswaldPresenceClient():
    """Optional teardown (playground exit) — keeps singleton for re-enter."""
    global _client
    if _client is None:
        return
    try:
        _client._stopPoll()
        _client._disarmInteract()
        _client._clearPrompt()
        _client._clearTip()
        _client._clearBody()
    except Exception:
        pass
