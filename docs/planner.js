/**
 * Route planning engine - assesses weather conditions for driving safety.
 */

const SAFETY = { SAFE: "safe", CAUTION: "caution", HAZARDOUS: "hazardous", DANGEROUS: "dangerous" };
const SAFETY_ORDER = [SAFETY.SAFE, SAFETY.CAUTION, SAFETY.HAZARDOUS, SAFETY.DANGEROUS];

function worstOf(a, b) {
  return SAFETY_ORDER.indexOf(a) >= SAFETY_ORDER.indexOf(b) ? a : b;
}

function assessObservation(obs) {
  let level = SAFETY.SAFE;
  const warnings = [];
  const recs = [];

  if (obs.wind_speed !== null) {
    if (obs.wind_speed >= 25) {
      level = SAFETY.DANGEROUS;
      warnings.push(`Extreme wind: ${obs.wind_speed} m/s at ${obs.station_name}. High risk of vehicle being blown off road.`);
      recs.push("Do NOT drive. Wait for conditions to improve.");
    } else if (obs.wind_speed >= 18) {
      level = worstOf(level, SAFETY.HAZARDOUS);
      warnings.push(`Very strong wind: ${obs.wind_speed} m/s at ${obs.station_name}`);
      recs.push("Only drive if necessary. Use extreme caution, especially on exposed roads.");
    } else if (obs.wind_speed >= 12) {
      level = worstOf(level, SAFETY.CAUTION);
      warnings.push(`Strong wind: ${obs.wind_speed} m/s at ${obs.station_name}`);
      recs.push("Reduce speed and maintain firm grip on steering wheel.");
    }
  }

  if (obs.wind_gust !== null && obs.wind_gust >= 25) {
    level = worstOf(level, SAFETY.HAZARDOUS);
    warnings.push(`Dangerous wind gusts: ${obs.wind_gust} m/s at ${obs.station_name}`);
  }

  if (obs.visibility !== null) {
    if (obs.visibility < 500) {
      level = worstOf(level, SAFETY.DANGEROUS);
      warnings.push(`Near-zero visibility: ${obs.visibility}m at ${obs.station_name}`);
      recs.push("Do NOT drive. Visibility dangerously low.");
    } else if (obs.visibility < 2000) {
      level = worstOf(level, SAFETY.HAZARDOUS);
      warnings.push(`Poor visibility: ${obs.visibility}m at ${obs.station_name}`);
      recs.push("Use fog lights. Drive very slowly.");
    } else if (obs.visibility < 5000) {
      level = worstOf(level, SAFETY.CAUTION);
      warnings.push(`Reduced visibility: ${obs.visibility}m at ${obs.station_name}`);
    }
  }

  if (obs.temperature !== null && obs.temperature <= 0) {
    level = worstOf(level, SAFETY.CAUTION);
    warnings.push(`Freezing conditions: ${obs.temperature}\u00B0C at ${obs.station_name}`);
    recs.push("Roads may be icy. Reduce speed and increase following distance.");
  }

  if (obs.road_temperature !== null && obs.road_temperature <= -2) {
    level = worstOf(level, SAFETY.HAZARDOUS);
    warnings.push(`Road surface freezing: ${obs.road_temperature}\u00B0C at ${obs.station_name}`);
    recs.push("Black ice likely. Drive with extreme caution.");
  }

  if (obs.precipitation !== null && obs.precipitation > 5) {
    level = worstOf(level, SAFETY.CAUTION);
    warnings.push(`Heavy precipitation: ${obs.precipitation}mm at ${obs.station_name}`);
  }

  return { level, warnings, recs };
}

function estimateExtraTime(safety, km) {
  const baseMin = (km / 80) * 60;
  const mult = { safe: 0, caution: 0.2, hazardous: 0.5, dangerous: 1.0 };
  return Math.round(baseMin * (mult[safety] || 0));
}

function assessSegment(segment, stationForecasts, roadConditions) {
  let worst = SAFETY.SAFE;
  const allWarnings = [];
  const allRecs = [];
  const weatherData = [];

  for (const sid of segment.stations) {
    const sf = stationForecasts[sid];
    if (!sf || !sf.forecasts.length) continue;
    const obs = sf.forecasts[0];
    weatherData.push(obs);

    const { level, warnings, recs } = assessObservation(obs);
    worst = worstOf(worst, level);
    allWarnings.push(...warnings);
    allRecs.push(...recs);
  }

  let roadCond = "";
  for (const [name, cond] of Object.entries(roadConditions)) {
    if (name.toLowerCase().includes(segment.from.toLowerCase()) ||
        name.toLowerCase().includes(segment.to.toLowerCase())) {
      roadCond = cond.condition || "";
      if (cond.description) allWarnings.push(`Road condition (${name}): ${cond.description}`);
      break;
    }
  }

  const uniqueRecs = [...new Set(allRecs)];

  return {
    segment,
    safety_level: worst,
    weather: weatherData,
    warnings: allWarnings,
    recommendations: uniqueRecs,
    road_condition: roadCond,
    extra_time_minutes: estimateExtraTime(worst, segment.km),
  };
}

async function planRoute(routeName, segmentIds) {
  let segments;
  let displayName;

  if (routeName) {
    segments = getRouteSegments(routeName);
    displayName = NAMED_ROUTES[routeName]?.name || routeName;
  } else {
    segments = segmentIds.map(getSegment).filter(Boolean);
    displayName = segments.map(s => s.name).join(" \u2192 ");
  }

  if (!segments.length) throw new Error("No segments found");

  const stationIds = getAllStationIds(segments);
  const [forecasts, roadConditions] = await Promise.all([
    fetchWeather(stationIds),
    fetchRoadConditions(),
  ]);

  const assessments = segments.map(seg => assessSegment(seg, forecasts, roadConditions));

  let overall = SAFETY.SAFE;
  const totalWarnings = [];
  for (const a of assessments) {
    overall = worstOf(overall, a.safety_level);
    totalWarnings.push(...a.warnings);
  }

  const totalKm = segments.reduce((sum, s) => sum + s.km, 0);
  const totalExtra = assessments.reduce((sum, a) => sum + a.extra_time_minutes, 0);

  return {
    route_name: displayName,
    overall_safety: overall,
    total_distance_km: totalKm,
    total_extra_time_minutes: totalExtra,
    total_warnings: totalWarnings,
    segments: assessments,
  };
}
