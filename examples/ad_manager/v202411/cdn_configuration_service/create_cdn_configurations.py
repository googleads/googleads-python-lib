#!/usr/bin/env python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""This code example creates new cdn configurations.

To determine which configurations exist, run get_all_cdn_configurations.py.
"""


# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize appropriate service.
  cdn_config_service = client.GetService('CdnConfigurationService',
                                         version='v202411')

  # Create cdn config objects.
  # Only LIVE_STREAM_SOURCE_CONTENT is currently supported by the API.
  configs = [{
      # Basic example with no security policies.
      'name': 'ApiConfig1',
      'cdnConfigurationType': 'LIVE_STREAM_SOURCE_CONTENT',
      'sourceContentConfiguration': {
          'ingestSettings': {
              'urlPrefix': 'ingest1.com',
              'securityPolicy': {
                  'securityPolicyType': 'NONE'
              }
          },
          'defaultDeliverySettings': {
              'urlPrefix': 'delivery1.com',
              'securityPolicy': {
                  'securityPolicyType': 'NONE'
              }
          }
      }
  }, {
      # Complex example with security policies.
      'name': 'ApiConfig2',
      'cdnConfigurationType': 'LIVE_STREAM_SOURCE_CONTENT',
      'sourceContentConfiguration': {
          'ingestSettings': {
              'urlPrefix': 'ingest1.com',
              'securityPolicy': {
                  'securityPolicyType': 'AKAMAI',
                  'disableServerSideUrlSigning': False,
                  'tokenAuthenticationKey': 'abc123',
              }
          },
          'defaultDeliverySettings': {
              'urlPrefix': 'delivery1.com',
              'securityPolicy': {
                  'securityPolicyType': 'AKAMAI',
                  'disableServerSideUrlSigning': True,
                  'originForwardingType': 'CONVENTIONAL',
                  'originPathPrefix': '/path/to/my/origin'
              }
          }
      }
  }]

  # Add configs.
  configs = cdn_config_service.createCdnConfigurations(configs)

  # Display results.
  for config in configs:
    print('Created CDN configuration with type "%s" and name  "%s".'
          % (config['cdnConfigurationType'], config['name']))


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
