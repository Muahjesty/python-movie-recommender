#!/usr/bin/env python3
"""
test_movie_recommender.py

Automatic test driver for movie_recommender.py.
It creates temporary input files, loads them, calls each required function,
prints actual results beside expected results, and reports pass/fail.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from movie_recommender import (
    get_top_n_genres,
    get_top_n_movies,
    get_top_n_movies_by_genre,
    get_user_preferred_genre,
    load_movies,
    load_ratings,
    recommend_movies_for_user,
)


MOVIES_DATA = """\
Action|1|Alpha (2020)
Action|2|Bravo (2021)
Comedy|3|Charlie (2019)
Comedy|4|Delta (2018)
Drama|5|Echo (2017)
Action|6|Foxtrot (2016)
Drama|7|Gamma (2015)
Action||Missing ID Movie
Badly formatted row
Action|8|Alpha (2020)
"""

RATINGS_DATA = """\
Alpha (2020)|4.0|u1
Alpha (2020)|5.0|u2
Bravo (2021)|5.0|u1
Bravo (2021)|4.0|u3
Charlie (2019)|2.0|u1
Charlie (2019)|4.0|u2
Delta (2018)|3.0|u2
Delta (2018)|4.0|u4
Echo (2017)|5.0|u3
Echo (2017)|4.0|u4
Foxtrot (2016)|4.5|u5
Gamma (2015)|1.0|u2
Unknown (2020)|5|u1
Alpha (2020)|bad|u9
Bravo (2021)|7|u8
Alpha (2020)|4.0|u1
Incomplete line
"""

EXPECTED_TOP_MOVIES = [
    ("Alpha (2020)", 4.5),
    ("Bravo (2021)", 4.5),
    ("Echo (2017)", 4.5),
]
EXPECTED_TOP_ACTION = [
    ("Alpha (2020)", 4.5),
    ("Bravo (2021)", 4.5),
    ("Foxtrot (2016)", 4.5),
]
EXPECTED_TOP_GENRES = [
    ("Action", 4.5),
    ("Drama", 2.75),
    ("Comedy", 3.25),
]
# Correct sorted order by descending value: Action 4.5, Comedy 3.25, Drama 2.75
EXPECTED_TOP_GENRES = [
    ("Action", 4.5),
    ("Comedy", 3.25),
    ("Drama", 2.75),
]
EXPECTED_USER_PREF = ("Action", 4.5)
EXPECTED_RECS_U1 = [("Foxtrot (2016)", 4.5)]


def write_temp_file(directory: Path, filename: str, content: str) -> Path:
    """Write content to a temporary file and return its path."""
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    return path


def compare(label: str, actual, expected) -> bool:
    """Print a comparison and return whether it passed."""
    passed = actual == expected
    status = "PASS" if passed else "FAIL"
    print(f"\n{label}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Result:   {status}")
    return passed


def main() -> None:
    """Create test files, execute tests, and summarize results."""
    passed = 0
    total = 0

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        movies_path = write_temp_file(temp_dir, "movies.txt", MOVIES_DATA)
        ratings_path = write_temp_file(temp_dir, "ratings.txt", RATINGS_DATA)

        movies, movie_warnings = load_movies(str(movies_path))
        ratings, rating_warnings = load_ratings(str(ratings_path), movies)

        total += 1
        if compare("Loaded movie count", len(movies), 7):
            passed += 1

        total += 1
        if compare("Loaded rating count", len(ratings), 12):
            passed += 1

        total += 1
        if compare("Movie warnings present", len(movie_warnings) >= 3, True):
            passed += 1

        total += 1
        if compare("Rating warnings present", len(rating_warnings) >= 5, True):
            passed += 1

        total += 1
        if compare("Top 3 movies", get_top_n_movies(movies, ratings, 3), EXPECTED_TOP_MOVIES):
            passed += 1

        total += 1
        if compare(
            "Top 3 Action movies",
            get_top_n_movies_by_genre(movies, ratings, "action", 3),
            EXPECTED_TOP_ACTION,
        ):
            passed += 1

        total += 1
        if compare("Top 3 genres", get_top_n_genres(movies, ratings, 3), EXPECTED_TOP_GENRES):
            passed += 1

        total += 1
        if compare(
            "Preferred genre for user u1",
            get_user_preferred_genre(ratings, "U1"),
            EXPECTED_USER_PREF,
        ):
            passed += 1

        total += 1
        if compare(
            "Recommendations for user u1",
            recommend_movies_for_user(movies, ratings, "u1"),
            EXPECTED_RECS_U1,
        ):
            passed += 1

        total += 1
        if compare(
            "Recommendations for unknown user",
            recommend_movies_for_user(movies, ratings, "unknown_user"),
            [],
        ):
            passed += 1

    print(f"\nSummary: passed {passed} of {total} checks.")


if __name__ == "__main__":
    main()
