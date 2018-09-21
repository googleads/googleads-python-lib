#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example shows how to upload offline data for store sales transactions.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

import datetime
import hashlib

from googleads import adwords
import pytz


_DT_FORMAT = '%Y%m%d %H%M%S'
# User identifier types whose values must be hashed.
_HASHED_IDENTIFIER_TYPES = ('HASHED_EMAIL', 'HASHED_FIRST_NAME',
                            'HASHED_LAST_NAME', 'HASHED_PHONE')
# The timezone to be used in this example. For valid timezone IDs, see:
# https://developers.google.com/adwords/api/docs/appendix/codes-formats#timezone-ids
_TIMEZONE = pytz.timezone('America/New_York')
# Name of the conversion tracker to upload to.
CONVERSION_NAME = 'INSERT_CONVERSION_NAME_HERE'
# Insert email addresses below for creating user identifiers.
EMAIL_ADDRESSES = ['EMAIL_ADDRESS_1', 'EMAIL_ADDRESS_2']
# The external upload ID can be any number that you use to keep track of your
# uploads.
EXTERNAL_UPLOAD_ID = 'INSERT_EXTERNAL_UPLOAD_ID'
# Store sales upload common metadata types
METADATA_TYPE_1P = 'FirstPartyUploadMetadata'
METADATA_TYPE_3P = 'ThirdPartyUploadMetadata'
# Set the below constant to METADATA_TYPE_3P if uploading third-party data.
STORE_SALES_UPLOAD_COMMON_METADATA_TYPE = METADATA_TYPE_1P
# The three constants below are needed when uploading third-party data. They
# are not used when uploading first-party data.
# Advertiser upload time to partner.
# For times, use the format yyyyMMdd HHmmss tz. For more details on formats,
# see:
# https://developers.google.com/adwords/api/docs/appendix/codes-formats#timezone-ids
ADVERTISER_UPLOAD_TIME = 'INSERT_ADVERTISER_UPLOAD_TIME_HERE'
# Indicates the version of the bridge map.
BRIDGE_MAP_VERSION_ID = 'INSERT_BRIDGE_MAP_VERSION_ID_HERE'
# The ID of the third party uploading the transaction feed.
PARTNER_ID = 'INSERT_PARTNER_ID_HERE'


