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

import googleads.common
import googleads.errors

# A giant dictionary of AdWords versions, the services they support, and which
# namespace those services are in.
_SERVICE_MAP = {
    'v201502': {
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
        'CustomerFeedService': 'cm',
        'CustomerService': 'mcm',
        'CustomerSyncService': 'ch',
        'DataService': 'cm',
        'ExperimentService': 'cm',
        'FeedItemService': 'cm',
        'FeedMappingService': 'cm',
        'FeedService': 'cm',
        'GeoLocationService': 'cm',
        'LabelService': 'cm',
        'LocationCriterionService': 'cm',
        'ManagedCustomerService': 'mcm',
        'MediaService': 'cm',
        'MutateJobService': 'cm',
        'OfflineConversionFeedService': 'cm',
        'ReportDefinitionService': 'cm',
        'SharedCriterionService': 'cm',
        'SharedSetService': 'cm',
        'TargetingIdeaService': 'o',
        'TrafficEstimatorService': 'o',
    },
    'v201506': {
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
        'CustomerFeedService': 'cm',
        'CustomerService': 'mcm',
        'CustomerSyncService': 'ch',
        'DataService': 'cm',
        'ExperimentService': 'cm',
        'FeedItemService': 'cm',
        'FeedMappingService': 'cm',
        'FeedService': 'cm',
        'GeoLocationService': 'cm',
        'LabelService': 'cm',
        'LocationCriterionService': 'cm',
        'ManagedCustomerService': 'mcm',
        'MediaService': 'cm',
        'MutateJobService': 'cm',
        'OfflineConversionFeedService': 'cm',
        'ReportDefinitionService': 'cm',
        'SharedCriterionService': 'cm',
        'SharedSetService': 'cm',
        'TargetingIdeaService': 'o',
        'TrafficEstimatorService': 'o',
    },
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
      required key was missing or an OAuth 2.0 key was missing.
    """
    if path is None:
      path = os.path.join(os.path.expanduser('~'), 'googleads.yaml')

    return cls(**googleads.common.LoadFromStorage(
        path, cls._YAML_KEY, cls._REQUIRED_INIT_VALUES,
        cls._OPTIONAL_INIT_VALUES))

  def __init__(
      self, developer_token, oauth2_client, user_agent,
      client_customer_id=None, validate_only=False, partial_failure=False,
      https_proxy=None, cache=None, transport_factory=None):
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
      transport_factory: Callable (e.g. class) to construct alternative
          transports for the Suds client.
    """
    if transport_factory and not callable(transport_factory):
        raise googleads.errors.GoogleAdsValueError(
            "The transport_factory argument must refer to a callable.")

    self.developer_token = developer_token
    self.oauth2_client = oauth2_client
    self.oauth2_client.Refresh()
    self.user_agent = user_agent
    self.client_customer_id = client_customer_id
    self.validate_only = validate_only
    self.partial_failure = partial_failure
    self.https_proxy = https_proxy
    self.cache = cache
    self.transport_factory = transport_factory

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
    transport = self.transport_factory() if self.transport_factory else None
    proxy_option = {'https': self.https_proxy} if self.https_proxy else None
    try:
      client = suds.client.Client(
          self._SOAP_SERVICE_FORMAT %
          (server, _SERVICE_MAP[version][service_name], version, service_name),
          proxy=proxy_option, cache=self.cache, timeout=3600,
          transport=transport)
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

  def GetBatchJobHelper(self):
    """Returns a BatchJobHelper to work with the BatchJobService.

      This is a convenience method. It is functionally identical to calling
      BatchJobHelper(adwords_client, version).

      Returns:
        An initialized BatchJobHelper tied to this client.
    """
    return BatchJobHelper(self)

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


class BatchJobHelperBase(object):
  """A utility that simplifies working with the BatchJobService."""
  # Used to remove namespace from xsi:type Element attributes.
  _ATTRIB_NAMESPACE_SUB = re.compile('ns[0-1]:')
  _UPLOAD_REQUEST_BODY_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<mutate xmlns="%s" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">%s
</mutate>"""

  def __init__(self, adwords_client, version=sorted(_SERVICE_MAP.keys())[-1]):
    """Initializes the BatchJobHelper.

    Args:
      adwords_client: an initialized AdWordsClient.
      version: a str indicating version of the AdWords API you intend to use.
        This will be set to the latest version of AdWords by default.
    """
    self.client = adwords_client
    self._temporary_id = 0  # Used for temporary IDs in BatchJobService.
    self._version = version
    self._adwords_endpoint = ('https://adwords.google.com/api/adwords/cm/%s' %
                              self._version)
    self._adwords_namespace = ('{%s}' % self._adwords_endpoint)
    # Used to remove the AdWords namespace from Element tags.
    self._tag_namespace_sub = re.compile(self._adwords_namespace)

  def GetId(self):
    """Produces a distinct sequential ID for the BatchJobService.

    Returns:
      A negative number that will be the temporary ID for an API resource.
    """
    self._temporary_id -= 1
    return self._temporary_id

  def UploadBatchJobOperations(self, upload_url, *operations):
    """Uploads operations to the given uploadUrl.

    Note: Each list of operations is expected to contain operations of the same
    type, similar to how one would normally send operations in an AdWords API
    Service request.

    Args:
      upload_url: a string url that the given operations will be uploaded to.
      *operations: one or more lists of operations as would be sent to the
        AdWords API for the associated service.
    """
    operations_xml = ''.join([
        self._GenerateOperationsXML(operations_list)
        for operations_list in operations])

    request_body = (self._UPLOAD_REQUEST_BODY_TEMPLATE %
                    (self._adwords_endpoint, operations_xml))

    req = urllib2.Request(upload_url)
    req.add_header('Content-Type', 'application/xml')
    urllib2.urlopen(req, data=request_body)

  def _GenerateOperationsXML(self, operations):
    """Generates XML for the given list of operations.

    Args:
      operations: a list of operations for single AdWords Service.
    Returns:
      A str containing the XML for only the operations, formatted to work
      with the BatchJobService.
    Raises:
      ValueError: if no xsi_type is specified for the operations.
    """
    if operations:
      # Verify that all operations included specify an xsi_type.
      for operation in operations:
        if 'xsi_type' not in operation:
          raise ValueError('Operations have no xsi_type specified.')
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
    service_name = operations[0]['xsi_type'].replace('Operation', 'Service')
    service = self.client.GetService(service_name, self._version)
    service.suds_client.set_options(nosend=True)
    service_request = service.mutate(operations).envelope
    service.suds_client.set_options(nosend=False)
    return service_request

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
      ValueError: If no Operation.Type element is found in the operations. This
        ordinarily happens if no xsi_type is specified for the operations.
    """
    # Extract mutate element from XML, this contains the operations.
    mutate = BatchJobHelper._GetRawOperationsFromXML(self, full_soap_xml)
    # Ensure operations are formatted correctly for BatchJobService.
    for operations in mutate:
      self._FormatForBatchJobService(operations)
      # Extract the operation type, ensure xsi:type is set for
      # BatchJobService. Even if xsi_type is set earlier, suds will end up
      # removing it when it sets Operation.Type.
      operation_type = operations.find('Operation.Type')
      if operation_type is None:
        raise ValueError('No xsi_type specified for the operations.')
      operations.attrib['xsi:type'] = operation_type.text
    operations_xml = ''.join([ElementTree.tostring(operations)
                              for operations in mutate])
    return operations_xml

  def _FormatForBatchJobService(self, element):
    """Formats contents of all operations for use with the BatchJobService.

    This will recursively remove unnecessary namespaces generated by suds that
    would prevent the operations from executing via the BatchJobService. It will
    also remove namespaces appended to the xsi:type in some cases that also
    cause issues for the BatchJobService.

    Args:
      element: a starting Element to be modified to the correct format.
    """
    # Remove any unnecessary AdWords namespace from the tag.
    element.tag = self._tag_namespace_sub.sub('', element.tag)
    xsi_type = element.attrib.get(
        '{http://www.w3.org/2001/XMLSchema-instance}type')
    # If an xsi_type attribute exists, ensure that the namespace is removed from
    # the type.
    if xsi_type:
      element.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] = (
          self._ATTRIB_NAMESPACE_SUB.sub('', xsi_type))
    for child in element:
      self._FormatForBatchJobService(child)

  def _GetRawOperationsFromXML(self, raw_request_xml):
    """Retrieve the raw set of operations from the request XML.

    Args:
      raw_request_xml: The full XML for the desired operation, as generated by
        suds.

    Returns:
      An unmodified mutate Element containing the operations from the raw
      request xml.

    Raises:
      AttributeError: if the provided XML isn't from AdWords.
    """
    root = ElementTree.fromstring(raw_request_xml)
    return root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body').find(
        '%smutate' % self._adwords_namespace)


