# CHIRP target

Renders `ResolvedLayout` → CHIRP generic CSV, which CHIRP can import
into any supported radio.

Not yet implemented. Notes:
- CHIRP CSV column order matters. Reference:
  <https://chirp.danplanet.com/projects/chirp/wiki/CSV_Format>
- CHIRP handles the FT-2800M and every Baofeng we own. It doesn't
  handle the DM-32 or the N76 — those get their own adapters.
- Bank / memory slot mapping is flat for most CHIRP radios; the
  "container" from a layout becomes a bank column when the radio
  supports it.
