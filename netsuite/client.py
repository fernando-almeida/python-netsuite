from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport

import zeep.helpers

from netsuite.api.types import AsyncStatusType

import logging

logger = logging.getLogger(__name__)

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

  def __init__(self, config, serialize_object_class=dict, search_preferences = None, preferences = None, logger = None):
    """
    Constructor
    
    Args:
      config: Dictionary with information on how to connect to the Netsuite API
      serialize_object_class: Class to use for serializing returned objects (optional)
      search_preferences: Default search preferences to use (optional)
      preferences: Default general preferences to use (optional)
    """

    self.logger = logger or logging.getLogger(__name__)

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
    Perform a custom search for record on the 1st page using the provided search type instance

    Args:
      search_type: Instance of a search type describing the filters to be applied
      search_preferences: Search preferences to use for this search (optional)

    Throws:
      Exception if not successful

    Returns:
      Instance of a SearchResult
    """

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
      raise Exception("Search result was not successful")

    
    return searchResult


  def asyncSearch(self, searchtype, search_preferences = None):
    """
      Perform an asynchronous search for record on the 1st page using the provided search type instance

    Args:
      search_type: Instance of a search type describing the filters to be applied
      search_preferences: Search preferences to use for this search (optional)

    Throws:
      Exception if not successful

    Returns:
      Instance of a SearchResult
    """
    search_preferences = search_preferences or self.search_preferences

    response = self.service.asyncSearch(
        searchRecord=searchtype,
        _soapheaders={
            'searchPreferences': search_preferences,
            'applicationInfo': self.app_info,
            'passport': self.passport,
        }
    )

    if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
      raise Exception(response.body.asyncStatusResult)

    return asyncStatusResult

  
  def search_all(self, searchtype, search_preferences = None):
    """
    Perform a custom search for all record using the provided search type instance

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

    nextPage = 1
    
    self.logger.debug('Fetching page {0}'.format(nextPage))

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
      return record

    record = searchResult.recordList.record;
    self.logger.debug('Found {0} of {1} record in page {2}/{3}'.format(len(record), searchResult.totalRecords, nextPage, searchResult.totalPages))

    nextPage = searchResult.pageIndex + 1
    while nextPage <= searchResult.totalPages:
      
      self.logger.debug('Fetching page {0}'.format(nextPage))
      # nextSearchType = SearchMoreWithIdRequest(searchId = searchResult.searchId, pageIndex= nextPage)

      response = self.service.searchMoreWithId(
        searchId = searchResult.searchId,
        pageIndex= nextPage,
        _soapheaders={
            'searchPreferences': search_preferences,
            'applicationInfo': self.app_info,
            'passport': self.passport,
        }
      )

      searchResult = response.body.searchResult
    
      if not searchResult.status.isSuccess:
        raise Exception("Search result was not successful for page {0} {1}".format(nextPage, searchResult.status))

      newRecords = searchResult.recordList.record
      self.logger.debug('Found {0} of {1} record in page {2}/{3}'.format(len(record), searchResult.totalRecords, nextPage, searchResult.totalPages))
      
      # Append search result record
      record += newRecords;

      nextPage += 1
    
    self.logger.info('Retrieved a total of {0} record from the search'.format(len(record)))

    if self.serialize_object_class:
      return [zeep.helpers.serialize_object(zeep_object, self.serialize_object_class) for zeep_object in record]

    return record

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

    raise NotImplementedError("Not implemented")



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

    if not response.body.writeResponse.status.isSuccess:
      raise Exception(response.body.writeResponse.status)
    
    # Update a list of records
  def updateList(self, record, preferences = None):
    """
    Update a list of record

    Args:
      record: List of records to update

    Returns:
      True if the update was successful of false otherwise
    """

    preferences = preferences or self.preferences

    response = self.service.updateList(
        record=record,
        _soapheaders={
            'preferences': preferences,
            'applicationInfo': self.app_info,
            'passport': self.passport,
      }
    )

    if not response.body.writeResponseList.status.isSuccess:
      raise Exception(response.body.writeResponseList.status)

    return response.body.writeResponseList.writeResponse

  def add(self, record, preferences = None):
    """
    Add a new entity record

    Args:
      record: New entity record to add
      preferences: General preferences
    """
    
    preferences = preferences or self.preferences

    response = self.service.add(
      record=record,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if not response.body.writeResponse.status.isSuccess:
          raise Exception(response.body.writeResponse.status)

  def addList(self, record, preferences = None):
    """
    Add a list of new entities record

    Args:
      record: List of new record entities to add
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.addList(
      record=record,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if not response.body.writeResponseList.status.isSuccess:
      raise Exception(response.body.writeResponseList.status)

    return response.writeResponseList.writeResponse

  def asyncAddList(self, record, preferences = None):
    """
    Add a list of new entities record asynchronously

    Args:
      record: List of new record entities to add
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.asyncAddList(
      record=record,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
      raise Exception(response.body.asyncStatusResult)

    return asyncStatusResult

  def asyncDeleteList(self, names, reason, preferences = None):
    """
    Delete a list of entitiy record asynchronously

    Args:
      record: List of record to delete asynchronously
      reason: Justification for deleting the record
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.asyncDeleteList(
      baseRef=names,
      deletionReason=reason,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
      raise Exception(response.body.asyncStatusResult)

    return asyncStatusResult

  def asyncInitializeList(self, record, preferences = None):
    """
    Initialiaze a list of with a list of record

    Args:
      record: List of record to initialize the list with
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.asyncInitializeList(
      record=record,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
      raise Exception(response.body.asyncStatusResult)

    return asyncStatusResult

  def asyncUpdateList(self, record, preferences = None):
    """
    Update a list of with a set of record

    Args:
      record: Set of record to update the list with
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.asyncUpdateList(
      record=record,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
      raise Exception(response.body.asyncStatusResult)

    return asyncStatusResult

  def asyncUpsertList(self, record, preferences = None):
    """
    Upsert a list of with a list of record

    Args:
      record: List of record to update the list with
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.asyncUpsertList(
      record=record,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if response.body.asyncStatusResult.status == AsyncStatusType.FAILED:
      raise Exception(response.body.asyncStatusResult)

    return asyncStatusResult

  def checkAsyncStatus(self, jobId, preferences = None):
    """
    Check the execution status of an asynchronous job

    Args:
      jobId: Asynchronous job identifier
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.checkAsyncStatus(
      jobId=jobId,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    return response.body.asyncStatusResult


  def getAsyncResult(self, jobId, pageIndex = 1, preferences = None):
    """
    Get the result for an asynchronous job

    Args:
      jobId: Asynchronous job identifier
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.checkAsyncStatus(
      jobId=jobId,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    return response.body.asyncResult


  def delete(self, baseRef,  deletionReason = None, preferences = None):
    """
    Delete a record from Oracle's Netsuite

    Args:
      baseRef: Reference to a record to delete
      deletionReason: Reason for deleting the record
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.delete(
      baseRef=baseRef,
      deletionReason=deletionReason,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if not response.body.writeResponse.status.isSuccess:
          raise Exception(response.body.writeResponse.status)

    return response.body

  def deleteList(self, baseRef,  deletionReason = None, preferences = None):
    """
    Delete a list of references to record from Oracle's Netsuite

    Args:
      baseRef: List of references to record to be deleted
      deletionReason: Reason for deleting the record
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.deleteList(
      baseRef=baseRef,
      deletionReason=deletionReason,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if not response.body.writeResponseList.status.isSuccess:
      raise Exception(response.body.writeResponseList.status)

    return response.writeResponseList.writeResponse


  def getList(self, recordRefs, preferences = None):
    """
    Upsert a list of with a list of record

    Args:
      recordRefs: List of record references to get lists from
      preferences: General preferences
    """
    preferences = preferences or self.preferences

    response = self.service.getList(
      baseRef=recordRefs,
     _soapheaders={
        'passport': self.passport,
        'applicationInfo': self.app_info,
        'preferences': preferences
    })

    if not response.body.readResponseList.status.isSuccess:
          raise Exception(response.body.writeResponse.status)

    return response.body




class NetsuiteApiBatchClient(object):
  """
  Oracle's Netsuite API Batch Client
  """

  class BatchableOperation(object):

    def __init__(self, batch_client, base_client, operation_name):
      self.batch_client = batch_client
      self.base_client = base_client
      self.operation_name = operation_name
      self.operation_category = self.batch_client.governance_model.get_operation_category(operation_name)
      self.operation_constraints = self.batch_client.governance_model.get_operation_constraints(self.operation_name)
      self.property_name = 'record' if self.operation_category != 'delete' else 'baseRef'

    def __call__(self, *args, **kwargs):
      """
      Call base method
      """

      num_queued_operations = len(self.batch_client.queued_operations[self.operation_category])

      should_execute_batch = "record_count" in self.operation_constraints and \
                  num_queued_operations == self.operation_constraints["record_count"]["value"]

      if should_execute_batch:
        self.batch_client._execute(self.operation_category)

      # TODO Currently, not handling disparate preferences
      preferences = kwargs["preferences"] if "preferences" in kwargs else None

      # Queue the operation for next execution
      record = []


      if self.property_name in kwargs:
        record = kwargs[self.property_name] if isinstance(kwargs[self.property_name], list) else [kwargs[self.property_name]]
      elif len(args) > 0:
        record = args[0] if isinstance(args[0], list) else [args[0]]
      else:
        raise Exception("Property \"{0}\" not found and args={1} kwargs={2}".format(self.property_name, args, kwargs))


      max_record_count = self.operation_constraints["record_count"]["value"]
      should_execute_batch = "record_count" in self.operation_constraints and \
                             (num_queued_operations + len(record)) >= max_record_count 

      if should_execute_batch:
        num_remaining_batch_records = max_record_count - num_queued_operations
        if num_remaining_batch_records > 0:
          logger.info("Queueing remaining {0} record for a total of {1}".format(num_remaining_batch_records, max_record_count))
          self.batch_client.queued_operations[self.operation_category] += record[:num_remaining_batch_records]
          del record[:num_remaining_batch_records]

        self.batch_client._execute(self.operation_category)

      if record:
        self.batch_client.queued_operations[self.operation_category] += record
        logger.info("Queued {0} record(s) category={1} ({2} of {3})".format(len(record), self.operation_category, num_queued_operations + 1, max_record_count))


  def __init__(self, governance_model, record_type_predicate = None, last_resort = False, dry_run = False, *args, **kwargs):
    """
    Constructor

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
      raise Exception("Netsuite API client does not support the attribute={0}".format(name) )

    if self.governance_model.is_operation_batchable(name):
      operation_category = self.governance_model.get_operation_category(name)
      return NetsuiteApiBatchClient.BatchableOperation(self, NetsuiteApiClient, name)

    return getattr(self.client, name)


  def execute(self):
    """
    Execute all pending batch operations
    """
    for operation_category, record in self.queued_operations.items():
      if not record:
        continue

      self._execute(operation_category)    

  def _execute(self, operation_category):
    """
    Execute a batch operation for all record belonging to an operation category

    Args:
      operation_category: Category of the operation to batch execute
    """

    batch_method_name = operation_category + 'List'
    operation_category_records = self.queued_operations[operation_category]
    logger.info("Executing batch operation {0} for category {1} with {2} record(s)".format(batch_method_name, operation_category, len(operation_category_records)))
    if not self.dry_run:
      getattr(self.client, batch_method_name)(record=operation_category_records)
    del self.queued_operations[operation_category][:]


  def __del__(self):
    """
    Destructor
    """
    
    if self.last_resort:
      logger.info("Executing last resort batch operations")
      self.execute()
