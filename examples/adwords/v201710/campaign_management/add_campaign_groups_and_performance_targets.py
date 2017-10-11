#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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

"""This example adds a campaign group and sets a performance target for it.

To get campaigns, run get_campaigns.py. To download reports, run
download_criteria_report_with_awql.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""

import datetime
import uuid
from googleads import adwords


CAMPAIGN_ID1 = 'INSERT_FIRST_CAMPAIGN_ID_HERE'
CAMPAIGN_ID2 = 'INSERT_SECOND_CAMPAIGN_ID_HERE'


def main(client, campaign_id1, campaign_id2):
  campaign_group_id = _CreateCampaignGroup(client)
  _AddCampaignsToGroup(client, campaign_group_id, [campaign_id1, campaign_id2])
  _CreatePerformanceTarget(client, campaign_group_id)
  print 'Campaign group and its performance target were setup successfully.'


def _CreateCampaignGroup(client):
  """Create a campaign group.

  Args:
    client: an AdWordsClient instance.

  Returns:
    The integer ID of the created campaign group.
  """
  # Get the CampaignGroupService.
  campaign_group_service = client.GetService('CampaignGroupService',
                                             version='v201710')

  # Create the operation.
  operations = [{
      'operator': 'ADD',
      # Create the campaign group.
      'operand': {
          'name': 'Mars campaign group #%d' % uuid.uuid4()
      }
  }]

  campaign_group = campaign_group_service.mutate(operations)['value'][0]
  campaign_group_id = campaign_group['id']

  # Display the results.
  print 'Campaign group with ID "%d" and name "%s" was created.' % (
      campaign_group_id, campaign_group['name'])

  return campaign_group_id


def _AddCampaignsToGroup(client, campaign_group_id, campaign_ids):
  """Adds multiple campaigns to a campaign group.

  Args:
    client: an AdWordsClient instance.
    campaign_group_id: an integer ID for the campaign group.
    campaign_ids: a list of integer IDs for campaigns.
  """
  # Get the CampaignService.
  campaign_service = client.GetService('CampaignService', version='v201710')

  # Create the operations.
  operations = [{
      'operator': 'SET',
      'operand': {
          'id': campaign_id,
          'campaignGroupId': campaign_group_id
      }
  } for campaign_id in campaign_ids]

  campaign_service.mutate(operations)

  # Display the results.
  print ('The following campaign IDs were added to the campaign group with ID '
         '"%d":\n\t%s' % (campaign_group_id, campaign_ids))


def _CreatePerformanceTarget(client, campaign_group_id):
  """Creates a performance target for the campaign group.

  Args:
    client: an AdWordsClient instance.
    campaign_group_id: an integer ID for the campaign group.
  """
  # Get the CampaignGroupPerformanceTargetService.
  cgpt_service = client.GetService('CampaignGroupPerformanceTargetService',
                                   version='v201710')

  # Create the operation.
  operations = [{
      'operator': 'ADD',
      # Create the performance target.
      'operand': {
          'campaignGroupId': campaign_group_id,
          'performanceTarget': {
              # Keep the CPC for the campaigns < $3.
              'efficiencyTargetType': 'CPC_LESS_THAN_OR_EQUAL_TO',
              'efficiencyTargetValue': 3000000,
              # Keep the maximum spend under $50.
              'spendTargetType': 'MAXIMUM',
              'spendTarget': {
                  'microAmount': 500000000
              },
              # Aim for at least 3000 clicks.
              'volumeGoalType': 'MAXIMIZE_CLICKS',
              'volumeTargetValue': 3000,
              # Start the performance target today, and run it for the next 90
              # days.
              'startDate': datetime.datetime.now().strftime('%Y%m%d'),
              'endDate': (datetime.datetime.now() +
                          datetime.timedelta(90)).strftime('%Y%m%d')
          }
      }
  }]

  cgpt = cgpt_service.mutate(operations)['value'][0]

  # Display the results.
  print ('Campaign performance target with ID "%d" was added for campaign '
         'group ID "%d".' % (cgpt['id'], cgpt['campaignGroupId']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID1, CAMPAIGN_ID2)
