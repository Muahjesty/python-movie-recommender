#!/usr/bin/env python3
"""
movie_recommender.py

A command-line movie recommendation system built for Python 3.12.
It loads a movies file and a ratings file, computes popularity metrics,
and recommends movies based on a user's preferred genre.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

MovieRecord = dict
RatingRecord = dict


def normalize_text(value: str) -> str:
    """Return a normalized version of text for case-insensitive matching."""
    return value.strip().casefold()


def safe_float(value: str) -> Optional[float]:
    """Convert a string to float, returning None if conversion fails."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_movies(file_path: str) -> Tuple[Dict[str, MovieRecord], List[str]]:
    """
    Load movies from a pipe-delimited file.

    Expected format per line:
    movie_genre|movie_id|movie_name

    Returns:
        A tuple containing:
        - A dictionary keyed by normalized movie name.
        - A list of warnings for skipped or corrected rows.
    """
    movies: Dict[str, MovieRecord] = {}
    warnings: List[str] = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                warnings.append(f"movies line {line_number}: skipped blank line")
                continue

            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 3:
                warnings.append(
                    f"movies line {line_number}: expected 3 fields, found {len(parts)}"
                )
                continue

            genre, movie_id, movie_name = parts
            if not genre or not movie_id or not movie_name:
                warnings.append(f"movies line {line_number}: missing required field")
                continue

            normalized_name = normalize_text(movie_name)
            if normalized_name in movies:
                warnings.append(
                    f"movies line {line_number}: duplicate movie name '{movie_name}' skipped"
                )
                continue

            movies[normalized_name] = {
                "genre": genre,
                "movie_id": movie_id,
                "name": movie_name,
                "normalized_name": normalized_name,
            }

    return movies, warnings


def load_ratings(
    file_path: str, movies: Dict[str, MovieRecord]
) -> Tuple[List[RatingRecord], List[str]]:
    """
    Load ratings from a pipe-delimited file.

    Expected format per line:
    movie_name|rating|user_id

    Rows referencing movies not present in the loaded movies dictionary
    are skipped. Ratings must be in the inclusive range [0, 5].

    Returns:
        A tuple containing:
        - A list of validated rating records.
        - A list of warnings for skipped rows.
    """
    ratings: List[RatingRecord] = []
    warnings: List[str] = []
    seen_user_movie_pairs: set[Tuple[str, str]] = set()

    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                warnings.append(f"ratings line {line_number}: skipped blank line")
                continue

            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 3:
                warnings.append(
                    f"ratings line {line_number}: expected 3 fields, found {len(parts)}"
                )
                continue

            movie_name, rating_text, user_id = parts
            if not movie_name or not rating_text or not user_id:
                warnings.append(f"ratings line {line_number}: missing required field")
                continue

            normalized_name = normalize_text(movie_name)
            if normalized_name not in movies:
                warnings.append(
                    f"ratings line {line_number}: unknown movie '{movie_name}' skipped"
                )
                continue

            rating_value = safe_float(rating_text)
            if rating_value is None:
                warnings.append(
                    f"ratings line {line_number}: invalid rating '{rating_text}' skipped"
                )
                continue

            if not (0 <= rating_value <= 5):
                warnings.append(
                    f"ratings line {line_number}: rating {rating_value} out of range skipped"
                )
                continue

            pair = (normalize_text(user_id), normalized_name)
            if pair in seen_user_movie_pairs:
                warnings.append(
                    f"ratings line {line_number}: duplicate rating by user '{user_id}' for '{movie_name}' skipped"
                )
                continue
            seen_user_movie_pairs.add(pair)

            ratings.append(
                {
                    "movie_name": movies[normalized_name]["name"],
                    "normalized_name": normalized_name,
                    "rating": rating_value,
                    "user_id": user_id.strip(),
                    "normalized_user_id": normalize_text(user_id),
                    "genre": movies[normalized_name]["genre"],
                }
            )

    return ratings, warnings


def compute_movie_average_ratings(
    movies: Dict[str, MovieRecord], ratings: List[RatingRecord]
) -> Dict[str, float]:
    """
    Compute the average rating for each movie that has at least one rating.

    Returns:
        A dictionary mapping normalized movie names to average rating values.
    """
    totals: Dict[str, float] = defaultdict(float)
    counts: Dict[str, int] = defaultdict(int)

    for rating in ratings:
        normalized_name = rating["normalized_name"]
        totals[normalized_name] += rating["rating"]
        counts[normalized_name] += 1

    return {
        normalized_name: totals[normalized_name] / counts[normalized_name]
        for normalized_name in counts
        if normalized_name in movies
    }


