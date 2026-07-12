"""Portable Pydantic models for the group / radio primitives.

These are intentionally target-agnostic. Every `targets/<name>/` adapter
translates from these models into whatever the radio wants to eat.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Tone
# ---------------------------------------------------------------------------

class DCS(BaseModel):
    """Digital Coded Squelch."""
    dcs: int = Field(ge=0, le=999)


Tone = float | DCS | None
"""PL Hz (float), DCS code, or no tone."""


# ---------------------------------------------------------------------------
# Channel primitives
# ---------------------------------------------------------------------------

Mode = Literal["FM", "NFM", "AM", "DMR"]
Bandwidth = Literal["wide", "narrow"]
License = Literal["none", "gmrs", "amateur"]


class InlineChannel(BaseModel):
    """Ad-hoc channel definition without an SSRF reference."""
    short_name: str = Field(max_length=8)
    name: str | None = Field(default=None, max_length=16)
    rx_freq_mhz: float
    tx_freq_mhz: float
    mode: Mode = "FM"
    bandwidth: Bandwidth = "wide"
    rx_tone: Tone = None
    tx_tone: Tone = None
    scan: bool = True
    rx_only: bool = False
    mute: bool = False


class ChannelRef(BaseModel):
    """A channel entry inside a group — either references SSRF or defines inline."""
    ssrf_ref: str | None = None
    inline: InlineChannel | None = None
    overrides: dict | None = None

    @field_validator("inline", mode="after")
    @classmethod
    def _one_of(cls, v, info):
        # Exactly one of ssrf_ref / inline must be set.
        ssrf_ref = info.data.get("ssrf_ref")
        if bool(ssrf_ref) == bool(v):
            raise ValueError("channel entry needs exactly one of ssrf_ref or inline")
        return v


class Group(BaseModel):
    """Portable channel group. Renders to region/zone/bank on target radios."""
    id: str
    name: str
    purpose: str = ""
    priority: int = 100
    services: list[str] = Field(default_factory=list)
    license: License = "none"
    channels: list[ChannelRef]


class GroupFile(BaseModel):
    """Top-level shape of a `groups/*.yml` file."""
    group: Group


def load_group(path: Path) -> Group:
    """Load one group YAML into a Group model."""
    raw = yaml.safe_load(path.read_text())
    return GroupFile.model_validate(raw).group


def load_groups(dir: Path) -> dict[str, Group]:
    """Load every group YAML under `dir/` keyed by group.id."""
    groups: dict[str, Group] = {}
    for p in sorted(dir.glob("*.yml")):
        if p.name.startswith("_") or p.name == "README.md":
            continue
        g = load_group(p)
        if g.id in groups:
            raise ValueError(f"duplicate group id {g.id!r} in {p}")
        groups[g.id] = g
    return groups


# ---------------------------------------------------------------------------
# Radio primitives
# ---------------------------------------------------------------------------

class RadioLicense(BaseModel):
    holder: str = ""
    call: str = ""
    classes: list[License] = Field(default_factory=list)


class TxPolicy(BaseModel):
    default_disabled: bool = True
    enabled_services: list[str] = Field(default_factory=list)


class Capacity(BaseModel):
    containers: int
    channels_per_container: int


class LayoutSlot(BaseModel):
    slot: int
    name: str
    groups: list[str] = Field(default_factory=list)
    pad_with: str | None = None


class Radio(BaseModel):
    id: str
    name: str
    vendor: str = ""
    model: str = ""
    serial: str = ""
    target: str
    ble_address: str = ""
    linux_bt_mac: str = ""       # BR/EDR MAC for RFCOMM on Linux; falls back
                                  # to ble_address / scan when empty
    license: RadioLicense = Field(default_factory=RadioLicense)
    tx_policy: TxPolicy = Field(default_factory=TxPolicy)
    capacity: Capacity
    layout: list[LayoutSlot]
    overrides: dict = Field(default_factory=dict)


class RadioFile(BaseModel):
    radio: Radio


def load_radio(path: Path) -> Radio:
    """Load one radio config."""
    raw = yaml.safe_load(path.read_text())
    return RadioFile.model_validate(raw).radio


def load_radios(dir: Path) -> dict[str, Radio]:
    """Load every radio YAML under `dir/` keyed by radio.id."""
    radios: dict[str, Radio] = {}
    for p in sorted(dir.glob("*.yml")):
        if p.name.startswith("_") or p.name == "README.md":
            continue
        r = load_radio(p)
        if r.id in radios:
            raise ValueError(f"duplicate radio id {r.id!r} in {p}")
        radios[r.id] = r
    return radios


# ---------------------------------------------------------------------------
# Resolved channels — what a target adapter sees
# ---------------------------------------------------------------------------

class ResolvedChannel(BaseModel):
    """A fully-materialized channel after group + tx-policy resolution.

    Target adapters consume ResolvedChannel; they never touch groups/radios directly.
    """
    group_id: str
    short_name: str
    name: str
    rx_freq_mhz: float
    tx_freq_mhz: float
    mode: Mode
    bandwidth: Bandwidth
    rx_tone: Tone
    tx_tone: Tone
    scan: bool
    rx_only: bool
    tx_disabled: bool         # from tx_policy + group license
    mute: bool
    service: str              # first entry of group.services or "unknown"


class ResolvedContainer(BaseModel):
    slot: int
    name: str
    channels: list[ResolvedChannel]


class ResolvedLayout(BaseModel):
    radio_id: str
    containers: list[ResolvedContainer]
