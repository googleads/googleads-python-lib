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

from contextlib import contextmanager
import logging
import os
import unittest

import googleads.ad_manager
import googleads.adwords
import googleads.errors
import googleads.util
from lxml import etree
import mock
import six
import suds
import suds.transport
from . import testing


_HTTP_CLIENT_PATH = 'httplib' if six.PY2 else 'http.client'


@testing.MultiBackendTest
class PatchesTest(unittest.TestCase):
  """Tests for the PatchHelper utility."""

  def setUp(self, soap_impl):
    self.soap_impl = soap_impl

    oauth_header = {'Authorization': 'header'}
    oauth2_client = mock.Mock()
    oauth2_client.CreateHttpHeader.return_value = dict(oauth_header)

    # AdWordsClient setup
    client_customer_id = 'client customer id'
    dev_token = '?wH47154M4n'
    user_agent = '4M153rAb13p1l30F53CR37s'
    self.adwords_client = googleads.adwords.AdWordsClient(
        dev_token, oauth2_client, user_agent,
        client_customer_id=client_customer_id, soap_impl=soap_impl)
    # AdWordsClient setup (compression enabled)
    self.adwords_client_with_compression = googleads.adwords.AdWordsClient(
        dev_token, oauth2_client, user_agent,
        client_customer_id=client_customer_id,
        enable_compression=True, soap_impl=soap_impl)
    self.adwords_version = sorted(googleads.adwords._SERVICE_MAP.keys())[-1]
    self.adwords_namespace_partial = (
        'https://adwords.google.com/api/adwords/%s/' + self.adwords_version)

    # AdManagerClient setup
    network_code = '12345'
    application_name = 'application name'
    self.ad_manager_client = googleads.ad_manager.AdManagerClient(
        oauth2_client, application_name, network_code, soap_impl=soap_impl)

    self.ad_manager_version = sorted(
        googleads.ad_manager._SERVICE_MAP.keys())[-1]
    self.ad_manager_namespace = (
        'https://www.google.com/apis/ads/publisher/%s'
        % self.ad_manager_version)

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
    statement = googleads.ad_manager.FilterStatement(query, values)

    line_item_service = self.ad_manager_client.GetService('LineItemService')

    line_item_action = {'xsi_type': 'ActivateLineItems'}
    request = line_item_service.GetRequestXML(
        'performLineItemAction', line_item_action, statement.ToStatement())

    line_item_action = request.find(
        './/{%s}lineItemAction' % self.ad_manager_namespace)

    # Assert that the request includes the action.
    self.assertIsNotNone(line_item_action)

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
    request = adgroup_criterion_service.GetRequestXML('mutate', operations)
    final_mobile_urls = request.find('.//{%s}finalMobileUrls' %
                                     self.adwords_namespace_partial % 'cm')
    final_urls = request.find('.//{%s}finalUrls' %
                              self.adwords_namespace_partial % 'cm')
    # Assert that the request includes the empty urls.
    self.assertIsNotNone(final_mobile_urls)
    self.assertIsNotNone(final_urls)

  def testPatchedSudsJurkoAppenderIssue78(self):
    """Verifies that issue 78 has been resolved with the patch."""
    # Create a fake customer that contains only an empty value for the
    # trackingUrl template. In the bug, this would be excluded from the output.
    customer = {'trackingUrlTemplate': '', 'xsi_type': 'Customer'}
    customer_service = self.adwords_client.GetService('CustomerService')
    request = customer_service.GetRequestXML('mutate', customer)
    tracking_url_template = request.find(
        './/{%s}trackingUrlTemplate' % self.adwords_namespace_partial % 'mcm')
    # Assert that the request includes the empty trackingUrlTemplate.
    self.assertIsNotNone(tracking_url_template)

  def testSudsJurkoSendWithCompression(self):
    """Verifies that the patched HttpTransport.send can decode gzip response."""
    # Not applicable to zeep
    if self.soap_impl == 'zeep':
      return

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
    # Not applicable to zeep
    if self.soap_impl == 'zeep':
      return

    test_dir = os.path.dirname(__file__)
    cs = self.adwords_client_with_compression.GetService('CampaignService')

    with mock.patch('suds.transport.http.HttpTransport.u2open') as mock_u2open:
      with mock.patch('%s.HTTPMessage' % _HTTP_CLIENT_PATH) as mock_headers:
        mock_headers.get.return_value = None
        with open(os.path.join(
            test_dir, 'test_data/compact_fault_response_envelope.txt'), 'rb'
                 ) as handler:
          url = 'https://ads.google.com'
          code = 500
          msg = ''
          hdrs = mock_headers
          mock_u2open.side_effect = six.moves.urllib.error.HTTPError(
              url, code, msg, hdrs, handler)
          try:
            cs.get()
          except googleads.errors.GoogleAdsServerFault as e:
            self.assertEqual(
                'Unmarshalling Error: For input string: '
                '"INSERT_ADVERTISER_COMPANY_ID_HERE" ',
                str(e))

  @contextmanager
  def mock_fault_response(self, response_file, version):
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(test_dir, response_file), 'rb') as handler:
      response_data = handler.read()
    if six.PY3:
      response_data = response_data.replace(
          b'{VERSION}', bytes(version, 'utf-8'))
    else:
      response_data = response_data.replace('{VERSION}', version)

    if self.soap_impl == 'suds':
      with mock.patch('suds.transport.http.HttpTransport.send') as mock_send:
        # Use a fake reply containing a fault SOAP response.
        reply_instance = mock.Mock()
        reply_instance.code = 500
        reply_instance.headers = {}
        reply_instance.message = response_data
        mock_send.return_value = reply_instance
        yield
    else:
      with mock.patch('zeep.transports.Transport.post') as mock_post:
        reply_instance = mock.Mock()
        reply_instance.status_code = 500
        reply_instance.headers = {}
        reply_instance.content = response_data
        mock_post.return_value = reply_instance
        yield

  def testSingleErrorListIssue90(self):
    """Verifies that issue 90 has been resolved with the patch."""
    query = 'WHERE 1 = 0'
    statement = googleads.ad_manager.FilterStatement(query)
    line_item_service = self.ad_manager_client.GetService('LineItemService')
    line_item_action = {'xsi_type': 'ActivateLineItems'}
    st = statement.ToStatement()
    with self.mock_fault_response(
        'test_data/fault_response_envelope.txt', self.ad_manager_version):
      try:
        line_item_service.performLineItemAction(line_item_action, st)
      except googleads.errors.GoogleAdsServerFault as e:
        self.assertEqual(1, len(e.errors))

  def testSingleErrorListIssue90_emptyErrors(self):
    """Verifies that issue 90 has been resolved with the patch."""
    query = 'WHERE 1 = 0'
    statement = googleads.ad_manager.FilterStatement(query)
    line_item_service = self.ad_manager_client.GetService('LineItemService')
    line_item_action = {'xsi_type': 'ActivateLineItems'}
    st = statement.ToStatement()

    with self.mock_fault_response(
        'test_data/empty_fault_response_envelope.txt', self.ad_manager_version):
      try:
        line_item_service.performLineItemAction(line_item_action, st)
      except googleads.errors.GoogleAdsServerFault as e:
        self.assertEqual(0, len(e.errors))

  def testSingleErrorListIssue90_multipleErrors(self):
    """Verifies that issue 90 has been resolved with the patch."""
    query = 'WHERE 1 = 0'
    statement = googleads.ad_manager.FilterStatement(query)
    line_item_service = self.ad_manager_client.GetService('LineItemService')
    line_item_action = {'xsi_type': 'ActivateLineItems'}
    st = statement.ToStatement()

    with self.mock_fault_response(
        'test_data/multi_errors_fault_response_envelope.txt',
        self.ad_manager_version):
      try:
        line_item_service.performLineItemAction(line_item_action, st)
      except googleads.errors.GoogleAdsServerFault as e:
        self.assertEqual(2, len(e.errors))


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
                   'authorization': 'Bearer abc123doremi'}
    expected_args = {'Content-Type': 'text/xml; charset=utf-8',
                     'authorization': self.redacted_text}
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
                                'authorization': 'abc123doremi'}
    request_instance.message = (self.test_request_envelope_template %
                                self.dev_token_template).encode('utf-8')
    expected_headers = {'User-Agent': 'user-agent',
                        'authorization': self.redacted_text}
    record = mock.Mock()
    record.args = (request_instance,)
    self.filter.filter(record)
    self.assertEqual(record.args[0].headers, expected_headers)
    self.assertEqual(record.args[0].message,
                     self.test_request_envelope_template % self.redacted_text)

