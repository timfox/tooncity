"""Trusted Oswald hub/street NPC-style presence before the twist.

Players meet Oswald as a rubber-hose plaza lead + short greet interact on
the TTC hub (authored plaza stand) and campaign ACTS streets (authored
street stands on stable landmarks — not SPAWN_FORWARD beside the local
toon) — the trust face they later lose at the finale betrayal. Beyond the
spawn-near-avatar CardMaker stub: fixed plaza + ACTS street placement,
idle bob, and a reclaim cheer beat when a street clears (`npcCheerStub` /
purity), then vanish for the twist. After ``oswaldCheered``, plaza/street
E-talk soft-nexts from unlock progress (trust ladder mid-act beats).
Stub-shippable: CardMaker silhouette + nametag (not a full DistributedNPC
/ DNA toon, not companion AI, not cream FX). Suppresses after reveal /
betrayal chase, including AI-persisted STATE_VICTORY mirrored on login.
Toontown spiritual sequel — no keyblades / KH branding.
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
    LerpPosInterval,
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


def hubGreetSoftNextTip(street):
    """Post-cheer hub greet pointing at soft-next street."""
    tmpl = str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT',
        'Oswald waves from the plaza — "{street} needs us next!"  |  '
        'Hop the tunnel  |  C campaign'))
    try:
        return tmpl.format(street=str(street))
    except Exception:
        return tmpl.replace('{street}', str(street))


def streetGreetSoftNextTip(street):
    """Post-cheer street greet pointing at soft-next street."""
    tmpl = str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT',
        'Oswald tips his ears — "Wash this stain — then {street}!"  |  '
        'F fight  |  Shift dodge  |  C campaign'))
    try:
        return tmpl.format(street=str(street))
    except Exception:
        return tmpl.replace('{street}', str(street))


def hubGreetCheeredTip():
    """Post-cheer hub greet before unlock advances soft-next."""
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_HUB_GREET_CHEERED',
        'Oswald waves — "That clean cheer sticks — keep reclaiming!"  |  '
        'Hop the tunnel  |  C campaign'))


def streetGreetCheeredTip():
    """Post-cheer street greet before unlock advances soft-next."""
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_STREET_GREET_CHEERED',
        'Oswald tips his ears — "We washed one street — packs still wait!"  |  '
        'F fight  |  Shift dodge  |  C campaign'))


def cheerTip():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_CHEER_TIP',
        'Oswald cheers — "Street\'s clean! On to the next!"  |  '
        'Hop the tunnel  |  C campaign'))


def firstMeetTip():
    """Once-ever trust tip after the first E-talk meet (survives relog)."""
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_FIRST_MEET_TIP',
        'You met Oswald — trust the plaza lead! He\'ll point the reclaim.  |  '
        'Hop a tunnel  |  C campaign'))


def metMsgName():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_MET_MSG',
        'oswaldPresenceMet'))


def metSyncMsgName():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_MET_SYNC_MSG',
        'oswaldMetSync'))


def cheeredMsgName():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_CHEERED_MSG',
        'oswaldPresenceCheered'))


def cheeredSyncMsgName():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_CHEERED_SYNC_MSG',
        'oswaldCheeredSync'))


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


def cheerOnReclaim():
    return bool(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_CHEER_ON_RECLAIM', True))


def cheerMsgName():
    return str(getattr(
        CampaignGlobals, 'OSWALD_PRESENCE_CHEER_MSG',
        'oswaldPresenceCheer'))


def hubPlazaPos():
    """Authored TTC plaza stand (x, y, z, h) or None if unset."""
    raw = getattr(CampaignGlobals, 'OSWALD_PRESENCE_HUB_POS', None)
    if raw is None:
        return None
    try:
        return (
            float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]))
    except Exception:
        return None


def _parseStandPos(raw):
    """Coerce (x, y, z, h) authored stand tuple or None."""
    if raw is None:
        return None
    try:
        return (
            float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]))
    except Exception:
        return None


def streetStandPos(zoneId):
    """Authored ACTS street stand (x, y, z, h) for zone, or None."""
    raw_map = getattr(CampaignGlobals, 'OSWALD_PRESENCE_STREET_POS', None)
    if not raw_map:
        return None
    try:
        zid = int(zoneId)
    except Exception:
        return None
    try:
        raw = raw_map.get(zid)
    except Exception:
        raw = None
    if raw is None:
        # Tolerate string keys from hand-edited tables.
        try:
            raw = raw_map.get(str(zid))
        except Exception:
            raw = None
    return _parseStandPos(raw)


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


def greetTipForZone(zoneId, cheered=False, softNextStreet=None):
    """Hub/street greet; soft-next after oswaldCheered + unlock progress.

    Pre-cheer: static hub/street copy. After the durable cheer latch, prefer
    soft-next templates filled from unlock progress (PlayEntry soft-next twin
    on the plaza NPC). First-meet tip stays separate (once-ever meet path).
    """
    helper = getattr(CampaignGlobals, 'oswaldPresenceGreetTip', None)
    if callable(helper):
        try:
            return str(helper(
                zoneId, cheered=cheered, softNextStreet=softNextStreet))
        except Exception:
            pass
    hub = int(getattr(CampaignGlobals, 'HUB_ZONE', -1))
    try:
        zid = int(zoneId)
    except Exception:
        zid = -1
    isHub = zid == hub
    if cheered:
        if softNextStreet:
            if isHub:
                return hubGreetSoftNextTip(softNextStreet)
            return streetGreetSoftNextTip(softNextStreet)
        if isHub:
            return hubGreetCheeredTip()
        return streetGreetCheeredTip()
    if isHub:
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
    """Plaza/street NPC-style body + greet interact + reclaim cheer.

    AI-free stub: place a rubber-hose silhouette at the authored TTC plaza
    stand or ACTS street landmark (near-avatar only as unmapped fallback),
    arm E-talk when approached, greet once per zone visit (first-ever meet
    uses the once-ever first-meet tip and persists ``oswaldMet``; later
    greets soft-next from ``oswaldCheered`` + unlock progress), cheer on
    street-clear purity messengers (first cheer latches + persists
    ``oswaldCheered``), clear after betrayal messengers / persisted victory
    sync.
    """

    def __init__(self):
        DirectObject.__init__(self)
        self._rootNP = None
        self._bodyNP = None
        self._armNP = None
        self._nametagNP = None
        self._tipNP = None
        self._tipIval = None
        self._promptNP = None
        self._waveIval = None
        self._cheerIval = None
        self._idleIval = None
        self._zoneId = None
        self._greetedZone = None
        # Durable first-meet latch (also hydrated from AI oswaldMet sync).
        self._oswaldMet = False
        # Durable first-cheer latch (also hydrated from AI oswaldCheered sync).
        self._oswaldCheered = False
        # Unlock soft-next for progress-aware greets after cheer latch.
        self._unlockedThrough = 0
        self._softNextStreet = None
        self._betrayed = False
        self._markerPos = None
        self._inRange = False
        self._interactArmed = False
        self._lastCheerT = -1.0
        self.accept('localAvatarZoneChange', self._onZoneChange)
        self.accept('oswaldRevealBanner', self._onBetrayal)
        self.accept('oswaldRevealSting', self._onBetrayal)
        self.accept('campaignVictory', self._onBetrayal)
        self.accept('oswaldBetrayalChase', self._onBetrayal)
        # Reclaim purity: director fires npcCheerStub / purityRestoreFx —
        # Oswald body must cheer (local-avatar bounce alone is not enough).
        self.accept('npcCheerStub', self._onReclaimCheer)
        self.accept('purityRestoreFx', self._onReclaimCheer)
        self.accept(cheerMsgName(), self._onReclaimCheer)
        # First-meet tip + persist — orphan send wired here (not PlayEntry).
        self.accept(metMsgName(), self._onOswaldPresenceMet)
        self.accept(metSyncMsgName(), self._onOswaldMetSync)
        # First reclaim cheer latch + persist — orphan send wired here.
        self.accept(cheeredMsgName(), self._onOswaldPresenceCheered)
        self.accept(cheeredSyncMsgName(), self._onOswaldCheeredSync)
        # Live act unlock — raise soft-next street for post-cheer greets.
        self.accept('campaignActUnlocked', self._onCampaignActUnlocked)
        # Login mirror — AI-persisted STATE_VICTORY must hide trusted Oswald
        # after relog (session-only `_betrayed` is not enough). Also hydrates
        # unlock soft-next for progress-aware plaza/street greets.
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
        self._oswaldMet = False
        self._oswaldCheered = False
        self._unlockedThrough = 0
        self._softNextStreet = None
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
        """Apply AI-persisted victory + unlock soft-next for greets."""
        try:
            from toontown.campaign import CampaignProgressSave
            mirror = CampaignProgressSave.clientMirrorFromProgress({
                'unlockedThrough': unlockedThrough,
                'state': state,
                'chaseCleared': chaseCleared,
                'reclaimCount': reclaimCount,
                # actIndex omitted — sanitize uses unlockedThrough as default.
            })
        except Exception:
            return
        betrayed = bool(mirror.get('betrayed'))
        if betrayed:
            self._unlockedThrough = int(mirror.get('unlockedThrough', 0) or 0)
            self._softNextStreet = None
            if not self._betrayed:
                self._onBetrayal()
            else:
                self._betrayed = True
            return
        # Fresh / mid-campaign — trusted face may return (replay wipe).
        wasBetrayed = self._betrayed
        self._betrayed = False
        self._unlockedThrough = int(mirror.get('unlockedThrough', 0) or 0)
        softStreet = mirror.get('softNextStreet')
        if softStreet:
            self._softNextStreet = str(softStreet)
        elif self._unlockedThrough <= 0:
            self._softNextStreet = None
        else:
            self._refreshSoftNextStreet()
        if wasBetrayed:
            # Re-arm marker in the current zone after a replay wipe sync.
            self._onZoneChange(self._zoneId)

    def _onCampaignActUnlocked(self, nextIndex=0, zoneId=0):
        """Raise unlock latch so post-cheer greets soft-next mid-session."""
        try:
            unlocked = int(nextIndex)
        except Exception:
            return
        if unlocked < 0:
            return
        self._unlockedThrough = max(int(self._unlockedThrough or 0), unlocked)
        self._refreshSoftNextStreet()

    def _refreshSoftNextStreet(self):
        """Derive soft-next street name from unlock progress (PlayEntry twin)."""
        try:
            from toontown.campaign import CampaignProgressSave
            soft = CampaignProgressSave.softNextStreetFromProgress({
                'unlockedThrough': int(self._unlockedThrough or 0),
                'actIndex': int(self._unlockedThrough or 0),
                'state': int(getattr(
                    CampaignGlobals, 'STATE_ACTIVE', 1)),
            })
            self._softNextStreet = str(soft) if soft else None
            return
        except Exception:
            pass
        acts = getattr(CampaignGlobals, 'ACTS', ()) or ()
        unlocked = int(self._unlockedThrough or 0)
        if unlocked <= 0 or not acts:
            self._softNextStreet = None
            return
        idx = max(0, min(unlocked, len(acts) - 1))
        name = acts[idx].get('name')
        self._softNextStreet = str(name) if name else None

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
        self._placeBody(zoneId)
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

    def _isHubZone(self, zoneId):
        try:
            return int(zoneId) == int(getattr(CampaignGlobals, 'HUB_ZONE', -1))
        except Exception:
            return False

    def _placeBody(self, zoneId):
        """Hub plaza / ACTS street authored stands; near-avatar as fallback."""
        if self._isHubZone(zoneId) and hubPlazaPos() is not None:
            self._placeBodyAtPlaza(zoneId)
            return
        stand = streetStandPos(zoneId)
        if stand is not None:
            self._placeBodyAtStreetStand(zoneId, stand)
            return
        # Unmapped presence zone — keep near-avatar field-lead fallback.
        self._placeBodyNearAvatar(zoneId)

    def _placeBodyAtAuthoredStand(self, stand):
        """Place the CardMaker stub at a fixed (x, y, z, h) landmark."""
        parent = getattr(base, 'render', None)  # noqa: F821
        if parent is None or stand is None:
            return
        x, y, z, h = stand
        root = parent.attachNewNode('oswaldPresenceNpc')
        root.setPos(x, y, z)
        try:
            root.setH(h)
            root.setP(0)
            root.setR(0)
        except Exception:
            pass
        bodyColor = self._bodyColor()
        self._buildNpcSilhouette(root, bodyColor)
        self._buildNametag(root, bodyColor)
        self._popAppear(root)
        self._rootNP = root
        self._markerPos = (x, y, z)
        self._startIdleBob()

    def _placeBodyAtPlaza(self, zoneId):
        self._placeBodyAtAuthoredStand(hubPlazaPos())

    def _placeBodyAtStreetStand(self, zoneId, stand=None):
        if stand is None:
            stand = streetStandPos(zoneId)
        self._placeBodyAtAuthoredStand(stand)

    def _placeBodyNearAvatar(self, zoneId):
        """Fallback when no authored plaza/street stand exists for the zone."""
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
        self._popAppear(root)

        self._rootNP = root
        self._markerPos = (x, y, baseZ)
        self._startIdleBob()

    def _popAppear(self, root):
        """Soft rubber-hose appear pop on the whole body."""
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

    def _buildNpcSilhouette(self, root, bodyColor):
        """Rubber-hose CardMaker body — meetable plaza NPC stub, not TextNode-only."""
        bodyRoot = root.attachNewNode('oswaldPresenceBody')

        torso = CardMaker('oswald-npc-torso')
        torso.setFrame(-0.55, 0.55, 0.55, 1.85)
        torsoNP = bodyRoot.attachNewNode(torso.generate())
        torsoNP.setColor(bodyColor)
        torsoNP.setBillboardPointEye()
        torsoNP.setTransparency(TransparencyAttrib.MAlpha)

        # Separate arm node so reclaim cheer can wave it (beyond flat stub).
        armRoot = bodyRoot.attachNewNode('oswaldPresenceArms')
        arm = CardMaker('oswald-npc-arm')
        arm.setFrame(-1.45, 1.45, 0.95, 1.28)
        armNP = armRoot.attachNewNode(arm.generate())
        armNP.setColor(_ARM_COLOR)
        armNP.setBillboardPointEye()
        armNP.setTransparency(TransparencyAttrib.MAlpha)
        self._armNP = armRoot

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

    def _startIdleBob(self):
        """Gentle plaza idle so the lead reads alive between greets."""
        self._stopIdleBob()
        if not bool(getattr(CampaignGlobals, 'OSWALD_PRESENCE_IDLE_BOB', True)):
            return
        body = self._bodyNP
        if body is None:
            return
        try:
            z0 = float(body.getZ())
            self._idleIval = Sequence(
                LerpPosInterval(body, 0.55, (0, 0, z0 + 0.06)),
                LerpPosInterval(body, 0.55, (0, 0, z0)),
                name='oswaldPresenceIdleBob',
            )
            self._idleIval.loop()
        except Exception:
            self._idleIval = None

    def _stopIdleBob(self):
        if self._idleIval is not None:
            try:
                self._idleIval.finish()
            except Exception:
                pass
            self._idleIval = None

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
        """Short greet interact — body wave + tip (once per zone visit).

        First-ever meet shows the once-ever first-meet tip and fires
        ``oswaldPresenceMet`` so the accept path can persist ``oswaldMet``.
        Later visits: static hub/street until ``oswaldCheered``, then
        progress-aware soft-next from unlock latch.
        """
        if self._greetedZone is not None and int(self._greetedZone) == int(
                zoneId):
            return
        self._greetedZone = int(zoneId)
        self._disarmInteract()
        self._clearPrompt()
        self._playGreetWave()
        firstMeet = not bool(self._oswaldMet)
        if firstMeet:
            tip = firstMeetTip()
        else:
            tip = greetTipForZone(
                zoneId,
                cheered=bool(self._oswaldCheered),
                softNextStreet=self._softNextStreet)
        self._showGreetTip(tip)
        try:
            messenger.send(  # noqa: F821
                metMsgName(), [int(zoneId), presenceLabel()])
        except Exception:
            pass

    def _onOswaldPresenceMet(self, zoneId=0, label=''):
        """Accept first-meet messenger — latch + AI-persist oswaldMet once."""
        if self._oswaldMet:
            return
        self._oswaldMet = True
        self._requestPersistMet()

    def _onOswaldMetSync(self, met=0):
        """Hydrate durable first-meet latch from AI setOswaldMet (relog)."""
        if int(met):
            self._oswaldMet = True

    def _requestPersistMet(self):
        """Ask AI to persist oswaldMet so first-meet tip stays once-ever."""
        try:
            pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        except Exception:
            pm = None
        if pm is not None and hasattr(pm, 'd_requestOswaldMet'):
            try:
                pm.d_requestOswaldMet()
            except Exception:
                pass

    def _onOswaldPresenceCheered(self, zoneId=0, label=''):
        """Accept reclaim-cheer messenger — latch + AI-persist oswaldCheered once.

        Live tip stays owned by ``playReclaimCheer``; this path retains the
        cheer-on-clear beat past session bounce and unlocks progress-aware
        plaza/street greet soft-next (trust→twist ladder).
        """
        if self._oswaldCheered:
            return
        self._oswaldCheered = True
        self._refreshSoftNextStreet()
        self._requestPersistCheered()

    def _onOswaldCheeredSync(self, cheered=0):
        """Hydrate durable first-cheer latch from AI setOswaldCheered (relog)."""
        if int(cheered):
            self._oswaldCheered = True
            self._refreshSoftNextStreet()

    def _requestPersistCheered(self):
        """Ask AI to persist oswaldCheered so cheer-on-clear survives bounce."""
        try:
            pm = getattr(base.cr, 'pollutionManager', None)  # noqa: F821
        except Exception:
            pm = None
        if pm is not None and hasattr(pm, 'd_requestOswaldCheered'):
            try:
                pm.d_requestOswaldCheered()
            except Exception:
                pass

    def _cheerDebounce(self, minGap=0.4):
        try:
            now = globalClock.getFrameTime()  # noqa: F821
        except Exception:
            return False
        if now - self._lastCheerT < float(minGap):
            return True
        self._lastCheerT = now
        return False

    def _onReclaimCheer(self, zoneId=None, *args):
        """Street clear / purity — Oswald body cheers (then still vanish on twist)."""
        if not cheerOnReclaim():
            return
        if self._betrayed or self._bodyNP is None:
            return
        if self._cheerDebounce():
            return
        self.playReclaimCheer(zoneId=zoneId, showTip=True)

    def playReclaimCheer(self, zoneId=None, showTip=True):
        """Public cheer beat for ReclaimCheer / director thin wire.

        Always body-bounces on clear. Tip uses the live cheer copy; fires
        ``oswaldPresenceCheered`` so the accept path can persist
        ``oswaldCheered`` beyond session bounce.
        """
        if self._betrayed or self._bodyNP is None:
            return False
        self._playCheerBounce()
        if showTip:
            self._showGreetTip(cheerTip())
        try:
            messenger.send(  # noqa: F821
                cheeredMsgName(), [
                    int(zoneId if zoneId is not None else (self._zoneId or 0)),
                    presenceLabel()])
        except Exception:
            pass
        return True

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
            arm = self._armNP
            parts = [
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
            ]
            if arm is not None:
                parts = [
                    Parallel(
                        LerpScaleInterval(
                            body, 0.10,
                            (baseScale[0] * 1.08, baseScale[1],
                             baseScale[2] * 1.12)),
                        LerpHprInterval(body, 0.10, (12, 0, 0)),
                        LerpHprInterval(arm, 0.10, (0, 0, 18)),
                    ),
                    Parallel(
                        LerpScaleInterval(body, 0.12, baseScale),
                        LerpHprInterval(body, 0.12, (0, 0, 0)),
                        LerpHprInterval(arm, 0.12, (0, 0, 0)),
                    ),
                    LerpHprInterval(body, 0.08, (-8, 0, 0)),
                    LerpHprInterval(body, 0.08, (0, 0, 0)),
                ]
            self._waveIval = Sequence(*parts, name='oswaldPresenceGreetWave')
            self._waveIval.start()
        except Exception:
            self._waveIval = None

    def _playCheerBounce(self):
        """Bigger rubber-hose cheer on street clear — arms up, hop, settle."""
        if self._cheerIval is not None:
            try:
                self._cheerIval.finish()
            except Exception:
                pass
            self._cheerIval = None
        body = self._bodyNP
        if body is None:
            return
        try:
            baseScale = body.getScale()
            arm = self._armNP
            hops = [
                Parallel(
                    LerpScaleInterval(
                        body, 0.10,
                        (baseScale[0] * 1.18, baseScale[1] * 1.05,
                         baseScale[2] * 0.88)),
                    LerpHprInterval(body, 0.10, (16, 0, 0)),
                ),
                Parallel(
                    LerpScaleInterval(
                        body, 0.14,
                        (baseScale[0] * 0.92, baseScale[1],
                         baseScale[2] * 1.22)),
                    LerpHprInterval(body, 0.14, (-14, 0, 0)),
                ),
                Parallel(
                    LerpScaleInterval(body, 0.16, baseScale),
                    LerpHprInterval(body, 0.16, (0, 0, 0)),
                ),
            ]
            if arm is not None:
                hops = [
                    Parallel(
                        LerpScaleInterval(
                            body, 0.10,
                            (baseScale[0] * 1.18, baseScale[1] * 1.05,
                             baseScale[2] * 0.88)),
                        LerpHprInterval(body, 0.10, (16, 0, 0)),
                        LerpHprInterval(arm, 0.10, (0, 0, 28)),
                    ),
                    Parallel(
                        LerpScaleInterval(
                            body, 0.14,
                            (baseScale[0] * 0.92, baseScale[1],
                             baseScale[2] * 1.22)),
                        LerpHprInterval(body, 0.14, (-14, 0, 0)),
                        LerpHprInterval(arm, 0.14, (0, 0, -12)),
                    ),
                    Parallel(
                        LerpScaleInterval(body, 0.16, baseScale),
                        LerpHprInterval(body, 0.16, (0, 0, 0)),
                        LerpHprInterval(arm, 0.16, (0, 0, 0)),
                    ),
                ]
            self._cheerIval = Sequence(*hops, name='oswaldPresenceReclaimCheer')
            self._cheerIval.start()
        except Exception:
            self._cheerIval = None

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
        # Cheer tips can be a beat shorter than greets.
        if tip == cheerTip():
            hold = max(1.0, float(getattr(
                CampaignGlobals, 'OSWALD_PRESENCE_CHEER_HOLD_SEC', 2.4)))
        elif tip == firstMeetTip():
            # First-meet trust beat holds a touch longer than zone greets.
            hold = max(hold, 3.6)
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
        self._stopIdleBob()
        if self._waveIval is not None:
            try:
                self._waveIval.pause()
            except Exception:
                pass
            self._waveIval = None
        if self._cheerIval is not None:
            try:
                self._cheerIval.finish()
            except Exception:
                pass
            self._cheerIval = None
        if self._rootNP is not None:
            try:
                self._rootNP.removeNode()
            except Exception:
                pass
            self._rootNP = None
        self._bodyNP = None
        self._armNP = None
        self._nametagNP = None
        self._markerPos = None


_client = None


def ensureOswaldPresenceClient():
    global _client
    if _client is None:
        _client = OswaldPresenceClient()
    return _client


def getOswaldPresenceClient():
    """Thin accessor for ReclaimCheer / director — may be None before ensure."""
    return _client


def refreshOswaldPresenceHub():
    """Thin hub re-arm for TTPlayground enter."""
    client = ensureOswaldPresenceClient()
    try:
        client.refreshHub()
    except Exception:
        pass
    return client


def playOswaldPresenceCheer(zoneId=None, showTip=True):
    """Thin reclaim cheer entry for ReclaimCheer / director."""
    client = ensureOswaldPresenceClient()
    try:
        return bool(client.playReclaimCheer(zoneId=zoneId, showTip=showTip))
    except Exception:
        return False


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
