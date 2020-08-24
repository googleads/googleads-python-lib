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

"""This code example creates new companies.

To determine which companies exist, run get_all_companies.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  company_service = client.GetService('CompanyService', version='v202008')

  # Create company objects.
  companies = [
      {
          'name': 'Advertiser #%s' % uuid.uuid4(),
          'type': 'ADVERTISER'
      },
      {
          'name': 'Agency #%s' % uuid.uuid4(),
          'type': 'AGENCY'
      }
  ]

  # Add companies.
  companies = company_service.createCompanies(companies)

  # Display results.
  for company in companies:
    print('Company with ID "%s", name "%s", and type "%s" was created.'
          % (company['id'], company['name'], company['type']))

if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
