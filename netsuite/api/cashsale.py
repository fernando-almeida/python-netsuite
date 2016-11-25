from netsuite.client import client, passport, app_info
from netsuite.service import (
    Address,
    CashSale,
    CashSaleItem,
    CashSaleItemList,
    RecordRef
)
from netsuite.api.customer import get_or_create_customer
from netsuite.test_data import prepare_address, prepare_customer_data
from datetime import datetime


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
    customer = get_or_create_customer(prepare_customer_data(data))
    print('****************customer**********', customer)
    cash_sale_data = {
        'itemList': item_list,
        'entity': RecordRef(internalId=customer.internalId),
        'email': data.email,
        'shippingAddress': Address(**shipping_address),
        'billingAddress': Address(**billing_address),
        'ccExpireDate': datetime(
            int(data.expiration_date_year),
            int(data.expiration_date_month),
            1
        ),
        'ccNumber': data.credit_card_number,
        'ccName': data.credit_card_owner,
        'ccSecurityCode': data.cvc2,
        'shippingCost': data.shipping_cost

    }
    cash_sale = CashSale(**cash_sale_data)
    response = client.service.add(cash_sale, _soapheaders={
        'passport': passport,
        'applicationInfo': app_info
    })
    print(etree.tostring(client.service._binding.create_message('add', cash_sale, _soapheaders={
        'passport': passport,
        'applicationInfo': app_info
    })))
    r = response.body.writeResponse
    print(r)
    if r.status.isSuccess:
        return r
