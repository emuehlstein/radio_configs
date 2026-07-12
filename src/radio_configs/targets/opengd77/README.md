# OpenGD77 target

Renders `ResolvedLayout` → OpenGD77 CPS CSVs:
`Channels.csv`, `Zones.csv`, `Contacts.csv`, `TG_Lists.csv`.

Not yet implemented. The write path from
`emuehlstein/OpenGD77_SSRFLite_Generator/generate_opengd_import.py`
already produces valid CSVs from SSRF+profile+policy. Porting plan:

1. Extract the OpenGD77 rendering logic from
   `OpenGD77_SSRFLite_Generator` into an adapter that consumes
   `ResolvedLayout` instead of the SSRF+profile pipeline directly.
2. Keep contacts + TG list generation from the upstream (DMR-specific).
3. Wire `radio-configs build --radio rt3-black` to emit into
   `artifacts/rt3-black/`.
