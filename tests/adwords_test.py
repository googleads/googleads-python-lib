# -*- coding: UTF-8 -*-
#
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Unit tests to cover the adwords module."""

import datetime
import io
import os
import re
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree import ElementTree

import googleads.adwords
import googleads.common
import googleads.errors
from . import testing
import lxml.etree
import mock
import yaml
import zeep.transports

CURRENT_VERSION = sorted(googleads.adwords._SERVICE_MAP.keys())[-1]
TEST_DIR = os.path.dirname(__file__)


def GetAdWordsClient(**kwargs):
  """Returns an initialized AdwordsClient for use in testing.

  If not specified, the keyword arguments will be set to default test values.

  Keyword Arguments:
    ccid: A str value for the AdWordsClient's client_customer_id.
    dev_token: A str value for the AdWordsClient's developer_token.
    oauth2_client: A GoogleOAuth2Client instance or mock implementing its
      interface.
    proxy_config: A googleads.common.ProxyConfig instance. If not specified,
      this will default to None to specify that no Proxy is being used.
    report_downloader_headers: A dict containing optional report downloader
      headers.
    user_agent: A str value for the AdWordsClient's user_agent.
    timeout: An integer timeout in MS for connections.

  Returns:
    An AdWordsClient instance intended for testing.
  """
  client_customer_id = kwargs.get('ccid', 'client customer id')
  dev_token = kwargs.get('dev_token', 'dev_token')
  user_agent = kwargs.get('user_agent', 'user_agent')
  validate_only = kwargs.get('validate_only', False)
  partial_failure = kwargs.get('partial_failure', False)
  report_downloader_headers = kwargs.get('report_downloader_headers', {})
  timeout = kwargs.get('timeout', 3600)

  if 'oauth2_client' in kwargs:
    oauth2_client = kwargs['oauth2_client']
  else:
    oauth_header = {'Authorization': 'header'}
    oauth2_client = mock.Mock()
    oauth2_client.CreateHttpHeader.return_value = dict(oauth_header)

  client = googleads.adwords.AdWordsClient(
      dev_token, oauth2_client, user_agent,
      client_customer_id=client_customer_id,
      cache=kwargs.get('cache'),
      proxy_config=kwargs.get('proxy_config'),
      validate_only=validate_only, partial_failure=partial_failure,
      report_downloader_headers=report_downloader_headers, timeout=timeout)

  return client


def GetProxyConfig(http_proxy_uri=None, https_proxy_uri=None, cafile=None,
                   disable_certificate_validation=None):
  """Returns an initialized ProxyConfig for use in testing.

  Args:
    http_proxy_uri: A str containing the full URI for the http proxy host. If
      this is not specified, the ProxyConfig will be initialized without an
      HTTP proxy configured.
    https_proxy_uri: A str containing the full URI for the https proxy host. If
      this is not specified, the ProxyConfig will be initialized without an
      HTTPS proxy configured.
    cafile: A str containing the path to a custom ca file.
    disable_certificate_validation: A boolean indicating whether or not to
      disable certificate validation.

  Returns:
    An initialized ProxyConfig using the given configurations.
  """
  return googleads.common.ProxyConfig(
      http_proxy_uri, https_proxy_uri, cafile=cafile,
      disable_certificate_validation=disable_certificate_validation)


class AdWordsHeaderHandlerTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.adwords._AdWordsHeaderHandler class."""

  def setUp(self):
    self.report_downloader_headers = {}
    self.oauth2_client = mock.Mock()
    self.oauth_header = {'Authorization': 'header'}
    self.oauth2_client.CreateHttpHeader.return_value = self.oauth_header
    self.ccid = 'client customer id'
    self.dev_token = 'developer token'
    self.user_agent = 'user agent!'
    self.validate_only = True
    self.partial_failure = False
    self.enable_compression = False
    self.utility_name = 'TestUtility'
    self.default_sig_template = ' (%s, %s, %s)'
    self.util_sig_template = ' (%s, %s, %s, %s)'
    self.aw_client = GetAdWordsClient(
        ccid=self.ccid, dev_token=self.dev_token,
        user_agent=self.user_agent, oauth2_client=self.oauth2_client,
        validate_only=self.validate_only, partial_failure=self.partial_failure,
        report_downloader_headers=self.report_downloader_headers)
    self.header_handler = googleads.adwords._AdWordsHeaderHandler(
        self.aw_client, CURRENT_VERSION, self.enable_compression, None)

    @googleads.common.RegisterUtility(self.utility_name)
    class TestUtility(object):

      def Test(self):
        pass

    self.test_utility = TestUtility()

  def testGetHTTPHeaders(self):
    header_result = self.header_handler.GetHTTPHeaders()
    # Check that the returned headers have the correct values.
    self.assertEqual(header_result, self.oauth_header)

  def testGetHTTPHeadersWithCustomHeaders(self):
    self.header_handler.custom_http_headers = {'X-My-Header': 'abc'}

    header_result = self.header_handler.GetHTTPHeaders()

    self.assertEqual(
        header_result, {'Authorization': 'header', 'X-My-Header': 'abc'})

  def testGetSOAPHeaders(self):
    create_method = mock.Mock()
    soap_header = self.header_handler.GetSOAPHeaders(create_method)
    # Check that the SOAP header has the correct values.
    create_method.assert_called_once_with(
        '{https://adwords.google.com/api/adwords/cm/%s}SoapHeader' %
        CURRENT_VERSION)
    self.assertEqual(self.ccid, soap_header.clientCustomerId)
    self.assertEqual(self.dev_token, soap_header.developerToken)
    self.assertEqual(
        ''.join([self.user_agent,
                 googleads.common.GenerateLibSig(
                     googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG)]),
        soap_header.userAgent)
    self.assertEqual(self.validate_only, soap_header.validateOnly)
    self.assertEqual(self.partial_failure, soap_header.partialFailure)

  def testGetHeadersUserAgentWithUtility(self):
    create_method = mock.Mock()

    with mock.patch('googleads.common._COMMON_LIB_SIG') as mock_common_sig:
      with mock.patch('googleads.common._PYTHON_VERSION') as mock_py_ver:
        self.test_utility.Test()  # This will register TestUtility.
        soap_header = self.header_handler.GetSOAPHeaders(create_method)

        self.assertEqual(
            ''.join([self.user_agent,
                     self.util_sig_template % (
                         googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG,
                         mock_common_sig,
                         mock_py_ver,
                         self.utility_name)
                    ]),
            soap_header.userAgent)

  def testGetHeadersUserAgentWithAndWithoutUtility(self):
    create_method = mock.Mock()

    with mock.patch('googleads.common._COMMON_LIB_SIG') as mock_common_sig:
      with mock.patch('googleads.common._PYTHON_VERSION') as mock_py_ver:
        # Check headers when utility registered.
        self.test_utility.Test()  # This will register TestUtility.
        soap_header = self.header_handler.GetSOAPHeaders(create_method)

        self.assertEqual(
            ''.join([self.user_agent,
                     self.util_sig_template % (
                         googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG,
                         mock_common_sig,
                         mock_py_ver,
                         self.utility_name)
                    ]),
            soap_header.userAgent)

        # Check headers when no utility should be registered.
        soap_header = self.header_handler.GetSOAPHeaders(create_method)
        self.assertEqual(
            ''.join([self.user_agent,
                     self.default_sig_template % (
                         googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG,
                         mock_common_sig,
                         mock_py_ver)
                    ]),
            soap_header.userAgent)

        # Verify that utility is registered in subsequent uses.
        self.test_utility.Test()  # This will register TestUtility.
        soap_header = self.header_handler.GetSOAPHeaders(create_method)

        self.assertEqual(
            ''.join([self.user_agent,
                     self.util_sig_template % (
                         googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG,
                         mock_common_sig,
                         mock_py_ver,
                         self.utility_name)
                    ]),
            soap_header.userAgent)

  def testGetReportDownloadHeadersOverrideDefaults(self):
    self.aw_client.report_downloader_headers = {
        'skip_report_header': True, 'skip_column_header': False,
        'skip_report_summary': False, 'use_raw_enum_values': True}
    expected_return_value = {
        'Content-type': 'application/x-www-form-urlencoded',
        'developerToken': self.dev_token,
        'clientCustomerId': self.ccid,
        'Authorization': 'header',
        'User-Agent': ''.join([
            self.user_agent,
            googleads.common.GenerateLibSig(
                googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG),
            ',gzip']),
        'skipReportHeader': 'False',
        'skipColumnHeader': 'True',
        'skipReportSummary': 'False',
        'useRawEnumValues': 'True'
    }
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders(
                         skip_report_header=False,
                         skip_column_header=True,
                         skip_report_summary=False,
                         use_raw_enum_values=True))

  def testGetReportDownloadHeadersWithDefaultsFromConfig(self):
    self.aw_client.report_download_headers = {
        'skip_report_header': True, 'skip_column_header': False,
        'skip_report_summary': False, 'use_raw_enum_values': True}
    expected_return_value = {
        'Content-type': 'application/x-www-form-urlencoded',
        'developerToken': self.dev_token,
        'clientCustomerId': self.ccid,
        'Authorization': 'header',
        'User-Agent': ''.join([
            self.user_agent,
            googleads.common.GenerateLibSig(
                googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG),
            ',gzip']),
        'skipReportHeader': 'True',
        'skipColumnHeader': 'False',
        'skipReportSummary': 'False',
        'useRawEnumValues': 'True'
    }
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders())

  def testGetReportDownloadHeadersWithInvalidKeyword(self):
    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        self.header_handler.GetReportDownloadHeaders, invalid_key_word=True)

  def testGetReportDownloadHeadersWithKeywordArguments(self):
    updated_ccid = 'updated client customer id'
    expected_return_value = {
        'Content-type': 'application/x-www-form-urlencoded',
        'developerToken': self.dev_token,
        'clientCustomerId': updated_ccid,
        'Authorization': 'header',
        'User-Agent': ''.join([
            self.user_agent,
            googleads.common.GenerateLibSig(
                googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG),
            ',gzip']),
        'skipReportHeader': 'True',
        'skipColumnHeader': 'True',
        'skipReportSummary': 'True',
        'includeZeroImpressions': 'True',
        'useRawEnumValues': 'True'
    }
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders(
                         skip_report_header=True,
                         skip_column_header=True,
                         skip_report_summary=True,
                         include_zero_impressions=True,
                         use_raw_enum_values=True,
                         client_customer_id=updated_ccid))

  def testGetReportDownloadHeadersWithNoOptionalHeaders(self):
    expected_return_value = {
        'Content-type': 'application/x-www-form-urlencoded',
        'developerToken': self.dev_token,
        'clientCustomerId': self.ccid,
        'Authorization': 'header',
        'User-Agent': ''.join([
            self.user_agent,
            googleads.common.GenerateLibSig(
                googleads.adwords._AdWordsHeaderHandler._PRODUCT_SIG),
            ',gzip'])
    }
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders())


