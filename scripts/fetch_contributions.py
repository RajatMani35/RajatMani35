import json
import re
from datetime import date, datetime, timedelta

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "RajatMani35"

URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}


# ============================================================
# FETCH GITHUB PAGE
# ============================================================

def fetch_page():

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# PARSE CONTRIBUTIONS
# ============================================================

def get_contributions(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # --------------------------------------------------------
    # Find GitHub contribution cells
    # --------------------------------------------------------

    cells = soup.select(
        "td.ContributionCalendar-day[data-date]"
    )

    print(
        f"Found {len(cells)} contribution cells"
    )

    if not cells:

        raise RuntimeError(
            "GitHub contribution cells were not found."
        )

    # --------------------------------------------------------
    # Create tooltip map
    #
    # GitHub stores the exact contribution count in a
    # <tool-tip> element.
    #
    # Example:
    #
    # 4 contributions on October 4th
    #
    # or:
    #
    # 1 contribution on September 10th
    # --------------------------------------------------------

    tooltip_map = {}

    tooltips = soup.find_all(
        "tool-tip"
    )

    print(
        f"Found {len(tooltips)} tooltips"
    )

    for tooltip in tooltips:

        tooltip_id = tooltip.get("for")

        if not tooltip_id:
            continue

        text = tooltip.get_text(
            " ",
            strip=True
        )

        # Find a number at the beginning.
        #
        # Examples:
        #
        # "4 contributions on..."
        # "1 contribution on..."
        #
        match = re.search(
            r"(\d+)\s+contribution",
            text,
            re.IGNORECASE
        )

        if match:

            count = int(
                match.group(1)
            )

        else:

            count = 0

        tooltip_map[tooltip_id] = count

    print(
        f"Mapped {len(tooltip_map)} contribution counts"
    )

    # --------------------------------------------------------
    # Build contribution list
    # --------------------------------------------------------

    days = []

    for cell in cells:

        cell_date = cell.get(
            "data-date"
        )

        if not cell_date:
            continue

        cell_id = cell.get(
            "id"
        )

        level_text = cell.get(
            "data-level",
            "0"
        )

        # Convert contribution level to integer
        try:

            level = int(
                level_text
            )

        except (
            TypeError,
            ValueError
        ):

            level = 0

        # Get contribution count
        count = tooltip_map.get(
            cell_id,
            0
        )

        days.append({
            "date": cell_date,
            "count": count,
            "level": level
        })

    # --------------------------------------------------------
    # Sort dates
    # --------------------------------------------------------

    days.sort(
        key=lambda day: day["date"]
    )

    return days


# ============================================================
# CALCULATE STATISTICS
# ============================================================

def calculate_stats(days):

    # --------------------------------------------------------
    # Total contributions
    # --------------------------------------------------------

    total = sum(
        day["count"]
        for day in days
    )

    # --------------------------------------------------------
    # Longest streak
    # --------------------------------------------------------

    longest_streak = 0
    streak = 0

    for day in days:

        if day["count"] > 0:

            streak += 1

            if streak > longest_streak:

                longest_streak = streak

        else:

            streak = 0

    # --------------------------------------------------------
    # Current streak
    # --------------------------------------------------------

    current_streak = 0

    day_map = {}

    for day in days:

        day_date = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        ).date()

        day_map[day_date] = day["count"]

    if day_map:

        latest_date = max(
            day_map.keys()
        )

        today = date.today()

        check_date = min(
            latest_date,
            today
        )

        # If today has no contribution,
        # check from yesterday.
        if day_map.get(
            check_date,
            0
        ) == 0:

            check_date -= timedelta(
                days=1
            )

        # Walk backwards while contributions exist
        while day_map.get(
            check_date,
            0
        ) > 0:

            current_streak += 1

            check_date -= timedelta(
                days=1
            )

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }


# ============================================================
# SAVE JSON
# ============================================================

def save_data(days, stats):

    data = {
        "username": USERNAME,
        "updated": date.today().isoformat(),
        "days": days,
        "stats": stats
    }

    with open(
        "data/contributions.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    return data


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("===================================")
    print(" GitHub Contribution Fetcher")
    print("===================================")
    print()

    print(
        f"Username: {USERNAME}"
    )

    print(
        f"URL: {URL}"
    )

    print()

    # --------------------------------------------------------
    # Fetch GitHub page
    # --------------------------------------------------------

    html = fetch_page()

    print(
        f"Downloaded: {len(html):,} characters"
    )

    print()

    # --------------------------------------------------------
    # Parse contributions
    # IMPORTANT: pass html here
    # --------------------------------------------------------

    days = get_contributions(
        html
    )

    # --------------------------------------------------------
    # Calculate statistics
    # --------------------------------------------------------

    stats = calculate_stats(
        days
    )

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    save_data(
        days,
        stats
    )

    # --------------------------------------------------------
    # Print result
    # --------------------------------------------------------

    print()
    print("===================================")
    print(" Done!")
    print("===================================")
    print()

    print(
        f"Days found: {len(days)}"
    )

    print(
        f"Total contributions: {stats['total']}"
    )

    print(
        f"Current streak: {stats['current_streak']}"
    )

    print(
        f"Longest streak: {stats['longest_streak']}"
    )

    print()

    print(
        "Saved: data/contributions.json"
    )

    print()


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()