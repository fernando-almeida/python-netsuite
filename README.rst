Python Netsuite
===============
Netsuite Python Toolkit for SuiteTalk SOAP API.

Example usage
-------------
Copy :code:`ns_config.py.txt` into :code:`ns_config.py` and update with your credentials.

.. code:: python

    from netsuite.client import client
    from netsuite.api.customer import get_customer

    # print names of first 100 customers
    for internal_id in range(100):
        customer = get_customer(internal_id)
        if customer:
            print(customer.firstName, customer.lastName)

NetSuite Documentation
----------------------
* `SuiteTalk Documentation <http://www.netsuite.com/portal/developers/resources/suitetalk-documentation.shtml>`_
* `Schema Browser (CashSale example) <http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_2/schema/record/cashsale.html?mode=package>`_


