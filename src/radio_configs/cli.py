"""Top-level CLI: `radio-configs build --radio <id>` etc."""
from __future__ import annotations

import json
from pathlib import Path

import click

from .models import load_groups, load_radios
from .resolver import resolve_layout


ROOT = Path(__file__).resolve().parents[2]


@click.group()
def main() -> None:
    """radio_configs — multi-radio codeplug pipeline."""


@main.command("list-radios")
def list_radios() -> None:
    """List all radios in `radios/`."""
    radios = load_radios(ROOT / "radios")
    for r in radios.values():
        click.echo(f"  {r.id:<20} target={r.target:<10} {r.name}")


@main.command("list-groups")
def list_groups() -> None:
    """List all groups in `groups/`."""
    groups = load_groups(ROOT / "groups")
    for g in sorted(groups.values(), key=lambda x: -x.priority):
        click.echo(f"  {g.id:<24} pri={g.priority:<3} svcs={','.join(g.services):<20} {g.name}")


@main.command("resolve")
@click.option("--radio", "radio_id", required=True, help="radio id (see list-radios)")
def resolve(radio_id: str) -> None:
    """Print the resolved layout for a radio as JSON."""
    groups = load_groups(ROOT / "groups")
    radios = load_radios(ROOT / "radios")
    if radio_id not in radios:
        raise click.ClickException(f"unknown radio {radio_id!r}")
    layout = resolve_layout(radios[radio_id], groups)
    click.echo(layout.model_dump_json(indent=2))


@main.command("plan")
@click.option("--radio", "radio_id", required=True)
def plan(radio_id: str) -> None:
    """Print a human-readable write plan for a radio."""
    groups = load_groups(ROOT / "groups")
    radios = load_radios(ROOT / "radios")
    if radio_id not in radios:
        raise click.ClickException(f"unknown radio {radio_id!r}")
    radio = radios[radio_id]
    layout = resolve_layout(radio, groups)

    click.echo(f"# {radio.name} ({radio.id}) — write plan\n")
    for c in layout.containers:
        click.echo(f"## Container {c.slot}: {c.name!r} — {len(c.channels)} channels")
        for i, ch in enumerate(c.channels, start=1):
            tone = "-"
            if isinstance(ch.rx_tone, (int, float)):
                tone = f"PL{ch.rx_tone}"
            elif ch.rx_tone is not None:
                tone = f"DCS{ch.rx_tone.dcs}"
            tx = "TX" if not ch.tx_disabled else "rx"
            click.echo(
                f"  {i:>2}. {ch.short_name:<8} {ch.rx_freq_mhz:>8.4f}/"
                f"{ch.tx_freq_mhz:<8.4f} {ch.bandwidth:<6} {tone:<8} "
                f"[{ch.service}] {tx}{' scan' if ch.scan else ''}"
            )
        # blanks
        radio_cap = radio.capacity.channels_per_container
        if len(c.channels) < radio_cap:
            click.echo(f"  slots {len(c.channels)+1}..{radio_cap}: BLANK")
        click.echo()


if __name__ == "__main__":
    main()
