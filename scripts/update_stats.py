#!/usr/bin/env python3
"""Generate the live GitHub activity graphics (pixel-art contribution heatmap + stats card).

Used by .github/workflows/update-stats.yml. Needs GH_TOKEN and GH_LOGIN in the environment.

  python scripts/update_stats.py --out assets/generated            # real data (Actions)
  python scripts/update_stats.py --out assets/generated --placeholder   # empty starter files
  python scripts/update_stats.py --out /tmp/preview --demo         # fake data, for design previews only
"""
import argparse
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from pixel import *  # noqa: F401,F403

W = 830

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


# --- data ---------------------------------------------------------------------
def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-graphics"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        raise SystemExit(f"GraphQL error: {payload.get('errors')}")
    u = payload["data"]["user"]
    cc = u["contributionsCollection"]
    langs = {}
    stars = 0
    for repo in u["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return {
        "weeks": [[d["contributionCount"] for d in w["contributionDays"]] for w in cc["contributionCalendar"]["weeks"]],
        "dates": [[d["date"] for d in w["contributionDays"]] for w in cc["contributionCalendar"]["weeks"]],
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "repos": u["repositories"]["totalCount"],
        "stars": stars,
        "followers": u["followers"]["totalCount"],
        "langs": langs,
    }


def calendar_shell(zero=True):
    """53 empty weeks ending this week, used for placeholders / demo data."""
    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 1 + 52 * 7)  # a Sunday
    weeks, dates = [], []
    for w in range(53):
        days = [start + dt.timedelta(days=w * 7 + i) for i in range(7)]
        dates.append([d.isoformat() for d in days if d <= today])
        weeks.append([0] * len(dates[-1]))
    return weeks, dates


def demo_data():
    random.seed(7)
    weeks, dates = calendar_shell()
    for w in range(len(weeks)):
        for d in range(len(weeks[w])):
            r = random.random()
            weeks[w][d] = 0 if r < 0.45 else random.choice([1, 2, 3, 5, 8, 12]) if r < 0.97 else 20
    return {
        "weeks": weeks, "dates": dates, "total": sum(map(sum, weeks)), "commits": 412, "prs": 38, "issues": 9,
        "reviews": 14, "repos": 12, "stars": 27, "followers": 9,
        "langs": {"Python": 52000, "JavaScript": 31000, "HTML": 22000, "Go": 14000, "Shell": 6000},
    }


def placeholder_data():
    weeks, dates = calendar_shell()
    return {"weeks": weeks, "dates": dates, "total": None, "commits": None, "prs": None, "issues": None,
            "reviews": None, "repos": None, "stars": None, "followers": None, "langs": {}}


def streaks(weeks):
    flat = [c for w in weeks for c in w]
    best = run = 0
    for c in flat:
        run = run + 1 if c else 0
        best = max(best, run)
    cur = 0
    for c in reversed(flat if flat and flat[-1] else flat[:-1]):
        if c:
            cur += 1
        else:
            break
    return best, cur


# --- contributions.svg --------------------------------------------------------
LEVELS = ["#1b1b1b", "#24403f", ACCENT, ACCENT_HI, GOLD]
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def thresholds(weeks):
    """Quartiles of the non-zero days (like GitHub), so one huge day doesn't wash out the rest."""
    nz = sorted(c for w in weeks for c in w if c > 0)
    if not nz:
        return (1, 1, 1)
    return tuple(nz[min(len(nz) - 1, int(len(nz) * q))] for q in (0.25, 0.5, 0.75))


def level(c, th):
    if c <= 0:
        return 0
    return 1 if c <= th[0] else 2 if c <= th[1] else 3 if c <= th[2] else 4


def cell_d(x, y):
    return f"M{x + 2} {y}h8v2h2v8h-2v2h-8v-2h-2v-8h2z"


