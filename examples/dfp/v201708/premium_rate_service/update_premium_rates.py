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

"""This example updates a premium rate to add a flat fee to an existing feature.

To determine which premium rates exist, run get_all_premium_rates.py.

"""


# Import appropriate modules from the client library.
from googleads import dfp

PREMIUM_RATE_ID = 'INSERT_PREMIUM_RATE_ID_HERE'


def main(client, premium_rate_id):
  # Initialize appropriate service.
  premium_rate_service = client.GetService('PremiumRateService',
                                           version='v201708')

  # Create statement object to select a single proposal by an ID.
  values = [{
      'key': 'id',
      'value': {
          'xsi_type': 'NumberValue',
          'value': premium_rate_id
      }
  }]
  query = 'WHERE id = :id ORDER BY id ASC'
  statement = dfp.FilterStatement(query, values, 1)

  # Get the premium rate.
  response = premium_rate_service.getPremiumRatesByStatement(
      statement.ToStatement())

  if 'results' in response:
    updated_premium_rates = []
    for premium_rate in response['results']:
      # Create a flat fee based premium rate value with a 10% increase.
      new_flat_fee_rate = {
          'premiumFeature': premium_rate['premiumFeature'],
          'rateType': 'CPM',
          'adjustmentSize': 10000,
          'adjustmentType': 'PERCENTAGE'
      }

      # Update the premium rate's premiumRateValues to include a flat fee
      # premium rate.

      existing_premium_rate_value = (
          [] if 'premiumRateValues' not in premium_rate else
          premium_rate['premiumRateValues'])
      existing_premium_rate_value.append(new_flat_fee_rate)
      premium_rate['premiumRateValues'] = existing_premium_rate_value

      updated_premium_rates.append(premium_rate)

    # Update products remotely.
    premium_rates = premium_rate_service.updatePremiumRates(
        updated_premium_rates)

    # Display results.
    if premium_rates:
      for premium_rate in premium_rates:
        print ('Premium rate with ID "%s", associated with rate card id'
               ' "%s" was updated.' % (premium_rate['id'],
                                       premium_rate['rateCardId']))
    else:
      print 'No premium rates were updated.'
  else:
    print 'No premium rates found to update.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PREMIUM_RATE_ID)
