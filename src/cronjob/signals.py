from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from cronjob.models import CronJob
import os

CRON_FILE_PATH = '/etc/cron.d/cronjob'

@receiver([post_save, post_delete], sender=CronJob)
def update_cron_file(sender, instance, **kwargs):
    """
    Signal to update the cron file when a CronJob is created, updated, or deleted.
    """
    generate_cron_file()

def generate_cron_file():
    """
    Regenerate the cron file with the list of all cronjobs.
    """
    cronjobs = CronJob.objects.all()
    cron_lines = []

    # Generate cron lines for each CronJob
    for cronjob in cronjobs:
        cron_line = f"{cronjob.schedule} root /usr/local/bin/python /app/manage.py run_cronjobs \"{cronjob.schedule}\" >> /var/log/cron.log 2>&1"
        cron_lines.append(cron_line)

    # Write to /etc/cron.d/cronjob
    with open(CRON_FILE_PATH, 'w') as cron_file:
        cron_file.write("\n".join(cron_lines) + "\n")
