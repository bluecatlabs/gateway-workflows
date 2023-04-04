# Copyright 2020-2023 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 2023-04-05
# Gateway Version: 23.1.0
# Description: Example Gateway workflow

# pylint: disable=redefined-builtin,missing-docstring
type = "ui"
sub_pages = [
    {
        "name": "delete_text_record_page",
        "title": "Delete Text Record",
        "endpoint": "delete_text_record/delete_text_record_endpoint",
        "description": "Delete Text Record",
    },
]
