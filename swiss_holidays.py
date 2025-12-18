"""
Swiss cantonal holidays for Valais and Zurich.
Hard-coded for 2025-2026; extend as needed.

Each entry: (month, day, name)
"""

VALAIS_HOLIDAYS = {
    2025: [
        (1, 1, "New Year"),
        (1, 2, "Berchtold's Day"),
        (4, 18, "Good Friday"),
        (4, 21, "Easter Monday"),
        (5, 1, "Labour Day"),
        (5, 29, "Ascension"),
        (6, 9, "Whit Monday"),
        (8, 15, "Assumption"),
        (11, 1, "All Saints"),
        (12, 25, "Christmas"),
        (12, 26, "Boxing Day"),
    ],
    2026: [
        (1, 1, "New Year"),
        (1, 2, "Berchtold's Day"),
        (4, 3, "Good Friday"),
        (4, 6, "Easter Monday"),
        (5, 1, "Labour Day"),
        (5, 14, "Ascension"),
        (5, 25, "Whit Monday"),
        (8, 15, "Assumption"),
        (11, 1, "All Saints"),
        (12, 25, "Christmas"),
        (12, 26, "Boxing Day"),
    ],
}

ZURICH_HOLIDAYS = {
    2025: [
        (1, 1, "New Year"),
        (1, 2, "Berchtold's Day"),
        (4, 18, "Good Friday"),
        (4, 21, "Easter Monday"),
        (5, 1, "Labour Day"),
        (5, 29, "Ascension"),
        (6, 9, "Whit Monday"),
        (8, 1, "Swiss National Day"),
        (12, 25, "Christmas"),
        (12, 26, "Boxing Day"),
    ],
    2026: [
        (1, 1, "New Year"),
        (1, 2, "Berchtold's Day"),
        (4, 3, "Good Friday"),
        (4, 6, "Easter Monday"),
        (5, 1, "Labour Day"),
        (5, 14, "Ascension"),
        (5, 25, "Whit Monday"),
        (8, 1, "Swiss National Day"),
        (12, 25, "Christmas"),
        (12, 26, "Boxing Day"),
    ],
}

CANTONS = {
    "valais": VALAIS_HOLIDAYS,
    "zurich": ZURICH_HOLIDAYS,
}


def get_holidays_for_canton_year(canton: str, year: int) -> list[tuple[int, int, str]]:
    """Return list of (month, day, name) for a canton and year."""
    canton_lower = canton.lower().strip()
    if canton_lower not in CANTONS:
        return []
    return CANTONS[canton_lower].get(year, [])


def is_holiday(canton: str, year: int, month: int, day: int) -> bool:
    """Check if a specific date is a holiday for a canton."""
    holidays = get_holidays_for_canton_year(canton, year)
    return (month, day) in [(m, d) for m, d, _ in holidays]
