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

"""This example adds a remarketing user list (a.k.a. audience).

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid
from googleads import adwords


PAGE_SIZE = 100


def main(client):
  # Initialize appropriate service.
  user_list_service = client.GetService(
      'AdwordsUserListService', version='v201809')
  conversion_tracker_service = client.GetService(
      'ConversionTrackerService', version='v201809')

  # Construct operations and add a user list.
  operations = [
      {
          'operator': 'ADD',
          'operand': {
              'xsi_type': 'BasicUserList',
              'name': 'Mars cruise customers #%s' % uuid.uuid4(),
              'description': 'A list of mars cruise customers in the last year',
              'membershipLifeSpan': '365',
              'conversionTypes': [
                  {
                      'name': ('Mars cruise customers #%s'
                               % uuid.uuid4())
                  }
              ],
              # Optional field.
              'status': 'OPEN',
          }
      }
  ]
  user_list_result = user_list_service.mutate(operations)

  # Capture the ID(s) of the conversion.
  if 'value' in user_list_result:
    conversion_ids = []
    for user_list in user_list_result['value']:
      if user_list['conversionTypes']:
        for conversion_type in user_list['conversionTypes']:
          conversion_ids.append(conversion_type['id'])

    # Create query.
    query = (adwords.ServiceQueryBuilder()
             .Select('Id', 'GoogleGlobalSiteTag', 'GoogleEventSnippet')
             .Where('Id').In(*conversion_ids)
             .Limit(0, PAGE_SIZE)
             .Build())

    conversions_map = {}

    # Get all conversion trackers.
    for page in query.Pager(conversion_tracker_service):
      if 'entries' in page:
        for conversion_tracker in page['entries']:
          conversions_map[conversion_tracker['id']] = conversion_tracker

    for user_list in user_list_result['value']:
      print ('User list with name "%s" and ID "%s" was added.'
             % (user_list['name'], user_list['id']))
      if user_list['conversionTypes']:
        for conversion_type in user_list['conversionTypes']:
          conversion_tracker = conversions_map[conversion_type['id']]
          print ('Google global site tag:\n%s\n\n'
                 % conversion_tracker['googleGlobalSiteTag'])
          print ('Google event snippet:\n%s\n\n'
                 % conversion_tracker['googleEventSnippet'])
  else:
    print 'No user lists were added.'


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
