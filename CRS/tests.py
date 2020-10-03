from django.test import TestCase
from .models import *

from random import randint
from django_pandas.io import read_frame
from surprise import Reader
from surprise import Dataset
from surprise import KNNBasic
from surprise import dump
import time

NUM_OF_USERS = 1000
NUM_OF_COURSES = 1200
RATINGS_PER_USER = 20


class RecommenderTimeTestCase(TestCase):
    def setUp(self):
        # create courses:
        for i in range(1,NUM_OF_COURSES):
            Course.objects.create(number=i,
                                  number_string=str(i),
                                  name=("course" + str(i)),
                                  info=("no info"),
                                  credit_points=3,)

        # create users:
        for i in range(1, NUM_OF_USERS):
            username = "user" + str(i)
            u = User.objects.create_user(username=username)
            u.student.credit_points = 100

            # add ratings for each user:
            for j in range(1, RATINGS_PER_USER):
                course = Course.objects.get(pk=randint(1, NUM_OF_COURSES-1))
                CourseRating.objects.create(user=u,
                                            course=course,
                                            difficulty=randint(1, 10),
                                            workload=randint(1, 10))

    def test_create_model(self):
        start_time = time.time()

        course_rating_qs = CourseRating.objects.all()
        course_rating_df = read_frame(course_rating_qs, verbose=False)

        # surprise library gets dataframe in this order: (user,course,rating)
        fields = ["user", "course", "workload"]
        course_rating_df = course_rating_df.loc[:, fields]

        reader = Reader(rating_scale=(1, 10))
        data = Dataset.load_from_df(course_rating_df, reader)
        algo = KNNBasic()
        trainset = data.build_full_trainset()
        algo.fit(trainset)
        print("--->traning time : %s seconds " % (time.time() - start_time))

        start_time = time.time()
        pred = algo.predict(100, 100, r_ui=5, verbose=True)
        print(pred.est)
        print(pred.details['was_impossible'])
        print("--->prediction time : %s seconds " % (time.time() - start_time))

        start_time = time.time()
        dump.dump("RecommenderDump", algo=algo, verbose=1)
        print("--->algo dump time : %s seconds " % (time.time() - start_time))

        start_time = time.time()
        dump.load("RecommenderDump")
        print("--->algo load time : %s seconds " % (time.time() - start_time))

