"""Readable life bar for Overlord, Corrupted Oswald, and Elite/Ambush packs.

Thin aspect2d HUD driven by DistributedCorruptToon client setHp/setMaxHp.
Shows one active subject at a time (finale Overlord, betrayal chase, or
soft-lock-preferred Elite / Ambush rename). Rubber-hose Toontown
spiritual-sequel tone only (not cream FX deepen; no KH).
"""

from panda3d.core import CardMaker, TextNode, TransparencyAttrib

from toontown.corruption import CorruptionGlobals


# Module singleton — one readable life bar for the active boss/chase.
_hud = None
_ownerDoId = None


def _getHud():
    global _hud
    if _hud is None:
        _hud = BossHpBarHud()
    return _hud


def syncFromCorruptToon(toon):
    """Show/update/hide the bar from a live DistributedCorruptToon client."""
    global _ownerDoId
    if toon is None:
        return
    doId = getattr(toon, 'doId', None)
    archetype = int(getattr(toon, 'archetype', CorruptionGlobals.ARCHETYPE_INK))
    name = str(getattr(toon, 'name', '') or '')
    hp = int(getattr(toon, 'hp', 0) or 0)
    maxHp = int(getattr(toon, 'maxHp', 0) or 0)
    # Mirror DistributedCorruptToon.__finalePhaseLook: reclaim director first,
    # then Overlord name tokens when phase is still unset.
    finalePhase = 0
    try:
        reclaim = getattr(base.cr, 'reclaimDirector', None)  # noqa: F821
        if reclaim is not None:
            finalePhase = int(getattr(reclaim, 'finalePhase', 0) or 0)
    except Exception:
        finalePhase = 0
    finalePhase = CorruptionGlobals.resolveBossHpBarFinalePhase(
        finalePhase, name)

    subject = CorruptionGlobals.isBossOrChaseHpBarSubject(
        archetype, name=name, finalePhase=finalePhase)
    alive = hp > 0 and maxHp > 0
    if not subject or not alive:
        if _ownerDoId is not None and doId == _ownerDoId:
            hideBossHpBar()
        return

    hud = _getHud()
    _ownerDoId = doId
    hud.update(
        hp=hp,
        maxHp=maxHp,
        name=name,
        archetype=archetype,
        finalePhase=finalePhase,
    )


def releaseCorruptToon(toon):
    """Drop the bar when the owning boss/chase disables or dies."""
    global _ownerDoId
    if toon is None:
        return
    doId = getattr(toon, 'doId', None)
    if _ownerDoId is not None and doId == _ownerDoId:
        hideBossHpBar()


def hideBossHpBar():
    global _ownerDoId
    _ownerDoId = None
    if _hud is not None:
        _hud.hide()


def destroyBossHpBar():
    global _hud, _ownerDoId
    _ownerDoId = None
    if _hud is not None:
        _hud.destroy()
        _hud = None


