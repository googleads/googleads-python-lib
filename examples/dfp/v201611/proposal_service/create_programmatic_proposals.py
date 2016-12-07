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

"""This code example creates new programmatic proposals.
"""

import uuid

# Import appropriate modules from the client library.
from googleads import dfp

ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'
PRIMARY_SALESPERSON_ID = 'INSERT_PRIMARY_SALESPERSON_ID_HERE'
PRIMARY_TRAFFICKER_ID = 'INSERT_PRIMARY_TRAFFICKER_ID_HERE'
BUYER_ID = 'INSERT_BUYER_ID_FROM_PQL_TABLE_HERE'


def main(client, advertiser_id, primary_salesperson_id, primary_trafficker_id,
         buyer_id):
  proposal_service = client.GetService('ProposalService', version='v201611')
  network_service = client.GetService('NetworkService', version='v201611')

  proposal = {
      # Setting required Marketplace information.
      'marketplaceInfo': {
          'buyerAccountId': buyer_id
      },
      'isProgrammatic': True,
      # Setting required common fields for Proposals.
      'name': 'Proposal #%s' % uuid.uuid4(),
      'advertiser': {
          'companyId': advertiser_id,
          'type': 'ADVERTISER'
      },
      'primarySalesperson': {
          'userId': primary_salesperson_id,
          'split': '100000'
      },
      'primaryTraffickerId': primary_trafficker_id,
      'probabilityOfClose': '100000',
      'budget': {
          'microAmount': '100000000',
          'currencyCode': network_service.getCurrentNetwork()['currencyCode']
      },
  }
  proposals = proposal_service.createProposals([proposal])

  # Display results.
  for proposal in proposals:
    print('Programmatic proposal with id \'%s\' and name \'%s\' was created.' %
          (proposal['id'], proposal['name']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, ADVERTISER_ID, PRIMARY_SALESPERSON_ID, PRIMARY_TRAFFICKER_ID,
       BUYER_ID)
