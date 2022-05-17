#!/usr/bin/env python
#
# Copyright 2020, Google LLC
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

"""This example gets the network's default third party data declarations."""


# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate services.
  network_service = client.GetService('NetworkService', version='v202205')
  pql_service = client.GetService('PublisherQueryLanguageService',
                                  version='v202205')

  # Fetch the default third party data declarations.
  declarations = network_service.getDefaultThirdPartyDataDeclaration()

  # Display the results.
  if declarations is None:
    print('No default ad technology partners have been set on this network.')
  elif (declarations['declarationType'] == 'NONE' or
        not declarations['thirdPartyCompanyIds']):
    print('This network has specified that there are no ad technology providers'
          ' associated with its reservation creatives by default.')
  else:
    print('This network has specified %d ad technology provider(s) associated'
          ' with its reservation creatives by default:' %
          len(declarations['thirdPartyCompanyIds']))

    # In this case, there are third party companies to be displayed, so fetch
    # the company names from the Rich_Media_Ad_Company PQL table.
    statement = (ad_manager.StatementBuilder(version='v202205')
                 .Select('Id, Name')
                 .From('Rich_Media_Ad_Company')
                 .Where('Id IN (:company_ids)')
                 .WithBindVariable('company_ids',
                                   declarations['thirdPartyCompanyIds']))

    while True:
      response = pql_service.select(statement.ToStatement())
      if 'rows' in response and len(response['rows']):
        for company in response['rows']:
          print('Name: %s, id: %s' % (company['values'][1]['value'],
                                      company['values'][0]['value']))
        statement.offset += statement.limit
      else:
        break


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
