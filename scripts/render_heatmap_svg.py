import json
from pathlib import Path
from html import escape


INPUT_FILE = Path("data/contributions.json")
OUTPUT_FILE = Path("rajat-heatmap.svg")

USERNAME = "RajatMani35"

CELL_SIZE = 13
GAP = 4

LEFT = 40
TOP = 90

BACKGROUND = "#0d1117"
TEXT_PRIMARY = "#c9d1d9"
TEXT_SECONDARY = "#8b949e"

COLORS = [
    "#161b22",  # level 0
    "#0e4429",  # level 1
    "#006d32",  # level 2
    "#26a641",  # level 3
    "#39d353",  # level 4
]


def load_data():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_color(level):

    level = max(
        0,
        min(
            int(level),
            4
        )
    )

    return COLORS[level]


def main():

    data = load_data()

    days = data["days"]

    stats = data.get(
        "stats",
        {}
    )

    # ------------------------------------------------
    # Create lookup by date
    # ------------------------------------------------

    day_map = {
        day["date"]: day
        for day in days
    }

    # ------------------------------------------------
    # We need 53 weeks × 7 days
    # ------------------------------------------------

    columns = 53
    rows = 7

    grid_width = (
        columns * CELL_SIZE
        + (columns - 1) * GAP
    )

    grid_height = (
        rows * CELL_SIZE
        + (rows - 1) * GAP
    )

    width = LEFT * 2 + grid_width
    height = 430

    # ------------------------------------------------
    # SVG header
    # ------------------------------------------------

    svg = []

    svg.append(
        f'''<svg
        xmlns="http://www.w3.org/2000/svg"
        width="{width}"
        height="{height}"
        viewBox="0 0 {width} {height}">
        '''
    )

    svg.append(
        f'''
        <rect
            width="100%"
            height="100%"
            rx="22"
            fill="{BACKGROUND}"
        />
        '''
    )

    # ------------------------------------------------
    # Title
    # ------------------------------------------------

    svg.append(
        f'''
        <text
            x="40"
            y="45"
            fill="{TEXT_PRIMARY}"
            font-family="monospace"
            font-size="22"
            font-weight="bold">
            github.com/{escape(USERNAME)}
        </text>
        '''
    )

    svg.append(
        f'''
        <text
            x="40"
            y="75"
            fill="{TEXT_SECONDARY}"
            font-family="monospace"
            font-size="14">
            contribution activity — last year
        </text>
        '''
    )

    # ------------------------------------------------
    # Find dates
    # ------------------------------------------------

    sorted_dates = sorted(
        day_map.keys()
    )

    if not sorted_dates:

        raise RuntimeError(
            "No contribution data found."
        )

    # Use the latest date in the JSON
    latest_date = sorted_dates[-1]

    from datetime import datetime, timedelta

    end_date = datetime.strptime(
        latest_date,
        "%Y-%m-%d"
    ).date()

    # Move forward to Saturday
    while end_date.weekday() != 5:
        end_date += timedelta(days=1)

    start_date = (
        end_date
        - timedelta(days=7 * 52 + 6)
    )

    # ------------------------------------------------
    # Draw contribution squares
    # ------------------------------------------------

    for column in range(columns):

        for row in range(rows):

            current_date = (
                start_date
                + timedelta(
                    days=column * 7 + row
                )
            )

            date_string = (
                current_date.isoformat()
            )

            day = day_map.get(
                date_string,
                {
                    "count": 0,
                    "level": 0
                }
            )

            level = day.get(
                "level",
                0
            )

            count = day.get(
                "count",
                0
            )

            x = (
                LEFT
                + column * (
                    CELL_SIZE + GAP
                )
            )

            y = (
                TOP
                + row * (
                    CELL_SIZE + GAP
                )
            )

            color = get_color(level)

            # ------------------------------------------------
            # Animated square
            # ------------------------------------------------

            delay = (
                column * 0.025
                + row * 0.01
            )

            svg.append(
                f'''
                <rect
                    x="{x}"
                    y="{y}"
                    width="{CELL_SIZE}"
                    height="{CELL_SIZE}"
                    rx="3"
                    fill="{color}"
                    opacity="0">

                    <title>
                        {count} contributions on {date_string}
                    </title>

                    <animate
                        attributeName="opacity"
                        from="0"
                        to="1"
                        dur="0.35s"
                        begin="{delay:.2f}s"
                        fill="freeze"
                    />

                </rect>
                '''
            )

    # ------------------------------------------------
    # Legend
    # ------------------------------------------------

    legend_y = 350

    svg.append(
        f'''
        <text
            x="40"
            y="{legend_y}"
            fill="{TEXT_SECONDARY}"
            font-family="monospace"
            font-size="14">
            Less
        </text>
        '''
    )

    legend_x = 120

    for i, color in enumerate(COLORS):

        x = (
            legend_x
            + i * 32
        )

        svg.append(
            f'''
            <rect
                x="{x}"
                y="{legend_y - 14}"
                width="26"
                height="26"
                rx="5"
                fill="{color}"
            />
            '''
        )

    svg.append(
        f'''
        <text
            x="{legend_x + 168}"
            y="{legend_y}"
            fill="{TEXT_SECONDARY}"
            font-family="monospace"
            font-size="14">
            More
        </text>
        '''
    )

    # ------------------------------------------------
    # Statistics
    # ------------------------------------------------

    total = stats.get(
        "total",
        sum(
            day["count"]
            for day in days
        )
    )

    current_streak = stats.get(
        "current_streak",
        0
    )

    longest_streak = stats.get(
        "longest_streak",
        0
    )

    svg.append(
        f'''
        <text
            x="40"
            y="410"
            fill="{TEXT_SECONDARY}"
            font-family="monospace"
            font-size="15">

            {total} contributions
            • {current_streak} day current streak
            • {longest_streak} day longest streak

        </text>
        '''
    )

    svg.append("</svg>")

    # ------------------------------------------------
    # Save SVG
    # ------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(svg)
        )

    print()
    print("Heatmap generated successfully!")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Total contributions: {total}")
    print()


if __name__ == "__main__":
    main()