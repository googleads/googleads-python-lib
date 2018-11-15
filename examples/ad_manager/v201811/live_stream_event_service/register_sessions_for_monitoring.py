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

"""This example registers all live stream event-sessions ids for monitoring."""

# Import appropriate modules from the client library.
from googleads import ad_manager

# List of session ids
SESSION_IDS = ['INSERT_SESSION_IDS_HERE']


def main(client, session_ids):
  # Initialize appropriate service.
  live_stream_event_service = client.GetService(
      'LiveStreamEventService', version='v201811')

  # Retrieve all sessions id that are being monitored
  session_ids = live_stream_event_service.registerSessionsForMonitoring(
      session_ids)
  if session_ids:
    for session_id in session_ids:
      # Print out some information for each live stream event.
      print 'Session with ID "%s" registered for monitoring.' % (session_id)

  print '\nNumber of results found: %s' % session_ids.size


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, SESSION_IDS)
