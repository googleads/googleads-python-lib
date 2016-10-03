#!/usr/bin/python
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


import re
import suds

from googleads import adwords

AD_GROUP_ID = 'INSERT_AD_GROUP_ID_HERE'


def main(client, ad_group_id):
  ad_group_ad_service = client.GetService('AdGroupAdService', 'v201609')

  # Create text ad.
  text_ad_operation = {
      'operator': 'ADD',
      'operand': {
          'adGroupId': ad_group_id,
          'ad': {
              # The 'xsi_type' field allows you to specify the xsi:type of the
              # object being created. It's only necessary when you must provide
              # an explicit type that the client library can't infer.
              'xsi_type': 'TextAd',
              'headline': 'Mars Cruise!!!',
              'description1': 'Visit the Red Planet in style.',
              'description2': 'Low-gravity fun for everyone!',
              'finalUrls': ['http://www.example.com'],
              'displayUrl': 'www.example.com',
          }
      }
  }

  operations = [text_ad_operation]

  # Validate the ad.
  try:
    # Enable "validate only" to check for errors.
    client.validate_only = True
    ad_group_ad_service.mutate(operations)
    print 'Validation successful, no errors returned.'
  except suds.WebFault, e:
    for error in e.fault.detail.ApiExceptionFault.errors:
      if error['ApiError.Type'] == 'PolicyViolationError':
        operation_index = re.findall(r'operations\[(.*)\]\.',
                                     error['fieldPath'])
        if operation_index:
          operation = operations[int(operation_index[0])]
          print ('Ad with headline \'%s\' violated %s policy \'%s\'.' %
                 (operation['operand']['ad']['headline'],
                  'exemptable' if error['isExemptable'] else 'non-exemptable',
                  error['externalPolicyName']))
          if error['isExemptable'].lower() == 'true':
            # Add exemption request to the operation.
            print ('Adding exemption request for policy name \'%s\' on text '
                   '\'%s\'.' %
                   (error['key']['policyName'], error['key']['violatingText']))
            if 'exemptionRequests' not in operation:
              operation['exemptionRequests'] = []
            operation['exemptionRequests'].append({
                'key': error['key']
            })
        else:
          # Remove non-exemptable operation
          print 'Removing the operation from the request.'
          operations.delete(operation)
      else:
        # Non-policy error returned, re-throw exception.
        raise e

  # Add these ads. Disable "validate only" so the ads will get created.
  client.validate_only = False
  if operations:
    response = ad_group_ad_service.mutate(operations)
    if response and response['value']:
      ads = response['value']
      print 'Added %s ad(s) to ad group %s.' % (len(ads), ad_group_id)
      for ad in ads:
        print ('  Ad id is %s, type is %s and status is \'%s\'.' %
               (ad['ad']['id'], ad['ad']['Ad.Type'], ad['status']))
    else:
      print 'No ads were added.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, AD_GROUP_ID)
