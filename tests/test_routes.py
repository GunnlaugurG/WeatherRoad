"""Tests for route definitions and lookups."""

from weatherroad.routes import (
    ALL_SEGMENTS,
    NAMED_ROUTES,
    RING_ROAD_SEGMENTS,
    get_all_station_ids,
    get_route_segments,
    get_segment,
)


def test_ring_road_has_nine_segments():
    assert len(RING_ROAD_SEGMENTS) == 9


def test_ring_road_forms_a_loop():
    """The Ring Road should start and end at Reykjavik."""
    assert RING_ROAD_SEGMENTS[0].from_town == "Reykjavik"
    assert RING_ROAD_SEGMENTS[-1].to_town == "Reykjavik"


def test_get_segment_found():
    seg = get_segment("ring-1")
    assert seg is not None
    assert seg.from_town == "Reykjavik"
    assert seg.to_town == "Borgarnes"


def test_get_segment_not_found():
    assert get_segment("nonexistent") is None


def test_get_route_segments():
    segments = get_route_segments("ring-road")
    assert len(segments) == 9
    assert segments[0].id == "ring-1"


def test_get_route_segments_unknown():
    assert get_route_segments("unknown-route") == []


def test_all_segments_have_weather_stations():
    for seg in ALL_SEGMENTS:
        assert len(seg.weather_station_ids) > 0, f"{seg.id} has no stations"


def test_get_all_station_ids_deduplicates():
    segments = get_route_segments("ring-road")
    ids = get_all_station_ids(segments)
    assert len(ids) == len(set(ids))


def test_named_routes_reference_valid_segments():
    for route_name, route in NAMED_ROUTES.items():
        for sid in route["segments"]:
            seg = get_segment(sid)
            assert seg is not None, f"Route '{route_name}' references unknown segment '{sid}'"
