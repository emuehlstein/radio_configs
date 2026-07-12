# SSRF-Lite data sourcing

The `ssrf/` directory in this repo is **vendored** from
[`emuehlstein/OpenGD77_SSRFLite_Generator`](https://github.com/emuehlstein/OpenGD77_SSRFLite_Generator).
This keeps `radio_configs` self-contained (no cross-repo runtime coupling)
while letting SSRF-Lite reference data live where it's already curated.

Currently vendored as a **subtree** rooted at `ssrf/`. To pull upstream
updates:

```zsh
git remote add ssrf-upstream git@github.com:emuehlstein/OpenGD77_SSRFLite_Generator.git 2>/dev/null || true
git fetch ssrf-upstream main
git subtree pull --prefix=ssrf ssrf-upstream main --squash
```

To push local edits back upstream (rare; SSRF-Lite reference data
should generally live in the source repo, not here):

```zsh
git subtree push --prefix=ssrf ssrf-upstream ssrf-changes-YYYYMMDD
# then open a PR from that branch upstream
```

## Alternative: git submodule

If you prefer a submodule instead of a subtree (avoids pulling upstream
history into this repo, but every clone requires
`git submodule update --init`), swap the recipe above for:

```zsh
git submodule add git@github.com:emuehlstein/OpenGD77_SSRFLite_Generator.git ssrf-src
ln -s ssrf-src/ssrf ssrf
```

The subtree approach is currently in use because it makes CI and offline
builds simpler.

## Policies

Upstream also ships `policies/` (rendering opinions). We mirror the ones
we use into `policies/` in this repo so per-radio configs can compose
them, but we do **not** subtree the policies tree — those are opinions
specific to this fleet.
