# Run it yourself

The script calls each SportsDataHQ brand's `get_ratings` tool over REST and writes the CSVs in `ratings/`. It uses only the Python standard library.

## Keys

Each brand issues its own API key, and a key works only on its own brand. Free keys (500 credits a month, no card) are at each brand's site.

| Variable | Brand | Leagues |
|---|---|---|
| `SDHQ_API_KEY_PUCK` | PuckAPI | NHL predictions |
| `SDHQ_API_KEY_DUNK` | DunkAPI | NBA, WNBA, NCAAM, NCAAW, NBL |
| `SDHQ_API_KEY_FASTBALL` | FastballAPI | MLB, NCAA baseball |
| `SDHQ_API_KEY_STRIKER` | StrikerAPI | 17 soccer leagues |
| `SDHQ_API_KEY_ACES` | AcesAPI | ATP, WTA, by surface |
| `SDHQ_API_KEY_BIRDIE` | BirdieAPI | PGA, LPGA, LIV, DP World, Korn Ferry |
| `SDHQ_API_KEY_FIGHTER` | FighterAPI | UFC |
| `SDHQ_API_KEY_YORKER` | YorkerAPI | Cricket |

A brand without a key is skipped.

## Commands

    python3 scripts/fetch_ratings.py --dry-run          # calls and credits, no requests
    export SDHQ_API_KEY_DUNK=...
    python3 scripts/fetch_ratings.py --only dunk         # one brand

Each `get_ratings` call costs 2 credits and the NHL predictions call 5. A full run of every league is 47 calls and 97 credits.

Exit codes: 0 when every call succeeded, 2 when some failed (the leagues that worked are still written), 1 when nothing was fetched.
