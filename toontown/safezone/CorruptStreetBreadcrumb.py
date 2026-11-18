"""Neighborhood-hub placemarkers for polluted reclaim streets.

World-space tip / signpost breadcrumbs on Toontown Central playground
tunnels that lead to Loopy Lane, Punchline Place, and Silly Street.
Players notice ink-stained streets from the hub without magic words.

After the appear hose-pop, placemarkers briefly pulse / cream-highlight
(#211), deepened with a juicier cream mid-settle + soft local cream
halo (#230), then cream rim deepen (#252: juicier peak/mid + soft mid
hold + micro rebound), then past #252 (#268), then past #268 (#277:
brighter/wider halo / longer mid hold / punchier rebound), then
deepened again past #277 (brighter/wider halo / longer mid hold /
punchier rebound) so discoverability reads punchier without KH branding
— distinct from fog edge cream rim deepen (#250), tunnel cream deepen
(#230 peak→mid→rest), #252 / #268 / #277 alone, birds-return wash
(#226 / #285), and crumb pip deepen (#258+). Separately, a short ink
crumb trail at the tunnel mouth pulses on a faster stagger (#216),
deepened with a juicier cream mid-settle + soft cream pip blot (#241),
then pip cream deepen (#258: juicier peak/mid + soft mid hold + micro
rebound), then past #258 (#270), then past #270 (#282: brighter/wider
pip / longer mid hold / punchier rebound), then deepened again past
#282 (brighter/wider pip / longer mid hold / punchier rebound) so
polluted streets read juicier from the playground side — distinct from
placemarker cream rim deepen (#252 / #268 / #277 + past-#277), fog
edge cream rim deepen (#250 / #295), #258 / #270 / #282 alone, tunnel
cream deepen (#230 / #290), and birds-return fullscreen wash
(#226 / #285).
A soft pollution fog edge veil also breathes at the playground-side
tunnel lip (#221 / #236), cream-rim deepened (#250: juicier peak/mid +
soft mid hold + micro rebound), then deepened again past #250
(brighter/wider rim / longer mid hold / punchier rebound) so polluted
borders read juicier — distinct from fog edge cream #236 / #250 alone,
birds-return cream deepen (#246 / #285), tunnel pulse cream rim
(#290), and placemarker/crumb cues.

When a polluted reclaim tunnel clears (or purityRestoreFx fires while
the hub is live), a brief birds-return cream wash pulses so the
playground feeling clean reads juicily beside PollutionStreetAudio
pure-street birds (#55) — see BirdsReturnCreamWashFx.

Reads PollutionManager + reclaim/campaign street tables (import only);
does not rewrite those packages. Soft-gate (#317+#320): locked campaign
acts do not get a full reclaim crumb — dim placemarkers keep explore
visible while the progression ladder reads from the hub. Client latch
tracks unlockedThrough via campaignActUnlocked (PlayEntry / purity
mirror) and campaignProgressSync (login rehydrate so crumbs undim
after relog without waiting for a live unlock). Rubber-hose Toontown
voice — no KH.
"""

from __future__ import annotations

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)
from direct.showbase.DirectObject import DirectObject
from panda3d.core import CardMaker, TextNode, TransparencyAttrib, Vec4

from toontown.toonbase import ToontownGlobals

notify = directNotify.newCategory('CorruptStreetBreadcrumb')

# Hub playground only — TTC is the explore → fight → reclaim launchpad.
_HUB_ZONE = ToontownGlobals.ToontownCentral

# Session latch for campaign act unlock (soft-gate parity with R).
# Raised by campaignActUnlocked and campaignProgressSync (login rehydrate).
# Default 0 = Loopy-only until unlock / sync.
_clientUnlockedThrough = 0
# Live hub breadcrumb instance (set by ensureCorruptStreetBreadcrumbs).
_activeBreadcrumb = None

# Placemarker float above tunnel mouth (world units).
_MARKER_Z = 4.5
_MARKER_SCALE = 1.35
# Quiet scale for locked-act dim placemarkers (no reclaim pulse juice).
_MARKER_SCALE_DIM = 1.05
# Soft rubber-hose pop when a polluted tunnel sign appears.
_POP_SQUASH = 0.72
_POP_STRETCH = 1.18
_POP_SETTLE_SEC = 0.28
# Brief attention pulse / cream highlight so reclaim tunnels read on the hub.
# Cream deepen (#230): warmer peak → soft mid settle + local cream halo.
# Cream rim deepen (#252): juicier halo peak/mid + mid hold + micro rebound.
# Past-#252 deepen (#268): brighter halo / longer mid hold / punchier rebound.
# Past-#268 deepen (#277): brighter/wider halo / longer mid hold / punchier rebound.
# Past-#277 deepen: brighter/wider halo / longer mid hold / punchier rebound —
# not fog rim #250; not crumb pip #258+; not birds #285; not #252 / #268 / #277 alone.
_PULSE_PEAK = 1.22
_PULSE_HALF_SEC = 0.16
_PULSE_BEATS = 2
_PULSE_GAP_SEC = 4.8
_PULSE_HIGHLIGHT = Vec4(1.0, 0.97, 0.38, 1.0)  # warmer sunny cream peak (past #277)
_PULSE_CREAM_MID = Vec4(1.0, 0.99, 0.86, 1.0)  # creamier soft settle before rest
_PULSE_CREAM_MID_SEC = 0.13  # longer linger than #277 0.12
_PULSE_REST = Vec4(1.0, 1.0, 1.0, 1.0)
# Soft local cream halo behind placemarker during notice pulse.
# Past-#277 deepen: juicier peak/mid + longer mid hold + punchier rebound
# settle — not fog rim #250 (slower/wider); not crumb pip #258+; not #277 alone.
_PULSE_HALO_NAME = 'corruptStreetPlacemarkerCreamHalo'
_PULSE_HALO_HALF_W = 3.15  # wider cream rim peeks past text (past #277 3.00)
_PULSE_HALO_HALF_H = 0.80
_PULSE_HALO_Z_OFF = -0.08
_PULSE_HALO_SCALE_PEAK = 1.54  # juicier than #277 1.50; < crumb pip 1.72
_PULSE_HALO_PEAK = Vec4(1.0, 0.99, 0.88, 0.54)  # brighter sunny cream rim
_PULSE_HALO_MID = Vec4(1.0, 0.98, 0.80, 0.34)
_PULSE_HALO_REST = Vec4(1.0, 0.97, 0.82, 0.0)
_PULSE_HALO_HOLD_SEC = 0.096  # longer than #277 0.092; still < fog rim (past #250)
_PULSE_HALO_REBOUND_SCALE = 1.16  # punchier than #277 1.14; < crumb pip 1.20
_PULSE_HALO_REBOUND_SEC = 0.076  # slightly longer than #277 0.072; < fog rebound
_PULSE_HALO_REBOUND_PEAK = Vec4(1.0, 0.99, 0.86, 0.24)  # warmer cream flash

# Tunnel-mouth ink crumb trail — distinct from overhead placemarker pulse.
# Cream deepen (#241): warmer peak → soft mid settle + local cream pip blot.
# Cream pip deepen (#258): juicier pip peak/mid + mid hold + micro rebound.
# Past-#258 deepen (#270): brighter/wider pip / longer mid hold / punchier rebound.
# Past-#270 deepen (#282): brighter/wider pip / longer mid hold / punchier rebound.
# Past-#282 deepen: brighter/wider pip / longer mid hold / punchier rebound
# — not placemarker halo rim #252+; not fog rim #250/#295; not tunnel #290;
# not birds #285; not #258 / #270 / #282 alone.
_CRUMB_GLYPH = '•'
_CRUMB_COUNT = 3
_CRUMB_Z = 1.05
_CRUMB_Y0 = -2.4
_CRUMB_Y_STEP = 1.05
_CRUMB_SCALE = 0.55
_CRUMB_PULSE_PEAK = 1.56  # juicier snap past #282 1.54; still < 1.6
_CRUMB_PULSE_HALF_SEC = 0.11
_CRUMB_PULSE_GAP_SEC = 3.1
_CRUMB_STAGGER_SEC = 0.13
_CRUMB_FG = Vec4(0.22, 0.10, 0.28, 0.95)
_CRUMB_SHADOW = Vec4(1.0, 0.92, 0.72, 0.75)
_CRUMB_HIGHLIGHT = Vec4(1.0, 0.93, 0.26, 1.0)  # warmer sunny cream peak (past #282)
_CRUMB_CREAM_MID = Vec4(1.0, 0.97, 0.76, 1.0)  # creamier soft settle before rest
_CRUMB_CREAM_MID_SEC = 0.11  # longer linger than #282 0.10; still < placemarker 0.13
_CRUMB_REST = Vec4(1.0, 1.0, 1.0, 1.0)
# Soft cream pip blot under each crumb during the trail pulse.
# Past-#282 deepen: juicier peak/mid + longer mid hold + punchier rebound
# settle — not placemarker halo #252+ / #268+ / #277+; not fog rim #250/#295;
# not tunnel #290; not birds #285; not #282 alone.
_CRUMB_PIP_NAME = 'corruptStreetCrumbCreamPip'
_CRUMB_PIP_HALF_W = 0.54  # wider trail blot past #282 0.50 — still << halo / fog
_CRUMB_PIP_HALF_H = 0.34
_CRUMB_PIP_Z_OFF = -0.06
_CRUMB_PIP_SCALE_PEAK = 1.72  # punchier than #282 1.68 / halo 1.54 / fog rim
_CRUMB_PIP_PEAK = Vec4(1.0, 0.99, 0.78, 0.56)  # brighter sunny cream pip (past #282)
_CRUMB_PIP_MID = Vec4(1.0, 0.96, 0.70, 0.34)
_CRUMB_PIP_REST = Vec4(1.0, 0.96, 0.78, 0.0)
_CRUMB_PIP_HOLD_SEC = 0.08  # longer than #282 0.07; still < halo 0.096 / fog rim
_CRUMB_PIP_REBOUND_SCALE = 1.20  # punchier than #282 1.18 / halo 1.16 / fog rim
_CRUMB_PIP_REBOUND_SEC = 0.068  # slightly longer than #282 0.062; still < halo 0.076
_CRUMB_PIP_REBOUND_PEAK = Vec4(1.0, 0.98, 0.76, 0.22)  # warmer cream flash

