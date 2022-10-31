import geohash

from prometheus_client import (
    CollectorRegistry,
    Counter,
    push_to_gateway
)


def add_decode(decode_data):
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
    data_labels = [k.replace('-', '_') for k in decode_data.keys()]

    registry = CollectorRegistry()
    c = Counter('decode_request', 'details about code decode request',
                data_labels, registry=registry)
    c.labels(decode_data.values()).inc(1)
    push_to_gateway('pushgateway:9091', job='decode_request',
                    registry=registry)  # push data to pushgateway
