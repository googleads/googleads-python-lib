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

import logging
import os
import re
import unittest
from xml.etree import ElementTree


import googleads.adwords
import googleads.dfp
import googleads.util
import mock
import suds.transport


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
    # AdWordsClient setup (compression enabled)
    self.adwords_client_with_compression = googleads.adwords.AdWordsClient(
        dev_token, oauth2_client, user_agent,
        client_customer_id=client_customer_id,
        enable_compression=True)

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

  def testSudsJurkoSendWithCompression(self):
    """Verifies that the patched HttpTransport.send can decode gzip response."""
    test_dir = os.path.dirname(__file__)
    cs = self.adwords_client_with_compression.GetService('CampaignService')

    with mock.patch('suds.transport.http.HttpTransport.u2open'):
      with mock.patch('suds.transport.Reply') as mock_reply:
        with open(os.path.join(
            test_dir, 'test_data/gzip_response.bin'), 'rb') as handler:
          # Use a fake reply containing a gzipped SOAP response.
          reply_instance = mock.Mock()
          reply_instance.code = 200
          reply_instance.headers = {'content-encoding': 'gzip'}
          reply_instance.message = handler.read()
          mock_reply.return_value = reply_instance
        # The send method would ordinarily fail to decompress the gzip SOAP
        # message without the patch, resulting in an exception being raised.
        cs.get()

  def testSingleErrorListIssue90(self):
    """Verifies that issue 90 has been resolved with the patch."""
    query = 'WHERE 1 = 0'
    statement = googleads.dfp.FilterStatement(query)
    line_item_service = self.dfp_client.GetService('LineItemService')
    line_item_action = {'xsi_type': 'ActivateLineItems'}
    st = statement.ToStatement()

    test_dir = os.path.dirname(__file__)

    with mock.patch('suds.transport.http.HttpTransport.send') as mock_send:
      with open(os.path.join(
          test_dir, 'test_data/fault_response_envelope.txt'), 'rb'
               ) as handler:
        # Use a fake reply containing a fault SOAP response.
        reply_instance = mock.Mock()
        reply_instance.code = 500
        reply_instance.headers = {}
        reply_instance.message = handler.read()
        mock_send.return_value = reply_instance
        try:
          line_item_service.performLineItemAction(line_item_action, st)
        except suds.WebFault, e:
          errors = e.fault.detail.ApiExceptionFault.errors
          self.assertIsInstance(errors, list)
          self.assertEqual(1, len(errors))

  def testSingleErrorListIssue90_emptyErrors(self):
    """Verifies that issue 90 has been resolved with the patch."""
    query = 'WHERE 1 = 0'
    statement = googleads.dfp.FilterStatement(query)
    line_item_service = self.dfp_client.GetService('LineItemService')
    line_item_action = {'xsi_type': 'ActivateLineItems'}
    st = statement.ToStatement()

    test_dir = os.path.dirname(__file__)

    with mock.patch('suds.transport.http.HttpTransport.send') as mock_send:
      with open(os.path.join(
          test_dir, 'test_data/empty_fault_response_envelope.txt'), 'rb'
               ) as handler:
        # Use a fake reply containing a fault SOAP response.
        reply_instance = mock.Mock()
        reply_instance.code = 500
        reply_instance.headers = {}
        reply_instance.message = handler.read()
        mock_send.return_value = reply_instance
        try:
          line_item_service.performLineItemAction(line_item_action, st)
        except suds.WebFault, e:
          errors = e.fault.detail.ApiExceptionFault.errors
          self.assertIsInstance(errors, list)
          self.assertEqual(0, len(errors))

  def testSingleErrorListIssue90_multipleErrors(self):
    """Verifies that issue 90 has been resolved with the patch."""
    query = 'WHERE 1 = 0'
    statement = googleads.dfp.FilterStatement(query)
    line_item_service = self.dfp_client.GetService('LineItemService')
    line_item_action = {'xsi_type': 'ActivateLineItems'}
    st = statement.ToStatement()

    test_dir = os.path.dirname(__file__)

    with mock.patch('suds.transport.http.HttpTransport.send') as mock_send:
      with open(os.path.join(
          test_dir, 'test_data/multi_errors_fault_response_envelope.txt'), 'rb'
               ) as handler:
        # Use a fake reply containing a fault SOAP response.
        reply_instance = mock.Mock()
        reply_instance.code = 500
        reply_instance.headers = {}
        reply_instance.message = handler.read()
        mock_send.return_value = reply_instance
        try:
          line_item_service.performLineItemAction(line_item_action, st)
        except suds.WebFault, e:
          errors = e.fault.detail.ApiExceptionFault.errors
          self.assertIsInstance(errors, list)
          self.assertEqual(2, len(errors))


