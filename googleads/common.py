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

"""Common client library functions and classes used by all products."""


import os
import ssl
import sys
import urllib2
import warnings

import httplib2
import socks
import suds
import suds.transport.http
import yaml

import googleads.errors
import googleads.oauth2
import googleads.patches

try:
  import urllib2.HTTPSHandler
except ImportError:
  # Python versions below 2.7.9 / 3.4 won't have this. In order to offer legacy
  # support (for now) we will work around this gracefully, but users will
  # not have certificate validation performed until they update.
  pass

VERSION = '4.0.0'
_COMMON_LIB_SIG = 'googleads/%s' % VERSION
_HTTP_PROXY_YAML_KEY = 'http_proxy'
_HTTPS_PROXY_YAML_KEY = 'https_proxy'
_PROXY_CONFIG_KEY = 'proxy_config'
_PYTHON_VERSION = 'Python/%d.%d.%d' % (sys.version_info[0], sys.version_info[1],
                                       sys.version_info[2])

# The keys in the authentication dictionary that are used to construct OAuth2
# credentials.
_OAUTH2_INSTALLED_APP_KEYS = ('client_id', 'client_secret', 'refresh_token')
_OAUTH2_SERVICE_ACCT_KEYS = ('service_account_email',
                             'path_to_private_key_file')

# The keys in the http_proxy and https_proxy dictionaries that are used to
# construct a Proxy, HTTPSProxy, and ProxyConfig instances.
# instance.
_PROXY_KEYS = ('host', 'port')

# Apply any necessary patches to dependency libraries.
googleads.patches.Apply()


def GenerateLibSig(short_name):
  """Generates a library signature suitable for a user agent field.

  Args:
    short_name: The short, product-specific string name for the library.
  Returns:
    A library signature string to append to user-supplied user-agent value.
  """
  return ' (%s, %s, %s)' % (short_name, _COMMON_LIB_SIG, _PYTHON_VERSION)


