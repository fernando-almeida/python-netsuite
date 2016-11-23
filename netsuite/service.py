from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
import ns_config

# cache WSDL and XSD for a year
cache = SqliteCache(timeout=60*60*24*365)
transport = Transport(cache=cache)
client = Client(ns_config.WSDL_URL, transport=transport)


Passport = client.get_type('ns1:Passport')
RecordRef = client.get_type('ns1:RecordRef')
ApplicationInfo = client.get_type('ns5:ApplicationInfo')
CustomerSearch = client.get_type('ns14:CustomerSearch')
ItemSearchBasic = client.get_type('ns6:ItemSearchBasic')
SearchPreferences = client.get_type('ns5:SearchPreferences')
SearchBooleanField = client.get_type('ns1:SearchBooleanField')
CashSale = client.get_type('ns20:CashSale')
Customer = client.get_type('ns14:Customer')
