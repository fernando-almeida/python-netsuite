#!/usr/bin/env python3
import unittest

from netsuite.api.customer import get_or_create_customer
from netsuite.test_data import customer_data


class NetsuiteTestCase(unittest.TestCase):

    def test_customer(self):
        customer = get_or_create_customer(customer_data)
        self.assertEqual(customer.firstName, 'Joe')
        self.assertTrue(customer.email.endswith('gmail.com'))


if __name__ == "__main__":
     unittest.main()
