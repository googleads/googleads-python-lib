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

"""This code example updates activities.

To determine which activities exist, run get_all_activities.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the activity to update.
ACTIVITY_ID = 'INSERT_ACTIVITY_ID_HERE'


def main(client, activity_id):
  # Initialize appropriate service.
  activity_service = client.GetService('ActivityService', version='v202102')

  # Create statement object to select one activity by ID to update.
  statement = (ad_manager.StatementBuilder(version='v202102')
               .Where('id = :activityId')
               .WithBindVariable('activityId', int(activity_id))
               .Limit(1))

  # Get activities by statement.
  response = activity_service.getActivitiesByStatement(
      statement.ToStatement())
  if 'results' in response and len(response['results']):
    updated_activities = []
    for activity in response['results']:
      # Update the expected URL.
      activity['expectedURL'] = 'https://google.com'
      updated_activities.append(activity)
    # Update the activity on the server.
    activities = activity_service.updateActivities(updated_activities)

    for updated_activity in activities:
      print(('Activity with ID "%s" and name "%s" was updated.')
            % (updated_activity['id'], updated_activity['name']))
  else:
    print('No activities found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ACTIVITY_ID)
