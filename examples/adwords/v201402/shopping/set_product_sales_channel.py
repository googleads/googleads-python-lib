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

"""This example sets the product sales channel.

Tags: CampaignCriterionService.mutate
"""

__author__ = ('api.msaniscalchi@gmail.com (Mark Saniscalchi)',
              'Joseph DiLallo')

# Import appropriate classes from the client library.
from googleads import adwords

CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'

# ProductSalesChannel is a fixedId criterion, with the possible values
# defined here.
ONLINE = '200'
LOCAL = '201'


def main(client, campaign_id):
  campaign_criterion_service = client.GetService(
      'CampaignCriterionService', version='v201402')

  product_sales_channel = {
      'xsi_type': 'ProductSalesChannel',
      'id': ONLINE
  }

  campaign_criterion = {
      'campaignId': campaign_id,
      'criterion': product_sales_channel
  }

  operations = [{
      'operator': 'ADD',
      'operand': campaign_criterion
  }]

  result = campaign_criterion_service.mutate(operations)

  for criterion in result['value']:
    print ('Added ProductSalesChannel CampaignCriterion with ID: %s'
           % (criterion['criterion']['id']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
