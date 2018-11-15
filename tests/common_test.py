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

"""Unit tests to cover the common module."""


from contextlib import contextmanager
import numbers
import os
import ssl
import unittest
import warnings

from pyfakefs import fake_filesystem
from pyfakefs import fake_tempfile
import mock
import requests.exceptions
import six
import suds
import suds.cache
import yaml
import zeep.cache

import googleads.common
import googleads.errors
import googleads.oauth2
from . import testing
import zeep.exceptions


URL_REQUEST_PATH = 'urllib2' if six.PY2 else 'urllib.request'
TEST_DIR = os.path.dirname(__file__)
CURRENT_VERSION = 'v201811'


class CommonTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.common module."""

  # Dictionaries with all the required OAuth2 keys
  _OAUTH_INSTALLED_APP_DICT = {'client_id': 'a', 'client_secret': 'b',
                               'refresh_token': 'c'}
  _OAUTH_SERVICE_ACCT_DICT = {
      'path_to_private_key_file': '/test/test.json',
      'delegated_account': 'delegated_account@example.com'}

  def setUp(self):
    self.filesystem = fake_filesystem.FakeFilesystem()
    self.tempfile = fake_tempfile.FakeTempfileModule(self.filesystem)
    self.fake_open = fake_filesystem.FakeFileOpen(self.filesystem)
    self.uri1 = 'http://h1:1'
    self.uri1_w_creds = 'http://username:password@h1:1'
    self.uri2 = 'http://h2:2'
    self.uplink_uri = 'http://127.0.0.1:999'
    self.test1_name = 'Test1'
    self.test2_name = 'Test2'
    self.test2_version = 'testing'
    self.fake_version = 'ignored'
    locale_patcher = mock.patch('googleads.common.locale.getdefaultlocale',
                                return_value=('en_us', 'UTF-8'))
    self.locale_patcher = locale_patcher.start()

    @googleads.common.RegisterUtility(self.test1_name)
    class Test1(object):

      def test(self):
        pass

    @googleads.common.RegisterUtility(self.test2_name,
                                      {'test': self.test2_version})
    class Test2(object):

      def test(self):
        pass

    self.test1 = Test1
    self.test2 = Test2

  def tearDown(self):
    super(CommonTest, self).tearDown()
    self.locale_patcher.stop()

  def testShouldWarnWithBadEncoding(self):
    self.locale_patcher.return_value = (None, None)
    test_major_value = 2
    test_minor_value = 6
    test_micro_value = 9
    with mock.patch('googleads.common._PY_VERSION_MAJOR', test_major_value):
      with mock.patch('googleads.common._PY_VERSION_MINOR', test_minor_value):
        with mock.patch('googleads.common._PY_VERSION_MICRO', test_micro_value):
          with mock.patch('googleads.common._logger') as mock_logger:
            googleads.common.CommonClient()
            mock_logger.warn.assert_called_once()

  def _CreateYamlFile(self, data, insert_oauth2_key=None, oauth_dict=None):
    """Return the filename of a yaml file created for testing."""
    yaml_file = self.tempfile.NamedTemporaryFile(delete=False)
    with self.fake_open(yaml_file.name, 'w') as yaml_handle:
      for key in data:
        if key is insert_oauth2_key:
          data[key].update(oauth_dict)
      yaml_handle.write(yaml.dump(data))

    return yaml_file.name

  def testLoadFromStorage_missingFile(self):
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromStorage,
          'yaml_filename', 'woo', [], [])

  def testLoadFromStorage_missingRequiredKey(self):
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      # Both keys are missing.
      yaml_fname = self._CreateYamlFile({'two': {}}, 'two',
                                        self._OAUTH_INSTALLED_APP_DICT)
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromStorage,
          yaml_fname, 'two', ['needed', 'keys'], [])

      # One key is missing.
      yaml_fname = self._CreateYamlFile({'three': {'needed': 'd'}}, 'three',
                                        self._OAUTH_INSTALLED_APP_DICT)
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromStorage,
          yaml_fname, 'three', ['needed', 'keys'], [])

  def testLoadFromStorage(self):
    # No optional keys present.
    yaml_fname = self._CreateYamlFile(
        {'one': {'needed': 'd', 'keys': 'e'}}, 'one',
        self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromStorage(
              yaml_fname, 'one', ['needed', 'keys'], ['other'])
          proxy_config.assert_called_once_with(
              http_proxy=None, https_proxy=None, cafile=None,
              disable_certificate_validation=False)
          mock_client.assert_called_once_with(
              'a', 'b', 'c', proxy_config=proxy_config.return_value)
          self.assertEqual({'oauth2_client': mock_client.return_value,
                            'needed': 'd', 'keys': 'e',
                            'proxy_config': proxy_config.return_value,
                            googleads.common.ENABLE_COMPRESSION_KEY: False,
                            googleads.common.CUSTOM_HEADERS_KEY: None},
                           rval)
          self.assertTrue(googleads.common._utility_registry._enabled)

    # Optional keys present
    logging_config = {'foo': 'bar'}
    yaml_fname = self._CreateYamlFile(
        {'one': {'needed': 'd', 'keys': 'e', 'other': 'f'},
         googleads.common._LOGGING_KEY: logging_config,
         googleads.common.SOAP_IMPLEMENTATION_KEY: 'suds',
         googleads.common.CUSTOM_HEADERS_KEY: {'X-My-Header': 'abc'}},
        'one', self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          with mock.patch('logging.config.dictConfig') as mock_dict_config:
            proxy_config.return_value = mock.Mock()
            rval = googleads.common.LoadFromStorage(
                yaml_fname, 'one', ['needed', 'keys'], ['other'])
            proxy_config.assert_called_once_with(
                http_proxy=None, https_proxy=None, cafile=None,
                disable_certificate_validation=False)
            mock_client.assert_called_once_with(
                'a', 'b', 'c', proxy_config=proxy_config.return_value)
            mock_dict_config.assert_called_once_with(logging_config)
            self.assertEqual({'oauth2_client': mock_client.return_value,
                              'needed': 'd', 'keys': 'e', 'other': 'f',
                              'proxy_config': proxy_config.return_value,
                              googleads.common.ENABLE_COMPRESSION_KEY: False,
                              googleads.common.SOAP_IMPLEMENTATION_KEY: 'suds',
                              googleads.common.CUSTOM_HEADERS_KEY: {
                                  'X-My-Header': 'abc'}},
                             rval)
            self.assertTrue(googleads.common._utility_registry._enabled)

  def testLoadFromStorage_relativePath(self):
    fake_os = fake_filesystem.FakeOsModule(self.filesystem)
    yaml_contents = {'one': {'needed': 'd', 'keys': 'e'}}
    yaml_contents['one'].update(self._OAUTH_INSTALLED_APP_DICT)
    self.filesystem.CreateFile('/home/test/yaml/googleads.yaml',
                               contents=yaml.dump(yaml_contents))
    fake_os.chdir('/home/test')

    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.os', fake_os):
        with mock.patch('googleads.common.open', self.fake_open, create=True):
          with mock.patch('googleads.common.ProxyConfig') as proxy_config:
            proxy_config.return_value = mock.Mock()
            rval = googleads.common.LoadFromStorage(
                'yaml/googleads.yaml', 'one', ['needed', 'keys'], ['other'])

        proxy_config.assert_called_once_with(
            http_proxy=None, https_proxy=None, cafile=None,
            disable_certificate_validation=False)
        mock_client.assert_called_once_with(
            'a', 'b', 'c', proxy_config=proxy_config.return_value)
        self.assertEqual({'oauth2_client': mock_client.return_value,
                          'proxy_config': proxy_config.return_value,
                          'needed': 'd', 'keys': 'e',
                          googleads.common.ENABLE_COMPRESSION_KEY: False,
                          googleads.common.CUSTOM_HEADERS_KEY: None}, rval)
        self.assertTrue(googleads.common._utility_registry._enabled)

  def _CreateYamlDoc(self, data, insert_oauth2_key=None, oauth_dict=None):
    """Return the yaml doc created for testing."""
    for key in data:
      if key is insert_oauth2_key:
        data[key].update(oauth_dict)
    return yaml.dump(data)

  def testExtractRequestSummaryFieldsForAdWords(self):
    root = suds.sax.element.Element('root', parent=None)
    client_customer_id = '111-222-3333'
    ccid_element = suds.sax.element.Element('clientCustomerId', parent=None)
    ccid_element.text = client_customer_id
    request_header_element = suds.sax.element.Element('RequestHeader',
                                                      parent=None)
    header_element = suds.sax.element.Element('Header', parent=None)
    method_name = 'someMethodName'
    method_element = suds.sax.element.Element(method_name)
    body = suds.sax.element.Element('Body', parent=None)
    request_header_element.append(ccid_element)
    header_element.append(request_header_element)
    body.append(method_element)
    root.append((header_element, body))
    expected_result = {
        'methodName': method_name,
        'clientCustomerId': client_customer_id
    }

    self.assertEqual(expected_result,
                     googleads.common._ExtractRequestSummaryFields(root))

  def testExtractRequestSummaryFieldsForAdManager(self):
    root = suds.sax.element.Element('root', parent=None)
    network_code = '111111111'
    nc_element = suds.sax.element.Element('networkCode', parent=None)
    nc_element.text = network_code
    request_header_element = suds.sax.element.Element('RequestHeader',
                                                      parent=None)
    header_element = suds.sax.element.Element('Header', parent=None)
    method_name = 'someMethodName'
    method_element = suds.sax.element.Element(method_name)
    body = suds.sax.element.Element('Body', parent=None)
    request_header_element.append(nc_element)
    header_element.append(request_header_element)
    body.append(method_element)
    root.append((header_element, body))
    expected_result = {
        'methodName': method_name,
        'networkCode': network_code
    }

    self.assertEqual(expected_result,
                     googleads.common._ExtractRequestSummaryFields(root))

  def testExtractResponseSummaryFieldsWithAdWordsFields(self):
    root = suds.sax.element.Element('Envelope', parent=None)
    doc = suds.sax.document.Document(root=root)
    request_id = '0'
    response_time = '1000'
    service_name = 'SomeService'
    method_name = 'someMethodName'
    operations = '0'
    rid_element = suds.sax.element.Element('requestId', parent=None)
    rid_element.text = request_id
    rt_element = suds.sax.element.Element('responseTime', parent=None)
    rt_element.text = response_time
    service_element = suds.sax.element.Element('serviceName', parent=None)
    service_element.text = service_name
    method_element = suds.sax.element.Element('methodName', parent=None)
    method_element.text = method_name
    ops_element = suds.sax.element.Element('operations', parent=None)
    ops_element.text = operations
    response_header_element = suds.sax.element.Element('ResponseHeader',
                                                       parent=None)
    header_element = suds.sax.element.Element('Header', parent=None)
    body = suds.sax.element.Element('Body', parent=None)
    response_header_element.append((rid_element, rt_element, service_element,
                                    method_element, ops_element))
    header_element.append(response_header_element)
    root.append((header_element, body))
    expected_result = {
        'requestId': request_id,
        'responseTime': response_time,
        'isFault': False,
        'serviceName': service_name,
        'methodName': method_name,
        'operations': operations
    }

    self.assertEqual(expected_result,
                     googleads.common._ExtractResponseSummaryFields(doc))

  def testExtractResponseSummaryFieldsWithFault(self):
    root = suds.sax.element.Element('Envelope', parent=None)
    doc = suds.sax.document.Document(root=root)
    request_id = '0'
    response_time = '1000'
    fault_string = 'I AM ERROR'
    rid_element = suds.sax.element.Element('requestId', parent=None)
    rid_element.text = suds.sax.text.Text(request_id)
    rt_element = suds.sax.element.Element('responseTime', parent=None)
    rt_element.text = suds.sax.text.Text(response_time)
    response_header_element = suds.sax.element.Element('ResponseHeader',
                                                       parent=None)
    header_element = suds.sax.element.Element('Header', parent=None)
    response_header_element.append((rid_element, rt_element))
    header_element.append(response_header_element)
    fault_element = suds.sax.element.Element('Fault', parent=None)
    fault_string_element = suds.sax.element.Element('faultstring', parent=None)
    fault_string_element.text = suds.sax.text.Text(fault_string)
    body = suds.sax.element.Element('Body', parent=None)
    fault_element.append(fault_string_element)
    body.append(fault_element)
    root.append((header_element, body))
    expected_result = {
        'requestId': request_id,
        'responseTime': response_time,
        'isFault': True,
        'faultMessage': fault_string
    }

    self.assertEqual(expected_result,
                     googleads.common._ExtractResponseSummaryFields(doc))

  def testExtractResponseSummaryFieldsWithoutFault(self):
    root = suds.sax.element.Element('Envelope', parent=None)
    doc = suds.sax.document.Document(root=root)
    request_id = '0'
    response_time = '1000'
    rid_element = suds.sax.element.Element('requestId', parent=None)
    rid_element.text = request_id
    rt_element = suds.sax.element.Element('responseTime', parent=None)
    rt_element.text = response_time
    response_header_element = suds.sax.element.Element('ResponseHeader',
                                                       parent=None)
    header_element = suds.sax.element.Element('Header', parent=None)
    body = suds.sax.element.Element('Body', parent=None)
    response_header_element.append((rid_element, rt_element))
    header_element.append(response_header_element)
    root.append((header_element, body))
    expected_result = {
        'requestId': request_id,
        'responseTime': response_time,
        'isFault': False
    }

    self.assertEqual(expected_result,
                     googleads.common._ExtractResponseSummaryFields(doc))

  def testCommonClient_deprecatedWarningLoggerByMicroValue(self):
    test_major_value = 2
    test_minor_value = 7
    test_micro_value = 6
    with mock.patch('googleads.common._PY_VERSION_MAJOR', test_major_value):
      with mock.patch('googleads.common._PY_VERSION_MINOR', test_minor_value):
        with mock.patch('googleads.common._PY_VERSION_MICRO', test_micro_value):
          with mock.patch('googleads.common._logger') as mock_logger:
            googleads.common.CommonClient()
            mock_logger.warning.assert_called_once_with(
                googleads.common._DEPRECATED_VERSION_TEMPLATE,
                test_major_value, test_minor_value, test_micro_value)

  def testLoadFromString_deprecatedWarningLoggerByMinorValue(self):
    test_major_value = 2
    test_minor_value = 6
    test_micro_value = 9
    with mock.patch('googleads.common._PY_VERSION_MAJOR', test_major_value):
      with mock.patch('googleads.common._PY_VERSION_MINOR', test_minor_value):
        with mock.patch('googleads.common._PY_VERSION_MICRO', test_micro_value):
          with mock.patch('googleads.common._logger') as mock_logger:
            googleads.common.CommonClient()
            mock_logger.warning.assert_called_once_with(
                googleads.common._DEPRECATED_VERSION_TEMPLATE,
                test_major_value, test_minor_value, test_micro_value)

  def testLoadFromString_emptyYamlString(self):
    yaml_doc = ''
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromString,
          yaml_doc, 'woo', [], [])

  def testLoadFromString_malformedYamlString(self):
    yaml_doc = 'woo:::'
    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        googleads.common.LoadFromString,
        yaml_doc, 'woo', [], [])

  def testLoadFromString_emptyProductData(self):
    yaml_doc = self._CreateYamlDoc({'woo': None})
    self.assertRaises(
        googleads.errors.GoogleAdsValueError,
        googleads.common.LoadFromString,
        yaml_doc, 'woo', [], [])

  def testLoadFromString_missingOAuthKey(self):
    yaml_doc = self._CreateYamlDoc({'woo': {}})
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromString,
          yaml_doc, 'woo', [], [])

  def testLoadFromString_missingProductYamlKey(self):
    yaml_doc = self._CreateYamlDoc({'woo': {}})
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromString,
          yaml_doc, 'bar', [], [])

  def testLoadFromString_missingRequiredKey(self):
    yaml_doc = self._CreateYamlDoc({'woo': {}})
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromString,
          yaml_doc, 'woo', ['bar'], [])

  def testLoadFromString_missingPartialInstalledAppOAuthCredential(self):
    yaml_doc = self._CreateYamlDoc({'woo': {}}, 'woo', {'client_id': 'abc'})
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      self.assertRaises(
          googleads.errors.GoogleAdsValueError,
          googleads.common.LoadFromString,
          yaml_doc, 'woo', [], [])

  def testLoadFromString_passesWithNoRequiredKeys(self):
    yaml_doc = self._CreateYamlDoc({'woo': {}}, 'woo',
                                   self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(yaml_doc, 'woo', [], [])

    proxy_config.assert_called_once_with(
        http_proxy=None, https_proxy=None, cafile=None,
        disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False,
                      googleads.common.CUSTOM_HEADERS_KEY: None}, rval)

  def testLoadFromString_passesWithHTTPAndHTTPSProxy(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'http': self.uri1,
             'https': self.uri2}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'adwords', [], [])

    proxy_config.assert_called_once_with(
        http_proxy=self.uri1, https_proxy=self.uri2, cafile=None,
        disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False,
                      googleads.common.CUSTOM_HEADERS_KEY: None}, rval)

  def testHTTPSProxyExtendsSSLSockTimeout(self):
    proxy_config = mock.MagicMock()
    with mock.patch('suds.transport.http.'
                    'HttpTransport.__init__') as mock_transport:
      googleads.common._SudsProxyTransport(1000, proxy_config)
      self.assertEqual(mock_transport.call_args_list[0][1]['timeout'], 1000)

  def testLoadFromString_passesWithHTTPProxy(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'http': self.uri1}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'adwords', [], [])
    proxy_config.assert_called_once_with(http_proxy=self.uri1,
                                         https_proxy=None, cafile=None,
                                         disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False,
                      googleads.common.CUSTOM_HEADERS_KEY: None}, rval)

  def testLoadFromString_passesWithHTTPProxyLogin(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'http': self.uri1_w_creds}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(yaml_doc, 'adwords', [], [])

    proxy_config.assert_called_once_with(http_proxy=self.uri1_w_creds,
                                         https_proxy=None, cafile=None,
                                         disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False,
                      googleads.common.CUSTOM_HEADERS_KEY: None}, rval)

  def testLoadFromString_passesWithHTTPSProxy(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'https': self.uri1}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(yaml_doc, 'adwords', [], [])

    proxy_config.assert_called_once_with(http_proxy=None,
                                         https_proxy=self.uri1,
                                         cafile=None,
                                         disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False,
                      googleads.common.CUSTOM_HEADERS_KEY: None}, rval)

  def testLoadFromString_passesWithHTTPSProxyLogin(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'https': self.uri1_w_creds}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(yaml_doc, 'adwords', [], [])

    proxy_config.assert_called_once_with(http_proxy=None,
                                         https_proxy=self.uri1_w_creds,
                                         cafile=None,
                                         disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False,
                      googleads.common.CUSTOM_HEADERS_KEY: None}, rval)

  def testLoadFromString_missingRequiredKeys(self):
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      # Both keys are missing.
      yaml_doc = self._CreateYamlDoc({
          'two': {}
      }, 'two', self._OAUTH_INSTALLED_APP_DICT)
      self.assertRaises(googleads.errors.GoogleAdsValueError,
                        googleads.common.LoadFromString, yaml_doc, 'two',
                        ['needed', 'keys'], [])

      # One key is missing.
      yaml_doc = self._CreateYamlDoc({
          'three': {
              'needed': 'd'
          }
      }, 'three', self._OAUTH_INSTALLED_APP_DICT)
      self.assertRaises(googleads.errors.GoogleAdsValueError,
                        googleads.common.LoadFromString, yaml_doc, 'three',
                        ['needed', 'keys'], [])

  def testLoadFromString_migrateToAdManager(self):
    with mock.patch('googleads.common.open', self.fake_open, create=True):
      # Both keys are missing.
      yaml_doc = self._CreateYamlDoc({
          'dfp': {}
      }, 'dfp', self._OAUTH_INSTALLED_APP_DICT)
      with self.assertRaises(googleads.errors.GoogleAdsValueError) as ctx:
        googleads.common.LoadFromString(yaml_doc, 'two', ['ad_manager'], [])

      self.assertIn('Please replace', str(ctx.exception))

  def testLoadFromString(self):
    # No optional keys present.
    yaml_doc = self._CreateYamlDoc({
        'one': {
            'needed': 'd',
            'keys': 'e'
        }
    }, 'one', self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'one', ['needed', 'keys'], ['other'])
          proxy_config.assert_called_once_with(
              http_proxy=None, https_proxy=None, cafile=None,
              disable_certificate_validation=False)
          mock_client.assert_called_once_with(
              'a', 'b', 'c', proxy_config=proxy_config.return_value)
          self.assertEqual({'oauth2_client': mock_client.return_value,
                            'needed': 'd', 'keys': 'e',
                            'proxy_config': proxy_config.return_value,
                            googleads.common.ENABLE_COMPRESSION_KEY: False,
                            googleads.common.CUSTOM_HEADERS_KEY: None},
                           rval)
          self.assertTrue(googleads.common._utility_registry._enabled)

    # The optional key is present.
    yaml_doc = self._CreateYamlDoc({'one': {'needed': 'd', 'keys': 'e',
                                            'other': 'f'}}, 'one',
                                   self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'one', ['needed', 'keys'], ['other'])
          proxy_config.assert_called_once_with(
              http_proxy=None, https_proxy=None, cafile=None,
              disable_certificate_validation=False)
          mock_client.assert_called_once_with(
              'a', 'b', 'c', proxy_config=proxy_config.return_value)
          self.assertEqual({'oauth2_client': mock_client.return_value,
                            'needed': 'd', 'keys': 'e', 'other': 'f',
                            'proxy_config': proxy_config.return_value,
                            googleads.common.ENABLE_COMPRESSION_KEY: False,
                            googleads.common.CUSTOM_HEADERS_KEY: None},
                           rval)
          self.assertTrue(googleads.common._utility_registry._enabled)

  def testLoadFromString_serviceAccount(self):
    ad_manager_scope = googleads.oauth2.GetAPIScope('ad_manager')
    # No optional keys present.
    yaml_doc = self._CreateYamlDoc(
        {'ad_manager': {'needed': 'd', 'keys': 'e'}},
        insert_oauth2_key='ad_manager',
        oauth_dict=self._OAUTH_SERVICE_ACCT_DICT)
    with mock.patch(
        'googleads.oauth2.GoogleServiceAccountClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'ad_manager', ['needed', 'keys'], ['other'])

    proxy_config.assert_called_once_with(
        http_proxy=None, https_proxy=None, cafile=None,
        disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        '/test/test.json', ad_manager_scope,
        sub='delegated_account@example.com',
        proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      'needed': 'd', 'keys': 'e',
                      googleads.common.ENABLE_COMPRESSION_KEY: False,
                      googleads.common.CUSTOM_HEADERS_KEY: None}, rval)
    self.assertTrue(googleads.common._utility_registry._enabled)

    # The optional key is present.
    yaml_doc = self._CreateYamlDoc(
        {'ad_manager': {'needed': 'd', 'keys': 'e', 'other': 'f'}},
        'ad_manager', self._OAUTH_SERVICE_ACCT_DICT)
    with mock.patch(
        'googleads.oauth2.GoogleServiceAccountClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'ad_manager', ['needed', 'keys'], ['other'])

    proxy_config.assert_called_once_with(
        http_proxy=None, https_proxy=None, cafile=None,
        disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        '/test/test.json', ad_manager_scope,
        sub='delegated_account@example.com',
        proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      'needed': 'd', 'keys': 'e', 'other': 'f',
                      googleads.common.ENABLE_COMPRESSION_KEY: False,
                      googleads.common.CUSTOM_HEADERS_KEY: None}, rval)
    self.assertTrue(googleads.common._utility_registry._enabled)


  def testLoadFromString_utilityRegistryDisabled(self):
    yaml_doc = self._CreateYamlDoc(
        {'one': {'needed': 'd', 'keys': 'e'},
         'include_utilities_in_user_agent': False},
        'one', self._OAUTH_INSTALLED_APP_DICT)

    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'one', ['needed', 'keys'], ['other'])
          proxy_config.assert_called_once_with(
              http_proxy=None, https_proxy=None, cafile=None,
              disable_certificate_validation=False)
          mock_client.assert_called_once_with(
              'a', 'b', 'c', proxy_config=proxy_config.return_value)
          self.assertEqual({'oauth2_client': mock_client.return_value,
                            'needed': 'd', 'keys': 'e',
                            'proxy_config': proxy_config.return_value,
                            googleads.common.ENABLE_COMPRESSION_KEY: False,
                            googleads.common.CUSTOM_HEADERS_KEY: None},
                           rval)
          self.assertFalse(googleads.common._utility_registry._enabled)


  def testLoadFromString_warningWithUnrecognizedKey(self):
    yaml_doc = self._CreateYamlDoc(
        {'kval': {'Im': 'here', 'whats': 'this?'}}, 'kval',
        self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with warnings.catch_warnings(record=True) as captured_warnings:
        with mock.patch('googleads.common.open', self.fake_open, create=True):
          with mock.patch('googleads.common.ProxyConfig') as proxy_config:
            proxy_config.return_value = mock.Mock()
            rval = googleads.common.LoadFromString(
                yaml_doc, 'kval', ['Im'], ['other'])
        mock_client.assert_called_once_with(
            'a', 'b', 'c', proxy_config=proxy_config.return_value)
        self.assertEqual(
            {
                'oauth2_client': mock_client.return_value,
                'Im': 'here',
                'proxy_config': proxy_config.return_value,
                googleads.common.ENABLE_COMPRESSION_KEY: False,
                googleads.common.CUSTOM_HEADERS_KEY: None
            }, rval)
        self.assertTrue(googleads.common._utility_registry._enabled)
        self.assertEqual(len(captured_warnings), 1)


  def testGenerateLibSig(self):
    my_name = 'Joseph'
    self.assertEqual(
        ' (%s, %s, %s)' % (my_name, googleads.common._COMMON_LIB_SIG,
                           googleads.common._PYTHON_VERSION),
        googleads.common.GenerateLibSig(my_name))


  def testGenerateLibSigWithUtilities(self):
    my_name = 'Mark'

    t1 = self.test1()
    t2 = self.test2()

    # The order of utilities in the generated library signature is not
    # guaranteed, so verify that the string contains the same values instead.
    # Make the first request using both utilities.
    t1.test()
    t2.test()
    expected = set((my_name, googleads.common._COMMON_LIB_SIG,
                    googleads.common._PYTHON_VERSION, self.test1_name,
                    '%s/%s' % (self.test2_name, self.test2_version)))
    generated = set(googleads.common.GenerateLibSig(my_name)[2:-1].split(', '))

    self.assertEqual(expected, generated)

    # Make another request, this time no utilities.
    expected = set((my_name, googleads.common._COMMON_LIB_SIG,
                    googleads.common._PYTHON_VERSION))
    generated = set(googleads.common.GenerateLibSig(my_name)[2:-1].split(', '))

    self.assertEqual(expected, generated)

    # Make another request, this time one utility.
    t1.test()
    expected = set((my_name, googleads.common._COMMON_LIB_SIG,
                    googleads.common._PYTHON_VERSION, self.test1_name))
    generated = set(googleads.common.GenerateLibSig(my_name)[2:-1].split(', '))

    self.assertEqual(expected, generated)


  def testGenerateLibSigWithUtilitiesDisabled(self):
    my_name = 'Mark'

    googleads.common.IncludeUtilitiesInUserAgent(False)

    t1 = self.test1()
    t1.test()
    t2 = self.test2()
    t2.test()

    self.assertEqual(
        ' (%s, %s, %s)' % (my_name, googleads.common._COMMON_LIB_SIG,
                           googleads.common._PYTHON_VERSION),
        googleads.common.GenerateLibSig(my_name))

  def testPackForSuds(self):
    factory = mock.Mock()

    # Test that anything other than list, tuple, and dict pass right through.
    self.assertEqual('input', googleads.common._PackForSuds('input', factory))
    self.assertEqual(set([1]),
                     googleads.common._PackForSuds(set([1]), factory))

    # Test that lists not containing dicts with xsi types return the same
    # values, and test that the input list was not modified.
    input_list = ['1', set([3]), {'moo': 'cow'}]
    self.assertEqual(['1', set([3]), {'moo': 'cow'}],
                     googleads.common._PackForSuds(input_list, factory))
    self.assertEqual(['1', set([3]), {'moo': 'cow'}], input_list)

    # Test that dicts without xsi types return the same values, and test that
    # the input dict was not modified
    input_dict = {'1': 'moo', frozenset([2]): ['val']}
    self.assertEqual({'1': 'moo', frozenset([2]): ['val']},
                     googleads.common._PackForSuds(input_dict, factory))
    self.assertEqual({'1': 'moo', frozenset([2]): ['val']}, input_dict)

    # Now it gets interesting... Test that a dictionary with xsi type gets
    # changed into an object. Test that the input dict is unmodified.
    input_dict = {'xsi_type': 'EliteCampaign', 'name': 'Sales', 'id': 123456,
                  'metadata': {'a': 'b'}}
    factory.create.return_value = mock.MagicMock()
    factory.create.return_value.__iter__.return_value = iter(
        [('id', 0), ('name', 1), ('metadata', 2), ('Campaign.Type', 3),
         ('status', 4)])

    rval = googleads.common._PackForSuds(input_dict, factory)
    factory.create.assert_called_once_with('EliteCampaign')
    self.assertEqual('Sales', rval.name)
    self.assertEqual(123456, rval.id)
    self.assertEqual({'a': 'b'}, rval.metadata)
    self.assertEqual('EliteCampaign', getattr(rval, 'Campaign.Type'))
    self.assertEqual(None, rval.status)
    self.assertEqual({'xsi_type': 'EliteCampaign', 'name': 'Sales',
                      'id': 123456, 'metadata': {'a': 'b'}}, input_dict)

    # Test that this all works recursively. Nest dictionaries in dictionaries in
    # lists in classes.
    factory = mock.Mock()
    factory.create.side_effect = [mock.MagicMock(), mock.MagicMock()]
    input_list = [{'xsi_type': 'EliteCampaign', 'name': 'Sales', 'id': None,
                   'metadata': {'xsi_type': 'metadata', 'a': {'b': 'c'}}},
                  {'i do not have': 'a type'}]
    rval = googleads.common._PackForSuds(input_list, factory)
    factory.create.assert_any_call('EliteCampaign')
    factory.create.assert_any_call('metadata')
    self.assertEqual(len(rval), 2)
    self.assertEqual('Sales', rval[0].name)
    self.assertIsInstance(rval[0].id, suds.null)
    self.assertEqual({'b': 'c'}, rval[0].metadata.a)
    self.assertEqual({'i do not have': 'a type'}, rval[1])
    self.assertEqual(
        [{'xsi_type': 'EliteCampaign', 'name': 'Sales', 'id': None,
          'metadata': {'xsi_type': 'metadata', 'a': {'b': 'c'}}},
         {'i do not have': 'a type'}], input_list)

  def testPackForSuds_applyCustomPacker(self):
    class CustomPacker(googleads.common.SoapPacker):
      @classmethod
      def Pack(cls, obj, version):
        if isinstance(obj, numbers.Number):
          return {'xsi_type': 'Integer', 'value': str(int(obj))}
        return obj

    factory = mock.Mock()
    factory.create.return_value = mock.MagicMock()
    factory.create.return_value.__iter__.return_value = iter(
        [('Number.Type', 0), ('value', 1)])
    number = 3.14159265358979323846264

    rval = googleads.common._PackForSuds(number, factory, CustomPacker,
                                         CURRENT_VERSION)
    self.assertEqual('Integer', getattr(rval, 'Number.Type'))
    self.assertEqual('3', rval.value)

  def testPackForSuds_secondNamespace(self):
    factory = mock.Mock()
    factory.create.side_effect = [suds.TypeNotFound(''), mock.MagicMock()]
    input_list = {'xsi_type': 'EliteCampaign', 'name': 'Sales'}
    rval = googleads.common._PackForSuds(input_list, factory)
    factory.create.assert_any_call('EliteCampaign')
    factory.create.assert_any_call('ns0:EliteCampaign')
    self.assertEqual('Sales', rval.name)


@contextmanager
def mock_zeep_client():
  mock_port = mock.MagicMock()
  mock_port.binding = mock.MagicMock()
  mock_service = mock.MagicMock()
  mock_service.ports.itervalues.return_value = iter([mock_port])
  mock_service.ports.values.return_value = iter([mock_port])  # For py3

  with mock.patch('googleads.common.zeep.Client') as mock_client:
    mock_services = mock_client.return_value.wsdl.services
    mock_services.itervalues.return_value = iter([mock_service])
    mock_services.values.return_value = iter([mock_service])  # For py3

    yield mock_client


class ZeepServiceProxyTest(unittest.TestCase):

  def setUp(self):
    super(ZeepServiceProxyTest, self).setUp()

    self.empty_proxy_config = googleads.common.ProxyConfig()
    self.timeout_100 = 100
    self.fake_version = 'ignored'

  def testCreateZeepClient(self):
    header_handler = mock.Mock()
    packer = mock.Mock()

    class MyCache(zeep.cache.Base):
      pass
    cache = MyCache()

    with mock_zeep_client() as mock_client, \
        mock.patch('googleads.common._ZeepAuthHeaderPlugin') as zeep_auth, \
        mock.patch('googleads.common._ZeepProxyTransport') as zeep_transport, \
        mock.patch('googleads.util.ZeepLogger') as zeep_logger:
      zeep_wrapper = googleads.common.ZeepServiceProxy(
          'http://abc', header_handler, packer, 'proxy', 'timeout',
          self.fake_version, cache)

      zeep_auth.assert_called_once_with(header_handler)
      plugins = [zeep_auth.return_value, zeep_logger.return_value]
      transport = zeep_transport.return_value
      zeep_transport.assert_called_once_with('timeout', 'proxy', cache)
      mock_client.assert_called_once_with(
          'http://abc', transport=transport, plugins=plugins)
      self.assertEqual(zeep_wrapper.zeep_client, mock_client.return_value)

  def testCreateSoapElementForType(self):
    header_handler = mock.Mock()
    packer = mock.Mock()

    with mock_zeep_client():
      zeep_wrapper = googleads.common.ZeepServiceProxy(
          'http://abc', header_handler, packer,
          self.empty_proxy_config, self.timeout_100, self.fake_version)

      type_mock = mock.Mock()
      zeep_wrapper.zeep_client.get_type.return_value = type_mock
      result = zeep_wrapper.CreateSoapElementForType('MyType')
      self.assertEqual(result, type_mock.return_value)
      zeep_wrapper.zeep_client.get_type.assert_called_once_with('MyType')

  def testWsdlHasMethod(self):
    header_handler = mock.Mock()
    packer = mock.Mock()

    with mock_zeep_client():
      zeep_wrapper = googleads.common.ZeepServiceProxy(
          'http://abc', header_handler, packer,
          self.empty_proxy_config, self.timeout_100, self.fake_version)

      with mock.patch.object(zeep_wrapper, '_method_bindings') as mock_bindings:
        get_method = mock_bindings.get

        self.assertTrue(zeep_wrapper._WsdlHasMethod('abc'))

        get_method.side_effect = ValueError
        self.assertFalse(zeep_wrapper._WsdlHasMethod('abc'))

  def testZeepErrorRaisesGoogleError(self):
    with mock_zeep_client() as mock_client:
      mock_client.side_effect = requests.exceptions.HTTPError

      with self.assertRaises(googleads.errors.GoogleAdsSoapTransportError):
        googleads.common.ZeepServiceProxy(
            'http://abc', None, None, self.empty_proxy_config, self.timeout_100,
            self.fake_version)

  @mock.patch('googleads.common._ZeepProxyTransport')
  def testSchemaHelperRaisesGoogleError(self, mock_transport_class):
    mock_transport_class.return_value.load.side_effect = (
        requests.exceptions.HTTPError)

    with self.assertRaises(googleads.errors.GoogleAdsSoapTransportError):
      googleads.common.ZeepSchemaHelper(None, None, None, 100, None)

  def testGetRequestXML(self):
    header_handler = mock.Mock()
    packer = mock.Mock()

    with mock_zeep_client():
      zeep_wrapper = googleads.common.ZeepServiceProxy(
          'http://abc', header_handler, packer,
          self.empty_proxy_config, self.timeout_100, self.fake_version)

      mock_create = zeep_wrapper.zeep_client.create_message

      with mock.patch.object(
          zeep_wrapper,
          '_GetZeepFormattedSOAPHeaders') as mock_get_headers, \
          mock.patch.object(zeep_wrapper, '_PackArguments') as mock_pack:
        mock_pack.return_value = [1, 2, 3]

        result = zeep_wrapper.GetRequestXML('someMethod', 'a', 1, 2)

        self.assertEqual(result, mock_create.return_value)
        mock_pack.assert_called_once_with(
            'someMethod', ('a', 1, 2), set_type_attrs=True)
        mock_create.assert_called_once_with(
            zeep_wrapper.zeep_client.service, 'someMethod', 1, 2, 3,
            _soapheaders=mock_get_headers.return_value)

  def testBadCacheType(self):
    header_handler = mock.Mock()
    packer = mock.Mock()

    with mock_zeep_client(), \
        self.assertRaises(googleads.errors.GoogleAdsValueError):
      googleads.common.ZeepServiceProxy(
          'http://abc', header_handler, packer,
          self.empty_proxy_config, self.timeout_100, self.fake_version,
          cache='not_a_zeep_cache')

  def testSchemaHelperBadCacheType(self):
    with self.assertRaises(googleads.errors.GoogleAdsValueError):
      googleads.common.ZeepSchemaHelper(None, None, None, None, 'not_zeep')

  def testAllowsNoCache(self):
    header_handler = mock.Mock()
    packer = mock.Mock()

    with mock_zeep_client(),\
        mock.patch('googleads.common._ZeepProxyTransport') as zeep_transport:
      googleads.common.ZeepServiceProxy(
          'http://abc', header_handler, packer,
          self.empty_proxy_config, self.timeout_100, self.fake_version,
          cache=googleads.common.ZeepServiceProxy.NO_CACHE)

      zeep_transport.assert_called_once_with(
          self.timeout_100, self.empty_proxy_config,
          googleads.common.ZeepServiceProxy.NO_CACHE)

  def testFaultWithErrors(self):
    detail = mock.Mock()
    fault = zeep.exceptions.Fault('message', detail=detail)
    header_handler = mock.Mock()
    packer = mock.Mock()

    with mock_zeep_client():
      zeep_wrapper = googleads.common.ZeepServiceProxy(
          'http://abc', header_handler, packer,
          googleads.common.ProxyConfig(), 100, self.fake_version)

      zeep_wrapper.zeep_client.service['mymethod'].side_effect = fault
      zeep_wrapper._GetBindingNamespace = mock.Mock()

      with self.assertRaises(googleads.errors.GoogleAdsServerFault) as e:
        zeep_wrapper.mymethod()

    self.assertEqual(e.exception.document, detail)
    self.assertIn('message', str(e.exception))

  def testIsBase64(self):
    result = googleads.common.ZeepServiceProxy._IsBase64('abcd')
    self.assertTrue(result)

  def testIsBase64Exception(self):
    result = googleads.common.ZeepServiceProxy._IsBase64('abc')
    self.assertFalse(result)

  def testIsBase64DataBad(self):
    result = googleads.common.ZeepServiceProxy._IsBase64('%%%%')
    self.assertFalse(result)


class TestZeepArgumentPacking(unittest.TestCase):

  def setUp(self):
    header_handler = mock.Mock()
    self.fake_version = 'ignored'
    wsdl_path = os.path.join(
        TEST_DIR, 'test_data/ad_manager_report_service.xml')
    self.zeep_client = googleads.common.ZeepServiceProxy(
        wsdl_path, header_handler, None, googleads.common.ProxyConfig(), 100,
        self.fake_version)

  def testPackArgumentsPrimitivesOnly(self):
    result = self.zeep_client._PackArguments('getReportJobStatus', [5])
    six.assertCountEqual(self, result, [5])

  def testPackArgumentsWithSimpleDict(self):
    opts = {
        'exportFormat': 'CSV',
        'includeReportProperties': False,
        'includeTotalsRow': True,
        'useGzipCompression': False}
    result = self.zeep_client._PackArguments(
        'getReportDownloadUrlWithOptions', [123, opts])
    self.assertEqual(result[0], 123)
    self.assertEqual(result[1].exportFormat, 'CSV')
    self.assertEqual(result[1].includeTotalsRow, True)

  def testPackArgumentsWithCustomTypeAndList(self):
    data = {
        'reportQuery': {
            'adUnitView': 'HIERARCHICAL',
            'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS'],
            'dateRangeType': 'LAST_WEEK',
            'dimensions': ['DATE', 'AD_UNIT_NAME'],
            'statement': {
                'query': 'WHERE PARENT_AD_UNIT_ID = :parentAdUnitId',
                'values': [{
                    'key': 'parentAdUnitId',
                    'value': {
                        'value': 606389, 'xsi_type': 'NumberValue'}}]}}}
    result = self.zeep_client._PackArguments('runReportJob', [data])
    self.assertEqual(result[0].reportQuery.adUnitView, 'HIERARCHICAL')
    self.assertEqual(result[0].reportQuery.dimensions[1], 'AD_UNIT_NAME')
    number_value = result[0].reportQuery.statement.values[0].value
    number_type = self.zeep_client.zeep_client.get_type('ns0:NumberValue')
    self.assertEqual(type(number_value), number_type._value_class)

  def testPackArgumentsLooksThroughSoapElements(self):
    map_type = self.zeep_client.zeep_client.get_type('ns0:String_ValueMapEntry')
    string_type = self.zeep_client.zeep_client.get_type('ns0:TextValue')

    element = self.zeep_client.zeep_client.get_type('ns0:ReportQuery')()
    element.statement = self.zeep_client.zeep_client.get_type('ns0:Statement')()
    element.statement.values = [{
        'key': 'Key1',
        'value': {
            'xsi_type': 'NumberValue',
            'value': 10
        }
    }, map_type(key='Key2', value=string_type(value='abc'))]

    result = self.zeep_client._PackArguments(
        'runReportJob', [{'reportQuery': element}])
    result_values = result[0].reportQuery.statement.values
    self.assertIsInstance(result_values[0], zeep.xsd.CompoundValue)
    self.assertIsInstance(result_values[1], zeep.xsd.CompoundValue)

  def testPackArgumentsWithCustomPacker(self):
    class CustomPacker(googleads.common.SoapPacker):

      def __init__(self):
        self._version = CURRENT_VERSION

      @classmethod
      def Pack(cls, obj, version):
        if isinstance(obj, numbers.Number):
          return '50'
        return obj

    self.zeep_client._packer = CustomPacker
    result = self.zeep_client._PackArguments('getReportJobStatus', [5])[0]
    self.assertEqual(result, '50')

  def testPackArgumentsBase64Warning(self):
    image_type = self.zeep_client.zeep_client.get_type('ns0:Image')
    b64_type = image_type.elements[0][1]
    data = 'abcd'  # This is valid base64

    with mock.patch('googleads.common._logger'):
      self.zeep_client._PackArgumentsHelper(b64_type, data, False)
      self.assertTrue(len(googleads.common._logger.warn.mock_calls))

  def testPackArgumentsMultipleSchemas(self):
    header_handler = mock.Mock()

    wsdl_path = os.path.join(
        TEST_DIR, 'test_data/traffic_estimator_service.xml')
    zeep_client = googleads.common.ZeepServiceProxy(
        wsdl_path, header_handler, None, googleads.common.ProxyConfig(), 100,
        self.fake_version)

    element = zeep_client.zeep_client.get_type('ns0:Criterion')
    data = {'xsi_type': 'Location', 'id': '2840'}

    result = zeep_client._PackArgumentsHelper(element, data, False)
    self.assertEqual(result.id, '2840')

  def testPackArgumentsBadType(self):
    element = self.zeep_client.zeep_client.get_type('ns0:Image')
    data = {'xsi_type': 'nope'}
    with self.assertRaises(zeep.exceptions.LookupError):
      self.zeep_client._PackArgumentsHelper(element, data, False)


class SudsServiceProxyTest(unittest.TestCase):
  """Tests for the googleads.common.SudsServiceProxy class."""

  def setUp(self):
    self.fake_version = 'ignored'

  def testCreateSudsClient(self):
    class MyCache(suds.cache.Cache):
      pass

    cache = MyCache()
    header_handler = mock.Mock()
    packer = mock.Mock()
    proxy_config = mock.Mock()

    with mock.patch('googleads.common.suds.client.Client') as mock_suds_client:
      mock_suds_client.return_value = 'suds_client'

      with mock.patch('googleads.common.LoggingMessagePlugin') as mock_logging:
        mock_logging.return_value = 'logging'

        with mock.patch('googleads.common'
                        '._SudsProxyTransport') as mock_transport:
          mock_transport.return_value = 'transport'

          suds_wrapper = googleads.common.SudsServiceProxy(
              'https://endpoint', header_handler, packer, proxy_config,
              1000, self.fake_version, cache)

          mock_transport.assert_called_once_with(1000, proxy_config)
          mock_suds_client.assert_called_once_with(
              'https://endpoint', timeout=1000, cache=cache,
              transport='transport', plugins=['logging'])
          self.assertEqual(suds_wrapper.suds_client, 'suds_client')

  @contextmanager
  def mock_suds_api(self):
    with mock.patch('googleads.common._SudsProxyTransport'), \
        mock.patch('googleads.common.suds.client.Client') as mock_suds_client:
      yield mock_suds_client

  def testSudsErrorRaisesGoogleError(self):
    with self.mock_suds_api() as mock_suds_client:
      mock_suds_client.side_effect = suds.transport.TransportError(None, None)
      with self.assertRaises(googleads.errors.GoogleAdsSoapTransportError):
        googleads.common.SudsServiceProxy(
            'https://endpoint', None, None, None, 1000, None)

  def testSchemaHelperRaisesGoogleError(self):
    with self.mock_suds_api() as mock_suds_client:
      mock_suds_client.side_effect = suds.transport.TransportError(None, None)

      with self.assertRaises(googleads.errors.GoogleAdsSoapTransportError):
        googleads.common.SudsSchemaHelper(None, None, None, 100, None)


  def testGetMethod(self):
    header_handler = mock.Mock()
    wrapped_method = mock.Mock()
    wrapped_method.return_value = 'wrap_result'

    with self.mock_suds_api() as mock_suds_client_class:
      mock_suds_client = mock.MagicMock()
      mock_suds_client_class.return_value = mock_suds_client

      suds_wrapper = googleads.common.SudsServiceProxy(
          'https://endpoint', header_handler, None, None, 1000,
          self.fake_version, None
      )

      with mock.patch.object(suds_wrapper, '_CreateMethod') as mock_create:
        mock_create.return_value = wrapped_method

        services_dict = {'method1': True}
        suds_contains_method = (mock_suds_client.wsdl.services[0].ports[0]
                                .methods.__contains__)
        suds_contains_method.side_effect = services_dict.__contains__
        result = suds_wrapper.method1()
        self.assertEqual(result, 'wrap_result')

  @contextmanager
  def get_suds_api_with_mocked_method(self, mock_method):
    header_handler = mock.Mock()
    with self.mock_suds_api() as mock_suds_client_class:
      mock_suds_client = mock.MagicMock()
      mock_suds_client_class.return_value = mock_suds_client

      suds_wrapper = googleads.common.SudsServiceProxy(
          'https://endpoint', header_handler, None, None, 1000, None
      )
      with mock.patch('googleads.common._ExtractResponseSummaryFields'):
        with mock.patch.object(suds_wrapper,
                               '_WsdlHasMethod') as mock_has_method:
          mock_has_method.return_value = True

          suds_wrapper.suds_client.service.method1 = mock_method
          suds_wrapper._method_proxies['method1'] = (
              suds_wrapper._CreateMethod('method1'))

          yield suds_wrapper

  def testNoDetailError(self):
    mock_method = mock.Mock()
    mock_document = mock.Mock()

    class MockFault(object):
      faultstring = 'abc'

    mock_method.side_effect = suds.WebFault(MockFault(), mock_document)

    with self.get_suds_api_with_mocked_method(mock_method) as suds_wrapper:
      with self.assertRaises(googleads.errors.GoogleAdsServerFault) as e:
        suds_wrapper.method1()

    self.assertEqual(len(e.exception.errors), 0)
    self.assertEqual(e.exception.document, mock_document)
    self.assertIn('abc', str(e.exception))

  def testEmptyListError(self):
    mock_method = mock.Mock()
    mock_document = mock.Mock()

    class MockFault(object):
      faultstring = 'abc'
      detail = mock.Mock()

      def __init__(self):
        self.detail.ApiExceptionFault.errors = None

    mock_fault = MockFault()

    mock_method.side_effect = suds.WebFault(mock_fault, mock_document)

    with self.get_suds_api_with_mocked_method(mock_method) as suds_wrapper:
      with self.assertRaises(googleads.errors.GoogleAdsServerFault) as e:
        suds_wrapper.method1()
    self.assertEqual(len(e.exception.errors), 0)
    self.assertEqual(e.exception.document, mock_document)
    self.assertIn('abc', str(e.exception))

  def testFaultWithErrors(self):
    mock_method = mock.Mock()
    mock_document = mock.Mock()

    class MockFault(object):
      faultstring = 'abc'
      detail = mock.Mock()

      def __init__(self):
        self.detail.ApiExceptionFault.errors = ['1', '2', '3']

    mock_fault = MockFault()

    mock_method.side_effect = suds.WebFault(mock_fault, mock_document)

    with self.get_suds_api_with_mocked_method(mock_method) as suds_wrapper:
      with self.assertRaises(googleads.errors.GoogleAdsServerFault) as e:
        suds_wrapper.method1()
    six.assertCountEqual(self, e.exception.errors, ['1', '2', '3'])
    self.assertEqual(e.exception.document, mock_document)
    self.assertIn('abc', str(e.exception))

  def testGetRequestXML(self):
    mock_method = mock.Mock()
    mock_method.return_value.envelope = '<a></a>'

    with self.get_suds_api_with_mocked_method(mock_method) as suds_wrapper, \
        mock.patch.object(suds_wrapper, 'SetHeaders'):
      ops = ['abc', '123']
      result = suds_wrapper.GetRequestXML('method1', ops)
      toggle_calls = [mock.call(nosend=True), mock.call(nosend=False)]
      suds_wrapper.suds_client.set_options.assert_has_calls(toggle_calls)
      self.assertEqual(result.tag, 'a')

  def testCreateSoapElementForType(self):
    with self.mock_suds_api():
      suds_wrapper = googleads.common.SudsServiceProxy(
          'https://endpoint', None, None, None, 1000, self.fake_version, None)
      suds_wrapper.suds_client.factory.create.return_value = 'result'

      result = suds_wrapper.CreateSoapElementForType('MyType')
      self.assertEqual(result, 'result')

  def testSetHeaders(self):
    with self.mock_suds_api():
      suds_wrapper = googleads.common.SudsServiceProxy(
          'https://endpoint', None, None, None, 1000, self.fake_version, None)

      suds_wrapper.SetHeaders('soap', 'http')
      suds_wrapper.suds_client.set_options.assert_called_once_with(
          soapheaders='soap', headers='http')

  def testBadCache(self):
    with self.mock_suds_api(), \
        self.assertRaises(googleads.errors.GoogleAdsValueError):
      googleads.common.SudsServiceProxy(
          'https://endpoint', None, None, None, 1000, 'not_a_suds_cache',
          self.fake_version)

  def testSchemaHelperBadCache(self):
    with self.assertRaises(googleads.errors.GoogleAdsValueError):
      googleads.common.SudsSchemaHelper(None, None, None, None, 'not_cache')


class LoggingMessagePluginTest(unittest.TestCase):
  """Tests for the googleads.common.LoggingMessagePlugin class."""

  def setUp(self):
    self.logging_message_plugin = googleads.common.LoggingMessagePlugin()

  def testMarshalled(self):
    envelope = 'envelope'
    marshalled_context = mock.Mock()
    marshalled_context.envelope = envelope

    with mock.patch('googleads.common._logger') as mock_logger:
      mock_logger.isEnabledFor.return_value = True
      with mock.patch(
          'googleads.common._ExtractRequestSummaryFields') as mk_ext:
        self.logging_message_plugin.marshalled(marshalled_context)
        mk_ext.assert_called_once_with(envelope)

  def testParsed(self):
    reply = 'reply'
    parsed_context = mock.Mock()
    parsed_context.reply = reply

    with mock.patch('googleads.common._logger') as mock_logger:
      mock_logger.isEnabledFor.return_value = True
      with mock.patch(
          'googleads.common._ExtractResponseSummaryFields') as mk_ext:
        self.logging_message_plugin.parsed(parsed_context)
        mk_ext.assert_called_once_with(reply)


class ProxyConfigTest(unittest.TestCase):
  """Tests for the googleads.common.ProxyConfig class."""

  def setUp(self):
    self.cafile = os.path.join(os.path.dirname(__file__), 'test_data/test.crt')
    self.proxy_no_credentials = 'http://host1:port1'
    self.proxy_with_credentials = 'http://username:password@host2:port2'

  def testBuildOpenerWithConfig(self):
    proxy_config = googleads.common.ProxyConfig(
        https_proxy=self.proxy_no_credentials)

    with mock.patch('%s.build_opener' % URL_REQUEST_PATH) as mck_build_opener:
      with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as mck_https_hndlr:
        with mock.patch('%s.ProxyHandler' % URL_REQUEST_PATH) as mck_prxy_hndlr:
          mck_https_hndlr_instance = mock.Mock()
          mck_https_hndlr.return_value = mck_https_hndlr_instance
          mck_prxy_hndlr_instance = mock.Mock()
          mck_prxy_hndlr.return_value = mck_prxy_hndlr_instance
          proxy_config.BuildOpener()
          mck_build_opener.assert_called_once_with(
              *[mck_https_hndlr_instance, mck_prxy_hndlr_instance])

  def testBuildOpenerWithDefaultConfig(self):
    proxy_config = googleads.common.ProxyConfig()

    with mock.patch('%s.build_opener' % URL_REQUEST_PATH) as mck_build_opener:
      with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as mock_https_hndlr:
        mock_https_hndlr_instance = mock.Mock
        mock_https_hndlr.return_value = mock_https_hndlr_instance
        proxy_config.BuildOpener()
        mck_build_opener.assert_called_once_with(*[mock_https_hndlr_instance])

  def testProxyConfigGetHandlersWithNoProxyOrSSLContext(self):
    proxy_config = googleads.common.ProxyConfig()
    with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
      https_handler_instance = mock.Mock()
      https_handler.return_value = https_handler_instance

      transport = googleads.common._SudsProxyTransport(0, proxy_config)
      self.assertIn(https_handler_instance, transport.handlers)

  def testProxyConfigGetHandlersWithProxy(self):
    with mock.patch('%s.ProxyHandler' % URL_REQUEST_PATH) as proxy_handler:
      proxy_handler_instance = mock.Mock()
      proxy_handler.return_value = proxy_handler_instance
      proxy_config = googleads.common.ProxyConfig(
          http_proxy=self.proxy_no_credentials)
      with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
        https_handler_instance = mock.Mock()
        https_handler.return_value = https_handler_instance

        transport = googleads.common._SudsProxyTransport(0, proxy_config)
        self.assertEqual(transport.handlers,
                         [https_handler_instance, proxy_handler_instance])
        proxy_handler.assert_called_once_with(
            {'http': self.proxy_no_credentials})

  def testProxyConfigGetHandlersWithProxyAndSLLContext(self):
    with mock.patch('googleads.common.ProxyConfig._InitSSLContext') as ssl_ctxt:
      ssl_ctxt.return_value = 'CONTEXT'
      with mock.patch('%s.ProxyHandler' % URL_REQUEST_PATH) as proxy_handler:
        proxy_handler.return_value = mock.Mock()
        with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
          https_handler.return_value = mock.Mock()

          proxy_config = googleads.common.ProxyConfig(
              https_proxy=self.proxy_no_credentials)
          transport = googleads.common._SudsProxyTransport(0, proxy_config)
          self.assertEqual(transport.handlers,
                           [https_handler.return_value,
                            proxy_handler.return_value])
          proxy_handler.assert_called_once_with(
              {'https': self.proxy_no_credentials})
          https_handler.assert_called_once_with(
              context=ssl_ctxt.return_value)

  def testProxyConfigWithNoProxy(self):
    proxy_config = googleads.common.ProxyConfig()
    self.assertEqual(proxy_config.proxies, {})
    self.assertIsInstance(
        proxy_config.ssl_context, ssl.SSLContext)

  def testProxyConfigWithHTTPProxy(self):
    proxy_config = googleads.common.ProxyConfig(
        http_proxy=self.proxy_no_credentials)
    self.assertEqual(proxy_config.proxies, {'http': self.proxy_no_credentials})
    self.assertIsInstance(
        proxy_config.ssl_context, ssl.SSLContext)

  def testProxyConfigWithHTTPSProxy(self):
    proxy_config = googleads.common.ProxyConfig(
        https_proxy=self.proxy_with_credentials,
        cafile=self.cafile)
    self.assertEqual(proxy_config.proxies, {
        'https': self.proxy_with_credentials})
    self.assertIsInstance(
        proxy_config.ssl_context, ssl.SSLContext)
    self.assertEqual(proxy_config.cafile, self.cafile)
    self.assertEqual(proxy_config.disable_certificate_validation, False)

  def testProxyConfigWithHTTPAndHTTPSProxy(self):
    proxy_config = googleads.common.ProxyConfig(
        http_proxy=self.proxy_with_credentials,
        https_proxy=self.proxy_no_credentials,
        disable_certificate_validation=True)
    self.assertEqual(proxy_config.proxies, {
        'http': self.proxy_with_credentials,
        'https': self.proxy_no_credentials})

    self.assertIsInstance(proxy_config.ssl_context, ssl.SSLContext)
    self.assertEqual(proxy_config.cafile, None)
    self.assertEqual(proxy_config.disable_certificate_validation, True)


class MockHeaders(object):

  def __init__(self, d):
    self.dict = d

    # If testing on Python 3, add get method to better mimic the
    # http.client.HTTPMessage behavior.
    if six.PY3:
      def py3_get(s):
        return self.dict.get(s)
      self.get = py3_get


class TestSudsRequestPatcher(unittest.TestCase):

  def testInflateSuccessfulRequestIfGzipped(self):
    with mock.patch('suds.transport.http.HttpTransport.getcookies'):
      with mock.patch('%s.OpenerDirector.open' % URL_REQUEST_PATH) as mock_open:
        with mock.patch('gzip.GzipFile.read') as mock_read:
          resp_fp = six.BytesIO()
          resp_fp.write(b'abc')
          resp_fp.flush()
          resp_fp.seek(0)
          resp = six.moves.urllib.response.addinfourl(
              resp_fp, MockHeaders({'content-encoding': 'gzip'}),
              'https://example.com', code=200)
          mock_open.return_value = resp

          req = suds.transport.Request('https://example.com',
                                       message='hello world')
          suds.transport.http.HttpTransport().send(req)
          mock_read.assert_called_once()

  def testInflateFailedRequestIfGzipped(self):

    with mock.patch('suds.transport.http.HttpTransport.getcookies'):
      with mock.patch('%s.OpenerDirector.open' % URL_REQUEST_PATH) as mock_open:
        with mock.patch('gzip.GzipFile') as mock_gzip:
          gzip_instance_mock = mock.MagicMock
          mock_gzip.return_value = gzip_instance_mock
          resp_fp = six.BytesIO()
          resp_fp.write(b'abc')
          resp_fp.flush()
          resp_fp.seek(0)
          resp = six.moves.urllib.response.addinfourl(
              resp_fp, MockHeaders({'content-encoding': 'gzip'}),
              'https://example.com', code=200)

          def fail_to_open(*args, **kwargs):
            raise six.moves.urllib.error.HTTPError(
                'https://example.com', 500, 'oops!',
                {'content-encoding': 'gzip'}, resp)
          mock_open.side_effect = fail_to_open

          req = suds.transport.Request('https://example.com',
                                       message='hello world')
          with self.assertRaises(suds.transport.TransportError) as exc:
            suds.transport.http.HttpTransport().send(req)
          self.assertEqual(exc.exception.fp, gzip_instance_mock)


if __name__ == '__main__':
  unittest.main()
