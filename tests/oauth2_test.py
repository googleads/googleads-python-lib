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

"""Unit tests to cover the oauth2 module."""


import datetime
import unittest


import httplib2
import mock

import googleads.common
import googleads.errors
import googleads.oauth2

from pyfakefs import fake_filesystem
from pyfakefs import fake_tempfile
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2Credentials

if googleads.oauth2.DEPRECATED_OAUTH2CLIENT:
  _SA_CRED_PATH = ('oauth2client.client'
                   '.SignedJwtAssertionCredentials')
else:
  _SA_CRED_PATH = 'oauth2client.service_account.ServiceAccountCredentials'


class GetAPIScopeTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GetAPIScope function."""

  def setUp(self):
    self.api_name_adwords = 'adwords'
    self.api_name_dfp = 'dfp'
    self.scope_adwords = 'https://www.googleapis.com/auth/adwords'
    self.scope_dfp = 'https://www.googleapis.com/auth/dfp'

  def testGetAPIScope_adwords(self):
    self.assertEquals(googleads.oauth2.GetAPIScope(self.api_name_adwords),
                      self.scope_adwords)

  def testGetAPIScope_badKey(self):
    self.assertRaises(googleads.errors.GoogleAdsValueError,
                      googleads.oauth2.GetAPIScope, 'fake_api_name')

  def testGetAPIScope_dfp(self):
    self.assertEquals(googleads.oauth2.GetAPIScope(self.api_name_dfp),
                      self.scope_dfp)


class GoogleOAuth2ClientTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleOAuth2Client class."""

  def testCreateHttpHeader(self):
    """For coverage."""
    self.assertRaises(
        NotImplementedError,
        googleads.oauth2.GoogleOAuth2Client().CreateHttpHeader)


class GoogleRefreshableOAuth2ClientTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleRefreshableOAuth2Client class."""

  def testRefresh(self):
    """For coverage."""
    self.assertRaises(
        NotImplementedError,
        googleads.oauth2.GoogleRefreshableOAuth2Client().Refresh)


class GoogleAccessTokenClientTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleAccessTokenClient class."""

  def setUp(self):
    self.access_token = 'a'
    self.token_expiry = (datetime.datetime.utcnow() +
                         datetime.timedelta(seconds=3600))
    self.expired_token_expiry = datetime.datetime(1980, 1, 1, 12)

  def testCreateHttpHeader(self):
    client = googleads.oauth2.GoogleAccessTokenClient(
        self.access_token, self.token_expiry)
    expected_header = {'Authorization': 'Bearer %s' % self.access_token}
    self.assertEqual(client.CreateHttpHeader(), expected_header)

  def testCreateHttpHeaderWithExpiredToken(self):
    expired_client = googleads.oauth2.GoogleAccessTokenClient(
        self.access_token, self.expired_token_expiry)
    self.assertRaises(googleads.errors.GoogleAdsError,
                      expired_client.CreateHttpHeader)


class GoogleRefreshTokenClientTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleRefreshTokenClient class."""

  def setUp(self):
    self.client_id = 'client_id'
    self.client_secret = 'itsasecret'
    self.refresh_token = 'refreshing'
    https_proxy_host = 'myproxy.com'
    https_proxy_port = 443
    self.https_proxy = googleads.common.ProxyConfig.Proxy(https_proxy_host,
                                                          https_proxy_port)
    self.proxy_config = googleads.common.ProxyConfig(
        https_proxy=self.https_proxy)
    self.access_token_unrefreshed = 'a'
    self.access_token_refreshed = 'b'

    # Mock out httplib2.Http for testing.
    self.http = mock.Mock(spec=httplib2.Http)
    self.opener = self.http.return_value = mock.Mock()
    self.opener.proxy_info = self.proxy_config.proxy_info
    self.opener.ca_certs = self.proxy_config.cafile
    self.opener.disable_ssl_certificate_valiation = (
        self.proxy_config.disable_certificate_validation)

    # Mock out oauth2client.client.OAuth2Credentials for testing
    self.oauth2_credentials = mock.Mock(spec=OAuth2Credentials)
    self.oauth2_credentials.return_value = mock.Mock()
    self.mock_oauth2_credentials = (self.oauth2_credentials.return_value)
    self.mock_oauth2_credentials.access_token = self.access_token_unrefreshed
    self.mock_oauth2_credentials.token_expiry = datetime.datetime(1980, 1, 1,
                                                                  12)

    def apply(headers):
      headers['Authorization'] = ('Bearer %s'
                                  % self.mock_oauth2_credentials.access_token)

    def refresh(mock_http):
      self.mock_oauth2_credentials.access_token = self.access_token_refreshed
      self.mock_oauth2_credentials.token_expiry = datetime.datetime.utcnow()

    self.mock_oauth2_credentials.apply = mock.Mock(side_effect=apply)
    self.mock_oauth2_credentials.refresh = mock.Mock(side_effect=refresh)
    with mock.patch('oauth2client.client.OAuth2Credentials',
                    self.oauth2_credentials):
      self.googleads_client = googleads.oauth2.GoogleRefreshTokenClient(
          self.client_id, self.client_secret, self.refresh_token,
          proxy_config=self.proxy_config,
          access_token=self.access_token_unrefreshed,
          token_expiry=self.mock_oauth2_credentials.token_expiry)

  def testCreateHttpHeader_noRefresh(self):
    header = {'Authorization': 'Bearer %s' % self.access_token_unrefreshed}
    self.mock_oauth2_credentials.token_expiry = None
    self.assertEqual(header, self.googleads_client.CreateHttpHeader())

  def testCreateHttpHeader_refresh(self):
    header = {u'Authorization': 'Bearer %s' % self.access_token_refreshed}

    with mock.patch('httplib2.Http', self.http):
      self.assertEqual(header, self.googleads_client.CreateHttpHeader())
      self.http.assert_called_once_with(
          ca_certs=None, proxy_info=self.proxy_config.proxy_info,
          disable_ssl_certificate_validation=(
              self.proxy_config.disable_certificate_validation))
      self.mock_oauth2_credentials.refresh.assert_called_once_with(
          self.opener)

  def testCreateHttpHeader_refreshFails(self):
    self.mock_oauth2_credentials.refresh.side_effect = AccessTokenRefreshError(
        'Invalid response 400')

    with mock.patch('httplib2.Http', self.http):
      self.assertRaises(AccessTokenRefreshError,
                        self.googleads_client.CreateHttpHeader)
      self.assertFalse(self.mock_oauth2_credentials.apply.called)


class GoogleServiceAccountTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleServiceAccountClient class."""

  def setUp(self):
    self.scope = 'scope'
    self.service_account_email = 'email@email.com'
    self.private_key = 'IT\'S A SECRET TO EVERYBODY.'
    self.private_key_password = 'notasecret'
    self.delegated_account = 'delegated_account@delegated.com'
    https_proxy_host = 'myproxy.com'
    https_proxy_port = 443
    https_proxy = googleads.common.ProxyConfig.Proxy(https_proxy_host,
                                                     https_proxy_port)
    self.proxy_config = googleads.common.ProxyConfig(https_proxy=https_proxy)
    self.https_proxy = '%s:%s' % (https_proxy_host, https_proxy_port)
    self.access_token_unrefreshed = 'a'
    self.access_token_refreshed = 'b'

    # Mock out filesystem and file for testing.
    filesystem = fake_filesystem.FakeFilesystem()
    tempfile = fake_tempfile.FakeTempfileModule(filesystem)
    self.fake_open = fake_filesystem.FakeFileOpen(filesystem)
    self.key_file_path = tempfile.NamedTemporaryFile(delete=False).name

    with self.fake_open(self.key_file_path, 'w') as file_handle:
      file_handle.write(self.private_key)

    # Mock out httplib2.Http for testing.
    self.http = mock.Mock(spec=httplib2.Http)
    self.opener = self.http.return_value = mock.Mock()
    self.opener.proxy_info = self.proxy_config.proxy_info
    self.opener.ca_certs = self.proxy_config.cafile
    self.opener.disable_ssl_certificate_valiation = (
        self.proxy_config.disable_certificate_validation)

    # Mock out service account credentials for testing.
    self.oauth2_credentials = mock.Mock()
    self.oauth2_credentials.return_value = mock.Mock()
    self.mock_oauth2_credentials = self.oauth2_credentials.return_value
    self.mock_oauth2_credentials.access_token = 'x'
    self.mock_oauth2_credentials.token_expiry = datetime.datetime(
        1980, 1, 1, 12)
    # Also mock out instantiation methods for newer oauth2client versions.
    self.oauth2_credentials.from_p12_keyfile.return_value = (
        self.mock_oauth2_credentials)
    self.oauth2_credentials.from_json_keyfile_name.return_value = (
        self.mock_oauth2_credentials)

    def apply(headers):
      headers['Authorization'] = ('Bearer %s'
                                  % self.mock_oauth2_credentials.access_token)

    def refresh(mock_http):
      self.mock_oauth2_credentials.access_token = (
          self.access_token_unrefreshed if
          self.mock_oauth2_credentials.access_token is 'x'
          else self.access_token_refreshed)
      self.mock_oauth2_credentials.token_expiry = datetime.datetime.utcnow()

    self.mock_oauth2_credentials.apply = mock.Mock(side_effect=apply)
    self.mock_oauth2_credentials.refresh = mock.Mock(side_effect=refresh)
    with mock.patch('__builtin__.open', self.fake_open):
      with mock.patch(_SA_CRED_PATH, self.oauth2_credentials):
        self.googleads_client = googleads.oauth2.GoogleServiceAccountClient(
            self.scope, self.service_account_email, self.key_file_path,
            self.private_key_password, proxy_config=self.proxy_config)
      # Undo the call count for the auto-refresh
      self.mock_oauth2_credentials.refresh.reset_mock()

  def testCreateGoogleServiceAccountClient_DelegatedJsonOAuth2Client4(self):
    # Mock out the oauth2client 4.0.0 oauth2client.service_account module to
    # verify that the correct parts are called.
    mock_oauth2client_4 = mock.Mock()
    mock_service_account_module = mock.Mock()
    mock_service_account_credentials = mock.Mock()
    mock_service_account_credentials_instance = mock.Mock()
    mock_from_json_keyfile_name = mock.Mock()
    mock_create_delegated = mock.Mock()
    mock_service_account_credentials_instance.create_delegated = (
        mock_create_delegated)
    mock_from_json_keyfile_name.return_value = (
        mock_service_account_credentials_instance)
    mock_service_account_credentials.from_json_keyfile_name = (
        mock_from_json_keyfile_name)
    mock_service_account_module.ServiceAccountCredentials = (
        mock_service_account_credentials)
    mock_oauth2client_4.service_account = mock_service_account_module
    mock_oauth2client_4.__version__ = '4.0.0'
    with mock.patch('googleads.oauth2.oauth2client',
                    mock_oauth2client_4):
      with mock.patch('googleads.oauth2.DEPRECATED_OAUTH2CLIENT', False):
        mock_oauth2client_4.service_account = mock_service_account_module
        # Create a GoogleServiceAccountClient and verify that the
        # ServiceAccountCredentials were correctly instantiated.
        googleads.oauth2.GoogleServiceAccountClient(
            self.scope, client_email=None, key_file=self.key_file_path,
            sub=self.delegated_account)
        mock_from_json_keyfile_name.assert_called_once_with(
            self.key_file_path, scopes=self.scope)
        mock_create_delegated.assert_called_once_with(self.delegated_account)

  def testCreateGoogleServiceAccountClient_DelegatedP12OAuth2Client4(self):
    # Mock out the oauth2client 4.0.0 oauth2client.service_account module to
    # verify that the correct parts are called.
    mock_oauth2client_4 = mock.Mock()
    mock_service_account_module = mock.Mock()
    mock_service_account_credentials = mock.Mock()
    mock_service_account_credentials_instance = mock.Mock()
    mock_from_p12_keyfile = mock.Mock()
    mock_create_delegated = mock.Mock()
    mock_service_account_credentials_instance.create_delegated = (
        mock_create_delegated)
    mock_from_p12_keyfile.return_value = (
        mock_service_account_credentials_instance)
    mock_service_account_credentials.from_p12_keyfile = (
        mock_from_p12_keyfile)
    mock_service_account_module.ServiceAccountCredentials = (
        mock_service_account_credentials)
    mock_oauth2client_4.service_account = mock_service_account_module
    mock_oauth2client_4.__version__ = '4.0.0'
    with mock.patch('googleads.oauth2.oauth2client',
                    mock_oauth2client_4):
      with mock.patch('googleads.oauth2.DEPRECATED_OAUTH2CLIENT', False):
        mock_oauth2client_4.service_account = mock_service_account_module
        # Create a GoogleServiceAccountClient and verify that the
        # ServiceAccountCredentials were correctly instantiated.
        googleads.oauth2.GoogleServiceAccountClient(
            self.scope, client_email=self.service_account_email,
            key_file=self.key_file_path, sub=self.delegated_account)
        mock_from_p12_keyfile.assert_called_once_with(
            self.service_account_email, self.key_file_path, scopes=self.scope)
        mock_create_delegated.assert_called_once_with(self.delegated_account)

  def testCreateGoogleServiceAccountClient_DelegatedP12OAuth2ClientDepr(self):
    # Mock out the oauth2client 1.4.12 oauth2client.client module to
    # verify that the correct parts are called.
    mock_oauth2client_depr = mock.Mock()
    mock_client_module = mock.Mock()
    mock_signed_jwt_credentials = mock.Mock()
    mock_signed_jwt_credentials_instance = mock.Mock()
    mock_signed_jwt_credentials.return_value = (
        mock_signed_jwt_credentials_instance)
    mock_client_module.SignedJwtAssertionCredentials = (
        mock_signed_jwt_credentials)
    mock_oauth2client_depr.client = mock_client_module
    mock_oauth2client_depr.__version__ = '1.4.12'

    # Mock out the oauth2client 1.4.12 oauth2client.client module to
    # verify that the correct parts are called.
    with mock.patch('googleads.oauth2.oauth2client',
                    mock_oauth2client_depr):
      with mock.patch('googleads.oauth2.DEPRECATED_OAUTH2CLIENT', True):
        with mock.patch('%s.open' % googleads.oauth2.__name__, self.fake_open,
                        create=True):
          googleads.oauth2.GoogleServiceAccountClient(
              self.scope, client_email=self.service_account_email,
              key_file=self.key_file_path, sub=self.delegated_account)
          mock_signed_jwt_credentials.assert_called_once_with(
              self.service_account_email, self.private_key, self.scope,
              private_key_password=self.private_key_password,
              user_agent='Google Ads Python Client Library',
              token_uri='https://accounts.google.com/o/oauth2/token',
              sub=self.delegated_account)

  def testCreateGoogleServiceAccountClient_JsonOAuth2Client4(self):
    # Mock out the oauth2client 4.0.0 oauth2client.service_account module to
    # verify that the correct parts are called.
    mock_oauth2client_4 = mock.Mock()
    mock_service_account_module = mock.Mock()
    mock_service_account_credentials = mock.Mock()
    mock_service_account_credentials_instance = mock.Mock()
    mock_from_json_keyfile_name = mock.Mock()
    mock_create_delegated = mock.Mock()
    mock_service_account_credentials_instance.create_delegated = (
        mock_create_delegated)
    mock_from_json_keyfile_name.return_value = (
        mock_service_account_credentials_instance)
    mock_service_account_credentials.from_json_keyfile_name = (
        mock_from_json_keyfile_name)
    mock_service_account_module.ServiceAccountCredentials = (
        mock_service_account_credentials)
    mock_oauth2client_4.service_account = mock_service_account_module
    mock_oauth2client_4.__version__ = '4.0.0'
    with mock.patch('googleads.oauth2.oauth2client',
                    mock_oauth2client_4):
      with mock.patch('googleads.oauth2.DEPRECATED_OAUTH2CLIENT', False):
        mock_oauth2client_4.service_account = mock_service_account_module
        # Create a GoogleServiceAccountClient and verify that the
        # ServiceAccountCredentials were correctly instantiated.
        googleads.oauth2.GoogleServiceAccountClient(
            self.scope, client_email=None, key_file=self.key_file_path)
        mock_from_json_keyfile_name.assert_called_once_with(
            self.key_file_path, scopes=self.scope)
        mock_create_delegated.assert_not_called()

  def testCreateGoogleServiceAccountClient_P12OAuth2Client4(self):
    # Mock out the oauth2client 4.0.0 oauth2client.service_account module to
    # verify that the correct parts are called.
    mock_oauth2client_4 = mock.Mock()
    mock_service_account_module = mock.Mock()
    mock_service_account_credentials = mock.Mock()
    mock_service_account_credentials_instance = mock.Mock()
    mock_from_p12_keyfile = mock.Mock()
    mock_create_delegated = mock.Mock()
    mock_service_account_credentials_instance.create_delegated = (
        mock_create_delegated)
    mock_from_p12_keyfile.return_value = (
        mock_service_account_credentials_instance)
    mock_service_account_credentials.from_p12_keyfile = (
        mock_from_p12_keyfile)
    mock_service_account_module.ServiceAccountCredentials = (
        mock_service_account_credentials)
    mock_oauth2client_4.service_account = mock_service_account_module
    mock_oauth2client_4.__version__ = '4.0.0'
    with mock.patch('googleads.oauth2.oauth2client',
                    mock_oauth2client_4):
      with mock.patch('googleads.oauth2.DEPRECATED_OAUTH2CLIENT', False):
        mock_oauth2client_4.service_account = mock_service_account_module
        # Create a GoogleServiceAccountClient and verify that the
        # ServiceAccountCredentials were correctly instantiated.
        googleads.oauth2.GoogleServiceAccountClient(
            self.scope, client_email=self.service_account_email,
            key_file=self.key_file_path)
        mock_from_p12_keyfile.assert_called_once_with(
            self.service_account_email, self.key_file_path, scopes=self.scope)
        mock_create_delegated.assert_not_called()

  def testCreateHttpHeader_noRefresh(self):
    header = {'Authorization': 'Bearer %s' % self.access_token_unrefreshed}
    self.mock_oauth2_credentials.token_expiry = None
    self.assertEqual(header, self.googleads_client.CreateHttpHeader())

  def testCreateHttpHeader_refresh(self):
    header = {u'Authorization': 'Bearer %s' % self.access_token_refreshed}

    with mock.patch('httplib2.Http', self.http):
      self.assertEqual(header, self.googleads_client.CreateHttpHeader())
      self.http.assert_called_once_with(
          ca_certs=None, proxy_info=self.proxy_config.proxy_info,
          disable_ssl_certificate_validation=(
              self.proxy_config.disable_certificate_validation))
      self.mock_oauth2_credentials.refresh.assert_called_once_with(
          self.opener)

  def testCreateHttpHeader_refreshFails(self):
    self.mock_oauth2_credentials.refresh.side_effect = AccessTokenRefreshError(
        'Invalid response 400')

    with mock.patch('httplib2.Http', self.http):
      self.assertRaises(AccessTokenRefreshError,
                        self.googleads_client.CreateHttpHeader)
      self.assertFalse(self.mock_oauth2_credentials.apply.called)

  def testIssue123(self):
    """Test that verifies the fix for Issue #123 on the GitHub Issue Tracker.

    See: https://github.com/googleads/googleads-python-lib/issues/123
    """
    with mock.patch('__builtin__.open'):
      with mock.patch(_SA_CRED_PATH, self.oauth2_credentials):
        googleads.oauth2.GoogleServiceAccountClient(
            self.scope, self.service_account_email, '/dev/null',
            self.private_key_password)


if __name__ == '__main__':
  unittest.main()
