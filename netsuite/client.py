from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport

import zeep.helpers

class NetsuiteApiClient(object):
  """ Abstract requests made to the Netsuite API"""

  class ModelWrapper(object):

    def __init__(self, client, model_aliases = None):
      """
      Constructor

      Args:
        client: SOAP client instance
        model_aliases: Dictionary with aliases for SOAP client types
      """
      self.client = client
      self.model_aliases = model_aliases

    def get_type(self, type_name):
      """
      Get the class object to create new instances of a given type name

      Args:
        type_name: Name of the type to create

      Returns:
        Class object to create instances of the given type name
      """
      if self.model_aliases and type_name in self.model_aliases:
        type_name = self.model_aliases[type_name]

      return self.client.get_type(type_name)

    def __getattr__(self, propertyName):
      return self.get_type(propertyName)

    def __getitem__(self, propertyName):
      return self.__getattr__(propertyName)


  # Default preferences to be used when searching
  DEFAULT_SEARCH_PREFERENCES_PARAMS = {
    "bodyFieldsOnly": True,
    "returnSearchColumns": True,
    "pageSize": 750 # 1000
  }

  # Default preferences to be used
  DEFAULT_PREFERENCES_PARAMS = {
    "warningAsError" : True,
    "disableMandatoryCustomFieldValidation": False,
    "disableSystemNotesForCustomFields": False,
    "ignoreReadOnlyFields": False,
    "runServerSuiteScriptAndTriggerWorkflows": True
  }

  DEFAULT_SOAP_CLIENT_CONFIG = {
    'cache': {
      'path': '/tmp/sqlite.db',
      'timeout': 31536000, # cache WSDL and XSD for a year (60*60*24*365)
    }
  }

  def __init__(self, config, serialize_object_class=dict, search_preferences = None, preferences = None):
    """
    Constructor
    
    Args:
      config: Dictionary with information on how to connect to the Netsuite API
      serialize_object_class: Class to use for serializing returned objects (optional)
      search_preferences: Default search preferences to use (optional)
      preferences: Default general preferences to use (optional)
    """

    # cache WSDL and XSD for a year
    ns_config = config["api"]
    self.soap_client_config = config["soapClient"] if "soapClient" in config else self.DEFAULT_SOAP_CLIENT_CONFIG
    cache = None
    if 'cache' in self.soap_client_config:
      cache = SqliteCache(**self.soap_client_config['cache'])

    transport = Transport(cache=cache)
    self.client = Client(ns_config['wsdlUrl'], transport=transport)

    # Register namespace alias
    if 'namespacePrefixes' in self.soap_client_config:
      for prefix, namespace in self.soap_client_config['namespacePrefixes'].items():
        self.client.set_ns_prefix(prefix, namespace)

    # Alias for the relevant WSDL service to use
    self.service = self.client.service

    models_aliases = self.soap_client_config["modelsAliases"] if "modelsAliases" in self.soap_client_config else None
    self.model_wrapper = self.ModelWrapper(self.client, models_aliases)

    self.app_info = self.models.ApplicationInfo(applicationId=ns_config['appId'])
    self.passport = self._make_passport(ns_config)
    self.search_preferences = self.models.SearchPreferences(**search_preferences) if search_preferences else self.models.SearchPreferences(**self.DEFAULT_SEARCH_PREFERENCES_PARAMS)
    self.preferences = self.models.Preferences(**preferences) if preferences else self.models.Preferences(**self.DEFAULT_PREFERENCES_PARAMS)

    # Specify the class to be used when serializing objects
    self.serialize_object_class = serialize_object_class
    self.logged_in = False


  def __getattr__(self, propertyName):
    """
    Get a computed property by it's name

    Args:
      propertyName: Name of the computed property to retrieve

    Returns:
      Property value
    """
    if propertyName == 'models':
      return self.model_wrapper

    raise Exception("Property name {0} does not exist".format(propertyName))

  def _make_passport(self, ns_config):
    """
    Create a passport instance to be used on requests

    Args:
      ns_config: Dictionary with configuration parameters

    Returns:
      Instance of Passport
    """
    role = self.models.RecordRef(internalId=ns_config['role'])
    return self.models.Passport(email=ns_config['email'],
                                password=ns_config['password'],
                                account=ns_config['account'],
                                role=role)


  def get_type(self, type_name):
    """
    Get the class object to create new instances of a given type name

    Args:
      type_name: Name of the type to create

    Returns:
      Class object to create instances of the given type name
    """

    return self.model_wrapper.get_type(type_name)

  def new_instance(self, type_name, params = None):
    """
    Create a new instance of the given type name initialized with params

    Args:
      type_name: Name of the type to instantiate
      params: Paramaters to use when instantiating the type (optional)

    Returns:
      New instance of the given type optionally initialized with params
    """
    typeClass = self.get_type(type_name)
    return typeClass() if not params else typeClass(**params)

  def get_factory(self, namespace):
    """
    Get a factory instance to generate types of a given namespace

    Args:
      namespace: Name of the namespace to build a type factory from

    Returns:
      Type factory instance for the given namespace
    """

    return self.client.type_factory(namespace)

  def login():
      self.passport = self._make_passport()
      loginResponse = client.service.login(passport=passport,
                  _soapheaders={'applicationInfo': self.app_info})

      self.logged_in = loginResponse.status.isSuccess
      if not self.logged_in:
        raise "Unsuccessful login"

      return client

  def logout(self):
    """
    Logout the user

    Returns:
      True if successful or False otherwise
    """

    if not self.logged_in:
      raise "Cannot logout because user is not logged in"

    logoutResponse = self.service.logout(self.models.LogoutRequest())
    self.logged_in = logoutResponse.status.isSuccess
    if self.logged_in:
      raise "Could not logout the user"

    return True

  def is_logged_in(self):
    """
    Check if the login has already been done

    Returns:
      True if the user has logged in or False otherwise
    """
    return self.logged_in

  def set_search_preferences(self, search_preferences):
    """
    Change the preferences for all search related queries 

    Args:
      search_preferences: The new search preferences to used as default in future requests
    """
    self.search_preferences = search_preferences
    

  def set_search_preferences(self, preferences):
    """
    Change the general preferences for operations

    Args:
      preferences: The new general preferences to be used as default in future requests
    """
    self.preferences = preferences
    

  def get_record_by_type(self, type, internal_id):
    """
    Get a single record of a given type based on its internal identifier

    Args:
      type: Type of record
      internal_id: Internal identificer that matches the instance

    Returns:
      Instance of the given type that has the given internal identifier or None otherwise
    """
    record = self.models.RecordRef(internalId=internal_id, type=type)
    response = self.service.get(record,
        _soapheaders={
            'applicationInfo': self.app_info,
            'passport': self.passport,
        }
    )
    r = response.body.readResponse
    if not r.status.isSuccess:
      raise Exception("Could not retrieve Record of type={0} with internalId={1}".format(type, internal_id))
    
    if self.serialize_object_class:
      return zeep.helpers.serialize_object(r.record, self.serialize_object_class)

    return r.record

  def search(self, searchtype, search_preferences = None):
    """
    Perform a custom search for records on the 1st page using the provided search type instance

    Args:
      search_type: Instance of a search type describing the filters to be applied
      search_preferences: Search preferences to use for this search (optional)

    Throws:
      Exception if not successful

    Returns:
      Instance of a SearchResult
    """
    #print(self.search_preferences)
    #print(self.app_info)
    #print(self.passport)

    search_preferences = search_preferences or self.search_preferences

    response = self.service.search(
        searchRecord=searchtype,
        _soapheaders={
            'searchPreferences': search_preferences,
            'applicationInfo': self.app_info,
            'passport': self.passport,
        }
    )


    searchResult = response.body.searchResult
    
    if not searchResult.status.isSuccess:
      raise "Search result was not successful"

    
    return searchResult

  
  def search_all(self, searchtype, search_preferences = None):
    """
    Perform a custom search for all records using the provided search type instance

    Args:
      search_type: Instance of a search type describing the filters to be applied
      search_preferences: Search preferences to use for this search (optional)

    Throws:
      Exception if not successful

    Returns:
      List of search results found
    """

    search_preferences = search_preferences or self.search_preferences

    results = []

    nextPage = 1
    print('Fetching page', nextPage)
    response = self.service.search(
        searchRecord=searchtype,
        _soapheaders={
            'searchPreferences': search_preferences,
            'applicationInfo': self.app_info,
            'passport': self.passport,
        }
    )

    searchResult = response.body.searchResult
    
    if not searchResult.status.isSuccess:
      raise "Search result was not successful"

    if searchResult.recordList is None:
      return []

    results = searchResult.recordList.record;
    print('Found {0} results in page {1}'.format(len(results), nextPage))

    nextPage = searchResult.pageIndex + 1
    while nextPage < searchResult.totalPages:
      
      print('Fetching page', nextPage)
      # nextSearchType = SearchMoreWithIdRequest(searchId = searchResult.searchId, pageIndex= nextPage)

      response = self.service.searchMoreWithId(
        searchId = searchResult.searchId, pageIndex= nextPage,
        _soapheaders={
            'searchPreferences': search_preferences,
            'applicationInfo': self.app_info,
            'passport': self.passport,
        }
      )

      searchResult = response.body.searchResult
    
      if not searchResult.status.isSuccess:
        raise "Search result was not successful for page {0}".format(nextPage)

      newRecords = searchResult.recordList.record
      print('Found {0} results in page {1}'.format(len(newRecords), nextPage))
      # Append search results records
      results += newRecords;

      nextPage += 1
      if nextPage >= searchResult.totalPages:
        break
    
    if self.serialize_object_class:
      return [zeep.helpers.serialize_object(zeep_object, self.serialize_object_class) for zeep_object in results]

    return results

  def get_values_for_field(self, record_type, field, preferences = None):
    """
    Get all eligible values for a particular field description
    """
    preferences = preferences or self.preferences

    # getSelectValue(fieldDescription: ns0:GetSelectValueFieldDescription, pageIndex: xsd:int, _soapheaders={passport: ns0:Passport, tokenPassport: ns0:TokenPassport, applicationInfo: ns4:ApplicationInfo, partnerInfo: ns4:PartnerInfo, preferences: ns4:Preferences}) -> header: {documentInfo: ns4:DocumentInfo}, body: ns4:getSelectValueResponse
    response = self.service.getSelectValue(
      fieldDescription=self.models.GetSelectValueFieldDescription(recordType=record_type, field=field),
      pageIndex=1,
      _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
      }
    )

    print(response)



  def update(self, record, preferences = None):
    """
    Update a single record of a given type
    
    Args:
      record: The instance of a given record type to update
      preferences: Preferences to be used upon the record update (optional)
    
    Returns:
      True if the update was successful of false otherwise   
    """

    """ Returns instance of UpdateResponse =>
          obj.writeResponse {
            status { statusDetail {
              code { },
              message,
              type
            }, 
            isSuccess
            },
            baseRef { name }  
    """

    preferences = preferences or self.preferences

    response = self.service.update(
        record=record,
        _soapheaders={
            'preferences': preferences,
            'applicationInfo': self.app_info,
            'passport': self.passport,
      }
    )

    print('Response', response)
    return response.body.writeResponse.status.isSuccess;

    
    # Update a list of recorsd
  def update_records(self, records, preferences = None):
    """
    Update a list of records

    Args:
      records: List of records to update

    Returns:
      True if the update was successful of false otherwise
    """

    preferences = preferences or self.preferences

    response = self.service.updateList(
        record=records,
        _soapheaders={
            'preferences': preferences,
            'applicationInfo': self.app_info,
            'passport': self.passport,
      }
    )

  def add(record):
    """
    Add a new entity records

    Args:
      record: New entity record to add
    """
    raise NotImplementedError

  def addList(records):
    """
    Add a list of new entities records

    Args:
      records: List of new record entities to add
    """
    raise NotImplementedError

  def addList(records):
    """
    Add a list of new entities records

    Args:
      records: List of new record entities to add
    """
    raise NotImplementedError

  def asyncAddList(records):
    """
    Add a list of new entities records asynchronously

    Args:
      records: List of new record entities to add
    """
    raise NotImplementedError

  def asyncDeleteList(records, reason):
    """
    Delete a list of entitiy records asynchronously

    Args:
      records: List of records to delete asynchronously
      reason: Justification for deleting the records
    """
    raise NotImplementedError