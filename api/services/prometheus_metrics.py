from flask import Blueprint
from flask import Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, multiprocess

prometheus_metrics = Blueprint('prometheus-metrics', __name__)


@prometheus_metrics.route('/metrics', methods=['get'])
def prometheus_metrics_get():
    """Scrape metrics"""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)
