"""Subsidiary operations."""

from .utils import search_all
from .types import RecordType


def get_subsidiaries(client, search_preferences=None, search_params=None):
    """Perform a basic search on existing subsidiaries.

    Args:
            client: Netsuite API client
            search_preferences: Preferences for returned search results  (optional)
            search_params: Parameters used to filter the search (optional)

    Returns:
            List of subsidiaries matching the criteria
    """

    return search_all(client, 'SubsidiarySearchBasic', search_preferences, search_params)


def get_subsidiary(client, internal_id):
    """Get a subsidiary record using its unique internal identifier.

    Args:
            client: Netsuite API client
            internal_id: Subsidiary unique internal identifier

    Returns:
            Subsidiary instance if found or None otherwise
    """
    return client.get_record_by_type(RecordType.subsidiary, internal_id)
