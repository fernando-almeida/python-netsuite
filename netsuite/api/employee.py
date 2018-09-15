"""Employee operations."""

from .utils import search_all, update
from .types import RecordType


def get_employees(client, search_preferences=None, search_params=None):
    """Perform a basic search on existing employees.

    Args:
            client: Netsuite API client
            search_preferences: Preferences for returned search results  (optional)
            search_params: Parameters used to filter the search for employees  (optional)

    Returns:
            List of employees matching the criteria
    """

    return search_all(client, 'EmployeeSearchBasic', search_preferences, search_params)


def get_employee(client, internal_id):
    """Get an employee record using its unique internal identifier.

    Args:
            client: Netsuite API client
            internal_id: Employee unique internal identifier

    Returns:
            Employee instance if found or None otherwise
    """
    return client.get_record_by_type(RecordType.Employee, internal_id)


def update_employee(client, internal_id, employee_data, preferences=None):
    """Update the employee's data with the given internal identifier.

    Args:
            client: Netsuite API client
            internal_id: Employee unique internal identifier
            employee_data: Dictionary with the employee data to update
            preferences: Preferences to be used during the operation (optional)
    """

    return update(client, 'Employee', internal_id, employee_data, preferences)
