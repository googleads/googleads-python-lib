#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""This example creates a new rate card.

To determine which rate cards exist, run get_all_rate_cards.py.
"""

# Import appropriate modules from the client library.
import random

from googleads import ad_manager

# Set the IDs of the teams this rate card should be visible to.
TEAM_IDS = ['INSERT_TEAM_ID_HERE']

# Set the currency code to create the rate card with.
CURRENCY_CODE = 'INSERT_CURRENCY_CODE_HERE'


def main(client):
  # Initialize appropriate service.
  rate_card_service = client.GetService('RateCardService', version='v201811')

  # Create a rate card.
  rate_card = {
      'name': 'RateCard #%d' % random.randint(0, 100000000),
      'currencyCode': CURRENCY_CODE,
      'pricingModel': 'NET',
  }

  # This field is optional.
  rate_card['appliedTeamIds'] = TEAM_IDS

  result = rate_card_service.createRateCards([rate_card])

  for new_rate_card in result:
    print ('A rate card with ID %s, name "%s", and currency code "%s" '
           'was created.' % (new_rate_card['id'],
                             new_rate_card['name'],
                             new_rate_card['currencyCode']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
