from zeep import Client


def login_client():
    client = Client(WSDL_URL)

    Record = client.get_type('ns1:RecordRef')
    AppInfo = client.get_type('ns5:ApplicationInfo')
    Passport = client.get_type('ns1:Passport')

    role = Record(internalId=NS_ROLE)
    app_info = AppInfo(applicationId=NS_APPID)
    passport = Passport(email=NS_EMAIL,
                        password=NS_PASSWORD,
                        account=NS_ACCOUNT,
                        role=role)

    login = client.service.login(passport=passport,
                _soapheaders={'applicationInfo': app_info})

    print('Login Response: ', login.status)
    return client, passport, app_info

