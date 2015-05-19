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

"""This code example creates new premium_rates.

To determine which premium_rates exist, run get_all_premium_rates.py.
"""

__author__ = 'Nicholas Chen'


# Import appropriate modules from the client library.
from googleads import dfp

RATE_CARD_ID = 'INSERT_RATE_CARD_ID_HERE'


def main(client, rate_card_id):
  # Initialize appropriate services.
  premium_rate_service = client.GetService('PremiumRateService',
                                           version='v201505')

  # Create an ad unit premium to apply to the rate card.
  ad_unit_premium_feature = {
      'xsi_type': 'AdUnitPremiumFeature'
  }

  # Create a CPC based premium rate value with adjustments in milli amounts.
  # This will adjust a CPC priced proposal line item that has
  # inventory targeting specified by 10% of the cost associated with the rate
  # card (this comes from a percentage adjustment).
  cpc_premium_rate_value = {
      'premiumFeature': ad_unit_premium_feature,
      'rateType': 'CPC',
      'adjustmentSize': 10000,
      'adjustmentType': 'PERCENTAGE'
  }

  # Create a CPM based premium rate value with adjustments in micro amounts.
  # This will adjust a CPM priced proposal line item that has
  # inventory targeting specified by 2 units of the currency associated with
  # the rate card (this comes from absolute value adjustment).
  cpm_premium_rate_value = {
      'premiumFeature': ad_unit_premium_feature,
      'rateType': 'CPM',
      'adjustmentSize': 2000000,
      'adjustmentType': 'ABSOLUTE_VALUE'
  }

  # Create premium_rate objects.
  premium_rate = {
      'rateCardId': rate_card_id,
      'pricingMethod': 'ANY_VALUE',
      'premiumFeature': ad_unit_premium_feature,
      'premiumRateValues': [cpc_premium_rate_value, cpm_premium_rate_value]
  }

  # Add premium_rates.
  premium_rates = premium_rate_service.createPremiumRates([premium_rate])

  # Display results.
  for premium_rate in premium_rates:
    print ('A premium rate for \'%s\' was added to the rate card with ID'
           ' of \'%s\'.\n'
           % (dfp.DfpClassType(premium_rate['premiumFeature']),
              premium_rate['id']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, RATE_CARD_ID)
