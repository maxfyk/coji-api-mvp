import geohash
from prometheus_client import (
    Gauge
)

from statics.constants import DECODE_LOGS_DATA_LABELS


class StatsLogger():
    def __init__(self):
        self.decode_request_labels_dict = {k: k.replace('-', '_') for k in DECODE_LOGS_DATA_LABELS}
        self.decode_request = self.get_new_decode_request_counter()

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

        out_data = {}
        for k, v in self.decode_request_labels_dict.items():
            out_data[v] = decode_data[k]
        self.decode_request.labels(*out_data.values()).inc(1)

    def get_new_decode_request_counter(self):
        return Gauge('decode_request', 'details about code decode request',
                       self.decode_request_labels_dict.values())


stats_logger = StatsLogger()
