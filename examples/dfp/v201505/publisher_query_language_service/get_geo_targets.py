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

"""This example gets geographic criteria from the Geo_Target table.

The types available to filter on include 'City', 'Country', 'Region', 'State',
'Postal_Code', and 'DMA_Region' (i.e. Metro).

A full list of available geo target types can be found at
https://developers.google.com/doubleclick-publishers/docs/reference/v201505/PublisherQueryLanguageService
"""


import tempfile

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize a report downloader.
  report_downloader = client.GetDataDownloader(version='v201505')

  output_file = tempfile.NamedTemporaryFile(
      prefix='geo_target_type_', suffix='.csv', mode='w', delete=False)

  # Create bind value to select geo-targets of type 'City'.
  values = [{
      'key': 'type',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'City'
      }
  }]

  pql_query = ('SELECT Name, Id FROM Geo_Target '
               'WHERE targetable = true AND Type = :type')

  # Downloads the response from PQL select statement to the specified file
  report_downloader.DownloadPqlResultToCsv(
      pql_query, output_file, values)
  output_file.close()

  print ('Saved geo targets to... %s' % output_file.name)


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