class BatchJobHelper(BatchJobHelperBase):
  def UploadBatchJobOperations(self, upload_url, *operations):
    """Uploads operations to the given uploadUrl.

    Note: Each list of operations is expected to contain operations of the same
    type, similar to how one would normally send operations in an AdWords API
    Service request.

    Args:
      upload_url: a string url that the given operations will be uploaded to.
      *operations: one or more lists of operations as would be sent to the
        AdWords API for the associated service.
    """
    operations_xml = ''.join([
        self._GenerateOperationsXML(operations_list)
        for operations_list in operations])

    request_body = (self._UPLOAD_REQUEST_BODY_TEMPLATE %
                    (self._adwords_endpoint, operations_xml))

    req = urllib2.Request(upload_url)
    req.add_header('Content-Type', 'application/xml')
    urllib2.urlopen(req, data=request_body)


class ReportDownloaderBase(object):
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
    if self._adwords_client.https_proxy:
      proxy_option = {'https': self._adwords_client.https_proxy}
    else:
      proxy_option = None

    schema_url = self._SCHEMA_FORMAT % (server, version)
    if self._adwords_client.transport_factory:
        transport = self._adwords_client.transport_factory()
    else:
        transport = None
    schema_client = suds.client.Client(
        schema_url,
        doctor=suds.xsd.doctor.ImportDoctor(suds.xsd.doctor.Import(
            self._namespace, schema_url)),
        proxy=proxy_option,
        cache=self._adwords_client.cache,
        transport=transport)
    schema = schema_client.wsdl.schema
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
    return self._DownloadReportAsString(
        self._SerializeReportDefinition(report_definition), kwargs)

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
    return self._DownloadReportAsString(
        self._SerializeAwql(query, file_format), kwargs)

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
    raise NotImplemented("This method needs to be implemented by subclasses.")

  def _DownloadReportAsString(self, post_body, kwargs):
    raise NotImplemented("This method needs to be implemented by subclasses.")

  def _DownloadReportAsStream(self, post_body, kwargs):
    raise NotImplemented("This method needs to be implemented by subclasses.")

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
    return {'__fmt': file_format, '__rdquery': query}

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
    return {'__rdxml': self._marshaller.process(content).plain()}


class ReportDownloader(ReportDownloaderBase):
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
    super(ReportDownloader, self).__init__(adwords_client, version=version, server=server)
    self._header_handler = _AdWordsHeaderHandler(adwords_client, version)

    if self._adwords_client.https_proxy:
    # Create an Opener to handle requests when downloading reports.
      self.url_opener = urllib2.build_opener(
          urllib2.ProxyHandler({'https': self._adwords_client.https_proxy}))
    else:
      self.url_opener = urllib2.build_opener()

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

  def _DownloadReportAsString(self, post_body, kwargs):
    """Downloads an AdWords report, returning a string.

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
    response = None
    try:
      response = self._DownloadReportAsStream(post_body, kwargs)
      return response.read().decode('utf-8')
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
    return urllib.urlencode(super(ReportDownloader, self)._SerializeAwql(query, file_format))

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
    return urllib.urlencode(super(ReportDownloader, self)._SerializeReportDefinition(report_definition))

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
