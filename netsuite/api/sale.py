from netsuite.client import client, passport, app_info
from netsuite.service import (
    Address,
    CashSale,
    CashSaleItem,
    CashSaleItemList,
    SalesOrder,
    SalesOrderItem,
    SalesOrderItemList,
    RecordRef,
    ListOrRecordRef
)
from netsuite.api.customer import get_or_create_customer
from netsuite.test_data import (
    prepare_address,
    prepare_customer_data,
)
from netsuite.utils import get_record_by_type

from datetime import datetime
from lxml import etree


def get_item_reference(item):
    return RecordRef(
        internalId=item.internal_id,
        type='inventoryItem'
    )


def create_cashsale_salesorder(data, sale_models):
    addressee = '%s %s' % (data.first_name, data.last_name)
    shipping_address = prepare_address(addressee, data.shipping_address)
    billing_address = prepare_address(addressee, data.billing_address)

    raw_item = [
        sale_models['item'](
            item=get_item_reference(item),
            quantity=item.quantity
        ) for item in data.line_items
    ]
    item_list = sale_models['item_list'](item=raw_item)
    customer = get_or_create_customer(prepare_customer_data(data))

    sale_data = {
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
    if sale_models['sale'] == SalesOrder:
        sale_data['shipAddressList'] = ListOrRecordRef(internalId=2)

    sale = sale_models['sale'](**sale_data)
    response = client.service.add(sale, _soapheaders={
        'passport': passport,
        'applicationInfo': app_info
    })
    # print(etree.tostring(client.service._binding.create_message('add', sale, _soapheaders={
    #    'passport': passport,
    #    'applicationInfo': app_info
    # })))
    r = response.body.writeResponse
    if r.status.isSuccess:
        record_type = None
        if sale_models['sale'] == SalesOrder:
            record_type = 'salesOrder'
        else:
            record_type = 'cashSale'
        result =  get_record_by_type(record_type, r.baseRef.internalId)
        return True, result
    return False, r


def create_cashsale(data):
    sale_models = {
        'sale': CashSale,
        'item': CashSaleItem,
        'item_list': CashSaleItemList
    }
    return create_cashsale_salesorder(data, sale_models)


def create_salesorder(data):
    sale_models = {
        'sale': SalesOrder,
        'item': SalesOrderItem,
        'item_list': SalesOrderItemList
    }
    return create_cashsale_salesorder(data, sale_models)
