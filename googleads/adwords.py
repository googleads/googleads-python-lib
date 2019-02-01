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

"""Client library for the AdWords API."""

import abc
import codecs
from collections import namedtuple
import datetime
import logging
import os
import re
import sys
import urllib
import urllib2
from xml.etree import ElementTree

import googleads.common
import googleads.errors
import six
import xmltodict
import yaml


_report_logger = logging.getLogger('%s.%s' % (__name__, 'report_downloader'))
_batch_job_logger = logging.getLogger('%s.%s'
                                      % (__name__, 'batch_job_helper'))

# The chunk size used for report downloads.
_CHUNK_SIZE = 16 * 1024
# A giant dictionary of AdWords versions, the services they support, and which
# namespace those services are in.
_SERVICE_MAP = {
    'v201806': {
        'AccountLabelService': 'mcm',
        'AdCustomizerFeedService': 'cm',
        'AdGroupAdService': 'cm',
        'AdGroupBidModifierService': 'cm',
        'AdGroupCriterionService': 'cm',
        'AdGroupExtensionSettingService': 'cm',
        'AdGroupFeedService': 'cm',
        'AdGroupService': 'cm',
        'AdParamService': 'cm',
        'AdService': 'cm',
        'AdwordsUserListService': 'rm',
        'AssetService': 'cm',
        'BatchJobService': 'cm',
        'BiddingStrategyService': 'cm',
        'BudgetOrderService': 'billing',
        'BudgetService': 'cm',
        'CampaignBidModifierService': 'cm',
        'CampaignCriterionService': 'cm',
        'CampaignExtensionSettingService': 'cm',
        'CampaignFeedService': 'cm',
        'CampaignGroupPerformanceTargetService': 'cm',
        'CampaignGroupService': 'cm',
        'CampaignService': 'cm',
        'CampaignSharedSetService': 'cm',
        'ConstantDataService': 'cm',
        'ConversionTrackerService': 'cm',
        'CustomAffinityService': 'rm',
        'CustomerExtensionSettingService': 'cm',
        'CustomerFeedService': 'cm',
        'CustomerNegativeCriterionService': 'cm',
        'CustomerService': 'mcm',
        'CustomerSyncService': 'ch',
        'DataService': 'cm',
        'DraftAsyncErrorService': 'cm',
        'DraftService': 'cm',
        'FeedItemService': 'cm',
        'FeedItemTargetService': 'cm',
        'FeedMappingService': 'cm',
        'FeedService': 'cm',
        'LabelService': 'cm',
        'LocationCriterionService': 'cm',
        'ManagedCustomerService': 'mcm',
        'MediaService': 'cm',
        'OfflineCallConversionFeedService': 'cm',
        'OfflineConversionAdjustmentFeedService': 'cm',
        'OfflineConversionFeedService': 'cm',
        'OfflineDataUploadService': 'rm',
        'ReportDefinitionService': 'cm',
        'SharedCriterionService': 'cm',
        'SharedSetService': 'cm',
        'TargetingIdeaService': 'o',
        'TrafficEstimatorService': 'o',
        'TrialAsyncErrorService': 'cm',
        'TrialService': 'cm'
    },
    'v201809': {
        'AccountLabelService': 'mcm',
        'AdCustomizerFeedService': 'cm',
        'AdGroupAdService': 'cm',
        'AdGroupBidModifierService': 'cm',
        'AdGroupCriterionService': 'cm',
        'AdGroupExtensionSettingService': 'cm',
        'AdGroupFeedService': 'cm',
        'AdGroupService': 'cm',
        'AdParamService': 'cm',
        'AdService': 'cm',
        'AdwordsUserListService': 'rm',
        'AssetService': 'cm',
        'BatchJobService': 'cm',
        'BiddingStrategyService': 'cm',
        'BudgetOrderService': 'billing',
        'BudgetService': 'cm',
        'CampaignBidModifierService': 'cm',
        'CampaignCriterionService': 'cm',
        'CampaignExtensionSettingService': 'cm',
        'CampaignFeedService': 'cm',
        'CampaignGroupPerformanceTargetService': 'cm',
        'CampaignGroupService': 'cm',
        'CampaignService': 'cm',
        'CampaignSharedSetService': 'cm',
        'ConstantDataService': 'cm',
        'ConversionTrackerService': 'cm',
        'CustomAffinityService': 'rm',
        'CustomerExtensionSettingService': 'cm',
        'CustomerFeedService': 'cm',
        'CustomerNegativeCriterionService': 'cm',
        'CustomerService': 'mcm',
        'CustomerSyncService': 'ch',
        'DataService': 'cm',
        'DraftAsyncErrorService': 'cm',
        'DraftService': 'cm',
        'FeedItemService': 'cm',
        'FeedItemTargetService': 'cm',
        'FeedMappingService': 'cm',
        'FeedService': 'cm',
        'LabelService': 'cm',
        'LocationCriterionService': 'cm',
        'ManagedCustomerService': 'mcm',
        'MediaService': 'cm',
        'OfflineCallConversionFeedService': 'cm',
        'OfflineConversionAdjustmentFeedService': 'cm',
        'OfflineConversionFeedService': 'cm',
        'OfflineDataUploadService': 'rm',
        'ReportDefinitionService': 'cm',
        'SharedCriterionService': 'cm',
        'SharedSetService': 'cm',
        'TargetingIdeaService': 'o',
        'TrafficEstimatorService': 'o',
        'TrialAsyncErrorService': 'cm',
        'TrialService': 'cm'
    }
}

# Supported kwargs for params sent in the report header.
_REPORT_HEADER_KWARGS = {'client_customer_id': 'clientCustomerId',
                         'include_zero_impressions': 'includeZeroImpressions',
                         'skip_report_header': 'skipReportHeader',
                         'skip_column_header': 'skipColumnHeader',
                         'skip_report_summary': 'skipReportSummary',
                         'use_raw_enum_values': 'useRawEnumValues'}

# The endpoint used by default when making AdWords API requests.
_DEFAULT_ENDPOINT = 'https://adwords.google.com'
# The user-agent used by default when making AdWords API requests.
_DEFAULT_USER_AGENT = 'unknown'


