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

"""This code example creates new creative sets.

To determine which creative sets exist, run get_all_creative_sets.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager

MASTER_CREATIVE_ID = 'INSERT_MASTER_CREATIVE_ID_HERE'
COMPANION_CREATIVE_ID = 'INSERT_COMPANION_CREATIVE_ID_HERE'


def main(client, master_creative_id, companion_creative_id):
  # Initialize appropriate service.
  creative_set_service = client.GetService('CreativeSetService',
                                           version='v202311')

  # Create creative set objects.
  creative_set = {'name': 'Creative set #%s' % uuid.uuid4(),
                  'masterCreativeId': master_creative_id,
                  'companionCreativeIds': [companion_creative_id]}

  # Add creative sets.
  creative_set = creative_set_service.createCreativeSet(creative_set)

  # Display results.
  if creative_set:
    print(('Creative set with ID "%s", master creative ID "%s", and '
           'companion creative IDs "%s" was created.') %
          (creative_set['id'], creative_set['masterCreativeId'], ','.join(
              str(v) for v in creative_set['companionCreativeIds'])))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, MASTER_CREATIVE_ID, COMPANION_CREATIVE_ID)
