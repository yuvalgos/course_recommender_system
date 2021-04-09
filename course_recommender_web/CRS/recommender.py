from .models import CourseRating
from django_pandas.io import read_frame
import time
import numpy as np

# limitations parameters
MIN_RATING_COUNT_FOR_USER = 4
MIN_RATING_COUNT_FOR_COURSE = 2


# algorithm hyper parameters:


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

    X, y_diff, y_wl = filter_data(course_rating_df)

    #return predicted_difficulty.est, predicted_workload.est, calc_time

