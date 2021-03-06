# Generated by Django 3.1 on 2020-09-07 16:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('number', models.IntegerField(primary_key=True, serialize=False)),
                ('number_string', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('info', models.TextField(max_length=1000)),
                ('credit_points', models.FloatField()),
                ('average_difficulty', models.FloatField(default=None, null=True)),
                ('average_workload', models.FloatField(default=None, null=True)),
                ('ratings_count', models.IntegerField(default=0)),
                ('average_grade_by_voters', models.FloatField(default=None, null=True)),
                ('grades_count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Courses',
            },
        ),
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Searches',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(default=None, null=True)),
                ('credit_points', models.FloatField(default=None, null=True)),
                ('faculty', models.CharField(blank=True, max_length=100)),
                ('degree_path', models.CharField(blank=True, max_length=100)),
                ('average_grade', models.FloatField(default=None, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
