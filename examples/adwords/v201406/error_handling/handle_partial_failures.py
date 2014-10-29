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

"""This example demonstrates how to handle partial failures.

To get ad groups, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: AdGroupCriterionService.mutate
"""

__author__ = ('api.kwinter@gmail.com (Kevin Winter)'
              'Joseph DiLallo')

import re

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Enable partial failure.
  client.partial_failure = True

  # Initialize appropriate service.
  ad_group_criterion_service = client.GetService(
      'AdGroupCriterionService', version='v201406')

  # Construct keyword ad group criteria objects.
  keywords = [
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': 'mars cruise'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': r'inv\@lid cruise'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': 'venus cruise'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Keyword',
              'matchType': 'BROAD',
              'text': r'b\(a\)d keyword cruise'
          }
      }
  ]

  # Construct operations and add ad group criteria.
  operations = []
  for keyword in keywords:
    operations.append(
        {
            'operator': 'ADD',
            'operand': keyword
        })
  result = ad_group_criterion_service.mutate(operations)

  # Display results.
  for criterion in result['value']:
    if criterion['AdGroupCriterion.Type'] == 'BiddableAdGroupCriterion':
      print ('Added keyword ad group criterion with ad group id \'%s\', '
             'criterion id \'%s\', text \'%s\', and match type \'%s\' was '
             'added.'
             % (criterion['adGroupId'], criterion['criterion']['id'],
                criterion['criterion']['text'],
                criterion['criterion']['matchType']))

  for error in result['partialFailureErrors']:
    index = re.findall(r'operations\[(.*)\]\.', error['fieldPath'])
    if index:
      print ('Keyword ad group criterion with ad group id \'%s\' and text '
             '\'%s\' triggered a failure for the following reason: \'%s\'.'
             % (keywords[int(index[0])]['adGroupId'],
                keywords[int(index[0])]['criterion']['text'],
                error['errorString']))
    else:
      print 'The following failure has occurred: \'%s\'.' % error['errorString']


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
