# Beyond the Coin Flip 🏏

**An interactive narrative visualisation of the ICC Men's T20 World Cup (2007–2026), built with D3.js**

Every T20 World Cup match starts with a coin toss — and with the folklore that winning it means you're halfway to winning the game. This project takes that belief, and two others fans repeat just as often, and tests them against twenty years of ball-by-ball data.

**🔗 Live demo:** https://guvvalagopireddy84.github.io/cricket-dashboard/
*(works best on a desktop browser — Chrome or Firefox)*

---

## The three questions

The whole page is one guided story in three acts, driven by a single edition selector at the top — change the year and every chart redraws together.

| Act | Question | Visualisation |
|---|---|---|
| 1. Does form matter? | Does pre-tournament form predict how far a team goes? | Sankey flow of form tiers → tournament finish, plus bat-shaped "form fill" bars |
| 2. The toss truth | How much does winning the toss really matter? | Head-to-head chord diagram linked to an interactive world map of ~200 venues, coloured by pitch type |
| 3. The match-winners | Who actually decides tournaments? | Top-5 batters and bowlers per edition with impact scores, wagon wheels of scoring zones, and top-down bowling pitch maps |

The two views in Act 2 are linked: hovering a team on the chord highlights the grounds it played at on the map. Every chart has a "?" guide explaining how to read it — the design goal was that a cricket fan with **no statistics background** can follow the whole story.

## How it's built

```
Raw data  →  Python pipeline  →  compact summary tables  →  single self-contained HTML page (D3 + Leaflet)
```

**Front end** — plain HTML/CSS/JavaScript with **D3.js v7** (d3-sankey, d3-chord, d3-arc for the wagon wheel, bat-fill and pitch map) and **Leaflet** for the venue map. Both libraries are inlined, so the page is fully portable — no server, no build step, no internet needed except the map's background tiles.

**Data pipeline** — the raw inputs are large and messy (~3,300 Cricsheet match files, ~56,000 rows of scraped ball-by-ball commentary, plus a separate 2024 dataset), so all heavy processing happens offline in Python (`data_pipeline/`):

- merges and normalises multiple sources into a single ball-by-ball table
- infers each player's country from the matches they appeared in
- extracts **wagon-wheel scoring zones** and **bowling length/line** by parsing commentary text for phrases like "yorker", "short", "outside off"
- recovers wickets stored only as text by scanning for dismissal phrases
- computes a custom **impact score** for batters (runs + boundaries + strike-rate bonus) and bowlers (wickets + runs saved vs tournament average + dot balls)
- exports tiny pre-computed JSON summaries that get embedded in the page — the browser only renders, never crunches raw data

## Repository contents

| File | What it is |
|---|---|
| `T20_WorldCup_Analysis.html` | The complete interactive visualisation — just open it in a browser |
| `data_pipeline/process_ch3.py` | Python pipeline that builds player impact, wagon-wheel and pitch-map data |
| `data/players_processed.json` | Example processed output used by the visualisation |

## Data sources

- Men's T20 International ball-by-ball data — [Cricsheet](https://cricsheet.org)
- ICC T20 World Cup ball-by-ball commentary, 2007–2026 (scraped), plus a supplementary 2024 match dataset
- Tournament outcomes from the public record

## Honest limitations

- Bowling length and line are **inferred from commentary text**, not ball-tracking — a faithful approximation, not sensor data
- The wagon wheel aggregates runs into eight zones rather than plotting individual shot coordinates
- A few early editions have sparse archived ball-by-ball data; these are flagged in the interface

## Background

Built as the Data Visualisation Project for **FIT5147 (Data Exploration and Visualisation)** at Monash University, using the Five Design-Sheet methodology — three complete alternative designs were sketched and the final combines the strongest ideas from each. Design and code by **Guvvala Gopi Reddy**

## Files
- `T20_WorldCup_Analysis.html` — the complete interactive visualisation (open this).
- `data_pipeline/process_ch3.py` — Python that builds the player-impact, wagon-wheel
  and bowling pitch-map data from the commentary + 2024 dataset.
- `data/players_processed.json` — example processed output used by the visualisation.
