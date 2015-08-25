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

"""Retrieves and displays available creative field values for a given string.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfa


CREATIVE_FIELD_ID = 'INSERT_CREATIVE_FIELD_ID_HERE'


def main(client, creative_field_id):
  # Initialize appropriate service.
  creative_field_service = client.GetService(
      'creativefield', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set up creative field value search criteria structure.
  creative_field_value_search_criteria = {
      'creativeFieldIds': [creative_field_id],
      'pageSize': '10'
  }

  # Get creative field values for the selected criteria.
  results = creative_field_service.getCreativeFieldValues(
      creative_field_value_search_criteria)

  # Display creative field value names and IDs.
  if results['records']:
    for creative_field_value in results['records']:
      print ('Creative field value with name \'%s\' and ID \'%s\' was found.'
             % (creative_field_value['name'], creative_field_value['id']))
  else:
    print 'No creative field values found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, CREATIVE_FIELD_ID)
