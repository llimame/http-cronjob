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
    Regenerate the cron file with the list of all cronjobs, preventing duplicates.
    """
    cronjobs = CronJob.objects.all()
    cron_dict = {}

    # Group cron jobs by their schedule
    for cronjob in cronjobs:
        command = f"/usr/local/bin/python /app/manage.py run_cronjobs \"{cronjob.schedule}\" >> /var/log/cron.log 2>&1"
        if cronjob.schedule in cron_dict:
            cron_dict[cronjob.schedule].append(command)
        else:
            cron_dict[cronjob.schedule] = [command]

    cron_lines = []

    # Generate unique cron lines
    for schedule, commands in cron_dict.items():
        combined_command = " && ".join(commands)
        cron_line = f"{schedule} root {combined_command}"
        cron_lines.append(cron_line)

    # Write to /etc/cron.d/cronjob
    tmp_cron_file_path = CRON_FILE_PATH + '.tmp'
    with open(tmp_cron_file_path, 'w') as cron_file:
        cron_file.write("\n".join(cron_lines) + "\n")
    os.rename(tmp_cron_file_path, CRON_FILE_PATH)
