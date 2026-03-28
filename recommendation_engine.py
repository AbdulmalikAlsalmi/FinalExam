class RecommendationEngine:
    def __init__(self, movie_catalog, ratings_data):
        self.movie_catalog = movie_catalog
        self.ratings_data = ratings_data

    # -----------------------------
    # recommendations are based on:
    # 1. matching genres from watched movies
    # 2. sorting matched movies by highest average rating
    # -----------------------------
    def generate_recommendations(self, user, top_n=5):
        preferred_genres = set()

        for movie_id in user.viewing_history:
            if movie_id in self.movie_catalog:
                preferred_genres.add(self.movie_catalog[movie_id].genre)

        recommended_movies = []

        for movie in self.movie_catalog.values():
            if movie.movie_id not in user.viewing_history and movie.genre in preferred_genres:
                recommended_movies.append(movie)
                
        # use sort function to sort the movies
        recommended_movies.sort(
            key=lambda movie: movie.get_average_rating(self.ratings_data),
            reverse=True
        )

        return recommended_movies[:top_n]