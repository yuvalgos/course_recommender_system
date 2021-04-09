from django.test import TestCase
from .models import *
from django_pandas.io import read_frame
import numpy as np


class RecommenderModuleTestCase(TestCase):
    def setUp(self):
        # create 6 courses:
        for i in range(6):
            Course.objects.create(number=i,
                                  number_string=str(i),
                                  name=("course" + str(i)),
                                  info=("no info"),
                                  credit_points=3,)

        # create 6 users:
        for i in range(6):
            username = "user" + str(i)
            u = User.objects.create_user(username=username)
            u.student.credit_points = 100
            # each user has rating for the courses {0,1..,user_id} which means
            # user1 has 1 rating, user1 has 2 and so on...
            for j in range(i+1):
                course = Course.objects.get(pk=j)
                CourseRating.objects.create(user=u,
                                            course=course,
                                            difficulty=5,
                                            workload=5)

    def test_filter_data(self):
        """ check that filter data takes out users and
        courses with insufficient amount of ratings """
        from .recommender import filter_data
        from .recommender import MIN_RATING_COUNT_FOR_USER, MIN_RATING_COUNT_FOR_COURSE

        course_rating_qs = CourseRating.objects.all()
        course_rating_df = read_frame(course_rating_qs, verbose=False)

        X, y_diff, y_wl = filter_data(course_rating_df)

        _, user_counts = np.unique(X[:,0], return_counts=True)
        assert user_counts.min() >= MIN_RATING_COUNT_FOR_USER

        _, course_counts = np.unique(X[:, 1], return_counts=True)
        assert course_counts.min() >= MIN_RATING_COUNT_FOR_COURSE

    def test_recommend(self):
        from .recommender import recommend

        pred_diff, pred_wl, calc_time = recommend(5, 3)
        # since all ratings are 5 and the user is not bias, predictions should be 5
        assert pred_diff == 5
        assert pred_wl == 5
        # it shouldn't take more then a second (well, a millisecond really)
        assert calc_time < 1


# NUM_OF_USERS = 1000
# NUM_OF_COURSES = 1200
# RATINGS_PER_USER = 20
#
#
# class RecommenderTimeTestCase(TestCase):
#     def setUp(self):
#         # create courses:
#         for i in range(1,NUM_OF_COURSES):
#             Course.objects.create(number=i,
#                                   number_string=str(i),
#                                   name=("course" + str(i)),
#                                   info=("no info"),
#                                   credit_points=3,)
#
#         # create users:
#         for i in range(1, NUM_OF_USERS):
#             username = "user" + str(i)
#             u = User.objects.create_user(username=username)
#             u.student.credit_points = 100
#
#             # add ratings for each user:
#             for j in range(1, RATINGS_PER_USER):
#                 course = Course.objects.get(pk=randint(1, NUM_OF_COURSES-1))
#                 CourseRating.objects.create(user=u,
#                                             course=course,
#                                             difficulty=randint(1, 10),
#                                             workload=randint(1, 10))
#
#     def test_create_model(self):
#         start_time = time.time()
#
#         course_rating_qs = CourseRating.objects.all()
#         course_rating_df = read_frame(course_rating_qs, verbose=False)
#
#         # surprise library gets dataframe in this order: (user,course,rating)
#         fields = ["user", "course", "workload"]
#         course_rating_df = course_rating_df.loc[:, fields]
#
#         reader = Reader(rating_scale=(1, 10))
#         data = Dataset.load_from_df(course_rating_df, reader)
#         algo = KNNBasic()
#         trainset = data.build_full_trainset()
#         algo.fit(trainset)
#         print("--->traning time : %s seconds " % (time.time() - start_time))
#
#         start_time = time.time()
#         pred = algo.predict(100, 100, r_ui=5, verbose=True)
#         print(pred.est)
#         print(pred.details['was_impossible'])
#         print("--->prediction time : %s seconds " % (time.time() - start_time))
#
#         start_time = time.time()
#         dump.dump("RecommenderDump", algo=algo, verbose=1)
#         print("--->algo dump time : %s seconds " % (time.time() - start_time))
#
#         start_time = time.time()
#         dump.load("RecommenderDump")
#         print("--->algo load time : %s seconds " % (time.time() - start_time))

