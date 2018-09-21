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

"""This example updates the bid of a keyword.

To add a keyword, run add_keywords.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'
CRITERION_ID = 'INSERT_KEYWORD_CRITERION_ID_HERE'


def main(client, ad_group_id, criterion_id):
  # Initialize appropriate service.
  ad_group_criterion_service = client.GetService(
      'AdGroupCriterionService', version='v201809')

  # Construct operations and update bids.

  operations = [{
      'operator': 'SET',
      'operand': {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'id': criterion_id,
          },
          'biddingStrategyConfiguration': {
              'bids': [
                  {
                      'xsi_type': 'CpcBid',
                      'bid': {
                          'microAmount': '1000000'
                      }
                  }
              ]
          }
      }
  }]
  ad_group_criteria = ad_group_criterion_service.mutate(operations)

  # Display results.
  if 'value' in ad_group_criteria:
    for criterion in ad_group_criteria['value']:
      if criterion['criterion']['Criterion.Type'] == 'Keyword':
        print ('Ad group criterion with ad group id "%s" and criterion id '
               '"%s" currently has bids:'
               % (criterion['adGroupId'], criterion['criterion']['id']))
        for bid in criterion['biddingStrategyConfiguration']['bids']:
          print '\tType: "%s", value: %s' % (bid['Bids.Type'],
                                             bid['bid']['microAmount'])
  else:
    print 'No ad group criteria were updated.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID, CRITERION_ID)
