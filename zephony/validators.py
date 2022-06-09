import re

from datetime import datetime
from voluptuous import (
    All,
    Any,
    Invalid,
    Length,
    # LengthInvalid,
    Optional,
    # Range,
    Required,
    # Schema,
    # ALLOW_EXTRA
)


def ValidEmail(msg=None):
    """
    Custom validator to validate the email address.
    """

    def f(email):
        if not re.match("[\w\.\-]*@[\w\.\-]*\.\w+", str(email)):
            raise Invalid(msg or ('Please use a valid Email ID'))

        return str(email)
    return f


def AllowedPassword():
    """
    Custom validator to validate the password.
    """

    def f(password):
        reg_exp = r'[a-zA-Z0-9~` !@#$%^&*()-_=+{}[]:;"\'<,>.?/|\]*'
        if not re.match(reg_exp, str(password)):
            raise Invalid('Invalid character(s) in password')

        if len(str(password)) > 50 or len(str(password)) < 5:
            raise Invalid('Password should be between 5 and 50 characters')

        return str(password)
    return f


def ValidDate(pattern='yyyy-mm-dd'):
    """
    Custom validator to validate the time range date format.
    """

    if pattern == 'yyyy-mm-ddThh:mm':
        format_ = '%Y-%m-%dT%H:%M'
    elif pattern == 'yyyy-mm-dd':
        format_ = '%Y-%m-%d'
    elif pattern == 'yyyy-mm':
        format_ = '%Y-%m'
    else:
        format_ = '%d/%m/%Y'

    def f(date_text):
        if not date:
            return date

        try:
            datetime.strptime(date_text, format_)
        except ValueError:
            raise Invalid('Date should be of the format {}'.format(pattern))

        return date_text
    return f


#TODO: Improve
def ValidTime(msg=None):
    def f(time_text):
        try:
            datetime.strptime(time_text, '%H:%M')
        except ValueError:
            raise Invalid(msg or 'Not a valid time. Format should be HH:MM')
        return time_text
    return f


def NonEmptyDict(msg='Cannot be empty'):
    def f(d):
        if len(d.keys()) == 0:
            raise Invalid(msg)
        return d
    return f


def ValidName(msg=None):
    def f(name):
        if len(str(name)) > 40 or len(str(name)) < 2:
            raise Invalid(msg or 'Name should be between 2 and 40 characters')

        return str(name)
    return f


def OnlyDigits(msg=None):
    def f(text):
        if not text.isdigit():
            raise Invalid(msg or 'Only digits are allowed')
        return text
    return f


#TODO: Improve
def ValidPhoneNumberDeprecated(msg=None):
    """
    References:
        - https://en.wikipedia.org/wiki/Telephone_numbering_plan
        - https://stackoverflow.com/questions/14894899/what-is-the-minimum-length-of-a-valid-international-phone-number
        - https://stackoverflow.com/questions/3350500/international-phone-number-max-and-min
    """

    def f(phone):
        # if not phone.isdigit():
        #     raise Invalid(msg or 'Il numero di telefono dovrebbe contenere solo cifre')

        if len(phone) < 5:
            raise Invalid(msg or 'Invalid phone number.')

        if len(phone) > 12:
            raise Invalid(msg or 'Invalid phone number.')

        return phone
    return f


#TODO: Improve
def ValidPhoneNumber(msg=None):
    """
    This uses the python port of Google's libphonenumber library to validate
    the phone numbers.

    Currently, the application allows only indian users to register in the
    application.
    """

    def f(mobile):
        # if not mobile.startswith('+'):
        #     mobile = '+91' + mobile
        # try:
        #     phonenumber = phonenumbers.parse(mobile, None)

        #     # Check, if the given number is a valid indian number
        #     # if phonenumber.country_code != 91:
        #     #     raise Invalid(
        #     #         'Currently the registration is not open to users outside '
        #     #         'India.'
        #     #     )
        # except phonenumbers.phonenumberutil.NumberParseException:
        #     raise Invalid('Not a valid mobile number')

        return mobile

    return f


#TODO: Improve
def ValidUsername(msg=None):
    def f(username):
        # Should start with an alphabet, can end with a digit or an alphabet and can
        # contain a dot.
        if not re.match("^[a-zA-Z]+[a-zA-z0-9]*[\.]?[a-zA-Z0-9]+$", str(username)):
            raise Invalid(
                msg or ('Il nome utente dovrebbe iniziare con un alfabeto, può finire'
                'con un alfabeto o una cifra e può contenere un punto')
            )

        if len(str(username)) > 20:
            raise Invalid(msg or ('Il nome utente non può contenere più di 20 caratteri'))

        if len(str(username)) < 4:
            raise Invalid(msg or ('Il nome utente non può essere inferiore a 4 caratteri'))

        return str(username)
    return f


def ValidWebURL(msg=None):
    """
    This is a custom validator for validating a website URL.
    """

    def f(url):
        if not re.match('^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$', str(url)):  # Breaking into multilines doesn't validate properly
            raise Invalid(msg or 'Use a valid URL')

        return str(url)
    return f

