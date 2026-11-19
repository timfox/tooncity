#!/usr/bin/env python3
"""Headless tests: boss HP bar uses per-hostile finalePhase, not director.

After Elite/Ambush bar parity (#390), Silly P1/P2 reclaim director
finalePhase >= 1 was applied to every corrupt sync. P2 Smudge adds
(finalePhase=0 at spawn) became bar subjects and stole last-writer
ownership from the Overlord — the same anti-pattern soft-lock docs forbid.

Loads CorruptionGlobals with a ToontownGlobals stub — no Panda3D.
BossHpBarHud wiring is AST-checked (imports pull panda).

Run from repo root:
  python3 tests/test_boss_hp_bar_own_finale_phase.py
  python3 -m unittest tests.test_boss_hp_bar_own_finale_phase -v
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


def _ensure_pkg(name: str) -> types.ModuleType:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = [str(REPO_ROOT / name.replace('.', '/'))]
        sys.modules[name] = mod
    return sys.modules[name]


def _load_panda_free_corruption():
    if REPO_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    for pkg in (
            'toontown', 'toontown.toonbase', 'toontown.corruption',
            'toontown.reclaim'):
        _ensure_pkg(pkg)

    tg = types.ModuleType('toontown.toonbase.ToontownGlobals')
    tg.LoopyLane = LOOPY
    tg.PunchlinePlace = PUNCHLINE
    tg.SillyStreet = SILLY
    tg.ToontownCentral = 2000
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
    return cg


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding='utf-8')


def _function_body_names(rel: str, func_name: str) -> set[str]:
    """Names + attrs referenced inside a module-level function body."""
    tree = ast.parse(_read(rel))
    out = set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != func_name:
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                out.add(child.id)
            elif isinstance(child, ast.Attribute):
                out.add(child.attr)
    return out


class BossHpBarOwnFinalePhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cg = _load_panda_free_corruption()

    def test_p2_smudge_adds_not_bar_subjects(self):
        """Street Smudge adds keep finalePhase=0 — never own the Overlord bar."""
        cg = self.cg
        subject = cg.isBossOrChaseHpBarSubject
        resolve = cg.resolveBossHpBarFinalePhase
        # P2 add spawn names (director street phase must not be applied).
        self.assertFalse(subject(
            cg.ARCHETYPE_INK, name='Ink Smudge', finalePhase=0))
        self.assertFalse(subject(
            cg.ARCHETYPE_INK, name='Ink Smudge 1', finalePhase=0))
        self.assertFalse(subject(
            cg.ARCHETYPE_INK, name='Ink Smudge 2', finalePhase=0))
        self.assertEqual(resolve(0, 'Ink Smudge'), 0)
        self.assertEqual(resolve(0, 'Ink Smudge 2'), 0)
        # Overlord via own phase or name tokens still owns the bar.
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=1))
        self.assertTrue(subject(cg.ARCHETYPE_INK, finalePhase=2))
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord', finalePhase=0))
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord Rising', finalePhase=0))
        self.assertTrue(subject(
            cg.ARCHETYPE_INK, name='Ink Overlord Unleashed', finalePhase=0))
        self.assertEqual(resolve(0, 'Ink Overlord'), 1)
        self.assertEqual(resolve(0, 'Ink Overlord Unleashed'), 2)
        # Per-toon phase wins when already set on the DO.
        self.assertEqual(resolve(2, 'Ink Smudge'), 2)
        self.assertEqual(resolve(1, 'Ink Overlord'), 1)

    def test_hud_sync_ignores_reclaim_director_phase(self):
        """syncFromCorruptToon must not read reclaimDirector.finalePhase."""
        rel = 'toontown/reclaim/BossHpBarHud.py'
        names = _function_body_names(rel, 'syncFromCorruptToon')
        self.assertIn('isBossOrChaseHpBarSubject', names)
        self.assertIn('_subjectFields', names)
        self.assertIn('shouldClaimBossHpBarOwnership', names)
        # Soft-lock anti-pattern lock: never glue street phase onto pack adds.
        self.assertNotIn('reclaimDirector', names)
        self.assertNotIn('base', names)
        field_names = _function_body_names(rel, '_subjectFields')
        self.assertIn('resolveBossHpBarFinalePhase', field_names)
        self.assertIn('getattr', field_names)
        self.assertIn('finalePhase', field_names)
        src = _read(rel)
        sync_idx = src.index('def syncFromCorruptToon')
        sync_snip = src[sync_idx:sync_idx + 1400]
        self.assertIn('_subjectFields', sync_snip)
        self.assertNotIn('reclaimDirector', sync_snip)
        fields_idx = src.index('def _subjectFields')
        fields_snip = src[fields_idx:fields_idx + 900]
        self.assertIn("getattr(toon, 'finalePhase'", fields_snip)
        # Module docs still call out P2 Smudge / soft-lock anti-pattern.
        self.assertIn('soft-lock', src.lower())
        self.assertIn('P2 Smudge', _read(
            'toontown/corruption/CorruptionGlobals.py'))

    def test_globals_docs_forbid_director_phase_on_adds(self):
        cg_src = _read('toontown/corruption/CorruptionGlobals.py')
        resolve_idx = cg_src.index('def resolveBossHpBarFinalePhase')
        resolve_snip = cg_src[resolve_idx:resolve_idx + 500]
        self.assertIn('own finalePhase', resolve_snip)
        self.assertIn('P2 Smudge', resolve_snip)
        self.assertIn('never reclaim-director', resolve_snip)
        gate_idx = cg_src.index('def isBossOrChaseHpBarSubject')
        gate_snip = cg_src[gate_idx:gate_idx + 700]
        self.assertIn('own finalePhase', gate_snip)
        self.assertIn('P2 Smudge', gate_snip)
        self.assertIn('never reclaim-director', gate_snip)
        # Soft-lock prefer docs already forbid the same pattern.
        soft_idx = cg_src.index('def isSoftLockPrioritySubject')
        soft_snip = cg_src[soft_idx:soft_idx + 500]
        self.assertIn('own finalePhase', soft_snip)
        self.assertIn('P2 Smudge', soft_snip)

    def test_no_cream_kh(self):
        for rel in (
                'toontown/reclaim/BossHpBarHud.py',
                'toontown/corruption/CorruptionGlobals.py',
        ):
            src = _read(rel).lower()
            # Narrow: this PR's subject/resolve helpers stay juice-free.
            if rel.endswith('BossHpBarHud.py'):
                self.assertNotIn('creamwash', src)
                self.assertNotIn('creamsplash', src)
                self.assertNotIn('keyblade', src)
                self.assertNotIn('kingdom hearts', src)
            else:
                gate_idx = _read(rel).index('def resolveBossHpBarFinalePhase')
                snip = _read(rel)[gate_idx:gate_idx + 1200].lower()
                self.assertNotIn('keyblade', snip)
                self.assertNotIn('kingdom hearts', snip)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        BossHpBarOwnFinalePhaseTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
