"""Resolve {radio + groups} → ResolvedLayout.

The resolver is where interop guarantees are locked in. Once a channel
becomes a ResolvedChannel it should render identically on every target.
"""
from __future__ import annotations

from .models import (
    Group,
    Radio,
    ResolvedChannel,
    ResolvedContainer,
    ResolvedLayout,
)


def _resolve_channel_entry(entry, group: Group, radio: Radio) -> ResolvedChannel:
    """Turn a ChannelRef inside a group into a ResolvedChannel."""
    if entry.inline is None:
        raise NotImplementedError(
            f"ssrf_ref resolution not implemented yet ({entry.ssrf_ref}). "
            "Vendor ssrf/ and add an SSRF loader."
        )
    inl = entry.inline
    ovr = entry.overrides or {}

    # Merge overrides. Only allow the safe subset.
    def _o(field, default):
        return ovr.get(field, default)

    # TX policy: if radio TX is default-disabled, only enable when the
    # group's service is in enabled_services AND the channel is not
    # marked rx_only.
    tx_disabled = False
    if radio.tx_policy.default_disabled:
        service_ok = any(s in radio.tx_policy.enabled_services for s in group.services)
        if not service_ok:
            tx_disabled = True
    if _o("rx_only", inl.rx_only):
        tx_disabled = True

    return ResolvedChannel(
        group_id=group.id,
        short_name=_o("short_name", inl.short_name),
        name=_o("name", inl.name or inl.short_name),
        rx_freq_mhz=inl.rx_freq_mhz,
        tx_freq_mhz=inl.tx_freq_mhz,
        mode=inl.mode,
        bandwidth=inl.bandwidth,
        rx_tone=inl.rx_tone,
        tx_tone=inl.tx_tone,
        scan=_o("scan", inl.scan),
        rx_only=_o("rx_only", inl.rx_only),
        tx_disabled=tx_disabled,
        mute=_o("mute", inl.mute),
        service=(group.services[0] if group.services else "unknown"),
    )


def resolve_layout(radio: Radio, groups: dict[str, Group]) -> ResolvedLayout:
    """Materialize a radio's layout using the loaded group catalog."""
    containers: list[ResolvedContainer] = []
    for slot_spec in radio.layout:
        channels: list[ResolvedChannel] = []
        for gid in slot_spec.groups:
            if gid not in groups:
                raise KeyError(
                    f"radio {radio.id!r} slot {slot_spec.slot} references "
                    f"unknown group {gid!r}"
                )
            g = groups[gid]
            for entry in g.channels:
                channels.append(_resolve_channel_entry(entry, g, radio))

        if len(channels) > radio.capacity.channels_per_container:
            raise ValueError(
                f"radio {radio.id!r} slot {slot_spec.slot} ({slot_spec.name!r}) "
                f"has {len(channels)} channels but the container cap is "
                f"{radio.capacity.channels_per_container}. Prune, split, or bump "
                "the cap."
            )

        containers.append(ResolvedContainer(
            slot=slot_spec.slot,
            name=slot_spec.name,
            channels=channels,
        ))

    if len(containers) > radio.capacity.containers:
        raise ValueError(
            f"radio {radio.id!r} declares {len(containers)} containers but "
            f"the capacity is {radio.capacity.containers}."
        )

    return ResolvedLayout(radio_id=radio.id, containers=containers)
