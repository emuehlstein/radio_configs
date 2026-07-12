# SSRF-Lite data sourcing

SSRF-Lite reference data comes from
[`emuehlstein/OpenGD77_SSRFLite_Generator`](https://github.com/emuehlstein/OpenGD77_SSRFLite_Generator)
and is vendored into this repo as a **git subtree** at
`vendor/OpenGD77_SSRFLite_Generator/`. The actual SSRF YAML files live
under `vendor/OpenGD77_SSRFLite_Generator/ssrf/`.

This keeps `radio_configs` self-contained (no cross-repo runtime
coupling) while letting SSRF-Lite reference data continue to live in
its upstream repo where it's already curated.

## Refresh from upstream

```zsh
git fetch ssrf-upstream main    # remote already configured
git subtree pull --prefix=vendor/OpenGD77_SSRFLite_Generator \
  ssrf-upstream main --squash
```

If the remote isn't set up yet in your local clone:

```zsh
git remote add ssrf-upstream \
  git@github.com:emuehlstein/OpenGD77_SSRFLite_Generator.git
```

## Push local edits back upstream (rare)

SSRF reference data should live in the source repo, not here. If you
need to push a fix out:

```zsh
git subtree push --prefix=vendor/OpenGD77_SSRFLite_Generator \
  ssrf-upstream ssrf-changes-YYYYMMDD
# then open a PR from that branch upstream
```

## Data layout

```
vendor/OpenGD77_SSRFLite_Generator/
├── ssrf/                             ← SSRF-Lite YAML lives here
│   ├── plans/US/…                    ← FCC channel plans (GMRS, MURS, etc.)
│   ├── systems/US/IL/Cook/Chicago/…  ← Chicagoland systems
│   ├── talkgroups/                   ← DMR/D-STAR talkgroup catalogs
│   └── _schema/                      ← Pydantic schema for validation
├── policies/                         ← Rendering opinions (upstream)
├── profiles/                         ← Preset SSRF filters (upstream)
└── generate_*.py                     ← Upstream CSV/CPS generators
```

Our `groups/*.yml` files can reference SSRF assignments by id
(e.g. `asgn_gmrs_evanston_725`) using the `ssrf_ref:` field — the
resolver will materialize them from `vendor/OpenGD77_SSRFLite_Generator/ssrf/`.
