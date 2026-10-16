# Owner review runtime mirror

The source of truth is quackles `tools/owner-review/`. Dream-loop's `scripts/`
copy shares the exact runtime, schema and regression-test bytes. Keep changes
synchronized with the public tool's `sync_mirror.py --mirror <dream-loop-tree>`
command. Use `--write` to synchronize and `--check` to verify parity.

The tool is derived from dream-loop under the [MIT license](../LICENSE). Its
stdlib server and catalog do not import private history seeds or imaging packages.
The optional `seed_owner_rating.py` remains local to dream-loop and imports the
generic `Catalog` helper. Historical judge preparation still requires dream-loop's
optional `ab_judge` helper and explicit pair IDs in the input anchor or manifest.

```sh
python3 scripts/owner_rating.py --data "$OWNER_REVIEW_DATA"
python3 scripts/run_tests.py
```

Pass the existing data directory explicitly when integrating this change. The
portable default is `$XDG_CACHE_HOME/owner-review`, falling back to
`$HOME/.cache/owner-review`. `OWNER_REVIEW_ARTIFACTS` can select the artifact root;
otherwise polling uses the data directory's sibling `night-v2`. `--no-watch`
serves an existing catalog without polling. No existing service is restarted by
this change.

Chat evidence uses original UTC timestamps and verbatim quotes. Null trial IDs
are valid only for element scope. UI confirmation appends an event with the same
aspect, scope and source receipt; stars remain null unless the owner selects them.
Only trial scope can change trial acceptance. `owner_aspects` describes component
feedback by mechanism. `owner-evidence.json` retains unbound element receipts
without assigning them to a mechanism, and a confirmation supersedes only its own
unbound source receipt.

The synthetic fixture and tests do not read chats or live label files. The mirror
includes archive-grounded dream planning and read-only ingestion. Preserve both
sets of behavior when integrating concurrent changes; run both suites and the
mirror parity check. Historical backfill and service restarts require separate
explicit owner authorization.
