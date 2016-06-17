# Copyright 2016 Google Inc. All Rights Reserved.
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

"""Utilities used by the client library."""

import threading

import suds


class PatchHelper(object):
  """Utility that applies patches on behalf of the Google Ads Client Library."""

  def Apply(self):
    """Apply patches used by the Google Ads Client Library."""
    self._ApplySudsJurkoAppenderPatch()

  def _ApplySudsJurkoAppenderPatch(self):
    """Appends a Monkey Patch to the suds.mx.appender module.

    This resolves an issue where empty objects are ignored and stripped from the
    request output. More details can be found on the suds-jurko issue tracker:
    https://goo.gl/uyYw0C
    """
    def PatchedAppend(self, parent, content):
      obj = content.value
      child = self.node(content)
      parent.append(child)
      for item in obj:
        cont = suds.mx.Content(tag=item[0], value=item[1])
        suds.mx.appender.Appender.append(self, child, cont)

    suds.mx.appender.ObjectAppender.append = PatchedAppend


class UtilityRegistry(object):
  """Utility that registers product utilities used in generating a request."""

  def __contains__(self, utility):
    with self._lock:
      return utility in self._registry

  def __init__(self):
    self._enabled = True
    self._registry = set()
    self._lock = threading.Lock()

  def __iter__(self):
    with self._lock:
      return iter(self._registry.copy())

  def __len__(self):
    with self._lock:
      return len(self._registry)

  def Add(self, obj):
    with self._lock:
      if self._enabled:
        self._registry.add(obj)

  def Clear(self):
    with self._lock:
      self._registry.clear()

  def SetEnabled(self, value):
    with self._lock:
      self._enabled = value
