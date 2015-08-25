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

"""Client library for the DoubleClick for Advertisers API."""


import os

import suds.client
import suds.sax.element
import suds.transport
import suds.wsse

import googleads.common
import googleads.errors


class DfaClient(object):
  """A central location to set headers and create web service clients.

  Attributes:
    username: A string representation of your DFA username.
    oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize your
        requests.
    application_name: An arbitrary string which will be used to identify your
        application
    https_proxy: A string identifying the URL of a proxy that all HTTPS requests
        should be routed through. Modifying this value will not affect any SOAP
        service clients you've already created.
  """

  # The key in the storage yaml which contains DFA data.
  _YAML_KEY = 'dfa'
  # A list of values which must be provided to use DFA.
  _REQUIRED_INIT_VALUES = ('application_name', 'username')
  # A list of values which may optionally be provided when using DFA.
  _OPTIONAL_INIT_VALUES = ()
  # The format of SOAP service WSDLs. A server, version, and service name need
  # to be formatted in.
  _SOAP_SERVICE_FORMAT = '%s/%s/api/dfa-api/%s?wsdl'
  # A giant dictionary of DFA versions and the services they support.
  _SERVICE_MAP = {
      'v1.19': ('ad', 'advertiser', 'advertisergroup', 'campaign', 'changelog',
                'contentcategory', 'creative', 'creativefield', 'creativegroup',
                'login', 'network', 'placement', 'site', 'size', 'spotlight',
                'strategy', 'subnetwork', 'user', 'userrole', 'report'),
      'v1.20': ('ad', 'advertiser', 'advertisergroup', 'campaign', 'changelog',
                'contentcategory', 'creative', 'creativefield', 'creativegroup',
                'login', 'network', 'placement', 'site', 'size', 'spotlight',
                'strategy', 'subnetwork', 'user', 'userrole', 'report'),
  }

  @classmethod
  def LoadFromStorage(cls, path=None):
    """Creates an DfaClient with information stored in a yaml file.

    Args:
      [optional]
      path: The path string to the file containing cached DFA data.

    Returns:
      A DfaClient initialized with the values cached in the file.

    Raises:
      A GoogleAdsValueError if the given yaml file does not contain the
      information necessary to instantiate a client object - either a
      required key was missing or an OAuth 2.0 key was missing.
    """
    if path is None:
      path = os.path.join(os.path.expanduser('~'), 'googleads.yaml')

    return cls(**googleads.common.LoadFromStorage(
        path, cls._YAML_KEY, cls._REQUIRED_INIT_VALUES,
        cls._OPTIONAL_INIT_VALUES))

  def __init__(self, username, oauth2_client, application_name,
               https_proxy=None, cache=None):
    """Initializes a DfaClient.

    For more information on these arguments, see our SOAP headers guide:
    https://developers.google.com/doubleclick-advertisers/docs/SOAP_headers

    Args:
      username: A string representation of your DFA username. This is likely not
          the same as your Google Account name.
      oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize
          your requests.
      application_name: An arbitrary string which will be used to identify your
          application
      [optional]
      https_proxy: A string identifying the proxy that all HTTPS requests
          should be routed through.
      cache: A subclass of suds.cache.Cache; defaults to None.
    """
    self.username = username
    self.oauth2_client = oauth2_client
    self.application_name = application_name
    self.https_proxy = https_proxy
    self.cache = cache
    self._header_handler = _DfaHeaderHandler(self)

  def GetService(self, service_name, version=sorted(_SERVICE_MAP.keys())[-1],
                 server='https://advertisersapi.doubleclick.com'):
    """Creates a service client for the given service.

    Args:
      service_name: A string identifying which DFA service to create a service
          client for.
      [optional]
      version: A string identifying the DFA version to connect to. This defaults
          to what is currently the latest version. This will be updated in
          future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the DFA API.

    Returns:
      A suds.client.ServiceSelector which has the headers and proxy configured
          for use.

    Raises:
      A GoogleAdsValueError if the service or version provided do not exist.
    """
    server = server[:-1] if server[-1] == '/' else server
    try:
      proxy_option = None
      if self.https_proxy:
        proxy_option = {
            'https': self.https_proxy
        }

      client = suds.client.Client(
          self._SOAP_SERVICE_FORMAT % (server, version, service_name),
          proxy=proxy_option, cache=self.cache, timeout=3600)
    except suds.transport.TransportError:
      if version in self._SERVICE_MAP:
        if service_name in self._SERVICE_MAP[version]:
          raise
        else:
          raise googleads.errors.GoogleAdsValueError(
              'Unrecognized service for the DFA API. Service given: %s '
              'Supported services: %s'
              % (service_name, self._SERVICE_MAP[version]))
      else:
        raise googleads.errors.GoogleAdsValueError(
            'Unrecognized version of the DFA API. Version given: %s Supported '
            'versions: %s' % (version, self._SERVICE_MAP.keys()))

    return googleads.common.SudsServiceProxy(client, self._header_handler)


class _DfaHeaderHandler(googleads.common.HeaderHandler):
  """Handler which sets the headers for a DFA SOAP call."""

  # The library signature for DFA, to be appended to all application_names.
  _LIB_SIG = googleads.common.GenerateLibSig('DfaApi-Python')

  def __init__(self, dfa_client):
    """Initializes a DfaHeaderHandler.

    Args:
      dfa_client: The DfaClient whose data will be used to fill in the headers.
          We retain a reference to this object so that the header handler picks
          up changes to the client.
    """
    self._dfa_client = dfa_client

  def SetHeaders(self, suds_client):
    """Sets the SOAP and HTTP headers on the given suds client."""
    wsse_header = suds.wsse.Security()
    wsse_header.tokens.append(
        suds.wsse.UsernameToken(self._dfa_client.username))
    request_header = suds.sax.element.Element('RequestHeader')
    request_header.append(
        suds.sax.element.Element('applicationName').setText(
            ''.join([self._dfa_client.application_name, self._LIB_SIG])))

    suds_client.set_options(
        wsse=wsse_header, soapheaders=request_header,
        headers=self._dfa_client.oauth2_client.CreateHttpHeader())
