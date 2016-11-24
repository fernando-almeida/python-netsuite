from netsuite.client import client
from netsuite.service import (
    CashSale,
    Address,
)
from netsuite.utils import get_record_by_type
from netsuite.api.customer import get_or_create_customer


def get_address(internal_id):
    return get_record_by_type('address', internal_id)


def create_address(address_data):
    address = Address(**address_data)
    response = client.service.add(address)
    r = response.body.writeResponse
    if r.status.isSuccess:
        internal_id = r.baseRef.internalId
    print(response)
    return get_address(internal_id)


#cash_sale = CashSale(entity='test')


def create_cashsale(data):
    """
    Map Smartbuy data to NetSuite CashSale
    """
    o = data

    return {
        'itemList': [ # CashSaleItem
                {'item': {'externalId': 'SOME_SKU'},
                 'quantity': 'SOME_QUANTITY'},
                # ...
        ],
        'entity': get_or_create_customer(o),  # customer
        'email': o.email,
        'shipAddressList': [],
        'billAddressList': ['billingAddress'],

        'ccExpireDate': '{:02}/{}' % (
                                o.expiration_date_month +\
                                o.expiration_date_year),
        'ccNumber': o.credit_card_number,
        'ccName': o.credit_card_owner,
        'ccSecurityCode': o.cvc2
    }
