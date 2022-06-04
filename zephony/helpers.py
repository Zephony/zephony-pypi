"""
The commonly used pieces of code are put inside functions here. The functions
here shouldn't be application specific but generic helpers for Python web
development.
"""

import time
import base64
import codecs
import csv
import json
import logging
import os
import math
import random
import re
import string
import hashlib
import pytz
import datetime
from datetime import datetime, timedelta
from email.utils import format_datetime
from dateutil import parser

import requests
from flask import (
    Flask, Response, request, current_app as app,
    render_template
)
# from twilio.base.exceptions import TwilioRestException
# from twilio.rest import Client as TwilioClient
from voluptuous import MultipleInvalid
from unicodedata import normalize
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


def is_allowed_file(filename, allowed_extensions={'csv'}):
    """
    This function allows checks if the extension of the filename received
    and returns a boolean value based on whether it is present in the
    `allowed_extensions` set or not.

    :param str filename: The name of the file
    :param set allowed_extensions: Allowed extensions

    :return bool:
    """

    file_extension = filename.rsplit('.', 1)[1].lower()
    return '.' in filename and file_extension in allowed_extensions


def get_rows_from_csv(f_path, header=False, delimiter=',',\
        int_fields=[], empty_check_col=None):
    """
    f_path - Represents the relative path of the CSV file
    header - Set to True if the first row is to be skipped.
    delimiter - CSV delimiter can be `,`, `;`, etc.
    int_fields - List of columns that has to be converted to integer
        - Empty values are returned as None.
    """

    with codecs.open(f_path, encoding='utf-8', errors='ignore') as f:
        f.seek(0)
        reader = csv.reader(f, delimiter=delimiter)

        # Skip the header if specified
        if header:
            next(reader)

        rows = []
        for row in reader:
            # Skip row if the required check is empty
            if empty_check_col is not None:
                if row[empty_check_col] == '':
                    continue

            for i, col in enumerate(row):
                row[i] = col.strip()
            rows.append(row)

        return rows


def get_rows_from_workbook_sheet(sheet, header=False, int_fields=[],\
        empty_check_col=None):
    """
    f_path - Represents the relative path of the CSV file
    header - Set to True if the first row is to be skipped.
    delimiter - CSV delimiter can be `,`, `;`, etc.
    int_fields - List of columns that has to be converted to integer
        - Empty values are returned as None.
    """

    reader = sheet.iter_rows()

    # Skip the header if specified
    if header:
        next(reader)

    rows = []
    for row in reader:
        # Skip row if the required check is empty
        if empty_check_col is not None:
            if row[empty_check_col] == '':
                continue

        new_row = []
        for i, col in enumerate(row):
            print(col.value, type(col.value))
            try:
                new_row.append( col.value.strip())
            except:
                new_row.append(str(col.value).strip())
        rows.append(new_row)

    return rows


def responsify(data, message=None, http_status=200, pagination=None,\
        summary=None):
    """
    Argument data refers to data or errors, the latter in case of the
    http_status being 4xx or 5xx.

    status:         str - 'success'/'error'
    http_status:    int - 200 to 599
    data (success)  array/dictionary/None - contains the data
    errors:         array -

    :param dict/list data: Data dict or list of errors
    :param str/None message: The optional message to be sent by the API
    :param int http_status: The status code of the response
    :param tuple pagination: current_page, standard_page_size, total_pages
    :param summary:

    :return dict: The dictionary response that has to be jsonified
    """

    if http_status < 400:
        res = {
            'status': 'success',
            'http_status': http_status,
            'data': data,
            'message': message,
        }
    else:
        res = {
            'status': 'error',
            'http_status': http_status,
            'errors': data,
            'message': message,
        }

    if pagination:
        res['pagination'] = {
            'current_page': pagination[0],
            'standard_page_size': pagination[1],
            'total_pages': pagination[2],
        }

    if summary:
        res['summary'] = {
            'active_count': summary[0],
        }

    return res


