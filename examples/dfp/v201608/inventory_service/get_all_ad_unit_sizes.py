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
"""This example gets all ad unit sizes.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  ad_unit_size_service = client.GetService(
      'InventoryService', version='v201608')

  # Create a statement to select ad unit sizes.
  statement = dfp.FilterStatement()

  # Retreive a small amount of ad unit sizes at a time, paging
  # through until all ad unit sizes have been retrieved.
  response = ad_unit_size_service.getAdUnitSizesByStatement(
      statement.ToStatement())
  if response:
    for ad_unit_size in response:
      # Print out some information for each ad unit size.
      if 'fullDisplayString' in ad_unit_size:
        print('Ad unit size with dimensions "%s" was found.\n' %
              (ad_unit_size['fullDisplayString']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
