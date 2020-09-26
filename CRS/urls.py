from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new_search', views.new_search, name='new_search'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('my_courses/', views.my_courses, name='my_courses'),
    path('add_course_rating/<int:course_number>', views.add_course_rating, name='add_course_rating'),
    path('edit_course_rating/<int:course_number>', views.edit_course_rating, name='edit_course_rating'),
    path('delete_course_rating/<int:course_number>', views.delete_course_rating, name='edit_course_rating'),
    path('course/<int:course_number>', views.course_view, name='course'),

    path('management', views.management, name='management'),
    path('add_courses', views.add_courses, name='add_courses'),
]
