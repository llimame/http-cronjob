from celery import shared_task
from .models import RequestStatistics, CronJob

@shared_task
def save_request_statistics(cronjob_id, app_id, url, status_code, response_time, success):
    RequestStatistics.objects.create(
        cronjob_id=cronjob_id,
        app_id=app_id,  # Use the app_id to set the foreign key
        url=url,
        status_code=status_code,
        response_time=response_time,
        success=success
    )
