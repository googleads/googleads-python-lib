#!/usr/bin/python
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

"""This code example updates the destination URL of a single image creative.

To determine which image creatives exist, run get_all_creatives.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp

IMAGE_CREATIVE_ID = 'INSERT_IMAGE_CREATIVE_ID_HERE'


def main(client, image_creative_id):
  # Initialize appropriate service.
  creative_service = client.GetService('CreativeService', version='v201508')

  # Create statement object to get all image creatives.
  values = [{
      'key': 'type',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'ImageCreative'
      }
  }, {
      'key': 'id',
      'value': {
          'xsi_type': 'NumberValue',
          'value': image_creative_id
      }
  }]
  query = 'WHERE creativeType = :type AND id = :id'
  statement = dfp.FilterStatement(query, values, 1)

  # Get creatives by statement.
  response = creative_service.getCreativesByStatement(
      statement.ToStatement())

  if 'results' in response:
    # Update each local creative object by changing its destination URL.
    updated_creatives = []
    for creative in response['results']:
      creative['destinationUrl'] = 'http://news.google.com'
      updated_creatives.append(creative)

    # Update creatives remotely.
    creatives = creative_service.updateCreatives(updated_creatives)

    # Display results.
    for creative in creatives:
      print ('Image creative with id \'%s\' and destination URL \'%s\' was '
             'updated.' % (creative['id'], creative['destinationUrl']))
  else:
    print 'No creatives found to update.'

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, IMAGE_CREATIVE_ID)
