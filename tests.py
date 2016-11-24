#!/usr/bin/env python3
import unittest

from netsuite.api.customer import get_or_create_customer
from netsuite.api.cashsale import create_address
from netsuite.test_data import (
    data,
    prepare_customer_data,
    prepare_address_data,
)


class NetsuiteTestCase(unittest.TestCase):

    def test_customer(self):
        customer_data = prepare_customer_data(data)
        customer = get_or_create_customer(customer_data)
        self.assertEqual(customer.firstName, 'Joe')
        self.assertTrue(customer.email.endswith('gmail.com'))

    def test_cashsale(self):
        addressee = '%s %s' % (data.first_name, data.last_name)
        address = data.billing_address
        address_data = prepare_address_data(addressee, address)
        print(address_data)
        address = create_address(address_data)
        self.assertEqual(address.addr1, '777 Green Avenue')


if __name__ == "__main__":
     unittest.main()
