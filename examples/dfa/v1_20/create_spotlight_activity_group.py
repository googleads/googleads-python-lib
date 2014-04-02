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

"""Creates a new activity group for a given spotlight configuration.

To get spotlight tag configuration, run get_advertisers.py. To get activity
types, run get_activity_types.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: spotlight.saveSpotlightActivityGroup
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


SPOTLIGHT_CONFIGURATION_ID = 'INSERT_SPOTLIGHT_CONFIGURATION_ID_HERE'
ACTIVITY_TYPE = 'INSERT_ACTIVITY_TYPE_HERE'
GROUP_NAME = 'INSERT_GROUP_NAME_HERE'


def main(client, spotlight_configuration_id, activity_type, group_name):
  # Initialize appropriate service.
  spotlight_service = client.GetService(
      'spotlight', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and save spotlight activity group.
  spotlight_activity_group = {
      'name': group_name,
      'spotlightConfigurationId': spotlight_configuration_id,
      'groupType': activity_type
  }
  result = spotlight_service.saveSpotlightActivityGroup(
      spotlight_activity_group)

  # Display results.
  print 'Spotlight activity group with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, SPOTLIGHT_CONFIGURATION_ID, ACTIVITY_TYPE, GROUP_NAME)
