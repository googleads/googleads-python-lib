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

"""This code example gets all image creatives.

To create an image creative, run create_creatives.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  creative_service = client.GetService('CreativeService', version='v201511')

  # Create statement object to only select image creatives.
  values = [{
      'key': 'creativeType',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'ImageCreative'
      }
  }]
  query = 'WHERE creativeType = :creativeType'
  statement = dfp.FilterStatement(query, values)

  # Get creatives by statement.
  while True:
    response = creative_service.getCreativesByStatement(
        statement.ToStatement())
    creatives = response['results']

    if creatives:
      # Display results.
      for creative in creatives:
        print ('Creative with id \'%s\', name \'%s\', and type \'%s\' was '
               'found.' % (creative['id'], creative['name'],
                           dfp.DfpClassType(creative)))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
