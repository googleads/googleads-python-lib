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


import datetime
from functools import wraps
import inspect
import locale
import logging
import logging.config
import os
import ssl
import sys
import threading
import urllib2
import warnings


import httplib2
import socks
import suds
import suds.transport.http
import yaml

import googleads.errors
import googleads.oauth2
import googleads.util

try:
  import urllib2.HTTPSHandler
except ImportError:
  # Python versions below 2.7.9 / 3.4 won't have this. In order to offer legacy
  # support (for now) we will work around this gracefully, but users will
  # not have certificate validation performed until they update.
  pass


logging.getLogger('suds.client').addFilter(googleads.util.GetSudsClientFilter())
logging.getLogger('suds.mx.core').addFilter(
    googleads.util.GetSudsMXCoreFilter())
logging.getLogger('suds.mx.literal').addFilter(
    googleads.util.GetSudsMXLiteralFilter())
logging.getLogger('suds.transport.http').addFilter(
    googleads.util.GetSudsTransportFilter())
_logger = logging.getLogger(__name__)

_PY_VERSION_MAJOR = sys.version_info.major
_PY_VERSION_MINOR = sys.version_info.minor
_PY_VERSION_MICRO = sys.version_info.micro
_DEPRECATED_VERSION_TEMPLATE = (
    'This library is being run by an unsupported Python version (%s.%s.%s). In '
    'order to benefit from important security improvements and ensure '
    'compatibility with this library, upgrade to Python 2.7.9 or higher.')


VERSION = '6.1.0'
_COMMON_LIB_SIG = 'googleads/%s' % VERSION
_LOGGING_KEY = 'logging'
_HTTP_PROXY_YAML_KEY = 'http_proxy'
_HTTPS_PROXY_YAML_KEY = 'https_proxy'
_PROXY_CONFIG_KEY = 'proxy_config'
_PYTHON_VERSION = 'Python/%d.%d.%d' % (
    _PY_VERSION_MAJOR, _PY_VERSION_MINOR, _PY_VERSION_MICRO)

# The required keys in the authentication dictionary that are used to construct
# installed application OAuth2 credentials.
_OAUTH2_INSTALLED_APP_KEYS = ('client_id', 'client_secret', 'refresh_token')

# The keys in the authentication dictionary that are used to construct service
# account OAuth2 credentials. This will differ based on the oauth2client
# installation.
if googleads.oauth2.DEPRECATED_OAUTH2CLIENT:
  _OAUTH2_SERVICE_ACCT_KEYS = ('service_account_email',
                               'path_to_private_key_file')
  _OAUTH2_SERVICE_ACCT_KEYS_OPTIONAL = ('delegated_account',)
else:
  _OAUTH2_SERVICE_ACCT_KEYS = ('path_to_private_key_file',)
  _OAUTH2_SERVICE_ACCT_KEYS_OPTIONAL = ('delegated_account',
                                        'service_account_email')

# The keys in the http_proxy and https_proxy dictionaries that are used to
# construct a Proxy, HTTPSProxy, and ProxyConfig instances.
# instance.
_PROXY_KEYS = ('host', 'port')

# A key used to configure the client to accept and automatically decompress
# gzip encoded SOAP responses.
ENABLE_COMPRESSION_KEY = 'enable_compression'

# Global variables used to enable and store utility usage stats.
_utility_registry = googleads.util.UtilityRegistry()
_UTILITY_REGISTER_YAML_KEY = 'include_utilities_in_user_agent'
_UTILITY_LOCK = threading.Lock()

# Apply any necessary patches to dependency libraries.
googleads.util.PatchHelper().Apply()


def GenerateLibSig(short_name):
  """Generates a library signature suitable for a user agent field.

  Args:
    short_name: The short, product-specific string name for the library.
  Returns:
    A library signature string to append to user-supplied user-agent value.
  """
  with _UTILITY_LOCK:
    utilities_used = ', '.join([utility for utility in _utility_registry])
    _utility_registry.Clear()

  if utilities_used:
    return ' (%s, %s, %s, %s)' % (short_name, _COMMON_LIB_SIG, _PYTHON_VERSION,
                                  utilities_used)
  else:
    return ' (%s, %s, %s)' % (short_name, _COMMON_LIB_SIG, _PYTHON_VERSION)


