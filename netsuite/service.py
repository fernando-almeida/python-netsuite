from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport

import ns_config

# cache WSDL and XSD for a year
cache = SqliteCache(timeout=60*60*24*365)
transport = Transport(cache=cache)
client = Client(ns_config.WSDL_URL, transport=transport)

model = client.get_type

Passport = model('ns1:Passport')
RecordRef = model('ns1:RecordRef')
ApplicationInfo = model('ns5:ApplicationInfo')
CustomerSearchBasic = model('ns6:CustomerSearchBasic')
ItemSearchBasic = model('ns6:ItemSearchBasic')
SearchPreferences = model('ns5:SearchPreferences')
SearchBooleanField = model('ns1:SearchBooleanField')
SearchStringField = model('ns1:SearchStringField')
SearchStringFieldOperator = model('ns2:SearchStringFieldOperator')
CashSale = model('ns20:CashSale')
Customer = model('ns14:Customer')
SearchMultiSelectField = model('ns1:SearchMultiSelectField')
