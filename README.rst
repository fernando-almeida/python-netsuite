Python Netsuite
===============
Netsuite Python Toolkit for SuiteTalk SOAP API.

Example usage
-------------
Copy :code:`ns_config.py.txt` into :code:`ns_config.py` and update with your credentials.

.. code:: python

    from netsuite.client import client
    from netsuite.service import RecordRef


    def get_customer_name(internal_id):
        record = RecordRef(internalId=internal_id, type='customer')
        response = client.service.get(record)
        r = response.body.readResponse
        if r.status.isSuccess:
            return '%s %s' % (r.record.firstName, r.record.lastName)


    # print names of first 100 customers
    for internal_id in range(100):
        print(get_customer_name(internal_id))

NetSuite Documentation
----------------------
* `SuiteTalk Documentation <http://www.netsuite.com/portal/developers/resources/suitetalk-documentation.shtml>`_
* `Schema Browser (CashSale example) <http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_2/schema/record/cashsale.html?mode=package>`_


