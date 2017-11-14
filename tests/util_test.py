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
import urllib2
from xml.etree import ElementTree


import googleads.adwords
import googleads.dfp
import googleads.util
import mock
import suds
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

  def testSudsJurkoSendWithException(self):
    """Verifies that the patched HttpTransport.send can escalate HTTPError."""
    test_dir = os.path.dirname(__file__)
    cs = self.adwords_client_with_compression.GetService('CampaignService')

    with mock.patch('suds.transport.http.HttpTransport.u2open') as mock_u2open:
      with mock.patch('httplib.HTTPMessage') as mock_headers:
        mock_headers.get.return_value = None
        with open(os.path.join(
            test_dir, 'test_data/compact_fault_response_envelope.txt'), 'rb'
                 ) as handler:
          url = 'https://ads.google.com'
          code = 500
          msg = ''
          hdrs = mock_headers
          mock_u2open.side_effect = urllib2.HTTPError(url, code, msg, hdrs,
                                                      handler)
          try:
            cs.get()
          except suds.WebFault, e:
            self.assertEqual(
                'Unmarshalling Error: For input string: '
                '"INSERT_ADVERTISER_COMPANY_ID_HERE" ',
                e.fault.faultstring)

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
    self.redacted_text = 'REDACTED'
    self.dev_token_template = ('<tns:developerToken>%s</tns:developerToken>')

  def testGetGoogleAdsCommonFilter(self):
    self.assertIs(self.filter, googleads.util.GetGoogleAdsCommonFilter())

  def testFilterAtInfoLevel(self):
    record = mock.Mock()
    record.levelno = logging.INFO

    doc = mock.Mock()
    doc.str.return_value = self.dev_token_template % 'test'

    record.args = [doc]
    self.filter.filter(record)
    self.assertEqual(
        record.args, (self.dev_token_template % self.redacted_text,))

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
    self.redacted_text = 'REDACTED'
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
                                    % self.redacted_text)))

  def testFilterWithSudsClientHeadersMessage(self):
    record = mock.Mock()
    record.msg = 'headers = %s'
    record.args = {'Content-Type': 'text/xml; charset=utf-8',
                   'Authorization': 'Bearer abc123doremi'}
    expected_args = {'Content-Type': 'text/xml; charset=utf-8',
                     'Authorization': self.redacted_text}
    self.filter.filter(record)
    self.assertEqual(record.args, expected_args)


class SudsMXCoreFilterTest(unittest.TestCase):
  """Tests for the SudsMXCoreFilter utility."""

  _DEVELOPER_TOKEN = 'developerToken'
  _REQUEST_HEADER = 'RequestHeader'

  def setUp(self):
    self.filter = googleads.util.GetSudsMXCoreFilter()
    self.redacted_text = 'REDACTED'
    self.developer_token_value = 'abc123doremi'

  def testGetSudsMXCoreFilter(self):
    self.assertIs(self.filter, googleads.util.GetSudsMXCoreFilter())

  def testFilterWithContentDeveloperToken(self):
    content = suds.mx.Content(tag=self._DEVELOPER_TOKEN,
                              value=self.developer_token_value)

    record = mock.Mock()
    record.args = [content]

    self.filter.filter(record)
    # Verify that the original copy wasn't modified.
    self.assertEqual(content.value, self.developer_token_value)
    # Verify that the args were modified.
    self.assertEqual(record.args[0].value, self.redacted_text)

  def testFilterWithContentRequestHeader(self):
    request_header_value = {
        self._DEVELOPER_TOKEN: self.developer_token_value
    }
    expected_filtered_value = {
        self._DEVELOPER_TOKEN: self.redacted_text
    }
    content = suds.mx.Content(tag=self._REQUEST_HEADER,
                              value=request_header_value)

    record = mock.Mock()
    record.args = [content]

    self.filter.filter(record)
    # Verify that the original copy wasn't modified.
    self.assertEqual(request_header_value[self._DEVELOPER_TOKEN],
                     self.developer_token_value)
    # Verify that the args were modified.
    self.assertEqual(record.args[0].value, expected_filtered_value)

  def testFilterWithElementRequestHeader(self):
    request_header_element = suds.sax.element.Element(
        self._REQUEST_HEADER, parent=None)
    child = suds.sax.element.Element(self._DEVELOPER_TOKEN, parent=None)
    child.text = suds.sax.text.Text(self.developer_token_value)
    request_header_element.append(child)

    record = mock.Mock()
    record.args = [request_header_element]

    self.filter.filter(record)
    # Verify that the original copy wasn't modified.
    self.assertEqual(child.text, suds.sax.text.Text(self.developer_token_value))
    # Verify that the args were modified.
    self.assertEqual(record.args[0].getChild(self._DEVELOPER_TOKEN).text,
                     suds.sax.text.Text(self.redacted_text))

  def testFilterWithNoArgs(self):
    record = mock.Mock()
    record.args = []
    self.filter.filter(record)

  def testFilterWithNoRequestHeader(self):
    foo_value = 'bar'
    lorem_value = 'ipsum'
    potayto_value = 'potahto'
    request_header_value = {
        'foo': foo_value,
        'lorem': lorem_value,
        'potayto': potayto_value
    }
    content = suds.mx.Content(tag=self._REQUEST_HEADER,
                              value=request_header_value)

    record = mock.Mock()
    record.args = [content]

    self.filter.filter(record)
    # Verify that the original copy wasn't modified.
    self.assertEqual(request_header_value['foo'], foo_value)
    self.assertEqual(request_header_value['lorem'], lorem_value)
    self.assertEqual(request_header_value['potayto'], potayto_value)
    # Verify that the args weren't modified.
    self.assertEqual(record.args[0].value, request_header_value)


