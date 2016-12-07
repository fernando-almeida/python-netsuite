from netsuite.client import client, app_info, passport
from netsuite.service import (
    RecordRef,
    SearchPreferences
)


class obj(object):
    """Dictionary to object utility.

    >>> d = {'b': {'c': 2}}
    >>> x = obj(d)
    >>> x.b.c
    2
    """
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x)
                   if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b)
                   if isinstance(b, dict) else b)


def get_record_by_type(type, internal_id):
    record = RecordRef(internalId=internal_id, type=type)
    response = client.service.get(record,
        _soapheaders={
            'applicationInfo': app_info,
            'passport': passport,
        }
    )
    r = response.body.readResponse
    if r.status.isSuccess:
        return r.record


def search_records_using(searchtype):
    search_preferences = SearchPreferences(
        bodyFieldsOnly=False,
        returnSearchColumns=True,
        pageSize=20
    )

    return client.service.search(
        searchRecord=searchtype,
        _soapheaders={
            'searchPreferences': search_preferences,
            'applicationInfo': app_info,
            'passport': passport,
        }
    )
