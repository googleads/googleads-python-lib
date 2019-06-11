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

import mock
import googleads.common
import googleads.errors
import googleads.oauth2
from pyfakefs import fake_filesystem
from pyfakefs import fake_tempfile
from google.auth.exceptions import RefreshError
from google.auth.transport import Request
from google.oauth2.credentials import Credentials


class GetAPIScopeTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GetAPIScope function."""

  def setUp(self):
    self.api_name_adwords = 'adwords'
    self.api_name_ad_manager = 'ad_manager'
    self.scope_adwords = 'https://www.googleapis.com/auth/adwords'
    self.scope_ad_manager = 'https://www.googleapis.com/auth/dfp'

  def testGetAPIScope_adwords(self):
    self.assertEquals(googleads.oauth2.GetAPIScope(self.api_name_adwords),
                      self.scope_adwords)

  def testGetAPIScope_badKey(self):
    self.assertRaises(googleads.errors.GoogleAdsValueError,
                      googleads.oauth2.GetAPIScope, 'fake_api_name')

  def testGetAPIScope_ad_manager(self):
    self.assertEqual(googleads.oauth2.GetAPIScope(self.api_name_ad_manager),
                     self.scope_ad_manager)


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
    expected_header = {'authorization': 'Bearer %s' % self.access_token}
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
    self.access_token_unrefreshed = 'a'
    self.access_token_refreshed = 'b'

    # Mock out google.auth.transport.Request for testing.
    self.mock_req = mock.Mock(spec=Request)
    self.mock_req.return_value = mock.Mock()
    self.mock_req_instance = self.mock_req.return_value

    # Mock out google.oauth2.credentials.Credentials for testing
    self.mock_credentials = mock.Mock(spec=Credentials)
    self.mock_credentials.return_value = mock.Mock()
    self.mock_credentials_instance = self.mock_credentials.return_value
    self.mock_credentials_instance.token = self.access_token_unrefreshed
    self.mock_credentials_instance.expiry = datetime.datetime(1980, 1, 1, 12)
    self.mock_credentials_instance.expired = True

    def apply(headers, token=None):
      headers['authorization'] = ('Bearer %s'
                                  % self.mock_credentials_instance.token)

    def refresh(request):
      self.mock_credentials_instance.token = self.access_token_refreshed
      self.mock_credentials_instance.expiry = datetime.datetime.utcnow()

    self.mock_credentials_instance.apply = mock.Mock(side_effect=apply)
    self.mock_credentials_instance.refresh = mock.Mock(side_effect=refresh)
    with mock.patch('google.oauth2.credentials.Credentials',
                    self.mock_credentials):
      self.refresh_client = googleads.oauth2.GoogleRefreshTokenClient(
          self.client_id, self.client_secret, self.refresh_token,
          access_token=self.access_token_unrefreshed,
          token_expiry=self.mock_credentials_instance.expiry)

  def testCreateHttpHeader_noRefresh(self):
    header = {'authorization': 'Bearer %s' % self.access_token_unrefreshed}
    self.mock_credentials_instance.expiry = (
        datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    self.mock_credentials_instance.expired = False
    self.assertEqual(header, self.refresh_client.CreateHttpHeader())

  def testCreateHttpHeader_refresh(self):
    expected_header = {u'authorization': 'Bearer %s'
                                         % self.access_token_refreshed}

    with mock.patch('requests.Session') as mock_session:
      mock_session_instance = mock.MagicMock()
      mock_session.return_value = mock_session_instance
      mock_session_instance.__enter__.return_value = mock_session_instance
      mock_session_instance.__exit__.return_value = None
      with mock.patch('google.auth.transport.requests.Request', self.mock_req):
        header = self.refresh_client.CreateHttpHeader()
        self.assertEqual(mock_session_instance.proxies, {})
        self.assertEqual(mock_session_instance.verify, True)
        self.assertEqual(mock_session_instance.cert, None)
        self.mock_req.assert_called_once_with(session=mock_session_instance)
        self.assertEqual(expected_header, header)
        self.mock_credentials_instance.refresh.assert_called_once_with(
            self.mock_req_instance)

  def testCreateHttpHeader_refreshWithConfiguredProxyConfig(self):
    https_proxy = 'http://myproxy.com:443'
    expected_proxies = {'https': https_proxy}
    proxy_config = googleads.common.ProxyConfig(https_proxy=https_proxy)
    self.refresh_client.proxy_config = proxy_config

    expected_header = {u'authorization': 'Bearer %s'
                                         % self.access_token_refreshed}

    with mock.patch('requests.Session') as mock_session:
      mock_session_instance = mock.MagicMock()
      mock_session.return_value = mock_session_instance
      mock_session_instance.__enter__.return_value = mock_session_instance
      mock_session_instance.__exit__.return_value = None
      with mock.patch('google.auth.transport.requests.Request', self.mock_req):
        header = self.refresh_client.CreateHttpHeader()
        self.assertEqual(mock_session_instance.proxies, expected_proxies)
        self.assertEqual(mock_session_instance.verify,
                         not proxy_config.disable_certificate_validation)
        self.assertEqual(mock_session_instance.cert,
                         proxy_config.cafile)
        self.mock_req.assert_called_once_with(session=mock_session_instance)
        self.assertEqual(expected_header, header)
        self.mock_credentials_instance.refresh.assert_called_once_with(
            self.mock_req_instance)

  def testCreateHttpHeader_refreshFails(self):
    self.mock_credentials_instance.refresh.side_effect = RefreshError(
        'Invalid response 400')

    with mock.patch('google.auth.transport.requests.Request', self.mock_req):
      self.assertRaises(RefreshError,
                        self.refresh_client.CreateHttpHeader)
      self.assertFalse(self.mock_credentials_instance.apply.called)


class GoogleServiceAccountTest(unittest.TestCase):
  """Tests for the googleads.oauth2.GoogleServiceAccountClient class."""

  def setUp(self):
    self.scope = 'scope'
    self.private_key = b'IT\'S A SECRET TO EVERYBODY.'
    self.delegated_account = 'delegated_account@delegated.com'

    # Mock out filesystem and file for testing.
    filesystem = fake_filesystem.FakeFilesystem()
    tempfile = fake_tempfile.FakeTempfileModule(filesystem)
    self.fake_open = fake_filesystem.FakeFileOpen(filesystem)
    self.key_file_path = tempfile.NamedTemporaryFile(delete=False).name
    self.cert_file_path = tempfile.NamedTemporaryFile(
        delete=False, prefix='cert_', suffix='.pem').name

    with self.fake_open(self.key_file_path, 'wb') as file_handle:
      file_handle.write(self.private_key)

    self.access_token_unrefreshed = 'a'
    self.access_token_refreshed = 'b'

    # Mock out google.auth.transport.Request for testing.
    self.mock_req = mock.Mock(spec=Request)
    self.mock_req.return_value = mock.Mock()
    self.mock_req_instance = self.mock_req.return_value

    # Mock out service account credentials for testing.
    self.mock_credentials = mock.Mock()
    self.mock_credentials.from_service_account_file.return_value = mock.Mock()
    self.mock_credentials_instance = (
        self.mock_credentials.from_service_account_file.return_value
    )
    self.mock_credentials_instance.token = 'x'
    self.mock_credentials_instance.expiry = datetime.datetime(
        1980, 1, 1, 12)
    self.mock_credentials_instance.expired = True

    def apply(headers, token=None):
      headers['authorization'] = ('Bearer %s'
                                  % self.mock_credentials_instance.token)

    def refresh(request):
      self.mock_credentials_instance.token = (
          self.access_token_unrefreshed if
          self.mock_credentials_instance.token is 'x'
          else self.access_token_refreshed)
      self.mock_credentials_instance.token_expiry = datetime.datetime.utcnow()

    self.mock_credentials_instance.apply = mock.Mock(side_effect=apply)
    self.mock_credentials_instance.refresh = mock.Mock(side_effect=refresh)
    with mock.patch('builtins.open', self.fake_open):
      with mock.patch('google.oauth2.service_account.Credentials',
                      self.mock_credentials):
        self.sa_client = googleads.oauth2.GoogleServiceAccountClient(
            self.key_file_path, self.scope)
      # Undo the call count for the auto-refresh
      self.mock_credentials_instance.refresh.reset_mock()

  def testCreateDelegatedGoogleServiceAccountClient(self):
    with mock.patch('google.oauth2.service_account.Credentials') as mock_cred:
      # Create a GoogleServiceAccountClient and verify that the delegated
      # service account Credentials were correctly instantiated.
      googleads.oauth2.GoogleServiceAccountClient(
          self.key_file_path, self.scope, sub=self.delegated_account)
      mock_cred.from_service_account_file.assert_called_once_with(
          self.key_file_path, scopes=[self.scope],
          subject=self.delegated_account)

  def testCreateHttpHeader_noRefresh(self):
    header = {'authorization': 'Bearer %s' % self.access_token_unrefreshed}
    self.mock_credentials_instance.expiry = (
        datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    self.mock_credentials_instance.expired = False
    self.assertEqual(header, self.sa_client.CreateHttpHeader())

  def testCreateHttpHeader_refresh(self):
    expected_header = {'authorization': 'Bearer %s'
                                        % self.access_token_refreshed}
    with mock.patch('requests.Session') as mock_session:
      mock_session_instance = mock.MagicMock()
      mock_session.return_value = mock_session_instance
      mock_session_instance.__enter__.return_value = mock_session_instance
      mock_session_instance.__exit__.return_value = None
      with mock.patch('google.auth.transport.requests.Request', self.mock_req):
        header = self.sa_client.CreateHttpHeader()
        self.assertEqual(mock_session_instance.proxies, {})
        self.assertEqual(mock_session_instance.verify, True)
        self.assertEqual(mock_session_instance.cert, None)
        self.mock_req.assert_called_once_with(session=mock_session_instance)
        self.assertEqual(expected_header, header)
      self.mock_credentials_instance.refresh.assert_called_once_with(
          self.mock_req_instance)

  def testCreateHttpHeader_refreshWithConfiguredProxyConfig(self):
    https_proxy = 'http://myproxy.com:443'
    proxy_config = googleads.common.ProxyConfig(https_proxy=https_proxy)
    expected_proxies = {'https': https_proxy}
    self.sa_client.proxy_config = proxy_config

    expected_header = {'authorization': 'Bearer %s'
                                        % self.access_token_refreshed}

    with mock.patch('requests.Session') as mock_session:
      mock_session_instance = mock.MagicMock()
      mock_session.return_value = mock_session_instance
      mock_session_instance.__enter__.return_value = mock_session_instance
      mock_session_instance.__exit__.return_value = None
      with mock.patch('google.auth.transport.requests.Request', self.mock_req):
        header = self.sa_client.CreateHttpHeader()
        self.assertEqual(mock_session_instance.proxies, expected_proxies)
        self.assertEqual(mock_session_instance.verify,
                         not proxy_config.disable_certificate_validation)
        self.assertEqual(mock_session_instance.cert,
                         proxy_config.cafile)
        self.mock_req.assert_called_once_with(session=mock_session_instance)
        self.assertEqual(expected_header, header)
      self.mock_credentials_instance.refresh.assert_called_once_with(
          self.mock_req_instance)

  def testCreateHttpHeader_refreshFails(self):
    self.mock_credentials_instance.refresh.side_effect = RefreshError(
        'Invalid response 400')

    with mock.patch('google.auth.transport.requests.Request', self.mock_req):
      self.assertRaises(RefreshError, self.sa_client.CreateHttpHeader)
      self.assertFalse(self.mock_credentials_instance.apply.called)


if __name__ == '__main__':
  unittest.main()
