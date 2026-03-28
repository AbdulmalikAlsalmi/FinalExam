import streamlit as st
from models import User, Movie, UserViewingHistory, Admin
from recommendation_engine import RecommendationEngine
from search_engine import SearchEngine
from analytics_engine import AnalyticsEngine

ADMIN_KEY = "ADMIN-1234"

# -----------------------------
# initialize system data from text files
# -----------------------------
def load_system():
    users = User.load_users()
    movies = Movie.load_movies()
    UserViewingHistory.load_viewing_history(users)
    ratings_data = Movie.load_ratings(users)

    return users, movies, ratings_data


# set page layout
st.set_page_config(page_title="Movie Recommendation System", layout="centered")

# adding css to the page format
st.markdown("""
    <style>
        .block-container {
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

if "users" not in st.session_state:
    users, movies, ratings_data = load_system()
    st.session_state.users = users
    st.session_state.movies = movies
    st.session_state.ratings_data = ratings_data

users = st.session_state.users
movies = st.session_state.movies
ratings_data = st.session_state.ratings_data

st.title("AI-Based Movie Recommendation System (MRS)")

if not users:
    st.error("No users found in users.txt")
    st.stop()

if not movies:
    st.error("No movies found in movies.txt")
    st.stop()

st.subheader("User Login")

user_ids = list(users.keys())
selected_user_id = st.selectbox("Enter or Select User ID", user_ids)

# prevent user from changing admin to customer with admin access
if "last_user_id" not in st.session_state:
    st.session_state.last_user_id = selected_user_id

if st.session_state.last_user_id != selected_user_id:
    st.session_state.admin_access = False
    st.session_state.last_user_id = selected_user_id

if st.button("Login"):
    st.session_state.logged_in_user = selected_user_id

if "logged_in_user" not in st.session_state:
    st.info("Please login using your user ID.")
    st.stop()

current_user = users[st.session_state.logged_in_user]
st.success(f"Logged in as {current_user.get_name()} ({current_user.get_user_id()})")


recommendation_engine = RecommendationEngine(movies, ratings_data)
search_engine = SearchEngine(movies, ratings_data)

analytics_engine = AnalyticsEngine(movies, ratings_data, users)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Rate a Movie",
    "Top-N Recommendations",
    "Search Movies",
    "User Dashboard",
    "Admin Console"
])

st.subheader("Access Control")

admin_key_input = st.text_input("Admin Console Key", type="password")

if st.button("Open Admin Console"):
    if isinstance(current_user, Admin) and admin_key_input == ADMIN_KEY:
        st.session_state.admin_access = True
        st.success("Admin console unlocked.")
    elif not isinstance(current_user, Admin):
        st.session_state.admin_access = False
        st.error("Access denied. The selected user is not an administrator.")
    else:
        st.session_state.admin_access = False
        st.error("Invalid admin key.")

if "admin_access" not in st.session_state:
    st.session_state.admin_access = False

st.write(f"Logged in as: {current_user.get_name()} | Role: {current_user.get_role()}")

# -----------------------------
# tab 1: rate movie
# -----------------------------
with tab1:
    st.subheader("Select a Movie and Rate It")

    movie_options = {
        f"{movie.title} ({movie.year})": movie.movie_id
        for movie in movies.values()
    }

    selected_movie_label = st.selectbox("Choose a movie", list(movie_options.keys()))
    selected_movie_id = movie_options[selected_movie_label]
    selected_movie = movies[selected_movie_id]

    rating = st.slider("Select rating", 1, 5, 3)

    if st.button("Submit Rating"):
        current_user.rate_movie(selected_movie_id, rating)
        current_user.watch_movie(selected_movie_id)

        Movie.save_rating(current_user.get_user_id(), selected_movie_id, rating)
        UserViewingHistory.save_viewing_history(users)

        st.session_state.ratings_data = Movie.load_ratings(users)
        ratings_data = st.session_state.ratings_data

        avg = selected_movie.get_average_rating(ratings_data)

        st.success(f"You rated '{selected_movie.title}' with {rating} star(s).")
        st.info(f"Updated average rating: {avg:.2f}")


# -----------------------------
# tab 2: recommendations
# -----------------------------
with tab2:
    st.subheader("Generate Top-N Recommendations")

    top_n = st.number_input("Enter N", min_value=1, max_value=10, value=5, step=1)

    if st.button("Show Recommendations"):
        recommendation_engine = RecommendationEngine(movies, st.session_state.ratings_data)
        recommendations = recommendation_engine.generate_recommendations(current_user, top_n)

        if not recommendations:
            st.warning("No recommendations available. Watch or rate more movies first.")
        else:
            st.write("### Recommended Movies")
            for movie in recommendations:
                st.write(
                    f"**{movie.title}** | Genre: {movie.genre} | Year: {movie.year} | "
                    f"Average Rating: {movie.get_average_rating(st.session_state.ratings_data):.2f}"
                )


# -----------------------------
# tab 3: search movies
# -----------------------------
with tab3:
    st.subheader("Search Movies")

    genres = ["All"] + sorted({movie.genre for movie in movies.values()})
    years = ["All"] + sorted({movie.year for movie in movies.values()})

    col1, col2, col3 = st.columns(3)

    with col1:
        title_keyword = st.text_input("Search by Title Keyword")

    with col2:
        genre = st.selectbox("Search by Genre", genres)

    with col3:
        year = st.selectbox("Search by Year", years)

    if st.button("Search"):
        results = search_engine.search_movies(title_keyword, genre, year)

        if not results:
            st.warning("No movies found.")
        else:
            st.write("### Search Results")
            for movie in results:
                st.write(
                    f"**{movie.title}** | Genre: {movie.genre} | Year: {movie.year} | "
                    f"Average Rating: {movie.get_average_rating(st.session_state.ratings_data):.2f}"
                )

# -----------------------------
# tab 4: user dashboard
# -----------------------------
with tab4:
    st.subheader("User Dashboard")

    # top recommendations
    st.write("### Top Recommended Movies")
    recommendation_engine = RecommendationEngine(movies, st.session_state.ratings_data)
    dashboard_recommendations = recommendation_engine.generate_recommendations(current_user, top_n=5)

    if not dashboard_recommendations:
        st.warning("No recommendations available yet.")
    else:
        for movie in dashboard_recommendations:
            st.write(
                f"**{movie.title}** | Genre: {movie.genre} | Year: {movie.year} | "
                f"Average Rating: {movie.get_average_rating(st.session_state.ratings_data):.2f}"
            )

    # trending movies
    st.write("### Trending Movies")
    trending_movies = analytics_engine.get_trending_movies(top_n=5)

    if trending_movies:
        for movie, views, avg_rating in trending_movies:
            st.write(
                f"**{movie.title}** | Views: {views} | Genre: {movie.genre} | "
                f"Average Rating: {avg_rating:.2f}"
            )
    else:
        st.warning("No trending movie data available.")

    # popular genres
    st.write("### Popular Genres")
    genre_data = analytics_engine.get_popular_genres()

    if genre_data:
        st.bar_chart(genre_data)
    else:
        st.warning("No genre data available.")

    # watch history table
    st.write("### Watch History")
    watch_history_df = analytics_engine.get_watch_history_table(current_user)

    if not watch_history_df.empty:
        st.dataframe(watch_history_df, use_container_width=True)
    else:
        st.info("No watch history found.")

    # rating logs table
    st.write("### Rating Logs")
    rating_logs_df = analytics_engine.get_rating_logs_table(current_user)

    if not rating_logs_df.empty:
        st.dataframe(rating_logs_df, use_container_width=True)
    else:
        st.info("No rating logs found.")

    # top rated movies chart
    st.write("### Top Rated Movies")
    top_rated_df = analytics_engine.get_top_rated_movies_chart_data(top_n=5)

    if not top_rated_df.empty:
        top_rated_df = top_rated_df.set_index("Title")
        st.bar_chart(top_rated_df)
    else:
        st.info("No rating data available for chart.")


# -----------------------------
# tab 5: admin console
# -----------------------------
with tab5:
    st.subheader("Administrative Console")

    if not st.session_state.admin_access:
        st.warning("Admin console is locked. Access requires an Admin user and the correct admin key.")
    else:
        st.success("Admin access granted.")

        analytics_engine = AnalyticsEngine(movies, st.session_state.ratings_data, users)

        admin_action = st.selectbox(
            "Select Admin Action",
            [
                "Add Movie",
                "Edit Movie",
                "Remove Movie",
                "View Engagement Analytics"
            ]
        )


        # -----------------------------
        # add movie
        # -----------------------------
        if admin_action == "Add Movie":
            st.write("### Add New Movie")

            new_movie_id = st.text_input("Movie ID")
            new_title = st.text_input("Title")
            new_genre = st.text_input("Genre")
            new_year = st.number_input("Year", min_value=1900, max_value=2100, value=2024, step=1)

            if st.button("Add Movie to Database"):
                if new_movie_id in movies:
                    st.error("Movie ID already exists.")
                else:
                    Movie.add_movie(movies, new_movie_id, new_title, new_genre, new_year)
                    st.session_state.movies = Movie.load_movies()
                    st.success("Movie added successfully.")


        # -----------------------------
        # edit movie
        # -----------------------------
        elif admin_action == "Edit Movie":
            st.write("### Edit Existing Movie")

            movie_ids = list(movies.keys())
            selected_movie_id = st.selectbox("Select Movie ID", movie_ids)

            selected_movie = movies[selected_movie_id]

            edit_title = st.text_input("Title", value=selected_movie.title)
            edit_genre = st.text_input("Genre", value=selected_movie.genre)
            edit_year = st.number_input("Year", min_value=1900, max_value=2100, value=int(selected_movie.year), step=1)

            if st.button("Save Movie Changes"):
                Movie.edit_movie(movies, selected_movie_id, edit_title, edit_genre, edit_year)
                st.session_state.movies = Movie.load_movies()
                st.success("Movie updated successfully.")


        # -----------------------------
        # remove movie
        # -----------------------------
        elif admin_action == "Remove Movie":
            st.write("### Remove Movie")

            movie_ids = list(movies.keys())
            selected_movie_id = st.selectbox("Select Movie to Remove", movie_ids)

            if st.button("Delete Movie"):
                Movie.remove_movie(movies, selected_movie_id)
                st.session_state.movies = Movie.load_movies()
                st.success("Movie removed successfully.")
        

        # -----------------------------
        # engagement analytics
        # -----------------------------
        elif admin_action == "View Engagement Analytics":
            st.write("### Engagement Analytics")

            st.write("#### Most-Watched Movies")
            most_watched = analytics_engine.get_most_watched_movies(top_n=5)

            if most_watched:
                for movie, views in most_watched:
                    st.write(f"**{movie.title}** | Views: {views}")
            else:
                st.info("No watch data available.")

            st.write("#### Top Active Users")
            active_users = analytics_engine.get_top_active_users(top_n=5)

            if active_users:
                for user, watch_count in active_users:
                    st.write(f"**{user.get_name()}** ({user.get_role()}) | Watch Count: {watch_count}")
            else:
                st.info("No user activity data available.")

            st.write("#### Trending Movies")
            trending_movies = analytics_engine.get_trending_movies(top_n=5)

            if trending_movies:
                for movie, views, avg_rating in trending_movies:
                    st.write(
                        f"**{movie.title}** | Views: {views} | "
                        f"Average Rating: {avg_rating:.2f}"
                    )
            else:
                st.info("No trending data available.")