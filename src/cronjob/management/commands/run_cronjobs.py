import requests
from django.core.management.base import BaseCommand
from cronjob.models import CronJob
from cronjob.tasks import save_request_statistics  # Import the task
from django.utils import timezone

# from httpcronjob.metrics import (
#     increment_success_metric,
#     increment_error_metric,
#     increment_latency_metric
# )

from httpcronjob.metrics import (
    cronjob_success_requests,
    cronjob_error_requests,
    cronjob_request_latency,
    cronjob_last_success_timestamp,
    cronjob_last_failure_timestamp
)


class Command(BaseCommand):
    help = 'Executes cron jobs and collects request statistics without saving them to the database.'

    def add_arguments(self, parser):
        # Define a custom argument for cron schedule
        parser.add_argument('schedule', type=str, nargs='?', default='* * * * *', help="Crontab schedule to match (e.g., '* * * * *').")

    def handle(self, *args, **kwargs):
        schedule = kwargs['schedule']
        cronjobs = CronJob.objects.filter(schedule=schedule)

        if not cronjobs.exists():
            self.stdout.write(self.style.WARNING(f'No cronjobs found for schedule: {schedule}'))
            return

        for cronjob in cronjobs:
            try:
                # Now, loop through all the apps related to the cronjob's group
                apps = cronjob.group.apps.all()  # Get all apps related to the CronJob group
                
                if not apps:
                    self.stdout.write(self.style.WARNING(f'No apps found for CronJob: {cronjob.uri}'))
                    continue

                for app in apps:
                    url = app.url + cronjob.uri
                    self.stdout.write(self.style.SUCCESS(f"Executing CronJob: {cronjob.uri} for URL: {url}"))
                    
                    headers = {
                        'X-CronJob-Schedule': cronjob.schedule,  # Custom header with cron job schedule
                        'User-Agent': 'http-cronjob 1.1'  # Custom User-Agent
                    }

                    # Measure the response time for the request
                    start_time = timezone.now()
                    response = requests.get(url, headers=headers, timeout=10)  # Pass the custom headers here
                    response_time = (timezone.now() - start_time).total_seconds()

                    # Update Prometheus metrics
                    if response.status_code == 200:
                        cronjob_success_requests.labels(status_code=response.status_code, endpoint=url).inc()
                        cronjob_last_success_timestamp.labels(status_code=response.status_code, endpoint=url).set(timezone.now().timestamp())
                    else:
                        cronjob_error_requests.labels(status_code=response.status_code, endpoint=url).inc()
                        cronjob_last_failure_timestamp.labels(status_code=response.status_code, endpoint=url).set(timezone.now().timestamp())

                    cronjob_request_latency.labels(endpoint=url).observe(response_time)
                    
                    # Use the Celery task to save request statistics
                    save_request_statistics.delay(
                        cronjob.id,  # Pass the cronjob ID
                        app.id,      # Pass the app ID
                        url,
                        response.status_code,
                        response_time,
                        response.status_code == 200
                    )

                    # Output request information
                    self.stdout.write(self.style.SUCCESS(f"Request to {url} completed. Status code: {response.status_code}, Time: {response_time} seconds"))

            except Exception as e:
                cronjob_error_requests.labels(status_code=e, endpoint=url).inc()
                cronjob_last_failure_timestamp.labels(status_code=e, endpoint=url).set(timezone.now().timestamp())
                #increment_error_metric(cronjob.uri, app.name)
                self.stdout.write(self.style.ERROR(f"Error executing CronJob {cronjob.uri}: {e}"))
