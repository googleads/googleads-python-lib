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

"""This example adds various types of negative criteria to a customer.

These criteria will be applied to all campaigns for the customer.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


def main(client):
  # Initialize appropriate service.
  customer_negative_criterion_service = client.GetService(
      'CustomerNegativeCriterionService', version='v201710')

  criteria = [
      # Exclude tragedy & conflict content.
      {
          'xsi_type': 'ContentLabel',
          'contentLabelType': 'TRAGEDY'
      },
      # Exclude a specific placement.
      {
          'xsi_type': 'Placement',
          'url': 'http://www.example.com'
      }
      # Additional criteria types are available for this service. See the types
      # listed under Criterion here:
      # https://developers.google.com/adwords/api/docs/reference/latest/CustomerNegativeCriterionService.Criterion
  ]

  # Create operations to add each of the criteria above.
  operations = [{
      'operator': 'ADD',
      'operand': {
          'criterion': criterion
      }
  } for criterion in criteria]

  # Make the mutate request.
  result = customer_negative_criterion_service.mutate(operations)

  # Display the resulting campaign criteria.
  for negative_criterion in result['value']:
    print ('Customer negative criterion with criterion ID "%s", and type "%s" '
           'was added.' % (negative_criterion['criterion']['id'],
                           negative_criterion['criterion']['type']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
