Python Netsuite
===============
Netsuite Python Toolkit for SuiteTalk SOAP API.

Copy `ns_config.py.txt` into `ns_config.py` and add your credentials.

Example usage
-------------
::

    from connect import login_client
    client, passport, app_info = login_client()

    Record = client.get_type('ns1:RecordRef')

    # print names of customers
    for i in range(100):
        record = Record(internalId=i, type='customer')
        response = client.service.get(record)
        r = response.body.readResponse
        if r.status.isSuccess:
            print(r.record.firstName, '', r.record.lastName)

NetSuite Documentation
----------------------
* `SuiteTalk Documentation <http://www.netsuite.com/portal/developers/resources/suitetalk-documentation.shtml>`_
* `Schema Browser (CashSale example) <http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_2/schema/record/cashsale.html?mode=package>`_


