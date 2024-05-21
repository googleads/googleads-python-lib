#!/usr/bin/env python
#
# Copyright 2021, Google LLC
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

"""This example pushes a LICA to a linked device for preview.

To determine which linked devices exist, use the PublisherQueryLanguageService
linked_device table.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the associated line item id and creative id to push, and set the linked
# device id where it will be pushed.
LINE_ITEM_ID = 'INSERT_LINE_ITEM_ID_HERE'
CREATIVE_ID = 'INSERT_CREATIVE_ID_HERE'
LINKED_DEVICE_ID = 'INSERT_LINKED_DEVICE_ID_HERE'


def main(client, line_item_id, creative_id, linked_device_id):
  # Initialize appropriate service.
  lica_service = client.GetService(
      'LineItemCreativeAssociationService', version='v202405')

  # Create query to select a single linked device.
  # Linked devices can be read from the linked_device PQL table.
  statement = (ad_manager.StatementBuilder(version='v202405')
               .Where('id = :linkedDeviceId')
               .WithBindVariable('linkedDeviceId', int(linked_device_id)))

  # Make call to push creatives to devices.
  result = lica_service.pushCreativeToDevices(statement.ToStatement(), {
      'lineItemId': line_item_id,
      'creativeId': creative_id
  })

  # Display results.
  if result and int(result['numChanges']) > 0:
    print('Pushed creatives to %s devices.' % result['numChanges'])
  else:
    print('No creatives were pushed.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, LINE_ITEM_ID, CREATIVE_ID, LINKED_DEVICE_ID)
