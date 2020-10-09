from .models import CourseRating
from django_pandas.io import read_frame
from surprise import Reader
from surprise import Dataset
from surprise import KNNBasic
from surprise import dump


# trains two models and dumps the surprise algorithem objects to a file named
# "RecommenderDumpDiff" (for difficulty) "RecommenderDumpWL" (for workload)
def train_recommender():
    course_rating_qs = CourseRating.objects.all()
    course_rating_df = read_frame(course_rating_qs, verbose=False)

    # surprise library gets dataframe in this order: (user,course,rating)
    fields_workload = ["user", "course", "difficulty"]
    df_difficulty = course_rating_df.loc[:, fields]
    fields_workload = ["user", "course", "workload"]
    df_workload = course_rating_df.loc[:, fields]

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

    dump.dump("RecommenderDumpDiff", algo=algorithm_difficulty)
    dump.dump("RecommenderDumpWL", algo=algorithm_workload)


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

