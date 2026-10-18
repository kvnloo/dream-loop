# Owner review portability and privacy

The runtime lives in `scripts/`. Its stdlib server and catalog do not require
project-specific history seeds or imaging packages. Downstream copies must test
compatibility explicitly; no private repository is a required source dependency.

```sh
python scripts/owner_rating.py --data "$OWNER_REVIEW_DATA"
python scripts/run_tests.py
```

Pass the data directory explicitly when integrating. The portable default is
`$XDG_CACHE_HOME/owner-review`, falling back to `$HOME/.cache/owner-review`.
`DREAM_LOOP_ADAPTER` selects an explicit trusted adapter file for project-specific
artifact layouts and live queues; see [meta-learning.md](meta-learning.md).
`--no-watch` serves an existing catalog without polling. No existing service is
restarted by a source change.

Catalog seeding requires an explicit external JSON manifest; see
[owner-rating.md](owner-rating.md). No private trial inventory, chat-ID decision
map, or inferred project root belongs in a distributable seed helper.

Chat evidence retains original UTC timestamps and verbatim receipts **locally**.
Null trial IDs are valid only for element scope. UI confirmation appends an event
with the same aspect, scope and source receipt; stars remain null unless selected.
Only trial scope can change trial acceptance. `owner_aspects` describes component
feedback by mechanism. `owner-evidence.json` retains unbound receipts without
assigning them to a mechanism.

Tests must generate synthetic fixtures without reading chats, production label
files, or private renders. Historical backfill, real data migration and service
restarts require separate authorization. Never publish generated reports or
catalogs merely because source tests pass: they can contain private paths and
verbatim conversations. Audit both the publishable tree and every outgoing Git
commit; a later deletion does not remove a disclosure from history.
