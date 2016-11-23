"""
Benchmark user journeys of 2,000 customers
"""

from connect import login_client
from collections import Counter
from pprint import pprint
from time import time

print('Logging in.')
client, passport, app_info = login_client()


def benchmark(customer_range=2000):
    print('Getting user journey statistics on first %s customers' % customer_range)
    print('This could take an hour.')
    now = time()
    Record = client.get_type('ns1:RecordRef')
    paths = []
    for i in range(customer_range):
        record = Record(internalId=i, type='customer')
        response = client.service.get(record)
        r = response.body.readResponse
        if r.status.isSuccess:
            path = r.record.clickStream
            paths.append(path)
    print('Completed in %s seconds.' % (time() - now))
    pprint(Counter(paths))

benchmark()
