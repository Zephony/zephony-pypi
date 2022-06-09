import logging

from functools import wraps
from flask import request, redirect

from .exceptions import (
    ObjectNotFound,
    AccessForbidden,
    InvalidRequestData,
    UnauthorizedAccess,
    InvalidRequestSchema,
)
from .helpers import (
    validate_schema_with_errors,
)

logger = logging.getLogger(__name__)


def admin_only(f):
    """
    This decorator raises a 403 exception if the user is not a Admin.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.user.is_admin():
            raise AccessForbidden(
                message=(
                    'You do not have permission to access this resource. '
                    'Please contact the administrator.'
                )
            )
        return f(*args, **kwargs)
    return decorated_function


def validate_schema(schema):
    """
    This function returns an empty list if there are no errors or a list of error
    dictionaries in case of an error(s).

    :param dict schema: The schema that the payload is to be validated against
    :param dict payload: The actual payload that has to be validated

    :return list(dict): Empty list if no errors
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload = request.get_json()

            errors = validate_schema_with_errors(schema, payload)
            if errors:
                raise InvalidRequestData(errors)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

