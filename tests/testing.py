# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Functions and classes used for unit tests."""


import functools
import unittest

import googleads.common


class CleanUtilityRegistryTestCase(unittest.TestCase):
  """Base class for testing content affecting the UtilityRegistry.

  Subclasses will clear the UtilityRegistry between each test to ensure that it
  is in a clean state before the next test.
  """

  def tearDown(self):
    """Ensures that the UtilityRegistry is cleared between tests."""
    googleads.common._utility_registry.Clear()

_SOAP_BACKENDS = ['suds', 'zeep']


def _CreatePatchedSetUp(func):
  """Create a setUp function that includes the SOAP implementation.

  Args:
    func: A reference to the original setUp function.

  Returns:
    The result of func called with soap_impl.
  """
  @functools.wraps(func)
  def SetUp(self):
    soap_impl = 'suds' if '_suds' in str(self) else 'zeep'
    return func(self, soap_impl)
  return SetUp


def MultiBackendTest(cls):
  """A decorator that patches a test suite to test with zeep and suds.

  Args:
    cls: The test suite to patch

  Returns:
    The patched suite.
  """
  for name, func in list(cls.__dict__.items()):
    if name.startswith('test'):
      for backend in _SOAP_BACKENDS:
        # Create a new test with _suds and _zeep
        setattr(cls, '%s_%s' % (name, backend), func)
      # Delete the original test
      delattr(cls, name)
  cls.setUp = _CreatePatchedSetUp(cls.setUp)
  return cls
