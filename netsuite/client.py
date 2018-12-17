"""API Client."""

import time
import hashlib
import hmac
import uuid
import base64
import os

from collections import namedtuple

import logging

from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
import zeep.helpers

from .api.types import AsyncStatusType, SignatureAlgorithm

LOGGER = logging.getLogger(__name__)

DEFAULT_HASH_ALGORITHM = 'sha256'

ALLOWED_HASH_ALGORITHMS = ['sha1', 'sha256']

HASH_ALGORITHM_NAMES_MAP = {
    'sha1': SignatureAlgorithm.HMAC_SHA1,
    'sha256': SignatureAlgorithm.HMAC_SHA256
}

NAMESPACE_ALIAS_TEMPLATES = {
    "Accounting": "urn:accounting_{}.lists.webservices.netsuite.com",
    "AccountingTypes": "urn:types.accounting_{}.lists.webservices.netsuite.com",
    "Bank": "urn:bank_{}.transactions.webservices.netsuite.com",
    "Common": "urn:common_{}.platform.webservices.netsuite.com",
    "CommonTypes": "urn:types.common_{}.platform.webservices.netsuite.com",
    "Communication": "urn:communication_{}.general.webservices.netsuite.com",
    "CommunicationTypes": "urn:types.communication_{}.general.webservices.netsuite.com",
    "Core": "urn:core_{}.platform.webservices.netsuite.com",
    "CoreTypes": "urn:types.core_{}.platform.webservices.netsuite.com",
    "Customers": "urn:customers_{}.transactions.webservices.netsuite.com",
    "CustomersTypes": "urn:types.customers_{}.transactions.webservices.netsuite.com",
    "CustomersTransactions": "customers_{}.transactions.webservices.netsuite.com",
    "Customization": "urn:customization_{}.setup.webservices.netsuite.com",
    "CustomizationTypes": "urn:types.customization_{}.setup.webservices.netsuite.com",
    "DemandPlanningTransactions": "urn:demandplanning_{}.transactions.webservices.netsuite.com",
    "DemandPlanningTransactionsTypes": "urn:types.demandplanning_{}.transactions.webservices.netsuite.com",
    "Employees": "urn:employees_{}.lists.webservices.netsuite.com",
    "EmployeeTypes": "urn:types.employees_{}.lists.webservices.netsuite.com",
    "EmployeesTransactions": "urn:employees_{}.transactions.webservices.netsuite.com",
    "EmployeesTransactionsTypes": "urn:types.employees_{}.transactions.webservices.netsuite.com",
    "FaultsTypes": "urn:types.faults_{}.platform.webservices.netsuite.com",
    "FileCabinet": "urn:filecabinet_{}.documents.webservices.netsuite.com",
    "FileCabinetTypes": "urn:types.filecabinet_{}.documents.webservices.netsuite.com",
    "Financial": "urn:financial_{}.transactions.webservices.netsuite.com",
    "FinancialTypes": "urn:types.financial_{}.transactions.webservices.netsuite.com",
    "General": "urn:general_{}.transactions.webservices.netsuite.com",
    "Inventory": "urn:inventory_{}.transactions.webservices.netsuite.com",
    "InventoryTypes": "urn:types.inventory_{}.transactions.webservices.netsuite.com",
    "Website": "urn:website_{}.lists.webservices.netsuite.com",
    "WebsiteTypes": "urn:types.website_{}.lists.webservices.netsuite.com",
    "Marketing": "urn:marketing_{}.lists.webservices.netsuite.com",
    "MarketingTypes": "urn:types.marketing_{}.lists.webservices.netsuite.com",
    "Messages": "urn:messages_{}.platform.webservices.netsuite.com",
    "PurchasesTransactions": "urn:purchases_{}.transactions.webservices.netsuite.com",
    "PurchasesTransactionsTypes": "urn:types.purchases_{}.transactions.webservices.netsuite.com",
    "Relationships": "urn:relationships_{}.lists.webservices.netsuite.com",
    "RelationshipTypes": "urn:types.relationships_{}.lists.webservices.netsuite.com",
    "Sales": "urn:sales_{}.transactions.webservices.netsuite.com",
    "SalesTypes": "urn:types.sales_{}.transactions.webservices.netsuite.com",
    "Scheduling": "urn:scheduling_{}.activities.webservices.netsuite.com",
    "SchedulingTypes": "urn:types.scheduling_{}.activities.webservices.netsuite.com",
    "Support": "urn:support_{}.lists.webservices.netsuite.com",
    "SupportTypes": "urn:types.support_{}.lists.webservices.netsuite.com",
    "SupplyChain": "urn:supplychain_{}.lists.webservices.netsuite.com",
    "SupplyChainTypes": "urn:types.supplychain_{}.lists.webservices.netsuite.com"
}

