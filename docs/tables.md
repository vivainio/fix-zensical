# Tables

A wide table. Use the full-screen button to read it comfortably.

| Option | Argument | Default | Effect | Exit code | Writes files | Use in CI | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *(none)* | | `.` | Install or update in every `zensical*.toml` | 0 | yes | no | Idempotent |
| `--repo` | path | `.` | Repository root | 0 | yes | yes | Finds configs and workflows |
| `--config` | file | all `zensical*.toml` | Only process these configs (repeatable) | 0 | yes | yes | Relative to repo |
| `--shared` | folder | off | One shared copy, per-file symlinks per book | 0 | yes | yes | Several books in one repo |
| `--check` | | off | Change nothing, report stale files | 1 if stale | no | yes | Fails the build when out of date |
| `--dry-run` | | off | Show what would change | 0 | no | no | Preview |
