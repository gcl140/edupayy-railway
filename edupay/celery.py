from datetime import timedelta
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edupay.settings')

app = Celery('edupay')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-reminders-every-morning': {
        'task': 'billing.tasks.send_invoice_reminders',
        'schedule': crontab(hour=12, minute=3),  # Every day at 8:00 AM
    },
}

# app.conf.beat_schedule = {
#     'send-reminders-every-minute': {
#         'task': 'billing.tasks.send_invoice_reminders',
#         'schedule': timedelta(minutes=1),  # Run every 1 minute
#     },
# }