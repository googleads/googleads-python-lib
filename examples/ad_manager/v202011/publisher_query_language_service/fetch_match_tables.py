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

"""This example fetches data from PQL tables and creates match table files."""


import tempfile

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize a report downloader.
  report_downloader = client.GetDataDownloader(version='v202011')

  line_items_file = tempfile.NamedTemporaryFile(
      prefix='line_items_', suffix='.csv', mode='w', delete=False)
  ad_units_file = tempfile.NamedTemporaryFile(
      prefix='ad_units_', suffix='.csv', mode='w', delete=False)

  line_items_pql_query = ('SELECT Name, Id, Status FROM Line_Item ORDER BY Id '
                          'ASC')
  ad_units_pql_query = 'SELECT Name, Id FROM Ad_Unit ORDER BY Id ASC'

  # Downloads the response from PQL select statement to the specified file
  report_downloader.DownloadPqlResultToCsv(
      line_items_pql_query, line_items_file)
  report_downloader.DownloadPqlResultToCsv(
      ad_units_pql_query, ad_units_file)

  line_items_file.close()
  ad_units_file.close()

  print('Saved line items to... %s' % line_items_file.name)
  print('Saved ad units to... %s' % ad_units_file.name)


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
