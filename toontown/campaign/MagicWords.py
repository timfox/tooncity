"""Campaign magic words — registered via MagicWordIndex import."""

from toontown.spellbook import MagicWordConfig
from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.campaign.CampaignDirectorAI import getCampaignDirector


class StartCampaign(MagicWord):
    aliases = ['startcampaign', 'campaignstart', 'begincampaign']
    desc = 'Start or resume the multi-neighborhood reclaim campaign act.'
    advancedDesc = (
        'Uses CampaignDirector + ReclaimDirector. Oswald leads Loopy → '
        'Punchline → Silly (hub/street NPC-style presence stub — body + '
        'E-talk greet — greets the trusted lead before the twist) '
        'two-phase Ink Overlord finale (act-enter banners: '
        'cream edge + soft cream wash pulse; Punchline Act 2 tip: hose pop + '
        'juicier deepened cream hose settle past #256 (overshoot → rest → '
        'micro rebound) + soft cream wash pulse; Silly Act 3 tip: hose pop + '
        'deepened cream hose settle past #279 + '
        'deepened soft cream wash pulse past #279 + cream aftershock past #279; '
        'early/mid trust settle: '
        'cream edge + soft '
        'cream wash pulse + cream aftershock; Loopy mid-act unease tip '
        '(smile sticks a rubbery half-beat before Punchline handoff; '
        'Oswald trust intact early); Loopy + Punchline mid-act '
        'trust fracture: off-tone cheer / tip unease + cool cream/shadow '
        'fleck edge; Silly Act 3 tip: Overlord foreshadow — cheer feels '
        'wrong + longer fracture hose settle + deepened cream hose settle '
        'past #279; '
        'Silly mid-act approach tip: '
        'Oswald almost confesses an uneasy half-truth (no twist spoil); act '
        'handoffs: carnival '
        'confetti / cream sparkle / '
        'juicier deepened edge settle past #271 + soft cream wash pulse; P1 magenta rise / P2 crimson unleash '
        'telegraphs + ink crown silhouette flash + FOV/flash sting; purity '
        'victory cheer: cream swell / sparkle / edge + soft cream wash '
        'pulse + cream aftershock; victory reveal sting: Oswald caused the '
        'corruption — betrayal handoff banner hose-pop + juicier deepened '
        'cream hose settle past #260 (overshoot → rest → micro rebound) + '
        'deepened victory/confetti twist cream sting past #265 '
        '(+ taller micro cream pop rebound + richer soft cream aftershock) '
        '+ rubber-hose silhouette shadow flash + FOV/SFX + soft cream '
        'aftershock framed by cream edge + soft cream wash pulse + cream '
        'aftershock; then a short fightable Corrupted Oswald chase/arena '
        'spawn as the betrayal gameplay consequence; chase clear lands a '
        'campaign epilogue soft-end handoff + hub victory replay tip). '
        'Toontown spiritual-sequel fantasy — no keyblades. '
        'Pair with ~hackslash 0.')
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = []

    def handleWord(self, invoker, avId, toon, *args):
        return getCampaignDirector(self.air).startCampaign(toon)


class AdvanceCampaign(MagicWord):
    aliases = ['advancecampaign', 'campaignadvance', 'nextact']
    desc = 'Advance the campaign to the next act (demo / force unlock).'
    advancedDesc = (
        'Without args, advances if unlocked. Pass "force" to skip the reclaim gate.')
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = [
        ('force', str, ''),
    ]

    def handleWord(self, invoker, avId, toon, *args):
        forceToken = ''
        if args:
            forceToken = str(args[0]).strip().lower()
        force = forceToken in ('force', '1', 'true', 'yes')
        return getCampaignDirector(self.air).advanceCampaign(toon, force=force)


class CampaignStatus(MagicWord):
    aliases = ['campaignstatus', 'campaign', 'campstatus']
    desc = 'Show multi-hood campaign progression status.'
    advancedDesc = 'Reports act index, unlocks, reclaim count, and hub/zone hints.'
    execLocation = MagicWordConfig.EXEC_LOC_SERVER
    accessLevel = 'MODERATOR'
    affectRange = [MagicWordConfig.AFFECT_SELF]
    arguments = []

    def handleWord(self, invoker, avId, toon, *args):
        return getCampaignDirector(self.air).statusText()


def registerCampaignMagicWords():
    StartCampaign()
    AdvanceCampaign()
    CampaignStatus()
