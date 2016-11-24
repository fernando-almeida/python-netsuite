#!/usr/bin/env python3
import unittest

from netsuite.api.customer import get_or_create_customer
from netsuite.api.cashsale import create_cashsale

from netsuite.test_data import (
    data,
    prepare_customer_data,
)


class NetsuiteTestCase(unittest.TestCase):

    def test_customer(self):
        customer_data = prepare_customer_data(data)
        customer = get_or_create_customer(customer_data)
        self.assertEqual(customer.firstName, 'Joe')
        self.assertTrue(customer.email.endswith('gmail.com'))

    def test_cashsale(self):
        cash_sale = create_cashsale(data)
        self.assertEqual(cash_sale.ccName, 'J. Bloggs')


if __name__ == "__main__":
     unittest.main()
