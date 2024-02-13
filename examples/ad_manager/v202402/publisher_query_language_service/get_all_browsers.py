#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""This example gets all browsers available to target from the Browser table.

Other tables include 'Bandwidth_Group', 'Browser_Language',
'Device_Capability', 'Operating_System', etc...

A full list of available criteria tables can be found at
https://developers.google.com/doubleclick-publishers/docs/reference/v201708/PublisherQueryLanguageService
"""


import tempfile

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize a report downloader.
  report_downloader = client.GetDataDownloader(version='v202402')

  with tempfile.NamedTemporaryFile(
      prefix='browser_data_',
      suffix='.csv', mode='w', delete=False) as browser_data_file:

    browser_pql_query = ('SELECT Id, BrowserName, MajorVersion, MinorVersion '
                         'FROM Browser '
                         'ORDER BY BrowserName ASC')

    # Downloads the response from PQL select statement to the specified file
    report_downloader.DownloadPqlResultToCsv(
        browser_pql_query, browser_data_file)

  print('Saved browser data to... %s' % browser_data_file.name)


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
