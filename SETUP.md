# Setup (for the repo owner)

The repo is private until reviewed. Nothing here runs without the secrets below.

## 1. Repo secrets

Each SportsDataHQ brand issues its own API key, and a key works only on its own
brand. Add one secret per brand (Settings, Secrets and variables, Actions):

| Secret | Brand | Feeds |
|---|---|---|
| `SDHQ_API_KEY_PUCK` | PuckAPI | NHL predictions |
| `SDHQ_API_KEY_DUNK` | DunkAPI | NBA, WNBA, NCAAM, NCAAW, NBL |
| `SDHQ_API_KEY_FASTBALL` | FastballAPI | MLB, NCAA baseball |
| `SDHQ_API_KEY_STRIKER` | StrikerAPI | 17 soccer leagues |
| `SDHQ_API_KEY_ACES` | AcesAPI | ATP, WTA, by surface |
| `SDHQ_API_KEY_BIRDIE` | BirdieAPI | PGA, LPGA, LIV, DP World, Korn Ferry |
| `SDHQ_API_KEY_FIGHTER` | FighterAPI | UFC |
| `SDHQ_API_KEY_YORKER` | YorkerAPI | Cricket |

`SDHQ_API_KEY` is an optional fallback used for any brand without its own
secret; a brand whose key is rejected is skipped, not failed.

Use an internal account's key for each brand, not a personal or customer key.

Credits: a full run is about 97 credits (46 get_ratings calls at 2 credits plus
one NHL predictions call at 5), so about 2,900 a month across all brands. Per
brand that is at most 34 credits a day (StrikerAPI), about 1,000 a month. The
free plan has 500 a month, so the internal accounts need a raised allowance
(or a comped paid plan) before the daily schedule is turned on.

## 2. Run it once

Actions tab, "Daily ratings", Run workflow. Check the run summary: calls ok,
credits used, and any brand skipped. Then confirm the schedule (11:00 UTC).

## 3. Locally

    export SDHQ_API_KEY_DUNK=...   # one per brand you want
    python3 scripts/fetch_ratings.py --only dunk
    python3 scripts/fetch_ratings.py --dry-run

## 4. Before making it public

- Open `ratings/` and confirm no odds, prices or box scores (there are none by design).
- Read README.md and ratings.ipynb. The notebook loads from the raw GitHub URL,
  which only works once the repo is public.
- Settings, General, make public. Add a short description and the topics.
