"""Predicates."""


class RecordTypeSelectorPredicate(object):
    """Check if a given record type should be selected."""

    def __init__(self, record_types=None)
        """Constructor.

        Args:
                record_types: Types of records
        """
        if not (isinstance(record_types, list)):
            raise Exception("Record types must be a list")

        self.record_types = record_types or []

    def __call__(self, record_type):
        """Check if a given record type should be batched.

        Args:
                record_type: Type of record to check for batching

        Returns:
                True if the record type should be selected or False otherwise
        """
        if not self.record_types:
            return False

        return record_type in self.record_types
