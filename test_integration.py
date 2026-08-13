from src.preprocessing import (
    load_data,
    create_user_movie_matrix
)

from src.similarity import (
    calculate_user_similarity,
    find_similar_users
)

from src.recommend import recommend_movies

from src.evaluation import (
    split_train_test,
    evaluate_precision_at_k
)


print("========== 1. 데이터 로드 ==========")

ratings, movies, tags, links = load_data()

print("ratings:", ratings.shape)
print("movies:", movies.shape)
print("tags:", tags.shape)
print("links:", links.shape)


print("\n========== 2. Train / Test 분리 ==========")

train_movie_data, test_movie_data = split_train_test(
    ratings,
    test_size=0.2,
    random_state=42
)

print("train:", train_movie_data.shape)
print("test :", test_movie_data.shape)


print("\n========== 3. User-Movie Matrix 생성 ==========")

user_movie_matrix, user_movie_matrix_filled = \
    create_user_movie_matrix(train_movie_data)

print("matrix:", user_movie_matrix.shape)
print("filled:", user_movie_matrix_filled.shape)


print("\n========== 4. Cosine Similarity 계산 ==========")

user_similarity_df = calculate_user_similarity(
    user_movie_matrix_filled
)

print("similarity:", user_similarity_df.shape)


print("\n========== 5. 유사 사용자 확인 ==========")

user_id = 1

similar_users = find_similar_users(
    user_similarity_df,
    user_id,
    top_k=5
)

print(similar_users)


print("\n========== 6. 추천 결과 생성 ==========")

recommendations = recommend_movies(
    user_id=user_id,
    train_movie_data=train_movie_data,
    user_similarity_df=user_similarity_df,
    movies=movies,
    top_n=10,
    neighbor_k=5,
    threshold=3.5
)

print(recommendations)


print("\n========== 7. Precision@K ==========")

precision = evaluate_precision_at_k(
    test_movie_data=test_movie_data,
    train_movie_data=train_movie_data,
    user_similarity_df=user_similarity_df,
    movies=movies,
    top_k=10,
    threshold=3.5,
    neighbor_k=5
)

print(f"Precision@10: {precision:.4f}")


print("\n========== 통합 테스트 완료 ==========")