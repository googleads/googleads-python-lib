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

"""This example gets all line items with names starting with 'line item'."""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

import tempfile

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize a report downloader.
  report_downloader = client.GetDataDownloader(version='v201408')

  output_file = tempfile.NamedTemporaryFile(
      prefix='line_items_named_like_', suffix='.csv', mode='w', delete=False)

  # Create bind value to select line items with names starting with 'line item'.
  values = [{
      'key': 'name',
      'value': {
          'xsi_type': 'TextValue',
          'value': 'line item%'
      }
  }]

  pql_query = ('SELECT Name, Id, Status FROM Line_Item '
               'WHERE Name LIKE :name')

  # Downloads the response from PQL select statement to the specified file
  report_downloader.DownloadPqlResultToCsv(
      pql_query, output_file, values)
  output_file.close()

  print ('Saved line items to... %s' % output_file.name)


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
