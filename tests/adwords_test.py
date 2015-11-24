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

import io
import os
import sys
import tempfile
import unittest
import urllib
import urllib2
from xml.etree import ElementTree


import googleads.adwords
import googleads.common
import googleads.errors
import mock


PYTHON2 = sys.version_info[0] == 2
URL_REQUEST_PATH = ('urllib2' if PYTHON2 else 'urllib.request')
CURRENT_VERSION = sorted(googleads.adwords._SERVICE_MAP.keys())[-1]


def GetAdWordsClient():
  """Returns an initialized AdwordsClient for use in testing."""
  oauth_header = {'Authorization': 'header'}
  client_customer_id = 'client customer id'
  dev_token = 'N3v3rG0nN4Giv3Y0uUp'
  user_agent = 'N3v3rG0nN4l37y0uDoWN'
  oauth2_client = mock.Mock()
  oauth2_client.CreateHttpHeader.return_value = dict(oauth_header)
  client = googleads.adwords.AdWordsClient(
      dev_token, oauth2_client, user_agent,
      client_customer_id=client_customer_id)
  return client


class AdWordsHeaderHandlerTest(unittest.TestCase):
  """Tests for the googleads.adwords._AdWordsHeaderHandler class."""

  def setUp(self):
    self.adwords_client = mock.Mock()
    self.header_handler = googleads.adwords._AdWordsHeaderHandler(
        self.adwords_client, CURRENT_VERSION)

  def testSetHeaders(self):
    suds_client = mock.Mock()
    ccid = 'client customer id'
    dev_token = 'developer token'
    user_agent = 'user agent!'
    validate_only = True
    partial_failure = False
    oauth_header = {'oauth': 'header'}
    self.adwords_client.client_customer_id = ccid
    self.adwords_client.developer_token = dev_token
    self.adwords_client.user_agent = user_agent
    self.adwords_client.validate_only = validate_only
    self.adwords_client.partial_failure = partial_failure
    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = (
        oauth_header)

    self.header_handler.SetHeaders(suds_client)

    # Check that the SOAP header has the correct values.
    suds_client.factory.create.assert_called_once_with(
        '{https://adwords.google.com/api/adwords/cm/%s}SoapHeader' %
        CURRENT_VERSION)
    soap_header = suds_client.factory.create.return_value
    self.assertEqual(ccid, soap_header.clientCustomerId)
    self.assertEqual(dev_token, soap_header.developerToken)
    self.assertEqual(
        ''.join([user_agent, googleads.adwords._AdWordsHeaderHandler._LIB_SIG]),
        soap_header.userAgent)
    self.assertEqual(validate_only, soap_header.validateOnly)
    self.assertEqual(partial_failure, soap_header.partialFailure)

    # Check that the suds client has the correct values.
    suds_client.set_options.assert_any_call(
        soapheaders=soap_header, headers=oauth_header)

  def testGetReportDownloadHeaders(self):
    ccid = 'client customer id'
    dev_token = 'developer token'
    user_agent = 'user agent!'
    oauth_header = {'Authorization': 'header'}
    self.adwords_client.client_customer_id = ccid
    self.adwords_client.developer_token = dev_token
    self.adwords_client.user_agent = user_agent
    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = dict(
        oauth_header)
    expected_return_value = {
        'Content-type': 'application/x-www-form-urlencoded',
        'developerToken': dev_token,
        'clientCustomerId': ccid,
        'Authorization': 'header',
        'User-Agent': ''.join([
            user_agent, googleads.adwords._AdWordsHeaderHandler._LIB_SIG,
            ',gzip']),
        'skipReportHeader': 'False',
        'skipColumnHeader': 'False',
        'skipReportSummary': 'False'
    }

    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = dict(
        oauth_header)
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders(
                         {'skip_report_header': False,
                          'skip_column_header': False,
                          'skip_report_summary': False}))

  def testGetReportDownloadHeadersWithInvalidKeyword(self):
    ccid = 'client customer id'
    dev_token = 'developer token'
    user_agent = 'user agent!'
    self.adwords_client.client_customer_id = ccid
    self.adwords_client.developer_token = dev_token
    self.adwords_client.user_agent = user_agent

    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        self.header_handler.GetReportDownloadHeaders,
        {'invalid_key_word': True})

  def testGetReportDownloadHeadersWithOptionalHeaders(self):
    ccid = 'client customer id'
    dev_token = 'developer token'
    user_agent = 'user agent!'
    oauth_header = {'Authorization': 'header'}
    self.adwords_client.client_customer_id = ccid
    self.adwords_client.developer_token = dev_token
    self.adwords_client.user_agent = user_agent
    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = dict(
        oauth_header)
    expected_return_value = {
        'Content-type': 'application/x-www-form-urlencoded',
        'developerToken': dev_token,
        'clientCustomerId': ccid,
        'Authorization': 'header',
        'User-Agent': ''.join([
            user_agent, googleads.adwords._AdWordsHeaderHandler._LIB_SIG,
            ',gzip']),
        'skipReportHeader': 'True',
        'skipColumnHeader': 'True',
        'skipReportSummary': 'True',
        'includeZeroImpressions': 'True'
    }

    self.adwords_client.oauth2_client.CreateHttpHeader.return_value = dict(
        oauth_header)
    self.assertEqual(expected_return_value,
                     self.header_handler.GetReportDownloadHeaders(
                         {'skip_report_header': True,
                          'skip_column_header': True,
                          'skip_report_summary': True,
                          'include_zero_impressions': True}))


