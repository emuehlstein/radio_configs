"""Cross-radio interop invariants.

These tests verify that the same *portable group* renders to the same
freq/tone/mode across every radio config it lands in. If two radios
disagree on the APRS freq, this file catches it before we push to a
handheld.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from radio_configs.models import load_groups, load_radios
from radio_configs.resolver import resolve_layout


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def groups():
    return load_groups(ROOT / "groups")


@pytest.fixture(scope="module")
def radios():
    return load_radios(ROOT / "radios")


def test_all_radios_resolve(groups, radios):
    """Every radio in radios/ must resolve without error."""
    assert radios, "no radios found"
    for rid, radio in radios.items():
        layout = resolve_layout(radio, groups)
        assert layout.radio_id == rid
        # capacity checks are inside resolve_layout


def test_group_freq_consistency(groups):
    """Groups may only define one freq/tone per short_name across their channels.

    This is a sanity check on the groups themselves before we even map them.
    """
    for gid, g in groups.items():
        seen: dict[str, tuple] = {}
        for entry in g.channels:
            if entry.inline is None:
                continue
            key = entry.inline.short_name
            sig = (
                entry.inline.rx_freq_mhz,
                entry.inline.tx_freq_mhz,
                entry.inline.bandwidth,
                repr(entry.inline.rx_tone),
                repr(entry.inline.tx_tone),
            )
            if key in seen and seen[key] != sig:
                pytest.fail(
                    f"group {gid!r} short_name {key!r} has conflicting definitions: "
                    f"{seen[key]} vs {sig}"
                )
            seen[key] = sig


def test_aprs_freq_is_stable(groups):
    """Nail down the North American APRS freq. 144.390 or bust."""
    g = groups.get("aprs_vhf")
    assert g, "aprs_vhf group missing"
    for entry in g.channels:
        if entry.inline and entry.inline.short_name == "APRS":
            assert entry.inline.rx_freq_mhz == 144.390
            assert entry.inline.tx_freq_mhz == 144.390
            return
    pytest.fail("aprs_vhf group has no 'APRS' short_name channel")


def test_family_net_uses_gmrs_frequencies(groups):
    """Family net channels must be in the GMRS band (462-467 MHz)."""
    g = groups.get("family_net")
    assert g, "family_net group missing"
    for entry in g.channels:
        if entry.inline:
            assert 462.0 <= entry.inline.rx_freq_mhz <= 467.7125, \
                f"family_net {entry.inline.short_name!r} out of GMRS range"


def test_weather_is_rx_only(groups):
    """Every NOAA WX channel must be marked rx_only."""
    g = groups.get("noaa_weather")
    assert g, "noaa_weather group missing"
    for entry in g.channels:
        assert entry.inline and entry.inline.rx_only, \
            f"noaa_weather {entry.inline.short_name!r} must be rx_only"
