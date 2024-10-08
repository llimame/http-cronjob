# Generated by Django 4.2.16 on 2024-09-20 13:12

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
            name='CronApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nome da aplicação, como App1.', max_length=100)),
                ('url', models.URLField(help_text='URL base do sistema, como http://app1.sample.com.')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Data e hora de criação.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Data e hora da última atualização.')),
                ('created_by', models.ForeignKey(blank=True, help_text='Usuário que criou o app.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CronJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(help_text='URI relativa do cron job, como /cron/send_email.php ou /cron/check_applicants.json.', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Descrição opcional do cron job.', null=True)),
                ('schedule', models.CharField(help_text="Padrão de execução: 'every minute', 'every 5 minutes', ou expressão crontab.", max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Data e hora de criação.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Data e hora da última atualização.')),
                ('app', models.ForeignKey(help_text='Aplicação à qual este cron job pertence.', on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='cronjob.cronapp')),
                ('created_by', models.ForeignKey(blank=True, help_text='Usuário que criou o cron job.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CronGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nome do grupo de cron jobs, como APP1.', max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Data e hora de criação.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Data e hora da última atualização.')),
                ('created_by', models.ForeignKey(blank=True, help_text='Usuário que criou o grupo.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='cronapp',
            name='group',
            field=models.ForeignKey(help_text='Grupo ao qual este app pertence.', on_delete=django.db.models.deletion.CASCADE, related_name='apps', to='cronjob.crongroup'),
        ),
    ]
