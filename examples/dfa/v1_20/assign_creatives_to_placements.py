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

"""Assigns creatives to placements and creates a unique ad for each assignment.

To get creatives, run get_creatives.py example. To get placements,
run get_placement.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: creative.assignCreativesToPlacements
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


CREATIVE_IDS = ['INSERT_FIRST_CREATIVE_ID', 'INSERT_SECOND_CREATIVE_ID']
PLACEMENT_IDS = ['INSERT_FIRST_PLACEMENT_ID', 'INSERT_SECOND_PLACEMENT_ID']


def main(client, creative_ids, placement_ids):
  # Initialize appropriate service.
  creative_service = client.GetService(
      'creative', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Create creative placement assignment structure.
  creative_placement_assignments = []
  for index in range(len(creative_ids)):
    creative_placement_assignments.append({
        'xsi_type': 'CreativePlacementAssignment',
        'creativeId': creative_ids[index],
        'placementId': placement_ids[index],
        'placementIds': placement_ids
    })

  # Submit the request.
  results = creative_service.assignCreativesToPlacements(
      creative_placement_assignments)

  # Display results.
  if results:
    for assignment_result in results:
      if assignment_result['errorMessage'] is None:
        print ('Ad with name \'%s\' and ID \'%s\' was created.' %
               (assignment_result['adName'], assignment_result['adId']))
      else:
        print ('Assignment unsuccessful for creative ID \'%s\' and placementID'
               ' \'%s\'. Error message says \'%s\'.'
               % (assignment_result['creativeId'],
                  assignment_result['placementId'],
                  assignment_result['errorMessage']))
  else:
    print 'No ads were created.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client, CREATIVE_IDS, PLACEMENT_IDS)
