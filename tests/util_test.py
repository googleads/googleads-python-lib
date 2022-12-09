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
import googleads.errors
import googleads.util
from lxml import etree
import mock


class PatchesTest(unittest.TestCase):
  """Tests for the PatchHelper utility."""

  def setUp(self):
    oauth_header = {'Authorization': 'header'}
    oauth2_client = mock.Mock()
    oauth2_client.CreateHttpHeader.return_value = dict(oauth_header)

    # AdManagerClient setup
    network_code = '12345'
    application_name = 'application name'
    self.ad_manager_client = googleads.ad_manager.AdManagerClient(
        oauth2_client, application_name, network_code)

    self.ad_manager_version = sorted(
        googleads.ad_manager._SERVICE_MAP.keys())[-1]
    self.ad_manager_namespace = (
        'https://www.google.com/apis/ads/publisher/%s'
        % self.ad_manager_version)

  @contextmanager
  def mock_fault_response(self, response_file, version):
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(test_dir, response_file), 'rb') as handler:
      response_data = handler.read()
    response_data = response_data.replace(b'{VERSION}', bytes(version, 'utf-8'))

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
    self.operation.binding.wsdl.services.keys.return_value = ['service_name']

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
