"""Short rubber-hose ink crown / silhouette flash on Ink Overlord telegraphs.

World-space CardMaker juice for finale phase wind-ups only — a readable crown
silhouette pops above the boss head so P1 magenta / P2 crimson telegraphs scan
as Overlord, not a street Smudge. Wired from
DistributedCorruptToon.announceAttackTelegraph when a finale phase look is
active. Toontown spiritual sequel — no keyblades / no KH branding.
"""

from panda3d.core import CardMaker, Point3, TransparencyAttrib, Vec3, Vec4

from direct.interval.IntervalGlobal import (
    Func,
    LerpColorScaleInterval,
    LerpScaleInterval,
    Parallel,
    Sequence,
    Wait,
)

from toontown.corruption import CorruptionGlobals


def overlordCrownLook(finaleLook=None, phase=1):
    """Resolve crown palette / motion; phase charge colors tint the flash."""
    look = dict(CorruptionGlobals.OVERLORD_TELEGRAPH_CROWN_LOOK)
    try:
        phaseIndex = max(1, int(phase))
    except (TypeError, ValueError):
        phaseIndex = 1
    # Slightly hotter / taller crown on unleashed so P2 still reads at a glance.
    if phaseIndex >= 2:
        look['peakAlpha'] = float(look.get('peakAlpha', 0.95)) * 1.02
        look['lift'] = float(look.get('lift', 3.35)) + 0.25
        look['scale'] = float(look.get('scale', 1.0)) * 1.12
    if finaleLook:
        charge = finaleLook.get('telegraphCharge')
        if charge and len(charge) >= 3:
            # Ink-black body with phase-tinted rim so magenta vs crimson sticks.
            rim = (
                min(1.35, charge[0] * 0.55),
                min(1.35, charge[1] * 0.55),
                min(1.35, charge[2] * 0.55),
                1.0,
            )
            look['rimColor'] = rim
            look['flashColor'] = (
                min(1.45, charge[0] * 0.7),
                min(1.45, charge[1] * 0.7),
                min(1.45, charge[2] * 0.7),
                1.0,
            )
    return look


