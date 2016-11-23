from netsuite.client import client
from netsuite.service import CashSale


cash_sale = CashSale(
    entity='test'
)


def test_cashsale(o):
    """
    Map Smartbuy data to NetSuite CashSale
    """
    return {
        'itemList': [ # CashSaleItem
                {'item': {'externalId': 'SOME_SKU'},
                 'quantity': 'SOME_QUANTITY'},
                # ...
        ],
        'entity': {},  # customer
        'email': o.email,
        'shipAddressList': [{
                'addressee': '%s %s' % (o.first_name, o.last_name),
                'phone': '%s %s' % (o.phone_country, o.phone_number),
                'addr1': o.address_line_1,
                'addr2': o.address_line_2,
                'state': o.region,
                'city': o.city,
                'zip': o.zip_code,
                'country': '__unitedStates'
        }],

        # 'billAddressList' 'billingAddress': ...

        'ccExpireDate': '{:02}/{}' % (
                                o.expiration_date_month +\
                                o.expiration_date_year),
        'ccNumber': o.credit_card_number,
        'ccName': o.credit_card_owner,
        'ccSecurityCode': o.cvc2
    }
