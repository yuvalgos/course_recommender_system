import numpy as np


# although it can be flattened because we are only using one algorithm, the
# full inheritance branch is implemented here :
class GenericAlgorithm:
    def __init__(self):
        self.is_trained = False

    def train(self, X, y):
        assert (X.shape[0] == len(y))
        assert (X.shape[1] == 2)
        self.is_trained = True

    def predict(self, x):
        assert (len(x) == 2)
        assert (self.is_trained is True)


class KNNGeneric(GenericAlgorithm):
    def __init__(self, k=5, min_support=2):
        assert (k >= 1)
        assert (min_support >= 1)
        super().__init__()

        self.k = k
        self.X = None
        self.y = None
        self.min_support = min_support

    def train(self, X, y):
        super().train(X, y)
        self.X = X
        self.y = y
        # all the calculations are going to be done in predict

    def predict(self, x):
        super().predict(x)


class KNNUser(KNNGeneric):
    """
     this is also an expandable class for other user based KNN algorithms
     which are going to use it's protected methods
    """

    def __init__(self, k=5, min_support=2):
        super().__init__(k, min_support)

    def _cosine_similarity(self, user1, user2):
        """
        compute the cosine similarity of two users using only courses they both
        rated. in order to do that the users must have at least self.min_support
        courses they both rated, otherwise None is returned.
        """
        # find all ratings indices for each user:
        u1_ratings_ind = np.where(self.X[:, 0] == user1)[0]
        u2_ratings_ind = np.where(self.X[:, 0] == user2)[0]
        X_u1 = self.X[u1_ratings_ind, :]
        X_u2 = self.X[u2_ratings_ind, :]
        y_u1 = self.y[u1_ratings_ind]
        y_u2 = self.y[u2_ratings_ind]

        # get the common courses and their indices in each users rating array
        common_courses, u1_ind_common, u2_ind_common = np.intersect1d(X_u1[:, 1],
                                                                      X_u2[:, 1],
                                                                      assume_unique=True,
                                                                      return_indices=True)
        # check support is large enough:
        if not len(common_courses) >= self.min_support:
            return None

        # create vectors for each user in the common courses space:
        y_u1_common = y_u1[u1_ind_common]
        y_u2_common = y_u2[u2_ind_common]

        # return cosine similarity in that space:
        return np.inner(y_u1_common, y_u2_common) / (np.linalg.norm(y_u1_common) *
                                                     np.linalg.norm(y_u2_common))

    def _compute_similarities(self, user, course):
        """
        *if no other users rated the course a None is returned*

        this method gets user and course to predict, and finds the potential
        neighbors as an array with three rows:
        user_similarities[0] are the users rated the course
        user_similarities[1] are thier similarities to user
        user_similarities[2] are thier ratings to the course

        *in case the similarity was impossible to compute it is -1 in the array*

        this data is is used in predict
        """
        # find all rating for this course and all the raters:
        course_ratings_indices = np.where(self.X[:, 1] == course)
        X_course = self.X[course_ratings_indices, :][0]
        y_course = self.y[course_ratings_indices]
        users_rated_course = X_course[:, 0]
        # the useres are sorted by their location on X_course and y_course

        if len(users_rated_course) == 0:
            return None

        # compute similaritiy between predicted user and each of the users rated
        # the course
        cosine_sim_vectorized = np.vectorize(self._cosine_similarity)
        similarities = cosine_sim_vectorized(users_rated_course, user)
        np.nan_to_num(similarities, nan=-1, copy=False)
        similarities[similarities == None] = -1

        user_similarities = [users_rated_course,
                             similarities,
                             y_course]
        user_similarities = np.array(user_similarities)

        return user_similarities

    def _get_knn_for_course(self, user, course):
        """
        returns neighbors vector with 3 rows and min(k,n_of_neighbors_for_this course) collumns:
        neighbors_vec[0] are the neighbors (users_id)
        neighbors_vec[1] are thier similarities to user
        neighbors_vec[2] are thier ratings to the course
        None is returned if there are no neighbors for this course
        """
        if user not in self.X[:, 0]:
            # print("user", user, "has no ratings in the train set")
            return None

        user_similarities = self._compute_similarities(user, course)
        if user_similarities is None:
            # no other users rated that course
            return None

        total_neighbors = len((user_similarities[1])[user_similarities[1] > 0])

        if total_neighbors < 1:
            # no other users rated that course with min_support
            return None

        if total_neighbors <= self.k:
            # there are exactly k users or less so they are all neighbors
            neighbors_indices = tuple(np.where(user_similarities[1] > 0)[0])
        else:
            neighbors_indices = tuple(
                np.argpartition(user_similarities[1], -self.k)[-self.k:])

        neighbors_vec = user_similarities[:, neighbors_indices]
        return neighbors_vec

    def predict(self, x):
        super().predict(x)
        user, course = x[0], x[1]

        neighbors_vec = self._get_knn_for_course(user, course)
        if neighbors_vec is None:
            return None

        y_course = neighbors_vec[2, :]
        return y_course.mean()


class KNNWithAllUsersThresoledBias(KNNUser):
    def __init__(self, k=7, min_support=2, bias_weight=1, bias_threshold=1):
        super().__init__(k, min_support)
        self.bias_weight = bias_weight
        self.bias_threshold = bias_threshold
        self.users_means = dict()
        self.mean_mean_rating = None

    def train(self, X, y):
        super().train(X, y)
        # since we are computing all users means anyway, we are going to save
        # them in a dictionary. in production we are going to get the values
        # from the database and update it incrementaly every time user rates
        users = np.unique(X[:, 0])
        for user in users:
            self.users_means[user] = y[X[:, 0] == user].mean()

        self.mean_mean_rating = sum(self.users_means.values()) / len(self.users_means)

        biases = self.mean_mean_rating - np.array([self.users_means[X[i, 0]]
                                                   for i in range(len(y))])
        biases[np.absolute(biases) < self.bias_threshold] = 0

        self.y_old = np.copy(y)
        self.y = y + biases * self.bias_weight
        self.y[self.y > 10] = 10
        self.y[self.y < 1] = 1

    def predict(self, x):
        KNNGeneric.predict(self, x)
        user, course = x[0], x[1]

        neighbors_vec = self._get_knn_for_course(user, course)
        if neighbors_vec is None:
            return None

        neighbors_users = neighbors_vec[0, :]
        similarities = neighbors_vec[1, :]
        y_course = neighbors_vec[2, :]

        knn_prediction = y_course.mean()
        bias = self.users_means[user] - self.mean_mean_rating
        bias = 0 if np.absolute(bias) < self.bias_threshold else bias

        res = knn_prediction + bias * self.bias_weight
        # threshold:
        if res > 10:
            res = 10
        elif res < 1:
            res = 1

        return res
