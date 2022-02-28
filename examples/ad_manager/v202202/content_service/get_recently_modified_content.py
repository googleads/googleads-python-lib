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

"""This example gets recently modified content."""

# Import appropriate modules from the client library.
from datetime import datetime
from datetime import timedelta

from googleads import ad_manager
import pytz


def main(client):
  # Initialize appropriate service.
  content_service = client.GetService('ContentService', version='v202202')

  last_modified = (datetime.now(tz=pytz.timezone('America/New_York'))
                   - timedelta(days=1))

  # Create a statement to get recently modified content based on
  # lastModifiedDateTime. Changes to content bundle associations will update
  # the lastModifiedDateTime, but CMS metadata changes may not change the
  # lastModifiedDateTime.
  statement = (ad_manager.StatementBuilder(version='v202202')
               .Where('lastModifiedDateTime >= :lastModifiedDateTime')
               .WithBindVariable('lastModifiedDateTime', last_modified))

  # Retrieve a small amount of content at a time, paging
  # through until all content have been retrieved.
  while True:
    response = content_service.getContentByStatement(statement.ToStatement())
    if 'results' in response and len(response['results']):
      for content in response['results']:
        # Print out some information for each content.
        content_description = ('Content with ID "%d" and name "%s"' %
                               (content['id'], content['name'].encode('utf-8')))
        if content['contentBundleIds']:
          content_description += (' belonging to bundle IDs %s' %
                                  content['contentBundleIds'])
        content_description += ' was found.'
        print(content_description)
      statement.offset += statement.limit
    else:
      break

  print('\nNumber of results found: %s' % response['totalResultSetSize'])


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
