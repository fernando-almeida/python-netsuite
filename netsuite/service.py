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
SearchMultiSelectField = model('ns1:SearchMultiSelectField')
Customer = model('ns14:Customer')
Address = model('ns6:Address')
Country = model('ns7:Country')

CashSale = model('ns20:CashSale')
CashSaleItem = model('ns20:CashSaleItem')
CashSaleItemList = model('ns20:CashSaleItemList')

SalesOrder = model('ns20:SalesOrder')
SalesOrderItem = model('ns20:SalesOrderItem')
SalesOrderItemList = model('ns20:SalesOrderItemList')
