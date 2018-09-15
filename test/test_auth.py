"""Netsuite authentication test module."""
import unittest

import logging.config


from netsuite.client import (NetsuiteApiClient,
                             parse_api_config,
                             build_api_config_dict_from_env)

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})


class NetsuiteAuthTestCase(unittest.TestCase):
    """Netsuite authentication testcase."""

    def test_tba_auth_from_env(self):
        """Test TBA."""
        api_config = parse_api_config()
        client = NetsuiteApiClient(
            api_config=api_config)
        search_type = client.models['Common:EmployeeSearchBasic']()
        client.search(search_type)

    def test_tba_auth_from_dict(self):
        """Test TBA from dict."""
        config = build_api_config_dict_from_env()
        api_config = parse_api_config(config)
        client = NetsuiteApiClient(
            api_config=api_config)
        search_type = client.models['Common:EmployeeSearchBasic']()
        client.search(search_type)

if __name__ == "__main__":
    unittest.main()
