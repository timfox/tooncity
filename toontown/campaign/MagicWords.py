"""Campaign magic words — registered via MagicWordIndex import."""

from toontown.spellbook import MagicWordConfig
from toontown.spellbook.MagicWordIndex import MagicWord
from toontown.campaign.CampaignDirectorAI import getCampaignDirector


class StartCampaign(MagicWord):
    aliases = ['startcampaign', 'campaignstart', 'begincampaign']
    desc = 'Start or resume the multi-neighborhood reclaim campaign act.'
    advancedDesc = (
        'Uses CampaignDirector + ReclaimDirector. Loopy → Punchline → '
        'Silly two-phase Ink Overlord finale (magenta rise → crimson unleash '
        'with FOV/flash sting; Oswald twist tease on victory). '
        'Toontown spiritual-sequel fantasy — no keyblades. Pair with ~hackslash 0.')
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
