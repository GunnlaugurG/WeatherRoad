"""Iceland route definitions with associated weather stations.

Defines segments of Iceland's Ring Road (Route 1) and other key routes,
mapping each segment to nearby Vedur.is weather stations for forecasts.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteSegment:
    """A segment of a driving route in Iceland."""

    id: str
    name: str
    from_town: str
    to_town: str
    distance_km: float
    route_number: int
    weather_station_ids: list[int]
    description: str


# Vedur.is weather station IDs for key locations around Iceland
STATIONS = {
    "reykjavik": 1,
    "keflavik": 990,
    "borgarnes": 1473,
    "blonduos": 2642,
    "akureyri": 422,
    "husavik": 2963,
    "egilsstadir": 571,
    "hofn": 705,
    "vik": 798,
    "selfoss": 1395,
    "isafjordur": 2315,
    "stykkisholmur": 1856,
    "vestmannaeyjar": 907,
    "kirkjubaejarklaustur": 749,
    "hella": 1175,
    "dalvik": 2430,
    "saudarkrokur": 2613,
}

# Ring Road (Route 1) segments going clockwise from Reykjavik
RING_ROAD_SEGMENTS = [
    RouteSegment(
        id="ring-1",
        name="Reykjavik to Borgarnes",
        from_town="Reykjavik",
        to_town="Borgarnes",
        distance_km=74,
        route_number=1,
        weather_station_ids=[1, 1473],
        description="Hvalfjordur tunnel route through West Iceland",
    ),
    RouteSegment(
        id="ring-2",
        name="Borgarnes to Blonduos",
        from_town="Borgarnes",
        to_town="Blonduos",
        distance_km=200,
        route_number=1,
        weather_station_ids=[1473, 2642],
        description="Through Hrutafjordur along the north coast",
    ),
    RouteSegment(
        id="ring-3",
        name="Blonduos to Akureyri",
        from_town="Blonduos",
        to_town="Akureyri",
        distance_km=145,
        route_number=1,
        weather_station_ids=[2642, 2613, 422],
        description="Along Skagafjordur to the capital of the north",
    ),
    RouteSegment(
        id="ring-4",
        name="Akureyri to Husavik",
        from_town="Akureyri",
        to_town="Husavik",
        distance_km=91,
        route_number=1,
        weather_station_ids=[422, 2963],
        description="Northeast Iceland, near whale watching capital",
    ),
    RouteSegment(
        id="ring-5",
        name="Husavik to Egilsstadir",
        from_town="Husavik",
        to_town="Egilsstadir",
        distance_km=206,
        route_number=1,
        weather_station_ids=[2963, 571],
        description="Through the remote northeast highlands",
    ),
    RouteSegment(
        id="ring-6",
        name="Egilsstadir to Hofn",
        from_town="Egilsstadir",
        to_town="Hofn",
        distance_km=244,
        route_number=1,
        weather_station_ids=[571, 705],
        description="East fjords coastal route with stunning views",
    ),
    RouteSegment(
        id="ring-7",
        name="Hofn to Vik",
        from_town="Hofn",
        to_town="Vik",
        distance_km=272,
        route_number=1,
        weather_station_ids=[705, 749, 798],
        description="Past Vatnajokull glacier and black sand beaches",
    ),
    RouteSegment(
        id="ring-8",
        name="Vik to Selfoss",
        from_town="Vik",
        to_town="Selfoss",
        distance_km=148,
        route_number=1,
        weather_station_ids=[798, 1175, 1395],
        description="South coast through Hella to the Golden Circle area",
    ),
    RouteSegment(
        id="ring-9",
        name="Selfoss to Reykjavik",
        from_town="Selfoss",
        to_town="Reykjavik",
        distance_km=57,
        route_number=1,
        weather_station_ids=[1395, 1],
        description="Quick drive back to the capital",
    ),
]

# Additional popular routes
EXTRA_ROUTES = [
    RouteSegment(
        id="kef-rvk",
        name="Keflavik Airport to Reykjavik",
        from_town="Keflavik",
        to_town="Reykjavik",
        distance_km=50,
        route_number=41,
        weather_station_ids=[990, 1],
        description="Airport transfer route via Reykjanesbraut",
    ),
    RouteSegment(
        id="west-1",
        name="Borgarnes to Stykkisholmur",
        from_town="Borgarnes",
        to_town="Stykkisholmur",
        distance_km=100,
        route_number=54,
        weather_station_ids=[1473, 1856],
        description="Snaefellsnes peninsula route",
    ),
    RouteSegment(
        id="west-2",
        name="Isafjordur Route",
        from_town="Borgarnes",
        to_town="Isafjordur",
        distance_km=380,
        route_number=61,
        weather_station_ids=[1473, 2315],
        description="Remote Westfjords route (check conditions carefully)",
    ),
]

ALL_SEGMENTS = RING_ROAD_SEGMENTS + EXTRA_ROUTES

# Named multi-segment routes
NAMED_ROUTES = {
    "ring-road": {
        "name": "Ring Road (Full Circle)",
        "segments": [s.id for s in RING_ROAD_SEGMENTS],
        "description": "Complete circuit of Iceland via Route 1",
    },
    "south-coast": {
        "name": "South Coast",
        "segments": ["ring-8", "ring-7"],
        "description": "Reykjavik area to Hofn via the south coast",
    },
    "north-iceland": {
        "name": "North Iceland",
        "segments": ["ring-3", "ring-4", "ring-5"],
        "description": "Blonduos to Egilsstadir through the north",
    },
    "golden-circle-area": {
        "name": "Golden Circle Area",
        "segments": ["ring-9", "ring-8"],
        "description": "Reykjavik to Selfoss to Vik area",
    },
    "airport-transfer": {
        "name": "Airport Transfer",
        "segments": ["kef-rvk"],
        "description": "Keflavik International Airport to Reykjavik",
    },
    "westfjords": {
        "name": "Westfjords",
        "segments": ["ring-1", "west-2"],
        "description": "Reykjavik to Isafjordur via Borgarnes",
    },
    "snaefellsnes": {
        "name": "Snaefellsnes Peninsula",
        "segments": ["ring-1", "west-1"],
        "description": "Reykjavik to Stykkisholmur via Borgarnes",
    },
}


def get_segment(segment_id: str) -> RouteSegment | None:
    """Look up a route segment by ID."""
    for s in ALL_SEGMENTS:
        if s.id == segment_id:
            return s
    return None


def get_route_segments(route_name: str) -> list[RouteSegment]:
    """Get all segments for a named route."""
    route = NAMED_ROUTES.get(route_name)
    if not route:
        return []
    segments = []
    for sid in route["segments"]:
        seg = get_segment(sid)
        if seg:
            segments.append(seg)
    return segments


def get_all_station_ids(segments: list[RouteSegment]) -> list[int]:
    """Collect unique weather station IDs from a list of segments."""
    seen = set()
    ids = []
    for seg in segments:
        for sid in seg.weather_station_ids:
            if sid not in seen:
                seen.add(sid)
                ids.append(sid)
    return ids
