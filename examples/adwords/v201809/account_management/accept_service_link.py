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

"""This example accepts a pending Google Merchant Center invitation link.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


from googleads import adwords


SERVICE_LINK_ID = 'INSERT_SERVICE_LINK_ID_HERE'


def main(client, service_link_id):
  # Initialize appropriate service.
  customer_service = client.GetService(
      'CustomerService', version='v201809')

  # Create the operation to set the status to ACTIVE.
  operations = [{
      'operator': 'SET',
      'operand': {
          'serviceLinkId': service_link_id,
          'serviceType': 'MERCHANT_CENTER',
          'linkStatus': 'ACTIVE',
      }
  }]

  # Update the service link.
  mutated_service_links = customer_service.mutateServiceLinks(operations)

  # Display results.
  for mutated_service_link in mutated_service_links:
    print ('Service link with service link ID "%s", type "%s" was updated '
           'to status: "%s".' % (mutated_service_link['serviceLinkId'],
                                 mutated_service_link['serviceType'],
                                 mutated_service_link['linkStatus']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client, SERVICE_LINK_ID)
