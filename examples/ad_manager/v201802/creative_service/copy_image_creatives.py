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

"""This example creates a copy of an image creative.

To determine which image creatives exist, run get_image_creatives.py
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the line item to pause.
CREATIVE_ID = 'INSERT_CREATIVE_ID_HERE'


def main(client):
  # Initialize appropriate service.
  creative_service = client.GetService('CreativeService', version='v201802')

  # Create a statement to get the image creative.
  statement = (ad_manager.StatementBuilder()
               .Where('id = :id')
               .OrderBy('id', ascending=True)
               .WithBindVariable('id', CREATIVE_ID))

  # Get the creative.
  query_result = creative_service.getCreativesByStatement(
      statement.ToStatement())

  image_creative = query_result['results'][0]

  # Build the new creative, set id to None to create a copy.
  image_creative['id'] = None
  image_creative['name'] = 'Copy of %s' % image_creative['name']

  result = creative_service.createCreatives([image_creative])[0]
  print ('A creative with ID %d, name "%s", and type "%s" was created and '
         'can be previewed at: %s' % (result['id'],
                                      result['name'],
                                      ad_manager.AdManagerClassType(result),
                                      result['previewUrl']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
