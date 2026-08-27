import streamlit as st

from src.preprocessing import load_data
from src.user import get_random_movies, create_user_profile
from src.similarity import calculate_new_user_similarity
from src.recommend import recommend_movies_for_new_user
from src.tmdb import get_poster_url


# ==================================================
# Page configuration
# ==================================================

st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide"
)


# ==================================================
# Custom CSS
# ==================================================

st.markdown(
    """
    <style>

    /* ---------------------------------------------
       Movie title
    --------------------------------------------- */

    .movie-title {
        font-size: 15px;
        font-weight: 600;
        line-height: 1.3;
        margin-top: 8px;
        height: 39px;
        overflow: hidden;
    }

    .movie-genre {
        font-size: 12px;
        color: #999;
        line-height: 1.3;
        margin-top: 4px;
        height: 32px;
        overflow: hidden;
    }


    /* ---------------------------------------------
       Movie rows
    --------------------------------------------- */

    .st-key-movie-row,
    .st-key-recommendation-row {

        width: 100% !important;
        max-width: 100% !important;

        overflow-x: auto !important;
        overflow-y: hidden !important;

        padding-bottom: 15px;
    }


    .st-key-movie-row > div,
    .st-key-recommendation-row > div {

        display: flex !important;

        flex-wrap: nowrap !important;

        width: max-content !important;
        max-width: none !important;

        gap: 16px !important;
    }


    .st-key-movie-row [data-testid="stHorizontalBlock"],
    .st-key-recommendation-row [data-testid="stHorizontalBlock"] {

        display: flex !important;

        flex-wrap: nowrap !important;

        width: max-content !important;
        max-width: none !important;

        overflow: visible !important;

        gap: 16px !important;
    }


    .st-key-movie-row [data-testid="stHorizontalBlock"] > div,
    .st-key-recommendation-row [data-testid="stHorizontalBlock"] > div {

        flex: 0 0 150px !important;

        width: 150px !important;
        min-width: 150px !important;
        max-width: 150px !important;
    }


    /* ---------------------------------------------
       Scrollbar
    --------------------------------------------- */

    .st-key-movie-row::-webkit-scrollbar,
    .st-key-recommendation-row::-webkit-scrollbar {

        height: 8px;
    }

    .st-key-movie-row::-webkit-scrollbar-thumb,
    .st-key-recommendation-row::-webkit-scrollbar-thumb {

        background: rgba(255, 255, 255, 0.25);
        border-radius: 10px;
    }

    .st-key-movie-row::-webkit-scrollbar-track,
    .st-key-recommendation-row::-webkit-scrollbar-track {

        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# Header
# ==================================================

st.title("CineMatch")

st.markdown(
    """
    CineMatch

    Discover your next favorite movie.

    Rate the movies you've seen.
    We'll find movies that match your taste.
    """
)


# ==================================================
# Load data
# ==================================================

ratings, movies, tags, links = load_data()


# ==================================================
# Select movies
# ==================================================

if (
    "sample_movies" not in st.session_state
    or "poster_url" not in st.session_state.sample_movies.columns
):

    sample_movies = get_random_movies(
        movies,
        ratings,
        n=10
    ).copy()

    # MovieLens movieId → TMDB movieId
    sample_movies["tmdbId"] = (
        sample_movies["movieId"]
        .map(
            links.set_index("movieId")["tmdbId"]
        )
    )

    # TMDB poster URL
    sample_movies["poster_url"] = (
        sample_movies["tmdbId"]
        .apply(get_poster_url)
    )

    st.session_state.sample_movies = sample_movies


sample_movies = st.session_state.sample_movies


# ==================================================
# Movie Taste Profile
# ==================================================

st.divider()

st.subheader("MOVIE TASTE PROFILE")


# ==================================================
# Rating input
# ==================================================

user_ratings = {}


with st.container(
    horizontal=True,
    horizontal_alignment="left",
    gap="small",
    key="movie-row"
):

    for _, movie in sample_movies.iterrows():

        with st.container(width=150):

            # Poster
            if movie["poster_url"]:

                st.image(
                    movie["poster_url"],
                    width=150
                )

            # Title / Genre
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

            # Rating
            rating = st.selectbox(
                "평점",
                ["안 봤어요", 1, 2, 3, 4, 5],
                key=f"rating_{movie['movieId']}",
                label_visibility="collapsed"
            )

            user_ratings[movie["movieId"]] = rating


# ==================================================
# Recommendation button
# ==================================================

if st.button(
    "Find My Matches →",
    type="primary",
    use_container_width=True
):

    # Count rated movies
    rated_movies = sum(
        rating != "안 봤어요"
        for rating in user_ratings.values()
    )

    if rated_movies < 3:

        st.warning(
            "최소 3편 이상의 영화에 평점을 남겨주세요."
        )

        st.stop()


    # --------------------------------------------------
    # Create new user profile
    # --------------------------------------------------

    user_profile = create_user_profile(
        sample_movies,
        user_ratings
    )


    # --------------------------------------------------
    # Calculate similarity
    # --------------------------------------------------

    similarities = calculate_new_user_similarity(
        user_profile,
        ratings
    )

    if similarities.empty:

        st.warning(
            "평가한 영화와 공통으로 평가한 영화가 충분한 사용자를 "
            "찾지 못했어. 다른 영화에 평점을 남겨 다시 시도해봐."
        )

        st.stop()


    # --------------------------------------------------
    # Generate recommendations
    # --------------------------------------------------

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


    if recommendations.empty:

        st.warning(
            "현재 평점 조합으로는 추천할 영화를 찾지 못했습니다. "
            "다른 영화에 평점을 남겨 다시 시도해주세요."
        )

        st.stop()


    # --------------------------------------------------
    # Save recommendation results
    # --------------------------------------------------

    st.session_state.recommendations = recommendations

    # 새로운 추천을 만들었으므로 이전 Pick 제거
    if "picked_movie" in st.session_state:
        del st.session_state.picked_movie


# ==================================================
# Recommendation Results
# ==================================================

if "recommendations" in st.session_state:

    recommendations = st.session_state.recommendations

    st.divider()

    st.subheader("YOUR RECOMMENDATIONS")


    # --------------------------------------------------
    # Recommendation cards
    # --------------------------------------------------

    with st.container(
        horizontal=True,
        horizontal_alignment="left",
        gap="small",
        key="recommendation-row"
    ):

        for _, movie in recommendations.iterrows():

            with st.container(width=150):

                # Poster
                if movie["poster_url"]:

                    st.image(
                        movie["poster_url"],
                        width=150
                    )

                # Title / Genre / Predicted rating
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


    # ==================================================
    # Pick My Movie
    # ==================================================

    st.divider()

    st.subheader("🍿 PICK MY MOVIE")

    st.write(
        "Can't decide? Let CineMatch pick one for you."
    )


    if st.button(
        "🎲 Pick a Movie",
        use_container_width=True
    ):

        picked_movie = recommendations.sample(
            n=1
        ).iloc[0]

        st.session_state.picked_movie = picked_movie


    # --------------------------------------------------
    # Show picked movie
    # --------------------------------------------------

    if "picked_movie" in st.session_state:

        picked_movie = st.session_state.picked_movie

        st.markdown("### 🎬 Tonight's Pick")

        col1, col2 = st.columns([1, 2])

        with col1:

            if picked_movie["poster_url"]:

                st.image(
                    picked_movie["poster_url"],
                    width=200
                )

        with col2:

            st.markdown(
                f"## {picked_movie['title']}"
            )

            st.write(
                picked_movie["genres"].replace("|", " · ")
            )

            st.write(
                f"⭐ Predicted rating: "
                f"**{picked_movie['predicted_rating']:.2f}**"
            )

            st.caption(
                "Picked randomly from your recommendations."
            )