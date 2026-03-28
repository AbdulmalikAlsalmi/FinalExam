from functools import reduce

class User:
    def __init__(self, user_id, name):
        self._user_id = user_id
        self._name = name
        self.viewing_history = []
        self.rated_movies = {}

    def get_user_id(self):
        return self.__user_id

    def get_name(self):
        return self.__name

    def get_user_id(self):
        return self._user_id

    def get_name(self):
        return self._name

    # polymorphic method
    def get_role(self):
        return "User"

    def watch_movie(self, movie_id):
        if movie_id not in self.viewing_history:
            self.viewing_history.append(movie_id)

    def rate_movie(self, movie_id, rating):
        self.rated_movies[movie_id] = rating

    # -----------------------------
    # static method to load users
    # -----------------------------
    @staticmethod
    def load_users(users_file="users.txt"):
        users = {}

        try:
            with open(users_file, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        parts = line.split(":")
                        # format: role:user_id:name
                        # check user role if admin or customer
                        if len(parts) == 3:
                            role, user_id, name = parts
                        else:
                            role = "Customer"
                            user_id, name = parts

                        if role == "Admin":
                            users[user_id] = Admin(user_id, name)
                        else:
                            users[user_id] = Customer(user_id, name)
        except FileNotFoundError:
            pass

        return users

    # -----------------------------
    # static method to save users
    # -----------------------------
    @staticmethod
    def save_users(users, users_file="users.txt"):
        with open(users_file, "w", encoding="utf-8") as file:
            for user in users.values():
                file.write(f"{user.get_role()}:{user.get_user_id()}:{user.get_name()}\n")

# customer is child of user class
class Customer(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name)

    def get_role(self):
        return "Customer"

# admin is child of user class
class Admin(User):
    def __init__(self, user_id, name):
        super().__init__(user_id, name)

    def get_role(self):
        return "Admin"

class Movie:
    def __init__(self, movie_id, title, genre, year):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre
        self.year = int(year)

    # -----------------------------
    # static method to load movies
    # -----------------------------
    @staticmethod
    def load_movies(movies_file="movies.txt"):
        movies = {}

        try:
            with open(movies_file, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        movie_id, title, genre, year = line.split(":")
                        movies[movie_id] = Movie(movie_id, title, genre, year)
        except FileNotFoundError:
            pass

        return movies

    # -----------------------------
    # static method to save movies
    # -----------------------------
    @staticmethod
    def save_movies(movies, movies_file="movies.txt"):
        with open(movies_file, "w", encoding="utf-8") as file:
            for movie in movies.values():
                file.write(f"{movie.movie_id}:{movie.title}:{movie.genre}:{movie.year}\n")

    # -----------------------------
    # static method to load ratings
    # -----------------------------
    @staticmethod
    def load_ratings(users, ratings_file="ratings.txt"):
        ratings_data = {}

        try:
            with open(ratings_file, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        user_id, movie_id, rating = line.split(":")

                        if user_id not in ratings_data:
                            ratings_data[user_id] = {}

                        ratings_data[user_id][movie_id] = float(rating)

                        if user_id in users:
                            users[user_id].rated_movies[movie_id] = float(rating)
        except FileNotFoundError:
            pass

        return ratings_data

    # -----------------------------
    # static method to save/update one rating
    # -----------------------------
    @staticmethod
    def save_rating(user_id, movie_id, rating, ratings_file="ratings.txt"):
        updated_lines = []
        rating_found = False

        try:
            with open(ratings_file, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        saved_user_id, saved_movie_id, saved_rating = line.split(":")

                        if saved_user_id == user_id and saved_movie_id == movie_id:
                            updated_lines.append(f"{user_id}:{movie_id}:{rating}\n")
                            rating_found = True
                        else:
                            updated_lines.append(line + "\n")
        except FileNotFoundError:
            pass

        if not rating_found:
            updated_lines.append(f"{user_id}:{movie_id}:{rating}\n")

        with open(ratings_file, "w", encoding="utf-8") as file:
            file.writelines(updated_lines)
    
    # -----------------------------
    # static method to add movie
    # -----------------------------
    @staticmethod
    def add_movie(movies, movie_id, title, genre, year, movies_file="movies.txt"):
        movies[movie_id] = Movie(movie_id, title, genre, year)
        Movie.save_movies(movies, movies_file)
    
    # -----------------------------
    # static method to edit movie
    # -----------------------------
    @staticmethod
    def edit_movie(movies, movie_id, title, genre, year, movies_file="movies.txt"):
        if movie_id in movies:
            movies[movie_id].title = title
            movies[movie_id].genre = genre
            movies[movie_id].year = int(year)
            Movie.save_movies(movies, movies_file)

    # -----------------------------
    # static method to remove movie
    # -----------------------------
    @staticmethod
    def remove_movie(movies, movie_id, movies_file="movies.txt"):
        if movie_id in movies:
            del movies[movie_id]
            Movie.save_movies(movies, movies_file)

    # -----------------------------
    # function to calculate average rating
    # -----------------------------
    def get_average_rating(self, ratings_data):
        movie_ratings = []

        for user_ratings in ratings_data.values():
            if self.movie_id in user_ratings:
                movie_ratings.append(float(user_ratings[self.movie_id]))

        if not movie_ratings:
            return 0.0

        total = reduce(lambda x, y: x + y, movie_ratings)
        return total / len(movie_ratings)


class UserViewingHistory:
    # -----------------------------
    # static method to load viewing history
    # -----------------------------
    @staticmethod
    def load_viewing_history(users, history_file="viewing_history.txt"):
        try:
            with open(history_file, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        user_id, movie_id = line.split(":")
                        if user_id in users:
                            if movie_id not in users[user_id].viewing_history:
                                users[user_id].viewing_history.append(movie_id)
        except FileNotFoundError:
            pass

    # -----------------------------
    # static method to save viewing history
    # -----------------------------
    @staticmethod
    def save_viewing_history(users, history_file="viewing_history.txt"):
        with open(history_file, "w", encoding="utf-8") as file:
            for user in users.values():
                for movie_id in user.viewing_history:
                    file.write(f"{user.get_user_id()}:{movie_id}\n")