# Generated by Django 3.1 on 2020-10-06 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRS', '0007_faculty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faculty',
            name='faculty',
            field=models.CharField(max_length=100),
        ),
    ]
