# jigsaw

Per-week subdirectory layout: `YYYY-Www/{source.png, meta.yaml, placements/}`. The `meta.yaml` records `generated_at`, `model`, `prompt`, and a `seed` (sha256 prefix of `source.png`) used to derive piece geometry deterministically in the browser.

Each placement is a commit creating `placements/NNN.json` (zero-padded piece id) with body `{"slot": [row, col]}`. The commit message body carries the canonical YAML event payload.
