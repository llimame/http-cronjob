from prometheus_client import multiprocess
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge
# Create a global registry
registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)
# Define metrics
cronjob_success_requests = Counter(
    'cronjob_success_requests', 
    'Count of successful requests made by the cronjob', 
    ['status_code', 'endpoint'], 
    registry=registry
)

cronjob_error_requests = Counter(
    'cronjob_error_requests', 
    'Count of failed requests made by the cronjob', 
    ['status_code', 'endpoint'], 
    registry=registry
)

cronjob_request_latency = Histogram(
    'cronjob_request_latency_seconds', 
    'Request latency for cronjob requests', 
    ['endpoint'], 
    registry=registry
)

cronjob_last_success_timestamp = Gauge(
    'cronjob_last_success_timestamp', 
    'Timestamp of the last successful cronjob execution', 
    ['status_code', 'endpoint']
)

cronjob_last_failure_timestamp = Gauge(
    'cronjob_last_failure_timestamp',
    'Timestamp of the last failed cronjob execution',
    ['status_code', 'endpoint'],
)
