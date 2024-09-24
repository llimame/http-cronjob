from django.contrib import admin
from .models import CronGroup, CronApp, CronJob, RequestStatistics

class CronJobInline(admin.TabularInline):
    model = CronJob
    extra = 0  # No extra forms
    readonly_fields = ['uri', 'description', 'schedule', 'created_at', 'updated_at', 'created_by']  # Make fields readonly

class CronAppInline(admin.TabularInline):
    model = CronApp
    extra = 0  # No extra forms
    readonly_fields = ['name', 'url', 'created_at', 'updated_at', 'created_by']  # Make fields readonly

@admin.register(CronGroup)
class CronGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_cron_jobs', 'get_cron_apps', 'created_at', 'updated_at', 'created_by')
    inlines = [CronJobInline, CronAppInline]

    def get_cron_jobs(self, obj):
        return ", ".join([job.uri for job in obj.jobs.all()])
    get_cron_jobs.short_description = 'Cron Jobs'

    def get_cron_apps(self, obj):
        return ", ".join([app.url for app in obj.apps.all()])
    get_cron_apps.short_description = 'Cron Apps'

    def get_readonly_fields(self, request, obj=None):
        return ['get_cron_jobs', 'get_cron_apps'] 


class RequestStatisticsInline(admin.TabularInline):
    model = RequestStatistics
    extra = 0
    readonly_fields = ('cronjob', 'app', 'url', 'status_code', 'response_time', 'success', 'timestamp')
    fields = readonly_fields  # Make all fields read-only

@admin.register(CronApp)
class CronAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'group')
    inlines = [RequestStatisticsInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Use select_related or prefetch_related correctly
        return qs.prefetch_related('request_statistics')
        
@admin.register(CronJob)
class CronJobAdmin(admin.ModelAdmin):
    list_display = ('uri', 'group', 'schedule', 'created_at', 'created_by')
    list_filter = ('group', 'created_by')
    search_fields = ('uri', 'description')


@admin.register(RequestStatistics)
class RequestStatisticsAdmin(admin.ModelAdmin):
    list_max_show_all = 10
    list_display = ('cronjob', 'url', 'status_code', 'response_time', 'success', 'timestamp')
    search_fields = ('cronjob', 'url')
    list_filter = ('success', 'status_code')