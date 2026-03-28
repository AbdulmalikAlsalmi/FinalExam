class SearchEngine:
    def __init__(self, movie_catalog, ratings_data):
        self.movie_catalog = movie_catalog
        self.ratings_data = ratings_data

    # -----------------------------
    # this function allow user to search by:
    # 1. title keyword
    # 2. genre
    # 3. year
    # -----------------------------
    def search_movies(self, title_keyword="", genre="All", year="All"):
        results = []

        for movie in self.movie_catalog.values():
            title_match = True
            genre_match = True
            year_match = True

            if title_keyword:
                title_match = title_keyword.lower() in movie.title.lower()

            if genre != "All":
                genre_match = movie.genre.lower() == genre.lower()

            if year != "All":
                year_match = movie.year == int(year)

            if title_match and genre_match and year_match:
                results.append(movie)

        return results