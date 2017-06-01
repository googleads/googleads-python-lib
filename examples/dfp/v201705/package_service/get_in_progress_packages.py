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
"""This example gets all packages in progress.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  pkg_service = client.GetService('PackageService', version='v201705')
  query = 'WHERE status = :status'
  values = [
      {'key': 'status',
       'value': {
           'xsi_type': 'TextValue',
           'value': 'IN_PROGRESS'
       }},
  ]
  # Create a statement to select packages.
  statement = dfp.FilterStatement(query, values)

  # Retrieve a small amount of packages at a time, paging
  # through until all packages have been retrieved.
  while True:
    response = pkg_service.getPackagesByStatement(statement.ToStatement())
    if 'results' in response:
      for pkg in response['results']:
        # Print out some information for each package.
        print(
            'Package with ID "%d", name "%s", and proposal ID "%d" was found.\n'
            % (pkg['id'], pkg['name'], pkg['proposalId']))
      statement.offset += dfp.SUGGESTED_PAGE_LIMIT
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
