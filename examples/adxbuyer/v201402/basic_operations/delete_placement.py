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

"""This example deletes an ad group criterion using the 'DELETE' operator.

To get ad group criteria, run get_placements.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: AdGroupCriterionService.mutate
"""

__author__ = 'api.kwinter@gmail.com (Kevin Winter)'

from googleads import adwords


AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'
CRITERION_ID = 'INSERT_CRITERION_ID_HERE'


def main(client, ad_group_id, criterion_id):
  # Initialize appropriate service.
  ad_group_criterion_service = client.GetService(
      'AdGroupCriterionService', version='v201402')

  # Construct operations and delete ad group criteria.
  operations = [
      {
          'operator': 'DELETE',
          'operand': {
              'xsi_type': 'BiddableAdGroupCriterion',
              'adGroupId': ad_group_id,
              'criterion': {
                  'xsi_type': 'Placement',
                  'id': criterion_id
              }
          }
      }
  ]
  result = ad_group_criterion_service.mutate(operations)

  # Display results.
  for criterion in result['value']:
    print ('Ad group criterion with ad group id \'%s\', criterion id \'%s\', '
           'and type \'%s\' was deleted.'
           % (criterion['adGroupId'], criterion['criterion']['id'],
              criterion['criterion']['Criterion.Type']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID, CRITERION_ID)
