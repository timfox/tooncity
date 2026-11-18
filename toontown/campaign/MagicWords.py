"""Campaign magic words — registered via MagicWordIndex import."""

from toontown.spellbook import MagicWordConfig
from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.campaign.CampaignDirectorAI import getCampaignDirector


class StartCampaign(MagicWord):
    aliases = ['startcampaign', 'campaignstart', 'begincampaign']
    desc = 'Start or resume the multi-neighborhood reclaim campaign act.'
    advancedDesc = (
        'Uses CampaignDirector + ReclaimDirector. Oswald leads Loopy → '
        'Punchline → Silly two-phase Ink Overlord finale (act-enter banners: '
        'cream edge + soft cream wash pulse; Punchline Act 2 tip: hose pop + '
        'cream hose settle + soft cream wash pulse; Silly Act 3 tip: hose pop + '
        'cream hose settle + soft cream wash pulse; early/mid trust settle: '
        'cream edge + soft '
        'cream wash pulse + cream aftershock; Loopy + Punchline mid-act '
        'trust fracture: off-tone cheer / tip unease + cool cream/shadow '
        'fleck edge; Silly Act 3 tip: Overlord foreshadow — cheer feels '
        'wrong + longer fracture hose settle + cream hose settle; mid-act '
        'approach tip: '
        'Oswald almost confesses an uneasy half-truth (no twist spoil); act '
        'handoffs: carnival '
        'confetti / cream sparkle / '
        'deepened edge settle + soft cream wash pulse; P1 magenta rise / P2 crimson unleash '
        'telegraphs + ink crown silhouette flash + FOV/flash sting; purity '
        'victory cheer: cream swell / sparkle / edge + soft cream wash '
        'pulse + cream aftershock; victory reveal sting: Oswald caused the '
        'corruption — betrayal handoff banner hose-pop + cream hose settle + '
        'deepened victory/confetti twist cream sting (+ soft cream aftershock) '
        '+ rubber-hose silhouette shadow flash + FOV/SFX + soft cream '
        'aftershock framed by cream edge + soft cream wash pulse + cream '
        'aftershock). Toontown '
        'spiritual-sequel fantasy — no keyblades. '
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