Passport = namedtuple('Passport', [
    'email',
    'password',
    'account',
    'role'])

TokenPassport = namedtuple('TokenPassport', [
    'account',
    'consumer_key',
    'consumer_secret',
    'token_id',
    'token_secret',
    'hash_algorithm'
])

ApiConfig = namedtuple('ApiConfig', [
    'wsdl_url',
    'application_id',
    'passport_type',
    'passport'
])

def build_api_config_dict_from_env():
    """Create API coniguration dict from env vars."""
    config = {
        "wsdlUrl": os.getenv('NETSUITE.WSDL_URL'),
        "applicationId": os.getenv('NETSUITE.APPLICATION_ID'),
        "passportType": os.getenv('NETSUITE.PASSPORT_TYPE')
    }
    passport_type = config['passportType'].lower().strip()
    if passport_type == 'tba':
        config["tokenPassport"] = {
            "account": os.getenv('NETSUITE.TOKEN_PASSPORT.ACCOUNT'),
            "consumerKey": os.getenv('NETSUITE.TOKEN_PASSPORT.CONSUMER_KEY'),
            "consumerSecret": os.getenv('NETSUITE.TOKEN_PASSPORT.CONSUMER_SECRET'),
            "tokenId": os.getenv('NETSUITE.TOKEN_PASSPORT.TOKEN_ID'),
            "tokenSecret": os.getenv('NETSUITE.TOKEN_PASSPORT.TOKEN_SECRET'),
            "hashAlgorithm": os.getenv('NETSUITE.TOKEN_PASSPORT.HASH_ALGORITHM')
        }
    elif passport_type == 'nlauth':
        config["passport"] = {
            "email": os.getenv('NETSUITE.PASSPORT.EMAIL'),
            "password": os.getenv('NETSUITE.PASSPORT.PASSWORD'),
            "role": os.getenv('NETSUITE.PASSPORT.ROLE'),
            "account": os.getenv('NETSUITE.PASSPORT.ACCOUNT')
        }
    else:
        raise Exception("Invalid passport type {}".format(passport_type))
    return config


def parse_api_config(config={}):
    """Parse API configuration from dict.

    Args:
        config (dict): API configuration dictionary
    Returns:
        ApiConfig instance
    """
    wsdl_url = os.getenv("NETSUITE.WSDL_URL") or config['wsdlUrl']
    application_id = os.getenv("NETSUITE.APPLICATION_ID") or config['applicationId']
    passport_type = (os.getenv("NETSUITE.PASSPORT_TYPE") or config['passportType']).lower().strip()
    passport = None
    if passport_type == 'nlauth':
        passport = Passport(
            email=os.getenv("NETSUITE.PASSPORT.EMAIL") or config['passport']['email'],
            password=os.getenv("NETSUITE.PASSPORT.PASSWORD") or config['passport']['password'],
            account=os.getenv("NETSUITE.PASSPORT.ACCOUNT") or config['passport']['account'],
            role=os.getenv("NETSUITE.PASSPORT.ROLE") or config['passport']['role'])
    elif passport_type == 'tba':
        passport = TokenPassport(
            account=os.getenv("NETSUITE.TOKEN_PASSPORT.ACCOUNT") or config['tokenPassport']['account'],
            consumer_key=os.getenv("NETSUITE.TOKEN_PASSPORT.CONSUMER_KEY") or config['tokenPassport']['consumerKey'],
            consumer_secret=os.getenv("NETSUITE.TOKEN_PASSPORT.CONSUMER_SECRET") or config['tokenPassport']['consumerSecret'],
            token_id=os.getenv("NETSUITE.TOKEN_PASSPORT.TOKEN_ID") or config['tokenPassport']['tokenId'],
            token_secret=os.getenv("NETSUITE.TOKEN_PASSPORT.TOKEN_SECRET") or config['tokenPassport']['tokenSecret'],
            hash_algorithm=os.getenv("NETSUITE.TOKEN_PASSPORT.HASH_ALGORITHM") or config['tokenPassport']['hashAlgorithm'])
    else:
        raise Exception('Invalid passport type {}'.format(passport_type))
    api_config = ApiConfig(
        wsdl_url=wsdl_url,
        application_id=application_id,
        passport_type=passport_type,
        passport=passport)
    return api_config

