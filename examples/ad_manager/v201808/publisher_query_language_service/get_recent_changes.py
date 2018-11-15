#!/usr/bin/env python
#
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

"""Gets recent changes in your network using the Change_History table.

A full list of available tables can be found at:
https://developers.google.com/doubleclick-publishers/docs/reference/latest/PublisherQueryLanguageService
"""

from datetime import date
from datetime import datetime
from datetime import timedelta

# Import appropriate modules from the client library.
from googleads import ad_manager
import pytz


def main(client):
  # Initialize appropriate service.
  pql_service = client.GetService('PublisherQueryLanguageService', 'v201808')

  end_date = datetime.now(tz=pytz.timezone('America/New_York'))
  start_date = end_date - timedelta(days=1)
  initial_query = ('ChangeDateTime > :startDateTime '
                   'AND ChangeDateTime < :endDateTime')
  pagination_query = 'Id < :id AND ' + initial_query

  statement = (ad_manager.StatementBuilder(version='v201808')
               .Select(('Id, ChangeDateTime, EntityId, EntityType, '
                        'Operation, UserId'))
               .From('Change_History')
               .Where(initial_query)
               .OrderBy('ChangeDateTime', ascending=False)
               .WithBindVariable('startDateTime', start_date)
               .WithBindVariable('endDateTime', end_date))

  keep_iterating = True
  i = 0
  total_rows = []

  while keep_iterating:
    response = pql_service.select(statement.ToStatement())
    column_types = ([column_type['labelName']
                     for column_type in response['columnTypes']])
    rows = response['rows']
    rows_length = len(rows)
    total_rows.extend(rows)

    if rows and rows_length > 0:
      # Get the earliest change ID in the result set.
      last_row = rows[-1]
      last_id = last_row['values'][0]['value']
      i += 1

      # Update the statement using the earliest row in the previous result.
      statement.Where(pagination_query)
      statement.WithBindVariable('id', last_id)

      print ('%d) %d changes prior to ID "%s" were found.\n'
             % (i, rows_length, last_id))

    keep_iterating = rows and len(rows) == statement.limit

  # Print out columns header
  print ','.join(column_types)

  # Print out every row
  for row in total_rows:
    print ConvertValueForCsv(row)


def ConvertValueForCsv(pql_value):
  """Sanitizes a field value from a Value object to a CSV suitable format.

  Args:
    pql_value: dict a dictionary containing the data for a single field of an
                 entity.

  Returns:
    str a CSV writer friendly value formatted by Value.Type.
  """
  if 'value' in pql_value:
    field = pql_value['value']
  elif 'values' in pql_value:
    field = pql_value['values']
  else:
    field = None

  if field:
    if isinstance(field, list):
      return ','.join(['"%s"' % str(ConvertValueForCsv(single_field))
                       for single_field in field])
    else:
      class_type = ad_manager.AdManagerClassType(pql_value)

      if class_type == 'TextValue':
        return field.replace('"', '""').encode('UTF8')
      elif class_type == 'NumberValue':
        return float(field) if '.' in field else int(field)
      elif class_type == 'DateTimeValue':
        return ConvertDateTimeToOffset(field)
      elif class_type == 'DateValue':
        return date(int(field['date']['year']),
                    int(field['date']['month']),
                    int(field['date']['day'])).isoformat()
      else:
        return field
  else:
    return '-'


def ConvertDateTimeToOffset(date_time_value):
  """Converts the PQL formatted response for a dateTime object.

  Output conforms to ISO 8061 format, e.g. 'YYYY-MM-DDTHH:MM:SSz.'

  Args:
    date_time_value: dict The date time value from the PQL response.

  Returns:
    str: A string representation of the date time value uniform to
        ReportService.
  """
  date_time_obj = datetime(int(date_time_value['date']['year']),
                           int(date_time_value['date']['month']),
                           int(date_time_value['date']['day']),
                           int(date_time_value['hour']),
                           int(date_time_value['minute']),
                           int(date_time_value['second']))
  date_time_str = pytz.timezone(
      date_time_value['timeZoneID']).localize(date_time_obj).isoformat()

  if date_time_str[-5:] == '00:00':
    return date_time_str[:-6] + 'Z'
  else:
    return date_time_str


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