class SudsMXLiteralFilterTest(unittest.TestCase):
  """Tests for the SudsMXLiteralFilter utility."""

  _DEVELOPER_TOKEN = 'developerToken'
  _REQUEST_HEADER = 'RequestHeader'

  def setUp(self):
    self.filter = googleads.util.GetSudsMXLiteralFilter()
    self.redacted_text = 'REDACTED'
    self.developer_token_value = 'abc123doremi'

  def testGetSudsMXLiteralFilter(self):
    self.assertIs(self.filter, googleads.util.GetSudsMXLiteralFilter())

  def testFilterWithContentDeveloperToken(self):
    content = suds.mx.Content(tag=self._DEVELOPER_TOKEN,
                              value=self.developer_token_value)

    record = mock.Mock()
    record.args = [content]

    self.filter.filter(record)
    # Verify that the original copy wasn't modified.
    self.assertEqual(content.value, self.developer_token_value)
    # Verify that the args were modified.
    self.assertEqual(record.args[0].value, self.redacted_text)

  def testFilterWithContentRequestHeader(self):
    request_header_value = {
        self._DEVELOPER_TOKEN: self.developer_token_value
    }
    expected_filtered_value = {
        self._DEVELOPER_TOKEN: self.redacted_text
    }
    content = suds.mx.Content(tag=self._REQUEST_HEADER,
                              value=request_header_value)

    record = mock.Mock()
    record.args = [content]

    self.filter.filter(record)
    # Verify that the original copy wasn't modified.
    self.assertEqual(request_header_value[self._DEVELOPER_TOKEN],
                     self.developer_token_value)
    # Verify that the args were modified.
    self.assertEqual(record.args[0].value, expected_filtered_value)

  def testFilterWithNoArgs(self):
    record = mock.Mock()
    record.args = []
    self.filter.filter(record)

  def testFilterWithNoRequestHeader(self):
    foo_value = 'bar'
    lorem_value = 'ipsum'
    potayto_value = 'potahto'
    request_header_value = {
        'foo': foo_value,
        'lorem': lorem_value,
        'potayto': potayto_value
    }
    content = suds.mx.Content(tag=self._REQUEST_HEADER,
                              value=request_header_value)

    record = mock.Mock()
    record.args = [content]

    self.filter.filter(record)
    # Verify that the original copy wasn't modified.
    self.assertEqual(request_header_value['foo'], foo_value)
    self.assertEqual(request_header_value['lorem'], lorem_value)
    self.assertEqual(request_header_value['potayto'], potayto_value)
    # Verify that the args weren't modified.
    self.assertEqual(record.args[0].value, request_header_value)


class SudsTransportFilterTest(unittest.TestCase):
  """Tests for the SudsTransportFilter utility."""

  def setUp(self):
    self.filter = googleads.util.GetSudsTransportFilter()
    self.redacted_text = 'REDACTED'
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
                        'Authorization': self.redacted_text}
    record = mock.Mock()
    record.args = (request_instance,)
    self.filter.filter(record)
    self.assertEqual(record.args[0].headers, expected_headers)
    self.assertEqual(record.args[0].message,
                     self.test_request_envelope_template % self.redacted_text)


if __name__ == '__main__':
  unittest.main()
