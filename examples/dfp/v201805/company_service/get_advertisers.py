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
"""This example gets all companies that are advertisers.
"""

# Import appropriate modules from the client library.
from googleads import dfp


def main(client):
  # Initialize appropriate service.
  company_service = client.GetService('CompanyService', version='v201805')
  # Create a statement to select companies.
  statement = (dfp.StatementBuilder()
               .Where('type = :type')
               .WithBindVariable('type', 'ADVERTISER'))

  # Retrieve a small amount of companies at a time, paging
  # through until all companies have been retrieved.
  while True:
    response = company_service.getCompaniesByStatement(statement.ToStatement())
    if 'results' in response:
      for company in response['results']:
        # Print out some information for each company.
        print('Company with ID "%d", name "%s", and type "%s" was found.\n' %
              (company['id'], company['name'], company['type']))
      statement.offset += statement.limit
    else:
      break

  print '\nNumber of results found: %s' % response['totalResultSetSize']


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client)
