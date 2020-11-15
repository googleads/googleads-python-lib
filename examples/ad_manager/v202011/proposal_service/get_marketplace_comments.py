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

"""This example gets the Marketplace comments for a programmatic proposal."""

# Import appropriate modules from the client library.
from datetime import datetime

from googleads import ad_manager


PROPOSAL_ID = 'INSERT_PROPOSAL_ID_HERE'


def main(client, proposal_id):
  # Initialize appropriate service.
  marketplace_comment_service = client.GetService(
      'ProposalService', version='v202011')
  query = 'WHERE proposalId = %s' % proposal_id
  # Create a statement to select marketplace comments.
  statement = {'query': query}

  response = marketplace_comment_service.getMarketplaceCommentsByStatement(
      statement)

  # Print out some information for each marketplace comment.
  for marketplace_comment in response['results']:
    date_time = marketplace_comment['creationTime']
    date_time_string = datetime(date_time['date']['year'],
                                date_time['date']['month'],
                                date_time['date']['day'], date_time['hour'],
                                date_time['minute'],
                                date_time['second']).isoformat()
    print('Marketplace comment with creation time "%s"and comment "%s" was '
          'found.\n' % (date_time_string, marketplace_comment['comment']))

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, PROPOSAL_ID)