class AdWordsClientTest(unittest.TestCase):
  """Tests for the googleads.adwords.AdWordsClient class."""

  def setUp(self):
    self.load_from_storage_path = os.path.join(
        os.path.dirname(__file__), 'test_data/adwords_googleads.yaml')
    self.https_proxy_uri = 'http://myproxy:443'
    self.proxy_config = GetProxyConfig(https_proxy_uri=self.https_proxy_uri)
    self.adwords_client = GetAdWordsClient()
    self.aw_client = GetAdWordsClient(proxy_config=self.proxy_config)
    self.header_handler = googleads.adwords._AdWordsHeaderHandler(
        self.adwords_client, CURRENT_VERSION, False, None)


  def testLoadFromStorage(self):
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient.Refresh'):
      self.assertIsInstance(googleads.adwords.AdWordsClient.LoadFromStorage(
          path=self.load_from_storage_path), googleads.adwords.AdWordsClient)

  def testLoadFromStorageWithCompressionEnabled(self):
    enable_compression = True
    user_agent_gzip_template = '%s (gzip)'
    default_user_agent = 'unit testing'

    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      mock_load.return_value = {
          'developer_token': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': mock.Mock(),
          'user_agent': default_user_agent,
          'enable_compression': enable_compression
      }
      client = googleads.adwords.AdWordsClient.LoadFromStorage()
      self.assertEqual(enable_compression, client.enable_compression)
      self.assertEqual(user_agent_gzip_template % default_user_agent,
                       client.user_agent)

  def testLoadFromStorageWithNonASCIIUserAgent(self):
    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      mock_load.return_value = {
          'developer_token': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': mock.Mock(),
          'user_agent': u'ゼロ'
      }
      self.assertRaises(googleads.errors.GoogleAdsValueError,
                        googleads.adwords.AdWordsClient.LoadFromStorage)

  def testLoadFromStorageWithNoUserAgent(self):
    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      mock_load.return_value = {
          'developer_token': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': mock.Mock()
      }

      client = googleads.adwords.AdWordsClient.LoadFromStorage()
      self.assertEqual(client.user_agent, 'unknown')

  def testGetService_success(self):
    client = GetAdWordsClient(
        timeout='timeout', cache='cache', proxy_config='proxy_config')
    client.enable_compression = True

    service_name = list(googleads.adwords._SERVICE_MAP[CURRENT_VERSION])[0]
    namespace = googleads.adwords._SERVICE_MAP[CURRENT_VERSION][service_name]
    # Use a custom server. Also test what happens if the server ends with a
    # trailing slash
    server = 'https://testing.test.com/'

    with mock.patch('googleads.common.'
                    'GetServiceClassForLibrary') as mock_get_service:
      with mock.patch('googleads.adwords.'
                      '_AdWordsHeaderHandler') as mock_header_handler:
        mock_header_handler.return_value = 'header_handler'

        impl = mock.Mock()
        mock_service = mock.Mock()
        impl.return_value = mock_service
        mock_get_service.return_value = impl

        service = client.GetService(service_name, CURRENT_VERSION, server)
        mock_header_handler.assert_called_once_with(
            client, CURRENT_VERSION, True, None)
        impl.assert_called_once_with(
            'https://testing.test.com/api/adwords/%s/%s/%s?wsdl' % (
                namespace, CURRENT_VERSION, service_name),
            'header_handler',
            googleads.adwords._AdWordsPacker,
            'proxy_config',
            'timeout',
            CURRENT_VERSION,
            cache='cache')
        self.assertEqual(service, mock_service)

  def testGetService_badService(self):
    version = CURRENT_VERSION
    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        self.adwords_client.GetService,
        'GYIVyievfyiovslf', version)

  def testGetService_badVersion(self):
    self.assertRaises(
        googleads.errors.GoogleAdsValueError, self.adwords_client.GetService,
        'CampaignService', '11111')

  def testGetBatchJobHelper(self):
    with mock.patch('googleads.adwords.BatchJobHelper') as mock_helper:
      self.assertEqual(
          mock_helper.return_value,
          self.adwords_client.GetBatchJobHelper())

  def testGetReportDownloader(self):
    with mock.patch('googleads.adwords.ReportDownloader') as mock_downloader:
      self.assertEqual(
          mock_downloader.return_value,
          self.adwords_client.GetReportDownloader('version', 'server'))
      mock_downloader.assert_called_once_with(
          self.adwords_client, 'version', 'server')

  def testSetClientCustomerId(self):
    create_method = mock.Mock()
    ccid = 'modified'
    # Check that the SOAP header has the modified client customer id.
    self.adwords_client.SetClientCustomerId(ccid)
    header_result = self.header_handler.GetSOAPHeaders(create_method)
    self.assertEqual(ccid, header_result.clientCustomerId)


class AdWordsClientIntegrationTest(unittest.TestCase):
  """Integration tests for googleads.adwords.AdWordsClient."""

  def testServiceMap(self):
    server = googleads.adwords._DEFAULT_ENDPOINT
    service_map = googleads.adwords._SERVICE_MAP
    wsdl_url_template = googleads.adwords.AdWordsClient._SOAP_SERVICE_FORMAT

    for version, services in service_map.items():
      for service, mapping in services.items():
        wsdl_url = wsdl_url_template % (server, mapping, version, service)
        try:
          urlopen(wsdl_url)
        except HTTPError:
          raise ValueError('AdWords API %s does not contain "%s" with mapping '
                           '"%s". The generated WSDL URL does not exist:\n%s'
                           % (version, service, mapping, wsdl_url))


class AdWordsPackerTest(unittest.TestCase):
  """Tests for the googleads.adwords._AdWordsPacker class."""

  def setUp(self):
    self.packer = googleads.adwords._AdWordsPacker

  def testAdWordsPackerForServiceQuery(self):
    query = (googleads.adwords.ServiceQueryBuilder()
             .Select('Id', 'Name', 'Status')
             .Where('Status').EqualTo('ENABLED')
             .OrderBy('Name')
             .Limit(0, 100)
             .Build())

    query_regex = (r'SELECT (.*) WHERE Status = "ENABLED"'
                   r' ORDER BY Name ASC LIMIT 0,100')

    self.assertRegexpMatches(self.packer.Pack(query, CURRENT_VERSION),
                             query_regex)

  def testAdWordsPackerForUnsupportedObjectType(self):
    obj = object()
    self.assertEqual(self.packer.Pack(obj, CURRENT_VERSION), obj)


class BatchJobHelperTest(testing.CleanUtilityRegistryTestCase):

  """Test suite for BatchJobHelper utility."""

  def setUp(self):
    """Prepare tests."""
    self.client = GetAdWordsClient()
    self.batch_job_helper = self.client.GetBatchJobHelper()

  def testGetId(self):
    expected = [-x for x in range(1, 101)]
    for value in expected:
      self.assertEqual(value, self.batch_job_helper.GetId())

  def testUploadOperations(self):
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    'BuildUploadRequest') as mock_build_request:
      mock_request = mock.Mock()
      mock_request.data = 'in disguise.'
      mock_request.get_full_url.return_value = 'https://google.com/'
      mock_request.headers = {'Content-range': 0, 'Content-length': 0}
      mock_build_request.return_value = mock_request
      with mock.patch('googleads.adwords.IncrementalUploadHelper'
                      '._InitializeURL') as mock_init:
        mock_init.return_value = 'https://www.google.com'
        with mock.patch('urllib.request.OpenerDirector.open') as mock_open:
          self.batch_job_helper.UploadOperations([[]])
          mock_open.assert_called_with(mock_request)


