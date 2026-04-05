/**
 * Iceland route definitions with associated weather stations.
 * Ring Road (Route 1) segments and additional popular routes.
 */

const STATIONS = {
  reykjavik: 1, keflavik: 990, borgarnes: 1473, blonduos: 2642,
  akureyri: 422, husavik: 2963, egilsstadir: 571, hofn: 705,
  vik: 798, selfoss: 1395, isafjordur: 2315, stykkisholmur: 1856,
  kirkjubaejarklaustur: 749, hella: 1175,
};

const RING_ROAD_SEGMENTS = [
  { id: "ring-1", name: "Reykjavik to Borgarnes", from: "Reykjavik", to: "Borgarnes", km: 74, route: 1, stations: [1, 1473], desc: "Hvalfjordur tunnel route through West Iceland" },
  { id: "ring-2", name: "Borgarnes to Blonduos", from: "Borgarnes", to: "Blonduos", km: 200, route: 1, stations: [1473, 2642], desc: "Through Hrutafjordur along the north coast" },
  { id: "ring-3", name: "Blonduos to Akureyri", from: "Blonduos", to: "Akureyri", km: 145, route: 1, stations: [2642, 422], desc: "Along Skagafjordur to the capital of the north" },
  { id: "ring-4", name: "Akureyri to Husavik", from: "Akureyri", to: "Husavik", km: 91, route: 1, stations: [422, 2963], desc: "Northeast Iceland, near whale watching capital" },
  { id: "ring-5", name: "Husavik to Egilsstadir", from: "Husavik", to: "Egilsstadir", km: 206, route: 1, stations: [2963, 571], desc: "Through the remote northeast highlands" },
  { id: "ring-6", name: "Egilsstadir to Hofn", from: "Egilsstadir", to: "Hofn", km: 244, route: 1, stations: [571, 705], desc: "East fjords coastal route with stunning views" },
  { id: "ring-7", name: "Hofn to Vik", from: "Hofn", to: "Vik", km: 272, route: 1, stations: [705, 749, 798], desc: "Past Vatnajokull glacier and black sand beaches" },
  { id: "ring-8", name: "Vik to Selfoss", from: "Vik", to: "Selfoss", km: 148, route: 1, stations: [798, 1175, 1395], desc: "South coast through Hella to the Golden Circle area" },
  { id: "ring-9", name: "Selfoss to Reykjavik", from: "Selfoss", to: "Reykjavik", km: 57, route: 1, stations: [1395, 1], desc: "Quick drive back to the capital" },
];

const EXTRA_ROUTES = [
  { id: "kef-rvk", name: "Keflavik Airport to Reykjavik", from: "Keflavik", to: "Reykjavik", km: 50, route: 41, stations: [990, 1], desc: "Airport transfer route via Reykjanesbraut" },
  { id: "west-1", name: "Borgarnes to Stykkisholmur", from: "Borgarnes", to: "Stykkisholmur", km: 100, route: 54, stations: [1473, 1856], desc: "Snaefellsnes peninsula route" },
  { id: "west-2", name: "Borgarnes to Isafjordur", from: "Borgarnes", to: "Isafjordur", km: 380, route: 61, stations: [1473, 2315], desc: "Remote Westfjords route (check conditions carefully)" },
];

const ALL_SEGMENTS = [...RING_ROAD_SEGMENTS, ...EXTRA_ROUTES];

const NAMED_ROUTES = {
  "ring-road": { name: "Ring Road (Full Circle)", segments: RING_ROAD_SEGMENTS.map(s => s.id), description: "Complete circuit of Iceland via Route 1" },
  "south-coast": { name: "South Coast", segments: ["ring-8", "ring-7"], description: "Reykjavik area to Hofn via the south coast" },
  "north-iceland": { name: "North Iceland", segments: ["ring-3", "ring-4", "ring-5"], description: "Blonduos to Egilsstadir through the north" },
  "golden-circle-area": { name: "Golden Circle Area", segments: ["ring-9", "ring-8"], description: "Reykjavik to Selfoss to Vik area" },
  "airport-transfer": { name: "Airport Transfer", segments: ["kef-rvk"], description: "Keflavik International Airport to Reykjavik" },
  "westfjords": { name: "Westfjords", segments: ["ring-1", "west-2"], description: "Reykjavik to Isafjordur via Borgarnes" },
  "snaefellsnes": { name: "Snaefellsnes Peninsula", segments: ["ring-1", "west-1"], description: "Reykjavik to Stykkisholmur via Borgarnes" },
};

function getSegment(id) {
  return ALL_SEGMENTS.find(s => s.id === id) || null;
}

function getRouteSegments(routeName) {
  const route = NAMED_ROUTES[routeName];
  if (!route) return [];
  return route.segments.map(getSegment).filter(Boolean);
}

function getAllStationIds(segments) {
  const seen = new Set();
  const ids = [];
  for (const seg of segments) {
    for (const sid of seg.stations) {
      if (!seen.has(sid)) { seen.add(sid); ids.push(sid); }
    }
  }
  return ids;
}
