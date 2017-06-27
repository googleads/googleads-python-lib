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

"""This example adds a label to multiple campaigns.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


CAMPAIGN_ID1 = 'INSERT_FIRST_CAMPAIGN_ID_HERE'
CAMPAIGN_ID2 = 'INSERT_SECOND_CAMPAIGN_ID_HERE'
LABEL_ID = 'INSERT_LABEL_ID_HERE'


def main(client, campaign_id1, campaign_id2, label_id):
  # Initialize appropriate service.
  campaign_service = client.GetService('CampaignService', version='v201702')

  operations = [
      {
          'operator': 'ADD',
          'operand': {
              'campaignId': campaign_id1,
              'labelId': label_id,
          }
      },
      {
          'operator': 'ADD',
          'operand': {
              'campaignId': campaign_id2,
              'labelId': label_id,
          }
      }
  ]

  result = campaign_service.mutateLabel(operations)

  # Display results.
  for label in result['value']:
    print ('CampaignLabel with campaignId "%s" and labelId "%s" was added.'
           % (label['campaignId'], label['labelId']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID1, CAMPAIGN_ID2, LABEL_ID)
