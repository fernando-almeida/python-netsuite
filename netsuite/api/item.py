"""
Product search
"""
from netsuite.service import (
    ItemSearchBasic,
    SearchMultiSelectField,
    RecordRef
)
from netsuite.utils import (
    get_record_by_type,
    search_records_using
)


def get_product(internal_id):
    return get_record_by_type('inventoryItem', internal_id)


def list_products(internal_ids):
    id_references = [RecordRef(internalId=id) for id in internal_ids]
    item_search = ItemSearchBasic(
        internalId=SearchMultiSelectField(
            searchValue=id_references,
            operator='anyOf'
        ))
    result = search_records_using(item_search)
    r = result.body.searchResult
    if r.status.isSuccess:
        return r.recordList.record
