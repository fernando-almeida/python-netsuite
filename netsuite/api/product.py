"""
Product search
"""
from netsuite.connect import login_client
from lxml import etree

client, passport, app_info = login_client()


def find_products():
    ItemSearch = client.get_type('ns6:ItemSearchBasic')
    SearchBooleanField = client.get_type('ns1:SearchBooleanField')
    item_search = ItemSearch(isInactive=SearchBooleanField(searchValue=True))
    SearchPreferences = client.get_type('ns5:SearchPreferences')
    search_preferences = SearchPreferences(bodyFieldsOnly=False,
                                           returnSearchColumns=True,
                                           pageSize=20)
    print('raw xml')
    print(etree.tostring(client.service._binding.create_message('search', item_search, _soapheaders={
        'searchPreferences': search_preferences,
        'applicationInfo': app_info,
        'passport': passport
    })))

    result = client.service.search(searchRecord=item_search, _soapheaders={
        'searchPreferences': search_preferences,
        'applicationInfo': app_info,
        'passport': passport,
    })
    print('result:')
    print(result)
