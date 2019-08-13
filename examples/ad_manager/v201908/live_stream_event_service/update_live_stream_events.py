#!/usr/bin/env python
#
# Copyright 2018 Google Inc. All Rights Reserved.
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

"""This code example updates live stream events.

To determine which live stream events exist, run get_all_live_stream_events.py.
"""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set ID of the LiveStreamEvent to get live stream events from.
LIVE_STREAM_EVENT_ID = 'INSERT_LIVE_STREAM_EVENT_ID_HERE'


def main(client, live_stream_event_id):
  # Initialize appropriate services.
  live_stream_events_service = client.GetService(
      'LiveStreamEventService', version='v201908')

  # Create statement object to only select matching live stream event.
  statement = (ad_manager.StatementBuilder(version='v201908')
               .Where(('Id = :id'))
               .WithBindVariable('id', int(live_stream_event_id))
               .Limit(500))

  # Get live stream events by statement.
  response = live_stream_events_service.getLiveStreamEventsByStatement(
      statement.ToStatement())

  # Set adTags to be updated.
  new_ad_tags = ['INSERT_NEW_AD_TAGS_HERE']

  if 'results' in response and len(response['results']):
    # Update each local live stream event by changing its attributes.
    updated_live_stream_events = []
    for live_stream_event in response['results']:
      live_stream_event['startDateTimeType'] = 'IMMEDIATELY'
      live_stream_event['adTags'] = new_ad_tags
      updated_live_stream_events.append(live_stream_event)

  # Update live stream events.
  live_stream_events = live_stream_events_service.updateLiveStreamEvents(
      updated_live_stream_events)

  # Display results.
  for live_stream_event in live_stream_events:
    print('Live stream event with id "%s", named "%s" and status %s was '
          'updated.' % (live_stream_event['id'], live_stream_event['name'],
                        live_stream_event['status']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, LIVE_STREAM_EVENT_ID)
