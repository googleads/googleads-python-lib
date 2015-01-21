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

"""OAuth 2.0 integration for the googleads library.

This module provides a basic interface which the googleads library uses to
authorize API requests and some simple implementations built on oauth2client. If
our OAuth 2.0 workflows doesn't meet your requirements, you can implement this
interface in your own way. For example, you could pull credentials from a shared
server and/or centralize refreshing credentials to prevent every Python process
from independently refreshing the credentials.
"""

__author__ = 'Mark Saniscalchi'

import datetime


import googleads.errors
import httplib2
import oauth2client.client

# The scopes used for authorizing with the APIs supported by this library.
SCOPES = {'adwords': 'https://www.googleapis.com/auth/adwords',
          'dfa': 'https://www.googleapis.com/auth/dfatrafficking',
          'dfp': 'https://www.googleapis.com/auth/dfp'}


def GetAPIScope(api_name):
  """Retrieves the scope for the given API name.

  Args:
    api_name: A string identifying the name of the API we want to retrieve a
        scope for.

  Returns:
    A string that is the scope for the given API name.

  Raises:
    GoogleAdsValueError: If the given api_name is invalid; accepted valus are
        "adwords", "dfa", and "dfp".
  """
  try:
    return SCOPES[api_name]
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Invalid API name "%s" provided. Acceptable values are: %s'
        % (api_name, SCOPES.keys()))


class GoogleOAuth2Client(object):
  """An OAuth 2.0 client for use with Google APIs.

  This interface assumes all responsibilty for refreshing credentials when
  necessary.
  """

  def CreateHttpHeader(self):
    """Creates an OAuth 2.0 HTTP header.

    The OAuth 2.0 credentials will be refreshed as necessary.

    Returns:
      A dictionary containing one entry: the OAuth 2.0 Bearer header under the
      'Authorization' key.
    """
    raise NotImplementedError('You must subclass GoogleOAuth2Client.')

  def Refresh(self):
    """Refreshes the access token used by the client."""
    raise NotImplementedError('You must subclass GoogleOAuth2Client.')


class GoogleRefreshTokenClient(GoogleOAuth2Client):
  """A simple client for using OAuth 2.0 for Google APIs with a refresh token.

  This class is not capable of supporting any flows other than taking an
  existing, active refresh token and generating credentials from it. It does not
  matter which of Google's OAuth 2.0 flows you used to generate the refresh
  token (installed application, web flow, etc.).

  Attributes:
    proxy_info: A ProxyInfo instance used for refresh requests.
  """
  # The web address for generating OAuth 2.0 credentials at Google.
  _GOOGLE_OAUTH2_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
  # We will refresh an OAuth 2.0 credential _OAUTH2_REFRESH_MINUTES_IN_ADVANCE
  # minutes in advance of its expiration.
  _OAUTH2_REFRESH_MINUTES_IN_ADVANCE = 5
  # The placeholder URL is used when adding the access token to our request. A
  # well-formed URL is required, but since we're using HTTP header placement for
  # the token, this URL is completely unused.
  _TOKEN_URL = 'https://www.google.com'
  _USER_AGENT = 'Google Ads Python Client Library'

  def __init__(self, client_id, client_secret, refresh_token, proxy_info=None,
               disable_ssl_certificate_validation=False, ca_certs=None):
    """Initializes a GoogleRefreshTokenClient.

    Args:
      client_id: A string containing your client ID.
      client_secret: A string containing your client secret.
      refresh_token: A string containing your refresh token.
      [optional]
      proxy_info: A ProxyInfo instance identifying the proxy used for all
                  requests.
      disable_ssl_certificate_validation: A boolean indicating whether ssl
          certificate validation should be disabled while using a proxy.
      ca_certs: A string identifying the path to a file containing root CA
          certificates for SSL server certificate validation.
    """
    self.oauth2credentials = oauth2client.client.OAuth2Credentials(
        None, client_id, client_secret, refresh_token,
        datetime.datetime(1980, 1, 1, 12), self._GOOGLE_OAUTH2_ENDPOINT,
        self._USER_AGENT)
    self.proxy_info = proxy_info
    self.disable_ssl_certificate_validation = disable_ssl_certificate_validation
    self.ca_certs = ca_certs

  def CreateHttpHeader(self):
    """Creates an OAuth 2.0 HTTP header.

    The OAuth 2.0 credentials will be refreshed as necessary. In the event that
    the credentials fail to refresh, a message is logged but no exception is
    raised.

    Returns:
      A dictionary containing one entry: the OAuth 2.0 Bearer header under the
      'Authorization' key.

    Raises:
      AccessTokenRefreshError: If the refresh fails.
    """
    oauth2_header = {}

    if(self.oauth2credentials.token_expiry is not None and
       (self.oauth2credentials.token_expiry - datetime.datetime.utcnow() <
        datetime.timedelta(minutes=self._OAUTH2_REFRESH_MINUTES_IN_ADVANCE))):
      self.Refresh()

    self.oauth2credentials.apply(oauth2_header)
    return oauth2_header

  def Refresh(self):
    """Uses the Refresh Token to retrieve and set a new Access Token.

    Raises:
      AccessTokenRefreshError: If the refresh fails.
    """
    self.oauth2credentials.refresh(
        httplib2.Http(
            proxy_info=self.proxy_info,
            ca_certs=self.ca_certs,
            disable_ssl_certificate_validation=(
                self.disable_ssl_certificate_validation)))


