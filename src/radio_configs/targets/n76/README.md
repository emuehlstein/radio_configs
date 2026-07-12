# N76 target

Live BLE writes to the Vero VR-N76 via
[`emuehlstein/benlink`](https://github.com/emuehlstein/benlink) (branch
`n76-support`).

## Radio-side limits

- **5 regions** × **32 slots** each = 160 channels total
- Region names are per-region strings (≤10 chars visible, may accept more)
- Channel names typically 8-10 chars visible

## Modes

- `write` — full write of every region in the radio config's layout
- `dry-run` — print the plan without touching the radio
- `rollback` — restore from the most recent backup

## Backup format

Full backups land under
`backups/n76-vero/n76-full-backup-<UTC timestamp>.json`. Every backup
snapshots **all 5 regions × 32 slots + region names** so any write is
fully reversible.

## Usage

```zsh
# Print the plan
uv run python -m radio_configs.targets.n76.writer --radio n76-vero --dry-run

# Apply (backs up first)
uv run python -m radio_configs.targets.n76.writer --radio n76-vero --apply

# Undo
uv run python -m radio_configs.targets.n76.writer --radio n76-vero --rollback
```

## Where this comes from

Derived from `emuehlstein/benlink/scripts/t3_region_setup_apply.py` —
that hand-written script proved the write path end-to-end. This adapter
generalizes it to read the plan from `{radio config + groups}` instead
of hard-coding it.
