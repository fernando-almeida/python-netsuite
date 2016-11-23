from zeep import Client
import ns_config


def login_client():
    client = Client(ns_config.WSDL_URL)

    Record = client.get_type('ns1:RecordRef')
    AppInfo = client.get_type('ns5:ApplicationInfo')
    Passport = client.get_type('ns1:Passport')

    role = Record(internalId=ns_config.NS_ROLE)
    app_info = AppInfo(applicationId=ns_config.NS_APPID)
    passport = Passport(email=ns_config.NS_EMAIL,
                        password=ns_config.NS_PASSWORD,
                        account=ns_config.NS_ACCOUNT,
                        role=role)

    login = client.service.login(passport=passport,
                _soapheaders={'applicationInfo': app_info})

    print('Login Response: ', login.status)
    return client, passport, app_info

