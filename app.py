import streamlit as st

from src.preprocessing import load_data
from src.user import get_random_movies, create_user_profile
from src.similarity import calculate_new_user_similarity
from src.recommend import recommend_movies_for_new_user
from src.tmdb import get_poster_url


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide"
)
st.markdown("""
<style>

.movie-title {
    font-size: 15px;
    font-weight: 600;
    line-height: 1.3;
    margin-top: 8px;
}

.movie-genre {
    font-size: 12px;
    color: #999;
    line-height: 1.3;
    margin-top: 4px;
}

/* 영화 가로 스크롤 */
.st-key-movie-row > div {
    overflow-x: auto !important;
    overflow-y: hidden !important;
}

.st-key-movie-row [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    gap: 16px !important;
    padding-bottom: 12px;
}

.st-key-movie-row [data-testid="stHorizontalBlock"] > div {
    flex: 0 0 150px !important;
    min-width: 150px !important;
    max-width: 150px !important;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("CineMatch")

st.markdown(
    """
    CineMatch

    Discover your next favorite movie.

    Rate the movies you've seen.
    We'll find movies that match your taste.
    """
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

ratings, movies, tags, links = load_data()


# --------------------------------------------------
# Select movies
# --------------------------------------------------

if (
    "sample_movies" not in st.session_state
    or "poster_url" not in st.session_state.sample_movies.columns
):
    
    sample_movies = get_random_movies(
        movies,
        ratings,
        n=10
    ).copy()

    sample_movies["tmdbId"] = (
        sample_movies["movieId"]
        .map(
            links.set_index("movieId")["tmdbId"]
        )
    )

    sample_movies["poster_url"] = (
        sample_movies["tmdbId"]
        .apply(get_poster_url)
    )

    st.session_state.sample_movies = sample_movies

sample_movies = st.session_state.sample_movies


st.divider()

st.subheader("MOVIE TASTE PROFILE")


# --------------------------------------------------
# Rating input
# --------------------------------------------------

user_ratings = {}

with st.container(
    horizontal=True,
    horizontal_alignment="left",
    gap="small",
    key="movie-row"
):

    for _, movie in sample_movies.iterrows():

        with st.container(width=150):

            if movie["poster_url"]:
                st.image(
                    movie["poster_url"],
                    width=150
                )

            st.markdown(
                f"""
                <div class="movie-title">
                    {movie['title']}
                </div>

                <div class="movie-genre">
                    {movie['genres'].replace("|", " · ")}
                </div>
                """,
                unsafe_allow_html=True
            )

            rating = st.selectbox(
                "평점",
                ["안 봤어요", 1, 2, 3, 4, 5],
                key=f"rating_{movie['movieId']}",
                label_visibility="collapsed"
            )

            user_ratings[movie["movieId"]] = rating


# --------------------------------------------------
# Recommendation button
# --------------------------------------------------

if st.button(
    "Find My Matches →",
    type="primary",
    use_container_width=True
):

    user_profile = create_user_profile(
        sample_movies,
        user_ratings
    )

    similarities = calculate_new_user_similarity(
        user_profile,
        ratings
    )

    recommendations = recommend_movies_for_new_user(
        user_profile=user_profile,
        ratings=ratings,
        similarities=similarities,
        movies=movies,
        links=links,
        top_n=10,
        neighbor_k=5,
        threshold=3.5
    )


    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    st.divider()

    st.subheader("YOUR PICKS")

    st.markdown("### YOUR RECOMMENDATIONS")

    st.write(
        "Movies picked for you"
    )

    st.markdown('<div class="movie-row">', unsafe_allow_html=True)

    with st.container(
        horizontal=True,
        horizontal_alignment="left",
        gap="small",
        key="recommendation-row"
    ):

        for _, movie in recommendations.iterrows():

            with st.container(width=150):

                if movie["poster_url"]:
                    st.image(
                        movie["poster_url"],
                        width=150
                    )

                st.markdown(
                    f"""
                    <div class="movie-title">
                        {movie['title']}
                    </div>

                    <div class="movie-genre">
                        {movie['genres'].replace("|", " · ")}
                    </div>

                    <div style="margin-top: 6px;">
                        ⭐ {movie['predicted_rating']:.2f}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    st.markdown('</div>', unsafe_allow_html=True)
        


    # --------------------------------------------------
    # Detailed information
    # --------------------------------------------------

    with st.expander("추천 시스템 상세 정보"):

        st.subheader("🔎 유사 사용자")

        st.dataframe(
            similarities.head(10),
            use_container_width=True
        )

        st.subheader("🎯 사용자 프로필")

        st.dataframe(
            user_profile,
            use_container_width=True
        )