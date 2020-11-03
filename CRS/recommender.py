from .models import CourseRating
from django_pandas.io import read_frame
from surprise import Reader
from surprise import Dataset
from surprise import KNNBasic
from surprise import dump
import time


# trains the model and returns recommendation for user and coruse in 1 function
# return value is : (difficulty, workload, calculation_time)
def recommend(user, course):
    start_time = time.time()

    course_rating_qs = CourseRating.objects.all()
    course_rating_df = read_frame(course_rating_qs, verbose=False)

    # surprise library gets dataframe in this order: (user,course,rating)
    fields_difficulty = ["user", "course", "difficulty"]
    df_difficulty = course_rating_df.loc[:, fields_difficulty]
    fields_workload = ["user", "course", "workload"]
    df_workload = course_rating_df.loc[:, fields_workload]

    reader = Reader(rating_scale=(1, 10))
    data_difficulty = Dataset.load_from_df(df_difficulty, reader)
    data_workload = Dataset.load_from_df(df_workload, reader)

    # todo: to be tuned:
    algorithm_difficulty = KNNBasic()
    trainset_difficulty = data_difficulty.build_full_trainset()
    algorithm_difficulty.fit(trainset_difficulty)

    algorithm_workload = KNNBasic()
    trainset_workload = data_workload.build_full_trainset()
    algorithm_workload.fit(trainset_workload)

    predicted_difficulty = algorithm_difficulty.predict(user, course)
    predicted_workload = algorithm_workload.predict(user, course)

    calc_time = str(time.time() - start_time)

    if predicted_difficulty.details['was_impossible'] or \
            predicted_workload.details['was_impossible']:
        return None, None, calc_time

    return predicted_difficulty.est, predicted_workload.est, calc_time



############# not used for now: ############
############################################
# trains two models and dumps the surprise algorithem objects to a file named
# "RecommenderDumpDiff" (for difficulty) "RecommenderDumpWL" (for workload)
def train_recommender():
    start_time = time.time()

    course_rating_qs = CourseRating.objects.all()
    course_rating_df = read_frame(course_rating_qs, verbose=False)

    # surprise library gets dataframe in this order: (user,course,rating)
    fields_difficulty = ["user", "course", "difficulty"]
    df_difficulty = course_rating_df.loc[:, fields_difficulty]
    fields_workload = ["user", "course", "workload"]
    df_workload = course_rating_df.loc[:, fields_workload]

    reader = Reader(rating_scale=(1, 10))
    data_difficulty = Dataset.load_from_df(df_difficulty, reader)
    data_workload = Dataset.load_from_df(df_workload, reader)

    # todo: to be tuned:
    algorithm_difficulty = KNNBasic()
    trainset_difficulty = data_difficulty.build_full_trainset()
    algorithm_difficulty.fit(trainset_difficulty)

    algorithm_workload = KNNBasic()
    trainset_workload = data_workload.build_full_trainset()
    algorithm_workload.fit(trainset_workload)

    # dump models to file:
    dump.dump("RecommenderDumpDiff", algo=algorithm_difficulty)
    dump.dump("RecommenderDumpWL", algo=algorithm_workload)


    print(">>>> recommender trained in " + str(time.time() - start_time) + "seocnds")


# return value: (difficulty, workload, was imposible?? (tbd) )
def get_recommendation(user, course):
    algorithm_difficulty = dump.load("RecommenderDumpDiff")
    algorithm_workload = dump.load("RecommenderDumpWL")

    predicted_difficulty = algorithm_difficulty.predict(user, course)
    predicted_workload = algorithm_workload.predict(user, course)

    if predicted_difficulty.details['was_impossible'] or\
        predicted_workload.details['was_impossible']:
        return None, None

    return predicted_difficulty.est, predicted_workload.est

