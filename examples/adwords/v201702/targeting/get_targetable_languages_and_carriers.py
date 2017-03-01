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

"""Retrieves all languages and carriers available for targeting.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""

from googleads import adwords


def main(client):
  # Initialize appropriate service.
  constant_data_service = client.GetService(
      'ConstantDataService', version='v201702')

  # Get all languages.
  languages = constant_data_service.getLanguageCriterion()

  # Display results.
  for language in languages:
    print ('Language with name \'%s\' and ID \'%s\' was found.'
           % (language['name'], language['id']))

  # Get all carriers.
  carriers = constant_data_service.getCarrierCriterion()

  # Display results.
  for carrier in carriers:
    print ('Carrier with name \'%s\', ID \'%s\', and country code \'%s\' was '
           'found.' % (
               carrier['name'], carrier['id'],
               getattr(carrier, 'countryCode', 'N/A')))


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client)
