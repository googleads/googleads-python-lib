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


import numbers
import os
import ssl
import unittest
import warnings

from pyfakefs import fake_filesystem
from pyfakefs import fake_tempfile
import mock
import six
import suds
import yaml

import googleads.common
import googleads.errors
import googleads.oauth2
from . import testing


URL_REQUEST_PATH = 'urllib2' if six.PY2 else 'urllib.request'


class CommonTest(testing.CleanUtilityRegistryTestCase):
  """Tests for the googleads.common module."""

  # Dictionaries with all the required OAuth2 keys
  _OAUTH_INSTALLED_APP_DICT = {'client_id': 'a', 'client_secret': 'b',
                               'refresh_token': 'c'}
  _OAUTH_SERVICE_ACCT_DICT = {
      'service_account_email': 'service_account@example.com',
      'path_to_private_key_file': '/test/test.p12',
      'delegated_account': 'delegated_account@example.com'}

  def setUp(self):
    self.filesystem = fake_filesystem.FakeFilesystem()
    self.tempfile = fake_tempfile.FakeTempfileModule(self.filesystem)
    self.fake_open = fake_filesystem.FakeFileOpen(self.filesystem)
    self.host1 = 'h1'
    self.port1 = 1
    self.host2 = 'h2'
    self.port2 = 2
    self.uplink_host = '127.0.0.1'
    self.uplink_port = 999
    self.username = 'username'
    self.password = 'password'
    self.test1_name = 'Test1'
    self.test2_name = 'Test2'
    self.test2_version = 'testing'

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
                            googleads.common.ENABLE_COMPRESSION_KEY: False},
                           rval)
          self.assertTrue(googleads.common._utility_registry._enabled)

    # Optional logging configuration key is present.
    logging_config = {'foo': 'bar'}
    yaml_fname = self._CreateYamlFile(
        {'one': {'needed': 'd', 'keys': 'e', 'other': 'f'},
         googleads.common._LOGGING_KEY: logging_config},
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
                              googleads.common.ENABLE_COMPRESSION_KEY: False},
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
                          googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)
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

  def testExtractRequestSummaryFieldsForDfp(self):
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

  def testLoadFromString_missingPartialServiceAcctOAuthCredential(self):
    yaml_doc = self._CreateYamlDoc({'woo': {}}, 'woo', {
        'service_account_email': 'abc@xyz.com'})
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
                      googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)

  def testLoadFromString_passesWithHTTPAndHTTPSProxy(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'http_proxy': {'host': self.host1, 'port': self.port1},
             'https_proxy': {'host': self.host2, 'port': self.port2}}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          with mock.patch('googleads.common.ProxyConfig.Proxy') as proxy:
            proxy.return_value = mock.Mock()
            rval = googleads.common.LoadFromString(
                yaml_doc, 'adwords', [], [])
    proxy.assert_has_calls([mock.call(self.host1, self.port1,
                                      username=None, password=None),
                            mock.call(self.host2, self.port2,
                                      username=None, password=None)])
    proxy_config.assert_called_once_with(
        http_proxy=proxy.return_value,
        https_proxy=proxy.return_value, cafile=None,
        disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)

  def testHTTPSProxyExtendsSSLSockTimeout(self):
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient'):
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('suds.transport.http.'
                        'HttpTransport.__init__') as mock_transport:
          proxy_config = googleads.common.ProxyConfig()
          proxy_config.GetSudsProxyTransport()
          mock_transport.assert_called_once()
          # 90 is the default, don't expect an exact value so that we can change
          # the timeout in the code without returning here.
          self.assertGreater(mock_transport.call_args_list[0][1]['timeout'], 90)

  def testLoadFromString_passesWithHTTPProxy(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'http_proxy': {'host': self.host1, 'port': self.port1}}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          with mock.patch('googleads.common.ProxyConfig.Proxy') as proxy:
            proxy.return_value = mock.Mock()
            rval = googleads.common.LoadFromString(
                yaml_doc, 'adwords', [], [])

    proxy.assert_called_once_with(self.host1, self.port1,
                                  username=None, password=None)
    proxy_config.assert_called_once_with(http_proxy=proxy.return_value,
                                         https_proxy=None, cafile=None,
                                         disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)

  def testLoadFromString_passesWithHTTPProxyLogin(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'http_proxy': {'host': self.host1, 'port': self.port1,
                            'username': self.username,
                            'password': self.password}}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          with mock.patch('googleads.common.ProxyConfig.Proxy') as proxy:
            proxy.return_value = mock.Mock()
            rval = googleads.common.LoadFromString(
                yaml_doc, 'adwords', [], [])

    proxy.assert_called_once_with(self.host1, self.port1,
                                  username=self.username,
                                  password=self.password)
    proxy_config.assert_called_once_with(http_proxy=proxy.return_value,
                                         https_proxy=None, cafile=None,
                                         disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)

  def testLoadFromString_passesWithHTTPSProxy(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'https_proxy': {'host': self.host1, 'port': self.port1}}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          with mock.patch('googleads.common.ProxyConfig.Proxy') as proxy:
            proxy.return_value = mock.Mock()
            rval = googleads.common.LoadFromString(
                yaml_doc, 'adwords', [], [])

    proxy.assert_called_once_with(self.host1, self.port1,
                                  username=None, password=None)
    proxy_config.assert_called_once_with(http_proxy=None,
                                         https_proxy=proxy.return_value,
                                         cafile=None,
                                         disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)

  def testLoadFromString_passesWithHTTPSProxyLogin(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'https_proxy': {'host': self.host1, 'port': self.port1,
                             'username': self.username,
                             'password': self.password}}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)
    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          with mock.patch('googleads.common.ProxyConfig.Proxy') as proxy:
            proxy.return_value = mock.Mock()
            rval = googleads.common.LoadFromString(
                yaml_doc, 'adwords', [], [])

    proxy.assert_called_once_with(self.host1, self.port1,
                                  username=self.username,
                                  password=self.password)
    proxy_config.assert_called_once_with(http_proxy=None,
                                         https_proxy=proxy.return_value,
                                         cafile=None,
                                         disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        'a', 'b', 'c', proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)

  def testLoadFromString_failsWithMisconfiguredProxy(self):
    yaml_doc = self._CreateYamlDoc(
        {'adwords': {},
         'proxy_config': {
             'http_proxy': {'host': self.host1}}},
        insert_oauth2_key='adwords', oauth_dict=self._OAUTH_INSTALLED_APP_DICT)

    with mock.patch('googleads.oauth2.GoogleRefreshTokenClient'):
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          with mock.patch('googleads.common.ProxyConfig.Proxy') as proxy:
            proxy.return_value = mock.Mock()
            self.assertRaises(googleads.errors.GoogleAdsValueError,
                              googleads.common.LoadFromString,
                              yaml_doc, 'adwords', [], [])

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
                            googleads.common.ENABLE_COMPRESSION_KEY: False},
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
                            googleads.common.ENABLE_COMPRESSION_KEY: False},
                           rval)
          self.assertTrue(googleads.common._utility_registry._enabled)

  def testLoadFromString_serviceAccountWithDeprecatedOAuth2Client(self):
    dfp_scope = googleads.oauth2.GetAPIScope('dfp')
    # No optional keys present.
    yaml_doc = self._CreateYamlDoc(
        {'dfp': {'needed': 'd', 'keys': 'e'}},
        insert_oauth2_key='dfp', oauth_dict=self._OAUTH_SERVICE_ACCT_DICT)
    with mock.patch(
        'googleads.oauth2.GoogleServiceAccountClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'dfp', ['needed', 'keys'], ['other'])

    proxy_config.assert_called_once_with(
        http_proxy=None, https_proxy=None, cafile=None,
        disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        dfp_scope, client_email='service_account@example.com',
        key_file='/test/test.p12', sub='delegated_account@example.com',
        proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      'needed': 'd', 'keys': 'e',
                      googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)
    self.assertTrue(googleads.common._utility_registry._enabled)

    # The optional key is present.
    yaml_doc = self._CreateYamlDoc(
        {'dfp': {'needed': 'd', 'keys': 'e', 'other': 'f'}}, 'dfp',
        self._OAUTH_SERVICE_ACCT_DICT)
    with mock.patch(
        'googleads.oauth2.GoogleServiceAccountClient') as mock_client:
      with mock.patch('googleads.common.open', self.fake_open, create=True):
        with mock.patch('googleads.common.ProxyConfig') as proxy_config:
          proxy_config.return_value = mock.Mock()
          rval = googleads.common.LoadFromString(
              yaml_doc, 'dfp', ['needed', 'keys'], ['other'])

    proxy_config.assert_called_once_with(
        http_proxy=None, https_proxy=None, cafile=None,
        disable_certificate_validation=False)
    mock_client.assert_called_once_with(
        dfp_scope, client_email='service_account@example.com',
        key_file='/test/test.p12', sub='delegated_account@example.com',
        proxy_config=proxy_config.return_value)
    self.assertEqual({'oauth2_client': mock_client.return_value,
                      'proxy_config': proxy_config.return_value,
                      'needed': 'd', 'keys': 'e', 'other': 'f',
                      googleads.common.ENABLE_COMPRESSION_KEY: False}, rval)
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
                            googleads.common.ENABLE_COMPRESSION_KEY: False},
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
                googleads.common.ENABLE_COMPRESSION_KEY: False
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
    self.assertIsInstance(rval, list)
    self.assertEqual('Sales', rval[0].name)
    self.assertIsInstance(rval[0].id, suds.null)
    self.assertEqual({'b': 'c'}, rval[0].metadata.a)
    self.assertEqual({'i do not have': 'a type'}, rval[1])
    self.assertEqual(
        [{'xsi_type': 'EliteCampaign', 'name': 'Sales', 'id': None,
          'metadata': {'xsi_type': 'metadata', 'a': {'b': 'c'}}},
         {'i do not have': 'a type'}], input_list)

  def testPackForSuds_applyCustomPacker(self):
    class CustomPacker(googleads.common.SudsPacker):
      @classmethod
      def Pack(cls, obj):
        if isinstance(obj, numbers.Number):
          return {'xsi_type': 'Integer', 'value': str(int(obj))}
        return obj

    factory = mock.Mock()
    factory.create.return_value = mock.MagicMock()
    factory.create.return_value.__iter__.return_value = iter(
        [('Number.Type', 0), ('value', 1)])
    number = 3.14159265358979323846264

    rval = googleads.common._PackForSuds(number, factory, CustomPacker)
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