def LoadFromString(yaml_doc, product_yaml_key, required_client_values,
                   optional_product_values):
  """Loads the data necessary for instantiating a client from file storage.

  In addition to the required_client_values argument, the yaml file must supply
  the keys used to create OAuth2 credentials. It may also optionally set proxy
  configurations.

  Args:
    yaml_doc: the yaml document whose keys should be used.
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
  data = yaml.safe_load(yaml_doc) or {}

  logging_config = data.get(_LOGGING_KEY)
  if logging_config:
    logging.config.dictConfig(logging_config)

  # Warn users on deprecated Python versions on initialization.
  if _PY_VERSION_MAJOR == 2:
    if _PY_VERSION_MINOR == 7 and _PY_VERSION_MICRO < 9:
      _logger.warning(_DEPRECATED_VERSION_TEMPLATE, _PY_VERSION_MAJOR,
                      _PY_VERSION_MINOR, _PY_VERSION_MICRO)
    elif _PY_VERSION_MINOR < 7:
      _logger.warning(_DEPRECATED_VERSION_TEMPLATE, _PY_VERSION_MAJOR,
                      _PY_VERSION_MINOR, _PY_VERSION_MICRO)

  # Warn users about using non-utf8 encoding
  _, encoding = locale.getdefaultlocale()
  if encoding is None or encoding.lower() != 'utf-8':
    _logger.warn('Your default encoding, %s, is not UTF-8. Please run this'
                 ' script with UTF-8 encoding to avoid errors.', encoding)

  try:
    product_data = data[product_yaml_key]
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'The "%s" configuration is missing'
        % (product_yaml_key,))

  if not isinstance(product_data, dict):
    raise googleads.errors.GoogleAdsValueError(
        'The "%s" configuration is empty or invalid'
        % (product_yaml_key,))

  IncludeUtilitiesInUserAgent(data.get(_UTILITY_REGISTER_YAML_KEY, True))

  original_keys = list(product_data.keys())
  client_kwargs = {}
  try:
    for key in required_client_values:
      client_kwargs[key] = product_data[key]
      del product_data[key]
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Some of the required values are missing. Required '
        'values are: %s, actual values are %s'
        % (required_client_values, original_keys))

  proxy_config_data = data.get(_PROXY_CONFIG_KEY, {})
  proxy_config = _ExtractProxyConfig(product_yaml_key, proxy_config_data)
  client_kwargs['proxy_config'] = proxy_config
  client_kwargs['oauth2_client'] = _ExtractOAuth2Client(
      product_yaml_key, product_data, proxy_config)

  client_kwargs[ENABLE_COMPRESSION_KEY] = data.get(
      ENABLE_COMPRESSION_KEY, False)

  for value in optional_product_values:
    if value in product_data:
      client_kwargs[value] = product_data[value]
      del product_data[value]

  if product_data:
    warnings.warn('Could not recognize the following keys: %s. '
                  'They were ignored.' % (product_data,), stacklevel=3)

  return client_kwargs


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
      yaml_doc = handle.read()
  except IOError:
    raise googleads.errors.GoogleAdsValueError(
        'Given yaml file, %s, could not be opened.' % path)

  try:
    client_kwargs = LoadFromString(yaml_doc, product_yaml_key,
                                   required_client_values,
                                   optional_product_values)
  except googleads.errors.GoogleAdsValueError as e:
    e.message = ('Given yaml file, %s, '
                 'could not find some keys. %s' % (path, e.message))
    raise

  return client_kwargs


def _ExtractOAuth2Client(product_yaml_key, product_data, proxy_config):
  """Generates an GoogleOAuth2Client subclass using the given product_data.

  Args:
    product_yaml_key: a string key identifying the product being configured.
    product_data: a dict containing the configurations for a given product.
    proxy_config: a ProxyConfig instance.

  Returns:
    An instantiated GoogleOAuth2Client subclass.

  Raises:
    A GoogleAdsValueError if the OAuth2 configuration for the given product is
    misconfigured.
  """
  oauth2_kwargs = {
      'proxy_config': proxy_config
  }

  if all(config in product_data for config in _OAUTH2_INSTALLED_APP_KEYS):
    oauth2_args = [
        product_data['client_id'], product_data['client_secret'],
        product_data['refresh_token']
    ]
    oauth2_client = googleads.oauth2.GoogleRefreshTokenClient
    for key in _OAUTH2_INSTALLED_APP_KEYS:
      del product_data[key]
  elif all(config in product_data for config in _OAUTH2_SERVICE_ACCT_KEYS):
    oauth2_args = [
        googleads.oauth2.GetAPIScope(product_yaml_key),
    ]
    oauth2_kwargs.update({
        'client_email': product_data.get('service_account_email'),
        'key_file': product_data['path_to_private_key_file'],
        'sub': product_data.get('delegated_account')
    })
    oauth2_client = googleads.oauth2.GoogleServiceAccountClient
    for key in _OAUTH2_SERVICE_ACCT_KEYS:
      del product_data[key]
    for optional_key in _OAUTH2_SERVICE_ACCT_KEYS_OPTIONAL:
      if optional_key in product_data:
        del product_data[optional_key]
  else:
    raise googleads.errors.GoogleAdsValueError(
        'Your yaml file is incorrectly configured for OAuth2. You need to '
        'specify credentials for either the installed application flow (%s) '
        'or service account flow (%s).' %
        (_OAUTH2_INSTALLED_APP_KEYS, _OAUTH2_SERVICE_ACCT_KEYS))

  return oauth2_client(*oauth2_args, **oauth2_kwargs)


def _ExtractProxyConfig(product_yaml_key, proxy_config_data):
  """Returns an initialized ProxyConfig using the given proxy_config_data.

  Args:
    product_yaml_key: a string indicating the client being loaded.
    proxy_config_data: a dict containing the contents of proxy_config from the
      YAML file.

  Returns:
    If there is a proxy to configure in proxy_config, this will return a
    ProxyConfig instance with those settings. Otherwise, it will return None.

  Raises:
    A GoogleAdsValueError if one of the required keys specified by _PROXY_KEYS
    is missing.
  """
  cafile = proxy_config_data.get('cafile', None)
  disable_certificate_validation = proxy_config_data.get(
      'disable_certificate_validation', False)
  http_proxy = _ExtractProxy(_HTTP_PROXY_YAML_KEY, proxy_config_data)
  https_proxy = _ExtractProxy(_HTTPS_PROXY_YAML_KEY, proxy_config_data)
  proxy_config = ProxyConfig(
      http_proxy=http_proxy,
      https_proxy=https_proxy,
      cafile=cafile,
      disable_certificate_validation=disable_certificate_validation)

  return proxy_config


def _ExtractProxy(proxy_yaml_key, proxy_config_data):
  """Extracts a ProxyConfig.Proxy from the proxy_config for a given key.

  Args:
    proxy_yaml_key: a key specifying the type of proxy for which data is being
      loaded.
    proxy_config_data: a dict containing the proxy configurations loaded from
      the YAML file.

  Returns:
    If the proxy_yaml_key exists in the proxy_config_data, this will return a
    ProxyConfig.Proxy instance initialized with the data associated with it.
    Otherwise, this will return None.

  Raises:
    A GoogleAdsValueError if one of the required keys specified by _PROXY_KEYS
    is missing.
  """
  proxy = None
  try:
    if proxy_yaml_key in proxy_config_data:
      proxy_data = proxy_config_data.get(proxy_yaml_key)
      original_proxy_keys = list(proxy_data.keys())
      proxy = ProxyConfig.Proxy(proxy_data['host'],
                                proxy_data['port'],
                                username=proxy_data.get('username'),
                                password=proxy_data.get('password'))
  except KeyError:
    raise googleads.errors.GoogleAdsValueError(
        'Your yaml file is missing some of the required proxy values. Required '
        'values are: %s, actual values are %s' %
        (_PROXY_KEYS, original_proxy_keys))

  return proxy


def _PackForSuds(obj, factory, datetime_packer=None):
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
    datetime_packer: A product specific function to unwrap date/datetimes.

  Returns:
    If the given obj was a dictionary that contained the 'xsi_type' key, this
    will be an instance of a class generated from the WSDL. Otherwise, this will
    be the same data type as the input obj was.
  """
  if datetime_packer and isinstance(obj, (datetime.datetime, datetime.date)):
    obj = datetime_packer(obj)
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
        setattr(new_obj, key, _PackForSuds(obj[key], factory,
                                           datetime_packer=datetime_packer))
    else:
      new_obj = {}
      for key in obj:
        new_obj[key] = _PackForSuds(obj[key], factory,
                                    datetime_packer=datetime_packer)
    return new_obj
  elif isinstance(obj, (list, tuple)):
    return [_PackForSuds(item, factory,
                         datetime_packer=datetime_packer) for item in obj]
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
  return obj and not isinstance(obj, basestring) and hasattr(obj, '__iter__')


