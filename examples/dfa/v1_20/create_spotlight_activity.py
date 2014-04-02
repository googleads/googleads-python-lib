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

"""This example creates a spotlight activity in a given activity group.

To create an activity group, run create_spotlight_activity_group.py. To get tag
methods types, run get_tag_methods.py. To get activity type IDs, run
get_activity_types.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: spotlight.saveSpotlightActivity
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


ACTIVITY_GROUP_ID = 'INSERT_ACTIVITY_GROUP_ID_HERE'
ACTIVITY_TYPE_ID = 'INSERT_ACTIVITY_TYPE_ID_HERE'
TAG_METHOD_TYPE_ID = 'INSERT_TAG_METHOD_TYPE_ID_HERE'
URL = 'INSERT_EXPECTED_URL_HERE'
ACTIVITY_NAME = 'INSERT_ACTIVITY_NAME_HERE'


def main(client, activity_group_id, activity_type_id, tag_method_type_id, url,
         activity_name):
  # Initialize appropriate service.
  spotlight_service = client.GetService(
      'spotlight', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and save spotlight activity.
  spotlight_activity = {
      'name': activity_name,
      'activityGroupId': activity_group_id,
      'activityTypeId': activity_type_id,
      'tagMethodTypeId': tag_method_type_id,
      'expectedUrl': url
  }
  result = spotlight_service.saveSpotlightActivity(spotlight_activity)

  # Display results.
  print 'Spotlight activity with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, ACTIVITY_GROUP_ID, ACTIVITY_TYPE_ID, TAG_METHOD_TYPE_ID, URL,
       ACTIVITY_NAME)
