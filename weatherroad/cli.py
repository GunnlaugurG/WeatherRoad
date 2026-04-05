"""Command-line interface for the Iceland Weather Route Planner."""

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .planner import RouteAssessment, SafetyLevel, SegmentAssessment, plan_route
from .routes import ALL_SEGMENTS, NAMED_ROUTES

console = Console()

SAFETY_COLORS = {
    SafetyLevel.SAFE: "green",
    SafetyLevel.CAUTION: "yellow",
    SafetyLevel.HAZARDOUS: "red",
    SafetyLevel.DANGEROUS: "bold red",
}

SAFETY_ICONS = {
    SafetyLevel.SAFE: "[green]OK[/green]",
    SafetyLevel.CAUTION: "[yellow]CAUTION[/yellow]",
    SafetyLevel.HAZARDOUS: "[red]HAZARDOUS[/red]",
    SafetyLevel.DANGEROUS: "[bold red]DANGEROUS[/bold red]",
}


def _print_segment(seg: SegmentAssessment) -> None:
    """Print details for a single segment assessment."""
    icon = SAFETY_ICONS[seg.safety_level]
    color = SAFETY_COLORS[seg.safety_level]

    console.print(
        f"\n  [{color}]{seg.segment.name}[/{color}] "
        f"({seg.segment.distance_km} km, Route {seg.segment.route_number}) - {icon}"
    )
    console.print(f"    {seg.segment.description}", style="dim")

    if seg.weather_data:
        for obs in seg.weather_data:
            parts = [f"[bold]{obs.station_name}[/bold]:"]
            if obs.temperature is not None:
                parts.append(f"{obs.temperature}°C")
            if obs.wind_speed is not None:
                parts.append(f"wind {obs.wind_speed} m/s")
            if obs.wind_gust is not None:
                parts.append(f"(gusts {obs.wind_gust} m/s)")
            if obs.wind_direction:
                parts.append(f"from {obs.wind_direction}")
            if obs.weather_description:
                parts.append(f"- {obs.weather_description}")
            if obs.visibility is not None:
                parts.append(f"| vis: {obs.visibility}m")
            console.print("    " + " ".join(parts))

    if seg.road_condition:
        console.print(f"    Road: {seg.road_condition}", style="dim")

    for w in seg.warnings:
        console.print(f"    [yellow]! {w}[/yellow]")

    for r in seg.recommendations:
        console.print(f"    [cyan]> {r}[/cyan]")

    if seg.estimated_extra_time_minutes > 0:
        console.print(
            f"    [dim]Estimated delay: +{seg.estimated_extra_time_minutes} min[/dim]"
        )


def _print_route_assessment(assessment: RouteAssessment) -> None:
    """Print a full route assessment."""
    overall_icon = SAFETY_ICONS[assessment.overall_safety]
    overall_color = SAFETY_COLORS[assessment.overall_safety]

    console.print()
    console.print(
        Panel(
            f"[bold]{assessment.route_name}[/bold]\n"
            f"Total distance: {assessment.total_distance_km} km\n"
            f"Overall: {overall_icon}\n"
            f"Estimated extra time: +{assessment.total_extra_time_minutes} min",
            title="[bold]WeatherRoad - Iceland Route Planner[/bold]",
            border_style=overall_color,
        )
    )

    for seg in assessment.segments:
        _print_segment(seg)

    console.print()

    if assessment.overall_safety == SafetyLevel.DANGEROUS:
        console.print(
            Panel(
                "[bold red]TRAVEL NOT RECOMMENDED[/bold red]\n"
                "Conditions along this route are dangerous. "
                "Postpone your trip or choose an alternative route.\n"
                "Check road.is and safetravel.is for updates.",
                border_style="red",
            )
        )
    elif assessment.overall_safety == SafetyLevel.HAZARDOUS:
        console.print(
            Panel(
                "[bold yellow]TRAVEL WITH EXTREME CAUTION[/bold yellow]\n"
                "Hazardous conditions on parts of this route. "
                "Only travel if necessary and well-prepared.\n"
                "Check road.is and safetravel.is for updates.",
                border_style="yellow",
            )
        )


def cmd_plan(args: argparse.Namespace) -> None:
    """Handle the 'plan' subcommand."""
    try:
        if args.route:
            assessment = plan_route(route_name=args.route)
        elif args.segments:
            assessment = plan_route(segment_ids=args.segments)
        else:
            console.print("[red]Specify --route or --segments[/red]")
            sys.exit(1)

        _print_route_assessment(assessment)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def cmd_routes(args: argparse.Namespace) -> None:
    """Handle the 'routes' subcommand - list available routes."""
    table = Table(title="Available Routes")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Segments", justify="right")

    for key, route in NAMED_ROUTES.items():
        table.add_row(key, route["description"], str(len(route["segments"])))

    console.print(table)


def cmd_segments(args: argparse.Namespace) -> None:
    """Handle the 'segments' subcommand - list all route segments."""
    table = Table(title="Route Segments")
    table.add_column("ID", style="cyan")
    table.add_column("From")
    table.add_column("To")
    table.add_column("Distance", justify="right")
    table.add_column("Route #", justify="right")

    for seg in ALL_SEGMENTS:
        table.add_row(
            seg.id,
            seg.from_town,
            seg.to_town,
            f"{seg.distance_km} km",
            str(seg.route_number),
        )

    console.print(table)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="weatherroad",
        description="Iceland Weather Route Planner - Plan safe driving routes around Iceland",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Plan a route and check conditions")
    plan_parser.add_argument(
        "--route", "-r",
        help="Name of a predefined route (use 'routes' command to list)",
    )
    plan_parser.add_argument(
        "--segments", "-s",
        nargs="+",
        help="List of segment IDs for a custom route",
    )
    plan_parser.set_defaults(func=cmd_plan)

    # Routes command
    routes_parser = subparsers.add_parser("routes", help="List available predefined routes")
    routes_parser.set_defaults(func=cmd_routes)

    # Segments command
    segments_parser = subparsers.add_parser("segments", help="List all route segments")
    segments_parser.set_defaults(func=cmd_segments)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