def send_email(to, subject, mailgun_config, template_string,\
        template=None, template_data=None, attachments=None,\
        from_=None, reply_to=None, recipient_vars=None,\
        delivery_time=None, env='development'):
    """
    Takes care of sending an email based on the email service configured with
    the application. This function is used to send both individual and bulk
    emails to keep the code DRY (Needs confirmation).

    mailgun_config = {
        'sender': None,
        'url': None,
        'api_key': None,
    }

    `recipient_vars` is a must when sending bulk emails if you want to make
    sure it is sent individually to the recipients, otherwise they have
    the rest of the recipient addresses too.

    :param str template: The HTML email template file path
    :param dict template_data: The data to be rendered with the template
    :param list(str) to: List of recipients - Mailgun recipient format
    :param str subject: The email subject
    :param dict mailgun_config: Contains keys: `URL`, `API_KEY`, `SENDER`
    :param list(str) attachments: List of file paths to be attached
    :param ??? recipient_vars: ???
    :param datetime delivery_time: The time the email has to be delivered

    :return requests.models.Response:
    """

    # logger.info(template_string)
    if template:
        html = render_template(template, data=template_data)
    else:
        html = template_string

    # logger.info(html)
    data = {
        'from': mailgun_config['SENDER'],
        'to': to,
        'subject': subject,
        'html': html,
    }

    if from_:
        data['from'] = from_

    if reply_to:
        data['h:Reply-To'] = reply_to

    if delivery_time:
        data['o:deliverytime'] = format_datetime(
            datetime.utcnow() + timedelta(days=int(deliverytime))
        )

    if recipient_vars:
        data['recipient-variables'] = recipient_vars

    #TODO: Attachments are not being delivered currently
    files = {}
    if attachments:
        for a in attachments:
            file_ = open(a[1:], 'rb')
            files['test'] = file_

    #TODO Detect environment without the app.env variable
    # Use dotenv?
    if env == 'development':
        logger.warning('Development environment detected, not sending email.')
        return None

    # Requesting to Mailgun's REST API
    # Note that the mailgun config URL is different if Mailgun is
    # configured to send emails from the EU server rather than the US server
    res = requests.post(
        mailgun_config['URL'] + '/messages',
        auth=('api', mailgun_config['API_KEY']),
        data=data,
        files=files,
    )
    return res


def send_sms(to, body, twilio_config, env='development'):
    """
    This method is a helper to send sms via the Twilio API.

    twilio_config = {
        'ACCOUNT_SID': str,
        'AUTH_TOKEN': str,
        'FROM_NUMBER': str,
    }

    :param string to: To phone number.
    :param string body: The sms body
    :param dict twilio_config: Contains keys: `ACCOUNT_SID`, `AUTH_TOKEN`, `FROM_NUMBER`
    """

    if env == 'development':
        logger.warning('Development environment detected, not sending SMS.')
        return None

    # Twilio client is configured with account sid + auth token
    twilio_client = TwilioClient(
        twilio_config['ACCOUNT_SID'],
        twilio_config['AUTH_TOKEN']
    )

    message = None
    try:
        message = twilio_client.messages.create(
            from_=twilio_config['FROM_NUMBER'],
            body=body,
            to=to,
        )

        logger.info(
            'Twilio message response with id: {}, status: {} for phone: {}'
            .format(
                message.sid,
                message.status,
                to,
            )
        )
    except TwilioRestException as te:
        logger.error(
            'Twilio request error: {} while sending SMS to {}'.format(
                te,
                to,
            )
        )
    except Exception as e:
        logger.error('Cannot send SMS. Unknown exception {}'.format(e))

    return message


def upload_base64_encoded_file(base64_value, filename):
    """
    This function handles uploading of a base64 encoded file and return the
    file object.

    :param ??? base64_value: The file bytes???
    :param filename str: ???

    :return file:
    """

    base64_file = bytes(base64_value, 'utf-8')
    with open(filename, 'wb') as f:
        f.write(base64.decodestring(base64_file))
        f.close()
    return f


def upload_file(file_, upload_type='image', config=None):
    """
    This function handles uploading of a file, getting the file object -
    typically returned by the Flask request handler.

    :param file file_: The file object that has to be saved

    :return str: The path of the saved file
    """

    upload_folder = config['FILE_UPLOAD_FOLDER']

    # Add timestamp to filename to avoid image replacement due to name
    # duplication
    timestamp = str(int(round(time.time() * 1000000)))
    filename = secure_filename(file_.filename)
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(timestamp, ext)

    f_path = os.path.join(upload_folder, filename)
    file_.save(f_path)

    return {
        'original_name': file_.filename,
        'name': filename,
        'type_': ext,
        'path': f_path
    }


def validate_schema_with_errors(schema, payload):
    """
    The first argument is the actual schema to be validated with and the second
    argument is the dictionary containing the data to be validated.

    It returns an empty list if there are no errors and a list of error
    dictionaries in case of an error(s).

    :param dict schema: Returns either False or a list of errors
    :param dict payload: Data object that has to be validated

    :return list(dict): Empty list if no errors
    """

    errors = []

    if not payload:
        return [{
            'field': 'data',
            'description': 'Request data cannot be null',
        }]

    try:
        schema(payload)
    except MultipleInvalid as e:
        for x in e.errors:
            field = str(x.path[0])
            if len(x.path) > 0:
                for node in x.path[1:]:
                    field += '.' + str(node)
            errors.append({
                'field': field,
                'description': str(x.error_message).capitalize(),
            })
    return errors


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def tokenify(text, delim='-', append_random=False, non_ascii=False):
    """
    This function generates a slug, with a default delimiter as an hyphen

    NFKD: Normalization Form - Compatibility Decomposition
    NFKD is used normalizing a literal in unicode.
    This uses the normalize function from the unicodedata module
    """

    result = []
    for word in _punct_re.split(text.lower()):
        if non_ascii:
            word = normalize('NFKD', word)
        else:
            word = normalize('NFKD', word).encode('ascii', 'ignore')\
                    .decode('utf-8')

        if word:
            result.append(word)

    result = delim.join(result)
    if append_random:
        result += delim + str(int(round(time.time()*10**6)))
    return result


