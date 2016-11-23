from zeep import Client
import config


def login_client():
    client = Client(config.WSDL_URL)

    Record = client.get_type('ns1:RecordRef')
    AppInfo = client.get_type('ns5:ApplicationInfo')
    Passport = client.get_type('ns1:Passport')

    role = Record(internalId=config.NS_ROLE)
    app_info = AppInfo(applicationId=config.NS_APPID)
    passport = Passport(email=config.NS_EMAIL,
                        password=config.NS_PASSWORD,
                        account=config.NS_ACCOUNT,
                        role=role)

    login = client.service.login(passport=passport,
                _soapheaders={'applicationInfo': app_info})

    print('Login Response: ', login.status)
    return client, passport, app_info

