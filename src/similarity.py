import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

#Cosine similarity 계산 함수
def calculate_user_similarity(user_movie_matrix_filled):
    user_similarity = cosine_similarity(user_movie_matrix_filled)

    user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_movie_matrix_filled.index,
    columns=user_movie_matrix_filled.index
)
    return user_similarity_df

#유사 사용자 찾기
def find_similar_users(user_similarity_df, user_id, top_k=10):
    if user_id not in user_similarity_df.index:
        return pd.Series(dtype=float)
    
    similar_users = (
        user_similarity_df.loc[user_id]
        .drop(user_id)
        .sort_values(ascending=False)
        .head(top_k)
    )

    return similar_users

def calculate_new_user_similarity(
    user_profile,
    ratings,
    min_common_movies=3
):
    # 새로운 사용자와 기존 사용자들의 Cosine Similarity를 계산한다.

    # 공통으로 평가한 영화가 최소 min_common_movies개 이상인
    # 기존 사용자만 유사도 계산에 사용한다.

    # 새로운 사용자가 실제로 평점을 남긴 영화만 사용
    new_user_ratings = user_profile.dropna(subset=["rating"])

    if new_user_ratings.empty:
        return pd.Series(dtype=float)

    # 새로운 사용자의 평점
    new_user_vector = (
        new_user_ratings
        .set_index("movieId")["rating"]
    )

    # 기존 사용자 × movieId 평점 matrix
    existing_matrix = ratings.pivot_table(
        index="userId",
        columns="movieId",
        values="rating"
    )

    similarities = {}

    for user_id, user_ratings in existing_matrix.iterrows():

        # 두 사용자가 공통으로 평가한 영화
        common_movies = new_user_vector.index.intersection(
            user_ratings.dropna().index
        )

        # 공통 영화가 너무 적으면 유사도 계산하지 않음
        if len(common_movies) < min_common_movies:
            continue

        new_vector = new_user_vector.loc[common_movies].values.reshape(1, -1)

        existing_vector = (
            user_ratings.loc[common_movies]
            .values
            .reshape(1, -1)
        )

        similarity = cosine_similarity(
            new_vector,
            existing_vector
        )[0][0]

        similarities[user_id] = similarity

    return pd.Series(similarities).sort_values(
        ascending=False
    )