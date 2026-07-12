# Groups

A **group** is a portable channel-group primitive. Every physical radio
maps groups to whatever it calls "zone" / "region" / "bank" / "memory
scan list."

## Schema

```yaml
group:
  id: "aprs_vhf"                    # stable, kebab-case, unique
  name: "APRS VHF"                  # display name (may be truncated per radio)
  purpose: "APRS packet on VHF"     # human summary
  priority: 100                     # ordering hint; higher = earlier
  services: ["amateur"]             # advisory; enforced by radio TX policy
  license: "amateur"                # min license class required to TX
                                    #   values: none | gmrs | amateur

  channels:
    # Each entry either references an SSRF assignment by id, or defines
    # an ad-hoc channel inline. Inline is discouraged — prefer adding to
    # SSRF and referencing.

    - ssrf_ref: "asgn_amateur_aprs_144390"        # canonical form
      overrides:
        short_name: "APRS"           # radio-agnostic short label
        scan: false
        rx_only: false

    - inline:                        # escape hatch
        short_name: "TEST"
        rx_freq_mhz: 146.520
        tx_freq_mhz: 146.520
        mode: "FM"
        bandwidth: "wide"            # wide | narrow
        rx_tone: null                # null | float (PL Hz) | {dcs: 023}
        tx_tone: null
        scan: true
        rx_only: false
```

## Group vs Zone vs Region

| Concept       | OpenGD77 | DM-32 | N76      | FT-2800M | Baofeng UV-5R | truSDX |
|---------------|----------|-------|----------|----------|---------------|--------|
| Container     | Zone     | Zone  | Region   | (none)   | (none)        | Bank   |
| Container cap | 250      | 250   | 5        | ~200 mem | 128 mem       | 4      |
| Channels/ea   | 80       | 16    | 32       | flat     | flat          | flat   |
| Total ch cap  | 1024     | 4000  | 160      | ~200     | 128           | ~50    |

The N76's tiny 160-channel budget is the tightest constraint. When a
radio can't fit every group, `targets/<radio>/mapper.py` decides truncation.

## Naming

Radio displays vary from 5 chars (Baofeng) to 12+ (N76). Groups should
declare a `short_name` (≤6 chars) that every radio can render, plus
optionally a `name` (≤12 chars) for radios with room. The `targets`
adapters may truncate further per their own display limits.