def contributions_svg(d, placeholder=False):
    weeks, dates = d["weeks"], d["dates"]
    th = thresholds(weeks)
    best, cur = streaks(weeks)
    total = d["total"] if d["total"] is not None else None
    cell, gap = 12, 3
    gx, gy = 19, 112
    h = 262
    fmt = lambda v: "--" if v is None else f"{v:,}"
    body = card(0, 0, W, h)
    # headline numbers
    for i, (lab, val, col) in enumerate([
        ("CONTRIBUTIONS, LAST YEAR", fmt(total), GOLD),
        ("LONGEST STREAK", "--" if placeholder else f"{best} DAYS", ACCENT_HI),
        ("CURRENT STREAK", "--" if placeholder else f"{cur} DAYS", ACCENT_HI),
    ]):
        x = 20 + i * 330 if i == 0 else 20 + 330 + (i - 1) * 215
        body += text(lab, x, 16, 2, MUTED) + text(val, x, 40, 3, col)
    # months
    labels, last_m = [], None
    for wi, ds in enumerate(dates):
        if ds and int(ds[0][5:7]) != last_m:
            last_m = int(ds[0][5:7])
            labels.append((wi, last_m))
    for i, (wi, m) in enumerate(labels):
        nxt = labels[i + 1][0] if i + 1 < len(labels) else None
        if (nxt is not None and nxt - wi < 4) or wi >= len(dates) - 3:
            continue  # drop a label that would collide with the next one (or run off the end)
        body += text(MONTHS[m - 1], gx + wi * (cell + gap), 82, 2, FAINT)
    # grid, one <g> per week so columns can ripple in
    for wi, w in enumerate(weeks):
        by_lvl = {}
        for di, c in enumerate(w):
            by_lvl.setdefault(level(c, th), []).append(cell_d(gx + wi * (cell + gap), gy + di * (cell + gap)))
        body += f'<g class="wk" style="animation-delay:{wi * 25}ms">'
        for lv in sorted(by_lvl):
            body += f'<path d="{"".join(by_lvl[lv])}" fill="{LEVELS[lv]}"/>'
        body += "</g>"
    # legend
    lx = W - 20
    body += text("MORE", lx, 224, 2, MUTED, anchor="end")
    x = lx - text_width("MORE", 2) - 10
    for lv in range(4, -1, -1):
        x -= 14
        body += f'<path d="{cell_d(x, 224)}" fill="{LEVELS[lv]}"/>'
    body += text("LESS", x - 10, 224, 2, MUTED, anchor="end")
    note = "RUN THE 'UPDATE PROFILE GRAPHICS' WORKFLOW TO FILL THIS IN" if placeholder else "UPDATED DAILY BY GITHUB ACTIONS"
    body += text(note, 20, 224, 2, FAINT)
    style = "@keyframes wk{from{opacity:0}}.wk{animation:wk .35s steps(3) both}"
    return svg(W, h, body, "Contribution heatmap", "Pixel-art GitHub contribution calendar for the last year.", style=style)


# --- activity.svg ---------------------------------------------------------------
LANG_COLORS = [ACCENT, BLUE_HI, GOLD, PURPLE, GREEN]


def activity_svg(d, placeholder=False):
    h = 232
    lw = 410
    body = card(0, 0, lw, h) + card(lw + 10, 0, W - lw - 10, h)
    fmt = lambda v: "--" if v is None else f"{v:,}"
    stats = [
        ("COMMITS", d["commits"]), ("PULL REQUESTS", d["prs"]),
        ("ISSUES", d["issues"]), ("CODE REVIEWS", d["reviews"]),
        ("PUBLIC REPOS", d["repos"]), ("STARS EARNED", d["stars"]),
    ]
    body += text("LAST 12 MONTHS", 20, 16, 2, ACCENT_HI)
    body += rect(20, 38, lw - 40, 1, RULE)
    for i, (lab, val) in enumerate(stats):
        col, row = i % 2, i // 2
        x, y = 20 + col * 190, 52 + row * 58
        body += text(lab, x, y, 2, MUTED) + text(fmt(val), x, y + 20, 3, GOLD if col == 0 and row == 0 else FG)
    # languages
    rx = lw + 30
    body += text("TOP LANGUAGES", rx, 16, 2, ACCENT_HI)
    body += rect(rx, 38, W - lw - 50, 1, RULE)
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:5]
    tot = sum(v for _, v in d["langs"].items()) or 1
    bx, bw = rx + 134, W - rx - 134 - 74 - 20
    if not langs:
        body += text("NO DATA YET", rx, 70, 2, FAINT)
    for i, (name, size) in enumerate(langs):
        y = 56 + i * 34
        pct = size / tot
        col = LANG_COLORS[i % len(LANG_COLORS)]
        body += text(name[:10], rx, y, 2, FG)
        body += rect(bx, y, bw, 16, BORDER) + rect(bx + 1, y + 1, bw - 2, 14, BG)
        body += rect(bx + 1, y + 1, max(2, round((bw - 2) * pct)), 14, col, f'class="grow" style="animation-delay:{i * 90}ms"')
        body += text(f"{pct * 100:.1f}%", W - 20, y, 2, MUTED, anchor="end")
    return svg(W, h, body, "GitHub activity", "Commits, pull requests, issues, reviews, repos, stars and top languages.", style=GROW_CSS)


def snake_placeholder():
    h = 120
    body = (
        card(0, 0, W, h)
        + text("CONTRIBUTION SNAKE", W // 2, 38, 3, ACCENT_HI, anchor="middle")
        + text("APPEARS AFTER THE FIRST WORKFLOW RUN", W // 2, 78, 2, MUTED, anchor="middle")
    )
    return svg(W, h, body, "Contribution snake placeholder")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/generated")
    ap.add_argument("--demo", action="store_true", help="fake data for previews")
    ap.add_argument("--placeholder", action="store_true", help="empty starter files")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if a.placeholder:
        data = placeholder_data()
    elif a.demo:
        data = demo_data()
    else:
        login, token = os.environ.get("GH_LOGIN"), os.environ.get("GH_TOKEN")
        if not login or not token:
            raise SystemExit("Set GH_LOGIN and GH_TOKEN (or use --demo / --placeholder).")
        data = fetch(login, token)

    with open(os.path.join(a.out, "contributions.svg"), "w") as f:
        f.write(contributions_svg(data, a.placeholder))
    with open(os.path.join(a.out, "activity.svg"), "w") as f:
        f.write(activity_svg(data, a.placeholder))
    if a.placeholder:
        with open(os.path.join(a.out, "snake.svg"), "w") as f:
            f.write(snake_placeholder())
    print("wrote", a.out)


if __name__ == "__main__":
    main()
