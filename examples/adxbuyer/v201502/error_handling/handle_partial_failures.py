#!/usr/bin/python
#
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""


import re

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  # Enable partial failure.
  client.partial_failure = True

  # Initialize appropriate service.
  ad_group_criterion_service = client.GetService(
      'AdGroupCriterionService', version='v201502')

  # Construct placement ad group criteria objects.
  placements = [
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Placement',
              'url': 'www.example.com/something'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Placement',
              'url': 'INVALID!!_URL'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Placement',
              'url': 'www.example.com/somethingelse'
          }
      },
      {
          'xsi_type': 'BiddableAdGroupCriterion',
          'adGroupId': ad_group_id,
          'criterion': {
              'xsi_type': 'Placement',
              'url': 'BAD!!_URL'
          }
      }
  ]

  # Construct operations and add ad group criteria.
  operations = []
  for placement in placements:
    operations.append(
        {
            'operator': 'ADD',
            'operand': placement
        })
  result = ad_group_criterion_service.mutate(operations)

  # Display results.
  for criterion in result['value']:
    if criterion['AdGroupCriterion.Type'] == 'BiddableAdGroupCriterion':
      print ('Added placement ad group criterion with ad group id \'%s\', '
             'criterion id \'%s\' and url \'%s\''
             % (criterion['adGroupId'], criterion['criterion']['id'],
                criterion['criterion']['url']))

  for error in result['partialFailureErrors']:
    index = re.findall(r'operations\[(.*)\]\.', error['fieldPath'])
    if index:
      print ('Placement ad group criterion with ad group id \'%s\' and url '
             '\'%s\' triggered a failure for the following reason: \'%s\'.'
             % (placements[int(index[0])]['adGroupId'],
                placements[int(index[0])]['criterion']['url'],
                error['errorString']))
    else:
      print 'The following failure has occurred: \'%s\'.' % error['errorString']


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
