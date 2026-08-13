from .similarity import find_similar_users
from src.tmdb import get_poster_url

#유사 사용자들의 평점 가져오기
def get_similar_ratings(ratings, top_similar_users):
    similar_ratings = ratings [
    ratings['userId'].isin(top_similar_users)
]

    return similar_ratings

#사용자가 본 영화 가져오기
def get_watched_movies(ratings, user_id):
    watched_movies = ratings[
        ratings['userId'] == user_id
    ]['movieId']

    return watched_movies

#이미 본 영화 제거
def get_candidate_movies(similar_ratings, watched_movies):
    candidate_movies = similar_ratings[
        ~similar_ratings['movieId'].isin(watched_movies)
    ]

    return candidate_movies

#유사도 추가
def add_similarity(candidate_movies, similar_users):
    candidate_movies = candidate_movies.copy()

    candidate_movies['similarity'] = candidate_movies['userId'].map(
        similar_users)

    return candidate_movies


#가중평균 계산
def weighted_average(group):
    return(
        (group['rating'] * group['similarity']).sum() 
        / group['similarity'].sum()
    )

#영화 추천
def recommend_movies(
        user_id,
        train_movie_data,
        user_similarity_df,
        movies,
        links,
        top_n=10,
        neighbor_k=10,
        threshold=0
):
    #유사 사용자 찾기
    similar_users = find_similar_users(
        user_similarity_df,
        user_id,
        top_k=neighbor_k
    )

    #유사 사용자들의 평점 가져오기
    similar_ratings = get_similar_ratings(
        train_movie_data,
        similar_users.index
    )

    #Threshold 적용
    similar_ratings = similar_ratings[
        similar_ratings['rating'] >= threshold
    ]

    #사용자가 이미 본 영화
    watched_movies = get_watched_movies(
        train_movie_data,
        user_id
    )

    #이미 본 영화 제거
    candidate_movies = get_candidate_movies(
        similar_ratings,
        watched_movies
    )

    #유사도 추가
    candidate_movies = add_similarity(
        candidate_movies,
        similar_users
    )

    #예상 평점 계산
    predicted_ratings = (
        candidate_movies
        .groupby('movieId')
        .apply(weighted_average)
        .sort_values(ascending=False)
    )

    #추천 결과 생성
    recommendations = (
        predicted_ratings
        .reset_index(name="predicted_rating")
        .merge(movies, on="movieId")
        .merge(
            links[["movieId", "tmdbId"]],
            on="movieId",
            how="left"
        )
        .sort_values(
            by="predicted_rating",
            ascending=False
        )
    )

    recommendations["poster_url"] = (
        recommendations["tmdbId"]
        .apply(get_poster_url)
    )

    recommendations = recommendations[
        ["title", "genres", "predicted_rating", "poster_url"]
    ]

    return recommendations.head(top_n)
    
def recommend_movies_for_new_user(
    user_profile,
    ratings,
    similarities,
    links,
    movies,
    top_n=10,
    neighbor_k=5,
    threshold=3.5
):
    """
    새로운 사용자의 영화 평점을 기반으로 영화를 추천한다.

    user_profile:
        새로운 사용자의 평점 정보
        movieId, title, rating

    ratings:
        기존 사용자들의 전체 평점 데이터

    similarities:
        새로운 사용자와 기존 사용자 간 similarity
        index = userId
    """

    # 1. 가장 유사한 사용자 Top K 선택
    similar_users = similarities.head(neighbor_k)

    # 2. 유사 사용자들의 평점 가져오기
    similar_ratings = get_similar_ratings(
        ratings,
        similar_users.index
    )

    # 3. Threshold 적용
    similar_ratings = similar_ratings[
        similar_ratings["rating"] >= threshold
    ]

    # 최소 3명의 유사 사용자가 평가한 영화만 후보로 사용
    movie_user_counts = (
        similar_ratings
        .groupby("movieId")["userId"]
        .nunique()
    )

    valid_movies = movie_user_counts[
        movie_user_counts >= 3
    ].index

    similar_ratings = similar_ratings[
        similar_ratings["movieId"].isin(valid_movies)
    ]

    # 4. 새로운 사용자가 이미 평가한 영화
    watched_movies = user_profile.dropna(
        subset=["rating"]
    )["movieId"]

    # 5. 이미 평가한 영화 제거
    candidate_movies = get_candidate_movies(
        similar_ratings,
        watched_movies
    )

    # 6. 유사도 추가
    candidate_movies = add_similarity(
        candidate_movies,
        similar_users
    )

    # 7. 예상 평점 계산
    predicted_ratings = (
        candidate_movies
        .groupby("movieId")
        .apply(weighted_average)
        .sort_values(ascending=False)
    )

    # 8. 영화 정보와 결합
    recommendations = (
        predicted_ratings
        .reset_index(name="predicted_rating")
        .merge(movies, on="movieId")
        .merge(
            links[["movieId", "tmdbId"]],
            on="movieId",
            how="left"
        )
        .sort_values(
            by="predicted_rating",
            ascending=False
        )
    )

    recommendations["poster_url"] = (
        recommendations["tmdbId"].apply(get_poster_url)
    )

    recommendations = recommendations[
        ["title", "genres", "predicted_rating", "poster_url"]
    ]

    return recommendations.head(top_n)

