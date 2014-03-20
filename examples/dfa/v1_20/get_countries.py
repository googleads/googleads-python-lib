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

"""Displays all countries matching a search criteria.

Tags: spotlight.getCountriesByCriteria
"""

__author__ = 'Joseph DiLallo'

# Import appropriate modules from the client library.
from googleads import dfa


def main(client):
  # Initialize appropriate service.
  spotlight_service = client.GetService(
      'spotlight', 'v1.20', 'https://advertisersapitest.doubleclick.net')

  # Set search criteria.
  country_search_criteria = {
      'secure': 'false'
  }

  # Get countries.
  results = spotlight_service.getCountriesByCriteria(
      country_search_criteria)

  # Display country names, codes and secure server support information.
  if results:
    for country in results:
      print ('Country with name \'%s\', country code \'%s\', and supports a'
             ' secure server? \'%s\'.'
             % (country['name'], country['countryCode'], country['secure']))
  else:
    print 'No countries found for your criteria.'


if __name__ == '__main__':
  # Initialize client object.
  dfa_client = dfa.DfaClient.LoadFromStorage()
  main(dfa_client)
