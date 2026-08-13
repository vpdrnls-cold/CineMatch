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

.movie-card {
    height: 150px;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    background-color: rgba(255,255,255,0.03);
    margin-bottom: 8px;
    box-sizing: border-box;
}

.movie-title {
    height: 52px; 
    font-size: 17px;
    font-weight: 600;
    line-height: 1.5;
    overflow: hidden;

.movie-genre {
    height: 38px;
    font-size: 13px;
    color: #999;
    line-height: 1.4;
    overflow: hidden;
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

cols = st.columns(5)

for i, (_, movie) in enumerate(sample_movies.iterrows()):

    with cols[i % 5]:

        if movie["poster_url"]:
            st.image(
                movie["poster_url"],
                use_container_width=True
            )

        st.markdown(
            f"""
<div class="movie-card">
    <div class="movie-title">
        {movie['title']}
    </div>
    <div class="movie-genre">
        {movie['genres'].replace("|", " · ")}
    </div>
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



st.divider()


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


    for _, movie in recommendations.iterrows():

        col1, col2 = st.columns([1, 3])

        with col1:
            if movie["poster_url"]:
                st.image(
                    movie["poster_url"],
                    use_container_width=True
                )

        with col2:
            st.markdown(
                f"""
                **{movie['title']}**

                {movie['genres']}  

                예상 평점 ⭐ **{movie['predicted_rating']:.2f}**
                """
            )

        st.divider()


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