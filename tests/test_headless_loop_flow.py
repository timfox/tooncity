#!/usr/bin/env python3
"""Headless behavioral deepen: explore → fight → reclaim → Oswald twist.

Panda-free proof of the multi-hood loop already shipped on develop (through
systems waves ending at PR #376 / wave H). Complements
`test_headless_loop_smoke.py` (registration / juice AST) and the focused
wave / act-param / kit suites by chaining the spiritual-sequel loop:

  explore — zone messengers, Oswald plaza NPC + reclaim cheer (#354) +
            first-meet tip / oswaldMet persist (#360) + oswaldCheered
            latch after reclaim cheer (#369) + soft-next greets from
            cheer/unlocks (#373), Loopy unease, hub breadcrumb act-unlock
            dim (#332) + progress-sync rehydrate (#357), chase-pending
            hub tip (#342)
  fight   — archetype kits, melee interrupt (#329/#348/#352/#363),
            Brute/Gagster counters (#343), Overlord rain/slam/ink_surge
            counters (#359), Smudge ink_dash/ink_splat interrupt+counters
            (#363), Oswald betrayal counters (#352), authoritative server
            melee damage from hitIndex (#366) + CampaignPower reclaimCount
            AI table (#371), juggle hang stun, reclaim KO fail + retry
            (#338), soft-lock boss priority (#339) + sticky yield (#347) +
            cycle-with-lock prefer (#356) + Elite/Ambush pack prefer
            (#375) + reclaimAmbushSpawn pressure/soft-lock cue (#372),
            Overlord P1 rising slam (#334) + move-id telegraph (#340) +
            rain linger sludge (#362), boss/chase HP bar (#331)
  reclaim — soft-gate + R hydrate, Silly Overlord HP→P2, ink_surge, elite
            modifiers / earlier-wave ambush + Silly between-swell
            (#345/#358) + ACTS C path elite/ambush mirror (#365) +
            finale C phase2 elite/ambush beside Unleashed adds (#376),
            street-clear jellybean/laff reward (#361), campaign progress
            client sync on login (#333), CampaignPower reclaimCount
            rehydrate (#349) + sync/purity dedupe (#367), SECURED
            purity-lock persist across AI restart (#368), campaignVictory
            client relay (#351)
  twist   — betrayal chase + kit + chase resume (#330) + false-clear gate
            (#341) + mid-chase HP persist (#350) + Oswald telegraph/hit AV
            (#344) + chase-clear epilogue + hub stain (#336) + hub-stain
            securedZones mirror (#374) + washed-plaza epilogue beat (#353)

No Panda3D, no resources, no invented gameplay — only concrete symbols and
pure helpers already on develop. Not a cream-FX deepen / no KH.

Run from repo root:
  python3 tests/test_headless_loop_flow.py
  python3 -m unittest tests.test_headless_loop_flow -v
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
HUB = 2000

EXPECTED_PACK_IDS = {
    LOOPY: 'loopy-smudge',
    PUNCHLINE: 'punchline-sludge',
    SILLY: 'silly-overlord',
}

EXPECTED_ACT_IDS = ('loopy', 'punchline', 'finale')
EXPECTED_NEXT_STREETS = {
    'loopy': 'Punchline Place',
    'punchline': 'Silly Street',
    'finale': None,
}


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _module_ast(rel: str) -> ast.AST:
    return ast.parse(_read(rel), filename=rel)


def _class_and_func_names(tree: ast.AST) -> set:
    names = set()
    for node in getattr(tree, 'body', []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _class_method_names(tree: ast.AST, class_name: str) -> set:
    for node in getattr(tree, 'body', []):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
    raise AssertionError('class %r not found' % class_name)


def _toplevel_assign_names(tree: ast.AST) -> set:
    names = set()
    for node in getattr(tree, 'body', []):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def _method_body_names(rel: str, class_name: str, method_name: str) -> set:
    """Names / attrs referenced inside one class method (AST scan)."""
    tree = _module_ast(rel)
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.name != method_name:
                continue
            for child in ast.walk(item):
                if isinstance(child, ast.Name):
                    out.add(child.id)
                elif isinstance(child, ast.Attribute):
                    out.add(child.attr)
    return out


def _accept_events(tree: ast.AST, class_name: str) -> set:
    """Collect string / name event targets passed to self.accept in a class."""
    events = set()
    for node in getattr(tree, 'body', []):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in ast.walk(node):
            if not isinstance(item, ast.Call):
                continue
            func = item.func
            if not (isinstance(func, ast.Attribute) and func.attr == 'accept'):
                continue
            if not item.args:
                continue
            arg0 = item.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                events.add(arg0.value)
            elif isinstance(arg0, ast.Str):  # py<3.8
                events.add(arg0.s)
            elif isinstance(arg0, ast.Name):
                events.add(arg0.id)
    return events


def _load_panda_free_loop_modules():
    """Stub ToontownGlobals; load Corruption / Reclaim / Campaign globals + save/stain."""
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim', 'toontown.campaign'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = HUB
    sys.modules['toontown.toonbase.ToontownGlobals'] = tg
    sys.modules['toontown.toonbase'].ToontownGlobals = tg

    cg_path = REPO_ROOT / 'toontown' / 'corruption' / 'CorruptionGlobals.py'
    cg_spec = importlib.util.spec_from_file_location(
        'toontown.corruption.CorruptionGlobals', cg_path)
    cg = importlib.util.module_from_spec(cg_spec)
    assert cg_spec.loader is not None
    sys.modules['toontown.corruption.CorruptionGlobals'] = cg
    cg_spec.loader.exec_module(cg)
    sys.modules['toontown.corruption'].CorruptionGlobals = cg

    rg_path = REPO_ROOT / 'toontown' / 'reclaim' / 'ReclaimGlobals.py'
    rg_spec = importlib.util.spec_from_file_location(
        'toontown.reclaim.ReclaimGlobals', rg_path)
    rg = importlib.util.module_from_spec(rg_spec)
    assert rg_spec.loader is not None
    sys.modules['toontown.reclaim.ReclaimGlobals'] = rg
    rg_spec.loader.exec_module(rg)
    sys.modules['toontown.reclaim'].ReclaimGlobals = rg

    camp_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignGlobals.py'
    camp_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignGlobals', camp_path)
    camp = importlib.util.module_from_spec(camp_spec)
    assert camp_spec.loader is not None
    sys.modules['toontown.campaign.CampaignGlobals'] = camp
    camp_spec.loader.exec_module(camp)
    sys.modules['toontown.campaign'].CampaignGlobals = camp

    save_path = REPO_ROOT / 'toontown' / 'campaign' / 'CampaignProgressSave.py'
    save_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.CampaignProgressSave', save_path)
    save = importlib.util.module_from_spec(save_spec)
    assert save_spec.loader is not None
    sys.modules['toontown.campaign.CampaignProgressSave'] = save
    save_spec.loader.exec_module(save)

    stain_path = REPO_ROOT / 'toontown' / 'campaign' / 'HubStain.py'
    stain_spec = importlib.util.spec_from_file_location(
        'toontown.campaign.HubStain', stain_path)
    stain = importlib.util.module_from_spec(stain_spec)
    assert stain_spec.loader is not None
    sys.modules['toontown.campaign.HubStain'] = stain
    stain_spec.loader.exec_module(stain)
    return camp, rg, cg, save, stain


def _extract_breadcrumb_unlock_helpers(rg):
    """Compile pollution + unlock breadcrumb helpers without panda imports."""
    crumb_rel = 'toontown/safezone/CorruptStreetBreadcrumb.py'
    path = REPO_ROOT / crumb_rel
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src, filename=crumb_rel)
    keep_assign = {'_clientUnlockedThrough'}
    keep_funcs = {
        'getClientUnlockedThrough',
        'setClientUnlockedThrough',
        'resetClientUnlockedThrough',
        '_streetActUnlocked',
        '_streetLooksPolluted',
        'streetNeedsBreadcrumb',
        'streetBreadcrumbDimmed',
    }
    keep = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in keep_assign:
                    keep.append(node)
                    break
        elif isinstance(node, ast.FunctionDef) and node.name in keep_funcs:
            keep.append(node)
    found = {n.name for n in keep if isinstance(n, ast.FunctionDef)}
    missing = keep_funcs - found
    if missing:
        raise AssertionError(
            'missing breadcrumb helpers %s in %s' % (sorted(missing), crumb_rel))
    mod = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(mod)
    reclaim_pkg = types.ModuleType('toontown.reclaim')
    reclaim_pkg.ReclaimGlobals = rg
    sys.modules['toontown.reclaim'] = reclaim_pkg
    ns = {'ReclaimGlobals': rg}
    exec(compile(mod, crumb_rel, 'exec'), ns)  # noqa: S102 — test harness
    return ns


def _load_soft_target_helpers():
    """HackSlashConfig + SoftTarget pure helpers (no MeleeCombat / Panda)."""
    for pkg in ('toontown', 'toontown.hackslash'):
        _ensure_pkg(pkg)

    cfg_path = REPO_ROOT / 'toontown' / 'hackslash' / 'HackSlashConfig.py'
    cfg_spec = importlib.util.spec_from_file_location(
        'toontown.hackslash.HackSlashConfig', cfg_path)
    cfg = importlib.util.module_from_spec(cfg_spec)
    assert cfg_spec.loader is not None
    sys.modules['toontown.hackslash.HackSlashConfig'] = cfg
    cfg_spec.loader.exec_module(cfg)
    sys.modules['toontown.hackslash'].HackSlashConfig = cfg

    soft_path = REPO_ROOT / 'toontown' / 'hackslash' / 'SoftTarget.py'
    soft_spec = importlib.util.spec_from_file_location(
        'toontown.hackslash.SoftTarget', soft_path)
    soft = importlib.util.module_from_spec(soft_spec)
    assert soft_spec.loader is not None
    sys.modules['toontown.hackslash.SoftTarget'] = soft
    soft_spec.loader.exec_module(soft)
    sys.modules['toontown.hackslash'].SoftTarget = soft
    return soft, cfg


def _extract_chase_combat_helpers(camp, cg):
    """Compile chase HP / defeat helpers without panda / DirectObject imports."""
    chase_rel = 'toontown/campaign/OswaldBetrayalChase.py'
    path = REPO_ROOT / chase_rel
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src, filename=chase_rel)
    keep_funcs = {'chaseHp', 'resolveChaseSpawnHp', 'chaseCombatDefeated'}
    keep = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in keep_funcs:
            keep.append(node)
    found = {n.name for n in keep if isinstance(n, ast.FunctionDef)}
    missing = keep_funcs - found
    if missing:
        raise AssertionError(
            'missing chase helpers %s in %s' % (sorted(missing), chase_rel))
    mod = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(mod)
    # chaseHp / resolveChaseSpawnHp close over CampaignGlobals + CorruptionGlobals.
    ns = {
        'CampaignGlobals': camp,
        'CorruptionGlobals': cg,
    }
    exec(compile(mod, chase_rel, 'exec'), ns)  # noqa: S102 — test harness
    return ns


class HeadlessLoopFlowTest(unittest.TestCase):
    """Coherent loop-chain checks beyond juice-registration smoke."""

    @classmethod
    def setUpClass(cls):
        cls.camp, cls.rg, cls.cg, cls.save, cls.stain = (
            _load_panda_free_loop_modules())
        cls.soft, cls.hs_cfg = _load_soft_target_helpers()
        cls.crumb = _extract_breadcrumb_unlock_helpers(cls.rg)
        cls.chase = _extract_chase_combat_helpers(cls.camp, cls.cg)
        cls.acts = list(cls.camp.ACTS)
        cls.act_by_id = {a['id']: a for a in cls.acts}

    def setUp(self):
        # Breadcrumb unlock latch is process-global; reset between tests.
        reset = self.crumb.get('resetClientUnlockedThrough')
        if callable(reset):
            reset()

    # --- explore leg: hood path / packs / hub tip ---

    def test_explore_hood_path_packs_and_acts_align(self):
        camp, rg = self.camp, self.rg
        self.assertEqual(int(camp.HUB_ZONE), HUB)
        self.assertEqual(camp.PROTAGONIST, 'Oswald')
        self.assertEqual(camp.RECLAIM_FACE, 'Oswald')
        self.assertEqual(tuple(a['id'] for a in self.acts), EXPECTED_ACT_IDS)

        for zone, pack_id in EXPECTED_PACK_IDS.items():
            pack = rg.streetPack(zone)
            self.assertIsNotNone(pack, msg='STREET_PACKS missing zone %s' % zone)
            self.assertEqual(pack.get('packId'), pack_id)
            self.assertTrue(pack.get('playEntryTip'))
            self.assertTrue(pack.get('waveScripts'))

        for act_id, next_street in EXPECTED_NEXT_STREETS.items():
            act = self.act_by_id[act_id]
            self.assertEqual(act.get('nextStreet'), next_street)
            pack = rg.streetPack(int(act['zoneId']))
            self.assertIsNotNone(pack)
            # Shared seed/pack sizing keys used when campaign attaches reclaim.
            for key in ('seedPollution', 'packSize', 'maxPacks', 'corruptHp'):
                self.assertIn(key, act)
                self.assertIn(key, pack)

        finale = self.act_by_id['finale']
        self.assertTrue(finale.get('finale'))
        self.assertEqual(int(finale['zoneId']), SILLY)
        self.assertEqual(finale.get('corruptName'), 'Ink Overlord')
        self.assertIn('phase2', finale)
        self.assertEqual(
            finale['phase2'].get('corruptName'), 'Ink Overlord Unleashed')

    def test_hub_tip_and_handoff_pure_helpers(self):
        camp = self.camp
        tip = camp.hubPlayEntryTip()
        self.assertIn('Oswald', tip)
        self.assertIn('Loopy Lane', tip)
        self.assertIn('C campaign', tip)
        self.assertNotIn('~startcampaign', tip)
        self.assertNotIn(str(LOOPY), tip)

        punch = camp.hubPlayEntryTip(nextStreet='Punchline Place')
        self.assertIn('Punchline Place', punch)
        self.assertNotIn('Loopy Lane', punch)

        # Post-victory hub tip (chase-clear epilogue soft-end).
        victory = camp.hubPlayEntryTip(victory=True)
        self.assertIn('Campaign complete', victory)
        self.assertIn('Loopy', victory)
        self.assertEqual(victory, camp.hubVictoryReplayTip())

        nxt = self.act_by_id['punchline']
        hint = camp.handoffTravelHint(nxt)
        self.assertIn('Punchline Place', hint)
        self.assertIn('Oswald', hint)
        self.assertNotIn('~startcampaign', hint)
        self.assertNotIn(str(PUNCHLINE), hint)

        # Soft next-street cue after Loopy clear — street name only.
        loopy = self.act_by_id['loopy']
        self.assertEqual(loopy.get('nextStreet'), 'Punchline Place')
        cue = loopy.get('nextCue') or ''
        self.assertIn('Punchline Place', cue)
        self.assertNotIn('~startcampaign', cue)

    def test_play_entry_and_breadcrumb_explore_wiring(self):
        play_src = _read('toontown/campaign/PlayEntry.py')
        play_tree = _module_ast('toontown/campaign/PlayEntry.py')
        play_names = _class_and_func_names(play_tree)
        self.assertIn('PlayEntryClient', play_names)
        self.assertIn('ensurePlayEntryClient', play_names)
        methods = _class_method_names(play_tree, 'PlayEntryClient')
        for method in (
                '_showHubTip', '_latchSoftNextCue', '_autoStartReclaim',
                '_requestCampaign', '_armSillyApproachTip',
                '_armLoopyApproachTip', '_onCampaignEpilogue'):
            self.assertIn(method, methods, msg='PlayEntryClient missing %s' % method)
        self.assertIn("accept('oswaldBetrayalChaseCleared'", play_src)
        self.assertIn("accept('campaignEpilogue'", play_src)

        self.assertIn('CampaignGlobals.ACTS', play_src)
        self.assertIn('HUB_ZONE', play_src)
        self.assertIn('_requestCampaign()', play_src)
        # Zone-change messenger re-arms tips/auto-campaign on tunnel hops.
        self.assertIn("accept('localAvatarZoneChange'", play_src)
        self.assertIn('getBranchZone', play_src)
        place_src = _read('toontown/hood/Place.py')
        self.assertIn("messenger.send('localAvatarZoneChange'", place_src)
        self.assertIn("messenger.send('localToonLeftZone'", place_src)
        street_src = _read('toontown/town/Street.py')
        hub_place_src = _read('toontown/safezone/Playground.py')
        self.assertIn('announceLocalAvatarZoneChange', street_src)
        self.assertIn('announceLocalToonLeftZone', street_src)
        self.assertIn('announceLocalAvatarZoneChange', hub_place_src)
        self.assertIn('announceLocalToonLeftZone', hub_place_src)
        # Auto path prefers campaign (C) over street-pack reclaim (R).
        auto_idx = play_src.find('def _autoStartReclaim')
        self.assertGreater(auto_idx, 0)
        auto_snip = play_src[auto_idx:auto_idx + 800]
        self.assertIn('_requestCampaign()', auto_snip)
        self.assertNotIn('_requestReclaim()', auto_snip)

        for pack_id in EXPECTED_PACK_IDS.values():
            self.assertIn(pack_id, play_src)

        crumb_rel = 'toontown/safezone/CorruptStreetBreadcrumb.py'
        self.assertTrue((REPO_ROOT / crumb_rel).is_file())
        crumb_names = _class_and_func_names(_module_ast(crumb_rel))
        for sym in (
                'streetNeedsBreadcrumb', 'CorruptStreetBreadcrumb',
                'ensureCorruptStreetBreadcrumbs', 'reclaimStreetEntries'):
            self.assertIn(sym, crumb_names)
        playground_src = _read('toontown/safezone/TTPlayground.py')
        self.assertIn('ensureCorruptStreetBreadcrumbs', playground_src)

    def test_explore_oswald_presence_and_loopy_unease(self):
        """Trusted face + mid-act Loopy foreshadow before Punchline handoff."""
        camp = self.camp
        self.assertTrue(camp.OSWALD_PRESENCE_ENABLED)
        self.assertEqual(camp.OSWALD_PRESENCE_LABEL, camp.PROTAGONIST)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_HUB_GREET)
        self.assertIn('Loopy', camp.OSWALD_PRESENCE_HUB_GREET)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_STREET_GREET)
        self.assertTrue(camp.OSWALD_PRESENCE_HIDE_ON_BETRAYAL)
        # Soft-next greets after oswaldCheered + unlocks (#TC-385 / post-#369).
        self.assertIn('{street}', camp.OSWALD_PRESENCE_HUB_GREET_SOFT_NEXT)
        self.assertIn('{street}', camp.OSWALD_PRESENCE_STREET_GREET_SOFT_NEXT)
        self.assertTrue(callable(camp.oswaldPresenceGreetTip))
        soft_hub = camp.oswaldPresenceGreetTip(
            HUB, cheered=True, softNextStreet='Punchline Place')
        self.assertIn('Punchline Place', soft_hub)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, camp.OSWALD_PRESENCE_HUB_GREET.lower())
            self.assertNotIn(banned, camp.OSWALD_PRESENCE_STREET_GREET.lower())
            self.assertNotIn(banned, soft_hub.lower())

        presence_rel = 'toontown/campaign/OswaldPresence.py'
        self.assertTrue((REPO_ROOT / presence_rel).is_file())
        presence_names = _class_and_func_names(_module_ast(presence_rel))
        for sym in (
                'presenceEnabled', 'shouldShowPresence', 'greetTipForZone',
                'hubPlazaPos', 'cheerOnReclaim', 'playOswaldPresenceCheer',
                'OswaldPresenceClient', 'ensureOswaldPresenceClient',
                'refreshOswaldPresenceHub', 'stopOswaldPresenceClient'):
            self.assertIn(sym, presence_names)
        presence_src = _read(presence_rel)
        self.assertIn("accept('localAvatarZoneChange'", presence_src)
        self.assertIn('oswaldRevealBanner', presence_src)
        self.assertIn('oswaldBetrayalChase', presence_src)
        # Plaza NPC deepen (#354) + ACTS street authored stands — beyond
        # spawn-near-avatar CardMaker stub; still not a DistributedNPC.
        self.assertIn('full DistributedNPC', presence_src)
        self.assertIn('CardMaker', presence_src)
        self.assertIn('_buildNpcSilhouette', presence_src)
        self.assertIn('_placeBodyAtPlaza', presence_src)
        self.assertIn('_placeBodyAtStreetStand', presence_src)
        self.assertIn('streetStandPos', presence_src)
        self.assertIn('playReclaimCheer', presence_src)
        self.assertIn('npcCheerStub', presence_src)
        self.assertIn('_armInteract', presence_src)
        self.assertIn("accept('e'", presence_src)
        self.assertIn('oswaldPresenceInteract', presence_src)
        self.assertIn('oswald-npc-torso', presence_src)
        self.assertNotIn("TextNode('oswaldPresenceLabel')", presence_src)
        self.assertNotIn('from toontown.toon', presence_src)
        self.assertNotIn('distributednpctoon', presence_src.lower())
        self.assertIn('Talk', camp.OSWALD_PRESENCE_INTERACT_PROMPT)
        self.assertGreater(float(camp.OSWALD_PRESENCE_INTERACT_RADIUS), 2.0)
        self.assertTrue(camp.OSWALD_PRESENCE_CHEER_ON_RECLAIM)
        self.assertTrue(camp.OSWALD_PRESENCE_IDLE_BOB)
        self.assertEqual(len(camp.OSWALD_PRESENCE_HUB_POS), 4)
        street_pos = camp.OSWALD_PRESENCE_STREET_POS
        self.assertIsInstance(street_pos, dict)
        for act in camp.ACTS:
            self.assertIn(int(act['zoneId']), street_pos)
            self.assertEqual(len(street_pos[int(act['zoneId'])]), 4)
        self.assertIn('Oswald', camp.OSWALD_PRESENCE_CHEER_TIP)
        self.assertIn('clean', camp.OSWALD_PRESENCE_CHEER_TIP.lower())
        self.assertEqual(camp.OSWALD_PRESENCE_CHEER_MSG, 'oswaldPresenceCheer')
        self.assertEqual(
            camp.OSWALD_PRESENCE_CHEERED_MSG, 'oswaldPresenceCheered')
        self.assertEqual(
            camp.OSWALD_PRESENCE_CHEERED_SYNC_MSG, 'oswaldCheeredSync')
        presence_accepts = _accept_events(
            _module_ast(presence_rel), 'OswaldPresenceClient')
        self.assertIn('npcCheerStub', presence_accepts)
        self.assertIn('campaignVictory', presence_accepts)
        # First-meet tip + durable oswaldMet (#360) — trust beat before twist.
        self.assertEqual(camp.OSWALD_PRESENCE_MET_MSG, 'oswaldPresenceMet')
        self.assertEqual(camp.OSWALD_PRESENCE_MET_SYNC_MSG, 'oswaldMetSync')
        meet_tip = camp.OSWALD_PRESENCE_FIRST_MEET_TIP
        self.assertIn('Oswald', meet_tip)
        self.assertIn('met', meet_tip.lower())
        self.assertIn('reclaim', meet_tip.lower())
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, meet_tip.lower())
        presence_methods = _class_method_names(
            _module_ast(presence_rel), 'OswaldPresenceClient')
        for method in (
                '_onOswaldPresenceMet', '_onOswaldMetSync',
                '_requestPersistMet', '_meetOswald',
                '_onOswaldPresenceCheered', '_onOswaldCheeredSync',
                '_requestPersistCheered',
                '_onCampaignActUnlocked', '_refreshSoftNextStreet'):
            self.assertIn(
                method, presence_methods,
                msg='OswaldPresenceClient missing %s' % method)
        self.assertIn('firstMeetTip', presence_names)
        self.assertIn('metMsgName', presence_names)
        self.assertIn('cheeredMsgName', presence_names)
        self.assertIn('cheeredSyncMsgName', presence_names)
        self.assertIn('hubGreetSoftNextTip', presence_names)
        self.assertIn('d_requestOswaldMet', presence_src)
        self.assertIn('d_requestOswaldCheered', presence_src)
        self.assertIn('OSWALD_PRESENCE_FIRST_MEET_TIP', presence_src)
        self.assertIn("accept('campaignActUnlocked'", presence_src)
        self.assertIn('cheered=bool(self._oswaldCheered)', presence_src)
        self.assertIn('softNextStreet=self._softNextStreet', presence_src)
        default_progress = self.save.defaultProgress()
        self.assertIn('oswaldMet', default_progress)
        self.assertEqual(default_progress['oswaldMet'], 0)
        self.assertIn('oswaldCheered', default_progress)
        self.assertEqual(default_progress['oswaldCheered'], 0)
        # #368 securedZones stay on the progress blob beside cheer latch.
        self.assertIn('securedZones', default_progress)
        self.assertEqual(default_progress['securedZones'], [])
        self.assertEqual(
            self.save.sanitizeProgress({'oswaldMet': 9})['oswaldMet'], 1)
        self.assertEqual(
            self.save.sanitizeProgress(
                {'oswaldCheered': 9})['oswaldCheered'], 1)
        # Cheer sanitize must not drop securedZones (#369 beside #368).
        cheer_keep = self.save.sanitizeProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'oswaldCheered': 1,
            'securedZones': [LOOPY],
        })
        self.assertEqual(cheer_keep['oswaldCheered'], 1)
        self.assertIn(LOOPY, cheer_keep['securedZones'])
        mirror_met = self.save.clientMirrorFromProgress({
            'unlockedThrough': 0,
            'state': camp.STATE_IDLE,
            'oswaldMet': 1,
            'oswaldCheered': 1,
        })
        self.assertEqual(mirror_met['oswaldMet'], 1)
        self.assertEqual(mirror_met['oswaldCheered'], 1)
        dc = _read('etc/toon.dc')
        pollution_block = dc.split('dclass PollutionManager')[1].split(
            'dclass ')[0]
        self.assertIn('requestOswaldMet() airecv clsend', pollution_block)
        self.assertIn('setOswaldMet(uint8)', pollution_block)
        self.assertIn(
            'requestOswaldCheered() airecv clsend', pollution_block)
        self.assertIn('setOswaldCheered(uint8)', pollution_block)
        camp_ai = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('def markOswaldMet', camp_ai)
        self.assertIn('def _pushOswaldMetToClient', camp_ai)
        self.assertIn('def markOswaldCheered', camp_ai)
        self.assertIn('def _pushOswaldCheeredToClient', camp_ai)
        cheer_src = _read('toontown/reclaim/ReclaimCheer.py')
        self.assertIn('_nudgeOswald', cheer_src)
        self.assertIn('ensureOswaldPresenceClient', cheer_src)
        self.assertIn('OSWALD_PRESENCE_CHEER_MSG', cheer_src)
        self.assertIn('oswaldPresenceCheer', cheer_src)
        director_src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('ensureOswaldPresenceClient', director_src)
        self.assertIn('npcCheerStub', director_src)

        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('ensureOswaldPresenceClient', play_src)
        playground_src = _read('toontown/safezone/TTPlayground.py')
        self.assertIn('refreshOswaldPresenceHub', playground_src)
        self.assertIn('stopOswaldPresenceClient', playground_src)

        # Loopy mid-act unease (#319) — approach tip + armer, no entryTip.
        loopy = self.act_by_id['loopy']
        tip = loopy.get('approachTip') or ''
        self.assertIn('Oswald', tip)
        self.assertIn('half-beat', tip.lower())
        self.assertFalse(bool(loopy.get('entryTip')))
        self.assertIn('_armLoopyApproachTip', play_src)
        self.assertIn('_showLoopyApproachTip', play_src)
        self.assertGreater(camp.LOOPY_APPROACH_TIP_DELAY_SEC, 0.0)

    def test_explore_hub_breadcrumb_act_unlock(self):
        """Hub crumbs dim locked acts; PlayEntry accepts campaignActUnlocked (#332)."""
        rg = self.rg
        crumb = self.crumb
        needs = crumb['streetNeedsBreadcrumb']
        dimmed = crumb['streetBreadcrumbDimmed']
        # Soft-gate parity: polluted Punchline/Silly stay reclaim-muted until unlock.
        self.assertTrue(needs(
            LOOPY, {}, seedPollution=0.55, pure=0.0, unlockedThrough=0))
        self.assertFalse(needs(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=0))
        self.assertTrue(needs(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=1))
        self.assertFalse(needs(
            SILLY, {}, seedPollution=0.80, pure=0.0, unlockedThrough=1))
        self.assertTrue(needs(
            SILLY, {}, seedPollution=0.80, pure=0.0, unlockedThrough=2))
        # Dim cue keeps locked polluted tunnels visible without reclaim invite.
        self.assertTrue(dimmed(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=0))
        self.assertFalse(dimmed(
            PUNCHLINE, {}, seedPollution=0.70, pure=0.0, unlockedThrough=1))
        self.assertFalse(dimmed(
            LOOPY, {}, seedPollution=0.55, pure=0.0, unlockedThrough=0))
        self.assertEqual(
            rg.streetPackRequiredActIndex(PUNCHLINE), 1)
        self.assertEqual(
            rg.streetPackRequiredActIndex(SILLY), 2)

        crumb_src = _read('toontown/safezone/CorruptStreetBreadcrumb.py')
        self.assertIn("self.accept('campaignActUnlocked'", crumb_src)
        self.assertIn('_onCampaignActUnlocked', crumb_src)
        self.assertIn("mode == 'dim'", crumb_src)
        self.assertIn('streetBreadcrumbDimmed', crumb_src)
        self.assertIn('unlockedThrough=unlocked', crumb_src)
        # Login sync rehydrates unlock latch so crumbs undim after relog.
        self.assertIn('_onCampaignProgressSync', crumb_src)
        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', crumb_src)
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn("self.accept('campaignActUnlocked'", play_src)
        self.assertIn('_onCampaignActUnlocked', play_src)
        self.assertIn('_mirrorCampaignActUnlocked', play_src)
        self.assertIn('noteCampaignActUnlocked', play_src)
        play_sync_idx = play_src.find('def _onCampaignProgressSync')
        self.assertGreater(play_sync_idx, 0)
        play_sync_next = play_src.find('\n    def ', play_sync_idx + 1)
        play_sync = play_src[
            play_sync_idx:(
                play_sync_next if play_sync_next > 0
                else play_sync_idx + 1800)]
        self.assertIn('noteCampaignActUnlocked', play_sync)
        director_src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn("'campaignActUnlocked'", director_src)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, crumb_src.lower())

    # --- fight leg: archetypes + soft-lock / melee juice ---

    def test_fight_leg_archetypes_and_overlord(self):
        cg = self.cg
        expected = {
            'Ink Smudge', 'Sludge Brute', 'Balloon Snare', 'Gunk Gagster'}
        names = set(cg.ARCHETYPE_NAMES.values())
        self.assertTrue(expected.issubset(names), msg=expected - names)

        for archetype_id, label in (
                (cg.ARCHETYPE_INK, 'Ink Smudge'),
                (cg.ARCHETYPE_BRUTE, 'Sludge Brute'),
                (cg.ARCHETYPE_SNARE, 'Balloon Snare'),
                (cg.ARCHETYPE_GAGSTER, 'Gunk Gagster')):
            self.assertEqual(cg.archetypeDefaultName(archetype_id), label)
            self.assertIn(archetype_id, cg.ARCHETYPE_STATS)

        ink = cg.ARCHETYPE_STATS[cg.ARCHETYPE_INK]
        self.assertEqual(ink.get('attackMove'), 'ink_dash')
        self.assertTrue(cg.INK_SMUDGE_KIT_ENABLED)
        gagster = cg.ARCHETYPE_STATS[cg.ARCHETYPE_GAGSTER]
        self.assertEqual(gagster.get('attackMove'), 'gag_lob')
        brute = cg.ARCHETYPE_STATS[cg.ARCHETYPE_BRUTE]
        self.assertEqual(brute.get('attackMove'), 'spit')
        self.assertTrue(cg.BRUTE_SPIT_PROJECTILE_ENABLED)
        self.assertTrue(cg.BRUTE_SLAM_SECONDARY_ENABLED)
        oswald = cg.ARCHETYPE_STATS[cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertEqual(oswald.get('attackMove'), 'betrayal_lunge')
        self.assertTrue(cg.OSWALD_BETRAYAL_KIT_ENABLED)

        # Ink Overlord is finale-only (not a street ARCHETYPE_* id).
        self.assertEqual(cg.FINALE_PHASE_LOOK[1].get('id'), 'rising')
        self.assertEqual(cg.FINALE_PHASE_LOOK[2].get('id'), 'unleashed')
        self.assertEqual(cg.OVERLORD_PHASE_COMBAT[1].get('moveMode'), 'rising')
        self.assertEqual(cg.OVERLORD_PHASE_COMBAT[2].get('moveMode'), 'enrage')
        self.assertEqual(cg.overlordP2AddCount(1), 0)
        self.assertGreater(cg.overlordP2AddCount(2), 0)

    def test_soft_lock_and_melee_juice_presence(self):
        soft, cfg = self.soft, self.hs_cfg
        cg = self.cg
        # Config armed for sticky soft-lock cycle + hit assist.
        self.assertTrue(cfg.TARGET_CYCLE_ENABLED)
        self.assertEqual(cfg.TARGET_CYCLE_NEXT_KEY, 'tab')
        self.assertEqual(cfg.TARGET_CYCLE_PREV_KEY, '`')
        self.assertTrue(cfg.LOCK_HIT_ASSIST_ENABLED)
        self.assertGreater(cfg.TARGET_RANGE, 0.0)
        self.assertGreaterEqual(cfg.TARGET_CYCLE_RANGE, cfg.TARGET_RANGE)

        # Pure helpers used by SoftTargetFinder.cycle / aim nudge.
        keys = [('doId', 1), ('doId', 2), ('doId', 3)]
        self.assertEqual(soft.nextCycleIndex(3, 0, 1), 1)
        self.assertEqual(soft.nextCycleIndex(3, 2, 1), 0)
        self.assertEqual(
            soft.pickCycleChoice(keys, ('doId', 1), 1),
            (('doId', 2), True))
        self.assertTrue(soft.shouldAssistAimOnHit(('doId', 1), ('doId', 1)))
        self.assertFalse(soft.shouldAssistAimOnHit(('doId', 1), ('doId', 2)))
        nudge = soft.assistAimYawNudge(20.0, frac=0.5, maxDeg=12.0, deadzoneDeg=0.0)
        self.assertGreater(nudge, 0.0)
        self.assertLessEqual(nudge, 12.0)

        # Soft-lock prefers Overlord / Corrupted Oswald over nearer pack adds
        # (#339) — climax/twist targeting must not glue to Smudge trash.
        self.assertTrue(cfg.TARGET_PRIORITY_ENABLED)
        rank = soft.softLockAcquireRank
        self.assertLess(rank(12.0, True), rank(3.0, False))
        self.assertLess(rank(5.0, True), rank(5.0, False))
        pick = soft.pickSoftLockAcquire
        smudge = ('doId', 1)
        overlord = ('doId', 2)
        oswald = ('doId', 3)
        self.assertEqual(
            pick([(False, 2.5, smudge), (True, 11.0, overlord)]),
            overlord)
        self.assertEqual(
            pick([(False, 1.0, smudge), (True, 10.5, oswald)]),
            oswald)
        self.assertEqual(
            pick([(False, 6.0, ('doId', 4)), (False, 3.0, smudge)]),
            smudge)
        subject = cg.isSoftLockPrioritySubject
        self.assertFalse(subject(cg.ARCHETYPE_INK))
        self.assertFalse(subject(cg.ARCHETYPE_BRUTE))
        self.assertTrue(subject(cg.ARCHETYPE_CORRUPT_OSWALD))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='Ink Overlord'))
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=1))
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=2))
        # Elite / Ambush rename prefixes permanently prefer (#375) — mid-wave
        # scrums must not glue onto nearer fodder (distinct from #372 pulse).
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ink Smudge'))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Elite'))
        self.assertFalse(subject(cg.ARCHETYPE_INK, name='Ambush'))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='Elite Ink Smudge'))
        self.assertTrue(subject(
            cg.ARCHETYPE_BRUTE, name='Ambush Sludge Brute'))
        self.assertTrue(subject(cg.ARCHETYPE_INK, name='elite ink smudge'))
        elite = ('doId', 5)
        ambush = ('doId', 6)
        self.assertEqual(
            pick([(False, 2.0, smudge), (True, 11.0, elite)]),
            elite)
        self.assertEqual(
            pick([(False, 1.5, smudge), (True, 10.0, ambush)]),
            ambush)
        soft_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('pickSoftLockAcquire', soft_src)
        self.assertIn('isSoftLockPrioritySubject', soft_src)
        self.assertIn('TARGET_PRIORITY_ENABLED', soft_src)
        self.assertIn('Elite / Ambush', soft_src)
        cg_src = _read('toontown/corruption/CorruptionGlobals.py')
        self.assertIn("startswith('elite ')", cg_src)
        self.assertIn("startswith('ambush ')", cg_src)
        # Sticky hold yields glued adds when Overlord/Oswald is in cone (#347).
        self.assertIn('shouldStickyYieldToPriority', soft_src)
        self.assertGreater(cfg.TARGET_LOCK_HOLD_SEC, 0.0)
        self.assertTrue(
            soft.shouldStickyYieldToPriority(False, True))
        self.assertFalse(
            soft.shouldStickyYieldToPriority(True, True))
        self.assertFalse(
            soft.shouldStickyYieldToPriority(False, False))
        self.assertFalse(
            soft.shouldStickyYieldToPriority(False, True, enabled=False))
        # Yield then #339 pick: nearer Smudge loses to Overlord / Oswald.
        self.assertEqual(
            pick([(False, 2.5, smudge), (True, 11.0, overlord)]),
            overlord)
        self.assertEqual(
            pick([(False, 1.0, smudge), (True, 10.5, oswald)]),
            oswald)
        acquire_names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            'acquire')
        for need in (
                'shouldStickyYieldToPriority', '_isPriorityTarget',
                'pickSoftLockAcquire', '_inStickyCone',
                'TARGET_LOCK_HOLD_SEC'):
            self.assertIn(need, acquire_names, msg='acquire missing %s' % need)
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('sticky hold yield', cfg_src.lower())
        # Tab/` cycle-with-lock jumps to Overlord/Oswald over yaw-orbit.
        self.assertIn('shouldCyclePreferPriority', soft_src)
        self.assertTrue(
            soft.shouldCyclePreferPriority(False, True))
        self.assertFalse(
            soft.shouldCyclePreferPriority(True, True))
        self.assertFalse(
            soft.shouldCyclePreferPriority(False, False))
        self.assertFalse(
            soft.shouldCyclePreferPriority(False, True, enabled=False))
        cycle_names = _method_body_names(
            'toontown/hackslash/SoftTarget.py',
            'SoftTargetFinder',
            'cycle')
        for need in (
                'shouldCyclePreferPriority', '_isPriorityTarget',
                'pickSoftLockAcquire', 'pickCycleChoice'):
            self.assertIn(need, cycle_names, msg='cycle missing %s' % need)
        self.assertIn('cycle-with-lock', cfg_src.lower())
        hs_init = _read('toontown/hackslash/__init__.py')
        self.assertIn('softLockAcquireRank', hs_init)
        self.assertIn('pickSoftLockAcquire', hs_init)
        self.assertIn('shouldStickyYieldToPriority', hs_init)
        self.assertIn('shouldCyclePreferPriority', hs_init)

        melee_tree = _module_ast('toontown/hackslash/MeleeCombat.py')
        melee_methods = _class_method_names(melee_tree, 'MeleeCombatController')
        for method in (
                '_cycleSoftLockTarget', '_onCycleNextPressed',
                '_onCyclePrevPressed', '_assistAimOnHit',
                '_updateSoftLockReticle'):
            self.assertIn(
                method, melee_methods,
                msg='MeleeCombatController missing %s' % method)
        melee_src = _read('toontown/hackslash/MeleeCombat.py')
        self.assertIn('TARGET_CYCLE_ENABLED', melee_src)
        self.assertIn('LOCK_HIT_ASSIST_ENABLED', melee_src)
        self.assertIn('SoftLockReticleFx', melee_src)

        # Authoritative server melee from hitIndex (#366) — fight integrity
        # for the whole explore→fight→reclaim loop (no client-trusted amount).
        dmg = cfg.meleeDamageFromHitIndex
        table = cfg.COMBO_DAMAGE
        self.assertEqual(len(table), cfg.COMBO_LENGTH)
        for idx, expected in enumerate(table):
            self.assertEqual(dmg(idx), int(expected))
        self.assertEqual(dmg(99), int(table[-1]))
        self.assertEqual(dmg(-1), int(table[0]))
        flag = int(cfg.MELEE_COUNTER_FLAG_PERFECT_DODGE)
        self.assertGreater(dmg(0, flag), int(table[0]))
        self.assertEqual(
            dmg(0, flag),
            cfg.perfectDodgeCounterOpenerDamage(int(table[0])))
        self.assertEqual(
            dmg(0, 0, damageTable=(999, 999, 999)),
            int(cfg.MELEE_DAMAGE_MAX))
        self.assertLessEqual(int(cfg.MELEE_DAMAGE_MAX), 80)
        cfg_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('def meleeDamageFromHitIndex', cfg_src)
        dmg_blob = cfg_src.split('def meleeDamageFromHitIndex', 1)[1][:700].lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, dmg_blob)
        corrupt_ai = _read('toontown/corruption/DistributedCorruptToonAI.py')
        req_idx = corrupt_ai.find('def requestHackSlashHit')
        self.assertGreater(req_idx, 0)
        req_snip = corrupt_ai[
            req_idx:corrupt_ai.find('\n    def ', req_idx + 1)]
        self.assertIn('hitIndex', req_snip)
        self.assertIn('counterFlags', req_snip)
        self.assertIn('meleeDamageFromHitIndex', req_snip)
        # CampaignPower reclaimCount table push (#371) — AI hit path must
        # scale from director reclaimCount, not process baseline alone.
        self.assertIn('__campaignPowerDamageTable', req_snip)
        self.assertIn('damageTable=table', req_snip)
        self.assertNotIn('min(80', req_snip)
        self.assertNotIn('damage=', req_snip.split('(', 1)[1].split(')', 1)[0])
        self.assertIn('takeHackSlashDamage(amount', req_snip)
        corrupt_client = _read(
            'toontown/corruption/DistributedCorruptToon.py')
        self.assertIn(
            "sendUpdate('requestHackSlashHit', [idx, flags])",
            corrupt_client)
        self.assertIn('_pendingCounterFlags', melee_src)
        self.assertIn('MELEE_COUNTER_FLAG_PERFECT_DODGE', melee_src)
        dc = _read('etc/toon.dc')
        self.assertIn('requestHackSlashHit(uint8, uint8)', dc)
        self.assertNotIn('requestHackSlashHit(uint16, uint8)', dc)
        self.assertIn('meleeDamageFromHitIndex', hs_init)
        target_src = _read('toontown/corruption/HackSlashTarget.py')
        self.assertIn('meleeDamageFromHitIndex', target_src)
        self.assertIn('counterFlags', target_src)

        # Soft-lock reticle / hit-assist cream modules stay registered.
        for rel in (
                'toontown/hackslash/SoftLockReticleFx.py',
                'toontown/hackslash/SoftLockCycleCreamWashFx.py',
                'toontown/hackslash/HitAssistCreamWashFx.py'):
            self.assertTrue(
                (REPO_ROOT / rel).is_file(), msg='missing %s' % rel)

    def test_fight_kits_juggle_stun_and_reclaim_ko(self):
        """Archetype kits + hang stun + KO→contested fail stay on the fight leg."""
        cg, cfg = self.cg, self.hs_cfg
        # Distinct attack moves across street kits + betrayal Oswald.
        self.assertEqual(cg.inkPickAttackMove(8.0), 'ink_dash')
        self.assertEqual(cg.inkPickAttackMove(2.0), 'ink_splat')
        self.assertTrue(cg.INK_SMUDGE_KIT_ENABLED)
        self.assertTrue(cg.INK_SPLAT_SECONDARY_ENABLED)
        self.assertTrue(cg.SNARE_LASH_YANK_ENABLED)
        dx, dy = cg.snareLashYankDelta(0.0, 0.0, 10.0, 0.0, dist=2.0, stop=1.5)
        self.assertLess(dx, 0.0)
        self.assertAlmostEqual(dy, 0.0, places=5)
        self.assertTrue(cg.ROLE_AI_ENABLED)
        self.assertEqual(
            cg.archetypeCombatRole(cg.ARCHETYPE_INK), cg.ROLE_ORBIT)
        self.assertEqual(
            cg.archetypeCombatRole(cg.ARCHETYPE_BRUTE), cg.ROLE_HOLD)
        self.assertEqual(
            cg.archetypeCombatRole(cg.ARCHETYPE_GAGSTER), cg.ROLE_KITE)
        self.assertEqual(
            cg.archetypeCombatRole(cg.ARCHETYPE_SNARE), cg.ROLE_FLANK)
        self.assertEqual(cg.oswaldPickAttackMove(8.0), 'betrayal_lunge')
        self.assertEqual(cg.oswaldPickAttackMove(2.0), 'stain_burst')
        self.assertTrue(cg.OSWALD_BETRAYAL_KIT_ENABLED)
        self.assertTrue(cg.OSWALD_BETRAYAL_SHOVE_ENABLED)

        # Server stun covers the juggle cancel window (#310).
        self.assertTrue(cfg.JUGGLE_HANG_STUN_ENABLED)
        mid_idx = cfg.LAUNCH_HIT_INDEX
        mid = cfg.juggleHangStunSec(mid_idx)
        self.assertGreater(mid, 0.0)
        corrupt_ai = _read('toontown/corruption/DistributedCorruptToonAI.py')
        for needle in (
                '__applyJuggleHangStun', 'isJuggleHangStunned',
                'juggleHangStunSec', 'JUGGLE_HANG_STUN_ENABLED'):
            self.assertIn(needle, corrupt_ai, msg='AI missing %s' % needle)

        # Melee mid-telegraph interrupt covers Snare + Brute spit + Gagster lob
        # + Overlord rain/slam/ink_surge + Smudge ink_dash/ink_splat + Oswald
        # betrayal_lunge/stain_burst.
        self.assertTrue(cg.BRUTE_SPIT_MELEE_INTERRUPT)
        self.assertTrue(cg.GAGSTER_LOB_MELEE_INTERRUPT)
        self.assertTrue(cg.OVERLORD_RAIN_MELEE_INTERRUPT)
        self.assertTrue(cg.OVERLORD_SLAM_MELEE_INTERRUPT)
        self.assertTrue(cg.OVERLORD_INK_SURGE_MELEE_INTERRUPT)
        self.assertTrue(cg.INK_DASH_MELEE_INTERRUPT)
        self.assertTrue(cg.INK_SPLAT_MELEE_INTERRUPT)
        self.assertTrue(cg.OSWALD_BETRAYAL_LUNGE_MELEE_INTERRUPT)
        self.assertTrue(cg.OSWALD_STAIN_BURST_MELEE_INTERRUPT)
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_BRUTE, 'spit'))
        self.assertFalse(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_BRUTE, 'slam'))
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_GAGSTER, 'gag_lob'))
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_INK, 'rain'))
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_INK, 'slam'))
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_INK, 'ink_surge'))
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_INK, 'ink_dash'))
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_INK, 'ink_splat'))
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_CORRUPT_OSWALD, 'betrayal_lunge'))
        self.assertTrue(cg.isMeleeInterruptibleTelegraph(
            cg.ARCHETYPE_CORRUPT_OSWALD, 'stain_burst'))
        self.assertIn('__maybeInterruptMeleeTelegraph', corrupt_ai)
        # Smudge interrupt rides the shared takeHackSlashDamage path (#363).
        take_idx = corrupt_ai.find('def takeHackSlashDamage')
        self.assertGreater(take_idx, 0)
        take_snip = corrupt_ai[take_idx:corrupt_ai.find('\n    def ', take_idx + 1)]
        self.assertIn('__maybeInterruptMeleeTelegraph', take_snip)
        take_l = take_snip.lower()
        self.assertIn('ink_dash', take_l)
        self.assertIn('ink_splat', take_l)
        # Dedicated counter windows (beyond interrupt) for spit / lob /
        # Oswald / Overlord rain·slam·ink_surge / Smudge ink_dash·ink_splat.
        self.assertTrue(cg.BRUTE_SPIT_COUNTER_ENABLED)
        self.assertTrue(cg.GAGSTER_LOB_COUNTER_ENABLED)
        self.assertTrue(cg.OSWALD_BETRAYAL_LUNGE_COUNTER_ENABLED)
        self.assertTrue(cg.OSWALD_STAIN_BURST_COUNTER_ENABLED)
        self.assertTrue(cg.OVERLORD_RAIN_COUNTER_ENABLED)
        self.assertTrue(cg.OVERLORD_SLAM_COUNTER_ENABLED)
        self.assertTrue(cg.OVERLORD_INK_SURGE_COUNTER_ENABLED)
        self.assertTrue(cg.INK_DASH_COUNTER_ENABLED)
        self.assertTrue(cg.INK_SPLAT_COUNTER_ENABLED)
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_BRUTE, 'spit'))
        self.assertFalse(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_BRUTE, 'slam'))
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_GAGSTER, 'gag_lob'))
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_CORRUPT_OSWALD, 'betrayal_lunge'))
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_CORRUPT_OSWALD, 'stain_burst'))
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_INK, 'rain'))
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_INK, 'slam'))
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_INK, 'ink_surge'))
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_INK, 'ink_dash'))
        self.assertTrue(cg.isDedicatedTelegraphCounterMove(
            cg.ARCHETYPE_INK, 'ink_splat'))
        corrupt_client = _read('toontown/corruption/DistributedCorruptToon.py')
        melee_src = _read('toontown/hackslash/MeleeCombat.py')
        self.assertIn('__scheduleBruteSpitCounter', corrupt_client)
        self.assertIn('__scheduleGagsterLobCounter', corrupt_client)
        self.assertIn('__scheduleOswaldBetrayalLungeCounter', corrupt_client)
        self.assertIn('__scheduleOswaldStainBurstCounter', corrupt_client)
        self.assertIn('__scheduleOverlordRainCounter', corrupt_client)
        self.assertIn('__scheduleOverlordSlamCounter', corrupt_client)
        self.assertIn('__scheduleOverlordInkSurgeCounter', corrupt_client)
        self.assertIn('__scheduleInkDashCounter', corrupt_client)
        self.assertIn('__scheduleInkSplatCounter', corrupt_client)
        self.assertIn('_onBruteSpitCounter', melee_src)
        self.assertIn('_onGagsterLobCounter', melee_src)
        self.assertIn('_onOswaldBetrayalLungeCounter', melee_src)
        self.assertIn('_onOswaldStainBurstCounter', melee_src)
        self.assertIn('_onOverlordRainCounter', melee_src)
        self.assertIn('_onOverlordSlamCounter', melee_src)
        self.assertIn('_onOverlordInkSurgeCounter', melee_src)
        self.assertIn('_onInkDashCounter', melee_src)
        self.assertIn('_onInkSplatCounter', melee_src)

        # Player KO during reclaim is an authored fail (#323/#324) + retry clear.
        rg = self.rg
        self.assertIn('fail', str(rg.BANNER_FAILED).lower())
        self.assertIn('knocked out', str(rg.BANNER_FAILED_SUB).lower())
        self.assertIn('Oswald', rg.BANNER_FAILED_SUB)
        fail_sub = str(rg.BANNER_FAILED_SUB).lower()
        self.assertTrue(
            'press r' in fail_sub or 're-enter' in fail_sub,
            msg='KO fail sub must cue press R / re-enter retry')
        self.assertTrue(hasattr(rg, 'BANNER_FAILED_RETRY_TIP'))
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, str(rg.BANNER_FAILED).lower())
            self.assertNotIn(banned, str(rg.BANNER_FAILED_SUB).lower())
        ai_src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('failStreetOnKnockout', ai_src)
        self.assertIn('announceReclaimFailed', ai_src)
        client_src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        self.assertIn('announceReclaimFailed', client_src)
        self.assertIn('BANNER_FAILED', client_src)
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn("self.accept('announceReclaimFailed'", play_src)
        self.assertIn('def _onReclaimFailed', play_src)
        fail_h = play_src.find('def _onReclaimFailed')
        self.assertGreater(fail_h, 0)
        fail_body = play_src[fail_h:play_src.find('\n    def ', fail_h + 1)]
        self.assertIn('self._reclaimLive = False', fail_body)
        # All corrupt damage paths (incl. stain_burst / ink_splat) share KO helper.
        for needle in (
                '__damageToonAndCheckReclaimKo',
                "context='stain_burst'",
                "context='ink_splat'",
                'failStreetOnKnockout'):
            self.assertIn(needle, corrupt_ai, msg='KO path missing %s' % needle)

    def test_fight_p1_rising_pressure_and_boss_hp_bar(self):
        """Overlord Rising slam (#334) + boss/chase HP bar (#331) stay readable."""
        cg = self.cg
        # P1 two-note kit: close slam or mid rain; ink_surge stays Unleashed-only.
        self.assertTrue(cg.OVERLORD_P1_SLAM_ENABLED)
        p1 = cg.overlordPhaseCombat(1)
        p2 = cg.overlordPhaseCombat(2)
        self.assertEqual(p1.get('moveMode'), 'rising')
        self.assertEqual(p2.get('moveMode'), 'enrage')
        for key in (
                'slamHitRange', 'slamNearMissRange', 'slamDamage',
                'slamTelegraphDelay', 'slamCooldown', 'slamMeleeRange'):
            self.assertIn(key, p1, msg='P1 missing %s' % key)
        for key in (
                'surgeMaxRange', 'surgeDash', 'surgeStop', 'surgeHitRange',
                'surgeDamage', 'surgeCooldown'):
            self.assertNotIn(key, p1, msg='P1 must not carry %s' % key)
            self.assertIn(key, p2, msg='P2 missing %s' % key)
        slam = cg.overlordSlamMeleeRange(p1)
        self.assertEqual(cg.overlordPickRisingMove(0.0, p1), 'slam')
        self.assertEqual(
            cg.overlordPickRisingMove(slam + 0.05, p1), 'rain')
        self.assertLess(p1['slamDamage'], p2['slamDamage'])
        corrupt_ai = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn('overlordPickRisingMove', corrupt_ai)
        self.assertIn("'rising'", corrupt_ai)

        # Boss / chase HP bar subjects: Overlord phases + Corrupted Oswald.
        self.assertTrue(cg.BOSS_HP_BAR_ENABLED)
        self.assertGreater(float(cg.BOSS_HP_BAR_WIDTH), 0.5)
        self.assertIn('Overlord', cg.BOSS_HP_BAR_DEFAULT_OVERLORD_LABEL)
        self.assertIn('Oswald', cg.BOSS_HP_BAR_DEFAULT_OSWALD_LABEL)
        self.assertFalse(cg.isBossOrChaseHpBarSubject(cg.ARCHETYPE_INK))
        self.assertFalse(cg.isBossOrChaseHpBarSubject(cg.ARCHETYPE_BRUTE))
        self.assertTrue(cg.isBossOrChaseHpBarSubject(cg.ARCHETYPE_CORRUPT_OSWALD))
        self.assertTrue(cg.isBossOrChaseHpBarSubject(
            cg.ARCHETYPE_INK, finalePhase=1))
        self.assertTrue(cg.isBossOrChaseHpBarSubject(
            cg.ARCHETYPE_INK, finalePhase=2))
        self.assertEqual(cg.bossHpBarRatio(50, 100), 0.5)
        self.assertEqual(cg.bossHpBarRatio(0, 100), 0.0)
        hud_rel = 'toontown/reclaim/BossHpBarHud.py'
        self.assertTrue((REPO_ROOT / hud_rel).is_file())
        hud_names = _class_and_func_names(_module_ast(hud_rel))
        for sym in (
                'BossHpBarHud', 'syncFromCorruptToon', 'releaseCorruptToon',
                'hideBossHpBar', 'destroyBossHpBar'):
            self.assertIn(sym, hud_names)
        hud_src = _read(hud_rel)
        self.assertIn('boss-chase-hp-bar', hud_src)
        self.assertNotIn('CreamWash', hud_src)
        corrupt_client = _read('toontown/corruption/DistributedCorruptToon.py')
        self.assertIn('BossHpBarHud', corrupt_client)
        self.assertIn('syncBossHpBar', corrupt_client)
        self.assertIn('releaseBossHpBar', corrupt_client)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, hud_src.lower())

    def test_fight_overlord_telegraph_move_id(self):
        """Overlord telegraph carries rain / slam / ink_surge (#340)."""
        cg = self.cg
        self.assertEqual(
            set(cg.OVERLORD_TELEGRAPH_MOVES),
            {'rain', 'slam', 'ink_surge'})
        self.assertEqual(cg.normalizeOverlordTelegraphMove('RAIN'), 'rain')
        self.assertEqual(
            cg.normalizeOverlordTelegraphMove('ink_surge'), 'ink_surge')
        self.assertEqual(cg.normalizeOverlordTelegraphMove('spit'), '')
        self.assertTrue(cg.overlordTelegraphShowsInkRain('rain'))
        self.assertFalse(cg.overlordTelegraphShowsInkRain('slam'))
        self.assertFalse(cg.overlordTelegraphShowsInkRain('ink_surge'))
        for move in ('rain', 'slam', 'ink_surge'):
            self.assertTrue(
                cg.overlordTelegraphShowsPunchWarn(move),
                msg='%s should show punch warn' % move)

        p2 = cg.overlordPhaseCombat(2)
        rain_r = cg.overlordTelegraphMoveHitRange('rain', 2, p2)
        slam_r = cg.overlordTelegraphMoveHitRange('slam', 2, p2)
        surge_r = cg.overlordTelegraphMoveHitRange('ink_surge', 2, p2)
        self.assertAlmostEqual(rain_r, float(p2['attackHitRange']))
        self.assertAlmostEqual(slam_r, float(p2['slamHitRange']))
        self.assertAlmostEqual(surge_r, float(p2['surgeHitRange']))
        self.assertLess(slam_r, surge_r)
        self.assertLess(surge_r, rain_r)
        slam_cue = cg.overlordTelegraphMoveHudCue('slam', 1, None)
        self.assertIn('SLAM', slam_cue)
        surge_cue = cg.overlordTelegraphMoveHudCue('ink_surge', 2, None)
        self.assertIn('SURGE', surge_cue)

        dc = _read('etc/toon.dc')
        self.assertIn('announceAttackTelegraph(string) broadcast;', dc)
        self.assertNotIn('announceAttackTelegraph() broadcast;', dc)
        corrupt_ai = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn(
            "sendUpdate('announceAttackTelegraph', [str(move or '')])",
            corrupt_ai)
        self.assertNotIn(
            "sendUpdate('announceAttackTelegraph', [])", corrupt_ai)

        client_src = _read('toontown/corruption/DistributedCorruptToon.py')
        telegraph = client_src[client_src.find('def announceAttackTelegraph'):]
        telegraph_end = telegraph.find('\n    def ', 1)
        body = telegraph if telegraph_end < 0 else telegraph[:telegraph_end]
        self.assertIn('moveId', body)
        self.assertIn('normalizeOverlordTelegraphMove', body)
        self.assertIn('overlordTelegraphShowsInkRain', body)
        self.assertIn('overlordTelegraphShowsPunchWarn', body)
        self.assertIn('overlordTelegraphMoveHudCue', body)
        self.assertIn('_telegraphMove', body)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, body.lower())

    # --- reclaim leg: wave scripts + director hooks ---

    def test_wave_scripts_resolve_across_loop_acts(self):
        rg, cg = self.rg, self.cg
        for act in self.acts:
            scripts = act.get('waveScripts')
            self.assertTrue(scripts, msg='%s missing waveScripts' % act['id'])
            for wave_i, _ in enumerate(scripts, start=1):
                resolved = rg.resolveWaveScript(scripts, wave_i)
                self.assertIsNotNone(
                    resolved,
                    msg='%s wave %s did not resolve' % (act['id'], wave_i))
                self.assertGreaterEqual(len(resolved), 1)
                size = rg.wavePackSize(
                    act['packSize'], wave_i, waveScript=resolved)
                self.assertEqual(size, len(resolved))

        # Finale P2 unleashed scripts also resolve and stay Overlord-only ink.
        phase2 = self.act_by_id['finale']['phase2']
        p2_scripts = phase2.get('waveScripts')
        self.assertTrue(p2_scripts)
        for wave_i, _ in enumerate(p2_scripts, start=1):
            resolved = rg.resolveWaveScript(p2_scripts, wave_i)
            self.assertIsNotNone(resolved)
            for archetype_id in resolved:
                self.assertEqual(
                    archetype_id, cg.ARCHETYPE_INK,
                    msg='P2 wave %s must stay Overlord ink, got %r'
                    % (wave_i, archetype_id))
        # Story P2 elite/ambush beside Unleashed Smudge adds (no R HP promote).
        self.assertEqual(phase2.get('addWaveStart'), 2)
        self.assertIn('waveModifiers', phase2)
        self.assertIn('ambushBeats', phase2)
        self.assertTrue(
            rg.waveIsElite(
                rg.resolveWaveModifiers(phase2['waveModifiers'], 2)))
        self.assertTrue(
            rg.waveIsElite(
                rg.resolveWaveModifiers(phase2['waveModifiers'], 3)))
        self.assertEqual(
            rg.resolveAmbushBeat(phase2['ambushBeats'], 1),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveAmbushBeat(phase2['ambushBeats'], 2),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertNotIn('overlordP2HpFrac', phase2)

        # STREET_PACKS scripts stay distinct across the three hoods.
        loopy = rg.resolveWaveScript(
            rg.streetPack(LOOPY)['waveScripts'], 1)
        punch = rg.resolveWaveScript(
            rg.streetPack(PUNCHLINE)['waveScripts'], 1)
        silly = rg.resolveWaveScript(
            rg.streetPack(SILLY)['waveScripts'], 1)
        self.assertEqual(loopy, [cg.ARCHETYPE_INK] * 3)
        self.assertIn(cg.ARCHETYPE_GAGSTER, punch)
        self.assertEqual(silly, [cg.ARCHETYPE_INK])

        # Elite last-wave buffs + earlier-wave ambush beats + Silly
        # between-swell pressure — not composition-only tokens.
        self.assertGreater(rg.ELITE_HP_MULT, 1.0)
        self.assertGreater(rg.ELITE_DAMAGE_MULT, 1.0)
        self.assertGreater(rg.AMBUSH_DELAY, 0.0)
        self.assertLess(rg.AMBUSH_DELAY, rg.WAVE_SPAWN_DELAY)
        loopy_pack = rg.streetPack(LOOPY)
        punch_pack = rg.streetPack(PUNCHLINE)
        silly_pack = rg.streetPack(SILLY)
        loopy_mods = rg.resolveWaveModifiers(loopy_pack['waveModifiers'], 4)
        self.assertTrue(rg.waveIsElite(loopy_mods))
        self.assertEqual(rg.waveHpMult(loopy_mods), rg.ELITE_HP_MULT)
        self.assertEqual(
            rg.resolveAmbushBeat(loopy_pack['ambushBeats'], 1),
            [cg.ARCHETYPE_INK])
        self.assertEqual(
            rg.resolveAmbushBeat(loopy_pack['ambushBeats'], 2),
            [cg.ARCHETYPE_SNARE])
        self.assertEqual(
            rg.resolveAmbushBeat(loopy_pack['ambushBeats'], 3),
            [cg.ARCHETYPE_SNARE])
        punch_mods = rg.resolveWaveModifiers(punch_pack['waveModifiers'], 4)
        self.assertTrue(rg.waveIsElite(punch_mods))
        self.assertEqual(
            rg.resolveAmbushBeat(punch_pack['ambushBeats'], 1),
            [cg.ARCHETYPE_GAGSTER])
        self.assertEqual(
            rg.resolveAmbushBeat(punch_pack['ambushBeats'], 3),
            [cg.ARCHETYPE_GAGSTER, cg.ARCHETYPE_SNARE])
        # Silly between-swell ambush + elite twin swell tables.
        self.assertIn('waveModifiers', silly_pack)
        self.assertIn('ambushBeats', silly_pack)
        silly_mods = rg.resolveWaveModifiers(silly_pack['waveModifiers'], 2)
        self.assertTrue(rg.waveIsElite(silly_mods))
        self.assertEqual(
            rg.resolveAmbushBeat(silly_pack['ambushBeats'], 1),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        for zone in (LOOPY, PUNCHLINE, SILLY):
            params = rg.streetPackParams(zone)
            self.assertIn('waveModifiers', params)
            self.assertIn('ambushBeats', params)

        # Campaign ACTS C path mirrors the same elite/ambush tables
        # (Loopy depth aligned to 4 + elite; no overlordP2HpFrac on C).
        act_by_id = {a['id']: a for a in self.acts}
        loopy_act = act_by_id['loopy']
        punch_act = act_by_id['punchline']
        finale_act = act_by_id['finale']
        self.assertEqual(loopy_act['maxPacks'], 4)
        self.assertEqual(len(loopy_act['waveScripts']), 4)
        self.assertEqual(
            loopy_act['waveModifiers'], loopy_pack['waveModifiers'])
        self.assertEqual(
            loopy_act['ambushBeats'], loopy_pack['ambushBeats'])
        self.assertEqual(
            punch_act['waveModifiers'], punch_pack['waveModifiers'])
        self.assertEqual(
            punch_act['ambushBeats'], punch_pack['ambushBeats'])
        self.assertEqual(
            finale_act['waveModifiers'], silly_pack['waveModifiers'])
        self.assertEqual(
            finale_act['ambushBeats'], silly_pack['ambushBeats'])
        self.assertNotIn('overlordP2HpFrac', finale_act)
        # Finale C phase2 replaces P1 tables with Unleashed elite/ambush.
        p2 = finale_act['phase2']
        self.assertNotEqual(p2['waveModifiers'], finale_act['waveModifiers'])
        self.assertNotEqual(p2['ambushBeats'], finale_act['ambushBeats'])
        self.assertTrue(
            rg.waveIsElite(
                rg.resolveWaveModifiers(p2['waveModifiers'], 3)))
        self.assertEqual(
            rg.resolveAmbushBeat(p2['ambushBeats'], 2),
            [cg.ARCHETYPE_INK, cg.ARCHETYPE_INK])
        self.assertNotIn('overlordP2HpFrac', p2)
        base_hp = 46
        elite_hp = rg.applyElitePackHp(base_hp, loopy_mods)
        self.assertGreater(elite_hp, base_hp)
        self.assertEqual(
            rg.applyElitePackName('Ink Smudge', loopy_mods),
            rg.ELITE_NAME_PREFIX + 'Ink Smudge')
        self.assertIn('ambush', rg.waveClearedOswaldTip(1, zoneId=LOOPY).lower())
        self.assertIn('ambush', rg.waveClearedOswaldTip(3, zoneId=LOOPY).lower())
        self.assertIn('ambush', rg.waveClearedOswaldTip(1, zoneId=SILLY).lower())
        self.assertIn('Elite', rg.waveAnnounceTitle(4, 4, zoneId=LOOPY))
        self.assertIn('elite', rg.waveOswaldTip(2, 2, zoneId=SILLY).lower())
        self.assertIn('ambush', rg.ambushOswaldTip(3, zoneId=LOOPY).lower())
        self.assertIn('ambush', rg.ambushOswaldTip(1, zoneId=SILLY).lower())
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            tip_blob = ' '.join([
                rg.waveClearedOswaldTip(1, zoneId=LOOPY),
                rg.waveClearedOswaldTip(3, zoneId=LOOPY),
                rg.waveClearedOswaldTip(1, zoneId=SILLY),
                rg.ambushOswaldTip(1, zoneId=LOOPY),
                rg.ambushOswaldTip(3, zoneId=LOOPY),
                rg.ambushOswaldTip(1, zoneId=SILLY),
                rg.waveAnnounceTitle(4, 4, zoneId=LOOPY),
                rg.waveOswaldTip(2, 2, zoneId=SILLY),
            ]).lower()
            self.assertNotIn(banned, tip_blob)

    def test_reclaim_director_loop_hooks(self):
        ai_src = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        for needle in (
                'waveScripts=', 'resolveWaveScript', 'self._waveScripts = waveScripts',
                'finalePhase', '_spawnPack', 'STATE_COMPLETE',
                'neighborhoodReclaimed'):
            self.assertIn(needle, ai_src, msg='AI director missing %s' % needle)

        # Elite modifiers + between-wave ambush (#345) stay on the AI director.
        ai_methods = _class_method_names(
            _module_ast('toontown/reclaim/DistributedReclaimDirectorAI.py'),
            'DistributedReclaimDirectorAI')
        for method in (
                '_spawnAmbush', '_scheduleAmbushIfNeeded',
                '_applyEliteModifiers'):
            self.assertIn(
                method, ai_methods,
                msg='AI director missing elite/ambush %s' % method)
        for needle in (
                'announceAmbushSpawn', 'waveModifiers=None', 'ambushBeats=None',
                'applyElitePackHp', 'applyWaveDamageMultToStats',
                'resolveAmbushBeat'):
            self.assertIn(
                needle, ai_src, msg='AI director missing %s' % needle)

        # Campaign C path forwards the same elite/ambush kwargs (#365; no
        # R-only overlordP2HpFrac promote onto ACTS start).
        camp_ai = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('waveModifiers=params.get(', camp_ai)
        self.assertIn('ambushBeats=params.get(', camp_ai)
        self.assertNotIn('overlordP2HpFrac=params.get', camp_ai)

        client_src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        for needle in (
                'announceReclaimComplete', 'FINALE_TWIST_TEASE',
                'oswaldRevealSting', 'finalePhase >= 2',
                '__evaluatePurityPressure', 'warnPressure'):
            self.assertIn(
                needle, client_src,
                msg='client director missing %s' % needle)
        self.assertIn('def announceAmbushSpawn', client_src)
        self.assertIn('ambushOswaldTip', client_src)
        self.assertIn('reclaimAmbushSpawn', client_src)
        self.assertIn('__onAmbushSpawnCue', client_src)
        self.assertIn('ambushMsgName()', client_src)
        self.assertIn('ambushPressureTipText', client_src)
        rg = self.rg
        self.assertTrue(rg.AMBUSH_PRESSURE_TIP_ENABLED)
        self.assertEqual(rg.ambushMsgName(), 'reclaimAmbushSpawn')
        self.assertIn('ambush', rg.ambushPressureTipText(3, 2).lower())
        melee_src = _read('toontown/hackslash/MeleeCombat.py')
        self.assertIn('_onAmbushSpawnPrefer', melee_src)
        soft_lock_src = _read('toontown/hackslash/SoftTarget.py')
        self.assertIn('pulseAmbushPrefer', soft_lock_src)
        dc = _read('etc/toon.dc')
        self.assertIn('announceAmbushSpawn(uint8, uint8) broadcast;', dc)

        # Secured purity-lock sparkle stays on the reclaim complete path.
        self.assertTrue(
            (REPO_ROOT / 'toontown/reclaim/SecuredLockSparkleFx.py').is_file())
        self.assertIn('SecuredLockSparkle', client_src)

        # Power bump scales melee with reclaim count (campaign depth).
        # After #366 AI used baseline COMBO_DAMAGE; reclaimCount table push
        # restores reclaim→power→fight on the authoritative path.
        power_src = _read('toontown/campaign/CampaignPower.py')
        self.assertIn('applyPowerBump', power_src)
        self.assertIn('POWER_BUMP_PER_RECLAIM', power_src)
        self.assertIn('reclaimCount', power_src)
        self.assertIn('comboDamageTableFromReclaimCount', power_src)
        self.assertGreater(self.camp.POWER_BUMP_PER_RECLAIM, 0.0)
        self.assertGreater(self.camp.POWER_BUMP_MAX, self.camp.POWER_BUMP_PER_RECLAIM)
        hs_cfg = self.hs_cfg
        hs_src = _read('toontown/hackslash/HackSlashConfig.py')
        self.assertIn('def comboDamageTableFromReclaimCount', hs_src)
        self.assertIn('def powerBumpMultiplier', hs_src)
        per = self.camp.POWER_BUMP_PER_RECLAIM
        cap = self.camp.POWER_BUMP_MAX
        baseline = hs_cfg.COMBO_DAMAGE
        bumped = hs_cfg.comboDamageTableFromReclaimCount(
            2, baseTable=baseline, perReclaim=per, bumpMax=cap)
        self.assertGreater(bumped[0], baseline[0])
        self.assertEqual(
            hs_cfg.meleeDamageFromHitIndex(0, 0, damageTable=bumped),
            int(bumped[0]))
        corrupt_ai = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn('__campaignPowerDamageTable', corrupt_ai)
        self.assertIn('comboDamageTableFromReclaimCount', corrupt_ai)
        self.assertIn('getCampaignDirector', corrupt_ai)
        # Street-clear slice reward beyond COMBO_DAMAGE (jellybean / laff trophy).
        self.assertIn('awardStreetClearReward', power_src)
        self.assertIn('streetClearJellybeans', power_src)
        self.assertIs(self.camp.STREET_CLEAR_REWARD_ENABLED, True)
        self.assertGreater(self.camp.STREET_CLEAR_JELLYBEANS, 0)
        self.assertGreater(self.camp.STREET_CLEAR_LAFF, 0)
        self.assertIn('_awardStreetClearRewards', ai_src)
        self.assertIn('awardStreetClearReward', ai_src)
        # Login rehydrate (#349) + sync/purity dedupe (#367): silent AI reclaimCount.
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('applyPowerBump', handoff_src)
        self.assertIn('_applyReclaimPower', handoff_src)
        sync_idx = handoff_src.find('def _onCampaignProgressSync')
        self.assertGreater(sync_idx, 0)
        sync_win = handoff_src[sync_idx:sync_idx + 1100]
        self.assertIn('reclaimCount', sync_win)
        self.assertIn('_localReclaimCount', sync_win)
        self.assertIn('_syncedReclaimCount', sync_win)
        self.assertIn('applyPowerBump', sync_win)
        self.assertNotIn('_celebrate', sync_win)
        purity_idx = handoff_src.find('def _onPurityRestore')
        self.assertGreater(purity_idx, 0)
        purity_win = handoff_src[purity_idx:purity_idx + 1100]
        # Idempotent dedupe vs progress sync (#367) — no blind +=1.
        self.assertIn('_applyReclaimPower', purity_win)
        self.assertIn('self._localReclaimCount + 1', purity_win)
        self.assertNotIn('_localReclaimCount += 1', purity_win)
        self.assertIn('max(self._syncedReclaimCount', purity_win)
        self.assertIn('synced > self._localReclaimCount', purity_win)
        self.assertIn('rewardLine', purity_win)
        self.assertIn('_streetClearRewardLine', purity_win)

    # --- campaign progression + Oswald twist ---

    def test_campaign_director_progression_hooks(self):
        director_src = _read('toontown/campaign/CampaignDirectorAI.py')
        director_tree = _module_ast('toontown/campaign/CampaignDirectorAI.py')
        methods = _class_method_names(director_tree, 'CampaignDirectorAI')
        for method in (
                'startCampaign', 'advanceCampaign', '_actParams',
                '_startActReclaim', '__onNeighborhoodReclaimed'):
            self.assertIn(
                method, methods,
                msg='CampaignDirectorAI missing %s' % method)

        self.assertIn("self.accept('neighborhoodReclaimed'", director_src)
        # Finale P1 clear advances phase then restarts reclaim before victory.
        self.assertIn('self._finalePhase = 1', director_src)
        self.assertIn("act.get('finale') and self._finalePhase < 1", director_src)
        self.assertIn('campaignVictory', director_src)
        self.assertIn('campaignActUnlocked', director_src)
        self.assertIn('handoffTravelHint', director_src)
        self.assertNotIn('~startcampaign', director_src)

        # State table used by status / victory gating.
        self.assertEqual(self.camp.STATE_IDLE, 0)
        self.assertEqual(self.camp.STATE_ACTIVE, 1)
        self.assertEqual(self.camp.STATE_VICTORY, 2)
        self.assertEqual(self.camp.STATE_NAMES[self.camp.STATE_VICTORY], 'victory')

        # Pollution manager R path delegates soft-gate + campaign prefer.
        pollution_src = _read('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('startStreetPackForToon', pollution_src)
        self.assertIn('startCampaign', pollution_src)
        self.assertIn('markStreetSecured', pollution_src)
        self.assertIn('markStreetContested', pollution_src)
        # SECURED purity-lock persist across AI restart (#368) — district
        # JSON + campaign securedZones hydrate keep cleared streets sealed.
        self.assertTrue(
            (REPO_ROOT / 'toontown/corruption/PollutionSecuredSave.py').is_file())
        self.assertIs(self.cg.POLLUTION_SECURED_PERSIST_ENABLED, True)
        self.assertEqual(
            self.cg.POLLUTION_SECURED_FILENAME, 'pollution_secured.json')
        pollution_methods = _class_method_names(
            _module_ast('toontown/corruption/PollutionManagerAI.py'),
            'PollutionManagerAI')
        for method in (
                '_hydrateSecuredLocks', '_persistSecuredLocks',
                'applySecuredZones', 'isPurityLocked'):
            self.assertIn(
                method, pollution_methods,
                msg='PollutionManagerAI missing secured persist %s' % method)
        self.assertIn('PollutionSecuredSave', pollution_src)
        delete_idx = pollution_src.find('def delete(self):')
        self.assertGreater(delete_idx, 0)
        delete_snip = pollution_src[delete_idx:delete_idx + 500]
        self.assertIn('_persistSecuredLocks', delete_snip)
        self.assertIn('_applySecuredZonesToPollution', director_src)
        hydrate_idx = director_src.find('def _hydrateFromToon')
        self.assertGreater(hydrate_idx, 0)
        hydrate_snip = director_src[hydrate_idx:hydrate_idx + 2200]
        self.assertIn('_applySecuredZonesToPollution', hydrate_snip)
        self.assertIn('securedZones', hydrate_snip)
        default_prog = self.save.defaultProgress()
        self.assertEqual(default_prog['securedZones'], [])
        # Older blobs without securedZones migrate from unlocks.
        migrated = self.save.sanitizeProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'state': self.camp.STATE_ACTIVE,
        })
        self.assertIn(LOOPY, migrated['securedZones'])
        self.assertNotIn(PUNCHLINE, migrated['securedZones'])
        secured_save_src = _read(
            'toontown/corruption/PollutionSecuredSave.py').lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, secured_save_src)
        reclaim_director_src = _read(
            'toontown/reclaim/DistributedReclaimDirectorAI.py')
        self.assertIn('startStreetPackForToon', reclaim_director_src)
        self.assertIn('streetPackUnlocked', reclaim_director_src)
        self.assertIn('STATE_ACTIVE', reclaim_director_src)
        self.assertIn('unlockedThrough', reclaim_director_src)

    def test_reclaim_soft_gate_hydrate_silly_hp_and_ink_surge(self):
        """Soft-gate + R hydrate + Silly HP→P2 + Overlord ink_surge stay chained."""
        rg, cg = self.rg, self.cg
        # Soft-gate (#317): Loopy open; Punchline/Silly unlock with story.
        self.assertEqual(rg.streetPackRequiredActIndex(LOOPY), 0)
        self.assertEqual(rg.streetPackRequiredActIndex(PUNCHLINE), 1)
        self.assertEqual(rg.streetPackRequiredActIndex(SILLY), 2)
        self.assertTrue(rg.streetPackUnlocked(LOOPY, 0))
        self.assertFalse(rg.streetPackUnlocked(PUNCHLINE, 0))
        self.assertTrue(rg.streetPackUnlocked(PUNCHLINE, 1))
        self.assertFalse(rg.streetPackUnlocked(SILLY, 1))
        self.assertTrue(rg.streetPackUnlocked(SILLY, 2))
        gate = rg.streetPackGateMessage(PUNCHLINE, 0, face='Oswald')
        self.assertIn('Punchline Place', gate)
        self.assertIn('Loopy Lane', gate)
        self.assertIn('Oswald', gate)
        self.assertNotIn('~startreclaim', gate)
        self.assertNotIn('keyblade', gate.lower())

        # R start hydrates campaign progress before unlock read (#320).
        reclaim_ai = _read('toontown/reclaim/DistributedReclaimDirectorAI.py')
        start_idx = reclaim_ai.find('def startStreetPackForToon')
        self.assertGreater(start_idx, 0)
        start_snip = reclaim_ai[start_idx:start_idx + 2200]
        self.assertIn('_hydrateFromToon', start_snip)
        hydrate_pos = start_snip.find('_hydrateFromToon')
        unlock_pos = start_snip.find('unlockedThrough', hydrate_pos)
        self.assertGreater(hydrate_pos, 0)
        self.assertGreater(unlock_pos, hydrate_pos)
        camp_ai = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('def _hydrateFromToon', camp_ai)

        # Silly street Overlord HP-threshold P2 (#312) — campaign twist still gated.
        silly = rg.streetPack(SILLY)
        self.assertEqual(silly.get('finalePhase'), 1)
        self.assertEqual(
            silly.get('overlordP2HpFrac'), rg.OVERLORD_STREET_P2_HP_FRAC)
        self.assertTrue(rg.overlordHpAtP2Threshold(45, 90, 0.5))
        self.assertFalse(rg.overlordHpAtP2Threshold(46, 90, 0.5))
        self.assertNotIn('overlordP2HpFrac', rg.streetPackParams(LOOPY))
        for sym in (
                '_maybePromoteStreetOverlordP2',
                '_promoteStreetOverlordP2',
                'overlordHpAtP2Threshold'):
            self.assertIn(sym, reclaim_ai, msg='Silly HP P2 missing %s' % sym)
        client_src = _read('toontown/reclaim/DistributedReclaimDirector.py')
        complete_idx = client_src.find('def announceReclaimComplete')
        self.assertGreater(complete_idx, 0)
        complete_snip = client_src[complete_idx:complete_idx + 2200]
        self.assertIn('startedUnleashed', complete_snip)
        self.assertIn('bannerPhase >= 2', complete_snip)

        # Overlord P2 three-note kit: slam / ink_surge / rain (#327).
        self.assertTrue(cg.OVERLORD_INK_SURGE_ENABLED)
        p2 = cg.overlordPhaseCombat(2)
        self.assertEqual(p2.get('moveMode'), 'enrage')
        for key in (
                'surgeMaxRange', 'surgeDash', 'surgeStop', 'surgeHitRange',
                'surgeDamage', 'surgeCooldown'):
            self.assertIn(key, p2, msg='P2 missing %s' % key)
        slam = cg.overlordSlamMeleeRange(p2)
        surge = cg.overlordSurgeMaxRange(p2)
        self.assertEqual(cg.overlordPickEnrageMove(0.0, p2), 'slam')
        self.assertEqual(
            cg.overlordPickEnrageMove(slam + 0.05, p2), 'ink_surge')
        self.assertEqual(
            cg.overlordPickEnrageMove(surge + 0.05, p2), 'rain')
        corrupt_ai = _read('toontown/corruption/DistributedCorruptToonAI.py')
        self.assertIn('ink_surge', corrupt_ai)
        self.assertIn('overlordPickEnrageMove', corrupt_ai)

        # Overlord ink-rain linger sludge (#362) — DoT/slow after rain land.
        self.assertTrue(cg.OVERLORD_RAIN_LINGER_ENABLED)
        self.assertGreater(float(cg.OVERLORD_RAIN_LINGER_SEC), 1.0)
        self.assertGreater(float(cg.OVERLORD_RAIN_LINGER_TICK_SEC), 0.0)
        self.assertLess(
            float(cg.OVERLORD_RAIN_LINGER_TICK_SEC),
            float(cg.OVERLORD_RAIN_LINGER_SEC))
        self.assertGreaterEqual(int(cg.OVERLORD_RAIN_LINGER_TICK_DAMAGE), 1)
        self.assertGreater(float(cg.OVERLORD_RAIN_LINGER_RADIUS), 0.0)
        self.assertGreater(float(cg.OVERLORD_RAIN_LINGER_SLOW_FACTOR), 0.0)
        self.assertLess(float(cg.OVERLORD_RAIN_LINGER_SLOW_FACTOR), 1.0)
        land_at = 10.0
        until = cg.overlordRainLingerUntil(land_at)
        self.assertAlmostEqual(
            until, land_at + cg.OVERLORD_RAIN_LINGER_SEC, places=4)
        self.assertGreaterEqual(cg.overlordRainLingerTickCount(), 3)
        self.assertTrue(cg.isInsideOverlordRainLinger(0.0, 0.0, 9.5))
        self.assertFalse(cg.isInsideOverlordRainLinger(10.0, 0.0, 9.5))
        for phase in (1, 2):
            combat = cg.OVERLORD_PHASE_COMBAT[phase]
            self.assertGreater(float(combat.get('rainLingerSec', 0)), 1.0)
            self.assertGreaterEqual(
                int(combat.get('rainLingerTickDamage', 0)), 1)
        ai_methods = _class_method_names(
            _module_ast('toontown/corruption/DistributedCorruptToonAI.py'),
            'DistributedCorruptToonAI')
        for method in (
                '__resolveOverlordRain', '__armOverlordRainLinger',
                '__tickOverlordRainLinger', '__clearOverlordRainLinger'):
            self.assertIn(method, ai_methods, msg='AI missing %s' % method)
        self.assertIn('__armOverlordRainLinger(ox, oy, hitRange)', corrupt_ai)
        resolve_idx = corrupt_ai.find('def __resolveOverlordRain')
        self.assertGreater(resolve_idx, 0)
        resolve_snip = corrupt_ai[
            resolve_idx:corrupt_ai.find('\n    def ', resolve_idx + 1)]
        self.assertIn('__armOverlordRainLinger', resolve_snip)
        corrupt_client = _read(
            'toontown/corruption/DistributedCorruptToon.py')
        client_methods = _class_method_names(
            _module_ast('toontown/corruption/DistributedCorruptToon.py'),
            'DistributedCorruptToon')
        for method in (
                '__playOverlordRainLingerPuddle',
                '__armOverlordRainSludgeSlow',
                '__tickOverlordRainSludgeSlow',
                '__clearOverlordRainSludgeSlow'):
            self.assertIn(
                method, client_methods, msg='client missing %s' % method)
        self.assertIn('OVERLORD_RAIN_LINGER_ENABLED', corrupt_client)
        self.assertIn('setWalkSpeedSlow', corrupt_client)
        linger_blob = (
            resolve_snip + corrupt_client[
                corrupt_client.find('def __playOverlordRainLingerPuddle'):
                corrupt_client.find(
                    '\n    def ',
                    corrupt_client.find('def __playOverlordRainLingerPuddle')
                    + 1)]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, linger_blob)

    def test_campaign_progress_client_sync_loop(self):
        """Login sync mirrors victory / unlock / chase / reclaim so hub truth survives (#333/#349/#351)."""
        camp, save = self.camp, self.save
        self.assertEqual(
            camp.CAMPAIGN_PROGRESS_SYNC_MSG, 'campaignProgressSync')
        self.assertEqual(camp.CAMPAIGN_VICTORY_MSG, 'campaignVictory')
        fresh = save.clientMirrorFromProgress(save.defaultProgress())
        self.assertFalse(fresh['victoryEpilogue'])
        self.assertFalse(fresh['betrayed'])
        self.assertFalse(fresh['chasePending'])
        self.assertEqual(fresh['unlockedThrough'], 0)
        self.assertEqual(fresh['reclaimCount'], 0)
        self.assertIsNone(fresh['softNextStreet'])
        # Persist blob carries reclaimCount + mid-chase HP fields.
        default = save.defaultProgress()
        self.assertIn('reclaimCount', default)
        self.assertIn('chaseHp', default)
        self.assertEqual(default['chaseHp'], 0)

        mid = save.clientMirrorFromProgress({
            'unlockedThrough': 1,
            'actIndex': 1,
            'state': camp.STATE_ACTIVE,
            'reclaimCount': 3,
            'chaseCleared': 0,
        })
        self.assertEqual(mid['unlockedThrough'], 1)
        self.assertEqual(mid['reclaimCount'], 3)
        self.assertIn('Punchline', mid['softNextStreet'] or '')

        pending = save.clientMirrorFromProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
            'chaseCleared': 0,
            'reclaimCount': 4,
            'chaseHp': 37,
        })
        self.assertTrue(pending['victoryEpilogue'])
        self.assertTrue(pending['betrayed'])
        self.assertTrue(pending['chasePending'])
        self.assertEqual(pending['reclaimCount'], 4)
        # clientMirror is presentation-only — chaseHp stays on the persist blob.
        sanitized = save.sanitizeProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
            'chaseCleared': 0,
            'chaseHp': 37,
        })
        self.assertEqual(sanitized['chaseHp'], 37)
        tip = camp.hubPlayEntryTip(
            victory=pending['victoryEpilogue'],
            chasePending=pending['chasePending'])
        self.assertEqual(tip, camp.HUB_CHASE_PENDING_TIP)
        self.assertNotIn('stain is washed', tip.lower())
        self.assertNotIn('Campaign complete', tip)

        cleared = save.clientMirrorFromProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
            'chaseCleared': 1,
            'chaseHp': 37,
        })
        self.assertTrue(cleared['victoryEpilogue'])
        self.assertFalse(cleared['chasePending'])
        cleared_blob = save.sanitizeProgress({
            'state': camp.STATE_VICTORY,
            'chaseCleared': 1,
            'chaseHp': 37,
        })
        self.assertEqual(cleared_blob['chaseHp'], 0)
        washed = camp.hubPlayEntryTip(
            victory=cleared['victoryEpilogue'],
            chasePending=cleared['chasePending'])
        self.assertEqual(washed, camp.HUB_VICTORY_TIP)
        self.assertIn('stain is washed', washed.lower())

        # Chase-pending hub tip (#342) — victory alone must not claim washed.
        self.assertTrue(hasattr(camp, 'HUB_CHASE_PENDING_TIP'))
        self.assertTrue(callable(camp.hubChasePendingTip))
        self.assertEqual(
            camp.hubPlayEntryTip(victory=True, chasePending=True),
            camp.hubChasePendingTip())
        self.assertIn('betrayal chase', camp.HUB_CHASE_PENDING_TIP.lower())
        self.assertNotIn(
            'stain is washed', camp.HUB_CHASE_PENDING_TIP.lower())
        # Legacy victory=True (no chasePending kw) still means washed tip.
        self.assertEqual(
            camp.hubPlayEntryTip(victory=True), camp.hubVictoryReplayTip())

        dc = _read('etc/toon.dc')
        self.assertIn('requestCampaignProgress', dc)
        self.assertIn('setCampaignProgress', dc)
        pollution_block = dc.split('dclass PollutionManager')[1].split(
            'dclass ')[0]
        self.assertIn(
            'setCampaignProgress(uint8, uint8, uint8, uint8)', pollution_block)
        self.assertIn('reclaimCount', pollution_block)
        self.assertIn('announceCampaignVictory(uint8)', pollution_block)

        play_src = _read('toontown/campaign/PlayEntry.py')
        for needle in (
                '_onCampaignProgressSync', '_bootCampaignProgress',
                'd_requestCampaignProgress', 'clientMirrorFromProgress',
                'CAMPAIGN_PROGRESS_SYNC_MSG'):
            self.assertIn(needle, play_src, msg='PlayEntry missing %s' % needle)
        # PlayEntry latches chasePending so hub tip stays honest (#342).
        self.assertIn('self._chasePending', play_src)
        self.assertIn("mirror.get('chasePending')", play_src)
        self.assertIn('chasePending=bool(self._chasePending)', play_src)
        victory_idx = play_src.find('def _onCampaignVictory')
        self.assertGreater(victory_idx, 0)
        victory_win = play_src[victory_idx:victory_idx + 400]
        self.assertIn('self._chasePending = True', victory_win)
        epi_idx = play_src.find('def _onCampaignEpilogue')
        self.assertGreater(epi_idx, 0)
        epi_win = play_src[epi_idx:epi_idx + 500]
        self.assertIn('self._chasePending = False', epi_win)
        show_idx = play_src.find('def _showHubTip')
        self.assertGreater(show_idx, 0)
        show_win = play_src[show_idx:show_idx + 1200]
        self.assertIn('self._chasePending', show_win)
        self.assertIn('wash the betrayal chase', show_win.lower())
        presence_src = _read('toontown/campaign/OswaldPresence.py')
        self.assertIn('_onCampaignProgressSync', presence_src)
        self.assertIn('CAMPAIGN_PROGRESS_SYNC_MSG', presence_src)
        director_src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('_pushProgressToClient', director_src)
        self.assertIn('_pushVictoryToClient', director_src)
        # campaignVictory relay (#351): both finale victory branches push.
        victory_marker = "messenger.send('campaignVictory'"
        first_vic = director_src.find(victory_marker)
        self.assertGreater(first_vic, 0)
        second_vic = director_src.find(victory_marker, first_vic + len(victory_marker))
        self.assertGreater(second_vic, first_vic)
        for idx in (first_vic, second_vic):
            window = director_src[idx:idx + 280]
            self.assertIn('_pushVictoryToClient', window)
        pollution_ai = _read('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('pushCampaignProgressToAvatar', pollution_ai)
        self.assertIn('pushCampaignVictoryToAvatar', pollution_ai)
        self.assertIn('requestCampaignProgress', pollution_ai)
        push_idx = pollution_ai.find('def pushCampaignProgressToAvatar')
        self.assertGreater(push_idx, 0)
        push_win = pollution_ai[push_idx:push_idx + 2200]
        self.assertIn("blob.get('reclaimCount'", push_win)
        self.assertIn(
            '[unlocked, state, chaseCleared, reclaimCount]', push_win)
        pollution_client = _read('toontown/corruption/PollutionManager.py')
        self.assertIn('setCampaignProgress', pollution_client)
        self.assertIn('announceCampaignVictory', pollution_client)
        self.assertIn('campaignReclaimCount', pollution_client)
        self.assertIn('d_requestCampaignProgress', pollution_client)
        set_idx = pollution_client.find('def setCampaignProgress')
        self.assertGreater(set_idx, 0)
        set_win = pollution_client[set_idx:set_idx + 900]
        self.assertIn('reclaimCount', set_win)
        # Live victory acceptors (#351) — not AI-local messenger only.
        for rel, class_name in (
                ('toontown/campaign/PlayEntry.py', 'PlayEntryClient'),
                ('toontown/campaign/OswaldPresence.py', 'OswaldPresenceClient'),
                ('toontown/campaign/OswaldBetrayalChase.py',
                 'OswaldBetrayalChaseClient'),
                ('toontown/campaign/FinalePhaseFx.py', 'FinalePhaseFxClient'),
                ('toontown/campaign/CampaignHandoff.py',
                 'CampaignHandoffClient')):
            events = _accept_events(_module_ast(rel), class_name)
            self.assertIn(
                'campaignVictory', events,
                msg='%s.%s must accept campaignVictory' % (rel, class_name))
        # Sync path copy only — PlayEntry module still mentions "no kh" in docs.
        sync_blob = ' '.join([
            camp.CAMPAIGN_PROGRESS_SYNC_MSG,
            camp.CAMPAIGN_VICTORY_MSG,
            tip,
            camp.HUB_CHASE_PENDING_TIP,
            mid.get('softNextStreet') or '',
        ]).lower()
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, sync_blob)

    def test_oswald_twist_hooks_and_fx_modules(self):
        camp = self.camp
        finale = self.act_by_id['finale']
        # Mid-act foreshadow vs finale sunny path (trustFracture off on Silly).
        self.assertIs(self.act_by_id['loopy'].get('trustFracture'), True)
        self.assertIs(self.act_by_id['punchline'].get('trustFracture'), True)
        self.assertFalse(bool(finale.get('trustFracture')))
        self.assertTrue(finale.get('entryTipUnease'))
        self.assertTrue(finale.get('betrayalHandoff'))
        approach = finale.get('approachTip') or ''
        self.assertIn('almost confess', approach.lower())
        self.assertNotIn('keyblade', approach.lower())
        loopy_approach = self.act_by_id['loopy'].get('approachTip') or ''
        self.assertIn('rubbery half-beat', loopy_approach.lower())
        self.assertNotIn('keyblade', loopy_approach.lower())
        self.assertFalse(bool(self.act_by_id['loopy'].get('entryTip')))
        handoff = finale.get('handoff') or ''
        self.assertIn('his all along', handoff.lower())

        # Explicit twist copy constants.
        tease = camp.FINALE_TWIST_TEASE
        self.assertIn('Oswald caused the corruption', tease)
        reveal = camp.FINALE_REVEAL_BANNER
        self.assertIn('OSWALD', reveal.upper())
        self.assertIn('CORRUPTION', reveal.upper())
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            self.assertNotIn(banned, tease.lower())
            self.assertNotIn(banned, reveal.lower())
            self.assertNotIn(banned, handoff.lower())

        # Twist presentation modules + messenger chain.
        for rel, symbols in (
                ('toontown/campaign/FinalePhaseFx.py',
                 ('FinalePhaseFxClient', 'ensureFinalePhaseFxClient',
                  'playOswaldReveal', 'oswaldRevealSting',
                  'oswaldRevealBanner', 'finalePhaseStingBanner')),
                ('toontown/campaign/VictoryTwistConfettiSting.py',
                 ('VictoryTwistConfettiSting',
                  'playVictoryTwistConfettiSting',
                  'clearVictoryTwistConfettiSting')),
                ('toontown/campaign/CampaignHandoff.py',
                 ('oswaldRevealBanner', '_onOswaldBetrayalBanner',
                  '_showBetrayalHandoff', 'betrayalHandoff',
                  'playVictoryTwistConfettiSting', 'campaignVictory',
                  'finalePhaseStingBanner', '_onFinalePhaseStingBanner',
                  '_showFinalePhaseStingPlate')),
                ('toontown/campaign/PlayEntry.py',
                 ('finalePhaseStingBanner', '_onFinalePhaseStingBanner',
                  'finalePhaseStingTipText')),
                ):
            path = REPO_ROOT / rel
            self.assertTrue(path.is_file(), msg='missing %s' % rel)
            src = _read(rel)
            for sym in symbols:
                self.assertIn(sym, src, msg='%s missing %s' % (rel, sym))

        finale_fx_names = _class_and_func_names(
            _module_ast('toontown/campaign/FinalePhaseFx.py'))
        self.assertIn('FinalePhaseFxClient', finale_fx_names)
        self.assertIn('ensureFinalePhaseFxClient', finale_fx_names)
        finale_methods = _class_method_names(
            _module_ast('toontown/campaign/FinalePhaseFx.py'),
            'FinalePhaseFxClient')
        for method in (
                '_onOswaldReveal', '_onCampaignVictory', 'playOswaldReveal',
                'playTransition'):
            self.assertIn(method, finale_methods)

        handoff_methods = _class_method_names(
            _module_ast('toontown/campaign/CampaignHandoff.py'),
            'CampaignHandoffClient')
        for method in (
                '_onOswaldBetrayalBanner', '_showBetrayalHandoff', '_onVictory',
                '_onFinalePhaseStingBanner', '_showFinalePhaseStingPlate'):
            self.assertIn(method, handoff_methods)

        # CampaignGlobals keeps betrayal / twist tunables assigned.
        camp_names = _toplevel_assign_names(
            _module_ast('toontown/campaign/CampaignGlobals.py'))
        for name in (
                'FINALE_TWIST_TEASE', 'FINALE_REVEAL_BANNER',
                'FINALE_REVEAL_DELAY_SEC', 'FINALE_BETRAYAL_HANDOFF_CUE',
                'VICTORY_TWIST_CONFETTI_ENABLED', 'SILLY_APPROACH_TIP_DELAY_SEC',
                'LOOPY_APPROACH_TIP_DELAY_SEC',
                'FINALE_PHASE_STING_BANNER_MSG',
                'FINALE_PHASE_STING_PLATE_ENABLED',
                'FINALE_PHASE_STING_TIP_ENABLED'):
            self.assertIn(name, camp_names)
        self.assertTrue(camp.VICTORY_TWIST_CONFETTI_ENABLED)
        self.assertGreater(camp.SILLY_APPROACH_TIP_DELAY_SEC, 0.0)
        self.assertGreater(camp.LOOPY_APPROACH_TIP_DELAY_SEC, 0.0)
        self.assertGreater(camp.FINALE_REVEAL_DELAY_SEC, 0.0)

    def test_twist_chase_betrayal_kit_and_epilogue(self):
        """Chase spawn + betrayal kit + chase-clear epilogue close the loop."""
        camp, cg = self.camp, self.cg
        self.assertTrue(camp.OSWALD_BETRAYAL_CHASE_ENABLED)
        self.assertIn('Corrupted Oswald', camp.OSWALD_BETRAYAL_CHASE_NAME)
        self.assertEqual(
            cg.archetypeDefaultName(cg.ARCHETYPE_CORRUPT_OSWALD),
            'Corrupted Oswald')
        oswald = cg.ARCHETYPE_STATS[cg.ARCHETYPE_CORRUPT_OSWALD]
        self.assertEqual(oswald.get('attackMove'), 'betrayal_lunge')
        self.assertGreater(float(oswald.get('lungeDashDist', 0)), 2.0)
        self.assertGreater(float(oswald.get('burstMeleeRange', 0)), 2.0)

        chase_rel = 'toontown/campaign/OswaldBetrayalChase.py'
        self.assertTrue((REPO_ROOT / chase_rel).is_file())
        chase_names = _class_and_func_names(_module_ast(chase_rel))
        for sym in (
                'spawnCorruptOswald', 'OswaldBetrayalChaseClient',
                'ensureOswaldBetrayalChaseClient', 'chaseAttackMove',
                'chaseHp', 'resolveChaseSpawnHp', 'chaseCombatDefeated',
                'epilogueEnabled', 'epilogueTitle', 'epilogueCue'):
            self.assertIn(sym, chase_names)
        chase_src = _read(chase_rel)
        self.assertIn('ARCHETYPE_CORRUPT_OSWALD', chase_src)
        self.assertIn('oswaldBetrayalChaseCleared', chase_src)
        self.assertIn('campaignEpilogue', chase_src)
        self.assertIn('_fireEpilogue', chase_src)
        self.assertIn("corrupt._stats['attackMove']", chase_src)
        self.assertIn('resolveChaseSpawnHp', chase_src)
        self.assertIn('announceCampaignVictory', chase_src)

        # Mid-chase HP persist (#350) — resume / relog must not full-heal.
        resolve = self.chase['resolveChaseSpawnHp']
        max_hp = self.chase['chaseHp']()
        self.assertGreater(max_hp, 10)
        self.assertEqual(resolve(None), (max_hp, max_hp))
        self.assertEqual(resolve(0), (max_hp, max_hp))
        mid_hp = max(1, max_hp // 2)
        self.assertEqual(resolve(mid_hp), (max_hp, mid_hp))
        self.assertEqual(resolve(max_hp + 50), (max_hp, max_hp))
        self.assertEqual(resolve(1), (max_hp, 1))
        save = self.save
        mid_blob = save.sanitizeProgress({
            'unlockedThrough': 2,
            'actIndex': 2,
            'state': camp.STATE_VICTORY,
            'chaseCleared': 0,
            'chaseHp': mid_hp,
        })
        self.assertEqual(mid_blob['chaseHp'], mid_hp)
        # Director snapshots live HP and passes remaining into spawn.
        director_src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('_snapshotOswaldChaseHp', director_src)
        self.assertIn('resolveChaseSpawnHp', director_src)
        self.assertIn('self.chaseHp', director_src)
        snap = director_src[director_src.find('def _snapshotOswaldChaseHp'):]
        snap = snap[:snap.find('\n    def ', 1)]
        self.assertIn('resolveChaseSpawnHp', snap)
        self.assertIn('self.chaseHp', snap)
        spawn = director_src[director_src.find(
            'def __spawnOswaldBetrayalChase'):]
        spawn = spawn[:spawn.find('\n    def ', 1)]
        self.assertIn('chaseHp', spawn)
        self.assertIn('spawnCorruptOswald', spawn)
        self.assertIn('remaining if remaining > 0 else None', spawn)
        save_src = _read('toontown/campaign/CampaignProgressSave.py')
        self.assertIn("'chaseHp'", save_src)
        self.assertIn('director.chaseHp', save_src)

        # Zone leave / DO despawn must NOT false-clear the chase (#341).
        defeated = self.chase['chaseCombatDefeated']
        self.assertFalse(defeated(None))
        self.assertFalse(defeated(types.SimpleNamespace(hp=40, _defeated=False)))
        self.assertTrue(defeated(types.SimpleNamespace(hp=0, _defeated=False)))
        self.assertTrue(defeated(types.SimpleNamespace(hp=12, _defeated=True)))
        poll = chase_src[chase_src.find('def _pollChaseClear'):]
        poll = poll[:poll.find('def _findLiveCorruptOswald')]
        self.assertIn('chaseCombatDefeated', poll)
        self.assertNotIn('treat as clear', poll.lower())
        self.assertIn('zone leave', poll.lower())
        self.assertEqual(poll.count('_emitChaseCleared'), 1)
        self.assertTrue(poll.rstrip().endswith('return task.again'))

        # Director schedules chase after finale; PlayEntry/Handoff accept clear.
        # Pending chase (victory + chaseCleared=0) must resume on hydrate / C (#330).
        director_methods = _class_method_names(
            _module_ast('toontown/campaign/CampaignDirectorAI.py'),
            'CampaignDirectorAI')
        self.assertIn('OswaldBetrayalChase', director_src)
        self.assertIn('_resumePendingOswaldBetrayalChase', director_methods)
        self.assertIn('_pendingOswaldBetrayalChase', director_methods)
        self.assertIn('_scheduleOswaldBetrayalChase', director_methods)
        self.assertIn('_snapshotOswaldChaseHp', director_methods)
        self.assertIn('__finishOswaldBetrayalChaseClear', director_methods)
        self.assertIn('OSWALD_BETRAYAL_CHASE_RESUME_MSG', director_src)
        self.assertIn('campaignEpilogue', director_src)
        self.assertTrue(camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG)
        self.assertIn('Oswald', camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG)
        self.assertIn('pending', camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG.lower())
        # Watch clears only via combat defeat; missing DO resumes instead.
        watch = director_src[director_src.find('def __watchOswaldBetrayalChase'):]
        watch = watch[:watch.find('def __finishOswaldBetrayalChaseClear')]
        self.assertIn('chaseCombatDefeated', watch)
        self.assertIn('_resumePendingOswaldBetrayalChase', watch)
        self.assertIn('_snapshotOswaldChaseHp', watch)
        self.assertNotIn('self.chaseCleared = 1', watch)
        finish = director_src[
            director_src.find('def __finishOswaldBetrayalChaseClear'):]
        finish = finish[:finish.find('def __onNeighborhoodReclaimed')]
        self.assertIn('self.chaseCleared = 1', finish)
        self.assertIn('self.chaseHp = 0', finish)
        self.assertIn('_syncHubStain', finish)
        self.assertIn('oswaldBetrayalChaseCleared', finish)
        self.assertIn('campaignEpilogue', finish)
        # Hydrate re-schedules; startCampaign resume tip precedes wipe-replay.
        hydrate_idx = director_src.find('def _hydrateFromToon')
        self.assertGreater(hydrate_idx, 0)
        hydrate_win = director_src[hydrate_idx:hydrate_idx + 2400]
        self.assertIn('_resumePendingOswaldBetrayalChase(toon)', hydrate_win)
        start_idx = director_src.find('def startCampaign')
        self.assertGreater(start_idx, 0)
        start_win = director_src[start_idx:start_idx + 1600]
        resume_at = start_win.find('_resumePendingOswaldBetrayalChase')
        wipe_at = start_win.find('self.chaseCleared = 0')
        self.assertGreater(resume_at, 0)
        self.assertGreater(wipe_at, resume_at)
        self.assertIn('OSWALD_BETRAYAL_CHASE_RESUME_MSG', start_win)
        self.assertIn('return tip', start_win)
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('ensureOswaldBetrayalChaseClient', play_src)
        self.assertIn("accept('oswaldBetrayalChaseCleared'", play_src)
        self.assertIn("accept('campaignEpilogue'", play_src)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('campaignEpilogue', handoff_src)
        self.assertIn('_onChaseCleared', handoff_src)

        # Epilogue soft-end (#326): victory hub tip + authored copy.
        self.assertTrue(camp.CAMPAIGN_EPILOGUE_ENABLED)
        self.assertIn('Oswald', camp.CAMPAIGN_EPILOGUE_SUB)
        self.assertIn('Replay', camp.CAMPAIGN_EPILOGUE_CUE)
        self.assertIn('Loopy', camp.CAMPAIGN_EPILOGUE_CUE)
        victory = camp.hubPlayEntryTip(victory=True)
        self.assertEqual(victory, camp.hubVictoryReplayTip())
        self.assertIn('Campaign complete', victory)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            blob = ' '.join([
                camp.OSWALD_BETRAYAL_CHASE_NAME,
                camp.OSWALD_BETRAYAL_CHASE_RESUME_MSG,
                camp.CAMPAIGN_EPILOGUE_TITLE,
                camp.CAMPAIGN_EPILOGUE_SUB,
                camp.CAMPAIGN_EPILOGUE_CUE,
                victory,
            ]).lower()
            self.assertNotIn(banned, blob)

    def test_twist_oswald_telegraph_hit_av(self):
        """Corrupted Oswald telegraph/hit AV stays distinct from Smudge (#344)."""
        cg = self.cg

        def _is_crimson(color):
            r, g, b = float(color[0]), float(color[1]), float(color[2])
            return r > g and r > b and b < 0.7 and g < 0.55

        # Crimson charge / hold — not Smudge purple.
        charge = cg.OSWALD_TELEGRAPH_CHARGE_COLOR
        hold = cg.OSWALD_TELEGRAPH_HOLD_COLOR
        smudge = cg.TELEGRAPH_CHARGE_COLOR
        self.assertTrue(_is_crimson(charge), msg=repr(charge))
        self.assertTrue(_is_crimson(hold), msg=repr(hold))
        self.assertNotEqual(tuple(charge[:3]), tuple(smudge[:3]))
        look = cg.OSWALD_TELEGRAPH_STAIN_LOOK
        self.assertEqual(look.get('id'), 'betrayal-crimson-lunge')
        for key in ('fistColor', 'rimColor', 'smearColor'):
            self.assertIn(key, look)
            self.assertTrue(_is_crimson(look[key]), msg='%s %r' % (key, look[key]))
        splash_looks = cg.OSWALD_BETRAYAL_SPLASH_LOOK
        for kind in ('hit', 'death'):
            splash = splash_looks[kind]
            self.assertIn('oswald', str(splash.get('id', '')).lower())
            self.assertTrue(_is_crimson(splash['splatColor']))
            self.assertNotEqual(
                splash.get('id'),
                cg.SMUDGE_INK_SPLASH_LOOK[kind].get('id'))

        tele_rel = 'toontown/corruption/OswaldBetrayalTelegraphFx.py'
        splash_rel = 'toontown/corruption/OswaldBetrayalSplashFx.py'
        self.assertTrue((REPO_ROOT / tele_rel).is_file())
        self.assertTrue((REPO_ROOT / splash_rel).is_file())
        tele_names = _class_and_func_names(_module_ast(tele_rel))
        splash_names = _class_and_func_names(_module_ast(splash_rel))
        self.assertIn('OswaldBetrayalTelegraphStain', tele_names)
        self.assertIn('oswaldTelegraphStainLook', tele_names)
        self.assertIn('OswaldBetrayalSplash', splash_names)
        self.assertIn('oswaldBetrayalSplashLook', splash_names)

        client_src = _read('toontown/corruption/DistributedCorruptToon.py')
        client_methods = _class_method_names(
            _module_ast('toontown/corruption/DistributedCorruptToon.py'),
            'DistributedCorruptToon')
        for name in (
                '__playOswaldTelegraphStain', '__clearOswaldTelegraphStain',
                '__playOswaldBetrayalSplash', '__isCorruptOswald'):
            self.assertIn(name, client_methods, msg='missing %s' % name)
        telegraph = client_src[client_src.find('def announceAttackTelegraph'):]
        telegraph_end = telegraph.find('\n    def ', 1)
        tele_body = (
            telegraph if telegraph_end < 0 else telegraph[:telegraph_end])
        self.assertIn('isOswald = self.__isCorruptOswald()', tele_body)
        self.assertIn('elif isOswald:', tele_body)
        self.assertIn('__playOswaldTelegraphStain()', tele_body)
        self.assertIn('and (not isOswald)', tele_body)
        hit = client_src[client_src.find('def announceAttackHit'):]
        hit_end = hit.find('\n    def ', 1)
        hit_body = hit if hit_end < 0 else hit[:hit_end]
        self.assertIn('elif isOswald:', hit_body)
        self.assertIn('__clearOswaldTelegraphStain()', hit_body)
        self.assertIn("__playOswaldBetrayalSplash(kind='hit')", client_src)
        self.assertIn(
            "__playOswaldBetrayalSplash(splatPos, kind='death')", client_src)
        self.assertIn(
            'ARCHETYPE_CORRUPT_OSWALD',
            client_src[client_src.find('def __playHitReaction'):])
        corr_init = _read('toontown/corruption/__init__.py')
        self.assertIn('OswaldBetrayalTelegraphFx', corr_init)
        self.assertIn('OswaldBetrayalSplashFx', corr_init)
        reclaim_md = _read('toontown/corruption/RECLAIM.md')
        self.assertIn('OswaldBetrayalTelegraphFx', reclaim_md)
        self.assertIn('OswaldBetrayalSplashFx', reclaim_md)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            blob = ' '.join([
                str(look.get('id', '')),
                str(splash_looks['hit'].get('id', '')),
            ]).lower()
            self.assertNotIn(banned, blob)

    def test_twist_hub_stain_after_betrayal(self):
        """Post-betrayal hub fog/confront (#336) until chase clear washes it."""
        camp, stain = self.camp, self.stain
        self.assertTrue(camp.HUB_STAIN_ENABLED)
        self.assertEqual(int(camp.HUB_ZONE), HUB)
        self.assertEqual(stain.hubStainZone(), HUB)
        self.assertGreater(float(camp.HUB_STAIN_POLLUTION), 0.0)
        self.assertLess(float(camp.HUB_STAIN_POLLUTION), 0.75)
        self.assertIn('stain', camp.HUB_STAIN_MSG.lower())
        self.assertTrue(camp.HUB_STAIN_CONFRONT_ENABLED)
        self.assertIn('Oswald', camp.HUB_STAIN_CONFRONT_LABEL)
        # Victory + chase pending stains hub; cleared / non-victory does not.
        self.assertTrue(stain.hubStainWanted(camp.STATE_VICTORY, chaseCleared=0))
        self.assertFalse(stain.hubStainWanted(camp.STATE_VICTORY, chaseCleared=1))
        self.assertFalse(stain.hubStainWanted(camp.STATE_ACTIVE, chaseCleared=0))
        self.assertFalse(stain.hubStainWanted(camp.STATE_IDLE, chaseCleared=0))

        stain_names = _class_and_func_names(
            _module_ast('toontown/campaign/HubStain.py'))
        for sym in (
                'hubStainWanted', 'applyHubStain', 'clearHubStain',
                'syncHubStain', 'hubStainEnabled'):
            self.assertIn(sym, stain_names)
        director_src = _read('toontown/campaign/CampaignDirectorAI.py')
        self.assertIn('_syncHubStain', director_src)
        self.assertIn('clearHubStain', director_src)
        self.assertIn('from toontown.campaign.HubStain import', director_src)
        pollution_ai = _read('toontown/corruption/PollutionManagerAI.py')
        self.assertIn('applyBetrayalHubStain', pollution_ai)
        self.assertIn('clearBetrayalHubStain', pollution_ai)
        # Hub stain drops campaign securedZones (#374; contested parity) so
        # hydrate cannot reseal TTC from a stale progress blob.
        apply_snip = pollution_ai[pollution_ai.find('def applyBetrayalHubStain'):]
        apply_snip = apply_snip[:apply_snip.find('def clearBetrayalHubStain')]
        self.assertIn('_mirrorSecuredZoneToCampaign', apply_snip)
        self.assertIn('secured=False', apply_snip)
        hydrate_idx = director_src.find('def _hydrateFromToon')
        self.assertGreater(hydrate_idx, 0)
        hydrate_snip = director_src[hydrate_idx:hydrate_idx + 2400]
        self.assertIn('mirrors secured=False', hydrate_snip)
        self.assertIn('_syncHubStain', hydrate_snip)

        confront_rel = 'toontown/campaign/HubStainConfront.py'
        self.assertTrue((REPO_ROOT / confront_rel).is_file())
        confront_names = _class_and_func_names(_module_ast(confront_rel))
        for sym in (
                'HubStainConfrontClient', 'ensureHubStainConfrontClient',
                'refreshHubStainConfront', 'stopHubStainConfront'):
            self.assertIn(sym, confront_names)
        # Washed-plaza epilogue beat after chase clear (#353) — beyond plate + tip.
        self.assertTrue(camp.HUB_EPILOGUE_BEAT_ENABLED)
        self.assertTrue(
            stain.hubEpilogueBeatWanted(camp.STATE_VICTORY, chaseCleared=1))
        self.assertFalse(
            stain.hubEpilogueBeatWanted(camp.STATE_VICTORY, chaseCleared=0))
        self.assertFalse(
            stain.hubEpilogueBeatWanted(camp.STATE_ACTIVE, chaseCleared=1))
        # Complementary: pending stains; cleared washes confront + shows beat.
        self.assertTrue(stain.hubStainWanted(camp.STATE_VICTORY, chaseCleared=0))
        self.assertFalse(stain.hubStainWanted(camp.STATE_VICTORY, chaseCleared=1))
        self.assertIn('washed', camp.HUB_EPILOGUE_BEAT_LABEL.lower())
        self.assertIn('Oswald', camp.HUB_EPILOGUE_BEAT_ABSENCE)
        self.assertIn('plaza', camp.HUB_EPILOGUE_BEAT_TIP.lower())
        self.assertIn('absence', camp.HUB_EPILOGUE_BEAT_TIP.lower())
        self.assertIn('Loopy', camp.HUB_EPILOGUE_BEAT_TIP)
        self.assertNotEqual(
            camp.HUB_EPILOGUE_BEAT_LABEL, camp.HUB_STAIN_CONFRONT_LABEL)
        self.assertNotIn(
            'wash the betrayal chase', camp.HUB_EPILOGUE_BEAT_TIP.lower())
        self.assertGreater(float(camp.HUB_EPILOGUE_BEAT_FORWARD), 0.0)
        epi_rel = 'toontown/campaign/HubEpilogueBeat.py'
        self.assertTrue((REPO_ROOT / epi_rel).is_file())
        epi_names = _class_and_func_names(_module_ast(epi_rel))
        for sym in (
                'HubEpilogueBeatClient', 'ensureHubEpilogueBeatClient',
                'refreshHubEpilogueBeat', 'stopHubEpilogueBeat',
                'clearHubEpilogueBeat', 'epilogueBeatEnabled',
                'epilogueBeatLabel', 'epilogueBeatAbsence', 'epilogueBeatTip'):
            self.assertIn(sym, epi_names)
        epi_src = _read(epi_rel)
        self.assertIn('hubEpilogueBeatWanted', epi_src)
        self.assertIn('hubStainCleared', epi_src)
        self.assertIn('oswaldBetrayalChaseCleared', epi_src)
        self.assertIn('campaignEpilogue', epi_src)
        self.assertIn('campaignProgressSync', epi_src)
        tt = _read('toontown/safezone/TTPlayground.py')
        self.assertIn('refreshHubStainConfront', tt)
        self.assertIn('stopHubStainConfront', tt)
        self.assertIn('refreshHubEpilogueBeat', tt)
        self.assertIn('stopHubEpilogueBeat', tt)
        # Trusted Oswald stub wiring must survive hub-stain mount.
        self.assertIn('refreshOswaldPresenceHub', tt)
        handoff_src = _read('toontown/campaign/CampaignHandoff.py')
        self.assertIn('_refreshHubEpilogueBeat', handoff_src)
        self.assertIn('refreshHubEpilogueBeat', handoff_src)
        self.assertIn('_showEpilogueHandoff', handoff_src)
        play_src = _read('toontown/campaign/PlayEntry.py')
        self.assertIn('ensureHubEpilogueBeatClient', play_src)
        self.assertIn('refreshHubEpilogueBeat', play_src)
        self.assertIn('clearHubEpilogueBeat', play_src)
        # Confront clear stays separate from washed-plaza beat module.
        confront_src = _read('toontown/campaign/HubStainConfront.py')
        self.assertIn('_onHubStainCleared', confront_src)
        self.assertNotIn('HubEpilogueBeat', confront_src)
        for banned in ('keyblade', 'kingdom hearts', 'sora'):
            blob = ' '.join([
                camp.HUB_STAIN_MSG,
                camp.HUB_STAIN_CLEAR_MSG,
                camp.HUB_STAIN_CONFRONT_LABEL,
                camp.HUB_STAIN_CONFRONT_TIP,
                camp.HUB_EPILOGUE_BEAT_LABEL,
                camp.HUB_EPILOGUE_BEAT_ABSENCE,
                camp.HUB_EPILOGUE_BEAT_TIP,
            ]).lower()
            self.assertNotIn(banned, blob)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HeadlessLoopFlowTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
