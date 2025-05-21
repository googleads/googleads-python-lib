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

"""This code example creates a new video creative for a given advertiser.

To determine which companies are advertisers, run get_advertisers.py.
To determine which creatives already exist, run get_all_creatives.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""

import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set id of the advertiser (company) that the creative will be assigned to.
ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'


def main(client, advertiser_id):
  # Initialize appropriate service.
  creative_service = client.GetService('CreativeService', version='v202505')

  # Create a video creative.
  creative = {
      'xsi_type': 'VideoCreative',
      'name': 'Video Creative #%s' % uuid.uuid4(),
      'advertiserId': advertiser_id,
      'size': {'width': '640', 'height': '360', 'isAspectRatio': False},
      'destinationUrl': 'https://google.com',
      'duration': '115000',
      'videoSourceUrl': (
          'https://storage.googleapis.com/interactive-media-ads/media/'
          'android.mp4')
  }

  # Call service to create the creative.
  creative = creative_service.createCreatives([creative])[0]

  # Display results.
  print('Video creative with id "%s" and name "%s" was created and can be '
        'previewed at:\n%s.'
        % (creative['id'], creative['name'], creative['vastPreviewUrl']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, ADVERTISER_ID)
