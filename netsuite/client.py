import ns_config
from netsuite.service import (client,
                              RecordRef,
                              ApplicationInfo,
                              Passport)


def make_passport():
    role = RecordRef(internalId=ns_config.NS_ROLE)
    return Passport(email=ns_config.NS_EMAIL,
                    password=ns_config.NS_PASSWORD,
                    account=ns_config.NS_ACCOUNT,
                    role=role)


def login():
    app_info = ApplicationInfo(applicationId=ns_config.NS_APPID)
    passport = make_passport()
    login = client.service.login(passport=passport,
                _soapheaders={'applicationInfo': app_info})

    print('Login Response: ', login.status)
    return client, app_info


passport = make_passport()
client, app_info = login()
