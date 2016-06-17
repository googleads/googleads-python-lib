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

"""Unit tests to cover the errors module."""

import re
import unittest
from xml.etree import ElementTree



import googleads.adwords
import googleads.dfp
import googleads.util
import mock


class PatchesTest(unittest.TestCase):
  """Tests for the PatchHelper utility."""

  def setUp(self):
    oauth_header = {'Authorization': 'header'}
    oauth2_client = mock.Mock()
    oauth2_client.CreateHttpHeader.return_value = dict(oauth_header)

    # AdWordsClient setup
    client_customer_id = 'client customer id'
    dev_token = '?wH47154M4n'
    user_agent = '4M153rAb13p1l30F53CR37s'
    self.adwords_client = googleads.adwords.AdWordsClient(
        dev_token, oauth2_client, user_agent,
        client_customer_id=client_customer_id)

    # DfpClient setup
    network_code = '12345'
    application_name = 'application name'
    self.dfp_client = googleads.dfp.DfpClient(
        oauth2_client, application_name, network_code)

  def testPatchedSudsJurkoAppender(self):
    """Tests to confirm that the appender no longer removes empty objects."""
    # Create a fake query & statement
    order_id = 1
    values = [{
        'key': 'orderId',
        'value': {
            'xsi_type': 'NumberValue',
            'value': order_id
        }
    }, {
        'key': 'status',
        'value': {
            'xsi_type': 'TextValue',
            'value': 'NEEDS_CREATIVES'
        }
    }]
    query = 'WHERE orderId = :orderId AND status = :status'
    statement = googleads.dfp.FilterStatement(query, values)

    line_item_service = self.dfp_client.GetService('LineItemService')
    line_item_service.suds_client.set_options(nosend=True)
    line_item_action = {'xsi_type': 'ActivateLineItems'}
    # Perform the ActivateLineItems action.
    request = line_item_service.performLineItemAction(
        line_item_action, statement.ToStatement()).envelope
    line_item_service.suds_client.set_options(nosend=False)
    # Strip namespace prefixes and parse.
    parsed_request = ElementTree.fromstring(re.sub('ns[0-1]:', '', request))
    line_item_action = parsed_request.find('Body').find('performLineItemAction')
    # Assert that the request includes the action.
    self.assertTrue(line_item_action is not None)

  def testPatchedSudsJurkoAppenderIssue63(self):
    """Verifies that issue 63 has been resolved with the patch."""
    # Create a fake operation to set a Keyword's finalMobileUrls and finalUrls
    # to a blank value. In the bug, these fields would be excluded from the
    # output.
    operations = [{
        'operator': 'SET',
        'operand': {
            'xsi_type': 'BiddableAdGroupCriterion',
            'adGroupId': 1,
            'criterion': {
                'id': 123456,
                'xsi_type': 'Keyword',
                'type': 'KEYWORD',
                'matchType': 'BROAD',
                'text': 'I AM ERROR',
            },
            # These two fields should appear in the request.
            'finalMobileUrls': {'urls': []},
            'finalUrls': {'urls': []}
        }
    }]
    adgroup_criterion_service = self.adwords_client.GetService(
        'AdGroupCriterionService')
    adgroup_criterion_service.suds_client.set_options(nosend=True)
    request = adgroup_criterion_service.mutate(operations).envelope
    adgroup_criterion_service.suds_client.set_options(nosend=False)
    # Strip namespace prefixes and parse.
    parsed_request = ElementTree.fromstring(re.sub('ns[0-1]:', '', request))
    operand = parsed_request.find('Body').find('mutate').find(
        'operations').find('operand')
    final_mobile_urls = operand.find('finalMobileUrls')
    final_urls = operand.find('finalUrls')
    # Assert that the request includes the empty urls.
    self.assertTrue(final_mobile_urls is not None)
    self.assertTrue(final_urls is not None)

  def testPatchedSudsJurkoAppenderIssue78(self):
    """Verifies that issue 78 has been resolved with the patch."""
    # Create a fake customer that contains only an empty value for the
    # trackingUrl template. In the bug, this would be excluded from the output.
    customer = {'trackingUrlTemplate': '', 'xsi_type': 'Customer'}
    customer_service = self.adwords_client.GetService('CustomerService')
    customer_service.suds_client.set_options(nosend=True)
    request = customer_service.mutate(customer).envelope
    customer_service.suds_client.set_options(nosend=False)
    # Strip namespace prefixes and parse.
    parsed_request = ElementTree.fromstring(re.sub('ns[0-1]:', '', request))
    tracking_url_template = parsed_request.find('Body').find('mutate').find(
        'customer').find('trackingUrlTemplate')
    # Assert that the request includes the empty trackingUrlTemplate.
    self.assertTrue(tracking_url_template is not None)


if __name__ == '__main__':
  unittest.main()
