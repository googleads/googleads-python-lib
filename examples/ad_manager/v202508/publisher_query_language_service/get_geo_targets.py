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

"""This example downloads geo targeting constants using PQL."""


import tempfile

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the type of geo target to query for.
GEO_TARGET_TYPE = 'City'


def main(client):
  # Initialize a report downloader.
  report_downloader = client.GetDataDownloader(version='v202508')

  with tempfile.NamedTemporaryFile(
      prefix='geo_data_',
      suffix='.csv', mode='w', delete=False) as geo_data_file:

    geo_pql_query = ('SELECT Id, Name, CanonicalParentId, ParentIds, '
                     'CountryCode, Type '
                     'FROM Geo_Target '
                     'WHERE Type = :type AND Targetable = true '
                     'ORDER BY CountryCode ASC, Name ASC')

    # Downloads the response from PQL select statement to the specified file
    report_downloader.DownloadPqlResultToCsv(
        geo_pql_query, geo_data_file, {'type': geo_target_type})

  print('Saved geo data to... %s' % geo_data_file.name)


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, GEO_TARGET_TYPE)
