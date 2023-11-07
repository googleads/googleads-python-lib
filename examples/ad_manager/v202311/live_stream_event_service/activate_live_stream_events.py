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

"""This code example activates paused live stream events."""

# Import appropriate modules from the client library.
from googleads import ad_manager

# Set the id of the LiveStreamEvent to get live stream events from.
LIVE_STREAM_EVENT_ID = 'INSERT_LIVE_STREAM_EVENT_ID_HERE'


def main(client, live_stream_event_id):
  # Initialize appropriate service.
  live_stream_event_service = client.GetService(
      'LiveStreamEventService', version='v202311')

  # Create query to find paused live stream events.
  statement = (ad_manager.StatementBuilder(version='v202311')
               .Where(('id = :id AND '
                       'status = :status'))
               .WithBindVariable('status', 'PAUSED')
               .WithBindVariable('id', int(live_stream_event_id))
               .Limit(500))

  live_stream_events_activated = 0

  # Get live stream events by statement.
  while True:
    response = live_stream_event_service.getLiveStreamEventsByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for live_stream_event in response['results']:
        print('live stream event with id "%s" and name "%s" will be activated.'
              % (live_stream_event['id'], live_stream_event['name']))

      # Perform action.
      result = live_stream_event_service.performLiveStreamEventAction({
          'xsi_type': 'ActivateLiveStreamEvents'
      }, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        live_stream_events_activated += int(result['numChanges'])
      statement.offset += ad_manager.SUGGESTED_PAGE_LIMIT
    else:
      break

  # Display results.
  if live_stream_events_activated > 0:
    print('# of live stream events activated: %s' % (
        live_stream_events_activated))
  else:
    print('No live stream events were activated.')


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, LIVE_STREAM_EVENT_ID)