def main(client, conversion_name, external_upload_id,
         store_sales_upload_common_metadata_type, email_addresses,
         advertiser_upload_time=None, bridge_map_version_id=None,
         partner_id=None):
  # Set partial failure to True since this example demonstrates how to handle
  # partial errors.
  client.partial_failure = True
  # Initialize appropriate services.
  offline_data_upload_service = client.GetService(
      'OfflineDataUploadService', version='v201809')

  # Create the first offline data for upload.
  # This transaction occurred 7 days ago with an amount of $200 USD.
  transaction_time_1 = (datetime.datetime.now(tz=_TIMEZONE) -
                        datetime.timedelta(days=7))
  offline_data_1 = {
      'StoreSalesTransaction': {
          'userIdentifiers': [
              _CreateUserIdentifier(identifier_type='HASHED_EMAIL',
                                    value=email_addresses[0]),
              _CreateUserIdentifier(identifier_type='STATE', value='New York')
          ],
          'transactionTime': _GetFormattedDateTime(transaction_time_1),
          'transactionAmount': {
              'currencyCode': 'USD',
              'money': {
                  'microAmount': 200000000
              }
          },
          'conversionName': conversion_name
      }
  }

  # Create the second offline data for upload.
  # This transaction occurred 14 days ago with amount of 450 EUR.
  transaction_time_2 = (datetime.datetime.now(tz=_TIMEZONE) -
                        datetime.timedelta(days=14))
  offline_data_2 = {
      'StoreSalesTransaction': {
          'userIdentifiers': [
              _CreateUserIdentifier(identifier_type='HASHED_EMAIL',
                                    value=email_addresses[1]),
              _CreateUserIdentifier(identifier_type='STATE', value='California')
          ],
          'transactionTime': _GetFormattedDateTime(transaction_time_2),
          'transactionAmount': {
              'currencyCode': 'EUR',
              'money': {
                  'microAmount': 450000000
              }
          },
          'conversionName': conversion_name
      }
  }

  # Set the type and metadata of this upload.
  upload_metadata = {
      'StoreSalesUploadCommonMetadata': {
          'xsi_type': store_sales_upload_common_metadata_type,
          'loyaltyRate': 1.0,
          'transactionUploadRate': 1.0,
      }
  }

  if store_sales_upload_common_metadata_type == METADATA_TYPE_1P:
    upload_type = 'STORE_SALES_UPLOAD_FIRST_PARTY'
  elif store_sales_upload_common_metadata_type == METADATA_TYPE_3P:
    upload_type = 'STORE_SALES_UPLOAD_THIRD_PARTY'
    upload_metadata['StoreSalesUploadCommonMetadata'].update({
        'advertiserUploadTime': advertiser_upload_time,
        'validTransactionRate': 1.0,
        'partnerMatchRate': 1.0,
        'partnerUploadRate': 1.0,
        'bridgeMapVersionId': bridge_map_version_id,
        'partnerId': partner_id
    })
  else:
    raise ValueError('Unknown metadata type.')

  # Create offline data upload
  offline_data_upload = {
      'externalUploadId': external_upload_id,
      'offlineDataList': [offline_data_1, offline_data_2],
      # Set the type of this upload.
      'uploadType': upload_type,
      'uploadMetadata': upload_metadata
  }

  # Create an offline data upload operation.
  operations = [{
      'operator': 'ADD',
      'operand': offline_data_upload
  }]

  # Upload offline data on the server and print the result.
  result = offline_data_upload_service.mutate(operations)
  offline_data_upload = result['value'][0]

  print ('Uploaded offline data with external upload ID "%d" and upload status '
         '"%s".' % (offline_data_upload['externalUploadId'],
                    offline_data_upload['uploadStatus']))

  # Print any partial data errors from the response.
  if result['partialFailureErrors']:
    for api_error in result['partialFailureErrors']:
      # Get the index of the failed operation from the error's field path
      # elements.
      operation_index = _GetFieldPathElementIndex(api_error, 'operations')

      if operation_index:
        failed_offline_data_upload = operations[operation_index]['operand']
        # Get the index of the entry in the offline data list from the error's
        # field path elements.
        offline_data_list_index = _GetFieldPathElementIndex(
            api_error, 'offlineDataList')
        print ('Offline data list entry "%d" in operation "%d" with external '
               'upload ID "%d" and type "%s" has triggered failure for the '
               'following reason: "%s"' % (
                   offline_data_list_index, operation_index,
                   failed_offline_data_upload['externalUploadId'],
                   failed_offline_data_upload['uploadType'],
                   api_error['errorString']))
      else:
        print ('A failure has occurred for the following reason: "%s".' % (
            api_error['errorString']))


def _CreateUserIdentifier(identifier_type=None, value=None):
  """Creates a user identifier from the specified type and value.

  Args:
    identifier_type: a str specifying the type of user identifier.
    value: a str value of the identifier; to be hashed using SHA-256 if needed.

  Returns:
    A dict specifying a user identifier, with a value hashed using SHA-256 if
      needed.
  """
  if identifier_type in _HASHED_IDENTIFIER_TYPES:
    # If the user identifier type is a hashed type, normalize and hash the
    # value.
    value = hashlib.sha256(value.strip().lower()).hexdigest()

  user_identifier = {
      'userIdentifierType': identifier_type,
      'value': value
  }

  return user_identifier


def _GetFieldPathElementIndex(api_error, field):
  """Retrieve the index of a given field in the api_error's fieldPathElements.

  Args:
    api_error: a dict containing a partialFailureError returned from the AdWords
      API.
    field: a str field for which this determines the index in the api_error's
      fieldPathElements.

  Returns:
    An int index of the field path element, or None if the specified field can't
    be found in the api_error.
  """
  field_path_elements = api_error['fieldPathElements']

  if field_path_elements:
    found_index = [field_path_element['index']
                   for field_path_element in field_path_elements
                   if field_path_element['field'] == field]
    if found_index:
      return found_index

  return None


def _GetFormattedDateTime(dt):
  """Formats the given datetime and timezone for use with AdWords.

  Args:
    dt: a datetime instance.

  Returns:
    A str representation of the datetime in the correct format for AdWords.
  """
  return '%s %s' % (datetime.datetime.strftime(dt, _DT_FORMAT), _TIMEZONE.zone)


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CONVERSION_NAME, EXTERNAL_UPLOAD_ID,
       STORE_SALES_UPLOAD_COMMON_METADATA_TYPE, EMAIL_ADDRESSES,
       ADVERTISER_UPLOAD_TIME, BRIDGE_MAP_VERSION_ID, PARTNER_ID)
