from netsuite.client import client
from netsuite.service import (
    Address,
    CashSale,
    CashSaleItem,
    CashSaleItemList,
    RecordRef
)
from netsuite.api.customer import get_or_create_customer

'''
cash_sale = CashSale(
    entity='test'
)
'''

def get_item_reference(item):
    return RecordRef(
        internalId=item.internal_id,
        type='inventoryItem'
    )


def create_address(address_data):
    address = Address(**address_data)
    response = client.service.add(address)
    r = response.body.writeResponse
    if r.status.isSuccess:
        return r.baseRef.internalId


def create_cashsale(data):
    """
    Map Smartbuy data to NetSuite CashSale
    """
    raw_item = [
        CashSaleItem(
            item=get_item_reference(item),
            quantity=item.quantity
        ) for item in data.line_items
    ]
    item_list = CashSaleItemList(item=raw_item)

    return {
        'itemList': item_list,
        'entity': {},  # customer
        'email': data.email,
        'shipAddressList': [],

        # 'billAddressList' 'billingAddress': ...

        'ccExpireDate': '{:02}/{}' % (
                                data.expiration_date_month +\
                                data.expiration_date_year),
        'ccNumber': data.credit_card_number,
        'ccName': data.credit_card_owner,
        'ccSecurityCode': data.cvc2
    }
