"""
Add a customer, lookup customer if adding fails with UNIQUE_CUST_ID_REQD.
Proceed to CashSale.
"""

from connect import login_client
from test_data import data

client, passport, app_info = login_client()

customer_data = {
    'lastName': data.first_name,
    'firstName': data.last_name,
    'phone': '%s%s' % (data.phone_country, data.phone_number),
    'email': data.email
}


def get_or_create_customer(customer_data):
    Customer = client.get_type('ns14:Customer')

    customer = Customer(**customer_data)
    # add a customer
    response = client.service.add(customer)
    print(response)
    r = response.body.writeResponse
    if r.status.isSuccess:
        internal_id = r.baseRef.internalId
        print('Customer added successfully with #%s' % internal_id)
        return internal_id
    else:
        return lookup_customer(customer_data)


def lookup_customer(customer_data):
    CustomerSearch = client.get_type('ns14:CustomerSearch')
    customer_search = CustomerSearch(**customer_data)
    #
    # response = client.service.get(record)
    # print(response)
    # r = response.body.readResponse
    # if r.status.isSuccess:
    #     return r.record.internalId


CashSale = client.get_type('ns20:CashSale')
cash_sale = CashSale(
    entity=
)