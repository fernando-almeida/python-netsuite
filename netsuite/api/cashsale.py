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
    o = data

    raw_item = [
        CashSaleItem(
            item=get_item_reference(item),
            quantity=item.quantity
        ) for item in o.line_items
    ]
    item_list = CashSaleItemList(item=raw_item)
    import ipdb;ipdb.set_trace()
    return {
        'itemList': item_list,
        'entity': {},  # customer
        'email': o.email,
        'shipAddressList': [],

        # 'billAddressList' 'billingAddress': ...

        'ccExpireDate': '{:02}/{}' % (
                                o.expiration_date_month +\
                                o.expiration_date_year),
        'ccNumber': o.credit_card_number,
        'ccName': o.credit_card_owner,
        'ccSecurityCode': o.cvc2
    }
