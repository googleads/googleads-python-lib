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

"""This example gets all image assets.

To upload an image asset, run upload_image_asset.py

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


PAGE_SIZE = 500


def main(client):
  # Initialize appropriate service.
  asset_service = client.GetService('AssetService', version='v201809')

  # Construct selector and get all images.
  offset = 0
  selector = {
      'fields': ['AssetName', 'AssetStatus', 'ImageFileSize', 'ImageWidth',
                 'ImageHeight', 'ImageFullSizeUrl'],
      'predicates': [{
          'field': 'AssetSubtype',
          'operator': 'IN',
          'values': ['IMAGE']
      }],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  while more_pages:
    page = asset_service.get(selector)

    # Display results.
    if 'entries' in page:
      for image in page['entries']:
        print('Image asset with id %s, name "%s", and status %s was found.\n'
              '\tSize is %sx%s and asset URL is %s.' %
              (image['assetId'], image['assetName'], image['assetStatus'],
               image['fullSizeInfo']['imageWidth'],
               image['fullSizeInfo']['imageHeight'],
               image['fullSizeInfo']['imageUrl']))
    else:
      print('No images/videos were found.')
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])



if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
