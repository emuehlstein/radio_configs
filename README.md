# radio_configs

**One canonical spec, many radios that talk to each other.**

This repo orchestrates codeplug generation across a heterogeneous fleet:
Vero VR-N76, TYT MD-UV380/RT3 (OpenGD77), BTECH DM-32 (`dmrconfig`),
Yaesu FT-2800M, (tr)uSDX, and various Baofengs (CHIRP). The source of
truth for RF facts is SSRF-Lite YAML; per-radio adapters render those
facts into whatever format each radio wants to eat.

## Design

```
┌────────────────┐   ┌────────────────┐   ┌────────────────┐   ┌────────────┐
│ SSRF-Lite      │ → │ Groups         │ → │ Radios         │ → │ Targets    │
│ (RF facts)     │   │ (opinions)     │   │ (device cfgs)  │   │ (adapters) │
└────────────────┘   └────────────────┘   └────────────────┘   └────────────┘
```

- **SSRF-Lite** — vendored from
  [`emuehlstein/OpenGD77_SSRFLite_Generator`](https://github.com/emuehlstein/OpenGD77_SSRFLite_Generator).
  Reference-only: freq, mode, tone, service, license class, coordinates.
  See `ssrf/` (linked or subtree-merged; see `SSRF-SOURCING.md`).
- **Groups** — portable channel-group primitives that map to whatever a
  given radio calls "zone" / "region" / "bank" / "memory scan list."
  Live in `groups/*.yml`.
- **Radios** — one file per physical device (`radios/n76-vero.yml`,
  `radios/rt3-black.yml`, ...) declaring which groups belong on which
  region/zone slot, TX policy, naming conventions, and any per-device
  overrides.
- **Targets** — per-radio adapters that consume `{ssrf + groups +
  radio.yml}` and emit the native format:
  - `targets/n76/`   — `benlink` live BLE / RFCOMM write (Vero VR-N76 firmware; 6 regions x 32 slots = 192 channels)
  - `targets/opengd77/` — CSVs for OpenGD77 CPS (RT3/UV380/MD-380/9600)
  - `targets/dm32/`  — `dmrconfig` text codeplug (BTECH DM-32)
  - `targets/chirp/` — CHIRP CSV/img (FT-2800M, Baofengs, TYT MD-9600)
  - `targets/trusdx/`— crib sheet + CAT commands (no native codeplug)

## Interop invariants

Cross-radio checks live in `tests/interop.py`:

- **APRS** must have identical freq/tone on every TX-capable VHF radio.
- **Family net / GMRS local** must be consistent across every GMRS radio.
- **Packet freqs** (VHF 1200 AFSK) must match between the FT-2800M
  Direwolf setup on the Bowmanville pi and any handheld running KISS TNC.
- **Simplex chat** channels must be identical across the fleet.

## Quick start

```zsh
# One-time
git submodule update --init --recursive   # pulls SSRF gen if used as submodule
uv sync

# Regenerate outputs for a specific radio
uv run python -m radio_configs build --radio n76-vero
uv run python -m radio_configs build --radio rt3-black --tx-service gmrs

# N76 live-write (BLE)
uv run python -m radio_configs.targets.n76.write --radio n76-vero --dry-run
uv run python -m radio_configs.targets.n76.write --radio n76-vero --apply
uv run python -m radio_configs.targets.n76.write --radio n76-vero --rollback

# Interop check
uv run python -m pytest tests/interop.py
```

## Layout

```
radio_configs/
├── README.md
├── SSRF-SOURCING.md          # how ssrf/ is vendored + refresh recipe
├── pyproject.toml
├── ssrf/                     # vendored from OpenGD77_SSRFLite_Generator
├── groups/                   # portable channel groups
│   ├── aprs_vhf.yml
│   ├── family_net.yml
│   ├── chicago_gmrs.yml
│   ├── chicago_amateur.yml
│   ├── noaa_weather.yml
│   └── ...
├── radios/                   # per-device configs
│   ├── n76-vero.yml
│   ├── rt3-black.yml
│   ├── dm32-1.yml
│   ├── ft2800m-bowmanville.yml
│   ├── trusdx-1.yml
│   └── uv5r-family-1.yml
├── targets/
│   ├── n76/
│   ├── opengd77/
│   ├── dm32/
│   ├── chirp/
│   └── trusdx/
├── artifacts/                # generated outputs (gitignored except backups/)
│   ├── n76-vero/
│   ├── rt3-black/
│   └── ...
├── backups/                  # radio state snapshots, kept in git
│   └── n76-vero/
└── tests/
    └── interop.py
```

## Safety

- **TX is off by default** for every generated channel. Use
  `--tx-service <service>` (or `--tx-all-services`) to opt in per service.
- N76 live writes always **full-backup all 5 regions to
  `backups/n76-vero/<timestamp>.json` before touching anything**, and
  ship with `--rollback`.
- Interop tests must pass before any live-write.

## Related repos

- `emuehlstein/OpenGD77_SSRFLite_Generator` — upstream SSRF-Lite + OpenGD77 generator
- `emuehlstein/benlink` (`n76-support` branch) — N76 BLE control library
- `emuehlstein/pyrepeater` — repeater controller (separate project)

## License

TBD. Data files (SSRF-Lite) inherit their upstream licenses.
