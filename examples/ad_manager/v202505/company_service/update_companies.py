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

"""This code example updates company comments.

To determine which companies exist, run get_all_companies.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the ID of the company to update.
COMPANY_ID = 'INSERT_COMPANY_ID_HERE'


def main(client, company_id):
  # Initialize appropriate service.
  company_service = client.GetService('CompanyService', version='v202505')

  # Create statement object to only select a single company by ID.
  statement = (ad_manager.StatementBuilder(version='v202505')
               .Where('id = :id')
               .WithBindVariable('id', int(company_id))
               .Limit(1))

  # Get companies by statement.
  response = company_service.getCompaniesByStatement(
      statement.ToStatement())
  if 'results' in response and len(response['results']):
    updated_companies = []
    for company in response['results']:
      company['comment'] += ' Updated.'
      updated_companies.append(company)

    # Update the companies on the server.
    companies = company_service.updateCompanies(updated_companies)

    # Display results.
    for company in companies:
      print(('Company with ID "%s", name "%s", and comment "%s"'
             ' was updated.')
            % (company['id'], company['name'], company['comment']))
  else:
    print('No companies found to update.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, COMPANY_ID)