# Playground-edge pollution fog breath — opacity/billow (not placemarker
# scale snap). Slower / softer than #211 / #216 so corruption presence
# reads at the tunnel lip. Cream deepen (#236): ink peak → cream mid
# settle + soft cream rim bloom. Rim deepen (#250): juicier peak/mid +
# mid hold + micro rebound. Past-#250 deepen: brighter/wider rim /
# longer mid hold / punchier rebound — not tunnel pulse #290; not
# placemarker halo #277+; not crumb pip #270+; not birds wash #285.
_FOG_NAME = 'playgroundPollutionFogEdge'
_FOG_Y = -0.55
_FOG_Z = 0.42
_FOG_HALF_W = 3.2
_FOG_HALF_H = 0.95
_FOG_SCALE = 1.0
_FOG_BILLOW = 1.14  # slightly juicier billow past #250 cream deepen
_FOG_PULSE_HALF_SEC = 0.46
_FOG_PULSE_GAP_SEC = 6.2
_FOG_REST = Vec4(0.16, 0.10, 0.20, 0.16)
_FOG_PEAK = Vec4(0.14, 0.08, 0.17, 0.40)  # slightly warmer / juicier ink peak
_FOG_CREAM_MID = Vec4(0.66, 0.52, 0.36, 0.30)  # creamier ink settle (past #250)
_FOG_CREAM_MID_SEC = 0.16  # longer linger than #250 0.14 — fog stays soft
# Soft cream rim under the ink fog during the edge breath.
# Past-#250 deepen: juicier peak/mid + longer mid hold + punchier rebound
# settle — not birds rising chirp/sky halo #246/#285; not tunnel #290;
# not #250 alone (peak 0.38 / scale 1.22 / hold 0.10 / rebound 1.06).
_FOG_CREAM_RIM_NAME = 'playgroundPollutionFogCreamRim'
_FOG_CREAM_RIM_HALF_W = 3.70  # wider cream rim peeks past ink fog (past #250 3.55)
_FOG_CREAM_RIM_HALF_H = 1.22
_FOG_CREAM_RIM_Y_OFF = 0.04
_FOG_CREAM_RIM_Z_OFF = -0.04
_FOG_CREAM_RIM_SCALE_PEAK = 1.28  # juicier than #250 1.22; < halo 1.54 / pip 1.72
_FOG_CREAM_RIM_PEAK = Vec4(1.0, 0.99, 0.88, 0.44)  # brighter sunny cream rim
_FOG_CREAM_RIM_MID = Vec4(1.0, 0.97, 0.80, 0.26)
_FOG_CREAM_RIM_REST = Vec4(1.0, 0.97, 0.82, 0.0)
_FOG_CREAM_RIM_HOLD_SEC = 0.12  # longer than #250 0.10; still > halo 0.096
_FOG_CREAM_RIM_REBOUND_SCALE = 1.10  # punchier than #250 1.06; < halo 1.16
_FOG_CREAM_RIM_REBOUND_SEC = 0.092  # longer than #250 0.08; still > halo 0.076
_FOG_CREAM_RIM_REBOUND_PEAK = Vec4(1.0, 0.98, 0.82, 0.14)  # warmer cream flash

# Short rubber-hose signpost copy (world placemarker — keep punchy).
_STREET_COPY = {
    ToontownGlobals.LoopyLane: 'Ink stains Loopy — hop in & reclaim!',
    ToontownGlobals.PunchlinePlace: 'Sludge jokes on Punchline — reclaim!',
    ToontownGlobals.SillyStreet: 'Silly Street ink-deep — reclaim with Oswald!',
}

# Ink-on-cream placemarker colors (readable against sunny TTC tunnels).
_TEXT_FG = Vec4(0.18, 0.12, 0.22, 1.0)
_TEXT_SHADOW = Vec4(1.0, 0.94, 0.78, 0.92)
# Locked-act dim placemarker — muted ink, no sunny reclaim pulse.
_TEXT_FG_DIM = Vec4(0.28, 0.24, 0.30, 0.48)
_TEXT_SHADOW_DIM = Vec4(0.92, 0.90, 0.86, 0.35)


def getClientUnlockedThrough():
    """Session campaign unlock cursor used by hub breadcrumb soft-gate."""
    return int(_clientUnlockedThrough)


def setClientUnlockedThrough(unlockedThrough):
    """Raise (never lower) the session unlock latch. Returns new value."""
    global _clientUnlockedThrough
    try:
        unlocked = max(0, int(unlockedThrough))
    except (TypeError, ValueError):
        unlocked = 0
    if unlocked > _clientUnlockedThrough:
        _clientUnlockedThrough = unlocked
    return int(_clientUnlockedThrough)


def noteCampaignActUnlocked(nextIndex, zoneId=None):
    """Latch unlock + refresh live hub crumbs (campaignActUnlocked consumer).

    zoneId is accepted for messenger parity with CampaignDirectorAI send
    args; refresh uses the latch, not the zone alone.
    """
    setClientUnlockedThrough(nextIndex)
    crumb = _activeBreadcrumb
    if crumb is not None and getattr(crumb, '_active', False):
        try:
            crumb.refresh()
        except Exception:
            notify.debug('breadcrumb refresh after act unlock failed')
    return getClientUnlockedThrough()


def resetClientUnlockedThrough():
    """Test / teardown helper — clears the session unlock latch."""
    global _clientUnlockedThrough
    _clientUnlockedThrough = 0


def _streetActUnlocked(zoneId, unlockedThrough):
    """True when soft-gate allows a full reclaim breadcrumb for zoneId."""
    try:
        from toontown.reclaim import ReclaimGlobals
        return bool(ReclaimGlobals.streetPackUnlocked(
            int(zoneId), unlockedThrough))
    except Exception:
        # Fail-open so hub discoverability survives missing reclaim tables.
        return True


def _streetLooksPolluted(zoneId, pollutionByZone, seedPollution, pure=0.0):
    """Pollution/seed sample — shared by full vs dim breadcrumb helpers."""
    zoneId = int(zoneId)
    pure = float(pure)
    if zoneId in pollutionByZone:
        try:
            return float(pollutionByZone[zoneId]) > pure
        except (TypeError, ValueError):
            return False
    try:
        return float(seedPollution) > pure
    except (TypeError, ValueError):
        return False


def reclaimStreetEntries():
    """[(zoneId, streetName, placemarkerText, seedPollution), ...] for hub tips.

    Prefers CampaignGlobals.ACTS, falls back to ReclaimGlobals.STREET_PACKS.
    Pure helper — safe for AST / headless import checks without Panda geom.
    """
    entries = []
    seen = set()
    try:
        from toontown.campaign import CampaignGlobals
        for act in getattr(CampaignGlobals, 'ACTS', ()) or ():
            zoneId = int(act.get('zoneId', 0) or 0)
            if zoneId <= 0 or zoneId in seen:
                continue
            name = act.get('name') or ('Street %s' % zoneId)
            seed = float(act.get('seedPollution', 0.0) or 0.0)
            text = _STREET_COPY.get(zoneId) or (
                'Corruption stains %s — hop the tunnel & reclaim!' % name)
            entries.append((zoneId, name, text, seed))
            seen.add(zoneId)
    except Exception:
        pass
    if entries:
        return entries
    try:
        from toontown.reclaim import ReclaimGlobals
        packs = getattr(ReclaimGlobals, 'STREET_PACKS', {}) or {}
        for zoneId, pack in packs.items():
            zoneId = int(zoneId)
            if zoneId in seen:
                continue
            name = (pack or {}).get('name') or ('Street %s' % zoneId)
            seed = float((pack or {}).get('seedPollution', 0.0) or 0.0)
            text = _STREET_COPY.get(zoneId) or (
                'Corruption stains %s — hop the tunnel & reclaim!' % name)
            entries.append((zoneId, name, text, seed))
            seen.add(zoneId)
    except Exception:
        pass
    return entries


