#!/usr/bin/python
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

"""This code example creates new proposals.

To determine which proposals exist, run get_all_proposals.py."""


import uuid

# Import appropriate modules from the client library.
from googleads import dfp

ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'
PRIMARY_SALESPERSON_ID = 'INSERT_PRIMARY_SALESPERSON_ID_HERE'
SECONDARY_SALESPERSON_ID = 'INSERT_SECONDARY_SALESPERSON_ID_HERE'
PRIMARY_TRAFFICKER_ID = 'INSERT_PRIMARY_TRAFFICKER_ID_HERE'


def main(client, advertiser_id, primary_salesperson_id,
         secondary_salesperson_id, primary_trafficker_id):
  # Initialize appropriate services.
  proposal_service = client.GetService('ProposalService', version='v201608')
  network_service = client.GetService('NetworkService', version='v201608')

  # Create proposal objects.
  proposal = {
      'name': 'Proposal #%s' % uuid.uuid4(),
      'advertiser': {
          'companyId': advertiser_id,
          'type': 'ADVERTISER'
      },
      'primarySalesperson': {
          'userId': primary_salesperson_id,
          'split': '75000'
      },
      'secondarySalespeople': [{
          'userId': secondary_salesperson_id,
          'split': '25000'
      }],
      'primaryTraffickerId': primary_trafficker_id,
      'probabilityOfClose': '100000',
      'budget': {
          'microAmount': '100000000',
          'currencyCode': network_service.getCurrentNetwork()['currencyCode']
      },
      'billingCap': 'CAPPED_CUMULATIVE',
      'billingSource': 'DFP_VOLUME'
  }

  # Add proposals.
  proposals = proposal_service.createProposals([proposal])

  # Display results.
  for proposal in proposals:
    print ('Proposal with id \'%s\' and name \'%s\' was created.'
           % (proposal['id'], proposal['name']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, ADVERTISER_ID, PRIMARY_SALESPERSON_ID,
       SECONDARY_SALESPERSON_ID, PRIMARY_TRAFFICKER_ID)
