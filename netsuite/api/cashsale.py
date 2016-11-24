from netsuite.client import client
from netsuite.service import (
    Address,
    CashSale,
    CashSaleItem,
    CashSaleItemList,
    RecordRef
)
from netsuite.api.customer import get_or_create_customer
from netsuite.test_data import prepare_address, prepare_customer_data


def get_item_reference(item):
    return RecordRef(
        internalId=item.internal_id,
        type='inventoryItem'
    )


def create_cashsale(data):
    addressee = '%s %s' % (data.first_name, data.last_name)
    shipping_address = prepare_address(addressee, data.shipping_address)
    billing_address = prepare_address(addressee, data.billing_address)

    raw_item = [
        CashSaleItem(
            item=get_item_reference(item),
            quantity=item.quantity
        ) for item in data.line_items
    ]
    item_list = CashSaleItemList(item=raw_item)

    cash_sale_data = {
        'itemList': item_list,
        'entity': get_or_create_customer(prepare_customer_data(data)),
        'email': data.email,
        'shipAddressList': [Address(**shipping_address)],
        'billAddressList': [Address(**billing_address)],

        'ccExpireDate': '{:02}/{}' % (
                                data.expiration_date_month +\
                                data.expiration_date_year),
        'ccNumber': data.credit_card_number,
        'ccName': data.credit_card_owner,
        'ccSecurityCode': data.cvc2
    }
    cash_sale = CashSale(**cash_sale_data)
    response = client.service.add(cash_sale)
    r = response.body.writeResponse
    if r.status.isSuccess:
        print(r)
        return r