def IncludeUtilitiesInUserAgent(value):
  """Configures the logging of utilities in the User-Agent.

  Args:
    value: a bool indicating that you want to include utility names in the
      User-Agent if set True, otherwise, these will not be added.
  """
  with _UTILITY_LOCK:
    _utility_registry.SetEnabled(value)


def RegisterUtility(utility_name, version_mapping=None):
  """Decorator that registers a class with the given utility name.

  This will only register the utilities being used if the UtilityRegistry is
  enabled. Note that only the utility class's public methods will cause the
  utility name to be added to the registry.

  Args:
    utility_name: A str specifying the utility name associated with the class.
    version_mapping: A dict containing optional version strings to append to the
    utility string for individual methods; where the key is the method name and
    the value is the text to be appended as the version.

  Returns:
    The decorated class.
  """
  def MethodDecorator(utility_method, version):
    """Decorates a method in the utility class."""
    registry_name = ('%s/%s' % (utility_name, version) if version
                     else utility_name)
    @wraps(utility_method)
    def Wrapper(*args, **kwargs):
      with _UTILITY_LOCK:
        _utility_registry.Add(registry_name)
      return utility_method(*args, **kwargs)
    return Wrapper

  def ClassDecorator(cls):
    """Decorates a utility class."""
    for name, method in inspect.getmembers(cls, inspect.ismethod):
      # Public methods of the class will have the decorator applied.
      if not name.startswith('_'):
        # The decorator will only be applied to unbound methods; this prevents
        # it from clobbering class methods. If the attribute doesn't exist, set
        # None for PY3 compatibility.
        if not getattr(method, '__self__', None):
          setattr(cls, name, MethodDecorator(
              method, version_mapping.get(name) if version_mapping else None))
    return cls

  return ClassDecorator


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
      if disable_ssl_certificate_validation:
        ssl._create_default_https_context = ssl._create_unverified_context
        ssl_context = ssl.create_default_context()
      else:
        ssl_context = ssl.create_default_context(cafile=cafile)
    except AttributeError:
      # Earlier versions lack ssl.create_default_context()
      # Rather than raising the exception, no context will be provided for
      # legacy support. Of course, this means no certificate validation is
      # taking place!
      return None

    return ssl_context

  def GetHandlers(self):
    """Retrieve the appropriate urllib2 handlers for the given configuration.

    Returns:
      A list of urllib2.BaseHandler subclasses to be used when making calls
      with proxy.
    """
    handlers = []

    if self._ssl_context:
      handlers.append(urllib2.HTTPSHandler(context=self._ssl_context))

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
      kwargs['timeout'] = 3600
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

  def __init__(self, suds_client, header_handler, datetime_packer=None):
    """Initializes a suds service proxy.

    Args:
      suds_client: The suds.client.Client whose service will be wrapped. Note
        that this is the client itself, not the client's embedded service
        object.
      header_handler: A HeaderHandler responsible for setting the SOAP and HTTP
          headers on the service client.
      datetime_packer: A product specific function to unwrap date/datetimes.
    """
    self.suds_client = suds_client
    self._header_handler = header_handler
    self._method_proxies = {}
    self._datetime_packer = datetime_packer

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

      try:
        return soap_service_method(
            *[_PackForSuds(arg, self.suds_client.factory,
                           self._datetime_packer) for arg in args])
      except suds.WebFault as e:
        if _logger.isEnabledFor(logging.WARNING):
          _logger.warning('Response summary - %s',
                          _ExtractResponseSummaryFields(e.document))

        _logger.info('SOAP response:\n%s', e.document)

        if not hasattr(e.fault, 'detail'):
          raise

        # Before re-throwing the WebFault exception, an error object needs to be
        # wrapped in a list for safe iteration.
        fault = e.fault.detail.ApiExceptionFault
        if not hasattr(fault, 'errors') or fault.errors is None:
          e.fault.detail.ApiExceptionFault.errors = []
          raise

        obj = fault.errors
        if not isinstance(obj, list):
          fault.errors = [obj]

        raise

    return MakeSoapRequest


