#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Creates a creative field value associated with a given creative field.

To get the creative field ID, run get_creative_fields.py.

Tags: creativefield.saveCreativeFieldValue
"""

__author__ = 'Joseph DiLallo'

# Import appropriate classes from the client library.
from googleads import dfa


CREATIVE_FIELD_ID = 'INSERT_CREATIVE_FIELD_ID_HERE'
CREATIVE_FIELD_VALUE_NAME = 'INSERT_CREATIVE_FIELD_VALUE_NAME_HERE'


def main(client, creative_field_id, creative_field_value_name):
  # Initialize appropriate service.
  creative_field_service = client.GetService(
      'creativefield', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and save creative field value.
  creative_field_value = {
      'name': creative_field_value_name,
      'creativeFieldId': creative_field_id,
      'id': '-1'
  }
  result = creative_field_service.saveCreativeFieldValue(
      creative_field_value)

  # Display results.
  print 'Creative field value with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, CREATIVE_FIELD_ID, CREATIVE_FIELD_VALUE_NAME)
