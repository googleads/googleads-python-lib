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

"""Patches applied by the Google Ads Client Library."""

import suds


def Apply():
  """Apply patches used by the Google Ads Client Library."""
  _ApplySudsJurkoAppenderPatch()


def _ApplySudsJurkoAppenderPatch():
  """Appends a Monkey Patch to the suds.mx.appender module.

  This resolves an issue where empty objects are ignored and stripped from the
  request output. More details can be found on the suds-jurko issue tracker:
  https://bitbucket.org/jurko/suds/issues/81/suds-should-support-an-empty-object
  """
  def PatchedAppend(self, parent, content):
    obj = content.value
    child = self.node(content)
    parent.append(child)
    for item in obj:
      cont = suds.mx.Content(tag=item[0], value=item[1])
      suds.mx.appender.Appender.append(self, child, cont)

  suds.mx.appender.ObjectAppender.append = PatchedAppend
