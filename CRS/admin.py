from django.contrib import admin
from .models import Search, Course, Student, CourseRating

# Register your models here.

admin.site.register(Search)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(CourseRating)