XML_WITH_DEV_TOKEN = (
    '<abc xmlns:ns0="http://abc">'
    '<ns0:developerToken>a token</ns0:developerToken>'
    '<sdf>hi</sdf>'
    '</abc>')
XML_WITH_DEV_TOKEN_SAFE = etree.fromstring(
    XML_WITH_DEV_TOKEN.replace('a token', 'REDACTED'))
XML_WITH_DEV_TOKEN = etree.fromstring(XML_WITH_DEV_TOKEN)
XML_PRETTY = etree.tostring(XML_WITH_DEV_TOKEN, pretty_print=True)
XML_PRETTY_SAFE = etree.tostring(XML_WITH_DEV_TOKEN_SAFE, pretty_print=True)
if six.PY3:
  XML_PRETTY_SAFE = XML_PRETTY_SAFE.decode('utf-8')
XML_WITH_FAULT = etree.fromstring(
    '<abc xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/">'
    '<ns0:Header>'
    '<child><key>value</key></child>'
    '</ns0:Header>'
    '<ns0:Fault>'
    '<faultstring>hi</faultstring>'
    '</ns0:Fault>'
    '</abc>')

ZEEP_HEADER = {'abc': 'hi', 'authorization': 'secret'}
ZEEP_HEADER_SAFE = ZEEP_HEADER.copy()
ZEEP_HEADER_SAFE['authorization'] = 'REDACTED'
BINDING_OPTIONS = {'address': 'myaddress'}


