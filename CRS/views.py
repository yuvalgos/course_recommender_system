import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django_email_verification import sendConfirm

from . import models
from .user.forms import *

from .add_courses_to_db import AddCoursesToDB, ClearCoursesDB

BASE_UG_COURSE_URL = 'https://ug3.technion.ac.il/rishum/course/'


# Create your views here.
def home(request):
    return render(request, template_name='CRS/index.html')


def instructions(request):
    return render(request, template_name='CRS/instructions.html')


def faq(request):
    return render(request, template_name='CRS/faq.html')


def contact_us(request):
    msg = ""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']

            email_content = "קיבלת מייל מ:" + sender_name + "\n" + \
                "שם משתמש:" + request.user.username + "\n" + \
                "מייל:" + sender_email + "\n\n" + \
                form.cleaned_data["message"]

            send_mail("מייל דרך צור קשר", email_content, sender_email,
                      ['TCourseRecommender@gmail.com'])

            msg = "ההודעה התקבלה, תודה!"
        else:
            msg = "תקלה, נסה שנית או שלח מייל"

    return render(request, 'CRS/contact_us.html', {'form': ContactForm(), 'msg': msg})


def new_search(request):
    search = request.POST.get('search')

    models.Search.objects.create(search=search)

    search_results_name = models.Course.objects.filter(name__contains=search)
    search_results_number = models.Course.objects.filter(
        number_string__contains=search)
    search_results = list(set(search_results_name) |
                          set(search_results_number))

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
    if request.user.is_authenticated:
        logout(request)

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

            user.student.credit_points = student_form.cleaned_data["credit_points"]
            user.student.semester = student_form.cleaned_data["semester"]
            user.student.degree_path = student_form.cleaned_data["degree_path"]
            user.student.faculty = student_form.data.get("faculty")
            # not using cleaned_data because clean data returns faculty model and student.faculty is saved as charfield

            user.student.save()
            sendConfirm(user) # sets EMAIL_ACTIVE_FIELD to false and sends confirmation email
            # login(request, user)
            return redirect(reverse("verification_email_sent"))
        else:
            # one of the forms is not valid:
            error_list = str(user_form.errors) + str(student_form.errors)
            return render(
                request, "registration/register.html",
                {"user_form": user_form,
                 'student_form': student_form,
                 'error_list': error_list}
            )


def verification_email_sent(request):
    return render(request, "registration/verification_email_sent.html")


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
             "course_number": course_number,
             "form": CourseRatingForm,
             }
        )
    elif request.method == "POST":
        course_rating_form = CourseRatingForm(request.POST)
        if course_rating_form.is_valid():
            # update course average rating:
            if course.average_difficulty is None or course.average_workload is None:
                # this is the first rating therefore it is the average
                course.average_difficulty = course_rating_form.cleaned_data['difficulty']
                course.average_workload = course_rating_form.cleaned_data['workload']
            else:
                # append new values to average by this formula
                course.average_difficulty = \
                    (float(course.average_difficulty) * float(course.ratings_count) +
                     float(course_rating_form.cleaned_data['difficulty'])) / (float(course.ratings_count) + 1)
                course.average_workload = \
                    (float(course.average_workload) * float(course.ratings_count) +
                     float(course_rating_form.cleaned_data['workload'])) / (float(course.ratings_count) + 1)
            course.ratings_count = course.ratings_count + 1

            course.save()
            course_rating_form.save(commit=False)
            course_rating_form.instance.course_id = course_number
            course_rating_form.instance.user = request.user
            course_rating_form.save()

        # if form is not valid, user is still redirected to my_courses, but it shouldn't happen
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
            {"form": CourseRatingForm(instance=course_rating),
             "course_name_and_number": course_name_and_number, }
        )

    elif request.method == "POST":
        form = CourseRatingForm(request.POST, instance=course_rating)
        if form.is_valid():
            old_diff = course_rating.difficulty
            old_wl = course_rating.workload
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

        # if form is not valid, user is still redirected to my_courses, but it shouldn't happen
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
    # ug_urls = BASE_UG_COURSE_URL + course.number_string
    return render(
        request, "CRS/course.html",
        {"course": course, }
    )


@login_required
def edit_profile(request):
    current_student = request.user.student
    if request.method == "GET":
        student_form = StudentEditForm(instance=current_student)
        return render(
            request, "CRS/edit_profile.html",
            {"student_form": student_form, }
        )
    elif request.method == "POST":
        student_form = StudentEditForm(request.POST)
        if student_form.is_valid():
            current_student.credit_points = \
                student_form.cleaned_data["credit_points"]
            current_student.semester = student_form.cleaned_data["semester"]
            current_student.degree_path = student_form.cleaned_data["degree_path"]
            current_student.faculty = student_form.data.get("faculty")
            # not using cleaned_data because clean data returns faculty model and
            # student.faculty is saved as charfield
            current_student.save()
            message = "נשמר בהצלחה"
            return render(
                request, "CRS/edit_profile.html",
                {"student_form": student_form,
                 "message": message,
                 }
            )
        else:
            return render(
                request, "CRS/edit_profile.html",
                {"student_form": student_form, }
            )


# ---------------------management:----------------------
@staff_member_required
def management(request):
    return render(request, template_name='CRS/management.html')


@staff_member_required
def add_courses(request):
    AddCoursesToDB()
    return redirect('management')
