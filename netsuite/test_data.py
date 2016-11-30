from netsuite.utils import obj

test_data = {
    'line_items': [
		{'internal_id': 165, 'quantity': 1}
	],
	'first_name': 'Joe',
	'last_name': 'Bloggs',
	'phone_number': '777777777',
	'email': 'fmalina@gmail.com',
	'password': 'ovcaaaa',
	'marketing_agreement': True,
    'shipping_address': {
	    'address_line_1': '777 Green Avenue',
	    'address_line_2': 'Spring Hill',
	    'city': 'Springfield',
	    'region': 'OR',
	    'zip_code': '12121',
	    'country': 'United States'
    },
	'credit_card_number': '4444333322221111',
	'credit_card_owner': 'J. Bloggs',
	'expiration_date_month': '1',
	'expiration_date_year': '2018',
	'cvc2': '333',
	'shipping_cost': 7.99
}
test_data['billing_address'] = test_data['shipping_address']

data = obj(test_data)


def prepare_customer_data(data):
    return {
        'firstName': data.first_name,
        'lastName': data.last_name,
        'phone': data.phone_number,
        'email': data.email
    }


def prepare_address(addressee, address):
    return {
        'addressee': addressee,
        'addr1': address.address_line_1,
        'addr2': address.address_line_2,
        'state': address.region,
        'city': address.city,
        'zip': address.zip_code.upper(),
        # 'country': '_unitedStates'
    }
