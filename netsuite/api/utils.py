
def search_all(client, search_type_name, search_preferences=None, search_params=None):
    """Perform a search to return all matching entities.

    Args:
            client: Netsuite API client
            search_preferences: Preferences for returned search results
            search_params: Parameters used to filter the search for departments (optional)

    Returns:
            List of departments matching the criteria
    """
    SearchType = client.models[search_type_name]
    search_record = SearchType() if not search_params else SearchType(**search_params)

    return client.search_all(search_record, search_preferences)


def update(client, record_type_name, internal_id, data, preferences=None):
    """Update the record with the given type name and internal identifier with the provided data.

    Args:
            client: Netsuite API client
            type_name: Name of the type of record to update
            internal_id: Unique internal identifier for the record type
            data: Dictionary with the data to update the record
            preferences: Preferences to be used during the operation (optional)
    """

    if not internal_id:
        raise Exception("Internal ID {} is invalid!".format(internal_id))

    if not isinstance(data, dict):
        raise Exception("Type of data {}. Expected dict!".format(type(data)))

    # Merge the data to update with the record internal identifier
    data.update({"internalId": internal_id})

    # Get the class to generate an instance of a given record type
    RecordType = client.models[record_type_name]

    # Instantiante record with the data to be updated
    record_with_data_to_update = RecordType(**data)

    return client.update(record_with_data_to_update)