class HeaderHandler(object):
  """A generic header handler interface that must be subclassed by each API."""

  def SetHeaders(self, client):
    """Sets the SOAP and HTTP headers on the given suds client."""
    raise NotImplementedError('You must subclass HeaderHandler.')


class LoggingMessagePlugin(suds.plugin.MessagePlugin):
  """A MessagePlugin used to log request summaries."""

  def marshalled(self, context):
    if _logger.isEnabledFor(logging.INFO):
      _logger.info('Request summary - %s',
                   _ExtractRequestSummaryFields(context.envelope))

  def parsed(self, context):
    if _logger.isEnabledFor(logging.INFO):
      _logger.info('Response summary - %s',
                   _ExtractResponseSummaryFields(context.reply))


def _ExtractRequestSummaryFields(document):
  """Extract logging fields from the request's suds.sax.element.Element.

  Args:
    document: A suds.sax.element.Element instance containing the API request.

  Returns:
    A dict mapping logging field names to their corresponding value.
  """
  headers = document.childAtPath('Header/RequestHeader')
  body = document.childAtPath('Body')

  summary_fields = {
      'methodName': body.getChildren()[0].name
  }

  # Extract AdWords-specific fields if they exist.
  # Note: We need to check if None because this will always evaluate False.
  client_customer_id = headers.getChild('clientCustomerId')
  if client_customer_id is not None:
    summary_fields['clientCustomerId'] = client_customer_id.text

  # Extract DFP-specific fields if they exist.
  # Note: We need to check if None because this will always evaluate False.
  network_code = headers.getChild('networkCode')
  if network_code is not None:
    summary_fields['networkCode'] = network_code.text

  return summary_fields