class BatchJobUploadRequestBuilderTest(testing.CleanUtilityRegistryTestCase):

  """Test suite for the BatchJobUploadRequestBuilder."""

  ENVELOPE_NS = 'http://schemas.xmlsoap.org/soap/envelope/'

  def setUp(self):
    """Prepare tests."""
    self.client = GetAdWordsClient()
    self.request_builder = self.client.GetBatchJobHelper()._request_builder
    self.version = self.request_builder._version
    self.upload_url = 'https://goo.gl/IaQQsJ'
    self.sample_xml = ('<operations><id>!n3vERg0Nn4Run4r0und4NDd35Er7Y0u!~</id>'
                       '</operations>')
    self.complete_request_body = '%s%s%s' % (
        self.request_builder._UPLOAD_PREFIX_TEMPLATE % (
            self.request_builder._adwords_endpoint),
        self.sample_xml,
        self.request_builder._UPLOAD_SUFFIX)
    self.request_body_complete = '%s%s%s' % (
        self.request_builder._UPLOAD_PREFIX_TEMPLATE % (
            self.request_builder._adwords_endpoint),
        self.sample_xml,
        self.request_builder._UPLOAD_SUFFIX)
    self.request_body_start = '%s%s' % (
        self.request_builder._UPLOAD_PREFIX_TEMPLATE %
        self.request_builder._adwords_endpoint, self.sample_xml)
    self.request_body_end = '%s%s' % (
        self.sample_xml,
        self.request_builder._UPLOAD_SUFFIX)
    self.single_upload_headers = {
        'Content-type': 'application/xml',
        'Content-range': 'bytes %s-%s/%s' % (
            0,
            self.request_builder._BATCH_JOB_INCREMENT - 1,
            self.request_builder._BATCH_JOB_INCREMENT),
        'Content-length': self.request_builder._BATCH_JOB_INCREMENT
        }
    self.incremental_upload_headers = {
        'Content-type': 'application/xml',
        'Content-range': 'bytes %s-%s/*' % (
            self.request_builder._BATCH_JOB_INCREMENT,
            (self.request_builder._BATCH_JOB_INCREMENT * 2) - 1
        ),
        'Content-length': self.request_builder._BATCH_JOB_INCREMENT
    }

  @classmethod
  def setUpClass(cls):
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(
        test_dir, 'test_data/batch_job_util_budget_template.txt')) as handler:
      cls.BUDGET_TEMPLATE = handler.read()
    with open(os.path.join(
        test_dir,
        'test_data/batch_job_util_campaign_criterion_template.txt')) as handler:
      cls.CAMPAIGN_CRITERION_TEMPLATE = handler.read()
    with open(os.path.join(
        test_dir,
        'test_data/batch_job_util_campaign_label_template.txt')) as handler:
      cls.CAMPAIGN_LABEL_TEMPLATE = handler.read()
    with open(os.path.join(
        test_dir, 'test_data/batch_job_util_invalid_request.txt')) as handler:
      cls.INVALID_API_REQUEST = handler.read()
    with open(os.path.join(
        test_dir, 'test_data/batch_job_util_not_request.txt')) as handler:
      cls.NOT_API_REQUEST = handler.read()
    with open(os.path.join(
        test_dir, 'test_data/batch_job_util_raw_request_template.txt')
             ) as handler:
      cls.RAW_API_REQUEST_TEMPLATE = handler.read()
    with open(os.path.join(
        test_dir, 'test_data/batch_job_util_operations_template.txt')
             ) as handler:
      cls.OPERATIONS_TEMPLATE = handler.read()
    with open(os.path.join(
        test_dir, 'test_data/batch_job_util_upload_template.txt')) as handler:
      cls.UPLOAD_OPERATIONS_TEMPLATE = handler.read()

  def ExpandOperandTemplate(self, operation_type, operand):
    """Expands the appropriate operand for the given operation_type.

    Args:
      operation_type: str indicating the type of operation the operand is being
        expanded for. Accepted types include: "BudgetOperation",
        "CampaignCriterionOperation", and "CampaignLabelOperation".
      operand: dict containing fields for the operation_type's operand.

    Returns:
      A str containing the expanded operand.

    Raises:
      ValueError: if an unsupported operation_type is specified.
    """
    if operation_type == 'BudgetOperation':
      return self.BUDGET_TEMPLATE % (
          operand['budgetId'], operand['name'],
          operand['amount']['microAmount'], operand['deliveryMethod'])
    elif operation_type == 'CampaignCriterionOperation':
      return self.CAMPAIGN_CRITERION_TEMPLATE % (
          operand['CampaignCriterion.Type'], operand['campaignId'],
          operand['criterion']['Criterion.Type'],
          operand['criterion']['text'],
          operand['criterion']['matchType'])
    elif operation_type == 'CampaignLabelOperation':
      return self.CAMPAIGN_LABEL_TEMPLATE % (
          operand['campaignId'], operand['labelId'])
    else:
      raise ValueError('Invalid operation_type "%s" specified.'
                       % operation_type)

  def GenerateOperations(self, operation_type, num_operations):
    """Generates a set of operations of the given type.

    Args:
      operation_type: str indicating the type of operation to be generated.
        Accepted types include: "BudgetOperation", "CampaignCriterionOperation",
        and "CampaignLabelOperation".
      num_operations: a positive int defining the number of operations to be
        generated.

    Returns:
      A tuple where the first item indicates the method to be used in the
      request and the second is a list of dictionaries containing distinct
      operations of the given operation_type.

    Raises:
      ValueError: if an unsupported operation_type is specified.
    """
    operation_range = range(1, num_operations + 1)

    if operation_type == 'BudgetOperation':
      return ('mutate', [{
          'operator': 'ADD',
          'xsi_type': 'BudgetOperation',
          'operand': {
              'budgetId': str(i),
              'name': 'Batch budget #%s' % i,
              'amount': {'microAmount': str(3333333 * i)},
              'deliveryMethod': 'STANDARD'}
      } for i in operation_range])
    elif operation_type == 'CampaignCriterionOperation':
      return ('mutate', [{
          'operator': 'ADD',
          'xsi_type': 'CampaignCriterionOperation',
          'operand': {
              'xsi_type': 'NegativeCampaignCriterion',
              'campaignId': str(100 * i),
              'criterion': {
                  'xsi_type': 'Keyword',
                  'text': 'venus %s' % i,
                  'matchType': 'BROAD'
              }
          }
      } for i in operation_range])
    elif operation_type == 'CampaignLabelOperation':
      return ('mutateLabel', [{
          'operator': 'ADD',
          'xsi_type': 'CampaignLabelOperation',
          'operand': {
              'campaignId': 123 * i,
              'labelId': 321 * i}
      } for i in operation_range])
    else:
      raise ValueError('Invalid operation_type "%s" specified.'
                       % operation_type)

  def GenerateValidRequest(self, operation_type, num_operations=1):
    """Generates a valid API request containing the given number of operations.

    Args:
      operation_type: str indicating the type of operation to be generated.
        Accepted types include: "BudgetOperation", "CampaignCriterionOperation",
        and "CampaignLabelOperation".
      num_operations: a positive int defining the number of operations to be
        generated.

    Returns:
      A tuple containing the operations used to construct str containing a valid
      API request.

    Raises:
      ValueError: if an unsupported operation_type is specified.
    """
    method, ops = self.GenerateOperations(operation_type, num_operations)

    ops_xml = ''.join([self.OPERATIONS_TEMPLATE % (
        op['operator'], op['xsi_type'],
        self.ExpandOperandTemplate(operation_type, op['operand'])
    ) for op in ops])

    request = self.RAW_API_REQUEST_TEMPLATE % (
        self.version, self.version, method, ops_xml, method)
    request = bytes(request, 'utf-8')
    request = lxml.etree.fromstring(request)

    return (ops, request)

  def GenerateValidUnicodeRequest(self, operations):
    """Generates a valid API request containing the given number of operations.

    Args:
      operations: a positive int defining the number of BudgetOperations to be
      generated.

    Returns:
      A tuple containing the operations used to construct unicode containing a
      valid API request.
    """
    ops = self.GenerateUnicodeBudgetOperations(operations)
    method = 'mutate'
    ops_xml = ''.join([self.OPERATIONS_TEMPLATE % (
        op['operator'], op['xsi_type'],
        self.ExpandOperandTemplate('BudgetOperation', op['operand'])
    ) for op in ops])

    request = (self.RAW_API_REQUEST_TEMPLATE % (
        self.version, self.version, method, ops_xml, method)).encode('utf-8')
    request = lxml.etree.fromstring(request)

    return (ops, request)

  def GenerateUnicodeBudgetOperations(self, operations):
    """Generates request containing given number of BudgetOperations.

    Args:
      operations: a positive int defining the number of BudgetOperations to be
        generated.
    Returns:
      A list of dictionaries containing distinct BudgetOperations.
    """
    return [{
        'operator': 'ADD',
        'xsi_type': 'BudgetOperation',
        'operand': {
            'budgetId': str(i),
            'name': u'アングリーバード Batch budget #%d' % i,
            'amount': {'microAmount': str(3333333 * i)},
            'deliveryMethod': 'STANDARD'}
    } for i in range(1, operations + 1)]

  def testGetPaddingLength(self):
    length = len(self.sample_xml)
    padding = self.request_builder._GetPaddingLength(length)
    self.assertTrue(
        padding == self.request_builder._BATCH_JOB_INCREMENT - length)

  def testExtractOperations(self):
    """Tests whether operations XML was extracted and formatted correctly.

    Verifies that the xsi_type has been properly assigned.
    """
    _, operations = self.GenerateOperations('CampaignCriterionOperation', 1)
    raw_xml = self.request_builder._GenerateRawRequestXML(operations)
    operations_xml = self.request_builder._ExtractOperations(raw_xml)
    # Put operations in a format that allows us to easily verify the behavior.
    ElementTree.register_namespace(
        'xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    # Need to declare xsi for ElementTree to parse operations properly.
    body = ElementTree.fromstring(
        '<body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">%s'
        '</body>' % operations_xml)
    self.assertTrue(body.tag == 'body')
    ops_element = body.find('operations')
    # Check that the xsi_type has been set correctly.
    self.assertTrue(ops_element.attrib[
        '{http://www.w3.org/2001/XMLSchema-instance}type'] ==
                    'CampaignCriterionOperation')
    operand = ops_element.find('operand')
    self.assertTrue(operand.attrib[
        '{http://www.w3.org/2001/XMLSchema-instance}type'] ==
                    'NegativeCampaignCriterion')
    criterion = operand.find('criterion')
    self.assertTrue(criterion.attrib[
        '{http://www.w3.org/2001/XMLSchema-instance}type'] ==
                    'Keyword')

  def testFormatForBatchJobService(self):
    """Tests whether namespaces have been removed."""
    operations_amount = 5
    _, ops = self.GenerateOperations('CampaignCriterionOperation',
                                     operations_amount)
    root = self.request_builder._GenerateRawRequestXML(ops)
    body = root.find('{%s}Body' % self.ENVELOPE_NS)
    mutate = body.find('{%s}mutate' % self.request_builder._adwords_endpoint)
    self.request_builder._FormatForBatchJobService(mutate)
    self.assertTrue(self.request_builder._adwords_endpoint not in mutate.tag)
    self.assertTrue(len(mutate) == operations_amount)

    for ops in mutate:
      self.assertTrue(self.request_builder._adwords_endpoint not in ops.tag)
      for child in ops:
        self.assertTrue(self.request_builder._adwords_endpoint not in
                        child.tag)
      operand = ops.find('operand')
      self.assertTrue(len(operand.attrib) == 1)
      self.assertTrue(
          'ns' not in
          operand.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'])
      for child in operand:
        self.assertTrue(self.request_builder._adwords_endpoint not in
                        child.tag)
      criterion = operand.find('criterion')
      self.assertTrue(
          'ns' not in
          criterion.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'])
      for child in criterion:
        self.assertTrue(self.request_builder._adwords_endpoint not in
                        child.tag)

  def testGenerateOperationsXMLNoXsiType(self):
    """Tests whether _GenerateOperationsXML raises ValueError if no xsi_type.
    """
    _, operations = self.GenerateOperations('CampaignCriterionOperation', 1)
    del operations[0]['xsi_type']
    self.assertRaises(
        googleads.errors.AdWordsBatchJobServiceInvalidOperationError,
        self.request_builder._GenerateOperationsXML, operations)

  def testGenerateOperationsXMLWithNoOperations(self):
    """Tests whether _GenerateOperationsXML produces empty str if no operations.
    """
    _, operations = self.GenerateOperations('CampaignCriterionOperation', 0)
    raw_xml = self.request_builder._GenerateOperationsXML(
        operations)
    self.assertTrue(raw_xml is '')

  def testGenerateRawRequestXMLFromBogusOperation(self):
    """Tests whether an invalid operation raises an Exception."""
    bogus_operations = [{
        'operator': 'ADD',
        'xsi_type': 'BogusOperation',
        'operand': {
            'bogusProperty': 'bogusValue'}
    }]

    self.assertRaises(KeyError,
                      self.request_builder._GenerateRawRequestXML,
                      bogus_operations)

  def testGenerateRawRequestXMLFromCampaignLabelOperation(self):
    """Tests whether raw request xml can be produced from a label operation."""
    ops = [{
        'operator': 'ADD',
        'xsi_type': 'CampaignLabelOperation',
        'operand': {'campaignId': 0, 'labelId': 0}
    }]

    root = self.request_builder._GenerateRawRequestXML(ops)
    self.assertTrue(len(root) == 2)
    body = root.find('{%s}Body' % self.ENVELOPE_NS)
    self.assertTrue(len(body) == 1)
    mutate_label = body.find('{%s}mutateLabel'
                             % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate_label) == len(ops))

  def testGenerateRawRequestXMLFromSingleOperation(self):
    """Tests whether raw request xml can be produced from a single operation."""
    operations_amount = 1
    _, ops = self.GenerateOperations('BudgetOperation', operations_amount)

    root = self.request_builder._GenerateRawRequestXML(ops)
    self.assertTrue(len(root) == 2)
    body = root.find('{%s}Body' % self.ENVELOPE_NS)
    self.assertTrue(len(body) == 1)
    mutate = body.find('{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(operations.tag, '{%s}operations' %
                       self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations.getchildren()) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(
          operations.find(
              '{%s}Operation.Type' %
              self.request_builder._adwords_endpoint).text,
          ops[i]['xsi_type'])
      operand = operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operand.getchildren()) ==
                      len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      amount = operand.find('{%s}amount' %
                            self.request_builder._adwords_endpoint)
      self.assertTrue(len(amount.getchildren()) ==
                      len(ops[i]['operand']['amount'].keys()))
      self.assertEqual(amount.find(
          '{%s}microAmount' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['amount']['microAmount'])
      self.assertEqual(operand.find(
          '{%s}deliveryMethod' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['deliveryMethod'])

  def testGenerateRawRequestXMLFromMultipleOperations(self):
    """Tests whether raw request xml can be produced for multiple operations."""
    operations_amount = 5
    _, ops = self.GenerateOperations('BudgetOperation', operations_amount)

    root = self.request_builder._GenerateRawRequestXML(ops)
    self.assertTrue(len(root) == 2)
    body = root.find('{%s}Body' % self.ENVELOPE_NS)
    self.assertTrue(len(body) == 1)
    mutate = body.find('{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(
          operations.tag,
          '{%s}operations' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations.getchildren()) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operand.getchildren()) ==
                      len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      amount = operand.find(
          '{%s}amount' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(amount.getchildren()) ==
                      len(ops[i]['operand']['amount'].keys()))
      self.assertEqual(amount.find(
          '{%s}microAmount' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['amount']['microAmount'])
      self.assertEqual(operand.find(
          '{%s}deliveryMethod' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['deliveryMethod'])

  def testGenerateRawUnicodeRequestXMLFromSingleOperation(self):
    """Tests whether raw request xml can be produced from a single operation."""
    operations_amount = 1
    ops = self.GenerateUnicodeBudgetOperations(operations_amount)

    root = self.request_builder._GenerateRawRequestXML(ops)
    self.assertTrue(len(root) == 2)
    body = root.find(u'{%s}Body' % self.ENVELOPE_NS)
    self.assertTrue(len(body) == 1)
    mutate = body.find(u'{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(operations.tag, '{%s}operations' %
                       self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations.getchildren()) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(
          operations.find(
              '{%s}Operation.Type' %
              self.request_builder._adwords_endpoint).text,
          ops[i]['xsi_type'])
      operand = operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operand.getchildren()) ==
                      len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      amount = operand.find('{%s}amount' %
                            self.request_builder._adwords_endpoint)
      self.assertTrue(len(amount.getchildren()) ==
                      len(ops[i]['operand']['amount'].keys()))
      self.assertEqual(amount.find(
          '{%s}microAmount' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['amount']['microAmount'])
      self.assertEqual(operand.find(
          '{%s}deliveryMethod' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['deliveryMethod'])

  def testGetRawOperationsFromValidSingleOperationMutateLabelRequest(self):
    """Test if operations XML can be retrieved for a single-op label request."""
    operations_amount = 1
    ops, request = self.GenerateValidRequest('CampaignLabelOperation',
                                             operations_amount)

    mutate = self.request_builder._GetRawOperationsFromXML(request)
    self.assertEqual(mutate.tag,
                     '{%s}mutateLabel' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate.getchildren()) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(
          operations.tag,
          '{%s}operations' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations.getchildren()) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operand.getchildren()) ==
                      len(ops[i]['operand'].keys()))
      self.assertEqual(int(operand.find(
          '{%s}campaignId' % self.request_builder._adwords_endpoint).text),
                       ops[i]['operand']['campaignId'])
      self.assertEqual(int(operand.find(
          '{%s}labelId' % self.request_builder._adwords_endpoint).text),
                       ops[i]['operand']['labelId'])

  def testGetRawOperationsFromValidSingleOperationRequest(self):
    """Test if operations XML can be retrieved for a single-op request.

    Also verifies that the contents of generated XML are correct.
    """
    operations_amount = 1
    ops, request = self.GenerateValidRequest('BudgetOperation',
                                             operations_amount)

    mutate = self.request_builder._GetRawOperationsFromXML(request)
    self.assertEqual(mutate.tag,
                     '{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate.getchildren()) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(
          operations.tag,
          '{%s}operations' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations.getchildren()) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operand.getchildren()) ==
                      len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      amount = operand.find(
          '{%s}amount' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(amount.getchildren()) ==
                      len(ops[i]['operand']['amount'].keys()))
      self.assertEqual(amount.find(
          '{%s}microAmount' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['amount']['microAmount'])
      self.assertEqual(operand.find(
          '{%s}deliveryMethod' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['deliveryMethod'])

  def testGetRawOperationsFromValidMultipleOperationRequest(self):
    """Test whether operations XML can be retrieved for a multi-op request.

    Also verifies that the contents of generated XML are correct.
    """
    operations_amount = 5
    ops, request = self.GenerateValidRequest('BudgetOperation',
                                             operations_amount)

    mutate = self.request_builder._GetRawOperationsFromXML(request)
    self.assertEqual(
        mutate.tag,
        '{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate.getchildren()) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(
          operations.tag,
          '{%s}operations' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations.getchildren()) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = (operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint))
      self.assertTrue(len(operand.getchildren()) ==
                      len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      amount = (operand.find(
          '{%s}amount' % self.request_builder._adwords_endpoint))
      self.assertTrue(len(amount.getchildren()) ==
                      len(ops[i]['operand']['amount'].keys()))
      self.assertEqual(amount.find(
          '{%s}microAmount' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['amount']['microAmount'])
      self.assertEqual(operand.find(
          '{%s}deliveryMethod' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['deliveryMethod'])

  def testGetRawOperationsFromValidMultipleOperationUnicodeRequest(self):
    """Test whether operations XML can be retrieved for a multi-op request.

    Also verifies that the contents of generated XML are correct.
    """
    operations_amount = 5
    ops, request = self.GenerateValidUnicodeRequest(operations_amount)

    mutate = self.request_builder._GetRawOperationsFromXML(request)
    self.assertEqual(
        mutate.tag,
        u'{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate.getchildren()) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(
          operations.tag,
          '{%s}operations' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations.getchildren()) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = (operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint))
      self.assertTrue(len(operand.getchildren()) ==
                      len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      amount = (operand.find(
          '{%s}amount' % self.request_builder._adwords_endpoint))
      self.assertTrue(len(amount.getchildren()) ==
                      len(ops[i]['operand']['amount'].keys()))
      self.assertEqual(amount.find(
          '{%s}microAmount' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['amount']['microAmount'])
      self.assertEqual(operand.find(
          '{%s}deliveryMethod' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['deliveryMethod'])

  def testGetRawOperationsFromValidZeroOperationRequest(self):
    """Test verifying empty request generated if no operations provided."""
    operations_amount = 0
    _, request = self.GenerateValidRequest('BudgetOperation',
                                           operations_amount)

    mutate = self.request_builder._GetRawOperationsFromXML(request)

    self.assertEqual(
        mutate.tag,
        '{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate.getchildren()) == operations_amount)

  def testGetRawOperationsFromInvalidRequest(self):
    """Test whether an invalid API request raises an Exception."""
    self.assertRaises(AttributeError,
                      self.request_builder._GetRawOperationsFromXML,
                      self.INVALID_API_REQUEST)

  def testGetRawOperationsFromNotXMLRequest(self):
    """Test whether non-XML input raises an Exception."""
    self.assertRaises(AttributeError,
                      self.request_builder._GetRawOperationsFromXML,
                      self.NOT_API_REQUEST)

  def testBuildRequestForSingleUpload(self):
    """Test whether a single upload request is build correctly."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    '_BuildUploadRequestBody') as mock_request_body_builder:
      mock_request_body_builder.return_value = self.sample_xml
      req = self.request_builder.BuildUploadRequest(self.upload_url, [[]],
                                                    is_last=True)
      self.assertEqual(req.headers, self.single_upload_headers)
      self.assertEqual(req.get_method(), 'PUT')

  def testBuildRequestForIncrementalUpload(self):
    """Test whether an incremental upload request is built correctly."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    '_BuildUploadRequestBody') as mock_request_body_builder:
      mock_request_body_builder.return_value = self.sample_xml
      req = self.request_builder.BuildUploadRequest(
          self.upload_url, [[]],
          current_content_length=self.request_builder._BATCH_JOB_INCREMENT)
      self.assertEqual(req.headers, self.incremental_upload_headers)
      self.assertEqual(req.get_method(), 'PUT')

  def testBuildUploadRequestBody(self):
    """Test whether a a complete request body is built correctly."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    '_GenerateOperationsXML') as mock_generate_xml:
      mock_generate_xml.return_value = self.sample_xml
      with mock.patch('googleads.adwords.BatchJobHelper._'
                      'UploadRequestBuilder.'
                      '_GetPaddingLength') as mock_get_padding_length:
        mock_get_padding_length.return_value = 0
        increment = self.request_builder._BuildUploadRequestBody([[]])
        self.assertTrue(increment == self.request_body_complete)

  def testBuildUploadRequestBodyWithSuffix(self):
    """Test whether a request body is built correctly with only the suffix."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    '_GenerateOperationsXML') as mock_generate_xml:
      mock_generate_xml.return_value = self.sample_xml
      with mock.patch('googleads.adwords.BatchJobHelper.'
                      '_UploadRequestBuilder.'
                      '_GetPaddingLength') as mock_get_padding_length:
        mock_get_padding_length.return_value = 0
        increment = self.request_builder._BuildUploadRequestBody(
            [[]], has_prefix=False)
        self.assertTrue(increment == self.request_body_end)

  def testBuildUploadRequestBodyWithoutPrefixOrSuffix(self):
    """Test whether a request body is built correctly without prefix/suffix."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    '_GenerateOperationsXML') as mock_generate_xml:
      mock_generate_xml.return_value = self.sample_xml
      with mock.patch('googleads.adwords.BatchJobHelper.'
                      '_UploadRequestBuilder.'
                      '_GetPaddingLength') as mock_get_padding_length:
        mock_get_padding_length.return_value = 0
        increment = self.request_builder._BuildUploadRequestBody(
            [[]], has_prefix=False, has_suffix=False)
        self.assertTrue(increment == self.sample_xml)

  def testBuildUploadRequestBodyWithOnlyPrefix(self):
    """Test whether a request body is built correctly with only the prefix."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    '_GenerateOperationsXML') as mock_generate_xml:
      mock_generate_xml.return_value = self.sample_xml
      with mock.patch('googleads.adwords.BatchJobHelper.'
                      '_UploadRequestBuilder.'
                      '_GetPaddingLength') as mock_get_padding_length:
        mock_get_padding_length.return_value = 0
        increment = self.request_builder._BuildUploadRequestBody(
            [[]], has_suffix=False)
        self.assertTrue(increment == self.request_body_start)


class IncrementalUploadHelperTest(testing.CleanUtilityRegistryTestCase):

  """Test suite for the IncrementalUploadHelper."""

  def GetIncrementalUploadHelper(self):
    with mock.patch('urllib.request.OpenerDirector.open') as mock_open:
      mock_open.return_value.headers = {'location': self.initialized_url}
      return self.batch_job_helper.GetIncrementalUploadHelper(self.original_url)

  def setUp(self):
    """Prepare tests."""
    self.client = GetAdWordsClient()
    self.server = 'https://test.com'
    self.version = 'test_version'
    self.batch_job_helper = self.client.GetBatchJobHelper(
        version=self.version, server=self.server)
    self.original_url = 'https://goo.gl/w8tkpK'
    self.initialized_url = 'https://goo.gl/Xtaq83'
    self.incremental_uploader = self.GetIncrementalUploadHelper()

    self.incremental_uploader_dump = (
        '{current_content_length: 0, is_last: false, '
        'server: \'https://test.com\', upload_url: \'https://goo.gl/Xtaq83\','
        'version: %s}\n' % self.version)

  def testDump(self):
    expected = yaml.load(self.incremental_uploader_dump)

    with tempfile.NamedTemporaryFile(delete=False, mode='w') as t:
      name = t.name
      self.incremental_uploader.Dump(t)

    with open(name, mode='r') as handler:
      dump_data = yaml.safe_load(handler)

    self.assertEqual(expected, dump_data)

  def testLoad(self):
    s = io.StringIO(self.incremental_uploader_dump)

    with mock.patch('urllib.request.OpenerDirector.open') as mock_open:
      mock_open.return_value.headers = {
          'location': self.initialized_url
      }
      with mock.patch('googleads.adwords.IncrementalUploadHelper'
                      '._InitializeURL') as mock_init:
        mock_init.return_value = self.initialized_url
        restored_uploader = googleads.adwords.IncrementalUploadHelper.Load(
            s, client=self.client)

    self.assertEquals(restored_uploader._current_content_length,
                      self.incremental_uploader._current_content_length)
    self.assertEquals(restored_uploader._is_last,
                      self.incremental_uploader._is_last)
    self.assertEquals(restored_uploader._request_builder._version,
                      self.version)
    self.assertEquals(restored_uploader._upload_url,
                      self.incremental_uploader._upload_url)
    self.assertEquals(restored_uploader._request_builder.GetServer(),
                      self.server)

  def testUploadOperations(self):
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    'BuildUploadRequest') as mock_build_request:
      mock_request = mock.MagicMock()
      mock_build_request.return_value = mock_request
      with mock.patch('urllib.request.OpenerDirector.open') as mock_open:
        self.incremental_uploader.UploadOperations([[]], True)
        mock_open.assert_called_with(mock_request)

  def testUploadOperationsWithError(self):
    error_url = 'https://google.com/'
    error_code = '404'
    error_message = 'I AM ERROR'
    error_headers = {}
    http_error = HTTPError(
        error_url, error_code, error_message, error_headers, None)

    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    'BuildUploadRequest') as mock_build_request:
      mock_request = mock.MagicMock()
      mock_build_request.return_value = mock_request
      with mock.patch('urllib.request.OpenerDirector.open') as mock_open:
        mock_open.side_effect = http_error
        self.assertRaises(
            HTTPError,
            self.incremental_uploader.UploadOperations, [[]], True)
        mock_open.assert_called_with(mock_request)

  def testUploadOperationsAfterFinished(self):
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_UploadRequestBuilder.'
                    'BuildUploadRequest') as mock_build_request:
      mock_request = mock.MagicMock()
      mock_build_request.return_value = mock_request
      with mock.patch('urllib.request.OpenerDirector.open'):
        self.incremental_uploader.UploadOperations([[]], True)
        self.assertRaises(
            googleads.errors.AdWordsBatchJobServiceInvalidOperationError,
            self.incremental_uploader.UploadOperations, {})

  def testRequestHasCustomHeaders(self):
    class MyOpener(object):
      addheaders = [('a', 'b')]
    opener = MyOpener()

    with mock.patch('googleads.adwords.build_opener') as mock_build_opener,\
        mock.patch('googleads.adwords.IncrementalUploadHelper._InitializeURL'):
      mock_build_opener.return_value = opener
      self.client.custom_http_headers = {'X-My-Headers': 'abc'}

      self.GetIncrementalUploadHelper()

      self.assertEqual(opener.addheaders, [('a', 'b'), ('X-My-Headers', 'abc')])


class ResponseParserTest(testing.CleanUtilityRegistryTestCase):
  """Test suite for the ResponseParser."""

  def setUp(self):
    """Prepare tests."""
    self.client = GetAdWordsClient()
    self.response_parser = googleads.adwords.BatchJobHelper.GetResponseParser()

  @classmethod
  def setUpClass(cls):
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(
        test_dir, 'test_data/batch_job_util_response_template.txt')) as handler:
      cls.API_RESPONSE_XML_TEMPLATE = handler.read()

  def testParseResponse(self):
    campaign_id = '1'
    name = 'Test Campaign'
    status = 'PAUSED'
    serving_status = 'SUSPENDED'
    start_date = '20151116'
    end_date = '20371230'
    budget_id = '2'
    budget_name = 'Test Budget'
    micro_amount = '50000000'
    delivery_method = 'STANDARD'
    is_explicitly_shared = 'true'
    bidding_strategy_type = 'MANUAL_CPC'

    response = (
        self.response_parser.ParseResponse(
            self.API_RESPONSE_XML_TEMPLATE %
            (campaign_id, name, status, serving_status, start_date, end_date,
             budget_id, budget_name, micro_amount, delivery_method,
             is_explicitly_shared, bidding_strategy_type))
        ['mutateResponse']['rval'])

    # Assert that we correct parsed the response (2 results: Budget & Campaign)
    self.assertTrue(len(response) == 2)

    campaign = response[1]['result']['Campaign']
    self.assertTrue(campaign['id'] == campaign_id)
    self.assertTrue(campaign['name'] == name)
    self.assertTrue(campaign['status'] == status)
    self.assertTrue(campaign['servingStatus'] == serving_status)
    self.assertTrue(campaign['startDate'] == start_date)
    self.assertTrue(campaign['endDate'] == end_date)
    self.assertTrue(campaign['budget']['name'] == budget_name)
    self.assertTrue(campaign['budget']['amount']['microAmount'] == micro_amount)
    self.assertTrue(campaign['budget']['isExplicitlyShared'] ==
                    is_explicitly_shared)
    self.assertTrue(
        campaign['biddingStrategyConfiguration']['biddingStrategyType'] ==
        bidding_strategy_type)

  def testParseUnicodeResponse(self):
    campaign_id = u'1'
    name = u'アングリーバード'
    status = u'PAUSED'
    serving_status = u'SUSPENDED'
    start_date = u'20151116'
    end_date = u'20371230'
    budget_id = u'2'
    budget_name = u'Test Budget'
    micro_amount = u'50000000'
    delivery_method = u'STANDARD'
    is_explicitly_shared = u'true'
    bidding_strategy_type = u'MANUAL_CPC'

    response = (
        self.response_parser.ParseResponse(
            self.API_RESPONSE_XML_TEMPLATE %
            (campaign_id, name, status, serving_status, start_date, end_date,
             budget_id, budget_name, micro_amount, delivery_method,
             is_explicitly_shared, bidding_strategy_type))
        ['mutateResponse']['rval'])

    self.assertTrue(len(response) == 2)
    campaign = response[1]['result']['Campaign']
    self.assertTrue(campaign['name'] == name)


def GetVersionedXSD(version):
  report_xsd = os.path.join(
      TEST_DIR, 'test_data/adwords_report_definition.xsd')

  with open(report_xsd, 'rb') as f:
    data = f.read()
    return data.replace(b'{VERSION}', bytes(version, 'utf-8'))


class ReportDownloaderZeepTest(testing.CleanUtilityRegistryTestCase):

  def setUp(self):
    self.version = CURRENT_VERSION
    self.opener = mock.Mock()
    self.adwords_client = mock.Mock()
    self.adwords_client.proxy_config = GetProxyConfig()
    self.adwords_client.cache = googleads.common.ZeepServiceProxy.NO_CACHE
    self.adwords_client.custom_http_headers = False
    self.header_handler = mock.Mock()

    post_body_path = os.path.join(
        TEST_DIR, 'test_data/adwords_report_post_body_no_formatting.txt')
    with open(post_body_path, 'r') as f:
      self.post_body_data = f.read().replace('{VERSION}', self.version)

    class XSDTransport(zeep.transports.Transport):

      def load(self, url):
        return GetVersionedXSD(CURRENT_VERSION)

    with mock.patch(
        'googleads.adwords._AdWordsHeaderHandler') as mock_handler:
      mock_handler.return_value = self.header_handler

      with mock.patch('googleads.common._ZeepProxyTransport') as mock_transport:
        mock_transport.return_value = XSDTransport()

        self.report_downloader = googleads.adwords.ReportDownloader(
            self.adwords_client, self.version
        )
    self.report_downloader.url_opener = self.opener

  @mock.patch('googleads.adwords._report_logger')
  @mock.patch.object(googleads.adwords, 'Request')
  def testDownloadReportWithZeep(self, mock_request, mock_logger):
    mock_logger.isEnabledFor.return_value = True
    output_file = io.StringIO()
    report_definition = {
        'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
        'dateRangeType': 'LAST_7_DAYS',
        'reportType': 'CRITERIA_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['CampaignId', 'AdGroupId', 'Id', 'CriteriaType',
                       'Criteria', 'FinalUrls', 'Impressions', 'Clicks', 'Cost']
        }
    }

    with mock.patch.object(self.report_downloader,
                           '_header_handler') as mock_header_handler, \
        (mock.patch.object(
            self.report_downloader,
            '_ExtractRequestSummaryFields')) as mock_extract_request_summary, \
        (mock.patch.object(
            self.report_downloader,
            '_ExtractResponseHeaders')) as mock_extract_response_headers:
      response_data = u'ABC 广告客户'
      response_fp = io.BytesIO()
      response_fp.write(bytes(response_data, 'utf-8'))
      response_fp.seek(0)
      mock_response = mock.Mock()
      mock_response.read.side_effect = response_fp.read
      mock_response.code = '200'
      self.opener.open.return_value = mock_response

      self.report_downloader.DownloadReport(report_definition, output_file,
                                            skip_report_header=True,
                                            use_raw_enum_values=False)

      mock_request.assert_called_once_with(
          self.report_downloader._end_point,
          (bytes(self.post_body_data, 'utf-8')),
          mock_header_handler.GetReportDownloadHeaders.return_value)

      output_file.seek(0)
      self.assertEqual(output_file.read(), response_data)
      mock_extract_request_summary.assert_called_once_with(
          mock_request.return_value)
      mock_extract_response_headers.assert_called_once_with(
          mock_response.headers)

class ReportDownloaderTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.adwords.ReportDownloader class."""

  def GetReportDownloader(self):
    with mock.patch(
        'googleads.adwords._AdWordsHeaderHandler') as mock_handler, \
        mock.patch('googleads.adwords.googleads.common'
                   '.GetSchemaHelperForLibrary') as mock_get_schema:
      mock_handler.return_value = self.header_handler
      mock_get_schema.return_value = mock.Mock()

      return googleads.adwords.ReportDownloader(
          self.adwords_client, self.version)

  def setUp(self):
    self.version = CURRENT_VERSION
    self.marshaller = mock.Mock()
    self.header_handler = mock.Mock()
    self.adwords_client = mock.Mock()
    self.adwords_client.proxy_config = GetProxyConfig()
    self.adwords_client.cache = googleads.common.ZeepServiceProxy.NO_CACHE
    self.adwords_client.custom_http_headers = False
    self.opener = mock.Mock()

    self.report_downloader = self.GetReportDownloader()
    self.report_downloader.url_opener = self.opener

    test_dir = os.path.dirname(__file__)
    test_data_path = os.path.join(test_dir, 'test_data/unicode_test_data.txt')
    with open(test_data_path, encoding='utf-8') as handler:
      self.budget_template = handler.read()

  def testSetsCustomHeaders(self):

    class MyOpener(object):
      addheaders = [('a', 'b')]
    opener = MyOpener()
    self.adwords_client.custom_http_headers = {'X-My-Header': 'abc'}

    with mock.patch('googleads.adwords.build_opener') as mock_build_opener:
      mock_build_opener.return_value = opener
      self.GetReportDownloader()

    self.assertEqual(opener.addheaders, [('a', 'b'), ('X-My-Header', 'abc')])

  @mock.patch('urllib.request.OpenerDirector.open')
  def testDownloadReportAsString(self, mock_request):
    serialize_response = mock.Mock()
    with mock.patch.object(
        self.report_downloader,
        '_DownloadReportAsStream') as mock_internal_download, \
        mock.patch.object(
            self.report_downloader,
            '_SerializeReportDefinition') as mock_internal_serialize:
      mock_internal_serialize.return_value = serialize_response

      self.report_downloader.DownloadReportAsString(
          'report_definition',
          some_arg='abc')

      mock_internal_serialize.assert_called_once_with('report_definition')
      mock_internal_download.assert_called_once_with(
          serialize_response,
          some_arg='abc')

  def testDownloadReportAsStringWithAwql(self):
    query = 'SELECT Id FROM Campaign WHERE NAME LIKE \'%Test%\''
    file_format = 'CSV'
    post_body = urlencode({'__fmt': file_format,
                                                  '__rdquery': query})
    post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    report_data = u'CONTENT STRING アングリーバード'
    report_contents = io.BytesIO()
    report_contents.write(bytes(report_data, 'utf-8'))
    report_contents.seek(0)
    fake_response = mock.Mock()
    fake_response.read.side_effect = report_contents.read
    fake_response.msg = 'fake message'
    fake_response.code = '200'

    with mock.patch.object(googleads.adwords, 'Request') as mock_request:
      mock_request_instance = mock.Mock()
      mock_request.return_value = mock_request_instance
      mock_request_instance.get_full_url.return_value = 'https://google.com/'
      mock_request_instance.headers = {}
      self.opener.open.return_value = fake_response
      s = self.report_downloader.DownloadReportAsStringWithAwql(
          query, file_format, include_zero_impressions=True,
          use_raw_enum_values=False)
      mock_request.assert_called_once_with(
          ('https://adwords.google.com/api/adwords/reportdownload/%s'
           % self.version), post_body, headers)
      self.opener.open.assert_called_once_with(mock_request.return_value)
    self.assertEqual(report_data, s)
    self.header_handler.GetReportDownloadHeaders.assert_called_once_with(
        include_zero_impressions=True, use_raw_enum_values=False)

  def testDownloadReportWithUnicodeReportDataIssue281(self):
    """This test verifies that issue #281 has been resolved.

    https://github.com/googleads/googleads-python-lib/issues/281

    Intentionally reads in a lot of unicode data with small chunk size to
    replicate issue where chunked data read in _DownloadReport on Python 3
    would cause a UnicodeDecodeError if multi-byte character were truncated.
    """
    test_dir = os.path.dirname(__file__)
    googleads.adwords._CHUNK_SIZE = 10  # Small chunk size used to replicate.

    with mock.patch.object(self.report_downloader,
                           '_DownloadReportAsStream') as stream:
      stream.return_value = open(os.path.join(
          test_dir, 'test_data/unicode_test_data.txt'), 'rb')
      report_definition = {'downloadFormat': 'CSV'}
      s = io.StringIO()
      self.report_downloader.DownloadReport(report_definition, output=s)

  def testDownloadReportCheckFormat_CSVStringSuccess(self):
    output_file = io.StringIO()

    try:
      self.report_downloader._DownloadReportCheckFormat('CSV', output_file)
    except googleads.errors.GoogleAdsValueError:
      self.fail('_DownloadReportCheckFormat raised GoogleAdsValueError'
                'unexpectedly!')

  def testDownloadReportCheckFormat_GZIPPEDBinaryFileSuccess(self):
    output_file = tempfile.TemporaryFile(mode='wb')

    try:
      self.report_downloader._DownloadReportCheckFormat(
          'GZIPPED_CSV', output_file)
    except googleads.errors.GoogleAdsValueError:
      self.fail('_DownloadReportCheckFormat raised GoogleAdsValueError'
                'unexpectedly!')

  def testDownloadReportCheckFormat_GZIPPEDBytesIOSuccess(self):
    output_file = io.BytesIO()

    try:
      self.report_downloader._DownloadReportCheckFormat('GZIPPED_CSV',
                                                        output_file)
    except googleads.errors.GoogleAdsValueError:
      self.fail('_DownloadReportCheckFormat raised GoogleAdsValueError'
                'unexpectedly!')

  def testDownloadReportCheckFormat_GZIPPEDStringFailure(self):
    output_file = io.StringIO()
    self.assertRaises(googleads.errors.GoogleAdsValueError,
                      self.report_downloader._DownloadReportCheckFormat,
                      'GZIPPED_CSV', output_file)

  def testDownloadReport_failure(self):
    output_file = io.StringIO()
    report_definition = {
        'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
        'dateRangeType': 'LAST_7_DAYS',
        'reportType': 'CRITERIA_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['CampaignId', 'AdGroupId', 'Id', 'CriteriaType',
                       'Criteria', 'FinalUrls', 'Impressions', 'Clicks', 'Cost']
        }
    }

    with mock.patch.object(self.report_downloader.url_opener,
                           'open') as mock_open:
      response_data = 'bad stuff happened'
      response_fp = io.BytesIO()
      response_fp.write(bytes(response_data, 'utf-8'))
      response_fp.seek(0)

      mock_open.side_effect = HTTPError(
          'http://abc', '500', 'whoops!', {}, response_fp)
      with mock.patch.object(self.report_downloader, '_header_handler'):
        with self.assertRaises(googleads.errors.AdWordsReportError):
          self.report_downloader.DownloadReport(report_definition, output_file,
                                                skip_report_header=True,
                                                use_raw_enum_values=False)

  def testDownloadReportWithAwql(self):
    output_file = io.StringIO()
    query = (googleads.adwords.ReportQueryBuilder()
             .Select('CampaignId').From('CAMPAIGN_PERFORMANCE_REPORT')
             .Where('CampaignStatus').EqualTo('ENABLED')
             .Build())
    file_format = 'CSV'
    post_body = urlencode({'__fmt': file_format,
                                                  '__rdquery': query})
    post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    report_data = u'CONTENT STRING 广告客户'
    report_contents = io.BytesIO()
    report_contents.write(bytes(report_data, 'utf-8'))
    report_contents.seek(0)
    fake_response = mock.Mock()
    fake_response.read.side_effect = report_contents.read
    fake_response.msg = 'fake message'
    fake_response.code = '200'

    with mock.patch.object(googleads.adwords, 'Request') as mock_request:
      mock_request_instance = mock.Mock()
      mock_request.return_value = mock_request_instance
      mock_request_instance.get_full_url.return_value = 'https://google.com/'
      mock_request_instance.headers = {}
      self.opener.open.return_value = fake_response
      self.report_downloader.DownloadReportWithAwql(
          query, file_format, output_file)

      mock_request.assert_called_once_with(
          ('https://adwords.google.com/api/adwords/reportdownload/%s'
           % self.version), post_body, headers)
      self.opener.open.assert_called_once_with(mock_request.return_value)

    self.assertEqual(report_data, output_file.getvalue())
    self.header_handler.GetReportDownloadHeaders.assert_called_once_with()

  def testExtractError_badRequest(self):
    response = mock.Mock()
    response.code = 400
    type_ = 'ReportDownloadError.INVALID_REPORT_DEFINITION_XML'
    trigger = 'Invalid enumeration.'
    field_path = 'Criteria.Type'
    error_template = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<reportDownloadError><ApiError><type>%s</type><trigger>%s</trigger>'
        '<fieldPath>%s</fieldPath></ApiError></reportDownloadError>')
    response_data = error_template % (type_, trigger, field_path)
    response_fp = io.BytesIO()
    response_fp.write(bytes(response_data, 'utf-8'))
    response_fp.seek(0)
    response.read.side_effect = response_fp.read

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(type_, rval.type)
    self.assertEqual(trigger, rval.trigger)
    self.assertEqual(field_path, rval.field_path)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(response_data, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportBadRequestError)

    # Check that if the XML fields are empty, this still functions.
    response_data = error_template % ('', '', '')
    response_fp = io.BytesIO()
    response_fp.write(bytes(response_data, 'utf-8'))
    response_fp.seek(0)
    response.read.side_effect = response_fp.read
    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(None, rval.type)
    self.assertEqual(None, rval.trigger)
    self.assertEqual(None, rval.field_path)

  def testExtractError_malformedBadRequest(self):
    response = mock.Mock()
    response.code = 400
    response_data = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<reportDownloadError><ApiError><type>1234</type>'
                     '<trigger>5678</trigger></ApiError></ExtraElement>'
                     '</reportDownloadError>')
    response_fp = io.BytesIO()
    response_fp.write(bytes(response_data, 'utf-8'))
    response_fp.seek(0)
    response.read.side_effect = response_fp.read

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(response_data, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportError)

  def testExtractError_notBadRequest(self):
    response = mock.Mock()
    response.code = 400
    content = 'Page not found!'
    response.read.return_value = (bytes(content, 'utf-8'))

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(content, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportError)

  def testSanitizeRequestHeaders(self):
    redacted_text = 'REDACTED'
    headers = {
        'foo': 'bar',
        'Developertoken': 'abc123doremi',
        'Authorization': 'Authorization',
        'lorem': 'ipsum'
    }

    sanitized_headers = self.report_downloader._SanitizeRequestHeaders(headers)

    self.assertNotEqual(headers, sanitized_headers)
    self.assertEqual(sanitized_headers['Developertoken'], redacted_text)
    self.assertEqual(sanitized_headers['Authorization'], redacted_text)

  def testExtractResponseHeaders(self):
    headers = '\n\n\nfoo: bar\nlorem: ipsum\ntomayto: tomahto\n'
    expected_headers = {
        'foo': 'bar',
        'lorem': 'ipsum',
        'tomayto': 'tomahto'
    }

    dict_headers = self.report_downloader._ExtractResponseHeaders(headers)

    self.assertEqual(dict_headers, expected_headers)


class QueryBuilderTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.adwords._QueryBuilder class."""

  def testSelect(self):
    with self.assertRaises(NotImplementedError):
      googleads.adwords._QueryBuilder().Select()

  def testFailUsingCopyConstructor(self):
    with self.assertRaises(googleads.errors.GoogleAdsValueError):
      (googleads.adwords
       ._QueryBuilder('SELECT Id FROM CAMPAIGN_PERFORMANCE_REPORT'))


class ReportQueryBuilderTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.adwords.ReportQueryBuilder class."""

  def testCopyConstructor(self):
    # Test using date range.
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' CAMPAIGN_PERFORMANCE_REPORT'
                     ' WHERE CampaignStatus = "ENABLED" DURING YESTERDAY')
    previous_query_builder = (googleads.adwords.ReportQueryBuilder()
                              .Select('CampaignId', 'CampaignName')
                              .From('CAMPAIGN_PERFORMANCE_REPORT')
                              .Where('CampaignStatus').EqualTo('ENABLED')
                              .During('YESTERDAY'))
    actual_query = (googleads.adwords.ReportQueryBuilder(previous_query_builder)
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

    # Test using start and end dates.
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' CAMPAIGN_PERFORMANCE_REPORT'
                     ' WHERE CampaignStatus = "ENABLED"'
                     ' DURING 20170101,20170131')
    previous_query_builder = (googleads.adwords.ReportQueryBuilder()
                              .Select('CampaignId', 'CampaignName')
                              .From('CAMPAIGN_PERFORMANCE_REPORT')
                              .Where('CampaignStatus').EqualTo('ENABLED')
                              .During(start_date='20170101',
                                      end_date='20170131'))
    actual_query = (googleads.adwords.ReportQueryBuilder(previous_query_builder)
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testFailUsingCopyConstructor(self):
    builder = googleads.adwords._QueryBuilder()
    builder.select = 'Id'
    with self.assertRaises(googleads.errors.GoogleAdsValueError):
      googleads.adwords.ReportQueryBuilder(builder)

  def testBuild(self):
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' CAMPAIGN_PERFORMANCE_REPORT')
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('CampaignId', 'CampaignName')
                    .From('CAMPAIGN_PERFORMANCE_REPORT')
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testBuild_stringWhereValue(self):
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' CAMPAIGN_PERFORMANCE_REPORT'
                     ' WHERE CampaignStatus = "ENABLED" DURING YESTERDAY')
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('CampaignId', 'CampaignName')
                    .From('CAMPAIGN_PERFORMANCE_REPORT')
                    .Where('CampaignStatus').EqualTo('ENABLED')
                    .During('YESTERDAY')
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testBuild_numericWhereValue(self):
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' ADGROUP_PERFORMANCE_REPORT'
                     ' WHERE AverageCpm >= 5.6 DURING TODAY')
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('CampaignId', 'CampaignName')
                    .From('ADGROUP_PERFORMANCE_REPORT')
                    .Where('AverageCpm').GreaterThanOrEqualTo(5.6)
                    .During('TODAY')
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testBuild_multipleStringWhereValues(self):
    expected_awql = ('SELECT Id, CampaignId, CampaignName FROM'
                     ' AD_PERFORMANCE_REPORT'
                     ' WHERE CampaignName CONTAINS_ALL ["white", "black"]'
                     ' DURING LAST_WEEK')
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('Id', 'CampaignId', 'CampaignName')
                    .From('AD_PERFORMANCE_REPORT')
                    .Where('CampaignName').ContainsAll('white', 'black')
                    .During('LAST_WEEK')
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testBuild_multipleNumericWhereValues(self):
    expected_awql = ('SELECT Id, CampaignId, CampaignName FROM'
                     ' AD_PERFORMANCE_REPORT'
                     ' WHERE CampaignId IN [1234, 5678] DURING LAST_WEEK')
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('Id', 'CampaignId', 'CampaignName')
                    .From('AD_PERFORMANCE_REPORT')
                    .Where('CampaignId').In(1234, 5678)
                    .During('LAST_WEEK')
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testBuild_multipleWhereConditions(self):
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' ADGROUP_PERFORMANCE_REPORT'
                     ' WHERE Clicks >= 500 AND CampaignName'
                     ' CONTAINS_IGNORE_CASE "promotion"'
                     ' AND AdGroupName STARTS_WITH "adwords_"'
                     ' AND BiddingStrategyName STARTS_WITH_IGNORE_CASE "europe"'
                     ' AND CustomerDescriptiveName CONTAINS "goog"'
                     ' AND CustomerDescriptiveName DOES_NOT_CONTAIN "asia"'
                     ' AND AccountDescriptiveName DOES_NOT_CONTAIN_IGNORE_CASE'
                     ' "group 3" AND CampaignStatus != "REMOVED"'
                     ' AND AdGroupStatus NOT_IN ["REMOVED", "PAUSED"]'
                     ' AND AdNetworkType1 CONTAINS_ANY ["SEARCH", "DISPLAY"]'
                     ' AND AdNetworkType2 CONTAINS_NONE'
                     ' ["YOUTUBE_SEARCH", "UNKNOWN"] AND AverageCpv > 20.7'
                     ' AND AllConversions < 100.6'
                     ' DURING 20170601,20170630')
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('CampaignId', 'CampaignName')
                    .From('ADGROUP_PERFORMANCE_REPORT')
                    .Where('Clicks').GreaterThanOrEqualTo(500)
                    .Where('CampaignName').ContainsIgnoreCase('promotion')
                    .Where('AdGroupName').StartsWith('adwords_')
                    .Where('BiddingStrategyName').StartsWithIgnoreCase('europe')
                    .Where('CustomerDescriptiveName').Contains('goog')
                    .Where('CustomerDescriptiveName').DoesNotContain('asia')
                    .Where('AccountDescriptiveName').DoesNotContainIgnoreCase(
                        'group 3')
                    .Where('CampaignStatus').NotEqualTo('REMOVED')
                    .Where('AdGroupStatus').NotIn('REMOVED', 'PAUSED')
                    .Where('AdNetworkType1').ContainsAny('SEARCH', 'DISPLAY')
                    .Where('AdNetworkType2').ContainsNone('YOUTUBE_SEARCH',
                                                          'UNKNOWN')
                    .Where('AverageCpv').GreaterThan(20.7)
                    .Where('AllConversions').LessThan(100.6)
                    .During(start_date='20170601', end_date='20170630')
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testBuild_noWhereClause(self):
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' ADGROUP_PERFORMANCE_REPORT DURING TODAY')
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('CampaignId', 'CampaignName')
                    .From('ADGROUP_PERFORMANCE_REPORT')
                    .During('TODAY')
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testBuild_noDuringClause(self):
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' ADGROUP_PERFORMANCE_REPORT'
                     ' WHERE Clicks <= 500')
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('CampaignId', 'CampaignName')
                    .From('ADGROUP_PERFORMANCE_REPORT')
                    .Where('Clicks').LessThanOrEqualTo(500)
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testBuild_selectIsNone(self):
    with self.assertRaises(ValueError):
      googleads.adwords.ReportQueryBuilder().Build()

  def testBuild_fromIsNone(self):
    with self.assertRaises(ValueError):
      googleads.adwords.ReportQueryBuilder().Select('Id').Build()

  def testDuring_usingPythonDateTime(self):
    expected_awql = ('SELECT CampaignId, CampaignName FROM'
                     ' CAMPAIGN_PERFORMANCE_REPORT'
                     ' WHERE CampaignStatus = "ENABLED"'
                     ' DURING 20170501,20170531')
    start_date = datetime.date(2017, 5, 1)
    end_date = start_date + datetime.timedelta(days=30)
    actual_query = (googleads.adwords.ReportQueryBuilder()
                    .Select('CampaignId', 'CampaignName')
                    .From('CAMPAIGN_PERFORMANCE_REPORT')
                    .Where('CampaignStatus').EqualTo('ENABLED')
                    .During(start_date=start_date, end_date=end_date)
                    .Build())
    self.assertEqual(expected_awql, str(actual_query))

  def testDuring_allParametersNone(self):
    with self.assertRaises(ValueError):
      googleads.adwords.ReportQueryBuilder().During()

  def testDuring_allParametersNotNone(self):
    with self.assertRaises(ValueError):
      googleads.adwords.ReportQueryBuilder().During('TODAY', '20170101',
                                                    '20170131')

  def testDuring_startOrEndDateNone(self):
    with self.assertRaises(ValueError):
      googleads.adwords.ReportQueryBuilder().During(start_date='20170101')
    with self.assertRaises(ValueError):
      googleads.adwords.ReportQueryBuilder().During(end_date='20170131')


class ServiceQueryBuilderTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.adwords.ServiceQueryBuilder class."""

  def testCopyConstructor(self):
    awql_regex = (r'SELECT (.*) WHERE Status = "ENABLED"'
                  r' ORDER BY Name ASC LIMIT 0,100')
    selected_fields = ['Id', 'Name']
    previous_query_builder = (googleads.adwords.ServiceQueryBuilder()
                              .Select(*selected_fields)
                              .Where('Status').EqualTo('ENABLED')
                              .OrderBy('Name')
                              .Limit(0, 100))

    actual_query = googleads.adwords.ServiceQueryBuilder(
        previous_query_builder).Build()
    match = re.match(awql_regex, str(actual_query))

    # The SELECT clause can show fields listed in any orders.
    self.assertCountEqual(selected_fields,
      [field.strip() for field in match.group(1).split(',')])
    self.assertRegexpMatches(str(actual_query), awql_regex)

  def testFailUsingCopyConstructor(self):
    builder = googleads.adwords._QueryBuilder()
    builder.select = 'Id'
    with self.assertRaises(googleads.errors.GoogleAdsValueError):
      googleads.adwords.ServiceQueryBuilder(builder)

  def testBuild(self):
    awql_regex = (r'SELECT (.*) LIMIT 0,100')
    selected_fields = ['Id', 'Name']
    actual_query = (googleads.adwords.ServiceQueryBuilder()
                    .Select(*selected_fields)
                    .Limit(0, 100)
                    .Build())
    match = re.match(awql_regex, str(actual_query))

    # The SELECT clause can show fields listed in any orders.
    self.assertCountEqual(selected_fields,
      [field.strip() for field in match.group(1).split(',')])
    self.assertRegexpMatches(str(actual_query), awql_regex)

  def testBuild_duplicateSelectedFieldsRetainOnlyUnique(self):
    awql_regex = (r'SELECT (.*) LIMIT 0,100')
    selected_fields = ['Id', 'Name', 'Name']
    actual_query = (googleads.adwords.ServiceQueryBuilder()
                    .Select(*selected_fields)
                    .Limit(0, 100)
                    .Build())
    match = re.match(awql_regex, str(actual_query))

    # The SELECT clause retains only unique fields.
    self.assertCountEqual(set(selected_fields),
      [field.strip() for field in match.group(1).split(',')])
    self.assertRegexpMatches(str(actual_query), awql_regex)

  def testBuild_whereConditions(self):
    awql_regex = (r'SELECT (.*)'
                  r' WHERE Name CONTAINS_IGNORE_CASE "promotion"'
                  r' AND Status NOT_IN \["REMOVED", "PAUSED"\]'
                  r' ORDER BY Name ASC'
                  r' LIMIT 100,100')
    selected_fields = ['Id', 'Name', 'Status']
    actual_query = (googleads.adwords.ServiceQueryBuilder()
                    .Select(*selected_fields)
                    .Where('Name').ContainsIgnoreCase('promotion')
                    .Where('Status').NotIn('REMOVED', 'PAUSED')
                    .OrderBy('Name')
                    .Limit(100, 100)
                    .Build())
    match = re.match(awql_regex, str(actual_query))

    # The SELECT clause can show fields listed in any orders.
    self.assertCountEqual(selected_fields,
      [field.strip() for field in match.group(1).split(',')])
    self.assertRegexpMatches(str(actual_query), awql_regex)

  def testBuild_orderByDesc(self):
    awql_regex = (r'SELECT (.*)'
                  r' ORDER BY Name DESC'
                  r' LIMIT 100,100')
    selected_fields = ['Id', 'Name', 'Status']
    actual_query = (googleads.adwords.ServiceQueryBuilder()
                    .Select(*selected_fields)
                    .OrderBy('Name', ascending=False)
                    .Limit(100, 100)
                    .Build())
    match = re.match(awql_regex, str(actual_query))

    # The SELECT clause can show fields listed in any orders.
    self.assertCountEqual(selected_fields,
      [field.strip() for field in match.group(1).split(',')])
    self.assertRegexpMatches(str(actual_query), awql_regex)

  def testBuild_selectIsNone(self):
    with self.assertRaises(ValueError):
      googleads.adwords.ServiceQueryBuilder().Build()

  def testBuild_limitStartIndexOrPageSizeIsNoneButNotTheOther(self):
    # A page size is not specified.
    with self.assertRaises(ValueError):
      (googleads.adwords.ServiceQueryBuilder()
       .Select('Id')
       .OrderBy('Name', ascending=False)
       .Limit(100, None)
       .Build())
    # A start index is not specified.
    with self.assertRaises(ValueError):
      (googleads.adwords.ServiceQueryBuilder()
       .Select('Id')
       .OrderBy('Name', ascending=False)
       .Limit(None, 100)
       .Build())


class ServiceQueryTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.adwords.ServiceQuery class."""

  def testNextPage(self):
    selected_fields = ['Id', 'Name']
    actual_query = (googleads.adwords.ServiceQueryBuilder()
                    .Select(*selected_fields)
                    .Limit(0, 100)
                    .Build())
    # Do next page and check if the LIMIT clause is modified correctly.
    awql_regex = (r'SELECT (.*) LIMIT 100,100')
    actual_query.NextPage()
    self.assertRegexpMatches(str(actual_query), awql_regex)

  def testNextPageForDataService(self):
    selected_fields = ['Id', 'Name']
    actual_query = (
        googleads.adwords.ServiceQueryBuilder().Select(*selected_fields).Limit(
            0, 2).Build())
    page = {
        'totalNumEntries': 3,
        'Page.Type': 'CriterionBidLandscapePage',
        'entries': [{
            'landscapePoints': ['fakePoint1', 'fakePoint2']
        }, {
            'landscapePoints': ['fakePoint3', 'fakePoint4']
        }]
    }

    # The LIMIT clause should be incremented by the number of bid landscape
    # points of the page.
    awql_regex = (r'SELECT (.*) LIMIT 4,2')
    actual_query.NextPage(page)
    self.assertRegexpMatches(str(actual_query), awql_regex)

  def testNextPageFail(self):
    actual_query = googleads.adwords.ServiceQuery('SELECT Id, Name', None, 100)

    with self.assertRaises(ValueError):
      actual_query.NextPage()

  def testHasNext(self):
    selected_fields = ['Id', 'Name']
    actual_query = (googleads.adwords.ServiceQueryBuilder()
                    .Select(*selected_fields)
                    .Limit(0, 1)
                    .Build())
    awql_regex = (r'SELECT (.*) LIMIT 0,1')
    self.assertRegexpMatches(str(actual_query), awql_regex)

    page = {'totalNumEntries': 3}

    self.assertTrue(actual_query.HasNext(page))
    awql_regex = (r'SELECT (.*) LIMIT 1,1')
    actual_query.NextPage()
    self.assertRegexpMatches(str(actual_query), awql_regex)

    self.assertTrue(actual_query.HasNext(page))
    awql_regex = (r'SELECT (.*) LIMIT 2,1')
    actual_query.NextPage()
    self.assertRegexpMatches(str(actual_query), awql_regex)

    self.assertFalse(actual_query.HasNext(page))

  def testHasNextForDataService(self):
    page = {
        'totalNumEntries': 3,
        'Page.Type': 'AdGroupBidLandscapePage',
        'entries': [{
            'landscapePoints': ['fakePoint1', 'fakePoint2']
        }, {
            'landscapePoints': ['fakePoint3', 'fakePoint4']
        }]
    }
    selected_fields = ['Id', 'Name']
    page_size = 2
    actual_query = (
        googleads.adwords.ServiceQueryBuilder().Select(*selected_fields).Limit(
            0, page_size).Build())
    # 2 * 2 landscape points are greater than page_size.
    self.assertTrue(actual_query.HasNext(page))

    page_size = 10
    actual_query = (
        googleads.adwords.ServiceQueryBuilder().Select(*selected_fields).Limit(
            0, page_size).Build())
    # 2 * 2 landscape points are less than page_size.
    self.assertFalse(actual_query.HasNext(page))

  def testHasNextFail(self):
    actual_query = googleads.adwords.ServiceQuery('SELECT Id, Name', None, 100)

    page = {'totalNumEntries': 10}
    with self.assertRaises(ValueError):
      actual_query.HasNext(page)

  def testPager(self):
    fake_page = {'totalNumEntries': 3}
    service = mock.Mock()
    service.query.return_value = fake_page

    query = (googleads.adwords.ServiceQueryBuilder()
             .Select('Id', 'Name')
             .Limit(0, 1)
             .Build())
    i = 0
    for page in query.Pager(service):
      self.assertEqual(fake_page['totalNumEntries'],
                       page['totalNumEntries'])
      i += 1
    # Pager should return the number of page equal to the 'totalNumEntries'
    # returned by a service.
    self.assertEqual(fake_page['totalNumEntries'], i)


if __name__ == '__main__':
  unittest.main()
