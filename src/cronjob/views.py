from django.http import HttpResponse
from prometheus_client import generate_latest
from httpcronjob.metrics import registry  # Import your registry

def metrics_view(request):
    return HttpResponse(generate_latest(registry), content_type="text/plain")
