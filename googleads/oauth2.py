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
authorize API requests and some simple implementations built on oauthlib. If our
OAuth 2.0 workflows doesn't meet your requirements, you can implement this
interface in your own way. For example, you could pull credentials from a shared
server and/or centralize refreshing credentials to prevent every Python process
from independently refreshing the credentials.
"""

__author__ = 'Joseph DiLallo'

import logging
import sys
import urllib2
import json

from oauthlib import oauth2

from googleads import errors

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


class GoogleRefreshTokenClient(GoogleOAuth2Client):
  """A simple client for using OAuth 2.0 for Google APIs with a refresh token.

  This class is not capable of supporting any flows other than taking an
  existing, active refresh token and generating credentials from it. It does not
  matter which of Google's OAuth 2.0 flows you used to generate the refresh
  token (installed application, web flow, etc.).

  Attributes:
    https_proxy: The address of a proxy to use for HTTPS refresh requests.
  """

  # The HTTP headers needed on OAuth 2.0 refresh requests.
  _OAUTH2_REFRESH_HEADERS = {'content-type':
                             'application/x-www-form-urlencoded'}
  # The web address for generating OAuth 2.0 credentials at Google.
  _GOOGLE_OAUTH2_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
  # The placeholder URL is used when adding the access token to our request. A
  # well-formed URL is required, but since we're using HTTP header placement for
  # the token, this URL is completely unused.
  _TOKEN_URL = 'https://www.google.com'

  def __init__(self, client_id, client_secret, refresh_token, https_proxy=None):
    """Initializes a GoogleRefreshTokenClient.

    Args:
      client_id: A string containing your client ID.
      client_secret: A string containing your client secret.
      refresh_token: A string containing your refresh token.
      [optional]
      https_proxy: A string identifying the URL of a proxy that all HTTPS
          requests should be routed through.
    """
    self._oauthlib_client = oauth2.BackendApplicationClient(
        client_id,
        token={'access_token': 'None', 'refresh_token': refresh_token,
               'token_type': 'Bearer', 'expires_in': '-30'})
    self._client_secret = client_secret
    self.https_proxy = https_proxy

  def HandleOAuthError(self, error):
    """HTTP Errors during OAuth operations are all handled here.

    Always raises an exception. Which one depends on the OAuth error code in
    the response body.

    The error param is should be of type urllib2.HTTPError.
    """

    error_str = u'{}'.format(error)

    # Most server errors are only temporary and may very well be successful
    # upon retry.
    if int(error.code) in (500, 502, 503, 504):
        raise errors.OAuthTemporaryServerError(error_str)

    # HTTPError instances have a read() method when it was given a file-object,
    # i.e. a response body is available.
    if hasattr(error, 'read'):
      msg_body = error.read()
    else:
      raise errors.OAuthUnknownError(error_str)

    # TODO: check content type of response before parsing json

    try:
      oauth_error = json.loads(msg_body)
    except ValueError:
      raise errors.OAuthUnknownError(error_str)

    # See http://tools.ietf.org/html/rfc6749#section-5.2 for error codes.
    error_map = {
      'invalid_request': errors.OAuthInvalidRequestError,
      'invalid_grant': errors.OAuthInvalidGrantError,
      'invalid_scope': errors.OAuthInvalidScopeError,
      'invalid_client': errors.OAuthInvalidClientError,
      'unauthorized_client': errors.OAuthUnauthorizedClientError,
      'unsupported_grant_type': errors.OAuthUnsupportedGrantTypeError,
    }

    error_msg = oauth_error.get('error')
    exc_type = error_map.get(error_msg, errors.OAuthUnknownError)
    raise exc_type(oauth_error)

  def CreateHttpHeader(self):
    """Creates an OAuth 2.0 HTTP header.

    The OAuth 2.0 credentials will be refreshed as necessary. In the event that
    the credentials fail to refresh, a message is logged but no exception is
    raised.

    Returns:
      A dictionary containing one entry: the OAuth 2.0 Bearer header under the
      'Authorization' key.
    """
    oauth2_header = {}
    try:
      _, oauth2_header, _ = self._oauthlib_client.add_token(self._TOKEN_URL)
    except oauth2.TokenExpiredError:
      post_body = self._oauthlib_client.prepare_refresh_body(
          client_id=self._oauthlib_client.client_id,
          client_secret=self._client_secret)
      if sys.version_info[0] == 3:
        post_body = bytes(post_body, 'utf8')
      try:
        request = urllib2.Request(self._GOOGLE_OAUTH2_ENDPOINT, post_body,
                                  self._OAUTH2_REFRESH_HEADERS)

        if self.https_proxy:
          proxy_support = urllib2.ProxyHandler({'https': self.https_proxy})
          opener = urllib2.build_opener(proxy_support)
        else:
          opener = urllib2.build_opener()

        # Need to decode the content - in Python 3 it's bytes, not a string.
        content = opener.open(request).read().decode()
        self._oauthlib_client.parse_request_body_response(content)
        _, oauth2_header, _ = self._oauthlib_client.add_token(self._TOKEN_URL)
      except urllib2.HTTPError, e:
        self.HandleOAuthError(e)
      except Exception, e:
        logging.warning('OAuth 2.0 credentials failed to refresh! Failure was: '
                        '%s', e)
    # In Python 2, the headers must all be str - not unicode - or else urllib2
    # will fail to parse the message. oauthlib returns unicode objects.
    if oauth2_header and sys.version_info[0] == 2:
      oauth2_header = {'Authorization': str(oauth2_header['Authorization'])}
    return oauth2_header