class AdWordsClient(googleads.common.CommonClient):
  """A central location to set headers and create web service clients.

  Attributes:
    developer_token: A string containing your AdWords API developer token.
    oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize your
        requests.
    user_agent: An arbitrary string which will be used to identify your
        application
    client_customer_id: A string identifying which AdWords customer you want to
        act as.
    validate_only: A boolean indicating if you want your request to be validated
        but not actually executed.
    partial_failure: A boolean indicating if you want your mutate calls
        containing several operations, some of which fail and some of which
        succeed, to result in a complete failure with no changes made or a
        partial failure with some changes made. Only certain services respect
        this header.
  """

  # The key in the storage yaml which contains AdWords data.
  _YAML_KEY = 'adwords'
  # A tuple containing values which must be provided to use AdWords.
  _REQUIRED_INIT_VALUES = ('developer_token',)
  # A tuple containing values which may optionally be provided when using
  # AdWords.
  _OPTIONAL_INIT_VALUES = (
      'validate_only', 'partial_failure', 'client_customer_id', 'user_agent',
  'report_downloader_headers',
  googleads.common.ENABLE_COMPRESSION_KEY)

  # The format of SOAP service WSDLs. A server, namespace, version, and service
  # name need to be formatted in.
  _SOAP_SERVICE_FORMAT = '%s/api/adwords/%s/%s/%s?wsdl'

  @classmethod
  def LoadFromString(cls, yaml_doc):
    """Creates an AdWordsClient with information stored in a yaml string.

    Args:
      yaml_doc: The yaml string containing the cached AdWords data.

    Returns:
      An AdWordsClient initialized with the values cached in the string.

    Raises:
      A GoogleAdsValueError if the given yaml string does not contain the
      information necessary to instantiate a client object - either a
      required key was missing or an OAuth2 key was missing.
    """
    return cls(**googleads.common.LoadFromString(
        yaml_doc, cls._YAML_KEY, cls._REQUIRED_INIT_VALUES,
        cls._OPTIONAL_INIT_VALUES))

  @classmethod
  def LoadFromStorage(cls, path=None):
    """Creates an AdWordsClient with information stored in a yaml file.

    Args:
      [optional]
      path: The path string to the file containing cached AdWords data.

    Returns:
      An AdWordsClient initialized with the values cached in the file.

    Raises:
      A GoogleAdsValueError if the given yaml file does not contain the
      information necessary to instantiate a client object - either a
      required key was missing or an OAuth2 key was missing.
    """
    if path is None:
      path = os.path.join(os.path.expanduser('~'), 'googleads.yaml')

    return cls(**googleads.common.LoadFromStorage(
        path, cls._YAML_KEY, cls._REQUIRED_INIT_VALUES,
        cls._OPTIONAL_INIT_VALUES))

  def __init__(self, developer_token, oauth2_client,
               user_agent=_DEFAULT_USER_AGENT, soap_impl='zeep',
               timeout=3600, **kwargs):
    """Initializes an AdWordsClient.

    For more information on these arguments, see our SOAP headers guide:
    https://developers.google.com/adwords/api/docs/guides/soap

    Args:
      developer_token: A string containing your AdWords API developer token.
      oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize
          your requests.
      user_agent: An arbitrary string containing only ASCII characters that will
          be used to identify your application. If not set, this will default to
          the string value "unknown".
      soap_impl: A string identifying which SOAP implementation to use. The
          options are 'zeep' or 'suds'.
      timeout: An integer time in MS to time out connections to AdWords.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string identifying which AdWords customer you want
          to act as. You do not have to provide this if you are using a client
          account. You probably want to provide this if you're using an AdWords
          manager account.
      validate_only: A boolean indicating if you want your request to be
          validated but not actually executed.
      partial_failure: A boolean indicating if you want your mutate calls
          containing several operations, some of which fail and some of which
          succeed, to result in a complete failure with no changes made or a
          partial failure with some changes made. Only certain services respect
          this header.
      cache: A subclass of zeep.cache.Base or suds.cache.Cache. If not set,
          this will default to a basic file cache. To disable caching for Zeep,
          pass googleads.common.ZeepServiceProxy.NO_CACHE.
      proxy_config: A googleads.common.ProxyConfig instance or None if a proxy
        isn't being used.
      report_downloader_headers: A dict containing optional headers to be used
        by default when making requests with the ReportDownloader.
      enable_compression: A boolean indicating if you want to enable compression
        of the SOAP response. If True, the SOAP response will use gzip
        compression, and will be decompressed for you automatically.

    Raises:
      GoogleAdsValueError: If the provided user_agent contains non-ASCII
        characters.
    """
    super(AdWordsClient, self).__init__()

    self.developer_token = developer_token
    self.oauth2_client = oauth2_client
    self.client_customer_id = kwargs.get('client_customer_id')
    self.user_agent = user_agent
    self.soap_impl = soap_impl
    self.custom_http_headers = kwargs.get('custom_http_headers')
    # Verify that the provided user_agent contains only ASCII characters. In
    # both Python 2 and Python 3, a UnicodeEncodeError will be raised if it
    # contains a non-ASCII character.
    try:
      self.user_agent.encode('ascii')
    except UnicodeEncodeError:
      raise googleads.errors.GoogleAdsValueError(
          'Invalid user_agent value, must contain only ASCII characters.')
    self.validate_only = kwargs.get('validate_only', False)
    self.partial_failure = kwargs.get('partial_failure', False)
    self.cache = kwargs.get('cache')
    proxy_config = kwargs.get('proxy_config')
    self.proxy_config = (proxy_config if proxy_config else
                         googleads.common.ProxyConfig())
    self.report_download_headers = kwargs.get('report_download_headers', {})
    self.enable_compression = kwargs.get(
        googleads.common.ENABLE_COMPRESSION_KEY, False)

    if self.enable_compression:
      self.user_agent = '%s (gzip)' % self.user_agent

    self.message_plugin = googleads.common.LoggingMessagePlugin()
    self.timeout = timeout

  def GetService(self, service_name, version=None, server=None):
    """Creates a service client for the given service.

    Args:
      service_name: A string identifying which AdWords service to create a
          service client for.
      [optional]
      version: A string identifying the AdWords version to connect to. This
          defaults to what is currently the latest version. This will be updated
          in future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the AdWords API.

    Returns:
      A googleads.common.GoogleSoapService instance which has the headers
      and proxy configured for use.

    Raises:
      A GoogleAdsValueError if the service or version provided do not exist.
    """
    if not server:
      server = _DEFAULT_ENDPOINT
    server = server.rstrip('/')

    if not version:
      version = sorted(_SERVICE_MAP.keys())[-1]

    try:
      version_service_mapping = _SERVICE_MAP[version][service_name]
    except KeyError:
      msg_fmt = 'Unrecognized %s for the AdWords API. Given: %s Supported: %s'

      if version in _SERVICE_MAP:
        raise googleads.errors.GoogleAdsValueError(
            msg_fmt % ('service', service_name, _SERVICE_MAP[version].keys()))
      else:
        raise googleads.errors.GoogleAdsValueError(
            msg_fmt % ('version', version, _SERVICE_MAP.keys()))

    service = googleads.common.GetServiceClassForLibrary(self.soap_impl)(
        self._SOAP_SERVICE_FORMAT % (
            server, version_service_mapping, version, service_name),
        _AdWordsHeaderHandler(
            self, version, self.enable_compression, self.custom_http_headers),
        _AdWordsPacker,
        self.proxy_config,
        self.timeout,
        version,
        cache=self.cache)

    return service

  def GetBatchJobHelper(self, version=sorted(_SERVICE_MAP.keys())[-1],
                        server=None):
    """Returns a BatchJobHelper to work with the BatchJobService.

      This is a convenience method. It is functionally identical to calling
      BatchJobHelper(adwords_client, version).

    Args:
      [optional]
      version: A string identifying the AdWords version to connect to. This
          defaults to what is currently the latest version. This will be updated
          in future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the AdWords API.

    Returns:
      An initialized BatchJobHelper tied to this client.
    """
    if not server:
      server = _DEFAULT_ENDPOINT

    request_builder = BatchJobHelper.GetRequestBuilder(
        self, version=version, server=server)
    response_parser = BatchJobHelper.GetResponseParser()

    return BatchJobHelper(request_builder, response_parser)

  def GetReportDownloader(self, version=sorted(_SERVICE_MAP.keys())[-1],
                          server=None):
    """Creates a downloader for AdWords reports.

    This is a convenience method. It is functionally identical to calling
    ReportDownloader(adwords_client, version, server).

    Args:
      [optional]
      version: A string identifying the AdWords version to connect to. This
          defaults to what is currently the latest version. This will be updated
          in future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the AdWords API.

    Returns:
      A ReportDownloader tied to this AdWordsClient, ready to download reports.
    """
    if not server:
      server = _DEFAULT_ENDPOINT

    return ReportDownloader(self, version, server)

  def SetClientCustomerId(self, client_customer_id):
    """Change the client customer id used by the AdWordsClient instance.

    Args:
      client_customer_id: str New Client Customer ID to use.
    """
    self.client_customer_id = client_customer_id


class _AdWordsHeaderHandler(googleads.common.HeaderHandler):
  """Handler which generates the headers for AdWords requests."""

  # The library signature for AdWords, to be appended to all user agents.
  _PRODUCT_SIG = 'AwApi-Python'
  # The name of the WSDL-defined SOAP Header class used in all SOAP requests.
  # The namespace needs the version of AdWords being used to be templated in.
  _SOAP_HEADER_CLASS = (
      '{https://adwords.google.com/api/adwords/cm/%s}SoapHeader')
  # The content type of report download requests
  _CONTENT_TYPE = 'application/x-www-form-urlencoded'

  def __init__(self, adwords_client, version,
               enable_compression, custom_http_headers=None):
    """Initializes an AdWordsHeaderHandler.

    Args:
      adwords_client: An AdWordsClient whose data will be used to fill in the
          headers. We retain a reference to this object so that the header
          handler picks up changes to the client.
      version: A string identifying which version of AdWords this header handler
          will be used for.
      enable_compression: A boolean indicating if you want to enable compression
        of the SOAP response. If True, the SOAP response will use gzip
        compression, and will be decompressed for you automatically.
      custom_http_headers: A dictionary of custom HTTP headers to send with all
        requests.
    """
    self._adwords_client = adwords_client
    self._version = version
    self.enable_compression = enable_compression
    self.custom_http_headers = custom_http_headers or {}

  def GetSOAPHeaders(self, create_method):
    """Returns the SOAP headers required for request authorization.

    Args:
      create_method: The SOAP library specific method used to instantiate SOAP
      objects.

    Returns:
      A SOAP object containing the headers.
    """
    header = create_method(self._SOAP_HEADER_CLASS % self._version)
    header.clientCustomerId = self._adwords_client.client_customer_id
    header.developerToken = self._adwords_client.developer_token
    header.userAgent = ''.join([
        self._adwords_client.user_agent,
        googleads.common.GenerateLibSig(self._PRODUCT_SIG)])
    header.validateOnly = self._adwords_client.validate_only
    header.partialFailure = self._adwords_client.partial_failure
    return header

  def GetHTTPHeaders(self):
    """Returns the HTTP headers required for request authorization.

    Returns:
      A dictionary containing the required headers.
    """
    http_headers = self._adwords_client.oauth2_client.CreateHttpHeader()
    if self.enable_compression:
      http_headers['accept-encoding'] = 'gzip'

    http_headers.update(self.custom_http_headers)

    return http_headers

  def GetReportDownloadHeaders(self, **kwargs):
    """Returns a dictionary of headers for a report download request.

    Note that the given keyword arguments will override any settings configured
    from the googleads.yaml file.

    Args:
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set by the AdWordsClient.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Returns:
      A dictionary containing the headers configured for downloading a report.

    Raises:
      GoogleAdsValueError: If one or more of the report header keyword arguments
        is invalid.
    """
    headers = self._adwords_client.oauth2_client.CreateHttpHeader()
    headers.update({
        'Content-type': self._CONTENT_TYPE,
        'developerToken': str(self._adwords_client.developer_token),
        'clientCustomerId': str(kwargs.get(
            'client_customer_id', self._adwords_client.client_customer_id)),
        'User-Agent': ''.join([
            self._adwords_client.user_agent,
            googleads.common.GenerateLibSig(self._PRODUCT_SIG),
            ',gzip'])
    })
    headers.update(self.custom_http_headers)

    updated_kwargs = dict(self._adwords_client.report_download_headers)
    updated_kwargs.update(kwargs)

    for kw in updated_kwargs:
      try:
        headers[_REPORT_HEADER_KWARGS[kw]] = str(updated_kwargs[kw])
      except KeyError:
        raise googleads.errors.GoogleAdsValueError(
            'The provided keyword "%s" is invalid. Accepted keywords are: %s'
            % (kw, _REPORT_HEADER_KWARGS.keys()))

    return headers


