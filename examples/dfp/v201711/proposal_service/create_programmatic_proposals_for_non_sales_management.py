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

"""Creates a programmatic proposal for networks not using sales management.
"""

import uuid

# Import appropriate modules from the client library.
from googleads import dfp

PROGRAMMATIC_BUYER_ID = 'INSERT_BUYER_ID_FROM_PQL_TABLE_HERE'
PRIMARY_SALESPERSON_ID = 'INSERT_PRIMARY_SALESPERSON_ID_HERE'
PRIMARY_TRAFFICKER_ID = 'INSERT_PRIMARY_TRAFFICKER_ID_HERE'


def main(client, programmatic_buyer_id, primary_salesperson_id,
         primary_trafficker_id):
  proposal_service = client.GetService('ProposalService', version='v201711')

  proposal = {
      # Setting required Marketplace information.
      'isProgrammatic': 'true',
      'marketplaceInfo': {
          'buyerAccountId': programmatic_buyer_id,
      },
      # Set common required fields for proposals.
      'name': 'Proposal #%s' % uuid.uuid4(),
      'primarySalesperson': {
          'userId': primary_salesperson_id,
          'split': '100000'
      },
      'primaryTraffickerId': primary_trafficker_id,
      'probabilityOfClose': '100000',
  }

  proposals = proposal_service.createProposals([proposal])

  # Display results.
  for proposal in proposals:
    print('Programmatic proposal with id "%s" and name "%s" was created.' %
          (proposal['id'], proposal['name']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PROGRAMMATIC_BUYER_ID, PRIMARY_SALESPERSON_ID,
       PRIMARY_TRAFFICKER_ID)
