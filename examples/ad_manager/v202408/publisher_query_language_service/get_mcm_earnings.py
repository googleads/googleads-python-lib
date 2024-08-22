#!/usr/bin/env python
#
# Copyright 2020 Google LLC
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

"""This example gets Multiple Customer Management earnings for the prior month.
"""

import datetime
import tempfile

# Import appropriate modules from the client library.
from googleads import ad_manager


def main(client):
  # Initialize a report downloader.
  data_downloader = client.GetDataDownloader(version='v202408')

  with tempfile.NamedTemporaryFile(
      prefix='mcm_earnings_',
      suffix='.csv', mode='w', delete=False) as mcm_earnings_file:

    this_month_start = datetime.date.today().replace(day=1)
    last_month_end = this_month_start - datetime.timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    mcm_earnings_query = ('SELECT Month, ChildName, ChildNetworkCode, '
                          'TotalEarningsCurrencyCode, TotalEarningsMicros, '
                          'ParentPaymentCurrencyCode, ParentPaymentMicros, '
                          'ChildPaymentCurrencyCode, ChildPaymentMicros, '
                          'DeductionsMicros '
                          'FROM Mcm_Earnings '
                          'WHERE Month = :month '
                          'ORDER BY ChildNetworkCode')

    # Downloads the response from PQL select statement to the specified file
    data_downloader.DownloadPqlResultToCsv(
        mcm_earnings_query, mcm_earnings_file, {'month': last_month_start})

    print('Saved MCM earnings to... %s' % mcm_earnings_file.name)


if __name__ == '__main__':
  # Initialize client object.
  ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
  main(ad_manager_client)