class AdWordsClientTest(unittest.TestCase):
  """Tests for the googleads.adwords.AdWordsClient class."""

  def setUp(self):
    self.https_proxy = 'myproxy:443'
    self.cache = None
    self.adwords_client = GetAdWordsClient()
    self.adwords_client.https_proxy = self.https_proxy
    self.header_handler = googleads.adwords._AdWordsHeaderHandler(
        self.adwords_client, CURRENT_VERSION)

  def testLoadFromStorage(self):
    with mock.patch('googleads.common.LoadFromStorage') as mock_load:
      mock_load.return_value = {
          'developer_token': 'abcdEFghIjkLMOpqRs',
          'oauth2_client': mock.Mock(),
          'user_agent': 'unit testing'
      }
      self.assertIsInstance(googleads.adwords.AdWordsClient.LoadFromStorage(),
                            googleads.adwords.AdWordsClient)

  def testGetService_success(self):
    version = CURRENT_VERSION
    service = googleads.adwords._SERVICE_MAP[version].keys()[0]
    namespace = googleads.adwords._SERVICE_MAP[version][service]

    # Use a custom server. Also test what happens if the server ends with a
    # trailing slash
    server = 'https://testing.test.com/'
    https_proxy = {'https': self.https_proxy}
    with mock.patch('suds.client.Client') as mock_client:
      suds_service = self.adwords_client.GetService(service, version, server)

      mock_client.assert_called_once_with(
          'https://testing.test.com/api/adwords/%s/%s/%s?wsdl'
          % (namespace, version, service), proxy=https_proxy, cache=self.cache,
          timeout=3600)
      self.assertIsInstance(suds_service, googleads.common.SudsServiceProxy)

    # Use the default server and https_proxy.
    self.adwords_client.https_proxy = None
    with mock.patch('suds.client.Client') as mock_client:
      suds_service = self.adwords_client.GetService(service, version)

      mock_client.assert_called_once_with(
          'https://adwords.google.com/api/adwords/%s/%s/%s?wsdl'
          % (namespace, version, service), proxy=None, cache=self.cache,
          timeout=3600)
      self.assertFalse(mock_client.return_value.set_options.called)
      self.assertIsInstance(suds_service, googleads.common.SudsServiceProxy)

  def testGetService_badService(self):
    version = CURRENT_VERSION
    self.assertRaises(
        googleads.errors.GoogleAdsValueError, self.adwords_client.GetService,
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
    suds_client = mock.Mock()
    ccid = 'modified'
    # Check that the SOAP header has the modified client customer id.
    self.adwords_client.SetClientCustomerId(ccid)
    self.header_handler.SetHeaders(suds_client)
    soap_header = suds_client.factory.create.return_value
    self.assertEqual(ccid, soap_header.clientCustomerId)


class BatchJobHelperTest(unittest.TestCase):

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
                    '_SudsUploadRequestBuilder.'
                    'BuildUploadRequest') as mock_build_request:
      mock_request = mock.MagicMock()
      mock_build_request.return_value = mock_request
      with mock.patch('urllib2.urlopen') as mock_urlopen:
        self.batch_job_helper.UploadOperations([[]])
        mock_urlopen.assert_called_with(mock_request)