class SudsServiceProxyTest(unittest.TestCase):
  """Tests for the googleads.common.SudsServiceProxy class."""

  def setUp(self):
    self.header_handler = mock.Mock()
    self.port = mock.Mock()
    self.port.methods = ('SoapMethod',)
    self.services = mock.Mock()
    self.services.ports = [self.port]
    self.client = mock.Mock()
    self.client.wsdl.services = [self.services]
    self.datetime_packer = mock.Mock()
    self.suds_service_wrapper = googleads.common.SudsServiceProxy(
        self.client, self.header_handler, self.datetime_packer)

  def testSudsServiceProxy(self):
    self.assertEqual(self.suds_service_wrapper.SoapMethod,
                     self.suds_service_wrapper._method_proxies['SoapMethod'])
    self.assertEqual(self.suds_service_wrapper.NotSoapMethod,
                     self.client.service.NotSoapMethod)

    with mock.patch('googleads.common._PackForSuds') as mock_pack_for_suds:
      mock_pack_for_suds.return_value = 'modified_test'
      self.suds_service_wrapper.SoapMethod('test')
      mock_pack_for_suds.assert_called_once_with('test', self.client.factory,
                                                 self.datetime_packer)

    self.client.service.SoapMethod.assert_called_once_with('modified_test')
    self.header_handler.SetHeaders.assert_called_once_with(self.client)


