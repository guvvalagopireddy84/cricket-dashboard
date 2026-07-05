# Beyond the Coin Flip — A T20 Cricket World Cup Analysis (2007–2026)

FIT5147 Data Visualisation Project (Part 2)
Author: Guvvala Gopi Reddy — 35363037

## What this is
An interactive narrative visualisation that explores what actually decides the
ICC Men's T20 World Cup across every edition from 2007 to 2026, for an audience
of cricket fans. It answers three questions on one page:

1. Does pre-tournament form predict where a team finishes?  (form-tier Sankey + form bars)
2. How much does winning the toss really matter?            (head-to-head chord + venue/pitch map)
3. Who are the match-winners, and do they win titles?       (top batters/bowlers, wagon wheel, pitch map, players-by-country)

A single year selector drives all three views together; the map stays constant
and is linked to the chord (hovering a team highlights where it played).

## How to view it
Open `T20_WorldCup_Analysis.html` in a modern browser (Chrome or Firefox).
Just double-click it, or drag it into a browser window. No server or internet is
required — d3.js and Leaflet are bundled inside the file, and all data is embedded.
(The only online resource is the map's background tiles; the data dots work offline.)

Each chart has a "?" icon that explains how to read it.

## How it is built (architecture)
- Front end: plain HTML/CSS/JavaScript using **d3.js v7** (Sankey, chord, wagon wheel,
  pitch map, bar charts) and **Leaflet** (venue map). Both libraries are inlined so
  the file is fully self-contained and portable.
- Back end / data pipeline: the raw datasets are large, so all heavy work is done
  **offline in Python** (see `data_pipeline/`). The scripts aggregate the raw
  ball-by-ball data into small summary tables (team form, head-to-head + toss
  conversion, ~204 geocoded venues, and per-edition top-5 batters/bowlers with
  wagon-wheel zones and bowling length/line grids). Only these summaries are embedded
  in the HTML as small JavaScript objects, so the browser only renders — it never
  processes the raw data. This keeps the page fast and the file ~1 MB.

Pipeline: raw sources  ->  Python aggregation  ->  embedded summary tables  ->  d3/Leaflet rendering.

## Data sources
- Men's T20 International ball-by-ball data — Cricsheet (cricsheet.org).
- ICC T20 World Cup ball-by-ball commentary, 2007–2026 (scraped); 2024 edition from a
  supplementary match dataset.
- Tournament outcomes (champion / runner-up / stage reached) from the public record.
- Player avatar images supplied by the author.

## Honesty / data notes (see report section 3.1)
- A few sparse early editions (limited archived ball-by-ball) use representative
  matchups for the chord; these are flagged in the interface.
- Bowling length and line for the pitch map are inferred by scanning commentary text
  for terms like "yorker", "short", "outside off" — a faithful pattern, not ball tracking.
- The wagon wheel is built from per-zone run totals (areas), not individual shot coordinates.

## Files
- `T20_WorldCup_Analysis.html` — the complete interactive visualisation (open this).
- `data_pipeline/process_ch3.py` — Python that builds the player-impact, wagon-wheel
  and bowling pitch-map data from the commentary + 2024 dataset.
- `data/players_processed.json` — example processed output used by the visualisation.