class GoogleAdsCommonFilterTest(unittest.TestCase):
  """Tests for the GoogleAdsCommonFilter utility."""

  def setUp(self):
    self.filter = googleads.util.GetGoogleAdsCommonFilter()
    self.omitted_text = 'OMITTED'
    self.dev_token_template = ('<tns:developerToken>%s</tns:developerToken>')

  def testGetGoogleAdsCommonFilter(self):
    self.assertIs(self.filter, googleads.util.GetGoogleAdsCommonFilter())

  def testFilterAtInfoLevel(self):
    record = mock.Mock()
    record.levelno = logging.INFO
    record.args = [self.dev_token_template % 'test']
    self.filter.filter(record)
    self.assertEqual(
        record.args, (self.dev_token_template % self.omitted_text,))

  def testFilterAtUnfilteredLevel(self):
    expected_args = (1, 2, 3, 4, 5)
    record = mock.Mock()
    record.levelno = logging.DEBUG
    record.args = expected_args
    self.filter.filter(record)
    self.assertEqual(record.args, expected_args)


class SudsClientFilterTest(unittest.TestCase):
  """Tests for the SudsClientFilter utility."""

  def setUp(self):
    self.filter = googleads.util.GetSudsClientFilter()
    self.omitted_text = 'OMITTED'
    self.dev_token_template = 'DevToken'
    self.location = 'https://www.google.com'
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(
        test_dir, 'test_data/request_envelope_template.txt'), 'r') as handler:
      self.test_request_envelope_template = handler.read()

  def testGetSudsClientFilter(self):
    self.assertIs(self.filter, googleads.util.GetSudsClientFilter())

  def testFilterWithSudsClientSOAPMessage(self):
    record = mock.Mock()
    soapenv = mock.Mock()
    soapenv.str.return_value = (self.test_request_envelope_template
                                % self.dev_token_template)
    record.msg = 'sending to (%s)\nmessage:\n%s'
    record.args = [self.location, soapenv]
    self.filter.filter(record)
    self.assertEqual(record.args, (self.location,
                                   (self.test_request_envelope_template
                                    % self.omitted_text)))

  def testFilterWithSudsClientHeadersMessage(self):
    record = mock.Mock()
    record.msg = 'headers = %s'
    record.args = {'Content-Type': 'text/xml; charset=utf-8',
                   'Authorization': 'Bearer abc123doremi'}
    expected_args = {'Content-Type': 'text/xml; charset=utf-8',
                     'Authorization': self.omitted_text}
    self.filter.filter(record)
    self.assertEqual(record.args, expected_args)


class SudsTransportFilterTest(unittest.TestCase):
  """Tests for the SudsTransportFilter utility."""

  def setUp(self):
    self.filter = googleads.util.GetSudsTransportFilter()
    self.omitted_text = 'OMITTED'
    self.dev_token_template = 'DevToken'
    self.location = 'https://www.google.com'
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(
        test_dir, 'test_data/request_envelope_template.txt'), 'r') as handler:
      self.test_request_envelope_template = handler.read()

  def testGetSudsTransportFilter(self):
    self.assertIs(self.filter, googleads.util.GetSudsTransportFilter())

  def testFilterSudsTransportRequest(self):
    request_instance = suds.transport.Request('https://www.google.com')
    request_instance.headers = {'User-Agent': 'user-agent',
                                'Authorization': 'abc123doremi'}
    request_instance.message = (self.test_request_envelope_template %
                                self.dev_token_template)
    expected_headers = {'User-Agent': 'user-agent',
                        'Authorization': self.omitted_text}
    record = mock.Mock()
    record.args = (request_instance,)
    self.filter.filter(record)
    self.assertEqual(record.args[0].headers, expected_headers)
    self.assertEqual(record.args[0].message,
                     self.test_request_envelope_template % self.omitted_text)


if __name__ == '__main__':
  unittest.main()