def streetNeedsBreadcrumb(zoneId, pollutionByZone, seedPollution, pure=0.0,
                           unlockedThrough=None):
    """True when a reclaim street needs a full hub reclaim breadcrumb.

    Known PollutionManager samples win; unknown zones fall back to seed
    pollution so Loopy / Punchline / Silly stay discoverable before visit.

    When unlockedThrough is provided, locked campaign acts (soft-gate
    parity with street-pack R) do not get a full reclaim invite — use
    streetBreadcrumbDimmed for the muted locked cue. When omitted, only
    pollution/seed is checked (headless helper backward compatible).
    """
    if not _streetLooksPolluted(
            zoneId, pollutionByZone, seedPollution, pure=pure):
        return False
    if unlockedThrough is None:
        return True
    return _streetActUnlocked(zoneId, unlockedThrough)


def streetBreadcrumbDimmed(zoneId, pollutionByZone, seedPollution, pure=0.0,
                           unlockedThrough=0):
    """True when polluted but act-locked — muted hub cue, not reclaim invite.

    Keeps explore discoverability for Punchline / Silly tunnels while the
    progression ladder dims locked reclaim invitations from TTC.
    """
    if not _streetLooksPolluted(
            zoneId, pollutionByZone, seedPollution, pure=pure):
        return False
    return not _streetActUnlocked(zoneId, unlockedThrough)


def placemarkerPulseParams():
    """Pure timing / scale for hub tunnel placemarker notice pulse.

    Headless-safe — no Panda geom. Used by AST / unit checks for the
    explore → fight attention cue on polluted reclaim tunnels.
    """
    return {
        'peak': float(_PULSE_PEAK),
        'halfSec': float(_PULSE_HALF_SEC),
        'beats': int(_PULSE_BEATS),
        'gapSec': float(_PULSE_GAP_SEC),
        'baseScale': float(_MARKER_SCALE),
    }


def placemarkerPulseCreamParams():
    """Pure cream-deepen params for hub tunnel placemarker notice pulse.

    Juicier cream mid-settle + local halo bloom on the #211 scale pulse
    (#230), cream rim deepen (#252: juicier peak/mid + mid hold + micro
    rebound), past-#252 deepen (#268), past-#268 deepen (#277), then
    past-#277 deepen (brighter/wider halo / longer mid hold / punchier
    rebound). Distinct from fog edge cream rim deepen (#250 slower/wider
    tunnel-lip), crumb pip deepen (#258+), BirdsReturnCreamWashFx
    fullscreen wash (#226 / #285), and the original #230 peak→mid→rest
    halo (no hold/rebound). Headless-safe — no Panda geom.
    """
    hi = _PULSE_HIGHLIGHT
    mid = _PULSE_CREAM_MID
    haloPeak = _PULSE_HALO_PEAK
    haloMid = _PULSE_HALO_MID
    rebound = _PULSE_HALO_REBOUND_PEAK
    return {
        'highlight': (float(hi[0]), float(hi[1]), float(hi[2]), float(hi[3])),
        'creamMid': (float(mid[0]), float(mid[1]), float(mid[2]), float(mid[3])),
        'creamMidSec': float(_PULSE_CREAM_MID_SEC),
        'haloPeakAlpha': float(haloPeak[3]),
        'haloMidAlpha': float(haloMid[3]),
        'haloScalePeak': float(_PULSE_HALO_SCALE_PEAK),
        'haloHalfW': float(_PULSE_HALO_HALF_W),
        'haloHalfH': float(_PULSE_HALO_HALF_H),
        'haloHoldSec': float(_PULSE_HALO_HOLD_SEC),
        'haloReboundScale': float(_PULSE_HALO_REBOUND_SCALE),
        'haloReboundSec': float(_PULSE_HALO_REBOUND_SEC),
        'haloReboundAlpha': float(rebound[3]),
        # Local placemarker cream rim — not fog rim / fullscreen wash.
        'haloRimRebound': True,
        'fullscreenWash': False,
        'fogRim': False,
        'birdsChirpFlecks': False,
    }


def streetBreadcrumbPulseParams():
    """Pure timing / scale for tunnel-mouth ink crumb trail pulse.

    Distinct from placemarkerPulseParams (#211): faster gap, single-beat
    stagger along the crumb trail so polluted streets read from the
    playground approach. Headless-safe — no Panda geom.
    """
    return {
        'peak': float(_CRUMB_PULSE_PEAK),
        'halfSec': float(_CRUMB_PULSE_HALF_SEC),
        'gapSec': float(_CRUMB_PULSE_GAP_SEC),
        'staggerSec': float(_CRUMB_STAGGER_SEC),
        'count': int(_CRUMB_COUNT),
        'baseScale': float(_CRUMB_SCALE),
    }


def streetBreadcrumbPulseCreamParams():
    """Pure cream-deepen params for tunnel-mouth ink crumb trail pulse.

    Juicier cream mid-settle + soft cream pip blot under each crumb
    (#241 deepen), then juicier pip peak/mid + mid hold + micro rebound
    (#258), then past #258 (#270), then past #270 (#282), then deepened
    again past #282 (brighter/wider pip / longer mid hold / punchier
    rebound). Distinct from placemarkerPulseCreamParams (#252 + past
    halo rim), playgroundFogEdgeCreamParams (#250 / #295 fog rim),
    tunnel pulse cream rim (#290), #258 / #270 / #282 alone, #241
    peak→mid→rest alone, and BirdsReturnCreamWashFx fullscreen wash
    (#226 / #285). Headless-safe — no Panda geom.
    """
    hi = _CRUMB_HIGHLIGHT
    mid = _CRUMB_CREAM_MID
    pipPeak = _CRUMB_PIP_PEAK
    pipMid = _CRUMB_PIP_MID
    rebound = _CRUMB_PIP_REBOUND_PEAK
    return {
        'highlight': (float(hi[0]), float(hi[1]), float(hi[2]), float(hi[3])),
        'creamMid': (float(mid[0]), float(mid[1]), float(mid[2]), float(mid[3])),
        'creamMidSec': float(_CRUMB_CREAM_MID_SEC),
        'pipPeakAlpha': float(pipPeak[3]),
        'pipMidAlpha': float(pipMid[3]),
        'pipScalePeak': float(_CRUMB_PIP_SCALE_PEAK),
        'pipHalfW': float(_CRUMB_PIP_HALF_W),
        'pipHalfH': float(_CRUMB_PIP_HALF_H),
        'pipHoldSec': float(_CRUMB_PIP_HOLD_SEC),
        'pipReboundScale': float(_CRUMB_PIP_REBOUND_SCALE),
        'pipReboundSec': float(_CRUMB_PIP_REBOUND_SEC),
        'pipReboundAlpha': float(rebound[3]),
        # Trail-local cream pip blot — not placemarker halo / fog rim / wash.
        'localPip': True,
        'pipRimRebound': True,
        'fullscreenWash': False,
        'placemarkerHalo': False,
        'fogRim': False,
    }


def playgroundFogEdgePulseParams():
    """Pure timing / alpha for playground pollution fog edge breath.

    Distinct from placemarkerPulseParams (#211) and
    streetBreadcrumbPulseParams (#216): slower gap, opacity+billow (no
    placemarker cream scale snap) so corruption presence reads at the
    tunnel lip before reclaim entry. Headless-safe — no Panda geom.
    """
    return {
        'halfSec': float(_FOG_PULSE_HALF_SEC),
        'gapSec': float(_FOG_PULSE_GAP_SEC),
        'restAlpha': float(_FOG_REST[3]),
        'peakAlpha': float(_FOG_PEAK[3]),
        'billow': float(_FOG_BILLOW),
        'baseScale': float(_FOG_SCALE),
    }


