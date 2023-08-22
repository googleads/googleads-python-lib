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

"""This code example updates activity groups.

To determine which activity groups exist, run get_all_activity_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the activity group and the company to update it with.
ACTIVITY_GROUP_ID = 'INSERT_ACTIVITY_GROUP_ID_HERE'
ADVERTISER_COMPANY_ID = 'INSERT_ADVERTISER_COMPANY_ID_HERE'


def main(client, activity_group_id, advertiser_company_id):
  # Initialize appropriate service.
  activity_group_service = client.GetService('ActivityGroupService',
                                             version='v202308')

  # Create statement object to select a single activity groups by ID.
  statement = (ad_manager.StatementBuilder(version='v202308')
               .Where('id = :activityGroupId')
               .WithBindVariable('activityGroupId', int(activity_group_id))
               .Limit(1))

  # Get activity groups by statement.
  response = activity_group_service.getActivityGroupsByStatement(
      statement.ToStatement())
  if 'results' in response and len(response['results']):
    updated_activity_groups = []
    for activity_group in response['results']:
      activity_group['companyIds'].append(advertiser_company_id)
      updated_activity_groups.append(activity_group)
    # Update the activity groups on the server.
    activity_groups = activity_group_service.updateActivityGroups(
        updated_activity_groups)

    for activity_group in activity_groups:
      print(('Activity group with ID "%s" and name "%s" was updated.')
            % (activity_group['id'], activity_group['name']))
  else:
    print('No activity groups found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ACTIVITY_GROUP_ID, ADVERTISER_COMPANY_ID)
