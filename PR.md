# feat: establish dream-loop v2 with reconciled main capabilities

## PR target

- Repository: **kvnloo/dream-loop**, not achimala/dream-loop.
- Base: `main`
- Head: `feat/dream-loop-v2`
- Proposed title: **feat: establish dream-loop v2 with reconciled main capabilities**

## Summary

Make dream-loop an independently maintained, project-agnostic visual iteration method with owner gates, calibrated critics, final-density/max-zoom fidelity, an event-sourced discovery tree and domain packs.

Merge the original v2 development line into fork main with both histories preserved. Keep v2's core/methods/templates, restore the newer main Fal/preview safeguards, and retain every main helper, schema and optional historical recipe. [RECONCILE.md](RECONCILE.md) accounts for all 48 main files, including 20 missing from the original v2 tip. Only conflicting historical **policy authority** is retired—not implementation capabilities.

- Retain PR #6's discovery implementation and tests byte-for-byte; cross-test all three implementations against both source suites.
- Keep Classic/Pro/Plus under explicit v2 owner/scope/permission overrides; repair Classic links and expose the retained tools/schemas through the reference index.
- Add behavioral tile-grid compatibility tests and document existing grid/overlap limits.
- Rewrite README and contribution guidance; add v2.0.0 changelog, original project and Dream-RSI credit, and Hermes/Claude Code/Codex installation.
- Keep upstream MIT copyright and permission text unchanged; the upstream and local license blob match.

## Validation

Local validation passed: **13 runner commands, 26 standalone Node tests, standalone HERMES_HOME-free lint, and six ledger cross-test combinations; zero failures.** [RECONCILE.md](RECONCILE.md) records the scope and limits. Commands:

- `python scripts/run_tests.py` (all Python and Node tests, plus lint)
- `node --test scripts/*.test.mjs`
- `env -u HERMES_HOME python scripts/lint_skill.py`
- Six ledger cross-test combinations; original v2 versus main implementation/test diffs are trailing-newline only.
- Every main file accounted for, both parents retained, clean final tree and `dream-loop` / `2.0.0` frontmatter.

Tests qualify offline machinery and localhost capture, not renderer quality, target-family calibration, model delivery or owner acceptance. No live API spending was required. The legacy tiled mesh helper retains documented divisible-grid and manual scaled-overlap constraints.

## Prepared publication commands — NOT EXECUTED

Run only after owner review, with a clean `feat/dream-loop-v2` checkout and freshly checked base. No force push is needed. Prefer a merge commit when accepting this PR to keep the explicit reconciliation ancestry.

```sh
git push -u origin feat/dream-loop-v2
gh pr create --repo kvnloo/dream-loop --base main --head feat/dream-loop-v2 --title "feat: establish dream-loop v2 with reconciled main capabilities" --body-file PR.md
```

The `--repo kvnloo/dream-loop` flag is mandatory: `gh pr create` in a fork can otherwise select its upstream parent. Do not run these commands against achimala/dream-loop. No PR, push, release tag, GitHub release or repository settings change has been made by this work.

## Proposed GitHub metadata — NOT APPLIED

**Description:** Evidence-driven visual iteration for agents: owner gates, calibrated critics, max-zoom fidelity, discovery history and domain packs.

**Topics:** `visual-iteration`, `agent-skills`, `hermes-agent`, `claude-code`, `codex`, `blender`, `threejs`, `visual-evaluation`, `human-in-the-loop`, `dream-rsi`.

## Fork-network decision — separate owner action

The project can present its own identity without detaching. Keeping the fork network preserves existing stars, issues, PR discussion/links and the upstream relationship; the GitHub fork badge remains.

If detachment is desired, contact [GitHub Support](https://support.github.com/request/fork) first and explicitly ask what can be preserved. Do not promise retention of stars/issues/PR links without their answer. Recreating a standalone repository preserves Git history if copied correctly but does **not** automatically transfer stars, watchers, issues, PRs, comments, settings or old numbered discussion links. Deleting/recreating the existing name is destructive; creating a separate repository and leaving the old one as a read-only pointer is less destructive but splits identity and still requires migration work.

**Current documentation correction:** the premise that only Support or recreation can detach a fork is no longer exhaustive. [GitHub's current detach documentation](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/detaching-a-fork) also describes a **Leave fork network** setting for eligible public forks under 1 GB with no child forks. It explicitly warns of lost issues, PRs, wikis, stars, watchers, comments and other metadata, and says detachment is permanent. Eligibility and preservation have **not** been qualified for this repository. This document prepares options only; no detachment or destructive command is authorized or executed.
