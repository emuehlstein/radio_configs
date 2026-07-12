"""Map ResolvedLayout → N76 benlink Channel objects.

Kept independent of `bleak`/`benlink` so `dry-run` can import this
without needing BLE libs on the machine.
"""
from __future__ import annotations

from dataclasses import dataclass

from radio_configs.models import ResolvedChannel, ResolvedLayout


@dataclass
class N76ChannelPlan:
    """One slot's worth of channel data, in a benlink-ready shape but plain-Python."""
    region_id: int          # 0-based
    channel_id: int         # 0-based, 0..31
    name: str
    rx_freq: float
    tx_freq: float
    bandwidth: str          # "WIDE" | "NARROW"
    rx_sub_audio: object    # None | float PL | ("D", dcs_int)
    tx_sub_audio: object
    scan: bool
    tx_disable: bool
    mute: bool


@dataclass
class N76RegionPlan:
    region_id: int
    name: str
    channels: list[N76ChannelPlan]      # filled slots (0..31)
    blank_slots: list[int]              # slot ids (0..31) to explicitly blank


@dataclass
class N76WritePlan:
    radio_id: str
    region_renames: dict[int, str]      # region_id → new name
    regions: list[N76RegionPlan]


# Names are truncated to N76's practical limits.
_N76_REGION_NAME_MAX = 10
_N76_CHANNEL_NAME_MAX = 10


def _bw(bw: str) -> str:
    return "WIDE" if bw == "wide" else "NARROW"


def _tone(t) -> object:
    """radio_configs Tone → benlink sub_audio field shape."""
    if t is None:
        return None
    if isinstance(t, (int, float)):
        return float(t)
    # DCS pydantic model
    if hasattr(t, "dcs"):
        return ("D", int(t.dcs))
    return None


def _trunc(s: str, n: int) -> str:
    return (s or "")[:n]


def build_plan(layout: ResolvedLayout, channels_per_region: int = 32) -> N76WritePlan:
    """Turn a ResolvedLayout into an N76 write plan.

    Channel slots are populated 0..(len-1), remaining slots up to
    channels_per_region-1 are added to blank_slots for explicit clearing.
    Region names shorter than N76's limits are used as-is.
    """
    region_renames: dict[int, str] = {}
    regions: list[N76RegionPlan] = []

    for container in layout.containers:
        rid = container.slot
        region_renames[rid] = _trunc(container.name, _N76_REGION_NAME_MAX)

        chan_plans: list[N76ChannelPlan] = []
        for i, ch in enumerate(container.channels):
            chan_plans.append(_channel_plan(rid, i, ch))

        blanks = list(range(len(chan_plans), channels_per_region))

        regions.append(N76RegionPlan(
            region_id=rid,
            name=_trunc(container.name, _N76_REGION_NAME_MAX),
            channels=chan_plans,
            blank_slots=blanks,
        ))

    return N76WritePlan(
        radio_id=layout.radio_id,
        region_renames=region_renames,
        regions=regions,
    )


def _channel_plan(region_id: int, slot_idx0: int, ch: ResolvedChannel) -> N76ChannelPlan:
    display_name = ch.name if ch.name and len(ch.name) <= _N76_CHANNEL_NAME_MAX else ch.short_name
    return N76ChannelPlan(
        region_id=region_id,
        channel_id=slot_idx0,
        name=_trunc(display_name, _N76_CHANNEL_NAME_MAX),
        rx_freq=float(ch.rx_freq_mhz),
        tx_freq=float(ch.tx_freq_mhz),
        bandwidth=_bw(ch.bandwidth),
        rx_sub_audio=_tone(ch.rx_tone),
        tx_sub_audio=_tone(ch.tx_tone),
        scan=bool(ch.scan),
        tx_disable=bool(ch.tx_disabled),
        mute=bool(ch.mute),
    )


def format_plan(plan: N76WritePlan) -> str:
    """Human-readable plan for --dry-run."""
    lines = [f"# N76 write plan for {plan.radio_id}\n"]
    lines.append("## Region renames")
    for rid, name in plan.region_renames.items():
        lines.append(f"  region {rid} → {name!r}")
    lines.append("")

    total_writes = 0
    for r in plan.regions:
        lines.append(f"## Region {r.region_id} ({r.name!r}) — "
                     f"{len(r.channels)} channels + {len(r.blank_slots)} blanks")
        for c in r.channels:
            tone = "-"
            if isinstance(c.rx_sub_audio, tuple):
                tone = f"DCS{c.rx_sub_audio[1]}"
            elif isinstance(c.rx_sub_audio, (int, float)):
                tone = f"PL{c.rx_sub_audio}"
            tx = "TX" if not c.tx_disable else "rx"
            lines.append(
                f"  slot {c.channel_id+1:>2}: {c.name:<10} "
                f"rx={c.rx_freq:>8.4f} tx={c.tx_freq:<8.4f} "
                f"{c.bandwidth:<6} {tone:<7} "
                f"{tx}{' scan' if c.scan else '':<5}"
                f"{' mute' if c.mute else ''}"
            )
            total_writes += 1
        if r.blank_slots:
            lines.append(f"  slots {r.blank_slots[0]+1}..{r.blank_slots[-1]+1}: BLANK")
            total_writes += len(r.blank_slots)
        lines.append("")

    total_writes += len(plan.region_renames)
    lines.append(f"TOTAL WRITES: {total_writes}")
    return "\n".join(lines)
