"""Tests for the route planning engine."""

from weatherroad.planner import (
    SafetyLevel,
    _assess_observation,
    _estimate_extra_time,
    assess_segment,
)
from weatherroad.routes import get_segment
from weatherroad.weather import StationForecast, WeatherObservation


def _make_obs(**kwargs) -> WeatherObservation:
    defaults = {
        "station_id": 1,
        "station_name": "Test",
        "time": "2025-01-01 12:00",
    }
    defaults.update(kwargs)
    return WeatherObservation(**defaults)


def test_calm_conditions():
    obs = _make_obs(wind_speed=5.0, visibility=10000, temperature=10.0)
    level, warnings, recs = _assess_observation(obs)
    assert level == SafetyLevel.SAFE
    assert len(warnings) == 0


def test_strong_wind_caution():
    obs = _make_obs(wind_speed=14.0, visibility=10000, temperature=10.0)
    level, warnings, recs = _assess_observation(obs)
    assert level == SafetyLevel.CAUTION
    assert any("Strong wind" in w for w in warnings)


def test_extreme_wind_dangerous():
    obs = _make_obs(wind_speed=30.0)
    level, warnings, recs = _assess_observation(obs)
    assert level == SafetyLevel.DANGEROUS
    assert any("NOT drive" in r for r in recs)


def test_poor_visibility_hazardous():
    obs = _make_obs(visibility=1500.0)
    level, warnings, recs = _assess_observation(obs)
    assert level == SafetyLevel.HAZARDOUS


def test_near_zero_visibility_dangerous():
    obs = _make_obs(visibility=200.0)
    level, warnings, recs = _assess_observation(obs)
    assert level == SafetyLevel.DANGEROUS


def test_freezing_temperature_caution():
    obs = _make_obs(temperature=-5.0)
    level, warnings, recs = _assess_observation(obs)
    assert level == SafetyLevel.CAUTION
    assert any("Freezing" in w for w in warnings)


def test_icy_road_hazardous():
    obs = _make_obs(temperature=-3.0, road_temperature=-5.0)
    level, warnings, recs = _assess_observation(obs)
    assert level == SafetyLevel.HAZARDOUS
    assert any("Black ice" in r for r in recs)


def test_estimate_extra_time_safe():
    assert _estimate_extra_time(SafetyLevel.SAFE, 100) == 0


def test_estimate_extra_time_hazardous():
    extra = _estimate_extra_time(SafetyLevel.HAZARDOUS, 100)
    assert extra > 0


def test_assess_segment_no_data():
    """Segment with no matching forecasts should default to safe."""
    segment = get_segment("ring-1")
    assessment = assess_segment(segment, {}, {})
    assert assessment.safety_level == SafetyLevel.SAFE
    assert len(assessment.weather_data) == 0


def test_assess_segment_with_data():
    segment = get_segment("ring-1")
    obs = _make_obs(station_id=1, wind_speed=20.0, temperature=-2.0)
    sf = StationForecast(station_id=1, station_name="Reykjavik", forecasts=[obs])
    assessment = assess_segment(segment, {1: sf}, {})
    assert assessment.safety_level in (SafetyLevel.HAZARDOUS, SafetyLevel.DANGEROUS)
    assert len(assessment.warnings) > 0
