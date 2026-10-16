# Owner chat backfill implementation boundaries

The portable review tool preserves source receipts, aspect scope and explicit
owner confirmations without granting whole-trial approval to component feedback.

Regression coverage uses disposable synthetic data for:

- Chat metadata and null trial bindings.
- Per-aspect precedence, deduplication and independent unbound receipts.
- Separate component counts and element summaries.
- Browser confirmation with null stars and no invented optics.
- Pairwise evidence when no catalog image is available.
- External data/artifact configuration and stdlib runtime portability.

Run `python scripts/run_tests.py` for offline tests. Optional browser coverage
requires `OWNER_REVIEW_BROWSER_MODULE` and, when needed,
`OWNER_REVIEW_CHROME`. Skipped browser tests are not browser validation.

Keep live chat imports, service restarts, downstream mirror synchronization and
project-specific registries outside this source change. See the
[privacy boundary](../../references/owner-review-port.md) and the
[synthetic case study](../../case-studies/owner-review-synthetic.md).
