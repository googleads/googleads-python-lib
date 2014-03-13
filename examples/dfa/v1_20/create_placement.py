#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""This example creates a placement in a given campaign.

Requires the DFA site ID and campaign ID in which the placement will be created
into. To create a campaign, run create_campaign.py. To get DFA site ID, run
get_dfa_site.py. To get a size ID, run get_size.py. To get placement types, run
get_placement_types.py. To get pricing types, run get_pricing_types.py.

Tags: placement.savePlacement
"""

__author__ = 'Joseph DiLallo'

# Import appropriate classes from the client library.
from googleads import dfa


PLACEMENT_NAME = 'INSERT_PLACEMENT_NAME_HERE'
DFA_SITE_ID = 'INSERT_DFA_SITE_ID_HERE'
CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'
PRICING_TYPE = 'INSERT_PRICING_TYPE_HERE'
PLACEMENT_TYPE = 'INSERT_PLACEMENT_TYPE_HERE'
SIZE_ID = 'INSERT_SIZE_ID_HERE'
START_DATE = '%(year)s-%(month)02d-%(day)02dT12:00:00' % {
    'year': 'INSERT_START_YEAR_HERE',
    'month': int('INSERT_START_MONTH_HERE'),
    'day': int('INSERT_START_DAY_HERE')}
END_DATE = '%(year)s-%(month)02d-%(day)02dT12:00:00' % {
    'year': 'INSERT_END_YEAR_HERE',
    'month': int('INSERT_END_MONTH_HERE'),
    'day': int('INSERT_END_DAY_HERE')}


def main(client, placement_name, dfa_site_id, campaign_id, pricing_type,
         placement_type, size_id, start_date, end_date):
  # Initialize appropriate service.
  placement_service = client.GetService(
      'placement', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Construct and save placement.
  placement = {
      'name': placement_name,
      'campaignId': campaign_id,
      'dfaSiteId': dfa_site_id,
      'sizeId': size_id,
      'placementType': placement_type,
      'pricingSchedule': {
          'startDate': start_date,
          'endDate': end_date,
          'pricingType': pricing_type
      }
  }

  # Set placement tag settings.
  tag_options = placement_service.getRegularPlacementTagOptions()
  tag_types = []
  for tag_listing in tag_options:
    tag_types.append(tag_listing['id'])

  placement['tagSettings'] = {'tagTypes': tag_types}

  result = placement_service.savePlacement(placement)

  # Display results.
  print 'Placement with ID \'%s\' was created.' % result['id']


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, PLACEMENT_NAME, DFA_SITE_ID, CAMPAIGN_ID, PRICING_TYPE,
       PLACEMENT_TYPE, SIZE_ID, START_DATE, END_DATE)