def _ExtractResponseSummaryFields(document):
  """Extract logging fields from the response's suds.sax.document.Document.

  Args:
    document: A suds.sax.document.Document instance containing the parsed
      API response for a given API request.

  Returns:
    A dict mapping logging field names to their corresponding value.
  """
  headers = document.childAtPath('Envelope/Header/ResponseHeader')
  body = document.childAtPath('Envelope/Body')
  summary_fields = {}

  if headers is not None:
    summary_fields['requestId'] = headers.getChild('requestId').text
    summary_fields['responseTime'] = headers.getChild('responseTime').text

    # Extract AdWords-specific summary fields if they are present.
    # Note: We need to check if None because this will always evaluate False.
    service_name = headers.getChild('serviceName')
    if service_name is not None:
      summary_fields['serviceName'] = service_name.text

    method_name = headers.getChild('methodName')
    if method_name is not None:
      summary_fields['methodName'] = method_name.text

    operations = headers.getChild('operations')
    if operations is not None:
      summary_fields['operations'] = operations.text

  if body is not None:
    # Extract fault if it exists.
    fault = body.getChild('Fault')
    if fault is not None:
      summary_fields['isFault'] = True
      # Cap length of faultstring to 16k characters for summary.
      summary_fields['faultMessage'] = fault.getChild(
          'faultstring').text[:16000]
    else:
      summary_fields['isFault'] = False

  return summary_fields