def sort_movie_names_by_average(
    movies: Dict[str, MovieRecord],
    average_ratings: Dict[str, float],
    names: Iterable[str],
) -> List[str]:
    """
    Sort movie names by descending average rating, then alphabetically by title.

    Returns:
        A list of normalized movie names in sorted order.
    """
    return sorted(
        names,
        key=lambda name: (-average_ratings[name], movies[name]["name"].casefold()),
    )


def get_top_n_movies(
    movies: Dict[str, MovieRecord], ratings: List[RatingRecord], n: int
) -> List[Tuple[str, float]]:
    """
    Return the top n movies ranked by average rating.

    Movies without any ratings are excluded.
    """
    if n <= 0:
        return []

    averages = compute_movie_average_ratings(movies, ratings)
    ordered_names = sort_movie_names_by_average(movies, averages, averages.keys())

    return [(movies[name]["name"], averages[name]) for name in ordered_names[:n]]


def get_top_n_movies_by_genre(
    movies: Dict[str, MovieRecord], ratings: List[RatingRecord], genre: str, n: int
) -> List[Tuple[str, float]]:
    """
    Return the top n movies in the given genre ranked by average rating.

    Genre matching is case-insensitive.
    """
    if n <= 0:
        return []

    target_genre = normalize_text(genre)
    averages = compute_movie_average_ratings(movies, ratings)

    matching_names = [
        normalized_name
        for normalized_name, movie in movies.items()
        if normalize_text(movie["genre"]) == target_genre and normalized_name in averages
    ]
    ordered_names = sort_movie_names_by_average(movies, averages, matching_names)

    return [(movies[name]["name"], averages[name]) for name in ordered_names[:n]]


def get_top_n_genres(
    movies: Dict[str, MovieRecord], ratings: List[RatingRecord], n: int
) -> List[Tuple[str, float]]:
    """
    Return the top n genres ranked by average of movie average ratings.

    A movie contributes to its genre only if that movie has at least one rating.
    """
    if n <= 0:
        return []

    movie_averages = compute_movie_average_ratings(movies, ratings)
    genre_totals: Dict[str, float] = defaultdict(float)
    genre_counts: Dict[str, int] = defaultdict(int)
    canonical_genre_names: Dict[str, str] = {}

    for normalized_name, average in movie_averages.items():
        genre = movies[normalized_name]["genre"]
        normalized_genre = normalize_text(genre)
        genre_totals[normalized_genre] += average
        genre_counts[normalized_genre] += 1
        canonical_genre_names.setdefault(normalized_genre, genre)

    ranked = sorted(
        (
            (
                canonical_genre_names[normalized_genre],
                genre_totals[normalized_genre] / genre_counts[normalized_genre],
            )
            for normalized_genre in genre_counts
        ),
        key=lambda item: (-item[1], item[0].casefold()),
    )
    return ranked[:n]


def get_user_preferred_genre(
    ratings: List[RatingRecord], user_id: str
) -> Optional[Tuple[str, float]]:
    """
    Return the user's preferred genre based on the average of the user's ratings in each genre.

    User id matching is case-insensitive.
    Returns None if the user has no ratings.
    """
    target_user = normalize_text(user_id)
    genre_totals: Dict[str, float] = defaultdict(float)
    genre_counts: Dict[str, int] = defaultdict(int)
    canonical_genre_names: Dict[str, str] = {}

    for rating in ratings:
        if rating["normalized_user_id"] != target_user:
            continue
        genre = rating["genre"]
        normalized_genre = normalize_text(genre)
        genre_totals[normalized_genre] += rating["rating"]
        genre_counts[normalized_genre] += 1
        canonical_genre_names.setdefault(normalized_genre, genre)

    if not genre_counts:
        return None

    ranked = sorted(
        (
            (
                canonical_genre_names[normalized_genre],
                genre_totals[normalized_genre] / genre_counts[normalized_genre],
            )
            for normalized_genre in genre_counts
        ),
        key=lambda item: (-item[1], item[0].casefold()),
    )
    return ranked[0]


