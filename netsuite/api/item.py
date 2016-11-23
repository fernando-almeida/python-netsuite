"""
Product search
"""
from netsuite.client import client, passport, app_info
from netsuite.service import (ItemSearchBasic,
                              SearchPreferences,
                              SearchMultiSelectField,
                              RecordRef)
from netsuite.utils import get_record_by_type

def get_product(internal_id):
    return get_record_by_type('inventoryItem', internal_id)


def list_products(internal_ids):
    id_references = [RecordRef(internalId=id) for id in internal_ids]
    item_search = ItemSearchBasic(internalId=SearchMultiSelectField(searchValue=id_references,
                                                                    operator='anyOf'
                                                                    ))
    search_preferences = SearchPreferences(bodyFieldsOnly=False,
                                           returnSearchColumns=True,
                                           pageSize=20)

    result = client.service.search(searchRecord=item_search, _soapheaders={
        'searchPreferences': search_preferences,
        'applicationInfo': app_info,
        'passport': passport,
    })

    if result['body']['searchResult']['status']['isSuccess']:
        return result['body']['searchResult']['recordList']['record']
