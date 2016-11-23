"""
Benchmark user journeys of 2,000 customers
"""
from netsuite.client import client
from netsuite.service import RecordRef

from collections import Counter
from pprint import pprint
from time import time


def benchmark(customer_range=2000):
    print('Getting user journey statistics on first %s customers' % customer_range)
    print('This could take an while.')
    now = time()
    paths = []
    for i in range(customer_range):
        record = RecordRef(internalId=i, type='customer')
        response = client.service.get(record)
        r = response.body.readResponse
        if r.status.isSuccess:
            path = r.record.clickStream
            paths.append(path)
    print('Completed in %s seconds.' % (time() - now))
    pprint(Counter(paths))

benchmark()
