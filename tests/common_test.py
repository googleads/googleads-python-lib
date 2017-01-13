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


import unittest
import urllib2
import warnings


from pyfakefs import fake_filesystem
from pyfakefs import fake_tempfile
import mock
import suds
import yaml

import googleads.common
import googleads.errors
import googleads.oauth2


class CommonTest(unittest.TestCase):
  """Tests for the googleads.common module."""

  # Dictionaries with all the required OAuth2 keys
  _OAUTH_INSTALLED_APP_DICT = {'client_id': 'a', 'client_secret': 'b',
                               'refresh_token': 'c'}
  _OAUTH_SERVICE_ACCT_DICT = {'service_account_email': 'test@test.com',
                              'path_to_private_key_file': '/test/test.p12'}

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
    yaml_fname = self._CreateYamlFile({'one': {'needed': 'd', 'keys': 'e'}},
                                      'one', self._OAUTH_INSTALLED_APP_DICT)
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

    # The optional key is present.
    yaml_fname = self._CreateYamlFile({'one': {'needed': 'd', 'keys': 'e',
                                               'other': 'f'}}, 'one',
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

  def testLoadFromString_deprecatedWarningLoggerByMicroValue(self):
    yaml_doc = self._CreateYamlDoc({
        'one': {
            'needed': 'd',
            'keys': 'e'
        }
    }, 'one', self._OAUTH_INSTALLED_APP_DICT)
    test_major_value = 2
    test_minor_value = 7
    test_micro_value = 6
    with mock.patch('googleads.common._PY_VERSION_MAJOR', test_major_value):
      with mock.patch('googleads.common._PY_VERSION_MINOR', test_minor_value):
        with mock.patch('googleads.common._PY_VERSION_MICRO', test_micro_value):
          with mock.patch('googleads.common._logger') as mock_logger:
            with mock.patch(
                'googleads.common.open', self.fake_open, create=True):
              googleads.common.LoadFromString(yaml_doc, 'one',
                                              ['needed', 'keys'], ['other'])
              mock_logger.warning.assert_called_once_with(
                  googleads.common._DEPRECATED_VERSION_TEMPLATE,
                  test_major_value, test_minor_value, test_micro_value)

  def testLoadFromString_deprecatedWarningLoggerByMinorValue(self):
    yaml_doc = self._CreateYamlDoc({'one': {'needed': 'd', 'keys': 'e'}},
                                   'one', self._OAUTH_INSTALLED_APP_DICT)
    test_major_value = 2
    test_minor_value = 6
    test_micro_value = 9
    with mock.patch('googleads.common._PY_VERSION_MAJOR', test_major_value):
      with mock.patch('googleads.common._PY_VERSION_MINOR', test_minor_value):
        with mock.patch('googleads.common._PY_VERSION_MICRO', test_micro_value):
          with mock.patch('googleads.common._logger') as mock_logger:
            with mock.patch(
                'googleads.common.open', self.fake_open, create=True):
              googleads.common.LoadFromString(yaml_doc, 'one',
                                              ['needed', 'keys'], ['other'])
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

  def testLoadFromString_serviceAccount(self):
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
        dfp_scope, 'test@test.com', '/test/test.p12',
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
        dfp_scope, 'test@test.com', '/test/test.p12',
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
    self.suds_service_wrapper = googleads.common.SudsServiceProxy(
        self.client, self.header_handler)

  def testSudsServiceProxy(self):
    self.assertEqual(self.suds_service_wrapper.SoapMethod,
                     self.suds_service_wrapper._method_proxies['SoapMethod'])
    self.assertEqual(self.suds_service_wrapper.NotSoapMethod,
                     self.client.service.NotSoapMethod)

    with mock.patch('googleads.common._PackForSuds') as mock_pack_for_suds:
      mock_pack_for_suds.return_value = 'modified_test'
      self.suds_service_wrapper.SoapMethod('test')
      mock_pack_for_suds.assert_called_once_with('test', self.client.factory)

    self.client.service.SoapMethod.assert_called_once_with('modified_test')
    self.header_handler.SetHeaders.assert_called_once_with(self.client)


class HeaderHandlerTest(unittest.TestCase):
  """Tests for the googleads.common.HeaderHeader class."""

  def testSetHeaders(self):
    """For coverage."""
    self.assertRaises(
        NotImplementedError, googleads.common.HeaderHandler().SetHeaders,
        mock.Mock())


class ProxyConfigTest(unittest.TestCase):
  """Tests fpr the googleads.common.ProxyConfig class."""

  def setUp(self):
    self.proxy_host1 = 'host1'
    self.proxy_port1 = 'port1'
    self.proxy_host2 = 'host2'
    self.proxy_port2 = 'port2'
    self.username = 'username'
    self.password = 'password'
    self.cafile = '/tmp/file.ca'

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
    self.assertEqual(proxy_config.GetHandlers(), [])

  def testProxyConfigGetHandlersWithProxy(self):
    http_proxy = googleads.common.ProxyConfig.Proxy(self.proxy_host1,
                                                    self.proxy_port1)
    with mock.patch('urllib2.ProxyHandler') as proxy_handler:
      proxy_handler.return_value = mock.Mock()
      proxy_config = googleads.common.ProxyConfig(http_proxy=http_proxy)
      self.assertEqual(proxy_config.GetHandlers(), [proxy_handler.return_value])
      proxy_handler.assert_called_once_with(
          {'http': '%s' % str(http_proxy)})

  def testProxyConfigGetHandlersWithProxyAndSLLContext(self):
    https_proxy = googleads.common.ProxyConfig.Proxy(self.proxy_host1,
                                                     self.proxy_port1)
    with mock.patch('googleads.common.ProxyConfig._InitSSLContext') as ssl_ctxt:
      ssl_ctxt.return_value = 'CONTEXT'
      with mock.patch('urllib2.ProxyHandler') as proxy_handler:
        proxy_handler.return_value = mock.Mock()
        with mock.patch('urllib2.HTTPSHandler') as https_handler:
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
    self.assertEqual(proxy_config.GetHandlers(), [])
    # Note: The ssl_context will always be None on incompatible versions of
    # Python. The version used internally doesn't support this feature. Another
    # impact is that HTTPSHandler will never be invoked in these tests.
    self.assertEqual(proxy_config._ssl_context, None)

    with mock.patch('googleads.common.ProxyConfig._SudsProxyTransport') as t:
      t.return_value = mock.Mock()
      transport = proxy_config.GetSudsProxyTransport()
      t.assert_called_once_with([])
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
    # Note: The ssl_context will always be None on incompatible versions of
    # Python. The version used internally doesn't support this feature. Another
    # impact is that HTTPSHandler will never be invoked in these tests.
    self.assertEqual(proxy_config._ssl_context, None)

    with mock.patch('googleads.common.ProxyConfig._SudsProxyTransport') as t:
      t.return_value = mock.Mock()
      with mock.patch('urllib2.ProxyHandler') as proxy_handler:
        proxy_handler.return_value = mock.Mock()
        self.assertEqual(proxy_config.GetHandlers(),
                         [proxy_handler.return_value])
        transport = proxy_config.GetSudsProxyTransport()
        t.assert_called_once_with([proxy_handler.return_value])
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
    # Note: The ssl_context will always be None on incompatible versions of
    # Python. The version used internally doesn't support this feature. Another
    # impact is that HTTPSHandler will never be invoked in these tests.
    self.assertEqual(proxy_config._ssl_context, None)
    self.assertEqual(proxy_config.cafile, self.cafile)
    self.assertEqual(proxy_config.disable_certificate_validation, False)

    with mock.patch('googleads.common.ProxyConfig._SudsProxyTransport') as t:
      t.return_value = mock.Mock()
      with mock.patch('urllib2.ProxyHandler') as proxy_handler:
        proxy_handler.return_value = mock.Mock()
        self.assertEqual(proxy_config.GetHandlers(),
                         [proxy_handler.return_value])
        transport = proxy_config.GetSudsProxyTransport()
        t.assert_called_once_with([proxy_handler.return_value])
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
    # Note: The ssl_context will always be None on incompatible versions of
    # Python. The version used internally doesn't support this feature. Another
    # impact is that HTTPSHandler will never be invoked in these tests.
    self.assertEqual(proxy_config._ssl_context, None)
    self.assertEqual(proxy_config.cafile, None)
    self.assertEqual(proxy_config.disable_certificate_validation, True)

    with mock.patch('googleads.common.ProxyConfig._SudsProxyTransport') as t:
      t.return_value = mock.Mock()
      with mock.patch('urllib2.ProxyHandler') as proxy_handler:
        proxy_handler.return_value = mock.Mock()
        self.assertEqual(proxy_config.GetHandlers(),
                         [proxy_handler.return_value])
        transport = proxy_config.GetSudsProxyTransport()
        t.assert_called_once_with([proxy_handler.return_value])
        self.assertEqual(t.return_value, transport)


if __name__ == '__main__':
  unittest.main()