def playgroundFogEdgeCreamParams():
    """Pure cream-deepen params for playground pollution fog edge breath.

    Cream mid-settle on the ink fog veil + juicier cream rim bloom at
    the tunnel lip (#236 deepen, rim deepen #250, then past-#250
    brighter/wider rim / longer mid hold / punchier rebound). Distinct
    from placemarkerPulseCreamParams / tunnel pulse cream rim (#290 —
    snappier hold/rebound), BirdsReturnCreamWashFx fullscreen wash +
    rising chirp (#246 / #226 / #285), crumb pip deepen (#258+), and
    the original #236 peak→mid→rest rim (no hold / rebound).
    Headless-safe — no Panda geom.
    """
    mid = _FOG_CREAM_MID
    rimPeak = _FOG_CREAM_RIM_PEAK
    rimMid = _FOG_CREAM_RIM_MID
    rebound = _FOG_CREAM_RIM_REBOUND_PEAK
    return {
        'creamMid': (float(mid[0]), float(mid[1]), float(mid[2]), float(mid[3])),
        'creamMidSec': float(_FOG_CREAM_MID_SEC),
        'creamMidAlpha': float(mid[3]),
        'rimPeakAlpha': float(rimPeak[3]),
        'rimMidAlpha': float(rimMid[3]),
        'rimScalePeak': float(_FOG_CREAM_RIM_SCALE_PEAK),
        'rimHalfW': float(_FOG_CREAM_RIM_HALF_W),
        'rimHalfH': float(_FOG_CREAM_RIM_HALF_H),
        'rimHoldSec': float(_FOG_CREAM_RIM_HOLD_SEC),
        'rimReboundScale': float(_FOG_CREAM_RIM_REBOUND_SCALE),
        'rimReboundSec': float(_FOG_CREAM_RIM_REBOUND_SEC),
        'rimReboundAlpha': float(rebound[3]),
        # Tunnel-lip world-space cream rim — not placemarker halo / wash.
        'localRim': True,
        'rimRebound': True,
        'fullscreenWash': False,
        'placemarkerHalo': False,
        'birdsChirpFlecks': False,
    }


def _pollutionPure():
    try:
        from toontown.corruption import CorruptionGlobals
        return float(getattr(CorruptionGlobals, 'POLLUTION_PURE', 0.0))
    except Exception:
        return 0.0


