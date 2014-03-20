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

"""This example creates a new rule based first party audience segment."""

__author__ = ('Nicholas Chen',
              'Joseph DiLallo')

import uuid

# Import appropriate modules from the client library.
from googleads import dfp

# Set the IDs of the custom criteria to be used in the segment rule.
CUSTOM_TARGETING_KEY_ID = 'INSERT_CUSTOM_TARGETING_KEY_ID_HERE'
CUSTOM_TARGETING_VALUE_ID = 'INSERT_CUSTOM_TARGETING_VALUE_ID_HERE'

def main(client, custom_targeting_key_id, custom_targeting_value_id):
  # Initialize client object.
  client = dfp.DfpClient.LoadFromStorage()

  # Initialize appropriate services.
  audience_segment_service = client.GetService(
      'AudienceSegmentService', version='v201403')
  network_service = client.GetService('NetworkService', version='v201403')

  # Get the root ad unit ID used to target the entire network.
  root_ad_unit_id = (
      network_service.getCurrentNetwork()['effectiveRootAdUnitId'])

  # Create inventory targeting (pointed at root ad unit i.e. the whole network)
  inventory_targeting = {
      'targetedAdUnits': [
          {'adUnitId': root_ad_unit_id}
      ]
  }

  # Create custom criteria.
  custom_criteria = [
      {
          'xsi_type': 'CustomCriteria',
          'keyId': CUSTOM_TARGETING_KEY_ID,
          'valueIds': [CUSTOM_TARGETING_VALUE_ID],
          'operator': 'IS'
      }
  ]

  # Create the custom criteria set.
  top_custom_criteria_set = {
      'logicalOperator': 'AND',
      'children': custom_criteria
  }

  # Create the audience segment rule.
  rule = {
      'inventoryRule': inventory_targeting,
      'customCriteriaRule': top_custom_criteria_set
  }

  # Create an audience segment.
  audience_segment = [
      {
          'xsi_type': 'RuleBasedFirstPartyAudienceSegment',
          'name': ('Sports enthusiasts audience segment %s' %
                   uuid.uuid4()),
          'description': 'Sports enthusiasts between the ages of 20 and 30',
          'pageViews': '6',
          'recencyDays': '6',
          'membershipExpirationDays': '88',
          'rule': rule
      }
  ]

  audience_segments = (
      audience_segment_service.createAudienceSegments(audience_segment))

  for created_audience_segment in audience_segments:
    print ('An audience segment with ID \'%s\', name \'%s\', and type \'%s\' '
           'was created.' % (created_audience_segment['id'],
                             created_audience_segment['name'],
                             created_audience_segment['type']))


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client,  CUSTOM_TARGETING_KEY_ID, CUSTOM_TARGETING_VALUE_ID)
