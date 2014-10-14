#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""This example gets all images and videos.

To upload an image, run upload_image.py. To upload video, see:
http://adwords.google.com/support/aw/bin/answer.py?hl=en&answer=39454.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: MediaService.get
"""

__author__ = ('api.kwinter@gmail.com (Kevin Winter)'
              'Joseph DiLallo')

from googleads import adwords


PAGE_SIZE = 500


def main(client):
  # Initialize appropriate service.
  media_service = client.GetService('MediaService', version='v201409')

  # Construct selector and get all images.
  offset = 0
  selector = {
      'fields': ['MediaId', 'Type', 'Width', 'Height', 'MimeType'],
      'predicates': [{
          'field': 'Type',
          'operator': 'IN',
          'values': ['IMAGE', 'VIDEO']
      }],
      'paging': {
          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)
      }
  }
  more_pages = True
  while more_pages:
    page = media_service.get(selector)

    # Display results.
    if 'entries' in page:
      for image in page['entries']:
        dimensions = dict([(entry['key'], entry['value'])
                           for entry in image['dimensions']])
        print ('Media with id \'%s\', dimensions \'%sx%s\', and MimeType \'%s\''
               ' was found.' % (image['mediaId'], dimensions['FULL']['height'],
                                dimensions['FULL']['width'], image['mimeType']))
    else:
      print 'No images/videos were found.'
    offset += PAGE_SIZE
    selector['paging']['startIndex'] = str(offset)
    more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