class _AdWordsPacker(googleads.common.SoapPacker):
  """A utility applying customized packing logic for AdWords."""

  @classmethod
  def Pack(cls, obj, version):
    """Pack the given object using AdWords-specific logic.

    Args:
      obj: an object to be packed for SOAP using AdWords-specific logic, if
          applicable.
      version: the version of the current API, e.g. 'v201809'

    Returns:
      The given object packed with AdWords-specific logic for SOAP, if
      applicable. Otherwise, returns the given object unmodified.
    """
    if isinstance(obj, ServiceQuery):
      return str(obj)
    return obj


@googleads.common.RegisterUtility('BatchJobHelper')
class BatchJobHelper(object):
  """A utility that simplifies working with the BatchJobService."""

  class AbstractResponseParser(object):
    """Interface for parsing responses from the BatchJobService."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def ParseResponse(self, batch_job_response):
      """Parses a Batch Job Service response..

      Args:
        batch_job_response: a str containing the response from the
        BatchJobService.
      """

  class _XMLToDictResponseParser(AbstractResponseParser):
    """Parses responses from the BatchJobService, returning as a dictionary."""

    def ParseResponse(self, batch_job_response):
      """Parses a Batch Job Service response.

      Args:
        batch_job_response: a str containing the response from the
        BatchJobService.

      Returns:
        An OrderedDict containing the Batch Job Service response.
      """
      return xmltodict.parse(batch_job_response)

  class AbstractUploadRequestBuilder(object):
    """Interface for building requests used to upload batch job operations."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def BuildUploadRequest(self, upload_url, operations, **kwargs):
      """Builds the BatchJob upload request.

      Args:
        upload_url: a string url that the given operations will be uploaded to.
        operations: a list where each element is a list containing operations
          for a single AdWords Service.
        **kwargs: optional keyword arguments.

      Returns:
        A urllib2.Request instance with the correct method, headers, and
        padding (if required) for the batch job upload.
      """

    @abc.abstractmethod
    def GetVersion(self):
      """Retrieves the version of AdWords used to build requests.

      Returns:
        A str indicating the version of AdWords for which requests are being
          built.
      """

    @abc.abstractmethod
    def GetServer(self):
      """Retrieves the endpoint used to access the AdWords API.

      Returns:
        A str indicating the version of AdWords endpoint being used.
      """

  class _UploadRequestBuilder(AbstractUploadRequestBuilder):
    """Builds requests used to upload operations for Batch Jobs."""
    # Used to remove namespace from xsi:type Element attributes.
    _ATTRIB_NAMESPACE_SUB = re.compile('ns[0-1]:')
    # Components of the upload request.
    _UPLOAD_PREFIX_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<mutate xmlns="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">"""
    _UPLOAD_SUFFIX = '</mutate>'
    # Incremental uploads must have a content-length that is a multiple of this.
    _BATCH_JOB_INCREMENT = 262144
    _OPERATION = namedtuple('Operation',
                            ['operation_type', 'service', 'method'])
    _OPERATION_MAP = {
        'AdGroupAdOperation': _OPERATION('AdGroupAdOperation',
                                         'AdGroupAdService', 'mutate'),
        'AdGroupAdLabelOperation': _OPERATION(
            'AdGroupAdLabelOperation', 'AdGroupAdService', 'mutateLabel'),
        'AdGroupBidModifierOperation': _OPERATION(
            'AdGroupBidModifierOperation', 'AdGroupBidModifierService',
            'mutate'),
        'AdGroupCriterionOperation': _OPERATION(
            'AdGroupCriterionOperation', 'AdGroupCriterionService', 'mutate'),
        'AdGroupCriterionLabelOperation': _OPERATION(
            'AdGroupCriterionLabelOperation', 'AdGroupCriterionService',
            'mutateLabel'),
        'AdGroupExtensionSettingOperation': _OPERATION(
            'AdGroupExtensionSettingOperation',
            'AdGroupExtensionSettingService', 'mutate'),
        'AdGroupOperation': _OPERATION('AdGroupOperation', 'AdGroupService',
                                       'mutate'),
        'AdGroupLabelOperation': _OPERATION('AdGroupLabelOperation',
                                            'AdGroupService', 'mutateLabel'),
        'BudgetOperation': _OPERATION('BudgetOperation', 'BudgetService',
                                      'mutate'),
        'CampaignCriterionOperation': _OPERATION(
            'CampaignCriterionOperation', 'CampaignCriterionService', 'mutate'),
        'CampaignExtensionSettingOperation': _OPERATION(
            'CampaignExtensionSettingOperation',
            'CampaignExtensionSettingService', 'mutate'),
        'CampaignOperation': _OPERATION('CampaignOperation',
                                        'CampaignService', 'mutate'),
        'CampaignLabelOperation': _OPERATION('CampaignLabelOperation',
                                             'CampaignService', 'mutateLabel'),
        'CampaignSharedSetOperation': _OPERATION(
            'CampaignSharedSetOperation', 'CampaignSharedSetService',
            'mutate'),
        'CustomerExtensionSettingOperation': _OPERATION(
            'CustomerExtensionSettingOperation',
            'CustomerExtensionSettingService', 'mutate'),
        'FeedItemOperation': _OPERATION('FeedItemOperation', 'FeedItemService',
                                        'mutate'),
        'FeedItemTargetOperation': _OPERATION(
            'FeedItemTargetOperation', 'FeedItemTargetService', 'mutate'),
        'SharedCriterionOperation': _OPERATION(
            'SharedCriterionOperation', 'SharedCriterionService', 'mutate'),
        'SharedSetOperation': _OPERATION('SharedSetOperation',
                                         'SharedSetService', 'mutate')
    }
    XSI_TYPE_STRING = '{http://www.w3.org/2001/XMLSchema-instance}type'

    def __init__(self, client, **kwargs):
      """Initializes an _UploadRequestBuilder.

      Arguments:
        client: an AdWordsClient instance.
        **kwargs: Keyword arguments.

      Keyword Arguments:
        version: a string identifying the AdWords version to connect to.
        server: a string identifying the webserver hosting the AdWords API.
      """
      self.client = client
      self._version = kwargs.get('version', sorted(_SERVICE_MAP.keys())[-1])
      self.server = kwargs.get('server', _DEFAULT_ENDPOINT)
      self._adwords_endpoint = ('%s/api/adwords/cm/%s' %
                                (self.server, self._version))
      self._adwords_namespace = ('{%s}' % self._adwords_endpoint)
      # Used to remove the AdWords namespace from Element tags.
      self._tag_namespace_sub = re.compile(self._adwords_namespace)

    def BuildUploadRequest(self, upload_url, operations, **kwargs):
      """Builds the BatchJob upload request.

      Args:
        upload_url: a string url that the given operations will be uploaded to.
        operations: a list where each element is a list containing operations
          for a single AdWords Service.
        **kwargs: optional keyword arguments.

      Keyword Arguments:
        current_content_length: an integer indicating the current total content
          length of an incremental upload request. If this keyword argument is
          provided, this request will be handled as an incremental upload.
        is_last: a boolean indicating whether this is the final request in an
          incremental upload.

      Returns:
        A urllib2.Request instance with the correct method, headers, and
        padding (if required) for the batch job upload.
      """
      current_content_length = kwargs.get('current_content_length', 0)
      is_last = kwargs.get('is_last')
      # Generate an unpadded request body
      request_body = self._BuildUploadRequestBody(
          operations,
          has_prefix=current_content_length == 0,
          has_suffix=is_last)
      req = urllib2.Request(upload_url)
      req.add_header('Content-Type', 'application/xml')
      # Determine length of this message and the required padding.
      new_content_length = current_content_length
      request_length = len(request_body.encode('utf-8'))
      padding_length = self._GetPaddingLength(request_length)
      padded_request_length = request_length + padding_length
      new_content_length += padded_request_length
      request_body += ' ' * padding_length
      req.get_method = lambda: 'PUT'  # Modify this into a PUT request.
      req.data = request_body.encode('utf-8')
      req.add_header('Content-Length', padded_request_length)
      req.add_header('Content-Range', 'bytes %s-%s/%s' % (
          current_content_length,
          new_content_length - 1,
          new_content_length if is_last else '*'
      ))

      return req

    def GetVersion(self):
      """Retrieves the version of AdWords used to build requests.

      Returns:
        A str indicating the version of AdWords for which requests are being
          built.
      """
      return self._version

    def GetServer(self):
      """Retrieves the endpoint used to access the AdWords API.

      Returns:
        A str indicating the version of AdWords endpoint being used.
      """
      return self.server

    def _BuildUploadRequestBody(self, operations, has_prefix=True,
                                has_suffix=True):
      """Builds an unpadded body containing operations for a BatchJob upload.

      Args:
        operations: a list where each element is a list containing operations
          for a single AdWords Service.
        has_prefix: a boolean indicating whether the prefix should be included
          in the request body.
        has_suffix: a boolean indicating whether the suffic should be included
          in the request body.

      Returns:
        A string containing the unpadded batch job upload request body.
      """
      operations_xml = ''.join([
          self._GenerateOperationsXML(operations_list)
          for operations_list in operations])
      request_body = '%s%s%s' % ((self._UPLOAD_PREFIX_TEMPLATE %
                                  self._adwords_endpoint) if has_prefix else '',
                                 operations_xml,
                                 self._UPLOAD_SUFFIX if has_suffix else '')
      return request_body

    def _ExtractOperations(self, full_soap_xml):
      """Extracts operations from API Request XML for use with BatchJobService.

      Args:
        full_soap_xml: The full XML for the desired operation.

      Returns:
        A string containing only the operations portion of the full XML request,
        formatted for use with the BatchJobService. If no operations are found,
        returns an empty string.

      Raises:
        GoogleAdsValueErrorr: If no Operation.Type element is found in the
        operations. This ordinarily happens if no xsi_type is specified for the
        operations.
      """
      # Extract method element (e.g. mutate, mutateLabel, etc...) from XML, this
      # contains the operations.
      method = self._GetRawOperationsFromXML(full_soap_xml)
      # Ensure operations are formatted correctly for BatchJobService.
      for operations in method:
        self._FormatForBatchJobService(operations)
        # Extract the operation type, ensure xsi:type is set for
        # BatchJobService. Even if xsi_type is set earlier, suds will end up
        # removing it when it sets Operation.Type.
        operation_type = operations.find('Operation.Type')
        if operation_type is None:
          raise googleads.errors.GoogleAdsValueError('No xsi_type specified '
                                                     'for the operations.')
        operations.attrib[self.XSI_TYPE_STRING] = operation_type.text
      operations_xml = ''.join([ElementTree.tostring(operation).decode('utf-8')
                                for operation in method])
      # Force removal of this line, which suds produces.
      operations_xml = operations_xml.replace(
          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', '')
      return operations_xml

    def _FormatForBatchJobService(self, element):
      """Formats contents of all operations for use with the BatchJobService.

      This will recursively remove unnecessary namespaces generated by suds that
      would prevent the operations from executing via the BatchJobService. It
      will also remove namespaces appended to the xsi:type in some cases that
      also cause issues for the BatchJobService.

      Args:
        element: a starting Element to be modified to the correct format.
      """
      # Remove any unnecessary AdWords namespace from the tag.
      element.tag = self._tag_namespace_sub.sub('', element.tag)
      xsi_type = element.attrib.get(
          '{http://www.w3.org/2001/XMLSchema-instance}type')
      # If an xsi_type attribute exists, ensure that the namespace is removed
      # from the type.
      if xsi_type:
        element.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = (
            self._ATTRIB_NAMESPACE_SUB.sub('', xsi_type))
      for child in element:
        self._FormatForBatchJobService(child)

    def _GenerateOperationsXML(self, operations):
      """Generates XML for the given list of operations.

      Args:
        operations: a list of operations for single AdWords Service.

      Returns:
        A str containing the XML for only the operations, formatted to work with
        the BatchJobService.

      Raises:
        GoogleAdsValueError: if no xsi_type is specified for the operations.
      """
      # Verify that all operations included specify an xsi_type.
      if operations:
        if any('xsi_type' not in operation for operation in operations):
          raise googleads.errors.AdWordsBatchJobServiceInvalidOperationError(
              'Operations have no xsi_type specified.')
        return self._ExtractOperations(self._GenerateRawRequestXML(operations))
      else:
        return ''

    def _GenerateRawRequestXML(self, operations):
      """Generates the raw XML for the operations sent to the given service.

      Args:
        operations: a list containing operations that could be run by the given
          service.

      Returns:
        An element containing the raw XML of the request to the given service
        that would execute the given operations

      Raises:
        KeyError: If the given operation type is not supported.
      """
      operation = self._OPERATION_MAP[operations[0]['xsi_type']]
      service = self.client.GetService(operation.service, self._version)
      return service.GetRequestXML(operation.method, operations)

    def _GetPaddingLength(self, length):
      """Retrieve the padding to be used in an incremental upload.

      Args:
        length: an integer containing the length of the operations XML to be
          uploaded as part of a batch job.
      Returns:
        An integer indicating the required padding to be applied in an
        incremental batch job upload request.
      """
      padding = self._BATCH_JOB_INCREMENT - (length % self._BATCH_JOB_INCREMENT)
      return 0 if padding == self._BATCH_JOB_INCREMENT else padding

    def _GetRawOperationsFromXML(self, raw_request_xml):
      """Retrieve the raw set of operations from the request XML.

      Args:
        raw_request_xml: The full XML for the desired operation.

      Returns:
        An unmodified Element containing the operations from the raw request
        xml.

      Raises:
        AttributeError: if the provided XML isn't from AdWords.
      """
      return raw_request_xml.find(
          '{http://schemas.xmlsoap.org/soap/envelope/}Body').find('.//')

  def __init__(self, request_builder, response_parser):
    """Initializes the BatchJobHelper.

    For general use, consider using AdWordsClient's GetBatchJobHelper method to
    receive an initialized BatchJobHelper using the default request builder and
    response parser.

    Args:
      request_builder: an AbstractUploadRequestBuilder instance.
      response_parser: an AbstractResponseParser instance.
    """
    self._temporary_id = 0  # Used for temporary IDs in BatchJobService.
    self._request_builder = request_builder
    self._response_parser = response_parser

  def GetId(self):
    """Produces a distinct sequential ID for the BatchJobService.

    Returns:
      A negative number that will be the temporary ID for an API resource.
    """
    self._temporary_id -= 1
    return self._temporary_id

  def GetIncrementalUploadHelper(self, upload_url, current_content_length=0):
    return IncrementalUploadHelper(
        self._request_builder, upload_url, current_content_length)

  @classmethod
  def GetRequestBuilder(cls, *args, **kwargs):
    """Get a new AbstractUploadRequestBuilder instance."""
    return cls._UploadRequestBuilder(*args, **kwargs)

  @classmethod
  def GetResponseParser(cls, *args, **kwargs):
    """Get a new AbstractResponseParser instance."""
    return cls._XMLToDictResponseParser(*args, **kwargs)

  def ParseResponse(self, batch_job_response):
    """Parses a Batch Job Service response and returns it as a suds object.

    Note: Unlike suds objects generated via an API call with suds, type
    information will be lost. All values are strings.

    Args:
      batch_job_response: a str containing the response from the
      BatchJobService.

    Returns:
      A suds object response generated from the provided batch_job_response.
    """
    return self._response_parser.ParseResponse(batch_job_response)

  def UploadOperations(self, upload_url, *operations):
    """Uploads all operations to the given uploadUrl in a single request.

    Note: Each list of operations is expected to contain operations of the same
    type, similar to how one would normally send operations in an AdWords API
    Service request.

    Args:
      upload_url: a string url that the given operations will be uploaded to.
      *operations: one or more lists of operations as would be sent to the
        AdWords API for the associated service.
    """
    uploader = IncrementalUploadHelper(self._request_builder, upload_url)
    uploader.UploadOperations(operations, is_last=True)


class IncrementalUploadHelper(object):
  """A utility for uploading operations for a BatchJob incrementally."""

  @classmethod
  def Load(cls, file_input, client=None):
    """Loads an IncrementalUploadHelper from the given file-like object.

    Args:
      file_input: a file-like object containing a serialized
        IncrementalUploadHelper.
      client: an AdWordsClient instance. If not specified, an AdWordsClient will
        be instantiated using the default configuration file.

    Returns:
      An IncrementalUploadHelper instance initialized using the contents of the
      serialized input file.

    Raises:
      GoogleAdsError: If there is an error reading the input file containing the
        serialized IncrementalUploadHelper.
      GoogleAdsValueError: If the contents of the input file can't be parsed to
        produce an IncrementalUploadHelper.
    """
    if client is None:
      client = AdWordsClient.LoadFromStorage()

    try:
      data = yaml.safe_load(file_input)
    except yaml.YAMLError as e:
      raise googleads.errors.GoogleAdsError(
          'Error loading IncrementalUploadHelper from file: %s' % str(e))

    try:
      request_builder = BatchJobHelper.GetRequestBuilder(
          client, version=data['version'], server=data['server']
      )

      return cls(request_builder, data['upload_url'],
                 current_content_length=data['current_content_length'],
                 is_last=data['is_last'])
    except KeyError as e:
      raise googleads.errors.GoogleAdsValueError(
          'Can\'t parse IncrementalUploadHelper from file. Required field '
          '"%s" is missing.' % e.message)

  def __init__(self, request_builder, upload_url, current_content_length=0,
               is_last=False):
    """Initializes the IncrementalUpload.

    Args:
      request_builder: an AbstractUploadRequestBuilder instance.
      upload_url: a string url provided by the BatchJobService.
      current_content_length: an integer identifying the current content length
        of data uploaded to the Batch Job.
      is_last: a boolean indicating whether this is the final increment.
    Raises:
      GoogleAdsValueError: if the content length is lower than 0.
    """
    self._request_builder = request_builder
    if current_content_length < 0:
      raise googleads.errors.GoogleAdsValueError(
          'Current content length %s is < 0.' % current_content_length)
    self._current_content_length = current_content_length
    self._is_last = is_last
    self._url_opener = urllib2.build_opener(
        *self._request_builder.client.proxy_config.GetHandlers())
    if self._request_builder.client.custom_http_headers:
      self._url_opener.addheaders.extend(
          self._request_builder.client.custom_http_headers.items())

    self._upload_url = self._InitializeURL(upload_url, current_content_length)

  def _InitializeURL(self, upload_url, current_content_length):
    """Ensures that the URL used to upload operations is properly initialized.

    Args:
      upload_url: a string url.
      current_content_length: an integer identifying the current content length
        of data uploaded to the Batch Job.

    Returns:
      An initialized string URL, or the provided string URL if the URL has
      already been initialized.
    """
    # If initialization is not necessary, return the provided upload_url.
    if current_content_length != 0:
      return upload_url

    headers = {
        'Content-Type': 'application/xml',
        'Content-Length': 0,
        'x-goog-resumable': 'start'
    }

    # Send an HTTP POST request to the given upload_url
    req = urllib2.Request(upload_url, data={}, headers=headers)
    resp = self._url_opener.open(req)

    return resp.headers['location']

  def Dump(self, output):
    """Serialize the IncrementalUploadHelper and store in file-like object.

    Args:
      output: a file-like object where the status of the IncrementalUploadHelper
        will be written.

    Raises:
      GoogleAdsError: If a YAMLError occurs while writing to the file.
    """
    data = {
        'current_content_length': self._current_content_length,
        'is_last': self._is_last,
        'server': self._request_builder.GetServer(),
        'upload_url': self._upload_url,
        'version': self._request_builder.GetVersion()
    }

    try:
      yaml.dump(data, output)
    except yaml.YAMLError as e:
      raise googleads.errors.GoogleAdsError(
          'Error dumping IncrementalUploadHelper to file: %s' % str(e))

  def UploadOperations(self, operations, is_last=False):
    """Uploads operations to the given uploadUrl in incremental steps.

    Note: Each list of operations is expected to contain operations of the
    same type, similar to how one would normally send operations in an
    AdWords API Service request.

    Args:
      operations: one or more lists of operations as would be sent to the
        AdWords API for the associated service.
      is_last: a boolean indicating whether this is the final increment to be
        added to the batch job.
    """
    if self._is_last:
      raise googleads.errors.AdWordsBatchJobServiceInvalidOperationError(
          'Can\'t add new operations to a completed incremental upload.')
    # Build the request
    req = self._request_builder.BuildUploadRequest(
        self._upload_url, operations,
        current_content_length=self._current_content_length, is_last=is_last)
    # Make the request, ignoring the urllib2.HTTPError raised due to HTTP status
    # code 308 (for resumable uploads).
    try:
      _batch_job_logger.debug('Outgoing request: %s %s %s',
                              req.get_full_url(), req.headers, req.data)

      self._url_opener.open(req)

      if _batch_job_logger.isEnabledFor(logging.INFO):
        _batch_job_logger.info('Request summary: %s',
                               self._ExtractRequestSummaryFields(req))
    except urllib2.HTTPError as e:
      if e.code != 308:
        if _batch_job_logger.isEnabledFor(logging.WARNING):
          _batch_job_logger.warning(
              'Request summary: %s',
              self._ExtractRequestSummaryFields(req, error=e))
        raise
    # Update upload status.
    self._current_content_length += len(req.data)
    self._is_last = is_last

  def _ExtractRequestSummaryFields(self, request, error=None):
    """Extract fields used in the summary logs.

    Args:
      request:  a urllib2.Request instance configured to make the request.
      [optional]
      error: a urllib2.HttpError instance used to retrieve error details.

    Returns:
      A dict containing the fields to be output in the summary logs.
    """
    headers = request.headers
    summary_fields = {
        'server': request.get_full_url(),
        'contentRange': headers['Content-range'],
        'contentLength': headers['Content-length']
    }

    if error:
      summary_fields['isError'] = True
      summary_fields['errorMessage'] = error.reason
    else:
      summary_fields['isError'] = False

    return summary_fields


@googleads.common.RegisterUtility(
    'ReportDownloader', {'DownloadReport': 'File',
                         'DownloadReportWithAwql': 'File',
                         'DownloadReportAsStream': 'Stream',
                         'DownloadReportAsStreamWithAwql': 'Stream',
                         'DownloadReportAsString': 'String',
                         'DownloadReportAsStringWithAwql': 'String'})
class ReportDownloader(object):
  """A utility that can be used to download reports from AdWords."""

  # The namespace format for report download requests. A version needs to be
  # formatted into it.
  _NAMESPACE_FORMAT = 'https://adwords.google.com/api/adwords/cm/%s'
  # The endpoint format for report download requests. A server and version need
  # to be formatted into it.
  _END_POINT_FORMAT = '%s/api/adwords/reportdownload/%s'
  # The schema location format for report download requests. A server and
  # version need to be formatted into it.
  _SCHEMA_FORMAT = '/'.join([_END_POINT_FORMAT, 'reportDefinition.xsd'])
  # The name of the complex type representing a report definition.
  _REPORT_DEFINITION_NAME = 'reportDefinition'
  # Used to extract the reporting URL for logging.
  _SERVER_PATTERN = re.compile('https?://(.+?)/.*')

  def __init__(self, adwords_client, version=sorted(_SERVICE_MAP.keys())[-1],
               server=None):
    """Initializes a ReportDownloader.

    Args:
      adwords_client: The AdwordsClient whose attributes will be used to
          authorize your report download requests.
      [optional]
      version: A string identifying the AdWords version to connect to. This
          defaults to what is currently the latest version. This will be updated
          in future releases to point to what is then the latest version.
      server: A string identifying the webserver hosting the AdWords API.
    """
    if not server:
      server = _DEFAULT_ENDPOINT

    server = server.rstrip('/')
    self._adwords_client = adwords_client
    self._namespace = self._NAMESPACE_FORMAT % version
    self._end_point = self._END_POINT_FORMAT % (server, version)
    self._header_handler = _AdWordsHeaderHandler(
        adwords_client, version, self._adwords_client.enable_compression,
        self._adwords_client.custom_http_headers)
    self.proxy_config = self._adwords_client.proxy_config
    handlers = self.proxy_config.GetHandlers()
    self.url_opener = urllib2.build_opener(*handlers)
    if self._adwords_client.custom_http_headers:
      self.url_opener.addheaders.extend(
          adwords_client.custom_http_headers.items())

    schema_url = self._SCHEMA_FORMAT % (server, version)
    service_class = (googleads.common
                     .GetSchemaHelperForLibrary(adwords_client.soap_impl))
    self.schema_helper = service_class(
        schema_url, self._adwords_client.timeout,
        self.proxy_config, self._namespace, self._adwords_client.cache)

  def _DownloadReportCheckFormat(self, file_format, output):
    """Verifies file format compatibility with given output."""
    encoding = getattr(output, 'encoding', None)

    # In Python 2 binary file encoding will be set to None, and StringIO /
    # BytesIO instances will not have an encoding attribute. In Python 3,
    # binary files don't have an encoding attribute, StringIO instances have an
    # encoding set to None, and BytesIO instances lack an encoding attribute.
    # As a result, if encoding is ever set, it indicates that the specified
    # output is incompatible with GZIPPED formats.
    if encoding and file_format.startswith('GZIPPED_'):
      raise googleads.errors.GoogleAdsValueError(
          'Need to specify a binary output for GZIPPED formats.')

    # Because Python 3 StringIO instances always have encoding set to None,
    # it's necessary to verify that StringIO instances aren't used with GZIPPED
    # formats. In Python 2, this wouldn't matter because StringIO instances
    # store bytes (appropriate for GZIPPED formats) rather than unicode data.
    if six.PY3:
      if (file_format.startswith('GZIPPED_')
          and isinstance(output, six.StringIO)):
        raise googleads.errors.GoogleAdsValueError(
            'Need to specify a binary output for GZIPPED formats.')

  def DownloadReport(self, report_definition, output=sys.stdout, **kwargs):
    """Downloads an AdWords report using a report definition.

    The report contents will be written to the given output.

    Args:
      report_definition: A dictionary or instance of the ReportDefinition class
          generated from the schema. This defines the contents of the report
          that will be downloaded.
      [optional]
      output: A writable object where the contents of the report will be written
          to. If the report is gzip compressed, you need to specify an output
          that can write binary data.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set for the client.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Raises:
      AdWordsReportBadRequestError: if the report download fails due to
          improper input.
      GoogleAdsValueError: if the user-specified report format is incompatible
          with the output.
      AdWordsReportError: if the request fails for any other reason; e.g. a
          network error.
    """
    self._DownloadReportCheckFormat(report_definition['downloadFormat'], output)
    self._DownloadReport(self._SerializeReportDefinition(report_definition),
                         output, **kwargs)

  def DownloadReportAsStream(self, report_definition, **kwargs):
    """Downloads an AdWords report using a report definition.

    This will return a stream, allowing you to retrieve the report contents.

    Args:
      report_definition: A dictionary or instance of the ReportDefinition class
          generated from the schema. This defines the contents of the report
          that will be downloaded.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set for the client.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Returns:
      A stream to be used in retrieving the report contents.

    Raises:
      AdWordsReportBadRequestError: if the report download fails due to
          improper input.
      GoogleAdsValueError: if the user-specified report format is incompatible
          with the output.
      AdWordsReportError: if the request fails for any other reason; e.g. a
          network error.
    """
    return self._DownloadReportAsStream(
        self._SerializeReportDefinition(report_definition), **kwargs)

  def DownloadReportAsStreamWithAwql(self, query, file_format, **kwargs):
    """Downloads an AdWords report using an AWQL query.

    The report contents will be returned as a stream.

    Args:
      query: A string containing the query which specifies the data you want
          your report to include.
      file_format: A string representing the output format for your report.
          Acceptable values can be found in our API documentation:
          https://developers.google.com/adwords/api/docs/guides/reporting
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set for the client.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Returns:
      A stream to be used in retrieving the report contents.

    Raises:
      AdWordsReportBadRequestError: if the report download fails due to
          improper input.
      GoogleAdsValueError: if the user-specified report format is incompatible
          with the output.
      AdWordsReportError: if the request fails for any other reason; e.g. a
          network error.
    """
    return self._DownloadReportAsStream(self._SerializeAwql(query, file_format),
                                        **kwargs)

  def DownloadReportAsString(self, report_definition, **kwargs):
    """Downloads an AdWords report using a report definition.

    The report contents will be returned as a string.

    Args:
      report_definition: A dictionary or instance of the ReportDefinition class
          generated from the schema. This defines the contents of the report
          that will be downloaded.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set for the client.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Returns:
      A string containing the report contents.

    Raises:
      AdWordsReportBadRequestError: if the report download fails due to
          improper input.
      GoogleAdsValueError: if the user-specified report format is incompatible
          with the output.
      AdWordsReportError: if the request fails for any other reason; e.g. a
          network error.
    """
    response = None
    try:
      response = self._DownloadReportAsStream(
          self._SerializeReportDefinition(report_definition), **kwargs)
      return response.read().decode('utf-8')
    finally:
      if response:
        response.close()

  def DownloadReportAsStringWithAwql(self, query, file_format, **kwargs):
    """Downloads an AdWords report using an AWQL query.

    The report contents will be returned as a string.

    Args:
      query: A string containing the query which specifies the data you want
          your report to include.
      file_format: A string representing the output format for your report.
          Acceptable values can be found in our API documentation:
          https://developers.google.com/adwords/api/docs/guides/reporting
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set for the client.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Returns:
      A string containing the report contents.

    Raises:
      AdWordsReportBadRequestError: if the report download fails due to
          improper input.
      GoogleAdsValueError: if the user-specified report format is incompatible
          with the output.
      AdWordsReportError: if the request fails for any other reason; e.g. a
          network error.
    """
    response = None
    try:
      response = self._DownloadReportAsStream(
          self._SerializeAwql(query, file_format), **kwargs)
      return response.read().decode('utf-8')
    finally:
      if response:
        response.close()

  def DownloadReportWithAwql(self, query, file_format, output=sys.stdout,
                             **kwargs):
    """Downloads an AdWords report using an AWQL query.

    The report contents will be written to the given output.

    Args:
      query: A string or ReportQuery object containing the query which
          specifies the data you want your report to include.
      file_format: A string representing the output format for your report.
          Acceptable values can be found in our API documentation:
          https://developers.google.com/adwords/api/docs/guides/reporting
      [optional]
      output: A writable object where the contents of the report will be written
          to. If the report is gzip compressed, you need to specify an output
          that can write binary data.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set for the client.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Raises:
      AdWordsReportBadRequestError: if the report download fails due to
          improper input.
      GoogleAdsValueError: if the user-specified report format is incompatible
          with the output.
      AdWordsReportError: if the request fails for any other reason; e.g. a
          network error.
    """
    self._DownloadReportCheckFormat(file_format, output)
    self._DownloadReport(self._SerializeAwql(query, file_format), output,
                         **kwargs)

  def _DownloadReport(self, post_body, output, **kwargs):
    """Downloads an AdWords report, writing the contents to the given file.

    This will attempt to determine the encoding of the specified output and
    read the report with the appropriate StreamReader.

    Args:
      post_body: The contents of the POST request's body as a URL encoded
          string.
      output: A writable object where the contents of the report will be written
          to.
      **kwargs: A dictionary containing optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set for the client.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Raises:
      AdWordsReportBadRequestError: if the report download fails due to
        improper input. In the event of certain other failures, a
        urllib2.URLError (Python 2) or urllib.error.URLError (Python 3) will be
        raised.
      AdWordsReportError: if the request fails for any other reason; e.g. a
          network error.
    """
    response = None
    try:
      response = self._DownloadReportAsStream(post_body, **kwargs)

      # Determine encoding of provided output.
      if six.PY3 and isinstance(output, six.StringIO):
        encoding = 'utf-8'
      else:
        encoding = getattr(output, 'encoding', None)

      # If any encoding is found, apply the appropriate StreamReader to the
      # response. When reading in chunks, this prevents truncation of multi-byte
      # characters; e.g. utf-8. For more details, see:
      # https://github.com/googleads/googleads-python-lib/issues/281
      if encoding:
        stream_reader = codecs.getreader(encoding)
        response = stream_reader(response)

      while True:
        chunk = response.read(_CHUNK_SIZE)
        if not chunk: break
        output.write(chunk)
    finally:
      if response:
        response.close()

  def _DownloadReportAsStream(self, post_body, **kwargs):
    """Downloads an AdWords report, returning a stream-like object.

    In Python 2, this will return a urllib2.addinfourl instance. In Python 3,
    this will return a http.client.HTTPResponse instance. In either case,
    reading from the stream-like object will return binary data.

    Args:
      post_body: The contents of the POST request's body as a URL encoded
          string.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
      client_customer_id: A string containing a client_customer_id intended to
        override the default value set for the client.
      include_zero_impressions: A boolean indicating whether the report should
        show rows with zero impressions.
      skip_report_header: A boolean indicating whether to include a header row
          containing the report name and date range. If false or not specified,
          report output will include the header row.
      skip_column_header: A boolean indicating whether to include column names
          in reports. If false or not specified, report output will include the
          column names.
      skip_report_summary: A boolean indicating whether to include a summary row
          containing the report totals. If false or not specified, report output
          will include the summary row.
      use_raw_enum_values: A boolean indicating whether to return enum field
          values as enums instead of display values.

    Returns:
      A stream to be used in retrieving the report contents.

    Raises:
      AdWordsReportBadRequestError: if the report download fails due to
        improper input. In the event of certain other failures, a
        urllib2.URLError (Python 2) or urllib.error.URLError (Python 3) will be
        raised.
      AdWordsReportError: if the request fails for any other reason; e.g. a
          network error.
    """
    if sys.version_info[0] == 3:
      post_body = bytes(post_body, 'utf8')

    request = urllib2.Request(
        self._end_point, post_body,
        self._header_handler.GetReportDownloadHeaders(**kwargs))
    try:
      if _report_logger.isEnabledFor(logging.DEBUG):
        _report_logger.debug('Outgoing request: %s %s',
                             self._SanitizeRequestHeaders(request.headers),
                             post_body)

      response = self.url_opener.open(request)

      if _report_logger.isEnabledFor(logging.INFO):
        _report_logger.info(
            'Request Summary: %s', self._ExtractRequestSummaryFields(request))

      if _report_logger.isEnabledFor(logging.DEBUG):
        _report_logger.debug('Incoming response: %s %s %s REDACTED REPORT DATA',
                             self._ExtractResponseHeaders(response.headers),
                             response.code, response.msg)
      return response
    except urllib2.HTTPError as e:
      error = self._ExtractError(e)
      if _report_logger.isEnabledFor(logging.WARNING):
        _report_logger.warning(
            'Request Summary: %s', self._ExtractRequestSummaryFields(
                request, error=error))
      raise error

  def _SanitizeRequestHeaders(self, headers):
    """Removes sensitive data from request headers for use in logging.

    Args:
      headers: a dict containing the headers to be sanitized.

    Returns:
      A  dict containing a sanitized copy of the provided headers.
    """
    sanitized_headers = dict(headers)

    sanitized_headers['Developertoken'] = 'REDACTED'
    sanitized_headers['Authorization'] = 'REDACTED'

    return sanitized_headers

  def _ExtractResponseHeaders(self, headers):
    """Extracts the given headers to a dict for logging.

    Args:
      headers: a httplib.HTTPMessage instance containing response headers.

    Returns:
      A dict containing the contents of the response headers.
    """
    header_lines = str(headers).split('\n')
    headers = {}

    for header_line in header_lines:
      if header_line:
        k, v = header_line.split(': ')
        headers[k] = v

    return headers

  def _ExtractRequestSummaryFields(self, request, error=None):
    """Extract fields used in the summary logs.

    Args:
      request:  a urllib2.Request instance.
      [optional]
      error: a googleads.errors.AdWordsReportError instance or subclass used to
          retrieve error details. This should only be present when an error
          occurred, otherwise it should be set to None for successful requests.

    Returns:
      A dict containing the fields to be output in the summary logs.
    """
    server = (self._SERVER_PATTERN.search(request.get_full_url())
              .group(1))
    headers = request.headers

    summary_fields = {
        'clientCustomerId': headers.get('Clientcustomerid'),
        'includeZeroImpressions': headers.get('Includezeroimpressions', False),
        'server': server,
        'skipColumnHeader': headers.get('Skipcolumnheader', False),
        'skipReportHeader': headers.get('Skipreportheader', False),
        'skipReportSummary': headers.get('Skipreportsummary', False),
    }

    if error:
      summary_fields['isError'] = True
      summary_fields['errorMessage'] = error.content
    else:
      summary_fields['isError'] = False

    return summary_fields

  def _SerializeAwql(self, query, file_format):
    """Serializes an AWQL query and file format for transport.

    Args:
      query: A string or ReportQuery object representing the AWQL query used in
          the report.
      file_format: A string representing the file format of the generated
          report.

    Returns:
      The given query and format URL encoded into the format needed for an
      AdWords report request as a string. This is intended to be a POST body.
    """
    return urllib.urlencode({'__fmt': file_format, '__rdquery': str(query)})

  def _SerializeReportDefinition(self, report_definition):
    """Serializes a report definition for transport.

    Args:
      report_definition: A dictionary or ReportDefinition object to be
          serialized.

    Returns:
      The given report definition serialized into XML and then URL encoded into
      the format needed for an AdWords report request as a string. This is
      intended to be a POST body.
    """
    return urllib.urlencode(
        {'__rdxml': self.schema_helper.GetSoapXMLForComplexType(
            self._REPORT_DEFINITION_NAME, report_definition)})

  def _ExtractError(self, error):
    """Attempts to extract information from a report download error XML message.

    Args:
      error: A urllib2.HTTPError describing the report download failure.

    Returns:
      An error that should be raised. If the content was an XML error message,
      an AdWordsReportBadRequestError will be returned. Otherwise, an
      AdWordsReportError will be returned.
    """
    content = error.read()
    if sys.version_info[0] == 3:
      content = content.decode()
    if 'reportDownloadError' in content:
      try:
        tree = ElementTree.fromstring(content)
        return googleads.errors.AdWordsReportBadRequestError(
            tree.find('./ApiError/type').text,
            tree.find('./ApiError/trigger').text,
            tree.find('./ApiError/fieldPath').text,
            error.code, error, content)
      except ElementTree.ParseError:
        pass
    return googleads.errors.AdWordsReportError(
        error.code, error, content)


class _QueryBuilder(object):
  """A query builder for building AWQL (AdWords Query Language) queries."""

  def __init__(self, query_builder=None):
    """Creates the query builder with the optional specified query builder.

    This class shouldn't be instantiated directly or extended. Use
    ReportQueryBuilder if you want to create a query for reporting or
    ServiceQueryBuilder if you want to create a query for services.

    Args:
      query_builder: An optional query builder whose properties will be copied
          over to this instance.

    Returns:
      The query builder.

    Raises:
      GoogleAdsValueError: If the passed query_builder isn't of the QueryBuilder
          type.
    """
    if query_builder is None:
      self.where_builders = []
    else:
      try:
        self.where_builders = list(query_builder.where_builders)
      except (AttributeError, TypeError):
        raise googleads.errors.GoogleAdsValueError(
            'The passed query builder should be of the QueryBuilder type.')

  def Select(self, *fields):
    """Sets a provided list of fields as selected fields for the query.

    Args:
      *fields: The specified list of fields to be added to a SELECT clause.

    Returns:
      This query builder.
    """
    raise NotImplementedError('You must subclass _QueryBuilder.')

  def Where(self, field):
    """Creates a WHERE builder using a provided field.

    Args:
      field: the field to be added as an argument in the WHERE clause.

    Returns:
      The created WHERE builder.
    """
    where_builder = _WhereBuilder(self, field)
    self.where_builders.append(where_builder)
    return where_builder


class _WhereBuilder(object):
  """A WHERE builder for building a WHERE clause in AWQL queries."""

  def __init__(self, query_builder, field):
    """Creates the WHERE builder with specified query builder and field.

    This class should be instantiated through _QueryBuilder.Where. Don't call
    this constructor directly.

    Args:
      query_builder: The query builder that this WHERE builder links to.
      field: The field to be used in the WHERE condition.

    Returns:
      The WHERE builder.
    """
    self._field = field
    self._query_builder = query_builder
    self._awql = None

  def EqualTo(self, value):
    """Sets the type of the WHERE clause as "equal to".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, '=')
    return self._query_builder

  def NotEqualTo(self, value):
    """Sets the type of the WHERE clause as "not equal to".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, '!=')
    return self._query_builder

  def GreaterThan(self, value):
    """Sets the type of the WHERE clause as "greater than".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, '>')
    return self._query_builder

  def GreaterThanOrEqualTo(self, value):
    """Sets the type of the WHERE clause as "greater than or equal to".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, '>=')
    return self._query_builder

  def LessThan(self, value):
    """Sets the type of the WHERE clause as "less than".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, '<')
    return self._query_builder

  def LessThanOrEqualTo(self, value):
    """Sets the type of the WHERE clause as "less than or equal to.

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, '<=')
    return self._query_builder

  def StartsWith(self, value):
    """Sets the type of the WHERE clause as "starts with".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, 'STARTS_WITH')
    return self._query_builder

  def StartsWithIgnoreCase(self, value):
    """Sets the type of the WHERE clause as "starts with ignore case".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value,
                                                  'STARTS_WITH_IGNORE_CASE')
    return self._query_builder

  def Contains(self, value):
    """Sets the type of the WHERE clause as "contains".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, 'CONTAINS')
    return self._query_builder

  def ContainsIgnoreCase(self, value):
    """Sets the type of the WHERE clause as "contains ignore case".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, 'CONTAINS_IGNORE_CASE')
    return self._query_builder

  def DoesNotContain(self, value):
    """Sets the type of the WHERE clause as "does not contain".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(value, 'DOES_NOT_CONTAIN')
    return self._query_builder

  def DoesNotContainIgnoreCase(self, value):
    """Sets the type of the WHERE clause as "doesn not contain ignore case".

    Args:
      value: The value to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateSingleValueCondition(
        value, 'DOES_NOT_CONTAIN_IGNORE_CASE')
    return self._query_builder

  def In(self, *values):
    """Sets the type of the WHERE clause as "in".

    Args:
      *values: The values to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateMultipleValuesCondition(values, 'IN')
    return self._query_builder

  def NotIn(self, *values):
    """Sets the type of the WHERE clause as "in".

    Args:
      *values: The values to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateMultipleValuesCondition(values, 'NOT_IN')
    return self._query_builder

  def ContainsAny(self, *values):
    """Sets the type of the WHERE clause as "contains any".

    Args:
      *values: The values to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateMultipleValuesCondition(values, 'CONTAINS_ANY')
    return self._query_builder

  def ContainsNone(self, *values):
    """Sets the type of the WHERE clause as "contains none".

    Args:
      *values: The values to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateMultipleValuesCondition(values, 'CONTAINS_NONE')
    return self._query_builder

  def ContainsAll(self, *values):
    """Sets the type of the WHERE clause as "contains all".

    Args:
      *values: The values to be used in the WHERE condition.

    Returns:
      The query builder that this WHERE builder links to.
    """
    self._awql = self._CreateMultipleValuesCondition(values, 'CONTAINS_ALL')
    return self._query_builder

  def Build(self):
    """Builds the WHERE clause by returning the stored AWQL.

    Returns:
      The resulting WHERE clause in AWQL format.
    """
    return self._awql

  def _CreateSingleValueCondition(self, value, operator):
    """Creates a single-value condition with the provided value and operator."""
    if isinstance(value, str) or isinstance(value, unicode):
      value = '"%s"' % value
    return '%s %s %s' % (self._field, operator, value)

  def _CreateMultipleValuesCondition(self, values, operator):
    """Creates a condition with the provided list of values and operator."""
    values = ['"%s"' % value if isinstance(value, str) or
              isinstance(value, unicode) else str(value) for value in values]
    return '%s %s [%s]' % (self._field, operator, ', '.join(values))


@googleads.common.RegisterUtility('ReportQueryBuilder')
class ReportQueryBuilder(_QueryBuilder):
  """A query builder for building AWQL queries for reporting."""

  def __init__(self, query_builder=None):
    """Creates the report query builder with the optionally specified builder.

    Creates the report query builder by initializing all attributes including
    the report name, time range, start and end date. If the optional query
    builder are specified, copy all its attributes to this instance.

    Args:
      query_builder: An optional query builder whose attributes will be copied
          over to this instance.

    Returns:
      This report query builder.

    Raises:
      GoogleAdsValueError: If the passed query_builder isn't of the QueryBuilder
          type.
    """
    _QueryBuilder.__init__(self, query_builder)
    if query_builder is None:
      self.select = None
      self.from_report = None
      self.date_range = None
      self.start_date = None
      self.end_date = None
    else:
      try:
        self.select = list(query_builder.select)
        self.from_report = query_builder.from_report
        self.date_range = query_builder.date_range
        self.start_date = query_builder.start_date
        self.end_date = query_builder.end_date
      except (AttributeError, TypeError):
        raise googleads.errors.GoogleAdsValueError(
            'The passed query builder should be of ReportQueryBuilder type.')

  def Select(self, *fields):
    """Sets a provided list of fields as selected fields for the query.

    Subsequent calls to this method overwrite the entire set of selected fields
    with the new one.

    Args:
      *fields: The specified list of fields to be added to a SELECT clause.

    Returns:
      This report query builder.
    """
    self.select = list(fields)
    return self

  def From(self, report_name):
    """Sets a provided report name as the argument to FROM clause.

    Args:
      report_name: The specified report name.

    Returns:
      This report query builder.
    """
    self.from_report = report_name
    return self

  def During(self, date_range=None, start_date=None, end_date=None):
    """Sets arguments for the DURING clause of the query.

    Sets arguments for the DURING clause using the provided date range or start
    and end dates. Only the date range or start and end date should be
    specified. If both are supplied, an error will be thrown. A valid date range
    string can be found at
    https://developers.google.com/adwords/api/docs/guides/reporting#date_ranges.
    Start and end dates should be in 'YYYYMMDD' format.

    Args:
      date_range: The specified date range string, e.g., YESTERDAY.
      start_date: The start date string in 'YYYYMMDD' format or an instance of
          datetime.date.
      end_date: The end date string in 'YYYYMMDD' format or an instance of
          datetime.date.

    Returns:
      This report query builder.

    Raises:
      ValueError: If all the arguments are None or both date_range and start
          and end dates have values or if start_date has value but end_date
          doesn't (and vice versa).
    """
    if date_range is None and (start_date is None or end_date is None):
      raise ValueError(
          'Either date_range or both start_date and end_date must not be None.')
    if date_range is not None and (start_date is not None
                                   or end_date is not None):
      raise ValueError(
          'If date_range is not None, start_date and end_date must be None '
          '(and vice versa).')
    self.date_range = date_range
    self.start_date = start_date
    self.end_date = end_date
    return self

  def Build(self):
    """Builds a ReportQuery object containing the created AWQL query.

    Returns:
      The created ReportQuery object.

    Raises:
      ValueError: If the selected fields or report name is not specified.
    """
    if self.select is None:
      raise ValueError('Must use Select() to specify SELECT clause for valid'
                       ' AWQL first.')
    if self.from_report is None:
      raise ValueError('Must use From() to specify FROM clause for valid AWQL'
                       ' first.')

    parts = ['SELECT ', (', '.join(self.select))]
    parts.extend([' FROM ', self.from_report])
    where_clause = (' WHERE %s' % ' AND '.join([builder.Build() for builder
                                                in self.where_builders])
                    if self.where_builders else '')
    parts += where_clause

    if self.date_range:
      parts.extend([' DURING ', self.date_range])
    elif self._start_date and self._end_date:
      parts.extend([' DURING ', '%s,%s' % (self._start_date, self._end_date)])
    awql = ''.join(parts)

    return ReportQuery(awql)

  @property
  def start_date(self):
    """Gets the start date of the query."""
    return self._start_date

  @start_date.setter
  def start_date(self, start_date):
    """Sets the start date of the query to the provided value."""
    if isinstance(start_date, datetime.date):
      self._start_date = '{:%Y%m%d}'.format(start_date)
    else:
      self._start_date = start_date

  @property
  def end_date(self):
    """Gets the end date of the query."""
    return self._end_date

  @end_date.setter
  def end_date(self, end_date):
    """Sets the end date of the query to the provided value."""
    if isinstance(end_date, datetime.date):
      self._end_date = '{:%Y%m%d}'.format(end_date)
    else:
      self._end_date = end_date


class ReportQuery(object):
  """A report query storing an AWQL query."""

  def __init__(self, awql):
    """Creates a report query instance storing the provided AWQL query."""
    self._awql = awql

  def __str__(self):
    """Returns the stored AWQL query."""
    return self._awql


@googleads.common.RegisterUtility('ServiceQueryBuilder')
class ServiceQueryBuilder(_QueryBuilder):
  """A query builder for building AWQL queries for services."""

  _ORDER_BY_CLAUSE = namedtuple('OrderByClause', ['field', 'direction'])

  def __init__(self, query_builder=None):
    """Creates the service query builder with the optionally specified builder.

    Creates the service query builder by initializing all attributes including
    oder by list, start index, and page size.
    If the optional query builder are specified, copy all its attributes to this
    instance.

    Args:
      query_builder: An optional query builder whose attributes will be copied
          over to this instance.

    Returns:
      This service query builder.

    Raises:
      GoogleAdsValueError: If the passed query_builder isn't of the QueryBuilder
          type.
    """
    _QueryBuilder.__init__(self, query_builder)
    if query_builder is None:
      self.select = set()
      self.order_by_list = []
      self.start_index = None
      self.page_size = None
    else:
      try:
        self.select = query_builder.select
        self.order_by_list = query_builder.order_by_list
        self.start_index = query_builder.start_index
        self.page_size = query_builder.page_size
      except (AttributeError, TypeError):
        raise googleads.errors.GoogleAdsValueError(
            'The passed query builder should be of ServiceQueryBuilder type.')

  def Select(self, *fields):
    """Sets a provided list of fields as selected fields for the query.

    Subsequent calls to this method overwrite the entire set of selected fields
    with the new one. Duplicate field names will be treated as one field.

    Args:
      *fields: The specified list of fields to be added to a SELECT clause.

    Returns:
      This service query builder.
    """
    self.select.update(fields)
    return self

  def OrderBy(self, field, ascending=True):
    """Adds the provided field to the order-by list with the provided direction.

    Args:
      field: The specified field to be added to the order-by list.
      ascending: If true, the newly created order-by clause will be in ascending
          order. Otherwise, it will be in descending order.

    Returns:
      This service query builder.
    """
    order_by = self._ORDER_BY_CLAUSE(field, 'ASC' if ascending else 'DESC')
    self.order_by_list.append(order_by)
    return self

  def Limit(self, start_index, page_size):
    """Sets the LIMIT clause using the provided start index and page size.

    Args:
      start_index: The specified start index for the LIMIT clause.
      page_size: The optional page size for the LIMIT clause.

    Returns:
      This service query builder.

    Raises:
      ValueError: If start_index is None but the page_size is not None or vice
          versa.
    """
    if ((start_index is None and page_size is not None)
        or (start_index is not None and page_size is None)):
      raise ValueError('Either both start_index and page_size must be None, or'
                       ' neither')
    self.start_index = start_index
    self.page_size = page_size
    return self

  def Build(self):
    """Builds a ServiceQuery object containing AWQL queries.

    Returns:
      The created ServiceQuery object.

    Raises:
      ValueError: If the selected fields or service name is not specified.
    """
    if not self.select:
      raise ValueError('Must use Select() to specify SELECT clause for valid'
                       ' AWQL first')

    parts = ['SELECT ', (', '.join(self.select))]
    where_clause = (' WHERE %s' % ' AND '.join(builder.Build() for builder
                                               in self.where_builders)
                    if self.where_builders else '')
    parts += where_clause

    if self.order_by_list:
      parts.extend([' ORDER BY ',
                    ', '.join('%s %s' % (order_by.field, order_by.direction)
                              for order_by in self.order_by_list)])
    awql = ''.join(parts)

    return ServiceQuery(awql, self.start_index, self.page_size)

  @property
  def select(self):
    """Gets the select set of the query."""
    return self._select

  @select.setter
  def select(self, select):
    """Sets the select set of the query to the copy of provided value."""
    self._select = set(select)

  @property
  def order_by_list(self):
    """Gets the order-by list of the query."""
    return self._order_by_list

  @order_by_list.setter
  def order_by_list(self, order_by_list):
    """Sets the order-by list of the query to the copy of provided value."""
    self._order_by_list = list(order_by_list)


class ServiceQuery(object):
  """A service query storing an AWQL query."""

  _BID_LANDSCAPE_PAGES = ('AdGroupBidLandscapePage',
                          'CriterionBidLandscapePage')
  _LANDSCAPE_POINTS = 'landscapePoints'
  _TOTAL_NUM_ENTRIES = 'totalNumEntries'
  _ENTRIES = 'entries'
  _PAGE_TYPE = 'Page.Type'

  def __init__(self, awql, start_index, page_size):
    """Creates a service query instance storing the provided AWQL query."""
    self._awql = awql
    self._start_index = start_index
    self._page_size = page_size
    self._total_num_entries = None

  def NextPage(self, page=None):
    """Sets the LIMIT clause of the AWQL to the next page.

    This method is meant to be used with HasNext(). When using DataService,
    page is needed, as its paging mechanism is different from other services.
    For details, see
    https://developers.google.com/adwords/api/docs/guides/bid-landscapes#paging_through_results.

    Args:
      page: An optional dict-like page returned in an API response, where the
          type depends on the configured SOAP client. The page contains the
          'totalNumEntries' key whose value represents the total number of
          results from making the query to the AdWords API services. This page
          is required when using this method with DataService.

    Returns:
      This service query object.

    Raises:
      ValueError: If the start index of this object is None, meaning that the
          LIMIT clause hasn't been set before.
    """
    if self._start_index is None:
      raise ValueError('Cannot page through query with no LIMIT clause.')

    # DataService has a different paging mechanism, resulting in different
    # method of determining if there is still a page left.
    page_size = None
    if (page and self._PAGE_TYPE in page
        and page[self._PAGE_TYPE] in self._BID_LANDSCAPE_PAGES):
      page_size = sum([len(bid_landscape[self._LANDSCAPE_POINTS])
                       for bid_landscape in page[self._ENTRIES]])

    increment = page_size or self._page_size
    self._start_index += increment
    return self

  def HasNext(self, page):
    """Checks if there is still a page left to query.

    This method is meant to be used with NextPage(). When using DataService,
    the paging mechanism is different from other services. For details, see
    https://developers.google.com/adwords/api/docs/guides/bid-landscapes#paging_through_results.

    Args:
      page: A dict-like page returned in an API response, where the type depends
          on the configured SOAP client. The page contains the 'totalNumEntries'
          key whose value represents the total number of results from making the
          query to the AdWords API services.

    Returns:
      True if there is still a page left.

    Raises:
      ValueError: If the start index of this object is None, meaning that the
          LIMIT clause hasn't been set before.
    """
    if self._start_index is None:
      raise ValueError('Cannot page through query with no LIMIT clause.')
    if page is None:
      raise ValueError('The passed page cannot be None.')

    # DataService has a different paging mechanism, resulting in different
    # method of determining if there is still a page left.
    if (self._PAGE_TYPE in page
        and page[self._PAGE_TYPE] in self._BID_LANDSCAPE_PAGES):
      if self._ENTRIES in page:
        total_landscape_points = sum([len(bid_landscape[self._LANDSCAPE_POINTS])
                                      for bid_landscape in page[self._ENTRIES]])
      else:
        total_landscape_points = 0
      return total_landscape_points >= self._page_size

    if not self._total_num_entries:
      self._total_num_entries = page[self._TOTAL_NUM_ENTRIES]
    return self._start_index + self._page_size < self._total_num_entries

  def Pager(self, service):
    """A page generator for this service query and the provided service.

    This generates a page as a result from using the provided service's query()
    method until there are no more results to fetch.

    Args:
      service: The service object for making a query using this service query.

    Yields:
      A resulting page from querying the provided service.
    """
    has_page = True
    while has_page:
      page = service.query(self)
      yield page
      has_page = self.HasNext(page)
      if has_page:
        self.NextPage()

  def __str__(self):
    """Returns the stored AWQL query combined with the LIMIT clause."""
    awql = self._awql + ' LIMIT %s,%s' % (self._start_index, self._page_size)
    return awql
