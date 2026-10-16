# Owner chat backfill and public review port

Implement the supplied owner-review spec locally. No live data, chat searches,
materializer runs, server restarts, fetches, pushes, or PRs.

1. RED: synthetic tests for chat metadata, null trial binding, precedence per
   aspect, history/deduplication, separate component counts and element summary.
   GREEN: update `scripts/meta_loop.py` without changing producer ownership.
2. RED: submission and browser tests for displaying receipts and confirming
   prefilled labels with null stars. GREEN: update server and UI; retain LOOK,
   CLEAR, scoped labels, retries and catalog polling.
3. RED: isolated stdlib/public-port tests. GREEN: extract generic catalog helpers,
   configure external data/artifact roots, preserve schema validation, copy shared
   runtime and tests byte-for-byte into quackles `tools/owner-review`. Add a
   synthetic fixture, launch/test scripts, license and source-of-truth docs.
4. Verify all dream-loop tests, tool tests, quackles npm test and npm run lint.
   Inspect privacy and mirror parity. Generate registry using existing script,
   write task receipt, commit both branches locally and report exact SHAs.

Watch malformed metadata, component labels replacing a previous trial label on
one aspect, replayed events, element-only confirmation with no candidates, and
catalog changes while a draft is active. Tests must use disposable local data.

Completed locally with observed RED then GREEN tests for every behavior change.
The independent review found dropped pairwise evidence and guessed optics on
quote-only confirmations; both now have browser regressions. Follow-up cases
cover a comparison with no catalog image and independent unbound receipts.

Final proof: the 20-command offline helper suite passes, including both headless
browser cases. The public tool suite passes 56 tests. Quackles npm test, lint and
5 registry tests pass. The existing unused-variable and Node module-type warnings
are recorded in the quackles task receipt. The mirror check confirms 18 identical
files. Parent integration and actual label import/service restart remain external
to this bounded code task.
