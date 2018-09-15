"""Department operations."""

from .utils import search_all
from .types import RecordType


def get_departments(client, search_preferences=None, search_params=None):
    """Perform a basic search on existing departments.

    Args:
            client: Netsuite API client
            search_preferences: Preferences for returned search results (optional)
            search_params: Parameters used to filter the search (optional)

    Returns:
            List of departments matching the criteria
    """

    return search_all(client, 'DepartmentSearchBasic', search_preferences, search_params)


def get_department(client, internal_id):
    """Get a department record using its unique internal identifier.

    Args:
            client: Netsuite API client
            internal_id: Department unique internal identifier

    Returns:
            Department instance if found or None otherwise
    """
    return client.get_record_by_type(RecordType.Department, internal_id)