class GoogleServiceAccountClient(GoogleOAuth2Client):
  """A simple client for using OAuth 2.0 for Google APIs with a service account.

  This class is not capable of supporting any flows other than generating
  credentials from a service account email and key file. This is incompatible
  with App Engine.

  Attributes:
    proxy_info: A ProxyInfo instance used for refresh requests.
  """
  # We will refresh an OAuth 2.0 credential _OAUTH2_REFRESH_MINUTES_IN_ADVANCE
  # minutes in advance of its expiration.
  _OAUTH2_REFRESH_MINUTES_IN_ADVANCE = 5
  _USER_AGENT = 'Google Ads Python Client Library'

  def __init__(self, scope, client_email, key_file,
               private_key_password='notasecret', sub=None, proxy_info=None,
               disable_ssl_certificate_validation=False, ca_certs=None):
    """Initializes a GoogleServiceAccountClient.

    Args:
      scope: The scope of the API you're authorizing for.
      client_email: A string containing your Service Account's email.
      key_file: A string containing the path to your key file.
      [optional]
      private_key_password: A string containing the password for your key file.
      sub: A string containing the email address of a user account you want to
           impersonate.
      proxy_info: A ProxyInfo instance identifying the proxy used for all
                  requests.
      disable_ssl_certificate_validation: A boolean indicating whether ssl
          certificate validation should be disabled while using a proxy.
      ca_certs: A string identifying the path to a file containing root CA
          certificates for SSL server certificate validation.

    Raises:
      GoogleAdsValueError: If the given key file does not exist.
    """
    try:
      with open(key_file) as f:
        private_key = f.read()
    except IOError:
      raise googleads.errors.GoogleAdsValueError('The specified key file (%s)'
                                                 ' does not exist.' % key_file)

    self.oauth2credentials = oauth2client.client.SignedJwtAssertionCredentials(
        client_email, private_key, scope, private_key_password,
        self._USER_AGENT, sub=sub)
    self.proxy_info = proxy_info
    self.disable_ssl_certificate_validation = disable_ssl_certificate_validation
    self.ca_certs = ca_certs
    self.Refresh()

  def CreateHttpHeader(self):
    """Creates an OAuth 2.0 HTTP header.

    The OAuth 2.0 credentials will be refreshed as necessary. In the event that
    the credentials fail to refresh, a message is logged but no exception is
    raised.

    Returns:
      A dictionary containing one entry: the OAuth 2.0 Bearer header under the
      'Authorization' key.

    Raises:
      AccessTokenRefreshError: If the refresh fails.
    """
    oauth2_header = {}

    if(self.oauth2credentials.token_expiry is not None and
       (self.oauth2credentials.token_expiry - datetime.datetime.utcnow() <
        datetime.timedelta(minutes=self._OAUTH2_REFRESH_MINUTES_IN_ADVANCE))):
      self.Refresh()

    self.oauth2credentials.apply(oauth2_header)
    return oauth2_header

  def Refresh(self):
    """Retrieve and set a new Access Token.

    Raises:
      AccessTokenRefreshError: If the refresh fails.
    """
    self.oauth2credentials.refresh(
        httplib2.Http(
            proxy_info=self.proxy_info,
            ca_certs=self.ca_certs,
            disable_ssl_certificate_validation=(
                self.disable_ssl_certificate_validation)))
