# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import make_response
import io
import csv
from bluecat.api_exception import PortalException, APIException
class bulk_handler:

    output      = None
    form_data   = None
    errors      = 0
    session     = None
    config      = None
    results     = {}

    #These will be called in the order below

    def __init__(self, g, form_data):
        self.form_data = form_data
        self.session = g
        try:
            self.config = g.user.get_api().get_entity_by_id(self.form_data.configuration.data)
        except PortalException:
            g.user.logger.info("Unable to get configuration")
            self.config = None

    def handle_row(self, key, row):
        self.results[key] = row

        if self.config is None:
            self.errors = self.errors + 1
            self.results[key]['result'] = "Unable to find configuration"
            return
        try:
            csv_network_name = row['Network_Name']
            csv_network = row['Network']
        except Exception as e:
            self.errors = self.errors+1
            self.results[key]['result'] = "Missing required value value: %s" % str(e)
            return
        finder_ip = csv_network.split("/")[0]
        try:
            block = self.config.get_ip_range_by_ip("IP4Block", finder_ip)
        except:
            self.errors = self.errors + 1
            self.results[key]['result'] = "Unable to get block"
            return
        try:
            block.add_ip4_network(csv_network, "name=%s" % csv_network_name)
        except (Exception, PortalException, APIException) as e:
            self.errors = self.errors + 1
            self.results[key]['result'] = "Unable to add network. %s" %str(e)
            return
        self.results[key]['result'] = "Added %s" % csv_network
        return



    def go_no_go(self):
        if self.errors > 0:
            return True, "We had one or more errors"
        elif self.config is None:
            return True, "Unable to find config"
        return True, "Success!"

    def return_action(self):
        final_results = []
        final_results.append(list(self.results[1].keys()))
        for k,v in list(self.results.items()):
            row = [value for key,value in list(v.items())]
            final_results.append(row)
        si = io.StringIO()
        w = csv.writer(si)
        w.writerows(final_results)
        output = make_response(si.getvalue())
        output.headers['Content-Disposition'] = 'attachment; filename=upload.csv'
        output.headers['Content-type'] = 'text/csv'
        return output

