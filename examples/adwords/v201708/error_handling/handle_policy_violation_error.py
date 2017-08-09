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

"""This example demonstrates how to handle policy violation errors.

To get ad groups, run get_ad_groups.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import suds

from googleads import adwords

AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  ad_group_ad_service = client.GetService('AdGroupAdService', 'v201708')

  # Create expanded text ad that violates an exemptable policy.
  exemptable_expanded_text_ad_operation = {
      'operator': 'ADD',
      'operand': {
          'adGroupId': ad_group_id,
          'ad': {
              # The 'xsi_type' field allows you to specify the xsi:type of the
              # object being created. It's only necessary when you must provide
              # an explicit type that the client library can't infer.
              'xsi_type': 'ExpandedTextAd',
              'headlinePart1': 'Mars Cruise!!!',
              'headlinePart2': 'Best space cruise line.',
              'description': 'Visit the Red Planet in style.',
              'finalUrls': ['http://www.example.com']
          }
      }
  }

  # Create text ad that violates a non-exemptable policy.
  non_exemptable_expanded_text_ad_operation = {
      'operator': 'ADD',
      'operand': {
          'adGroupId': ad_group_id,
          'ad': {
              # The 'xsi_type' field allows you to specify the xsi:type of the
              # object being created. It's only necessary when you must provide
              # an explicit type that the client library can't infer.
              'xsi_type': 'ExpandedTextAd',
              'headlinePart1': 'Mars Cruise with too long of a headline.',
              'headlinePart2': 'Best space cruise line.',
              'description': 'Visit the Red Planet in style.',
              'finalUrls': ['http://www.example.com']
          }
      }
  }

  operations = [exemptable_expanded_text_ad_operation,
                non_exemptable_expanded_text_ad_operation]

  # Validate the ad.
  try:
    # Enable "validate only" to check for errors.
    client.validate_only = True
    ad_group_ad_service.mutate(operations)
    print 'Validation successful, no errors returned.'
  except suds.WebFault, e:
    for error in e.fault.detail.ApiExceptionFault.errors:
      # Get the index of the failed operation from the error's field path
      # elements.
      field_path_elements = error['fieldPathElements']
      first_field_path_element = None

      if field_path_elements:
        first_field_path_element = field_path_elements[0]

      # If the operation index is not present on the first error field path
      # element, then there's no way to determine which operation to remove,
      # so simply throw the exception.
      if (not (first_field_path_element
               and first_field_path_element['field'] == 'operations'
               and first_field_path_element['index'])):
        raise e

      operation_index = first_field_path_element['index']
      index = int(operation_index[0])
      operation = operations[index]
      if not HandleAPIError(error, operation):
        # Set non-exemptable operation to None to mark for deletion.
        print ('Removing operation with non-exemptable error at index %s.'
               % operation_index)
        operations[index] = None

    # Remove the non-exemptable operations.
    operations = [op for op in operations if op is not None]

  # Add these ads. Disable "validate only" so the ads will get created.
  client.validate_only = False
  if operations:
    response = ad_group_ad_service.mutate(operations)
    if response and response['value']:
      ads = response['value']
      print 'Added %s ad(s) to ad group %s.' % (len(ads), ad_group_id)
      for ad in ads:
        print ('  Ad id is %s, type is %s and status is "%s".' %
               (ad['ad']['id'], ad['ad']['Ad.Type'], ad['status']))
    else:
      print 'No ads were added.'


def HandleAPIError(error, operation):
  """Makes an exemption for exemptable PolicyViolationErrors.

  Args:
    error: the error associated with the given operation.
    operation: the operation associated with the given error.

  Returns:
    A boolean that is True if the given error was an exemptable
    PolicyViolationError; otherwise, returns False.
  """
  is_exemptable = False

  # Determine if the operation can be resubmitted with an exemption request.
  if error['ApiError.Type'] == 'PolicyViolationError':
    expanded_text_ad = operation['operand']['ad']
    is_exemptable = (error['isExemptable'] if 'isExemptable' in error else
                     False)
    print ('Ad with headline "%s - %s" violated %s policy "%s".' %
           (expanded_text_ad['headlinePart1'],
            expanded_text_ad['headlinePart2'],
            'exemptable' if is_exemptable else 'non-exemptable',
            error['externalPolicyName']))

  if is_exemptable:
    # Add exemption request to the operation.
    print ('Adding exemption request for policy name "%s" on text "%s".'
           % (error['key']['policyName'], error['key']['violatingText']))
    if 'exemptionRequests' not in operation:
      operation['exemptionRequests'] = []
    operation['exemptionRequests'].append({'key': error['key']})

  return is_exemptable


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
