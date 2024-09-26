from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone  # Add this line
import re

class CronGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Nome do grupo de cron jobs, como APP1.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora de criação.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data e hora da última atualização.")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuário que criou o grupo.")
    
    def __str__(self):
        return self.name


class CronApp(models.Model):
    group = models.ForeignKey(CronGroup, related_name='apps', on_delete=models.CASCADE, help_text="Grupo ao qual este app pertence.")
    name = models.CharField(max_length=100, help_text="Nome da aplicação, como App1.")
    url = models.URLField(help_text="URL base do sistema, como http://app1.sample.com.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora de criação.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data e hora da última atualização.")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuário que criou o app.")
    
    def __str__(self):
        return f"{self.name} ({self.url})"


class CronJob(models.Model):
    group = models.ForeignKey(CronGroup, related_name='jobs', on_delete=models.CASCADE, help_text="Grupo ao qual este cron job pertence.")
    uri = models.CharField(max_length=255, help_text="URI relativa do cron job, como /cron/send_email.php ou /cron/check_applicants.json.")
    description = models.TextField(blank=True, null=True, help_text="Descrição opcional do cron job.")
    schedule = models.CharField(max_length=100, help_text="Padrão de execução: 'every minute', 'every 5 minutes', ou expressão crontab.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data e hora de criação.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data e hora da última atualização.")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuário que criou o cron job.")

    def __str__(self):
        return f"{self.uri} (Grupo: {self.group.name})"

    def clean(self):
        cron_patterns = [
            r'^\* \* \* \* \*$',  # Every minute
            r'^\*/\d+ \* \* \* \*$',  # Every X minutes
            r'^\d+ \* \* \* \*$',  # Specific minute every hour
            r'^\d+ \d+ \* \* \*$',  # Specific minute and hour every day
            r'^\d+ \d+ \d+ \* \*$',  # Specific day of the month
            r'^\d+ \d+ \d+ \d+ \*$',  # Specific month
            r'^\d+ \d+ \d+ \d+ \d+$',  # Specific day of the week
            r'^\* \d+ \* \* \*$',  # Every minute during a specific hour
            r'^\* \* \d+ \* \*$',  # Every minute of a specific day
            r'^\* \* \* \d+ \*$',  # Every minute of a specific month
            r'^\* \* \* \* \d+$',  # Every minute of a specific day of the week
            r'^\*/\d+ \d+ \* \* \*$',  # Every X minutes during a specific hour
            r'^\*/\d+ \d+ \d+ \* \*$',  # Every X minutes during a specific day of the month
            r'^\*/\d+ \d+ \d+ \d+ \*$',  # Every X minutes during a specific month
            r'^\*/\d+ \d+ \d+ \d+ \d+$',  # Every X minutes on a specific day of the week
            r'^\d+ \*/\d+ \* \* \*$',  # Specific minute every X hours
            r'^\d+ \*/\d+ \d+ \* \*$',  # Specific minute on every X day of the month
            r'^\d+ \*/\d+ \d+ \d+ \*$',  # Specific minute on every X month
            r'^\d+ \*/\d+ \d+ \d+ \d+$',  # Specific minute on every X day of the week
            r'^\*/\d+ \*/\d+ \* \* \*$',  # Every X minutes every X hours
            r'^\*/\d+ \*/\d+ \d+ \* \*$',  # Every X minutes every X hours on specific day of the month
            r'^\*/\d+ \*/\d+ \d+ \d+ \*$',  # Every X minutes every X hours on specific month
            r'^\*/\d+ \*/\d+ \d+ \d+ \d+$',  # Every X minutes every X hours on specific day of the week
            r'^\* \*/\d+ \* \* \d+$',  # Every minute every X hours on a specific day of the week
            r'^\d+ \d+ \d+ \d+ \*/\d+$',  # Specific minute, hour, day of the month, and month every X day of the week
            r'^\*/\d+ \*/\d+ \*/\d+ \* \*$',  # Every X minutes every X hours every X day of the month
            r'^\*/\d+ \*/\d+ \*/\d+ \*/\d+$',  # Every X minutes every X hours every X day of the month every X day of the week
            r'^\*/\d+ \*/\d+ \*/\d+ \*/\d+ \*/\d+$',  # Fully flexible pattern
            r'^\d+ \d+ \* \* \d+$',
            # Add more patterns as necessary
        ]

        if not any(re.match(pattern, self.schedule) for pattern in cron_patterns) and self.schedule not in ["every minute", "every 5 minutes"]:
            raise ValidationError('O padrão de execução deve ser "every minute", "every 5 minutes", ou uma expressão crontab válida.')


class RequestStatistics(models.Model):
    cronjob = models.ForeignKey(CronJob, on_delete=models.CASCADE, related_name='request_statistics')  # Changed related_name
    app = models.ForeignKey(CronApp, on_delete=models.CASCADE, related_name='request_statistics')  # Keep as is
    url = models.URLField()
    status_code = models.IntegerField()
    response_time = models.FloatField()
    success = models.BooleanField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']  # Order by timestamp descending

    def __str__(self):
        return f"{self.cronjob} - {self.url} - {self.status_code} - {self.timestamp}"
