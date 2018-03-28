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

"""This example uploads an HTML5 zip file.

"""

import urllib2
from googleads import adwords


def main(client):
  # Initialize appropriate service.
  media_service = client.GetService('MediaService', version='v201802')
  # Create HTML5 media.
  html5_zip = GetHTML5ZipFromUrl('https://goo.gl/9Y7qI2')
  # Create a media bundle containing the zip file with all the HTML5 components.
  media = [{
      'xsi_type': 'MediaBundle',
      'data': html5_zip,
      'type': 'MEDIA_BUNDLE'
  }]
  # Upload HTML5 zip.
  response = media_service.upload(media)

  if response:
    for media in response:
      print(
          'HTML5 media with ID %d, dimensions %dx%d, and MIME type "%s" '
          'uploaded successfully.' %
          (media['mediaId'], media['dimensions'][0]['value']['width'],
           media['dimensions'][0]['value']['height'], media['mimeType']))


def GetHTML5ZipFromUrl(url):
  """Retrieve zip file from the given URL."""
  response = urllib2.urlopen(url)
  # Note: The utf-8 decode is for 2to3 Python 3 compatibility.
  return response.read().decode('utf-8')


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()
  main(adwords_client)
