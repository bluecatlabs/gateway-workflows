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

from flask import url_for, redirect, flash
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
        #add your code below

    def handle_row(self, key, row):
        print(row)

    def go_no_go(self):
        #This has to return T/F and a message
        if self.errors > 0:
            #roll things back?
            return False, ""
        return True, ""

    def return_action(self):
        #You must return something the endpoint can return with validity (file or location)
        flash("done!")
        return redirect(url_for('bulkbulk_bulk'))

