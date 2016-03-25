#!/usr/bin/python
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

"""This example gets all LocationCriterion.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


def GetLocationString(location):
  return '%s (%s)' % (location['locationName'], location['displayType']
                      if 'displayType' in location else None)


def main(client):
  # Initialize appropriate service.
  location_criterion_service = client.GetService(
      'LocationCriterionService', version='v201603')

  location_names = ['Paris', 'Quebec', 'Spain', 'Deutchland']

  # Create the selector.
  selector = {
      'fields': ['Id', 'LocationName', 'DisplayType', 'CanonicalName',
                 'ParentLocations', 'Reach', 'TargetingStatus'],
      'predicates': [{
          'field': 'LocationName',
          'operator': 'IN',
          'values': location_names
      }, {
          'field': 'Locale',
          'operator': 'EQUALS',
          'values': ['en']
      }]
  }

  # Make the get request.
  location_criteria = location_criterion_service.get(selector)

  # Display the resulting location criteria.
  for location_criterion in location_criteria:
    parent_string = ''
    if ('parentLocations' in location_criterion['location']
        and location_criterion['location']['parentLocations']):
      parent_string = ', '.join([GetLocationString(parent)for parent in
                                 location_criterion['location']
                                 ['parentLocations']])
    print ('The search term \'%s\' returned the location \'%s\' of type \'%s\''
           ' with parent locations \'%s\', reach \'%s\' and id \'%s\' (%s)'
           % (location_criterion['searchTerm'],
              location_criterion['location']['locationName'],
              location_criterion['location']['displayType'], parent_string,
              location_criterion['reach']
              if 'reach' in location_criterion else None,
              location_criterion['location']['id'],
              location_criterion['location']['targetingStatus']))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
