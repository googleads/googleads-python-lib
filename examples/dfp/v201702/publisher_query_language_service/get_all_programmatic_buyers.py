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

"""This example fetches programmatic buyer information from the PQL table."""


import tempfile

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize a report downloader.
  data_downloader = client.GetDataDownloader(version='v201702')

  programmatic_buyers_file = tempfile.NamedTemporaryFile(
      prefix='programmatic_buyers_', suffix='.csv', mode='w', delete=False)

  programmatic_buyers_query = ('SELECT BuyerAccountId, Name '
                               'FROM Programmatic_Buyer '
                               'ORDER BY BuyerAccountId ASC')

  # Downloads the response from PQL select statement to the specified file
  data_downloader.DownloadPqlResultToCsv(
      programmatic_buyers_query, programmatic_buyers_file)

  programmatic_buyers_file.close()

  print 'Saved programmatic buyers to... %s' % programmatic_buyers_file.name


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
