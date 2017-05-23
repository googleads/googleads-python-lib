#!/usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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

"""This code example creates new contacts.

To determine which contacts exist, run get_all_contacts.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


import uuid

# Import appropriate modules from the client library.
from googleads import dfp

# Set the ID of the advertiser company this contact is associated with.
ADVERTISER_COMPANY_ID = 'INSERT_ADVERTISER_COMPANY_ID_HERE'

# Set the ID of the agency company this contact is associated with.
AGENCY_COMPANY_ID = 'INSERT_AGENCY_COMPANY_ID_HERE'


def main(client, advertiser_company_id, agency_company_id):
  # Initialize appropriate service.
  contact_service = client.GetService('ContactService', version='v201611')

  # Create an advertiser contact.
  advertiser_contact = {
      'name': 'Mr. Advertiser #%s' % uuid.uuid4(),
      'email': 'advertiser@advertising.com',
      'companyId': advertiser_company_id
  }

  # Create an agency contact.
  agency_contact = {
      'name': 'Ms. Agency #%s' % uuid.uuid4(),
      'email': 'agency@agencies.com',
      'companyId': agency_company_id
  }

  # Create the contacts on the server.
  contacts = contact_service.createContacts([advertiser_contact,
                                             agency_contact])

  # Display results.
  for contact in contacts:
    print ('Contact with ID \'%s\' name \'%s\' was created.'
           % (contact['id'], contact['name']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, ADVERTISER_COMPANY_ID, AGENCY_COMPANY_ID)
