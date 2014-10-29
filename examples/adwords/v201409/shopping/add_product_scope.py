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

"""Restricts  products that will be included in a campaign with a ProductScope.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: CampaignCriterionService.mutate
"""

__author__ = ('api.msaniscalchi@gmail.com (Mark Saniscalchi)',
              'Joseph DiLallo')

# Import appropriate modules from the client library.
from googleads import adwords

CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'


def main(client, campaign_id):
  campaign_criterion_service = client.GetService(
      'CampaignCriterionService', version='v201409')

  product_scope = {
      'xsi_type': 'ProductScope',
      # This set of dimensions is for demonstration purposes only. It would be
      # extremely unlikely that you want to include so many dimensions in your
      # product scope.
      'dimensions': [
          {
              'xsi_type': 'ProductBrand',
              'value': 'Nexus'
          },
          {
              'xsi_type': 'ProductCanonicalCondition',
              'condition': 'NEW'
          },
          {
              'xsi_type': 'ProductCustomAttribute',
              'type': 'CUSTOM_ATTRIBUTE_0',
              'value': 'my attribute value'
          },
          {
              'xsi_type': 'ProductOfferId',
              'value': 'book1'
          },
          {
              'xsi_type': 'ProductType',
              'type': 'PRODUCT_TYPE_L1',
              'value': 'Media'
          },
          {
              'xsi_type': 'ProductType',
              'type': 'PRODUCT_TYPE_L2',
              'value': 'Books'
          },
          # The value for the bidding category is a fixed ID for the "Luggage
          # & Bags" category. You can retrieve IDs for categories from the
          # ConstantDataService. See the "GetProductCategoryTaxonomy" example
          # for more details.
          {
              'xsi_type': 'ProductBiddingCategory',
              'type': 'BIDDING_CATEGORY_L1',
              'value': '-5914235892932915235'
          }
      ]
  }

  campaign_criterion = {
      'campaignId': campaign_id,
      'criterion': product_scope
  }

  operations = [{
      'operator': 'ADD',
      'operand': campaign_criterion
  }]

  # Make the request
  result = campaign_criterion_service.mutate(operations)

  for criterion in result['value']:
    print ('Created a ProductScope criterion with Id: %s'
           % criterion['criterion']['id'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, CAMPAIGN_ID)
