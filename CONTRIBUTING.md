# Contributing

Contribute to [kvnloo/dream-loop](https://github.com/kvnloo/dream-loop). Read [SKILL.md](SKILL.md): v2 is the default method; Classic/Pro/Plus are opt-in compatibility recipes, not competing defaults. Preserve the MIT notice and [Anshu Chimala's original attribution](https://github.com/achimala/dream-loop).

1. **Orient:** name the domain, policy or helper contract you are changing. Inspect the current base and preserve main-only capabilities when reconciling older feature branches; [RECONCILE.md](RECONCILE.md) records the v2 decisions.
2. **Evidence:** run `python scripts/run_tests.py`, `node --test scripts/*.test.mjs` and `python scripts/lint_skill.py`. Add behavioral tests for helper changes; do not replace behavior with source-string assertions. Never spend on APIs or upload private material as a test default.
3. **Visual methods:** include actual output, controls, failure cases and transfer limits. A beautiful example or passing unit test does not establish a method's general quality. State which domain/optional recipe was exercised and what remains unverified.
4. **PR:** target this repository's `main` explicitly: `gh pr create --repo kvnloo/dream-loop --base main --head YOUR_BRANCH`. On a fork, the CLI otherwise may choose the upstream parent. Maintainers merge; workers and bots do not.

The [Verified OSS Loop](https://github.com/kvnloo/verified-oss-loop) contribution contract is a useful evidence standard. Keep private project artifacts, credentials and rendered production evidence out of this skill repository. Do not push or open a PR without the owner's authorization.