def generate_nonce():
    """Generate a nonce to be used with OAuth."""
    return ''.join([uuid.uuid1().hex, uuid.uuid4().hex])

def generate_namespace_prefixes(version):
    """Generate namespace alias.

    Args:
        version (tuple): Version
    Returns:
        Dictionary of namespace alias
    """
    return {
        alias: template.format('_'.join(version))
        for alias, template in NAMESPACE_ALIAS_TEMPLATES.items()
    }

class NetsuiteApiClient(object):
    """ Abstract requests made to Oracle Netsuite Web Services."""

    class ModelWrapper(object):
        """Model wrapper."""

        def __init__(self, netsuite_api_client, types_aliases=None):
            """Constructor.

            Args:
                netsuite_api_client: Netsuite API client instance
                types_aliases: Dictionary with aliases for SOAP client types
            """
            self.netsuite_api_client = netsuite_api_client
            self.types_aliases = types_aliases

        def get_type(self, type_name):
            """Get the class object to create new instances of a given type name.

            Args:
                type_name: Name of the type to create

            Returns:
                Class object to create instances of the given type name
            """
            if self.types_aliases and type_name in self.types_aliases:
                type_name = self.types_aliases[type_name]

            return self.netsuite_api_client.client.get_type(type_name)

        def __getattr__(self, name):
            if name in self.netsuite_api_client.namespace_prefixes:
                return self.netsuite_api_client.client.type_factory(name)

            return self.get_type(name)

        def __getitem__(self, name):
            return self.__getattr__(name)

    # Default preferences to be used when searching
    DEFAULT_SEARCH_PREFERENCES_PARAMS = {
        "bodyFieldsOnly": True,
        "returnSearchColumns": True,
        "pageSize": 750  # 1000
    }

    # Default preferences to be used
    DEFAULT_PREFERENCES_PARAMS = {
        "warningAsError": True,
        "disableMandatoryCustomFieldValidation": False,
        "disableSystemNotesForCustomFields": False,
        "ignoreReadOnlyFields": False,
        "runServerSuiteScriptAndTriggerWorkflows": True
    }

    DEFAULT_SOAP_CLIENT_CONFIG = {
        'cache': {
            'path': '/tmp/sqlite.db',
            # cache WSDL and XSD for a year (60*60*24*365)
            'timeout': 31536000,
        }
    }

    def __init__(
            self,
            api_config,
            soap_client_config=None,
            serialize_object_class=dict,
            search_preferences=None,
            preferences=None):
        """Constructor.

        Args:
            api_config: Dictionary with information on how to connect to the Netsuite API
            soap_client_config: SOAP client configuration (optional)
            serialize_object_class: Class to use for serializing returned objects (optional)
            search_preferences: Default search preferences to use (optional)
            preferences: Default general preferences to use (optional)
        """
        # cache WSDL and XSD for a year
        self.api_config = api_config
        self.soap_client_config = soap_client_config or self.DEFAULT_SOAP_CLIENT_CONFIG
        cache = None
        if 'cache' in self.soap_client_config:
            cache = SqliteCache(**self.soap_client_config.get('cache'))

        transport = Transport(cache=cache)
        self.client = Client(self.api_config.wsdl_url, transport=transport)

        # Extract WS version
        version = tuple(
            value
            for value in self.api_config.wsdl_url.split('/')[-2][1:].split('_')
            if value != '0')

        # Register namespace alias
        self.namespace_prefixes = generate_namespace_prefixes(version)
        for prefix, namespace in self.namespace_prefixes.items():
            self.client.set_ns_prefix(prefix, namespace)

        # Alias for the relevant WSDL service to use
        self.service = self.client.service

        types_aliases = self.soap_client_config.get("typesAliases", None)
        self.model_wrapper = self.ModelWrapper(
            self,
            types_aliases)

        self.application_info = self.models.Messages.ApplicationInfo(applicationId=api_config.application_id)

        self.search_preferences = self.models.Messages.SearchPreferences(
            **(search_preferences if search_preferences else self.DEFAULT_SEARCH_PREFERENCES_PARAMS))
        self.preferences = self.models.Messages.Preferences(
            **preferences) if preferences else self.models.Messages.Preferences(**self.DEFAULT_PREFERENCES_PARAMS)

        # Specify the class to be used when serializing objects
        self.serialize_object_class = serialize_object_class
        self.logged_in = False

    def __getattr__(self, property_name):
        """Get a computed property by it's name.

        Args:
            propertyName: Name of the computed property to retrieve

        Returns:
            Property value
        """
        if property_name == 'models':
            return self.model_wrapper

        raise Exception("Property name {} does not exist".format(property_name))

    def _make_token_passport(self, passport):
        """Create a token passport.

        Args:
            passport: TokenPassport config

        Returns:
            Instance of TokenPassport
        """
        nonce = generate_nonce()

        timestamp = int(round(time.time()))
        hash_algorithm_name = self.api_config.passport.hash_algorithm or DEFAULT_HASH_ALGORITHM
        if hash_algorithm_name not in HASH_ALGORITHM_NAMES_MAP:
            raise Exception('Hash algorithm {} not supported'.format(
                hash_algorithm_name))
        if hash_algorithm_name not in hashlib.algorithms_available:
            raise Exception('Hash algorithm {} not available'.format(
                hash_algorithm_name))
        hash_algorithm_impl = getattr(hashlib, hash_algorithm_name)
        base_string = '&'.join(
            [passport.account, passport.consumer_key, passport.token_id, nonce, str(timestamp)])
        key = '&'.join([passport.consumer_secret, passport.token_secret])
        signature_hash = hmac.new(key.encode(), base_string.encode(), hash_algorithm_impl)
        signature = base64.b64encode(signature_hash.digest()).decode()
        token_passport_signature = self.models.Core.TokenPassportSignature(
            signature,
            algorithm=HASH_ALGORITHM_NAMES_MAP[hash_algorithm_name]
        )
        token_passport = self.models.Core.TokenPassport(
            account=passport.account,
            consumerKey=passport.consumer_key,
            token=passport.token_id,
            nonce=nonce,
            timestamp=timestamp,
            signature=token_passport_signature)
        return token_passport

    def _make_passport(self, passport):
        """Create a passport instance to be used on requests.

        Args:
            passport: Dictionary with configuration parameters

        Returns:
            Instance of Passport
        """
        role = self.models.Core.RecordRef(internalId=passport.role)
        return self.models.Core.Passport(
            email=passport.email,
            password=passport.password,
            account=passport.account,
            role=role)

    def get_type(self, type_name):
        """Get the class object to create new instances of a given type name.

        Args:
            type_name: Name of the type to create

        Returns:
            Class object to create instances of the given type name
        """

        return self.model_wrapper.get_type(type_name)

    def new_instance(self, type_name, params=None):
        """Create a new instance of the given type name initialized with params.

        Args:
            type_name: Name of the type to instantiate
            params: Paramaters to use when instantiating the type (optional)

        Returns:
            New instance of the given type optionally initialized with params
        """
        type_class = self.get_type(type_name)
        return type_class() if not params else type_class(**params)

    def get_factory(self, namespace):
        """Get a factory instance to generate types of a given namespace.

        Args:
            namespace: Name of the namespace to build a type factory from

        Returns:
            Type factory instance for the given namespace
        """

        return self.client.type_factory(namespace)

    def login(self):
        """Perform a user login."""
        passport = self._make_passport(self.api_config.passport)
        login_response = self.client.service.login(
            passport=passport,
            _soap_headers={
                'applicationInfo': self.app_info
            })

        self.logged_in = login_response.status.isSuccess
        if not self.logged_in:
            raise Exception("Unsuccessful login")

    def logout(self):
        """Logout the user.

        Returns:
            True if successful or False otherwise
        """

        if not self.logged_in:
            raise Exception("Cannot logout because user is not logged in")

        logout_response = self.service.logout(self.models.Core.LogoutRequest())
        self.logged_in = logout_response.status.isSuccess
        if self.logged_in:
            raise Exception("Could not logout the user")

        return True

    def is_logged_in(self):
        """Check if the login has already been done.

        Returns:
            True if the user has logged in or False otherwise
        """
        return self.logged_in

    def set_search_preferences(self, search_preferences):
        """Change the preferences for all search related queries.

        Args:
            search_preferences: The new search preferences to used as default in future requests
        """
        self.search_preferences = search_preferences

    def set_preferences(self, preferences):
        """Change the general preferences for operations.

        Args:
            preferences: The new general preferences to be used as default in future requests
        """
        self.preferences = preferences

    def get_record_by_type(self, record_type, internal_id):
        """Get a single record of a given type based on its internal identifier.

        Args:
            record_type: Type of record
            internal_id: Internal identificer that matches the instance

        Returns:
            Instance of the given type that has the given internal identifier or None otherwise
        """
        record = self.models.Core.RecordRef(internalId=internal_id, type=record_type)
        soap_headers = self._build_soap_passport_header()
        response = self.service.get(
            record,
            _soapheaders=soap_headers)
        read_response = response.body.readResponse
        if not read_response.status.isSuccess:
            raise Exception(
                "Could not retrieve Record of type={} with internalId={}".format(
                    record_type, internal_id))

        if self.serialize_object_class:
            return zeep.helpers.serialize_object(read_response.record, self.serialize_object_class)

        return read_response.record

    def search(self, search_type, search_preferences=None):
        """Perform a custom search for record on the 1st page using the provided search type instance.

        Args:
            search_type: Instance of a search type describing the filters to be applied
            search_preferences: Search preferences to use for this search (optional)

        Throws:
            Exception if not successful

        Returns:
            Instance of a SearchResult
        """

        search_preferences = search_preferences or self.search_preferences
        soap_headers = {
            'searchPreferences': search_preferences,
        }
        soap_headers.update(self._build_soap_passport_header())
        response = self.service.search(
            searchRecord=search_type,
            _soapheaders=soap_headers
        )

        search_result = response.body.searchResult

        if not search_result.status.isSuccess:
            raise Exception("Search result was not successful")

        return search_result

    def async_search(self, search_type, search_preferences=None):
        """Perform an asynchronous search for record on the 1st page using the provided search type instance.

        Args:
            search_type: Instance of a search type describing the filters to be applied
            search_preferences: Search preferences to use for this search (optional)

        Throws:
            Exception if not successful

        Returns:
            Instance of a SearchResult
        """
        search_preferences = search_preferences or self.search_preferences
        soap_headers = {
            'searchPreferences': search_preferences,
        }
        soap_headers.update(self._build_soap_passport_header())
        response = self.service.asyncSearch(
            searchRecord=search_type,
            _soapheaders=soap_headers
        )

        if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
            raise Exception(response.body.asyncStatusResult)

        return response.body.asyncResult

    def search_all(self, search_type, search_preferences=None):
        """Perform a custom search for all record using the provided search type instance.

        Args:
            search_type: Instance of a search type describing the filters to be applied
            search_preferences: Search preferences to use for this search (optional)

        Throws:
            Exception if not successful

        Returns:
            List of search result record found
        """

        search_preferences = search_preferences or self.search_preferences

        record = []

        next_page = 1

        LOGGER.debug('Fetching page %d', next_page)
        soap_headers = {
            'searchPreferences': search_preferences,
        }
        soap_headers.update(self._build_soap_passport_header())
        response = self.service.search(
            searchRecord=search_type,
            _soapheaders=soap_headers
        )

        search_result = response.body.searchResult

        if not search_result.status.isSuccess:
            raise Exception("Search result was not successful")

        if search_result.recordList is None:
            return record

        record = search_result.recordList.record
        LOGGER.debug('Found %d of %d record in page %d/%d',
                     len(record),
                     search_result.totalRecords,
                     next_page,
                     search_result.totalPages)

        next_page = search_result.pageIndex + 1
        while next_page <= search_result.totalPages:
            LOGGER.debug('Fetching page %d', next_page)
            # nextSearchType = SearchMoreWithIdRequest(searchId = searchResult.searchId, pageIndex= nextPage)
            soap_headers.update(self._build_soap_passport_header())
            response = self.service.searchMoreWithId(
                searchId=search_result.searchId,
                pageIndex=next_page,
                _soapheaders=soap_headers
            )

            search_result = response.body.searchResult

            if not search_result.status.isSuccess:
                raise Exception("Search result was not successful for page {} {}".format(
                    next_page,
                    search_result.status))

            new_records = search_result.recordList.record
            LOGGER.debug('Found %d of %d records in page %d/%d',
                         len(record),
                         search_result.totalRecords,
                         next_page,
                         search_result.totalPages)

            # Append search result record
            record += new_records

            next_page += 1

        LOGGER.info(
            'Retrieved a total of %d records from the search', len(record))

        if self.serialize_object_class:
            return [zeep.helpers.serialize_object(zeep_object, self.serialize_object_class) for zeep_object in record]

        return record

    def get_values_for_field(self, record_type, field, preferences=None):
        """Get all eligible values for a particular field description."""
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())
        self.service.getSelectValue(
            fieldDescription=self.models.Core.GetSelectValueFieldDescription(
                recordType=record_type,
                field=field),
            pageIndex=1,
            _soapheaders=soap_headers
        )

        raise NotImplementedError("Not implemented")

    def update(self, record, preferences=None):
        """Update a single record of a given type.

        Args:
            record: The instance of a given record type to update
            preferences: Preferences to be used upon the record update (optional)

        Returns:
            True if the update was successful of false otherwise

        Returns instance of UpdateResponse =>
            obj.writeResponse {
            status { statusDetail {
                code { },
                message,
                type
            },
            isSuccess
            },
            base_ref { name }
        """

        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.update(
            record=record,
            _soapheaders=soap_headers
        )

        if not response.body.writeResponse.status.isSuccess:
            raise Exception(response.body.writeResponse.status)

        # Update a list of records
    def update_list(self, record, preferences=None):
        """Update a list of records.

        Args:
            record: List of records to update

        Returns:
            True if the update was successful of false otherwise
        """

        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.updateList(
            record=record,
            _soapheaders=soap_headers
        )

        if not response.body.writeResponseList.status.isSuccess:
            raise Exception(response.body.writeResponseList.status)

        return response.body.writeResponseList.writeResponse

    def add(self, record, preferences=None):
        """Add a new entity record.

        Args:
            record: New entity record to add
            preferences: General preferences
        """

        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.add(
            record=record,
            _soapheaders=soap_headers)

        if not response.body.writeResponse.status.isSuccess:
            raise Exception(response.body.writeResponse.status)

    def add_list(self, record, preferences=None):
        """Add a list of new entities record.

        Args:
            record: List of new record entities to add
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.addList(
            record=record,
            _soapheaders=soap_headers)

        if not response.body.writeResponseList.status.isSuccess:
            raise Exception(response.body.writeResponseList.status)

        return response.writeResponseList.writeResponse

    def async_add_list(self, record, preferences=None):
        """Add a list of new entities record asynchronously.

        Args:
            record: List of new record entities to add
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.asyncAddList(
            record=record,
            _soapheaders=soap_headers)

        if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
            raise Exception(response.body.asyncStatusResult)

        return response.body.asyncResult

    def async_delete_list(self, names, reason, preferences=None):
        """Delete a list of entitiy record asynchronously.

        Args:
            record: List of record to delete asynchronously
            reason: Justification for deleting the record
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.asyncDeleteList(
            base_ref=names,
            deletion_reason=reason,
            _soapheaders=soap_headers)

        if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
            raise Exception(response.body.asyncStatusResult)

        return response.body.asyncResult

    def async_initialize_list(self, record, preferences=None):
        """Initialiaze a list of with a list of record.

        Args:
            record: List of record to initialize the list with
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.asyncInitializeList(
            record=record,
            _soapheaders=soap_headers)

        if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
            raise Exception(response.body.asyncStatusResult)

        return response.body.asyncResult

    def async_update_list(self, record, preferences=None):
        """Update a list of with a set of record.

        Args:
            record: Set of record to update the list with
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.asyncUpdateList(
            record=record,
            _soapheaders=soap_headers)

        if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
            raise Exception(response.body.asyncStatusResult)

        return response.body.asyncResult

    def async_upsert_list(self, record, preferences=None):
        """Upsert a list of with a list of record.

        Args:
            record: List of record to update the list with
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.asyncUpsertList(
            record=record,
            _soapheaders=soap_headers)

        if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
            raise Exception(response.body.asyncStatusResult)

        return response.body.asyncResult

    def check_async_status(self, job_id, preferences=None):
        """Check the execution status of an asynchronous job.

        Args:
            job_id: Asynchronous job identifier
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.checkAsyncStatus(
            job_id=job_id,
            _soapheaders=soap_headers)

        return response.body.asyncResult

    def get_async_result(self, job_id, page_index=1, preferences=None):
        """Get the result for an asynchronous job.

        Args:
            job_id: Asynchronous job identifier
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.checkAsyncStatus(
            job_id=job_id,
            _soapheaders=soap_headers)

        return response.body.asyncResult

    def delete(self, base_ref, deletion_reason=None, preferences=None):
        """Delete a record from Oracle's Netsuite.

        Args:
            base_ref: Reference to a record to delete
            deletion_reason: Reason for deleting the record
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.delete(
            base_ref=base_ref,
            deletion_reason=deletion_reason,
            _soapheaders=soap_headers)

        if not response.body.writeResponse.status.isSuccess:
            raise Exception(response.body.writeResponse.status)

        return response.body

    def delete_list(self, base_ref, deletion_reason=None, preferences=None):
        """Delete a list of references to record from Oracle's Netsuite.

        Args:
            base_ref: List of references to record to be deleted
            deletion_reason: Reason for deleting the record
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.deleteList(
            base_ref=base_ref,
            deletion_reason=deletion_reason,
            _soapheaders=soap_headers)

        if not response.body.writeResponseList.status.isSuccess:
            raise Exception(response.body.writeResponseList.status)

        return response.writeResponseList.writeResponse

    def get_list(self, record_refs, preferences=None):
        """Get a list of records by their identifiers.

        Args:
            record_refs: List of record references to get lists from
            preferences: General preferences
        """
        preferences = preferences or self.preferences
        soap_headers = {
            'preferences': preferences,
        }
        soap_headers.update(self._build_soap_passport_header())

        response = self.service.getList(
            base_ref=record_refs,
            _soapheaders=soap_headers)

        if not response.body.readResponseList.status.isSuccess:
            raise Exception(response.body.writeResponse.status)

        return response.body

    def _build_soap_passport_header(self):
        """Build passport dict."""
        if self.api_config.passport_type == 'tba':
            return {
                'tokenPassport': self._make_token_passport(self.api_config.passport)
            }
        if self.api_config.passport_type == 'nlauth':
            return {
                'applicationInfo': self.application_info,
                'passport': self._make_passport(self.api_config.passport)
            }
        raise Exception(
            'Unsupported authentication type {}'.format(self.api_config.passport_type))