class HeaderHandlerTest(unittest.TestCase):
  """Tests for the googleads.common.HeaderHeader class."""

  def testSetHeaders(self):
    """For coverage."""
    self.assertRaises(
        NotImplementedError, googleads.common.HeaderHandler().SetHeaders,
        mock.Mock())


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
  """Tests fpr the googleads.common.ProxyConfig class."""

  def setUp(self):
    self.proxy_host1 = 'host1'
    self.proxy_port1 = 'port1'
    self.proxy_host2 = 'host2'
    self.proxy_port2 = 'port2'
    self.username = 'username'
    self.password = 'password'
    self.cafile = os.path.join(os.path.dirname(__file__), 'test_data/test.crt')

    self.proxy_no_credentials = googleads.common.ProxyConfig.Proxy(
        self.proxy_host1, self.proxy_port1)

    self.proxy_with_credentials = googleads.common.ProxyConfig.Proxy(
        self.proxy_host2, self.proxy_port2, username=self.username,
        password=self.password)

  def testProxyToStringWithCredentials(self):
    proxy = googleads.common.ProxyConfig.Proxy(
        self.proxy_host1, self.proxy_port1, username=self.username,
        password=self.password)
    self.assertEqual(str(proxy),
                     '%s:%s@%s:%s' % (self.username, self.password,
                                      self.proxy_host1,
                                      self.proxy_port1))

  def testProxyToStringWithoutCredentials(self):
    proxy = googleads.common.ProxyConfig.Proxy(
        self.proxy_host2, self.proxy_port2)
    self.assertEqual(str(proxy),
                     '%s:%s' % (self.proxy_host2, self.proxy_port2))

  def testProxyToStringWithOnlyUsername(self):
    proxy = googleads.common.ProxyConfig.Proxy(
        self.proxy_host1, self.proxy_port1, username=self.username)
    self.assertEqual(str(proxy),
                     '%s:@%s:%s' % (self.username, self.proxy_host1,
                                    self.proxy_port1))

  def testProxyConfigGetHandlersWithNoProxyOrSSLContext(self):
    proxy_config = googleads.common.ProxyConfig()
    with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
      https_handler_instance = mock.Mock()
      https_handler.return_value = https_handler_instance
      self.assertIn(https_handler_instance, proxy_config.GetHandlers())

  def testProxyConfigGetHandlersWithProxy(self):
    http_proxy = googleads.common.ProxyConfig.Proxy(self.proxy_host1,
                                                    self.proxy_port1)
    with mock.patch('%s.ProxyHandler' % URL_REQUEST_PATH) as proxy_handler:
      proxy_handler_instance = mock.Mock()
      proxy_handler.return_value = proxy_handler_instance
      proxy_config = googleads.common.ProxyConfig(http_proxy=http_proxy)
      with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
        https_handler_instance = mock.Mock()
        https_handler.return_value = https_handler_instance
        self.assertEqual(proxy_config.GetHandlers(),
                         [https_handler_instance, proxy_handler_instance])
        proxy_handler.assert_called_once_with(
            {'http': '%s' % str(http_proxy)})

  def testProxyConfigGetHandlersWithProxyAndSLLContext(self):
    https_proxy = googleads.common.ProxyConfig.Proxy(self.proxy_host1,
                                                     self.proxy_port1)
    with mock.patch('googleads.common.ProxyConfig._InitSSLContext') as ssl_ctxt:
      ssl_ctxt.return_value = 'CONTEXT'
      with mock.patch('%s.ProxyHandler' % URL_REQUEST_PATH) as proxy_handler:
        proxy_handler.return_value = mock.Mock()
        with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
          https_handler.return_value = mock.Mock()
          proxy_config = googleads.common.ProxyConfig(https_proxy=https_proxy)
          self.assertEqual(proxy_config.GetHandlers(),
                           [https_handler.return_value,
                            proxy_handler.return_value])
          proxy_handler.assert_called_once_with(
              {'https': '%s' % str(https_proxy)})
          https_handler.assert_called_once_with(
              context=ssl_ctxt.return_value)

  def testProxyConfigWithNoProxy(self):
    proxy_config = googleads.common.ProxyConfig()
    self.assertEqual(proxy_config.proxy_info, None)

    with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
      https_handler_instance = mock.Mock()
      https_handler.return_value = https_handler_instance
      self.assertEqual(proxy_config.GetHandlers(),
                       [https_handler_instance])
      self.assertIsInstance(
          proxy_config._ssl_context, ssl.SSLContext)

    with mock.patch('googleads.common.ProxyConfig._SudsProxyTransport') as t:
      t.return_value = mock.Mock()
      with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
        https_handler_instance = mock.Mock()
        https_handler.return_value = https_handler_instance
        transport = proxy_config.GetSudsProxyTransport()
        t.assert_called_once_with([https_handler_instance])
        self.assertEqual(t.return_value, transport)

  def testProxyConfigWithHTTPProxy(self):
    with mock.patch('httplib2.ProxyInfo') as proxy_info:
      proxy_info.return_value = mock.Mock()
      with mock.patch('socks.PROXY_TYPE_HTTP') as proxy_type:
        proxy_config = googleads.common.ProxyConfig(
            http_proxy=self.proxy_no_credentials)
        proxy_info.assert_called_once_with(
            proxy_type, self.proxy_host1, self.proxy_port1,
            proxy_user=None, proxy_pass='')
        self.assertEqual(proxy_config.proxy_info, proxy_info.return_value)
    self.assertEqual(proxy_config._proxy_option, {'http': '%s:%s' % (
        self.proxy_host1, self.proxy_port1)})
    self.assertIsInstance(
        proxy_config._ssl_context, ssl.SSLContext)

    with mock.patch('googleads.common.ProxyConfig._SudsProxyTransport') as t:
      t.return_value = mock.Mock()
      with mock.patch('%s.ProxyHandler' % URL_REQUEST_PATH) as proxy_handler:
        proxy_handler_instance = mock.Mock()
        proxy_handler.return_value = proxy_handler_instance
        with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
          https_handler_instance = mock.Mock()
          https_handler.return_value = https_handler_instance
          self.assertEqual(proxy_config.GetHandlers(),
                           [https_handler_instance, proxy_handler_instance])
          transport = proxy_config.GetSudsProxyTransport()
          t.assert_called_once_with(
              [https_handler_instance, proxy_handler_instance])
          self.assertEqual(t.return_value, transport)

  def testProxyConfigWithHTTPSProxy(self):
    with mock.patch('httplib2.ProxyInfo') as proxy_info:
      proxy_info.return_value = mock.Mock()
      with mock.patch('socks.PROXY_TYPE_HTTP') as proxy_type:
        proxy_config = googleads.common.ProxyConfig(
            https_proxy=self.proxy_with_credentials,
            cafile=self.cafile)
        proxy_info.assert_called_once_with(
            proxy_type, self.proxy_host2, self.proxy_port2,
            proxy_user=self.username, proxy_pass=self.password)
        self.assertEqual(proxy_config.proxy_info, proxy_info.return_value)
    self.assertEqual(proxy_config._proxy_option, {'https': '%s:%s@%s:%s' % (
        self.username, self.password, self.proxy_host2,
        self.proxy_port2)})
    self.assertIsInstance(
        proxy_config._ssl_context, ssl.SSLContext)
    self.assertEqual(proxy_config.cafile, self.cafile)
    self.assertEqual(proxy_config.disable_certificate_validation, False)

    with mock.patch('googleads.common.ProxyConfig._SudsProxyTransport') as t:
      t.return_value = mock.Mock()
      with mock.patch('%s.ProxyHandler' % URL_REQUEST_PATH) as proxy_handler:
        proxy_handler_instance = mock.Mock()
        proxy_handler.return_value = proxy_handler_instance
        with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
          https_handler_instance = mock.Mock()
          https_handler.return_value = https_handler_instance
          self.assertEqual(
              proxy_config.GetHandlers(),
              [https_handler_instance, proxy_handler_instance])
          transport = proxy_config.GetSudsProxyTransport()
          t.assert_called_once_with(
              [https_handler_instance, proxy_handler_instance])
          self.assertEqual(t.return_value, transport)

  def testProxyConfigWithHTTPAndHTTPSProxy(self):
    with mock.patch('httplib2.ProxyInfo') as proxy_info:
      proxy_info.return_value = mock.Mock()
      with mock.patch('socks.PROXY_TYPE_HTTP') as proxy_type:
        proxy_config = googleads.common.ProxyConfig(
            http_proxy=self.proxy_with_credentials,
            https_proxy=self.proxy_no_credentials,
            disable_certificate_validation=True)
        proxy_info.assert_called_once_with(
            proxy_type, self.proxy_host1, self.proxy_port1,
            proxy_user=None, proxy_pass='')
        self.assertEqual(proxy_config.proxy_info, proxy_info.return_value)
    self.assertEqual(proxy_config._proxy_option, {
        'http': '%s:%s@%s:%s' % (self.username, self.password,
                                 self.proxy_host2, self.proxy_port2),
        'https': '%s:%s' % (self.proxy_host1, self.proxy_port1)})

    self.assertIsInstance(proxy_config._ssl_context, ssl.SSLContext)
    self.assertEqual(proxy_config.cafile, None)
    self.assertEqual(proxy_config.disable_certificate_validation, True)

    with mock.patch('googleads.common.ProxyConfig._SudsProxyTransport') as t:
      t.return_value = mock.Mock()
      with mock.patch('%s.ProxyHandler' % URL_REQUEST_PATH) as proxy_handler:
        proxy_handler_instance = mock.Mock()
        proxy_handler.return_value = proxy_handler_instance

        with mock.patch('%s.HTTPSHandler' % URL_REQUEST_PATH) as https_handler:
          https_handler_instance = mock.Mock()
          https_handler.return_value = https_handler_instance
          self.assertEqual(
              proxy_config.GetHandlers(),
              [https_handler_instance, proxy_handler_instance])
          transport = proxy_config.GetSudsProxyTransport()
          t.assert_called_once_with(
              [https_handler_instance, proxy_handler_instance])
          self.assertEqual(t.return_value, transport)


class TestSudsRequestPatcher(unittest.TestCase):

  class MockHeaders(object):

    def __init__(self, d):
      self.dict = d

      # If testing on Python 3, add get method to better mimic the
      # http.client.HTTPMessage behavior.
      if six.PY3:
        def py3_get(s):
          return self.dict.get(s)
        self.get = py3_get

  def testInflateSuccessfulRequestIfGzipped(self):
    with mock.patch('suds.transport.http.HttpTransport.getcookies'):
      with mock.patch('%s.OpenerDirector.open' % URL_REQUEST_PATH) as mock_open:
        with mock.patch('gzip.GzipFile.read') as mock_read:
          resp_fp = six.BytesIO()
          resp_fp.write(b'abc')
          resp_fp.flush()
          resp_fp.seek(0)
          resp = six.moves.urllib.response.addinfourl(
              resp_fp, self.MockHeaders({'content-encoding': 'gzip'}),
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
              resp_fp, self.MockHeaders({'content-encoding': 'gzip'}),
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
