"""Customer operations."""

from .types import RecordType


def get_customer(client, internal_id):
    """Get a customer record using its unique internal identifier.

    Args:
        client: Netsuite API client
        internal_id: Customer unique internal identifier

    Returns:
        Customer instance if found or None otherwise
    """
    return get_record_by_type(RecordType.Customer, internal_id)
