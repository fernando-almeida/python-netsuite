
import json
import os

import sys

# Datetime objects
from datetime import datetime

# Datetime parser
from dateutil import parser as datetime_parser

# Timezones database
from pytz import timezone

import re

from itertools import ifilter

import logging

# Get the logger instance for the module
LOGGER = logging.getLogger(__name__)


class GovernanceModel(object):
    """Governance model."""

    CONFIG_KEY = "config"
    SCHEDULES_KEY = "schedules"
    RECORD_LIMITS_KEY = "record_limits"
    REQUEST_LIMITS_KEY = "request_limits"

    MANDATORY_ROOT_KEYS = [
		SCHEDULES_KEY,
        RECORD_LIMITS_KEY,
		REQUEST_LIMITS_KEY
	]

    DEFAULT_TIMEZONE = "UTC"

    TIME_FORMAT = "%H:%M:%S"

    ASYNC_OPERATION_RE = re.compile(r'(^async|Async)')

    OPERATION_NAME_TO_CATEGORY_RULES = [
        {"category": "add", "regex": re.compile("(^add)(List)?")},
        {"category": "update", "regex": re.compile("(^update)(List)?")},
        {"category": "delete", "regex": re.compile("(^delete)(List)?")},
        {"category": "search_page", "regex": re.compile("(^search|Search)")}
    ]

    BATCHABLE_OPERATION_CATEGORIES = ["add", "update", "delete"]

    def __init__(self, config):
        """Constructor.

        Args:
                config: Governance model configuration
        """

        self.validate_config(config)
        self.config = config

    def _get_timezone(self):
        """Get the timezone used for date/time constraints.

        Return:
                The timezone used to describe date/time in the configuration settings
        """
        timezone_str = self.DEFAULT_TIMEZONE

        if "config" in self.config and "timezone" in self.config["config"]:
            timezone_str = self.config["config"]["timezone"]

        return timezone(timezone_str)

    def find_schedule(self, date=None):
        """Find the schedule that maps to the given date.

        Args:
                date: The reference date to find the schedule for
        Return:
                Schedule identifier or None if no match is found
        """
        if not "schedules" in self.config:
            raise Exception("No schedules defined")

        if not date:
            date = datetime.now(self._get_timezone())
        else:
            # Make sure that date's timezone is correct
            raise Exception("Convert date to correct timezone")

        for schedule_id, schedule in self.config["schedules"].items():
            start_time = datetime_parser.parse(schedule["start_time"]).time()
            end_time = datetime_parser.parse(schedule["end_time"]).time()
            if (date.time() >= start_time and date.time() <= end_time) or
				(start_time > end_time and date.time() <= end_time):
                return schedule_id

        raise Exception("Shedule not found for date {0}".format(date))

    def get_operation_category(self, operation_name):
        """Get the name of the category for a given WSDL operation name.

        Args:
                operation_name: Name of the WDSL operation

        Returns:
                The name of the category or None if not found
        """

        iter = filter(
			lambda rule: rule["regex"].match(operation_name),
            self.OPERATION_NAME_TO_CATEGORY_RULES)
        rule = next(iter, None) if iter else None
        return rule["category"] if rule else None

    def is_operation_batchable(self, operation_name):
        """Check if a given operation name is batchable.

        Args:
                operation_name: Name of the WSDL operation to check

        Returns:
                True if the operation is batchable or False otherwise
        """

        operation_category = self.get_operation_category(operation_name)
        if not operation_category:
            return None

        return operation_category in self.get_batchable_operation_categories()

    def is_async_operation(self, operation_name):
        """Check if a given operation is asynchronous given its name .

        Args:
                operation_name: Name of the WDSL operation

        Returns:
                True if the operation is asynchronous or False otherwise
        """
        return not self.ASYNC_OPERATION_RE.match(operation_name) is None

    def has_constraints(self, operation_name):
        """Check if a given operation has constraints given its name.

        Args:
                operation_name: Name of the WSDL operation

        Returns:
                True if the operation is constrained or False otherwise
        """
        return not get_record_constraints(operation_name) is None

    def get_operation_constraints(self, operation_name):
        """Get the constraints for a given operation name.

        Args:
                operation_name: Name of the WDSL operation

        Returns:
                Dictionary of applicable constraints
        """
        operation_category = self.get_operation_category(operation_name)
        if not operation_category:
            LOGGER.debug("No category found for operation {0} so it has no constraints".format(
                operation_name))
            return None

        is_synchronous = not self.is_async_operation(operation_name)
        schedule_id = self.find_schedule()

        operation_constraints = {}
        operation_constraints.update(self.get_operation_category_constraints(
            operation_category, is_synchronous, schedule_id))
        operation_constraints.update(
            self.get_request_constraints(operation_name))

        return operation_constraints

    def get_operation_category_constraints(self, operation_category, is_synchronous=True, schedule_id=None):
        """Get the constraints for a given operation category, synchronous type and schedule identifier.

        Args:
                operation_category: Category of the operation
                is_synchronous: Boolean flag stating whether the operation is meant to executed synchronously
                schedule_id: Schedule identifier

        Returns:
                Dictionary of applicable constraints 
        """
        synchronous_key = "synchronous" if is_synchronous else "asynchronous"

        record_limits = self.config["record_limits"]
        if not synchronous_key in record_limits:
            raise Exception("Property {0} does not exist for record limits")

        if not "operations" in record_limits[synchronous_key][schedule_id]:
            raise Exception("Property \"operations\" is not on records_limits[\"{0}\"][\"{1}\"]".format(
                synchronous_key, schedule_id))

        operations = record_limits[synchronous_key][schedule_id]["operations"]

        if not operation_category in operations:
            raise Exception("Operation category {0} is not on record_limits[\"{1}\"][\"operations\"]".format(
                operation_category, synchronous_key))

        # Found constraints for the given operation category
        return operations[operation_category]

    def get_request_constraints(self, operation_name):
        """Get all request constraints related with the operation.

		Args:
			operation_name: Name of the operation
        """
        return self.config["request_limits"]

    @classmethod
    def get_batchable_operation_categories(cls):
        return cls.BATCHABLE_OPERATION_CATEGORIES

    @classmethod
    def get_operation_categories(cls):
        return (item["category"] for item in cls.OPERATION_NAME_TO_CATEGORY_RULES)

    @classmethod
    def validate_config(cls, config):
        """Validate a given configuration.

        Args:
                config: The configuration object to be validated
        """
        if not isinstance(config, dict):
            raise Exception("Governance configuration must be a dictionary")

        missing_mandatory_keys = []
        # Config property is optional
        for mandatory_key in cls.MANDATORY_ROOT_KEYS:
            if not mandatory_key in config:
                missing_mandatory_keys += [mandatory_key]

        if missing_mandatory_keys:
            raise Exception("The following mandatory keys (\"{0}\") are missing.".format(
                '\",\"'.join(missing_mandatory_keys)))

        # TODO Complete validation for the nested keys

    @classmethod
    def from_file(cls, config_filepath):
        if not os.path.exists(config_filepath):
            raise Exception("Configuration file path does not exist")

        with open(config_filepath, "r") as config_file:
            config = json.load(config_file)
            return GovernanceModel(config)
