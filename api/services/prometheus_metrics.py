import os
import glob

[os.remove(f) for f in glob.glob('/app/prometheus_metrics/*')]
os.environ['prometheus_multiproc_dir'] = '/app/prometheus_metrics'

from modules import stats_logger
from flask import Blueprint
from flask import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, multiprocess

prometheus_metrics = Blueprint('prometheus-metrics', __name__)


@prometheus_metrics.route('/metrics', methods=['get'])
def prometheus_metrics_get():
    """Scrape metrics"""
    try:
        stats_logger.registry.collect()
        resp = Response(generate_latest(stats_logger.registry), mimetype=CONTENT_TYPE_LATEST)
        stats_logger.decode_request.clear()
        return resp
    except Exception as e:
        print(e)
        return ''
