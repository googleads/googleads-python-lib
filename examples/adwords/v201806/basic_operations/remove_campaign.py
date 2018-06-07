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

"""This example deletes a campaign by setting the status to 'REMOVED'.

To get campaigns, run get_campaigns.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'


def main(client, campaign_id):
  # Initialize appropriate service.
  campaign_service = client.GetService('CampaignService', version='v201806')

  # Construct operations and delete campaign.
  operations = [{
      'operator': 'SET',
      'operand': {
          'id': campaign_id,
          'status': 'REMOVED'
      }
  }]
  result = campaign_service.mutate(operations)

  # Display results.
  for campaign in result['value']:
    print ('Campaign with name "%s" and id "%s" was deleted.'
           % (campaign['name'], campaign['id']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
