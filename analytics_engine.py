import pandas as pd

class AnalyticsEngine:
    def __init__(self, movie_catalog, ratings_data, users):
        self.movie_catalog = movie_catalog
        self.ratings_data = ratings_data
        self.users = users

    # -----------------------------
    # function to get most popular genres
    # count how many watched movies belong to each genre
    # -----------------------------
    def get_popular_genres(self):
        genre_count = {}

        for user in self.users.values():
            for movie_id in user.viewing_history:
                if movie_id in self.movie_catalog:
                    genre = self.movie_catalog[movie_id].genre
                    genre_count[genre] = genre_count.get(genre, 0) + 1

        return genre_count

    # -----------------------------
    # function to get most popular genres
    # count how many watched movies belong to each genre
    # -----------------------------
    def get_popular_genres(self):
        genre_count = {}

        for user in self.users.values():
            for movie_id in user.viewing_history:
                if movie_id in self.movie_catalog:
                    genre = self.movie_catalog[movie_id].genre
                    genre_count[genre] = genre_count.get(genre, 0) + 1

        return genre_count

    # -----------------------------
    # function to get trending movies
    # trending depends on number of views first,
    # then average rating
    # -----------------------------
    def get_trending_movies(self, top_n=5):
        movie_views = {}

        for user in self.users.values():
            for movie_id in user.viewing_history:
                movie_views[movie_id] = movie_views.get(movie_id, 0) + 1

        trending = []

        for movie_id, movie in self.movie_catalog.items():
            views = movie_views.get(movie_id, 0)
            avg_rating = movie.get_average_rating(self.ratings_data)
            trending.append((movie, views, avg_rating))

        trending.sort(key=lambda item: (item[1], item[2]), reverse=True)
        return trending[:top_n]

    # -----------------------------
    # function to prepare watch history table
    # -----------------------------
    def get_watch_history_table(self, user):
        rows = []

        for movie_id in user.viewing_history:
            if movie_id in self.movie_catalog:
                movie = self.movie_catalog[movie_id]
                rows.append({
                    "Movie ID": movie.movie_id,
                    "Title": movie.title,
                    "Genre": movie.genre,
                    "Year": movie.year
                })

        return pd.DataFrame(rows)

    # -----------------------------
    # function to prepare top rated movies chart data
    # -----------------------------
    def get_top_rated_movies_chart_data(self, top_n=5):
        rows = []

        for movie in self.movie_catalog.values():
            rows.append({
                "Title": movie.title,
                "Average Rating": movie.get_average_rating(self.ratings_data)
            })

        df = pd.DataFrame(rows)
        df = df.sort_values(by="Average Rating", ascending=False).head(top_n)

        return df

    # -----------------------------
    # function to get ratings
    # -----------------------------
    def get_rating_logs_table(self, user):
        rows = []

        for movie_id, rating in user.rated_movies.items():
            if movie_id in self.movie_catalog:
                movie = self.movie_catalog[movie_id]
                rows.append({
                    "Movie ID": movie.movie_id,
                    "Title": movie.title,
                    "Genre": movie.genre,
                    "Year": movie.year,
                    "User Rating": rating,
                    "Average Rating": round(movie.get_average_rating(self.ratings_data), 2)
                })

        return pd.DataFrame(rows)

    # -----------------------------
    # function to get most watched movies
    # count how many times each movie appears in users' watch histories
    # -----------------------------
    def get_most_watched_movies(self, top_n=5):
        movie_views = {}

        for user in self.users.values():
            for movie_id in user.viewing_history:
                movie_views[movie_id] = movie_views.get(movie_id, 0) + 1

        rows = []
        for movie_id, views in movie_views.items():
            if movie_id in self.movie_catalog:
                movie = self.movie_catalog[movie_id]
                rows.append((movie, views))

        rows.sort(key=lambda item: item[1], reverse=True)
        return rows[:top_n]

    # -----------------------------
    # function to get top active users
    # active user = highest watch count
    # -----------------------------
    def get_top_active_users(self, top_n=5):
        rows = []

        for user in self.users.values():
            rows.append((user, len(user.viewing_history)))

        rows.sort(key=lambda item: item[1], reverse=True)
        return rows[:top_n]
