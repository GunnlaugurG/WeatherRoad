"""Route planning engine that combines weather data with route information.

Analyzes weather conditions along route segments and provides safety
assessments and driving recommendations for Iceland travel.
"""

from dataclasses import dataclass, field
from enum import Enum

from .routes import RouteSegment, get_all_station_ids, get_route_segments, get_segment
from .weather import StationForecast, WeatherObservation, fetch_road_conditions, fetch_weather


class SafetyLevel(Enum):
    """Overall safety classification for a route segment."""

    SAFE = "safe"
    CAUTION = "caution"
    HAZARDOUS = "hazardous"
    DANGEROUS = "dangerous"


@dataclass
class SegmentAssessment:
    """Weather and safety assessment for a single route segment."""

    segment: RouteSegment
    safety_level: SafetyLevel
    weather_data: list[WeatherObservation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    road_condition: str = ""
    estimated_extra_time_minutes: int = 0


@dataclass
class RouteAssessment:
    """Complete assessment for a multi-segment route."""

    route_name: str
    segments: list[SegmentAssessment]
    overall_safety: SafetyLevel
    total_distance_km: float
    total_warnings: list[str] = field(default_factory=list)

    @property
    def total_extra_time_minutes(self) -> int:
        return sum(s.estimated_extra_time_minutes for s in self.segments)


def _assess_observation(obs: WeatherObservation) -> tuple[SafetyLevel, list[str], list[str]]:
    """Assess a single weather observation for driving safety."""
    warnings = []
    recommendations = []
    worst_level = SafetyLevel.SAFE

    # Wind assessment
    if obs.wind_speed is not None:
        if obs.wind_speed >= 25:
            worst_level = SafetyLevel.DANGEROUS
            warnings.append(
                f"Extreme wind: {obs.wind_speed} m/s at {obs.station_name}. "
                "High risk of vehicle being blown off road."
            )
            recommendations.append("Do NOT drive. Wait for conditions to improve.")
        elif obs.wind_speed >= 18:
            worst_level = max(worst_level, SafetyLevel.HAZARDOUS, key=lambda x: list(SafetyLevel).index(x))
            warnings.append(f"Very strong wind: {obs.wind_speed} m/s at {obs.station_name}")
            recommendations.append(
                "Only drive if necessary. Use extreme caution, especially on exposed roads."
            )
        elif obs.wind_speed >= 12:
            worst_level = max(worst_level, SafetyLevel.CAUTION, key=lambda x: list(SafetyLevel).index(x))
            warnings.append(f"Strong wind: {obs.wind_speed} m/s at {obs.station_name}")
            recommendations.append("Reduce speed and maintain firm grip on steering wheel.")

    # Wind gust assessment
    if obs.wind_gust is not None and obs.wind_gust >= 25:
        if worst_level.value in ("safe", "caution"):
            worst_level = SafetyLevel.HAZARDOUS
        warnings.append(f"Dangerous wind gusts: {obs.wind_gust} m/s at {obs.station_name}")

    # Visibility assessment
    if obs.visibility is not None:
        if obs.visibility < 500:
            worst_level = max(worst_level, SafetyLevel.DANGEROUS, key=lambda x: list(SafetyLevel).index(x))
            warnings.append(f"Near-zero visibility: {obs.visibility}m at {obs.station_name}")
            recommendations.append("Do NOT drive. Visibility dangerously low.")
        elif obs.visibility < 2000:
            worst_level = max(worst_level, SafetyLevel.HAZARDOUS, key=lambda x: list(SafetyLevel).index(x))
            warnings.append(f"Poor visibility: {obs.visibility}m at {obs.station_name}")
            recommendations.append("Use fog lights. Drive very slowly.")
        elif obs.visibility < 5000:
            worst_level = max(worst_level, SafetyLevel.CAUTION, key=lambda x: list(SafetyLevel).index(x))
            warnings.append(f"Reduced visibility: {obs.visibility}m at {obs.station_name}")

    # Temperature / icy road assessment
    if obs.temperature is not None and obs.temperature <= 0:
        if worst_level == SafetyLevel.SAFE:
            worst_level = SafetyLevel.CAUTION
        warnings.append(f"Freezing conditions: {obs.temperature}°C at {obs.station_name}")
        recommendations.append("Roads may be icy. Reduce speed and increase following distance.")

    if obs.road_temperature is not None and obs.road_temperature <= -2:
        worst_level = max(worst_level, SafetyLevel.HAZARDOUS, key=lambda x: list(SafetyLevel).index(x))
        warnings.append(f"Road surface freezing: {obs.road_temperature}°C at {obs.station_name}")
        recommendations.append("Black ice likely. Drive with extreme caution.")

    # Precipitation
    if obs.precipitation is not None and obs.precipitation > 5:
        if worst_level == SafetyLevel.SAFE:
            worst_level = SafetyLevel.CAUTION
        warnings.append(f"Heavy precipitation: {obs.precipitation}mm at {obs.station_name}")

    return worst_level, warnings, recommendations


def _estimate_extra_time(safety: SafetyLevel, distance_km: float) -> int:
    """Estimate additional travel time in minutes due to conditions."""
    # Assume base speed ~80 km/h on Route 1
    base_minutes = (distance_km / 80) * 60
    multipliers = {
        SafetyLevel.SAFE: 0,
        SafetyLevel.CAUTION: 0.2,
        SafetyLevel.HAZARDOUS: 0.5,
        SafetyLevel.DANGEROUS: 1.0,
    }
    return int(base_minutes * multipliers[safety])


def assess_segment(
    segment: RouteSegment,
    station_forecasts: dict[int, StationForecast],
    road_conditions: dict[str, dict],
) -> SegmentAssessment:
    """Assess a single route segment using available weather data."""
    all_warnings = []
    all_recommendations = []
    worst_safety = SafetyLevel.SAFE
    weather_data = []

    for station_id in segment.weather_station_ids:
        sf = station_forecasts.get(station_id)
        if not sf or not sf.forecasts:
            continue
        # Use the first (most recent/nearest) forecast
        obs = sf.forecasts[0]
        weather_data.append(obs)

        level, warnings, recs = _assess_observation(obs)
        all_warnings.extend(warnings)
        all_recommendations.extend(recs)
        if list(SafetyLevel).index(level) > list(SafetyLevel).index(worst_safety):
            worst_safety = level

    # Check road conditions
    road_cond = ""
    for name, cond in road_conditions.items():
        if segment.from_town.lower() in name.lower() or segment.to_town.lower() in name.lower():
            road_cond = cond.get("condition", "")
            desc = cond.get("description", "")
            if desc:
                all_warnings.append(f"Road condition ({name}): {desc}")
            break

    # Deduplicate recommendations
    seen = set()
    unique_recs = []
    for r in all_recommendations:
        if r not in seen:
            seen.add(r)
            unique_recs.append(r)

    return SegmentAssessment(
        segment=segment,
        safety_level=worst_safety,
        weather_data=weather_data,
        warnings=all_warnings,
        recommendations=unique_recs,
        road_condition=road_cond,
        estimated_extra_time_minutes=_estimate_extra_time(worst_safety, segment.distance_km),
    )


def plan_route(
    route_name: str | None = None,
    segment_ids: list[str] | None = None,
) -> RouteAssessment:
    """Plan a route and assess weather conditions along it.

    Args:
        route_name: Name of a predefined route (e.g., "ring-road").
        segment_ids: List of segment IDs for a custom route.

    Returns:
        RouteAssessment with safety levels and recommendations.
    """
    if route_name:
        segments = get_route_segments(route_name)
        display_name = route_name
    elif segment_ids:
        segments = [get_segment(sid) for sid in segment_ids]
        segments = [s for s in segments if s is not None]
        display_name = " -> ".join(s.name for s in segments)
    else:
        raise ValueError("Provide either route_name or segment_ids")

    if not segments:
        raise ValueError(f"No segments found for route: {route_name or segment_ids}")

    # Fetch weather for all stations along the route
    station_ids = get_all_station_ids(segments)
    forecasts_list = fetch_weather(station_ids, data_type="forec")
    station_forecasts = {sf.station_id: sf for sf in forecasts_list}

    # Fetch road conditions
    road_conditions = fetch_road_conditions()

    # Assess each segment
    assessments = []
    for segment in segments:
        assessment = assess_segment(segment, station_forecasts, road_conditions)
        assessments.append(assessment)

    # Overall safety is the worst of any segment
    overall = SafetyLevel.SAFE
    total_warnings = []
    for a in assessments:
        if list(SafetyLevel).index(a.safety_level) > list(SafetyLevel).index(overall):
            overall = a.safety_level
        total_warnings.extend(a.warnings)

    total_distance = sum(s.distance_km for s in segments)

    return RouteAssessment(
        route_name=display_name,
        segments=assessments,
        overall_safety=overall,
        total_distance_km=total_distance,
        total_warnings=total_warnings,
    )
