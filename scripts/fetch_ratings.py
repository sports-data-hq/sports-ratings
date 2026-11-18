#!/usr/bin/env python3
"""Fetch SportsDataHQ ratings over the public REST API and write CSV files.

For every job below this writes ratings/<sport>/<league>.csv (today's ratings,
replaced each run) and appends to ratings/<sport>/<league>_history.csv with a
date column (rows for the same date are replaced, so a rerun is safe).

Only our own derived ratings and minimal identifiers are stored. Stdlib only.

Keys: each brand has its own API key. Set SDHQ_API_KEY_<BRAND> (for example
SDHQ_API_KEY_DUNK). SDHQ_API_KEY is used as a fallback for any brand without
its own variable; a brand whose key is rejected or missing is skipped.

Usage:
  python3 scripts/fetch_ratings.py                # all brands
  python3 scripts/fetch_ratings.py --only dunk    # one brand
  python3 scripts/fetch_ratings.py --dry-run      # list the calls and credits
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDITS_PER_CALL = 2  # get_ratings costs 2 credits on every brand

COLUMNS = ["date", "league", "variant", "group", "rank", "id", "name", "abbrev",
           "country", "rating", "games", "last_played", "as_of"]

# brand -> (domain, env suffix)
BRANDS = {
    "puck": "puckapi.com", "dunk": "dunkapi.com", "fastball": "fastballapi.com",
    "striker": "strikerapi.com", "aces": "acesapi.com", "birdie": "birdieapi.com",
    "fighter": "fighterapi.com", "yorker": "yorkerapi.com",
}


def job(brand, sport, file, league, variant="", params=None, tool="get_ratings"):
    return dict(brand=brand, sport=sport, file=file, league=league,
                variant=variant, params=params or {}, tool=tool)


JOBS = []
# Basketball (DunkAPI)
for lg, lim in [("nba", 100), ("wnba", 100), ("ncaam", 500), ("ncaaw", 500), ("nbl", 100)]:
    JOBS.append(job("dunk", "basketball", lg, lg, params={"league": lg, "limit": lim}))
# Baseball (FastballAPI)
for lg, lim in [("mlb", 100), ("ncaabase", 500)]:
    JOBS.append(job("fastball", "baseball", lg, lg, params={"league": lg, "limit": lim}))
# Soccer (StrikerAPI)
for lg in ["soccer", "mls", "laliga", "seriea", "bundesliga", "ligue1", "ucl",
           "championship", "nwsl", "ligamx", "uel", "uecl", "eredivisie",
           "primeira", "scotland", "brazil", "argentina"]:
    file = "premier_league" if lg == "soccer" else lg
    JOBS.append(job("striker", "soccer", file, lg, params={"league": lg, "limit": 100}))
# Tennis (AcesAPI): overall and by surface
for tour, lg in [("atp", "tennis"), ("wta", "wta")]:
    JOBS.append(job("aces", "tennis", tour, tour, "overall", {"league": lg, "limit": 200}))
    for surf in ["hard", "clay", "grass"]:
        JOBS.append(job("aces", "tennis", tour, tour, surf,
                        {"league": lg, "surface": surf, "limit": 200}))
# Golf (BirdieAPI)
for lg, file in [("golf", "pga"), ("lpga", "lpga"), ("liv", "liv"),
                 ("dpwt", "dpwt"), ("kornferry", "kornferry")]:
    JOBS.append(job("birdie", "golf", file, file, params={"league": lg, "limit": 200}))
# MMA (FighterAPI): UFC
JOBS.append(job("fighter", "mma", "ufc", "ufc", params={"league": "mma", "limit": 300}))
# Cricket (YorkerAPI): men's and women's, by format
for fmt in ["test", "odi", "t20"]:
    for gender in ["male", "female"]:
        JOBS.append(job("yorker", "cricket", "international", "international", fmt,
                        {"format": fmt, "gender": gender, "team_type": "international", "limit": 100}))
for gender in ["male", "female"]:
    JOBS.append(job("yorker", "cricket", "t20_club", "t20_club", "t20",
                    {"format": "t20", "gender": gender, "team_type": "club", "limit": 100}))


def first(d, *names):
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return ""


def normalize(row, j, today, as_of_top, group_hint):
    """Map one API row to our columns. Unknown fields are dropped."""
    return {
        "date": today,
        "league": j["league"],
        "variant": j["variant"],
        "group": first(row, "weight_class") or group_hint or first(row, "gender"),
        "rank": first(row, "rank"),
        "id": first(row, "team_id", "player_id", "fighter_id", "id"),
        "name": first(row, "name", "team"),
        "abbrev": first(row, "abbrev"),
        "country": first(row, "country"),
        "rating": first(row, "rating", "elo"),
        "games": first(row, "matches", "surface_matches", "fights", "weighted_rounds"),
        "last_played": first(row, "last_game", "last_match", "last_fight"),
        "as_of": first(row, "as_of", "rated_after") or as_of_top,
    }


def call(domain, tool, body, key):
    req = urllib.request.Request(
        f"https://mcp.{domain}/v1/{tool}", data=json.dumps(body).encode(),
        headers={"x-api-key": key, "content-type": "application/json",
                 "user-agent": "sdhq-sports-ratings/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        used = int(r.headers.get("x-credits-used") or 0)
        return json.loads(r.read().decode()), used


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


PRED_COLUMNS = ["date", "game_id", "game_date", "start_time_utc", "home", "away",
                "home_win_prob", "away_win_prob", "grade"]


def fetch_nhl_predictions(today, key):
    """NHL has no get_ratings tool; publish the model's win probabilities instead (5 credits)."""
    data, used = call(BRANDS["puck"], "get_predictions", {}, key)
    games = (data.get("data", data)).get("games") or []
    rows = [{"date": today, "game_id": g.get("gameId"), "game_date": g.get("gameDate"),
             "start_time_utc": g.get("startTimeUtc"), "home": g.get("homeTeam"),
             "away": g.get("awayTeam"), "home_win_prob": g.get("homeWinProb"),
             "away_win_prob": g.get("awayWinProb"), "grade": g.get("grade")} for g in games]
    base = os.path.join(ROOT, "ratings", "hockey", "nhl_predictions")
    old = [r for r in read_csv(base + "_history.csv") if r["date"] != today]
    for path, keep in [(base + ".csv", []), (base + "_history.csv", old)]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=PRED_COLUMNS)
            w.writeheader()
            w.writerows(keep + rows)
    return len(rows), used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="run one brand, for example dunk")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    jobs = [j for j in JOBS if not args.only or j["brand"] == args.only]
    if args.dry_run:
        print(f"{len(jobs)} calls, {len(jobs) * CREDITS_PER_CALL} credits")
        return 0

    # Group rows by output file so variants share one file.
    outputs, done, skipped, failed = {}, 0, {}, []
    credits = 0
    for j in jobs:
        brand = j["brand"]
        key = os.environ.get(f"SDHQ_API_KEY_{brand.upper()}") or os.environ.get("SDHQ_API_KEY")
        if not key:
            skipped[brand] = "no key"
            continue
        if brand in skipped:
            continue
        try:
            data, used = call(BRANDS[brand], j["tool"], j["params"], key)
        except urllib.error.HTTPError as e:
            if e.code in (401, 402):
                skipped[brand] = f"HTTP {e.code}"
                continue
            failed.append(f"{brand}/{j['file']}/{j['variant']}: HTTP {e.code}")
            continue
        except Exception as e:  # network or parse error
            failed.append(f"{brand}/{j['file']}/{j['variant']}: {type(e).__name__}")
            continue
        credits += used
        payload = data.get("data", data)
        rows = payload.get("ratings") or []
        if not rows:
            failed.append(f"{brand}/{j['file']}/{j['variant']}: empty")
            continue
        group_hint = j["params"].get("gender", "")
        top_asof = payload.get("as_of") or ""
        rec = [normalize(r, j, today, top_asof, group_hint) for r in rows]
        outputs.setdefault((j["sport"], j["file"]), []).extend(rec)
        done += 1

    for (sport, file), rows in outputs.items():
        base = os.path.join(ROOT, "ratings", sport, file)
        write_csv(base + ".csv", rows)
        hist = [r for r in read_csv(base + "_history.csv") if r["date"] != today]
        write_csv(base + "_history.csv", hist + rows)

    pkey = os.environ.get("SDHQ_API_KEY_PUCK") or os.environ.get("SDHQ_API_KEY")
    if (not args.only or args.only == "puck") and pkey:
        try:
            n, used = fetch_nhl_predictions(today, pkey)
            credits += used
            done += 1
            print(f"nhl predictions: {n} games")
        except urllib.error.HTTPError as e:
            skipped["puck"] = f"HTTP {e.code}"
        except Exception as e:
            failed.append(f"puck/predictions: {type(e).__name__}")
    else:
        skipped.setdefault("puck", "no key")
    print(f"date {today}: {done}/{len(jobs) + 1} calls ok, {credits} credits used, "
          f"{len(outputs)} files written")
    for b, why in skipped.items():
        print(f"skipped {b}: {why}")
    for f in failed:
        print(f"failed {f}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as s:
            s.write(f"Ratings run {today}: {done}/{len(jobs) + 1} calls, {credits} credits. "
                    f"Skipped: {skipped or 'none'}. Failed: {len(failed)}\n")
    return 0 if done else 1


if __name__ == "__main__":
    sys.exit(main())