class BossHpBarHud(object):
    """Horizontal life bar: empty = defeated, full = max HP."""

    def __init__(self):
        self._root = None
        self._rimNP = None
        self._trackNP = None
        self._fillNP = None
        self._labelNP = None
        self._pctNP = None
        self._hp = None
        self._maxHp = None

    def isShown(self):
        return self._root is not None and not self._root.isEmpty()

    def show(self):
        if self.isShown():
            return
        g = CorruptionGlobals
        halfW = g.BOSS_HP_BAR_WIDTH * 0.5
        halfH = g.BOSS_HP_BAR_HEIGHT * 0.5
        pad = g.BOSS_HP_BAR_RIM_PAD

        root = aspect2d.attachNewNode('boss-chase-hp-bar')  # noqa: F821
        root.setPos(*g.BOSS_HP_BAR_POS)
        root.setBin('fixed', g.BOSS_HP_BAR_BIN)
        root.setDepthTest(False)
        root.setDepthWrite(False)
        self._root = root

        rcm = CardMaker('boss-chase-hp-rim')
        rcm.setFrame(-halfW - pad, halfW + pad, -halfH - pad, halfH + pad)
        rim = root.attachNewNode(rcm.generate())
        rim.setTransparency(TransparencyAttrib.MAlpha)
        rim.setColor(*g.BOSS_HP_BAR_RIM_COLOR)
        rim.setBin('fixed', g.BOSS_HP_BAR_BIN - 1)
        self._rimNP = rim

        tcm = CardMaker('boss-chase-hp-track')
        tcm.setFrame(-halfW, halfW, -halfH, halfH)
        track = root.attachNewNode(tcm.generate())
        track.setTransparency(TransparencyAttrib.MAlpha)
        track.setColor(*g.BOSS_HP_BAR_TRACK_COLOR)
        self._trackNP = track

        fcm = CardMaker('boss-chase-hp-fill')
        fcm.setFrame(0.0, g.BOSS_HP_BAR_WIDTH, -halfH, halfH)
        fill = root.attachNewNode(fcm.generate())
        fill.setPos(-halfW, 0, 0)
        fill.setTransparency(TransparencyAttrib.MAlpha)
        fill.setColor(*g.BOSS_HP_BAR_FILL_OVERLORD_P1)
        fill.setScale(0.001, 1, 1)
        self._fillNP = fill

        ltn = TextNode('boss-chase-hp-label')
        ltn.setText(g.BOSS_HP_BAR_DEFAULT_OVERLORD_LABEL)
        ltn.setAlign(TextNode.ACenter)
        ltn.setTextColor(*g.BOSS_HP_BAR_LABEL_COLOR)
        ltn.setShadow(0.04, 0.04)
        ltn.setShadowColor(0, 0, 0, 0.8)
        label = root.attachNewNode(ltn)
        label.setScale(g.BOSS_HP_BAR_LABEL_SCALE)
        label.setPos(0, 0, g.BOSS_HP_BAR_LABEL_Z)
        self._labelNP = label

        ptn = TextNode('boss-chase-hp-pct')
        ptn.setText('100%')
        ptn.setAlign(TextNode.ACenter)
        ptn.setTextColor(*g.BOSS_HP_BAR_PCT_COLOR)
        ptn.setShadow(0.04, 0.04)
        ptn.setShadowColor(0, 0, 0, 0.75)
        pct = root.attachNewNode(ptn)
        pct.setScale(g.BOSS_HP_BAR_PCT_SCALE)
        pct.setPos(0, 0, g.BOSS_HP_BAR_PCT_Z)
        self._pctNP = pct

    def hide(self):
        if self._root is not None and not self._root.isEmpty():
            self._root.removeNode()
        self._root = None
        self._rimNP = None
        self._trackNP = None
        self._fillNP = None
        self._labelNP = None
        self._pctNP = None
        self._hp = None
        self._maxHp = None

    def destroy(self):
        self.hide()

    def update(self, hp, maxHp, name='', archetype=0, finalePhase=0):
        """Refresh fill / label from synced hp + subject identity."""
        if not self.isShown():
            self.show()

        ratio = CorruptionGlobals.bossHpBarRatio(hp, maxHp)
        self._hp = int(hp)
        self._maxHp = int(maxHp)

        fillColor = CorruptionGlobals.bossHpBarFillColor(
            archetype, finalePhase=finalePhase, name=name)
        rimColor = CorruptionGlobals.bossHpBarRimColor(
            archetype, finalePhase=finalePhase, name=name)
        label = CorruptionGlobals.bossHpBarLabel(
            name=name, archetype=archetype, finalePhase=finalePhase)

        if self._fillNP is not None and not self._fillNP.isEmpty():
            sx = max(0.001, float(ratio))
            self._fillNP.setScale(sx, 1, 1)
            self._fillNP.setColor(*fillColor)
        if self._rimNP is not None and not self._rimNP.isEmpty():
            self._rimNP.setColor(*rimColor)
        if self._labelNP is not None and not self._labelNP.isEmpty():
            self._labelNP.node().setText(label)
        if self._pctNP is not None and not self._pctNP.isEmpty():
            self._pctNP.node().setText('%.0f%%' % (ratio * 100.0))
