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

"""Creates a draft and accesses its associated draft campaign.

See the Campaign Drafts and Experiments guide for more information:
https://developers.google.com/adwords/api/docs/guides/campaign-drafts-experiments

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid
from googleads import adwords


BASE_CAMPAIGN_ID = 'INSERT_BASE_CAMPAIGN_ID_HERE'


def main(client, base_campaign_id):
  draft_service = client.GetService('DraftService', version='v201702')

  draft = {
      'baseCampaignId': base_campaign_id,
      'draftName': 'Test Draft #%s' % uuid.uuid4()
  }

  draft_operation = {'operator': 'ADD', 'operand': draft}
  draft = draft_service.mutate([draft_operation])['value'][0]
  draft_campaign_id = draft['draftCampaignId']

  # Once the draft is created, you can modify the draft campaign as if it were a
  # real campaign. For example, you may add criteria, adjust bids, or even
  # include additional ads. Adding a criteria is shown here.
  campaign_criterion_service = client.GetService('CampaignCriterionService',
                                                 version='v201702')

  criterion = {
      'xsi_type': 'Language',
      'id': 1003  # Spanish
  }

  criterion_operation = {
      # Make sure to use the draftCampaignId when modifying the virtual draft
      # campaign.
      'operator': 'ADD',
      'operand': {
          'campaignId': draft_campaign_id,
          'criterion': criterion
      }
  }

  criterion = campaign_criterion_service.mutate([criterion_operation])[
      'value'][0]

  print ('Draft updated to include criteria in campaign with ID %d' %
         draft_campaign_id)


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, BASE_CAMPAIGN_ID)
