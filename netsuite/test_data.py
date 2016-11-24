from netsuite.utils import obj

test_data = {
    'line_items': [
		{'internal_id': 21, 'quantity': 1},
		{'internal_id': 22, 'quantity': 2}
	],
	'first_name': 'Joe',
	'last_name': 'Bloggs',
	'phone_country': '1',
	'phone_number': '777777777',
	'email': 'fmalina@gmail.com',
	'password': 'ovcaaaa',
	'marketing_agreement': True,

	'address_line_1': '777 Green Avenue',
	'address_line_2': 'Spring Hill',
	'city': 'Springfield',
	'region': 'OR',
	'zip_code': '121212',
	'country': 'United States',

	'billing_address_line_1': '777 Green Avenue',
	'billing_address_line_2': 'Spring Hill',
	'billing_city': 'Springfield',
	'billing_region': 'OR',
	'billing_zip_code': '121212',
	'billing_country': 'United States',

	'credit_card_number': '4444333322221111',
	'credit_card_owner': 'J. Bloggs',
	'expiration_date_month': '1',
	'expiration_date_year': '2018',
	'cvc2': '333'
}

data = obj(test_data)

customer_data = {
    'firstName': data.first_name,
    'lastName': data.last_name,
    'phone': '%s%s' % (data.phone_country, data.phone_number),
    'email': data.email
}

address_data = {
    'addressee': '%s %s' % (data.first_name, data.last_name),
    'addr1': data.address_line_1,
    'addr2': data.address_line_2,
    'state': data.region,
    'city': data.city,
    'zip': data.zip_code,
    'country': '__unitedStates'
}
