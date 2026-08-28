import pandas as pd
from pathlib import Path

#프로젝트의 data 폴더 경로
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_data():
    try:
        ratings = pd.read_csv(DATA_DIR / "ratings.csv")
        movies = pd.read_csv(DATA_DIR / "movies.csv")
        tags = pd.read_csv(DATA_DIR / "tags.csv")
        links = pd.read_csv(DATA_DIR / "links.csv")
    except FileNotFoundError as e :
        raise FileNotFoundError(
            f"데이터 파일을 찾을 수 없습니다: {e}. "
            f"'{DATA_DIR}' 경로에 movies.csv, ratings.csv, tags.csv, "
            f"links.csv 파일이 있는지 확인하세요."
        ) from e

    ratings.drop(columns=['timestamp'], inplace=True)

    return ratings, movies, tags, links

def create_user_movie_matrix(train_movie_data):
    user_movie_matrix = train_movie_data.pivot_table(
        index="userId",
        columns="movieId",
        values="rating"
    )

    user_movie_matrix_filled = user_movie_matrix.fillna(0)

    return user_movie_matrix, user_movie_matrix_filled