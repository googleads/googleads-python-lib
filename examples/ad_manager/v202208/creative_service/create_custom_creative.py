#!/usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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

"""This example creates a custom creative for a given advertiser.

This feature is only available to Ad Manager 360 solution networks. To determine
which companies are advertisers, run get_advertisers.py. To determine
which creative templates exist, run get_all_creative_templates.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import os
import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set id of the advertiser (company) that the creative will be assigned to.
ADVERTISER_ID = 'INSERT_ADVERTISER_COMPANY_ID_HERE'


def main(client, advertiser_id):
  # Initialize appropriate service.
  creative_service = client.GetService('CreativeService', version='v202208')

  # Get the image data for the creative.
  image_data = open(os.path.join(os.path.split(__file__)[0], '..', '..', 'data',
                                 'medium_rectangle.jpg'), 'r').read()

  # Create the HTML snippet used in the custom creative.
  html_snippet = ('<a href=\'%s%s\'><img src="%s"/></a><br>Click above for '
                  'great deals!') % ('%%CLICK_URL_UNESC%%', '%%DEST_URL%%',
                                     '%%FILE:IMAGE_ASSET%%')

  # Create custom creative.
  creative = {
      'xsi_type': 'CustomCreative',
      'name': 'Custom Creative #%s' % uuid.uuid4(),
      'advertiserId': advertiser_id,
      'size': {'width': '300', 'height': '250'},
      'destinationUrl': 'http://google.com',
      'customCreativeAssets': [
          {
              'xsi_type': 'CustomCreativeAsset',
              'macroName': 'IMAGE_ASSET',
              'asset': {
                  'assetByteArray': image_data,
                  'fileName': 'image%s.jpg' % uuid.uuid4()
              }
          }
      ],
      'htmlSnippet': html_snippet
  }

  # Call service to create the creative.
  creatives = creative_service.createCreatives([creative])

  # Display results.
  if creatives:
    creative = creatives[0]
    print('Template creative with id "%s", name "%s", and type "%s" was '
          'created and can be previewed at %s.'
          % (creative['id'], creative['name'],
              ad_manager.AdManagerClassType(creative), creative['previewUrl']))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ADVERTISER_ID)
