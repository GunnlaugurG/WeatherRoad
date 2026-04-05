/**
 * Fetch weather data from Vedur.is and road conditions from Vegagerdin.
 * Uses CORS proxies as fallback since these APIs don't set CORS headers.
 */

const VEDUR_API = "https://xmlweather.vedur.is";
const VEGAGERDIN_API = "https://gis.vegagerdin.is/arcgis/rest/services/vegagerdin/faerd_01/MapServer/0/query";

// Public CORS proxies to try (Vedur.is and Vegagerdin don't send CORS headers)
const CORS_PROXIES = [
  url => `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`,
  url => `https://corsproxy.io/?${encodeURIComponent(url)}`,
];

async function fetchWithCorsRetry(url) {
  // Try direct first
  try {
    const resp = await fetch(url, { signal: AbortSignal.timeout(10000) });
    if (resp.ok) return await resp.text();
  } catch (_) { /* CORS or network error, try proxies */ }

  for (const proxy of CORS_PROXIES) {
    try {
      const resp = await fetch(proxy(url), { signal: AbortSignal.timeout(15000) });
      if (resp.ok) return await resp.text();
    } catch (_) { continue; }
  }

  throw new Error(`Failed to fetch: ${url}`);
}

function parseFloat2(text) {
  if (!text || text.trim() === "") return null;
  const n = parseFloat(text.replace(",", "."));
  return isNaN(n) ? null : n;
}

function parseVedurXml(xmlText) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(xmlText, "text/xml");
  const results = {};

  for (const station of doc.querySelectorAll("station")) {
    const id = parseInt(station.getAttribute("id"), 10);
    const name = station.getAttribute("name") || "Unknown";
    const forecasts = [];

    for (const entry of station.querySelectorAll("forecast, observation")) {
      forecasts.push({
        station_id: id,
        station_name: name,
        time: (entry.querySelector("ftime") || entry.querySelector("time") || {}).textContent || "",
        temperature: parseFloat2((entry.querySelector("T") || {}).textContent),
        wind_speed: parseFloat2((entry.querySelector("F") || {}).textContent),
        wind_gust: parseFloat2((entry.querySelector("FX") || {}).textContent),
        wind_direction: (entry.querySelector("D") || {}).textContent || "",
        weather_description: (entry.querySelector("W") || {}).textContent || "",
        visibility: parseFloat2((entry.querySelector("V") || {}).textContent),
        precipitation: parseFloat2((entry.querySelector("R") || {}).textContent),
        road_temperature: parseFloat2((entry.querySelector("RTE") || {}).textContent),
      });
    }

    results[id] = { station_id: id, station_name: name, forecasts };
  }

  return results;
}

async function fetchWeather(stationIds) {
  const ids = stationIds.join(";");
  const params = "T;F;FX;D;W;V;N;R;RTE";
  const url = `${VEDUR_API}/?op_w=xml&type=forec&lang=en&view=xml&ids=${ids}&params=${params}`;

  const text = await fetchWithCorsRetry(url);
  return parseVedurXml(text);
}

async function fetchRoadConditions() {
  const url = `${VEGAGERDIN_API}?where=1%3D1&outFields=*&f=json`;

  try {
    const text = await fetchWithCorsRetry(url);
    const data = JSON.parse(text);
    const conditions = {};

    for (const feature of (data.features || [])) {
      const attrs = feature.attributes || {};
      const name = attrs.Nafn || attrs.NAME || "";
      if (name) {
        conditions[name] = {
          condition: attrs.Faerd || attrs.CONDITION || "Unknown",
          description: attrs.Lysing || attrs.DESCRIPTION || "",
        };
      }
    }
    return conditions;
  } catch (_) {
    return {};
  }
}