class NetsuiteApiBatchClient(object):
    """Oracle's Netsuite API Batch Client."""

    class BatchableOperation(object):
        """Batchable operation."""

        def __init__(self, batch_client, base_client, operation_name):
            """Constructor."""
            self.batch_client = batch_client
            self.base_client = base_client
            self.operation_name = operation_name
            self.operation_category = self.batch_client.governance_model.get_operation_category(
                operation_name)
            self.operation_constraints = self.batch_client.governance_model.get_operation_constraints(
                self.operation_name)
            self.property_name = 'record' if self.operation_category != 'delete' else 'base_ref'

        def __call__(self, *args, **kwargs):
            """Call base method."""

            num_queued_operations = len(
                self.batch_client.queued_operations[self.operation_category])

            should_execute_batch = "record_count" in self.operation_constraints and \
                num_queued_operations == self.operation_constraints["record_count"]["value"]

            if should_execute_batch:
                self.batch_client._execute(self.operation_category)

            # TODO Currently, not handling disparate preferences
            # preferences = kwargs.pop("preferences", None)

            # Queue the operation for next execution
            record = []

            if self.property_name in kwargs:
                record = kwargs[self.property_name] if isinstance(
                    kwargs[self.property_name], list) else [kwargs[self.property_name]]
            elif args:
                record = args[0] if isinstance(args[0], list) else [args[0]]
            else:
                raise Exception("Property \"{}\" not found and args={} kwargs={}".format(
                    self.property_name, args, kwargs))

            max_record_count = self.operation_constraints["record_count"]["value"]
            should_execute_batch = "record_count" in self.operation_constraints and \
                (num_queued_operations + len(record)) >= max_record_count

            if should_execute_batch:
                num_remaining_batch_records = max_record_count - num_queued_operations
                if num_remaining_batch_records > 0:
                    LOGGER.info("Queueing remaining %d records for a total of %d",
                                num_remaining_batch_records,
                                max_record_count)
                    self.batch_client.queued_operations[self.operation_category] += record[:num_remaining_batch_records]
                    del record[:num_remaining_batch_records]

                self.batch_client._execute(self.operation_category)

            if record:
                self.batch_client.queued_operations[self.operation_category] += record
                LOGGER.info("Queued %d record(s) category=%s (%d of %d)",
                            len(record),
                            self.operation_category,
                            num_queued_operations + 1,
                            max_record_count)

    def __init__(self, governance_model, record_type_predicate=None, last_resort=False, dry_run=False, *args, **kwargs):
        """Constructor.

        Args:
            governance_model: The governance model from which decisions should be based on
            record_type_predicate: Predicate that checks whether a given record type should be batched (optional)
        """
        self.client = NetsuiteApiClient(*args, **kwargs)

        # Store a reference to the governance model
        self.governance_model = governance_model

        # Record type batch selector
        self.record_type_predicate = record_type_predicate or (lambda x: True)

        self.dry_run = dry_run

        # Try to execute batch operations before the object is delete
        self.last_resort = last_resort

        # Dictionary to keep track of the different operation types
        self.queued_operations = {}
        for operation_category in self.governance_model.get_batchable_operation_categories():
            self.queued_operations[operation_category] = []

    def __getattr__(self, name):
        if not hasattr(self.client, name):
            raise Exception("Netsuite API client does not support the attribute={}".format(name))

        if self.governance_model.is_operation_batchable(name):
            # operation_category = self.governance_model.get_operation_category(name)
            return NetsuiteApiBatchClient.BatchableOperation(self, NetsuiteApiClient, name)

        return getattr(self.client, name)

    def execute(self):
        """Execute all pending batch operations."""
        for operation_category, record in self.queued_operations.items():
            if not record:
                continue
            self._execute(operation_category)

    def _execute(self, operation_category):
        """Execute a batch operation for all record belonging to an operation category.

        Args:
            operation_category: Category of the operation to batch execute
        """

        batch_method_name = operation_category + 'List'
        operation_category_records = self.queued_operations[operation_category]
        LOGGER.info("Executing batch operation %s for category %s with %d record(s)",
                    batch_method_name,
                    operation_category,
                    len(operation_category_records))
        if not self.dry_run:
            getattr(self.client, batch_method_name)(record=operation_category_records)
        del self.queued_operations[operation_category][:]

    def __del__(self):
        """Destructor."""

        if self.last_resort:
            LOGGER.info("Executing last resort batch operations")
            self.execute()
