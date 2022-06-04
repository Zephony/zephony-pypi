"""
This file contains all the custom exception definitions we use for the
application.
"""


class InvalidCredentials(Exception):
    """
    This exception to be raised when the user's login credentials are wrong.
    """

    def __init__(self, errors=[], message=None):
        self.errors = errors[:] if errors else []
        self.message = message


class InvalidDateTimeError(Exception):
    """
    As of now, this is primarily used for appointments and call logs.
    When a datetime value of unexpected, or unsupported format is given,
    raise this.
    """

    def __init__(self, errors=None):
        """
        :param list(dict) errors: Each dict has keys `field` & `description`
        """

        self.errors = errors[:] if errors else []


class InvalidRequestData(Exception):
    """
    The request data was semantically invalid. This exception is usually raised
    from the actions or the models layer. This exception is not to be confused
    with the custom exceptions of Voluptuous which is used to validate the
    schema of the request data rather than the actual value of the data
    being sent.
    """

    def __init__(self, errors=None, message=None):
        """
        :param list(dict) errors: Each dict has keys `field` & `description`
        """

        self.errors = errors[:] if errors else []
        self.message = message


class InvalidRequestSchema(Exception):
    def __init__(self, errors=[], message=None):
        self.errors = errors[:] if errors else []
        self.message = message


class ObjectNotFound(Exception):
    def __init__(self, errors=[], message=None):
        self.errors = errors[:] if errors else []
        self.message = message


class ServerError(Exception):
    """
    This exception to be raised on all internal server error so that frontend can show a proper response
    """

    def __init__(self, errors=None):
        """
        :param list(dict) errors: Each dict has keys `field` & `description`
        """
        if not errors:
            errors = [
                {
                    'field': None,
                    'description': 'Unknown server error. Contact admin',
                }
            ]
        self.errors = errors[:] if errors else []


class UnsupportedFormat():
    """
    Raised when the current application doesn't support the format of the
    file. It can be image, or other files.

    When the requested format is not implemented, Raise a NotImplemented
    error instead.
    """

    def __init__(self, errors=None, message=None):
        self.errors = errors[:] if errors else []
        self.message = message


class UnauthorizedAccess(Exception):
    """
    When a user is unauthorized, this exception is raised
    """

    def __init__(self, errors=None, message=None):
        """
        :param list(dict) errors: Each dict has keys `field` & `description`
        """

        self.errors = errors[:] if errors else []
        self.message = message


class AccessForbidden(Exception):
    """
    When a user has invalid permission to a resource, this exception is raised
    """

    def __init__(self, errors=None, message=None):
        """
        :param list(dict) errors: Each dict has keys `field` & `description`
        """

        self.errors = errors[:] if errors else None
        self.message = message


class ResourceNotFound(Exception):
    """
    The requested resource is not found. This exception is usually raised
    from the actions layer, when the requested resource is invalid.
    """

    def __init__(self, errors=[], message=None):
        self.errors = errors[:] if errors else None
        self.message = message

