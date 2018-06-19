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

"""This code example activates a product template.

To determine which product templates exist, run get_all_product_templates.py.

"""


# Import appropriate modules from the client library.
from googleads import dfp

# Set the id of the product template to activate.
PRODUCT_TEMPLATE_ID = 'INSERT_PRODUCT_TEMPLATE_ID_HERE'


def main(client, product_template_id):
  # Initialize appropriate service.
  product_template_service = client.GetService(
      'ProductTemplateService', version='v201802')

  # Create query.
  statement = (dfp.StatementBuilder()
               .Where('id = :id')
               .WithBindVariable('id', long(product_template_id))
               .Limit(1))

  product_templates_activated = 0

  # Get product_templates by statement.
  while True:
    response = product_template_service.getProductTemplatesByStatement(
        statement.ToStatement())
    if 'results' in response and len(response['results']):
      for product_template in response['results']:
        print ('Product template with id "%s" and name "%s" will be '
               'activated.' % (product_template['id'],
                               product_template['name']))

      # Perform action.
      result = product_template_service.performProductTemplateAction(
          {'xsi_type': 'ActivateProductTemplates'}, statement.ToStatement())
      if result and int(result['numChanges']) > 0:
        product_templates_activated += int(result['numChanges'])
      statement.offset += statement.limit
    else:
      break

  # Display results.
  if product_templates_activated > 0:
    print ('Number of product templates '
           'activated: %s' % product_templates_activated)
  else:
    print 'No product templates were activated.'


if __name__ == '__main__':
  # Initialize client object.
  dfp_client = dfp.DfpClient.LoadFromStorage()
  main(dfp_client, PRODUCT_TEMPLATE_ID)