class ZeepLoggerTest(unittest.TestCase):

  def setUp(self):
    self.logger = mock.Mock()
    self.zeep_logger = googleads.util.ZeepLogger()
    self.zeep_logger._logger = self.logger
    self.operation = mock.Mock()
    self.operation.name = 'opname'
    if six.PY2:
      self.operation.binding.wsdl.services.keys.return_value = ['service_name']
    else:
      self.operation.binding.wsdl.services.keys.return_value = (
          iter(['service_name']))

  def enable_log_levels(self, *levels):
    self.logger.isEnabledFor.side_effect = lambda lvl: lvl in levels

  def testIngressPassesThroughArguments(self):
    self.enable_log_levels()

    # This result isn't related to logging, just confirming that the plugin
    # is passing along the data unmodified.
    result = self.zeep_logger.ingress(
        XML_WITH_DEV_TOKEN, ZEEP_HEADER, self.operation)

    self.assertEqual(result, (XML_WITH_DEV_TOKEN, ZEEP_HEADER))

  def testIngressNoLoggingByDefault(self):
    self.enable_log_levels()

    self.zeep_logger.ingress(
        XML_WITH_DEV_TOKEN, ZEEP_HEADER, self.operation)

    self.logger.debug.assert_not_called()

  def testIngressDebugLogging(self):
    self.enable_log_levels(logging.DEBUG)

    # Re-using the XML with <developerToken> for convenience, but this
    # is testing inbound data, which would not have anything sensitive in it.
    self.zeep_logger.ingress(
        XML_WITH_DEV_TOKEN, ZEEP_HEADER, self.operation)

    self.logger.debug.assert_called_once_with(
        googleads.util._RESPONSE_XML_LOG_LINE, XML_PRETTY)

  def testIngressFaultLogging(self):
    self.enable_log_levels(logging.WARN)

    self.zeep_logger.ingress(
        XML_WITH_FAULT, ZEEP_HEADER, self.operation)

    self.assertEqual({'faultMessage': 'hi',
                      'key': 'value',
                      'methodName': 'opname',
                      'serviceName': 'service_name'},
                     self.logger.warn.mock_calls[0][1][1])

  def testEgressPassesThroughArguments(self):
    self.enable_log_levels()

    self.enable_log_levels(logging.DEBUG)

    # This result isn't related to logging, just confirming that the plugin
    # is passing along the data unmodified.
    result = self.zeep_logger.egress(
        XML_WITH_DEV_TOKEN, ZEEP_HEADER, self.operation, BINDING_OPTIONS)

    self.assertEqual(result, (XML_WITH_DEV_TOKEN, ZEEP_HEADER))

  def testEgressNoLoggingByDefault(self):
    self.enable_log_levels()

    self.zeep_logger.egress(
        XML_WITH_DEV_TOKEN, ZEEP_HEADER, self.operation, BINDING_OPTIONS)

    self.logger.debug.assert_not_called()

  def testEgressDebugLogging(self):
    self.enable_log_levels(logging.DEBUG)
    self.zeep_logger.egress(
        XML_WITH_DEV_TOKEN, ZEEP_HEADER, self.operation, BINDING_OPTIONS)

    # With egress, they should be redacted.
    self.logger.debug.assert_called_once_with(
        googleads.util._REQUEST_XML_LOG_LINE, ZEEP_HEADER_SAFE, XML_PRETTY_SAFE)

  def testEgressInfoLogging(self):

    self.enable_log_levels(logging.INFO)
    self.zeep_logger.egress(
        XML_WITH_DEV_TOKEN, ZEEP_HEADER, self.operation, BINDING_OPTIONS)

    self.logger.info.assert_called_once_with(
        googleads.util._REQUEST_LOG_LINE, 'service_name', 'opname', 'myaddress')


if __name__ == '__main__':
  unittest.main()
