from .models import CourseRating
from django_pandas.io import read_frame
import time
import numpy as np

from .recommender_algorithms import KNNWithAllUsersThresoledBias

# limitations parameters
MIN_RATING_COUNT_FOR_USER = 4
MIN_RATING_COUNT_FOR_COURSE = 2


# algorithm hyper parameters:
ALG_MIN_SUPPORT = 2
ALG_K = 7
ALG_DIFF_BIAS_WEIGHT = 0.65
ALG_DIFF_BIAS_THRESHOLD = 0.5
ALG_WL_BIAS_WEIGHT = 0.95
ALG_WL_BIAS_THRESHOLD = 1.8


def filter_data(course_rating_df):
    """
     gets raw users data frame from the data base and returns X, y_diff and y_wl
     filtered numpy arrays for the algorithm to train
    """
    users_counts = course_rating_df["user"].value_counts()
    filtered_users_counts = users_counts[users_counts >= MIN_RATING_COUNT_FOR_USER]

    courses_counts = course_rating_df["course"].value_counts()
    filtered_courses_counts = courses_counts[courses_counts >= MIN_RATING_COUNT_FOR_COURSE]

    filtered_ratings_df = course_rating_df[
        course_rating_df["user"].isin(filtered_users_counts.index)
    ]
    filtered_ratings_df = filtered_ratings_df[
        filtered_ratings_df["course"].isin(filtered_courses_counts.index)
    ]

    X = filtered_ratings_df[["user", "course"]].to_numpy()
    y_diff = filtered_ratings_df["difficulty"].to_numpy()
    y_wl = filtered_ratings_df["workload"].to_numpy()

    return X, y_diff, y_wl


def recommend(user, course):
    """
     trains the model and returns recommendation for user and coruse (both difficulty and workload)
     return value is : (difficulty, workload, calculation_time)
    """
    start_time = time.time()

    # query all ratings from database:
    course_rating_qs = CourseRating.objects.all()
    course_rating_df = read_frame(course_rating_qs, verbose=False)

    # get filtered numpy arrays:
    X, y_diff, y_wl = filter_data(course_rating_df)

    # create algorithms and train them:
    algo_diff = KNNWithAllUsersThresoledBias(k=ALG_K,
                                             min_support=ALG_MIN_SUPPORT,
                                             bias_weight=ALG_DIFF_BIAS_WEIGHT,
                                             bias_threshold=ALG_DIFF_BIAS_THRESHOLD)
    algo_wl = KNNWithAllUsersThresoledBias(k=ALG_K,
                                           min_support=ALG_MIN_SUPPORT,
                                           bias_weight=ALG_WL_BIAS_WEIGHT,
                                           bias_threshold=ALG_WL_BIAS_THRESHOLD)

    algo_diff.train(X, y_diff)
    algo_wl.train(X, y_wl)

    calc_time = time.time() - start_time

    return algo_diff.predict((user, course)), algo_wl.predict((user, course)), calc_time

