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

"""This code example creates new live stream events.

To determine which live stream events exist, run get_all_live_stream_events.py.
To determine which cdn configurations exist, run get_cdn_configurations.py.
"""

import datetime
import uuid

# Import appropriate modules from the client library.
from googleads import ad_manager
import pytz

# Set content urls and adTags to use
CONTENT_URLS = ['INSERT_CONTENT_URLS_HERE']
AD_TAGS = ['INSERT_AD_TAGS_HERE']


def main(client, content_urls, ad_tags):
  # Initialize appropriate services.
  live_events_service = client.GetService(
      'LiveStreamEventService', version='v202102')

  # Stream will play for 365 days
  start_datetime = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
  end_datetime = start_datetime + datetime.timedelta(days=365)

  # Create live stream event objects
  live_stream_events = [{
      'name': 'Live Stream Event #%s' % uuid.uuid4(),
      'startDateTime': start_datetime,
      'endDateTime': end_datetime,
      'contentUrls': content_urls,
      'adTags': ad_tags
  }]

  # Add live stream events.
  live_stream_events = live_events_service.createLiveStreamEvents(
      live_stream_events)

  # Display results.
  for live_stream_event in live_stream_events:
    print(
        'Live stream event with id "%s", named "%s" and status %s was created.'
        % (live_stream_event['id'], live_stream_event['name'],
           live_stream_event['status']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client, CONTENT_URLS, AD_TAGS)
