from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_recommender_system.settings')
# celery settings for the demo_project
app = Celery('course_recommender_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
# here is the beat schedule dictionary defined
app.conf.beat_schedule = {
    'print-every-thrusday': {
        'task': 'CRS.tasks.test',
        'schedule': crontab(minute="*"),
    },
}
app.conf.timezone = 'UTC'
app.autodiscover_tasks()
