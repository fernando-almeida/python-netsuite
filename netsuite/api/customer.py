"""
Add a customer, lookup customer if adding fails with UNIQUE_CUST_ID_REQD.
Proceed to CashSale.
"""
from netsuite.client import client
from netsuite.utils import (
    get_record_by_type,
    search_records_using
)
from netsuite.service import (
    Customer,
    CustomerSearchBasic,
    SearchStringField
)


def get_or_create_customer(customer_data):
    customer = Customer(**customer_data)
    response = client.service.add(customer)
    print(response)
    r = response.body.writeResponse
    if r.status.isSuccess:
        return r.baseRef.internalId
    elif r.status.statusDetail[0].code == 'UNIQUE_CUST_ID_REQD':
        return lookup_customer_by_name_and_email(customer_data)


def get_customer(internal_id):
    return get_record_by_type('customer', internal_id)


def lookup_customer_by_name_and_email(customer_data):
    name_and_email = {k: v for k, v in customer_data.items()
                      if k in ['firstName', 'lastName', 'email']}
    search_fields = {k: SearchStringField(searchValue=v, operator='is')
                     for k, v in name_and_email(customer_data)}
    customer_search = CustomerSearchBasic(**search_fields)
    response = search_records_using(customer_search)

    r = response.body.searchResult
    if r.status.isSuccess:
        records = r.recordList.record
        if len(records) > 0:
            return records[0]
