#!/usr/bin/python
#
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

"""Unit tests to cover the errors module."""

__author__ = 'Joseph DiLallo'

import unittest

from googleads import errors


class ErrorsTest(unittest.TestCase):

  """Tests for the googleads.errors module."""

  def testGoogleAdsError(self):
    """Coverage test only for the GoogleAdsError class."""
    errors.GoogleAdsError('error message')

  def testGoogleAdsValueError(self):
    """Coverage test only for the GoogleAdsValueError class."""
    errors.GoogleAdsValueError('error message2')

  def testAdWordsReportError(self):
    """Coverage test only for the AdWordsReportError class."""
    errors.AdWordsReportError('code', 'response', 'error message3')

  def testAdWordsReportBadRequestError(self):
    """Coverage test only for the AdWordsReportBadRequestError class."""
    errors.AdWordsReportBadRequestError(
        'type', 'trigger', 'fieldpath', 'code', 'response', 'error message')

if __name__ == '__main__':
  unittest.main()
