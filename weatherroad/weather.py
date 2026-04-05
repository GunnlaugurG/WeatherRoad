"""Fetch weather data from the Icelandic Meteorological Office (Vedur.is).

Uses the public XML API to get forecasts and observations for weather stations.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime

import requests

VEDUR_API_BASE = "https://xmlweather.vedur.is"
REQUEST_TIMEOUT = 15


@dataclass
class WeatherObservation:
    """A single weather observation or forecast point."""

    station_id: int
    station_name: str
    time: str
    temperature: float | None = None
    wind_speed: float | None = None
    wind_gust: float | None = None
    wind_direction: str = ""
    weather_description: str = ""
    visibility: float | None = None
    precipitation: float | None = None
    cloud_cover: str = ""
    road_temperature: float | None = None

    @property
    def wind_severity(self) -> str:
        """Classify wind conditions for driving safety."""
        if self.wind_speed is None:
            return "unknown"
        if self.wind_speed >= 25:
            return "dangerous"
        if self.wind_speed >= 18:
            return "severe"
        if self.wind_speed >= 12:
            return "strong"
        if self.wind_speed >= 8:
            return "moderate"
        return "calm"

    @property
    def visibility_rating(self) -> str:
        """Classify visibility for driving safety."""
        if self.visibility is None:
            return "unknown"
        if self.visibility < 500:
            return "very_poor"
        if self.visibility < 2000:
            return "poor"
        if self.visibility < 5000:
            return "moderate"
        return "good"


@dataclass
class StationForecast:
    """Weather forecast for a station with multiple time points."""

    station_id: int
    station_name: str
    forecasts: list[WeatherObservation] = field(default_factory=list)


def _parse_float(text: str | None) -> float | None:
    """Safely parse a float from XML text."""
    if text is None or text.strip() == "":
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def _parse_station(station_elem: ET.Element, data_type: str) -> StationForecast:
    """Parse a single station element from the Vedur.is XML response."""
    station_id = int(station_elem.get("id", "0"))
    station_name = station_elem.get("name", "Unknown")

    forecast = StationForecast(
        station_id=station_id,
        station_name=station_name,
    )

    tag = "forecast" if data_type == "forec" else "observation"

    for entry in station_elem.findall(tag):
        obs = WeatherObservation(
            station_id=station_id,
            station_name=station_name,
            time=entry.findtext("ftime", "") or entry.findtext("time", ""),
            temperature=_parse_float(entry.findtext("T")),
            wind_speed=_parse_float(entry.findtext("F")),
            wind_gust=_parse_float(entry.findtext("FX")),
            wind_direction=entry.findtext("D", ""),
            weather_description=entry.findtext("W", ""),
            visibility=_parse_float(entry.findtext("V")),
            precipitation=_parse_float(entry.findtext("R")),
            cloud_cover=entry.findtext("N", ""),
            road_temperature=_parse_float(entry.findtext("RTE")),
        )
        forecast.forecasts.append(obs)

    return forecast


def fetch_weather(
    station_ids: list[int],
    data_type: str = "forec",
    lang: str = "en",
) -> list[StationForecast]:
    """Fetch weather data from Vedur.is for the given station IDs.

    Args:
        station_ids: List of Vedur.is weather station IDs.
        data_type: "forec" for forecast, "obs" for observations.
        lang: Language code ("en" or "is").

    Returns:
        List of StationForecast objects.
    """
    ids_str = ";".join(str(s) for s in station_ids)
    params = "T;F;FX;D;W;V;N;R;RTE"

    url = (
        f"{VEDUR_API_BASE}/"
        f"?op_w=xml&type={data_type}&lang={lang}"
        f"&view=xml&ids={ids_str}&params={params}"
    )

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    results = []

    for station_elem in root.findall(".//station"):
        results.append(_parse_station(station_elem, data_type))

    return results


def fetch_road_conditions() -> dict[str, dict]:
    """Fetch current road conditions from Vegagerdin (Icelandic Road Administration).

    Returns:
        Dictionary mapping road segment names to condition info.
    """
    url = (
        "https://gis.vegagerdin.is/arcgis/rest/services/"
        "vegagerdin/faerd_01/MapServer/0/query"
        "?where=1%3D1&outFields=*&f=json"
    )

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return {}

    conditions = {}
    for feature in data.get("features", []):
        attrs = feature.get("attributes", {})
        name = attrs.get("Nafn", attrs.get("NAME", ""))
        if name:
            conditions[name] = {
                "condition": attrs.get("Faerd", attrs.get("CONDITION", "Unknown")),
                "description": attrs.get("Lysing", attrs.get("DESCRIPTION", "")),
                "last_updated": attrs.get("Pimedags", ""),
            }

    return conditions
