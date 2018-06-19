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

"""This code example updates contact addresses.

To determine which contacts exist, run get_all_contacts.py.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""


# Import appropriate modules from the client library.
from googleads import dfp

# Set the ID of the contact to update.
CONTACT_ID = 'INSERT_CONTACT_ID_HERE'


def main(client, contact_id):
  # Initialize appropriate service.
  contact_service = client.GetService('ContactService', version='v201805')

  # Create statement object to select the single contact by ID.
  statement = (dfp.StatementBuilder()
               .Where('id = :id')
               .WithBindVariable('id', long(contact_id))
               .Limit(1))

  # Get contacts by statement.
  response = contact_service.getContactsByStatement(
      statement.ToStatement())

  if 'results' in response and len(response['results']):
    updated_contacts = []
    for contact in response['results']:
      contact['address'] = '123 New Street, New York, NY, 10011'
      updated_contacts.append(contact)

    # Update the contact on the server.
    contacts = contact_service.updateContacts(updated_contacts)

    # Display results.
    for contact in contacts:
      print (('Contact with ID "%s", name "%s", and address "%s" '
              'was updated.')
             % (contact['id'], contact['name'], contact['address']))
  else:
    print 'No contacts found to update.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, CONTACT_ID)
