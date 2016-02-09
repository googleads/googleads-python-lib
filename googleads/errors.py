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

"""Errors used by the Google Ads Client Library."""


class GoogleAdsError(Exception):
  """Parent class of all errors raised by this library."""
  pass


class GoogleAdsValueError(GoogleAdsError):
  """Error indicating that the user input for a function was invalid."""
  pass


class AdWordsReportError(GoogleAdsError):
  """Error indicating that an AdWords report download request failed.

  Attributes:
    code: The HTTP status code with which the report failed.
    error: The urllib2.HTTPError (Python 2) or urllib.error.HTTPError
          (Python 3) describing the failure.
    content: The actual HTTP response content. This could be something like a
        404 page or an XML error message from the AdWords report service.
  """

  def __init__(self, code, error, content, message=None):
    """Initializes an AdWordsReportError.

    Args:
      code: The HTTP status code number that was returned.
      error: The urllib2.HTTPError (Python 2) or urllib.error.HTTPError
          (Python 3) describing the failure.
      content: The HTTP response body as a string.
      [optional]
      message: A user-friendly error message string. If one is not provided, a
          default message will be used.
    """
    super(AdWordsReportError, self).__init__(
        message if message else ('AdWords report download failed with HTTP '
                                 'status code: %s' % code))
    self.code = code
    self.error = error
    self.content = content


class AdWordsReportBadRequestError(AdWordsReportError):
  """Error indicating a bad request was made to the AdWords report service.

  Attributes:
    type: A string identifying what type of error this is.
    trigger: A string containing the value from your request that caused the
        problem.
    field_path: A string showing where, in the report's fields, the trigger can
        be found.
  """

  def __init__(self, type_, trigger, field_path, code, error, content):
    """Initializes an AdWordsReportError.

    Args:
      type_: A string identifying what type of error this is.
      trigger: A string containing the value from your request that caused the
          problem.
      field_path: A string showing where, in the report's fields, the trigger
          can be found.
      code: The HTTP status code number that was returned.
      error: The urllib2.HTTPError (Python 2) or urllib.error.HTTPError
          (Python 3) describing the failure.
      content: The HTTP response body as a string.
    """
    super(AdWordsReportBadRequestError, self).__init__(
        code, error, content, 'Type: %s\nTrigger: %s\nField Path: %s' %
        (type_, trigger, field_path))
    self.type = type_
    self.trigger = trigger
    self.field_path = field_path


class AdWordsBatchJobServiceInvalidOperationError(GoogleAdsError):
  """Error indicating that an upload operation is malformed."""
  pass


class DfpReportError(GoogleAdsError):
  """Error indicating that a DFP report download request failed.

  Attributes:
    report_job_id: The ID of the report job which failed.
  """

  def __init__(self, report_job_id):
    """Initializes a DfpReportError.

    Args:
      report_job_id: The ID of the report job which failed.
    """
    super(DfpReportError, self).__init__(
        'DFP report job failed. The ID of the failed report is: %s'
        % report_job_id)
    self.report_job_id = report_job_id