def random_string_generator(size=5, chars=None):
    """

    Returns a random string of digits.
    """

    if not chars:
        chars = string.digits+string.ascii_letters

    return ''.join(random.choice(chars) for _ in range(size))


def get_datetime(s):
    """
    This function converts the date/datetime string to python's
    datetime object.
    Accepted formats: yyyy-mm-dd, yyyy-mm-dd hh:mm, yyyy-mm-ddThh-mm

    :param str s:

    :return datetime:
    """

    # Remove unwanted characters from the datetime
    # Bank transactions and SDD status has these characters in date
    s = s.strip(' ')

    # Nesting exception looks ugly but no better alternative found yet:
    # https://softwareengineering.stackexchange.com/questions/118788/
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')
        except ValueError:
            try:
                return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    try:
                        return datetime.datetime.strptime(s, '%d/%m/%Y')
                    except ValueError:
                        return None


def serialize_datetime(datetime_object, without_day=False):
    """
    This function serialized the datetime object representation into a
    universally acceptable string format.

    If without_day is set to True, this function converts the date
    into a format like yyyy-mm.

    :param datetime datetime_object:
    :param bool without_day:

    :return str:
    """

    if not datetime_object:
        return None

    if without_day:
        return datetime.datetime.strftime(date, '%Y-%m')

    return str(datetime_object)


def convert_date_deprecated(date):
    """
    This function converts the date into a format like dd/mm/yy
    :param date:

    :return:
    """

    converted_date = datetime.datetime.strftime(date, "%d/%m/%Y")
    return converted_date


def convert_datetime_to_utc(datetime_obj, timezone):
    """
    This function converts the given time of the given timezone to the
    UTC time.
    """

    local = pytz.timezone(timezone)
    local_dt = local.localize(datetime_obj, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)

    return utc_dt


def normalize_date(date):
    """
    This function converts any date string into a standard date object.

    :param date object:

    :return:
    """

    if not date:
        return None

    date = parser.parse(date.strip())

    return date


def generate_checksum_of_file(fpath):
    """
    This function generates md5 checksum of the given file and returns it.

    :param str fname: Path of the file

    :return str: Hash string of the file
    """

    hash_md5 = hashlib.md5()
    with open(fpath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def add_pagination(query_params, default_page=1, default_page_size=100):
    # Pagination stuff
    page = query_params.get('page', default_page)
    try:
        page = int(page)
        if page <= 0:
            raise ValueError
    except (TypeError, ValueError):
        page = default_page

    page_size = query_params.get('page_size', default_page_size)
    try:
        page_size = int(page_size)
        if page_size <= 0:
            raise ValueError
    except (TypeError, ValueError):
        page_size = default_page_size

    query_params['page'] = page
    query_params['page_size'] = page_size

    return query_params


# Flask related
def add_urls(blueprint, resource_classes):
    """
    This function adds the URL rules of all the resources that is
    being passed as an argument list using Flask's add_url_rule method.
    This allows us to group requests and HTTP method handlers ins
    classes with each method handler as a function.

    :param Blueprint blueprint: The blueprint to which the routes are
        to be attached
    :param list(object) resource_classes: The user defined resource classes
    """

    for cls in resource_classes:
        cls_name = cls.__name__

        if hasattr(cls, 'get_all'):
            blueprint.add_url_rule(
                cls.collection_route,
                cls_name + '_get_all',
                view_func=cls.get_all,
                methods=['GET']
            )
        if hasattr(cls, 'post'):
            blueprint.add_url_rule(
                cls.collection_route,
                cls_name + '_post',
                view_func=cls.post,
                methods=['POST']
            )
        if hasattr(cls, 'get'):
            blueprint.add_url_rule(
                cls.resource_route,
                cls_name + '_get',
                view_func=cls.get,
                methods=['GET']
            )
        if hasattr(cls, 'patch'):
            blueprint.add_url_rule(
                cls.resource_route,
                cls_name + '_patch',
                view_func=cls.patch,
                methods=['PATCH']
            )
        if hasattr(cls, 'delete'):
            blueprint.add_url_rule(
                cls.resource_route,
                cls_name + '_delete',
                view_func=cls.delete,
                methods=['DELETE']
            )


class ApiFlask(Flask):
    """
    ApiFlask is inherited from the Flask class to override the make_response
    function to automatically convert a returned dictionary to a JSON response.
    """

    def make_response(self, rv):
        if isinstance(rv, dict):
            return Response(
                json.dumps(rv),
                status=rv['http_status'],
                mimetype='application/json',
            )
        return Flask.make_response(self, rv)


