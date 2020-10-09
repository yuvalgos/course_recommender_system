import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from . import models
from .user.forms import *

from .add_courses_to_db import AddCoursesToDB, ClearCoursesDB

BASE_UG_COURSE_URL = 'https://ug3.technion.ac.il/rishum/course/'


# todo: use this in course page:
# ug_urls = BASE_UG_COURSE_URL + course.number_string

# Create your views here.
def home(request):
    return render(request, template_name='base.html')


def new_search(request):
    search = request.POST.get('search')

    # todo:check if it is nessesary to keep searches,
    #  delete this and the whole model if it isn't
    models.Search.objects.create(search=search)

    search_results_name = models.Course.objects.filter(name__contains=search)
    search_results_number = models.Course.objects.filter(
        number_string__contains=search)
    search_results = list(set(search_results_name) |
                          set(search_results_number))

    if len(search_results) == 1:
        # todo: there is one course, redirect to course page
        pass

    search_message = ''
    if len(search_results) == 0:
        search_message = "אין תוצאות עבור: " + search
    else:
        search_message = "חיפוש: " + search

    data_to_show = {
        'search_message': search_message,
        'search_results': search_results,
    }

    return render(request, 'CRS/new_search.html', data_to_show)


@transaction.atomic
def register(request):
    if request.method == "GET":
        return render(
            request, "registration/register.html",
            {"user_form": CustomUserCreationForm,
             'student_form': StudentRegForm}
        )

    elif request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)
        student_form = StudentRegForm(request.POST)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save()
            # todo : validate data, probably going to have to do that in forms.py
            #  maybe use student_form.cleaned_data or something similar and a for loop
            #  example: https://stackoverflow.com/questions/42960271/not-null-constraint-failed-core-profile-user-id

            user.student.credit_points = student_form.cleaned_data["credit_points"]
            user.student.semester = student_form.cleaned_data["semester"]
            user.student.degree_path = student_form.cleaned_data["degree_path"]
            user.student.faculty = student_form.data.get("faculty")
            # not using cleaned_data because clean data returns faculty model and student.faculty is saved as charfield

            user.student.save()
            login(request, user)
            return redirect(reverse("home"))
        else:
            # one of the forms is not valid:
            print(user_form.errors)
            print(student_form.errors)
            error_list = str(user_form.errors) + str(student_form.errors)
            print(student_form.errors)
            return render(
                request, "registration/register.html",
                {"user_form": user_form,
                 'student_form': student_form,
                 'error_list': error_list}
            )


# show courses the courses rated by the user
@login_required
def my_courses(request):
    current_user = request.user
    course_ratings = models.CourseRating.objects.filter(user=current_user).order_by('-updated_at')

    if len(course_ratings) == 0:
        page_title = "עדיין לא דירגת קורסים! חפש קורס והוסף לו דירוג."
        total_credit = 0
    else:
        page_title = "הקורסים שדירגת"
        total_credit = sum(rating.course.credit_points for rating in course_ratings)

    data_to_show = {
        "course_ratings": course_ratings,
        "page_title": page_title,
        "total_credit": total_credit,
    }
    return render(request, 'CRS/my_courses.html', data_to_show)


@login_required
def add_course_rating(request, course_number):
    course = get_object_or_404(models.Course, pk=course_number)

    # check if user already has rating to that course :
    course_ratings = models.CourseRating.objects.filter(user=request.user,
                                                        course=course)
    if len(course_ratings) != 0:
        return redirect(reverse("edit_course_rating",
                                kwargs={'course_number': course.number}))

    if request.method == "GET":
        course_name_and_number = course.number_string + " " + course.name
        return render(
            request, "CRS/add_course_rating.html",
            {"course_name_and_number": course_name_and_number,
             "course_number": course_number}
        )

    elif request.method == "POST":
        # todo: add data validation
        course_rating = CourseRating(user=request.user,
                                     course=course,
                                     difficulty=request.POST.get('difficulty'),
                                     workload=request.POST.get('workload'))
        if request.POST.get('grade_radio_button') == "show_grade":
            course_rating.final_grade = request.POST.get('grade')
        course_rating.save()

        # update course average rating:
        if course.average_difficulty is None or course.average_workload is None:
            # this is the first rating therefore it is the average
            course.average_difficulty = course_rating.difficulty
            course.average_workload = course_rating.workload
        else:
            # append new values to average by this formula
            course.average_difficulty =\
                (float(course.average_difficulty) * float(course.ratings_count) +
                 float(course_rating.difficulty)) / (float(course.ratings_count) + 1)
            course.average_workload = \
                (float(course.average_workload) * float(course.ratings_count) +
                 float(course_rating.workload)) / (float(course.ratings_count) + 1)
        course.ratings_count = course.ratings_count + 1
        course.save()

        return redirect(reverse("my_courses"))


@login_required
def edit_course_rating(request, course_number):
    course = get_object_or_404(models.Course, pk=course_number)
    course_rating = get_object_or_404(CourseRating,
                                      course=course,
                                      user=request.user)
    if request.method == "GET":
        course_name_and_number = course.number_string + " " + course.name
        return render(
            request, "CRS/edit_course_rating.html",
            {"form": EditCourseRatingForm(instance=course_rating),
             "course_name_and_number": course_name_and_number, }
        )

    elif request.method == "POST":
        # todo: and if form is valid
        old_diff = course_rating.difficulty
        old_wl = course_rating.workload
        print(old_diff)
        form = EditCourseRatingForm(request.POST, instance=course_rating)
        form.save()
        new_diff = course_rating.difficulty
        new_wl = course_rating.workload

        # update course average ratings:
        course_sum_diff = course.average_difficulty * float(course.ratings_count)
        course_sum_wl = course.average_workload * float(course.ratings_count)
        course_sum_diff = course_sum_diff - old_diff + new_diff
        course_sum_wl = course_sum_wl - old_wl + new_wl
        course.average_difficulty = course_sum_diff / float(course.ratings_count)
        course.average_workload = course_sum_wl / float(course.ratings_count)
        course.save()

        return redirect(reverse("my_courses"))


@login_required
def delete_course_rating(request, course_number):
    print("-----------------------------------------------------here")
    course = get_object_or_404(models.Course, pk=course_number)
    course_rating = get_object_or_404(CourseRating,
                                      course=course,
                                      user=request.user)
    old_difficulty = course_rating.difficulty
    old_workload = course_rating.workload
    course_rating.delete()

    # update new course average:
    if course.ratings_count == 1:
        # it was the only rating for this course
        course.average_difficulty = None
        course.average_workload = None
    else:
        course_sum_diff = course.average_difficulty * float(course.ratings_count)
        course_sum_wl = course.average_workload * float(course.ratings_count)
        course_sum_diff = course_sum_diff - old_difficulty
        course_sum_wl = course_sum_wl - old_workload
        course.average_difficulty = course_sum_diff / float(course.ratings_count - 1)
        course.average_workload = course_sum_wl / float(course.ratings_count - 1)
    course.ratings_count = course.ratings_count - 1
    course.save()

    return redirect(reverse("my_courses"))


def course_view(request, course_number):
    course = get_object_or_404(models.Course, pk=course_number)

    return render(
        request, "CRS/course.html",
        {"course": course, }
    )


# ---------------------management:----------------------
@staff_member_required
def management(request):
    return render(request, template_name='CRS/management.html')


@staff_member_required
def add_courses(request):
    AddCoursesToDB()
    return redirect('management')
