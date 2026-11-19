"""Offline USD → BAM bake entry for Toon City props (dry-run stub).

Production path (plan PR 3): compose / validate USDA → emit a bake plan →
eventually run real workers (USDA→EGG→``egg2bam``, DNA code registration).

This module is **headless** and **dry-run by default**. It does **not**
invoke ``egg2bam``, Maya, Blender, or Hydra. Cloud agents and CI stay green
without DCC binaries or a display.

Hook points for real bake workers
---------------------------------
Plug real implementations into the callables registered under
``HOOK_POINTS`` (or subclass / replace via ``register_hook``). Dry-run
never calls them; ``bake_fixture(..., dry_run=False)`` invokes each hook
in order and records status on the plan. Missing hooks remain stubs and
do not fail dry-run.

| Hook id         | Intended work                                      |
| --------------- | -------------------------------------------------- |
| ``usd_to_egg``  | Convert USDA geom / materials → EGG (or mesh IR)   |
| ``egg2bam``     | Shell out to ``egg2bam`` → ``phase_*/models/….bam`` |
| ``dna_register``| Emit / merge DNA storage code for PropPool / DNA   |

Non-goals (this PR): no gameplay loader changes, no cream FX, no KH
content, no Hydra imaging in the client.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Optional

from toontown.usd.bake_plan import (
    BakePlanError,
    plan_from_fixture,
    plan_to_json,
    write_plan_json,
)

# ---------------------------------------------------------------------------
# Worker hook registry (documented extension points)
# ---------------------------------------------------------------------------

HookFn = Callable[[Mapping[str, Any]], Mapping[str, Any]]

HOOK_POINTS: Dict[str, Optional[HookFn]] = {
    # Convert USDA geom → EGG (or direct mesh IR). Real worker: DCC / pxr.
    'usd_to_egg': None,
    # Run egg2bam → phase_*/models/….bam. Real worker needs egg2bam on PATH.
    'egg2bam': None,
    # Register DNA storage code string for PropPool / DNAStorage.
    'dna_register': None,
}

_HOOK_ORDER = ('usd_to_egg', 'egg2bam', 'dna_register')


def register_hook(hook_id: str, fn: Optional[HookFn]) -> None:
    """Install or clear a bake worker hook (``None`` restores stub)."""
    if hook_id not in HOOK_POINTS:
        raise KeyError(
            f'Unknown bake hook {hook_id!r}; '
            f'known: {", ".join(_HOOK_ORDER)}'
        )
    HOOK_POINTS[hook_id] = fn


def describe_hooks() -> List[Dict[str, str]]:
    """Return human-readable hook point docs for tooling / README."""
    docs = {
        'usd_to_egg': (
            'Convert USDA geometry/materials to EGG or an intermediate mesh '
            'IR. Optional pxr; never required for dry-run CI.'
        ),
        'egg2bam': (
            'Invoke egg2bam (or equivalent) to write the target '
            'phase_*/models/….bam path from the plan. Dry-run skips this '
            'entirely — no egg2bam binary needed.'
        ),
        'dna_register': (
            'Emit or merge a DNA storage code string (tc:dnaCode) so '
            'PropPool / DNAStorage can resolve the baked BAM at runtime.'
        ),
    }
    out: List[Dict[str, str]] = []
    for hook_id in _HOOK_ORDER:
        out.append({
            'id': hook_id,
            'registered': 'yes' if HOOK_POINTS.get(hook_id) else 'stub',
            'doc': docs[hook_id],
        })
    return out


def _run_hooks(plan: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """Invoke registered hooks in order; stubs record skipped status."""
    results: List[Dict[str, Any]] = []
    for hook_id in _HOOK_ORDER:
        fn = HOOK_POINTS.get(hook_id)
        entry: Dict[str, Any] = {'id': hook_id}
        if fn is None:
            entry['status'] = 'skipped_stub'
            entry['detail'] = (
                f'No worker registered for {hook_id}; '
                'see bake_bam.HOOK_POINTS / register_hook'
            )
        else:
            try:
                result = dict(fn(plan))
                entry['status'] = str(result.get('status', 'ok'))
                entry['detail'] = result.get('detail')
            except Exception as exc:  # pragma: no cover - worker-specific
                entry['status'] = 'error'
                entry['detail'] = str(exc)
        results.append(entry)

    plan['hookResults'] = results
    if any(r['status'] == 'error' for r in results):
        plan['status'] = 'failed'
    elif all(r['status'] == 'skipped_stub' for r in results):
        plan['status'] = 'planned_no_workers'
    else:
        plan['status'] = 'baked'
    return plan


def bake_fixture(
    name: str,
    *,
    dry_run: bool = True,
    plan_out: Optional[Path] = None,
) -> Dict[str, Any]:
    """Offline bake entry for a USD fixture (default: dry-run plan only).

    Parameters
    ----------
    name:
        Fixture stem or ``.usda`` filename under ``toontown/usd/fixtures/``.
    dry_run:
        When True (default), emit the bake plan JSON structure and **do not**
        call ``egg2bam`` or any registered hooks. Safe for cloud agents.
    plan_out:
        Optional filesystem path to write the plan JSON.

    Returns
    -------
    dict
        Deterministic bake plan (see ``bake_plan.plan_from_fixture``).
    """
    plan = plan_from_fixture(name, dry_run=dry_run)

    if dry_run:
        plan['status'] = 'dry_run'
        plan['egg2bamRequired'] = False
        plan['note'] = (
            'Dry-run only: no egg2bam, no DCC, no Hydra. '
            'Hook points documented in toontown.usd.bake_bam.HOOK_POINTS.'
        )
    else:
        plan['dryRun'] = False
        plan['egg2bamRequired'] = HOOK_POINTS.get('egg2bam') is not None
        _run_hooks(plan)

    if plan_out is not None:
        write_plan_json(plan, Path(plan_out))
        plan['planOut'] = str(Path(plan_out))

    return plan


def bake_fixture_json(
    name: str,
    *,
    dry_run: bool = True,
    indent: int = 2,
) -> str:
    """Convenience: bake (dry-run) and return deterministic JSON text."""
    return plan_to_json(bake_fixture(name, dry_run=dry_run), indent=indent)


def main(argv: Optional[List[str]] = None) -> int:
    """Minimal CLI: ``python -m toontown.usd.bake_bam smoke_prop``."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description=(
            'Offline USD prop bake stub (dry-run by default; no egg2bam).'
        ),
    )
    parser.add_argument(
        'fixture',
        nargs='?',
        default='smoke_prop',
        help='Fixture stem under toontown/usd/fixtures/ (default: smoke_prop)',
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Invoke registered hooks (still no-op if hooks are stubs)',
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='Optional path to write bake plan JSON',
    )
    parser.add_argument(
        '--describe-hooks',
        action='store_true',
        help='Print hook point docs and exit',
    )
    args = parser.parse_args(argv)

    if args.describe_hooks:
        for hook in describe_hooks():
            print(f"{hook['id']} [{hook['registered']}]: {hook['doc']}")
        return 0

    try:
        plan = bake_fixture(
            args.fixture,
            dry_run=not args.execute,
            plan_out=args.output,
        )
    except (BakePlanError, FileNotFoundError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1

    sys.stdout.write(plan_to_json(plan))
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
