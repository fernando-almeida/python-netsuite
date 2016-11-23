from zeep import Client
import ns_config

client = Client(ns_config.WSDL_URL)

Passport = client.get_type('ns1:Passport')
RecordRef = client.get_type('ns1:RecordRef')
ApplicationInfo = client.get_type('ns5:ApplicationInfo')
CustomerSearch = client.get_type('ns14:CustomerSearch')
ItemSearchBasic = client.get_type('ns6:ItemSearchBasic')
SearchPreferences = client.get_type('ns5:SearchPreferences')
SearchBooleanField = client.get_type('ns1:SearchBooleanField')
CashSale = client.get_type('ns20:CashSale')
Customer = client.get_type('ns14:Customer')
SearchMultiSelectField = client.get_type('ns1:SearchMultiSelectField')