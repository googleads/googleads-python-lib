#!/usr/bin/python
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

"""This example updates status for a given ad group.

To get ad groups, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Initialize appropriate service.
  ad_group_service = client.GetService('AdGroupService', version='v201506')

  # Construct operations and update an ad group.
  operations = [{
      'operator': 'SET',
      'operand': {
          'id': ad_group_id,
          'status': 'PAUSED'
      }
  }]
  ad_groups = ad_group_service.mutate(operations)

  # Display results.
  for ad_group in ad_groups['value']:
    print ('Ad group with name \'%s\' and id \'%s\' was updated.'
           % (ad_group['name'], ad_group['id']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
