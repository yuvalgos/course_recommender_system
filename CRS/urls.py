from django.urls import path, include
from . import views
from django_email_verification import urls as mail_urls

urlpatterns = [
    path('', views.home, name='home'),
    path('new_search', views.new_search, name='new_search'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('register/verification_email_sent', views.verification_email_sent,
         name='verification_email_sent'),
    path('my_courses/', views.my_courses, name='my_courses'),
    path('add_course_rating/<int:course_number>', views.add_course_rating,
         name='add_course_rating'),
    path('edit_course_rating/<int:course_number>', views.edit_course_rating,
         name='edit_course_rating'),
    path('delete_course_rating/<int:course_number>', views.delete_course_rating,
         name='delete_course_rating'),
    path('edit_profile/', views.edit_profile,name='edit_profile'),
    path('course/<int:course_number>', views.course_view, name='course'),
    path('course/<int:course_number>/estimate<int:estimate>', views.course_view, name='course_estimate'),
    path('email/', include(mail_urls)),
    path('instructions', views.instructions, name='instructions'),
    path('faq', views.faq, name='faq'),
    path('contact_us', views.contact_us, name='contact_us'),

    path('management', views.management, name='management'),
    path('add_courses', views.add_courses, name='add_courses'),
    path('add_extra_courses', views.add_extra_courses, name='add_extra_courses'),
    path('download_ratings', views.download_ratings, name='download_ratings'),
    path('run_script', views.run_script, name='run_script'),
]
