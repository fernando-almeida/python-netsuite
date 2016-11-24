"""
Add a customer, lookup customer if adding fails with UNIQUE_CUST_ID_REQD.
Proceed to CashSale.
"""

from netsuite.client import client
from netsuite.test_data import data
from netsuite.utils import (
    get_record_by_type,
    search_records_using
)
from netsuite.service import (
    Customer,
    CustomerSearchBasic,
    SearchStringField
)

customer_data = {
    'lastName': data.first_name,
    'firstName': data.last_name,
    'phone': '%s%s' % (data.phone_country, data.phone_number),
    'email': data.email
}


def get_or_create_customer(customer_data):
    customer = Customer(**customer_data)
    # add a customer
    response = client.service.add(customer)
    print(response)
    r = response.body.writeResponse
    if r.status.isSuccess:
        internal_id = r.baseRef.internalId
        print('Customer added successfully with #%s' % internal_id)
        return internal_id
    elif r.status.statusDetail[0].code == 'UNIQUE_CUST_ID_REQD':
        return lookup_customer(customer_data)


def get_customer(internal_id):
    return get_record_by_type('customer', internal_id)


def lookup_customer(customer_data):
    d = {}
    for k, v in customer_data.items():
        if k == 'phone':
            continue
        d[k] = SearchStringField(searchValue=v, operator='is')

    customer_search = CustomerSearchBasic(**d)
    response = result = search_records_using(customer_search)

    r = response.body.searchResult
    if r.status.isSuccess:
        records = r.recordList.record
        if len(records) > 0:
            return records[0]
