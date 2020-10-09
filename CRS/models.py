from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


NO_VALUE = -1


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    semester = models.IntegerField(default=None, null=True, blank=True)
    credit_points = models.FloatField(default=None, null=True, blank=True)
    faculty = models.CharField(max_length=100, null=True, blank=True)
    degree_path = models.CharField(max_length=100, null=True, blank=True)
    average_grade = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.student.save()


class Course(models.Model):
    number = models.IntegerField(primary_key=True)
    number_string = models.CharField(max_length=20)  # includes zeroes at the beginning
    name = models.CharField(max_length=200)
    info = models.TextField(max_length=1000)
    credit_points = models.FloatField()

    average_difficulty = models.FloatField(default=None, null=True)
    average_workload = models.FloatField(default=None, null=True)
    ratings_count = models.IntegerField(default=0)
    average_grade_by_voters = models.FloatField(default=None, null=True)
    grades_count = models.IntegerField(default=0)

    def __str__(self):
        str = self.number_string + " | " + self.name
        return str

    class Meta:
        verbose_name_plural = "Courses"


class CourseRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    difficulty = models.FloatField()
    workload = models.FloatField()
    final_grade = models.IntegerField(default=None, null=True, blank=True)
    semesters_taken = models.CharField(max_length=200, default=None, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "user: " + self.user.__str__() + \
               " \ course: " + self.course.__str__() + \
               " \ diff: " + str(self.difficulty) + \
               " \ workload: " + str(self.workload)


class Search(models.Model):
    search = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.search)

    class Meta:
        verbose_name_plural = "Searches"


class Faculty(models.Model):
    faculty = models.CharField(max_length=100)

    def __str__(self):
        return self.faculty
