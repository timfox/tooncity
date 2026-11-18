#!/usr/bin/env python3
"""Headless tests: street-clear reclaim reward beyond CampaignPower bump.

Loads CampaignGlobals / CampaignPower with a ToontownGlobals stub — no
Panda3D. Asserts jellybean / laff / trophy payload math, AI award to a
stub toon, reclaim director __complete wiring, and CampaignHandoff plate
line beyond COMBO_DAMAGE.

Run from repo root:
  python3 tests/test_street_clear_reclaim_reward.py
  python3 -m unittest tests.test_street_clear_reclaim_reward -v
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

LOOPY = 2200
PUNCHLINE = 2300
SILLY = 2100
TTC = 2000


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_modules():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, REPO_ROOT.as_posix())

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim', 'toontown.campaign', 'toontown.hackslash'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = TTC
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    hs = types.ModuleType('toontown.hackslash.HackSlashConfig')
    hs.COMBO_DAMAGE = (8, 12, 28)
    sys.modules['toontown.hackslash.HackSlashConfig'] = hs
    sys.modules['toontown.hackslash'].HackSlashConfig = hs

    cg_path = REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
    cg_spec = importlib.util.spec_from_file_location(
        'toontown.corruption.CorruptionGlobals', cg_path)
    cg = importlib.util.module_from_spec(cg_spec)
    assert cg_spec.loader is not None
    sys.modules['toontown.corruption.CorruptionGlobals'] = cg
    cg_spec.loader.exec_module(cg)

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp

    power_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignPower.py'
    power_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignPower', power_path)
    power = importlib.util.module_from_spec(power_spec)
    assert power_spec.loader is not None
    sys.modules['toontown.campaign.CampaignPower'] = power
    power_spec.loader.exec_module(power)

    return camp, power, hs


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            names = set()
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(item.name)
            return names
    return set()


class _StubToon:
    def __init__(self):
        self.money = 0
        self.maxMoney = 100
        self.bankMoney = 0
        self.hp = 10
        self.maxHp = 15
        self.messages = []
        self.toonUps = []

    def addMoney(self, delta):
        self.money = min(self.maxMoney, self.money + int(delta))

    def toonUp(self, amount, quietly=0, sendTotal=1):
        self.toonUps.append(int(amount))
        self.hp = min(self.maxHp, self.hp + int(amount))

    def d_setSystemMessage(self, _code, text):
        self.messages.append(str(text))


class StreetClearReclaimRewardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.camp, cls.power, cls.hs = _load_panda_free_modules()

    def setUp(self):
        self.hs.COMBO_DAMAGE = (8, 12, 28)
        self.power._BASE_DAMAGE = None
        # Restore tunables if a prior test flipped the enable flag.
        self.camp.STREET_CLEAR_REWARD_ENABLED = True

    def test_globals_define_street_clear_reward_beyond_power_bump(self):
        camp = self.camp
        self.assertTrue(hasattr(camp, 'POWER_BUMP_PER_RECLAIM'))
        self.assertIs(camp.STREET_CLEAR_REWARD_ENABLED, True)
        self.assertGreater(camp.STREET_CLEAR_JELLYBEANS, 0)
        self.assertGreaterEqual(
            camp.STREET_CLEAR_JELLYBEANS_MAX, camp.STREET_CLEAR_JELLYBEANS)
        self.assertGreater(camp.STREET_CLEAR_LAFF, 0)
        self.assertIn('%s', camp.STREET_CLEAR_TROPHY_FMT)
        self.assertIn('jellybean', camp.STREET_CLEAR_REWARD_MSG_FMT.lower())
        self.assertIn('Street Trophy', camp.STREET_CLEAR_REWARD_HANDOFF_FMT)
        # No KH / cream-only framing in reward copy.
        blob = ' '.join([
            camp.STREET_CLEAR_TROPHY_FMT,
            camp.STREET_CLEAR_REWARD_MSG_FMT,
            camp.STREET_CLEAR_REWARD_HANDOFF_FMT,
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora', 'heartless'):
            self.assertNotIn(banned, blob)

    def test_jellybean_scales_with_reclaim_count_and_caps(self):
        camp = self.camp
        power = self.power
        base = camp.STREET_CLEAR_JELLYBEANS
        bonus = camp.STREET_CLEAR_JELLYBEANS_BONUS_PER_RECLAIM
        cap = camp.STREET_CLEAR_JELLYBEANS_MAX

        self.assertEqual(power.streetClearJellybeans(1), base)
        self.assertEqual(
            power.streetClearJellybeans(2), base + bonus)
        self.assertEqual(
            power.streetClearJellybeans(3), base + 2 * bonus)
        # Cap holds even for huge reclaim counts.
        self.assertEqual(power.streetClearJellybeans(99), cap)
        self.assertEqual(power.streetClearLaff(), camp.STREET_CLEAR_LAFF)

    def test_payload_includes_trophy_and_handoff_line(self):
        power = self.power
        payload = power.streetClearRewardPayload(
            reclaimCount=1, zoneId=LOOPY)
        self.assertTrue(payload['enabled'])
        self.assertEqual(
            payload['jellybeans'], self.camp.STREET_CLEAR_JELLYBEANS)
        self.assertEqual(payload['laff'], self.camp.STREET_CLEAR_LAFF)
        self.assertIn('Loopy Lane', payload['trophy'])
        self.assertIn('Street Trophy', payload['trophy'])
        self.assertIn('jellybeans', payload['whisper'])
        self.assertIn('laff', payload['whisper'])
        self.assertIn('beans', payload['handoff'])
        self.assertIn('laff', payload['handoff'])
        # Punchline resolves from ACTS too.
        punch = power.streetClearRewardPayload(
            reclaimCount=2, zoneId=PUNCHLINE)
        self.assertIn('Punchline Place', punch['trophy'])
        self.assertEqual(
            punch['jellybeans'],
            self.camp.STREET_CLEAR_JELLYBEANS
            + self.camp.STREET_CLEAR_JELLYBEANS_BONUS_PER_RECLAIM)

    def test_award_grants_jellybeans_and_laff_to_stub_toon(self):
        power = self.power
        toon = _StubToon()
        toon.hp = 8
        payload = power.awardStreetClearReward(
            toon, reclaimCount=1, zoneId=LOOPY)
        self.assertIsNotNone(payload)
        self.assertEqual(toon.money, self.camp.STREET_CLEAR_JELLYBEANS)
        self.assertEqual(toon.toonUps, [self.camp.STREET_CLEAR_LAFF])
        self.assertEqual(toon.hp, 8 + self.camp.STREET_CLEAR_LAFF)
        self.assertTrue(toon.messages)
        self.assertIn('Street Trophy', toon.messages[0])
        self.assertIn('Loopy Lane', toon.messages[0])

    def test_award_disabled_returns_none_without_mutating(self):
        power = self.power
        self.camp.STREET_CLEAR_REWARD_ENABLED = False
        toon = _StubToon()
        result = power.awardStreetClearReward(
            toon, reclaimCount=1, zoneId=LOOPY)
        self.assertIsNone(result)
        self.assertEqual(toon.money, 0)
        self.assertEqual(toon.toonUps, [])
        self.assertEqual(toon.messages, [])

    def test_power_bump_still_independent_of_street_reward(self):
        """COMBO_DAMAGE bump stays; street reward is additive payoff."""
        power = self.power
        hs = self.hs
        mult = power.applyPowerBump(1)
        self.assertAlmostEqual(
            mult, 1.0 + self.camp.POWER_BUMP_PER_RECLAIM)
        expected = tuple(
            max(1, int(round(d * mult))) for d in (8, 12, 28))
        self.assertEqual(hs.COMBO_DAMAGE, expected)
        # Reward helpers do not touch combo damage.
        before = tuple(hs.COMBO_DAMAGE)
        power.streetClearRewardPayload(reclaimCount=3, zoneId=SILLY)
        self.assertEqual(hs.COMBO_DAMAGE, before)

    def test_reclaim_director_awards_on_complete(self):
        ai_src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        complete_idx = ai_src.find('def __complete(self):')
        self.assertGreater(complete_idx, 0)
        # Look through __complete + following helper start.
        next_def = ai_src.find('\n    def ', complete_idx + 1)
        # Prefer window covering award helper.
        award_idx = ai_src.find('def _awardStreetClearRewards')
        self.assertGreater(award_idx, complete_idx)
        complete_snip = ai_src[complete_idx:award_idx + 80]
        self.assertIn('neighborhoodReclaimed', complete_snip)
        self.assertIn('_awardStreetClearRewards', complete_snip)
        # Stub comment replaced — real reward beyond progression hook.
        self.assertNotIn('Minimal progression stub', complete_snip)

        methods = _class_method_names(
            _module_ast('toontown/reclaim/DistributedReclaimDirectorAI.py'),
            'DistributedReclaimDirectorAI')
        self.assertIn('_awardStreetClearRewards', methods)

        award_snip = ai_src[award_idx:award_idx + 1600]
        self.assertIn('awardStreetClearReward', award_snip)
        self.assertIn('DistributedToonAI', award_snip)
        self.assertIn('reclaimCount', award_snip)
        self.assertIn('zoneId', award_snip)
        # Skip sad toons (KO fail path).
        self.assertIn('hp', award_snip)

    def test_handoff_shows_reward_line_beyond_power_bump(self):
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('streetClearRewardPayload', handoff_src)
        self.assertIn('streetClearRewardEnabled', handoff_src)
        self.assertIn('rewardLine', handoff_src)
        self.assertIn('campaign-handoff-reward', handoff_src)
        self.assertIn('_streetClearRewardLine', handoff_src)
        purity_idx = handoff_src.find('def _onPurityRestore')
        self.assertGreater(purity_idx, 0)
        purity_win = handoff_src[purity_idx:purity_idx + 900]
        self.assertIn('applyPowerBump', purity_win)
        self.assertIn('rewardLine', purity_win)
        self.assertIn('_streetClearRewardLine', purity_win)

    def test_campaign_power_exports_reward_helpers(self):
        power_src = _read('toontown/campaign/CampaignPower.py')
        for name in (
                'applyPowerBump',
                'streetClearJellybeans',
                'streetClearLaff',
                'streetClearTrophyLabel',
                'streetClearRewardPayload',
                'awardStreetClearReward',
                'streetClearRewardEnabled'):
            self.assertIn(name, power_src)
        # Still documents power bump + street reward (not cream / KH).
        self.assertIn('jellybean', power_src.lower())
        self.assertIn('laff', power_src.lower())
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, power_src.lower())


if __name__ == '__main__':
    unittest.main()