def LoadFromStorage(path, product_yaml_key, required_client_values,
                    optional_product_values):
  """Loads the data necessary for instantiating a client from file storage.

  In addition to the required_client_values argument, the yaml file must supply
  the keys used to create OAuth2 credentials. It may also optionally set proxy
  configurations.

  Args:
    path: A path string to the yaml document whose keys should be used.
    product_yaml_key: The key to read in the yaml as a string.
    required_client_values: A tuple of strings representing values which must
      be in the yaml file for a supported API. If one of these keys is not in
      the yaml file, an error will  be raised.
    optional_product_values: A tuple of strings representing optional values
      which may be in the yaml file.

  Returns:
    A dictionary map of the keys in the yaml file to their values. This will not
    contain the keys used for OAuth2 client creation and instead will have a
    GoogleOAuth2Client object stored in the 'oauth2_client' field.

  Raises:
    A GoogleAdsValueError if the given yaml file does not contain the
    information necessary to instantiate a client object - either a
    required_client_values key was missing or an OAuth2 key was missing.
  """
  if not os.path.isabs(path):
    path = os.path.expanduser(path)
  try:
    with open(path, 'rb') as handle:
      data = yaml.safe_load(handle.read())
      product_data = data[product_yaml_key]
      proxy_config_data = data.get(_PROXY_CONFIG_KEY) or {}
  except IOError:
    raise googleads.errors.GoogleAdsValueError(
        'Given yaml file, %s, could not be opened.' % path)
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Given yaml file, %s, does not contain a "%s" configuration.'
        % (path, product_yaml_key))

  original_keys = list(product_data.keys())
  client_kwargs = {}
  try:
    for key in required_client_values:
      client_kwargs[key] = product_data[key]
      del product_data[key]
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Your yaml file, %s, is missing some of the required values. Required '
        'values are: %s, actual values are %s'
        % (path, required_client_values, original_keys))

  http_proxy = None
  https_proxy = None

  # HTTP Proxy Config
  try:
    if 'http_proxy' in proxy_config_data:
      http_proxy_data = proxy_config_data.get('http_proxy')
      original_http_proxy_keys = list(http_proxy_data.keys())
      http_proxy = ProxyConfig.Proxy(
          http_proxy_data['host'], http_proxy_data['port'],
          username=http_proxy_data.get('username'),
          password=http_proxy_data.get('password'))
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Your yaml file, %s, is missing some of the required http proxy '
        'values. Required values are: %s, actual values are %s'
        % (path, _PROXY_KEYS, original_http_proxy_keys))
  # HTTPS Proxy Config
  # Note: If both HTTP and HTTPS proxies are specified, the ProxyInfo used
  # by oauth2.py will always be the HTTPS proxy.
  try:
    if 'https_proxy' in proxy_config_data:
      https_proxy_data = proxy_config_data.get('https_proxy')
      original_https_proxy_keys = list(https_proxy_data.keys())
      https_proxy = ProxyConfig.Proxy(
          https_proxy_data['host'], https_proxy_data['port'],
          username=https_proxy_data.get('username'),
          password=https_proxy_data.get('password'))
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Your yaml file, %s, is missing some of the required https proxy '
        'values. Required values are: %s, actual values are %s'
        % (path, _PROXY_KEYS, original_https_proxy_keys))

  cafile = proxy_config_data.get('cafile', None)
  disable_certificate_validation = proxy_config_data.get(
      'disable_certificate_validation', False)
  proxy_config = ProxyConfig(
      http_proxy=http_proxy, https_proxy=https_proxy, cafile=cafile,
      disable_certificate_validation=disable_certificate_validation)
  client_kwargs['proxy_config'] = proxy_config

  if all(config in product_data for config in _OAUTH2_INSTALLED_APP_KEYS):
    # Use provided configurations for the installed application flow.
    client_kwargs['oauth2_client'] = (
        googleads.oauth2.GoogleRefreshTokenClient(
            product_data['client_id'], product_data['client_secret'],
            product_data['refresh_token'], proxy_config=proxy_config))
    for key in _OAUTH2_INSTALLED_APP_KEYS:
      del product_data[key]
  elif all(config in product_data for config in _OAUTH2_SERVICE_ACCT_KEYS):
    # Use provided configurations for the service account flow.
    client_kwargs['oauth2_client'] = (
        googleads.oauth2.GoogleServiceAccountClient(
            googleads.oauth2.GetAPIScope(product_yaml_key),
            product_data['service_account_email'],
            product_data['path_to_private_key_file'],
            proxy_config=proxy_config))
    for key in _OAUTH2_SERVICE_ACCT_KEYS:
      del product_data[key]
  else:
    raise googleads.errors.GoogleAdsValueError(
        'Your yaml file, %s, is incorrectly configured for OAuth2. You '
        'need to specify credentials for either the installed application '
        'flow (%s) or service account flow (%s). Actual values provided are: '
        '%s' % (path, _OAUTH2_INSTALLED_APP_KEYS, _OAUTH2_SERVICE_ACCT_KEYS,
                original_keys))

  for value in optional_product_values:
    if value in product_data:
      client_kwargs[value] = product_data[value]
      del product_data[value]

  if product_data:
    warnings.warn(
        'Your yaml file, %s, contains the following unrecognized '
        'keys: %s. They were ignored.' % (path, product_data), stacklevel=3)

  return client_kwargs


def _PackForSuds(obj, factory):
  """Packs SOAP input into the format we want for suds.

  The main goal here is to pack dictionaries with an 'xsi_type' key into
  objects. This allows dictionary syntax to be used even with complex types
  extending other complex types. The contents of dictionaries and lists/tuples
  are recursively packed. Mutable types are copied - we don't mutate the input.

  Args:
    obj: A parameter for a SOAP request which will be packed. If this is
        a dictionary or list, the contents will recursively be packed. If this
        is not a dictionary or list, the contents will be recursively searched
        for instances of unpacked dictionaries or lists.
    factory: The suds.client.Factory object which can create instances of the
        classes generated from the WSDL.

  Returns:
    If the given obj was a dictionary that contained the 'xsi_type' key, this
    will be an instance of a class generated from the WSDL. Otherwise, this will
    be the same data type as the input obj was.
  """
  if obj in ({}, None):
    # Force suds to serialize empty objects. There are legitimate use cases for
    # this, for example passing in an empty SearchCriteria object to a DFA
    # search method in order to select everything.
    return suds.null()
  elif isinstance(obj, dict):
    if 'xsi_type' in obj:
      try:
        new_obj = factory.create(obj['xsi_type'])
      except suds.TypeNotFound:
        new_obj = factory.create(':'.join(['ns0', obj['xsi_type']]))
      # Suds sends an empty XML element for enum types which are not set. None
      # of Google's Ads APIs will accept this. Initializing all of the fields in
      # a suds object to None will ensure that they don't get serialized at all
      # unless the user sets a value. User values explicitly set to None will be
      # packed into a suds.null() object.
      for param, _ in new_obj:
        # Another problem is that the suds.mx.appender.ObjectAppender won't
        # serialize object types with no fields set, but both AdWords and DFP
        # rely on sending objects with just the xsi:type set. The below "if"
        # statement is an ugly hack that gets this to work in all(?) situations
        # by taking advantage of the fact that these classes generally all have
        # a type field. The only other option is to monkey patch ObjectAppender.
        if param.endswith('.Type'):
          setattr(new_obj, param, obj['xsi_type'])
        else:
          setattr(new_obj, param, None)
      for key in obj:
        if key == 'xsi_type': continue
        setattr(new_obj, key, _PackForSuds(obj[key], factory))
    else:
      new_obj = {}
      for key in obj:
        new_obj[key] = _PackForSuds(obj[key], factory)
    return new_obj
  elif isinstance(obj, (list, tuple)):
    return [_PackForSuds(item, factory) for item in obj]
  else:
    _RecurseOverObject(obj, factory)
    return obj


