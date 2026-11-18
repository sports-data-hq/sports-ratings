# sports-ratings

Team, player and fighter ratings from SportsDataHQ's own models, as CSV files, with the code that produces them. Updated daily.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sports-data-hq/sports-ratings/blob/main/ratings.ipynb)

Ratings by SportsDataHQ (sportsdatahq.com). Data is CC BY 4.0, code is MIT.

## What is in here

Only our derived numbers and the minimum needed to identify them: id, name, league, season date. No odds or prices, no play-by-play, no box scores.

| Folder | League files | Source brand |
|---|---|---|
| `ratings/basketball/` | `nba`, `wnba`, `ncaam`, `ncaaw`, `nbl` | [DunkAPI](https://dunkapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) |
| `ratings/baseball/` | `mlb`, `ncaabase` | [FastballAPI](https://fastballapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) |
| `ratings/soccer/` | Premier League (`premier_league`), `mls`, `laliga`, `seriea`, `bundesliga`, `ligue1`, `ucl`, `championship`, `nwsl`, `ligamx`, `uel`, `uecl`, `eredivisie`, `primeira`, `scotland`, `brazil`, `argentina` | [StrikerAPI](https://strikerapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) |
| `ratings/tennis/` | `atp`, `wta` (overall and by surface) | [AcesAPI](https://acesapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) |
| `ratings/golf/` | `pga`, `lpga`, `liv`, `dpwt`, `kornferry` | [BirdieAPI](https://birdieapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) |
| `ratings/mma/` | `ufc` | [FighterAPI](https://fighterapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) |
| `ratings/cricket/` | `international`, `t20_club` (men and women, by format) | [YorkerAPI](https://yorkerapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) |
| `ratings/hockey/` | `nhl_predictions` (game win probabilities) | [PuckAPI](https://puckapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) |

Each league has two files: `<league>.csv` (today's ratings, replaced each run) and `<league>_history.csv` (every day since this repo started collecting, one block of rows per date).

## Update schedule

A GitHub Actions workflow runs daily at 11:00 UTC, after the data jobs finish at 10:00 UTC, and commits any change. Ratings only move when games or matches finish, so some leagues are unchanged for days, and off-season leagues do not change at all. History starts on the first run date; it is not backfilled.

## Columns

Rating files:

| Column | Meaning |
|---|---|
| `date` | Date of the run (UTC). The key for history files. |
| `league` | League file name. |
| `variant` | Tennis: `overall`, `hard`, `clay`, `grass`. Cricket: `test`, `odi`, `t20`. Empty elsewhere. |
| `group` | Cricket: `male` or `female`. UFC: weight class. Empty elsewhere. |
| `rank` | Rank within the file's league, variant and group, best first. |
| `id` | The brand's team, player or fighter id. |
| `name` | Name. |
| `abbrev` | Team abbreviation where one exists. |
| `country` | Player country (tennis, golf). |
| `rating` | The rating. See methods below for the scale. |
| `games` | Sample behind the rating where given: matches, fights or weighted rounds. |
| `last_played` | Date of the last game, match or fight where given. |
| `as_of` | When the rating was last updated. |

`nhl_predictions.csv` has `date, game_id, game_date, start_time_utc, home, away, home_win_prob, away_win_prob, grade`. `grade` is the model's confidence band for the game, A to D.

## Methods

Each rating is our own model output, computed from results.

- **Basketball (NBA, WNBA, NCAAM, NCAAW, NBL):** Elo from every final game in our data, with home advantage and a margin-of-victory multiplier. Ratings regress a quarter of the way to the mean between seasons. 1500 is average; a 100-point gap is about a 64% favourite on a neutral floor.
- **Baseball (MLB, NCAA):** Elo from every final game in our data, with home advantage and a small margin multiplier. Ratings regress a third of the way to the mean between seasons. 1500 is average.
- **Soccer:** Elo from every final match in the competition, K 20, home advantage 60 points (none at neutral venues), scaled by goal difference, a third of the way back to 1500 between seasons. 400 points is 10-to-1 odds. A rating moves only on that competition's matches, so ratings are not comparable across leagues.
- **Tennis:** Elo from every completed singles match on the tour since 2007 (main draw and qualifying), start 1500, K = 250 / (matches + 5)^0.4. The surface rating counts only matches on that surface. Walkovers, defaults and retirements are not rated. A player needs at least 10 rated matches to be listed, and players with no rated match in the past year are left out.
- **Golf:** not Elo. Strokes per round better than an average player in the same field, from every full round: each round is compared with the field's average on the same course that day, adjusted for how strong the field was, weighted toward recent rounds (half-life one year) and shrunk toward zero for players with few rounds. Positive is better, 0 is average. Measured within one tour.
- **MMA (UFC):** Elo from UFC results alone: start 1500, K 40 for a fighter's first five bouts then 24, finishes weighted 1.15, draws 0.5, no contests unrated.
- **Cricket:** Elo per format from every decided, tied or drawn match since 2001 in our record: start 1500, a tie or draw scores a half, K shrinks with matches played. Franchises and countries are separate pools, and men's and women's sides are separate teams.
- **NHL:** win probabilities for each game on the day's slate from PuckAPI's game model (not Elo). The model's accuracy is a walk-forward backtest, not a live record.

Full definitions are in each brand's docs under `get_ratings`.

## Run it yourself

    python3 scripts/fetch_ratings.py --dry-run

The script uses only the Python standard library. Each brand's API key works only on that brand; see [SETUP.md](SETUP.md). A free key (500 credits a month, no card) is enough to pull a few leagues yourself, and the notebook shows how.

## Licence

- Data in `ratings/`: [CC BY 4.0](LICENSE-DATA.md). Required credit: **Ratings by SportsDataHQ (sportsdatahq.com)**.
- Code: [MIT](LICENSE).

The ratings are derived model outputs. Names identify ratings only; no league, team or athlete rights are granted.

## Want more

The API serves fresher and deeper data: ratings for any date, season and league option, plus schedules, standings and team and player statistics. Each brand has a free tier of 500 credits a month.

[PuckAPI](https://puckapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) · [DunkAPI](https://dunkapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) · [FastballAPI](https://fastballapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) · [StrikerAPI](https://strikerapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) · [AcesAPI](https://acesapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) · [BirdieAPI](https://birdieapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) · [FighterAPI](https://fighterapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings) · [YorkerAPI](https://yorkerapi.com/?utm_source=github&utm_medium=readme&utm_campaign=sports-ratings)
