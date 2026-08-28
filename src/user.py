import numpy as np

def get_random_movies(movies, ratings, n=10, min_ratings=50):

    rating_counts = (
        ratings.groupby("movieId")
        .size()
        .reset_index(name="rating_count")
    )

    popular_movies = rating_counts[
        rating_counts["rating_count"] >= min_ratings
    ]

    candidate_movies = movies[
        movies["movieId"].isin(popular_movies["movieId"])
    ]

    #실제 존재하는 개수만큼만 뽑도록 제한
    sample_size = min(n, len(candidate_movies))

    return candidate_movies.sample(n=sample_size)


def create_user_profile(sample_movies, user_ratings):

    profile = sample_movies[["movieId", "title"]].copy()

    profile["rating"] = profile["movieId"].map(user_ratings)

    profile["rating"] = profile["rating"].replace(
        "안 봤어요",
        np.nan
    )

    return profile