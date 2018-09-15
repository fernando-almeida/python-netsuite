NETSUITE_NAMESPACE_PREFIXES = {
    "Accounting": "urn:accounting_2016_2.lists.webservices.netsuite.com",
    "AccountingTypes": "urn:types.accounting_2016_2.lists.webservices.netsuite.com",
    "Bank": "urn:bank_2016_2.transactions.webservices.netsuite.com",
    "Common": "urn:common_2016_2.platform.webservices.netsuite.com",
    "CommonTypes": "urn:types.common_2016_2.platform.webservices.netsuite.com",
    "Communication": "urn:communication_2016_2.general.webservices.netsuite.com",
    "CommunicationTypes": "urn:types.communication_2016_2.general.webservices.netsuite.com",
    "Core": "urn:core_2016_2.platform.webservices.netsuite.com",
    "CoreTypes": "urn:types.core_2016_2.platform.webservices.netsuite.com",
    "Customers": "urn:customers_2016_2.transactions.webservices.netsuite.com",
    "CustomersTypes": "urn:types.customers_2016_2.transactions.webservices.netsuite.com",
    "Customization": "urn:customization_2016_2.setup.webservices.netsuite.com",
    "CustomizationTypes": "urn:types.customization_2016_2.setup.webservices.netsuite.com",
    "DemandPlanning": "urn:demandplanning_2016_2.transactions.webservices.netsuite.com",
    "DemandPlanningTypes": "urn:types.demandplanning_2016_2.transactions.webservices.netsuite.com",
    "Employees": "urn:employees_2016_2.lists.webservices.netsuite.com",
    "EmployeesTransactions": "urn:employees_2016_2.transactions.webservices.netsuite.com",
    "EmployeeTypes": "urn:types.employees_2016_2.transactions.webservices.netsuite.com",
    "Faults": "urn:faults_2016_2.platform.webservices.netsuite.com",
    "FaultsTypes": "urn:types.faults_2016_2.platform.webservices.netsuite.com",
    "FileCabinet": "urn:filecabinet_2016_2.documents.webservices.netsuite.com",
    "FileCabinetTypes": "urn:types.filecabinet_2016_2.documents.webservices.netsuite.com",
    "Financial": "urn:financial_2016_2.transactions.webservices.netsuite.com",
    "FinancialTypes": "urn:types.financial_2016_2.transactions.webservices.netsuite.com",
    "General": "urn:general_2016_2.transactions.webservices.netsuite.com",
    "Inventory": "urn:inventory_2016_2.transactions.webservices.netsuite.com",
    "InventoryTypes": "urn:types.inventory_2016_2.transactions.webservices.netsuite.com",
    "Website": "urn:website_2016_2.lists.webservices.netsuite.com",
    "WebsiteTypes": "urn:types.website_2016_2.lists.webservices.netsuite.com",
    "Marketing": "urn:marketing_2016_2.lists.webservices.netsuite.com",
    "MarketingTypes": "urn:types.marketing_2016_2.lists.webservices.netsuite.com",
    "Messages": "urn:messages_2016_2.platform.webservices.netsuite.com",
    "Purchases": "urn:purchases_2016_2.transactions.webservices.netsuite.com",
    "PurchasesTypes": "urn:types.purchases_2016_2.transactions.webservices.netsuite.com",
    "Relationships": "urn:relationships_2016_2.lists.webservices.netsuite.com",
    "RelationshipTypes": "urn:types.relationships_2016_2.lists.webservices.netsuite.com",
    "Sales": "urn:sales_2016_2.transactions.webservices.netsuite.com",
    "SaleTypes": "urn:types.sales_2016_2.transactions.webservices.netsuite.com",
    "Scheduling": "urn:scheduling_2016_2.activities.webservices.netsuite.com",
    "SchedulingTypes": "urn:types.scheduling_2016_2.activities.webservices.netsuite.com",
    "Support": "urn:support_2016_2.lists.webservices.netsuite.com",
    "SupportTypes": "urn:types.support_2016_2.lists.webservices.netsuite.com",
    "SupplyChain": "urn:supplychain_2016_2.lists.webservices.netsuite.com",
    "SupplyChainTypes": "urn:types.supplychain_2016_2.lists.webservices.netsuite.com"
}


# Model name alias
NETSUITE_MODEL_ALIAS_DEFINITIONS = {
    'Passport': 'Core:Passport',
    'RecordRef': 'Core:RecordRef',
    'ListOrRecordRef': 'Core:ListOrRecordRef',
    'ApplicationInfo': 'Messages:ApplicationInfo',
    'CustomerSearchBasic': 'Common:CustomerSearchBasic',
    'ItemSearchBasic': 'Common:ItemSearchBasic',
    'SearchPreferences': 'Messages:SearchPreferences',
    'SearchBooleanField': 'Core:SearchBooleanField',
    'SearchStringField': 'Core:SearchStringField',
    'SearchStringFieldOperator': 'CoreTypes:SearchStringFieldOperator',
    'SearchMultiSelectField': 'Core:SearchMultiSelectField',

    'Customer': 'Relationships:Customer',
    'Address': 'Common:Address',
    'Country': 'CommonTypes:Country',

    'CashSale': 'Sales:CashSale',
    'CashSaleItem': 'Sales:CashSaleItem',
    'CashSaleItemList': 'Sales:CashSaleItemList',

    'SalesOrder': 'Sales:SalesOrder',
    'SalesOrderItem': 'Sales:SalesOrderItem',
    'SalesOrderItemList': 'Sales:SalesOrderItemList',

    # Custom data
    'CustomFieldList': 'Core:CustomFieldList',
    'CustomFieldRef': 'Core:CustomFieldRef',
    'StringCustomFieldRef': 'Core:StringCustomFieldRef',

    # Preferences
    'Preferences': 'Messages:Preferences',

    # Search
    'SearchRecord': 'Core:SearchRecord',
    'SearchMoreWithIdRequest': 'Messages:SearchMoreWithIdRequest',

    'GetSelectValueFieldDescription': 'Core:GetSelectValueFieldDescription',

    # Subsidiary search models
    'SubsidiarySearchBasic': 'Common:SubsidiarySearchBasic',
    'SubsidiarySearchRowBasic': 'Common:SubsidiarySearchRowBasic',

    # Employee search models
    'EmployeeSearchBasic': 'Common:EmployeeSearchBasic',
    'EmployeeSearchRowBasic': 'Common:EmployeeSearchRowBasic',

    'LocationSearchBasic': 'Common:LocationSearchBasic',
    'LocationSearchRowBasic': 'Common:LocationSearchRowBasic',


    'DepartmentSearchBasic': 'Common:DepartmentSearchBasic',
    'DepartmentSearchRowBasic': 'Common:DepartmentSearchRowBasic',

    'ResourceAllocationSearchBasic': 'Common:ResourceAllocationSearchBasic',
    'ResourceAllocationSearchRowBasic': 'Common:ResourceAllocationSearchRowBasic',


    # Employee model
    'Employee': 'Employees:Employee',

    # Session management
    'LogoutRequest': 'Messages:LogoutRequest'
}
