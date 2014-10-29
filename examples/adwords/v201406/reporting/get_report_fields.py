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

"""This example gets report fields.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

Tags: ReportDefinitionService.getReportFields
"""

__author__ = ('api.kwinter@gmail.com (Kevin Winter)'
              'Joseph DiLallo')

from googleads import adwords


REPORT_TYPE = 'INSERT_REPORT_TYPE_HERE'


def main(client, report_type):
  # Initialize appropriate service.
  report_definition_service = client.GetService(
      'ReportDefinitionService', version='v201406')

  # Get report fields.
  fields = report_definition_service.getReportFields(report_type)

  # Display results.
  print 'Report type \'%s\' contains the following fields:' % report_type
  for field in fields:
    print ' - %s (%s)' % (field['fieldName'], field['fieldType'])
    if 'enumValues' in field:
      print '  := [%s]' % ', '.join(field['enumValues'])


if __name__ == '__main__':
  # Initialize client object.
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  main(adwords_client, REPORT_TYPE)
