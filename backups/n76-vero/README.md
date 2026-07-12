# n76-vero backups

Full-radio snapshots (all 6 regions × 32 slots + region names) taken
before every `--apply` write. Format documented in
`src/radio_configs/targets/n76/writer.py::_save_backup`.

Restore with:

```zsh
uv run python -m radio_configs.targets.n76.writer --radio n76-vero --rollback
```

`--rollback` restores from the **most recent** backup in this
directory. If you need to restore from an older one, rename it so it
sorts last, or edit the plan and `--apply` again.

## Log

| File                                    | Notes |
| --------------------------------------- | ----- |
| `n76-full-backup-20260711-235149.json`  | Pre-Chicago-layout write. Captures Eric's earlier MA-oriented setup: regions `Family Ops` / `HAM` / `GRMS` / `Marine` / `MURS` / `GMRS`. Restore this to get the previous state back. |
