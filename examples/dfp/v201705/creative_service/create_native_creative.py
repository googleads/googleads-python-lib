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

"""This code example creates a new native creative for a given advertiser.

To determine which companies are advertisers, run get_advertisers.py.

The code in this example will use app data from the Google sample app
'Pie Noon':

https://play.google.com/store/apps/details?id=com.google.fpl.pie_noon&hl=en

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.
"""

import base64
import urllib2
import uuid

# Import appropriate modules from the client library.
from googleads import dfp

# Set id of the advertiser (company) that the creative will be assigned to.
ADVERTISER_ID = 'INSERT_ADVERTISER_ID_HERE'
ICON_URL = ('https://lh4.ggpht.com/GIGNKdGHMEHFDw6TM2bgAUDKPQQRIReKZPqEpMeEhZO'
            'PYnTdOQGaSpGSEZflIFs0iw=h300')
APP_ICON_SMALL = ('https://lh6.ggpht.com/Jzvjne5CLs6fJ1MHF-XeuUfpABzl0YNMlp4Rp'
                  'HnvPRCIj4--eTDwtyouwUDzVVekXw=w300')


def main(client, advertiser_id):
  # Initialize appropriate service.
  creative_service = client.GetService('CreativeService', version='v201705')

  # Use the system defined native app install creative template.
  creative_template_id = '10004400'

  image_data = urllib2.urlopen(ICON_URL).read()
  image_data = base64.b64encode(image_data)

  app_icon_data = urllib2.urlopen(APP_ICON_SMALL).read()
  app_icon_data = base64.b64encode(app_icon_data)

  # Create creative from templates.
  creative = {
      'xsi_type': 'TemplateCreative',
      'name': 'Native Creative #%s' % uuid.uuid4(),
      'advertiserId': advertiser_id,
      'size': {'width': '1', 'height': '1', 'isAspectRatio': False},
      'creativeTemplateId': creative_template_id,
      'destinationUrl': ('https://play.google.com/store/apps/details?id='
                         'com.google.fpl.pie_noon'),
      'creativeTemplateVariableValues': [
          {
              'xsi_type': 'AssetCreativeTemplateVariableValue',
              'uniqueName': 'Image',
              'asset': {
                  'assetByteArray': image_data,
                  'fileName': 'file%s.png' % uuid.uuid4()
              }
          },
          {
              'xsi_type': 'AssetCreativeTemplateVariableValue',
              'uniqueName': 'Appicon',
              'asset': {
                  'assetByteArray': app_icon_data,
                  'fileName': 'appicon%s.png' % uuid.uuid4()
              }
          },
          {
              'xsi_type': 'StringCreativeTemplateVariableValue',
              'uniqueName': 'Price',
              'value': 'Free'
          },
          {
              'xsi_type': 'StringCreativeTemplateVariableValue',
              'uniqueName': 'Calltoaction',
              'value': 'Install'
          },
          {
              'xsi_type': 'StringCreativeTemplateVariableValue',
              'uniqueName': 'Starrating',
              'value': '4'
          },
          {
              'xsi_type': 'StringCreativeTemplateVariableValue',
              'uniqueName': 'Store',
              'value': 'Google Play'
          },
          {
              'xsi_type': 'UrlCreativeTemplateVariableValue',
              'uniqueName': 'DeeplinkclickactionURL',
              'value': 'market://details?id=com.google.fpl.pie_noon'
          },
          {
              'xsi_type': 'StringCreativeTemplateVariableValue',
              'uniqueName': 'Body',
              'value': 'Try multi-screen mode!'
          },
          {
              'xsi_type': 'StringCreativeTemplateVariableValue',
              'uniqueName': 'Headline',
              'value': 'Pie Noon'
          }
      ]
  }

  # Call service to create the creative.
  creative = creative_service.createCreatives([creative])[0]

  # Display results.
  print ('Native creative with id "%s" and name "%s" was '
         'created and can be previewed at %s.'
         % (creative['id'], creative['name'], creative['previewUrl']))

if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, ADVERTISER_ID)
