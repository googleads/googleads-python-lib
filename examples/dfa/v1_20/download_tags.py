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

"""This example downloads HTML Tags for a given campaign and placement ID.

To create campaigns, run create_campaign.py. To create placements, run
create_placement.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfa


CAMPAIGN_ID = 'INSERT_CAMPAIGN_ID_HERE'
PLACEMENT_ID = 'INSERT_PLACEMENT_ID_HERE'


def main(client, campaign_id, placement_id):
  # Initialize appropriate service.
  placement_service = client.GetService(
      'placement', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set placement tag search criteria.
  placement_tag_criteria = {
      'id': placement_id
  }

  # Get placement tag options.
  tag_options = placement_service.getRegularPlacementTagOptions()
  tag_types = [tag_listing['id'] for tag_listing in tag_options]

  # Add all types of tag options to the search criteria.
  placement_tag_criteria['tagOptionIds'] = tag_types

  # Create a list of placement tag search criterias.
  placement_tag_criterias = [placement_tag_criteria]

  # Get HTML tags for the placements.
  results = placement_service.getPlacementTagData(
      campaign_id, placement_tag_criterias)

  # Display tags for the placement ID used as criteria.
  for result in results:
    for placement_tag_info in result['placementTagInfos']:
      print 'Iframe/JavaScript tag for placement \'%s\' is \n%s\n' % (
          placement_tag_info['placement']['name'],
          placement_tag_info['iframeJavaScriptTag'])
      print 'JavaScript tag for placement \'%s\' is \n%s\n' % (
          placement_tag_info['placement']['name'],
          placement_tag_info['javaScriptTag'])
      print 'Standard tag for placement \'%s\' is \n%s\n' % (
          placement_tag_info['placement']['name'],
          placement_tag_info['standardTag'])
      print 'Internal Redirect tag for placement \'%s\' is \n%s\n' % (
          placement_tag_info['placement']['name'],
          placement_tag_info['internalRedirectTag'])


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, CAMPAIGN_ID, PLACEMENT_ID)
