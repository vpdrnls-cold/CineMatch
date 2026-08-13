from sklearn.model_selection import train_test_split
import pandas as pd

from .recommend import recommend_movies

#training set과 test set 나누기
def split_train_test(movie_data, test_size=0.2, random_state=42):
    train_list = []
    test_list = []

    for user_id, group in movie_data.groupby('userId'):
        train, test = train_test_split(
            group, 
            test_size=test_size, 
            random_state=random_state
        )
        train_list.append(train)
        test_list.append(test)

    train_movie_data = pd.concat(train_list)
    test_movie_data = pd.concat(test_list)

    return train_movie_data, test_movie_data

#실제로 좋아한 영화 가져오기
def get_actual_movies(test_movie_data, user_id, threshold, movies):
    actual_movies = test_movie_data[
        (test_movie_data['userId'] == user_id) & 
        (test_movie_data['rating'] >= threshold)
    ].merge(
        movies,
        on="movieId"
    )
    return actual_movies

#Precision@k 계산
def precision_at_k(recommended_movies, actual_movies, top_k):
    #영화제목만 추출
    recommended_titles = set(
        recommended_movies["title"]
    )

    #실제 좋아한 영화 제목 추출
    actual_titles = set(
        actual_movies["title"]
    )

    #추천영화와 실제 좋아한 영화의 교집합
    hits = recommended_titles & actual_titles

    #Precision 계산
    precision = len(hits) / top_k

    return precision

#전체 사용자에 대한 평균 Precision@K 계산
def evaluate_precision_at_k(
        test_movie_data,
        train_movie_data,
        user_similarity_df,
        movies,
        top_k=10,
        threshold=4.0,
        neighbor_k=5
):

    test_users = test_movie_data["userId"].unique()

    precision_scores = []

    for user_id in test_users:

        #추천 영화 생성
        recommendations = recommend_movies(
            user_id = user_id,
            train_movie_data=train_movie_data,
            user_similarity_df=user_similarity_df,
            movies=movies,
            links=links,
            top_n = top_k,
            neighbor_k = neighbor_k,
            threshold = threshold
        )

        #실제 좋아한 영화
        actual_movies = get_actual_movies(
            test_movie_data,
            user_id,
            threshold,
            movies
        )
        
        #Precision@K 계산
        precision = precision_at_k(
            recommendations,
            actual_movies,
            top_k=top_k
        )

        precision_scores.append(precision)

    #전체 사용자 평균 Precision@K 
    mean_precision = sum(precision_scores) / len(precision_scores)

    return mean_precision