def _RecurseOverObject(obj, factory, parent=None):
  """Recurses over a nested structure to look for changes in Suds objects.

    Args:
      obj: A parameter for a SOAP request field which is to be inspected and
          will be packed for Suds if an xsi_type is specified, otherwise will be
          left unaltered.
      factory: The suds.client.Factory object which can create instances of the
          classes generated from the WSDL.
      parent: The parent object that contains the obj parameter to be inspected.
  """
  if _IsSudsIterable(obj):
    # Since in-place modification of the Suds object is taking place, the
    # iterator should be done over a frozen copy of the unpacked fields.
    copy_of_obj = tuple(obj)
    for item in copy_of_obj:
      if _IsSudsIterable(item):
        if 'xsi_type' in item:
          if isinstance(obj, tuple):
            parent[obj[0]] = _PackForSuds(obj[1], factory)
          else:
            obj.remove(item)
            obj.append(_PackForSuds(item, factory))
        _RecurseOverObject(item, factory, obj)


def _IsSudsIterable(obj):
  """A short helper method to determine if a field is iterable for Suds."""
  return (obj and not isinstance(obj, basestring) and hasattr(obj, '__iter__'))


class ProxyConfig(object):
  """A utility for configuring the usage of a proxy."""

  def __init__(self, http_proxy=None, https_proxy=None, cafile=None,
               disable_certificate_validation=False):
    self._http_proxy = http_proxy
    self._https_proxy = https_proxy
    # Initialize httplib2.ProxyInfo used by oauth2client and a proxy option
    # dictionary used to generate the urllib2.ProxyHandler used by suds and
    # urllib2. For the ProxyInfo object, the HTTPS proxy will always be used
    # over the HTTP proxy if it is available.
    self.proxy_info = None
    self._proxy_option = {}
    if self._https_proxy:
      self.proxy_info = httplib2.ProxyInfo(
          socks.PROXY_TYPE_HTTP, self._https_proxy.host, self._https_proxy.port,
          proxy_user=self._https_proxy.username,
          proxy_pass=self._https_proxy.password)
      self._proxy_option['https'] = str(self._https_proxy)
    if self._http_proxy:
      if not self.proxy_info:
        self.proxy_info = httplib2.ProxyInfo(
            socks.PROXY_TYPE_HTTP, self._http_proxy.host, self._http_proxy.port,
            proxy_user=self._http_proxy.username,
            proxy_pass=self._http_proxy.password)
      self._proxy_option['http'] = str(self._http_proxy)

    self.disable_certificate_validation = disable_certificate_validation
    self.cafile = None if disable_certificate_validation else cafile
    # Initialize the context used to generate the urllib2.HTTPSHandler (in
    # Python 2.7.9+ and 3.4+) used by suds and urllib2.
    self._ssl_context = self._InitSSLContext(
        self.cafile, self.disable_certificate_validation)

  def _InitSSLContext(self, cafile=None,
                      disable_ssl_certificate_validation=False):
    """Creates a ssl.SSLContext with the given settings.

    Args:
      cafile: A str identifying the resolved path to the cafile. If not set,
        this will use the system default cafile.
      disable_ssl_certificate_validation: A boolean indicating whether
        certificate verification is disabled. For security purposes, it is
        highly recommended that certificate verification remain enabled.

    Returns:
      An ssl.SSLContext instance, or None if the version of Python being used
      doesn't support it.
    """
    # Attempt to create a context; this should succeed in Python 2 versions
    # 2.7.9+ and Python 3 versions 3.4+.
    try:
      ssl_context = ssl.create_default_context(cafile=cafile)
    except AttributeError:
      # Earlier versions lack ssl.create_default_context()
      # Rather than raising the exception, no context will be provided for
      # legacy support. Of course, this means no certificate validation is
      # taking place!
      return None

    if disable_ssl_certificate_validation:
      ssl_context.verify_mode = ssl.CERT_NONE

    return ssl_context

  def GetHandlers(self):
    """Retrieve the appropriate urllib2 handlers for the given configuration.

    Returns:
      A list of urllib2.BaseHandler subclasses to be used when making calls
      with proxy.
    """
    handlers = []

    if self._ssl_context:
      handlers.append(urllib2.HTTPSHandler(self._ssl_context))

    if self._proxy_option:
      handlers.append(urllib2.ProxyHandler(self._proxy_option))

    return handlers

  def GetSudsProxyTransport(self):
    """Retrieve a suds.transport.http.HttpTransport to be used with suds.

    This will apply all handlers relevant to the usage of the proxy
    configuration automatically.

    Returns:
      A _SudsProxyTransport instance used to make requests with suds using the
      configured proxy.
    """
    return self._SudsProxyTransport(self.GetHandlers())

  class Proxy(object):
    """Defines settings for a proxy connection."""

    STR_TEMPLATE = '%s:%s'
    CRED_TEMPLATE = '%s@%s'

    def __init__(self, host, port, username=None, password=''):
      self.host = host
      self.port = port
      self.username = username
      self.password = password

    def __str__(self):
      if self.username:
        s = self.CRED_TEMPLATE % (
            self.STR_TEMPLATE % (
                self.username, self.password),
            self.STR_TEMPLATE % (self.host, self.port))
      else:
        s = self.STR_TEMPLATE % (self.host, self.port)
      return s

  class _SudsProxyTransport(suds.transport.http.HttpTransport):
    """A transport that applies the given handlers for usage with a proxy."""

    def __init__(self, handlers, **kwargs):
      """Initializes SudsHTTPSTransport.

      Args:
        handlers: an iterable of urllib2.BaseHandler subclasses.
        **kwargs: Keyword arguments.
      """
      suds.transport.http.HttpTransport.__init__(self, **kwargs)
      self.handlers = handlers

    def u2handlers(self):
      """Get a collection of urllib2 handlers to be installed in the opener.

      Returns:
        A list of handlers to be installed to the OpenerDirector used by suds.
      """
      # Start with the default set of handlers.
      return_handlers = suds.transport.http.HttpTransport.u2handlers(self)
      return_handlers.extend(self.handlers)

      return return_handlers