class CorruptStreetBreadcrumb(DirectObject):
    """Attach / refresh polluted-street placemarkers on hub playground tunnels."""

    notify = notify

    def __init__(self, playground):
        DirectObject.__init__(self)
        self._playground = playground
        self._markers = {}  # zoneId -> NodePath
        self._markerMode = {}  # zoneId -> 'full' | 'dim'
        self._pulseHalos = {}  # zoneId -> NodePath (cream deepen halo)
        self._crumbTrails = {}  # zoneId -> [NodePath, ...]
        self._crumbCreamPips = {}  # zoneId -> [NodePath, ...] (crumb cream pips)
        self._fogEdges = {}  # zoneId -> NodePath
        self._fogCreamRims = {}  # zoneId -> NodePath (fog edge cream rim)
        self._popIvals = {}
        self._pulseIvals = {}
        self._crumbPulseIvals = {}
        self._fogPulseIvals = {}
        self._lastPollutionLevels = {}  # zoneId -> last known level
        self._active = False

    def start(self):
        if self._active:
            return
        self._active = True
        self.accept('pollutionChanged', self._onPollutionChanged)
        self.accept('purityRestoreFx', self._onPurityRestore)
        # AI / PlayEntry purity mirror — refresh crumbs when acts unlock.
        self.accept('campaignActUnlocked', self._onCampaignActUnlocked)
        # Login / persist push — raise latch so dim crumbs undim after relog.
        try:
            from toontown.campaign import CampaignGlobals
            syncMsg = getattr(
                CampaignGlobals, 'CAMPAIGN_PROGRESS_SYNC_MSG',
                'campaignProgressSync')
        except Exception:
            syncMsg = 'campaignProgressSync'
        self.accept(syncMsg, self._onCampaignProgressSync)
        self.accept('exitPlayground', self.stop)
        self._requestStreetPollution()
        self.refresh()

    def stop(self):
        if not self._active and not self._markers:
            return
        self._active = False
        self.ignore('pollutionChanged')
        self.ignore('purityRestoreFx')
        self.ignore('campaignActUnlocked')
        try:
            from toontown.campaign import CampaignGlobals
            syncMsg = getattr(
                CampaignGlobals, 'CAMPAIGN_PROGRESS_SYNC_MSG',
                'campaignProgressSync')
        except Exception:
            syncMsg = 'campaignProgressSync'
        self.ignore(syncMsg)
        self.ignore('exitPlayground')
        self._clearMarkers()
        self._clearBirdsReturnCreamWash()

    def destroy(self):
        self.stop()
        self.ignoreAll()
        self._playground = None

    def _cueBirdsReturnCreamWash(self):
        """Soft cream wash when playground pollution clears / birds return."""
        try:
            from toontown.safezone.BirdsReturnCreamWashFx import (
                playBirdsReturnCreamWash)
            playBirdsReturnCreamWash()
        except Exception:
            self.notify.debug('birds return cream wash unavailable')

    def _clearBirdsReturnCreamWash(self):
        try:
            from toontown.safezone.BirdsReturnCreamWashFx import (
                clearBirdsReturnCreamWash)
            clearBirdsReturnCreamWash()
        except Exception:
            pass

    def _requestStreetPollution(self):
        """Ask PollutionManager for Loopy / Punchline / Silly samples."""
        pm = getattr(getattr(base, 'cr', None), 'pollutionManager', None)  # noqa: F821
        if pm is None or not hasattr(pm, 'd_requestZonePollution'):
            return
        for zoneId, _name, _text, _seed in reclaimStreetEntries():
            try:
                pm.d_requestZonePollution(int(zoneId))
            except Exception:
                self.notify.debug('pollution request failed for %s' % zoneId)

    def _pollutionMap(self):
        pm = getattr(getattr(base, 'cr', None), 'pollutionManager', None)  # noqa: F821
        if pm is None:
            return {}
        return dict(getattr(pm, 'zonePollution', {}) or {})

    def _onPollutionChanged(self, zoneId=None, level=None):
        if not self._active:
            return
        # Only refresh when a reclaim street (or unknown) updates.
        reclaimZones = {z for z, _n, _t, _s in reclaimStreetEntries()}
        if zoneId is not None and int(zoneId) not in reclaimZones:
            return
        prevLevel = None
        if zoneId is not None:
            zid = int(zoneId)
            prevLevel = self._lastPollutionLevels.get(zid)
            if level is not None:
                try:
                    self._lastPollutionLevels[zid] = float(level)
                except (TypeError, ValueError):
                    pass
        hadMarker = (
            zoneId is not None and int(zoneId) in self._markers)
        self.refresh()
        # Pollution clear → cream wash beside pure-street birds return (#55).
        # Debounce lives in BirdsReturnCreamWashFx.
        clearedMarker = (
            hadMarker and zoneId is not None
            and int(zoneId) not in self._markers)
        flippedPure = False
        if prevLevel is not None and level is not None:
            try:
                from toontown.safezone.BirdsReturnCreamWashFx import (
                    shouldPlayBirdsReturnCreamWash)
                flippedPure = shouldPlayBirdsReturnCreamWash(
                    prevLevel, level)
            except Exception:
                flippedPure = False
        if clearedMarker or flippedPure:
            self._cueBirdsReturnCreamWash()

    def _onPurityRestore(self, *args):
        if not self._active:
            return
        hadAny = bool(self._markers)
        self.refresh()
        # Reclaim complete / purity restore while hub live — birds return cue.
        if hadAny or args:
            self._cueBirdsReturnCreamWash()

    def _onCampaignActUnlocked(self, nextIndex=0, zoneId=0):
        """Promote dim → full crumbs when the campaign soft-gate advances."""
        if not self._active:
            # Still latch so the next hub enter sees the unlock.
            setClientUnlockedThrough(nextIndex)
            return
        noteCampaignActUnlocked(nextIndex, zoneId)

    def _onCampaignProgressSync(
            self, unlockedThrough=0, state=0, chaseCleared=0, reclaimCount=0):
        """Rehydrate unlock latch from AI progress so hub crumbs undim on relog.

        state / chaseCleared / reclaimCount accepted for campaignProgressSync
        arity (tip / presence / power paths); crumbs only need unlock cursor.
        """
        if not self._active:
            setClientUnlockedThrough(unlockedThrough)
            return
        noteCampaignActUnlocked(unlockedThrough)

    def refresh(self):
        if not self._active:
            return
        playground = self._playground
        if playground is None:
            return
        hoodId = getattr(getattr(playground, 'loader', None), 'hood', None)
        hoodId = getattr(hoodId, 'id', None)
        if hoodId is not None and int(hoodId) != int(_HUB_ZONE):
            self._clearMarkers()
            return
        pollution = self._pollutionMap()
        pure = _pollutionPure()
        unlocked = getClientUnlockedThrough()
        wanted = {}  # zoneId -> (name, text, mode)
        for zoneId, name, text, seed in reclaimStreetEntries():
            zid = int(zoneId)
            if streetNeedsBreadcrumb(
                    zid, pollution, seed, pure=pure,
                    unlockedThrough=unlocked):
                wanted[zid] = (name, text, 'full')
            elif streetBreadcrumbDimmed(
                    zid, pollution, seed, pure=pure,
                    unlockedThrough=unlocked):
                wanted[zid] = (name, text, 'dim')
        # Drop cleared / no-longer-wanted streets (caller may cue birds wash).
        for zoneId in list(self._markers.keys()):
            if zoneId not in wanted:
                self._removeMarker(zoneId)
        # Ensure placemarkers; rebuild when soft-gate mode flips dim ↔ full.
        for zoneId, (name, text, mode) in wanted.items():
            if (zoneId not in self._markers
                    or self._markerMode.get(zoneId) != mode):
                if zoneId in self._markers:
                    self._removeMarker(zoneId)
                self._attachMarker(zoneId, name, text, mode=mode)

    def _findLinkTunnel(self, zoneId):
        playground = self._playground
        if playground is None:
            return None
        nodeList = getattr(getattr(playground, 'loader', None), 'nodeList', None)
        if not nodeList:
            return None
        # linktunnel_<hood>_<zone> — HoodMgr parses parts[1]/parts[2].
        zoneId = int(zoneId)
        for root in nodeList:
            try:
                matches = root.findAllMatches('**/linktunnel*')
            except Exception:
                continue
            for i in range(matches.getNumPaths()):
                link = matches.getPath(i)
                parts = (link.getName() or '').split('_')
                if len(parts) < 3:
                    continue
                try:
                    if int(parts[2]) == zoneId:
                        return link
                except ValueError:
                    continue
        return None

    def _attachMarker(self, zoneId, streetName, text, mode='full'):
        link = self._findLinkTunnel(zoneId)
        if link is None or link.isEmpty():
            self.notify.debug(
                'no linktunnel for polluted street %s (%s)' % (zoneId, streetName))
            return
        mode = 'dim' if mode == 'dim' else 'full'
        # Avoid stacking if DNA already has a leftover marker name.
        existing = link.find('**/corruptStreetBreadcrumb')
        if not existing.isEmpty():
            existing.removeNode()
        tn = TextNode('corruptStreetBreadcrumbText')
        try:
            tn.setFont(ToontownGlobals.getSignFont())
        except Exception:
            pass
        tn.setText(text)
        tn.setAlign(TextNode.ACenter)
        if mode == 'dim':
            tn.setTextColor(_TEXT_FG_DIM)
            try:
                tn.setShadow(0.03, 0.03)
                tn.setShadowColor(_TEXT_SHADOW_DIM)
            except Exception:
                pass
        else:
            tn.setTextColor(_TEXT_FG)
            try:
                tn.setShadow(0.04, 0.04)
                tn.setShadowColor(_TEXT_SHADOW)
            except Exception:
                pass
        np = link.attachNewNode(tn)
        np.setName('corruptStreetBreadcrumb')
        np.setPos(0, 0, _MARKER_Z)
        if mode == 'dim':
            np.setScale(_MARKER_SCALE_DIM)
            try:
                np.setTransparency(TransparencyAttrib.MAlpha)
                np.setColorScale(1, 1, 1, 0.55)
            except Exception:
                pass
        else:
            np.setScale(_MARKER_SCALE)
        np.setBillboardPointEye()
        np.setDepthWrite(0)
        np.setBin('fixed', 40)
        self._markers[int(zoneId)] = np
        self._markerMode[int(zoneId)] = mode
        if mode == 'dim':
            # Locked act: muted placemarker only — no reclaim pulse juice.
            self.notify.debug(
                'dim placemarker on tunnel → %s (%s)' % (streetName, zoneId))
            return
        halo = self._attachPulseCreamHalo(link, zoneId)
        crumbs = self._attachCrumbTrail(link, zoneId)
        fog = self._attachFogEdge(link, zoneId)
        rim = self._attachFogCreamRim(link, zoneId)
        self._playPop(zoneId, np, crumbs, fog, halo=halo, rim=rim)
        self.notify.debug(
            'placemarker on tunnel → %s (%s)' % (streetName, zoneId))

    def _attachPulseCreamHalo(self, link, zoneId):
        """Soft local cream halo behind placemarker — deepen #211 cream cue."""
        zoneId = int(zoneId)
        old = self._pulseHalos.pop(zoneId, None)
        if old is not None:
            try:
                old.removeNode()
            except Exception:
                pass
        leftover = link.find('**/%s' % _PULSE_HALO_NAME)
        if not leftover.isEmpty():
            leftover.removeNode()
        halo = None
        try:
            cm = CardMaker(_PULSE_HALO_NAME)
            cm.setFrame(
                -_PULSE_HALO_HALF_W, _PULSE_HALO_HALF_W,
                -_PULSE_HALO_HALF_H, _PULSE_HALO_HALF_H)
            halo = link.attachNewNode(cm.generate())
            halo.setName(_PULSE_HALO_NAME)
            halo.setTransparency(TransparencyAttrib.MAlpha)
            # Sit just behind the placemarker text (bin under fixed/40).
            halo.setPos(0, 0, _MARKER_Z + _PULSE_HALO_Z_OFF)
            halo.setScale(1.0)
            halo.setColorScale(_PULSE_HALO_REST)
            halo.setDepthWrite(0)
            halo.setBin('fixed', 38)  # under placemarker (40), over fog (37)
            halo.setBillboardPointEye()
        except Exception:
            self.notify.debug(
                'placemarker cream halo unavailable for zone %s' % zoneId)
            halo = None
        if halo is not None:
            self._pulseHalos[zoneId] = halo
        return halo

    def _attachFogEdge(self, link, zoneId):
        """Soft ink fog veil at the playground-side tunnel lip."""
        zoneId = int(zoneId)
        self._stopFogPulse(zoneId)
        old = self._fogEdges.pop(zoneId, None)
        if old is not None:
            try:
                old.removeNode()
            except Exception:
                pass
        leftover = link.find('**/%s' % _FOG_NAME)
        if not leftover.isEmpty():
            leftover.removeNode()
        fog = None
        try:
            cm = CardMaker(_FOG_NAME)
            cm.setFrame(-_FOG_HALF_W, _FOG_HALF_W, 0.0, _FOG_HALF_H * 2.0)
            fog = link.attachNewNode(cm.generate())
            fog.setName(_FOG_NAME)
            fog.setTransparency(TransparencyAttrib.MAlpha)
            fog.setPos(0, _FOG_Y, _FOG_Z)
            fog.setScale(_FOG_SCALE)
            fog.setColorScale(_FOG_REST)
            fog.setDepthWrite(0)
            fog.setBin('fixed', 37)  # under crumb (39) + placemarker (40)
            fog.setBillboardPointEye()
        except Exception:
            self.notify.debug('fog edge unavailable for zone %s' % zoneId)
            fog = None
        if fog is not None:
            self._fogEdges[zoneId] = fog
        return fog

    def _attachFogCreamRim(self, link, zoneId):
        """Soft cream rim under ink fog — deepen rim juice past #250."""
        zoneId = int(zoneId)
        old = self._fogCreamRims.pop(zoneId, None)
        if old is not None:
            try:
                old.removeNode()
            except Exception:
                pass
        leftover = link.find('**/%s' % _FOG_CREAM_RIM_NAME)
        if not leftover.isEmpty():
            leftover.removeNode()
        rim = None
        try:
            cm = CardMaker(_FOG_CREAM_RIM_NAME)
            cm.setFrame(
                -_FOG_CREAM_RIM_HALF_W, _FOG_CREAM_RIM_HALF_W,
                0.0, _FOG_CREAM_RIM_HALF_H * 2.0)
            rim = link.attachNewNode(cm.generate())
            rim.setName(_FOG_CREAM_RIM_NAME)
            rim.setTransparency(TransparencyAttrib.MAlpha)
            # Sit just behind / under the ink fog so cream peeks as a rim.
            rim.setPos(0, _FOG_Y + _FOG_CREAM_RIM_Y_OFF, _FOG_Z + _FOG_CREAM_RIM_Z_OFF)
            rim.setScale(1.0)
            rim.setColorScale(_FOG_CREAM_RIM_REST)
            rim.setDepthWrite(0)
            rim.setBin('fixed', 36)  # under ink fog (37)
            rim.setBillboardPointEye()
        except Exception:
            self.notify.debug(
                'fog cream rim unavailable for zone %s' % zoneId)
            rim = None
        if rim is not None:
            self._fogCreamRims[zoneId] = rim
        return rim

    def _attachCrumbTrail(self, link, zoneId):
        """Ink crumb dots at the tunnel mouth — playground-side breadcrumb."""
        zoneId = int(zoneId)
        self._stopCrumbPulse(zoneId)
        oldTrail = self._crumbTrails.pop(zoneId, None)
        if oldTrail:
            for crumb in oldTrail:
                try:
                    crumb.removeNode()
                except Exception:
                    pass
        oldPips = self._crumbCreamPips.pop(zoneId, None)
        if oldPips:
            for pip in oldPips:
                try:
                    pip.removeNode()
                except Exception:
                    pass
        # Drop leftover DNA crumbs if a prior session left them.
        leftover = link.find('**/corruptStreetCrumbTrail')
        if not leftover.isEmpty():
            leftover.removeNode()
        root = link.attachNewNode('corruptStreetCrumbTrail')
        crumbs = []
        pips = []
        for i in range(max(1, int(_CRUMB_COUNT))):
            y = _CRUMB_Y0 + (i * _CRUMB_Y_STEP)
            # Soft cream pip blot under the ink crumb (cream deepen).
            pip = self._makeCrumbCreamPip(root, i, y)
            if pip is not None:
                pips.append(pip)
            tn = TextNode('corruptStreetCrumbText-%s' % i)
            try:
                tn.setFont(ToontownGlobals.getSignFont())
            except Exception:
                pass
            tn.setText(_CRUMB_GLYPH)
            tn.setAlign(TextNode.ACenter)
            tn.setTextColor(_CRUMB_FG)
            try:
                tn.setShadow(0.03, 0.03)
                tn.setShadowColor(_CRUMB_SHADOW)
            except Exception:
                pass
            crumb = root.attachNewNode(tn)
            crumb.setName('corruptStreetCrumb')
            crumb.setPos(0, y, _CRUMB_Z)
            crumb.setScale(_CRUMB_SCALE)
            crumb.setBillboardPointEye()
            crumb.setDepthWrite(0)
            crumb.setBin('fixed', 39)
            crumbs.append(crumb)
        self._crumbTrails[zoneId] = crumbs
        self._crumbCreamPips[zoneId] = pips
        return crumbs

    def _makeCrumbCreamPip(self, root, index, y):
        """Soft cream pip blot under one crumb — deepen #216 cream cue."""
        pip = None
        try:
            cm = CardMaker('%s-%s' % (_CRUMB_PIP_NAME, index))
            cm.setFrame(
                -_CRUMB_PIP_HALF_W, _CRUMB_PIP_HALF_W,
                -_CRUMB_PIP_HALF_H, _CRUMB_PIP_HALF_H)
            pip = root.attachNewNode(cm.generate())
            pip.setName(_CRUMB_PIP_NAME)
            pip.setTransparency(TransparencyAttrib.MAlpha)
            # Sit just under the ink crumb so cream peeks as a tiny blot.
            pip.setPos(0, y, _CRUMB_Z + _CRUMB_PIP_Z_OFF)
            pip.setScale(1.0)
            pip.setColorScale(_CRUMB_PIP_REST)
            pip.setDepthWrite(0)
            pip.setBin('fixed', 38)  # under crumb (39), over fog (37)
            pip.setBillboardPointEye()
        except Exception:
            self.notify.debug('crumb cream pip unavailable at index %s' % index)
            pip = None
        return pip

    def _playPop(self, zoneId, np, crumbs=None, fog=None, halo=None, rim=None):
        self._stopPulse(zoneId)
        self._stopCrumbPulse(zoneId)
        self._stopFogPulse(zoneId)
        old = self._popIvals.pop(zoneId, None)
        if old is not None:
            try:
                old.finish()
            except Exception:
                pass
        if halo is None:
            halo = self._pulseHalos.get(int(zoneId))
        if rim is None:
            rim = self._fogCreamRims.get(int(zoneId))
        baseScale = _MARKER_SCALE
        ival = Sequence(
            LerpScaleInterval(
                np, _POP_SETTLE_SEC * 0.35,
                baseScale * _POP_SQUASH,
                startScale=baseScale * 0.05),
            LerpScaleInterval(
                np, _POP_SETTLE_SEC * 0.35,
                baseScale * _POP_STRETCH,
                startScale=baseScale * _POP_SQUASH),
            LerpScaleInterval(
                np, _POP_SETTLE_SEC * 0.30,
                baseScale,
                startScale=baseScale * _POP_STRETCH),
            # Placemarker + crumb cream deepen + fog-edge cream pulses.
            Func(self._startPulseLoop, zoneId, np, halo),
            Func(self._startCrumbPulseLoop, zoneId, crumbs or ()),
            Func(self._startFogPulseLoop, zoneId, fog, rim),
        )
        self._popIvals[zoneId] = ival
        try:
            ival.start()
        except Exception:
            np.setScale(baseScale)
            self._startPulseLoop(zoneId, np, halo)
            self._startCrumbPulseLoop(zoneId, crumbs or ())
            self._startFogPulseLoop(zoneId, fog, rim)

    def _buildNoticePulseIval(self, np, halo=None):
        """One brief rubber-hose scale + deepened cream highlight pulse."""
        baseScale = _MARKER_SCALE
        half = max(0.01, float(_PULSE_HALF_SEC))
        midSec = max(0.01, float(_PULSE_CREAM_MID_SEC))
        peak = baseScale * float(_PULSE_PEAK)
        restCs = _PULSE_REST
        hiCs = _PULSE_HIGHLIGHT
        midCs = _PULSE_CREAM_MID
        # Scale still snaps out/in; cream settles peak → mid → rest (juicier).
        scaleOut = half
        scaleIn = half + midSec
        beats = []
        for _ in range(max(1, int(_PULSE_BEATS))):
            parts = [
                Sequence(
                    LerpScaleInterval(
                        np, scaleOut, peak, startScale=baseScale,
                        blendType='easeOut'),
                    LerpScaleInterval(
                        np, scaleIn, baseScale, startScale=peak,
                        blendType='easeIn'),
                ),
                Sequence(
                    LerpColorScaleInterval(
                        np, half, hiCs, startColorScale=restCs,
                        blendType='easeOut'),
                    LerpColorScaleInterval(
                        np, midSec, midCs, startColorScale=hiCs,
                        blendType='easeInOut'),
                    LerpColorScaleInterval(
                        np, half, restCs, startColorScale=midCs,
                        blendType='easeIn'),
                ),
            ]
            if halo is not None:
                parts.append(self._buildPulseCreamHaloIval(halo, half, midSec))
            beats.append(Parallel(*parts))
        return Sequence(*beats)

    def _buildPulseCreamHaloIval(self, halo, half, midSec):
        """Local cream halo bloom — juicier peak → mid hold → rest → rebound.

        Past-#277 deepen (brighter/wider peak / longer hold / punchier rebound).
        Distinct from #230 peak→mid→rest (no hold/rebound), #252 / #268 / #277
        alone, fog rim #250 (slower/wider tunnel-lip), crumb pip #258+, and
        birds #246 / #285 rising chirp/sky halo.
        """
        peakScale = float(_PULSE_HALO_SCALE_PEAK)
        holdSec = max(0.04, float(_PULSE_HALO_HOLD_SEC))
        reboundSec = max(0.04, float(_PULSE_HALO_REBOUND_SEC))
        reboundScale = float(_PULSE_HALO_REBOUND_SCALE)
        settleSec = max(0.04, float(midSec))
        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    halo, half, _PULSE_HALO_PEAK,
                    startColorScale=_PULSE_HALO_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    halo, settleSec, _PULSE_HALO_MID,
                    startColorScale=_PULSE_HALO_PEAK, blendType='easeInOut'),
                # Soft mid linger so the sunny cream rim reads before fade.
                LerpColorScaleInterval(
                    halo, holdSec, _PULSE_HALO_MID,
                    startColorScale=_PULSE_HALO_MID, blendType='easeInOut'),
                LerpColorScaleInterval(
                    halo, half, _PULSE_HALO_REST,
                    startColorScale=_PULSE_HALO_MID, blendType='easeIn'),
                # Micro cream rebound flash — rim deepen residual (not #250).
                LerpColorScaleInterval(
                    halo, reboundSec * 0.45, _PULSE_HALO_REBOUND_PEAK,
                    startColorScale=_PULSE_HALO_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    halo, reboundSec * 0.55, _PULSE_HALO_REST,
                    startColorScale=_PULSE_HALO_REBOUND_PEAK,
                    blendType='easeIn'),
            ),
            Sequence(
                LerpScaleInterval(
                    halo, half, peakScale, startScale=1.0,
                    blendType='easeOut'),
                LerpScaleInterval(
                    halo, settleSec + holdSec, 1.0, startScale=peakScale,
                    blendType='easeIn'),
                Wait(half),  # color fade to rest; hold scale at 1.0
                LerpScaleInterval(
                    halo, reboundSec * 0.45, reboundScale, startScale=1.0,
                    blendType='easeOut'),
                LerpScaleInterval(
                    halo, reboundSec * 0.55, 1.0, startScale=reboundScale,
                    blendType='easeIn'),
            ),
        )

    def _startPulseLoop(self, zoneId, np, halo=None):
        """Sparse brief pulses while the polluted placemarker stays up."""
        zoneId = int(zoneId)
        if not self._active or self._markers.get(zoneId) is not np:
            return
        if np is None:
            return
        try:
            if np.isEmpty():
                return
        except Exception:
            return
        if halo is None:
            halo = self._pulseHalos.get(zoneId)
        self._stopPulse(zoneId)
        try:
            np.setColorScale(_PULSE_REST)
            np.setScale(_MARKER_SCALE)
        except Exception:
            pass
        if halo is not None:
            try:
                halo.setColorScale(_PULSE_HALO_REST)
                halo.setScale(1.0)
            except Exception:
                pass
        gap = max(0.5, float(_PULSE_GAP_SEC))
        loop = Sequence(
            self._buildNoticePulseIval(np, halo),
            Wait(gap),
        )
        self._pulseIvals[zoneId] = loop
        try:
            loop.loop()
        except Exception:
            self._pulseIvals.pop(zoneId, None)
            try:
                np.setScale(_MARKER_SCALE)
                np.setColorScale(_PULSE_REST)
            except Exception:
                pass
            if halo is not None:
                try:
                    halo.setColorScale(_PULSE_HALO_REST)
                    halo.setScale(1.0)
                except Exception:
                    pass

    def _stopPulse(self, zoneId):
        zoneId = int(zoneId)
        ival = self._pulseIvals.pop(zoneId, None)
        if ival is not None:
            try:
                ival.finish()
            except Exception:
                try:
                    ival.pause()
                except Exception:
                    pass
        halo = self._pulseHalos.get(zoneId)
        if halo is not None:
            try:
                halo.setColorScale(_PULSE_HALO_REST)
                halo.setScale(1.0)
            except Exception:
                pass

    def _buildCrumbPulseIval(self, crumb, pip=None):
        """One brief scale + deepened cream beat on a single trail crumb."""
        baseScale = _CRUMB_SCALE
        half = max(0.01, float(_CRUMB_PULSE_HALF_SEC))
        midSec = max(0.01, float(_CRUMB_CREAM_MID_SEC))
        peak = baseScale * float(_CRUMB_PULSE_PEAK)
        # Scale still snaps out/in; cream settles peak → mid → rest (juicier).
        scaleOut = half
        scaleIn = half + midSec
        parts = [
            Sequence(
                LerpScaleInterval(
                    crumb, scaleOut, peak, startScale=baseScale,
                    blendType='easeOut'),
                LerpScaleInterval(
                    crumb, scaleIn, baseScale, startScale=peak,
                    blendType='easeIn'),
            ),
            Sequence(
                LerpColorScaleInterval(
                    crumb, half, _CRUMB_HIGHLIGHT,
                    startColorScale=_CRUMB_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    crumb, midSec, _CRUMB_CREAM_MID,
                    startColorScale=_CRUMB_HIGHLIGHT, blendType='easeInOut'),
                LerpColorScaleInterval(
                    crumb, half, _CRUMB_REST,
                    startColorScale=_CRUMB_CREAM_MID, blendType='easeIn'),
            ),
        ]
        if pip is not None:
            parts.append(self._buildCrumbCreamPipIval(pip, half, midSec))
        return Parallel(*parts)

    def _buildCrumbCreamPipIval(self, pip, half, midSec):
        """Trail cream pip bloom — juicier peak → mid hold → rest → rebound.

        Past-#258 deepen (brighter/wider pip + longer hold + punchier
        rebound). Distinct from #241 peak→mid→rest (no hold/rebound),
        #258 pip deepen alone, placemarker halo rim #252+, and fog rim
        #250.
        """
        peakScale = float(_CRUMB_PIP_SCALE_PEAK)
        holdSec = max(0.03, float(_CRUMB_PIP_HOLD_SEC))
        reboundSec = max(0.03, float(_CRUMB_PIP_REBOUND_SEC))
        reboundScale = float(_CRUMB_PIP_REBOUND_SCALE)
        # Settle mid window uses crumb cream midSec; pip then holds + rebounds.
        settleSec = max(0.03, float(midSec))
        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    pip, half, _CRUMB_PIP_PEAK,
                    startColorScale=_CRUMB_PIP_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    pip, settleSec, _CRUMB_PIP_MID,
                    startColorScale=_CRUMB_PIP_PEAK, blendType='easeInOut'),
                # Soft mid linger so the sunny pip blot reads before fade.
                LerpColorScaleInterval(
                    pip, holdSec, _CRUMB_PIP_MID,
                    startColorScale=_CRUMB_PIP_MID, blendType='easeInOut'),
                LerpColorScaleInterval(
                    pip, half, _CRUMB_PIP_REST,
                    startColorScale=_CRUMB_PIP_MID, blendType='easeIn'),
                # Micro cream rebound flash — pip deepen residual (not #252).
                LerpColorScaleInterval(
                    pip, reboundSec * 0.45, _CRUMB_PIP_REBOUND_PEAK,
                    startColorScale=_CRUMB_PIP_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    pip, reboundSec * 0.55, _CRUMB_PIP_REST,
                    startColorScale=_CRUMB_PIP_REBOUND_PEAK,
                    blendType='easeIn'),
            ),
            Sequence(
                LerpScaleInterval(
                    pip, half, peakScale, startScale=1.0,
                    blendType='easeOut'),
                LerpScaleInterval(
                    pip, settleSec + holdSec, 1.0, startScale=peakScale,
                    blendType='easeIn'),
                Wait(half),  # color fade to rest; hold scale at 1.0
                LerpScaleInterval(
                    pip, reboundSec * 0.45, reboundScale, startScale=1.0,
                    blendType='easeOut'),
                LerpScaleInterval(
                    pip, reboundSec * 0.55, 1.0, startScale=reboundScale,
                    blendType='easeIn'),
            ),
        )

    def _startCrumbPulseLoop(self, zoneId, crumbs=None):
        """Staggered crumb-trail cream pulse — faster / distinct from placemarker."""
        zoneId = int(zoneId)
        # Always pulse the live trail for this zone (Func may pass a snapshot).
        crumbs = self._crumbTrails.get(zoneId) or []
        pips = self._crumbCreamPips.get(zoneId) or []
        if not self._active or not crumbs:
            return
        alive = []
        for crumb in crumbs:
            try:
                if crumb is not None and not crumb.isEmpty():
                    alive.append(crumb)
            except Exception:
                continue
        if not alive:
            return
        alivePips = []
        for pip in pips:
            try:
                if pip is not None and not pip.isEmpty():
                    alivePips.append(pip)
            except Exception:
                continue
        self._stopCrumbPulse(zoneId)
        for crumb in alive:
            try:
                crumb.setColorScale(_CRUMB_REST)
                crumb.setScale(_CRUMB_SCALE)
            except Exception:
                pass
        for pip in alivePips:
            try:
                pip.setColorScale(_CRUMB_PIP_REST)
                pip.setScale(1.0)
            except Exception:
                pass
        stagger = max(0.0, float(_CRUMB_STAGGER_SEC))
        gap = max(0.4, float(_CRUMB_PULSE_GAP_SEC))
        # Overlapping chase into the tunnel — not the overhead placemarker loop.
        parts = []
        for i, crumb in enumerate(alive):
            pip = alivePips[i] if i < len(alivePips) else None
            parts.append(Sequence(
                Wait(stagger * i),
                self._buildCrumbPulseIval(crumb, pip),
            ))
        loop = Sequence(Parallel(*parts), Wait(gap))
        self._crumbPulseIvals[zoneId] = loop
        try:
            loop.loop()
        except Exception:
            self._crumbPulseIvals.pop(zoneId, None)
            for crumb in alive:
                try:
                    crumb.setScale(_CRUMB_SCALE)
                    crumb.setColorScale(_CRUMB_REST)
                except Exception:
                    pass
            for pip in alivePips:
                try:
                    pip.setColorScale(_CRUMB_PIP_REST)
                    pip.setScale(1.0)
                except Exception:
                    pass

    def _stopCrumbPulse(self, zoneId):
        zoneId = int(zoneId)
        ival = self._crumbPulseIvals.pop(zoneId, None)
        if ival is not None:
            try:
                ival.finish()
            except Exception:
                try:
                    ival.pause()
                except Exception:
                    pass
        pips = self._crumbCreamPips.get(zoneId) or []
        for pip in pips:
            try:
                pip.setColorScale(_CRUMB_PIP_REST)
                pip.setScale(1.0)
            except Exception:
                pass

    def _buildFogPulseIval(self, fog, rim=None):
        """One soft opacity + billow breath with cream mid-settle / rim."""
        half = max(0.05, float(_FOG_PULSE_HALF_SEC))
        midSec = max(0.04, float(_FOG_CREAM_MID_SEC))
        baseScale = float(_FOG_SCALE)
        peakScale = baseScale * float(_FOG_BILLOW)
        # Billow out on peak; settle through cream mid window then rest.
        billowOut = half
        billowIn = half + midSec
        parts = [
            Sequence(
                LerpColorScaleInterval(
                    fog, half, _FOG_PEAK, startColorScale=_FOG_REST,
                    blendType='easeInOut'),
                LerpColorScaleInterval(
                    fog, midSec, _FOG_CREAM_MID, startColorScale=_FOG_PEAK,
                    blendType='easeInOut'),
                LerpColorScaleInterval(
                    fog, half, _FOG_REST, startColorScale=_FOG_CREAM_MID,
                    blendType='easeInOut'),
            ),
            Sequence(
                LerpScaleInterval(
                    fog, billowOut, peakScale, startScale=baseScale,
                    blendType='easeInOut'),
                LerpScaleInterval(
                    fog, billowIn, baseScale, startScale=peakScale,
                    blendType='easeInOut'),
            ),
        ]
        if rim is not None:
            parts.append(self._buildFogCreamRimIval(rim, half, midSec))
        return Parallel(*parts)

    def _buildFogCreamRimIval(self, rim, half, midSec):
        """Tunnel-lip cream rim bloom — juicier peak → mid hold → rest → rebound.

        Past-#250 deepen (brighter/wider peak / longer hold / punchier
        rebound). Distinct from #236 peak→mid→rest (no hold/rebound),
        #250 alone, birds #246 / #285 rising chirp/sky halo, tunnel
        pulse cream rim #290, and placemarker/crumb snappier rim deepen.
        """
        peakScale = float(_FOG_CREAM_RIM_SCALE_PEAK)
        holdSec = max(0.04, float(_FOG_CREAM_RIM_HOLD_SEC))
        reboundSec = max(0.04, float(_FOG_CREAM_RIM_REBOUND_SEC))
        reboundScale = float(_FOG_CREAM_RIM_REBOUND_SCALE)
        # Settle mid window uses fog cream midSec; rim then holds + rebounds.
        settleSec = max(0.04, float(midSec))
        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    rim, half, _FOG_CREAM_RIM_PEAK,
                    startColorScale=_FOG_CREAM_RIM_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    rim, settleSec, _FOG_CREAM_RIM_MID,
                    startColorScale=_FOG_CREAM_RIM_PEAK, blendType='easeInOut'),
                # Soft mid linger so the sunny rim reads before fade.
                LerpColorScaleInterval(
                    rim, holdSec, _FOG_CREAM_RIM_MID,
                    startColorScale=_FOG_CREAM_RIM_MID, blendType='easeInOut'),
                LerpColorScaleInterval(
                    rim, half, _FOG_CREAM_RIM_REST,
                    startColorScale=_FOG_CREAM_RIM_MID, blendType='easeIn'),
                # Micro cream rebound flash — rim deepen residual (not #246).
                LerpColorScaleInterval(
                    rim, reboundSec * 0.45, _FOG_CREAM_RIM_REBOUND_PEAK,
                    startColorScale=_FOG_CREAM_RIM_REST, blendType='easeOut'),
                LerpColorScaleInterval(
                    rim, reboundSec * 0.55, _FOG_CREAM_RIM_REST,
                    startColorScale=_FOG_CREAM_RIM_REBOUND_PEAK,
                    blendType='easeIn'),
            ),
            Sequence(
                LerpScaleInterval(
                    rim, half, peakScale, startScale=1.0,
                    blendType='easeOut'),
                LerpScaleInterval(
                    rim, settleSec + holdSec, 1.0, startScale=peakScale,
                    blendType='easeIn'),
                Wait(half),  # color fade to rest; hold scale at 1.0
                LerpScaleInterval(
                    rim, reboundSec * 0.45, reboundScale, startScale=1.0,
                    blendType='easeOut'),
                LerpScaleInterval(
                    rim, reboundSec * 0.55, 1.0, startScale=reboundScale,
                    blendType='easeIn'),
            ),
        )

    def _startFogPulseLoop(self, zoneId, fog=None, rim=None):
        """Slow fog-edge cream breath — distinct from placemarker + crumb."""
        zoneId = int(zoneId)
        fog = self._fogEdges.get(zoneId) if fog is None else fog
        # Prefer the live fog edge for this zone (Func may pass a snapshot).
        live = self._fogEdges.get(zoneId)
        if live is not None:
            fog = live
        if rim is None:
            rim = self._fogCreamRims.get(zoneId)
        liveRim = self._fogCreamRims.get(zoneId)
        if liveRim is not None:
            rim = liveRim
        if not self._active or fog is None:
            return
        try:
            if fog.isEmpty():
                return
        except Exception:
            return
        self._stopFogPulse(zoneId)
        try:
            fog.setColorScale(_FOG_REST)
            fog.setScale(_FOG_SCALE)
        except Exception:
            pass
        if rim is not None:
            try:
                rim.setColorScale(_FOG_CREAM_RIM_REST)
                rim.setScale(1.0)
            except Exception:
                pass
        gap = max(0.8, float(_FOG_PULSE_GAP_SEC))
        loop = Sequence(self._buildFogPulseIval(fog, rim), Wait(gap))
        self._fogPulseIvals[zoneId] = loop
        try:
            loop.loop()
        except Exception:
            self._fogPulseIvals.pop(zoneId, None)
            try:
                fog.setColorScale(_FOG_REST)
                fog.setScale(_FOG_SCALE)
            except Exception:
                pass
            if rim is not None:
                try:
                    rim.setColorScale(_FOG_CREAM_RIM_REST)
                    rim.setScale(1.0)
                except Exception:
                    pass

    def _stopFogPulse(self, zoneId):
        zoneId = int(zoneId)
        ival = self._fogPulseIvals.pop(zoneId, None)
        if ival is not None:
            try:
                ival.finish()
            except Exception:
                try:
                    ival.pause()
                except Exception:
                    pass
        rim = self._fogCreamRims.get(zoneId)
        if rim is not None:
            try:
                rim.setColorScale(_FOG_CREAM_RIM_REST)
                rim.setScale(1.0)
            except Exception:
                pass

    def _removeMarker(self, zoneId):
        zoneId = int(zoneId)
        self._markerMode.pop(zoneId, None)
        self._stopPulse(zoneId)
        self._stopCrumbPulse(zoneId)
        self._stopFogPulse(zoneId)
        ival = self._popIvals.pop(zoneId, None)
        if ival is not None:
            try:
                ival.finish()
            except Exception:
                pass
        halo = self._pulseHalos.pop(zoneId, None)
        if halo is not None:
            try:
                halo.removeNode()
            except Exception:
                pass
        fog = self._fogEdges.pop(zoneId, None)
        if fog is not None:
            try:
                fog.removeNode()
            except Exception:
                pass
        rim = self._fogCreamRims.pop(zoneId, None)
        if rim is not None:
            try:
                rim.removeNode()
            except Exception:
                pass
        # Pop pip list so trail-root remove covers them; fall back if needed.
        pips = self._crumbCreamPips.pop(zoneId, None)
        trail = self._crumbTrails.pop(zoneId, None)
        if trail:
            # Remove trail root (parent of crumbs + cream pips) when present.
            root = None
            try:
                root = trail[0].getParent()
            except Exception:
                root = None
            if root is not None:
                try:
                    if not root.isEmpty() and root.getName() == 'corruptStreetCrumbTrail':
                        root.removeNode()
                        trail = None
                        pips = None
                except Exception:
                    pass
            if trail:
                for crumb in trail:
                    try:
                        crumb.removeNode()
                    except Exception:
                        pass
            if pips:
                for pip in pips:
                    try:
                        pip.removeNode()
                    except Exception:
                        pass
        elif pips:
            for pip in pips:
                try:
                    pip.removeNode()
                except Exception:
                    pass
        np = self._markers.pop(zoneId, None)
        if np is not None:
            try:
                np.removeNode()
            except Exception:
                pass

    def _clearMarkers(self):
        for zoneId in list(self._markers.keys()):
            self._removeMarker(zoneId)


def ensureCorruptStreetBreadcrumbs(playground):
    """Start (or refresh) hub tunnel placemarkers for the given playground."""
    global _activeBreadcrumb
    if playground is None:
        return None
    if _activeBreadcrumb is not None:
        try:
            _activeBreadcrumb.destroy()
        except Exception:
            pass
        _activeBreadcrumb = None
    crumb = CorruptStreetBreadcrumb(playground)
    crumb.start()
    _activeBreadcrumb = crumb
    return crumb


def stopCorruptStreetBreadcrumbs():
    global _activeBreadcrumb
    if _activeBreadcrumb is not None:
        try:
            _activeBreadcrumb.destroy()
        except Exception:
            pass
        _activeBreadcrumb = None
