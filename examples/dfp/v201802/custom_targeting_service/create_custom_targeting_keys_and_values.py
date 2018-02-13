#!/usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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

"""This example creates new custom targeting keys and values.

To determine which custom targeting keys and values exist, run
get_all_custom_targeting_keys_and_values.py. To target these custom targeting
keys and values, run target_custom_criteria_example.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  custom_targeting_service = client.GetService(
      'CustomTargetingService', version='v201802')

  # Create custom targeting key objects.
  keys = [
      {
          'displayName': 'gender',
          'name': 'g',
          'type': 'PREDEFINED'
      },
      {
          'displayName': 'car model',
          'name': 'c',
          'type': 'FREEFORM'
      },
      # Add predefined key that may be use for content targeting.
      {
          'displayName': 'genre',
          'name': 'genre',
          'type': 'PREDEFINED'
      }
  ]

  # Add custom targeting keys.
  keys = custom_targeting_service.createCustomTargetingKeys(keys)

  # Display results.
  if keys:
    for key in keys:
      print ('A custom targeting key with id "%s", name "%s", and display '
             'name "%s" was created.' % (key['id'], key['name'],
                                         key['displayName']))
  else:
    print 'No keys were created.'

  # Create custom targeting value objects.
  values = [
      {
          'customTargetingKeyId': keys[0]['id'],
          'displayName': 'male',
          # Name is set to 1 so that the actual name can be hidden from website
          # users.
          'name': '1',
          'matchType': 'EXACT'
      },
      {
          'customTargetingKeyId': keys[0]['id'],
          'displayName': 'female',
          # Name is set to 2 so that the actual name can be hidden from website
          # users.
          'name': '2',
          'matchType': 'EXACT'
      },
      {
          'customTargetingKeyId': keys[1]['id'],
          'displayName': 'honda civic',
          'name': 'honda civic',
          'matchType': 'EXACT'
      },
      {
          'customTargetingKeyId': keys[1]['id'],
          'displayName': 'toyota',
          'name': 'toyota',
          'matchType': 'EXACT'
      },
      {
          'customTargetingKeyId': keys[2]['id'],
          'displayName': 'comedy',
          'name': 'comedy',
          'matchType': 'EXACT'
      },
      {
          'customTargetingKeyId': keys[2]['id'],
          'displayName': 'drama',
          'name': 'drama',
          'matchType': 'EXACT'
      }
  ]

  # Add custom targeting values.
  values = custom_targeting_service.createCustomTargetingValues(values)

  # Display results.
  if values:
    for value in values:
      print ('A custom targeting value with id "%s", belonging to key with id'
             ' "%s", name "%s", and display name "%s" was created.'
             % (value['id'], value['customTargetingKeyId'], value['name'],
                value['displayName']))
  else:
    print 'No values were created.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