class SudsServiceProxy(object):
  """Wraps a suds service object, allowing custom logic to be injected.

  This class is responsible for refreshing the HTTP and SOAP headers, so changes
  to the client object will be reflected in future SOAP calls, and for
  transforming SOAP call input parameters, allowing dictionary syntax to be used
  with all SOAP complex types.

  Attributes:
    suds_client: The suds.client.Client this service belongs to. If you are
        familiar with suds and want to use autogenerated classes, you can access
        the client and its factory,
  """

  def __init__(self, suds_client, header_handler):
    """Initializes a suds service proxy.

    Args:
      suds_client: The suds.client.Client whose service will be wrapped. Note
        that this is the client itself, not the client's embedded service
        object.
      header_handler: A HeaderHandler responsible for setting the SOAP and HTTP
          headers on the service client.
    """
    self.suds_client = suds_client
    self._header_handler = header_handler
    self._method_proxies = {}

  def __getattr__(self, attr):
    if attr in self.suds_client.wsdl.services[0].ports[0].methods:
      if attr not in self._method_proxies:
        self._method_proxies[attr] = self._CreateMethod(attr)
      return self._method_proxies[attr]
    else:
      return getattr(self.suds_client.service, attr)

  def _CreateMethod(self, method_name):
    """Create a method wrapping an invocation to the SOAP service.

    Args:
      method_name: A string identifying the name of the SOAP method to call.

    Returns:
      A callable that can be used to make the desired SOAP request.
    """
    soap_service_method = getattr(self.suds_client.service, method_name)

    def MakeSoapRequest(*args):
      """Perform a SOAP call."""
      self._header_handler.SetHeaders(self.suds_client)
      return soap_service_method(*[_PackForSuds(arg, self.suds_client.factory)
                                   for arg in args])

    return MakeSoapRequest


class HeaderHandler(object):
  """A generic header handler interface that must be subclassed by each API."""

  def SetHeaders(self, client):
    """Sets the SOAP and HTTP headers on the given suds client."""
    raise NotImplementedError('You must subclass HeaderHandler.')
