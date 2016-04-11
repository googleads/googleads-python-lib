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

from collections import namedtuple
import io
import os
import re
import sys
import urllib
import urllib2
from xml.etree import ElementTree


import suds.client
import suds.mx.literal
import suds.xsd.doctor
import xmltodict
import yaml

import googleads.common
import googleads.errors

# A giant dictionary of AdWords versions, the services they support, and which
# namespace those services are in.
_SERVICE_MAP = {
    'v201509': {
        'AccountLabelService': 'mcm',
        'AdCustomizerFeedService': 'cm',
        'AdGroupAdService': 'cm',
        'AdGroupBidModifierService': 'cm',
        'AdGroupCriterionService': 'cm',
        'AdGroupExtensionSettingService': 'cm',
        'AdGroupFeedService': 'cm',
        'AdGroupService': 'cm',
        'AdParamService': 'cm',
        'BatchJobService': 'cm',
        'BudgetOrderService': 'billing',
        'CampaignCriterionService': 'cm',
        'CampaignExtensionSettingService': 'cm',
        'CampaignFeedService': 'cm',
        'CampaignService': 'cm',
        'CampaignSharedSetService': 'cm',
        'ConstantDataService': 'cm',
        'ConversionTrackerService': 'cm',
        'CustomerExtensionSettingService': 'cm',
        'CustomerSyncService': 'ch',
        'DataService': 'cm',
        'ExperimentService': 'cm',
        'FeedItemService': 'cm',
        'FeedMappingService': 'cm',
        'FeedService': 'cm',
        'LocationCriterionService': 'cm',
        'MediaService': 'cm',
        'MutateJobService': 'cm',
        'OfflineConversionFeedService': 'cm',
        'ReportDefinitionService': 'cm',
        'SharedCriterionService': 'cm',
        'SharedSetService': 'cm',
        'TargetingIdeaService': 'o',
        'TrafficEstimatorService': 'o',
        'ManagedCustomerService': 'mcm',
        'CustomerService': 'mcm',
        'CustomerFeedService': 'cm',
        'BudgetService': 'cm',
        'BiddingStrategyService': 'cm',
        'AdwordsUserListService': 'rm',
        'LabelService': 'cm',
    },
    'v201601': {
        'AccountLabelService': 'mcm',
        'AdCustomizerFeedService': 'cm',
        'AdGroupAdService': 'cm',
        'AdGroupBidModifierService': 'cm',
        'AdGroupCriterionService': 'cm',
        'AdGroupExtensionSettingService': 'cm',
        'AdGroupFeedService': 'cm',
        'AdGroupService': 'cm',
        'AdParamService': 'cm',
        'BatchJobService': 'cm',
        'BudgetOrderService': 'billing',
        'CampaignCriterionService': 'cm',
        'CampaignExtensionSettingService': 'cm',
        'CampaignFeedService': 'cm',
        'CampaignService': 'cm',
        'CampaignSharedSetService': 'cm',
        'ConstantDataService': 'cm',
        'ConversionTrackerService': 'cm',
        'CustomerExtensionSettingService': 'cm',
        'CustomerSyncService': 'ch',
        'DataService': 'cm',
        'ExperimentService': 'cm',
        'FeedItemService': 'cm',
        'FeedMappingService': 'cm',
        'FeedService': 'cm',
        'LocationCriterionService': 'cm',
        'MediaService': 'cm',
        'MutateJobService': 'cm',
        'OfflineConversionFeedService': 'cm',
        'ReportDefinitionService': 'cm',
        'SharedCriterionService': 'cm',
        'SharedSetService': 'cm',
        'TargetingIdeaService': 'o',
        'TrafficEstimatorService': 'o',
        'ManagedCustomerService': 'mcm',
        'CustomerService': 'mcm',
        'CustomerFeedService': 'cm',
        'BudgetService': 'cm',
        'BiddingStrategyService': 'cm',
        'AdwordsUserListService': 'rm',
        'LabelService': 'cm',
    },
    'v201603': {
        'AccountLabelService': 'mcm',
        'AdCustomizerFeedService': 'cm',
        'AdGroupAdService': 'cm',
        'AdGroupBidModifierService': 'cm',
        'AdGroupCriterionService': 'cm',
        'AdGroupExtensionSettingService': 'cm',
        'AdGroupFeedService': 'cm',
        'AdGroupService': 'cm',
        'AdParamService': 'cm',
        'AdwordsUserListService': 'rm',
        'BatchJobService': 'cm',
        'BiddingStrategyService': 'cm',
        'BudgetOrderService': 'billing',
        'BudgetService': 'cm',
        'CampaignCriterionService': 'cm',
        'CampaignExtensionSettingService': 'cm',
        'CampaignFeedService': 'cm',
        'CampaignService': 'cm',
        'CampaignSharedSetService': 'cm',
        'ConstantDataService': 'cm',
        'ConversionTrackerService': 'cm',
        'CustomerExtensionSettingService': 'cm',
        'CustomerService': 'mcm',
        'CustomerSyncService': 'ch',
        'CustomerFeedService': 'cm',
        'DataService': 'cm',
        'DraftAsyncErrorService': 'cm',
        'DraftService': 'cm',
        'ExperimentService': 'cm',
        'FeedItemService': 'cm',
        'FeedMappingService': 'cm',
        'FeedService': 'cm',
        'LabelService': 'cm',
        'LocationCriterionService': 'cm',
        'ManagedCustomerService': 'mcm',
        'MediaService': 'cm',
        'OfflineConversionFeedService': 'cm',
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
_REPORT_HEADER_KWARGS = {'include_zero_impressions': 'includeZeroImpressions',
                         'skip_report_header': 'skipReportHeader',
                         'skip_column_header': 'skipColumnHeader',
                         'skip_report_summary': 'skipReportSummary'}

# The endpoint used by default when making AdWords API requests.
_DEFAULT_ENDPOINT = 'https://adwords.google.com'


class AdWordsClient(object):
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
    https_proxy: A string identifying the URL of a proxy that all HTTPS requests
        should be routed through. Modifying this value will not affect any SOAP
        service clients you've already created.
  """

  # The key in the storage yaml which contains AdWords data.
  _YAML_KEY = 'adwords'
  # A list of values which must be provided to use AdWords.
  _REQUIRED_INIT_VALUES = ('user_agent', 'developer_token')
  # A list of values which may optionally be provided when using AdWords.
  _OPTIONAL_INIT_VALUES = ('validate_only', 'partial_failure',
                           'client_customer_id')
  # The format of SOAP service WSDLs. A server, namespace, version, and service
  # name need to be formatted in.
  _SOAP_SERVICE_FORMAT = '%s/api/adwords/%s/%s/%s?wsdl'

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

  def __init__(
      self, developer_token, oauth2_client, user_agent,
      client_customer_id=None, validate_only=False, partial_failure=False,
      https_proxy=None, cache=None):
    """Initializes an AdWordsClient.

    For more information on these arguments, see our SOAP headers guide:
    https://developers.google.com/adwords/api/docs/guides/soap

    Args:
      developer_token: A string containing your AdWords API developer token.
      oauth2_client: A googleads.oauth2.GoogleOAuth2Client used to authorize
          your requests.
      user_agent: An arbitrary string which will be used to identify your
          application
      [optional]
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
      https_proxy: A string identifying the proxy that all HTTPS requests
          should be routed through.
      cache: A subclass of suds.cache.Cache; defaults to None.
    """
    self.developer_token = developer_token
    self.oauth2_client = oauth2_client
    self.oauth2_client.Refresh()
    self.user_agent = user_agent
    self.client_customer_id = client_customer_id
    self.validate_only = validate_only
    self.partial_failure = partial_failure
    self.https_proxy = https_proxy
    self.cache = cache

  def GetService(self, service_name, version=sorted(_SERVICE_MAP.keys())[-1],
                 server=_DEFAULT_ENDPOINT):
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
      A suds.client.ServiceSelector which has the headers and proxy configured
          for use.

    Raises:
      A GoogleAdsValueError if the service or version provided do not exist.
    """
    if server[-1] == '/': server = server[:-1]
    try:
      proxy_option = None
      if self.https_proxy:
        proxy_option = {
            'https': self.https_proxy
        }

      client = suds.client.Client(
          self._SOAP_SERVICE_FORMAT %
          (server, _SERVICE_MAP[version][service_name], version, service_name),
          proxy=proxy_option, cache=self.cache, timeout=3600)
    except KeyError:
      if version in _SERVICE_MAP:
        raise googleads.errors.GoogleAdsValueError(
            'Unrecognized service for the AdWords API. Service given: %s '
            'Supported services: %s'
            % (service_name, _SERVICE_MAP[version].keys()))
      else:
        raise googleads.errors.GoogleAdsValueError(
            'Unrecognized version of the AdWords API. Version given: %s '
            'Supported versions: %s' % (version, _SERVICE_MAP.keys()))

    return googleads.common.SudsServiceProxy(
        client, _AdWordsHeaderHandler(self, version))

  def GetBatchJobHelper(self, version=sorted(_SERVICE_MAP.keys())[-1],
                        server=_DEFAULT_ENDPOINT):
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
    request_builder = BatchJobHelper.GetRequestBuilder(
        client=self, version=version, server=server)
    response_parser = BatchJobHelper.GetResponseParser()

    return BatchJobHelper(request_builder, response_parser, version=version)

  def GetReportDownloader(self, version=sorted(_SERVICE_MAP.keys())[-1],
                          server=_DEFAULT_ENDPOINT):
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
  _LIB_SIG = googleads.common.GenerateLibSig('AwApi-Python')
  # The name of the WSDL-defined SOAP Header class used in all SOAP requests.
  # The namespace needs the version of AdWords being used to be templated in.
  _SOAP_HEADER_CLASS = ('{https://adwords.google.com/api/adwords/cm/%s}'
                        'SoapHeader')
  # The content type of report download requests
  _CONTENT_TYPE = 'application/x-www-form-urlencoded'

  def __init__(self, adwords_client, version):
    """Initializes an AdWordsHeaderHandler.

    Args:
      adwords_client: An AdWordsClient whose data will be used to fill in the
          headers. We retain a reference to this object so that the header
          handler picks up changes to the client.
      version: A string identifying which version of AdWords this header handler
          will be used for.
    """
    self._adwords_client = adwords_client
    self._version = version

  def SetHeaders(self, suds_client):
    """Sets the SOAP and HTTP headers on the given suds client."""
    header = suds_client.factory.create(self._SOAP_HEADER_CLASS % self._version)
    header.clientCustomerId = self._adwords_client.client_customer_id
    header.developerToken = self._adwords_client.developer_token
    header.userAgent = ''.join([self._adwords_client.user_agent, self._LIB_SIG])
    header.validateOnly = self._adwords_client.validate_only
    header.partialFailure = self._adwords_client.partial_failure

    suds_client.set_options(
        soapheaders=header,
        headers=self._adwords_client.oauth2_client.CreateHttpHeader())

  def GetReportDownloadHeaders(self, kwargs):
    """Returns a dictionary of headers for a report download request.

    Args:
      kwargs: A dictionary containing optional keyword arguments.

    Keyword Arguments:
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

    Returns:
      A dictionary containing the headers configured for downloading a report.
    """
    headers = self._adwords_client.oauth2_client.CreateHttpHeader()
    headers.update({
        'Content-type': self._CONTENT_TYPE,
        'developerToken': str(self._adwords_client.developer_token),
        'clientCustomerId': str(self._adwords_client.client_customer_id),
        'User-Agent': ''.join([self._adwords_client.user_agent, self._LIB_SIG,
                               ',gzip'])
    })

    for kw in kwargs:
      try:
        headers.update({_REPORT_HEADER_KWARGS[kw]: str(kwargs[kw])})
      except KeyError:
        raise googleads.errors.GoogleAdsValueError(
            'The provided keyword "%s" is invalid. Accepted keywords are: %s'
            % (kw, _REPORT_HEADER_KWARGS.keys()))

    return headers


class BatchJobHelper(object):
  """A utility that simplifies working with the BatchJobService."""

  class AbstractResponseParser(object):
    """Interface for parsing responses from the BatchJobService."""

    def ParseResponse(self, batch_job_response):
      """Parses a Batch Job Service response..

      Args:
        batch_job_response: a str containing the response from the
        BatchJobService.
      """
      raise NotImplementedError('You must subclass'
                                'AbstractResponseParser.')

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
      raise NotImplementedError('You must subclass'
                                'AbstractUploadRequestBuilder.')

  class _SudsUploadRequestBuilder(AbstractUploadRequestBuilder):
    """Builds requests used to upload operations for Batch Jobs."""
    # Used to remove namespace from xsi:type Element attributes.
    _ATTRIB_NAMESPACE_SUB = re.compile('ns[0-1]:')
    # Components of the upload request.
    _UPLOAD_PREFIX_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<mutate xmlns="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">"""
    _UPLOAD_SUFFIX = '</mutate>'
    # Incremental uploads must have a content-length that is a multiple of this.
    _BATCH_JOB_INCREMENT = 262144
    # Generate a mapping of Operations to their service and methods.
    _OPERATION_MAP = {
        op[0]: namedtuple('Operation', ['operation_type', 'service', 'method'])
               (op[0], op[1], op[2])
        for op in (
            ('AdGroupAdOperation', 'AdGroupAdService', 'mutate'),
            ('AdGroupAdLabelOperation', 'AdGroupAdService', 'mutateLabel'),
            ('AdGroupBidModifierOperation', 'AdGroupBidModifierService',
             'mutate'),
            ('AdGroupCriterionOperation', 'AdGroupCriterionService',
             'mutate'),
            ('AdGroupCriterionLabelOperation', 'AdGroupCriterionService',
             'mutateLabel'),
            ('AdGroupOperation', 'AdGroupService', 'mutate'),
            ('AdGroupLabelOperation', 'AdGroupService', 'mutateLabel'),
            ('BudgetOperation', 'BudgetService', 'mutate'),
            ('CampaignCriterionOperation', 'CampaignCriterionService',
             'mutate'),
            ('CampaignOperation', 'CampaignService', 'mutate'),
            ('CampaignLabelOperation', 'CampaignService', 'mutateLabel'),
            ('FeedItemOperation', 'FeedItemService', 'mutate')
        )
    }

    def __init__(self, **kwargs):
      """Initializes a _SudsUploadRequestBuilder.

      Arguments:
        **kwargs: Keyword arguments.

      Keyword Arguments:
        client: an AdWordsClient instance.
        version: a string identifying the AdWords version to connect to.
        server: a string identifying the webserver hosting the AdWords API.

      Raises:
        AttributeError: if no client is specified in the Keyword Arguments.
      """
      if 'client' not in kwargs:
        raise AttributeError('No client specified for Request Builder.')

      self._version = kwargs.get('version', sorted(_SERVICE_MAP.keys())[-1])
      self._client = kwargs['client']
      server = kwargs.get('server', _DEFAULT_ENDPOINT)
      self._adwords_endpoint = ('%s/api/adwords/cm/%s' %
                                (server, self._version))
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
      req.add_header('Content-Length', padded_request_length)
      req.add_header('Content-Range', 'bytes %s-%s/%s' % (
          current_content_length,
          new_content_length - 1,
          new_content_length if is_last else '*'
      ))
      req.data = request_body.encode('utf-8')
      return req

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
        full_soap_xml: The full XML for the desired operation, as generated by
          suds.

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
        operations.attrib['xsi:type'] = operation_type.text
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
      if operations:
            # Verify that all operations included specify an xsi_type.
        for operation in operations:
          if 'xsi_type' not in operation:
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
        A str containing the raw XML of the request to the given service that
        would execute the given operations.
      """
      try:
        operation = self._OPERATION_MAP[operations[0]['xsi_type']]
      except KeyError, e:
        raise googleads.errors.GoogleAdsValueError('"%s" is an unsupported '
                                                   'operation.' % e.message)
      service = self._client.GetService(operation.service, self._version)
      service.suds_client.set_options(nosend=True)
      service_request = (getattr(service, operation.method)
                         (operations).envelope)
      service.suds_client.set_options(nosend=False)
      return service_request

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
        raw_request_xml: The full XML for the desired operation, as generated by
          suds.

      Returns:
        An unmodified Element containing the operations from the raw request
        xml.

      Raises:
        AttributeError: if the provided XML isn't from AdWords.
      """
      root = ElementTree.fromstring(raw_request_xml)
      return root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body').find(
          './/')

  def __init__(self, request_builder, response_parser,
               version=sorted(_SERVICE_MAP.keys())[-1]):
    """Initializes the BatchJobHelper.

    For general use, consider using AdWordsClient's GetBatchJobHelper method to
    receive an initialized BatchJobHelper using the default request builder and
    response parser.

    Args:
      request_builder: an AbstractUploadRequestBuilder instance.
      response_parser: an AbstractResponseParser instance.
      version: A string identifying the AdWords version to connect to. This
        defaults to what is currently the latest version. This will be updated
        in future releases to point to what is then the latest version.
    """
    self._temporary_id = 0  # Used for temporary IDs in BatchJobService.
    self._request_builder = request_builder
    self._response_parser = response_parser
    self._version = version

  def GetId(self):
    """Produces a distinct sequential ID for the BatchJobService.

    Returns:
      A negative number that will be the temporary ID for an API resource.
    """
    self._temporary_id -= 1
    return self._temporary_id

  def GetIncrementalUploadHelper(self, upload_url, current_content_length=0):
    return IncrementalUploadHelper(self._request_builder, upload_url,
                                   current_content_length,
                                   version=self._version)

  @classmethod
  def GetRequestBuilder(cls, **kwargs):
    """Get a new AbstractUploadRequestBuilder instance."""
    return cls._SudsUploadRequestBuilder(**kwargs)

  @classmethod
  def GetResponseParser(cls, **kwargs):
    """Get a new AbstractResponseParser instance."""
    return cls._XMLToDictResponseParser(**kwargs)

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
    uploader = IncrementalUploadHelper(self._request_builder, upload_url,
                                       version=self._version)
    uploader.UploadOperations(operations, is_last=True)


class IncrementalUploadHelper(object):
  """A utility for uploading operations for a BatchJob incrementally."""

  @classmethod
  def Load(cls, file_input, client=None):
    """Loads an IncrementalUploadHelper from the given file-like object.

    Args:
      file_input: a file-like object containing a serialized
        IncrementalUploadHelper.
      client: an AdWordsClient instance.

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
    except yaml.YAMLError:
      raise googleads.errors.GoogleAdsError(
          'Error loading IncrementalUploadHelper from file.')

    batch_job_helper = client.GetBatchJobHelper(version=data['version'])
    request_builder = batch_job_helper.GetRequestBuilder(
        client=client, version=data['version'])

    try:
      return cls(request_builder, data['upload_url'],
                 current_content_length=data['current_content_length'],
                 is_last=data['is_last'], version=data['version'])
    except KeyError:
      raise googleads.errors.GoogleAdsValueError(
          'Can\'t parse IncrementalUploadHelper from file.')

  def __init__(self, request_builder, upload_url, current_content_length=0,
               is_last=False, version=sorted(_SERVICE_MAP.keys())[-1]):
    """Initializes the IncrementalUpload.

    Args:
      request_builder: an AbstractUploadRequestBuilder instance.
      upload_url: a string url provided by the BatchJobService.
      current_content_length: an integer identifying the current content length
        of data uploaded to the Batch Job.
      is_last: a boolean indicating whether this is the final increment.
      version: A string identifying the AdWords version to connect to. This
        defaults to what is currently the latest version. This will be updated
        in future releases to point to what is then the latest version.
    Raises:
      GoogleAdsValueError: if the content length is lower than 0.
    """
    self._version = version
    self._request_builder = request_builder
    if current_content_length < 0:
      raise googleads.errors.GoogleAdsValueError(
          'Current content length %s is < 0.' % current_content_length)
    self._current_content_length = current_content_length
    self._upload_url = self._InitializeURL(upload_url, current_content_length)
    self._is_last = is_last

  def _InitializeURL(self, upload_url, current_content_length):
    """Ensures that the URL used to upload operations is properly initialized.

    Initialization is only necessary in v201601 or higher when the
    current_content_length is 0.

    Args:
      upload_url: a string url.
      current_content_length: an integer identifying the current content length
        of data uploaded to the Batch Job.

    Returns:
      An initialized string URL, or the provided string URL if the URL has
      already been initialized or the version is below v201601.
    """
    # If initialization is not necessary, return the provided upload_url.
    if (self._version < 'v201601'
        or current_content_length != 0):
      return upload_url

    headers = {
        'Content-Type': 'application/xml',
        'Content-Length': 0,
        'x-goog-resumable': 'start'
    }

    # Send an HTTP POST request to the given upload_url
    req = urllib2.Request(upload_url, data={}, headers=headers)
    resp = urllib2.urlopen(req)

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
        'upload_url': self._upload_url,
        'version': self._version
    }

    try:
      yaml.dump(data, output)
    except yaml.YAMLError:
      raise googleads.errors.GoogleAdsError(
          'Error dumping IncrementalUploadHelper to file.')

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
    if self._is_last is True:
      raise googleads.errors.AdWordsBatchJobServiceInvalidOperationError(
          'Can\'t add new operations to a completed incremental upload.')
    # Build the request
    req = self._request_builder.BuildUploadRequest(
        self._upload_url, operations,
        current_content_length=self._current_content_length, is_last=is_last)
    # Make the request, ignoring the urllib2.HTTPError raised due to HTTP status
    # code 308 (for resumable uploads).
    try:
      urllib2.urlopen(req)
    except urllib2.HTTPError, e:
      if e.code != 308:
        raise urllib2.HTTPError(e)
    # Update upload status.
    self._current_content_length += len(req.data)
    self._is_last = is_last


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

  def __init__(self, adwords_client, version=sorted(_SERVICE_MAP.keys())[-1],
               server=_DEFAULT_ENDPOINT):
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
    if server[-1] == '/': server = server[:-1]
    self._adwords_client = adwords_client
    self._namespace = self._NAMESPACE_FORMAT % version
    self._end_point = self._END_POINT_FORMAT % (server, version)
    self._header_handler = _AdWordsHeaderHandler(adwords_client, version)

    proxy_option = None
    if self._adwords_client.https_proxy:
      proxy_option = {'https': self._adwords_client.https_proxy}
    # Create an Opener to handle requests when downloading reports.
      self.url_opener = urllib2.build_opener(
          urllib2.ProxyHandler({'https': self._adwords_client.https_proxy}))
    else:
      self.url_opener = urllib2.build_opener()

    schema_url = self._SCHEMA_FORMAT % (server, version)
    schema = suds.client.Client(
        schema_url,
        doctor=suds.xsd.doctor.ImportDoctor(suds.xsd.doctor.Import(
            self._namespace, schema_url)),
        proxy=proxy_option, cache=self._adwords_client.cache).wsdl.schema
    self._report_definition_type = schema.elements[
        (self._REPORT_DEFINITION_NAME, self._namespace)]
    self._marshaller = suds.mx.literal.Literal(schema)

  def _DownloadReportCheckFormat(self, file_format, output):
    if(file_format.startswith('GZIPPED_')
       and not (('b' in getattr(output, 'mode', 'w')) or
                type(output) is io.BytesIO)):
      raise googleads.errors.GoogleAdsValueError('Need to specify a binary'
                                                 ' output for GZIPPED formats.')

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
                         output, kwargs)

  def DownloadReportAsStream(self, report_definition, **kwargs):
    """Downloads an AdWords report using a report definition.

    This will return a stream, allowing you to retrieve the report contents.

    Args:
      report_definition: A dictionary or instance of the ReportDefinition class
          generated from the schema. This defines the contents of the report
          that will be downloaded.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
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
        self._SerializeReportDefinition(report_definition), kwargs)

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
                                        kwargs)

  def DownloadReportAsString(self, report_definition, **kwargs):
    """Downloads an AdWords report using a report definition.

    The report contents will be returned as a string.

    Args:
      report_definition: A dictionary or instance of the ReportDefinition class
          generated from the schema. This defines the contents of the report
          that will be downloaded.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
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
          self._SerializeReportDefinition(report_definition), kwargs)
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
          self._SerializeAwql(query, file_format), kwargs)
      return response.read().decode('utf-8')
    finally:
      if response:
        response.close()

  def DownloadReportWithAwql(self, query, file_format, output=sys.stdout,
                             **kwargs):
    """Downloads an AdWords report using an AWQL query.

    The report contents will be written to the given output.

    Args:
      query: A string containing the query which specifies the data you want
          your report to include.
      file_format: A string representing the output format for your report.
          Acceptable values can be found in our API documentation:
          https://developers.google.com/adwords/api/docs/guides/reporting
      [optional]
      output: A writable object where the contents of the report will be written
          to. If the report is gzip compressed, you need to specify an output
          that can write binary data.
      **kwargs: Optional keyword arguments.

    Keyword Arguments:
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
                         kwargs)

  def _DownloadReport(self, post_body, output, kwargs):
    """Downloads an AdWords report, writing the contents to the given file.

    Args:
      post_body: The contents of the POST request's body as a URL encoded
          string.
      output: A writable object where the contents of the report will be written
          to.
      kwargs: A dictionary containing optional keyword arguments.

    Keyword Arguments:
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
      response = self._DownloadReportAsStream(post_body, kwargs)
      output.write(response.read().decode() if sys.version_info[0] == 3
                   and (getattr(output, 'mode', 'w') == 'w'
                        and type(output) is not io.BytesIO)
                   else response.read())
    finally:
      if response:
        response.close()

  def _DownloadReportAsStream(self, post_body, kwargs):
    """Downloads an AdWords report, returning a stream.

    Args:
      post_body: The contents of the POST request's body as a URL encoded
          string.
      kwargs: A dictionary containing optional keyword arguments.

    Keyword Arguments:
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
        self._header_handler.GetReportDownloadHeaders(kwargs))
    try:
      return self.url_opener.open(request)
    except urllib2.HTTPError, e:
      raise self._ExtractError(e)

  def _SerializeAwql(self, query, file_format):
    """Serializes an AWQL query and file format for transport.

    Args:
      query: A string representing the AWQL query used in the report.
      file_format: A string representing the file format of the generated
          report.

    Returns:
      The given query and format URL encoded into the format needed for an
      AdWords report request as a string. This is intended to be a POST body.
    """
    return urllib.urlencode({'__fmt': file_format, '__rdquery': query})

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
    content = suds.mx.Content(
        tag=self._REPORT_DEFINITION_NAME, value=report_definition,
        name=self._REPORT_DEFINITION_NAME, type=self._report_definition_type)
    return urllib.urlencode({'__rdxml': self._marshaller.process(content)})

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
