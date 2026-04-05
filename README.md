# WeatherRoad - Iceland Weather Route Planner

Plan safe driving routes around Iceland based on real-time weather forecasts and road conditions.

WeatherRoad fetches live data from the [Icelandic Meteorological Office](https://vedur.is) and the [Icelandic Road Administration](https://road.is) to assess driving conditions along Iceland's routes, including the famous Ring Road (Route 1).

## Features

- Real-time weather forecasts for route segments from Vedur.is
- Road condition data from Vegagerdin (Icelandic Road Administration)
- Safety assessments: SAFE, CAUTION, HAZARDOUS, or DANGEROUS
- Wind, visibility, temperature, and ice warnings
- Estimated travel delays based on conditions
- Predefined routes: Ring Road, South Coast, Westfjords, and more
- Custom route planning using individual segments

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Usage

### List available routes

```bash
weatherroad routes
```

### List all route segments

```bash
weatherroad segments
```

### Plan a predefined route

```bash
weatherroad plan --route ring-road
weatherroad plan --route south-coast
weatherroad plan --route airport-transfer
```

### Plan a custom route

```bash
weatherroad plan --segments ring-1 ring-2 ring-3
```

## Available Predefined Routes

| Route | Description |
|-------|-------------|
| `ring-road` | Complete Ring Road circuit (Route 1) |
| `south-coast` | South coast from Selfoss to Hofn |
| `north-iceland` | Blonduos to Egilsstadir through the north |
| `golden-circle-area` | Reykjavik to Vik area |
| `airport-transfer` | Keflavik Airport to Reykjavik |
| `westfjords` | Reykjavik to Isafjordur |
| `snaefellsnes` | Reykjavik to Stykkisholmur |

## Safety Levels

- **SAFE** - Normal driving conditions
- **CAUTION** - Increased care needed (moderate wind, freezing temps, reduced visibility)
- **HAZARDOUS** - Only travel if necessary (strong wind, poor visibility, icy roads)
- **DANGEROUS** - Do not travel (extreme wind, near-zero visibility)

## Data Sources

- **Weather**: [Vedur.is](https://vedur.is) - Icelandic Meteorological Office XML API
- **Road Conditions**: [Vegagerdin](https://road.is) - Icelandic Road Administration ArcGIS API

## Running Tests

```bash
pytest
```

## License

MIT