class BatchJobUploadRequestBuilderTest(unittest.TestCase):

  """Test suite for the BatchJobUploadRequestBuilder."""

  ENVELOPE_NS = 'http://schemas.xmlsoap.org/soap/envelope/'

  def setUp(self):
    """Prepare tests."""
    self.client = GetAdWordsClient()
    self.request_builder = self.client.GetBatchJobHelper()._request_builder
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
    self.single_upload_headers = {'Content-type': 'application/xml'}
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
        test_dir, 'data/batch_job_util_invalid_request.txt')) as handler:
      cls.INVALID_API_REQUEST = handler.read()
    with open(os.path.join(
        test_dir, 'data/batch_job_util_not_request.txt')) as handler:
      cls.NOT_API_REQUEST = handler.read()
    with open(os.path.join(
        test_dir, 'data/batch_job_util_raw_request_template.txt')) as handler:
      cls.RAW_API_REQUEST_TEMPLATE = handler.read()
    with open(os.path.join(
        test_dir, 'data/batch_job_util_raw_operation_template.txt')) as handler:
      cls.RAW_OPERATION_TEMPLATE = handler.read()
    with open(os.path.join(
        test_dir, 'data/batch_job_util_upload_template.txt')) as handler:
      cls.UPLOAD_OPERATIONS_TEMPLATE = handler.read()

  def GenerateBudgetOperations(self, operations):
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
            'name': 'Batch budget #%s' % i,
            'period': 'DAILY',
            'amount': {'microAmount': str(3333333 * i)},
            'deliveryMethod': 'STANDARD'}
    } for i in range(1, operations + 1)]

  def GenerateCampaignCriterionOperations(self, operations):
    """Generates request containing given number of CampaignCriterionOperations.

    Args:
      operations: a positive int defining the number of
      CampaignCriterionOperations to be generated.
    Returns:
      A list of dictionaries containing distinct CampaignCriterionOperations.
    """
    return [{
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
    } for i in range(1, operations + 1)]

  def GenerateValidRequest(self, operations):
    """Generates a valid API request containing the given number of operations.

    Args:
      operations: a positive int defining the number of BudgetOperations to be
        generated.

    Returns:
      A tuple containing the operations used to construct str containing a valid
      API request.
    """
    ops = self.GenerateBudgetOperations(operations)
    ops_xml = ''.join([self.RAW_OPERATION_TEMPLATE % (
        op['operator'], op['xsi_type'], op['operand']['budgetId'],
        op['operand']['name'], op['operand']['period'],
        op['operand']['amount']['microAmount'],
        op['operand']['deliveryMethod']
    ) for op in ops])
    request = self.RAW_API_REQUEST_TEMPLATE % (ops_xml)
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
    ops_xml = ''.join([self.RAW_OPERATION_TEMPLATE.decode('utf-8') % (
        op[u'operator'], op[u'xsi_type'], op[u'operand'][u'budgetId'],
        op[u'operand'][u'name'], op[u'operand'][u'period'],
        op[u'operand'][u'amount'][u'microAmount'],
        op[u'operand'][u'deliveryMethod']
    ) for op in ops])
    request = self.RAW_API_REQUEST_TEMPLATE.decode('utf-8') % (ops_xml)
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
        u'operator': u'ADD',
        u'xsi_type': u'BudgetOperation',
        u'operand': {
            u'budgetId': str(i).decode('utf-8'),
            u'name': u'アングリーバード Batch budget #%s' % i,
            u'period': u'DAILY',
            u'amount': {u'microAmount': str(3333333 * i).decode('utf-8')},
            u'deliveryMethod': u'STANDARD'}
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
    operations = self.GenerateCampaignCriterionOperations(1)
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
    ops = self.GenerateCampaignCriterionOperations(operations_amount)
    root = ElementTree.fromstring(self.request_builder._GenerateRawRequestXML(
        ops))
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
    operations = self.GenerateCampaignCriterionOperations(1)
    del operations[0]['xsi_type']
    self.assertRaises(
        googleads.errors.AdWordsBatchJobServiceInvalidOperationError,
        self.request_builder._GenerateOperationsXML, operations)

  def testGenerateOperationsXMLWithNoOperations(self):
    """Tests whether _GenerateOperationsXML produces empty str if no operations.
    """
    operations = self.GenerateCampaignCriterionOperations(0)
    raw_xml = self.request_builder._GenerateOperationsXML(
        operations)
    self.assertTrue(raw_xml is '')

  def testGenerateRawRequestXMLFromSingleOperation(self):
    """Tests whether raw request xml can be produced from a single operation."""
    operations_amount = 1
    ops = self.GenerateBudgetOperations(operations_amount)

    root = ElementTree.fromstring(
        self.request_builder._GenerateRawRequestXML(ops))
    self.assertTrue(len(root) == 2)
    body = root.find('{%s}Body' % self.ENVELOPE_NS)
    self.assertTrue(len(body) == 1)
    mutate = body.find('{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(operations.tag, '{%s}operations' %
                       self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations._children) == len(ops[i].keys()))
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
      self.assertTrue(len(operand._children) == len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      self.assertEqual(
          operand.find(
              '{%s}period' %
              self.request_builder._adwords_endpoint).text,
          ops[i]['operand']['period'])
      amount = operand.find('{%s}amount' %
                            self.request_builder._adwords_endpoint)
      self.assertTrue(len(amount._children) ==
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
    ops = self.GenerateBudgetOperations(operations_amount)

    root = ElementTree.fromstring(
        self.request_builder._GenerateRawRequestXML(ops))
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
      self.assertTrue(len(operations._children) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operand._children) == len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      self.assertEqual(operand.find(
          '{%s}period' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['period'])
      amount = operand.find(
          '{%s}amount' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(amount._children) ==
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

    root = ElementTree.fromstring(
        self.request_builder._GenerateRawRequestXML(ops))
    self.assertTrue(len(root) == 2)
    body = root.find(u'{%s}Body' % self.ENVELOPE_NS)
    self.assertTrue(len(body) == 1)
    mutate = body.find(u'{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(operations.tag, '{%s}operations' %
                       self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations._children) == len(ops[i].keys()))
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
      self.assertTrue(len(operand._children) == len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      self.assertEqual(
          operand.find(
              '{%s}period' %
              self.request_builder._adwords_endpoint).text,
          ops[i]['operand']['period'])
      amount = operand.find('{%s}amount' %
                            self.request_builder._adwords_endpoint)
      self.assertTrue(len(amount._children) ==
                      len(ops[i]['operand']['amount'].keys()))
      self.assertEqual(amount.find(
          '{%s}microAmount' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['amount']['microAmount'])
      self.assertEqual(operand.find(
          '{%s}deliveryMethod' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['deliveryMethod'])

  def testGetRawOperationsFromValidSingleOperationRequest(self):
    """Test whether operations XML can be retrieved for a single-op request.

    Also verifies that the contents of generated XML are correct.
    """
    operations_amount = 1
    ops, request = self.GenerateValidRequest(operations_amount)

    mutate = self.request_builder._GetRawOperationsFromXML(request)
    self.assertEqual(mutate.tag,
                     '{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate._children) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(
          operations.tag,
          '{%s}operations' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations._children) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operand._children) == len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      self.assertEqual(operand.find(
          '{%s}period' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['period'])
      amount = operand.find(
          '{%s}amount' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(amount._children) ==
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
    ops, request = self.GenerateValidRequest(operations_amount)

    mutate = self.request_builder._GetRawOperationsFromXML(request)
    self.assertEqual(
        mutate.tag,
        '{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate._children) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(
          operations.tag,
          '{%s}operations' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations._children) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = (operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint))
      self.assertTrue(len(operand._children) == len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      self.assertEqual(operand.find(
          '{%s}period' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['period'])
      amount = (operand.find(
          '{%s}amount' % self.request_builder._adwords_endpoint))
      self.assertTrue(len(amount._children) ==
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
    self.assertTrue(len(mutate._children) == operations_amount)

    for i in range(0, operations_amount):
      operations = mutate[i]
      self.assertEqual(
          operations.tag,
          '{%s}operations' % self.request_builder._adwords_endpoint)
      self.assertTrue(len(operations._children) == len(ops[i].keys()))
      self.assertEqual(operations.find(
          '{%s}operator' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operator'])
      self.assertEqual(operations.find(
          '{%s}Operation.Type' % self.request_builder._adwords_endpoint).text,
                       ops[i]['xsi_type'])
      operand = (operations.find(
          '{%s}operand' % self.request_builder._adwords_endpoint))
      self.assertTrue(len(operand._children) == len(ops[i]['operand'].keys()))
      self.assertEqual(operand.find(
          '{%s}budgetId' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['budgetId'])
      self.assertEqual(operand.find(
          '{%s}name' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['name'])
      self.assertEqual(operand.find(
          '{%s}period' % self.request_builder._adwords_endpoint).text,
                       ops[i]['operand']['period'])
      amount = (operand.find(
          '{%s}amount' % self.request_builder._adwords_endpoint))
      self.assertTrue(len(amount._children) ==
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
    _, request = self.GenerateValidRequest(operations_amount)

    mutate = self.request_builder._GetRawOperationsFromXML(request)
    self.assertEqual(
        mutate.tag,
        '{%s}mutate' % self.request_builder._adwords_endpoint)
    self.assertTrue(len(mutate._children) == operations_amount)

  def testGetRawOperationsFromInvalidRequest(self):
    """Test whether an invalid API request raises an Exception."""
    self.assertRaises(AttributeError,
                      self.request_builder._GetRawOperationsFromXML,
                      self.INVALID_API_REQUEST)

  def testGetRawOperationsFromNotXMLRequest(self):
    """Test whether non-XML input raises an Exception."""
    self.assertRaises(ElementTree.ParseError,
                      self.request_builder._GetRawOperationsFromXML,
                      self.NOT_API_REQUEST)

  def testBuildRequestForSingleUpload(self):
    """Test whether a single upload request is build correctly."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_SudsUploadRequestBuilder.'
                    '_BuildUploadRequestBody') as mock_request_body_builder:
      mock_request_body_builder.return_value = self.sample_xml
      req = self.request_builder.BuildUploadRequest(self.upload_url, [[]])
      self.assertEqual(req.headers, self.single_upload_headers)
      self.assertEqual(req.get_method(), 'POST')

  def testBuildRequestForIncrementalUpload(self):
    """Test whether an incremental upload request is built correctly."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_SudsUploadRequestBuilder.'
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
                    '_SudsUploadRequestBuilder.'
                    '_GenerateOperationsXML') as mock_generate_xml:
      mock_generate_xml.return_value = self.sample_xml
      with mock.patch('googleads.adwords.BatchJobHelper._'
                      'SudsUploadRequestBuilder.'
                      '_GetPaddingLength') as mock_get_padding_length:
        mock_get_padding_length.return_value = 0
        increment = self.request_builder._BuildUploadRequestBody([[]])
        self.assertTrue(increment == self.request_body_complete)

  def testBuildUploadRequestBodyWithSuffix(self):
    """Test whether a request body is built correctly with only the suffix."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_SudsUploadRequestBuilder.'
                    '_GenerateOperationsXML') as mock_generate_xml:
      mock_generate_xml.return_value = self.sample_xml
      with mock.patch('googleads.adwords.BatchJobHelper.'
                      '_SudsUploadRequestBuilder.'
                      '_GetPaddingLength') as mock_get_padding_length:
        mock_get_padding_length.return_value = 0
        increment = self.request_builder._BuildUploadRequestBody(
            [[]], has_prefix=False)
        self.assertTrue(increment == self.request_body_end)

  def testBuildUploadRequestBodyWithoutPrefixOrSuffix(self):
    """Test whether a request body is built correctly without prefix/suffix."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_SudsUploadRequestBuilder.'
                    '_GenerateOperationsXML') as mock_generate_xml:
      mock_generate_xml.return_value = self.sample_xml
      with mock.patch('googleads.adwords.BatchJobHelper.'
                      '_SudsUploadRequestBuilder.'
                      '_GetPaddingLength') as mock_get_padding_length:
        mock_get_padding_length.return_value = 0
        increment = self.request_builder._BuildUploadRequestBody(
            [[]], has_prefix=False, has_suffix=False)
        self.assertTrue(increment == self.sample_xml)

  def testBuildUploadRequestBodyWithOnlyPrefix(self):
    """Test whether a request body is built correctly with only the prefix."""
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_SudsUploadRequestBuilder.'
                    '_GenerateOperationsXML') as mock_generate_xml:
      mock_generate_xml.return_value = self.sample_xml
      with mock.patch('googleads.adwords.BatchJobHelper.'
                      '_SudsUploadRequestBuilder.'
                      '_GetPaddingLength') as mock_get_padding_length:
        mock_get_padding_length.return_value = 0
        increment = self.request_builder._BuildUploadRequestBody(
            [[]], has_suffix=False)
        self.assertTrue(increment == self.request_body_start)


class IncrementalUploadHelperTest(unittest.TestCase):

  """Test suite for the IncrementalUploadHelper."""

  def setUp(self):
    """Prepare tests."""
    self.client = GetAdWordsClient()
    self.batch_job_helper = self.client.GetBatchJobHelper()
    self.incremental_uploader = (
        self.batch_job_helper.GetIncrementalUploadHelper(
            'https://goo.gl/Xtaq83'))

  def testUploadOperations(self):
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_SudsUploadRequestBuilder.'
                    'BuildUploadRequest') as mock_build_request:
      mock_request = mock.MagicMock()
      mock_build_request.return_value = mock_request
      with mock.patch('urllib2.urlopen') as mock_urlopen:
        self.incremental_uploader.UploadOperations([[]], True)
        mock_urlopen.assert_called_with(mock_request)

  def testUploadOperationsAfterFinished(self):
    with mock.patch('googleads.adwords.BatchJobHelper.'
                    '_SudsUploadRequestBuilder.'
                    'BuildUploadRequest') as mock_build_request:
      mock_request = mock.MagicMock()
      mock_build_request.return_value = mock_request
      with mock.patch('urllib2.urlopen'):
        self.incremental_uploader.UploadOperations([[]], True)
        self.assertRaises(
            googleads.errors.AdWordsBatchJobServiceInvalidOperationError,
            self.incremental_uploader.UploadOperations, {})


class ResponseParserTest(unittest.TestCase):
  """Test suite for the ResponseParser."""

  def setUp(self):
    """Prepare tests."""
    self.client = GetAdWordsClient()
    self.response_parser = googleads.adwords.BatchJobHelper.GetResponseParser()

  @classmethod
  def setUpClass(cls):
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(
        test_dir, 'data/batch_job_util_response_template.txt')) as handler:
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
    period = 'DAILY'
    micro_amount = '50000000'
    delivery_method = 'STANDARD'
    is_explicitly_shared = 'true'
    bidding_strategy_type = 'MANUAL_CPC'

    response = (
        self.response_parser.ParseResponse(
            self.API_RESPONSE_XML_TEMPLATE %
            (campaign_id, name, status,
             serving_status, start_date,
             end_date, budget_id,
             budget_name, period,
             micro_amount, delivery_method,
             is_explicitly_shared,
             bidding_strategy_type))
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
    period = u'DAILY'
    micro_amount = u'50000000'
    delivery_method = u'STANDARD'
    is_explicitly_shared = u'true'
    bidding_strategy_type = u'MANUAL_CPC'

    response = (
        self.response_parser.ParseResponse(
            self.API_RESPONSE_XML_TEMPLATE %
            (campaign_id, name, status,
             serving_status, start_date,
             end_date, budget_id,
             budget_name, period,
             micro_amount, delivery_method,
             is_explicitly_shared,
             bidding_strategy_type))
        ['mutateResponse']['rval'])

    self.assertTrue(len(response) == 2)
    campaign = response[1]['result']['Campaign']
    self.assertTrue(campaign['name'] == name)


class ReportDownloaderTest(unittest.TestCase):
  """Tests for the googleads.adwords.ReportDownloader class."""

  def setUp(self):
    self.version = CURRENT_VERSION
    self.marshaller = mock.Mock()
    self.header_handler = mock.Mock()
    self.adwords_client = mock.Mock()
    self.opener = mock.Mock()
    self.adwords_client.https_proxy = 'my.proxy.gov:443'
    with mock.patch('suds.client.Client'):
      with mock.patch('suds.xsd.doctor'):
        with mock.patch('suds.mx.literal.Literal') as mock_literal:
          with mock.patch(
              'googleads.adwords._AdWordsHeaderHandler') as mock_handler:
            with mock.patch(
                URL_REQUEST_PATH + '.OpenerDirector') as mock_opener:
              mock_literal.return_value = self.marshaller
              mock_handler.return_value = self.header_handler
              mock_opener.return_value = self.opener
              self.report_downloader = googleads.adwords.ReportDownloader(
                  self.adwords_client, self.version)

  def testDownloadReport(self):
    output_file = io.StringIO()
    report_definition = {'table': 'campaigns',
                         'downloadFormat': 'CSV'}
    serialized_report = 'nuinbwuign'
    post_body = urllib.urlencode({'__rdxml': serialized_report})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'CONTENT STRING 广告客户'
    fake_request = io.StringIO() if PYTHON2 else io.BytesIO()
    fake_request.write(content if PYTHON2 else bytes(content, 'utf-8'))
    fake_request.seek(0)
    self.marshaller.process.return_value = serialized_report

    with mock.patch('suds.mx.Content') as mock_content:
      with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
        self.opener.open.return_value = fake_request
        self.report_downloader.DownloadReport(report_definition, output_file)
        mock_request.assert_called_once_with(
            ('https://adwords.google.com/api/adwords/reportdownload/%s'
             % self.version), post_body, headers)
        self.opener.open.assert_called_once_with(mock_request.return_value)
        self.marshaller.process.assert_called_once_with(
            mock_content.return_value)
        self.assertEqual(content, output_file.getvalue())
        self.header_handler.GetReportDownloadHeaders.assert_called_once_with({})

  def testDownloadReportAsString(self):
    report_definition = {'table': 'campaigns',
                         'downloadFormat': 'CSV'}
    serialized_report = 'nuinbwuign'
    post_body = urllib.urlencode({'__rdxml': serialized_report})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'CONTENT STRING アングリーバード'
    fake_request = io.BytesIO()
    fake_request.write(content.encode('utf-8') if PYTHON2
                       else bytes(content, 'utf-8'))
    fake_request.seek(0)
    self.marshaller.process.return_value = serialized_report

    with mock.patch('suds.mx.Content') as mock_content:
      with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
        self.opener.open.return_value = fake_request
        s = self.report_downloader.DownloadReportAsString(report_definition)
        mock_request.assert_called_once_with(
            ('https://adwords.google.com/api/adwords/reportdownload/%s'
             % self.version), post_body, headers)
        self.opener.open.assert_called_once_with(mock_request.return_value)
        self.marshaller.process.assert_called_once_with(
            mock_content.return_value)
        self.assertEqual(content, s)
        self.header_handler.GetReportDownloadHeaders.assert_called_once_with({})

  def testDownloadReportAsStringWithAwql(self):
    query = 'SELECT Id FROM Campaign WHERE NAME LIKE \'%Test%\''
    file_format = 'CSV'
    post_body = urllib.urlencode({'__fmt': file_format, '__rdquery': query})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'CONTENT STRING アングリーバード'
    fake_request = io.BytesIO()
    fake_request.write(content.encode('utf-8') if PYTHON2
                       else bytes(content, 'utf-8'))
    fake_request.seek(0)
    with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
      self.opener.open.return_value = fake_request
      s = self.report_downloader.DownloadReportAsStringWithAwql(query,
                                                                file_format)
      mock_request.assert_called_once_with(
          ('https://adwords.google.com/api/adwords/reportdownload/%s'
           % self.version), post_body, headers)
      self.opener.open.assert_called_once_with(mock_request.return_value)
    self.assertEqual(content, s)
    self.header_handler.GetReportDownloadHeaders.assert_called_once_with({})

  def testDownloadReportCheckFormat_CSVStringSuccess(self):
    output_file = io.StringIO()

    try:
      self.report_downloader._DownloadReportCheckFormat('CSV', output_file)
    except googleads.errors.GoogleAdsValueError:
      self.fail('_DownloadReportCheckFormat raised GoogleAdsValueError'
                'unexpectedly!')

  def testDownloadReportCheckFormat_GZIPPEDBinaryFileSuccess(self):
    output_file = io.StringIO()

    try:
      self.report_downloader._DownloadReportCheckFormat('CSV', output_file)
    except googleads.errors.GoogleAdsValueError:
      self.fail('_DownloadReportCheckFormat raised GoogleAdsValueError'
                'unexpectedly!')

  def testDownloadReportCheckFormat_GZIPPEDBytesIOSuccess(self):
    output_file = tempfile.TemporaryFile(mode='wb')

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
    report_definition = {'table': 'campaigns',
                         'downloadFormat': 'CSV'}
    serialized_report = 'hjuibnibguo'
    post_body = urllib.urlencode({'__rdxml': serialized_report})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'Page not found. :-('
    fake_request = io.StringIO() if PYTHON2 else io.BytesIO()
    fake_request.write(content if PYTHON2 else bytes(content, 'utf-8'))
    fake_request.seek(0)
    error = urllib2.HTTPError('', 400, 'Bad Request', {}, fp=fake_request)

    self.marshaller.process.return_value = serialized_report

    with mock.patch('suds.mx.Content') as mock_content:
      with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
        self.opener.open.side_effect = error
        self.assertRaises(
            googleads.errors.AdWordsReportError,
            self.report_downloader.DownloadReport, report_definition,
            output_file)

        mock_request.assert_called_once_with(
            ('https://adwords.google.com/api/adwords/reportdownload/%s'
             % self.version), post_body, headers)
        self.opener.open.assert_called_once_with(mock_request.return_value)
        self.marshaller.process.assert_called_once_with(
            mock_content.return_value)
        self.assertEqual('', output_file.getvalue())
        self.header_handler.GetReportDownloadHeaders.assert_called_once_with({})

  def testDownloadReportWithAwql(self):
    output_file = io.StringIO()
    query = 'SELECT Id FROM Campaign WHERE NAME LIKE \'%Test%\''
    file_format = 'CSV'
    post_body = urllib.urlencode({'__fmt': file_format, '__rdquery': query})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'CONTENT STRING 广告客户'
    fake_request = io.StringIO() if PYTHON2 else io.BytesIO()
    fake_request.write(content if PYTHON2 else bytes(content, 'utf-8'))
    fake_request.seek(0)

    with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
      self.opener.open.return_value = fake_request
      self.report_downloader.DownloadReportWithAwql(
          query, file_format, output_file)

      mock_request.assert_called_once_with(
          ('https://adwords.google.com/api/adwords/reportdownload/%s'
           % self.version), post_body, headers)
      self.opener.open.assert_called_once_with(mock_request.return_value)

    self.assertEqual(content, output_file.getvalue())
    self.header_handler.GetReportDownloadHeaders.assert_called_once_with({})

  def testDownloadReportWithBytesIO(self):
    output_file = io.BytesIO()
    report_definition = {'table': 'campaigns',
                         'downloadFormat': 'GZIPPED_CSV'}
    serialized_report = 'nuinbwuign'
    post_body = urllib.urlencode({'__rdxml': serialized_report})
    if not PYTHON2:
      post_body = bytes(post_body, 'utf-8')
    headers = {'Authorization': 'ya29.something'}
    self.header_handler.GetReportDownloadHeaders.return_value = headers
    content = u'CONTENT STRING 广告客户'
    fake_request = io.BytesIO()
    fake_request.write(content.encode('utf-8') if PYTHON2
                       else bytes(content, 'utf-8'))
    fake_request.seek(0)
    self.marshaller.process.return_value = serialized_report

    with mock.patch('suds.mx.Content') as mock_content:
      with mock.patch(URL_REQUEST_PATH + '.Request') as mock_request:
        self.opener.open.return_value = fake_request
        self.report_downloader.DownloadReport(report_definition, output_file)
        mock_request.assert_called_once_with(
            ('https://adwords.google.com/api/adwords/reportdownload/%s'
             % self.version), post_body, headers)
        self.opener.open.assert_called_once_with(mock_request.return_value)
        self.marshaller.process.assert_called_once_with(
            mock_content.return_value)
        self.assertEqual(content, output_file.getvalue().decode('utf-8'))
        self.header_handler.GetReportDownloadHeaders.assert_called_once_with({})

  def testExtractError_badRequest(self):
    response = mock.Mock()
    response.code = 400
    type_ = 'ReportDownloadError.INVALID_REPORT_DEFINITION_XML'
    trigger = 'Invalid enumeration.'
    field_path = 'Criteria.Type'
    content_template = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<reportDownloadError><ApiError><type>%s</type><trigger>%s</trigger>'
        '<fieldPath>%s</fieldPath></ApiError></reportDownloadError>')
    content = content_template % (type_, trigger, field_path)
    response.read.return_value = (content if PYTHON2
                                  else bytes(content, 'utf-8'))

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(type_, rval.type)
    self.assertEqual(trigger, rval.trigger)
    self.assertEqual(field_path, rval.field_path)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(content, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportBadRequestError)

    # Check that if the XML fields are empty, this still functions.
    content = content_template % ('', '', '')
    response.read.return_value = (content if PYTHON2
                                  else bytes(content, 'utf-8'))
    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(None, rval.type)
    self.assertEqual(None, rval.trigger)
    self.assertEqual(None, rval.field_path)

  def testExtractError_malformedBadRequest(self):
    response = mock.Mock()
    response.code = 400
    content = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<reportDownloadError><ApiError><type>1234</type><trigger>5678'
               '</trigger></ApiError></ExtraElement></reportDownloadError>')
    response.read.return_value = (content if PYTHON2
                                  else bytes(content, 'utf-8'))

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(content, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportError)

  def testExtractError_notBadRequest(self):
    response = mock.Mock()
    response.code = 400
    content = 'Page not found!'
    response.read.return_value = (content if PYTHON2
                                  else bytes(content, 'utf-8'))

    rval = self.report_downloader._ExtractError(response)
    self.assertEqual(response.code, rval.code)
    self.assertEqual(response, rval.error)
    self.assertEqual(content, rval.content)
    self.assertIsInstance(rval, googleads.errors.AdWordsReportError)


if __name__ == '__main__':
  unittest.main()
