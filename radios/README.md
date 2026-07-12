# Radios

Per-physical-device configs. Each file names one radio and declares
which groups belong on which container slot (region / zone / bank /
whatever), plus TX policy and any per-device overrides.

## Schema

```yaml
radio:
  id: "n76-vero"                    # stable, kebab-case, unique
  name: "Vero VR-N76"               # display name
  vendor: "Vero"
  model: "VR-N76"
  serial: "..."                     # optional
  target: "n76"                     # matches targets/<target>/
  ble_address: "377F7AC2-..."       # optional; benlink auto-scans if missing

  license:
    holder: "Eric M."
    call: "KC9MHE"                  # optional
    classes: ["amateur", "gmrs"]    # which service-license classes apply

  tx_policy:
    default_disabled: true
    enabled_services: ["amateur", "gmrs"]
    # Enable TX only on channels whose group service ∈ enabled_services.
    # Per-group and per-channel overrides via `overrides:` below.

  capacity:
    # Advisory. Targets enforce their own hard caps from `targets/<t>/limits.py`.
    containers: 5                   # regions (N76), zones (OpenGD77/DM32), banks
    channels_per_container: 32

  layout:
    # Ordered list of {container_slot, group_id, options}. Slot indexing
    # is target-specific (N76 uses 0..4 for regions; OpenGD77 uses 1..N).
    - slot: 0
      name: "Ham"                   # overrides radio-side container name
      groups: ["simplex_2m", "simplex_70cm", "chicago_2m_repeaters"]
      pad_with: null                # what to do with unused slots in the container
    - slot: 1
      name: "APRS"
      groups: ["aprs_vhf", "packet_vhf"]
    ...

  overrides:
    # Per-channel escape hatches
    "chicago_2m_repeaters:NS9RC":
      rx_tone: 100.0                # correct a tone if SSRF is wrong
```

## Slot budgeting

Targets fail loudly if a group list exceeds a container's channel cap.
The mapper's job is to either fit everything, split a group across
containers, or ask the user to prune.
