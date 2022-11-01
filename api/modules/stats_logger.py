import geohash
from prometheus_client import (
    Counter
)

from statics.constants import DECODE_LOGS_DATA_LABELS


class StatsLogger():
    def __init__(self):
        self.decode_request = Counter('decode_request', 'details about code decode request',
                                      DECODE_LOGS_DATA_LABELS)

    def add_decode_request(self, decode_data):
        """Save decode details to prometheus"""
        geohash_val = None
        if decode_data['lat'] and decode_data['lon']:
            geohash_val = geohash.encode(
                latitude=decode_data['lat'],
                longitude=decode_data['lon'],
                precision=7
            )
        del decode_data['lat']
        del decode_data['lon']
        decode_data['location'] = geohash_val

        self.decode_request.labels(*decode_data.values()).inc(1)


stats_logger = StatsLogger()
