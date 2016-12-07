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

"""This code example creates new activities.

To determine which activities groups exist, run get_all_activities.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid

# Import appropriate modules from the client library.
from googleads import dfp

# Set the ID of the activity group this activity is associated with.
ACTIVITY_GROUP_ID = 'INSERT_ACTIVITY_GROUP_ID_HERE'


def main(client, activity_group_id):
  # Initialize appropriate service.
  activity_service = client.GetService('ActivityService', version='v201611')

  # Create a daily visits activity.
  daily_visits_activity = {
      'name': 'Activity #%s' % uuid.uuid4(),
      'activityGroupId': activity_group_id,
      'type': 'DAILY_VISITS'
  }

  # Create a custom activity.
  custom_activity = {
      'name': 'Activity #%s' % uuid.uuid4(),
      'activityGroupId': activity_group_id,
      'type': 'CUSTOM'
  }

  # Create the activities on the server.
  activities = activity_service.createActivities([
      daily_visits_activity, custom_activity])

  # Display results.
  for activity in activities:
    print ('An activity with ID \'%s\', name \'%s\', and type \'%s\' was '
           'created.' % (activity['id'], activity['name'], activity['type']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, ACTIVITY_GROUP_ID)