class OverlordTelegraphCrown(object):
    """Owns the brief ink crown silhouette flash above the Overlord."""

    def __init__(self):
        self._ival = None
        self._root = None

    def play(self, pos, finaleLook=None, phase=1, parent=None):
        """Spawn crown flash at `pos` (render space). Returns Sequence or None."""
        self.clear()
        look = overlordCrownLook(finaleLook=finaleLook, phase=phase)
        parentNP = parent
        if parentNP is None:
            try:
                parentNP = render  # noqa: F821
            except Exception:
                return None
        try:
            origin = Point3(
                pos[0], pos[1], pos[2] + float(look['lift']))
        except Exception:
            origin = Point3(0, 0, float(look['lift']))

        root = self._buildCrown(parentNP, origin, look)
        if root is None:
            return None
        self._root = root

        ival = self._buildFlashInterval(root, look)
        if ival is None:
            self.clear()
            return None
        self._ival = Sequence(
            ival,
            Func(self.clear),
            name='overlordTelegraphCrownFlash',
        )
        self._ival.start()
        return self._ival

    def clear(self):
        if self._ival is not None:
            try:
                self._ival.pause()
            except Exception:
                pass
            self._ival = None
        root = self._root
        self._root = None
        if root is not None:
            try:
                if not root.isEmpty():
                    root.removeNode()
            except Exception:
                pass

    def _buildCrown(self, parentNP, origin, look):
        """Rubber-hose ink crown + tiny boss head silhouette (CardMaker pieces).

        Reads as a cartoon crown flash above the Overlord — band, three spikes,
        drip tip, and a round head blob so the telegraph silhouette scans as
        boss wind-up. No KH props.
        """
        try:
            root = parentNP.attachNewNode('overlord-telegraph-crown')
            root.setPos(origin)
            root.setBillboardPointEye()
            root.setTransparency(TransparencyAttrib.MAlpha)
            root.setColorScale(1, 1, 1, 0)
            root.setBin('fixed', int(look.get('binSort', 44)))
            root.setDepthWrite(False)
            root.setScale(float(look.get('scale', 1.0)))

            body = look.get('bodyColor', (0.06, 0.02, 0.08, 1.0))
            rim = look.get('rimColor', (0.85, 0.25, 0.95, 1.0))

            # Local-space pieces (world units before root scale).
            # Head blob first (behind), then crown band / spikes / drip.
            pieces = (
                # Boss head silhouette under the crown
                ('head', 0.0, -0.55, 0.42, 0.36, body),
                # Crown band
                ('band', 0.0, -0.08, 0.58, 0.14, body),
                # Left spike
                ('spike-l', -0.38, 0.28, 0.12, 0.32, body),
                # Center spike (tallest)
                ('spike-c', 0.0, 0.42, 0.14, 0.42, body),
                # Right spike
                ('spike-r', 0.38, 0.28, 0.12, 0.32, body),
                # Phase-tinted rim tips on spikes
                ('tip-l', -0.38, 0.52, 0.07, 0.1, rim),
                ('tip-c', 0.0, 0.72, 0.08, 0.12, rim),
                ('tip-r', 0.38, 0.52, 0.07, 0.1, rim),
                # Ink drip under crown — telegraph charge read
                ('drip', 0.0, -0.88, 0.09, 0.18, body),
            )
            binSort = int(look.get('binSort', 44))
            for name, cx, cz, halfW, halfH, color in pieces:
                cm = CardMaker('overlord-crown-%s' % name)
                cm.setFrame(cx - halfW, cx + halfW, cz - halfH, cz + halfH)
                piece = root.attachNewNode(cm.generate())
                piece.setTransparency(TransparencyAttrib.MAlpha)
                piece.setColor(color[0], color[1], color[2], 1)
                piece.setBin('fixed', binSort)
                piece.setDepthWrite(False)
            return root
        except Exception:
            return None

    def _buildFlashInterval(self, root, look):
        """Squash → stretch → settle + alpha flash for the ink crown."""
        try:
            if root is None or root.isEmpty():
                return None
        except Exception:
            return None

        peakA = float(look.get('peakAlpha', 0.95))
        fadeIn = float(look.get('fadeInSec', 0.05))
        holdSec = float(look.get('holdSec', 0.18))
        fadeOut = float(look.get('fadeOutSec', 0.32))
        squash = look.get('squash', (1.4, 1.0, 0.55))
        stretch = look.get('stretch', (0.7, 1.0, 1.55))
        squashSec = float(look.get('squashSec', 0.06))
        stretchSec = float(look.get('stretchSec', 0.1))
        settleSec = float(look.get('settleSec', 0.14))
        baseScale = float(look.get('scale', 1.0))
        flash = look.get('flashColor', (1.15, 0.45, 1.25, 1.0))

        squashScale = Vec3(
            baseScale * squash[0], baseScale * squash[1],
            baseScale * squash[2])
        stretchScale = Vec3(
            baseScale * stretch[0], baseScale * stretch[1],
            baseScale * stretch[2])
        settleScale = Vec3(baseScale, baseScale, baseScale)

        # Brief color punch on the whole crown so phase tint flares.
        flashPeak = Vec4(
            min(1.6, flash[0] * 1.15),
            min(1.6, flash[1] * 1.15),
            min(1.6, flash[2] * 1.15),
            peakA,
        )

        return Parallel(
            Sequence(
                LerpColorScaleInterval(
                    root, fadeIn, flashPeak, blendType='easeOut'),
                Wait(holdSec),
                LerpColorScaleInterval(
                    root, fadeOut, Vec4(1, 1, 1, 0), blendType='easeIn'),
            ),
            Sequence(
                LerpScaleInterval(root, squashSec, squashScale),
                LerpScaleInterval(root, stretchSec, stretchScale),
                LerpScaleInterval(root, settleSec, settleScale),
            ),
            name='overlordCrownHoseFlash',
        )
