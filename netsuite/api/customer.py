"""
Add a customer, lookup customer if adding fails with UNIQUE_CUST_ID_REQD.
Proceed to CashSale.
"""

from netsuite.client import client
from netsuite.test_data import data
from netsuite.service import (Customer,
                              CustomerSearch,
                              RecordRef)


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
    record = RecordRef(internalId=internal_id, type='customer')
    response = client.service.get(record)
    r = response.body.readResponse
    if r.status.isSuccess:
        return r.record


def lookup_customer(customer_data):
    pass

    # customer_search = CustomerSearch(**customer_data)
    # response = client.service.get(record)
    # print(response)
    # r = response.body.readResponse
    # if r.status.isSuccess:
    #     return r.record.internalId
