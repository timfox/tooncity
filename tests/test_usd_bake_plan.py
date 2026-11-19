#!/usr/bin/env python3
"""Headless USD offline bake-plan gates for props (PR 3).

Given ``smoke_prop.usda``, emit deterministic bake plan JSON with target
``phase_*/models/….bam`` and DNA code string. Dry-run does not require
``egg2bam``. Hook points for real workers are documented on
``toontown.usd.bake_bam``.

Run from repo root:
  python3 -m unittest tests.test_usd_bake_plan -v
  python3 tests/test_usd_bake_plan.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from toontown.usd import bake_bam  # noqa: E402
from toontown.usd.bake_bam import (  # noqa: E402
    HOOK_POINTS,
    bake_fixture,
    bake_fixture_json,
    describe_hooks,
    register_hook,
)
from toontown.usd.bake_plan import (  # noqa: E402
    SCHEMA_VERSION,
    BakePlanError,
    plan_from_fixture,
    plan_to_json,
)

SMOKE_PROP = 'smoke_prop'
EXPECTED_BAM = 'phase_5/models/props/loopy_ink_banner.bam'
EXPECTED_DNA = 'loopy_ink_banner'

_BANNED = (
    'keyblade',
    'kingdom hearts',
    'kingdomhearts',
    'sora',
    'heartless',
)


class TestSmokePropBakePlan(unittest.TestCase):
    def test_plan_from_smoke_prop_bam_and_dna(self):
        plan = plan_from_fixture(SMOKE_PROP)
        self.assertEqual(plan['schemaVersion'], SCHEMA_VERSION)
        self.assertEqual(plan['source'], SMOKE_PROP)
        self.assertEqual(plan['kind'], 'TcProp')
        self.assertEqual(plan['bamPath'], EXPECTED_BAM)
        self.assertEqual(plan['dnaCode'], EXPECTED_DNA)
        self.assertTrue(plan['bamPath'].startswith('phase_'))
        self.assertIn('/models/', plan['bamPath'])
        self.assertTrue(plan['bamPath'].endswith('.bam'))
        self.assertTrue(plan['dryRun'])
        self.assertEqual(plan['status'], 'planned')
        self.assertEqual(plan['hood'], 'TT')
        self.assertEqual(plan['primName'], 'SmokePropRoot')

    def test_plan_json_is_deterministic(self):
        a = plan_to_json(plan_from_fixture(SMOKE_PROP))
        b = plan_to_json(plan_from_fixture(SMOKE_PROP))
        self.assertEqual(a, b)
        # Round-trip through json.loads keeps required fields.
        data = json.loads(a)
        self.assertEqual(data['bamPath'], EXPECTED_BAM)
        self.assertEqual(data['dnaCode'], EXPECTED_DNA)
        # Key order stable across dumps (first keys match schema order).
        keys = list(data.keys())
        self.assertEqual(keys[0], 'schemaVersion')
        self.assertLess(keys.index('bamPath'), keys.index('dnaCode'))

    def test_two_independent_json_dumps_byte_identical(self):
        """Acceptance: deterministic bake plan JSON for smoke_prop."""
        j1 = bake_fixture_json(SMOKE_PROP, dry_run=True)
        j2 = bake_fixture_json(SMOKE_PROP, dry_run=True)
        self.assertEqual(j1, j2)
        self.assertIn(EXPECTED_BAM, j1)
        self.assertIn(EXPECTED_DNA, j1)


class TestBakeBamDryRun(unittest.TestCase):
    def test_dry_run_does_not_require_egg2bam(self):
        egg2bam = shutil.which('egg2bam')
        plan = bake_fixture(SMOKE_PROP, dry_run=True)
        self.assertEqual(plan['status'], 'dry_run')
        self.assertFalse(plan['egg2bamRequired'])
        self.assertTrue(plan['dryRun'])
        self.assertEqual(plan['bamPath'], EXPECTED_BAM)
        self.assertEqual(plan['dnaCode'], EXPECTED_DNA)
        # Dry-run succeeds whether or not egg2bam is on PATH.
        self.assertIsNone(plan.get('hookResults'))
        # Document that CI does not need the binary.
        if egg2bam is None:
            self.assertIsNone(shutil.which('egg2bam'))

    def test_dry_run_writes_plan_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'smoke_prop.bake.json'
            plan = bake_fixture(SMOKE_PROP, dry_run=True, plan_out=out)
            self.assertTrue(out.is_file())
            loaded = json.loads(out.read_text(encoding='utf-8'))
            self.assertEqual(loaded['bamPath'], EXPECTED_BAM)
            self.assertEqual(loaded['dnaCode'], EXPECTED_DNA)
            self.assertEqual(plan['planOut'], str(out))

    def test_package_exports(self):
        import toontown.usd as usd_pkg
        self.assertTrue(callable(usd_pkg.bake_fixture))
        self.assertTrue(callable(usd_pkg.plan_from_fixture))
        self.assertTrue(callable(usd_pkg.plan_to_json))


class TestBakeHooks(unittest.TestCase):
    def tearDown(self):
        # Restore stub registry after tests that register hooks.
        for hook_id in list(HOOK_POINTS.keys()):
            register_hook(hook_id, None)

    def test_hook_points_documented(self):
        hooks = describe_hooks()
        ids = [h['id'] for h in hooks]
        self.assertEqual(ids, ['usd_to_egg', 'egg2bam', 'dna_register'])
        for h in hooks:
            self.assertEqual(h['registered'], 'stub')
            self.assertTrue(h['doc'])
            low = h['doc'].lower()
            for token in _BANNED:
                self.assertNotIn(token, low)

        # Module docstring / HOOK_POINTS name the same extension points.
        self.assertIn('usd_to_egg', bake_bam.HOOK_POINTS)
        self.assertIn('egg2bam', bake_bam.HOOK_POINTS)
        self.assertIn('dna_register', bake_bam.HOOK_POINTS)
        mod_doc = (bake_bam.__doc__ or '').lower()
        self.assertIn('egg2bam', mod_doc)
        self.assertIn('hook', mod_doc)
        for token in _BANNED:
            self.assertNotIn(token, mod_doc)

    def test_execute_with_stub_hooks_skips_workers(self):
        plan = bake_fixture(SMOKE_PROP, dry_run=False)
        self.assertFalse(plan['dryRun'])
        self.assertEqual(plan['status'], 'planned_no_workers')
        results = plan['hookResults']
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r['status'] == 'skipped_stub' for r in results))

    def test_registered_hook_runs_on_execute(self):
        seen = []

        def fake_egg2bam(plan):
            seen.append(plan['bamPath'])
            return {'status': 'ok', 'detail': 'fake bam written'}

        register_hook('egg2bam', fake_egg2bam)
        plan = bake_fixture(SMOKE_PROP, dry_run=False)
        self.assertEqual(seen, [EXPECTED_BAM])
        by_id = {r['id']: r for r in plan['hookResults']}
        self.assertEqual(by_id['egg2bam']['status'], 'ok')
        self.assertEqual(by_id['usd_to_egg']['status'], 'skipped_stub')
        self.assertEqual(plan['status'], 'baked')


class TestBakePlanErrors(unittest.TestCase):
    def test_missing_prop_raises(self):
        from toontown.usd.bake_plan import plan_from_parsed

        with self.assertRaises(BakePlanError):
            plan_from_parsed(
                {'kinds': ['TcStreetRoot'], 'primRecords': [], 'customData': {}},
                source='no_prop',
            )

    def test_missing_dna_code_raises(self):
        from toontown.usd.bake_plan import plan_from_parsed

        parsed = {
            'kinds': ['TcProp'],
            'prims': ['P'],
            'primRecords': [{
                'name': 'P',
                'kind': 'TcProp',
                'customData': {
                    'kind': 'TcProp',
                    'bamPath': 'phase_5/models/props/x.bam',
                },
            }],
            'customData': {},
        }
        with self.assertRaises(BakePlanError) as ctx:
            plan_from_parsed(parsed, source='no_dna')
        self.assertIn('dnaCode', str(ctx.exception))


class TestNoKhInBakeModules(unittest.TestCase):
    def test_bake_sources_clean(self):
        # Production modules only — this test file holds the ban list itself.
        for rel in (
            'toontown/usd/bake_plan.py',
            'toontown/usd/bake_bam.py',
        ):
            text = (REPO_ROOT / rel).read_text(encoding='utf-8').lower()
            for token in _BANNED:
                self.assertNotIn(token, text, f'{rel} has banned token')


if __name__ == '__main__':
    unittest.main()
