import ns_config
from netsuite.service import (client,
                              RecordRef,
                              ApplicationInfo,
                              Passport)


def login():
    role = RecordRef(internalId=ns_config.NS_ROLE)
    app_info = ApplicationInfo(applicationId=ns_config.NS_APPID)
    passport = Passport(email=ns_config.NS_EMAIL,
                        password=ns_config.NS_PASSWORD,
                        account=ns_config.NS_ACCOUNT,
                        role=role)

    login = client.service.login(passport=passport,
                _soapheaders={'applicationInfo': app_info})

    print('Login Response: ', login.status)
    return client, passport, app_info


client, passport, app_info = login()
