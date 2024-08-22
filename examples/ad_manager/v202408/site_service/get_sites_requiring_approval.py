#!/usr/bin/env python
#
# Copyright 2020 Google LLC
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

"""This example gets Sites under MCM requiring review."""

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  site_service = client.GetService('SiteService', version='v202408')

  # Create a statement to select Sites needing approval.
  statement = ad_manager.StatementBuilder(version='v202408').Where(
      "approvalStatus = 'REQUIRES_REVIEW'")

  # Retrieve a small number of sites at a time, paging through until all sites
  # have been retrieved.
  while True:
    response = site_service.getSitesByStatement(statement.ToStatement())
    if 'results' in response and len(response['results']):
      for site in response['results']:
        # Print out some information for each site.
        print('Site with Id %d and URL "%s" was found.' %
              (site['id'], site['url']))
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