def recommend_movies_for_user(
    movies: Dict[str, MovieRecord], ratings: List[RatingRecord], user_id: str
) -> List[Tuple[str, float]]:
    """
    Recommend up to 3 movies from the user's top genre that the user has not rated.

    Recommendations are ranked by overall movie average rating.
    """
    preferred = get_user_preferred_genre(ratings, user_id)
    if preferred is None:
        return []

    preferred_genre = preferred[0]
    target_user = normalize_text(user_id)
    rated_movies = {
        rating["normalized_name"]
        for rating in ratings
        if rating["normalized_user_id"] == target_user
    }

    top_movies_in_genre = get_top_n_movies_by_genre(
        movies, ratings, preferred_genre, n=len(movies)
    )

    recommendations: List[Tuple[str, float]] = []
    for movie_name, average_rating in top_movies_in_genre:
        normalized_name = normalize_text(movie_name)
        if normalized_name not in rated_movies:
            recommendations.append((movie_name, average_rating))
        if len(recommendations) == 3:
            break

    return recommendations


def print_ranked_items(items: List[Tuple[str, float]], label: str) -> None:
    """Print a ranked list of items with numeric scores."""
    if not items:
        print(f"No {label} found.")
        return

    for index, (name, value) in enumerate(items, start=1):
        print(f"{index}. {name} - {value:.2f}")


def print_warnings(warnings: List[str]) -> None:
    """Print parser warnings if any were generated."""
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("\nNo input warnings.")


def prompt_int(message: str) -> int:
    """Prompt until the user enters a valid integer."""
    while True:
        raw_value = input(message).strip()
        try:
            return int(raw_value)
        except ValueError:
            print("Please enter a valid integer.")


def main() -> None:
    """Run the command-line interface for the movie recommender."""
    movies: Dict[str, MovieRecord] = {}
    ratings: List[RatingRecord] = []
    movie_warnings: List[str] = []
    rating_warnings: List[str] = []

    while True:
        print("\nMovie Recommendation System")
        print("1. Load movies file")
        print("2. Load ratings file")
        print("3. Show top n movies")
        print("4. Show top n movies in a genre")
        print("5. Show top n genres")
        print("6. Show user's preferred genre")
        print("7. Recommend movies for user")
        print("8. Show input warnings")
        print("9. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            file_path = input("Enter movies file path: ").strip()
            try:
                movies, movie_warnings = load_movies(file_path)
                print(f"Loaded {len(movies)} movies.")
            except FileNotFoundError:
                print("Movies file not found.")
        elif choice == "2":
            if not movies:
                print("Load the movies file first.")
                continue
            file_path = input("Enter ratings file path: ").strip()
            try:
                ratings, rating_warnings = load_ratings(file_path, movies)
                print(f"Loaded {len(ratings)} ratings.")
            except FileNotFoundError:
                print("Ratings file not found.")
        elif choice == "3":
            if not movies or not ratings:
                print("Load both movies and ratings first.")
                continue
            n = prompt_int("Enter n: ")
            print_ranked_items(get_top_n_movies(movies, ratings, n), "movies")
        elif choice == "4":
            if not movies or not ratings:
                print("Load both movies and ratings first.")
                continue
            genre = input("Enter genre: ").strip()
            n = prompt_int("Enter n: ")
            print_ranked_items(
                get_top_n_movies_by_genre(movies, ratings, genre, n), "movies"
            )
        elif choice == "5":
            if not movies or not ratings:
                print("Load both movies and ratings first.")
                continue
            n = prompt_int("Enter n: ")
            print_ranked_items(get_top_n_genres(movies, ratings, n), "genres")
        elif choice == "6":
            if not ratings:
                print("Load ratings first.")
                continue
            user_id = input("Enter user id: ").strip()
            preferred = get_user_preferred_genre(ratings, user_id)
            if preferred is None:
                print("User has no ratings.")
            else:
                genre, average = preferred
                print(f"Preferred genre: {genre} - {average:.2f}")
        elif choice == "7":
            if not movies or not ratings:
                print("Load both movies and ratings first.")
                continue
            user_id = input("Enter user id: ").strip()
            print_ranked_items(
                recommend_movies_for_user(movies, ratings, user_id), "recommendations"
            )
        elif choice == "8":
            print_warnings(movie_warnings + rating_warnings)
        elif choice == "9":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
