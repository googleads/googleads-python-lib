#!/usr/bin/env python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example uploads an image asset.

To get image assets, run get_all_image_assets.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords
import requests


def main(client):
  # Initialize appropriate service.
  asset_service = client.GetService('AssetService', version='v201809')

  image_request = requests.get('https://goo.gl/3b9Wfh')
  image_data = image_request.content

  # Construct media and upload image asset.
  image_asset = {
      'xsi_type': 'ImageAsset',
      # Optional: Provide a unique friendly name to identify your asset. If you
      # specify the assetName field, then both the asset name and the image
      # being uploaded should be unique, and should not match another ACTIVE
      # asset in this customer account.
      # 'assetName': 'Jupiter Trip #' + str(uuid.uuid4())[:8],
      'imageData': image_data,

  }

  operation = {'operator': 'ADD', 'operand': image_asset}

  asset = asset_service.mutate([operation])['value'][0]

  # Display results.
  if asset:
    print('Image asset with id %s, name "%s", and status %s was created.\n'
          '\tSize is %sx%s and asset URL is %s.' %
          (asset['assetId'], asset['assetName'], asset['assetStatus'],
           asset['fullSizeInfo']['imageWidth'],
           asset['fullSizeInfo']['imageHeight'],
           asset['fullSizeInfo']['imageUrl']))
  else:
    print('No images were uploaded.')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
