"""Flask web application for the Iceland Weather Route Planner."""

from flask import Flask, jsonify, render_template, request

from .planner import SafetyLevel, plan_route
from .routes import ALL_SEGMENTS, NAMED_ROUTES

app = Flask(__name__)


@app.route("/")
def index():
    """Main page with the route planner interface."""
    return render_template(
        "index.html",
        named_routes=NAMED_ROUTES,
        segments=ALL_SEGMENTS,
    )


@app.route("/api/plan", methods=["POST"])
def api_plan():
    """API endpoint to plan a route and get weather assessment."""
    data = request.get_json()
    route_name = data.get("route")
    segment_ids = data.get("segments")

    try:
        assessment = plan_route(route_name=route_name, segment_ids=segment_ids)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    segments_data = []
    for seg in assessment.segments:
        weather_points = []
        for obs in seg.weather_data:
            weather_points.append({
                "station_name": obs.station_name,
                "temperature": obs.temperature,
                "wind_speed": obs.wind_speed,
                "wind_gust": obs.wind_gust,
                "wind_direction": obs.wind_direction,
                "weather_description": obs.weather_description,
                "visibility": obs.visibility,
                "precipitation": obs.precipitation,
                "road_temperature": obs.road_temperature,
            })

        segments_data.append({
            "id": seg.segment.id,
            "name": seg.segment.name,
            "from_town": seg.segment.from_town,
            "to_town": seg.segment.to_town,
            "distance_km": seg.segment.distance_km,
            "route_number": seg.segment.route_number,
            "description": seg.segment.description,
            "safety_level": seg.safety_level.value,
            "warnings": seg.warnings,
            "recommendations": seg.recommendations,
            "road_condition": seg.road_condition,
            "extra_time_minutes": seg.estimated_extra_time_minutes,
            "weather": weather_points,
        })

    return jsonify({
        "route_name": assessment.route_name,
        "overall_safety": assessment.overall_safety.value,
        "total_distance_km": assessment.total_distance_km,
        "total_extra_time_minutes": assessment.total_extra_time_minutes,
        "total_warnings": assessment.total_warnings,
        "segments": segments_data,
    })


@app.route("/api/routes")
def api_routes():
    """List available predefined routes."""
    return jsonify(NAMED_ROUTES)


@app.route("/api/segments")
def api_segments():
    """List all route segments."""
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "from_town": s.from_town,
            "to_town": s.to_town,
            "distance_km": s.distance_km,
            "route_number": s.route_number,
            "description": s.description,
        }
        for s in ALL_SEGMENTS
    ])


def run():
    """Run the development server."""
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    run()
