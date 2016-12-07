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

"""This example uploads an image.

To get images, run get_all_images.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import base64
from googleads import adwords


IMAGE_FILENAME = 'INSERT_IMAGE_PATH_HERE'


def main(client, image_filename):
  # Initialize appropriate service.
  media_service = client.GetService('MediaService', version='v201605')

  with open(image_filename, 'rb') as image_handle:
    image_data = base64.encodestring(image_handle.read()).decode('utf-8')

  # Construct media and upload image.
  media = [{
      'xsi_type': 'Image',
      'data': image_data,
      'type': 'IMAGE'
  }]
  media = media_service.upload(media)[0]

  # Display results.
  if media:
    dimensions = dict([(entry['key'], entry['value'])
                       for entry in media['dimensions']])
    print ('Image with id \'%s\', dimensions \'%sx%s\', and MimeType \'%s\' was'
           ' uploaded.' % (media['mediaId'], dimensions['FULL']['height'],
                           dimensions['FULL']['width'], media['mimeType']))
  else:
    print 'No images were uploaded.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, IMAGE_FILENAME)
